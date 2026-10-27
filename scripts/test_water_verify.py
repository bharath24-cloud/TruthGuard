import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.database.database import SessionLocal
from backend.app.services.verification_service import verification_service

db = SessionLocal()
try:
    print("Running verification on water answer with a.txt in index...")
    q = "What is water composed of?"
    a = "Water is a chemical compound with the formula H2O. Each water molecule contains two hydrogen atoms and one oxygen atom."
    report = verification_service.run_verification(
        db=db,
        question=q,
        answer=a,
        evidence_source="documents",
        top_k=5
    )
    print(f"Total claims: {report.total_claims}")
    print(f"Supported claims: {report.supported_claims}")
    print(f"Contradicted claims: {report.contradicted_claims}")
    print(f"Insufficient claims: {report.insufficient_claims}")
    for c in report.claims:
        print(f"[{c.claim_id}] {c.normalized_claim} -> Verdict: {c.verdict} (Conf: {c.confidence}) Reason: {c.inference_reason}")
        for ev in c.evidence_list:
            print(f"   Ev: {ev.document_name} (Sim: {ev.similarity_score}, NLI: {ev.nli_label}, Ent: {ev.entailment_prob})")
finally:
    db.close()
