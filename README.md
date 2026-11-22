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
# 1. Clone the repository and enter the project folder
(git clone https://github.com/rambhute74-source/05_SourceCode.git
cd 05_SourceCode)

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
# Windows PowerShell:
Copy-Item .env.example .env
# Linux / macOS:
cp .env.example .env
# Add an OpenRouter API key to .env to enable LLM-backed features.
```

---

## 2. Running Tests (Acceptance Criterion A12)

Execute the complete test suite covering all 12 acceptance criteria (A1–A12) along with dynamic configuration, Prometheus telemetry, prompt linking, and query enhancement:

```bash
python -m pytest tests/ -v
```

All 33 unit, integration, and operational tests execute and pass cleanly (14 acceptance tests, 5 environment configuration tests, 4 Prometheus monitoring tests, 6 prompt linking tests, and 4 query enhancer tests).

---

## 3. Running the Unattended Evaluation Harness (Criteria A9 & A10)

The evaluation harness processes any input ticket dataset unattended without hardcoded paths, producing comprehensive business, technical, and governance metrics reports:

```bash
python -m evaluation.harness --input data/development_tickets.json --output evaluation/results/
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
- `GET /metrics`: Prometheus metrics scrape endpoint (traffic volume, confidence, latency, guardrail trips).

---

## 5. Monitoring Dashboard

Start the API server first, then start Prometheus and Grafana:

```bash
# Terminal 1: start the CloudServe API and metrics server
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# Terminal 2: start the monitoring containers
cd monitoring
docker compose up -d
```

Open the monitoring services in a browser:

- **Grafana dashboard:** <http://localhost:3000>
- **Provisioned CloudServe dashboard:** <http://localhost:3000/d/cloudserve-monitoring>
- **Prometheus:** <http://localhost:9090>
- **API metrics:** <http://localhost:8000/metrics>

Grafana accepts the configured credentials `admin` / `admin`. Anonymous access is also enabled. The CloudServe dashboard is automatically provisioned in the **CloudServe** folder.

To stop the monitoring containers:

```bash
cd monitoring
docker compose down
```

---

## 6. System Architecture

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
        [3. Query Enhancer (src/query_enhancer.py - PR-02b)]
       └── Vocabulary Bridging & Symptom-to-KB Title Expansion
                       │
                       ▼
         [4. Classification (src/classify.py - PR-01)]
       ├── Intent Category (22 Classes)
       ├── Urgency Level (High, Medium, Low)
       └── Calibrated Confidence Score [0.0 - 1.0]
                       │
                       ▼
     [5. Dual Retrieval Engine (src/retrieve.py - PR-02)]
       ├── Dense Chroma Vector Store (all-MiniLM-L6-v2, 59 chunks)
       └── Sublinear TF-IDF Deterministic Fallback (29 Articles)
                       │
                       ▼
      [6. Grounded Generator (src/generate.py - PR-04)]
       ├── Explicit Machine-Draft Disclosure Header
       ├── Exact Citations to Retrieved Articles
       └── Adherence to `must_not_claim` Policies
                       │
                       ▼
       [7. Outbound Guardrails (src/guardrails.py)]
       ├── Grounding & Unsupported Claim Checks
       └── Outbound PII Leakage Protection
                       │
                       ▼
     [8. Deterministic Router (src/route.py - PR-03/PR-05)]
       ├── Fail-closed for Protected Intents (Security, Billing, Compliance)
       ├── Dynamic Confidence Threshold Enforcement (>= 0.80 from .env)
       ├── Containment Kill Switch Enforcement (KILL_SWITCH_ACTIVE)
       └── Automated Draft vs. Context-Rich Escalation Brief
                       │
                       ▼
       [9. Decision Logger (src/logging_store.py)]
       └── Persistent SQLite Audit Log (1:1 Reconciliation)
                       │
                       ▼
     [10. Telemetry & Monitoring (src/monitoring.py)]
       └── Prometheus Exporter (/metrics:8001) & Grafana Dashboard
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
| **A9** | Unattended full evaluation run | `python -m evaluation.harness` on tickets | **PASS** |
| **A10** | Metrics report generated automatically | `evaluation/results/metrics_report.json` | **PASS** |
| **A11** | Failure handling without crashing | `test_a11_pipeline_handles_malformed_input` | **PASS** |
| **A12** | Test suite runs and passes with single command | `python -m pytest tests/ -v` (33/33 pass) | **PASS** |
| **Ext-1** | Dynamic .env Configuration & Kill Switch | `tests/test_env_config.py` (5/5 pass) | **PASS** |
| **Ext-2** | Prometheus Telemetry & Metrics Scrape | `tests/test_monitoring.py` (4/4 pass) | **PASS** |
| **Ext-3** | Versioned Prompt Linking & Registry | `tests/test_prompt_linking.py` (6/6 pass) | **PASS** |
| **Ext-4** | PR-02b Query Enhancer & Vocabulary Bridging | `tests/test_query_enhancer.py` (4/4 pass) | **PASS** |

---

## 7. Attribution & AI Tool Use Declaration

This project was engineered and implemented by **Ram Bhute** as the Capstone Project for Forward Deployed AI Engineering.

### Core Frameworks & Open Source Libraries
- **LLM Foundation Model**: Meta LLaMA 3.1 8B Instruct (`meta-llama/llama-3.1-8b-instruct`) accessed via OpenRouter API.
- **Dense Embeddings & Vector Storage**: Sentence-Transformers (`all-MiniLM-L6-v2`) and ChromaDB vector store.
- **Web API & Validation**: FastAPI (`0.104.0+`), Uvicorn, and Pydantic v2.
- **Machine Learning & Retrieval**: Scikit-Learn (TF-IDF vectorizer, cosine similarity).
- **Observability**: Prometheus Client (`prometheus_client`) and Grafana dashboard templates.
- **Testing**: PyTest (`pytest`, `pytest-asyncio`).

### AI Assistance Declaration
In accordance with Stage 6 submission guidelines:
- **AI Tool Used**: Antigravity / Gemini CLI acting as an AI pair programmer.
- **Nature of Assistance**: Assisted with initial boilerplate scaffolding, test case expansion across edge scenarios, and markdown/document styling synchronization.
- **Human Oversight**: All architecture decisions, prompt engineering formulations, guardrail boundaries, routing logic, and verification were directed, reviewed, and finalized by Ram Bhute.

