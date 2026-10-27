import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import requests

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.datasets.fever_loader import normalize_fever_title
from backend.app.nlp.retriever import fever_retriever


class FEVEREvidenceIndexer:
    """
    Builds and maintains the dedicated FEVER Evidence Corpus FAISS Knowledge Base.
    Ensures strict role separation:
      - Claims and gold labels belong strictly to verification examples.
      - Factual Wikipedia text belongs strictly to this evidence corpus.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (settings.DATASETS_PATH / "fever")
        self.cache_dir = self.data_dir / "evidence_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TruthGuardResearchBot/1.0 (NLP Evidence Verification; contact@truthguard.ai)"
        })

    def _sanitize_filename(self, name: str) -> str:
        """Converts arbitrary titles into filesystem-safe names."""
        return re.sub(r'[\\/*?:"<>| ]', "_", name)

    def fetch_wikipedia_page(self, wiki_title: str) -> Optional[Dict[str, Any]]:
        """
        Fetches full plaintext article extract from Wikipedia API or local cache.
        Returns dict with title, extract, and split sentences.
        """
        clean_title = normalize_fever_title(wiki_title)
        safe_name = self._sanitize_filename(clean_title)
        cache_file = self.cache_dir / f"{safe_name}.json"

        # Check local cache
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cached page '{safe_name}': {e}")

        # Fetch via MediaWiki API
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": "1",
            "titles": clean_title,
            "redirects": "1",
            "format": "json"
        }

        try:
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                pages = resp.json().get("query", {}).get("pages", {})
                for pid, pdata in pages.items():
                    if pid == "-1":
                        logger.warning(f"Wikipedia page not found: '{clean_title}'")
                        return None
                    
                    extract_text = pdata.get("extract", "").strip()
                    if not extract_text:
                        return None

                    # Split text into discrete sentences
                    raw_sents = re.split(r'(?<=[.!?])\s+', extract_text)
                    clean_sents = [s.strip() for s in raw_sents if len(s.strip()) > 10]

                    page_info = {
                        "raw_fever_title": wiki_title,
                        "clean_title": clean_title,
                        "page_id": pid,
                        "url": f"https://en.wikipedia.org/wiki/{clean_title.replace(' ', '_')}",
                        "sentence_count": len(clean_sents),
                        "sentences": clean_sents,
                        "cached_at": datetime.utcnow().isoformat()
                    }

                    # Save to local cache
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(page_info, f, indent=2, ensure_ascii=False)

                    return page_info
            else:
                logger.warning(f"Wikipedia API error {resp.status_code} for '{clean_title}'")
                return None
        except Exception as e:
            logger.error(f"Failed to fetch Wikipedia page '{clean_title}': {e}")
            return None

    def build_index_from_prepared_dataset(
        self,
        prepared_dataset_path: Path,
        max_articles: Optional[int] = None,
        rebuild: bool = True
    ) -> Dict[str, Any]:
        """
        Extracts all Wikipedia titles referenced in the prepared dataset,
        retrieves their sentences, and indexes them into fever_retriever.
        """
        if not prepared_dataset_path.exists():
            raise FileNotFoundError(f"Prepared dataset not found: {prepared_dataset_path}")

        logger.info(f"Scanning referenced Wikipedia titles in {prepared_dataset_path}...")
        needed_titles: Set[str] = set()

        with open(prepared_dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    for title in item.get("wikipedia_titles", []):
                        if title:
                            needed_titles.add(title)

        logger.info(f"Found {len(needed_titles)} unique Wikipedia articles referenced in prepared dataset.")

        if max_articles:
            needed_titles = set(list(needed_titles)[:max_articles])
            logger.info(f"Limited indexing to {len(needed_titles)} articles.")

        if rebuild:
            logger.info("Rebuilding FEVER FAISS knowledge base from scratch...")
            fever_retriever.clear()

        resolved_count = 0
        failed_count = 0
        all_chunks: List[Dict[str, Any]] = []
        seen_passages: Set[int] = set()

        for idx, title in enumerate(sorted(list(needed_titles)), 1):
            page_data = self.fetch_wikipedia_page(title)
            if not page_data or not page_data.get("sentences"):
                failed_count += 1
                continue

            resolved_count += 1
            clean_t = page_data["clean_title"]
            safe_name = self._sanitize_filename(clean_t)

            for s_idx, sent in enumerate(page_data["sentences"][:20]):  # Index lead 20 sentences per article
                text_hash = hash(sent.lower())
                if text_hash in seen_passages:
                    continue
                seen_passages.add(text_hash)

                all_chunks.append({
                    "chunk_id": f"fever_{safe_name}_s{s_idx}",
                    "document_id": f"fever_wiki_{safe_name}",
                    "document_name": f"Wikipedia: {clean_t}",
                    "page_number": s_idx + 1,
                    "content": sent,
                    "source_type": "fever"
                })

            # Batch index in chunks of 200
            if len(all_chunks) >= 200:
                fever_retriever.add_chunks(all_chunks)
                all_chunks = []

            if idx % 25 == 0 or idx == len(needed_titles):
                logger.info(f"Indexed [{idx}/{len(needed_titles)}] articles. Total vectors: {fever_retriever.index.ntotal}")

        # Index any remaining chunks
        if all_chunks:
            fever_retriever.add_chunks(all_chunks)

        fever_retriever.save_index()

        summary = {
            "index_name": "fever_knowledge_base",
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "total_articles_referenced": len(needed_titles),
            "articles_resolved": resolved_count,
            "articles_unresolved": failed_count,
            "total_vectors_indexed": fever_retriever.index.ntotal,
            "rebuilt_at": datetime.utcnow().isoformat()
        }

        summary_path = settings.INDEXES_PATH / "fever_knowledge_base_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"FEVER Knowledge Base indexing complete: {summary}")
        return summary


fever_indexer = FEVEREvidenceIndexer()
