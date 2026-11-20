# CloudServe Prompt Library & Registry

Welcome to the CloudServe Prompt Engineering & Template Registry. All prompts are extracted directly from the ground-truth specification workbook ([Stage_3_Prompt_Library.docx](../Inputs/03_Workbooks/Stage_3_Prompt_Library.docx)).

> [!NOTE]
> **Prompt Architecture & Design Principles**:
> 1. **Strict Trust Boundaries**: Inputs wrapped in explicit XML tags (e.g. `<ticket_text>`, `<customer_supplied_metadata>`) treat customer inputs as untrusted data, mitigating direct and indirect prompt injection attacks.
> 2. **Agent-Assist Constraint**: All drafting and classification prompts enforce the rule that CloudServe is an agent-assist copilot; no message is transmitted to external customers without explicit human review and sign-off.
> 3. **Structured Outputs**: Every prompt mandates a deterministic JSON schema with typed fields and explicit error/abstention codes.
> 4. **Grounded Retrieval & Citations**: Draft generation strictly prohibits hallucinated assertions, unverified SLA promises, or unsourced troubleshooting steps.

---

## Prompt Registry Index

| Prompt ID | Prompt Name | Serves Requirement | File Reference | Category |
| :--- | :--- | :--- | :--- | :--- |
| `SP-01` | **Requirement-to-Technical-Specification Generator** | `FR-01–FR-08` | [SP-01_requirement_to_technical_specification_generator.txt](specification/SP-01_requirement_to_technical_specification_generator.txt) <br> *([View Markdown](specification/SP-01_specification_generator.md))* | Specification |
| `SP-02` | **Acceptance-Criteria and Test-Scenario Generator** | `FR-01–FR-08` | [SP-02_acceptance_criteria_and_test_scenario_generator.txt](specification/SP-02_acceptance_criteria_and_test_scenario_generator.txt) <br> *([View Markdown](specification/SP-02_test_scenario_generator.md))* | Specification |
| `PR-01` | **Ticket Intent, Urgency Context and Uncertainty Classifier** | `FR-01` | [PR-01_ticket_intent__urgency_context_and_uncertainty_classifier.txt](build/PR-01_ticket_intent__urgency_context_and_uncertainty_classifier.txt) <br> *([View Markdown](build/PR-01_ticket_classifier.md))* | Build |
| `PR-02` | **Approved Knowledge-Base Retrieval and Evidence Framing** | `FR-02, FR-06` | [PR-02_approved_knowledge_base_retrieval_and_evidence_framing.txt](build/PR-02_approved_knowledge_base_retrieval_and_evidence_framing.txt) <br> *([View Markdown](build/PR-02_knowledge_retriever.md))* | Build |
| `PR-02b` | **Search Query Reformulation and Technical Expansion Assistant** | `FR-02, FR-06` | [PR-02b_query_enhancer.txt](build/PR-02b_query_enhancer.txt) <br> *([View Markdown](build/PR-02b_query_enhancer.md))* | Build |
| `PR-03` | **Safety Gate and Human-Routing Decision** | `FR-04` | [PR-03_safety_gate_and_human_routing_decision.txt](build/PR-03_safety_gate_and_human_routing_decision.txt) <br> *([View Markdown](build/PR-03_safety_gate_router.md))* | Build |
| `PR-04` | **Source-Grounded Response Draft Generator** | `` | [PR-04_source_grounded_response_draft_generator.txt](build/PR-04_source_grounded_response_draft_generator.txt) <br> *([View Markdown](build/PR-04_draft_generator.md))* | Build |
| `PR-05` | **Context-Rich Escalation Handoff Builder** | `FR-05` | [PR-05_context_rich_escalation_handoff_builder.txt](build/PR-05_context_rich_escalation_handoff_builder.txt) <br> *([View Markdown](build/PR-05_escalation_handoff.md))* | Build |
| `PR-06` | **Support Outcome and Operational Event Summariser** | `FR-07, FR-08` | [PR-06_support_outcome_and_operational_event_summariser.txt](build/PR-06_support_outcome_and_operational_event_summariser.txt) <br> *([View Markdown](build/PR-06_outcome_summariser.md))* | Build |
| `RV-01` | **Requirement, Prompt and Implementation Compliance Reviewer** | `FR-01–FR-08 and applicable NFRs` | [RV-01_requirement__prompt_and_implementation_compliance_reviewer.txt](evaluation/RV-01_requirement__prompt_and_implementation_compliance_reviewer.txt) <br> *([View Markdown](evaluation/RV-01_compliance_reviewer.md))* | Review |
| `EV-01` | **Grounded Answer and Citation Quality Evaluator** | `FR-02, FR-03, FR-06; NFR-03, NFR-05` | [EV-01_grounded_answer_and_citation_quality_evaluator.txt](evaluation/EV-01_grounded_answer_and_citation_quality_evaluator.txt) <br> *([View Markdown](evaluation/EV-01_grounding_evaluator.md))* | Evaluation |
| `EV-02` | **Unsupported-Claim and Safety Boundary Evaluator** | `FR-03, FR-04, FR-06; NFR-03` | [EV-02_unsupported_claim_and_safety_boundary_evaluator.txt](evaluation/EV-02_unsupported_claim_and_safety_boundary_evaluator.txt) <br> *([View Markdown](evaluation/EV-02_safety_evaluator.md))* | Evaluation |
| `EV-03` | **Segmented Outcome and Fairness Evaluator** | `FR-07, FR-08; NFR-06` | [EV-03_segmented_outcome_and_fairness_evaluator.txt](evaluation/EV-03_segmented_outcome_and_fairness_evaluator.txt) <br> *([View Markdown](evaluation/EV-03_fairness_evaluator.md))* | Evaluation |

