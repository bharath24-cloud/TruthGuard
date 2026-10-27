import argparse
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.datasets.fever_evidence_indexer import fever_indexer


def main():
    parser = argparse.ArgumentParser(description="TruthGuard FEVER Evidence Corpus FAISS Indexer")
    parser.add_argument("--split", type=str, default="paper_dev",
                        help="FEVER split corresponding to prepared dataset")
    parser.add_argument("--limit", type=int, default=1000,
                        help="Sample size of prepared dataset")
    parser.add_argument("--input", type=str, default=None,
                        help="Explicit path to prepared JSONL dataset")
    parser.add_argument("--max-articles", type=int, default=None,
                        help="Cap on Wikipedia articles to index (for rapid dev)")
    parser.add_argument("--rebuild", action="store_true", default=True,
                        help="Rebuild FAISS index from scratch")

    args = parser.parse_args()

    input_path = Path(args.input) if args.input else (settings.DATASETS_PATH / "fever" / "prepared" / f"fever_{args.split}_{args.limit}.jsonl")

    print(f"==================================================")
    print(f"TruthGuard: FEVER Evidence Corpus Indexing")
    print(f"Target: {input_path}")
    print(f"==================================================")

    if not input_path.exists():
        print(f"\n[ERROR] File not found: {input_path}", file=sys.stderr)
        print("Please run 'python -m experiments.prepare_fever' first.", file=sys.stderr)
        sys.exit(1)

    try:
        summary = fever_indexer.build_index_from_prepared_dataset(
            prepared_dataset_path=input_path,
            max_articles=args.max_articles,
            rebuild=args.rebuild
        )
        print("\n[SUCCESS] FEVER Knowledge Base FAISS index successfully created!")
        print(f"Articles Resolved: {summary.get('articles_resolved')} / {summary.get('total_articles_referenced')}")
        print(f"Total Vectors in FAISS Index: {summary.get('total_vectors_indexed')}")
        print(f"Summary saved to: data/indexes/fever_knowledge_base_summary.json")
    except Exception as e:
        print(f"\n[ERROR] Indexing failed: {e}", file=sys.stderr)
        logger.error(f"Indexing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
