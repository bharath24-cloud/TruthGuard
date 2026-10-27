"""
TruthGuard Architecture Pipeline - Draw.io XML, SVG, and High-Res PNG Generator
Generates Figure 3.1: TruthGuard End-to-End System Architecture Pipeline with rich icons and unique design.
"""
import os
import xml.sax.saxutils as saxutils
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_drawio_xml():
    """Generates the native Draw.io XML file with icon badges and unique styling."""
    
    page_w = 1800
    page_h = 1290
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<mxfile host="app.diagrams.net" modified="2026-10-19T12:00:00.000Z" agent="Mozilla/5.0" version="24.7.17" type="device">',
        '  <diagram id="TruthGuard-End-to-End-Architecture" name="TruthGuard End-to-End System Architecture Pipeline">',
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

    def add_icon_badge(badge_id, icon_char, bg_color, stroke_color, x, y, size=32):
        style = f"ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor={bg_color};strokeColor={stroke_color};strokeWidth=2;fontColor=#FFFFFF;fontSize=16;fontStyle=1;align=center;verticalAlign=middle;shadow=1;"
        add_cell(badge_id, icon_char, style, x, y, size, size)

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

    # 1. Title Banner
    add_cell(
        "title_banner",
        "<table style='width:100%;height:100%;color:#FFFFFF;'>"
        "<tr><td style='width:50px;text-align:center;font-size:28px;'>🛡️</td>"
        "<td style='text-align:center;'>"
        "<b style='font-size:18px;letter-spacing:1px;'>TRUTHGUARD: END-TO-END SYSTEM ARCHITECTURE PIPELINE</b><br/>"
        "<span style='font-size:12px;color:#93C5FD;'>Modular Multi-Stage Verification • Dual-Corpus FAISS Retrieval • DeBERTa-v3 Cross-Encoder NLI • Closed-Loop Reverification</span>"
        "</td>"
        "<td style='width:180px;text-align:right;font-size:11px;color:#E2E8F0;padding-right:15px;'>"
        "<span style='background:#1D4ED8;padding:3px 8px;border-radius:4px;border:1px solid #3B82F6;'>v2.4 LOCAL • 296ms</span>"
        "</td></tr></table>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#1E40AF;strokeWidth=2.5;fontColor=#FFFFFF;arcSize=8;",
        40, 20, 1720, 65
    )

    # 2. Containers / Zones
    # Zone 1: Input & Ingestion
    add_cell(
        "zone_ingestion",
        "📂  INPUT ACQUISITION & KNOWLEDGE BASE INGESTION",
        "swimlane;startSize=32;rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FDFA;strokeColor=#0D9488;strokeWidth=2;fontColor=#0F766E;fontStyle=1;fontSize=13;arcSize=6;collapsible=0;",
        40, 95, 370, 780
    )

    # Zone 2: Core Verification Pipeline
    add_cell(
        "zone_core_nlp",
        "🔬  CORE NLP VERIFICATION PIPELINE (STAGES 1 - 4)",
        "swimlane;startSize=32;rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#2563EB;strokeWidth=2;fontColor=#1D4ED8;fontStyle=1;fontSize=13;arcSize=6;collapsible=0;",
        430, 95, 450, 780
    )

    # Zone 3: Scoring & Closed Loop Reverification
    add_cell(
        "zone_scoring_reverif",
        "📊  RISK SCORING & CLOSED-LOOP REVERIFICATION",
        "swimlane;startSize=32;rounded=1;whiteSpace=wrap;html=1;fillColor=#FAF5FF;strokeColor=#7C3AED;strokeWidth=2;fontColor=#6B21A8;fontStyle=1;fontSize=13;arcSize=6;collapsible=0;",
        900, 95, 440, 780
    )

    # Zone 4: Hardware Partitioning
    add_cell(
        "zone_hardware",
        "⚡  HARDWARE PARTITIONING (4GB VRAM WORKSTATION)",
        "swimlane;startSize=32;rounded=1;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor=#475569;strokeWidth=2;fontColor=#1E293B;fontStyle=1;fontSize=13;arcSize=6;collapsible=0;",
        1360, 95, 400, 780
    )

    # Zone 1 Cards & Icon Badges
    # Mode A
    add_cell(
        "node_mode_a",
        "<div style='margin-left:36px;'>"
        "<span style='background:#0D9488;color:#FFF;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>MODE A</span> "
        "<b>Direct Verification</b><br/>"
        "<font style='font-size:11px;color:#134E4A;'>User Question + External Candidate Answer<br/>(Audits arbitrary external LLM or human text)</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#CCFBF1;strokeColor=#14B8A6;strokeWidth=1.5;fontColor=#134E4A;arcSize=8;align=left;",
        60, 140, 330, 65
    )
    add_icon_badge("ico_mode_a", "💬", "#0D9488", "#042F2E", 68, 154, 28)

    # Mode B
    add_cell(
        "node_mode_b",
        "<div style='margin-left:36px;'>"
        "<span style='background:#0D9488;color:#FFF;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>MODE B • GPU</span> "
        "<b>Autonomous Generation</b><br/>"
        "<font style='font-size:11px;color:#134E4A;'>User Question → Local LLM: <b>Ollama qwen3:8b</b><br/>Runs on GPU (~2.4 GB VRAM) → Synthesizes response</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#CCFBF1;strokeColor=#14B8A6;strokeWidth=1.5;fontColor=#134E4A;arcSize=8;align=left;",
        60, 220, 330, 70
    )
    add_icon_badge("ico_mode_b", "🤖", "#0D9488", "#042F2E", 68, 238, 28)

    # Private Docs
    add_cell(
        "node_doc_upload",
        "<div style='margin-left:36px;'>"
        "<span style='background:#0284C7;color:#FFF;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>PDF / TXT / MD</span> "
        "<b>Private Document Library</b><br/>"
        "<font style='font-size:11px;color:#0369A1;'>User Ingestion via PyMuPDF (fitz)<br/>Text Normalization & SHA-256 Deduplication</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E0F2FE;strokeColor=#0284C7;strokeWidth=1.5;fontColor=#0369A1;arcSize=8;align=left;",
        60, 310, 330, 70
    )
    add_icon_badge("ico_doc", "📄", "#0284C7", "#075985", 68, 328, 28)

    # FEVER Corpus
    add_cell(
        "node_fever_corpus",
        "<div style='margin-left:36px;'>"
        "<span style='background:#0284C7;color:#FFF;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>BENCHMARK</span> "
        "<b>FEVER Corpus (Wikipedia)</b><br/>"
        "<font style='font-size:11px;color:#0369A1;'>570 Pre-Processed Articles • 1,000 Pairs<br/><b>Zero-Leakage Protocol:</b> Gold labels withheld</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E0F2FE;strokeColor=#0284C7;strokeWidth=1.5;fontColor=#0369A1;arcSize=8;align=left;",
        60, 400, 330, 70
    )
    add_icon_badge("ico_fever", "🌐", "#0284C7", "#075985", 68, 418, 28)

    # Chunking
    add_cell(
        "node_chunking",
        "<div style='margin-left:36px;'>"
        "<span style='background:#7C3AED;color:#FFF;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>SEGMENTATION</span> "
        "<b>Sliding-Window Chunking</b><br/>"
        "<font style='font-size:11px;color:#5B21B6;'>Passage size <i>C = 500</i> chars, overlap <i>O = 100</i><br/>Preserves character provenance, page # & chunk IDs</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#EDE9FE;strokeColor=#7C3AED;strokeWidth=1.5;fontColor=#5B21B6;arcSize=8;align=left;",
        60, 490, 330, 70
    )
    add_icon_badge("ico_chunk", "✂️", "#7C3AED", "#4C1D95", 68, 508, 28)

    # Embedding
    add_cell(
        "node_passage_embed",
        "<div style='margin-left:36px;'>"
        "<span style='background:#4F46E5;color:#FFF;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>R^384 DENSE</span> "
        "<b>MiniLM-L6 Embedding</b><br/>"
        "<font style='font-size:11px;color:#3730A3;'><i>sentence-transformers/all-MiniLM-L6-v2</i><br/>Maps passages to L2-normalized vectors on CPU</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#4F46E5;strokeWidth=1.5;fontColor=#3730A3;arcSize=8;align=left;",
        60, 580, 330, 70
    )
    add_icon_badge("ico_embed", "📐", "#4F46E5", "#312E81", 68, 598, 28)

    # FAISS Store
    add_cell(
        "node_faiss_store",
        "<div style='margin-left:36px;'>"
        "<span style='background:#4F46E5;color:#FFF;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>FAISS IndexFlatIP</span> "
        "<b>Vector Store</b><br/>"
        "<font style='font-size:11px;color:#3730A3;'>Exact Cosine Similarity via Inner Product<br/><i>sim(q, v) = q_hat · v_hat = cos(θ)</i><br/>Sub-20ms queries across corpus</font>"
        "</div>",
        "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=12;fillColor=#EEF2FF;strokeColor=#4F46E5;strokeWidth=2;fontColor=#312E81;fontStyle=1;align=left;",
        60, 670, 330, 90
    )
    add_icon_badge("ico_faiss", "🗄️", "#4F46E5", "#312E81", 68, 695, 28)

    # Missing Guardrail
    add_cell(
        "node_empty_guard",
        "<div style='margin-left:36px;'>"
        "<span style='background:#DC2626;color:#FFF;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>GUARDRAIL</span> "
        "<b>Missing Corpus Fallback</b><br/>"
        "<font style='font-size:10.5px;color:#991B1B;'>No docs? → <i>NO_DOCUMENTS_INDEXED</i><br/>Confidence = null (No hallucinated verdict)</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FEE2E2;strokeColor=#EF4444;strokeWidth=1.5;fontColor=#991B1B;arcSize=8;align=left;",
        60, 780, 330, 65
    )
    add_icon_badge("ico_guard", "🛑", "#DC2626", "#7F1D1D", 68, 796, 28)

    # Zone 2 Cards & Icon Badges (Core Verification Stages 1 - 4)
    # Stage 1
    add_cell(
        "node_stage1",
        "<div style='margin-left:42px;'>"
        "<span style='background:#2563EB;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>STAGE 1</span> "
        "<b style='font-size:13px;color:#1E3A8A;'>Syntactic Atomic Claim Decomposition</b><br/>"
        "<font style='font-size:11px;color:#1E40AF;'>• Sentence boundary detection & regex coordinating conjunction split<br/>"
        "• <b>Character Span Tracking:</b> Exact <i>start_offset</i> & <i>end_offset</i> in text<br/>"
        "• <b>Empirical Classifier:</b> Tags subjective/unverifiable statements<br/>"
        "• <i>Output:</i> Stream of Atomic Propositional Claims {C_1, C_2, ..., C_N}</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#DBEAFE;strokeColor=#2563EB;strokeWidth=1.5;fontColor=#1E3A8A;arcSize=8;align=left;",
        450, 140, 410, 120
    )
    add_icon_badge("ico_s1", "🧩", "#2563EB", "#1E3A8A", 458, 155, 34)

    # Stage 2
    add_cell(
        "node_stage2",
        "<div style='margin-left:42px;'>"
        "<span style='background:#6366F1;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>STAGE 2</span> "
        "<b style='font-size:13px;color:#312E81;'>Multi-Source Semantic Evidence Retrieval</b><br/>"
        "<font style='font-size:11px;color:#3730A3;'>• Encodes atomic claim C_i into query vector q_hat via MiniLM-L6 (CPU)<br/>"
        "• FAISS IndexFlatIP inner-product search computes exact cosine similarity<br/>"
        "• Retrieves top-k candidate passages (k = 3, threshold τ_sim ≥ 0.25)<br/>"
        "• 0 matches? Emits <i>NO_EVIDENCE_RETRIEVED</i> (Confidence = null)</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#6366F1;strokeWidth=1.5;fontColor=#312E81;arcSize=8;align=left;",
        450, 295, 410, 125
    )
    add_icon_badge("ico_s2", "🔍", "#6366F1", "#312E81", 458, 312, 34)

    # Stage 3
    add_cell(
        "node_stage3",
        "<div style='margin-left:42px;'>"
        "<span style='background:#D97706;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>STAGE 3</span> "
        "<b style='font-size:13px;color:#78350F;'>Deep Cross-Encoder NLI Inference</b><br/>"
        "<font style='font-size:11px;color:#92400E;'>• Model: <b>cross-encoder/nli-deberta-v3-small</b> (44M params on CPU)<br/>"
        "• Input: <i>[CLS] Retrieved Passage E_j [SEP] Atomic Claim C_i [SEP]</i><br/>"
        "• Full all-to-all cross-attention across premise and hypothesis tokens<br/>"
        "• Softmax Logits: <b>P(contradiction), P(entailment), P(neutral)</b><br/>"
        "• <b>Calibrated Thresholds:</b> τ_entail ≥ 0.55, τ_contra ≥ 0.50</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#D97706;strokeWidth=1.5;fontColor=#78350F;arcSize=8;align=left;",
        450, 455, 410, 135
    )
    add_icon_badge("ico_s3", "🧠", "#D97706", "#78350F", 458, 472, 34)

    # Stage 4
    add_cell(
        "node_stage4",
        "<div style='margin-left:42px;'>"
        "<span style='background:#DC2626;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>STAGE 4</span> "
        "<b style='font-size:13px;color:#7F1D1D;'>Multi-Evidence Arbitration Policy</b><br/>"
        "<font style='font-size:11px;color:#991B1B;'>Deterministic 4-Way Decision Rules per Claim:<br/>"
        "• <b>SUPPORTED:</b> max P(entailment) ≥ 0.55 without contradiction<br/>"
        "• <b>CONTRADICTED:</b> max P(contradiction) ≥ 0.50 without strong entailment<br/>"
        "• <b>CONFLICTING:</b> Distinct passages show both P_e ≥ 0.55 AND P_c ≥ 0.50<br/>"
        "• <b>INSUFFICIENT EVIDENCE:</b> Below thresholds, 0 retrieved, or subjective<br/>"
        "• <i>Confidence Calibration:</i> Set to <b>null</b> for missing/unverifiable evidence</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FEE2E2;strokeColor=#DC2626;strokeWidth=1.5;fontColor=#7F1D1D;arcSize=8;align=left;",
        450, 625, 410, 165
    )
    add_icon_badge("ico_s4", "⚖️", "#DC2626", "#7F1D1D", 458, 645, 34)

    # Zone 3 Cards & Icon Badges (Risk Scoring & Closed Loop Reverification)
    # Stage 5
    add_cell(
        "node_stage5",
        "<div style='margin-left:42px;'>"
        "<span style='background:#DB2777;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>STAGE 5</span> "
        "<b style='font-size:13px;color:#831843;'>Mathematical Hallucination Risk Scorer</b><br/>"
        "<font style='font-size:11px;color:#9D174D;'>Deterministic empirical formulation (bounded in [0.0, 1.0]):<br/>"
        "• <b>Contradiction Rate:</b> <i>R_contra = N_contra / max(1, N_verifiable)</i><br/>"
        "• <b>Unsupported Rate:</b> <i>R_unsupp = (N_contra + N_insuff + N_conf) / N_total</i><br/>"
        "• <b>Composite Risk:</b> <i>S_risk = min(1.0, 0.70·R_contra + 0.30·R_unsupp)</i><br/>"
        "• <b>Explainability Engine:</b> Builds citation cards with doc name, page #,<br/>"
        "  chunk ID, verbatim quote snippet, and similarity score</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FDF2F8;strokeColor=#DB2777;strokeWidth=1.5;fontColor=#831843;arcSize=8;align=left;",
        920, 140, 400, 155
    )
    add_icon_badge("ico_s5", "🧮", "#DB2777", "#831843", 928, 155, 34)

    # Decision Diamond
    add_cell(
        "node_decision",
        "<b>⚠️ Contradictions<br/>Detected?</b><br/>"
        "<font style='font-size:10px;font-weight:normal;'>(N_contra &gt; 0)</font>",
        "rhombus;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#D97706;strokeWidth=2;fontColor=#92400E;fontStyle=1;align=center;",
        1035, 325, 170, 85
    )

    # Stage 6 Grounded Correction
    add_cell(
        "node_stage6_correction",
        "<div style='margin-left:42px;'>"
        "<span style='background:#7C3AED;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>STAGE 6</span> "
        "<b style='font-size:13px;color:#4C1D95;'>Evidence-Grounded Correction Engine</b><br/>"
        "<font style='font-size:11px;color:#5B21B6;'>• Replaces contradicted spans with ground truth facts<br/>"
        "• Context-Constrained Prompting with retrieved reference passages<br/>"
        "• Local LLM: <b>Ollama qwen3:8b</b> on GPU (~2.4 GB VRAM)<br/>"
        "• Preserves supported sentences; rewrites only refuted clauses</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#EDE9FE;strokeColor=#7C3AED;strokeWidth=1.5;fontColor=#4C1D95;arcSize=8;align=left;",
        920, 445, 400, 120
    )
    add_icon_badge("ico_s6", "✍️", "#7C3AED", "#4C1D95", 928, 460, 34)

    # Closed-Loop Reverification
    add_cell(
        "node_stage6_reverify",
        "<div style='margin-left:42px;'>"
        "<span style='background:#7C3AED;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>CLOSED-LOOP</span> "
        "<b style='font-size:13px;color:#4C1D95;'>Reverification Audit Engine</b><br/>"
        "<font style='font-size:11px;color:#5B21B6;'>• Corrected text is automatically looped back to <b>Stages 1 - 4</b><br/>"
        "• Decomposes revised answer and re-queries FAISS + NLI<br/>"
        "• <b>Verification Invariant:</b> Guarantees <b>0 remaining contradictions</b><br/>"
        "• Emits reverification badge & side-by-side diff comparison</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#EDE9FE;strokeColor=#7C3AED;strokeWidth=2;fontColor=#4C1D95;arcSize=8;align=left;",
        920, 600, 400, 125
    )
    add_icon_badge("ico_reverify", "🔄", "#7C3AED", "#4C1D95", 928, 615, 34)

    # Audit Pass
    add_cell(
        "node_audit_pass",
        "<table style='width:100%;height:100%;color:#14532D;'>"
        "<tr><td style='width:35px;font-size:22px;text-align:center;'>✅</td>"
        "<td><b>Audit Complete: Verified Factual Output</b><br/>"
        "<font style='font-size:10.5px;color:#15803D;'>0 Contradictions • Evidence Provenance Bound • Streamed to API & UI</font>"
        "</td></tr></table>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#DCFCE7;strokeColor=#16A34A;strokeWidth=2;fontColor=#14532D;arcSize=8;",
        920, 765, 400, 55
    )

    # Zone 4 Cards & Icon Badges (Hardware Budgeting)
    # GPU Box
    add_cell(
        "node_gpu_box",
        "<div style='margin-left:42px;'>"
        "<span style='background:#059669;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>NVIDIA GPU</span> "
        "<b style='font-size:13px;color:#064E3B;'>RTX 3050 Laptop (4 GB)</b><br/>"
        "<font style='font-size:11px;color:#047857;'><b>Dedicated to Generative LLM:</b><br/>"
        "• <b>Ollama Runtime</b> running <i>qwen3:8b</i> (or <i>qwen2.5:3b</i>)<br/>"
        "• VRAM Allocation: <b>~2.4 GB VRAM</b> (&le; 60% capacity)<br/>"
        "• <b>Roles:</b> Mode B Generation & Stage 6 Grounded Correction<br/>"
        "• Zero competition with embedding or NLI models<br/>"
        "• <b>Prevents CUDA Out-Of-Memory (OOM) fatal crashes</b></font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#059669;strokeWidth=1.5;fontColor=#064E3B;arcSize=8;align=left;",
        1380, 140, 360, 170
    )
    add_icon_badge("ico_gpu", "⚡", "#059669", "#064E3B", 1388, 155, 34)

    # CPU Box
    add_cell(
        "node_cpu_box",
        "<div style='margin-left:42px;'>"
        "<span style='background:#2563EB;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>HOST CPU</span> "
        "<b style='font-size:13px;color:#1E3A8A;'>CPU & Multi-Threaded RAM</b><br/>"
        "<font style='font-size:11px;color:#1E40AF;'><b>Dedicated to Verification Pipeline:</b><br/>"
        "• <b>Sentence-Transformers:</b> <i>all-MiniLM-L6-v2</i> (384-dim)<br/>"
        "• <b>Cross-Encoder NLI:</b> <i>nli-deberta-v3-small</i> (44M params)<br/>"
        "• <b>FAISS Index:</b> <i>IndexFlatIP</i> vector search<br/>"
        "• Working Set Memory: <b>~3.2 GB</b> Host System RAM<br/>"
        "• PyTorch CPU threads enable fast parallel inference</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#2563EB;strokeWidth=1.5;fontColor=#1E3A8A;arcSize=8;align=left;",
        1380, 335, 360, 170
    )
    add_icon_badge("ico_cpu", "💻", "#2563EB", "#1E3A8A", 1388, 350, 34)

    # Benchmarks Box
    add_cell(
        "node_bench_box",
        "<div style='margin-left:42px;'>"
        "<span style='background:#EF4444;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>BENCHMARKS</span> "
        "<b style='font-size:13px;color:#7F1D1D;'>Local Empirical Metrics</b><br/>"
        "<font style='font-size:11px;color:#991B1B;'><b>Measured Results on Local System:</b><br/>"
        "• <b>FEVER Accuracy:</b> <b>90.0%</b> (Macro F1: 89.9%)<br/>"
        "• <b>FEVER Recall@3:</b> <b>100.0%</b> (Zero-leakage Wikipedia)<br/>"
        "• <b>Claim Extraction Latency:</b> 42 ms<br/>"
        "• <b>FAISS Vector Search Latency:</b> 18 ms<br/>"
        "• <b>Cross-Encoder NLI Latency:</b> 212 ms<br/>"
        "• <b>Arbitration & Scoring Latency:</b> 24 ms<br/>"
        "• <b>Warm Verification Total:</b> <b>296 ms</b> (&lt; 0.6 s)<br/>"
        "• <b>Operational API Cost:</b> <b>$0.00</b> (100% Local / Offline)</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF2F2;strokeColor=#EF4444;strokeWidth=1.5;fontColor=#7F1D1D;arcSize=8;align=left;",
        1380, 530, 360, 220
    )
    add_icon_badge("ico_bench", "🏆", "#EF4444", "#7F1D1D", 1388, 545, 34)

    # Zone 5: Serving, Persistence & UI
    add_cell(
        "zone_serving",
        "🚀  API SERVING, DATABASE PERSISTENCE & USER EXPERIENCE LAYER",
        "swimlane;startSize=30;rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#0284C7;strokeWidth=2;fontColor=#0369A1;fontStyle=1;fontSize=13;arcSize=6;collapsible=0;",
        40, 895, 1720, 220
    )

    add_cell(
        "node_api",
        "<div style='margin-left:42px;'>"
        "<span style='background:#0284C7;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>REST API</span> "
        "<b style='font-size:13px;color:#0369A1;'>FastAPI Asynchronous Backend Engine</b><br/>"
        "<font style='font-size:11px;color:#0284C7;'>• Endpoints: <code>/verify</code>, <code>/verify-stream</code>, <code>/upload</code>, <code>/documents</code>, <code>/health</code><br/>"
        "• Asynchronous request pipeline with CORS middleware & Pydantic validation<br/>"
        "• Multi-document ingestion endpoint with automated sliding-window chunking<br/>"
        "• Deterministic reason codes (<code>NO_DOCUMENTS_INDEXED</code>, <code>NO_EVIDENCE_RETRIEVED</code>)</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E0F2FE;strokeColor=#0284C7;strokeWidth=1.5;fontColor=#0369A1;arcSize=8;align=left;",
        60, 940, 410, 155
    )
    add_icon_badge("ico_api", "⚡", "#0284C7", "#0369A1", 68, 955, 34)

    add_cell(
        "node_db",
        "<div style='margin-left:42px;'>"
        "<span style='background:#4F46E5;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>SQLITE</span> "
        "<b style='font-size:13px;color:#312E81;'>SQLite Relational Persistence</b><br/>"
        "<font style='font-size:11px;color:#3730A3;'>• File: <code>data/truthguard.db</code><br/>"
        "• Tables: <code>verification_runs</code>, <code>claims</code>, <code>evidence</code>, <code>documents</code><br/>"
        "• Persists complete audit trail, claim offsets, verdicts & risk scores<br/>"
        "• Ingested document registry with SHA-256 deduplication hashing</font>"
        "</div>",
        "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=12;fillColor=#EEF2FF;strokeColor=#4F46E5;strokeWidth=1.5;fontColor=#312E81;fontStyle=1;align=left;",
        490, 940, 360, 155
    )
    add_icon_badge("ico_db", "💾", "#4F46E5", "#312E81", 498, 960, 34)

    add_cell(
        "node_ui",
        "<div style='margin-left:42px;'>"
        "<span style='background:#0D9488;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:bold;'>WEB UI</span> "
        "<b style='font-size:13px;color:#0F766E;'>Modern React 18 + TailwindCSS Dashboard User Interface</b><br/>"
        "<font style='font-size:11px;color:#0F766E;'>• <b>Interactive Answer Inspector:</b> Real-time color-coded inline span highlights (Green = Supported, Red = Contradicted, Yellow = Conflicting, Gray = Insufficient)<br/>"
        "• <b>Hallucination Risk Gauge:</b> Animated circular risk meter showing composite score S_risk, Contradiction Rate, and Unsupported Claim Rate<br/>"
        "• <b>Evidence Provenance Cards:</b> Displays document title, page number, chunk ID, verbatim excerpt snippet, and cosine similarity badge<br/>"
        "• <b>Diff Reverification View:</b> Side-by-side inspection showing original refuted claims vs. evidence-grounded corrected text</font>"
        "</div>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FDFA;strokeColor=#0D9488;strokeWidth=1.5;fontColor=#134E4A;arcSize=8;align=left;",
        870, 940, 870, 155
    )
    add_icon_badge("ico_ui", "🖥️", "#0D9488", "#0F766E", 878, 955, 34)

    # Legend Bar
    add_cell(
        "node_legend",
        "<font style='font-size:11px;'><b>LEGEND & ICONS:</b> &nbsp;&nbsp; "
        "<span style='background-color:#CCFBF1;color:#134E4A;padding:2px 8px;border-radius:4px;border:1px solid #14B8A6;'>💬 Input Modes</span> &nbsp;&nbsp; "
        "<span style='background-color:#E0F2FE;color:#0369A1;padding:2px 8px;border-radius:4px;border:1px solid #0284C7;'>📄 Document &amp; FEVER Corpus</span> &nbsp;&nbsp; "
        "<span style='background-color:#EEF2FF;color:#3730A3;padding:2px 8px;border-radius:4px;border:1px solid #4F46E5;'>📐 Embeddings &amp; 🗄️ FAISS Retrieval</span> &nbsp;&nbsp; "
        "<span style='background-color:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:4px;border:1px solid #D97706;'>🧠 DeBERTa-v3 Cross-Encoder NLI</span> &nbsp;&nbsp; "
        "<span style='background-color:#FEE2E2;color:#991B1B;padding:2px 8px;border-radius:4px;border:1px solid #DC2626;'>⚖️ Arbitration &amp; 🧮 Risk Scoring</span> &nbsp;&nbsp; "
        "<span style='background-color:#EDE9FE;color:#5B21B6;padding:2px 8px;border-radius:4px;border:1px solid #7C3AED;'>✍️ Grounded Correction &amp; 🔄 Closed Loop</span> &nbsp;&nbsp; "
        "<span style='background-color:#ECFDF5;color:#047857;padding:2px 8px;border-radius:4px;border:1px solid #059669;'>⚡ Hardware Budgeting</span></font>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#94A3B8;strokeWidth=1.5;fontColor=#334155;arcSize=6;align=center;",
        40, 1130, 1720, 50
    )

    # Connecting Edges
    edge_style_blue = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2563EB;strokeWidth=2;endArrow=classic;endFill=1;fontColor=#1E293B;fontSize=10;"
    edge_style_purple = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#7C3AED;strokeWidth=2;endArrow=classic;endFill=1;fontColor=#5B21B6;fontSize=10;"
    edge_style_teal = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0D9488;strokeWidth=2;endArrow=classic;endFill=1;fontColor=#134E4A;fontSize=10;"
    edge_style_red = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=2;endArrow=classic;endFill=1;fontColor=#991B1B;fontSize=10;"
    edge_style_green = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;endArrow=classic;endFill=1;fontColor=#15803D;fontSize=10;"
    edge_style_loop = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#9333EA;strokeWidth=3;dashed=1;dashPattern=6 3;endArrow=classic;endFill=1;fontColor=#6B21A8;fontSize=11;fontStyle=1;"

    # Mode A -> Stage 1
    add_edge("e_mode_a_s1", "Candidate Answer", edge_style_blue, "node_mode_a", "node_stage1")
    # Mode B -> Stage 1
    add_edge("e_mode_b_s1", "Synthesized Response", edge_style_blue, "node_mode_b", "node_stage1")

    # Ingestion flow
    add_edge("e_doc_chunk", "Raw Text", edge_style_teal, "node_doc_upload", "node_chunking")
    add_edge("e_fever_chunk", "Wikipedia Articles", edge_style_teal, "node_fever_corpus", "node_chunking")
    add_edge("e_chunk_embed", "Overlapping Chunks (500 chars)", edge_style_purple, "node_chunking", "node_passage_embed")
    add_edge("e_embed_faiss", "L2 Normalized R^384 Vectors", edge_style_purple, "node_passage_embed", "node_faiss_store")

    # Stage 1 -> Stage 2
    add_edge("e_s1_s2", "Atomic Claims {C_i} + Character Offsets", edge_style_blue, "node_stage1", "node_stage2")
    # FAISS -> Stage 2
    add_edge("e_faiss_s2", "Top-3 Matches (Inner Product sim ≥ 0.25)", edge_style_purple, "node_faiss_store", "node_stage2", points=[(410, 715), (410, 360)])
    # Stage 2 -> Stage 3
    add_edge("e_s2_s3", "Retrieved Context Passages + Claim Pairs", edge_style_blue, "node_stage2", "node_stage3")
    # Stage 3 -> Stage 4
    add_edge("e_s3_s4", "Softmax Probabilities [P_c, P_e, P_n]", edge_style_red, "node_stage3", "node_stage4")

    # Stage 4 -> Stage 5
    add_edge("e_s4_s5", "4-Way Claim Verdicts", edge_style_red, "node_stage4", "node_stage5", points=[(880, 710), (880, 220)])

    # Stage 5 -> Decision
    add_edge("e_s5_dec", "Contradiction Count", edge_style_purple, "node_stage5", "node_decision")

    # Decision -> Stage 6 Correction (Yes)
    add_edge("e_dec_corr", "Yes (N_contra > 0)", edge_style_red, "node_decision", "node_stage6_correction")

    # Decision -> Audit Pass (No)
    add_edge("e_dec_pass", "No (0 Contradictions)", edge_style_green, "node_decision", "node_audit_pass", points=[(1120, 410), (1240, 410), (1240, 790)])

    # Stage 6 Correction -> Reverification
    add_edge("e_corr_reverif", "Corrected Text + Context", edge_style_purple, "node_stage6_correction", "node_stage6_reverify")

    # Reverification -> Stage 1 (Closed-Loop Reverification Loopback!)
    add_edge("e_reverif_loop", "CLOSED-LOOP REVERIFICATION AUDIT (GUARANTEES 0 CONTRADICTIONS)", edge_style_loop, "node_stage6_reverify", "node_stage1", points=[(920, 665), (880, 665), (880, 180)])

    # Reverification -> Audit Pass
    add_edge("e_reverif_pass", "Verified Factual", edge_style_green, "node_stage6_reverify", "node_audit_pass")

    # Audit Pass -> FastAPI Backend
    add_edge("e_pass_api", "Verified Audit Payload", edge_style_teal, "node_audit_pass", "node_api", points=[(1120, 845), (265, 845)])

    # API -> DB
    add_edge("e_api_db", "Persist Run, Claims & Metrics", edge_style_blue, "node_api", "node_db")

    # API -> React UI
    add_edge("e_api_ui", "Stream Verified JSON & Provenance", edge_style_teal, "node_api", "node_ui", points=[(265, 1100), (900, 1100)])

    # XML Footer
    xml_lines.append('      </root>')
    xml_lines.append('    </mxGraphModel>')
    xml_lines.append('  </diagram>')
    xml_lines.append('</mxfile>')

    return '\n'.join(xml_lines)

