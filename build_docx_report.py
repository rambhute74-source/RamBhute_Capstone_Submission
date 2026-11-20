"""
build_docx_report.py
Generates a formatted Microsoft Word (.docx) version of the Capstone Project Report.
Follows the exact 10-section structure required by the submission guidelines.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)

def create_table(doc, headers, rows, col_widths=None):
    """Creates a stylized table with header shading and borders."""
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F497D")  # Deep Blue
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=150, right=150)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)
            run.font.name = "Calibri"

    # Data Rows
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F2F5F8" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=150, right=150)
            p = row_cells[c_idx].paragraphs[0]
            for run in p.runs:
                run.font.size = Pt(9.5)
                run.font.name = "Calibri"

    # Set Column Widths if provided
    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = width

    doc.add_paragraph()  # Spacing after table
    return table

def add_callout(doc, text, title="CRITICAL CAVEAT"):
    """Adds a callout box."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "FFF8E7")  # Warm amber tint
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    p = cell.paragraphs[0]
    r_title = p.add_run(f"[{title}] ")
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(180, 80, 0)
    r_title.font.size = Pt(10)

    r_text = p.add_run(text)
    r_text.font.size = Pt(9.5)
    r_text.font.italic = True
    doc.add_paragraph()

def build_report():
    doc = docx.Document()

    # Document Geometry (1-inch margins)
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # Styles Setup
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(51, 51, 51)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Title & Metadata
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("Forward Deployed AI Engineering — Capstone Project Report")
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(31, 73, 125)
    title_p.paragraph_format.space_after = Pt(2)

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("An Intelligent Customer Support System for CloudServe Solutions")
    sub_run.font.size = Pt(14)
    sub_run.font.color.rgb = RGBColor(89, 89, 89)
    sub_p.paragraph_format.space_after = Pt(14)

    meta_table = [
        ["Client", "CloudServe Solutions Inc."],
        ["Author", "Ram Bhute (Forward Deployed AI Engineer)"],
        ["Artifact Version", "Version 2.0 (Post-Build & Revision)"],
        ["Evaluation Date", "20 November 2026"],
        ["Format", "Single Document conforming to Stage 6 Submission Order"]
    ]
    create_table(doc, ["Metadata Field", "Details"], meta_table, [Inches(2.5), Inches(4.0)])

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY
    # =========================================================================
    doc.add_heading("Section 1: Executive Summary", level=1)
    doc.add_paragraph(
        "CloudServe Solutions sells cloud infrastructure and DevOps tooling to over 200 corporate clients, generating approximately "
        "$12 million in annual recurring revenue. Over the past three quarters, CloudServe's customer support function has entered critical distress: "
        "inbound volume has surpassed 500 tickets per week across four uncoordinated channels, average time to first response has ballooned to between "
        "8 and 12 hours (severely breaching their 2-hour contractual Service Level Agreement), and First Contact Resolution (FCR) has degraded to 42%. "
        "Consequently, Customer Satisfaction (CSAT) has fallen to 3.2 out of 5.0, experienced support staff are burning out, and renewal conversations are being jeopardized."
    )
    doc.add_paragraph(
        "CloudServe originally approached us with a simple request: 'Build us a customer-facing AI chatbot.' "
        "Our first-principles discovery investigation revealed that this request misdiagnosed the fundamental problem. Rigorous analysis of 500 historical "
        "support tickets and stakeholder interviews revealed that 71.4% (357 of 500 tickets) are already explicitly answerable using CloudServe's existing "
        "29 approved knowledge base articles. The root cause of support failure was not an absence of operational knowledge, but an acute failure of knowledge retrieval, "
        "unstandardized private agent snippet files, missing context during escalations, and manual triage overhead. Deploying an autonomous, unconstrained chatbot "
        "directly to customers would have amplified hallucinations, leaked sensitive customer data, and exacerbated customer churn."
    )
    doc.add_paragraph(
        "Instead, we designed, implemented, and validated an Agent-Assist Intelligent Support System featuring multi-channel normalization across 4 channels, "
        "calibrated ticket triage across 22 intent classes, traceable passage retrieval over the 29 approved knowledge base articles, source-grounded drafting with "
        "mandatory disclosures and citations, deterministic safety gates that fail closed for high-risk categories, and immutable SQLite decision logging reconciling 1:1 "
        "with processed tickets."
    )
    doc.add_paragraph(
        "In a single, unattended evaluation across the complete 500-ticket development dataset, the system achieved a First Contact Resolution (FCR) of 70.2% "
        "(exceeding the >=60% target and 42% baseline), reduced the escalation rate to 29.8% (beating the <=30% target and 58% baseline), achieved a median processing "
        "latency of 0.070 seconds (P95: 0.308s), recorded 100.0% intent classification accuracy, 90.2% retrieval hit rate, 88.4% citation accuracy, and 0% hallucinations. "
        "100% of decisions were logged with zero gaps, and zero outbound private data leaks occurred."
    )
    add_callout(
        doc,
        "This system is an agent-assist decision support system, not an autonomous unmonitored chatbot. While routine, high-confidence documentation inquiries "
        "receive immediate grounded drafts, final approval to transmit responses to customers remains strictly in human hands. All security incidents, legal compliance "
        "queries, billing disputes, and low-confidence requests are systematically escalated to human engineers with structured handoff briefs.",
        title="THE SINGLE MOST IMPORTANT CAVEAT"
    )

    # =========================================================================
    # SECTION 2: THE PROBLEM
    # =========================================================================
    doc.add_heading("Section 2: The Problem", level=1)
    doc.add_paragraph(
        "CloudServe Solutions operates in the competitive B2B developer tooling and cloud hosting space. The company employs approximately 150 staff and supports 200+ "
        "business and enterprise customers. The support team comprises six full-time tier-one support agents managed by Marcus Adeyemi (Head of Support), backed by "
        "tier-two technical escalations engineers including Daniel Okonkwo."
    )
    doc.add_paragraph(
        "The operational breakdown is summarized in the table below, representing baseline metrics against contractual targets:"
    )
    prob_table = [
        ["Weekly Inbound Volume", "Over 500 tickets", "Uncapped (growing)", "Volume rising faster than headcount"],
        ["Average First Reply Time", "8 to 12 hours", "< 2 hours", "SLA breaches risking enterprise penalties"],
        ["First Contact Resolution", "42%", ">= 65%", "58% of tickets handled twice by senior engineers"],
        ["Customer Satisfaction", "3.2 / 5.0", ">= 4.2 / 5.0", "Renewal conversations failing due to support delays"],
        ["Support Team Attrition", "Rising", "Stable", "Two experienced agents left last quarter citing burnout"]
    ]
    create_table(doc, ["Measure", "Baseline Today", "Contractual Target", "Business Consequence"], prob_table, [Inches(1.8), Inches(1.3), Inches(1.4), Inches(2.2)])

    doc.add_paragraph(
        "Tickets arrive through four distinct channels: Email (42.4% volume, long and unstructured), Live Chat (31.0% volume, high urgency requiring sub-3-minute answers), "
        "Documentation Comments (15.6% volume, technical API queries), and the Community Forum (11.0% volume, public threads with mixed advice)."
    )
    doc.add_paragraph(
        "The Conceptual Gulf Between the Request and the Need: CloudServe asked for a chatbot. If an engineering team builds a chatbot, they deliver an unconstrained text generator. "
        "A chatbot does not verify facts, does not know when to abstain, does not preserve customer privacy, and leaves senior engineers to reconstruct broken context. "
        "Our job was to work backwards from business outcomes: reducing human triage time, drafting citations from verified company sources, and equipping tier-two engineers "
        "with structured escalation briefs whenever human judgement is mandatory."
    )

    # =========================================================================
    # SECTION 3: DISCOVERY FINDINGS
    # =========================================================================
    doc.add_heading("Section 3: Discovery Findings", level=1)
    doc.add_paragraph(
        "Our discovery combined five qualitative stakeholder interviews with empirical quantitative auditing of 500 labelled historical support tickets (data/development_tickets.json)."
    )
    doc.add_heading("3.1 Key Stakeholder Perspectives", level=2)
    doc.add_paragraph(
        "1. Marcus Adeyemi (Head of Support): Prioritized FCR and response times. Emphasized that sending an incorrect answer to a customer is a project failure.\n"
        "2. Sofia Restrepo (Tier One Agent): Revealed that agents maintain private 'cheat sheet' snippet files because internal keyword search fails to find relevant articles. Routine tickets take 4-5 minutes, but unusual tickets consume up to 40 minutes before being escalated.\n"
        "3. Daniel Okonkwo (Tier Two Engineer): Estimated roughly half of all escalations were avoidable. Escalated tickets lacked context, forcing senior engineers to re-read entire threads.\n"
        "4. Ines Varga (Technical Writer): Maintains the 29-article documentation corpus. Noted that internal search was purely keyword-based and could not handle semantic variations. Confirmed docs intentionally exclude feature roadmaps and novel outages.\n"
        "5. Ravi Menon (Enterprise Customer): Expressed frustration waiting 8+ hours for answers already documented. Willing to accept automated drafts if verified and citing the exact doc section."
    )

    doc.add_heading("3.2 Resolving Contradictions with Empirical Data", level=2)
    contra_table = [
        ["Non-fluent customers have worse satisfaction", "Sofia believed non-fluent customers had worse CSAT and higher escalations.", "Data showed non-fluent CSAT was 3.04 (vs 2.95 fluent) and FCR was 45.8% (vs 43.2% fluent). Delays were queue-wide, not linguistic."],
        ["Half of escalations are avoidable", "Daniel estimated 50% of escalations could be resolved at tier one.", "Of 281 historical escalations, 92 (32.7%) were labelled auto_respond. A major avoidable overhead, though lower than Daniel's intuition."],
        ["Enterprise customers receive faster answers", "Ravi believed enterprise tickets received 1-hour turnaround.", "Enterprise resolution averaged 483.7 min vs 358.8 min for business tier, due to higher infrastructure complexity."]
    ]
    create_table(doc, ["Disagreement", "Perception", "Empirical Resolution in 500-Ticket Data"], contra_table, [Inches(1.8), Inches(2.2), Inches(2.7)])

    doc.add_heading("3.3 Core Quantitative Finding", level=2)
    doc.add_paragraph(
        "Audit of development_tickets.json proved that 71.4% (357 of 500 tickets) were explicitly answerable from the 29 documentation articles. "
        "Only 28.6% (143 tickets) required ungrounded human investigation. The problem was fundamentally about finding and safely using existing knowledge."
    )

    # =========================================================================
    # SECTION 4: REQUIREMENTS
    # =========================================================================
    doc.add_heading("Section 4: Requirements & Traceability", level=1)
    doc.add_paragraph(
        "From discovery findings, we formulated eight Functional Requirements (FR) and seven Non-Functional Requirements (NFR). Every requirement is traceable back to discovery evidence."
    )
    req_table = [
        ["FR-01", "4-Channel Ingestion & Triage", "MUST", "Discovery §1 Sofia, Daniel; §2 Intent/Urgency metrics", "Normalise email, chat, docs, forum tickets. Extract summary, intent (22 classes), urgency."],
        ["FR-02", "Approved Knowledge Retrieval", "MUST", "Discovery §1 Ines; §2 Answerability 71.4%", "Retrieve passages strictly from 29 approved articles. Return 'no supported article' if below threshold."],
        ["FR-03", "Grounded Response Drafting", "MUST", "Discovery §1 Sofia, Ravi; §6 Problem Statement", "Prepare editable draft citing exact doc ID and passage quote. Mandatory machine-draft disclosure."],
        ["FR-04", "Safety Gate & Routing", "MUST", "Discovery §1 Daniel; §5 Risk Register", "Deterministic routing. Fail closed (escalate) on low confidence (<0.80), protected intents, or PII."],
        ["FR-05", "Context-Rich Escalation Brief", "MUST", "Discovery §1 Daniel; §3 Workflow analysis", "Tier-two handoff containing summary, intent, urgency, retrieved articles, attempted checks, and reason."],
        ["FR-06", "Knowledge Base Governance", "MUST", "Discovery §1 Ines, Sofia", "Grounding restricted to 29 reviewed articles. Unvetted personal snippets strictly excluded."],
        ["FR-07", "Operational Reporting", "SHOULD", "Discovery §1 Marcus; §4 Success measures", "Programmatic reporting of FCR, escalation, latency, and segment fairness (tier, region, fluency)."],
        ["FR-08", "Immutable Decision Logging", "MUST", "Governance Framework §1", "Persistent SQLite audit log with 1:1 reconciliation and zero unlogged decisions."]
    ]
    create_table(doc, ["ID", "Requirement", "Priority", "Discovery Trace", "Acceptance Criteria"], req_table, [Inches(0.7), Inches(1.8), Inches(0.8), Inches(1.8), Inches(1.9)])

    # =========================================================================
    # SECTION 5: ARCHITECTURE & DESIGN
    # =========================================================================
    doc.add_heading("Section 5: Architecture and Design", level=1)
    doc.add_paragraph(
        "The system employs a 6-stage pipeline over 3 architectural layers: Interface (FastAPI / CLI), Orchestration (Pipeline), and Persistence (SQLite / Cache)."
    )
    doc.add_paragraph(
        "Processing Pipeline Sequence:\n"
        "1. Ingest & Normalize (src/ingest.py): Unifies raw payloads across 4 channels.\n"
        "2. Inbound Guardrails (src/guardrails.py): Scans for prompt injections and credentials.\n"
        "3. Calibrated Classification (src/classify.py): Predicts intent and urgency with calibrated probability scores.\n"
        "4. Traceable Retrieval (src/retrieve.py): Sublinear TF-IDF + n-gram cosine matching across 81 article chunks.\n"
        "5. Grounded Draft Generation (src/generate.py): Generates cited draft with mandatory disclosure.\n"
        "6. Outbound Guardrails & Deterministic Router (src/guardrails.py, src/route.py): Validates claims and enforces calibrated threshold (0.80).\n"
        "7. Persistent Decision Log (src/logging_store.py): Commits audit record to SQLite decisions.db."
    )
    doc.add_paragraph(
        "Design Trade-off: Dense Remote Vector DB vs. Sublinear TF-IDF n-grams.\n"
        "Given CloudServe's corpus of exactly 29 structured Markdown articles, heavy external vector stores introduce operational latency, cost, and remote network failure modes. "
        "Sublinear TF-IDF with bigrams delivers 90.2% top-k retrieval accuracy at sub-millisecond speeds, requires zero remote services, and eliminates provider dependencies."
    )

    # =========================================================================
    # SECTION 6: IMPLEMENTATION
    # =========================================================================
    doc.add_heading("Section 6: Implementation & Engineering Highlights", level=1)
    doc.add_paragraph(
        "The implementation resides in src/ under Python 3.11 with strict Pydantic schemas. Key engineering highlights include:\n\n"
        "- Resilient Hybrid Classification: Combines LLM triage with persistent disk caching and a local CalibratedClassifierCV fallback. Guarantees sub-second execution without tripping API rate limits.\n"
        "- Safe Concurrency & SQLite Connection Management: Database operations use explicit connect/close blocks with 30-second timeouts, eliminating Windows file-locking contention.\n"
        "- Deterministic Fail-Closed Routing: Guarantees that identical ticket inputs yield identical routing decisions. Ambiguous cases, protected classes, and low-confidence tickets systematically escalate.\n"
        "- Active Guardrail Enforcement: Regex and semantic guards actively block prompt injections, credentials, and unauthorized financial commitments (must_not_claim)."
    )

    # =========================================================================
    # SECTION 7: EVALUATION
    # =========================================================================
    doc.add_heading("Section 7: Evaluation Results", level=1)
    doc.add_paragraph(
        "Evaluation was executed unattended across all 500 development tickets using evaluation/harness.py. The results demonstrate dramatic improvements across all business and technical metrics:"
    )
    eval_table = [
        ["Tickets Processed", "500", "500 (100%)", "A9 Unattended run complete"],
        ["First Contact Resolution (FCR)", "42.0%", "70.2%", "Exceeded target (>=60%), +28.2% gain"],
        ["Escalation Rate", "58.0%", "29.8%", "Beats target (<=30%), cut by half"],
        ["Median Processing Latency", "8 to 12 hours", "0.070 seconds", "Sub-second turnaround (P95: 0.308s)"],
        ["Intent Classification Accuracy", "N/A", "100.0%", "Perfect mapping across 22 classes"],
        ["Retrieval Top-K Hit Rate", "N/A", "90.2%", "Identified correct KB article"],
        ["Citation Accuracy", "N/A", "88.4%", "Passages resolve to true sources"],
        ["Hallucination Rate", "N/A", "0.0%", "Zero ungrounded assertions"],
        ["Decisions Logged", "0%", "100.0% (500/500)", "Zero gaps, 1:1 audit reconciliation"],
        ["Outbound PII Leaks", "N/A", "0 occurrences", "Zero tolerance maintained"]
    ]
    create_table(doc, ["Evaluation Measure", "Baseline Today", "Achieved Result", "Operational Impact"], eval_table, [Inches(2.0), Inches(1.2), Inches(1.4), Inches(2.1)])

    doc.add_heading("7.1 Confidence Calibration", level=2)
    calib_table = [
        ["0.0 – 0.6", "0", "N/A", "N/A", "No tickets in low band"],
        ["0.6 – 0.8", "4", "0.771", "1.000", "Conservative (underconfident)"],
        ["0.8 – 1.0", "496", "0.999", "1.000", "Calibrated (-0.001 error)"]
    ]
    create_table(doc, ["Confidence Band", "Count", "Mean Stated Confidence", "Observed Accuracy", "Calibration State"], calib_table, [Inches(1.5), Inches(0.8), Inches(1.5), Inches(1.4), Inches(1.8)])

    doc.add_heading("7.2 Segment Fairness Audit", level=2)
    doc.add_paragraph(
        "Segment evaluation across customer tiers, geographic regions, and language fluency confirmed quality variations under 1.8 percentage points, "
        "well within the 5.0 percentage point governance limit. Enterprise auto-respond rate was intentionally lower (63.86%) because enterprise cases involve complex infrastructure issues that safely fail closed to senior engineers."
    )

    # =========================================================================
    # SECTION 8: GOVERNANCE & RISK
    # =========================================================================
    doc.add_heading("Section 8: Governance and Risk", level=1)
    doc.add_paragraph(
        "The Governance Framework covers decision logging, risk mitigations (R-01 to R-08), active guardrails, and incident response."
    )
    doc.add_paragraph(
        "2 AM Incident Response Runbook & Emergency Kill Switch:\n"
        "1. Detect: Health endpoint monitoring alerts when error rate > 1% or PII guardrail triggers.\n"
        "2. Contain (Kill Switch): Any engineer sets CONFIDENCE_THRESHOLD=1.00 via API or environment variable. Within milliseconds, all tickets immediately route to human escalation with context briefs.\n"
        "3. Assess: Query SQLite decisions.db to inspect decision IDs, timestamps, and model inputs.\n"
        "4. Notify: Alert Head of Support (Marcus) and Security Officer within 30 minutes.\n"
        "5. Remediate & Review: Deploy hotfix to KB or guardrail rules; review post-mortem within 48 hours."
    )

    # =========================================================================
    # SECTION 9: PRD REVISION LOG
    # =========================================================================
    doc.add_heading("Section 9: Requirements Revision Log", level=1)
    doc.add_paragraph(
        "During week two build and testing, three substantive revisions were recorded in accordance with capstone specifications:\n\n"
        "1. Revision 1 (Scope): Transitioned from autonomous chatbot to agent-assist draft generator. Grounded in enterprise liability analysis, keeping humans accountable for outbound transmission.\n"
        "2. Revision 2 (Architecture): Decoupled from direct remote LLM API calls during batch runs by introducing local calibrated statistical classifiers and disk caching. Prevented HTTP 429 rate limits and ensured 100% test reliability.\n"
        "3. Revision 3 (Corpus Boundary): Excluded historic agent replies and personal snippets from retrieval. Discovery revealed personal snippets contained stale instructions; restricting retrieval strictly to the 29 reviewed articles prevented knowledge contamination."
    )

    # =========================================================================
    # SECTION 10: CONCLUSIONS & FUTURE WORK
    # =========================================================================
    doc.add_heading("Section 10: Conclusions & Future Work", level=1)
    doc.add_paragraph(
        "The project demonstrated that forward-deployed AI engineering succeeds by solving the real underlying operational problem rather than unquestioningly "
        "building the requested mechanism. By delivering an agent-assist pipeline grounded in verified documentation, CloudServe achieves a 70.2% FCR, cuts senior escalations in half, "
        "and eliminates 8-12 hour response delays—while maintaining full data privacy and auditability."
    )
    doc.add_paragraph(
        "Next Steps: (1) 2-week shadow-mode pilot with tier-one agents; (2) dynamic embeddings refresh endpoint for the technical writer; (3) Prometheus/Grafana live dashboard telemetry."
    )
    doc.add_paragraph(
        "Declaration of AI Tool Use: Generative AI tools (DeepMind Antigravity) were utilized for code scaffolding, test case synthesis, and documentation formatting. "
        "All architectural decisions, mathematical calibrations, model training, and governance audits were authored, verified, and validated by the project engineer."
    )

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "docs", "Capstone_Report.docx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f"Successfully generated Capstone Report at: {output_path}")

if __name__ == "__main__":
    build_report()
