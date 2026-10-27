import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Literal
import random

from backend.app.core.config import PROJECT_ROOT, settings
from backend.app.core.logging import logger

HaluEvalTask = Literal["qa", "dialogue", "summarization", "general"]


class HaluEvalExample:
    """
    Standardized internal representation of a HaluEval benchmark example.
    Preserves all original fields while exposing normalized query, response,
    context (knowledge/document), and ground-truth hallucination label.
    """

    def __init__(
        self,
        example_id: Optional[str] = None,
        task: HaluEvalTask = "qa",
        query: Optional[str] = None,
        response: str = "",
        is_hallucinated: Optional[bool] = None,
        ground_truth: Optional[str] = None,
        context: Optional[str] = None,
        context_type: str = "none",
        hallucination_spans: Optional[List[str]] = None,
        raw_record: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        prompt: Optional[str] = None,
        ground_truth_label: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        self.example_id = example_id or id or "unknown"
        self.task = task
        self.query = query or prompt or ""
        self.response = response
        self.metadata = metadata or raw_record or kwargs or {}
        gt = ground_truth or ground_truth_label
        if gt:
            self.ground_truth = gt
            self.is_hallucinated = (gt == "hallucinated") if is_hallucinated is None else is_hallucinated
        else:
            self.is_hallucinated = is_hallucinated if is_hallucinated is not None else False
            self.ground_truth = "hallucinated" if self.is_hallucinated else "faithful"
        self.context = context
        self.context_type = context_type
        self.hallucination_spans = hallucination_spans or []
        self.raw_record = raw_record or {}

    @property
    def id(self) -> str:
        return self.example_id

    @property
    def prompt(self) -> str:
        return self.query

    @property
    def ground_truth_label(self) -> str:
        return self.ground_truth

    def to_dict(self) -> Dict[str, Any]:
        return {
            "example_id": self.example_id,
            "task": self.task,
            "query": self.query,
            "response": self.response,
            "is_hallucinated": self.is_hallucinated,
            "ground_truth": self.ground_truth,
            "context": self.context,
            "context_type": self.context_type,
            "hallucination_spans": self.hallucination_spans
        }


class HaluEvalAdapter:
    """
    Reusable, production-grade dataset adapter for HaluEval.
    Reads local JSON/JSONL files without re-downloading, validates schemas,
    normalizes records into HaluEvalExample, handles malformed records safely,
    and supports deterministic, balanced sampling.
    """

    DATA_DIR = PROJECT_ROOT / "HaluEval-main" / "data"

    TASK_FILES = {
        "qa": "qa_data.json",
        "dialogue": "dialogue_data.json",
        "summarization": "summarization_data.json",
        "general": "general_data.json"
    }

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or self.DATA_DIR

    def get_dataset_status(self) -> Dict[str, Any]:
        """Audits file availability, sizes, and record counts across all HaluEval tasks."""
        status = {}
        for task, fname in self.TASK_FILES.items():
            fpath = self.data_dir / fname
            if not fpath.exists():
                status[task] = {
                    "available": False,
                    "file_path": str(fpath),
                    "error": "File not found"
                }
                continue

            size_mb = round(fpath.stat().st_size / (1024 * 1024), 2)
            try:
                valid_count = 0
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            valid_count += 1
                status[task] = {
                    "available": True,
                    "file_path": str(fpath),
                    "size_mb": size_mb,
                    "total_records": valid_count,
                    "context_provided": task in ["qa", "dialogue", "summarization"]
                }
            except Exception as e:
                status[task] = {
                    "available": False,
                    "file_path": str(fpath),
                    "error": str(e)
                }
        return status

    def load_task_examples(
        self,
        task: HaluEvalTask,
        limit: Optional[int] = None,
        seed: int = 42,
        sampling_strategy: Literal["balanced_paired", "balanced_sampled", "sequential"] = "balanced_sampled"
    ) -> Tuple[List[HaluEvalExample], Dict[str, Any]]:
        """
        Loads and validates examples for a specific HaluEval task.

        Sampling strategies:
        - 'balanced_sampled': For qa/dialogue/summarization, deterministically selects either
          hallucinated or right response using seeded coin-flip per record to build a balanced dataset.
        - 'balanced_paired': Returns both hallucinated and right responses as separate examples (2x examples).
        - 'sequential': Reads top-N records directly in original file order.

        Returns:
            examples: List[HaluEvalExample]
            report: metadata dictionary tracking valid/skipped counts and label distributions.
        """
        if task not in self.TASK_FILES:
            raise ValueError(f"Unknown HaluEval task: {task}. Must be one of {list(self.TASK_FILES.keys())}")

        file_path = self.data_dir / self.TASK_FILES[task]
        if not file_path.exists():
            raise FileNotFoundError(f"HaluEval dataset file not found at: {file_path}")

        rng = random.Random(seed)
        examples: List[HaluEvalExample] = []
        skipped_count = 0
        skip_reasons: Dict[str, int] = {}
        total_raw_records = 0

        with open(file_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                line_str = line.strip()
                if not line_str:
                    continue
                total_raw_records += 1

                try:
                    record = json.loads(line_str)
                except Exception as e:
                    skipped_count += 1
                    skip_reasons["json_decode_error"] = skip_reasons.get("json_decode_error", 0) + 1
                    continue

                parsed = self._parse_record(record, task, line_idx, rng, sampling_strategy)
                if not parsed:
                    skipped_count += 1
                    skip_reasons["missing_required_fields"] = skip_reasons.get("missing_required_fields", 0) + 1
                    continue

                if task == "general" and sampling_strategy == "balanced_sampled" and limit:
                    target_per_class = limit // 2
                    hallu_count = sum(1 for e in examples if e.is_hallucinated)
                    faith_count = sum(1 for e in examples if not e.is_hallucinated)

                    if parsed.is_hallucinated and hallu_count < target_per_class:
                        examples.append(parsed)
                    elif not parsed.is_hallucinated and faith_count < (limit - target_per_class):
                        examples.append(parsed)

                    if len(examples) >= limit:
                        break
                else:
                    if isinstance(parsed, list):
                        examples.extend(parsed)
                    else:
                        examples.append(parsed)

                    if limit and len(examples) >= limit:
                        examples = examples[:limit]
                        break

        label_dist = {
            "hallucinated": sum(1 for e in examples if e.is_hallucinated),
            "faithful": sum(1 for e in examples if not e.is_hallucinated)
        }

        report = {
            "task": task,
            "file": str(file_path),
            "total_raw_processed": total_raw_records,
            "valid_examples_extracted": len(examples),
            "skipped_records": skipped_count,
            "skip_reasons": skip_reasons,
            "label_distribution": label_dist,
            "sampling_strategy": sampling_strategy,
            "seed": seed
        }

        logger.info(
            f"Loaded {len(examples)} HaluEval examples for task '{task}' "
            f"(hallucinated: {label_dist['hallucinated']}, faithful: {label_dist['faithful']})."
        )
        return examples, report

    def _parse_record(
        self,
        record: Dict[str, Any],
        task: HaluEvalTask,
        index: int,
        rng: random.Random,
        strategy: str
    ) -> Optional[Any]:
        """Parses a single raw record according to the task schema."""
        if task == "qa":
            return self._parse_qa_record(record, index, rng, strategy)
        elif task == "dialogue":
            return self._parse_dialogue_record(record, index, rng, strategy)
        elif task == "summarization":
            return self._parse_summarization_record(record, index, rng, strategy)
        elif task == "general":
            return self._parse_general_record(record, index)
        return None

    def _parse_qa_record(
        self,
        record: Dict[str, Any],
        index: int,
        rng: random.Random,
        strategy: str
    ) -> Optional[Any]:
        question = record.get("question")
        hallucinated_ans = record.get("hallucinated_answer")
        right_ans = record.get("right_answer")
        knowledge = record.get("knowledge", "")

        if not question or not (hallucinated_ans or right_ans):
            return None

        if strategy == "balanced_paired" and hallucinated_ans and right_ans:
            return [
                HaluEvalExample(
                    example_id=f"halueval_qa_{index}_hallu",
                    task="qa",
                    query=question,
                    response=hallucinated_ans,
                    is_hallucinated=True,
                    ground_truth="hallucinated",
                    context=knowledge,
                    context_type="knowledge",
                    raw_record=record
                ),
                HaluEvalExample(
                    example_id=f"halueval_qa_{index}_faith",
                    task="qa",
                    query=question,
                    response=right_ans,
                    is_hallucinated=False,
                    ground_truth="faithful",
                    context=knowledge,
                    context_type="knowledge",
                    raw_record=record
                )
            ]

        # Seeded deterministic coin-flip for balanced single-sample evaluation
        select_hallucinated = rng.random() > 0.5
        if select_hallucinated and hallucinated_ans:
            resp = hallucinated_ans
            is_hallu = True
            gt = "hallucinated"
        elif right_ans:
            resp = right_ans
            is_hallu = False
            gt = "faithful"
        else:
            resp = hallucinated_ans
            is_hallu = True
            gt = "hallucinated"

        return HaluEvalExample(
            example_id=f"halueval_qa_{index}",
            task="qa",
            query=question,
            response=resp,
            is_hallucinated=is_hallu,
            ground_truth=gt,
            context=knowledge,
            context_type="knowledge",
            raw_record=record
        )

    def _parse_dialogue_record(
        self,
        record: Dict[str, Any],
        index: int,
        rng: random.Random,
        strategy: str
    ) -> Optional[Any]:
        dialog_history = record.get("dialogue_history")
        hallucinated_resp = record.get("hallucinated_response")
        right_resp = record.get("right_response")
        knowledge = record.get("knowledge", "")

        if not dialog_history or not (hallucinated_resp or right_resp):
            return None

        if strategy == "balanced_paired" and hallucinated_resp and right_resp:
            return [
                HaluEvalExample(
                    example_id=f"halueval_dial_{index}_hallu",
                    task="dialogue",
                    query=dialog_history,
                    response=hallucinated_resp,
                    is_hallucinated=True,
                    ground_truth="hallucinated",
                    context=knowledge,
                    context_type="knowledge",
                    raw_record=record
                ),
                HaluEvalExample(
                    example_id=f"halueval_dial_{index}_faith",
                    task="dialogue",
                    query=dialog_history,
                    response=right_resp,
                    is_hallucinated=False,
                    ground_truth="faithful",
                    context=knowledge,
                    context_type="knowledge",
                    raw_record=record
                )
            ]

        select_hallucinated = rng.random() > 0.5
        if select_hallucinated and hallucinated_resp:
            resp = hallucinated_resp
            is_hallu = True
            gt = "hallucinated"
        elif right_resp:
            resp = right_resp
            is_hallu = False
            gt = "faithful"
        else:
            resp = hallucinated_resp
            is_hallu = True
            gt = "hallucinated"

        return HaluEvalExample(
            example_id=f"halueval_dial_{index}",
            task="dialogue",
            query=dialog_history,
            response=resp,
            is_hallucinated=is_hallu,
            ground_truth=gt,
            context=knowledge,
            context_type="knowledge",
            raw_record=record
        )

    def _parse_summarization_record(
        self,
        record: Dict[str, Any],
        index: int,
        rng: random.Random,
        strategy: str
    ) -> Optional[Any]:
        document = record.get("document")
        hallucinated_sum = record.get("hallucinated_summary")
        right_sum = record.get("right_summary")

        if not document or not (hallucinated_sum or right_sum):
            return None

        if strategy == "balanced_paired" and hallucinated_sum and right_sum:
            return [
                HaluEvalExample(
                    example_id=f"halueval_summ_{index}_hallu",
                    task="summarization",
                    query="Summarize the document accurately:",
                    response=hallucinated_sum,
                    is_hallucinated=True,
                    ground_truth="hallucinated",
                    context=document,
                    context_type="document",
                    raw_record=record
                ),
                HaluEvalExample(
                    example_id=f"halueval_summ_{index}_faith",
                    task="summarization",
                    query="Summarize the document accurately:",
                    response=right_sum,
                    is_hallucinated=False,
                    ground_truth="faithful",
                    context=document,
                    context_type="document",
                    raw_record=record
                )
            ]

        select_hallucinated = rng.random() > 0.5
        if select_hallucinated and hallucinated_sum:
            resp = hallucinated_sum
            is_hallu = True
            gt = "hallucinated"
        elif right_sum:
            resp = right_sum
            is_hallu = False
            gt = "faithful"
        else:
            resp = hallucinated_sum
            is_hallu = True
            gt = "hallucinated"

        return HaluEvalExample(
            example_id=f"halueval_summ_{index}",
            task="summarization",
            query="Summarize the document accurately:",
            response=resp,
            is_hallucinated=is_hallu,
            ground_truth=gt,
            context=document,
            context_type="document",
            raw_record=record
        )

    def _parse_general_record(
        self,
        record: Dict[str, Any],
        index: int
    ) -> Optional[HaluEvalExample]:
        query = record.get("user_query")
        response = record.get("chatgpt_response")
        raw_label = str(record.get("hallucination", "")).strip().lower()

        if not query or not response or raw_label not in ["yes", "no"]:
            return None

        is_hallu = (raw_label == "yes")
        gt = "hallucinated" if is_hallu else "faithful"
        spans = record.get("hallucination_spans", [])

        return HaluEvalExample(
            example_id=f"halueval_gen_{record.get('ID', index)}",
            task="general",
            query=query,
            response=response,
            is_hallucinated=is_hallu,
            ground_truth=gt,
            context=None,
            context_type="none",
            hallucination_spans=spans if isinstance(spans, list) else [],
            raw_record=record
        )


halueval_adapter = HaluEvalAdapter()
