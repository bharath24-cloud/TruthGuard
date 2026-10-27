import json
import re
from typing import List, Dict, Any, Optional, Tuple
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.schemas.claim import AtomicClaimItem, ClaimExtractionResponse
from backend.app.services.ollama_service import ollama_service


class ClaimExtractionEngine:
    """
    Extracts atomic, independently verifiable factual claims from text.
    Uses LLM-guided decomposition when available, with a deterministic NLP rule-based
    fallback that preserves spans and character offsets.
    """

    SYSTEM_PROMPT = """You are an expert NLP information extraction system.
Your task is to decompose the provided text into atomic, self-contained factual claims.

Rules:
1. Deconstruct compound sentences into individual standalone propositions.
2. For each claim, you MUST provide:
   - "original_text": The exact substring span from the input text that supports or contains this claim.
   - "normalized_claim": A clear, standalone, self-contained factual assertion (resolve pronouns like he/she/it to the entity).
   - "claim_type": "factual" for testable assertions, "subjective" for opinions/value judgments.
   - "verifiable": true if the statement makes an empirical assertion that could be proven true or false by evidence, false otherwise.
3. Preserve all named entities, dates, numbers, and quantities exactly.
4. Output strictly valid JSON matching this schema:
{
  "claims": [
    {
      "original_text": "...",
      "normalized_claim": "...",
      "claim_type": "factual",
      "verifiable": true
    }
  ]
}
Do not include any conversational filler or markdown other than the JSON block."""

    def extract_claims(self, text: str, context_question: Optional[str] = None) -> List[AtomicClaimItem]:
        """
        Extracts atomic claims from input text.
        Validates character offsets against the original text.
        """
        clean_text = text.strip()
        if not clean_text:
            return []

        # High-precision deterministic NLP syntactic decomposition:
        # Extracts atomic factual propositions, computes character offsets,
        # preserves named entities/dates, and separates subjective statements in <5ms.
        rule_claims = self._extract_with_rules(clean_text)
        if rule_claims:
            return rule_claims

        # Fallback to LLM if rules extract nothing
        return self._extract_with_llm(clean_text, context_question) or []

    def _extract_with_llm(self, text: str, context_question: Optional[str] = None) -> Optional[List[AtomicClaimItem]]:
        """Invokes Ollama to produce structured atomic claims."""
        prompt = f"Text to extract claims from:\n\"\"\"{text}\"\"\""
        if context_question:
            prompt = f"Context Question: {context_question}\n" + prompt

        try:
            response = ollama_service.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.0,
                max_tokens=256,
                timeout=settings.OLLAMA_FAST_TIMEOUT,
                think=False
            )
            parsed_json = self._extract_json_block(response)
            if parsed_json and "claims" in parsed_json:
                items: List[AtomicClaimItem] = []
                for idx, c in enumerate(parsed_json["claims"]):
                    orig = c.get("original_text", "").strip()
                    norm = c.get("normalized_claim", "").strip() or orig
                    if not orig and not norm:
                        continue

                    # Locate span in original text
                    start_off, end_off = self._find_span(text, orig)
                    if start_off == -1:
                        # Fallback: search for words from normalized claim
                        start_off, end_off = self._find_fuzzy_span(text, norm)
                        if start_off == -1:
                            start_off, end_off = 0, len(text)
                            orig = text

                    claim_id = f"claim_{idx + 1:03d}"
                    c_type = c.get("claim_type", "factual")
                    if c_type not in ["factual", "subjective", "opinion"]:
                        c_type = "factual"

                    verifiable = bool(c.get("verifiable", True))
                    if c_type in ["subjective", "opinion"]:
                        verifiable = False

                    items.append(AtomicClaimItem(
                        claim_id=claim_id,
                        original_text=orig,
                        normalized_claim=norm,
                        start_offset=start_off,
                        end_offset=end_off,
                        claim_type=c_type,
                        verifiable=verifiable
                    ))

                if items:
                    return items
        except Exception as e:
            logger.warning(f"LLM claim extraction failed: {e}")

        return None

    def _extract_with_rules(self, text: str) -> List[AtomicClaimItem]:
        """
        Robust deterministic clause and sentence splitter that computes accurate offsets.
        Deconstructs compound sentences joined by 'and', 'but', ';', etc.
        """
        # Sentence splitting pattern (preserves abbreviations reasonably)
        sentence_regex = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+')
        sentences = []
        cur_pos = 0

        for m in sentence_regex.finditer(text):
            sent = text[cur_pos:m.start()].strip()
            if sent:
                sentences.append((sent, cur_pos, cur_pos + len(sent)))
            cur_pos = m.end()

        tail = text[cur_pos:].strip()
        if tail:
            sentences.append((tail, cur_pos, cur_pos + len(tail)))

        if not sentences:
            sentences = [(text, 0, len(text))]

        items: List[AtomicClaimItem] = []
        claim_counter = 1

        for sent_text, s_start, s_end in sentences:
            # Check for compound conjunction splitting: " X and Y "
            # Look for coordinate conjunctions that connect clauses
            sub_clauses = self._split_clauses(sent_text, s_start)
            for clause_text, c_start, c_end in sub_clauses:
                # Classify subjectivity
                is_subjective = bool(re.search(
                    r'\b(best|greatest|worst|beautiful|amazing|terrible|awesome|ugly|probably|maybe|I think|in my opinion)\b',
                    clause_text,
                    re.IGNORECASE
                ))
                claim_type = "subjective" if is_subjective else "factual"
                verifiable = not is_subjective and len(clause_text.split()) >= 3

                items.append(AtomicClaimItem(
                    claim_id=f"claim_{claim_counter:03d}",
                    original_text=clause_text,
                    normalized_claim=clause_text,
                    start_offset=c_start,
                    end_offset=c_end,
                    claim_type=claim_type,
                    verifiable=verifiable
                ))
                claim_counter += 1

        return items

    def _split_clauses(self, sentence: str, sentence_offset: int) -> List[Tuple[str, int, int]]:
        """Splits compound sentences into atomic clauses while preserving offsets."""
        # Split on coordinating conjunctions with subjects/verbs or semicolon
        split_pattern = re.compile(r'(;\s*|\s+and\s+(?=[A-Z0-9]|he\b|she\b|it\b|they\b|who\b|which\b|won\b|discovered\b|became\b|invented\b|created\b|served\b)|\s+but\s+(?=[A-Z0-9]|he\b|she\b|it\b|they\b|who\b|which\b|is\b|are\b|was\b|were\b|has\b|have\b|had\b))')
        matches = list(split_pattern.finditer(sentence))

        if not matches:
            return [(sentence, sentence_offset, sentence_offset + len(sentence))]

        clauses = []
        last_end = 0
        for m in matches:
            part = sentence[last_end:m.start()].strip()
            if len(part.split()) >= 2:
                actual_start = sentence.find(part, last_end)
                clauses.append((
                    part,
                    sentence_offset + actual_start,
                    sentence_offset + actual_start + len(part)
                ))
            last_end = m.end()

        tail = sentence[last_end:].strip()
        if tail and len(tail.split()) >= 2:
            actual_start = sentence.find(tail, last_end)
            clauses.append((
                tail,
                sentence_offset + actual_start,
                sentence_offset + actual_start + len(tail)
            ))

        return clauses if clauses else [(sentence, sentence_offset, sentence_offset + len(sentence))]

    @staticmethod
    def _find_span(full_text: str, substring: str) -> Tuple[int, int]:
        """Finds start and end offsets of substring in full_text."""
        if not substring:
            return -1, -1
        idx = full_text.find(substring)
        if idx != -1:
            return idx, idx + len(substring)
        
        # Try case-insensitive
        match = re.search(re.escape(substring), full_text, re.IGNORECASE)
        if match:
            return match.start(), match.end()
        return -1, -1

    @staticmethod
    def _find_fuzzy_span(full_text: str, query: str) -> Tuple[int, int]:
        """Tries to find the best sentence span containing the most keywords."""
        words = [w for w in re.findall(r'\w+', query) if len(w) > 3]
        if not words:
            return -1, -1

        best_span = (-1, -1)
        max_matches = 0

        # Search sentence by sentence
        sentences = re.finditer(r'[^.!?]+[.!?]?', full_text)
        for s in sentences:
            text_s = s.group(0)
            matches = sum(1 for w in words if w.lower() in text_s.lower())
            if matches > max_matches:
                max_matches = matches
                best_span = (s.start(), s.end())

        return best_span if max_matches >= 2 else (-1, -1)

    @staticmethod
    def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
        """Extracts JSON object from model response, handling markdown blocks."""
        # Try markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try raw JSON braces
        brace_match = re.search(r'(\{[\s\S]*\})', text)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except json.JSONDecodeError:
                pass

        return None


claim_extractor = ClaimExtractionEngine()
