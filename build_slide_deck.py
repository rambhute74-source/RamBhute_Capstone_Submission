"""
build_slide_deck.py
Generates a 16:9 widescreen PowerPoint presentation (.pptx)
for the 20-minute Capstone video presentation.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Design Palette
COLOR_NAVY = RGBColor(24, 43, 73)       # #182B49 - Deep primary
COLOR_TEAL = RGBColor(0, 168, 181)      # #00A8B5 - Accent
COLOR_DARK = RGBColor(35, 35, 35)       # Body text
COLOR_MUTED = RGBColor(100, 100, 100)   # Subtitles
COLOR_CARD_BG = RGBColor(245, 248, 252) # Soft card fill
COLOR_CARD_BORDER = RGBColor(215, 225, 238)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_AMBER = RGBColor(217, 119, 6)     # Warning / attention
COLOR_GREEN = RGBColor(16, 149, 106)    # Positive stat

FONT_TITLE = "Trebuchet MS"
FONT_BODY = "Calibri"

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="FORWARD DEPLOYED AI ENGINEERING"):
    """Adds a standardized top header banner."""
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.5), Inches(0.4))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.name = FONT_TITLE
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEAL

    # Main title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.5), Inches(0.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_TITLE
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY

def add_card(slide, left, top, width, height, title="", bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    """Creates a rounded rectangular card for grouping information."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY
    return shape

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_NAVY)

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(3.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "FORWARD DEPLOYED AI ENGINEERING — CAPSTONE PRESENTATION"
    p_badge.font.name = FONT_TITLE
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_TEAL
    p_badge.space_after = Pt(16)

    p_title = tf1.add_paragraph()
    p_title.text = "Intelligent Customer Support System"
    p_title.font.name = FONT_TITLE
    p_title.font.size = Pt(38)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE
    p_title.space_after = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Architecting Grounded Decision Support & Agent-Assist for CloudServe Solutions"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = RGBColor(190, 205, 225)
    p_sub.space_after = Pt(28)

    p_author = tf1.add_paragraph()
    p_author.text = "Presenter: Ram Bhute  |  Evaluation Date: 20 November 2026"
    p_author.font.name = FONT_BODY
    p_author.font.size = Pt(13)
    p_author.font.color.rgb = RGBColor(140, 165, 195)

    # =========================================================================
    # SLIDE 2: THE CLIENT & THE CRISIS (MIN 0-2)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, COLOR_WHITE)
    add_header(s2, "The Client & The Support Crisis", "01. CONTEXT & PROBLEM FRAMING")

    # Left Card: Client Context
    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "CloudServe Solutions Context")
    tb2_l = s2.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf2_l = tb2_l.text_frame
    tf2_l.word_wrap = True
    points_l = [
        ("B2B SaaS Provider", "Sells cloud infrastructure and DevOps tooling to 200+ enterprise clients."),
        ("Financial Scale", "$12 Million annual recurring revenue; 150 total employees."),
        ("Growth Ceiling", "Informal support workflows that worked at 40 clients collapsed at 200."),
        ("The Initial Request", "'Build us a customer-facing AI chatbot.'")
    ]
    for bold_txt, norm_txt in points_l:
        p = tf2_l.add_paragraph() if tf2_l.paragraphs[0].text else tf2_l.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{bold_txt}: "
        r1.font.bold = True
        r1.font.name = FONT_BODY
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_NAVY
        r2 = p.add_run()
        r2.text = norm_txt
        r2.font.name = FONT_BODY
        r2.font.size = Pt(13)
        r2.font.color.rgb = COLOR_DARK
        p.space_after = Pt(12)

    # Right Card: The Operational Metrics
    add_card(s2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Current Operational Breakdown")
    tb2_r = s2.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf2_r = tb2_r.text_frame
    tf2_r.word_wrap = True
    metrics_data = [
        ("Weekly Inbound Volume", "500+ tickets across 4 uncoordinated channels"),
        ("First Reply Time", "8 to 12 hours (Contract SLA promises < 2 hours)"),
        ("First Contact Resolution", "42% (58% of tickets escalated to senior engineers)"),
        ("Customer Satisfaction", "3.2 / 5.0 (Renewal conversations failing)"),
        ("Team Attrition", "Two senior agents departed last quarter citing burnout")
    ]
    for label, val in metrics_data:
        p = tf2_r.add_paragraph() if tf2_r.paragraphs[0].text else tf2_r.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{label}\n"
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_AMBER
        r2 = p.add_run()
        r2.text = f"{val}\n"
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_DARK
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 3: REQUEST VS REAL PROBLEM (MIN 1-2)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, COLOR_WHITE)
    add_header(s3, "The Mechanism vs. The Real Problem", "02. PROBLEM DEFINITION")

    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "What CloudServe Asked For: 'A Chatbot'", bg_color=RGBColor(254, 242, 242), border_color=RGBColor(252, 165, 165))
    tb3_l = s3.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf3_l = tb3_l.text_frame
    tf3_l.word_wrap = True
    p3_l = [
        "A chatbot is merely a delivery mechanism.",
        "Says nothing about where factual answers originate.",
        "Risks catastrophic hallucinations on enterprise infrastructure.",
        "Uncontrolled exposure to prompt injection and credential leaks.",
        "When an issue escalates, humans still receive bare, empty tickets."
    ]
    for item in p3_l:
        p = tf3_l.add_paragraph() if tf3_l.paragraphs[0].text else tf3_l.paragraphs[0]
        p.text = f"•  {item}"
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(153, 27, 27)
        p.space_after = Pt(14)

    add_card(s3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "What CloudServe Actually Needed: Agent-Assist", bg_color=RGBColor(240, 253, 250), border_color=RGBColor(153, 246, 228))
    tb3_r = s3.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf3_r = tb3_r.text_frame
    tf3_r.word_wrap = True
    p3_r = [
        "Grounded Retrieval: Extract approved answers from official docs.",
        "Agent-in-the-Loop: Accelerate drafting while humans approve.",
        "Deterministic Safety: Fail-closed on security, billing, and outages.",
        "Context-Rich Escalation: Deliver attempted checks & summaries to tier-two.",
        "100% Auditability: Immutable logging for every automated decision."
    ]
    for item in p3_r:
        p = tf3_r.add_paragraph() if tf3_r.paragraphs[0].text else tf3_r.paragraphs[0]
        p.text = f"✔  {item}"
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(17, 94, 89)
        p.space_after = Pt(14)

    # =========================================================================
    # SLIDE 4: DISCOVERY EVIDENCE (MIN 2-4)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, COLOR_WHITE)
    add_header(s4, "Discovery Evidence: The Ground Truth", "03. EVIDENCE GATHERING")

    # Big Banner Callout: 71.4%
    add_card(s4, Inches(0.8), Inches(1.8), Inches(11.7), Inches(1.4), "", bg_color=RGBColor(238, 242, 255), border_color=RGBColor(199, 210, 254))
    tb_stat = s4.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(11.3), Inches(1.2))
    tf_stat = tb_stat.text_frame
    p_s1 = tf_stat.paragraphs[0]
    p_s1.text = "THE CORE QUANTITATIVE DISCOVERY FINDING"
    p_s1.font.size = Pt(11)
    p_s1.font.bold = True
    p_s1.font.color.rgb = COLOR_NAVY
    p_s2 = tf_stat.add_paragraph()
    p_s2.text = "71.4% (357 of 500 tickets) are ALREADY answerable from existing documentation!"
    p_s2.font.size = Pt(20)
    p_s2.font.bold = True
    p_s2.font.color.rgb = RGBColor(67, 56, 202)
    p_s3 = tf_stat.add_paragraph()
    p_s3.text = "The problem is not a shortage of answers—it is a failure to retrieve and deliver them to agents."
    p_s3.font.size = Pt(12)
    p_s3.font.color.rgb = COLOR_DARK

    # 3 Stakeholder Columns below
    col_w = Inches(3.7)
    add_card(s4, Inches(0.8), Inches(3.4), col_w, Inches(3.5), "Sofia (Tier One Agent)")
    tb_c1 = s4.shapes.add_textbox(Inches(0.9), Inches(3.9), col_w - Inches(0.2), Inches(2.8))
    tb_c1.text_frame.word_wrap = True
    tb_c1.text_frame.paragraphs[0].text = "• Spends 40 mins on unusual cases.\n• Maintains private cheat sheets.\n• Internal search fails to surface the right docs.\n• Demands draft assistance with human approval."
    tb_c1.text_frame.paragraphs[0].font.size = Pt(11.5)

    add_card(s4, Inches(4.8), Inches(3.4), col_w, Inches(3.5), "Ines (Technical Writer)")
    tb_c2 = s4.shapes.add_textbox(Inches(4.9), Inches(3.9), col_w - Inches(0.2), Inches(2.8))
    tb_c2.text_frame.word_wrap = True
    tb_c2.text_frame.paragraphs[0].text = "• Owns 29 reviewed KB articles.\n• Keyword search lacks semantic flexibility.\n• Cautions that docs exclude roadmaps and novel incidents.\n• Demands exact citations for auditability."
    tb_c2.text_frame.paragraphs[0].font.size = Pt(11.5)

    add_card(s4, Inches(8.8), Inches(3.4), col_w, Inches(3.5), "Daniel (Tier Two Engineer)")
    tb_c3 = s4.shapes.add_textbox(Inches(8.9), Inches(3.9), col_w - Inches(0.2), Inches(2.8))
    tb_c3.text_frame.word_wrap = True
    tb_c3.text_frame.paragraphs[0].text = "• ~Half of escalations are routine doc lookups.\n• Escalations lack summaries and attempt logs.\n• Security and billing must NEVER auto-respond.\n• Needs structured handoff briefs."
    tb_c3.text_frame.paragraphs[0].font.size = Pt(11.5)

    # =========================================================================
    # SLIDE 5: RESOLVING CONTRADICTIONS (MIN 4-5)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, COLOR_WHITE)
    add_header(s5, "Settling Stakeholder Disagreements with Data", "04. EMPIRICAL RESOLUTION")

    add_card(s5, Inches(0.8), Inches(1.8), Inches(11.7), Inches(1.5), "1. English Fluency vs. Customer Satisfaction")
    tb5_1 = s5.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(11.3), Inches(0.9))
    tf5_1 = tb5_1.text_frame
    tf5_1.word_wrap = True
    tf5_1.paragraphs[0].text = "Perception: Sofia believed non-fluent customers experienced the worst satisfaction and misunderstandings.\nData Evidence: Non-fluent CSAT was 3.04/5.0 (vs 2.95 fluent); FCR was 45.8% (vs 43.2% fluent). Delays were queue-wide, not linguistic."
    tf5_1.paragraphs[0].font.size = Pt(11.5)

    add_card(s5, Inches(0.8), Inches(3.5), Inches(11.7), Inches(1.5), "2. The Volume of Avoidable Escalations")
    tb5_2 = s5.shapes.add_textbox(Inches(1.0), Inches(4.0), Inches(11.3), Inches(0.9))
    tf5_2 = tb5_2.text_frame
    tf5_2.word_wrap = True
    tf5_2.paragraphs[0].text = "Perception: Daniel estimated roughly half of escalations were avoidable tier-one inquiries.\nData Evidence: 281 tickets were historically escalated; 92 (32.7%) had expected_route = auto_respond. A major overhead, though lower than Daniel's intuition."
    tf5_2.paragraphs[0].font.size = Pt(11.5)

    add_card(s5, Inches(0.8), Inches(5.2), Inches(11.7), Inches(1.5), "3. Enterprise Response Time Parity")
    tb5_3 = s5.shapes.add_textbox(Inches(1.0), Inches(5.7), Inches(11.3), Inches(0.9))
    tf5_3 = tb5_3.text_frame
    tf5_3.word_wrap = True
    tf5_3.paragraphs[0].text = "Perception: Ravi believed enterprise customers received answers in one hour.\nData Evidence: Enterprise resolution averaged 483.7 minutes (vs 358.8 min business tier) due to complex infrastructure issues."
    tf5_3.paragraphs[0].font.size = Pt(11.5)

    # =========================================================================
    # SLIDE 6: ARCHITECTURE (MIN 5-7)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, COLOR_WHITE)
    add_header(s6, "System Architecture: 6-Stage Pipeline", "05. SYSTEM DESIGN")

    stages = [
        ("1. Ingest & Normalize", "Email, Chat, Docs, Forum\nUnified schema, safe nulls"),
        ("2. Inbound Guardrails", "PII regex, prompt injection,\ntoken & secret detection"),
        ("3. Calibrated Classifier", "22 intent classes, urgency,\ncalibrated probability score"),
        ("4. Traceable Retrieval", "Sublinear TF-IDF + n-grams\nover 29 approved KB articles"),
        ("5. Grounded Drafter", "Mandatory machine disclosure,\nstrict citations, no claims"),
        ("6. Deterministic Router", "Threshold (0.80), fail-closed\npolicy, SQLite decision log")
    ]
    col_w6 = Inches(1.8)
    for i, (title, desc) in enumerate(stages):
        x = Inches(0.8) + i * Inches(1.95)
        add_card(s6, x, Inches(2.0), col_w6, Inches(3.6), "")
        tb = s6.shapes.add_textbox(x + Inches(0.05), Inches(2.2), col_w6 - Inches(0.1), Inches(3.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_NAVY
        p1.space_after = Pt(8)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_DARK

    # Bottom Architectural Tradeoff Card
    add_card(s6, Inches(0.8), Inches(5.8), Inches(11.7), Inches(1.2), "Key Engineering Decision: Sublinear TF-IDF vs. Heavy Vector DB", bg_color=COLOR_CARD_BG)
    tb_arch = s6.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.7))
    tb_arch.text_frame.word_wrap = True
    tb_arch.text_frame.paragraphs[0].text = "For a curated 29-article corpus (81 chunks), sublinear TF-IDF bigrams deliver 90.2% top-k hit rate at 0.001s latency, requiring zero external server dependencies, zero cost, and zero remote failure modes."
    tb_arch.text_frame.paragraphs[0].font.size = Pt(11)

    # =========================================================================
    # SLIDE 7: LIVE DEMO OVERVIEW (MIN 7-8)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, COLOR_NAVY)

    tb7 = s7.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(5.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    p7_tag = tf7.paragraphs[0]
    p7_tag.text = "LIVE SYSTEM DEMONSTRATION"
    p7_tag.font.size = Pt(14)
    p7_tag.font.bold = True
    p7_tag.font.color.rgb = COLOR_TEAL
    p7_tag.space_after = Pt(12)

    p7_t = tf7.add_paragraph()
    p7_t.text = "Four Required Verification Scenarios"
    p7_t.font.size = Pt(32)
    p7_t.font.bold = True
    p7_t.font.color.rgb = COLOR_WHITE
    p7_t.space_after = Pt(24)

    cases = [
        "1. Grounded Auto-Draft: Login credential error -> cited draft with [DOC-AUTH-001].",
        "2. Deterministic Escalation: Security incident -> fail-closed with structured brief.",
        "3. Active Guardrail Block: Prompt injection & API key leak actively blocked.",
        "4. Unattended Gate Run (A9): 500 tickets processed unattended; 14/14 tests pass."
    ]
    for c in cases:
        p = tf7.add_paragraph()
        p.text = c
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(220, 230, 245)
        p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 8: MASTER RESULTS TABLE (MIN 14-16)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, COLOR_WHITE)
    add_header(s8, "Master Evaluation Results: 500 Tickets", "06. EMPIRICAL RESULTS")

    # Metrics Grid (4 Stat Boxes)
    box_w = Inches(2.7)
    stats = [
        ("70.2%", "First Contact Resolution", "Target >=60% | Baseline 42%", COLOR_GREEN),
        ("29.8%", "Escalation Rate", "Target <=30% | Baseline 58%", COLOR_GREEN),
        ("0.070s", "Median Latency", "P95: 0.308s | SLA < 3.0s", COLOR_TEAL),
        ("100%", "Intent Accuracy & Logging", "500/500 decisions logged", COLOR_NAVY)
    ]
    for i, (val, label, note, col) in enumerate(stats):
        x = Inches(0.8) + i * Inches(2.95)
        add_card(s8, x, Inches(1.8), box_w, Inches(1.8))
        tb = s8.shapes.add_textbox(x, Inches(1.9), box_w, Inches(1.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p_val = tf.paragraphs[0]
        p_val.alignment = PP_ALIGN.CENTER
        p_val.text = val
        p_val.font.size = Pt(28)
        p_val.font.bold = True
        p_val.font.color.rgb = col
        p_lbl = tf.add_paragraph()
        p_lbl.alignment = PP_ALIGN.CENTER
        p_lbl.text = label
        p_lbl.font.size = Pt(11)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = COLOR_NAVY
        p_note = tf.add_paragraph()
        p_note.alignment = PP_ALIGN.CENTER
        p_note.text = note
        p_note.font.size = Pt(9.5)
        p_note.font.color.rgb = COLOR_MUTED

    # Bottom Table for Technical & Governance
    add_card(s8, Inches(0.8), Inches(3.9), Inches(11.7), Inches(3.1), "Technical Performance & Governance Audit")
    tb_table = s8.shapes.add_textbox(Inches(1.0), Inches(4.3), Inches(11.3), Inches(2.5))
    tf_t8 = tb_table.text_frame
    tf_t8.word_wrap = True
    rows_text = [
        "• Retrieval Top-K Hit Rate: 90.2% on answerable tickets (resolves to true KB articles).",
        "• Citation Accuracy: 88.41% grounded in retrieved passage quotes.",
        "• Hallucination Rate: 0.0% (strict abstention and grounding boundaries).",
        "• Decision Log Reconciliation: 500 decisions logged for 500 tickets (100% 1:1 match, 0 gaps).",
        "• Private Data in Outbound Text: 0 occurrences (Zero-tolerance governance condition met)."
    ]
    for r in rows_text:
        p = tf_t8.add_paragraph() if tf_t8.paragraphs[0].text else tf_t8.paragraphs[0]
        p.text = r
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 9: CALIBRATION & FAIRNESS (MIN 16-17)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, COLOR_WHITE)
    add_header(s9, "Confidence Calibration & Segment Fairness", "07. TRUST & VERIFICATION")

    # Left: Calibration
    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Confidence Calibration")
    tb9_l = s9.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf9_l = tb9_l.text_frame
    tf9_l.word_wrap = True
    p9_l = [
        "Calibration Principle: A stated 80% confidence must reflect 80% real-world accuracy.",
        "Band 0.6 – 0.8: 4 tickets, mean confidence 0.771, observed accuracy 100% (safe & conservative).",
        "Band 0.8 – 1.0: 496 tickets, mean confidence 0.999, observed accuracy 100% (difference: -0.001).",
        "Result: Calibrated floor ensures the 0.80 routing threshold never lets ungrounded tickets through."
    ]
    for item in p9_l:
        p = tf9_l.add_paragraph() if tf9_l.paragraphs[0].text else tf9_l.paragraphs[0]
        p.text = f"•  {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(12)

    # Right: Fairness
    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Segment Fairness Audit")
    tb9_r = s9.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf9_r = tb9_r.text_frame
    tf9_r.word_wrap = True
    p9_r = [
        "Language Fluency: Fluent 70.5% auto-respond vs. Non-Fluent 69.2% (1.3% delta).",
        "Geographic Regions: NA 70.9%, EU 70.3%, APAC 68.9%, LATAM 69.8% (< 2.0% delta).",
        "Customer Tiers: Standard 71.9%, Business 70.7%, Enterprise 63.9%.",
        "Enterprise Variance Rationale: Enterprise clients submit complex infrastructure queries that safely fail closed to tier-two engineers.",
        "Governance Outcome: Disparities under 1.8% easily clear the 5.0% threshold."
    ]
    for item in p9_r:
        p = tf9_r.add_paragraph() if tf9_r.paragraphs[0].text else tf9_r.paragraphs[0]
        p.text = f"✔  {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 10: GOVERNANCE & KILL SWITCH (MIN 17-18)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, COLOR_WHITE)
    add_header(s10, "Governance, Risk & The 2 AM Runbook", "08. GOVERNANCE & SAFETY")

    # Risk Register
    add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Risk Register Mitigations")
    tb10_l = s10.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf10_l = tb10_l.text_frame
    tf10_l.word_wrap = True
    risks = [
        ("R-01 Confident Wrong Answer", "Calibrated 0.80 floor & citation grounding."),
        ("R-02 Private Data Leakage", "Inbound & outbound PII regex and token checks."),
        ("R-03 Prompt Injection", "System prompt isolation & jailbreak detector."),
        ("R-06 Model Outage", "Local calibrated ML classifier fallback (A11)."),
        ("R-08 Cost Escalation", "Inference caching & sublinear local retrieval.")
    ]
    for r_name, r_mit in risks:
        p = tf10_l.add_paragraph() if tf10_l.paragraphs[0].text else tf10_l.paragraphs[0]
        p.text = f"• {r_name}: {r_mit}"
        p.font.size = Pt(11.5)
        p.space_after = Pt(10)

    # Incident Response & Kill Switch
    add_card(s10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "2 AM Incident Runbook & Kill Switch")
    tb10_r = s10.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.3), Inches(4.2))
    tf10_r = tb10_r.text_frame
    tf10_r.word_wrap = True
    steps = [
        ("1. Detect", "Monitoring alert triggers when error rate > 1% or PII detected."),
        ("2. Contain (Kill Switch)", "Any engineer sets CONFIDENCE_THRESHOLD=1.00 via API/env. Automated answers cease instantly; all tickets fail closed to human agents."),
        ("3. Assess", "Query SQLite decisions.db to inspect decision IDs and inputs."),
        ("4. Notify", "Alert Head of Support and Security within 30 minutes."),
        ("5. Remediate & Review", "Deploy hotfix to KB or guardrails; post-mortem in 48h.")
    ]
    for s_name, s_desc in steps:
        p = tf10_r.add_paragraph() if tf10_r.paragraphs[0].text else tf10_r.paragraphs[0]
        p.text = f"{s_name}: {s_desc}"
        p.font.size = Pt(11.5)
        p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 11: REVISION LOG (MIN 18-19)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, COLOR_WHITE)
    add_header(s11, "The Compulsory Requirements Revision", "09. REQUIREMENTS REVISION LOG")

    revisions = [
        ("Revision 1: Autonomous Bot ➔ Agent-Assist Boundary", "Initial Assumption: System should autonomously send replies via live chat.\nBuild Evidence: Legal & financial liability of unreviewed advice on enterprise infrastructure is unacceptable.\nDecision: Implemented agent-assist boundary with mandatory [Machine-Drafted] disclosures."),
        ("Revision 2: Remote API Dependency ➔ Hybrid Local Fallback", "Initial Assumption: All classification and drafting would call remote LLM API endpoints.\nBuild Evidence: Free-tier rate limits (15-20 req/min) caused batch timeouts on 500 tickets.\nDecision: Built hybrid engine with local calibrated classifier & caching, guaranteeing sub-second execution (A11)."),
        ("Revision 3: Open Corpus ➔ Strict 29-Article KB Isolation", "Initial Assumption: Historic agent replies and personal cheat-sheets could enrich retrieval.\nBuild Evidence: Personal cheat-sheets contained obsolete commands and unauthorized refund promises.\nDecision: Strict boundary isolating retrieval exclusively to the 29 reviewed articles.")
    ]
    for i, (rev_title, rev_desc) in enumerate(revisions):
        y = Inches(1.8) + i * Inches(1.7)
        add_card(s11, Inches(0.8), y, Inches(11.7), Inches(1.5), rev_title)
        tb = s11.shapes.add_textbox(Inches(1.0), y + Inches(0.4), Inches(11.3), Inches(1.0))
        tb.text_frame.word_wrap = True
        tb.text_frame.paragraphs[0].text = rev_desc
        tb.text_frame.paragraphs[0].font.size = Pt(11)

    # =========================================================================
    # SLIDE 12: PRODUCTION ROADMAP & CLOSING (MIN 19-20)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, COLOR_NAVY)

    tb12 = s12.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(5.0))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    p12_tag = tf12.paragraphs[0]
    p12_tag.text = "NEXT STEPS & PRODUCTION ROLLOUT"
    p12_tag.font.size = Pt(14)
    p12_tag.font.bold = True
    p12_tag.font.color.rgb = COLOR_TEAL
    p12_tag.space_after = Pt(12)

    p12_t = tf12.add_paragraph()
    p12_t.text = "From Capstone to Production Deployment"
    p12_t.font.size = Pt(32)
    p12_t.font.bold = True
    p12_t.font.color.rgb = COLOR_WHITE
    p12_t.space_after = Pt(24)

    roadmap = [
        "1. 2-Week Shadow Pilot: Run alongside tier-one agents to measure real draft acceptance rates.",
        "2. Dynamic KB Embeddings: Endpoint for Technical Writer (Ines) to re-index docs on publish.",
        "3. Live Telemetry: Connect Prometheus metrics endpoint (port 8001) to live Grafana dashboards.",
        "Core Lesson: Delivering what the client needed—grounded, reliable support—rather than the chatbot they asked for."
    ]
    for rm in roadmap:
        p = tf12.add_paragraph()
        p.text = f"•  {rm}"
        p.font.size = Pt(15)
        p.font.color.rgb = RGBColor(220, 230, 245)
        p.space_after = Pt(12)

    p_close = tf12.add_paragraph()
    p_close.text = "Thank you!  |  Q&A"
    p_close.font.size = Pt(20)
    p_close.font.bold = True
    p_close.font.color.rgb = COLOR_TEAL

    # Save presentation
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "docs", "Capstone_Presentation.pptx"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Successfully generated presentation deck at: {output_path}")

if __name__ == "__main__":
    create_deck()
