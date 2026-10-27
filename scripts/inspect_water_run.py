import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('data/truthguard.db')
cur = conn.cursor()
cur.execute("SELECT id, question, original_answer, evidence_source FROM verification_runs WHERE id = 'e33ccf3a-83a3-44ee-ad90-7269cf341a65'")
row = cur.fetchone()
if row:
    print(f"Run ID: {row[0]}")
    print(f"Question: {row[1]}")
    print(f"Original Answer:\n{row[2]}")
    print(f"Evidence Source: {row[3]}")
    
    cur.execute("SELECT claim_id, normalized_claim, verdict, confidence, inference_reason FROM extracted_claims WHERE verification_id = 'e33ccf3a-83a3-44ee-ad90-7269cf341a65'")
    claims = cur.fetchall()
    print(f"\nExtracted Claims ({len(claims)}):")
    for c in claims:
        print(f"  [{c[0]}] {c[1]}")
        print(f"      Verdict: {c[2]} | Conf: {c[3]} | Reason: {c[4]}")
        cur.execute("SELECT chunk_id, document_name, similarity_score, nli_label, entailment_prob, contradiction_prob, neutral_prob, passage_text FROM claim_evidence WHERE claim_id = (SELECT id FROM extracted_claims WHERE verification_id = 'e33ccf3a-83a3-44ee-ad90-7269cf341a65' AND claim_id = ?)", (c[0],))
        evs = cur.fetchall()
        print(f"      Evidences matched: {len(evs)}")
        for ev in evs:
            print(f"        Doc: {ev[1]} (Sim: {ev[2]}) -> NLI: {ev[3]} (E:{ev[4]}, C:{ev[5]}, N:{ev[6]})")
            print(f"        Passage: {repr(ev[7][:80])}")

print("\n--- All other water runs ---")
cur.execute("SELECT id, question, evidence_source, total_claims, supported_claims, contradicted_claims, insufficient_claims FROM verification_runs WHERE question LIKE '%water%' OR original_answer LIKE '%water%'")
for r in cur.fetchall():
    print(r)
