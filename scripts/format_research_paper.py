"""
TruthGuard Master Academic Document Formatter
Systematically inspects and formats ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx
into ADA23DLU04_PROJECT_REPORT_FORMATTED.docx.
"""
import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color="F1F5F9"):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_styling(table):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    for r_idx, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if r_idx == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            if r_idx == 0:
                set_cell_background(cell, "F1F5F9")
            
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    if r_idx == 0:
                        run.bold = True
                        run.font.size = Pt(10)
                        run.font.color.rgb = RGBColor(15, 23, 42)
                    else:
                        run.font.size = Pt(9.5)
                        run.font.color.rgb = RGBColor(30, 41, 59)

def format_all_tables(doc):
    print(f"Formatting {len(doc.tables)} tables...")
    for i, t in enumerate(doc.tables):
        set_table_styling(t)
    print("All tables successfully standardized with cantSplit, tblHeader, cell margins, and professional borders.")

if __name__ == "__main__":
    src_path = r"docs\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx"
    doc = docx.Document(src_path)
    format_all_tables(doc)
    doc.save(r"docs\test_tables_formatted.docx")
    print("Table formatting test complete.")
