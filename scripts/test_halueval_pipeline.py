import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.datasets.halueval_adapter import halueval_adapter
from backend.app.nlp.claim_extractor import claim_extractor
from backend.app.nlp.nli_verifier import nli_verifier
from backend.app.nlp.embeddings import embedding_engine
import numpy as np
import time

examples, rep = halueval_adapter.load_task_examples("qa", limit=5, seed=42)

print(f"Loaded {len(examples)} examples. Running test pipeline...")

for ex in examples:
    t0 = time.perf_counter()
    print("=" * 60)
    print(f"ID: {ex.example_id} | GT: {ex.ground_truth}")
    print(f"Q: {ex.query}")
    print(f"Resp: {ex.response}")
    print(f"Knowledge: {ex.context[:100]}...")

    # 1. Claims
    claims = claim_extractor.extract_claims(ex.response, context_question=ex.query)
    if not claims:
        # Fallback to response text
        from backend.app.schemas.claim import AtomicClaimItem
        claims = [AtomicClaimItem(
            claim_id="claim_001",
            original_text=ex.response,
            normalized_claim=f"{ex.query} -> {ex.response}",
            start_offset=0,
            end_offset=len(ex.response),
            claim_type="factual",
            verifiable=True
        )]
    print(f"Claims extracted: {len(claims)}")
    for c in claims:
        print(f"  Claim: {c.normalized_claim}")

    # 2. Context passages
    context_sents = [s.strip() for s in ex.context.split(".") if len(s.strip()) > 10]
    if not context_sents:
        context_sents = [ex.context]

    # Rank context sentences by embedding similarity to response
    q_emb = embedding_engine.encode([ex.response], normalize_embeddings=True)
    c_embs = embedding_engine.encode(context_sents, normalize_embeddings=True)
    sims = np.dot(c_embs, q_emb.T).flatten()
    top_indices = np.argsort(-sims)[:3]
    top_passages = [context_sents[idx] for idx in top_indices]

    # 3. NLI pairs
    for c in claims:
        pairs = [(p, c.normalized_claim) for p in top_passages]
        nli_res = nli_verifier.predict_batch(pairs)
        for p, r in zip(top_passages, nli_res):
            print(f"  NLI vs '{p[:50]}...': {r['nli_label']} (E:{r['entailment_prob']}, C:{r['contradiction_prob']}, N:{r['neutral_prob']})")
    print(f"Elapsed: {(time.perf_counter() - t0) * 1000:.1f}ms")
