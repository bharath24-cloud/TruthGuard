import argparse
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.app.database.database import get_db
from backend.app.services.evaluation_service import evaluation_service


def main():
    parser = argparse.ArgumentParser(description="TruthGuard FEVER Scientific Benchmark Evaluation")
    parser.add_argument("--samples", type=int, default=25,
                        help="Number of evaluation samples (default: 25)")
    parser.add_argument("--source", type=str, default="fever", choices=["fever", "documents", "both"],
                        help="Evidence source for retrieval ('fever', 'documents', or 'both')")
    parser.add_argument("--split", type=str, default="paper_dev",
                        help="FEVER split to evaluate (default: paper_dev)")
    parser.add_argument("--top-k", type=int, default=3,
                        help="Top-K evidence passages per claim (default: 3)")
    parser.add_argument("--experiment", type=str, default="B", choices=["A", "B", "all"],
                        help="Experiment ID: A (Baseline/Documents), B (FEVER Knowledge Base), all (A and B comparison)")

    args = parser.parse_args()

    db_gen = get_db()
    db = next(db_gen)

    experiments_to_run = []
    if args.experiment in ("A", "all"):
        experiments_to_run.append(("Experiment A (TruthGuard Baseline - Uploaded Docs)", "documents"))
    if args.experiment in ("B", "all"):
        experiments_to_run.append(("Experiment B (FEVER-Integrated Knowledge Base)", "fever"))

    print("=================================================================")
    print("TruthGuard: Reproducible FEVER Scientific Evaluation Pipeline")
    print(f"Sample Size: {args.samples} | Split: {args.split} | Top-K: {args.top_k}")
    print("Zero Data Leakage: Gold labels are withheld from prediction pipeline")
    print("=================================================================\n")

    results = []
    for exp_title, src in experiments_to_run:
        print(f"--- Running {exp_title} ---")
        try:
            exp = evaluation_service.run_benchmark(
                db=db,
                benchmark_name="FEVER",
                sample_size=args.samples,
                evidence_source=src,
                split=args.split,
                top_k=args.top_k
            )
            print(f"Accuracy:            {exp.accuracy * 100:.2f}%")
            print(f"Macro Precision:     {exp.precision:.4f}")
            print(f"Macro Recall:        {exp.recall:.4f}")
            print(f"Macro F1 Score:      {exp.f1_score:.4f}")
            print(f"Retrieval Recall@K:  {exp.retrieval_recall_at_k * 100:.2f}%")
            print(f"Average Latency:     {exp.latency_per_sample_ms:.1f} ms/sample")
            print(f"Confusion Matrix:    {exp.confusion_matrix}\n")
            results.append(exp.model_dump())
        except Exception as e:
            print(f"[ERROR] Evaluation failed for {exp_title}: {e}\n", file=sys.stderr)

    report_path = "experiments/fever_evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(results, rf, indent=2, default=str)
    print(f"[DONE] Full evaluation results persisted to {report_path}")


if __name__ == "__main__":
    main()
