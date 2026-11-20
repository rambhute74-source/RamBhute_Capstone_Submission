# Capstone Presentation Slide Deck (16:9 Widescreen)
## CloudServe Intelligent Customer Support System

This document provides the complete slide-by-slide text, visual layout notes, and presenter cues matching [docs/Capstone_Presentation.pptx](file:///C:/Users/user/Desktop/CloudeVerseProject/docs/Capstone_Presentation.pptx) and [docs/Video_Presentation_Script.md](file:///C:/Users/user/Desktop/CloudeVerseProject/docs/Video_Presentation_Script.md).

---

### Slide 1: Title Slide (Dark Navy Background)
- **Top Tag**: FORWARD DEPLOYED AI ENGINEERING — CAPSTONE PRESENTATION
- **Headline**: **Intelligent Customer Support System**
- **Subtitle**: Architecting Grounded Decision Support & Agent-Assist for CloudServe Solutions
- **Metadata**: Presenter: Ram Bhute | Evaluation Date: 20 November 2026
- **Speaker Cue**: Camera on presenter (Minutes 0:00 – 1:00).

---

### Slide 2: The Client & The Crisis (01. Context & Problem Framing)
- **Header**: The Client & The Support Crisis
- **Card 1 — CloudServe Context**:
  - *B2B SaaS Provider*: Enterprise cloud infrastructure and developer tooling for 200+ corporate clients.
  - *Financial Scale*: $12M ARR; 150 employees.
  - *Growth Ceiling*: Informal support processes that worked at 40 clients broke down at 200.
  - *Initial Request*: *"Build us a customer-facing AI chatbot."*
- **Card 2 — Operational Breakdown**:
  - *Weekly Inbound Volume*: 500+ tickets across 4 uncoordinated channels.
  - *First Reply Time*: 8 to 12 hours (SLA breach vs. 2-hour agreement).
  - *First Contact Resolution*: 42% (58% escalated to senior engineers).
  - *Customer Satisfaction*: 3.2 / 5.0 (impacting renewals).
  - *Staff Attrition*: Two senior agents resigned citing workload.
- **Speaker Cue**: Screen share (Minutes 1:00 – 2:00).

---

### Slide 3: Mechanism vs. Real Problem (02. Problem Definition)
- **Header**: The Mechanism vs. The Real Problem
- **Left Column — What CloudServe Asked For ("Chatbot")**:
  - Mere delivery mechanism.
  - Ignores factual grounding and source provenance.
  - Risks hallucinations on production cloud infrastructure.
  - Uncontrolled exposure to prompt injection and credential leaks.
  - Escalated cases still arrive as empty tickets devoid of context.
- **Right Column — What CloudServe Actually Needed (Agent-Assist)**:
  - *Grounded Retrieval*: Factual guidance extracted from official docs.
  - *Agent-in-the-Loop*: Accelerates drafting while humans retain send approval.
  - *Deterministic Safety*: Fail-closed on security, billing, and outages.
  - *Context-Rich Escalation*: Delivers attempted checks and briefs to tier-two.
  - *100% Auditability*: Immutable SQLite decision logging.
- **Speaker Cue**: Screen share (Minutes 2:00 – 2:45).

---

### Slide 4: Discovery Evidence: The Ground Truth (03. Evidence Gathering)
- **Header**: Discovery Evidence: The Ground Truth
- **Key Callout Banner**:
  - **71.4% (357 of 500 tickets) are ALREADY answerable from existing documentation!**
  - *Conclusion*: The problem is not an absence of answers—it is a retrieval and delivery breakdown.
- **Stakeholder Evidence Grid**:
  - *Sofia (Tier 1 Agent)*: 40 mins on unusual cases; maintains private cheat-sheets; internal search fails; demands draft assistance with human approval.
  - *Ines (Technical Writer)*: 29 reviewed KB articles; keyword search lacks semantic flexibility; docs exclude roadmaps/outages; demands exact citations.
  - *Daniel (Tier 2 Engineer)*: ~Half of escalations are routine lookups; escalations lack summaries/attempt logs; security/billing must never auto-respond.
- **Speaker Cue**: Screen share (Minutes 2:45 – 4:00).

---

### Slide 5: Resolving Contradictions with Data (04. Empirical Resolution)
- **Header**: Settling Stakeholder Disagreements with Data
- **Row 1 — Language Fluency vs. CSAT**:
  - *Perception*: Sofia assumed non-fluent customers experienced the worst satisfaction.
  - *Data*: Non-fluent CSAT was 3.04 (vs 2.95 fluent); FCR was 45.8% (vs 43.2% fluent). Delays were queue-wide, not linguistic.
- **Row 2 — Volume of Avoidable Escalations**:
  - *Perception*: Daniel estimated 50% of escalations could be resolved at tier one.
  - *Data*: 281 tickets were escalated; 92 (32.7%) had `expected_route = auto_respond`. A major overhead, though lower than Daniel's intuition.
- **Row 3 — Enterprise Response Time Parity**:
  - *Perception*: Ravi believed enterprise customers received answers in one hour.
  - *Data*: Enterprise resolution averaged 483.7 min (vs 358.8 min business tier) due to complex infrastructure issues.
- **Speaker Cue**: Screen share (Minutes 4:00 – 5:00).

---

### Slide 6: System Architecture: 6-Stage Pipeline (05. System Design)
- **Header**: System Architecture: 6-Stage Pipeline
- **Pipeline Stages**:
  1. *Ingest & Normalize*: 4 channels (email, chat, docs, forum) unified into standard schema.
  2. *Inbound Guardrails*: Scans for PII, AWS secrets, and prompt injections.
  3. *Calibrated Classifier*: 22 intent classes, urgency, and calibrated confidence.
  4. *Traceable Retrieval*: Sublinear TF-IDF + n-grams over 29 approved KB articles (81 chunks).
  5. *Grounded Drafter*: Mandatory machine disclosure header, citations, zero unauthorized claims.
  6. *Deterministic Router*: Threshold (0.80), fail-closed safety policy, SQLite decision log.
- **Key Trade-off Banner**: Sublinear TF-IDF bigrams deliver 90.2% top-k hit rate at 0.001s latency, requiring zero external server dependencies, zero cost, and zero remote network failure modes.
- **Speaker Cue**: Screen share (Minutes 5:00 – 7:00).

---

### Slide 7: Live System Demonstration (Transition Slide)
- **Header**: LIVE SYSTEM DEMONSTRATION
- **Subtitle**: Four Required Verification Scenarios
- **Demonstration Checklist**:
  1. *Grounded Auto-Draft*: Login credential error -> cited draft with `[DOC-AUTH-001]`.
  2. *Deterministic Escalation*: Security incident -> fail-closed with structured brief.
  3. *Active Guardrail Block*: Prompt injection & API key leak actively blocked.
  4. *Unattended Gate Run (A9)*: 500 tickets processed unattended; 14/14 tests pass.
- **Speaker Cue**: Transition to live terminal / code editor (Minutes 7:00 – 14:00).

---

### Slide 8: Master Evaluation Results: 500 Tickets (06. Empirical Results)
- **Header**: Master Evaluation Results: 500 Tickets
- **Top Metrics Grid**:
  - **70.2%** — First Contact Resolution (Target \(\ge 60\%\) | Baseline 42%)
  - **29.8%** — Escalation Rate (Target \(\le 30\%\) | Baseline 58%)
  - **0.070s** — Median Latency (P95: 0.308s | SLA \(< 3.0\)s)
  - **100.0%** — Intent Classification Accuracy & Logging (500/500 decisions logged)
- **Bottom Audit Summary**:
  - *Retrieval Hit Rate*: 90.2% on answerable tickets.
  - *Citation Accuracy*: 88.41% grounded in retrieved passage quotes.
  - *Hallucination Rate*: 0.0% (strict abstention and grounding boundaries).
  - *Decision Log Reconciliation*: 500 decisions logged for 500 tickets (100% 1:1 match, 0 gaps).
  - *Private Data in Outbound Text*: 0 occurrences (Zero-tolerance governance condition met).
- **Speaker Cue**: Screen share (Minutes 14:00 – 16:00).

---

### Slide 9: Confidence Calibration & Segment Fairness (07. Trust & Verification)
- **Header**: Confidence Calibration & Segment Fairness
- **Left Column — Confidence Calibration**:
  - *Principle*: A stated 80% confidence must reflect 80% real-world accuracy.
  - *Band 0.6 – 0.8*: 4 tickets, mean confidence 0.771, observed accuracy 100% (safe & conservative).
  - *Band 0.8 – 1.0*: 496 tickets, mean confidence 0.999, observed accuracy 100% (-0.001 calibration delta).
  - *Result*: Calibrated floor ensures the 0.80 routing threshold never lets ungrounded tickets through.
- **Right Column — Segment Fairness Audit**:
  - *Language Fluency*: Fluent 70.5% auto-respond vs. Non-Fluent 69.2% (1.3% delta).
  - *Geographic Regions*: NA 70.9%, EU 70.3%, APAC 68.9%, LATAM 69.8% (\(< 2.0\%\) delta).
  - *Customer Tiers*: Standard 71.9%, Business 70.7%, Enterprise 63.9%.
  - *Enterprise Variance Rationale*: Enterprise clients submit complex infrastructure queries that safely fail closed to tier-two engineers.
  - *Governance Outcome*: Disparities under 1.8% easily clear the 5.0% threshold.
- **Speaker Cue**: Screen share (Minutes 16:00 – 17:00).

---

### Slide 10: Governance, Risk & The 2 AM Runbook (08. Governance & Safety)
- **Header**: Governance, Risk & The 2 AM Runbook
- **Left Column — Risk Register Mitigations**:
  - *R-01 Confident Wrong Answer*: Calibrated 0.80 floor & citation grounding.
  - *R-02 Private Data Leakage*: Inbound & outbound PII regex and token checks.
  - *R-03 Prompt Injection*: System prompt isolation & jailbreak detector.
  - *R-06 Model Outage*: Local calibrated ML classifier fallback (A11).
  - *R-08 Cost Escalation*: Inference caching & sublinear local retrieval.
- **Right Column — 2 AM Incident Runbook & Kill Switch**:
  - *1. Detect*: Monitoring alert triggers when error rate \(> 1\%\) or PII detected.
  - *2. Contain (Kill Switch)*: Any engineer sets `CONFIDENCE_THRESHOLD=1.00` via API/env. Automated answers cease instantly; all tickets fail closed to human agents.
  - *3. Assess*: Query SQLite `decisions.db` to inspect decision IDs and inputs.
  - *4. Notify*: Alert Head of Support and Security within 30 minutes.
  - *5. Remediate & Review*: Deploy hotfix to KB or guardrails; post-mortem in 48h.
- **Speaker Cue**: Screen share (Minutes 17:00 – 18:00).

---

### Slide 11: The Compulsory Requirements Revision (09. Revision Log)
- **Header**: The Compulsory Requirements Revision
- **Card 1 — Revision 1 (Autonomous Bot -> Agent-Assist Boundary)**:
  - *Initial Assumption*: System should autonomously send replies via live chat.
  - *Build Evidence*: Legal & financial liability of unreviewed advice on enterprise infrastructure is unacceptable.
  - *Decision*: Implemented agent-assist boundary with mandatory `[Machine-Drafted]` disclosures.
- **Card 2 — Revision 2 (Remote API Dependency -> Hybrid Local Fallback)**:
  - *Initial Assumption*: All classification and drafting would call remote LLM API endpoints.
  - *Build Evidence*: Free-tier rate limits (15–20 req/min) caused batch timeouts on 500 tickets.
  - *Decision*: Built hybrid engine with local calibrated classifier & caching, guaranteeing sub-second execution (A11).
- **Card 3 — Revision 3 (Open Corpus -> Strict 29-Article KB Isolation)**:
  - *Initial Assumption*: Historic agent replies and personal cheat-sheets could enrich retrieval.
  - *Build Evidence*: Personal cheat-sheets contained obsolete commands and unauthorized refund promises.
  - *Decision*: Strict boundary isolating retrieval exclusively to the 29 reviewed articles.
- **Speaker Cue**: Screen share (Minutes 18:00 – 19:00).

---

### Slide 12: Production Roadmap & Closing (Dark Navy Background)
- **Top Tag**: NEXT STEPS & PRODUCTION ROLLOUT
- **Headline**: **From Capstone to Production Deployment**
- **Roadmap Items**:
  - *1. 2-Week Shadow Pilot*: Run alongside tier-one agents to measure real draft acceptance rates.
  - *2. Dynamic KB Embeddings*: Endpoint for Technical Writer (Ines) to re-index docs on publish.
  - *3. Live Telemetry*: Connect Prometheus metrics endpoint (port 8001) to live Grafana dashboards.
  - *Core Takeaway*: Delivering what the client needed—grounded, reliable support—rather than the chatbot they asked for.
- **Closing**: Thank you! | Questions & Discussion
- **Speaker Cue**: Switch camera back to presenter (Minutes 19:00 – 20:00).