---

## Directory Organization

```text
prompts/
├── README.md                      # This master registry index
├── specification/                 # SP-01, SP-02 (Requirements to technical specs and test cases)
│   ├── SP-01_requirement_to_technical_specification_generator.txt
│   ├── SP-01_specification_generator.md
│   ├── SP-02_acceptance_criteria_and_test_scenario_generator.txt
│   └── SP-02_test_scenario_generator.md
├── build/                         # PR-01 to PR-06 (Core runtime pipeline prompts)
│   ├── PR-01_ticket_intent__urgency_context_and_uncertainty_classifier.txt
│   ├── PR-01_ticket_classifier.md
│   ├── PR-02_approved_knowledge_base_retrieval_and_evidence_framing.txt
│   ├── PR-02_knowledge_retriever.md
│   ├── PR-02b_query_enhancer.txt
│   ├── PR-02b_query_enhancer.md
│   ├── PR-03_safety_gate_and_human_routing_decision.txt
│   ├── PR-03_safety_gate_router.md
│   ├── PR-04_source_grounded_response_draft_generator.txt
│   ├── PR-04_draft_generator.md
│   ├── PR-05_context_rich_escalation_handoff_builder.txt
│   ├── PR-05_escalation_handoff.md
│   ├── PR-06_support_outcome_and_operational_event_summariser.txt
│   └── PR-06_outcome_summariser.md
├── evaluation/                    # EV-01 to EV-03, RV-01 (Quality, safety, fairness & compliance)
│   ├── EV-01_grounded_answer_and_citation_quality_evaluator.txt
│   ├── EV-01_grounding_evaluator.md
│   ├── EV-02_unsupported_claim_and_safety_boundary_evaluator.txt
│   ├── EV-02_safety_evaluator.md
│   ├── EV-03_segmented_outcome_and_fairness_evaluator.txt
│   ├── EV-03_fairness_evaluator.md
│   ├── RV-01_requirement__prompt_and_implementation_compliance_reviewer.txt
│   └── RV-01_compliance_reviewer.md
└── review/                        # Dedicated review category mirror
    └── RV-01_compliance_reviewer.md
```

---

## Model Selection & Unpinned Model Fields

In `Stage_3_Prompt_Library.docx`, the `Model used` metadata row was left unpinned/blank (`['Model used', '']`). This was by design in the Stage 3 Specification so that:
- Prompts remain model-agnostic and portable across frontier LLMs (e.g., Anthropic Claude 3.5 Sonnet, Google Gemini 2.5 Flash / Pro, OpenAI GPT-4o).
- In local development and batch offline evaluation, the pipeline operates with deterministic, calibrated machine learning engines (calibrated TF-IDF + Logistic Regression classifiers and n-gram BM25 cosine retrievers) providing sub-second latency and zero API dependency.
- In production, the pipeline connects dynamically via the OpenRouter API (`OPENROUTER_API_KEY`) to any configured frontier model without requiring prompt modification.
