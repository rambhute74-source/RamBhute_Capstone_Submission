import os
import docx

doc_path = r"C:\Users\user\Desktop\CloudeVerseProject\Inputs\03_Workbooks\Stage_3_Prompt_Library.docx"
base_dir = r"C:\Users\user\Desktop\CloudeVerseProject\prompts"

doc = docx.Document(doc_path)

# Prompt metadata mapping
PROMPTS = [
    {
        "id": "SP-01",
        "name": "Requirement-to-Technical-Specification Generator",
        "category": "specification",
        "meta_table_idx": 3,
        "text_table_idx": 4,
        "long_filename": "SP-01_requirement_to_technical_specification_generator.txt",
        "short_filename": "SP-01_specification_generator.md",
        "subfolder": "specification"
    },
    {
        "id": "SP-02",
        "name": "Acceptance-Criteria and Test-Scenario Generator",
        "category": "specification",
        "meta_table_idx": 5,
        "text_table_idx": 6,
        "long_filename": "SP-02_acceptance_criteria_and_test_scenario_generator.txt",
        "short_filename": "SP-02_test_scenario_generator.md",
        "subfolder": "specification"
    },
    {
        "id": "PR-01",
        "name": "Ticket Intent, Urgency Context and Uncertainty Classifier",
        "category": "build",
        "meta_table_idx": 7,
        "text_table_idx": 8,
        "long_filename": "PR-01_ticket_intent__urgency_context_and_uncertainty_classifier.txt",
        "short_filename": "PR-01_ticket_classifier.md",
        "subfolder": "build"
    },
    {
        "id": "PR-02",
        "name": "Approved Knowledge-Base Retrieval and Evidence Framing",
        "category": "build",
        "meta_table_idx": 9,
        "text_table_idx": 10,
        "long_filename": "PR-02_approved_knowledge_base_retrieval_and_evidence_framing.txt",
        "short_filename": "PR-02_knowledge_retriever.md",
        "subfolder": "build"
    },
    {
        "id": "PR-03",
        "name": "Safety Gate and Human-Routing Decision",
        "category": "build",
        "meta_table_idx": 11,
        "text_table_idx": 12,
        "long_filename": "PR-03_safety_gate_and_human_routing_decision.txt",
        "short_filename": "PR-03_safety_gate_router.md",
        "subfolder": "build"
    },
    {
        "id": "PR-04",
        "name": "Source-Grounded Response Draft Generator",
        "category": "build",
        "meta_table_idx": 13,
        "text_table_idx": 14,
        "long_filename": "PR-04_source_grounded_response_draft_generator.txt",
        "short_filename": "PR-04_draft_generator.md",
        "subfolder": "build"
    },
    {
        "id": "PR-05",
        "name": "Context-Rich Escalation Handoff Builder",
        "category": "build",
        "meta_table_idx": 15,
        "text_table_idx": 16,
        "long_filename": "PR-05_context_rich_escalation_handoff_builder.txt",
        "short_filename": "PR-05_escalation_handoff.md",
        "subfolder": "build"
    },
    {
        "id": "PR-06",
        "name": "Support Outcome and Operational Event Summariser",
        "category": "build",
        "meta_table_idx": 17,
        "text_table_idx": 18,
        "long_filename": "PR-06_support_outcome_and_operational_event_summariser.txt",
        "short_filename": "PR-06_outcome_summariser.md",
        "subfolder": "build"
    },
    {
        "id": "RV-01",
        "name": "Requirement, Prompt and Implementation Compliance Reviewer",
        "category": "review",
        "meta_table_idx": 19,
        "text_table_idx": 20,
        "long_filename": "RV-01_requirement__prompt_and_implementation_compliance_reviewer.txt",
        "short_filename": "RV-01_compliance_reviewer.md",
        "subfolder": "evaluation" # keep in evaluation for compat, also review
    },
    {
        "id": "EV-01",
        "name": "Grounded Answer and Citation Quality Evaluator",
        "category": "evaluation",
        "meta_table_idx": 21,
        "text_table_idx": 22,
        "long_filename": "EV-01_grounded_answer_and_citation_quality_evaluator.txt",
        "short_filename": "EV-01_grounding_evaluator.md",
        "subfolder": "evaluation"
    },
    {
        "id": "EV-02",
        "name": "Unsupported-Claim and Safety Boundary Evaluator",
        "category": "evaluation",
        "meta_table_idx": 23,
        "text_table_idx": 24,
        "long_filename": "EV-02_unsupported_claim_and_safety_boundary_evaluator.txt",
        "short_filename": "EV-02_safety_evaluator.md",
        "subfolder": "evaluation"
    },
    {
        "id": "EV-03",
        "name": "Segmented Outcome and Fairness Evaluator",
        "category": "evaluation",
        "meta_table_idx": 25,
        "text_table_idx": 26,
        "long_filename": "EV-03_segmented_outcome_and_fairness_evaluator.txt",
        "short_filename": "EV-03_fairness_evaluator.md",
        "subfolder": "evaluation"
    }
]

# Ensure subdirectories exist
for sub in ["specification", "build", "evaluation", "review"]:
    os.makedirs(os.path.join(base_dir, sub), exist_ok=True)

readme_rows = []

