"""
TruthGuard Professional Research Project Presentation Generator
Generates a 12-slide, 16:9 widescreen, publication-grade PowerPoint presentation
for B.Tech Artificial Intelligence and Data Analytics project defense.
"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Initialize presentation with 16:9 widescreen format
prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Color Palette Constants
COLOR_NAVY_HERO = RGBColor(10, 25, 47)      # #0A192F (Dark background for Title & Conclusion)
COLOR_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A (Primary dark slate text/elements)
COLOR_NAVY_CARD = RGBColor(24, 39, 64)      # #182740 (Card background on dark slides)
COLOR_WHITE = RGBColor(255, 255, 255)       # #FFFFFF (Pure white)
COLOR_BG_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC (Light slide canvas)
COLOR_CARD_LIGHT = RGBColor(255, 255, 255)  # #FFFFFF (Card background on light slides)
COLOR_BORDER_LIGHT = RGBColor(226, 232, 240)# #E2E8F0 (Subtle border)
COLOR_CYAN_ACCENT = RGBColor(6, 182, 212)   # #06B6D4 (Vibrant cyan)
COLOR_BLUE_ACCENT = RGBColor(14, 165, 233)  # #0EA5E9 (Sky blue)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B (Cool gray)
COLOR_GREEN = RGBColor(16, 185, 129)        # #10B981 (Supported)
COLOR_RED = RGBColor(239, 68, 68)           # #EF4444 (Contradicted)
COLOR_AMBER = RGBColor(245, 158, 11)        # #F59E0B (Insufficient Evidence)

FONT_HEADING = "Trebuchet MS"
FONT_BODY = "Calibri"
FONT_CODE = "Consolas"

# Asset Paths
FIG_DIR = "docs/figures/extracted"
FIG3_1 = os.path.join(FIG_DIR, "image1.png")
FIG3_2 = os.path.join(FIG_DIR, "image2.png")
FIG3_3 = os.path.join(FIG_DIR, "image3.png")
FIG3_4 = os.path.join(FIG_DIR, "image4.png")
FIG3_5 = os.path.join(FIG_DIR, "image5.png")
FIG4_1 = os.path.join(FIG_DIR, "image6.png")
FIG4_2 = "docs/figures/fig4_2_latency_breakdown.png"

# ==============================================================================
# Helper Functions
# ==============================================================================

def set_slide_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_header(slide, category_text, title_text, dark_mode=False):
    # Category Pill
    pill_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.35))
    tf_p = pill_box.text_frame
    tf_p.word_wrap = True
    p_p = tf_p.paragraphs[0]
    p_p.text = category_text.upper()
    p_p.font.name = FONT_BODY
    p_p.font.size = Pt(10)
    p_p.font.bold = True
    p_p.font.color.rgb = COLOR_CYAN_ACCENT

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE if dark_mode else COLOR_NAVY_DARK

    # Subtle horizontal line divider
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Pt(1.5))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_BLUE_ACCENT if dark_mode else COLOR_BORDER_LIGHT
    line.line.fill.background()

def add_footer(slide, current_idx, total_slides=12, dark_mode=False):
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.35))
    tf = footer_box.text_frame
    p = tf.paragraphs[0]
    p.text = "TruthGuard: Explainable NLP Hallucination Verification Framework | B.Tech Capstone Defense"
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MUTED

    num_box = slide.shapes.add_textbox(Inches(11.0), Inches(7.05), Inches(1.5), Inches(0.35))
    tf_num = num_box.text_frame
    p_num = tf_num.paragraphs[0]
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.text = f"{current_idx} / {total_slides}"
    p_num.font.name = FONT_BODY
    p_num.font.size = Pt(9.5)
    p_num.font.bold = True
    p_num.font.color.rgb = COLOR_CYAN_ACCENT if dark_mode else COLOR_TEXT_MUTED

def add_card(slide, left, top, width, height, bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT, border_width=1):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card

def add_speaker_notes(slide, text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = text.strip()

print("Presentation builder initialized. Generating 12 widescreen slides...")

# ==============================================================================
# SLIDE 1 — TITLE SLIDE
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
set_slide_background(slide1, COLOR_NAVY_HERO)

# Decorative cyan glow accent
accent_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.0), Inches(1.2), Pt(4))
accent_bar.fill.solid()
accent_bar.fill.fore_color.rgb = COLOR_CYAN_ACCENT
accent_bar.line.fill.background()

# Title Category
cat_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.5), Inches(0.4))
tf_cat = cat_box.text_frame
p_cat = tf_cat.paragraphs[0]
p_cat.text = "B.TECH CAPSTONE PROJECT DEFENSE | ARTIFICIAL INTELLIGENCE & DATA ANALYTICS"
p_cat.font.name = FONT_BODY
p_cat.font.size = Pt(11)
p_cat.font.bold = True
p_cat.font.color.rgb = COLOR_CYAN_ACCENT

# Main Project Title
t_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(1.8))
tf_t = t_box.text_frame
tf_t.word_wrap = True
p_t1 = tf_t.paragraphs[0]
p_t1.text = "TRUTHGUARD"
p_t1.font.name = FONT_HEADING
p_t1.font.size = Pt(40)
p_t1.font.bold = True
p_t1.font.color.rgb = COLOR_WHITE

p_t2 = tf_t.add_paragraph()
p_t2.text = "An Explainable Framework for Hallucination Detection, Multi-Source Evidence Verification, and Evidence-Grounded Automatic Correction in Large Language Model Responses"
p_t2.font.name = FONT_BODY
p_t2.font.size = Pt(16)
p_t2.font.color.rgb = RGBColor(203, 213, 225)
p_t2.space_before = Pt(8)

# Metadata Card Grid (Left: Candidate & Guide | Right: Department & Institute)
add_card(slide1, Inches(0.8), Inches(3.9), Inches(5.6), Inches(2.6), bg_color=COLOR_NAVY_CARD, border_color=RGBColor(51, 65, 85))
meta_left = slide1.shapes.add_textbox(Inches(1.0), Inches(4.05), Inches(5.2), Inches(2.3))
tf_ml = meta_left.text_frame
tf_ml.word_wrap = True

p_ml1 = tf_ml.paragraphs[0]
p_ml1.text = "SUBMITTED BY"
p_ml1.font.size = Pt(9.5)
p_ml1.font.bold = True
p_ml1.font.color.rgb = COLOR_CYAN_ACCENT

p_ml2 = tf_ml.add_paragraph()
p_ml2.text = "BHARATHRAM K"
p_ml2.font.size = Pt(15)
p_ml2.font.bold = True
p_ml2.font.color.rgb = COLOR_WHITE

p_ml3 = tf_ml.add_paragraph()
p_ml3.text = "Register No.: E0324006 | Branch: CSE (AIDA)"
p_ml3.font.size = Pt(11)
p_ml3.font.color.rgb = RGBColor(148, 163, 184)
p_ml3.space_after = Pt(12)

p_ml4 = tf_ml.add_paragraph()
p_ml4.text = "PROJECT SUPERVISOR & GUIDE"
p_ml4.font.size = Pt(9.5)
p_ml4.font.bold = True
p_ml4.font.color.rgb = COLOR_CYAN_ACCENT

p_ml5 = tf_ml.add_paragraph()
p_ml5.text = "Dr. SUJA GOLDEN SHINY S"
p_ml5.font.size = Pt(13)
p_ml5.font.bold = True
p_ml5.font.color.rgb = COLOR_WHITE

p_ml6 = tf_ml.add_paragraph()
p_ml6.text = "Assistant Professor, Department of CSE (AIDA)"
p_ml6.font.size = Pt(10.5)
p_ml6.font.color.rgb = RGBColor(148, 163, 184)

# Right Metadata Card
add_card(slide1, Inches(6.8), Inches(3.9), Inches(5.7), Inches(2.6), bg_color=COLOR_NAVY_CARD, border_color=RGBColor(51, 65, 85))
meta_right = slide1.shapes.add_textbox(Inches(7.0), Inches(4.05), Inches(5.3), Inches(2.3))
tf_mr = meta_right.text_frame
tf_mr.word_wrap = True

p_mr1 = tf_mr.paragraphs[0]
p_mr1.text = "INSTITUTION & DEPARTMENT"
p_mr1.font.size = Pt(9.5)
p_mr1.font.bold = True
p_mr1.font.color.rgb = COLOR_CYAN_ACCENT

p_mr2 = tf_mr.add_paragraph()
p_mr2.text = "Department of Computer Science & Engineering\n(Artificial Intelligence and Data Analytics)"
p_mr2.font.size = Pt(12.5)
p_mr2.font.bold = True
p_mr2.font.color.rgb = COLOR_WHITE
p_mr2.space_before = Pt(4)
p_mr2.space_after = Pt(8)

p_mr3 = tf_mr.add_paragraph()
p_mr3.text = "Sri Ramachandra Faculty of Engineering and Technology (SRET)\nSri Ramachandra Institute of Higher Education and Research\nPorur, Chennai – 600 116, Tamil Nadu, India"
p_mr3.font.size = Pt(10.5)
p_mr3.font.color.rgb = RGBColor(148, 163, 184)
p_mr3.space_after = Pt(8)

p_mr4 = tf_mr.add_paragraph()
p_mr4.text = "ACADEMIC YEAR: 2026 – 2027"
p_mr4.font.size = Pt(10)
p_mr4.font.bold = True
p_mr4.font.color.rgb = COLOR_CYAN_ACCENT

add_footer(slide1, 1, 12, dark_mode=True)
add_speaker_notes(slide1, 
    "Good morning respected members of the evaluation committee, project supervisor Dr. Suja Golden Shiny, and faculty members. "
    "I am Bharathram K (Reg. No. E0324006), final year B.Tech student in Computer Science and Engineering specializing in Artificial Intelligence and Data Analytics. "
    "Today, I present my capstone project defense titled 'TruthGuard: An Explainable Framework for Hallucination Detection, Multi-Source Evidence Verification, and Evidence-Grounded Automatic Correction in LLM Responses'. "
    "In this presentation, I will walk you through the architectural design, algorithmic formulations, empirical benchmarks on the FEVER dataset, and live demonstrations of our locally deployed verification framework."
)

# ==============================================================================
# SLIDE 2 — ABSTRACT & PROBLEM STATEMENT
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
set_slide_background(slide2, COLOR_BG_LIGHT)
add_header(slide2, "RESEARCH CONTEXT & PROBLEM STATEMENT", "The LLM Hallucination Dilemma in High-Stakes Deployments")

# 4 Key Problem Statement Cards (2x2 Grid)
cards_data_s2 = [
    ("The Generative Hallucination Crisis", 
     "Contemporary Large Language Models (LLMs) synthesize grammatically fluent, highly persuasive responses that frequently contain fabricated assertions, erroneous dates, invented citations, and demonstrably false empirical claims.", 
     COLOR_RED),
    ("Catastrophic Domain Risks", 
     "In mission-critical domains such as clinical medicine, legal contracts, avionics, and financial analysis, ungrounded LLM outputs introduce severe liability, regulatory non-compliance, and direct hazards to human life.", 
     COLOR_AMBER),
    ("Limitations of 'LLM-as-a-Judge'", 
     "Mainstream commercial pipelines rely on prompt-based LLM evaluators (e.g., GPT-4-as-a-judge). These introduce massive token costs, latency spikes (>3s), non-deterministic scoring, data leakage, and suffer from self-hallucination.", 
     COLOR_NAVY_DARK),
    ("The TruthGuard Paradigm Shift", 
     "TruthGuard resolves this via an explainable, deterministic NLP pipeline: atomic claim decomposition, FAISS inner-product dense retrieval, calibrated cross-encoder NLI, and closed-loop local self-correction executing on commodity hardware.", 
     COLOR_GREEN)
]

for idx, (title, desc, accent) in enumerate(cards_data_s2):
    r = idx // 2
    c = idx % 2
    left = Inches(0.8 + c * 5.95)
    top = Inches(1.6 + r * 2.55)
    add_card(slide2, left, top, Inches(5.75), Inches(2.35), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    
    # Left accent strip
    strip = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Pt(4), Inches(2.35))
    strip.fill.solid()
    strip.fill.fore_color.rgb = accent
    strip.line.fill.background()

    tb = slide2.shapes.add_textbox(left + Inches(0.25), top + Inches(0.15), Inches(5.3), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_NAVY_DARK

    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = RGBColor(51, 65, 85)
    p2.space_before = Pt(6)

add_footer(slide2, 2, 12)
add_speaker_notes(slide2,
    "Slide 2 establishes the fundamental motivation behind TruthGuard. While modern LLMs produce syntactically impeccable language, they lack an internal representation of ground truth, operating fundamentally as probabilistic next-token predictors. "
    "In high-stakes enterprise applications, relying on an unverified LLM is untenable. Current industry solutions predominantly use monolithic prompt-based LLM-as-a-judge architectures. "
    "However, our audit revealed three fatal drawbacks: first, LLM judges frequently hallucinate during evaluation; second, they conflate unverified assertions with factual contradictions; and third, they transmit sensitive proprietary context to external cloud APIs. "
    "TruthGuard introduces a ground-truth anchored framework designed from first principles for deterministic local verification."
)

# ==============================================================================
# SLIDE 3 — OBJECTIVES & RESEARCH GAP
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
set_slide_background(slide3, COLOR_BG_LIGHT)
add_header(slide3, "RESEARCH FOUNDATION", "Identified Research Gaps & TruthGuard Objectives")

# Left Column: Research Gaps Contrast Table (Inches(0.8) to Inches(6.5))
add_card(slide3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_gap = slide3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
tf_gap = tb_gap.text_frame
tf_gap.word_wrap = True

p_g0 = tf_gap.paragraphs[0]
p_g0.text = "CRITICAL LIMITATIONS IN EXISTING APPROACHES"
p_g0.font.name = FONT_HEADING
p_g0.font.size = Pt(12)
p_g0.font.bold = True
p_g0.font.color.rgb = COLOR_RED
p_g0.space_after = Pt(8)

gaps = [
    ("Coarse Document-Level Verification: ", "Existing tools audit entire passages holistically, failing to pinpoint the exact clause or sentence responsible for factual falsehoods."),
    ("Conflation of Uncertainty & Falsehood: ", "Standard benchmarks treat 'insufficient evidence' identically to 'direct factual contradictions', distorting reliability metrics."),
    ("Open-Loop Detection Without Remedy: ", "State-of-the-art detectors merely flag errors, abandoning users without verifiable, evidence-grounded corrections."),
    ("Hardware Inaccessibility & Cloud Lock-in: ", "Current multi-agent consensus networks require multi-GPU cloud clusters, preventing private edge deployment.")
]

for title, desc in gaps:
    p = tf_gap.add_paragraph()
    r1 = p.add_run()
    r1.text = "• " + title
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_NAVY_DARK
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(8)

# Right Column: TruthGuard 5 Core Objectives (Inches(6.7) to Inches(12.5))
add_card(slide3, Inches(6.7), Inches(1.6), Inches(5.8), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_obj = slide3.shapes.add_textbox(Inches(6.9), Inches(1.8), Inches(5.4), Inches(4.7))
tf_obj = tb_obj.text_frame
tf_obj.word_wrap = True

p_o0 = tf_obj.paragraphs[0]
p_o0.text = "TRUTHGUARD CORE TECHNICAL OBJECTIVES"
p_o0.font.name = FONT_HEADING
p_o0.font.size = Pt(12)
p_o0.font.bold = True
p_o0.font.color.rgb = COLOR_BLUE_ACCENT
p_o0.space_after = Pt(8)

objectives = [
    ("1. Syntactic Atomic Claim Decomposition: ", "Decompose multi-sentence text into single testable assertions while tracking exact character spans [start, end]."),
    ("2. Multi-Source Dense FAISS Vector Retrieval: ", "Index reference corpus via L2-normalized 384-d embeddings (MiniLM-L6) and exact inner-product search (IndexFlatIP)."),
    ("3. Calibrated Cross-Encoder NLI Inference: ", "Deploy DeBERTa-v3 cross-encoder with calibrated entailment (0.55) and contradiction (0.50) decision thresholds."),
    ("4. Deterministic Arbitration & Risk Index: ", "Formulate an explainable 4-way decision matrix and a mathematically bounded composite hallucination risk score in [0.0, 1.0]."),
    ("5. Closed-Loop Generative Correction: ", "Constrain a local 4-bit LLM (qwen3:8b) to rewrite contradicted spans and automatically re-verify the output closed-loop.")
]

for title, desc in objectives:
    p = tf_obj.add_paragraph()
    r1 = p.add_run()
    r1.text = title
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_NAVY_DARK
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(8)

add_footer(slide3, 3, 12)
add_speaker_notes(slide3,
    "On Slide 3, we contrast the major research gaps in existing literature with TruthGuard's five foundational objectives. "
    "Current hallucination detectors suffer from coarse paragraph granularity: when an entire answer is flagged as false, human auditors cannot tell which specific assertion failed. "
    "TruthGuard solves this by extracting atomic propositions and tracking exact character offsets. Furthermore, we address the critical distinction between lack of evidence and direct contradiction. "
    "Finally, our fifth objective introduces a closed-loop generative repair engine that ensures the corrected response is re-audited before being returned to the user."
)

# ==============================================================================
# SLIDE 4 — PROPOSED SYSTEM ARCHITECTURE (Figure 3.1)
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
set_slide_background(slide4, COLOR_BG_LIGHT)
add_header(slide4, "SYSTEM METHODOLOGY & WORKFLOW", "TruthGuard End-to-End System Architecture Pipeline")

# Left Column: Figure 3.1 Diagram Image
if os.path.exists(FIG3_1):
    add_card(slide4, Inches(0.8), Inches(1.6), Inches(7.2), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    slide4.shapes.add_picture(FIG3_1, Inches(0.9), Inches(1.7), width=Inches(7.0))
    # Caption
    c_box = slide4.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(7.0), Inches(0.35))
    tf_c = c_box.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    p_c.text = "Figure 3.1: Sequential End-to-End TruthGuard Verification & Correction Pipeline"
    p_c.font.size = Pt(9.5)
    p_c.font.italic = True
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED

# Right Column: Architectural Highlights Cards
add_card(slide4, Inches(8.2), Inches(1.6), Inches(4.3), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_arch = slide4.shapes.add_textbox(Inches(8.35), Inches(1.75), Inches(4.0), Inches(4.8))
tf_a = tb_arch.text_frame
tf_a.word_wrap = True

p_a0 = tf_a.paragraphs[0]
p_a0.text = "PIPELINE EXECUTION STAGES"
p_a0.font.name = FONT_HEADING
p_a0.font.size = Pt(12)
p_a0.font.bold = True
p_a0.font.color.rgb = COLOR_BLUE_ACCENT
p_a0.space_after = Pt(8)

stages = [
    ("Stage 1: Syntactic Claim Decomposition", "Extracts atomic factual statements and binds character coordinates [start, end] for surgical attribution.", COLOR_BLUE_ACCENT),
    ("Stage 2: Multi-Source Vector Retrieval", "FAISS IndexFlatIP searches 384-d L2-normalized embeddings over Wikipedia and uploaded private libraries.", COLOR_CYAN_ACCENT),
    ("Stage 3: Calibrated Cross-Encoder NLI", "DeBERTa-v3 pairs claim with retrieved evidence, executing full pairwise cross-attention logits inference.", COLOR_GREEN),
    ("Stage 4: Closed-Loop Generative Repair", "Local Ollama LLM (qwen3:8b) rewrites refuted spans; pipeline re-verifies revised text closed-loop.", COLOR_AMBER)
]

for title, desc, col in stages:
    p = tf_a.add_paragraph()
    r1 = p.add_run()
    r1.text = "■ " + title + "\n"
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = col
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(8)

add_footer(slide4, 4, 12)
add_speaker_notes(slide4,
    "Slide 4 presents the complete end-to-end architectural pipeline of TruthGuard, visualized in Figure 3.1. "
    "The pipeline operates across four sequential stages: First, raw model generation enters the syntactic preprocessing layer where compound assertions are decomposed into atomic claims. "
    "Second, each claim is projected into dense embedding space via MiniLM and searched across our FAISS vector index. "
    "Third, top-k evidence passages are coupled with the claim and evaluated by our DeBERTa cross-encoder to compute calibrated softmax arbitration. "
    "Finally, if contradictions are identified, our closed-loop grounded correction module triggers local Ollama inference to rewrite the contradictory span while enforcing provenance citations."
)

# ==============================================================================
# SLIDE 5 — ATOMIC CLAIM DECOMPOSITION (Figure 3.2)
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
set_slide_background(slide5, COLOR_BG_LIGHT)
add_header(slide5, "PIPELINE STAGE 1", "Syntactic Atomic Claim Decomposition & Character Span Tracking")

# Left Column: Figure 3.2
if os.path.exists(FIG3_2):
    add_card(slide5, Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    slide5.shapes.add_picture(FIG3_2, Inches(0.9), Inches(1.75), width=Inches(6.6))
    c_box = slide5.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(6.6), Inches(0.35))
    tf_c = c_box.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    p_c.text = "Figure 3.2: Atomic Claim Decomposition & Span Attribution Workflow"
    p_c.font.size = Pt(9.5)
    p_c.font.italic = True
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED

# Right Column: Technical Details & Concrete Example
add_card(slide5, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_c5 = slide5.shapes.add_textbox(Inches(8.0), Inches(1.75), Inches(4.3), Inches(4.8))
tf_c5 = tb_c5.text_frame
tf_c5.word_wrap = True

p_c0 = tf_c5.paragraphs[0]
p_c0.text = "DECOMPOSITION METHODOLOGY"
p_c0.font.name = FONT_HEADING
p_c0.font.size = Pt(12)
p_c0.font.bold = True
p_c0.font.color.rgb = COLOR_BLUE_ACCENT
p_c0.space_after = Pt(6)

c5_points = [
    ("Surgical Proposition Extraction: ", "Complex responses containing multiple conjuncts ('and', 'while', 'but') are broken into isolated atomic propositions, preventing true statements from masking falsehoods."),
    ("Character-Level Span Attribution: ", "TruthGuard tracks exact byte offsets [start_char, end_char]. This enables fine-grained UI highlighting and allows our correction engine to replace only refuted text."),
    ("Verifiability Gating: ", "Distinguishes empirical factual assertions from subjective beliefs or greetings. Non-empirical claims are safely categorized as unverifiable rather than penalized as false.")
]

for title, desc in c5_points:
    p = tf_c5.add_paragraph()
    r1 = p.add_run()
    r1.text = "• " + title
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_NAVY_DARK
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(6)

# Example Box inside right column
ex_card = add_card(slide5, Inches(8.0), Inches(4.85), Inches(4.3), Inches(1.65), bg_color=COLOR_BG_LIGHT, border_color=COLOR_BLUE_ACCENT)
tb_ex = slide5.shapes.add_textbox(Inches(8.1), Inches(4.9), Inches(4.1), Inches(1.5))
tf_ex = tb_ex.text_frame
tf_ex.word_wrap = True
p_e1 = tf_ex.paragraphs[0]
p_e1.text = "DECOMPOSITION WALKTHROUGH EXAMPLE:"
p_e1.font.size = Pt(9)
p_e1.font.bold = True
p_e1.font.color.rgb = COLOR_BLUE_ACCENT

p_e2 = tf_ex.add_paragraph()
p_e2.text = "Input: 'Marie Curie discovered radium in 1898 and won 5 Nobel Prizes.'"
p_e2.font.size = Pt(9)
p_e2.font.italic = True
p_e2.font.color.rgb = COLOR_NAVY_DARK

p_e3 = tf_ex.add_paragraph()
p_e3.text = "→ Claim 1: 'Marie Curie discovered radium in 1898' [0, 40]\n→ Claim 2: 'won five Nobel Prizes' [45, 65]"
p_e3.font.name = FONT_CODE
p_e3.font.size = Pt(8.5)
p_e3.font.color.rgb = COLOR_NAVY_DARK

add_footer(slide5, 5, 12)
add_speaker_notes(slide5,
    "Slide 5 details Stage 1: Atomic Claim Decomposition. In natural text, multiple claims are routinely joined using conjunctions. "
    "If an LLM says 'Marie Curie discovered radium and won 5 Nobel Prizes', half the sentence is true while the second half is an egregious hallucination. "
    "TruthGuard's syntactic parsing breaks this sentence into discrete claims and records their exact character boundaries. "
    "As shown in Figure 3.2, character span tracking is essential: it allows our frontend to apply colored highlighting and ensures that our downstream correction module rewrites only the corrupted substring."
)

# ==============================================================================
# SLIDE 6 — EVIDENCE RETRIEVAL AND FAISS (Figure 3.3)
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
set_slide_background(slide6, COLOR_BG_LIGHT)
add_header(slide6, "PIPELINE STAGE 2", "Dense Semantic Vector Retrieval & FAISS Inner Product Search")

# Left Column: Figure 3.3
if os.path.exists(FIG3_3):
    add_card(slide6, Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    slide6.shapes.add_picture(FIG3_3, Inches(0.9), Inches(1.75), width=Inches(6.6))
    c_box = slide6.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(6.6), Inches(0.35))
    tf_c = c_box.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    p_c.text = "Figure 3.3: Dense Vector Retrieval & FAISS Inner Product Search in Unit Hypersphere"
    p_c.font.size = Pt(9.5)
    p_c.font.italic = True
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED

# Right Column: Retrieval Mathematics & Performance
add_card(slide6, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_c6 = slide6.shapes.add_textbox(Inches(8.0), Inches(1.75), Inches(4.3), Inches(4.8))
tf_c6 = tb_c6.text_frame
tf_c6.word_wrap = True

p_r0 = tf_c6.paragraphs[0]
p_r0.text = "VECTOR RETRIEVAL FORMULATION"
p_r0.font.name = FONT_HEADING
p_r0.font.size = Pt(12)
p_r0.font.bold = True
p_r0.font.color.rgb = COLOR_BLUE_ACCENT
p_r0.space_after = Pt(6)

ret_points = [
    ("Dense Embedding Engine: ", "Passages and claim hypotheses are mapped into a 384-dimensional continuous vector space using sentence-transformers/all-MiniLM-L6-v2."),
    ("Unit-Hypersphere Normalization: ", "Every passage vector v and query vector q is L2-normalized: q̂ = q / ||q||_2, v̂ = v / ||v||_2."),
    ("Exact Inner Product Matching: ", "Configured via faiss.IndexFlatIP(384). Because vectors are unit normalized, inner product evaluation equals exact cosine similarity: sim(q, v) = q̂ · v̂ = cos(θ)."),
    ("Calibrated Similarity Gating: ", "Top-k candidate evidence passages are filtered with similarity threshold tau_sim = 0.25, eliminating noisy irrelevant context."),
    ("Zero-Leakage Provenance: ", "Every retrieved chunk maintains explicit pointers to source document name, page number, and chunk offset.")
]

for title, desc in ret_points:
    p = tf_c6.add_paragraph()
    r1 = p.add_run()
    r1.text = "• " + title
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_NAVY_DARK
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(6)

add_footer(slide6, 6, 12)
add_speaker_notes(slide6,
    "Slide 6 covers Stage 2: Dense Semantic Vector Retrieval in FAISS. Rather than relying on fragile keyword matching like BM25 alone, TruthGuard projects all passages into a 384-dimensional latent semantic space using MiniLM-L6. "
    "A key engineering optimization here is our unit hypersphere L2-normalization: by normalizing both query and passage vectors to unit length, FAISS's IndexFlatIP inner product search mathematically equals exact cosine similarity. "
    "This yields sub-10ms retrieval latency over thousands of passages while achieving 100% Recall@3 on the FEVER benchmark. "
    "Passages falling below our calibrated similarity threshold of 0.25 are discarded to protect against noisy evidence injection."
)

# ==============================================================================
# SLIDE 7 — NLI VERIFICATION & DECISION LOGIC (Figure 3.4)
# ==============================================================================
slide7 = prs.slides.add_slide(blank_layout)
set_slide_background(slide7, COLOR_BG_LIGHT)
add_header(slide7, "PIPELINE STAGE 3", "Cross-Encoder Natural Language Inference & Multi-Evidence Arbitration")

# Left Column: Figure 3.4
if os.path.exists(FIG3_4):
    add_card(slide7, Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    slide7.shapes.add_picture(FIG3_4, Inches(0.9), Inches(1.75), width=Inches(6.6))
    c_box = slide7.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(6.6), Inches(0.35))
    tf_c = c_box.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    p_c.text = "Figure 3.4: Cross-Encoder NLI Softmax Arbitration & Multi-Evidence Decision Matrix"
    p_c.font.size = Pt(9.5)
    p_c.font.italic = True
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED

# Right Column: Arbitration Policy & Risk Index
add_card(slide7, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_c7 = slide7.shapes.add_textbox(Inches(8.0), Inches(1.75), Inches(4.3), Inches(4.8))
tf_c7 = tb_c7.text_frame
tf_c7.word_wrap = True

p_n0 = tf_c7.paragraphs[0]
p_n0.text = "CROSS-ATTENTION ARBITRATION MATRIX"
p_n0.font.name = FONT_HEADING
p_n0.font.size = Pt(11.5)
p_n0.font.bold = True
p_n0.font.color.rgb = COLOR_BLUE_ACCENT
p_n0.space_after = Pt(4)

nli_states = [
    ("SUPPORTED (Green)", "max P(entailment) >= 0.55 across retrieved evidence passages.", COLOR_GREEN),
    ("CONTRADICTED (Red)", "max P(contradiction) >= 0.50 without conflicting entailment.", COLOR_RED),
    ("CONFLICTING EVIDENCE", "Distinct retrieved passages yield both strong entailment and strong contradiction.", COLOR_BLUE_ACCENT),
    ("INSUFFICIENT EVIDENCE (Amber)", "No evidence candidate reaches threshold, or claim is subjective. Confidence set to null.", COLOR_AMBER)
]

for title, desc, col in nli_states:
    p = tf_c7.add_paragraph()
    r1 = p.add_run()
    r1.text = "■ " + title + ": "
    r1.font.bold = True
    r1.font.size = Pt(9.5)
    r1.font.color.rgb = col
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(4)

# Risk Formula Callout
risk_box = add_card(slide7, Inches(8.0), Inches(4.8), Inches(4.3), Inches(1.7), bg_color=COLOR_BG_LIGHT, border_color=COLOR_CYAN_ACCENT)
tb_r = slide7.shapes.add_textbox(Inches(8.1), Inches(4.85), Inches(4.1), Inches(1.6))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p_rf1 = tf_r.paragraphs[0]
p_rf1.text = "COMPOSITE HALLUCINATION RISK SCORE:"
p_rf1.font.size = Pt(9)
p_rf1.font.bold = True
p_rf1.font.color.rgb = COLOR_BLUE_ACCENT

p_rf2 = tf_r.add_paragraph()
p_rf2.text = "S_risk = min(1.0,  0.70·R_contra + 0.30·R_unsupported)"
p_rf2.font.name = FONT_CODE
p_rf2.font.size = Pt(9.5)
p_rf2.font.bold = True
p_rf2.font.color.rgb = COLOR_NAVY_DARK

p_rf3 = tf_r.add_paragraph()
p_rf3.text = "Direct contradictions are heavily penalized (70% weight); unverified claims incur proportionate moderate penalty (30% weight), guaranteeing a strictly bounded score in [0.0, 1.0]."
p_rf3.font.size = Pt(8.5)
p_rf3.font.color.rgb = RGBColor(71, 85, 105)

add_footer(slide7, 7, 12)
add_speaker_notes(slide7,
    "Slide 7 describes Stage 3: Calibrated Cross-Encoder Natural Language Inference. Unlike dual bi-encoders that process texts separately, our DeBERTa cross-encoder concatenates premise and hypothesis into a single sequence, allowing full pairwise cross-attention. "
    "The model outputs unnormalized logits across contradiction, entailment, and neutral. "
    "Crucially, our multi-evidence arbitration policy resolves cases where multiple passages return conflicting signals. "
    "When evidence is absent, TruthGuard honestly assigns 'Insufficient Evidence' with an uncalibrated null confidence rather than guessing. "
    "Finally, our composite Hallucination Risk Score penalizes direct falsehoods at 70% weight while treating unverified claims at 30% weight."
)

# ==============================================================================
# SLIDE 8 — EVIDENCE-GROUNDED CORRECTION (Figure 3.5)
# ==============================================================================
slide8 = prs.slides.add_slide(blank_layout)
set_slide_background(slide8, COLOR_BG_LIGHT)
add_header(slide8, "PIPELINE STAGE 4", "Closed-Loop Grounded Generative Correction & Re-Verification")

# Left Column: Figure 3.5
if os.path.exists(FIG3_5):
    add_card(slide8, Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    slide8.shapes.add_picture(FIG3_5, Inches(0.9), Inches(1.75), width=Inches(6.6))
    c_box = slide8.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(6.6), Inches(0.35))
    tf_c = c_box.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    p_c.text = "Figure 3.5: Closed-Loop Grounded Correction & Automated Re-Verification Audit"
    p_c.font.size = Pt(9.5)
    p_c.font.italic = True
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED

# Right Column: The Correction Feedback Loop
add_card(slide8, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_c8 = slide8.shapes.add_textbox(Inches(8.0), Inches(1.75), Inches(4.3), Inches(4.8))
tf_c8 = tb_c8.text_frame
tf_c8.word_wrap = True

p_corr0 = tf_c8.paragraphs[0]
p_corr0.text = "CLOSED-LOOP CORRECTION MECHANISM"
p_corr0.font.name = FONT_HEADING
p_corr0.font.size = Pt(11.5)
p_corr0.font.bold = True
p_corr0.font.color.rgb = COLOR_BLUE_ACCENT
p_corr0.space_after = Pt(6)

corr_steps = [
    ("Targeted Evidence Prompting: ", "When contradicted claims are detected during arbitration, TruthGuard constructs a constrained revision prompt containing only the contradicted spans and retrieved verified reference passages."),
    ("Surgical Text Rewriting: ", "A local 4-bit instruction-tuned LLM (qwen3:8b via Ollama) rewrites only the corrupted substrings, preserving verified facts and embedding mandatory citations [Source: {doc}, p. {page}]."),
    ("Automated Re-Verification Audit: ", "Crucially, the revised response is automatically re-routed through TruthGuard's full verification pipeline in a closed loop."),
    ("Zero-Contradiction Guarantee: ", "The report is delivered to the client only after the automated re-verification audit mathematically confirms exactly 0 residual contradictions.")
]

for title, desc in corr_steps:
    p = tf_c8.add_paragraph()
    r1 = p.add_run()
    r1.text = "• " + title
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_NAVY_DARK
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(6)

add_footer(slide8, 8, 12)
add_speaker_notes(slide8,
    "Slide 8 illustrates Stage 4: Closed-Loop Grounded Correction. A fundamental shortcoming of existing fact-checking frameworks is that they operate in an open loop: they identify errors but take no corrective action. "
    "TruthGuard bridges this gap. When a contradiction is flagged, our system compiles the refuted spans alongside the verified evidence and instructs a local quantized Ollama model to perform a surgical rewrite. "
    "The crucial novelty is our closed-loop re-verification audit: we do not blindly trust the correction. "
    "The revised text is re-ingested, decomposed, and verified a second time. Only when the re-audit confirms zero contradictions is the final validated answer returned."
)

# ==============================================================================
# SLIDE 9 — DATASETS & IMPLEMENTATION ARCHITECTURE
# ==============================================================================
slide9 = prs.slides.add_slide(blank_layout)
set_slide_background(slide9, COLOR_BG_LIGHT)
add_header(slide9, "DATASETS & ENGINEERING IMPLEMENTATION", "Corpus Partitioning, Evaluation Benchmarks & Tech Stack")

# Left Column: Dual Role of Datasets (Inches(0.8) to Inches(6.5))
add_card(slide9, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_d9 = slide9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
tf_d9 = tb_d9.text_frame
tf_d9.word_wrap = True

p_d0 = tf_d9.paragraphs[0]
p_d0.text = "DUAL-ROLE DATASET ARCHITECTURE"
p_d0.font.name = FONT_HEADING
p_d0.font.size = Pt(12)
p_d0.font.bold = True
p_d0.font.color.rgb = COLOR_BLUE_ACCENT
p_d0.space_after = Pt(8)

data_roles = [
    ("Evaluation Benchmark Corpus (FEVER & HaluEval):", 
     "Used exclusively to evaluate classification accuracy, recall, and precision. FEVER contains 185,445 claims across SUPPORTS, REFUTES, and NOT ENOUGH INFO. HaluEval provides 35,000 hallucinated QA, dialogue, and summary pairs. Strictly segregated under zero-data-leakage protocols."),
    ("Evidence Retrieval Library (Knowledge Base):", 
     "The separate repository of truth against which claims are audited. Comprises uploaded enterprise documents (PDF, DOCX, TXT), technical manuals, and pre-indexed Wikipedia knowledge passages partitioned into 500-character chunks with 100-character sliding overlap.")
]

for title, desc in data_roles:
    p = tf_d9.add_paragraph()
    r1 = p.add_run()
    r1.text = title + "\n"
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_NAVY_DARK
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(10)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(12)

# Right Column: Full-Stack Technology Stack
add_card(slide9, Inches(6.7), Inches(1.6), Inches(5.8), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_st = slide9.shapes.add_textbox(Inches(6.9), Inches(1.8), Inches(5.4), Inches(4.7))
tf_st = tb_st.text_frame
tf_st.word_wrap = True

p_s0 = tf_st.paragraphs[0]
p_s0.text = "FULL-STACK TECHNOLOGY ECOSYSTEM"
p_s0.font.name = FONT_HEADING
p_s0.font.size = Pt(12)
p_s0.font.bold = True
p_s0.font.color.rgb = COLOR_CYAN_ACCENT
p_s0.space_after = Pt(6)

tech_stack = [
    ("NLP & Transformers", "PyTorch 2.2, Hugging Face Transformers, DeBERTa-v3-small (NLI), SpaCy 3.7 (NLP parsing)"),
    ("Vector Retrieval", "FAISS IndexFlatIP (Facebook AI), Sentence-Transformers all-MiniLM-L6-v2 (384-dim)"),
    ("Backend API & Runtime", "FastAPI (REST endpoints), Python 3.11, Uvicorn ASGI, Pydantic data schemas"),
    ("Generative LLM Runtime", "Ollama Engine, Qwen 2.5/3 (8B Instruct, 4-bit quantized, GPU accelerated)"),
    ("Modern Web Frontend", "React 19, TypeScript, Tailwind CSS, Vite, Lucide Icons, Framer Motion")
]

for layer, tools in tech_stack:
    p = tf_st.add_paragraph()
    r1 = p.add_run()
    r1.text = "■ " + layer + ":\n"
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_NAVY_DARK
    r2 = p.add_run()
    r2.text = tools
    r2.font.name = FONT_CODE
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(51, 65, 85)
    p.space_after = Pt(6)

add_footer(slide9, 9, 12)
add_speaker_notes(slide9,
    "Slide 9 clarifies an important distinction in our methodology: the dual role of datasets. "
    "We strictly distinguish between the evaluation benchmark datasets—specifically FEVER and HaluEval, which contain labeled claims used solely to test model accuracy—and our Evidence Library, which comprises reference documents indexed into FAISS. "
    "On the right, we highlight TruthGuard's full-stack technology ecosystem: a high-performance Python 3.11 and FastAPI backend orchestrating PyTorch and Hugging Face models, paired with a responsive React 19 TypeScript dashboard. "
    "Crucially, our local Ollama runtime allows local 4-bit inference, eliminating cloud dependencies."
)

# ==============================================================================
# SLIDE 10 — EXPERIMENTAL RESULTS (Figures 4.1 & 4.2)
# ==============================================================================
slide10 = prs.slides.add_slide(blank_layout)
set_slide_background(slide10, COLOR_BG_LIGHT)
add_header(slide10, "EMPIRICAL BENCHMARKS & EVALUATION", "Experimental Results on FEVER Benchmark & Latency Breakdown")

# Top Metrics Badges (4 cards across top)
metrics_top = [
    ("90.0%", "3-Class Accuracy", "FEVER Fact Verification Benchmark", COLOR_GREEN),
    ("89.9%", "Macro F1-Score", "Balanced across All 3 Classes", COLOR_BLUE_ACCENT),
    ("100.0%", "Recall@3 Evidence", "Gold Evidence in Top-3 Candidates", COLOR_CYAN_ACCENT),
    ("296.3 ms", "Warm Query Latency", "Interactive Sub-Second Response", COLOR_AMBER)
]

for idx, (val, label, sub, col) in enumerate(metrics_top):
    left = Inches(0.8 + idx * 2.98)
    add_card(slide10, left, Inches(1.5), Inches(2.8), Inches(1.2), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    tb_m = slide10.shapes.add_textbox(left + Inches(0.1), Inches(1.55), Inches(2.6), Inches(1.1))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    p1 = tf_m.paragraphs[0]
    p1.text = val
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = col
    
    p2 = tf_m.add_paragraph()
    p2.text = label
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_NAVY_DARK

    p3 = tf_m.add_paragraph()
    p3.text = sub
    p3.font.name = FONT_BODY
    p3.font.size = Pt(8)
    p3.font.color.rgb = COLOR_TEXT_MUTED

# Left Bottom: Figure 4.1 Confusion Matrix
if os.path.exists(FIG4_1):
    add_card(slide10, Inches(0.8), Inches(2.85), Inches(5.7), Inches(3.9), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    slide10.shapes.add_picture(FIG4_1, Inches(0.95), Inches(2.95), width=Inches(5.4))
    c_box = slide10.shapes.add_textbox(Inches(0.95), Inches(6.4), Inches(5.4), Inches(0.3))
    tf_c = c_box.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    p_c.text = "Figure 4.1: Empirical FEVER 3-Class Confusion Matrix Heatmap"
    p_c.font.size = Pt(9)
    p_c.font.italic = True
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED

# Right Bottom: Figure 4.2 Latency Breakdown
if os.path.exists(FIG4_2):
    add_card(slide10, Inches(6.8), Inches(2.85), Inches(5.7), Inches(3.9), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
    slide10.shapes.add_picture(FIG4_2, Inches(6.9), Inches(2.95), width=Inches(5.5))
    c_box2 = slide10.shapes.add_textbox(Inches(6.9), Inches(6.4), Inches(5.5), Inches(0.3))
    tf_c2 = c_box2.text_frame
    p_c2 = tf_c2.paragraphs[0]
    p_c2.alignment = PP_ALIGN.CENTER
    p_c2.text = "Figure 4.2: End-to-End Latency Breakdown Across Execution Stages"
    p_c2.font.size = Pt(9)
    p_c2.font.italic = True
    p_c2.font.bold = True
    p_c2.font.color.rgb = COLOR_TEXT_MUTED

add_footer(slide10, 10, 12)
add_speaker_notes(slide10,
    "Slide 10 presents our empirical evaluation results conducted on local workstation hardware. "
    "Evaluating against the standardized FEVER fact verification benchmark under strict zero-leakage conditions, TruthGuard achieved 90.0% multi-class accuracy and an 89.9% Macro F1-score. "
    "As shown in the confusion matrix on the left (Figure 4.1), TruthGuard demonstrates exceptional sensitivity on contradicted assertions, capturing 100% of factual falsehoods with zero false negatives. "
    "On the right (Figure 4.2), our latency profiling demonstrates a total warm verification latency of 296.3 milliseconds. "
    "While DeBERTa inference accounts for 96.3% of the time, executing on multi-core CPU threads preserves 100% of GPU VRAM for the local generative correction LLM."
)

# ==============================================================================
# SLIDE 11 — DEMONSTRATION, LIMITATIONS & FUTURE WORK
# ==============================================================================
slide11 = prs.slides.add_slide(blank_layout)
set_slide_background(slide11, COLOR_BG_LIGHT)
add_header(slide11, "SYSTEM DEMONSTRATION & ROADMAP", "Real-World Verification Demonstration, Limitations & Future Work")

# Left Column: Real-World Walkthrough (Marie Curie Case Study)
add_card(slide11, Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_w = slide11.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.4), Inches(4.8))
tf_w = tb_w.text_frame
tf_w.word_wrap = True

p_w0 = tf_w.paragraphs[0]
p_w0.text = "REAL-WORLD VERIFICATION WALKTHROUGH"
p_w0.font.name = FONT_HEADING
p_w0.font.size = Pt(12)
p_w0.font.bold = True
p_w0.font.color.rgb = COLOR_BLUE_ACCENT
p_w0.space_after = Pt(4)

p_w1 = tf_w.add_paragraph()
p_w1.text = "Query: 'What did Marie Curie discover and how many Nobel Prizes did she win?'"
p_w1.font.size = Pt(9.5)
p_w1.font.bold = True
p_w1.font.color.rgb = COLOR_NAVY_DARK

p_w2 = tf_w.add_paragraph()
p_w2.text = "Audited Answer: 'Marie Curie discovered radium in 1898 and won five Nobel Prizes. She was the greatest human ever born.'"
p_w2.font.size = Pt(9)
p_w2.font.italic = True
p_w2.font.color.rgb = RGBColor(100, 116, 139)
p_w2.space_after = Pt(6)

claims_demo = [
    ("[claim_001] Discovered Radium (1898): ", "SUPPORTED / Conflicting (99.8% conf). Passage verified discovery.", COLOR_GREEN),
    ("[claim_002] Won Five Nobel Prizes: ", "CONTRADICTED (99.7% conf). Gold passage proved 2 Nobel Prizes.", COLOR_RED),
    ("[claim_003] Greatest human ever born: ", "INSUFFICIENT EVIDENCE (null conf). Correctly flagged as subjective.", COLOR_AMBER)
]

for tag, desc, col in claims_demo:
    p = tf_w.add_paragraph()
    r1 = p.add_run()
    r1.text = tag
    r1.font.bold = True
    r1.font.size = Pt(9)
    r1.font.color.rgb = col
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(4)

p_w3 = tf_w.add_paragraph()
p_w3.text = "Risk Score: 65.0% | Contradiction Rate: 50.0% | Pipeline Latency: 578.4 ms"
p_w3.font.name = FONT_CODE
p_w3.font.size = Pt(8.5)
p_w3.font.bold = True
p_w3.font.color.rgb = COLOR_NAVY_DARK
p_w3.space_before = Pt(4)

p_w4 = tf_w.add_paragraph()
p_w4.text = "Grounded Revision: 'Marie Curie discovered radium in 1898 and was awarded two Nobel Prizes... [Source: Biography, p. 1]'\n→ Re-verification: 0 Contradictions remaining."
p_w4.font.size = Pt(9)
p_w4.font.bold = True
p_w4.font.color.rgb = COLOR_GREEN

# Right Column: Limitations & Future Work
add_card(slide11, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.1), bg_color=COLOR_WHITE, border_color=COLOR_BORDER_LIGHT)
tb_fw = slide11.shapes.add_textbox(Inches(7.1), Inches(1.75), Inches(5.2), Inches(4.8))
tf_fw = tb_fw.text_frame
tf_fw.word_wrap = True

p_f0 = tf_fw.paragraphs[0]
p_f0.text = "CURRENT LIMITATIONS & FUTURE ROADMAP"
p_f0.font.name = FONT_HEADING
p_f0.font.size = Pt(12)
p_f0.font.bold = True
p_f0.font.color.rgb = COLOR_CYAN_ACCENT
p_f0.space_after = Pt(6)

future_items = [
    ("Current Limitation — Single-Hop Retrieval: ", "Currently verifies claims against contiguous passages; lacks multi-hop relational chaining across independent documents."),
    ("Future 1: Multimodal Vision-Language Auditing: ", "Extending claim extraction and dense retrieval to audit charts, biomedical scans, and diagrams in Vision-Language Models (VLMs)."),
    ("Future 2: Graph-Guided Multi-Hop Reasoning: ", "Integrating knowledge graphs (Neo4j) to verify complex transitive inference chains across distributed corporate knowledge bases."),
    ("Future 3: INT8 Quantization via TensorRT: ", "Quantizing cross-encoder weights to 8-bit precision using ONNX Runtime to achieve sub-100ms verification latencies."),
    ("Future 4: Multi-Agent Autonomous Auditing: ", "Deploying TruthGuard as an autonomous critic agent within multi-agent consensus networks for real-time code and reasoning audits.")
]

for title, desc in future_items:
    p = tf_fw.add_paragraph()
    r1 = p.add_run()
    r1.text = "• " + title
    r1.font.bold = True
    r1.font.size = Pt(9.5)
    r1.font.color.rgb = COLOR_NAVY_DARK
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor(71, 85, 105)
    p.space_after = Pt(6)

add_footer(slide11, 11, 12)
add_speaker_notes(slide11,
    "Slide 11 demonstrates TruthGuard on a real-world test prompt regarding Marie Curie. "
    "The input answer contains a blend of a true claim, a factual contradiction (claiming 5 Nobel prizes instead of 2), and a subjective non-empirical statement. "
    "TruthGuard successfully dissected all three claims in 578.4 ms: claim 1 was supported; claim 2 was contradicted at 99.7% confidence; and claim 3 was correctly recognized as subjective with null confidence. "
    "Our generative engine revised the response to two Nobel prizes, and our closed-loop re-verification audit confirmed zero remaining contradictions. "
    "On the right, we acknowledge current single-hop constraints and outline our technical roadmap, including multimodal VLM verification and graph-guided multi-hop reasoning."
)

# ==============================================================================
# SLIDE 12 — CONCLUSION & Q&A
# ==============================================================================
slide12 = prs.slides.add_slide(blank_layout)
set_slide_background(slide12, COLOR_NAVY_HERO)

# Header
cat_box12 = slide12.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.5), Inches(0.35))
tf_c12 = cat_box12.text_frame
p_c12 = tf_c12.paragraphs[0]
p_c12.text = "CAPSTONE PROJECT CONCLUSION & DEFENSE"
p_c12.font.name = FONT_BODY
p_c12.font.size = Pt(11)
p_c12.font.bold = True
p_c12.font.color.rgb = COLOR_CYAN_ACCENT

t_box12 = slide12.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.65))
tf_t12 = t_box12.text_frame
p_t12 = tf_t12.paragraphs[0]
p_t12.text = "Scientific Contributions & Open Discussion"
p_t12.font.name = FONT_HEADING
p_t12.font.size = Pt(24)
p_t12.font.bold = True
p_t12.font.color.rgb = COLOR_WHITE

line12 = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Pt(1.5))
line12.fill.solid()
line12.fill.fore_color.rgb = COLOR_BLUE_ACCENT
line12.line.fill.background()

# Left Column: Summary of Scientific Contributions
add_card(slide12, Inches(0.8), Inches(1.75), Inches(6.0), Inches(5.0), bg_color=COLOR_NAVY_CARD, border_color=RGBColor(51, 65, 85))
tb_con = slide12.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(5.6), Inches(4.6))
tf_con = tb_con.text_frame
tf_con.word_wrap = True

p_cn0 = tf_con.paragraphs[0]
p_cn0.text = "SUMMARY OF RESEARCH CONTRIBUTIONS"
p_cn0.font.name = FONT_HEADING
p_cn0.font.size = Pt(12)
p_cn0.font.bold = True
p_cn0.font.color.rgb = COLOR_CYAN_ACCENT
p_cn0.space_after = Pt(8)

con_points = [
    ("Granular Span-Level Verification: ", "Decomposed complex natural language into atomic testable propositions with exact byte offsets [start, end], moving beyond coarse document-level opacity."),
    ("Calibrated Softmax Evidence Arbitration: ", "Formulated an honest multi-evidence decision matrix that strictly separates unverified assertions from direct contradictions, eliminating false alarms."),
    ("Closed-Loop Grounded Self-Correction: ", "Engineered a closed-loop revision pipeline that rewrites contradicted claims with verified evidence and mathematically re-audits outputs before delivery."),
    ("Privacy-Preserving Edge Accessibility: ", "Eliminated cloud token costs and GPU memory bottlenecks via CPU/GPU workload partitioning, executing 100% locally on 4 GB VRAM consumer workstations.")
]

for title, desc in con_points:
    p = tf_con.add_paragraph()
    r1 = p.add_run()
    r1.text = "✔ " + title
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_WHITE
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(148, 163, 184)
    p.space_after = Pt(8)

# Right Column: Questions & Answers Hero Card
add_card(slide12, Inches(7.1), Inches(1.75), Inches(5.4), Inches(5.0), bg_color=COLOR_NAVY_CARD, border_color=COLOR_BLUE_ACCENT)
tb_qa = slide12.shapes.add_textbox(Inches(7.3), Inches(2.1), Inches(5.0), Inches(4.3))
tf_qa = tb_qa.text_frame
tf_qa.word_wrap = True

p_q1 = tf_qa.paragraphs[0]
p_q1.alignment = PP_ALIGN.CENTER
p_q1.text = "QUESTIONS & ANSWERS"
p_q1.font.name = FONT_HEADING
p_q1.font.size = Pt(22)
p_q1.font.bold = True
p_q1.font.color.rgb = COLOR_CYAN_ACCENT
p_q1.space_after = Pt(8)

p_q2 = tf_qa.add_paragraph()
p_q2.alignment = PP_ALIGN.CENTER
p_q2.text = "Thank you to the evaluation committee, project guide Dr. Suja Golden Shiny, and faculty members for your valuable time and mentorship."
p_q2.font.size = Pt(11)
p_q2.font.color.rgb = RGBColor(203, 213, 225)
p_q2.space_after = Pt(16)

p_q3 = tf_qa.add_paragraph()
p_q3.alignment = PP_ALIGN.CENTER
p_q3.text = "TruthGuard Project Repository:\nDesktop/TRUTHGUARD"
p_q3.font.name = FONT_CODE
p_q3.font.size = Pt(10)
p_q3.font.bold = True
p_q3.font.color.rgb = COLOR_BLUE_ACCENT
p_q3.space_after = Pt(16)

p_q4 = tf_qa.add_paragraph()
p_q4.alignment = PP_ALIGN.CENTER
p_q4.text = "I welcome any questions, technical inquiries,\nor suggestions from the committee."
p_q4.font.size = Pt(11)
p_q4.font.bold = True
p_q4.font.color.rgb = COLOR_WHITE

add_footer(slide12, 12, 12, dark_mode=True)
add_speaker_notes(slide12,
    "In conclusion, TruthGuard establishes a rigorous, reproducible, and explainable foundation for hallucination mitigation in large language models. "
    "By uniting fine-grained atomic claim decomposition, unit-hypersphere FAISS dense retrieval, calibrated DeBERTa cross-encoders, and closed-loop local LLM self-correction, "
    "we demonstrate that trustworthy AI safeguards can be deployed entirely offline on commodity engineering hardware without sacrificing accuracy. "
    "I express my deepest gratitude to my supervisor Dr. Suja Golden Shiny for her guidance throughout this research. "
    "Thank you for your time and attention. I am now open to your questions and technical feedback."
)

# ==============================================================================
# Save Presentation & Export PDF Preview
# ==============================================================================
os.makedirs("docs", exist_ok=True)
pptx_path = os.path.abspath("docs/TruthGuard_Project_Presentation.pptx")
pdf_path = os.path.abspath("docs/TruthGuard_Project_Presentation.pdf")

prs.save(pptx_path)
print(f"Successfully generated PowerPoint presentation at: {pptx_path}")

# Export PDF Preview using PowerPoint COM
try:
    import win32com.client
    ppt_app = win32com.client.Dispatch("PowerPoint.Application")
    deck = ppt_app.Presentations.Open(pptx_path, WithWindow=False)
    deck.SaveAs(pdf_path, 32) # 32 = ppSaveAsPDF
    deck.Close()
    ppt_app.Quit()
    print(f"Successfully exported PDF presentation preview at: {pdf_path}")
except Exception as e:
    print(f"PowerPoint COM PDF export encountered notice: {e}")

print("Master Presentation Generation Complete!")
