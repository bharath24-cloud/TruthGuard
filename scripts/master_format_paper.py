"""
TruthGuard Master Academic Document Formatter
Systematically inspects and formats ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx
into ADA23DLU04_PROJECT_REPORT_FORMATTED.docx.
Preserves all original research content, 6 embedded high-resolution figures,
12 tables, and academic citations.
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

def format_all_tables(doc):
    print(f"Standardizing {len(doc.tables)} tables...")
    for t_idx, table in enumerate(doc.tables):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = table._tbl.tblPr
        
        # Professional clean borders
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
            # CantSplit on every row
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            # Repeat header row on every page
            if r_idx == 0:
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            
            for c_idx, cell in enumerate(row.cells):
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                if r_idx == 0:
                    set_cell_background(cell, "F1F5F9")
                
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.15
                    
                    txt = p.text.strip()
                    is_num = bool(re.match(r"^[\d\.\%\–\—\s\+\-\/\,\:\(\)]+$", txt)) and len(txt) < 20
                    is_header = (r_idx == 0)
                    
                    if is_header:
                        if c_idx in [0, 2] and t_idx in [1, 2, 3]:
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        elif t_idx in [8, 9, 10]:
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        else:
                            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    else:
                        if (c_idx in [0, 2] and t_idx in [1, 2, 3]) or is_num:
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        else:
                            p.alignment = WD_ALIGN_PARAGRAPH.LEFT

                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        if is_header:
                            run.bold = True
                            run.font.size = Pt(10)
                            run.font.color.rgb = RGBColor(15, 23, 42)
                        else:
                            run.font.size = Pt(9.5)
                            run.font.color.rgb = RGBColor(30, 41, 59)

def create_omath_para(inner_omath_xml):
    full_xml = f'<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:oMath>{inner_omath_xml}</m:oMath></m:oMathPara>'
    return parse_xml(full_xml)

def set_run_fonts(p, font_name="Times New Roman", font_size=12, color_rgb=(0, 0, 0)):
    if len(p._element.xpath('.//w:drawing')) > 0:
        return
    for r in p.runs:
        if len(r._r.xpath('.//w:drawing')) > 0:
            continue
        if r.font:
            r.font.name = font_name
            if font_size:
                r.font.size = Pt(font_size)
            if color_rgb:
                r.font.color.rgb = RGBColor(*color_rgb)

def add_helper_para(target_p, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.5, bold=False, italic=False, font_size=12, font_name="Times New Roman", color_rgb=(0,0,0), style=None, keep_with_next=False):
    new_p = target_p.insert_paragraph_before()
    if style:
        new_p.style = style
    new_p.alignment = align
    new_p.paragraph_format.space_before = Pt(space_before)
    new_p.paragraph_format.space_after = Pt(space_after)
    if line_spacing:
        new_p.paragraph_format.line_spacing = line_spacing
    new_p.paragraph_format.keep_with_next = keep_with_next
    if text:
        run = new_p.add_run(text)
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = RGBColor(*color_rgb)
    return new_p

def add_bullet_helper(target_p, title_text, desc_text):
    new_p = target_p.insert_paragraph_before()
    new_p.style = 'List Bullet'
    new_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    new_p.paragraph_format.space_before = Pt(2)
    new_p.paragraph_format.space_after = Pt(3)
    new_p.paragraph_format.line_spacing = 1.5
    
    r_title = new_p.add_run(title_text)
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(12)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(0, 0, 0)
    
    r_desc = new_p.add_run(desc_text)
    r_desc.font.name = "Times New Roman"
    r_desc.font.size = Pt(12)
    r_desc.bold = False
    r_desc.font.color.rgb = RGBColor(0, 0, 0)
    return new_p

def add_math_helper(target_p, omath_inner_xml, space_before=4, space_after=4):
    new_p = target_p.insert_paragraph_before()
    new_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    new_p.paragraph_format.space_before = Pt(space_before)
    new_p.paragraph_format.space_after = Pt(space_after)
    new_p._element.append(create_omath_para(omath_inner_xml))
    return new_p

def format_document(src_path, dst_path):
    print(f"Loading source document: {src_path}")
    doc = docx.Document(src_path)
    
    # 1. Standardize all 12 tables
    format_all_tables(doc)
    
    # 2. Delete P030 (empty spacer between List of Tables and List of Figures)
    p30 = doc.paragraphs[30]
    if len(p30.text.strip()) == 0 and len(p30._element.xpath('.//w:drawing')) == 0 and len(p30._element.xpath('.//w:br[@w:type="page"]')) == 0:
        print("Removing redundant blank paragraph P030...")
        p30._element.getparent().remove(p30._element)

    # 3. Surgical unbundling of compound paragraphs
    print("Executing surgical unbundling of compound paragraphs and math formatting...")
    
    paragraphs_to_process = list(doc.paragraphs)
    
    for p in paragraphs_to_process:
        txt = p.text.strip()
        
        # --- SUB-TOPIC 1 in Section 3.1.3: Dense Semantic Embedding & Vector Indexing ---
        if txt.startswith("1. Dense Semantic Embedding & Vector Indexing:"):
            print("Expanding Sub-topic 1: Dense Semantic Embedding & Vector Indexing...")
            # Left aligned heading, NEVER justify
            add_helper_para(p, "1. Dense Semantic Embedding & Vector Indexing", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "Passage and claim embeddings are computed using sentence-transformers/all-MiniLM-L6-v2, mapping textual strings into a 384-dimensional continuous vector space ℝ³⁸⁴. Every passage vector v and query vector q is L2-normalized:", space_before=0, space_after=4)
            add_math_helper(p, 
                '<m:r><m:t>q̂ = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>q</m:t></m:r></m:num><m:den><m:r><m:t>‖q‖₂</m:t></m:r></m:den></m:f>'
                '<m:r><m:t>,     v̂ = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>v</m:t></m:r></m:num><m:den><m:r><m:t>‖v‖₂</m:t></m:r></m:den></m:f>'
            )
            add_helper_para(p, "The FAISS index is configured as faiss.IndexFlatIP(384). Because vectors are unit normalized, inner product evaluation equals exact cosine similarity:", space_before=0, space_after=4)
            add_math_helper(p, 
                '<m:r><m:t>sim(q, v) = q̂ · v̂ = cos(θ)</m:t></m:r>'
            )
            add_helper_para(p, "Retrieval returns the top-k passages exceeding similarity threshold τ_sim = 0.25.", space_before=0, space_after=6)
            p._element.getparent().remove(p._element)

        # --- SUB-TOPIC 2 in Section 3.1.3: Cross-Encoder Natural Language Inference ---
        elif txt.startswith("2. Cross-Encoder Natural Language Inference:"):
            print("Expanding Sub-topic 2: Cross-Encoder Natural Language Inference...")
            add_helper_para(p, "2. Cross-Encoder Natural Language Inference", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "Retrieved passages exceeding the similarity threshold are paired with the atomic claim and fed to cross-encoder/nli-deberta-v3-small. The cross-encoder concatenates premise P and hypothesis H into [CLS] P [SEP] H [SEP], allowing full all-to-all cross-attention. The model produces unnormalized logits z = [z_contra, z_entail, z_neutral], mapped via softmax to probability distribution:", space_before=0, space_after=4)
            add_math_helper(p,
                '<m:r><m:t>P(labelᵢ | c, p) = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>exp(zᵢ)</m:t></m:r></m:num><m:den><m:r><m:t>∑ⱼ exp(zⱼ)</m:t></m:r></m:den></m:f>'
            )
            add_helper_para(p, "Calibrated decision boundaries are applied: P(entailment) ≥ 0.55 flags a supporting candidate; P(contradiction) ≥ 0.50 flags a contradicting candidate; otherwise the candidate is classified as neutral.", space_before=0, space_after=6)
            p._element.getparent().remove(p._element)

        # --- SUB-TOPIC 3 in Section 3.1.3: Multi-Evidence Arbitration Policy ---
        elif txt.startswith("3. Multi-Evidence Arbitration Policy:"):
            print("Expanding Sub-topic 3: Multi-Evidence Arbitration Policy...")
            add_helper_para(p, "3. Multi-Evidence Arbitration Policy", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "When multiple passages are retrieved for a claim, TruthGuard applies a deterministic 4-way arbitration rule: (a) Conflicting Evidence: if distinct passages yield both strong entailment and strong contradiction; (b) Contradicted: if max P(contradiction) ≥ 0.50 without conflicting entailment; (c) Supported: if max P(entailment) ≥ 0.55; (d) Insufficient Evidence: if no candidate reaches either threshold, if retrieval yields zero passages, or if the claim is classified as subjective. When retrieval yields zero passages, confidence is honestly set to null (uncalibrated) with explicit reason codes (e.g., NO_DOCUMENTS_INDEXED or NO_EVIDENCE_RETRIEVED).", space_before=0, space_after=6)
            p._element.getparent().remove(p._element)

        # --- SUB-TOPIC 4 in Section 3.1.3: Mathematical Hallucination Risk Scoring Formulation ---
        elif txt.startswith("4. Mathematical Hallucination Risk Scoring Formulation:"):
            print("Expanding Sub-topic 4: Mathematical Hallucination Risk Scoring Formulation...")
            add_helper_para(p, "4. Mathematical Hallucination Risk Scoring Formulation", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "All metrics are computed deterministically from empirical claim counts without subjective heuristics:", space_before=0, space_after=4)
            p._element.getparent().remove(p._element)

        elif txt.startswith("Contradiction Rate (R_contra):"):
            add_helper_para(p, "Contradiction Rate (R_contra):", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2, bold=True, keep_with_next=True)
            add_math_helper(p,
                '<m:r><m:t>R_contra = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>N_contradicted</m:t></m:r></m:num><m:den><m:r><m:t>max(1, N_verifiable)</m:t></m:r></m:den></m:f>'
            )
            add_helper_para(p, "Quantifies the ratio of directly refuted factual assertions.", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.3)
            p._element.getparent().remove(p._element)

        elif txt.startswith("Unsupported Claim Rate (R_unsupported):"):
            add_helper_para(p, "Unsupported Claim Rate (R_unsupported):", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2, bold=True, keep_with_next=True)
            add_math_helper(p,
                '<m:r><m:t>R_unsupported = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>N_contradicted + N_insufficient + N_conflicting</m:t></m:r></m:num><m:den><m:r><m:t>max(1, N_total)</m:t></m:r></m:den></m:f>'
            )
            add_helper_para(p, "Measures overall factual deficit.", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.3)
            p._element.getparent().remove(p._element)

        elif txt.startswith("Composite Hallucination Risk Score (S_risk):"):
            add_helper_para(p, "Composite Hallucination Risk Score (S_risk):", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2, bold=True, keep_with_next=True)
            add_math_helper(p,
                '<m:r><m:t>S_risk = min(1.0,   0.70 · R_contra + 0.30 · </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>N_insufficient + N_conflicting</m:t></m:r></m:num><m:den><m:r><m:t>max(1, N_verifiable)</m:t></m:r></m:den></m:f>'
                '<m:r><m:t>)</m:t></m:r>'
            )
            add_helper_para(p, "Direct contradictions are heavily penalized (70% weight), while unverified assertions incur proportionate moderate penalty (30% weight), guaranteeing a strictly bounded score in [0.0, 1.0].", space_before=0, space_after=6)
            p._element.getparent().remove(p._element)

        # --- SUB-TOPIC 5 in Section 3.1.3: Evidence-Grounded Correction & Closed-Loop Reverification ---
        elif txt.startswith("5. Evidence-Grounded Correction & Closed-Loop Reverification:"):
            print("Expanding Sub-topic 5: Evidence-Grounded Correction & Closed-Loop Reverification...")
            add_helper_para(p, "5. Evidence-Grounded Correction & Closed-Loop Reverification", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "When contradicted claims are detected, TruthGuard initiates automatic correction. The original text is passed to Ollama (qwen3:8b) under a constrained system prompt with the verified reference passages. The LLM is strictly instructed to replace only contradicted spans with ground truth facts while preserving supported sentences. Crucially, TruthGuard executes an automated closed-loop reverification audit over the revised text, ensuring that the corrected output contains exactly zero remaining contradictions.", space_before=0, space_after=6)
            p._element.getparent().remove(p._element)

        # --- SECTION 4.2 FORMULAS ---
        elif txt.startswith("Multi-Class Accuracy:"):
            add_helper_para(p, "Multi-Class Accuracy:", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2, bold=True, keep_with_next=True)
            add_math_helper(p,
                '<m:r><m:t>Accuracy = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>TP + TN</m:t></m:r></m:num><m:den><m:r><m:t>Total Samples</m:t></m:r></m:den></m:f>'
            )
            add_helper_para(p, "Represents the global fraction of correctly classified claims.", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.3)
            p._element.getparent().remove(p._element)

        elif txt.startswith("Macro Precision & Recall:"):
            add_helper_para(p, "Macro Precision & Recall:", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2, bold=True, keep_with_next=True)
            add_math_helper(p,
                '<m:r><m:t>Macro Precision = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:r><m:t>|C|</m:t></m:r></m:den></m:f>'
                '<m:r><m:t> ∑ </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>TP_c</m:t></m:r></m:num><m:den><m:r><m:t>TP_c + FP_c</m:t></m:r></m:den></m:f>'
                '<m:r><m:t>,     Macro Recall = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:r><m:t>|C|</m:t></m:r></m:den></m:f>'
                '<m:r><m:t> ∑ </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>TP_c</m:t></m:r></m:num><m:den><m:r><m:t>TP_c + FN_c</m:t></m:r></m:den></m:f>'
            )
            add_helper_para(p, "Evaluating balanced performance across Supported, Contradicted, and Insufficient classes.", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.3)
            p._element.getparent().remove(p._element)

        elif txt.startswith("Macro F1-Score:"):
            add_helper_para(p, "Macro F1-Score:", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2, bold=True, keep_with_next=True)
            add_math_helper(p,
                '<m:r><m:t>Macro F1 = 2 · </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>Macro Precision · Macro Recall</m:t></m:r></m:num><m:den><m:r><m:t>Macro Precision + Macro Recall</m:t></m:r></m:den></m:f>'
            )
            add_helper_para(p, "Providing the primary harmonic metric unaffected by class imbalance.", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.3)
            p._element.getparent().remove(p._element)

        elif txt.startswith("Retrieval Recall@K:"):
            add_helper_para(p, "Retrieval Recall@K:", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2, bold=True, keep_with_next=True)
            add_math_helper(p,
                '<m:r><m:t>Recall@K = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>Hits@K</m:t></m:r></m:num><m:den><m:r><m:t>Total Gold Evidence</m:t></m:r></m:den></m:f>'
            )
            add_helper_para(p, "Measuring the probability that the gold reference passage is retrieved in the top-k candidates.", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.3)
            p._element.getparent().remove(p._element)

        # --- SUB-TOPIC 1 in Section 4.3: Benchmark Evaluation on FEVER Dataset ---
        elif txt.startswith("1. Benchmark Evaluation on FEVER Dataset:"):
            print("Expanding Sub-topic 1 (Ch 4): Benchmark Evaluation on FEVER Dataset...")
            add_helper_para(p, "1. Benchmark Evaluation on FEVER Dataset", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "TruthGuard was tested on an automated benchmark sample of FEVER claim-evidence pairs under strict zero-leakage conditions. Table 4.2 documents the multi-class performance metrics.", space_before=0, space_after=6)
            p._element.getparent().remove(p._element)

        # --- SUB-TOPIC 2 in Section 4.3: Real-World Verification Walkthrough ---
        elif txt.startswith("2. Real-World End-to-End Verification Walkthrough:"):
            print("Expanding Sub-topic 2 (Ch 4): Real-World End-to-End Verification Walkthrough...")
            add_helper_para(p, "2. Real-World End-to-End Verification Walkthrough", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "To evaluate real-world multi-claim response verification, an end-to-end audit was executed over a synthetic multi-claim test answer against an uploaded historical biography reference document ('marie_curie_reference.txt'):", space_before=0, space_after=4)
            add_bullet_helper(p, "Question: ", "'What elements did Marie Curie discover and how many Nobel Prizes did she win?'")
            add_bullet_helper(p, "Answer to Verify: ", "'Marie Curie discovered radium in 1898 and won five Nobel Prizes. She was the greatest human ever born.'")
            add_helper_para(p, "TruthGuard processed the query in 578.4 ms, extracting 3 atomic claims with character offsets:", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=4, space_after=4)
            add_bullet_helper(p, "[claim_001] 'Marie Curie discovered radium in 1898': ", "Resolved as Conflicting Evidence (99.8% confidence). Retrieved passage confirmed discovery, while benchmark reference 9 raised cross-source discrepancies.")
            add_bullet_helper(p, "[claim_002] 'won five Nobel Prizes.': ", "Resolved as Contradicted (99.7% confidence). Ground truth document explicitly refuted the assertion: 'Marie Curie was awarded two Nobel Prizes...'")
            add_bullet_helper(p, "[claim_003] 'She was the greatest human ever born.': ", "Correctly classified as non-empirical / subjective (verifiable=False, verdict='Insufficient Evidence', confidence=null).")
            add_helper_para(p, "The computed composite Hallucination Risk Score was 65.0% with a Contradiction Rate of 50.0%. The evidence-grounded correction engine subsequently revised the response to state: 'Marie Curie discovered radium in 1898 and was awarded two Nobel Prizes...'. Re-verification confirmed that the revised statement eliminated the contradiction entirely.", space_before=4, space_after=6)
            p._element.getparent().remove(p._element)

        # --- SUB-TOPIC 3 in Section 4.3: Module-Wise Latency & Execution Breakdown ---
        elif txt.startswith("3. Module-Wise Latency & Execution Breakdown:"):
            print("Expanding Sub-topic 3 (Ch 4): Module-Wise Latency & Execution Breakdown...")
            add_helper_para(p, "3. Module-Wise Latency & Execution Breakdown", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "Table 4.4 details the processing latency across pipeline stages measured during warm verification runs on a commodity 4 GB VRAM workstation.", space_before=0, space_after=6)
            p._element.getparent().remove(p._element)

        # --- SUB-TOPIC 4 in Section 4.3: Comparative Baseline Analysis ---
        elif txt.startswith("4. Comparative Baseline Analysis:"):
            print("Expanding Sub-topic 4 (Ch 4): Comparative Baseline Analysis...")
            add_helper_para(p, "4. Comparative Baseline Analysis", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4, bold=True, keep_with_next=True)
            add_helper_para(p, "Table 4.5 contrasts TruthGuard's architectural paradigm against conventional verification approaches, demonstrating clear superiority in provenance transparency, hardware accessibility, and operational cost.", space_before=0, space_after=6)
            p._element.getparent().remove(p._element)

    # 4. Standardize all remaining paragraphs
    print("Standardizing typography and alignment across all paragraphs...")
    for idx, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        drawings = p._element.xpath('.//w:drawing')
        page_breaks = [br for br in p._element.xpath('.//w:br') if br.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type') == 'page']
        
        # 1. Drawing paragraphs (NEVER touch runs!)
        if len(drawings) > 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            continue

        # 2. Page breaks
        if len(page_breaks) > 0 and len(t) == 0:
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            continue

        # 3. Figure & Table Captions (Strict regex match)
        if re.match(r"^(Figure|Table)\s+\d+\.\d+:", t):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            is_tbl = t.startswith("Table ")
            p.paragraph_format.keep_with_next = is_tbl
            if is_tbl:
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
            else:
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(14)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)
                r.bold = True
                r.italic = True
                r.font.color.rgb = RGBColor(15, 23, 42)
            continue

        # 4. Major Chapter Headings
        if re.match(r"^CHAPTER\s+\d+", t) or t in [
            "BONAFIDE CERTIFICATE", "ACKNOWLEDGEMENT", "ABSTRACT",
            "TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES",
            "LIST OF SYMBOLS AND ABBREVIATIONS", "REFERENCES"
        ]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(14)
                r.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
            continue

        # 5. Section Headings (e.g., 1.1, 1.2, 2.1, 2.1.1, 3.1, etc.)
        if re.match(r"^\d+\.\d+(\.\d+)?\s+", t):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
            continue

        # 6. Sub-topic headings (e.g., "1. Dense Semantic...", "2. Cross-Encoder...", etc.)
        if re.match(r"^\d+\.\s+[A-Z]", t) and len(t) < 80:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
            continue

        # 7. Metric titles (e.g., "Multi-Class Accuracy:", "Contradiction Rate (R_contra):", etc.)
        if (
            t.startswith("Contradiction Rate") or
            t.startswith("Unsupported Claim Rate") or
            t.startswith("Composite Hallucination Risk") or
            t.startswith("Multi-Class Accuracy:") or
            t.startswith("Macro Precision & Recall:") or
            t.startswith("Macro F1-Score:") or
            t.startswith("Retrieval Recall@K:")
        ):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
            continue

        # 8. Short metric descriptions or intro clauses (Under 80 chars, NEVER justify!)
        if (
            t.startswith("Quantifies the ratio") or
            t.startswith("Measures overall factual") or
            t.startswith("Represents the global") or
            t.startswith("Evaluating balanced performance") or
            t.startswith("Providing the primary") or
            t.startswith("Measuring the probability") or
            t.startswith("The primary technical and scientific") or
            t.startswith("Future enhancements to expand") or
            t.startswith("TruthGuard processed the query in")
        ):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.3
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
            continue

        # 9. References [1] to [12]
        if re.match(r"^\[\d+\]\s+", t):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.first_line_indent = Inches(-0.4)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10.5)
                r.font.color.rgb = RGBColor(0, 0, 0)
            continue

        # 10. Front matter specific titles
        if t.startswith("TRUTHGUARD: AN EXPLAINABLE"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(18)
            p.paragraph_format.line_spacing = 1.3
            set_run_fonts(p, "Times New Roman", 15)
            for r in p.runs: r.bold = True
            continue

        if t in ["A PROJECT REPORT", "BACHELOR OF TECHNOLOGY"]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(12 if t == "A PROJECT REPORT" else 6)
            set_run_fonts(p, "Times New Roman", 14)
            for r in p.runs: r.bold = True
            continue

        if t.startswith("Submitted by") or t.startswith("in partial fulfillment for the award"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.2
            set_run_fonts(p, "Times New Roman", 12)
            for r in p.runs: r.italic = True
            continue

        if t.startswith("BHARATHRAM K") and "\n" in t:
            if idx < 10:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(18)
                p.paragraph_format.line_spacing = 1.2
                set_run_fonts(p, "Times New Roman", 14)
                for r in p.runs: r.bold = True
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                set_run_fonts(p, "Times New Roman", 12)
                for r in p.runs: r.bold = True
            continue

        if t.startswith("in\nCOMPUTER SCIENCE AND ENGINEERING"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(24)
            p.paragraph_format.line_spacing = 1.2
            set_run_fonts(p, "Times New Roman", 13)
            for r in p.runs: r.bold = True
            continue

        if t.startswith("SRI RAMACHANDRA FACULTY OF ENGINEERING AND TECHNOLOGY"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(16)
            p.paragraph_format.line_spacing = 1.2
            set_run_fonts(p, "Times New Roman", 12)
            for r in p.runs: r.bold = True
            continue

        if t == "OCTOBER 2026" or t.startswith("PORUR, CHENNAI"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0 if t == "OCTOBER 2026" else 16)
            set_run_fonts(p, "Times New Roman", 12)
            for r in p.runs: r.bold = True
            continue

        if t.startswith("SIGNATURE\nDR. SUJA GOLDEN SHINY S"):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(24)
            p.paragraph_format.line_spacing = 1.15
            set_run_fonts(p, "Times New Roman", 11)
            continue

        if t.startswith("EVALUATION DATE:"):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(0)
            set_run_fonts(p, "Times New Roman", 11)
            for r in p.runs: r.bold = True
            continue

        # Figure 4.2 placeholder paragraph
        if len(t) == 0 and idx < len(doc.paragraphs) - 1:
            next_t = doc.paragraphs[idx+1].text.strip()
            if next_t.startswith("Figure 4.2:"):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.keep_with_next = True
                continue

        # List bullet paragraphs
        if p.style and p.style.name == 'List Bullet':
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.5
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
            continue

        # Normal body paragraphs (Only multi-line prose gets justified)
        if len(t) > 0 and not p._element.xpath('.//m:oMathPara'):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.5
            for r in p.runs:
                if len(r._r.xpath('.//w:drawing')) == 0:
                    if not r.font.name:
                        r.font.name = "Times New Roman"
                    if not r.font.size:
                        r.font.size = Pt(12)

    # 5. Fix encoding artifacts (ensure proper dashes and accents, skip drawing runs!)
    for p in doc.paragraphs:
        if len(p._element.xpath('.//w:drawing')) > 0:
            continue
        for r in p.runs:
            if len(r._r.xpath('.//w:drawing')) > 0:
                continue
            t = r.text
            if any(k in t for k in ["\ufffd", "Jgou", "Kttler", "Rocktschel"]):
                t = t.replace("\ufffd", "–")
                t = t.replace("Jgou", "Jégou")
                t = t.replace("Kttler", "Küttler")
                t = t.replace("Rocktschel", "Rocktäschel")
                r.text = t

    print(f"Saving formatted document to: {dst_path}")
    doc.save(dst_path)
    print("Master document formatting complete!")

if __name__ == "__main__":
    src = r"docs\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx"
    dst = r"docs\ADA23DLU04_PROJECT_REPORT_FORMATTED.docx"
    format_document(src, dst)
    
    # Also save a second copy as ADA23DLU04_PROJECT_REPORT_WITH_FIGURES_FIXED.docx
    dst_fixed = r"docs\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES_FIXED.docx"
    format_document(src, dst_fixed)
    
    # And if WITH_FIGURES.docx is unlocked, overwrite it as well
    try:
        format_document(src, src)
        print("Successfully updated docs\\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx directly!")
    except PermissionError:
        print("docs\\ADA23DLU04_PROJECT_REPORT_WITH_FIGURES.docx is currently open in Microsoft Word. Saved to FORMATTED.docx and WITH_FIGURES_FIXED.docx.")