for item in PROMPTS:
    meta_t = doc.tables[item["meta_table_idx"]]
    text_t = doc.tables[item["text_table_idx"]]
    
    meta = {r.cells[0].text.strip(): r.cells[1].text.strip() for r in meta_t.rows if len(r.cells) >= 2}
    
    prompt_text = ""
    if len(text_t.rows) > 1 and len(text_t.rows[1].cells) > 0:
        prompt_text = text_t.rows[1].cells[0].text.strip()
        
    serves = meta.get("Serves requirement", "N/A")
    category = meta.get("Category", item["category"].capitalize())
    version = meta.get("Version", "1.0")
    model_used = meta.get("Model used", "Model-Agnostic / Configured LLM (e.g., google/gemini-2.5-flash or anthropic/claude-3.5-sonnet via OpenRouter)")
    if not model_used.strip():
        model_used = "Configured OpenRouter / Fallback Engine (Model-Agnostic)"
    inputs_exp = meta.get("Inputs it expects", "")
    output_fmt = meta.get("Output format required", "")
    known_weakness = meta.get("Known weaknesses", "")
    
    # 1. Plain text format (preserving lines)
    plain_content = f"# {item['id']} - {item['name']}\n\n"
    plain_content += f"Metadata:\n"
    plain_content += f"- ID: {item['id']}\n"
    plain_content += f"- Category: {category}\n"
    plain_content += f"- Serves: {serves}\n"
    plain_content += f"- Version: {version}\n"
    plain_content += f"- Model: {model_used}\n\n"
    plain_content += f"--- PROMPT TEXT ---\n\n"
    plain_content += prompt_text + "\n"
    
    # 2. Markdown format (rich formatting)
    md_content = f"# {item['id']}: {item['name']}\n\n"
    md_content += f"| Metadata Attribute | Value |\n"
    md_content += f"| :--- | :--- |\n"
    md_content += f"| **Prompt ID** | `{item['id']}` |\n"
    md_content += f"| **Category** | {category} |\n"
    md_content += f"| **Serves Requirement** | {serves} |\n"
    md_content += f"| **Version** | {version} |\n"
    md_content += f"| **Target Model** | {model_used} |\n"
    md_content += f"| **Inputs Expected** | {inputs_exp} |\n"
    md_content += f"| **Output Format** | {output_fmt} |\n"
    if known_weakness:
        md_content += f"| **Known Weaknesses** | {known_weakness} |\n"
    md_content += f"\n---\n\n"
    md_content += f"## Prompt Template\n\n"
    
    # Format the prompt text nicely into markdown sections
    # Replace JSON blocks with ```json code blocks
    lines = prompt_text.splitlines()
    in_json = False
    json_lines = []
    
    formatted_body = []
    for line in lines:
        stripped = line.strip()
        if stripped in ["ROLE", "TASK", "TRUST BOUNDARY", "INPUTS", "RULES", "OUTPUT", "CRITERIA", "EVALUATION CRITERIA"]:
            if in_json:
                formatted_body.append("```json\n" + "\n".join(json_lines) + "\n```\n")
                json_lines = []
                in_json = False
            formatted_body.append(f"\n### {stripped}\n")
        elif stripped.startswith("{") and not in_json:
            in_json = True
            json_lines.append(line)
        elif in_json:
            json_lines.append(line)
            if stripped.startswith("}"):
                formatted_body.append("```json\n" + "\n".join(json_lines) + "\n```\n")
                json_lines = []
                in_json = False
        else:
            formatted_body.append(line)
            
    if in_json and json_lines:
        formatted_body.append("```json\n" + "\n".join(json_lines) + "\n```\n")
        
    md_content += "\n".join(formatted_body).strip() + "\n"
    
    # Save target files
    # Target 1: Exact original path in subfolder (e.g. prompts/build/PR-01_...txt)
    target_sub_txt = os.path.join(base_dir, item["subfolder"], item["long_filename"])
    with open(target_sub_txt, "w", encoding="utf-8") as f:
        f.write(plain_content)
        
    # Target 2: Root copy of long_filename (for flat lookup / backward compat)
    target_root_txt = os.path.join(base_dir, item["long_filename"])
    with open(target_root_txt, "w", encoding="utf-8") as f:
        f.write(plain_content)
        
    # Target 3: Short named .md file in subfolder
    target_sub_md = os.path.join(base_dir, item["subfolder"], item["short_filename"])
    with open(target_sub_md, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    # Target 4: If category is review, also place in review/
    if item["category"] == "review":
        target_rev_md = os.path.join(base_dir, "review", item["short_filename"])
        with open(target_rev_md, "w", encoding="utf-8") as f:
            f.write(md_content)
            
    # Add to README table
    rel_path_txt = f"{item['subfolder']}/{item['long_filename']}"
    rel_path_md = f"{item['subfolder']}/{item['short_filename']}"
    readme_rows.append(
        f"| `{item['id']}` | **{item['name']}** | `{serves}` | [{item['long_filename']}]({rel_path_txt}) <br> *([View Markdown]({rel_path_md}))* | {category} |"
    )

# Write master README.md
readme_content = f"""# CloudServe Prompt Library & Registry

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
""" + "\n".join(readme_rows) + """

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
"""

with open(os.path.join(base_dir, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

print("Clean prompt generation complete!")
