import argparse
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.app.core.logging import logger
from backend.app.datasets.fever_loader import fever_loader


def main():
    parser = argparse.ArgumentParser(description="TruthGuard FEVER Benchmark Dataset Preparation")
    parser.add_argument("--split", type=str, default="paper_dev", choices=["paper_dev", "train", "paper_test"],
                        help="FEVER split to prepare (default: paper_dev)")
    parser.add_argument("--limit", type=int, default=1000,
                        help="Sample size limit (default: 1000)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducible sampling (default: 42)")
    parser.add_argument("--force-download", action="store_true",
                        help="Force re-download even if cached")

    args = parser.parse_args()

    print(f"==================================================")
    print(f"TruthGuard: FEVER Dataset Preparation")
    print(f"Split: {args.split} | Limit: {args.limit} | Seed: {args.seed}")
    print(f"==================================================")

    try:
        out_path, summary = fever_loader.prepare_dataset(
            split=args.split,
            limit=args.limit,
            seed=args.seed,
            force_download=args.force_download
        )
        print("\n[SUCCESS] FEVER dataset successfully prepared!")
        print(f"Saved to: {out_path}")
        print(f"Class Distribution: {summary.get('class_distribution')}")
        print(f"Unique Wikipedia Articles: {summary.get('unique_wikipedia_articles_referenced')}")
        print(f"Duplicates Removed: {summary.get('duplicates_removed')}")
    except Exception as e:
        print(f"\n[ERROR] Preparation failed: {e}", file=sys.stderr)
        logger.error(f"Preparation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
