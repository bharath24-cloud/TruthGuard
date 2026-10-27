import docx
import re

doc = docx.Document(r"docs\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx")

issues = []

print(f"Total Paragraphs: {len(doc.paragraphs)}")
print(f"Total Tables: {len(doc.tables)}")

for idx, p in enumerate(doc.paragraphs):
    text = p.text
    # 1. Blank paragraphs
    if len(text.strip()) == 0:
        # Check if it has drawing
        drawings = p._element.xpath(".//w:drawing")
        if not drawings:
            issues.append((idx, "BLANK_PARAGRAPH", "Empty paragraph used for spacing", ""))
        continue

    # 2. Encoding artifacts (like replacement char \ufffd or )
    if "" in text or "\ufffd" in text:
        issues.append((idx, "ENCODING_ARTIFACT", "Contains broken character '' or replacement character", text[:80]))

    # 3. Multiple consecutive spaces
    if re.search(r"[^\S\r\n]{2,}", text):
        matches = re.findall(r"[^\S\r\n]{2,}", text)
        issues.append((idx, "MULTIPLE_SPACES", f"Contains {len(matches)} occurrences of 2+ consecutive spaces", text[:80]))

    # 4. Embedded manual line breaks (\n, \r, \x0b) inside normal body paragraphs
    if "\n" in text or "\r" in text or "\x0b" in text:
        # Check if heading or code block
        is_heading = text.startswith("CHAPTER") or text.startswith("TRUTHGUARD:")
        if not is_heading:
            issues.append((idx, "MANUAL_LINEBREAK", "Contains embedded manual newline / line break inside paragraph causing stretched justification", text[:80]))

    # 5. Inconsistent alignment
    align_str = str(p.alignment)
    # Check if heading
    is_ch = re.match(r"^CHAPTER\s+\d+", text)
    is_sec = re.match(r"^\d+\.\d+", text)
    is_front = text in ["ABSTRACT", "ACKNOWLEDGEMENT", "BONAFIDE CERTIFICATE", "TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES", "LIST OF SYMBOLS AND ABBREVIATIONS", "REFERENCES"]
    is_caption = text.startswith("Figure ") or text.startswith("Table ")
    
    if is_ch or is_front:
        if p.alignment != docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER:
            issues.append((idx, "HEADING_ALIGNMENT", f"Major heading has alignment {align_str} instead of CENTER", text[:60]))
    elif is_sec:
        if p.alignment != docx.enum.text.WD_ALIGN_PARAGRAPH.LEFT and p.alignment is not None:
            issues.append((idx, "SECTION_ALIGNMENT", f"Section heading has alignment {align_str} instead of LEFT", text[:60]))
    elif is_caption:
        if p.alignment != docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER:
            issues.append((idx, "CAPTION_ALIGNMENT", f"Caption has alignment {align_str} instead of CENTER", text[:60]))
    else:
        # Body paragraph
        if len(text) > 100:
            if p.alignment != docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY:
                issues.append((idx, "BODY_ALIGNMENT", f"Body paragraph has alignment {align_str} instead of JUSTIFY", text[:80]))

    # 6. Inconsistent fonts or font sizes across runs
    fonts = set()
    sizes = set()
    for r in p.runs:
        if r.text.strip():
            if r.font and r.font.name:
                fonts.add(r.font.name)
            if r.font and r.font.size:
                sizes.add(r.font.size.pt)
    if len(fonts) > 1:
        issues.append((idx, "MIXED_FONTS", f"Mixed font families in single paragraph: {fonts}", text[:60]))
    if len(sizes) > 1:
        issues.append((idx, "MIXED_SIZES", f"Mixed font sizes in single paragraph: {sizes}", text[:60]))

    # 7. Broken equations or unformatted raw math formulas
    if (" = " in text or " / " in text or "R_contra" in text or "P(label" in text or "sim(q" in text) and len(text) > 50:
        if not text.startswith("Table") and not text.startswith("Figure"):
            issues.append((idx, "RAW_EQUATION_IN_PROSE", "Inline raw mathematical formulas embedded in prose needing standard formatting", text[:80]))

print(f"\nTotal Identified Issues: {len(issues)}")
for idx, cat, desc, sample in issues:
    print(f"P{idx:03d} | [{cat:22s}] {desc} | sample: '{sample}'")
