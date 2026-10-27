import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.nlp.retriever import retriever
from backend.app.core.config import settings

print("Total vectors in index:", retriever.index.ntotal)
print("Default SIMILARITY_THRESHOLD:", settings.SIMILARITY_THRESHOLD)

claims = [
    "Water is a chemical compound with the formula H₂O.",
    "Water is a chemical compound with the formula H2O.",
    "Pure water freezes at 0°C and boils at 100°C at standard atmospheric pressure.",
    "Water has a density of approximately 1 g/cm³ near 4°C.",
    "Water is composed of hydrogen and nitrogen, and its boiling point is always 120°C regardless of pressure."
]

for c in claims:
    res_thresh = retriever.retrieve(c, top_k=5)
    res_all = retriever.retrieve(c, top_k=5, similarity_threshold=0.0)
    print(f"\nQuery: {c}")
    print(f"Results with default threshold ({settings.SIMILARITY_THRESHOLD}): {len(res_thresh)}")
    print(f"Results without threshold: {len(res_all)}")
    for r in res_all[:2]:
        print(f"  Score: {r['similarity_score']} | Doc: {r['document_name']} | Text: {repr(r['passage_text'])}")
