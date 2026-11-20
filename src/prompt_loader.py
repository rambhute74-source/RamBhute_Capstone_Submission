"""
CloudServe Prompt Registry & Dynamic Runtime Loader
Connects the runtime pipeline directly to the versioned prompt files in `prompts/`.
Guarantees that files in `prompts/` are the active single source of truth, not dummy files.
"""

import os
import re
from typing import Dict, Any, List, Optional

PROMPTS_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "prompts")
)

PROMPT_FILE_MAP = {
    "SP-01": os.path.join(PROMPTS_ROOT, "specification", "SP-01_requirement_to_technical_specification_generator.txt"),
    "SP-02": os.path.join(PROMPTS_ROOT, "specification", "SP-02_acceptance_criteria_and_test_scenario_generator.txt"),
    "PR-01": os.path.join(PROMPTS_ROOT, "build", "PR-01_ticket_intent__urgency_context_and_uncertainty_classifier.txt"),
    "PR-02": os.path.join(PROMPTS_ROOT, "build", "PR-02_approved_knowledge_base_retrieval_and_evidence_framing.txt"),
    "PR-02b": os.path.join(PROMPTS_ROOT, "build", "PR-02b_query_enhancer.txt"),
    "PR-03": os.path.join(PROMPTS_ROOT, "build", "PR-03_safety_gate_and_human_routing_decision.txt"),
    "PR-04": os.path.join(PROMPTS_ROOT, "build", "PR-04_source_grounded_response_draft_generator.txt"),
    "PR-05": os.path.join(PROMPTS_ROOT, "build", "PR-05_context_rich_escalation_handoff_builder.txt"),
    "PR-06": os.path.join(PROMPTS_ROOT, "build", "PR-06_support_outcome_and_operational_event_summariser.txt"),
    "RV-01": os.path.join(PROMPTS_ROOT, "review", "RV-01_compliance_reviewer.md"),
    "EV-01": os.path.join(PROMPTS_ROOT, "evaluation", "EV-01_grounded_answer_and_citation_quality_evaluator.txt"),
    "EV-02": os.path.join(PROMPTS_ROOT, "evaluation", "EV-02_unsupported_claim_and_safety_boundary_evaluator.txt"),
    "EV-03": os.path.join(PROMPTS_ROOT, "evaluation", "EV-03_segmented_outcome_and_fairness_evaluator.txt"),
}

# Fallback root paths if subfolders are organized differently
FALLBACK_ROOT_MAP = {
    k: os.path.join(PROMPTS_ROOT, os.path.basename(v))
    for k, v in PROMPT_FILE_MAP.items()
}


