import docx

doc = docx.Document(r"docs\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx")

with open(r"docs\paragraphs_dump.txt", "w", encoding="utf-8") as f:
    for idx, p in enumerate(doc.paragraphs):
        drawings = len(p._element.xpath(".//w:drawing"))
        text = p.text
        f.write(f"--- P{idx:03d} | align={p.alignment} | drawings={drawings} | len={len(text)} ---\n")
        f.write(f"Text: {text}\n")
        runs_desc = []
        for r_idx, r in enumerate(p.runs):
            r_drawings = len(r._element.xpath(".//w:drawing"))
            fn = r.font.name if r.font else None
            fs = r.font.size.pt if (r.font and r.font.size) else None
            runs_desc.append(f"R{r_idx}(draw={r_drawings},fn={fn},fs={fs},b={r.bold},i={r.italic})")
        f.write(f"Runs: {', '.join(runs_desc)}\n\n")

print("Dumped all paragraphs to docs/paragraphs_dump.txt")