def generate_svg():
    """Generates an enhanced standalone scalable vector SVG representation with vector icon glyphs and unique cards."""
    svg_lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 1220" width="100%" height="100%" style="background-color: #F8FAFC; font-family: \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;">',
        '  <defs>',
        '    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563EB"/>',
        '    </marker>',
        '    <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7C3AED"/>',
        '    </marker>',
        '    <marker id="arrow-teal" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0D9488"/>',
        '    </marker>',
        '    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#DC2626"/>',
        '    </marker>',
        '    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#16A34A"/>',
        '    </marker>',
        '    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">',
        '      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.10"/>',
        '    </filter>',
        '    <linearGradient id="header-grad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#0F172A" />',
        '      <stop offset="50%" stop-color="#1E3A8A" />',
        '      <stop offset="100%" stop-color="#0F172A" />',
        '    </linearGradient>',
        '  </defs>',
    ]

    # Title Banner with Logo Shield Icon
    svg_lines.append('  <rect x="40" y="20" width="1720" height="65" rx="8" fill="url(#header-grad)" stroke="#1E40AF" stroke-width="2.5" filter="url(#shadow)"/>')
    # Shield vector icon
    svg_lines.append('  <g transform="translate(65, 32) scale(1.6)">'
                     '    <path d="M 12 2 L 4 5 L 4 11 C 4 16.5 7.5 21.5 12 23 C 16.5 21.5 20 16.5 20 11 L 20 5 Z" fill="#2563EB" stroke="#60A5FA" stroke-width="1.5"/>'
                     '    <path d="M 9 12 L 11 14 L 15 9" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
                     '  </g>')
    svg_lines.append('  <text x="900" y="48" fill="#FFFFFF" font-size="19" font-weight="bold" text-anchor="middle" letter-spacing="1">TRUTHGUARD: END-TO-END SYSTEM ARCHITECTURE PIPELINE</text>')
    svg_lines.append('  <text x="900" y="70" fill="#93C5FD" font-size="12" text-anchor="middle">Modular Multi-Stage Verification • Dual-Corpus FAISS Retrieval • DeBERTa-v3 Cross-Encoder NLI • Closed-Loop Reverification</text>')
    svg_lines.append('  <rect x="1560" y="34" width="170" height="36" rx="6" fill="#1D4ED8" stroke="#3B82F6" stroke-width="1"/>')
    svg_lines.append('  <text x="1645" y="57" fill="#FFFFFF" font-size="11" font-weight="bold" text-anchor="middle">v2.4 LOCAL • 296ms</text>')

    # Containers
    def draw_box(x, y, w, h, icon_sym, title, fill, stroke, title_color):
        svg_lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2" filter="url(#shadow)"/>')
        svg_lines.append(f'  <path d="M {x} {y+32} L {x+w} {y+32}" stroke="{stroke}" stroke-width="1.5"/>')
        svg_lines.append(f'  <text x="{x+20}" y="{y+21}" fill="{title_color}" font-size="13" font-weight="bold">{icon_sym}  {title}</text>')

    draw_box(40, 95, 370, 780, "📂", "INPUT ACQUISITION &amp; KNOWLEDGE BASE INGESTION", "#F0FDFA", "#0D9488", "#0F766E")
    draw_box(430, 95, 450, 780, "🔬", "CORE NLP VERIFICATION PIPELINE (STAGES 1 - 4)", "#F8FAFC", "#2563EB", "#1D4ED8")
    draw_box(900, 95, 440, 780, "📊", "RISK SCORING &amp; CLOSED-LOOP REVERIFICATION", "#FAF5FF", "#7C3AED", "#6B21A8")
    draw_box(1360, 95, 400, 780, "⚡", "HARDWARE PARTITIONING (4GB VRAM BUDGET)", "#F1F5F9", "#475569", "#1E293B")
    draw_box(40, 895, 1720, 220, "🚀", "API SERVING, DATABASE PERSISTENCE &amp; USER EXPERIENCE LAYER", "#F8FAFC", "#0284C7", "#0369A1")

    # Card with Icon Badge Helper
    def draw_icon_card(x, y, w, h, icon_char, badge_text, title, lines, fill, stroke, text_color, badge_bg="#2563EB", is_diamond=False):
        if is_diamond:
            cx, cy = x + w/2, y + h/2
            svg_lines.append(f'  <polygon points="{cx},{y} {x+w},{cy} {cx},{y+h} {x},{cy}" fill="{fill}" stroke="{stroke}" stroke-width="2" filter="url(#shadow)"/>')
            svg_lines.append(f'  <text x="{cx}" y="{cy-8}" fill="{text_color}" font-size="12" font-weight="bold" text-anchor="middle">{icon_char} {saxutils.escape(title)}</text>')
            for i, line in enumerate(lines):
                l_esc = saxutils.escape(line)
                svg_lines.append(f'  <text x="{cx}" y="{cy+10 + i*14}" fill="{text_color}" font-size="10" text-anchor="middle">{l_esc}</text>')
            return

        svg_lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5" filter="url(#shadow)"/>')
        # Circular Icon Badge
        svg_lines.append(f'  <circle cx="{x+25}" cy="{y+25}" r="15" fill="{badge_bg}" stroke="{stroke}" stroke-width="1.5"/>')
        svg_lines.append(f'  <text x="{x+25}" y="{y+30}" fill="#FFFFFF" font-size="14" text-anchor="middle">{icon_char}</text>')
        
        # Pill Tag
        if badge_text:
            b_esc = saxutils.escape(badge_text)
            b_w = len(badge_text) * 6.5 + 12
            svg_lines.append(f'  <rect x="{x+48}" y="{y+10}" width="{b_w}" height="16" rx="4" fill="{badge_bg}"/>')
            svg_lines.append(f'  <text x="{x+48 + b_w/2}" y="{y+22}" fill="#FFFFFF" font-size="9.5" font-weight="bold" text-anchor="middle">{b_esc}</text>')
            title_x = x + 54 + b_w
        else:
            title_x = x + 48

        # Title
        t_esc = saxutils.escape(title)
        svg_lines.append(f'  <text x="{title_x}" y="{y+23}" fill="{text_color}" font-size="12" font-weight="bold">{t_esc}</text>')
        
        # Content lines
        for i, line in enumerate(lines):
            l_esc = saxutils.escape(line)
            svg_lines.append(f'  <text x="{x+14}" y="{y+46 + i*16}" fill="{text_color}" font-size="10.5">{l_esc}</text>')

    # Zone 1 Cards
    draw_icon_card(60, 140, 330, 65, "💬", "MODE A", "Direct Verification",
                   ["User Question + External Candidate Answer", "(Audits arbitrary external LLM or human text)"],
                   "#CCFBF1", "#14B8A6", "#134E4A", badge_bg="#0D9488")

    draw_icon_card(60, 220, 330, 70, "🤖", "MODE B • GPU", "Autonomous Generation",
                   ["User Question → Local LLM: Ollama qwen3:8b", "Runs on GPU (~2.4 GB VRAM) → Synthesizes response"],
                   "#CCFBF1", "#14B8A6", "#134E4A", badge_bg="#0D9488")

    draw_icon_card(60, 310, 330, 70, "📄", "PDF / TXT / MD", "Private Document Library",
                   ["User Ingestion via PyMuPDF (fitz)", "Text Normalization &amp; SHA-256 Deduplication"],
                   "#E0F2FE", "#0284C7", "#0369A1", badge_bg="#0284C7")

    draw_icon_card(60, 400, 330, 70, "🌐", "BENCHMARK", "FEVER Benchmark Corpus",
                   ["570 Pre-Processed Articles • 1,000 Pairs", "Zero-Leakage Protocol: Gold labels withheld"],
                   "#E0F2FE", "#0284C7", "#0369A1", badge_bg="#0284C7")

    draw_icon_card(60, 490, 330, 70, "✂️", "SEGMENTATION", "Sliding-Window Chunking",
                   ["Passage size C = 500 chars, overlap O = 100", "Preserves character provenance, page # &amp; chunk IDs"],
                   "#EDE9FE", "#7C3AED", "#5B21B6", badge_bg="#7C3AED")

    draw_icon_card(60, 580, 330, 70, "📐", "R^384 DENSE", "MiniLM-L6 Embedding",
                   ["sentence-transformers/all-MiniLM-L6-v2", "Maps passages to L2-normalized vectors on CPU"],
                   "#EEF2FF", "#4F46E5", "#3730A3", badge_bg="#4F46E5")

    draw_icon_card(60, 670, 330, 90, "🗄️", "FAISS IndexFlatIP", "Vector Store",
                   ["Exact Cosine Similarity via Inner Product", "sim(q, v) = q_hat · v_hat = cos(θ)", "Sub-20ms queries across corpus"],
                   "#EEF2FF", "#4F46E5", "#312E81", badge_bg="#4F46E5")

    draw_icon_card(60, 780, 330, 65, "🛑", "GUARDRAIL", "Missing Corpus Fallback",
                   ["No docs uploaded? → NO_DOCUMENTS_INDEXED", "Confidence = null (Honest uncalibrated verdict)"],
                   "#FEE2E2", "#EF4444", "#991B1B", badge_bg="#DC2626")

    # Zone 2 Cards (Core NLP Stages 1 - 4)
    draw_icon_card(450, 140, 410, 120, "🧩", "STAGE 1", "Syntactic Claim Decomposition",
                   ["• Sentence boundary detection &amp; regex coordinating conjunction split",
                    "• Character Span Tracking: Exact start_offset &amp; end_offset in text",
                    "• Empirical Classifier: Tags subjective / non-verifiable claims",
                    "• Output: Stream of Atomic Hypotheses {C_1, C_2, ..., C_N}"],
                   "#DBEAFE", "#2563EB", "#1E3A8A", badge_bg="#2563EB")

    draw_icon_card(450, 295, 410, 125, "🔍", "STAGE 2", "Multi-Source Semantic Retrieval",
                   ["• Encodes atomic claim C_i into query vector q_hat via MiniLM-L6 (CPU)",
                    "• FAISS IndexFlatIP inner-product search computes exact cosine similarity",
                    "• Retrieves top-k candidate passages (k = 3, threshold τ_sim ≥ 0.25)",
                    "• 0 matches? Emits NO_EVIDENCE_RETRIEVED (Confidence = null)"],
                   "#EEF2FF", "#6366F1", "#312E81", badge_bg="#6366F1")

    draw_icon_card(450, 455, 410, 135, "🧠", "STAGE 3", "Deep Cross-Encoder NLI Inference",
                   ["• Model: cross-encoder/nli-deberta-v3-small (44M params on CPU)",
                    "• Input: [CLS] Retrieved Passage E_j [SEP] Atomic Claim C_i [SEP]",
                    "• Full all-to-all cross-attention across premise and hypothesis tokens",
                    "• Softmax Logits: P(contradiction), P(entailment), P(neutral)",
                    "• Calibrated Thresholds: τ_entail ≥ 0.55, τ_contra ≥ 0.50"],
                   "#FEF3C7", "#D97706", "#78350F", badge_bg="#D97706")

    draw_icon_card(450, 625, 410, 165, "⚖️", "STAGE 4", "Multi-Evidence Arbitration Policy",
                   ["Deterministic 4-Way Decision Rules per Claim:",
                    "• SUPPORTED: max P(entailment) ≥ 0.55 without contradiction",
                    "• CONTRADICTED: max P(contradiction) ≥ 0.50 without entailment",
                    "• CONFLICTING: Distinct passages show both P_e ≥ 0.55 AND P_c ≥ 0.50",
                    "• INSUFFICIENT EVIDENCE: Below thresholds, 0 retrieved, or subjective",
                    "• Confidence Calibration: Set to null for missing/unverifiable evidence"],
                   "#FEE2E2", "#DC2626", "#7F1D1D", badge_bg="#DC2626")

    # Zone 3 Cards (Risk Scoring & Closed Loop Reverification)
    draw_icon_card(920, 140, 400, 155, "🧮", "STAGE 5", "Hallucination Risk Scorer",
                   ["Deterministic empirical formulation bounded in [0.0, 1.0]:",
                    "• Contradiction Rate: R_contra = N_contra / max(1, N_verifiable)",
                    "• Unsupported Rate: R_unsupp = (N_contra + N_insuff + N_conf) / N_total",
                    "• Composite Risk: S_risk = min(1.0, 0.70·R_contra + 0.30·R_unsupp)",
                    "• Explainability Engine: Provenance cards with doc name, page #,",
                    "  chunk ID, verbatim quote snippet, and similarity score"],
                   "#FDF2F8", "#DB2777", "#831843", badge_bg="#DB2777")

    draw_icon_card(1035, 325, 170, 85, "⚠️", "", "Contradictions?",
                   ["Detected?", "(N_contra > 0)"],
                   "#FEF3C7", "#D97706", "#92400E", is_diamond=True)

    draw_icon_card(920, 445, 400, 120, "✍️", "STAGE 6", "Evidence-Grounded Correction",
                   ["• Replaces contradicted spans with ground truth facts",
                    "• Context-Constrained Prompting with retrieved reference passages",
                    "• Local LLM: Ollama qwen3:8b on GPU (~2.4 GB VRAM)",
                    "• Preserves supported sentences; rewrites only refuted clauses"],
                   "#EDE9FE", "#7C3AED", "#4C1D95", badge_bg="#7C3AED")

    draw_icon_card(920, 600, 400, 125, "🔄", "CLOSED-LOOP", "Reverification Audit Engine",
                   ["• Corrected text is automatically looped back to Stages 1 - 4",
                    "• Decomposes revised answer and re-queries FAISS + NLI",
                    "• Verification Invariant: Guarantees 0 remaining contradictions",
                    "• Emits reverification badge &amp; side-by-side diff comparison"],
                   "#EDE9FE", "#7C3AED", "#4C1D95", badge_bg="#7C3AED")

    # Audit Pass
    svg_lines.append('  <rect x="920" y="765" width="400" height="55" rx="8" fill="#DCFCE7" stroke="#16A34A" stroke-width="2" filter="url(#shadow)"/>')
    svg_lines.append('  <circle cx="945" cy="792" r="14" fill="#16A34A"/>')
    svg_lines.append('  <text x="945" y="797" fill="#FFFFFF" font-size="14" text-anchor="middle">✅</text>')
    svg_lines.append('  <text x="968" y="787" fill="#14532D" font-size="12" font-weight="bold">Audit Complete: Verified Factual Output</text>')
    svg_lines.append('  <text x="968" y="805" fill="#15803D" font-size="10.5">0 Contradictions • Evidence Provenance Bound • Streamed to API &amp; UI</text>')

    # Zone 4 Cards (Hardware Partitioning)
    draw_icon_card(1380, 140, 360, 170, "⚡", "NVIDIA GPU", "RTX 3050 Laptop (4 GB)",
                   ["Dedicated to Generative LLM:",
                    "• Ollama Runtime running qwen3:8b (or qwen2.5:3b)",
                    "• VRAM Allocation: ~2.4 GB VRAM (≤ 60% capacity)",
                    "• Roles: Mode B Generation &amp; Stage 6 Grounded Correction",
                    "• Zero competition with embedding or NLI models",
                    "• Prevents CUDA Out-Of-Memory (OOM) fatal crashes"],
                   "#ECFDF5", "#059669", "#064E3B", badge_bg="#059669")

    draw_icon_card(1380, 335, 360, 170, "💻", "HOST CPU", "CPU &amp; Multi-Threaded RAM",
                   ["Dedicated to Verification Pipeline:",
                    "• Sentence-Transformers: all-MiniLM-L6-v2 (384-dim)",
                    "• Cross-Encoder NLI: nli-deberta-v3-small (44M params)",
                    "• FAISS Index: IndexFlatIP vector search",
                    "• Working Set Memory: ~3.2 GB Host System RAM",
                    "• PyTorch CPU threads enable fast parallel inference"],
                   "#EFF6FF", "#2563EB", "#1E3A8A", badge_bg="#2563EB")

    draw_icon_card(1380, 530, 360, 220, "🏆", "BENCHMARKS", "Local Empirical Metrics",
                   ["Measured Results on Local System:",
                    "• FEVER Accuracy: 90.0% (Macro F1: 89.9%)",
                    "• FEVER Recall@3: 100.0% (Zero-leakage Wikipedia)",
                    "• Claim Extraction Latency: 42 ms",
                    "• FAISS Vector Search Latency: 18 ms",
                    "• Cross-Encoder NLI Latency: 212 ms",
                    "• Arbitration &amp; Scoring Latency: 24 ms",
                    "• Warm Verification Total: 296 ms (< 0.6 s)",
                    "• Operational API Cost: $0.00 (100% Local / Offline)"],
                   "#FEF2F2", "#EF4444", "#7F1D1D", badge_bg="#EF4444")

    # Zone 5 Cards (Serving & UI)
    draw_icon_card(60, 940, 410, 155, "⚡", "FASTAPI ASYNC", "FastAPI Backend Engine",
                   ["• Endpoints: /verify, /verify-stream, /upload, /documents, /health",
                    "• Asynchronous request pipeline with CORS middleware &amp; Pydantic validation",
                    "• Multi-document ingestion endpoint with automated sliding-window chunking",
                    "• Deterministic reason codes (NO_DOCUMENTS_INDEXED, NO_EVIDENCE_RETRIEVED)"],
                   "#E0F2FE", "#0284C7", "#0369A1", badge_bg="#0284C7")

    draw_icon_card(490, 940, 360, 155, "💾", "SQLITE RELATIONAL", "Relational Persistence",
                   ["• File: data/truthguard.db",
                    "• Tables: verification_runs, claims, evidence, documents",
                    "• Persists complete audit trail, claim offsets, verdicts &amp; risk scores",
                    "• Ingested document registry with SHA-256 deduplication hashing"],
                   "#EEF2FF", "#4F46E5", "#312E81", badge_bg="#4F46E5")

    draw_icon_card(870, 940, 870, 155, "🖥️", "REACT 18 + TAILWIND", "Interactive UI Dashboard",
                   ["• Interactive Answer Inspector: Real-time color-coded inline span highlights (Green = Supported, Red = Contradicted, Yellow = Conflicting, Gray = Insufficient)",
                    "• Hallucination Risk Gauge: Animated circular risk meter showing composite score S_risk, Contradiction Rate, and Unsupported Claim Rate",
                    "• Evidence Provenance Cards: Displays document title, page number, chunk ID, verbatim excerpt snippet, and cosine similarity badge",
                    "• Diff Reverification View: Side-by-side inspection showing original refuted claims vs. evidence-grounded corrected text"],
                   "#F0FDFA", "#0D9488", "#0F766E", badge_bg="#0D9488")

    # Legend Bar
    svg_lines.append('  <rect x="40" y="1130" width="1720" height="50" rx="6" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.5"/>')
    svg_lines.append('  <text x="900" y="1160" fill="#334155" font-size="11.5" text-anchor="middle">'
                     '<tspan font-weight="bold">LEGEND &amp; ICONS:   </tspan>'
                     '<tspan fill="#134E4A">💬 Input Modes   </tspan>'
                     '<tspan fill="#0369A1">📄 Document &amp; FEVER Corpus   </tspan>'
                     '<tspan fill="#3730A3">📐 Embeddings &amp; 🗄️ FAISS Retrieval   </tspan>'
                     '<tspan fill="#92400E">🧠 Cross-Encoder NLI   </tspan>'
                     '<tspan fill="#991B1B">⚖️ Arbitration &amp; 🧮 Risk Scoring   </tspan>'
                     '<tspan fill="#5B21B6">✍️ Grounded Correction &amp; 🔄 Closed Loop   </tspan>'
                     '<tspan fill="#047857">⚡ Hardware Budgeting</tspan></text>')

    # Connectors
    def draw_path(d, stroke, marker, dashed=False, stroke_w=2):
        dash_attr = 'stroke-dasharray="6,4"' if dashed else ''
        svg_lines.append(f'  <path d="{d}" fill="none" stroke="{stroke}" stroke-width="{stroke_w}" {dash_attr} marker-end="url(#{marker})"/>')

    # Mode A / B -> Stage 1
    draw_path("M 390 172 L 450 172", "#2563EB", "arrow-blue")
    draw_path("M 390 255 L 420 255 L 420 210 L 450 210", "#2563EB", "arrow-blue")

    # Ingestion flow
    draw_path("M 225 380 L 225 490", "#0D9488", "arrow-teal")
    draw_path("M 225 470 L 225 490", "#0D9488", "arrow-teal")
    draw_path("M 225 560 L 225 580", "#7C3AED", "arrow-purple")
    draw_path("M 225 650 L 225 670", "#7C3AED", "arrow-purple")

    # FAISS -> Stage 2
    draw_path("M 390 715 L 420 715 L 420 360 L 450 360", "#7C3AED", "arrow-purple")

    # Stage 1 -> 2 -> 3 -> 4
    draw_path("M 655 260 L 655 295", "#2563EB", "arrow-blue")
    draw_path("M 655 420 L 655 455", "#2563EB", "arrow-blue")
    draw_path("M 655 590 L 655 625", "#DC2626", "arrow-red")

    # Stage 4 -> Stage 5
    draw_path("M 860 710 L 890 710 L 890 215 L 920 215", "#DC2626", "arrow-red")

    # Stage 5 -> Decision
    draw_path("M 1120 295 L 1120 325", "#7C3AED", "arrow-purple")

    # Decision -> Stage 6 (Yes)
    draw_path("M 1120 410 L 1120 445", "#DC2626", "arrow-red")

    # Decision -> Pass (No)
    draw_path("M 1205 367 L 1260 367 L 1260 790 L 1320 790", "#16A34A", "arrow-green")

    # Stage 6 -> Reverification
    draw_path("M 1120 565 L 1120 600", "#7C3AED", "arrow-purple")

    # Closed-Loop Reverification Loopback (Stage 6 Reverif -> Stage 1)
    draw_path("M 920 665 L 880 665 L 880 180 L 860 180", "#9333EA", "arrow-purple", dashed=True, stroke_w=2.8)
    # Loopback Chip Callout on Path
    svg_lines.append('  <rect x="800" y="270" width="160" height="24" rx="4" fill="#7C3AED" stroke="#5B21B6" stroke-width="1"/>')
    svg_lines.append('  <text x="880" y="286" fill="#FFFFFF" font-size="9" font-weight="bold" text-anchor="middle">🔄 CLOSED-LOOP RE-AUDIT</text>')

    # Reverification -> Audit Pass
    draw_path("M 1120 725 L 1120 765", "#16A34A", "arrow-green")

    # Audit Pass -> FastAPI Backend
    draw_path("M 920 790 L 265 790 L 265 940", "#0D9488", "arrow-teal")

    # API -> DB & API -> UI
    draw_path("M 470 1017 L 490 1017", "#2563EB", "arrow-blue")
    draw_path("M 850 1017 L 870 1017", "#0D9488", "arrow-teal")

    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)

def generate_high_res_png(output_path):
    """Uses matplotlib to render a publication-grade 300 DPI PNG diagram with icons and unique badges."""
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Segoe UI Emoji', 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, ax = plt.subplots(figsize=(24, 16), dpi=300)
    ax.set_xlim(0, 1800)
    ax.set_ylim(0, 1220)
    ax.invert_yaxis()
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')

    # Draw Title Banner
    ax.add_patch(patches.FancyBboxPatch((40, 20), 1720, 65, boxstyle="round,pad=0,rounding_size=8",
                                        facecolor='#0F172A', edgecolor='#1E40AF', linewidth=2.5))
    ax.text(80, 52, "🛡️", fontname='Segoe UI Emoji', fontsize=20, ha='center', va='center')
    ax.text(900, 44, "TRUTHGUARD: END-TO-END SYSTEM ARCHITECTURE PIPELINE",
            color='white', fontsize=18, fontweight='bold', ha='center', va='center')
    ax.text(900, 68, "Modular Multi-Stage Verification • Dual-Corpus FAISS Retrieval • DeBERTa-v3 Cross-Encoder NLI • Closed-Loop Reverification",
            color='#93C5FD', fontsize=10.5, ha='center', va='center')
    ax.add_patch(patches.FancyBboxPatch((1560, 34), 170, 36, boxstyle="round,pad=0,rounding_size=6",
                                        facecolor='#1D4ED8', edgecolor='#3B82F6', linewidth=1))
    ax.text(1645, 52, "v2.4 LOCAL • 296ms", color='white', fontsize=9.5, fontweight='bold', ha='center', va='center')

    # Containers
    def draw_container(x, y, w, h, icon_sym, title, face, edge, title_col):
        ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=8",
                                            facecolor=face, edgecolor=edge, linewidth=2))
        ax.plot([x, x+w], [y+32, y+32], color=edge, linewidth=1.5)
        ax.text(x + 20, y + 18, f"{icon_sym}  {title}", fontname='Segoe UI Emoji', color=title_col, fontsize=12, fontweight='bold', ha='left', va='center')

    draw_container(40, 95, 370, 780, "📂", "INPUT ACQUISITION & KNOWLEDGE BASE INGESTION", '#F0FDFA', '#0D9488', '#0F766E')
    draw_container(430, 95, 450, 780, "🔬", "CORE NLP VERIFICATION PIPELINE (STAGES 1 - 4)", '#F8FAFC', '#2563EB', '#1D4ED8')
    draw_container(900, 95, 440, 780, "📊", "RISK SCORING & CLOSED-LOOP REVERIFICATION", '#FAF5FF', '#7C3AED', '#6B21A8')
    draw_container(1360, 95, 400, 780, "⚡", "HARDWARE PARTITIONING (4GB VRAM BUDGET)", '#F1F5F9', '#475569', '#1E293B')
    draw_container(40, 895, 1720, 220, "🚀", "API SERVING, DATABASE PERSISTENCE & USER EXPERIENCE LAYER", '#F8FAFC', '#0284C7', '#0369A1')

    # Card with Icon Helper
    def draw_card(x, y, w, h, icon_char, badge_text, title, lines, face, edge, col, badge_bg='#2563EB', is_diamond=False):
        if is_diamond:
            pts = [(x + w/2, y), (x + w, y + h/2), (x + w/2, y + h), (x, y + h/2)]
            poly = patches.Polygon(pts, facecolor=face, edgecolor=edge, linewidth=2)
            ax.add_patch(poly)
            ax.text(x + w/2, y + h/2 - 6, f"{icon_char} {title}", fontname='Segoe UI Emoji', color=col, fontsize=10, fontweight='bold', ha='center', va='center')
            for i, line in enumerate(lines):
                ax.text(x + w/2, y + h/2 + 10 + i*12, line, color=col, fontsize=8.5, ha='center', va='center')
            return

        ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6",
                                            facecolor=face, edgecolor=edge, linewidth=1.5))
        # Icon Circle
        circle = patches.Circle((x + 24, y + 24), radius=14, facecolor=badge_bg, edgecolor=edge, linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x + 24, y + 25, icon_char, fontname='Segoe UI Emoji', color='white', fontsize=11, ha='center', va='center')

        # Badge pill
        if badge_text:
            b_w = len(badge_text) * 6.5 + 10
            ax.add_patch(patches.FancyBboxPatch((x + 46, y + 12), b_w, 16, boxstyle="round,pad=0,rounding_size=4",
                                                facecolor=badge_bg, edgecolor='none'))
            ax.text(x + 46 + b_w/2, y + 20, badge_text, color='white', fontsize=7.5, fontweight='bold', ha='center', va='center')
            title_x = x + 52 + b_w
        else:
            title_x = x + 46

        # Title
        ax.text(title_x, y + 21, title, color=col, fontsize=9.5, fontweight='bold', ha='left', va='center')
        
        # Content
        for i, line in enumerate(lines):
            ax.text(x + 14, y + 42 + i*14, line, color=col, fontsize=8.5, ha='left', va='center')

    # Zone 1
    draw_card(60, 140, 330, 65, "💬", "MODE A", "Direct Verification",
              ["User Question + External Candidate Answer", "(Audits arbitrary external LLM or human text)"],
              '#CCFBF1', '#14B8A6', '#134E4A', badge_bg='#0D9488')
    draw_card(60, 220, 330, 70, "🤖", "MODE B • GPU", "Autonomous Generation",
              ["User Question → Local LLM: Ollama qwen3:8b", "Runs on GPU (~2.4 GB VRAM) → Synthesizes response"],
              '#CCFBF1', '#14B8A6', '#134E4A', badge_bg='#0D9488')
    draw_card(60, 310, 330, 70, "📄", "PDF / TXT / MD", "Private Document Library",
              ["User Ingestion via PyMuPDF (fitz)", "Text Normalization & SHA-256 Deduplication"],
              '#E0F2FE', '#0284C7', '#0369A1', badge_bg='#0284C7')
    draw_card(60, 400, 330, 70, "🌐", "BENCHMARK", "FEVER Benchmark Corpus",
              ["570 Pre-Processed Articles • 1,000 Pairs", "Zero-Leakage Protocol: Gold labels withheld"],
              '#E0F2FE', '#0284C7', '#0369A1', badge_bg='#0284C7')
    draw_card(60, 490, 330, 70, "✂️", "SEGMENTATION", "Sliding-Window Chunking",
              ["Passage size C = 500 chars, overlap O = 100", "Preserves character provenance, page # & chunk IDs"],
              '#EDE9FE', '#7C3AED', '#5B21B6', badge_bg='#7C3AED')
    draw_card(60, 580, 330, 70, "📐", "R^384 DENSE", "MiniLM-L6 Embedding",
              ["sentence-transformers/all-MiniLM-L6-v2", "Maps passages to L2-normalized vectors on CPU"],
              '#EEF2FF', '#4F46E5', '#3730A3', badge_bg='#4F46E5')
    draw_card(60, 670, 330, 90, "🗄️", "FAISS IndexFlatIP", "Vector Store",
              ["Exact Cosine Similarity via Inner Product", "sim(q, v) = q_hat · v_hat = cos(θ)", "Sub-20ms queries across corpus"],
              '#EEF2FF', '#4F46E5', '#312E81', badge_bg='#4F46E5')
    draw_card(60, 780, 330, 65, "🛑", "GUARDRAIL", "Missing Corpus Fallback",
              ["No docs uploaded? → NO_DOCUMENTS_INDEXED", "Confidence = null (Honest uncalibrated verdict)"],
              '#FEE2E2', '#EF4444', '#991B1B', badge_bg='#DC2626')

    # Zone 2
    draw_card(450, 140, 410, 120, "🧩", "STAGE 1", "Syntactic Claim Decomposition",
              ["• Sentence boundary detection & regex coordinating conjunction split",
               "• Character Span Tracking: Exact start_offset & end_offset in text",
               "• Empirical Classifier: Tags subjective / non-verifiable claims",
               "• Output: Stream of Atomic Hypotheses {C_1, C_2, ..., C_N}"],
              '#DBEAFE', '#2563EB', '#1E3A8A', badge_bg='#2563EB')
    draw_card(450, 295, 410, 125, "🔍", "STAGE 2", "Multi-Source Semantic Retrieval",
              ["• Encodes atomic claim C_i into query vector q_hat via MiniLM-L6 (CPU)",
               "• FAISS IndexFlatIP inner-product search computes exact cosine similarity",
               "• Retrieves top-k candidate passages (k = 3, threshold τ_sim ≥ 0.25)",
               "• 0 matches? Emits NO_EVIDENCE_RETRIEVED (Confidence = null)"],
              '#EEF2FF', '#6366F1', '#312E81', badge_bg='#6366F1')
    draw_card(450, 455, 410, 135, "🧠", "STAGE 3", "Deep Cross-Encoder NLI Inference",
              ["• Model: cross-encoder/nli-deberta-v3-small (44M params on CPU)",
               "• Input: [CLS] Retrieved Passage E_j [SEP] Atomic Claim C_i [SEP]",
               "• Full all-to-all cross-attention across premise and hypothesis tokens",
               "• Softmax Logits: P(contradiction), P(entailment), P(neutral)",
               "• Calibrated Thresholds: τ_entail ≥ 0.55, τ_contra ≥ 0.50"],
              '#FEF3C7', '#D97706', '#78350F', badge_bg='#D97706')
    draw_card(450, 625, 410, 165, "⚖️", "STAGE 4", "Multi-Evidence Arbitration Policy",
              ["Deterministic 4-Way Decision Rules per Claim:",
               "• SUPPORTED: max P(entailment) ≥ 0.55 without contradiction",
               "• CONTRADICTED: max P(contradiction) ≥ 0.50 without entailment",
               "• CONFLICTING: Distinct passages show both P_e ≥ 0.55 AND P_c ≥ 0.50",
               "• INSUFFICIENT EVIDENCE: Below thresholds, 0 retrieved, or subjective",
               "• Confidence Calibration: Set to null for missing/unverifiable evidence"],
              '#FEE2E2', '#DC2626', '#7F1D1D', badge_bg='#DC2626')

    # Zone 3
    draw_card(920, 140, 400, 155, "🧮", "STAGE 5", "Hallucination Risk Scorer",
              ["Deterministic empirical formulation bounded in [0.0, 1.0]:",
               "• Contradiction Rate: R_contra = N_contra / max(1, N_verifiable)",
               "• Unsupported Rate: R_unsupp = (N_contra + N_insuff + N_conf) / N_total",
               "• Composite Risk: S_risk = min(1.0, 0.70·R_contra + 0.30·R_unsupp)",
               "• Explainability Engine: Provenance cards with doc name, page #,",
               "  chunk ID, verbatim quote snippet, and similarity score"],
              '#FDF2F8', '#DB2777', '#831843', badge_bg='#DB2777')
    draw_card(1035, 325, 170, 85, "⚠️", "", "Contradictions?",
              ["Detected?", "(N_contra > 0)"],
              '#FEF3C7', '#D97706', '#92400E', is_diamond=True)
    draw_card(920, 445, 400, 120, "✍️", "STAGE 6", "Evidence-Grounded Correction",
              ["• Replaces contradicted spans with ground truth facts",
               "• Context-Constrained Prompting with retrieved reference passages",
               "• Local LLM: Ollama qwen3:8b on GPU (~2.4 GB VRAM)",
               "• Preserves supported sentences; rewrites only refuted clauses"],
              '#EDE9FE', '#7C3AED', '#4C1D95', badge_bg='#7C3AED')
    draw_card(920, 600, 400, 125, "🔄", "CLOSED-LOOP", "Reverification Audit Engine",
              ["• Corrected text is automatically looped back to Stages 1 - 4",
               "• Decomposes revised answer and re-queries FAISS + NLI",
               "• Verification Invariant: Guarantees 0 remaining contradictions",
               "• Emits reverification badge & side-by-side diff comparison"],
              '#EDE9FE', '#7C3AED', '#4C1D95', badge_bg='#7C3AED')

    # Audit Pass
    ax.add_patch(patches.FancyBboxPatch((920, 765), 400, 55, boxstyle="round,pad=0,rounding_size=6",
                                        facecolor='#DCFCE7', edgecolor='#16A34A', linewidth=2))
    circle_pass = patches.Circle((945, 792), radius=14, facecolor='#16A34A', edgecolor='#14532D', linewidth=1.5)
    ax.add_patch(circle_pass)
    # Draw sharp vector checkmark
    ax.plot([938, 943, 952], [792, 797, 786], color='white', linewidth=2.5, solid_capstyle='round')
    ax.text(968, 784, "Audit Complete: Verified Factual Output", color='#14532D', fontsize=10, fontweight='bold', ha='left', va='center')
    ax.text(968, 802, "0 Contradictions • Evidence Provenance Bound • Streamed to API & UI", color='#15803D', fontsize=8.5, ha='left', va='center')

    # Zone 4
    draw_card(1380, 140, 360, 170, "⚡", "NVIDIA GPU", "RTX 3050 Laptop (4 GB)",
              ["Dedicated to Generative LLM:",
               "• Ollama Runtime running qwen3:8b (or qwen2.5:3b)",
               "• VRAM Allocation: ~2.4 GB VRAM (≤ 60% capacity)",
               "• Roles: Mode B Generation & Stage 6 Grounded Correction",
               "• Zero competition with embedding or NLI models",
               "• Prevents CUDA Out-Of-Memory (OOM) fatal crashes"],
              '#ECFDF5', '#059669', '#064E3B', badge_bg='#059669')
    draw_card(1380, 335, 360, 170, "💻", "HOST CPU", "CPU & Multi-Threaded RAM",
              ["Dedicated to Verification Pipeline:",
               "• Sentence-Transformers: all-MiniLM-L6-v2 (384-dim)",
               "• Cross-Encoder NLI: nli-deberta-v3-small (44M params)",
               "• FAISS Index: IndexFlatIP vector search",
               "• Working Set Memory: ~3.2 GB Host System RAM",
               "• PyTorch CPU threads enable fast parallel inference"],
              '#EFF6FF', '#2563EB', '#1E3A8A', badge_bg='#2563EB')
    draw_card(1380, 530, 360, 220, "🏆", "BENCHMARKS", "Local Empirical Metrics",
              ["Measured Results on Local System:",
               "• FEVER Accuracy: 90.0% (Macro F1: 89.9%)",
               "• FEVER Recall@3: 100.0% (Zero-leakage Wikipedia)",
               "• Claim Extraction Latency: 42 ms",
               "• FAISS Vector Search Latency: 18 ms",
               "• Cross-Encoder NLI Latency: 212 ms",
               "• Arbitration & Scoring Latency: 24 ms",
               "• Warm Verification Total: 296 ms (< 0.6 s)",
               "• Operational API Cost: $0.00 (100% Local / Offline)"],
              '#FEF2F2', '#EF4444', '#7F1D1D', badge_bg='#EF4444')

    # Zone 5
    draw_card(60, 940, 410, 155, "⚡", "FASTAPI ASYNC", "FastAPI Backend Engine",
              ["• Endpoints: /verify, /verify-stream, /upload, /documents, /health",
               "• Asynchronous request pipeline with CORS middleware & Pydantic validation",
               "• Multi-document ingestion endpoint with automated sliding-window chunking",
               "• Deterministic reason codes (NO_DOCUMENTS_INDEXED, NO_EVIDENCE_RETRIEVED)"],
              '#E0F2FE', '#0284C7', '#0369A1', badge_bg='#0284C7')
    draw_card(490, 940, 360, 155, "💾", "SQLITE RELATIONAL", "Relational Persistence",
              ["• File: data/truthguard.db",
               "• Tables: verification_runs, claims, evidence, documents",
               "• Persists complete audit trail, claim offsets, verdicts & risk scores",
               "• Ingested document registry with SHA-256 deduplication hashing"],
              '#EEF2FF', '#4F46E5', '#312E81', badge_bg='#4F46E5')
    draw_card(870, 940, 870, 155, "🖥️", "REACT 18 + TAILWIND", "Interactive UI Dashboard",
              ["• Interactive Answer Inspector: Real-time color-coded inline span highlights (Green = Supported, Red = Contradicted, Yellow = Conflicting, Gray = Insufficient)",
               "• Hallucination Risk Gauge: Animated circular risk meter showing composite score S_risk, Contradiction Rate, and Unsupported Claim Rate",
               "• Evidence Provenance Cards: Displays document title, page number, chunk ID, verbatim excerpt snippet, and cosine similarity badge",
               "• Diff Reverification View: Side-by-side inspection showing original refuted claims vs. evidence-grounded corrected text"],
              '#F0FDFA', '#0D9488', '#0F766E', badge_bg='#0D9488')

    # Legend
    ax.add_patch(patches.FancyBboxPatch((40, 1130), 1720, 50, boxstyle="round,pad=0,rounding_size=6",
                                        facecolor='#F8FAFC', edgecolor='#94A3B8', linewidth=1.5))
    ax.text(900, 1155, "LEGEND & ICONS:   💬 Input Modes   📄 Document & FEVER Corpus   📐 Embeddings & 🗄️ FAISS Retrieval   🧠 Cross-Encoder NLI   ⚖️ Arbitration & 🧮 Risk Scoring   ✍️ Grounded Correction & 🔄 Closed Loop   ⚡ Hardware Budgeting",
            fontname='Segoe UI Emoji', color='#334155', fontsize=9.5, fontweight='bold', ha='center', va='center')

    # Draw Arrows
    def draw_arrow(x1, y1, x2, y2, col, dashed=False, lw=1.5):
        ls = '--' if dashed else '-'
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=col, lw=lw, linestyle=ls))

    # Mode A / B -> Stage 1
    draw_arrow(390, 172, 450, 172, '#2563EB')
    draw_arrow(390, 255, 450, 210, '#2563EB')

    # Ingestion flow
    draw_arrow(225, 380, 225, 490, '#0D9488')
    draw_arrow(225, 470, 225, 490, '#0D9488')
    draw_arrow(225, 560, 225, 580, '#7C3AED')
    draw_arrow(225, 650, 225, 670, '#7C3AED')

    # FAISS -> Stage 2
    draw_arrow(390, 715, 450, 360, '#7C3AED')

    # Stage 1 -> 2 -> 3 -> 4
    draw_arrow(655, 260, 655, 295, '#2563EB')
    draw_arrow(655, 420, 655, 455, '#2563EB')
    draw_arrow(655, 590, 655, 625, '#DC2626')

    # Stage 4 -> Stage 5
    draw_arrow(860, 710, 920, 215, '#DC2626')

    # Stage 5 -> Decision
    draw_arrow(1120, 295, 1120, 325, '#7C3AED')

    # Decision -> Stage 6 (Yes)
    draw_arrow(1120, 410, 1120, 445, '#DC2626')

    # Decision -> Pass (No)
    draw_arrow(1205, 367, 1260, 790, '#16A34A')

    # Stage 6 -> Reverification
    draw_arrow(1120, 565, 1120, 600, '#7C3AED')

    # Reverification -> Stage 1 (Loopback)
    draw_arrow(920, 665, 860, 180, '#9333EA', dashed=True, lw=2.2)
    # Loopback Chip Callout on Path
    ax.add_patch(patches.FancyBboxPatch((800, 270), 160, 24, boxstyle="round,pad=0,rounding_size=4",
                                        facecolor='#7C3AED', edgecolor='#5B21B6', linewidth=1))
    ax.text(880, 282, "🔄 CLOSED-LOOP RE-AUDIT", fontname='Segoe UI Emoji', color='white', fontsize=7.5, fontweight='bold', ha='center', va='center')

    # Reverification -> Audit Pass
    draw_arrow(1120, 725, 1120, 765, '#16A34A')

    # Audit Pass -> FastAPI Backend
    draw_arrow(920, 790, 265, 940, '#0D9488')

    # API -> DB & API -> UI
    draw_arrow(470, 1017, 490, 1017, '#2563EB')
    draw_arrow(850, 1017, 870, 1017, '#0D9488')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Successfully generated high-res PNG at: {output_path}")

def main():
    out_dir = r"docs\figures"
    os.makedirs(out_dir, exist_ok=True)

    drawio_path = os.path.join(out_dir, "truthguard_architecture_pipeline.drawio")
    svg_path = os.path.join(out_dir, "truthguard_architecture_pipeline.svg")
    png_path = os.path.join(out_dir, "truthguard_architecture_pipeline.png")

    print("1. Generating Draw.io native XML diagram with icons and badges...")
    xml_content = generate_drawio_xml()
    with open(drawio_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"-> Saved Draw.io diagram to: {drawio_path}")

    print("2. Generating enhanced SVG vector diagram...")
    svg_content = generate_svg()
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"-> Saved SVG diagram to: {svg_path}")

    print("3. Generating 300 DPI high-resolution PNG diagram...")
    generate_high_res_png(png_path)

    print("\nAll diagram assets successfully updated in docs/figures/!")

if __name__ == "__main__":
    main()
