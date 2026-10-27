# TruthGuard: Research Evaluation & Benchmark Methodology

## 1. Benchmark Datasets
TruthGuard integrates normalized evaluation splits from three established NLP benchmarks:

1. **FEVER (Fact Extraction and VERification):**
   - Focus: Sentence-level claims paired with Wikipedia evidence passages.
   - Ground Truth Labels: `SUPPORTS` (Supported), `REFUTES` (Contradicted), `NOT ENOUGH INFO` (Insufficient Evidence).
2. **HaluEval (Hallucination Evaluation for Large Language Models):**
   - Focus: Question answering and summary generation pairs labeled as `faithful` vs `hallucinated`.
3. **TruthfulQA:**
   - Focus: Testing resistance to prevalent human misconceptions and falsehoods across health, law, science, and history.

---

## 2. Experimental Results Actually Obtained

The following results were measured during automated execution on local hardware:

| Benchmark | Sample Size | Accuracy | Precision | Recall | Macro F1 | Recall@K | Latency / Sample |
|---|---|---|---|---|---|---|---|
| **FEVER** | 10 pairs | **90.0%** | **90.0%** | **91.7%** | **89.9%** | **100.0%** | 231 ms |
| **Warm Verification Query** | 1 multi-claim answer | — | — | — | — | — | **550 ms** |

### Confusion Matrix (FEVER Evaluation Run):
```
Actual \ Predicted   | Contradicted | Supported
------------------------------------------------
Contradicted         |      4       |     0
Supported            |      1       |     5
```
- **False Negative Rate:** 0.0% on refutations (all 4 refuted claims correctly flagged).
- **Retrieval Recall@3:** 100% of ground-truth evidence passages retrieved within top-3 candidates.
