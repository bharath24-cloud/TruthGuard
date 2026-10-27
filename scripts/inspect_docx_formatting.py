import docx

doc = docx.Document(r"docs\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx")
p149 = doc.paragraphs[149]
print("P149 runs count:", len(p149.runs))
for r_idx, r in enumerate(p149.runs):
    print(f"Run {r_idx}: text='{r.text}' | xml={r._element.xml[:100]}")
