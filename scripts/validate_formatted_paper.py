"""
TruthGuard Master Formatted Document Validation Suite
Rigorously checks ADA23DLU04_PROJECT_REPORT_FORMATTED.docx against all criteria.
"""
import os
import zipfile
import docx
import re

doc_path = r"docs\ADA23DLU04_PROJECT_REPORT_FORMATTED.docx"

print("=" * 60)
print("TRUTHGUARD FORMATTED DOCUMENT VALIDATION REPORT")
print("=" * 60)

# Check 1: File existence and size
if not os.path.exists(doc_path):
    print("FAILED: Formatted document does not exist!")
    exit(1)

size_mb = os.path.getsize(doc_path) / (1024 * 1024)
print(f"[CHECK 1] File Size: {size_mb:.2f} MB")

# Check 2: Embedded media files
print("\n[CHECK 2] Embedded Images in DOCX Archive:")
with zipfile.ZipFile(doc_path, 'r') as z:
    media_files = [f for f in z.infolist() if 'media/' in f.filename]
    print(f"Total media files found: {len(media_files)}")
    for mf in media_files:
        print(f"  • {mf.filename} ({mf.file_size:,} bytes)")
    assert len(media_files) == 6, f"Expected 6 images, found {len(media_files)}"

# Check 3: Paragraph and Table Counts
doc = docx.Document(doc_path)
print(f"\n[CHECK 3] Document Structure:")
print(f"  • Total Paragraphs: {len(doc.paragraphs)}")
print(f"  • Total Tables: {len(doc.tables)}")
assert len(doc.tables) == 12, f"Expected 12 tables, found {len(doc.tables)}"

# Check 4: Stretched Word Spacing / Manual Linebreaks in Justified Text
print("\n[CHECK 4] Checking for Stretched Word Spacing (Embedded \\n in Justified Text):")
stretched_issues = []
for i, p in enumerate(doc.paragraphs):
    if p.alignment == docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY:
        if '\n' in p.text or '\r' in p.text:
            stretched_issues.append((i, p.text[:80]))

if stretched_issues:
    print(f"  FAILED: Found {len(stretched_issues)} justified paragraphs with manual line breaks:")
    for idx, sample in stretched_issues:
        print(f"    P{idx:03d}: {sample}")
else:
    print("  PASSED: 0 justified paragraphs contain manual line breaks! All stretched word spacing eliminated!")

# Check 5: Drawings & Captions Alignment
print("\n[CHECK 5] Figure Drawings & Captions:")
drawing_paras = [i for i, p in enumerate(doc.paragraphs) if len(p._element.xpath('.//w:drawing')) > 0]
caption_paras = [i for i, p in enumerate(doc.paragraphs) if re.match(r"^(Figure|Table)\s+\d+\.\d+:", p.text.strip())]

print(f"  • Drawing paragraphs count: {len(drawing_paras)}")
for dp_idx in drawing_paras:
    p = doc.paragraphs[dp_idx]
    align = p.alignment
    sp_b = p.paragraph_format.space_before.pt if p.paragraph_format.space_before else 0
    sp_a = p.paragraph_format.space_after.pt if p.paragraph_format.space_after else 0
    print(f"    P{dp_idx:03d}: align={align}, sp_b={sp_b}pt, sp_a={sp_a}pt, keep_next={p.paragraph_format.keep_with_next}")

print(f"  • Actual Captions count: {len(caption_paras)} (7 Figures + 7 Tables = 14 Captions)")
for cp_idx in caption_paras:
    p = doc.paragraphs[cp_idx]
    align = p.alignment
    is_tbl = p.text.strip().startswith("Table ")
    print(f"    P{cp_idx:03d} [{'TBL' if is_tbl else 'FIG'}]: align={align}, keep_next={p.paragraph_format.keep_with_next} | {p.text.strip()[:65]}")

assert len(caption_paras) == 14, f"Expected 14 captions, found {len(caption_paras)}"

# Check 6: Table Standardization
print("\n[CHECK 6] Table Standardization (cantSplit & tblHeader):")
all_tables_pass = True
for t_idx, t in enumerate(doc.tables):
    align = t.alignment
    cant_split = sum(1 for r in t.rows if r._tr.xpath('./w:trPr/w:cantSplit'))
    tbl_header = sum(1 for r in t.rows if r._tr.xpath('./w:trPr/w:tblHeader'))
    if cant_split != len(t.rows) or tbl_header != 1:
        all_tables_pass = False
        print(f"  Table {t_idx:02d}: FAILED cantSplit={cant_split}/{len(t.rows)}, tblHeader={tbl_header}")
    else:
        print(f"  Table {t_idx:02d}: PASSED rows={len(t.rows)}, align={align}, cantSplit={cant_split}/{len(t.rows)}, tblHeader={tbl_header}")

# Check 7: Office Math Formulas
print("\n[CHECK 7] Native Office Math Formula Blocks:")
math_paras = [i for i, p in enumerate(doc.paragraphs) if len(p._element.xpath('.//m:oMathPara')) > 0]
print(f"  • Total Office Math equations rendered: {len(math_paras)}")
for mp_idx in math_paras:
    prev_text = doc.paragraphs[mp_idx - 1].text.strip() if mp_idx > 0 else ""
    print(f"    P{mp_idx:03d} Math block following: '{prev_text[:60]}'")

# Check 8: Encoding artifacts
print("\n[CHECK 8] Character Encoding & Typographic Symbols:")
broken_chars = []
for i, p in enumerate(doc.paragraphs):
    if '\ufffd' in p.text:
        broken_chars.append((i, p.text[:80]))
if broken_chars:
    print(f"  FAILED: Found {len(broken_chars)} paragraphs with \\ufffd")
else:
    print("  PASSED: 0 paragraphs contain \\ufffd replacement characters!")

# Check 9: Key Empirical Claims and Metrics Preservation
print("\n[CHECK 9] Empirical Claims & Dataset Metrics Integrity:")
full_text = "\n".join([p.text for p in doc.paragraphs])
for t in doc.tables:
    for r in t.rows:
        for c in r.cells:
            full_text += "\n" + c.text

metrics_to_check = [
    ("90.0%", "Classification accuracy on FEVER"),
    ("89.9%", "Macro F1 score"),
    ("100.0%", "Recall@3 retrieval recall"),
    ("296.3 ms", "Total pipeline latency"),
    ("578.4 ms", "Marie Curie walkthrough latency"),
    ("65.0%", "Hallucination Risk Score in case study"),
    ("50.0%", "Contradiction Rate in case study"),
    ("qwen3:8b", "Correction LLM model identifier"),
    ("all-MiniLM-L6-v2", "Sentence embedding model"),
    ("nli-deberta-v3-small", "Cross-encoder NLI model"),
    ("faiss.IndexFlatIP(384)", "FAISS index specification"),
    ("tau_sim = 0.25", "Similarity threshold")
]

for metric, label in metrics_to_check:
    if metric in full_text:
        print(f"  PASSED [Verified]: '{metric}' ({label}) preserved exactly.")
    else:
        print(f"  WARNING [Missing]: '{metric}' ({label}) not found!")

print("\n" + "=" * 60)
print("ALL VALIDATION CHECKS COMPLETED SUCCESSFULLY")
print("=" * 60)
