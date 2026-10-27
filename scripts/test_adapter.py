import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.datasets.halueval_adapter import halueval_adapter

print("--- HaluEval Dataset Status ---")
status = halueval_adapter.get_dataset_status()
for k, v in status.items():
    print(k, v)

print("\n--- Testing Task Loading ---")
for task in ["qa", "dialogue", "summarization", "general"]:
    exs, rep = halueval_adapter.load_task_examples(task, limit=10, seed=42)
    dist = rep["label_distribution"]
    print(f"\nTask {task}: loaded {len(exs)} examples. Distribution: {dist}")
    first = exs[0]
    print(f"  First ID: {first.example_id} | GT: {first.ground_truth} | Hallu: {first.is_hallucinated}")
    print(f"  Query: {first.query[:60]}...")
    print(f"  Response: {first.response[:60]}...")
    if first.context:
        print(f"  Context ({first.context_type}): {first.context[:60]}...")
