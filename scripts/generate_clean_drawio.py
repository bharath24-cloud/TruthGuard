"""
TruthGuard Architecture Pipeline - Clean & Professional Draw.io, SVG, and High-Res PNG Generator
Generates an executive, publication-grade Figure 3.1: TruthGuard End-to-End System Architecture Pipeline.
Features minimalist vector icons, clean card elevations, refined typography, and disciplined color grading.
"""
import os
import xml.sax.saxutils as saxutils
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def get_svg_icons():
    """Returns clean, minimalist Feather/Lucide-style SVG vector icon snippets (viewBox 0 0 24 24)."""
    return {
        "shield_check": (
            '<path d="M12 2L4 5v6c0 5.55 3.84 10.74 8 12 4.16-1.26 8-6.45 8-12V5l-8-3z" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M9 12l2 2 4-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        ),
        "user_input": (
            '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8" y1="9" x2="16" y2="9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
            '<line x1="8" y1="13" x2="13" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        ),
        "bot_ai": (
            '<rect x="3" y="11" width="18" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<circle cx="12" cy="5" r="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M12 7v4" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8" y1="16" x2="8" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
            '<line x1="16" y1="16" x2="16" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        ),
        "document": (
            '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="14 2 14 8 20 8" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
            '<line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
            '<line x1="10" y1="9" x2="8" y2="9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        ),
        "globe": (
            '<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="2" y1="12" x2="22" y2="12" stroke="currentColor" stroke-width="2"/>'
            '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" fill="none" stroke="currentColor" stroke-width="2"/>'
        ),
        "scissors": (
            '<circle cx="6" cy="6" r="3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<circle cx="6" cy="18" r="3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="20" y1="4" x2="8.12" y2="15.88" stroke="currentColor" stroke-width="2"/>'
            '<line x1="14.47" y1="14.48" x2="20" y2="20" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8.12" y1="8.12" x2="12" y2="12" stroke="currentColor" stroke-width="2"/>'
        ),
        "vector_math": (
            '<rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M7 8h2v8H7M15 8h2v8h-2" stroke="currentColor" stroke-width="1.5"/>'
            '<circle cx="12" cy="12" r="2" fill="currentColor"/>'
        ),
        "database": (
            '<ellipse cx="12" cy="5" rx="9" ry="3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" fill="none" stroke="currentColor" stroke-width="2"/>'
        ),
        "alert_triangle": (
            '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
            '<line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        ),
        "layers": (
            '<polygon points="12 2 2 7 12 12 22 7 12 2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="2 17 12 22 22 17" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="2 12 12 17 22 12" fill="none" stroke="currentColor" stroke-width="2"/>'
        ),
        "search": (
            '<circle cx="11" cy="11" r="8" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="21" y1="21" x2="16.65" y2="16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        ),
        "cross_attention": (
            '<circle cx="6" cy="6" r="3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<circle cx="18" cy="18" r="3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M9 9l6 6M18 6l-3 3M6 18l3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        ),
        "scale": (
            '<line x1="12" y1="3" x2="12" y2="21" stroke="currentColor" stroke-width="2"/>'
            '<line x1="5" y1="6" x2="19" y2="6" stroke="currentColor" stroke-width="2"/>'
            '<path d="M5 6l-3 6h6zM19 6l-3 6h6z" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        ),
        "gauge": (
            '<path d="M12 2a10 10 0 0 0-10 10c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M12 9v3l2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        ),
        "edit_pen": (
            '<path d="M12 20h9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
            '<path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" fill="none" stroke="currentColor" stroke-width="2"/>'
        ),
        "refresh": (
            '<polyline points="23 4 23 10 17 10" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="1 20 1 14 7 14" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" fill="none" stroke="currentColor" stroke-width="2"/>'
        ),
        "cpu": (
            '<rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<rect x="9" y="9" width="6" height="6" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="9" y1="1" x2="9" y2="4" stroke="currentColor" stroke-width="2"/>'
            '<line x1="15" y1="1" x2="15" y2="4" stroke="currentColor" stroke-width="2"/>'
            '<line x1="9" y1="20" x2="9" y2="23" stroke="currentColor" stroke-width="2"/>'
            '<line x1="15" y1="20" x2="15" y2="23" stroke="currentColor" stroke-width="2"/>'
            '<line x1="1" y1="9" x2="4" y2="9" stroke="currentColor" stroke-width="2"/>'
            '<line x1="1" y1="15" x2="4" y2="15" stroke="currentColor" stroke-width="2"/>'
            '<line x1="20" y1="9" x2="23" y2="9" stroke="currentColor" stroke-width="2"/>'
            '<line x1="20" y1="15" x2="23" y2="15" stroke="currentColor" stroke-width="2"/>'
        ),
        "gpu": (
            '<rect x="2" y="6" width="20" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<circle cx="8" cy="12" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '<circle cx="16" cy="12" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '<line x1="6" y1="18" x2="6" y2="21" stroke="currentColor" stroke-width="2"/>'
            '<line x1="18" y1="18" x2="18" y2="21" stroke="currentColor" stroke-width="2"/>'
        ),
        "trophy": (
            '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M4 22h16" stroke="currentColor" stroke-width="2"/>'
            '<path d="M10 14.66V17c0 .55-.45 1-1 1H8v4h8v-4h-1c-.55 0-1-.45-1-1v-2.34" stroke="currentColor" stroke-width="2"/>'
            '<path d="M18 2H6v7a6 6 0 0 0 12 0V2z" fill="none" stroke="currentColor" stroke-width="2"/>'
        ),
        "server": (
            '<rect x="2" y="2" width="20" height="8" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<rect x="2" y="14" width="20" height="8" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="6" y1="6" x2="6.01" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
            '<line x1="6" y1="18" x2="6.01" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        ),
        "layout": (
            '<rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2"/>'
            '<line x1="9" y1="21" x2="9" y2="9" stroke="currentColor" stroke-width="2"/>'
        )
    }

def generate_drawio_xml():
    """Generates an executive, publication-grade Draw.io XML architecture diagram."""
    
    page_w = 1800
    page_h = 1260
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<mxfile host="app.diagrams.net" modified="2026-10-19T14:45:00.000Z" agent="Mozilla/5.0" version="24.7.17" type="device">',
        '  <diagram id="TruthGuard-System-Architecture" name="TruthGuard System Architecture Pipeline">',
        f'    <mxGraphModel dx="1600" dy="1100" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_w}" pageHeight="{page_h}" background="#F8FAFC" math="1" shadow="0">',
        '      <root>',
        '        <mxCell id="0" />',
        '        <mxCell id="1" parent="0" />',
    ]

    def add_cell(cell_id, value, style, x, y, w, h, parent="1", is_vertex=True):
        val_escaped = saxutils.escape(value, {'"': '&quot;', "'": '&apos;'})
        style_escaped = saxutils.escape(style, {'"': '&quot;', "'": '&apos;'})
        v_attr = 'vertex="1"' if is_vertex else 'edge="1"'
        xml_lines.append(f'        <mxCell id="{cell_id}" value="{val_escaped}" style="{style_escaped}" {v_attr} parent="{parent}">')
        xml_lines.append(f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />')
        xml_lines.append('        </mxCell>')

    def add_card(card_id, accent_color, tag_text, title, lines, x, y, w, h):
        """Creates an executive modern card with clean left accent band, badge pill, and clear typography."""
        content = (
            f"<div style='padding:6px 10px;font-family:Inter,Segoe UI,Helvetica,Arial,sans-serif;'>"
            f"  <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;'>"
            f"    <span style='font-size:12px;font-weight:700;color:#0F172A;letter-spacing:-0.2px;'>{title}</span>"
            f"    <span style='background-color:{accent_color}1A;color:{accent_color};border:1px solid {accent_color}4D;padding:1px 6px;border-radius:4px;font-size:9.5px;font-weight:700;'>{tag_text}</span>"
            f"  </div>"
            f"  <div style='height:1px;background-color:#E2E8F0;margin:3px 0 6px 0;'></div>"
        )
        for line in lines:
            content += f"  <div style='font-size:10.5px;color:#334155;line-height:1.45;margin-bottom:2px;'>{line}</div>"
        content += "</div>"
        
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#FFFFFF;strokeColor=#CBD5E1;strokeWidth=1.5;"
            f"shadow=0;align=left;verticalAlign=top;"
        )
        add_cell(card_id, content, style, x, y, w, h)
        
        # Left accent stripe (clean visual anchor)
        add_cell(f"stripe_{card_id}", "", f"rounded=1;fillColor={accent_color};strokeColor=none;arcSize=50;", x+2, y+4, 4, h-8)

    def add_edge(edge_id, value, style, src_id, dst_id, parent="1", points=None):
        val_escaped = saxutils.escape(value, {'"': '&quot;', "'": '&apos;'})
        style_escaped = saxutils.escape(style, {'"': '&quot;', "'": '&apos;'})
        xml_lines.append(f'        <mxCell id="{edge_id}" value="{val_escaped}" style="{style_escaped}" edge="1" parent="{parent}" source="{src_id}" target="{dst_id}">')
        xml_lines.append('          <mxGeometry relative="1" as="geometry">')
        if points:
            xml_lines.append('            <Array as="points">')
            for px, py in points:
                xml_lines.append(f'              <mxPoint x="{px}" y="{py}" />')
            xml_lines.append('            </Array>')
        xml_lines.append('          </mxGeometry>')
        xml_lines.append('        </mxCell>')

    # 1. Header Banner
    add_cell(
        "header_banner",
        "<table style='width:100%;height:100%;color:#FFFFFF;font-family:Inter,Segoe UI,sans-serif;'>"
        "<tr>"
        "<td style='padding-left:20px;text-align:left;'>"
        "  <div style='font-size:18px;font-weight:800;letter-spacing:-0.3px;color:#F8FAFC;'>TRUTHGUARD: END-TO-END SYSTEM ARCHITECTURE PIPELINE</div>"
        "  <div style='font-size:11.5px;color:#94A3B8;margin-top:2px;'>Local Multi-Stage Fact Verification, Cross-Encoder NLI, and Closed-Loop Hallucination Auditing</div>"
        "</td>"
        "<td style='padding-right:20px;text-align:right;'>"
        "  <span style='background:#1E293B;color:#38BDF8;border:1px solid #0284C7;padding:4px 10px;border-radius:6px;font-size:10.5px;font-weight:700;'>IEEE ACADEMIC FORMAT • LOCAL RUNTIME • SUB-600ms</span>"
        "</td>"
        "</tr>"
        "</table>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#1E293B;strokeWidth=1;arcSize=6;shadow=0;",
        40, 20, 1720, 65
    )

    # 2. Four Vertical Swimlane Zones (Clean Containers with subtle borders)
    def add_zone(zone_id, title, x, y, w, h, bg_color="#F8FAFC", stroke_color="#CBD5E1", title_color="#0F172A"):
        style = (
            f"swimlane;startSize=30;rounded=1;whiteSpace=wrap;html=1;arcSize=6;collapsible=0;"
            f"fillColor={bg_color};strokeColor={stroke_color};strokeWidth=1.5;fontColor={title_color};"
            f"fontStyle=1;fontSize=12;fontFamily=Inter,Segoe UI,sans-serif;align=center;"
        )
        add_cell(zone_id, title, style, x, y, w, h)

    # Zone 1: Ingestion
    add_zone("zone_ingestion", "1. KNOWLEDGE BASE & INPUT INGESTION", 40, 100, 370, 785, "#F8FAFC", "#94A3B8", "#0F172A")
    # Zone 2: Verification Core
    add_zone("zone_core", "2. MULTI-STAGE VERIFICATION CORE", 430, 100, 450, 785, "#F8FAFC", "#3B82F6", "#1D4ED8")
    # Zone 3: Risk Scoring & Reverification
    add_zone("zone_audit", "3. RISK SCORING & CLOSED-LOOP AUDIT", 900, 100, 440, 785, "#F8FAFC", "#7C3AED", "#6B21A8")
    # Zone 4: Hardware Budget
    add_zone("zone_hardware", "4. WORKSTATION HARDWARE PARTITIONING", 1360, 100, 400, 785, "#F8FAFC", "#64748B", "#1E293B")

    # Zone 1 Cards
    add_card("card_mode_a", "#0284C7", "MODE A", "Direct Query-Answer Input",
             ["• Ingests user inquiry paired with external answer",
              "• Audits arbitrary LLM responses or human authored text"],
             60, 145, 330, 65)

    add_card("card_mode_b", "#0284C7", "MODE B", "Autonomous Generation Engine",
             ["• Inquiry passed to local LLM: <b>Ollama qwen3:8b</b>",
              "• Synthesizes response on dedicated GPU (~2.4 GB VRAM)"],
             60, 225, 330, 70)

    add_card("card_docs", "#0284C7", "PDF / TXT / MD", "Private Document Library",
             ["• Parsed via PyMuPDF (fitz) with character normalization",
              "• SHA-256 cryptographic deduplication hashing"],
             60, 310, 330, 70)

    add_card("card_fever", "#0284C7", "FEVER", "Benchmark Wikipedia Corpus",
             ["• 570 atomic Wikipedia articles • 1,000 evaluation pairs",
              "• <b>Zero-Leakage Protocol:</b> Gold labels withheld at retrieval"],
             60, 395, 330, 70)

    add_card("card_chunk", "#4F46E5", "CHUNK=500", "Sliding-Window Chunking",
             ["• Character window <i>C = 500</i>, overlap <i>O = 100</i> chars",
              "• Preserves exact paragraph boundaries, page # & chunk IDs"],
             60, 480, 330, 70)

    add_card("card_embed", "#4F46E5", "R^384", "Dense Embedding Engine",
             ["• <b>all-MiniLM-L6-v2</b> (Sentence-Transformers on CPU)",
              "• Maps passage text into continuous L2-normalized <b>R^384</b>"],
             60, 565, 330, 70)

    add_card("card_faiss", "#4F46E5", "FAISS", "IndexFlatIP Vector Storage",
             ["• Exact Inner Product evaluation: <i>sim(q, v) = cos(θ)</i>",
              "• Sub-20ms dense vector retrieval against indexed corpus"],
             60, 650, 330, 75)

    add_card("card_guard", "#DC2626", "GUARDRAIL", "Missing Corpus Safety Fallback",
             ["• If index is empty → Emits <i>NO_DOCUMENTS_INDEXED</i>",
              "• Calibration safety: Assigns <b>confidence = null</b>"],
             60, 740, 330, 65)

    # Zone 2 Cards (Verification Core Stages 1 - 4)
    add_card("card_s1", "#2563EB", "STAGE 1", "Syntactic Atomic Claim Decomposition",
             ["• Sentence boundary detection with coordinating conjunction regex",
              "• Splits compound clauses (<i>and, but, whereas</i>) into atomic hypotheses",
              "• <b>Character Span Offsets:</b> Stores exact [start_offset, end_offset]",
              "• Empirical classifier filters subjective / non-verifiable statements"],
             450, 145, 410, 125)

    add_card("card_s2", "#4F46E5", "STAGE 2", "Multi-Source Semantic Vector Retrieval",
             ["• Encodes query claim into R^384 vector via MiniLM-L6 (CPU)",
              "• Executes FAISS inner product search for exact cosine similarity",
              "• Retrieves top-k candidate passages (<i>k = 3</i>, threshold <i>τ_sim ≥ 0.25</i>)",
              "• Zero matches trigger fallback reason: <i>NO_EVIDENCE_RETRIEVED</i>"],
             450, 295, 410, 125)

    add_card("card_s3", "#D97706", "STAGE 3", "Cross-Encoder Natural Language Inference",
             ["• Model: <b>cross-encoder/nli-deberta-v3-small</b> (44M params, CPU)",
              "• Token sequence: <i>[CLS] Passage Premise [SEP] Atomic Claim [SEP]</i>",
              "• Full all-to-all cross-attention across premise and hypothesis tokens",
              "• Softmax Logits: <b>P(contradiction), P(entailment), P(neutral)</b>",
              "• <b>Calibrated Thresholds:</b> <i>τ_entail ≥ 0.55</i>, <i>τ_contra ≥ 0.50</i>"],
             450, 445, 410, 145)

    add_card("card_s4", "#DC2626", "STAGE 4", "Multi-Evidence Arbitration Policy",
             ["• <b>Supported:</b> max P(entailment) ≥ 0.55 without contradiction",
              "• <b>Contradicted:</b> max P(contradiction) ≥ 0.50 without entailment",
              "• <b>Conflicting:</b> Distinct passages yield both P_e ≥ 0.55 AND P_c ≥ 0.50",
              "• <b>Insufficient Evidence:</b> Below thresholds, 0 retrieved, or subjective",
              "• <i>Null Calibration:</i> Unverifiable statements assigned confidence = null"],
             450, 615, 410, 155)

    # Zone 3 Cards (Scoring, Correction & Reverification)
    add_card("card_s5", "#7C3AED", "STAGE 5", "Mathematical Hallucination Risk Scorer",
             ["• <b>Contradiction Rate:</b> <i>R_contra = N_contra / max(1, N_verifiable)</i>",
              "• <b>Unsupported Rate:</b> <i>R_unsupp = (N_contra + N_insuff + N_conf) / N_total</i>",
              "• <b>Composite Risk:</b> <i>S_risk = min(1.0, 0.70·R_contra + 0.30·R_unsupp)</i>",
              "• <b>Explainability:</b> Document provenance, page #, chunk ID & similarity"],
             920, 145, 400, 145)

    # Decision Node (Clean Diamond with crisp border)
    add_cell(
        "card_decision",
        "<div style='text-align:center;font-family:Inter,Segoe UI,sans-serif;'>"
        "  <div style='font-size:11px;font-weight:700;color:#92400E;'>Contradictions<br/>Detected?</div>"
        "  <div style='font-size:9.5px;color:#B45309;margin-top:2px;'>(N_contra &gt; 0)</div>"
        "</div>",
        "rhombus;whiteSpace=wrap;html=1;arcSize=4;fillColor=#FEF3C7;strokeColor=#D97706;strokeWidth=1.5;shadow=0;",
        1035, 315, 170, 80
    )

    add_card("card_s6", "#7C3AED", "STAGE 6", "Evidence-Grounded Correction Engine",
             ["• Selectively replaces contradicted spans with verified ground truth",
              "• Context-constrained prompting via local <b>Ollama qwen3:8b</b> on GPU",
              "• Preserves supported sentences; rewrites only refuted clauses"],
             920, 420, 400, 115)

    add_card("card_reverif", "#7C3AED", "CLOSED-LOOP", "Reverification Audit Engine",
             ["• Revised output is automatically looped back through <b>Stages 1 - 4</b>",
              "• <b>Verification Invariant:</b> Mathematically guarantees 0 contradictions",
              "• Emits reverification certification and side-by-side diff view"],
             920, 560, 400, 120)

    # Verified Output Card (Green certified banner)
    add_cell(
        "card_pass",
        "<div style='padding:6px 14px;font-family:Inter,Segoe UI,sans-serif;'>"
        "  <div style='display:flex;align-items:center;justify-content:space-between;'>"
        "    <span style='font-size:12.5px;font-weight:700;color:#14532D;'>Audit Complete: Verified Factual Output</span>"
        "    <span style='background:#16A34A;color:#FFFFFF;padding:1px 6px;border-radius:4px;font-size:9.5px;font-weight:700;'>CERTIFIED</span>"
        "  </div>"
        "  <div style='font-size:10.5px;color:#15803D;margin-top:3px;'>0 Contradictions • Evidence Provenance Grounded • Ready for Export & UI</div>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#DCFCE7;strokeColor=#16A34A;strokeWidth=1.5;shadow=0;",
        920, 705, 400, 55
    )

    # Zone 4 Cards (Hardware Partitioning)
    add_card("card_gpu", "#059669", "RTX 3050 (4GB)", "Dedicated Generative GPU Memory",
             ["• <b>Ollama LLM Runtime:</b> Dedicated to <i>qwen3:8b</i>",
              "• Working VRAM: <b>~2.4 GB VRAM</b> (&le; 60% GPU threshold)",
              "• Roles: Mode B Response Synthesis & Stage 6 Grounded Correction",
              "• Prevents fatal CUDA Out-Of-Memory (OOM) concurrency crashes"],
             1380, 145, 360, 145)

    add_card("card_cpu", "#2563EB", "HOST CPU & RAM", "Verification Pipeline Compute",
             ["• <b>Sentence-Transformers:</b> <i>all-MiniLM-L6-v2</i> (384-dim, CPU)",
              "• <b>Cross-Encoder NLI:</b> <i>nli-deberta-v3-small</i> (44M params, CPU)",
              "• <b>FAISS Index:</b> <i>IndexFlatIP</i> cosine search in RAM",
              "• Working Memory Footprint: <b>~3.2 GB</b> Host System RAM",
              "• Zero VRAM competition between LLM and Verification models"],
             1380, 310, 360, 155)

    add_card("card_bench", "#0F172A", "BENCHMARKS", "Empirical Evaluation Metrics",
             ["• <b>FEVER Fact Verification Accuracy:</b> <b>90.0%</b> (Macro F1: 89.9%)",
              "• <b>FEVER Recall@3 (Evidence Retrieval):</b> <b>100.0%</b>",
              "• <b>Claim Decomposition Latency:</b> 42 ms",
              "• <b>FAISS Vector Search Latency:</b> 18 ms",
              "• <b>Cross-Encoder NLI Latency:</b> 212 ms",
              "• <b>Warm Verification Total:</b> <b>296 ms</b> (&lt; 0.6 seconds)",
              "• <b>Cloud API Cost:</b> <b>$0.00 / query</b> (100% Offline & Private)"],
             1380, 485, 360, 195)

    # Zone 5: Serving, Persistence & Presentation (Bottom Container)
    add_zone("zone_serving", "5. API SERVING, DATABASE PERSISTENCE & USER EXPERIENCE LAYER", 40, 905, 1720, 210, "#F8FAFC", "#64748B", "#0F172A")

    add_card("card_api", "#0284C7", "FASTAPI", "High-Throughput Asynchronous Backend",
             ["• REST Endpoints: <code>/verify</code>, <code>/verify-stream</code>, <code>/upload</code>, <code>/documents</code>, <code>/health</code>",
              "• Asynchronous ASGI pipeline with Pydantic request validation & CORS middleware",
              "• Structured error reporting with deterministic reason codes (<code>NO_DOCUMENTS_INDEXED</code>)"],
             60, 945, 410, 145)

    add_card("card_db", "#4F46E5", "SQLITE", "Relational Database Persistence",
             ["• File: <code>data/truthguard.db</code> (Local, Zero-cloud)",
              "• Schema Tables: <code>verification_runs</code>, <code>claims</code>, <code>evidence</code>, <code>documents</code>",
              "• Stores audit trail, character offsets, verdicts, hallucination scores & SHA-256 hashes"],
             490, 945, 360, 145)

    add_card("card_ui", "#0D9488", "REACT 18", "Modern Interactive Audit Dashboard",
             ["• <b>Interactive Answer Inspector:</b> Real-time span highlighting (Supported, Contradicted, Conflicting, Insufficient)",
              "• <b>Hallucination Risk Gauge:</b> Circular risk meter showing composite score S_risk, Contradiction Rate, and Unsupported Rate",
              "• <b>Evidence Provenance Cards:</b> Document name, page number, chunk ID, verbatim citation snippet, and similarity score",
              "• <b>Diff Reverification View:</b> Side-by-side inspection showing refuted assertions vs. grounded corrected text"],
             870, 945, 870, 145)

    # 6. Minimalist Legend Bar
    add_cell(
        "legend_bar",
        "<div style='font-family:Inter,Segoe UI,sans-serif;font-size:11px;color:#475569;display:flex;align-items:center;justify-content:center;height:100%;'>"
        "  <span style='font-weight:700;color:#0F172A;margin-right:15px;'>PIPELINE LEGEND:</span>"
        "  <span style='background:#E0F2FE;color:#0369A1;padding:2px 8px;border-radius:4px;font-weight:600;margin-right:10px;'>■ Ingestion &amp; Input Flow</span>"
        "  <span style='background:#EEF2FF;color:#3730A3;padding:2px 8px;border-radius:4px;font-weight:600;margin-right:10px;'>■ Dense Vector Indexing (FAISS)</span>"
        "  <span style='background:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:4px;font-weight:600;margin-right:10px;'>■ DeBERTa-v3 Cross-Encoder NLI</span>"
        "  <span style='background:#FEE2E2;color:#991B1B;padding:2px 8px;border-radius:4px;font-weight:600;margin-right:10px;'>■ Arbitration &amp; Risk Scoring</span>"
        "  <span style='background:#EDE9FE;color:#5B21B6;padding:2px 8px;border-radius:4px;font-weight:600;margin-right:10px;'>■ Closed-Loop Reverification</span>"
        "  <span style='background:#ECFDF5;color:#064E3B;padding:2px 8px;border-radius:4px;font-weight:600;'>■ Hardware Allocation</span>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#FFFFFF;strokeColor=#CBD5E1;strokeWidth=1;shadow=0;",
        40, 1130, 1720, 45
    )

    # 7. Clean Connectors (Subtle, sleek, with pill labels)
    style_conn_blue = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2563EB;strokeWidth=1.5;endArrow=classic;endFill=1;fontColor:#1E293B;fontSize=10;"
    style_conn_purple = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#6366F1;strokeWidth=1.5;endArrow=classic;endFill=1;fontColor:#3730A3;fontSize=10;"
    style_conn_slate = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#64748B;strokeWidth=1.5;endArrow=classic;endFill=1;fontColor:#334155;fontSize=10;"
    style_conn_red = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=1.5;endArrow=classic;endFill=1;fontColor:#991B1B;fontSize=10;"
    style_conn_green = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=1.5;endArrow=classic;endFill=1;fontColor:#15803D;fontSize=10;"
    style_loop = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#7C3AED;strokeWidth=2.2;dashed=1;dashPattern=6 3;endArrow=classic;endFill=1;fontColor:#6B21A8;fontSize=10.5;fontStyle=1;"

    # Mode A / B -> Stage 1
    add_edge("e_mode_a_s1", "Candidate Answer", style_conn_blue, "card_mode_a", "card_s1")
    add_edge("e_mode_b_s1", "Synthesized Text", style_conn_blue, "card_mode_b", "card_s1")

    # Ingestion flow
    add_edge("e_doc_chunk", "Raw Text", style_conn_slate, "card_docs", "card_chunk")
    add_edge("e_fever_chunk", "Wikipedia", style_conn_slate, "card_fever", "card_chunk")
    add_edge("e_chunk_embed", "500-char Chunks", style_conn_purple, "card_chunk", "card_embed")
    add_edge("e_embed_faiss", "L2 R^384 Vectors", style_conn_purple, "card_embed", "card_faiss")

    # FAISS -> Stage 2
    add_edge("e_faiss_s2", "Top-3 Matches (sim ≥ 0.25)", style_conn_purple, "card_faiss", "card_s2", points=[(410, 685), (410, 355)])

    # Stage 1 -> 2 -> 3 -> 4
    add_edge("e_s1_s2", "Atomic Claims + Offsets", style_conn_blue, "card_s1", "card_s2")
    add_edge("e_s2_s3", "Premise-Hypothesis Pairs", style_conn_blue, "card_s2", "card_s3")
    add_edge("e_s3_s4", "Softmax [P_c, P_e, P_n]", style_conn_red, "card_s3", "card_s4")

    # Stage 4 -> Stage 5
    add_edge("e_s4_s5", "4-Way Verdicts", style_conn_red, "card_s4", "card_s5", points=[(880, 690), (880, 215)])

    # Stage 5 -> Decision
    add_edge("e_s5_dec", "Contradiction Count", style_conn_purple, "card_s5", "card_decision")

    # Decision -> Stage 6 (Yes)
    add_edge("e_dec_corr", "Yes (N_contra > 0)", style_conn_red, "card_decision", "card_s6")

    # Decision -> Pass (No)
    add_edge("e_dec_pass", "No (0 Contradictions)", style_conn_green, "card_decision", "card_pass", points=[(1120, 395), (1240, 395), (1240, 730)])

    # Stage 6 -> Reverification
    add_edge("e_corr_reverif", "Corrected Text + Evidence", style_conn_purple, "card_s6", "card_reverif")

    # Reverification -> Stage 1 (Closed-Loop Reverification Loopback)
    add_edge("e_reverif_loop", "CLOSED-LOOP REVERIFICATION AUDIT (GUARANTEES 0 CONTRADICTIONS)", style_loop, "card_reverif", "card_s1", points=[(920, 620), (880, 620), (880, 180)])

    # Reverification -> Pass
    add_edge("e_reverif_pass", "Verified Factual", style_conn_green, "card_reverif", "card_pass")

    # Pass -> FastAPI Backend
    add_edge("e_pass_api", "Verified Audit Payload", style_conn_slate, "card_pass", "card_api", points=[(1120, 760), (265, 760), (265, 945)])

    # API -> DB & API -> UI
    add_edge("e_api_db", "Persist Run", style_conn_blue, "card_api", "card_db")
    add_edge("e_api_ui", "Stream Verified JSON", style_conn_slate, "card_api", "card_ui", points=[(265, 1090), (900, 1090)])

    xml_lines.append('      </root>')
    xml_lines.append('    </mxGraphModel>')
    xml_lines.append('  </diagram>')
    xml_lines.append('</mxfile>')

    return '\n'.join(xml_lines)

def generate_clean_svg():
    """Generates an executive, publication-grade SVG diagram with clean vector icons."""
    icons = get_svg_icons()
    
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 1200" width="100%" height="100%" style="background-color: #F8FAFC; font-family: Inter, Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif;">',
        '  <defs>',
        '    <marker id="arr-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2563EB"/></marker>',
        '    <marker id="arr-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6366F1"/></marker>',
        '    <marker id="arr-slate" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#64748B"/></marker>',
        '    <marker id="arr-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#DC2626"/></marker>',
        '    <marker id="arr-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#16A34A"/></marker>',
        '    <marker id="arr-loop" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#7C3AED"/></marker>',
        '    <filter id="card-shadow" x="-2%" y="-2%" width="104%" height="106%"><feDropShadow dx="0" dy="1.5" stdDeviation="2.5" flood-color="#0F172A" flood-opacity="0.05"/></filter>',
        '  </defs>',
    ]

    # Header Banner
    svg.append('  <rect x="40" y="20" width="1720" height="65" rx="6" fill="#0F172A" stroke="#1E293B" stroke-width="1"/>')
    svg.append(f'  <g transform="translate(60, 36) scale(1.3)" color="#38BDF8">{icons["shield_check"]}</g>')
    svg.append('  <text x="105" y="46" fill="#F8FAFC" font-size="17" font-weight="700" letter-spacing="-0.3">TRUTHGUARD: END-TO-END SYSTEM ARCHITECTURE PIPELINE</text>')
    svg.append('  <text x="105" y="66" fill="#94A3B8" font-size="11.5">Local Multi-Stage Fact Verification, Cross-Encoder NLI, and Closed-Loop Hallucination Auditing</text>')
    svg.append('  <rect x="1440" y="35" width="300" height="34" rx="6" fill="#1E293B" stroke="#0284C7" stroke-width="1"/>')
    svg.append('  <text x="1590" y="56" fill="#38BDF8" font-size="10.5" font-weight="700" text-anchor="middle">IEEE ACADEMIC FORMAT • LOCAL • SUB-600ms</text>')

    # Containers / Swimlanes
    def draw_zone(x, y, w, h, title, stroke_col="#CBD5E1", title_col="#0F172A"):
        svg.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#F8FAFC" stroke="{stroke_col}" stroke-width="1.5"/>')
        svg.append(f'  <path d="M {x} {y+30} L {x+w} {y+30}" stroke="{stroke_col}" stroke-width="1"/>')
        svg.append(f'  <text x="{x+16}" y="{y+20}" fill="{title_col}" font-size="11.5" font-weight="700" letter-spacing="0.5">{title}</text>')

    draw_zone(40, 100, 370, 785, "1. KNOWLEDGE BASE &amp; INPUT INGESTION", "#94A3B8", "#0F172A")
    draw_zone(430, 100, 450, 785, "2. MULTI-STAGE VERIFICATION CORE", "#3B82F6", "#1D4ED8")
    draw_zone(900, 100, 440, 785, "3. RISK SCORING &amp; CLOSED-LOOP AUDIT", "#7C3AED", "#6B21A8")
    draw_zone(1360, 100, 400, 785, "4. WORKSTATION HARDWARE PARTITIONING", "#64748B", "#1E293B")
    draw_zone(40, 905, 1720, 210, "5. API SERVING, DATABASE PERSISTENCE &amp; USER EXPERIENCE LAYER", "#64748B", "#0F172A")

    # Clean Card Function
    def draw_card(x, y, w, h, icon_name, accent_color, tag, title, lines, is_diamond=False):
        if is_diamond:
            cx, cy = x + w/2, y + h/2
            svg.append(f'  <polygon points="{cx},{y} {x+w},{cy} {cx},{y+h} {x},{cy}" fill="#FEF3C7" stroke="#D97706" stroke-width="1.5" filter="url(#card-shadow)"/>')
            svg.append(f'  <text x="{cx}" y="{cy-6}" fill="#92400E" font-size="11" font-weight="700" text-anchor="middle">{title}</text>')
            for i, line in enumerate(lines):
                svg.append(f'  <text x="{cx}" y="{cy+10 + i*13}" fill="#B45309" font-size="9.5" text-anchor="middle">{saxutils.escape(line)}</text>')
            return

        svg.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" filter="url(#card-shadow)"/>')
        # Left Accent Stripe
        svg.append(f'  <rect x="{x+1.5}" y="{y+4}" width="3.5" height="{h-8}" rx="2" fill="{accent_color}"/>')
        # Icon Box
        svg.append(f'  <rect x="{x+12}" y="{y+10}" width="24" height="24" rx="4" fill="{accent_color}1A"/>')
        if icon_name in icons:
            svg.append(f'  <g transform="translate({x+16}, {y+14}) scale(0.66)" color="{accent_color}">{icons[icon_name]}</g>')
        # Title
        svg.append(f'  <text x="{x+44}" y="{y+23}" fill="#0F172A" font-size="11.5" font-weight="700">{saxutils.escape(title)}</text>')
        # Tag Badge
        if tag:
            tag_w = len(tag) * 6.2 + 10
            svg.append(f'  <rect x="{x+w - tag_w - 12}" y="{y+11}" width="{tag_w}" height="18" rx="3" fill="{accent_color}14" stroke="{accent_color}4D" stroke-width="1"/>')
            svg.append(f'  <text x="{x+w - tag_w/2 - 12}" y="{y+23}" fill="{accent_color}" font-size="9" font-weight="700" text-anchor="middle">{tag}</text>')
        # Divider
        svg.append(f'  <line x1="{x+12}" y1="{y+38}" x2="{x+w-12}" y2="{y+38}" stroke="#F1F5F9" stroke-width="1"/>')
        # Body Lines
        for i, line in enumerate(lines):
            l_esc = saxutils.escape(line)
            svg.append(f'  <text x="{x+14}" y="{y+52 + i*15}" fill="#334155" font-size="10">{l_esc}</text>')

    # Zone 1 Cards
    draw_card(60, 145, 330, 65, "user_input", "#0284C7", "MODE A", "Direct Query-Answer Input",
              ["• Ingests user inquiry paired with external candidate answer",
               "• Audits arbitrary LLM responses or human authored text"])

    draw_card(60, 225, 330, 70, "bot_ai", "#0284C7", "MODE B", "Autonomous Generation Engine",
              ["• Inquiry passed to local LLM: Ollama qwen3:8b",
               "• Synthesizes response on dedicated GPU (~2.4 GB VRAM)"])

    draw_card(60, 310, 330, 70, "document", "#0284C7", "PDF / TXT / MD", "Private Document Library",
              ["• Parsed via PyMuPDF (fitz) with character normalization",
               "• SHA-256 cryptographic deduplication hashing"])

    draw_card(60, 395, 330, 70, "globe", "#0284C7", "FEVER", "Benchmark Wikipedia Corpus",
              ["• 570 atomic Wikipedia articles • 1,000 evaluation pairs",
               "• Zero-Leakage Protocol: Gold labels withheld at retrieval"])

    draw_card(60, 480, 330, 70, "scissors", "#4F46E5", "CHUNK=500", "Sliding-Window Chunking",
              ["• Character window C = 500, overlap O = 100 chars",
               "• Preserves exact paragraph boundaries, page # &amp; chunk IDs"])

    draw_card(60, 565, 330, 70, "vector_math", "#4F46E5", "R^384", "Dense Embedding Engine",
              ["• all-MiniLM-L6-v2 (Sentence-Transformers on CPU)",
               "• Maps passage text into continuous L2-normalized R^384"])

    draw_card(60, 650, 330, 75, "database", "#4F46E5", "FAISS", "IndexFlatIP Vector Storage",
              ["• Exact Inner Product evaluation: sim(q, v) = cos(θ)",
               "• Sub-20ms dense vector retrieval against indexed corpus"])

    draw_card(60, 740, 330, 65, "alert_triangle", "#DC2626", "GUARDRAIL", "Missing Corpus Safety Fallback",
              ["• If index is empty → Emits NO_DOCUMENTS_INDEXED",
               "• Calibration safety: Assigns confidence = null"])

    # Zone 2 Cards
    draw_card(450, 145, 410, 125, "layers", "#2563EB", "STAGE 1", "Syntactic Claim Decomposition",
              ["• Sentence boundary detection with coordinating conjunction regex",
               "• Splits compound clauses (and, but, whereas) into atomic hypotheses",
               "• Character Span Offsets: Stores exact [start_offset, end_offset]",
               "• Empirical classifier filters subjective / non-verifiable statements"])

    draw_card(450, 295, 410, 125, "search", "#4F46E5", "STAGE 2", "Multi-Source Semantic Retrieval",
              ["• Encodes query claim into R^384 vector via MiniLM-L6 (CPU)",
               "• Executes FAISS inner product search for exact cosine similarity",
               "• Retrieves top-k candidate passages (k = 3, threshold τ_sim ≥ 0.25)",
               "• Zero matches trigger fallback reason: NO_EVIDENCE_RETRIEVED"])

    draw_card(450, 445, 410, 145, "cross_attention", "#D97706", "STAGE 3", "Cross-Encoder NLI Inference",
              ["• Model: cross-encoder/nli-deberta-v3-small (44M params, CPU)",
               "• Token sequence: [CLS] Passage Premise [SEP] Atomic Claim [SEP]",
               "• Full all-to-all cross-attention across premise and hypothesis tokens",
               "• Softmax Logits: P(contradiction), P(entailment), P(neutral)",
               "• Calibrated Thresholds: τ_entail ≥ 0.55, τ_contra ≥ 0.50"])

    draw_card(450, 615, 410, 155, "scale", "#DC2626", "STAGE 4", "Multi-Evidence Arbitration Policy",
              ["• Supported: max P(entailment) ≥ 0.55 without contradiction",
               "• Contradicted: max P(contradiction) ≥ 0.50 without entailment",
               "• Conflicting: Distinct passages yield both P_e ≥ 0.55 AND P_c ≥ 0.50",
               "• Insufficient Evidence: Below thresholds, 0 retrieved, or subjective",
               "• Null Calibration: Unverifiable statements assigned confidence = null"])

    # Zone 3 Cards
    draw_card(920, 145, 400, 145, "gauge", "#7C3AED", "STAGE 5", "Mathematical Hallucination Risk Scorer",
              ["• Contradiction Rate: R_contra = N_contra / max(1, N_verifiable)",
               "• Unsupported Rate: R_unsupp = (N_contra + N_insuff + N_conf) / N_total",
               "• Composite Risk: S_risk = min(1.0, 0.70·R_contra + 0.30·R_unsupp)",
               "• Explainability: Document provenance, page #, chunk ID &amp; similarity"])

    draw_card(1035, 315, 170, 80, "", "", "", "Contradictions?", ["Detected?", "(N_contra > 0)"], is_diamond=True)

    draw_card(920, 420, 400, 115, "edit_pen", "#7C3AED", "STAGE 6", "Evidence-Grounded Correction Engine",
              ["• Selectively replaces contradicted spans with verified ground truth",
               "• Context-constrained prompting via local Ollama qwen3:8b on GPU",
               "• Preserves supported sentences; rewrites only refuted clauses"])

    draw_card(920, 560, 400, 120, "refresh", "#7C3AED", "CLOSED-LOOP", "Reverification Audit Engine",
              ["• Revised output is automatically looped back through Stages 1 - 4",
               "• Verification Invariant: Mathematically guarantees 0 contradictions",
               "• Emits reverification certification and side-by-side diff view"])

    # Pass Card
    svg.append('  <rect x="920" y="705" width="400" height="55" rx="6" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5"/>')
    svg.append(f'  <g transform="translate(936, 720) scale(1.1)" color="#16A34A">{icons["shield_check"]}</g>')
    svg.append('  <text x="975" y="726" fill="#14532D" font-size="12" font-weight="700">Audit Complete: Verified Factual Output</text>')
    svg.append('  <text x="975" y="744" fill="#15803D" font-size="10.5">0 Contradictions • Evidence Provenance Grounded • Ready for Export &amp; UI</text>')
    svg.append('  <rect x="1235" y="718" width="70" height="20" rx="3" fill="#16A34A"/>')
    svg.append('  <text x="1270" y="732" fill="#FFFFFF" font-size="9" font-weight="700" text-anchor="middle">CERTIFIED</text>')

    # Zone 4 Cards
    draw_card(1380, 145, 360, 145, "gpu", "#059669", "RTX 3050 (4GB)", "Dedicated GPU Allocation",
              ["• Ollama LLM Runtime: Dedicated to qwen3:8b",
               "• Working VRAM: ~2.4 GB VRAM (≤ 60% GPU threshold)",
               "• Roles: Mode B Response Synthesis &amp; Stage 6 Grounded Correction",
               "• Prevents fatal CUDA Out-Of-Memory (OOM) concurrency crashes"])

    draw_card(1380, 310, 360, 155, "cpu", "#2563EB", "HOST CPU &amp; RAM", "Verification Pipeline Compute",
              ["• Sentence-Transformers: all-MiniLM-L6-v2 (384-dim, CPU)",
               "• Cross-Encoder NLI: nli-deberta-v3-small (44M params, CPU)",
               "• FAISS Index: IndexFlatIP cosine search in RAM",
               "• Working Memory Footprint: ~3.2 GB Host System RAM",
               "• Zero VRAM competition between LLM and Verification models"])

    draw_card(1380, 485, 360, 195, "trophy", "#0F172A", "BENCHMARKS", "Empirical Evaluation Metrics",
              ["• FEVER Fact Verification Accuracy: 90.0% (Macro F1: 89.9%)",
               "• FEVER Recall@3 (Evidence Retrieval): 100.0%",
               "• Claim Decomposition Latency: 42 ms",
               "• FAISS Vector Search Latency: 18 ms",
               "• Cross-Encoder NLI Latency: 212 ms",
               "• Warm Verification Total: 296 ms (< 0.6 seconds)",
               "• Cloud API Cost: $0.00 / query (100% Offline &amp; Private)"])

    # Zone 5 Cards
    draw_card(60, 945, 410, 145, "server", "#0284C7", "FASTAPI", "High-Throughput Asynchronous Backend",
              ["• REST Endpoints: /verify, /verify-stream, /upload, /documents, /health",
               "• Asynchronous ASGI pipeline with Pydantic request validation &amp; CORS middleware",
               "• Structured error reporting with deterministic reason codes (NO_DOCUMENTS_INDEXED)"])

    draw_card(490, 945, 360, 145, "database", "#4F46E5", "SQLITE", "Relational Database Persistence",
              ["• File: data/truthguard.db (Local, Zero-cloud)",
               "• Schema Tables: verification_runs, claims, evidence, documents",
               "• Stores audit trail, character offsets, verdicts, hallucination scores &amp; SHA-256 hashes"])

    draw_card(870, 945, 870, 145, "layout", "#0D9488", "REACT 18", "Modern Interactive Audit Dashboard",
              ["• Interactive Answer Inspector: Real-time span highlighting (Supported, Contradicted, Conflicting, Insufficient)",
               "• Hallucination Risk Gauge: Circular risk meter showing composite score S_risk, Contradiction Rate, and Unsupported Rate",
               "• Evidence Provenance Cards: Document name, page number, chunk ID, verbatim citation snippet, and similarity score",
               "• Diff Reverification View: Side-by-side inspection showing refuted assertions vs. grounded corrected text"])

    # Legend Bar
    svg.append('  <rect x="40" y="1130" width="1720" height="45" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1"/>')
    svg.append('  <text x="900" y="1158" fill="#475569" font-size="11" text-anchor="middle">'
               '<tspan font-weight="700" fill="#0F172A">PIPELINE LEGEND:   </tspan>'
               '<tspan fill="#0369A1">■ Ingestion &amp; Input Flow   </tspan>'
               '<tspan fill="#3730A3">■ Dense Vector Indexing (FAISS)   </tspan>'
               '<tspan fill="#92400E">■ DeBERTa-v3 Cross-Encoder NLI   </tspan>'
               '<tspan fill="#991B1B">■ Arbitration &amp; Risk Scoring   </tspan>'
               '<tspan fill="#5B21B6">■ Closed-Loop Reverification   </tspan>'
               '<tspan fill="#064E3B">■ Hardware Allocation</tspan></text>')

    # Connectors
    def draw_path(d, stroke, marker, dashed=False, stroke_w=1.5):
        dash_attr = 'stroke-dasharray="6,4"' if dashed else ''
        svg.append(f'  <path d="{d}" fill="none" stroke="{stroke}" stroke-width="{stroke_w}" {dash_attr} marker-end="url(#{marker})"/>')

    # Mode A / B -> Stage 1
    draw_path("M 390 177 L 450 177", "#2563EB", "arr-blue")
    draw_path("M 390 260 L 420 260 L 420 210 L 450 210", "#2563EB", "arr-blue")

    # Ingestion flow
    draw_path("M 225 380 L 225 480", "#64748B", "arr-slate")
    draw_path("M 225 465 L 225 480", "#64748B", "arr-slate")
    draw_path("M 225 550 L 225 565", "#6366F1", "arr-purple")
    draw_path("M 225 635 L 225 650", "#6366F1", "arr-purple")

    # FAISS -> Stage 2
    draw_path("M 390 685 L 420 685 L 420 355 L 450 355", "#6366F1", "arr-purple")

    # Stage 1 -> 2 -> 3 -> 4
    draw_path("M 655 270 L 655 295", "#2563EB", "arr-blue")
    draw_path("M 655 420 L 655 445", "#2563EB", "arr-blue")
    draw_path("M 655 590 L 655 615", "#DC2626", "arr-red")

    # Stage 4 -> Stage 5
    draw_path("M 860 690 L 880 690 L 880 215 L 920 215", "#DC2626", "arr-red")

    # Stage 5 -> Decision
    draw_path("M 1120 290 L 1120 315", "#6366F1", "arr-purple")

    # Decision -> Stage 6 (Yes)
    draw_path("M 1120 395 L 1120 420", "#DC2626", "arr-red")

    # Decision -> Pass (No)
    draw_path("M 1205 355 L 1260 355 L 1260 705", "#16A34A", "arr-green")

    # Stage 6 -> Reverification
    draw_path("M 1120 535 L 1120 560", "#6366F1", "arr-purple")

    # Closed-Loop Reverification Loopback (Stage 6 Reverif -> Stage 1)
    draw_path("M 920 620 L 880 620 L 880 180 L 860 180", "#7C3AED", "arr-loop", dashed=True, stroke_w=2.2)
    # Loopback Chip Callout on Path
    svg.append('  <rect x="790" y="270" width="180" height="24" rx="4" fill="#7C3AED" stroke="#5B21B6" stroke-width="1"/>')
    svg.append('  <text x="880" y="286" fill="#FFFFFF" font-size="9" font-weight="700" text-anchor="middle">CLOSED-LOOP RE-AUDIT INVARIANT</text>')

    # Reverification -> Pass
    draw_path("M 1120 680 L 1120 705", "#16A34A", "arr-green")

    # Pass -> FastAPI Backend
    draw_path("M 920 735 L 265 735 L 265 945", "#64748B", "arr-slate")

    # API -> DB & API -> UI
    draw_path("M 470 1017 L 490 1017", "#2563EB", "arr-blue")
    draw_path("M 850 1017 L 870 1017", "#64748B", "arr-slate")

    svg.append('</svg>')
    return '\n'.join(svg)

def generate_clean_png(output_path):
    """Generates an executive 300 DPI publication-grade PNG diagram."""
    plt.rcParams['font.sans-serif'] = ['Inter', 'Segoe UI', 'DejaVu Sans', 'Arial']
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, ax = plt.subplots(figsize=(24, 16), dpi=300)
    ax.set_xlim(0, 1800)
    ax.set_ylim(0, 1200)
    ax.invert_yaxis()
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')

    # Header Banner
    ax.add_patch(patches.FancyBboxPatch((40, 20), 1720, 65, boxstyle="round,pad=0,rounding_size=6",
                                        facecolor='#0F172A', edgecolor='#1E293B', linewidth=1))
    ax.text(60, 48, "TRUTHGUARD: END-TO-END SYSTEM ARCHITECTURE PIPELINE",
            color='#F8FAFC', fontsize=16, fontweight='bold', ha='left', va='center')
    ax.text(60, 68, "Local Multi-Stage Fact Verification, Cross-Encoder NLI, and Closed-Loop Hallucination Auditing",
            color='#94A3B8', fontsize=10, ha='left', va='center')
    ax.add_patch(patches.FancyBboxPatch((1440, 35), 300, 34, boxstyle="round,pad=0,rounding_size=6",
                                        facecolor='#1E293B', edgecolor='#0284C7', linewidth=1))
    ax.text(1590, 52, "IEEE ACADEMIC FORMAT • LOCAL • SUB-600ms",
            color='#38BDF8', fontsize=9.5, fontweight='bold', ha='center', va='center')

    # Container zones
    def draw_zone(x, y, w, h, title, col='#CBD5E1'):
        ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6",
                                            facecolor='#F8FAFC', edgecolor=col, linewidth=1.5))
        ax.plot([x, x+w], [y+30, y+30], color=col, linewidth=1)
        ax.text(x + 16, y + 17, title, color='#0F172A', fontsize=10.5, fontweight='bold', ha='left', va='center')

    draw_zone(40, 100, 370, 785, "1. KNOWLEDGE BASE & INPUT INGESTION", "#94A3B8")
    draw_zone(430, 100, 450, 785, "2. MULTI-STAGE VERIFICATION CORE", "#3B82F6")
    draw_zone(900, 100, 440, 785, "3. RISK SCORING & CLOSED-LOOP AUDIT", "#7C3AED")
    draw_zone(1360, 100, 400, 785, "4. WORKSTATION HARDWARE PARTITIONING", "#64748B")
    draw_zone(40, 905, 1720, 210, "5. API SERVING, DATABASE PERSISTENCE & USER EXPERIENCE LAYER", "#64748B")

    # Card function
    def draw_card(x, y, w, h, accent_col, tag, title, lines, is_diamond=False):
        if is_diamond:
            pts = [(x + w/2, y), (x + w, y + h/2), (x + w/2, y + h), (x, y + h/2)]
            poly = patches.Polygon(pts, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.5)
            ax.add_patch(poly)
            ax.text(x + w/2, y + h/2 - 6, title, color='#92400E', fontsize=10, fontweight='bold', ha='center', va='center')
            for i, line in enumerate(lines):
                ax.text(x + w/2, y + h/2 + 10 + i*12, line, color='#B45309', fontsize=8.5, ha='center', va='center')
            return

        ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6",
                                            facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1.2))
        ax.add_patch(patches.FancyBboxPatch((x+1.5, y+4), 3.5, h-8, boxstyle="round,pad=0,rounding_size=2",
                                            facecolor=accent_col, edgecolor='none'))
        ax.text(x + 14, y + 18, title, color='#0F172A', fontsize=10, fontweight='bold', ha='left', va='center')
        if tag:
            t_w = len(tag) * 6 + 10
            ax.add_patch(patches.FancyBboxPatch((x + w - t_w - 12, y + 9), t_w, 18, boxstyle="round,pad=0,rounding_size=3",
                                                facecolor=accent_col + '1A', edgecolor=accent_col + '66', linewidth=1))
            ax.text(x + w - t_w/2 - 12, y + 18, tag, color=accent_col, fontsize=7.5, fontweight='bold', ha='center', va='center')
        ax.plot([x+12, x+w-12], [y+32, y+32], color='#F1F5F9', linewidth=1)
        for i, line in enumerate(lines):
            ax.text(x + 14, y + 46 + i*14, line, color='#334155', fontsize=8.2, ha='left', va='center')

    # Zone 1
    draw_card(60, 145, 330, 65, "#0284C7", "MODE A", "Direct Query-Answer Input",
              ["• Ingests user inquiry paired with external candidate answer",
               "• Audits arbitrary LLM responses or human authored text"])
    draw_card(60, 225, 330, 70, "#0284C7", "MODE B", "Autonomous Generation Engine",
              ["• Inquiry passed to local LLM: Ollama qwen3:8b",
               "• Synthesizes response on dedicated GPU (~2.4 GB VRAM)"])
    draw_card(60, 310, 330, 70, "#0284C7", "PDF / TXT / MD", "Private Document Library",
              ["• Parsed via PyMuPDF (fitz) with character normalization",
               "• SHA-256 cryptographic deduplication hashing"])
    draw_card(60, 395, 330, 70, "#0284C7", "FEVER", "Benchmark Wikipedia Corpus",
              ["• 570 atomic Wikipedia articles • 1,000 evaluation pairs",
               "• Zero-Leakage Protocol: Gold labels withheld at retrieval"])
    draw_card(60, 480, 330, 70, "#4F46E5", "CHUNK=500", "Sliding-Window Chunking",
              ["• Character window C = 500, overlap O = 100 chars",
               "• Preserves exact paragraph boundaries, page # & chunk IDs"])
    draw_card(60, 565, 330, 70, "#4F46E5", "R^384", "Dense Embedding Engine",
              ["• all-MiniLM-L6-v2 (Sentence-Transformers on CPU)",
               "• Maps passage text into continuous L2-normalized R^384"])
    draw_card(60, 650, 330, 75, "#4F46E5", "FAISS", "IndexFlatIP Vector Storage",
              ["• Exact Inner Product evaluation: sim(q, v) = cos(θ)",
               "• Sub-20ms dense vector retrieval against indexed corpus"])
    draw_card(60, 740, 330, 65, "#DC2626", "GUARDRAIL", "Missing Corpus Safety Fallback",
              ["• If index is empty → Emits NO_DOCUMENTS_INDEXED",
               "• Calibration safety: Assigns confidence = null"])

    # Zone 2
    draw_card(450, 145, 410, 125, "#2563EB", "STAGE 1", "Syntactic Claim Decomposition",
              ["• Sentence boundary detection with coordinating conjunction regex",
               "• Splits compound clauses (and, but, whereas) into atomic hypotheses",
               "• Character Span Offsets: Stores exact [start_offset, end_offset]",
               "• Empirical classifier filters subjective / non-verifiable statements"])
    draw_card(450, 295, 410, 125, "#4F46E5", "STAGE 2", "Multi-Source Semantic Retrieval",
              ["• Encodes query claim into R^384 vector via MiniLM-L6 (CPU)",
               "• Executes FAISS inner product search for exact cosine similarity",
               "• Retrieves top-k candidate passages (k = 3, threshold τ_sim ≥ 0.25)",
               "• Zero matches trigger fallback reason: NO_EVIDENCE_RETRIEVED"])
    draw_card(450, 445, 410, 145, "#D97706", "STAGE 3", "Cross-Encoder NLI Inference",
              ["• Model: cross-encoder/nli-deberta-v3-small (44M params, CPU)",
               "• Token sequence: [CLS] Passage Premise [SEP] Atomic Claim [SEP]",
               "• Full all-to-all cross-attention across premise and hypothesis tokens",
               "• Softmax Logits: P(contradiction), P(entailment), P(neutral)",
               "• Calibrated Thresholds: τ_entail ≥ 0.55, τ_contra ≥ 0.50"])
    draw_card(450, 615, 410, 155, "#DC2626", "STAGE 4", "Multi-Evidence Arbitration Policy",
              ["• Supported: max P(entailment) ≥ 0.55 without contradiction",
               "• Contradicted: max P(contradiction) ≥ 0.50 without entailment",
               "• Conflicting: Distinct passages yield both P_e ≥ 0.55 AND P_c ≥ 0.50",
               "• Insufficient Evidence: Below thresholds, 0 retrieved, or subjective",
               "• Null Calibration: Unverifiable statements assigned confidence = null"])

    # Zone 3
    draw_card(920, 145, 400, 145, "#7C3AED", "STAGE 5", "Mathematical Hallucination Risk Scorer",
              ["• Contradiction Rate: R_contra = N_contra / max(1, N_verifiable)",
               "• Unsupported Rate: R_unsupp = (N_contra + N_insuff + N_conf) / N_total",
               "• Composite Risk: S_risk = min(1.0, 0.70·R_contra + 0.30·R_unsupp)",
               "• Explainability: Document provenance, page #, chunk ID & similarity"])
    draw_card(1035, 315, 170, 80, "#D97706", "", "Contradictions?", ["Detected?", "(N_contra > 0)"], is_diamond=True)
    draw_card(920, 420, 400, 115, "#7C3AED", "STAGE 6", "Evidence-Grounded Correction Engine",
              ["• Selectively replaces contradicted spans with verified ground truth",
               "• Context-constrained prompting via local Ollama qwen3:8b on GPU",
               "• Preserves supported sentences; rewrites only refuted clauses"])
    draw_card(920, 560, 400, 120, "#7C3AED", "CLOSED-LOOP", "Reverification Audit Engine",
              ["• Revised output is automatically looped back through Stages 1 - 4",
               "• Verification Invariant: Mathematically guarantees 0 contradictions",
               "• Emits reverification certification and side-by-side diff view"])

    # Pass Card
    ax.add_patch(patches.FancyBboxPatch((920, 705), 400, 55, boxstyle="round,pad=0,rounding_size=6",
                                        facecolor='#DCFCE7', edgecolor='#16A34A', linewidth=1.5))
    ax.plot([935, 940, 948], [732, 737, 727], color='#16A34A', linewidth=2.5, solid_capstyle='round')
    ax.text(960, 724, "Audit Complete: Verified Factual Output", color='#14532D', fontsize=10.5, fontweight='bold', ha='left', va='center')
    ax.text(960, 742, "0 Contradictions • Evidence Provenance Grounded • Ready for Export & UI", color='#15803D', fontsize=8.5, ha='left', va='center')
    ax.add_patch(patches.FancyBboxPatch((1240, 716), 65, 20, boxstyle="round,pad=0,rounding_size=3",
                                        facecolor='#16A34A', edgecolor='none'))
    ax.text(1272, 726, "CERTIFIED", color='white', fontsize=7.5, fontweight='bold', ha='center', va='center')

    # Zone 4
    draw_card(1380, 145, 360, 145, "#059669", "RTX 3050 (4GB)", "Dedicated GPU Allocation",
              ["• Ollama LLM Runtime: Dedicated to qwen3:8b",
               "• Working VRAM: ~2.4 GB VRAM (≤ 60% GPU threshold)",
               "• Roles: Mode B Response Synthesis & Stage 6 Grounded Correction",
               "• Prevents fatal CUDA Out-Of-Memory (OOM) concurrency crashes"])
    draw_card(1380, 310, 360, 155, "#2563EB", "HOST CPU & RAM", "Verification Pipeline Compute",
              ["• Sentence-Transformers: all-MiniLM-L6-v2 (384-dim, CPU)",
               "• Cross-Encoder NLI: nli-deberta-v3-small (44M params, CPU)",
               "• FAISS Index: IndexFlatIP cosine search in RAM",
               "• Working Memory Footprint: ~3.2 GB Host System RAM",
               "• Zero VRAM competition between LLM and Verification models"])
    draw_card(1380, 485, 360, 195, "#0F172A", "BENCHMARKS", "Empirical Evaluation Metrics",
              ["• FEVER Fact Verification Accuracy: 90.0% (Macro F1: 89.9%)",
               "• FEVER Recall@3 (Evidence Retrieval): 100.0%",
               "• Claim Decomposition Latency: 42 ms",
               "• FAISS Vector Search Latency: 18 ms",
               "• Cross-Encoder NLI Latency: 212 ms",
               "• Warm Verification Total: 296 ms (< 0.6 seconds)",
               "• Cloud API Cost: $0.00 / query (100% Offline & Private)"])

    # Zone 5
    draw_card(60, 945, 410, 145, "#0284C7", "FASTAPI", "High-Throughput Asynchronous Backend",
              ["• REST Endpoints: /verify, /verify-stream, /upload, /documents, /health",
               "• Asynchronous ASGI pipeline with Pydantic request validation & CORS middleware",
               "• Structured error reporting with deterministic reason codes (NO_DOCUMENTS_INDEXED)"])
    draw_card(490, 945, 360, 145, "#4F46E5", "SQLITE", "Relational Database Persistence",
              ["• File: data/truthguard.db (Local, Zero-cloud)",
               "• Schema Tables: verification_runs, claims, evidence, documents",
               "• Stores audit trail, character offsets, verdicts, hallucination scores & SHA-256 hashes"])
    draw_card(870, 945, 870, 145, "#0D9488", "REACT 18", "Modern Interactive Audit Dashboard",
              ["• Interactive Answer Inspector: Real-time span highlighting (Supported, Contradicted, Conflicting, Insufficient)",
               "• Hallucination Risk Gauge: Circular risk meter showing composite score S_risk, Contradiction Rate, and Unsupported Rate",
               "• Evidence Provenance Cards: Document name, page number, chunk ID, verbatim citation snippet, and similarity score",
               "• Diff Reverification View: Side-by-side inspection showing refuted assertions vs. grounded corrected text"])

    # Legend
    ax.add_patch(patches.FancyBboxPatch((40, 1130), 1720, 45, boxstyle="round,pad=0,rounding_size=6",
                                        facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1))
    ax.text(900, 1152, "PIPELINE LEGEND:   ■ Ingestion & Input Flow   ■ Dense Vector Indexing (FAISS)   ■ DeBERTa-v3 Cross-Encoder NLI   ■ Arbitration & Risk Scoring   ■ Closed-Loop Reverification   ■ Hardware Allocation",
            color='#475569', fontsize=9.5, fontweight='bold', ha='center', va='center')

    # Connectors
    def draw_arrow(x1, y1, x2, y2, col, dashed=False, lw=1.5):
        ls = '--' if dashed else '-'
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=col, lw=lw, linestyle=ls))

    draw_arrow(390, 177, 450, 177, '#2563EB')
    draw_arrow(390, 260, 450, 210, '#2563EB')
    draw_arrow(225, 380, 225, 480, '#64748B')
    draw_arrow(225, 465, 225, 480, '#64748B')
    draw_arrow(225, 550, 225, 565, '#6366F1')
    draw_arrow(225, 635, 225, 650, '#6366F1')
    draw_arrow(390, 685, 450, 355, '#6366F1')
    draw_arrow(655, 270, 655, 295, '#2563EB')
    draw_arrow(655, 420, 655, 445, '#2563EB')
    draw_arrow(655, 590, 655, 615, '#DC2626')
    draw_arrow(860, 690, 920, 215, '#DC2626')
    draw_arrow(1120, 290, 1120, 315, '#6366F1')
    draw_arrow(1120, 395, 1120, 420, '#DC2626')
    draw_arrow(1205, 355, 1260, 705, '#16A34A')
    draw_arrow(1120, 535, 1120, 560, '#6366F1')
    draw_arrow(920, 620, 860, 180, '#7C3AED', dashed=True, lw=2.2)
    ax.add_patch(patches.FancyBboxPatch((790, 270), 180, 24, boxstyle="round,pad=0,rounding_size=4",
                                        facecolor='#7C3AED', edgecolor='#5B21B6', linewidth=1))
    ax.text(880, 282, "CLOSED-LOOP RE-AUDIT INVARIANT", color='white', fontsize=7.5, fontweight='bold', ha='center', va='center')
    draw_arrow(1120, 680, 1120, 705, '#16A34A')
    draw_arrow(920, 735, 265, 945, '#64748B')
    draw_arrow(470, 1017, 490, 1017, '#2563EB')
    draw_arrow(850, 1017, 870, 1017, '#64748B')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Successfully generated clean high-res PNG at: {output_path}")

def main():
    out_dir = r"docs\figures"
    os.makedirs(out_dir, exist_ok=True)

    drawio_path = os.path.join(out_dir, "truthguard_architecture_pipeline.drawio")
    svg_path = os.path.join(out_dir, "truthguard_architecture_pipeline.svg")
    png_path = os.path.join(out_dir, "truthguard_architecture_pipeline.png")

    print("1. Generating Clean & Professional Draw.io diagram...")
    xml_content = generate_drawio_xml()
    with open(drawio_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"-> Saved clean Draw.io diagram to: {drawio_path}")

    print("2. Generating Clean Vector SVG diagram...")
    svg_content = generate_clean_svg()
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"-> Saved clean SVG diagram to: {svg_path}")

    print("3. Generating 300 DPI Publication-Grade PNG diagram...")
    generate_clean_png(png_path)

    print("\nAll clean, professional diagram assets successfully generated in docs/figures/!")

if __name__ == "__main__":
    main()
