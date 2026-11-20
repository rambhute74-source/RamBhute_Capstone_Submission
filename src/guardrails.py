"""
src/guardrails.py
Safety gate and guardrails validating responses for PII, prompt injection,
unsupported claims, and out-of-scope commitments.
Meets Acceptance Criterion A7 and Functional Requirement FR-04.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GuardrailCheckResult(BaseModel):
    passed: bool
    blocked: bool
    trigger_type: Optional[str] = None  # pii, injection, unsupported_claim, scope_violation
    details: str
    checks: Dict[str, str] = Field(default_factory=dict)  # check_name -> "pass" | "fail"


class GuardrailsEngine:
    """
    Evaluates text and draft responses against strict safety policies.
    Can actively BLOCK responses, failing closed.
    """

    # Regex patterns for private sensitive data (PII)
    PII_PATTERNS = {
        "api_key": r"(?:sk-[a-zA-Z0-9_\-]{20,}|ghp_[a-zA-Z0-9]{36}|bearer\s+[a-zA-Z0-9_\-\.]{20,})",
        "credit_card": r"\b(?:\d{4}[ -]?){3}\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "password": r"(?:password|passwd|pwd)\s*[:=]\s*[^\s]+",
        "aws_secret": r"(?:aws_secret_access_key|access_token)\s*[:=]\s*[A-Za-z0-9/+=]{20,}",
    }

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"disregard\s+(?:all\s+)?prior\s+instructions",
        r"system\s*prompt",
        r"you\s+are\s+now\s+(?:DAN|an\s+unrestricted)",
        r"reveal\s+(?:your\s+)?(?:secret|api\s*key|token|instructions)",
        r"override\s+safety\s+checks",
        r"bypass\s+all\s+guardrails",
    ]

    # Prohibited claims (must_not_claim rules from senior agents)
    FORBIDDEN_CLAIMS = [
        r"refund\s+(?:has\s+been|will\s+be)\s+issued",
        r"credit\s+(?:has\s+been|will\s+be)\s+applied\s+to\s+your\s+account",
        r"guarantee(?:d)?\s+resolution\s+within",
        r"we\s+can\s+manually\s+move\s+your\s+data\s+to\s+another\s+region",
        r"the\s+bug\s+will\s+be\s+fixed\s+by\s+(?:tomorrow|next\s+week)",
        r"compensation\s+will\s+be\s+provided",
    ]

    def check_pii(self, text: str) -> Optional[str]:
        """Check for presence of sensitive personal data or credentials."""
        for name, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return f"Detected potential {name}"
        return None

    def check_injection(self, text: str) -> Optional[str]:
        """Check for adversarial prompt injection attempts."""
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return f"Detected adversarial prompt injection attempt: '{pattern}'"
        return None

    def check_unsupported_claims(self, text: str) -> Optional[str]:
        """Check for prohibited claims or unverified financial/timeline commitments."""
        for pattern in self.FORBIDDEN_CLAIMS:
            if re.search(pattern, text, re.IGNORECASE):
                return f"Draft contains prohibited commitment/unsupported claim: '{pattern}'"
        return None

    def validate_inbound_ticket(self, text: str) -> GuardrailCheckResult:
        """Runs checks on inbound customer text."""
        checks = {"pii": "pass", "injection": "pass"}
        
        injection_issue = self.check_injection(text)
        if injection_issue:
            checks["injection"] = "fail"
            return GuardrailCheckResult(
                passed=False,
                blocked=True,
                trigger_type="injection",
                details=injection_issue,
                checks=checks,
            )

        pii_issue = self.check_pii(text)
        if pii_issue:
            checks["pii"] = "fail"
            return GuardrailCheckResult(
                passed=False,
                blocked=True,
                trigger_type="pii",
                details=pii_issue,
                checks=checks,
            )

        return GuardrailCheckResult(
            passed=True,
            blocked=False,
            details="Inbound text passed safety guardrails.",
            checks=checks,
        )

    def validate_outbound_draft(
        self, draft_text: str, retrieved_passages: List[str]
    ) -> GuardrailCheckResult:
        """
        Runs comprehensive checks on outbound drafts before release.
        Blocks any response leaking PII, making unauthorized promises, or failing grounding.
        """
        checks = {
            "pii": "pass",
            "unsupported_claim": "pass",
            "grounding": "pass",
        }

        # Check PII in outbound
        pii_issue = self.check_pii(draft_text)
        if pii_issue:
            checks["pii"] = "fail"
            return GuardrailCheckResult(
                passed=False,
                blocked=True,
                trigger_type="pii",
                details=f"Outbound draft contains private data: {pii_issue}",
                checks=checks,
            )

        # Check unsupported claims
        claim_issue = self.check_unsupported_claims(draft_text)
        if claim_issue:
            checks["unsupported_claim"] = "fail"
            return GuardrailCheckResult(
                passed=False,
                blocked=True,
                trigger_type="unsupported_claim",
                details=claim_issue,
                checks=checks,
            )

        # Basic grounding check: draft must not be completely disconnected from passages
        if retrieved_passages:
            combined_context = " ".join(retrieved_passages).lower()
            # If draft claims specific instructions not anywhere in retrieved context
            words = [w for w in re.findall(r"\w{5,}", draft_text.lower()) if w not in {"cloudserve", "support", "document", "please", "thanks", "contact", "regards"}]
            matched_words = [w for w in words if w in combined_context]
            if len(words) >= 5 and len(matched_words) / len(words) < 0.15:
                checks["grounding"] = "fail"
                return GuardrailCheckResult(
                    passed=False,
                    blocked=True,
                    trigger_type="unsupported_claim",
                    details="Draft content is not grounded in retrieved documentation passages.",
                    checks=checks,
                )

        return GuardrailCheckResult(
            passed=True,
            blocked=False,
            details="Outbound draft verified by all guardrails.",
            checks=checks,
        )
