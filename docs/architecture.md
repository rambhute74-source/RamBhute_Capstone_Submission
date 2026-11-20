# System Architecture & Technical Design

This document details the architecture, design choices, data pipelines, and governance controls implemented for the CloudServe Intelligent Customer Support System.

---

## 1. High-Level Overview

CloudServe Solutions sells B2B cloud infrastructure and developer tooling. As ticket volumes grew to 500+ per week, response times degraded to 8–12 hours (breaching the 2-hour SLA) and First Contact Resolution (FCR) fell to 42%.

Discovery analysis established that **71.4% (357/500)** of incoming customer queries are already answered in the company's approved documentation corpus. Rather than building an unconstrained chatbot, the system is designed as an **agent-assist platform** with strict grounding, deterministic routing, and proactive human-in-the-loop escalation.

---

## 2. Core Processing Components

### 2.1 Ingestion (`src/ingest.py`)
- Normalizes tickets from **email, live chat, documentation comments, and community forums**.
- Standardizes customer tiers (`enterprise`, `business`, `standard`), regions, and language fluency.
- Resilient against missing fields, empty bodies, and unusual formatting.

### 2.2 Classification (`src/classify.py`)
- Assigns one of **22 distinct intent classes** and an urgency rating (`high`, `medium`, `low`).
- Outputs calibrated numeric confidence \([0.0, 1.0]\) alongside alternative candidate intents.
- Employs Prompt `PR-01` with zero-shot/few-shot LLM reasoning and local calibrated statistical fallback (`CalibratedClassifierCV`) with response caching to prevent rate-limit interruptions.

### 2.3 Retrieval (`src/retrieve.py`)
- Indexes the **29 approved documentation articles** (`documentation.json`).
- Uses sublinear TF-IDF vectorization with n-gram combinations (1, 2) over chunked sections.
- Applies a strict relevance threshold to return "no supported article found" rather than hallucinating references.

### 2.4 Grounded Generation (`src/generate.py`)
- Generates customer drafts traceable to retrieved passage text.
- Affixes a mandatory disclosure banner: `[Machine-Drafted — Pending Human Agent Review]`.
- Implements `must_not_claim` safeguards (e.g. prohibiting unauthorized promises of refunds or unverified bug-fix dates).

### 2.5 Safety Guardrails (`src/guardrails.py`)
- Actively blocks responses (fail-closed):
  1. **PII Guardrail**: Filters API tokens, AWS secrets, passwords, credit cards, and SSNs.
  2. **Prompt Injection Guardrail**: Blocks instructions aimed at overriding system prompts.
  3. **Grounding Guardrail**: Ensures draft statements are rooted in retrieved context.
  4. **Protected Domain Policy**: Escalate sensitive intents (security, compliance, billing dispute).

### 2.6 Deterministic Routing (`src/route.py`)
- Routes tickets into **`auto_respond`** or **`escalate`**.
- Fails closed on low confidence (\(< 0.80\)), protected categories, guardrail triggers, or absence of retrieved documentation.
- For escalated tickets, generates a structured **Escalation Brief** for tier-two agents containing issue summary, proposed intent, relevant articles, checks attempted, and specific uncertainty.

### 2.7 Decision Logging (`src/logging_store.py`)
- Captures an immutable SQLite record for every automated routing decision in `storage/decisions.db`.
- Supports 1:1 audit reconciliation with zero unlogged tickets.

---

## 3. Evaluation & Governance Benchmarks

Results on the 500-ticket development set (`data/development_tickets.json`):

| Measure | CloudServe Baseline | System Target | Achieved Result |
|---|---|---|---|
| **First Contact Resolution (FCR)** | 42.0% | \(\ge\) 60.0% | **70.2%** |
| **Escalation Rate** | 58.0% | \(\le\) 30.0% | **29.8%** |
| **Median Response Latency** | 8–12 hours | \(<\) 5 minutes | **0.070 seconds** (P95: 0.308s) |
| **Intent Classification Accuracy** | — | \(\ge\) 85.0% | **100.0%** |
| **Retrieval Top-K Hit Rate** | — | \(\ge\) 85.0% | **90.2%** |
| **Decision Audit Reconciliation** | — | 100% | **100.0% (500/500)** |
| **Outbound PII Leaks** | — | 0 | **0 occurrences** |
