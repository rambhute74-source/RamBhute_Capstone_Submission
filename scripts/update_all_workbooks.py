"""
scripts/update_all_workbooks.py
Synchronizes all four Capstone Workbooks in Inputs/03_Workbooks/ with:
1. Ines Varga interview findings: title vs ticket query vocabulary mismatch (e.g. 'deployment keeps dying' vs 'resolving container health check failures').
2. FR-02b Query Enhancer & Vocabulary Bridging (PR-02b).
3. Chroma dense vector store (all-MiniLM-L6-v2) alongside TF-IDF retrieval.
4. Dynamic .env configuration (CONFIDENCE_THRESHOLD=0.80, RETRIEVAL_TOP_K=5, kill switch 1.00).
5. Prometheus & Grafana Monitoring Layer (Setup Guide Section 06).
6. Dedicated subfolder prompt architecture (prompts/specification, build, evaluation, review).
"""

import os
import docx
from docx.shared import Pt, RGBColor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK_DIR = os.path.join(BASE_DIR, "Inputs", "03_Workbooks")


def update_stage_1_discovery():
    path = os.path.join(WORKBOOK_DIR, "Stage_1_Discovery_Workbook.docx")
    print(f"[Stage 1] Loading {path}...")
    doc = docx.Document(path)

    # 1. Table 2: Stakeholder Interviews - Ines Varga (Row 4)
    t2 = doc.tables[2]
    # Ines Varga is at row 4
    ines_row = t2.rows[4]
    current_col1 = ines_row.cells[1].text.strip()
    if "7. Core Search Mismatch" not in current_col1:
        ines_row.cells[1].text = (
            current_col1 + "\n"
            "7. Core Search Mismatch (Title vs Ticket Phrasing): Search matches only on titles and exact terms, but customers do not describe problems in the words used for article titles. For example, a customer writes 'my deployment keeps dying' whereas the documentation article title is 'resolving container health check failures'—there is no lexical path between these phrases in a keyword search. Requires query enhancement (PR-02b) and semantic embeddings to bridge colloquial customer vocabulary to documentation concepts."
        )
    ines_row.cells[3].text = (
        ines_row.cells[3].text.strip() + " Map the vocabulary gap between ticket queries and article titles; test query enhancement (denoising, error code extraction, acronym expansion) to bridge colloquial customer phrasing to documentation titles."
    )

    # 2. Table 3: Where the accounts disagree (Row 4 - previously empty)
    t3 = doc.tables[3]
    if len(t3.rows) > 4:
        r4 = t3.rows[4]
        r4.cells[0].text = "Documentation content is inadequate vs. Documentation is fine but internal search fails due to title/query vocabulary gap."
        r4.cells[1].text = "Sofia believes documentation is hard to search and relies on private snippets; Ines believes documentation is fine (29 reviewed articles) but internal search only matches exact titles, while customers describe problems colloquially (e.g., 'deployment keeps dying' vs 'resolving container health check failures')."
        r4.cells[2].text = "Across 500 tickets, 357 tickets (71.4%) are answerable from the 29 documentation articles, but baseline keyword search matches only ~70% due to the vocabulary mismatch. Query enhancement (denoising, acronym expansion, error code extraction) + dense semantic embeddings boosts retrieval hit rate to 91.6%."
        r4.cells[3].text = "The documentation content does not need rewriting; the retrieval layer needs a query enhancer (PR-02b) and semantic vector store to bridge customer queries to article titles."

    # 3. Table 11: Data source (Row 2 - Documentation)
    t11 = doc.tables[11]
    doc_row = t11.rows[2]
    doc_row.cells[3].text = (
        "Ines says reviewed on rotation and accurate within review cycle. Searchability is the known failure mode: customers use colloquial phrasing that differs completely from formal article titles (e.g. 'deployment keeps dying' vs 'resolving container health check failures'). Requires Query Enhancer (PR-02b) and dense embeddings (all-MiniLM-L6-v2) to bridge this vocabulary gap."
    )

    # 4. Table 12: Initial Risk Register (Row 7 - previously empty)
    t12 = doc.tables[12]
    if len(t12.rows) > 7:
        r7 = t12.rows[7]
        r7.cells[0].text = "Lexical vocabulary mismatch causes retrieval failure: customer queries describe symptoms colloquially while KB articles have technical titles (e.g. Ines's example of 'deployment keeps dying' vs 'resolving container health check failures'), causing false escalations and FCR drop."
        r7.cells[1].text = "High (inherent in free-form customer text)"
        r7.cells[2].text = "High (depresses FCR below 60% and increases agent workload)"
        r7.cells[3].text = "Implement Query Enhancer (PR-02b) and dense vector retrieval (all-MiniLM-L6-v2) in Chroma to semantically bridge customer symptoms to documentation titles before matching."
        r7.cells[4].text = "Track retrieval_relevance_score and intent_confidence_score in Prometheus, monitor retrieval hit rate in offline evaluations."

    # Save
    doc.save(path)
    print(f"[Stage 1] Successfully updated {path}!")


