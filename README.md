# CloudServe Intelligent Customer Support System

An end-to-end forward deployed AI engineering system for CloudServe Solutions.
Built to address support queue bottlenecks, eliminate avoidable escalations, ensure strict data privacy and grounded citations, and maintain auditable decision logging.

---

## 1. Quick Start Guide

### Prerequisites
- Python 3.10 or later (`python --version`)
- Git

### Installation

```bash
# 1. Clone repository and navigate to root
 cd C:\Users\user\Desktop\CloudeVerseProject ('Sample Path')

# 2. Create and activate a virtual environment
python -m venv .venv

# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# 3. Install pinned dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env to verify OPENROUTER_API_KEY and model configurations
```

---

## 2. Running Tests (Acceptance Criterion A12)

Execute the complete test suite covering all 12 acceptance criteria (A1–A12):

```bash
python -m pytest tests/ -v
```

All 14 unit and integration tests execute and pass cleanly.

---

## 3. Running the Unattended Evaluation Harness (Criteria A9 & A10)

The evaluation harness processes any input ticket dataset unattended without hardcoded paths, producing comprehensive business, technical, and governance metrics reports:

```bash
python -m evaluation.harness --input data/validation_tickets.json --output evaluation/results/
```

### Evaluation Output Artifacts
The harness automatically outputs:
- `evaluation/results/metrics_report.json`: Master JSON report containing volume, business, technical, governance, and fairness metrics.
- `evaluation/results/metrics_summary.txt`: Human-readable executive summary.
- `evaluation/results/calibration_table.csv`: Stated confidence vs. observed accuracy per bin.
- `evaluation/results/fairness_audit.csv`: Segmented quality across customer tiers, regions, and fluency.
- `evaluation/results/processed_tickets.json`: Detailed per-ticket execution trace.

---

## 4. Starting the API Server

Launch the FastAPI application:

```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### API Endpoints
- `POST /tickets/process`: Process a single ticket end-to-end through triage, retrieval, guardrails, and routing.
- `POST /tickets/batch`: Batch process multiple tickets.
- `GET /decisions`: Query the persistent SQLite audit log.
- `GET /health`: Health and knowledge base index status.

---

## 5. System Architecture

```
[Inbound Tickets (4 Channels: Email, Chat, Docs, Forum)]
                       │
                       ▼
            [1. Ingest & Normalize (src/ingest.py)]
                       │
                       ▼
       [2. Inbound Guardrails (src/guardrails.py)]
       ├── PII Detection (API keys, credentials, SSN)
       └── Prompt Injection / Instruction Integrity
                       │
                       ▼
        [3. Classification (src/classify.py)]
       ├── Intent Category (22 Classes)
       ├── Urgency Level (High, Medium, Low)
       └── Calibrated Confidence Score [0.0 - 1.0]
                       │
                       ▼
         [4. Retrieval (src/retrieve.py)]
       └── TF-IDF / Sublinear n-grams over 29 Approved KB Articles
                       │
                       ▼
      [5. Grounded Generator (src/generate.py)]
       ├── Explicit Machine-Draft Disclosure Header
       ├── Exact Citations to Retrieved Articles
       └── Adherence to `must_not_claim` Policies
                       │
                       ▼
       [6. Outbound Guardrails (src/guardrails.py)]
       ├── Grounding & Unsupported Claim Checks
       └── Outbound PII Leakage Protection
                       │
                       ▼
      [7. Deterministic Router (src/route.py)]
       ├── Fail-closed for Protected Intents (Security, Billing, Compliance)
       ├── Threshold Enforcement (>= 0.80)
       ├── Automated Draft vs. Context-Rich Escalation Brief
                       │
                       ▼
      [8. Decision Logger (src/logging_store.py)]
       └── Persistent SQLite Audit Log (1:1 Reconciliation)
```

---

## 6. Acceptance Criteria Compliance Matrix

| Criterion | Requirement | Verification Method | Status |
|---|---|---|---|
| **A1** | Runs from clean checkout | Documented commands in README | **PASS** |
| **A2** | Ingests 4 channels into normalized representation | `test_a2_four_channel_ingestion` | **PASS** |
| **A3** | Intent & urgency classification with numeric confidence | `test_a3_classification_confidence` | **PASS** |
| **A4** | Retrieval against 29 approved KB articles | `test_a4_retrieval_returns_traceable_sources` | **PASS** |
| **A5** | Deterministic routing with calibrated threshold | `test_a5_routing_is_deterministic` | **PASS** |
| **A6** | Generated answers carry valid citations | `test_a6_answer_generation_and_citations` | **PASS** |
| **A7** | Guardrail actively blocks adversarial & PII inputs | `test_a7_guardrail_blocks_prompt_injection` | **PASS** |
| **A8** | Persistent decision log reconciling 1:1 | `test_a8_decision_logging_and_reconciliation` | **PASS** |
| **A9** | Unattended full evaluation run | `python -m evaluation.harness` on 500 tickets | **PASS** |
| **A10** | Metrics report generated automatically | `evaluation/results/metrics_report.json` | **PASS** |
| **A11** | Failure handling without crashing | `test_a11_pipeline_handles_malformed_input` | **PASS** |
| **A12** | Test suite runs and passes with single command | `python -m pytest tests/ -v` (14/14 pass) | **PASS** |
