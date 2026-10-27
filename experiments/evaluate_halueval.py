import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.app.core.config import PROJECT_ROOT, settings
from backend.app.core.logging import logger
from backend.app.datasets.halueval_adapter import halueval_adapter, HaluEvalTask
from backend.app.nlp.halueval_verifier import halueval_verifier


def run_benchmark(
    task: str = "qa",
    limit: int = 30,
    seed: int = 42,
    evidence_source: str = "context",
    sampling_strategy: str = "balanced_sampled",
    output_path: Optional[str] = None,
    resume: bool = True
) -> Dict[str, Any]:
    """
    Executes a leak-free, reproducible evaluation benchmark over real HaluEval examples.
    Saves individual example predictions and computes exact scikit-learn metrics.
    """
    print("=" * 75)
    print(f"TRUTHGUARD BENCHMARK EVALUATION — HALUEVAL ({task.upper()})")
    print("=" * 75)
    print(f"Task:                  {task}")
    print(f"Requested Sample Size: {limit}")
    print(f"Random Seed:           {seed}")
    print(f"Evidence Source:       {evidence_source}")
    print(f"Sampling Strategy:     {sampling_strategy}")
    print(f"Model Configuration:   CrossEncoder ({settings.NLI_MODEL_NAME}) on {settings.NLI_DEVICE}")
    print("-" * 75)

    default_output_dir = PROJECT_ROOT / "data" / "evaluations"
    default_output_dir.mkdir(parents=True, exist_ok=True)
    out_file = Path(output_path) if output_path else default_output_dir / f"halueval_{task}_eval_{limit}_seed{seed}.json"

    # Check for existing partial results if resuming
    existing_predictions: List[Dict[str, Any]] = []
    completed_ids = set()
    if resume and out_file.exists():
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                if "predictions" in saved_data:
                    existing_predictions = saved_data["predictions"]
                    completed_ids = {p["example_id"] for p in existing_predictions}
                    print(f"Found existing evaluation file with {len(completed_ids)} completed sample(s). Resuming...")
        except Exception as e:
            logger.warning(f"Could not read existing file for resume: {e}")

    # Load authentic examples from HaluEval
    t_load_start = time.perf_counter()
    examples, load_report = halueval_adapter.load_task_examples(
        task=task,  # type: ignore
        limit=limit,
        seed=seed,
        sampling_strategy=sampling_strategy  # type: ignore
    )
    load_time = (time.perf_counter() - t_load_start) * 1000

    print(f"Loaded {len(examples)} examples in {load_time:.1f}ms.")
    print(f"Dataset Distribution: {load_report['label_distribution']}")
    print("-" * 75)

    predictions = list(existing_predictions)
    t0_all = time.perf_counter()

    for idx, ex in enumerate(examples):
        if ex.example_id in completed_ids:
            continue

        print(f"[{len(predictions) + 1}/{len(examples)}] Verifying {ex.example_id} (GT: {ex.ground_truth})...", end="", flush=True)
        pred = halueval_verifier.verify_example(
            example=ex,
            evidence_source=evidence_source,
            top_k=settings.RETRIEVAL_TOP_K
        )
        predictions.append(pred)

        match_symbol = "✓" if pred["is_correct"] else "✗"
        print(f" -> Pred: {pred['predicted_label']} [{match_symbol}] ({pred['latency_ms']:.1f}ms)")

        # Periodically save intermediate progress
        if len(predictions) % 5 == 0 or len(predictions) == len(examples):
            partial_metrics = halueval_verifier.calculate_benchmark_metrics(predictions)
            interim_report = {
                "benchmark_name": "HaluEval",
                "task": task,
                "evaluated_samples": len(predictions),
                "total_requested": len(examples),
                "seed": seed,
                "evidence_source": evidence_source,
                "metrics": partial_metrics,
                "dataset_report": load_report,
                "predictions": predictions
            }
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(interim_report, f, indent=2, ensure_ascii=False)

    total_duration = time.perf_counter() - t0_all
    final_metrics = halueval_verifier.calculate_benchmark_metrics(predictions)

    final_report = {
        "benchmark_name": "HaluEval",
        "task": task,
        "evaluated_samples": len(predictions),
        "total_requested": len(examples),
        "seed": seed,
        "evidence_source": evidence_source,
        "metrics": final_metrics,
        "dataset_report": load_report,
        "total_duration_seconds": round(total_duration, 2),
        "predictions": predictions
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)

    # Print summary table
    print("\n" + "=" * 75)
    print("EMPIRICAL BENCHMARK RESULTS")
    print("=" * 75)
    print(f"Total Evaluated:  {final_metrics['total_evaluated']}")
    print(f"Accuracy:         {final_metrics['accuracy'] * 100:.2f}%")
    print(f"Macro Precision:  {final_metrics['precision'] * 100:.2f}%")
    print(f"Macro Recall:     {final_metrics['recall'] * 100:.2f}%")
    print(f"Macro F1 Score:   {final_metrics['macro_f1'] * 100:.2f}%")
    print(f"Weighted F1:      {final_metrics['weighted_f1'] * 100:.2f}%")
    print(f"Average Latency:  {final_metrics['avg_latency_ms']:.1f} ms/sample")
    print(f"Total Duration:   {total_duration:.2f}s")
    print("-" * 75)
    print("Per-Class Breakdown:")
    for cls_name, vals in final_metrics["per_class"].items():
        print(f"  [{cls_name.upper()}] P: {vals['precision']*100:.1f}%, R: {vals['recall']*100:.1f}%, F1: {vals['f1']*100:.1f}% (Support: {vals['support']})")
    print("-" * 75)
    print("Confusion Matrix (Rows: Ground Truth, Cols: Predicted):")
    cm = final_metrics["confusion_matrix"]
    print(f"               Pred: Hallucinated | Pred: Faithful")
    print(f"Actual Hallu:       {cm.get('hallucinated', {}).get('hallucinated', 0):>10}    |    {cm.get('hallucinated', {}).get('faithful', 0):>10}")
    print(f"Actual Faith:       {cm.get('faithful', {}).get('hallucinated', 0):>10}    |    {cm.get('faithful', {}).get('faithful', 0):>10}")
    print("=" * 75)
    print(f"Full per-example predictions and metrics saved to:\n  {out_file}")
    print("=" * 75)

    return final_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TruthGuard HaluEval Benchmark Runner")
    parser.add_argument("--task", default="qa", choices=["qa", "dialogue", "summarization", "general", "all"], help="HaluEval task to evaluate")
    parser.add_argument("--limit", type=int, default=30, help="Number of examples to evaluate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible sampling")
    parser.add_argument("--evidence-source", default="context", choices=["context", "fever", "documents", "both"], help="Evidence source for verification")
    parser.add_argument("--strategy", default="balanced_sampled", choices=["balanced_sampled", "balanced_paired", "sequential"], help="Sampling strategy")
    parser.add_argument("--output", default=None, help="Output JSON path")
    parser.add_argument("--no-resume", action="store_true", help="Do not resume previous run")

    args = parser.parse_args()

    if args.task == "all":
        for t in ["qa", "dialogue", "summarization", "general"]:
            run_benchmark(
                task=t,
                limit=args.limit,
                seed=args.seed,
                evidence_source="context" if t != "general" else "documents",
                sampling_strategy=args.strategy,
                resume=not args.no_resume
            )
    else:
        run_benchmark(
            task=args.task,
            limit=args.limit,
            seed=args.seed,
            evidence_source=args.evidence_source,
            sampling_strategy=args.strategy,
            output_path=args.output,
            resume=not args.no_resume
        )