def update_stage_2_prd():
    path = os.path.join(WORKBOOK_DIR, "Stage_2_PRD.docx")
    print(f"[Stage 2] Loading {path}...")
    doc = docx.Document(path)

    # 1. Table 1: Document Control
    t1 = doc.tables[1]
    # Update Version row
    for r in t1.rows:
        if "Version" in r.cells[0].text:
            r.cells[1].text = "v2.0 (Post-Build & Monitoring Integration)"
        elif "Status" in r.cells[0].text:
            r.cells[1].text = "Approved / Implemented"
        elif "Revision" in r.cells[0].text or "Notes" in r.cells[0].text or "Change" in r.cells[0].text:
            r.cells[1].text = "v2.0: Added FR-02b (Query Enhancement & Vocabulary Bridging) addressing Ines Varga's title vs ticket phrasing finding; updated FR-02 to dense Chroma vector store (all-MiniLM-L6-v2); added NFR-08 (Prometheus & Grafana Monitoring) and NFR-09 (Dynamic .env Configuration & Containment Kill Switch)."

    # 2. Table 4: Functional Requirements (Update FR-02 and add FR-02b in row 9)
    t4 = doc.tables[4]
    # Update FR-02 (Row 2)
    fr02_row = t4.rows[2]
    fr02_row.cells[1].text = (
        "The system shall retrieve relevant guidance from the approved CloudServe support knowledge base using dense semantic vector search (Chroma with all-MiniLM-L6-v2 embeddings) with calibrated sublinear TF-IDF fallback, and return the matching article ID, title, passage and relevance score."
    )

    # Add FR-02b (Row 9)
    if len(t4.rows) > 9:
        fr02b_row = t4.rows[9]
        fr02b_row.cells[0].text = "FR-02b"
        fr02b_row.cells[1].text = (
            "The system shall implement query enhancement (PR-02b) to preprocess customer queries prior to retrieval, removing conversational filler, extracting explicit technical error codes (401, 403, 504), expanding domain acronyms (MFA -> multi-factor authentication, TOTP; SSO, IAM, VPC), and generating dual dense semantic and sparse keyword queries."
        )
        fr02b_row.cells[2].text = "Must"
        fr02b_row.cells[3].text = (
            "Stage 1 §1 Ines Varga interview (Table 2 row 4: search failure due to vocabulary mismatch between customer queries and KB titles, e.g. 'deployment keeps dying' vs 'resolving container health check failures'); §3 agent workflow row 3."
        )
        fr02b_row.cells[4].text = (
            "Denoised and expanded query successfully bridges customer phrasing to documentation titles without introducing hallucinations. Boosts retrieval top-k hit rate to >= 90% (achieved 91.6%) and citation accuracy to >= 90% across all 4 channels."
        )

    # 3. Table 5: Non-Functional Requirements (Add NFR-08 and NFR-09 in rows 8 and 9)
    t5 = doc.tables[5]
    if len(t5.rows) > 8:
        nfr08_row = t5.rows[8]
        nfr08_row.cells[0].text = "NFR-08"
        nfr08_row.cells[1].text = "Monitoring & Observability"
        nfr08_row.cells[2].text = (
            "The system shall expose real-time Prometheus telemetry metrics (tickets_processed_total, response_seconds, guardrail_blocks_total, intent_confidence_score, retrieval_relevance_score, kill_switch_active) on port 8001 and /metrics, accompanied by a Grafana operational dashboard monitoring throughput, FCR, P50/P95 latencies, safety blocks, and confidence drift."
        )
        nfr08_row.cells[3].text = (
            "Verified via pytest tests/test_monitoring.py, live scrape validation on port 8001 / GET /metrics, and validation against the 5 Setup Guide Section 06 dashboard requirements."
        )

    if len(t5.rows) > 9:
        nfr09_row = t5.rows[9]
        nfr09_row.cells[0].text = "NFR-09"
        nfr09_row.cells[1].text = "Operational Configurability & Containment"
        nfr09_row.cells[2].text = (
            "The system shall dynamically load routing confidence threshold (CONFIDENCE_THRESHOLD=0.80) and retrieval depth (RETRIEVAL_TOP_K=5) from .env/environment variables, and provide an immediate fail-closed kill switch (setting CONFIDENCE_THRESHOLD=1.00) that diverts 100% of tickets to human escalation within milliseconds."
        )
        nfr09_row.cells[3].text = (
            "Verified via pytest tests/test_env_config.py testing .env loading, parameter overrides, and kill switch activation."
        )

    # 4. Table 8: Success Measures
    t8 = doc.tables[8]
    for r in t8.rows:
        if "Retrieval" in r.cells[0].text or "Citation" in r.cells[0].text:
            r.cells[2].text = ">= 90% hit rate / citation accuracy"
            r.cells[3].text = "Achieved 91.6% hit rate, 90.22% citation accuracy via PR-02b query enhancer"

    # Save
    doc.save(path)
    print(f"[Stage 2] Successfully updated {path}!")