class PromptRegistry:
    """Manages loading, parsing, and rendering versioned prompt templates from the filesystem."""

    def __init__(self, prompts_dir: Optional[str] = None):
        self.prompts_dir = prompts_dir or PROMPTS_ROOT
        self._cache: Dict[str, str] = {}
        self._metadata_cache: Dict[str, Dict[str, str]] = {}

    def get_prompt_path(self, prompt_id: str) -> str:
        """Resolve absolute file path for a prompt ID."""
        primary = PROMPT_FILE_MAP.get(prompt_id)
        if primary and os.path.exists(primary):
            return primary
        fallback = FALLBACK_ROOT_MAP.get(prompt_id)
        if fallback and os.path.exists(fallback):
            return fallback
        # Search anywhere in prompts_dir
        for root, _, files in os.walk(self.prompts_dir):
            for f in files:
                if f.startswith(prompt_id):
                    return os.path.join(root, f)
        raise FileNotFoundError(f"Prompt file for '{prompt_id}' not found in {self.prompts_dir}")

    def load_prompt_file(self, prompt_id: str) -> str:
        """Load raw prompt file content from disk with caching."""
        if prompt_id in self._cache:
            return self._cache[prompt_id]

        file_path = self.get_prompt_path(prompt_id)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self._cache[prompt_id] = content
        return content

    def get_prompt_text(self, prompt_id: str) -> str:
        """Extract the pure instructions / template text, stripping metadata headers."""
        raw = self.load_prompt_file(prompt_id)
        if "--- PROMPT TEXT ---" in raw:
            parts = raw.split("--- PROMPT TEXT ---", 1)
            return parts[1].strip()
        # If it's a markdown file with ## Prompt Template
        if "## Prompt Template" in raw:
            parts = raw.split("## Prompt Template", 1)
            return parts[1].strip()
        return raw.strip()

    def get_prompt_version(self, prompt_id: str) -> str:
        """Retrieve version string from prompt header."""
        raw = self.load_prompt_file(prompt_id)
        m = re.search(r"Version:\s*([^\n]+)", raw)
        if m:
            return f"{prompt_id} v{m.group(1).strip()}"
        return f"{prompt_id} v1.0"

    # --- Structured Renderers for Runtime Components ---

    def render_pr01_classifier(
        self,
        ticket_body: str,
        channel: str,
        urgency: str = "medium",
        allowed_intents: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Render PR-01 Ticket intent and urgency classifier from prompts/build/PR-01..."""
        import json
        template = self.get_prompt_text("PR-01")
        intents_list = json.dumps(allowed_intents or [])
        meta_str = json.dumps(metadata or {"channel": channel})

        rendered = template.replace("{{TICKET_BODY}}", ticket_body.strip())
        rendered = rendered.replace("{{TICKET_THREAD_OR_EMPTY}}", "")
        rendered = rendered.replace("{{TICKET_METADATA}}", meta_str)
        rendered = rendered.replace("{{SUPPLIED_URGENCY}}", urgency)
        rendered = rendered.replace("{{ALLOWED_INTENTS}}", intents_list)
        rendered = rendered.replace("{{INTENT_TAXONOMY}}", intents_list)
        return rendered

    def render_pr02b_query_enhancer(
        self,
        ticket_body: str,
        channel: str = "email",
        detected_intent: str = "general_inquiry",
    ) -> str:
        """Render PR-02b Search query reformulation prompt from prompts/build/PR-02b_query_enhancer.txt"""
        template = self.get_prompt_text("PR-02b")
        rendered = template.replace("{{TICKET_TEXT}}", ticket_body.strip())
        rendered = rendered.replace("{{TICKET_CHANNEL}}", channel)
        rendered = rendered.replace("{{DETECTED_INTENT}}", detected_intent)
        return rendered

    def render_pr04_draft(
        self,
        ticket_text: str,
        customer_name: str,
        channel: str,
        retrieved_passages: List[Dict[str, Any]],
        intent: str,
        safety_gate_passed: bool = True,
    ) -> str:
        """Render PR-04 Grounded response draft generator from prompts/build/PR-04..."""
        import json
        template = self.get_prompt_text("PR-04")
        passages_str = "\n\n".join(
            [f"[{p.get('doc_id')}] {p.get('title')}:\n{p.get('passage')}" for p in retrieved_passages]
        )
        classifier_json = json.dumps({"intent": intent, "channel": channel, "customer_name": customer_name})
        safety_json = json.dumps({"safety_gate_passed": safety_gate_passed, "action": "ALLOW_DRAFT"})
        style_guide = "Professional, concise, grounded in documentation, cite document IDs explicitly in brackets [DOC-ID]."

        rendered = template.replace("{{TICKET_TEXT_AND_CONTEXT}}", ticket_text.strip())
        rendered = rendered.replace("{{CLASSIFIER_JSON}}", classifier_json)
        rendered = rendered.replace("{{SAFETY_GATE_JSON}}", safety_json)
        rendered = rendered.replace("{{RETRIEVAL_RESULTS}}", passages_str)
        rendered = rendered.replace("{{APPROVED_RESPONSE_STYLE_OR_EMPTY}}", style_guide)
        return rendered

    def render_pr05_escalation(
        self,
        ticket_text: str,
        ticket_id: str,
        channel: str,
        urgency: str,
        intent: str,
        escalation_reason: str,
        retrieved_docs: List[str],
    ) -> str:
        """Render PR-05 Context-rich escalation handoff from prompts/build/PR-05..."""
        import json
        template = self.get_prompt_text("PR-05")
        classifier_json = json.dumps({"intent": intent, "urgency": urgency})
        retrieval_json = json.dumps({"retrieved_docs": retrieved_docs})
        safety_json = json.dumps({"routing": "ESCALATE", "reason": escalation_reason})

        rendered = template.replace("{{ORIGINAL_TICKET_AND_THREAD}}", f"[{ticket_id}] ({channel}): {ticket_text}")
        rendered = rendered.replace("{{CLASSIFIER_JSON}}", classifier_json)
        rendered = rendered.replace("{{RETRIEVAL_JSON}}", retrieval_json)
        rendered = rendered.replace("{{SAFETY_GATE_JSON}}", safety_json)
        rendered = rendered.replace("{{RECORDED_AGENT_ACTIONS}}", "Ingested, classified, evaluated against safety gate")
        rendered = rendered.replace("{{ESCALATION_REASON}}", escalation_reason)
        return rendered


# Global singleton instance for application runtime
prompt_registry = PromptRegistry()
