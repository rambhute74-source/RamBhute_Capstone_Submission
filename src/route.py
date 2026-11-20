"""
src/route.py
Applies deterministic safety gates and calibrated thresholds to route tickets
to auto_respond or escalate.
Meets Acceptance Criterion A5 and Functional Requirements FR-04 and FR-05.
"""

import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from src.classify import ClassificationResult, PROTECTED_INTENTS
from src.guardrails import GuardrailCheckResult
from src.retrieve import RetrievedSource

load_dotenv()


class EscalationBrief(BaseModel):
    ticket_id: str
    summary: str
    proposed_intent: str
    urgency: str
    retrieved_sources: List[str]
    checks_attempted: List[str]
    missing_information: str
    escalation_reason: str


class RoutingDecision(BaseModel):
    action: str  # "auto_respond" | "escalate" | "block"
    confidence: float
    threshold_applied: float
    reason: str
    escalation_brief: Optional[EscalationBrief] = None
    is_deterministic: bool = True


class Router:
    """
    Deterministic routing engine.
    Given the same inputs, it produces the exact same routing decision.
    """

    def __init__(self, confidence_threshold: Optional[float] = None):
        load_dotenv()
        env_thresh = os.getenv("CONFIDENCE_THRESHOLD")
        if confidence_threshold is not None:
            self.threshold = float(confidence_threshold)
        elif env_thresh:
            try:
                self.threshold = float(env_thresh)
            except ValueError:
                self.threshold = 0.80
        else:
            self.threshold = 0.80

    def route(
        self,
        ticket_id: str,
        classification: ClassificationResult,
        retrieved_sources: List[RetrievedSource],
        inbound_guard: GuardrailCheckResult,
        outbound_guard: Optional[GuardrailCheckResult] = None,
        must_not_auto_respond: bool = False,
    ) -> RoutingDecision:
        """
        Determines routing decision with deterministic fail-closed safety logic.
        """
        checks_attempted = [
            f"Classified intent as '{classification.intent}' (confidence: {classification.intent_confidence:.2f})",
            f"Evaluated urgency as '{classification.urgency}'",
            f"Inbound guardrail result: {'pass' if inbound_guard.passed else 'fail'}",
        ]
        if retrieved_sources:
            checks_attempted.append(
                f"Retrieved {len(retrieved_sources)} approved articles: {', '.join([s.doc_id for s in retrieved_sources[:3]])}"
            )
        else:
            checks_attempted.append("Retrieved 0 approved articles matching threshold")

        # 1. Inbound Guardrail Trigger (PII / Injection)
        if inbound_guard.blocked:
            reason = f"Blocked by inbound guardrail: {inbound_guard.details}"
            brief = EscalationBrief(
                ticket_id=ticket_id,
                summary=classification.concise_summary,
                proposed_intent=classification.intent,
                urgency="high",
                retrieved_sources=[s.doc_id for s in retrieved_sources],
                checks_attempted=checks_attempted,
                missing_information="Security/Privacy audit required",
                escalation_reason=reason,
            )
            return RoutingDecision(
                action="block",
                confidence=classification.intent_confidence,
                threshold_applied=self.threshold,
                reason=reason,
                escalation_brief=brief,
            )

        # 2. Protected Category / Must Not Auto Respond
        if must_not_auto_respond or classification.intent in PROTECTED_INTENTS:
            reason = (
                f"Policy constraint: Intent '{classification.intent}' is a protected domain "
                "(security, compliance, billing dispute, or unanswerable request) requiring human engineer."
            )
            brief = EscalationBrief(
                ticket_id=ticket_id,
                summary=classification.concise_summary,
                proposed_intent=classification.intent,
                urgency=classification.urgency,
                retrieved_sources=[s.doc_id for s in retrieved_sources],
                checks_attempted=checks_attempted,
                missing_information="Human expert analysis required",
                escalation_reason=reason,
            )
            return RoutingDecision(
                action="escalate",
                confidence=classification.intent_confidence,
                threshold_applied=self.threshold,
                reason=reason,
                escalation_brief=brief,
            )

        # 3. Low Confidence
        if classification.intent_confidence < self.threshold:
            reason = (
                f"Confidence floor not met: Intent confidence {classification.intent_confidence:.2f} "
                f"is below calibrated threshold {self.threshold:.2f}."
            )
            brief = EscalationBrief(
                ticket_id=ticket_id,
                summary=classification.concise_summary,
                proposed_intent=classification.intent,
                urgency=classification.urgency,
                retrieved_sources=[s.doc_id for s in retrieved_sources],
                checks_attempted=checks_attempted,
                missing_information="Agent confirmation of ambiguous request",
                escalation_reason=reason,
            )
            return RoutingDecision(
                action="escalate",
                confidence=classification.intent_confidence,
                threshold_applied=self.threshold,
                reason=reason,
                escalation_brief=brief,
            )

        # 4. No Grounding Sources
        if not retrieved_sources:
            reason = "No relevant approved documentation passages retrieved above relevance threshold."
            brief = EscalationBrief(
                ticket_id=ticket_id,
                summary=classification.concise_summary,
                proposed_intent=classification.intent,
                urgency=classification.urgency,
                retrieved_sources=[],
                checks_attempted=checks_attempted,
                missing_information="Approved KB article missing or unindexed",
                escalation_reason=reason,
            )
            return RoutingDecision(
                action="escalate",
                confidence=classification.intent_confidence,
                threshold_applied=self.threshold,
                reason=reason,
                escalation_brief=brief,
            )

        # 5. Outbound Guardrail Trigger
        if outbound_guard and outbound_guard.blocked:
            reason = f"Outbound guardrail blocked response draft: {outbound_guard.details}"
            brief = EscalationBrief(
                ticket_id=ticket_id,
                summary=classification.concise_summary,
                proposed_intent=classification.intent,
                urgency=classification.urgency,
                retrieved_sources=[s.doc_id for s in retrieved_sources],
                checks_attempted=checks_attempted,
                missing_information="Correction of draft claims required",
                escalation_reason=reason,
            )
            return RoutingDecision(
                action="escalate",
                confidence=classification.intent_confidence,
                threshold_applied=self.threshold,
                reason=reason,
                escalation_brief=brief,
            )

        # 6. Eligible for Automated Draft
        reason = (
            f"Confidence {classification.intent_confidence:.2f} >= {self.threshold:.2f}, "
            f"grounded in [{retrieved_sources[0].doc_id}], intent '{classification.intent}' is eligible for auto-drafting."
        )
        return RoutingDecision(
            action="auto_respond",
            confidence=classification.intent_confidence,
            threshold_applied=self.threshold,
            reason=reason,
            escalation_brief=None,
        )
