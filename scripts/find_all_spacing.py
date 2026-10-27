import docx

for path in [r"docs\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx", r"docs\ADA23DLU04_PROJECT_REPORT_FORMATTED.docx"]:
    print("=" * 60)
    print("Checking:", path)
    doc = docx.Document(path)
    found = 0
    for i, p in enumerate(doc.paragraphs):
        t = p.text
        issues = []
        if "  " in t:
            issues.append(f"multiple spaces ({t.count('  ')})")
        if "\t" in t:
            issues.append("tabs")
        if "\xa0" in t:
            issues.append("nbsp")
        if "\n" in t:
            issues.append(f"newlines ({t.count(chr(10))})")
        if p.alignment == docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY and len(t.strip()) < 80 and len(t.strip()) > 0:
            issues.append(f"justified short text (len={len(t.strip())})")
        if issues:
            found += 1
            print(f"P{i:03d} [align={p.alignment}]: {issues} | text: {repr(t[:65])}")
    print(f"Total paragraphs with potential spacing flags: {found}")
