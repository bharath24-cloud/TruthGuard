import json
import time
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1"

def run_e2e_validation():
    print("=" * 70)
    print("TRUTHGUARD END-TO-END VALIDATION & EXPERIMENTAL MEASUREMENT")
    print("=" * 70)

    # 1. Health Check
    t0 = time.time()
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print(f"[1/7] Health Check: OK ({time.time() - t0:.2f}s)")
    print(f"      Backend Version: {health['version']}")
    print(f"      Ollama Status: {health['ollama']['status']} ({health['ollama']['default_model']})")
    print(f"      NLI Model: {health['models']['nli_model']}")
    print(f"      Embedding Model: {health['models']['embedding_model']}")

    # 2. Document Ingestion
    doc_path = Path("marie_curie_test.txt")
    doc_content = """Marie Sklodowska Curie was a Polish and naturalized-French physicist and chemist.
In 1898, Marie and her husband Pierre Curie discovered the radioactive elements polonium and radium.
Marie Curie was awarded two Nobel Prizes: the 1903 Nobel Prize in Physics and the 1911 Nobel Prize in Chemistry.
She was born in Warsaw, Poland on 7 November 1867 and died in 1934 in France."""
    doc_path.write_text(doc_content, encoding="utf-8")

    t0 = time.time()
    with open(doc_path, "rb") as f:
        upload_res = requests.post(f"{BASE_URL}/documents/upload", files={"file": ("marie_curie_reference.txt", f)})
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    doc_info = upload_res.json()
    print(f"\n[2/7] Document Ingestion: OK ({time.time() - t0:.2f}s)")
    print(f"      Document ID: {doc_info['document']['id']}")
    print(f"      Passages Chunked & Indexed in FAISS: {doc_info['chunks_created']}")

    # 3. Verification of Hallucinated vs Faithful Answer
    # Answer contains:
    # 1. Marie Curie discovered radium in 1898. (FAITHFUL / SUPPORTED)
    # 2. Marie Curie won five Nobel Prizes. (CONTRADICTION / HALLUCINATED)
    # 3. She was the greatest human ever born. (SUBJECTIVE / UNVERIFIABLE)
    test_question = "What elements did Marie Curie discover and how many Nobel Prizes did she win?"
    test_answer = "Marie Curie discovered radium in 1898 and won five Nobel Prizes. She was the greatest human ever born."

    print(f"\n[3/7] Verifying Test Answer...")
    print(f"      Question: \"{test_question}\"")
    print(f"      Answer to Verify: \"{test_answer}\"")

    t0 = time.time()
    verify_payload = {
        "question": test_question,
        "answer": test_answer,
        "model_name": "qwen3:8b",
        "top_k": 3
    }
    verify_res = requests.post(f"{BASE_URL}/verify", json=verify_payload)
    assert verify_res.status_code == 200, f"Verification failed: {verify_res.text}"
    report = verify_res.json()
    verification_latency = time.time() - t0

    print(f"      Verification Completed in {verification_latency:.2f}s (API report latency: {report['latency_ms']}ms)")
    print(f"      Total Claims Extracted: {report['total_claims']}")
    print(f"      Supported Claims: {report['supported_claims']}")
    print(f"      Contradicted Claims: {report['contradicted_claims']}")
    print(f"      Unverified Claims: {report['insufficient_claims']}")
    print(f"      Hallucination Score: {report['hallucination_score'] * 100:.1f}%")
    print(f"      Contradiction Rate: {report['contradiction_rate'] * 100:.1f}%")

    print("\n[4/7] Claim-Level Inference Verdicts:")
    for c in report["claims"]:
        print(f"      [{c['claim_id']}] \"{c['normalized_claim']}\"")
        conf_str = f"{c['confidence'] * 100:.1f}%" if c['confidence'] is not None else "N/A (No Evidence / Subjective)"
        print(f"           Verdict: {c['verdict']} (Confidence: {conf_str})")
        print(f"           Rationale: {c['explanation']}")
        if c["evidence_list"]:
            top_ev = c["evidence_list"][0]
            print(f"           Top Evidence: \"{top_ev['passage_text'][:80]}...\" (NLI: {top_ev['nli_label']})")

    # 5. Evidence-Grounded Correction & Reverification
    print(f"\n[5/7] Running Evidence-Grounded Correction Engine...")
    t0 = time.time()
    correct_payload = {
        "verification_id": report["id"],
        "model_name": "qwen3:8b"
    }
    correct_res = requests.post(f"{BASE_URL}/correct", json=correct_payload)
    assert correct_res.status_code == 200, f"Correction failed: {correct_res.text}"
    correction = correct_res.json()
    correction_latency = time.time() - t0

    print(f"      Correction Completed in {correction_latency:.2f}s")
    print(f"      Original Answer: \"{correction['original_answer']}\"")
    print(f"      Corrected Answer: \"{correction['corrected_answer']}\"")
    print(f"      Claims Corrected: {correction['claims_corrected']}")
    print(f"      Is Fully Supported: {correction['is_fully_supported']}")
    print(f"      Newly Introduced Unsupported Claims: {correction['newly_introduced_unsupported']}")
    print(f"      Audit Summary: {correction['explanation']}")

    # 6. Evaluation Lab Benchmark (FEVER)
    print(f"\n[6/7] Running Empirical Benchmark on FEVER Dataset...")
    t0 = time.time()
    eval_payload = {
        "benchmark_name": "FEVER",
        "sample_size": 10,
        "top_k": 3
    }
    eval_res = requests.post(f"{BASE_URL}/evaluations/run", json=eval_payload)
    assert eval_res.status_code == 200, f"Evaluation failed: {eval_res.text}"
    exp = eval_res.json()
    eval_latency = time.time() - t0

    print(f"      FEVER Benchmark Completed in {eval_latency:.2f}s")
    print(f"      Accuracy: {exp['accuracy'] * 100:.1f}%")
    print(f"      Precision: {exp['precision'] * 100:.1f}%")
    print(f"      Recall: {exp['recall'] * 100:.1f}%")
    print(f"      Macro F1: {exp['f1_score'] * 100:.1f}%")
    print(f"      Retrieval Recall@K: {exp['retrieval_recall_at_k'] * 100:.1f}%")
    print(f"      Confusion Matrix:")
    print(f"      {json.dumps(exp['confusion_matrix'], indent=6)}")

    # 7. Verification History Persistence Check
    print(f"\n[7/7] Checking Persistence & Retrieval from History...")
    history_res = requests.get(f"{BASE_URL}/verifications")
    assert history_res.status_code == 200
    all_runs = history_res.json()
    print(f"      Retrieved {len(all_runs)} historical run(s) from SQLite database.")

    # Clean up test file
    if doc_path.exists():
        doc_path.unlink()

    # Save validation report
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "health": health,
        "verification_run": report,
        "correction_run": correction,
        "evaluation_experiment": exp,
        "history_count": len(all_runs)
    }
    Path("experiments/validation_run_report.json").write_text(
        json.dumps(report_data, indent=2), encoding="utf-8"
    )
    print("\n" + "=" * 70)
    print("SUCCESS: ALL 7 VALIDATION PHASES COMPLETED AND VERIFIED!")
    print("Experimental results persisted to experiments/validation_run_report.json")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_validation()