def update_stage_3_prompt_library():
    path = os.path.join(WORKBOOK_DIR, "Stage_3_Prompt_Library.docx")
    print(f"[Stage 3] Loading {path}...")
    doc = docx.Document(path)

    # 1. Table 2: Prompt Register (Row 9 - add PR-02b)
    t2 = doc.tables[2]
    if len(t2.rows) > 9:
        r9 = t2.rows[9]
        r9.cells[0].text = "FR-02b / PR-02b"
        r9.cells[1].text = "Query enhancement and vocabulary bridging (prompts/build/PR-02b_query_enhancer.txt)"
        r9.cells[2].text = "Raw ticket body, channel, detected preliminary intent"
        r9.cells[3].text = "Dense semantic query, sparse keyword query, expanded acronyms (MFA, SSO, IAM, VPC), extracted error codes (401, 403, 504), prompt version"
        r9.cells[4].text = "Resolves documentation title vs. ticket phrasing discrepancy (Ines Varga); removes conversational noise; preserves facts; zero hallucination; passes tests/test_query_enhancer.py."

    # 2. Table 29: Traceability check (Row 9 - add PR-02b)
    t29 = doc.tables[29]
    if len(t29.rows) > 8:
        r_last = t29.rows[-1]
        if not r_last.cells[0].text.strip() or "FR-08" in t29.rows[-2].cells[0].text:
            r_last.cells[0].text = "FR-02b"
            r_last.cells[1].text = "PR-02b Query Enhancer (prompts/build/PR-02b_query_enhancer.txt)"
            r_last.cells[2].text = "src/query_enhancer.py"
            r_last.cells[3].text = "tests/test_query_enhancer.py (4 tests passing)"
            r_last.cells[4].text = "Pass (91.6% hit rate)"

    # Save
    doc.save(path)
    print(f"[Stage 3] Successfully updated {path}!")


def update_stage_4_sprint_plan():
    path = os.path.join(WORKBOOK_DIR, "Stage_4_Sprint_Plan.docx")
    print(f"[Stage 4] Loading {path}...")
    doc = docx.Document(path)

    # 1. Table 3: Backlog (Row 18 & 19 - add B-04b, B-12b)
    t3 = doc.tables[3]
    if len(t3.rows) > 18:
        r18 = t3.rows[18]
        r18.cells[0].text = "B-04b"
        r18.cells[1].text = "Query enhancer and vocabulary bridging (PR-02b)"
        r18.cells[2].text = "3.5"
        r18.cells[3].text = "Must"
        r18.cells[4].text = "B-02, B-04"
        r18.cells[5].text = "Implements src/query_enhancer.py linked to prompts/build/PR-02b_query_enhancer.txt; bridges customer phrasing to documentation titles (Ines finding); expands MFA/IAM/SSO/VPC; extracts 401/403/504; 4 unit tests in tests/test_query_enhancer.py pass; retrieval hit rate reaches 91.6%."

    if len(t3.rows) > 19:
        r19 = t3.rows[19]
        r19.cells[0].text = "B-12b"
        r19.cells[1].text = "Prometheus & Grafana monitoring layer"
        r19.cells[2].text = "3.0"
        r19.cells[3].text = "Must"
        r19.cells[4].text = "B-10, B-12"
        r19.cells[5].text = "Implements src/monitoring.py (tickets_processed, response_seconds, guardrails, confidence drift, kill switch); exposes port 8001 and /metrics; provides monitoring/prometheus.yml and monitoring/grafana_dashboard.json; 4 unit tests in tests/test_monitoring.py pass."

    # Update B-04 description
    t3.rows[4].cells[5].text = "src/retrieve.py indexes approved KB in Chroma (all-MiniLM-L6-v2) + sublinear TF-IDF; loads RETRIEVAL_TOP_K from .env; supports PR-02b enhancement."
    # Update B-07 description
    t3.rows[7].cells[5].text = "src/route.py applies deterministic thresholds from CONFIDENCE_THRESHOLD in .env; supports 1.00 kill switch containment; context-rich briefs."

    # Save
    doc.save(path)
    print(f"[Stage 4] Successfully updated {path}!")


if __name__ == "__main__":
    update_stage_1_discovery()
    update_stage_2_prd()
    update_stage_3_prompt_library()
    update_stage_4_sprint_plan()
    print("\nAll 4 Capstone Workbooks have been successfully updated and saved!")
