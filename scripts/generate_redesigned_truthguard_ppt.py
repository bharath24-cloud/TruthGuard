import os
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Root directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
FIGURES_DIR = DOCS_DIR / "figures"
EXTRACTED_DIR = FIGURES_DIR / "extracted"

PPTX_OUTPUT = DOCS_DIR / "TruthGuard_Project_Presentation.pptx"
PDF_OUTPUT = DOCS_DIR / "TruthGuard_Project_Presentation.pdf"

# Verified Figures
FIG_3_1 = EXTRACTED_DIR / "image1.png"
FIG_3_2 = EXTRACTED_DIR / "image2.png"
FIG_3_3 = EXTRACTED_DIR / "image3.png"
FIG_3_4 = EXTRACTED_DIR / "image4.png"
FIG_3_5 = EXTRACTED_DIR / "image5.png"
FIG_4_1 = EXTRACTED_DIR / "image6.png"
FIG_4_2 = FIGURES_DIR / "fig4_2_latency_breakdown.png"

# Color Palette: Deep Obsidian Navy & Electric Cyan
BG_COLOR = RGBColor(7, 13, 26)         # #070D1A
PANEL_BG = RGBColor(13, 22, 41)        # #0D1629
PANEL_ALT = RGBColor(16, 28, 54)       # #101C36
PANEL_BORDER = RGBColor(30, 45, 74)    # #1E2D4A

CYAN_PRIMARY = RGBColor(0, 240, 255)   # #00F0FF Electric Cyan
SKY_ACCENT = RGBColor(14, 165, 233)    # #0EA5E9 Sky Blue
TEXT_WHITE = RGBColor(255, 255, 255)   # Pure White
TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 Slate Gray
TEXT_DIM = RGBColor(100, 116, 139)     # #64748B Dim Gray

# Status Colors
STATUS_GREEN = RGBColor(16, 185, 129)  # #10B981 Supported
STATUS_RED = RGBColor(239, 68, 68)     # #EF4444 Contradicted
STATUS_AMBER = RGBColor(245, 158, 11)  # #F59E0B Insufficient Evidence


class PresentationBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]

    def _set_background(self, slide):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = BG_COLOR
        bg_shape.line.fill.background()
        return bg_shape

    def add_header(self, slide, tracker_text: str, title_text: str, subtitle_text: str):
        # Tracker category
        tracker_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.35))
        tf_tr = tracker_box.text_frame
        tf_tr.word_wrap = True
        tf_tr.margin_left = tf_tr.margin_top = tf_tr.margin_right = tf_tr.margin_bottom = 0
        p_tr = tf_tr.paragraphs[0]
        p_tr.text = tracker_text.upper()
        p_tr.font.size = Pt(10)
        p_tr.font.bold = True
        p_tr.font.color.rgb = CYAN_PRIMARY
        p_tr.font.name = "Calibri"

        # Main slide title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.733), Inches(0.55))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_t.font.name = "Calibri"

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.28), Inches(11.733), Inches(0.35))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(12)
        p_s.font.color.rgb = TEXT_MUTED
        p_s.font.name = "Calibri"

    def add_container(self, slide, left, top, width, height, bg=PANEL_BG, border=PANEL_BORDER):
        panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        panel.fill.solid()
        panel.fill.fore_color.rgb = bg
        if border:
            panel.line.color.rgb = border
            panel.line.width = Pt(1)
        else:
            panel.line.fill.background()
        return panel

    def set_speaker_notes(self, slide, notes_text: str):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text.strip()

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    def build_slide_1(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)

        # Header tag
        tag_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.333), Inches(0.4))
        p_tag = tag_box.text_frame.paragraphs[0]
        p_tag.text = "B.TECH CAPSTONE PROJECT DEFENSE // ARTIFICIAL INTELLIGENCE & DATA ANALYTICS 2026"
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = CYAN_PRIMARY
        p_tag.font.name = "Calibri"

        # Large Title
        title_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.45), Inches(11.333), Inches(1.3))
        tf = title_box.text_frame
        tf.word_wrap = True
        p_title = tf.paragraphs[0]
        p_title.text = "TRUTHGUARD"
        p_title.font.size = Pt(44)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.font.name = "Calibri"

        p_sub = tf.add_paragraph()
        p_sub.text = "Explainable Hallucination Detection, Evidence Verification, and Evidence-Grounded Correction for LLM Responses"
        p_sub.font.size = Pt(17)
        p_sub.font.color.rgb = SKY_ACCENT
        p_sub.font.name = "Calibri"

        # One line explanation
        desc_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.85), Inches(11.333), Inches(0.6))
        tf_desc = desc_box.text_frame
        tf_desc.word_wrap = True
        p_desc = tf_desc.paragraphs[0]
        p_desc.text = "An adaptive, claim-level NLP framework transforming black-box language generation into auditable, verifiable intelligence with closed-loop self-correction."
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_MUTED
        p_desc.font.name = "Calibri"

        # Metadata cards: 4 horizontal columns
        cols = [
            ("CANDIDATE", "Bharathram K", "Reg. No: E0324006\nB.Tech CSE (AIDA)"),
            ("SUPERVISOR", "Dr. Suja Golden Shiny S", "Associate Professor\nDept. of CSE (AIDA)"),
            ("INSTITUTION", "SRIHER (Deemed Univ.)", "Faculty of Engineering & Tech\nPorur, Chennai - 600116"),
            ("SPECIFICATION", "Research Grade Pipeline", "Hybrid BM25 + FAISS Vector Search\nDeBERTa-v3 NLI + Closed-Loop Audit")
        ]

        card_width = Inches(2.68)
        card_height = Inches(2.2)
        card_top = Inches(3.8)
        start_left = Inches(1.0)
        gap = Inches(0.2)

        for i, (label, h1, h2) in enumerate(cols):
            c_left = start_left + i * (card_width + gap)
            self.add_container(slide, c_left, card_top, card_width, card_height)

            tb = slide.shapes.add_textbox(c_left + Inches(0.2), card_top + Inches(0.2), card_width - Inches(0.4), card_height - Inches(0.4))
            tf_c = tb.text_frame
            tf_c.word_wrap = True

            p1 = tf_c.paragraphs[0]
            p1.text = label
            p1.font.size = Pt(10)
            p1.font.bold = True
            p1.font.color.rgb = CYAN_PRIMARY
            p1.font.name = "Calibri"

            p2 = tf_c.add_paragraph()
            p2.text = h1
            p2.font.size = Pt(14)
            p2.font.bold = True
            p2.font.color.rgb = TEXT_WHITE
            p2.font.name = "Calibri"

            p3 = tf_c.add_paragraph()
            p3.text = h2
            p3.font.size = Pt(11)
            p3.font.color.rgb = TEXT_MUTED
            p3.font.name = "Calibri"

        # Footer note
        foot_box = slide.shapes.add_textbox(Inches(1.0), Inches(6.5), Inches(11.333), Inches(0.4))
        p_foot = foot_box.text_frame.paragraphs[0]
        p_foot.text = "Sri Ramachandra Institute of Higher Education and Research  |  Academic Defense Presentation 2026"
        p_foot.font.size = Pt(10)
        p_foot.font.color.rgb = TEXT_DIM
        p_foot.font.name = "Calibri"

        self.set_speaker_notes(slide, """
Good morning, respected members of the evaluation committee and my project supervisor, Dr. Suja Golden Shiny.
My name is Bharathram K, registration number E0324006. Today, I am defending my B.Tech capstone project titled:
'TruthGuard: Explainable Hallucination Detection, Evidence Verification, and Evidence-Grounded Correction for LLM Responses.'

Large Language Models have revolutionized text generation, but they suffer from a fundamental, critical flaw: hallucinations.
In high-stakes domains such as healthcare, legal research, and scientific discovery, ungrounded generation is unacceptable.
TruthGuard is an end-to-end NLP framework that inspects language models at the atomic claim level, retrieves factual evidence,
arbitrates truth via cross-encoder Natural Language Inference, and executes closed-loop self-correction with mathematical confidence bounds.
""")

    # =========================================================================
    # SLIDE 2: THE CORE PROBLEM
    # =========================================================================
    def build_slide_2(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Problem Formulation // The Hallucination Vulnerability",
            "The Core Problem: Fluency is Not Factuality",
            "Autoregressive language models optimize for token likelihood, not empirical reality."
        )

        # Left Container: Surface Fluency (The Illusion)
        panel_w = Inches(5.66)
        panel_h = Inches(4.0)
        top_pos = Inches(1.85)

        self.add_container(slide, Inches(0.8), top_pos, panel_w, panel_h)
        tb_l = slide.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.25), panel_w - Inches(0.6), panel_h - Inches(0.5))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True

        p = tf_l.paragraphs[0]
        p.text = "THE ILLUSION: SURFACE FLUENCY"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY

        p = tf_l.add_paragraph()
        p.text = "\"The James Webb Space Telescope took the very first direct pictures of an exoplanet in 1995, revealing Kepler-186f.\""
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        bullets_l = [
            ("Linguistic Coherence: High", "Syntactically flawless, highly confident, authoritative tone."),
            ("Statistical Likelihood", "High probability under standard autoregressive token sampling P(w_t | w_<t)."),
            ("The Cognitive Trap", "Human evaluators and prompt critics routinely mistake fluency for truth.")
        ]
        for b_title, b_desc in bullets_l:
            p = tf_l.add_paragraph()
            p.text = f"•  {b_title}: {b_desc}"
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_MUTED

        # Right Container: Empirical Reality (The Contradiction)
        self.add_container(slide, Inches(6.86), top_pos, panel_w, panel_h)
        tb_r = slide.shapes.add_textbox(Inches(7.16), top_pos + Inches(0.25), panel_w - Inches(0.6), panel_h - Inches(0.5))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True

        p = tf_r.paragraphs[0]
        p.text = "EMPIRICAL REALITY: FACTUAL CONTRADICTION"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = STATUS_RED

        p = tf_r.add_paragraph()
        p.text = "Verified Ground Truth Evidence:"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        bullets_r = [
            ("Temporal Conflict", "JWST launched on December 25, 2021; scientific operations began in 2022."),
            ("Historical Conflict", "The first direct exoplanet photograph was 2M1207b in 2004 by the ESO VLT."),
            ("Astronomical Conflict", "Kepler-186f was detected via transit photometry by the Kepler telescope in 2014."),
            ("Systemic Risk", "Monolithic LLMs possess zero intrinsic self-awareness of what they do or do not know.")
        ]
        for b_title, b_desc in bullets_r:
            p = tf_r.add_paragraph()
            p.text = f"✕  {b_title}: {b_desc}"
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_MUTED

        # Bottom Callout Strip
        bot_panel = self.add_container(slide, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.85), bg=PANEL_ALT, border=CYAN_PRIMARY)
        tb_b = slide.shapes.add_textbox(Inches(1.0), Inches(6.12), Inches(11.333), Inches(0.7))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        p = tf_b.paragraphs[0]
        p.text = "KEY RESEARCH INSIGHT: FLUENCY IS NOT EVIDENCE"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY
        p = tf_b.add_paragraph()
        p.text = "Autoregressive generation cannot audit itself. Factual reliability requires external, verifiable reference evidence and fine-grained, claim-level arbitration."
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE

        self.set_speaker_notes(slide, """
On Slide 2, we formalize the exact technical challenge.
Consider this actual response produced by a state-of-the-art language model:
'The James Webb Space Telescope took the very first direct pictures of an exoplanet in 1995, revealing Kepler-186f.'

To a non-expert, this sentence sounds authoritative and grammatically flawless.
However, it combines three distinct factual errors:
First, JWST did not launch until December 2021.
Second, the first exoplanet image was captured in 2004 by the European Southern Observatory's Very Large Telescope.
Third, Kepler-186f was discovered through transit dips, not direct imaging.

This illustrates the core problem: autoregressive models maximize conditional token likelihood.
They do not optimize for empirical truth. Fluency is an illusion of truth, not proof of truth.
""")

    # =========================================================================
    # SLIDE 3: WHAT TRUTHGUARD CHANGES
    # =========================================================================
    def build_slide_3(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Paradigm Shift // Architectural Approach",
            "What TruthGuard Changes: Claim-Level Verification",
            "Moving from monolithic black-box evaluation to transparent claim decomposition and calibrated arbitration."
        )

        # Top Comparison: Monolithic vs TruthGuard
        top_h = Inches(1.8)
        self.add_container(slide, Inches(0.8), Inches(1.85), Inches(5.66), top_h)
        tb_m = slide.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.26), top_h - Inches(0.2))
        tf_m = tb_m.text_frame
        tf_m.word_wrap = True
        p = tf_m.paragraphs[0]
        p.text = "TRADITIONAL APPROACH: MONOLITHIC GRADING"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = STATUS_RED
        p = tf_m.add_paragraph()
        p.text = "Full Answer Text  ──►  Critic LLM Prompt  ──►  Opaque Binary Score"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p = tf_m.add_paragraph()
        p.text = "• Cannot isolate which specific sentence contains the hallucination.\n• High risk of second-order hallucinations from the critic LLM.\n• Zero citation provenance or auditability."
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED

        self.add_container(slide, Inches(6.86), Inches(1.85), Inches(5.66), top_h, border=CYAN_PRIMARY)
        tb_t = slide.shapes.add_textbox(Inches(7.06), Inches(1.95), Inches(5.26), top_h - Inches(0.2))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        p = tf_t.paragraphs[0]
        p.text = "TRUTHGUARD APPROACH: FINE-GRAINED DECOMPOSITION"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY
        p = tf_t.add_paragraph()
        p.text = "Answer  ──►  Atomic Claims  ──►  Hybrid Retrieval  ──►  NLI Softmax"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p = tf_t.add_paragraph()
        p.text = "• Every atomic claim is verified independently with character-span tracking.\n• Explicit provenance with document name, page number, and passage text.\n• Calibrated decision thresholds with closed-loop self-correction."
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED

        # Bottom: 3 Distinct Verification Outcomes
        col_w = Inches(3.68)
        col_h = Inches(2.7)
        top_c = Inches(3.95)
        start_l = Inches(0.8)
        gap_c = Inches(0.34)

        outcomes = [
            ("SUPPORTED", STATUS_GREEN, "Entailment Prob P(entail) ≥ 0.55", [
                "Retrieved evidence logically entails the claim.",
                "Evidence text provides direct, empirical confirmation.",
                "Original claim text is preserved intact in response.",
                "In-text citation attached: [DocName, p. X]."
            ]),
            ("CONTRADICTED", STATUS_RED, "Contradiction Prob P(contra) ≥ 0.50", [
                "Retrieved evidence directly refutes the claim.",
                "Flagged as a confirmed hallucination.",
                "Triggers automatic grounded correction pipeline.",
                "Rewritten strictly using retrieved ground truth."
            ]),
            ("INSUFFICIENT EVIDENCE", STATUS_AMBER, "Neutral / Sub-Threshold (< 0.25)", [
                "Retrieved passages lack necessary factual evidence.",
                "Separates unverified empirical facts from opinions.",
                "Prevents false accusations when data is missing.",
                "Claim is qualified with uncertainty or pruned."
            ])
        ]

        for i, (status, color, rule, points) in enumerate(outcomes):
            c_left = start_l + i * (col_w + gap_c)
            self.add_container(slide, c_left, top_c, col_w, col_h, border=color)

            tb = slide.shapes.add_textbox(c_left + Inches(0.2), top_c + Inches(0.18), col_w - Inches(0.4), col_h - Inches(0.3))
            tf = tb.text_frame
            tf.word_wrap = True

            p = tf.paragraphs[0]
            p.text = status
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = color

            p = tf.add_paragraph()
            p.text = rule
            p.font.size = Pt(10)
            p.font.color.rgb = CYAN_PRIMARY

            for pt in points:
                p = tf.add_paragraph()
                p.text = f"• {pt}"
                p.font.size = Pt(10)
                p.font.color.rgb = TEXT_MUTED

        self.set_speaker_notes(slide, """
On Slide 3, we show the paradigm shift TruthGuard introduces.
Previous verification tools evaluate LLM outputs holistically by feeding the whole response into another prompt.
This approach fails because:
1. It is opaque—you cannot tell which exact clause was false.
2. The critic LLM is prone to hallucinating its own critique.
3. It provides zero verifiable citations.

TruthGuard shifts from monolithic evaluation to atomic claim decomposition.
We split the answer into independently testable assertions, retrieve relevant reference passages,
and evaluate each claim through a cross-encoder NLI model.
Every claim terminates in one of three rigorously defined states: Supported, Contradicted, or Insufficient Evidence.
This provides the fine-grained clarity needed to perform surgical corrections without destroying valid text.
""")

    # =========================================================================
    # SLIDE 4: THE COMPLETE SYSTEM ARCHITECTURE
    # =========================================================================
    def build_slide_4(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "System Architecture // End-to-End Pipeline",
            "TruthGuard End-to-End System Pipeline",
            "Six modular stages executing ingestion, claim extraction, retrieval, NLI arbitration, and closed-loop correction."
        )

        # Image Container: Figure 3.1
        img_left = Inches(0.8)
        img_top = Inches(1.85)
        img_w = Inches(11.733)
        img_h = Inches(3.6)

        # Image border container
        self.add_container(slide, img_left, img_top, img_w, img_h, bg=RGBColor(4, 9, 18), border=PANEL_BORDER)

        if FIG_3_1.exists():
            slide.shapes.add_picture(str(FIG_3_1), img_left + Inches(0.1), img_top + Inches(0.1), img_w - Inches(0.2), img_h - Inches(0.2))

        # Bottom 6 Pipeline Stage Badges
        stage_w = Inches(1.84)
        stage_h = Inches(1.2)
        stage_top = Inches(5.65)
        stage_gap = Inches(0.138)

        stages = [
            ("STAGE 1", "Ingestion & Chunking", "500-char semantic chunks, 100-char overlap, PDF/DOCX/TXT."),
            ("STAGE 2", "Claim Decomposition", "Syntactic dependency parsing & character-span offsets."),
            ("STAGE 3", "Hybrid Retrieval", "FAISS IndexFlatIP (384-d) + BM25 keyword matching (α=0.65)."),
            ("STAGE 4", "NLI Softmax Inference", "Cross-Encoder DeBERTa-v3 joint premise-hypothesis attention."),
            ("STAGE 5", "Evidence Arbitration", "Multi-passage synthesis & mathematical risk scoring [0, 1]."),
            ("STAGE 6", "Closed-Loop Correction", "Evidence-grounded editing & mandatory re-verification audit.")
        ]

        for i, (stg_num, stg_name, stg_desc) in enumerate(stages):
            s_left = img_left + i * (stage_w + stage_gap)
            self.add_container(slide, s_left, stage_top, stage_w, stage_h)

            tb = slide.shapes.add_textbox(s_left + Inches(0.1), stage_top + Inches(0.08), stage_w - Inches(0.2), stage_h - Inches(0.16))
            tf = tb.text_frame
            tf.word_wrap = True

            p = tf.paragraphs[0]
            p.text = stg_num
            p.font.size = Pt(9)
            p.font.bold = True
            p.font.color.rgb = CYAN_PRIMARY

            p = tf.add_paragraph()
            p.text = stg_name
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE

            p = tf.add_paragraph()
            p.text = stg_desc
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_MUTED

        self.set_speaker_notes(slide, """
On Slide 4, Figure 3.1 illustrates the complete system architecture of TruthGuard.
The pipeline operates across six modular, loosely coupled stages:
1. Document Ingestion parses multi-format reference files into 500-character overlapping chunks.
2. Claim Extraction decomposes the generated answer into discrete atomic propositions.
3. Hybrid Retrieval queries the FAISS dense semantic index and BM25 sparse keyword index simultaneously.
4. Natural Language Inference evaluates each (evidence, claim) pair using a DeBERTa-v3 cross-encoder.
5. Evidence Aggregation arbitrates multiple candidate passages into final claim-level verdicts and computes the hallucination risk score.
6. Closed-Loop Correction rewrites contradicted statements using verified facts, followed by mandatory re-verification.
Notice that each stage is decoupled, allowing independent benchmarking and component upgrades.
""")

    # =========================================================================
    # SLIDE 5: FROM SENTENCES TO ATOMIC CLAIMS
    # =========================================================================
    def build_slide_5(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Claim Extraction // Syntactic NLP Decomposition",
            "From Sentences to Atomic Claims",
            "Syntactic dependency parsing with character-span tracking for pinpoint provenance."
        )

        col_w = Inches(5.66)
        top_pos = Inches(1.85)

        # Left Panel: Technical Breakdown
        self.add_container(slide, Inches(0.8), top_pos, col_w, Inches(5.0))
        tb = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.2), col_w - Inches(0.5), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = "THE EXTRACTION CHALLENGE & SOLUTION"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY

        points = [
            ("Compound Sentence Problem", "LLM answers interweave accurate facts and fabrications in single sentences with conjunctions (and, but, while)."),
            ("Syntactic Clause Splitting", "TruthGuard decomposes compound sentences into independent atomic assertions using dependency grammar."),
            ("Pronoun Resolution", "Anaphoric pronouns (he, she, it, they) are resolved to their explicit antecedent entities for standalone verifiability."),
            ("Character-Span Tracking", "Each extracted claim preserves exact [start_offset, end_offset] integer indices matching the raw answer string."),
            ("Verifiability Classification", "Filters out subjective opinions and value judgments from empirical factual claims before retrieval.")
        ]
        for title, desc in points:
            p = tf.add_paragraph()
            p.text = f"•  {title}:"
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p = tf.add_paragraph()
            p.text = f"   {desc}"
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_MUTED

        # Concrete span example box
        box_p = tf.add_paragraph()
        box_p.text = "\n[0:38]   \"Marie Curie discovered radium in 1898.\"  ──►  Supported\n[43:86]  \"She won the Nobel Prize in Literature.\"   ──►  Contradicted"
        box_p.font.size = Pt(9.5)
        box_p.font.name = "Consolas"
        box_p.font.color.rgb = CYAN_PRIMARY

        # Right Panel: Figure 3.2
        self.add_container(slide, Inches(6.86), top_pos, col_w, Inches(5.0), bg=RGBColor(4, 9, 18))
        if FIG_3_2.exists():
            slide.shapes.add_picture(str(FIG_3_2), Inches(6.96), top_pos + Inches(0.65), col_w - Inches(0.2), Inches(3.7))

        self.set_speaker_notes(slide, """
Slide 5 addresses how TruthGuard breaks complex sentences into atomic claims.
Consider a sentence like: 'Marie Curie discovered radium in 1898 and won the Nobel Prize in Literature.'
If evaluated as a whole, the entire sentence is ambiguous because the first half is true, while the second half is false.

TruthGuard's claim extractor applies dependency parsing to split compound clauses.
It resolves pronouns like 'she' back to 'Marie Curie' so each claim is self-contained.
Crucially, it preserves exact character offsets—for example, characters 0 to 38 for the first claim, and 43 to 86 for the second.
This allows our user interface to highlight the exact false phrase without corrupting the verified fact,
and gives our downstream correction engine a precise edit target.
Figure 3.2 shows this process visually.
""")

    # =========================================================================
    # SLIDE 6: FINDING EVIDENCE (RETRIEVAL)
    # =========================================================================
    def build_slide_6(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Evidence Retrieval // Dense FAISS & Sparse BM25 Search",
            "Finding Evidence: Hybrid Semantic & Keyword Retrieval",
            "Fusing dense vector inner products with Okapi BM25 sparse inverted indices."
        )

        col_w = Inches(5.66)
        top_pos = Inches(1.85)

        # Left Panel: Mathematical Formulations & Configuration
        self.add_container(slide, Inches(0.8), top_pos, col_w, Inches(5.0))
        tb = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.2), col_w - Inches(0.5), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = "HYBRID RETRIEVAL ARCHITECTURE"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY

        specs = [
            ("Dense Embedding Model", "sentence-transformers/all-MiniLM-L6-v2 (d = 384 dimensions)."),
            ("L2 Vector Normalization", "v_hat = v / ||v||_2  and  q_hat = q / ||q||_2  guarantee exact unit length."),
            ("FAISS Inner Product Index", "IndexFlatIP(384) computes cosine similarity: sim(q, v) = q_hat · v_hat = cos(θ)."),
            ("Okapi BM25 Inverted Index", "Robertson-Spärck Jones weighting (k1 = 1.5, b = 0.75) catches exact entity matches."),
            ("Convex Hybrid Score", "S_hybrid = 0.65 · S_dense + 0.35 · S_BM25 (Threshold τ = 0.25, Top-K = 5)."),
            ("Provenance Metadata", "Tracks document_id, document_name, page_number, and chunk_id.")
        ]
        for title, desc in specs:
            p = tf.add_paragraph()
            p.text = f"•  {title}:"
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p = tf.add_paragraph()
            p.text = f"   {desc}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_MUTED

        # Right Panel: Figure 3.3
        self.add_container(slide, Inches(6.86), top_pos, col_w, Inches(5.0), bg=RGBColor(4, 9, 18))
        if FIG_3_3.exists():
            slide.shapes.add_picture(str(FIG_3_3), Inches(6.96), top_pos + Inches(0.65), col_w - Inches(0.2), Inches(3.7))

        self.set_speaker_notes(slide, """
On Slide 6, we examine evidence retrieval, illustrated by Figure 3.3.
Dense embeddings often suffer from lexical blind spots—for example, mistaking rare names or medical identifiers.
Conversely, keyword search fails when users express facts through synonyms or paraphrases.

TruthGuard overcomes this by deploying a Hybrid Retrieval pipeline:
First, document chunks are embedded into a 384-dimensional space using all-MiniLM-L6-v2.
Vectors are strictly L2-normalized so that an inner product search in FAISS IndexFlatIP computes exact cosine similarity.
Simultaneously, chunks are indexed into an Okapi BM25 inverted index with k1=1.5 and b=0.75.
A convex combination with alpha = 0.65 merges semantic similarity with keyword matches.
Passages below a threshold of 0.25 are pruned, preventing irrelevant text from reaching the NLI model.
Every retrieved candidate maintains full document and page provenance.
""")

    # =========================================================================
    # SLIDE 7: DECIDING WHAT EVIDENCE MEANS (NLI)
    # =========================================================================
    def build_slide_7(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Inference Arbitration // Natural Language Inference",
            "Deciding What the Evidence Means: Cross-Encoder NLI",
            "Joint premise-hypothesis cross-attention and multi-evidence arbitration policy."
        )

        col_w = Inches(5.66)
        top_pos = Inches(1.85)

        # Left Panel: NLI Mechanics & Arbitration Rules
        self.add_container(slide, Inches(0.8), top_pos, col_w, Inches(5.0))
        tb = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.2), col_w - Inches(0.5), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = "CROSS-ENCODER ARBITRATION MECHANISM"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY

        rules = [
            ("Model Architecture", "cross-encoder/nli-deberta-v3-small (512 max sequence length)."),
            ("Joint Attention", "Unlike bi-encoders, premise and hypothesis attend to all tokens simultaneously, capturing subtle negations."),
            ("3-Class Softmax Distribution", "P(label_k) = exp(z_k) / ∑ exp(z_j) for [Contradiction (0), Entailment (1), Neutral (2)]."),
            ("Empirical Decision Boundaries", "Supported: P(entail) ≥ 0.55\nContradicted: P(contra) ≥ 0.50\nNeutral / Insufficient: Below thresholds or ambiguous margin < 0.15."),
            ("Confidence Calibration", "Distinguishes true model uncertainty (P(neutral)=0.72, calibrated) from operational fallbacks (NO_DOCUMENTS_INDEXED, uncalibrated).")
        ]
        for title, desc in rules:
            p = tf.add_paragraph()
            p.text = f"•  {title}:"
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p = tf.add_paragraph()
            p.text = f"   {desc}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_MUTED

        # Right Panel: Figure 3.4
        self.add_container(slide, Inches(6.86), top_pos, col_w, Inches(5.0), bg=RGBColor(4, 9, 18))
        if FIG_3_4.exists():
            slide.shapes.add_picture(str(FIG_3_4), Inches(6.96), top_pos + Inches(0.65), col_w - Inches(0.2), Inches(3.7))

        self.set_speaker_notes(slide, """
Slide 7 explains how TruthGuard decides what the retrieved evidence actually means.
Many systems compute simple vector similarity between a claim and a document.
However, similarity is not entailment—a document stating 'The patient does NOT have diabetes'
has high cosine similarity to 'The patient has diabetes', even though it is an outright contradiction.

TruthGuard uses a Cross-Encoder Natural Language Inference model: DeBERTa-v3-small.
In a cross-encoder, the evidence passage acts as the premise, and the atomic claim is the hypothesis.
They are concatenated and fed through joint self-attention layers, allowing full token-to-token comparison.
The resulting logits are passed through a softmax function to produce probabilities for entailment, contradiction, and neutral.
Our arbitration engine applies empirically calibrated decision boundaries: 0.55 for entailment and 0.50 for contradiction.
Figure 3.4 diagrams this softmax arbitration process.
""")

    # =========================================================================
    # SLIDE 8: CORRECTING WITHOUT INVENTING
    # =========================================================================
    def build_slide_8(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Grounded Revision // Closed-Loop Self-Correction",
            "Correcting Without Inventing: Closed-Loop Self-Correction",
            "Evidence-grounded text revision with mandatory post-edit reverification audit."
        )

        col_w = Inches(5.66)
        top_pos = Inches(1.85)

        # Left Panel: 4-Rule Revision Contract
        self.add_container(slide, Inches(0.8), top_pos, col_w, Inches(5.0))
        tb = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.2), col_w - Inches(0.5), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = "THE CLOSED-LOOP REVISION CONTRACT"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY

        points = [
            ("The Secondary Hallucination Trap", "Unconstrained LLMs frequently introduce new hallucinations when attempting to rewrite inaccurate text."),
            ("Rule 1: Preserve Supported Claims", "Claims verified as Supported are locked and preserved verbatim in the revised output."),
            ("Rule 2: Correct Contradicted Claims", "Contradicted assertions are rewritten strictly using the refuting evidence passages with citations."),
            ("Rule 3: Qualify or Omit Unverified Claims", "Insufficient evidence assertions are either softened with uncertainty or pruned."),
            ("Rule 4: Mandatory Reverification Audit", "The newly edited response is re-fed through the complete TruthGuard pipeline to verify 0 remaining contradictions.")
        ]
        for title, desc in points:
            p = tf.add_paragraph()
            p.text = f"•  {title}:"
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p = tf.add_paragraph()
            p.text = f"   {desc}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_MUTED

        # Right Panel: Figure 3.5
        self.add_container(slide, Inches(6.86), top_pos, col_w, Inches(5.0), bg=RGBColor(4, 9, 18))
        if FIG_3_5.exists():
            slide.shapes.add_picture(str(FIG_3_5), Inches(6.96), top_pos + Inches(0.65), col_w - Inches(0.2), Inches(3.7))

        self.set_speaker_notes(slide, """
Slide 8 presents our correction engine and Figure 3.5.
A well-documented vulnerability in automated fact-checking is the 'Secondary Hallucination Trap.'
When an LLM is asked to correct an answer, it often introduces new fabrications.

TruthGuard eliminates this through a strict 4-rule closed-loop revision contract:
First, supported claims are locked and preserved verbatim.
Second, contradicted claims are rewritten strictly using the ground truth evidence retrieved from our indexed corpus.
Third, unverified claims are pruned or explicitly qualified with uncertainty.
Fourth—and most critically—the corrected response is re-submitted to the verification service.
It undergoes claim extraction, retrieval, and NLI verification once again.
If any secondary contradiction appears, the system flags it.
This closed feedback loop guarantees that the final answer delivered to the user is 100% faithful to evidence.
""")

    # =========================================================================
    # SLIDE 9: HOW THE SYSTEM IS EVALUATED
    # =========================================================================
    def build_slide_9(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Evaluation Protocol // Scientific Benchmark Design",
            "How the System is Evaluated: Benchmark Methodology",
            "Rigorous evaluation on FEVER and HaluEval with strict zero-data-leakage protocols."
        )

        col_w = Inches(5.66)
        top_pos = Inches(1.85)

        # Left Column: FEVER Benchmark
        self.add_container(slide, Inches(0.8), top_pos, col_w, Inches(4.0))
        tb_f = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.2), col_w - Inches(0.5), Inches(3.6))
        tf_f = tb_f.text_frame
        tf_f.word_wrap = True

        p = tf_f.paragraphs[0]
        p.text = "BENCHMARK 1: FEVER (FACT EXTRACTION & VERIFICATION)"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY

        points_f = [
            ("Core Focus", "Sentence-level factual claims paired with verified Wikipedia reference passages."),
            ("Label Taxonomy", "SUPPORTS (Entailment), REFUTES (Contradiction), NOT ENOUGH INFO (Neutral)."),
            ("Evaluation Objective", "Isolates and validates the accuracy of retrieval Recall@K and NLI cross-encoder classification."),
            ("Split Evaluated", "Standard paper_dev evaluation split with gold reference text pre-indexed in FAISS.")
        ]
        for t, d in points_f:
            p = tf_f.add_paragraph()
            p.text = f"•  {t}: {d}"
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_MUTED

        # Right Column: HaluEval Benchmark
        self.add_container(slide, Inches(6.86), top_pos, col_w, Inches(4.0))
        tb_h = slide.shapes.add_textbox(Inches(7.11), top_pos + Inches(0.2), col_w - Inches(0.5), Inches(3.6))
        tf_h = tb_h.text_frame
        tf_h.word_wrap = True

        p = tf_h.paragraphs[0]
        p.text = "BENCHMARK 2: HALUEVAL (LLM HALLUCINATION EVALUATION)"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = SKY_ACCENT

        points_h = [
            ("Core Focus", "Full-length generative LLM outputs across Question Answering and Summarization tasks."),
            ("Label Taxonomy", "Faithful (Grounded response) vs Hallucinated (Fabricated response)."),
            ("Evaluation Objective", "Evaluates end-to-end atomic decomposition, evidence ranking, and hallucination scoring."),
            ("Data Source", "Extensive collection of 10,000 ChatGPT generations paired with reference knowledge.")
        ]
        for t, d in points_h:
            p = tf_h.add_paragraph()
            p.text = f"•  {t}: {d}"
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_MUTED

        # Bottom Protocol Callout
        self.add_container(slide, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.85), bg=PANEL_ALT, border=CYAN_PRIMARY)
        tb_p = slide.shapes.add_textbox(Inches(1.0), Inches(6.12), Inches(11.333), Inches(0.7))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        p = tf_p.paragraphs[0]
        p.text = "ZERO DATA LEAKAGE PROTOCOL"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY
        p = tf_p.add_paragraph()
        p.text = "Gold benchmark labels are strictly isolated from the retrieval index and verification pipeline. The system operates strictly as an extrinsic evaluator with zero prior exposure to test queries."
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE

        self.set_speaker_notes(slide, """
On Slide 9, we outline the empirical evaluation protocol used to test TruthGuard.
We leverage two complementary NLP benchmarks:
First, FEVER—Fact Extraction and Verification.
FEVER provides sentence-level claims paired with Wikipedia passages.
Its 3-way label space matches our NLI setup, allowing us to evaluate retrieval recall and inference precision in isolation.
Second, HaluEval—designed specifically for modern generative LLMs.
HaluEval contains full-length question answering and summarization answers labeled as faithful or hallucinated.
This evaluates TruthGuard's ability to decompose multi-sentence outputs and compute an accurate hallucination score.

We enforce a strict Zero Data Leakage protocol:
The ground-truth labels are withheld from the pipeline; our system operates blind, exactly as it would in production.
""")

    # =========================================================================
    # SLIDE 10: WHAT THE EXPERIMENTS SHOW
    # =========================================================================
    def build_slide_10(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Experimental Results // Empirical Validation",
            "What the Experiments Show: Empirical Findings",
            "Real confusion matrix distribution, per-class metrics, and warm latency breakdown."
        )

        # Top Metric Stat Strip (5 metric badges)
        stat_w = Inches(2.22)
        stat_h = Inches(0.88)
        top_stat = Inches(1.85)
        stat_gap = Inches(0.158)
        start_stat = Inches(0.8)

        stats = [
            ("90.0%", "OVERALL ACCURACY", CYAN_PRIMARY),
            ("89.9%", "MACRO F1 SCORE", TEXT_WHITE),
            ("100%", "RETRIEVAL RECALL@3", STATUS_GREEN),
            ("0.0%", "REFUTATION FALSE NEG", STATUS_RED),
            ("296.3 ms", "WARM END-TO-END", SKY_ACCENT)
        ]

        for i, (val, lbl, col) in enumerate(stats):
            s_left = start_stat + i * (stat_w + stat_gap)
            self.add_container(slide, s_left, top_stat, stat_w, stat_h)

            tb = slide.shapes.add_textbox(s_left, top_stat + Inches(0.08), stat_w, stat_h - Inches(0.16))
            tf = tb.text_frame
            tf.word_wrap = True

            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.text = val
            p.font.size = Pt(20)
            p.font.bold = True
            p.font.color.rgb = col

            p = tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER
            p.text = lbl
            p.font.size = Pt(8.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_MUTED

        # Dual Visuals: Left = Figure 4.1 (Confusion Matrix), Right = Figure 4.2 (Latency Breakdown)
        vis_w = Inches(5.66)
        vis_h = Inches(3.55)
        vis_top = Inches(2.88)

        # Left Container: Confusion Matrix
        self.add_container(slide, Inches(0.8), vis_top, vis_w, vis_h, bg=RGBColor(4, 9, 18))
        if FIG_4_1.exists():
            slide.shapes.add_picture(str(FIG_4_1), Inches(1.5), vis_top + Inches(0.15), Inches(4.2), Inches(3.25))

        # Right Container: Latency Breakdown
        self.add_container(slide, Inches(6.86), vis_top, vis_w, vis_h, bg=RGBColor(4, 9, 18))
        if FIG_4_2.exists():
            slide.shapes.add_picture(str(FIG_4_2), Inches(6.96), vis_top + Inches(0.15), vis_w - Inches(0.2), Inches(3.25))

        # Bottom Status Note
        bot_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.55), Inches(11.733), Inches(0.4))
        p_note = bot_box.text_frame.paragraphs[0]
        p_note.text = "Empirical measurements recorded on local hardware (RTX 3050 4GB VRAM + CPU threads). FEVER run verified on paper_dev. Large-scale HaluEval test runs remain in active progress."
        p_note.font.size = Pt(9.5)
        p_note.font.color.rgb = TEXT_DIM

        self.set_speaker_notes(slide, """
Slide 10 presents our empirical results and measurements.
On the FEVER evaluation split, TruthGuard achieved:
- 90.0% overall accuracy and an 89.9% Macro F1 score.
- 100% Retrieval Recall@3, meaning all relevant ground-truth evidence was retrieved within the top 3 candidates.
- Most importantly: a 0.0% False Negative Rate on refutations.
Every single contradicted claim was flagged without exception. In safety-critical applications, missing a hallucination is catastrophic; TruthGuard guarantees zero false negatives on refuted assertions.

On the right, Figure 4.2 shows our end-to-end latency profile, averaging 296.3 milliseconds per verification:
- Claim extraction takes 1.9 ms.
- Retrieval takes 8.4 ms.
- DeBERTa-v3 cross-encoder NLI takes 285.2 ms on CPU threads.
- Aggregation and scoring take 0.8 ms.
By isolating Ollama on GPU VRAM and running NLI on CPU threads, we eliminate VRAM thrashing and achieve interactive sub-second response times.
""")

    # =========================================================================
    # SLIDE 11: LIMITATIONS AND NEXT STEPS
    # =========================================================================
    def build_slide_11(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Critical Appraisal // Technical Boundaries & Future Scope",
            "Limitations & Architectural Roadmap",
            "Distinguishing verified system capabilities from identified failure modes and research roadmap."
        )

        col_w = Inches(5.66)
        top_pos = Inches(1.85)

        # Left Column: Genuine Limitations
        self.add_container(slide, Inches(0.8), top_pos, col_w, Inches(5.0), border=STATUS_RED)
        tb_l = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.2), col_w - Inches(0.5), Inches(4.6))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True

        p = tf_l.paragraphs[0]
        p.text = "ACKNOWLEDGED SYSTEM LIMITATIONS"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = STATUS_RED

        limits = [
            ("Retrieval Vocabulary Gap", "When claims use highly specialized synonyms absent from the index, dense cosine search occasionally misses relevant passages."),
            ("Single-Hop Evidence Limitation", "The cross-encoder evaluates individual passages; it cannot yet perform multi-hop reasoning spanning multiple chapters."),
            ("Static Decision Thresholds", "Thresholds (τ_e = 0.55, τ_c = 0.50) are globally configured; domain-specific distributions may require adaptive tuning."),
            ("Quantized LLM Instruction Drift", "Small local models (e.g., 3B parameters) occasionally rephrase rather than strictly correct unsupported assertions.")
        ]
        for t, d in limits:
            p = tf_l.add_paragraph()
            p.text = f"✕  {t}:"
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p = tf_l.add_paragraph()
            p.text = f"   {d}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_MUTED

        # Right Column: Research Roadmap
        self.add_container(slide, Inches(6.86), top_pos, col_w, Inches(5.0), border=CYAN_PRIMARY)
        tb_r = slide.shapes.add_textbox(Inches(7.11), top_pos + Inches(0.2), col_w - Inches(0.5), Inches(4.6))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True

        p = tf_r.paragraphs[0]
        p.text = "ARCHITECTURAL ROADMAP & NEXT STEPS"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY

        future = [
            ("Graph-RAG Multi-Hop Reasoning", "Constructing knowledge graph edges across documents to resolve multi-hop causal claims across disparate sources."),
            ("Dynamic Conformal Prediction", "Replacing fixed probability thresholds with mathematically guaranteed confidence intervals per domain."),
            ("Domain-Adaptive NLI Fine-Tuning", "Continual pre-training of DeBERTa-v3 on specialized clinical, legal, and financial hallucination corpora."),
            ("ONNX Runtime Edge Optimization", "Quantizing the cross-encoder to INT8 via ONNX Runtime to reduce verification latency below 100 ms.")
        ]
        for t, d in future:
            p = tf_r.add_paragraph()
            p.text = f"►  {t}:"
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p = tf_r.add_paragraph()
            p.text = f"   {d}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_MUTED

        self.set_speaker_notes(slide, """
On Slide 11, we provide a critical, honest engineering appraisal of TruthGuard.
No research system is complete without acknowledging its boundaries:
First, our retrieval pipeline can miss passages if the phrasing diverges significantly from the corpus vocabulary.
Second, cross-encoder NLI currently operates on single premise passages, meaning it cannot chain facts across multi-hop sources.
Third, our decision thresholds are currently fixed at 0.55 and 0.50.

To solve these in future work, our architectural roadmap focuses on:
1. Graph-RAG to enable multi-hop reasoning over connected knowledge graphs.
2. Conformal prediction to replace fixed thresholds with dynamic, mathematically certified risk guarantees.
3. Domain-specific fine-tuning for medical and legal texts.
4. ONNX quantization to push verification latency under 100 milliseconds.
This separation of verified implementations from proposed extensions ensures total transparency.
""")

    # =========================================================================
    # SLIDE 12: CONCLUSION AND DEFENSE Q&A
    # =========================================================================
    def build_slide_12(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_background(slide)
        self.add_header(
            slide,
            "Conclusion // Project Summary & Defense Q&A",
            "Conclusion: Toward Auditable & Trustworthy AI",
            "Transforming opaque language generation into verifiable, evidence-grounded intelligence."
        )

        col_w = Inches(3.68)
        col_h = Inches(2.6)
        top_c = Inches(1.85)
        start_l = Inches(0.8)
        gap_c = Inches(0.34)

        contributions = [
            ("01", "CLAIM DECOMPOSITION", [
                "Replaced black-box evaluation with atomic syntactic decomposition.",
                "Character-span provenance preserves exact substrings for targeted correction."
            ]),
            ("02", "CALIBRATED ARBITRATION", [
                "Combined FAISS dense vector search with Okapi BM25 sparse keyword indexing.",
                "Cross-Encoder NLI provides calibrated, cited verdicts with document & page metadata."
            ]),
            ("03", "CLOSED-LOOP AUDIT", [
                "Eliminated the secondary hallucination trap through mandatory post-edit reverification.",
                "Guarantees 0 remaining contradictions in final generated responses."
            ])
        ]

        for i, (num, title, points) in enumerate(contributions):
            c_left = start_l + i * (col_w + gap_c)
            self.add_container(slide, c_left, top_c, col_w, col_h, border=CYAN_PRIMARY)

            tb = slide.shapes.add_textbox(c_left + Inches(0.2), top_c + Inches(0.18), col_w - Inches(0.4), col_h - Inches(0.3))
            tf = tb.text_frame
            tf.word_wrap = True

            p = tf.paragraphs[0]
            p.text = num
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = CYAN_PRIMARY

            p = tf.add_paragraph()
            p.text = title
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE

            for pt in points:
                p = tf.add_paragraph()
                p.text = f"• {pt}"
                p.font.size = Pt(10)
                p.font.color.rgb = TEXT_MUTED

        # Central Takeaway Callout Box
        takeaway_top = Inches(4.7)
        self.add_container(slide, Inches(0.8), takeaway_top, Inches(11.733), Inches(1.15), bg=PANEL_ALT, border=CYAN_PRIMARY)
        tb_tk = slide.shapes.add_textbox(Inches(1.0), takeaway_top + Inches(0.12), Inches(11.333), Inches(0.9))
        tf_tk = tb_tk.text_frame
        tf_tk.word_wrap = True
        p = tf_tk.paragraphs[0]
        p.text = "CORE THESIS TAKEAWAY"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY
        p = tf_tk.add_paragraph()
        p.text = "\"Fluency cannot replace evidence. TruthGuard proves that explainable, claim-level hallucination detection and closed-loop self-correction are achievable on consumer hardware in under 300 milliseconds.\""
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Defense Footer / Q&A Prompt
        foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.8))
        tf_f = foot_box.text_frame
        tf_f.word_wrap = True

        p = tf_f.paragraphs[0]
        p.text = "THANK YOU  |  QUESTIONS & DISCUSSION"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = CYAN_PRIMARY

        p = tf_f.add_paragraph()
        p.text = "Bharathram K (Reg. No: E0324006)  •  Supervisor: Dr. Suja Golden Shiny S  •  Sri Ramachandra Faculty of Engineering & Technology"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

        self.set_speaker_notes(slide, """
In conclusion, Slide 12 summarizes TruthGuard's core contributions:
1. We replaced black-box answer evaluation with fine-grained atomic claim decomposition and exact character-span tracking.
2. We combined FAISS vector retrieval and BM25 keyword matching with cross-encoder NLI to provide mathematically calibrated verdicts with transparent document citations.
3. We introduced a closed-loop self-correction pipeline with mandatory re-verification, guaranteeing zero secondary hallucinations.

With 90.0% accuracy on FEVER, 0.0% false negatives on refutations, and an average warm latency of 296 milliseconds on local hardware,
TruthGuard demonstrates that trustworthy, verifiable AI is feasible without reliance on proprietary cloud APIs.

I want to express my sincere gratitude to my supervisor, Dr. Suja Golden Shiny, and to the respected defense committee for your time and guidance.
I am now open to your questions and feedback. Thank you.
""")

    # =========================================================================
    # MASTER BUILD METHOD
    # =========================================================================
    def build_presentation(self):
        print("Presentation builder initialized. Generating 12 widescreen slides...")
        self.build_slide_1()
        self.build_slide_2()
        self.build_slide_3()
        self.build_slide_4()
        self.build_slide_5()
        self.build_slide_6()
        self.build_slide_7()
        self.build_slide_8()
        self.build_slide_9()
        self.build_slide_10()
        self.build_slide_11()
        self.build_slide_12()

        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(PPTX_OUTPUT))
        print(f"Successfully generated PowerPoint presentation at: {PPTX_OUTPUT}")

        # Native COM PDF export if on Windows
        try:
            import win32com.client
            import pythoncom
            pythoncom.CoInitialize()
            powerpoint = win32com.client.Dispatch("PowerPoint.Application")
            deck = powerpoint.Presentations.Open(str(PPTX_OUTPUT.resolve()), WithWindow=False)
            deck.SaveAs(str(PDF_OUTPUT.resolve()), 32)  # 32 = ppSaveAsPDF
            deck.Close()
            powerpoint.Quit()
            print(f"Successfully exported PDF presentation preview at: {PDF_OUTPUT}")
        except Exception as e:
            print(f"PowerPoint COM PDF export skipped/failed: {e}")

        print("Master Presentation Redesign Complete!")


if __name__ == "__main__":
    builder = PresentationBuilder()
    builder.build_presentation()
