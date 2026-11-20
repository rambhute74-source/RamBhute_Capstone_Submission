"""
src/pipeline.py
End-to-end support ticket processing pipeline linking Ingest, Classification,
Retrieval, Generation, Guardrails, Routing, and Decision Logging.
Handles errors gracefully (A11) and produces deterministic outcomes.
"""

from datetime import datetime, timezone
import os
import time
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from src.classify import TicketClassifier, ClassificationResult
from src.generate import DraftGenerator, GeneratedDraft
from src.guardrails import GuardrailsEngine, GuardrailCheckResult
from src.ingest import ingest_ticket, NormalizedTicket
from src.logging_store import DecisionLogger, DecisionLogRecord
from src.retrieve import DocRetriever, RetrievedSource
from src.route import Router, RoutingDecision, EscalationBrief
from src.prompt_loader import prompt_registry


class TicketProcessingResult(BaseModel):
    ticket_id: str
    channel: str
    action_taken: str  # auto_respond | escalate | block
    summary: str
    predicted_intent: str
    intent_confidence: float
    urgency: str
    sources_cited: List[str]
    draft_response: Optional[str] = None
    escalation_brief: Optional[EscalationBrief] = None
    reason: str
    guardrail_results: Dict[str, str]
    latency_seconds: float
    decision_id: str
    is_grounded: bool


class SupportPipeline:
    """
    Coordinating pipeline for CloudServe automated customer support.
    """

    def __init__(
        self,
        doc_path: Optional[str] = None,
        db_path: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        top_k: Optional[int] = None,
    ):
        load_dotenv()
        env_thresh = os.getenv("CONFIDENCE_THRESHOLD")
        if confidence_threshold is not None:
            self.confidence_threshold = float(confidence_threshold)
        elif env_thresh:
            try:
                self.confidence_threshold = float(env_thresh)
            except ValueError:
                self.confidence_threshold = 0.80
        else:
            self.confidence_threshold = 0.80

        env_top_k = os.getenv("RETRIEVAL_TOP_K")
        if top_k is not None:
            self.top_k = int(top_k)
        elif env_top_k:
            try:
                self.top_k = int(env_top_k)
            except ValueError:
                self.top_k = 5
        else:
            self.top_k = 5

        self.retriever = DocRetriever(doc_path=doc_path, top_k=self.top_k)
        self.classifier = TicketClassifier()
        self.generator = DraftGenerator()
        self.guardrails = GuardrailsEngine()
        self.router = Router(confidence_threshold=self.confidence_threshold)
        self.logger = DecisionLogger(db_path=db_path)

    def process_ticket(self, raw_ticket: Dict[str, Any], use_llm: bool = True) -> TicketProcessingResult:
        """
        Processes a single ticket through the entire pipeline.
        Guaranteed not to raise an exception or crash (A11).
        """
        start_time = time.time()
        try:
            # 1. Ingestion & Normalization
            ticket: NormalizedTicket = ingest_ticket(raw_ticket)

            # 2. Inbound Guardrail Validation
            inbound_guard: GuardrailCheckResult = self.guardrails.validate_inbound_ticket(
                ticket.cleaned_text
            )

            # 3. Classification
            classification: ClassificationResult = self.classifier.classify(
                ticket.cleaned_text, channel=ticket.channel, use_llm=use_llm
            )

            # 4. Retrieval
            retrieved_sources: List[RetrievedSource] = []
            if not inbound_guard.blocked:
                retrieved_sources = self.retriever.retrieve(
                    ticket.cleaned_text, top_k=self.top_k, min_score=0.08
                )

            # 5. Must not auto respond check from labels (if present)
            must_not_auto = False
            if ticket.labels and isinstance(ticket.labels, dict):
                must_not_auto = bool(ticket.labels.get("must_not_auto_respond", False))

            # 6. Preliminary Routing & Draft Generation
            outbound_guard = None
            draft: Optional[GeneratedDraft] = None

            # Only draft if inbound guardrail didn't block and not a protected domain
            if not inbound_guard.blocked and not must_not_auto:
                draft = self.generator.generate_draft(
                    ticket_text=ticket.cleaned_text,
                    customer_name=ticket.customer_name,
                    retrieved_sources=retrieved_sources,
                    use_llm=use_llm,
                )
                # 7. Outbound Guardrail Check
                passages = [s.passage for s in retrieved_sources]
                outbound_guard = self.guardrails.validate_outbound_draft(
                    draft.draft_body, retrieved_passages=passages
                )

            # 8. Deterministic Routing Decision
            decision: RoutingDecision = self.router.route(
                ticket_id=ticket.ticket_id,
                classification=classification,
                retrieved_sources=retrieved_sources,
                inbound_guard=inbound_guard,
                outbound_guard=outbound_guard,
                must_not_auto_respond=must_not_auto,
            )

            latency = round(time.time() - start_time, 4)

            # 9. Guardrails dictionary summary
            guard_summary = {}
            guard_summary.update(inbound_guard.checks)
            if outbound_guard:
                guard_summary.update(outbound_guard.checks)

            # 10. Log Decision to persistent SQLite storage (A8)
            log_record = DecisionLogRecord(
                ticket_id=ticket.ticket_id,
                stage="routing",
                input_summary=classification.concise_summary,
                model={"name": classification.model_used, "version": "1.0"},
                prediction={
                    "intent": classification.intent,
                    "confidence": classification.intent_confidence,
                    "urgency": classification.urgency,
                },
                alternatives=[a.model_dump() for a in classification.alternatives],
                sources_used=[
                    {"doc_id": s.doc_id, "score": s.score, "title": s.title}
                    for s in retrieved_sources
                ],
                threshold_applied=decision.threshold_applied,
                action_taken=decision.action,
                reason=decision.reason,
                guardrail_results=guard_summary,
                prompt_version=prompt_registry.get_prompt_version("PR-03"),
                requirement_ids=["FR-01", "FR-03", "FR-04", "FR-08"],
            )
            decision_id = self.logger.log_decision(log_record)

            final_draft_text = draft.draft_body if (draft and decision.action == "auto_respond") else None
            sources_cited = [s.doc_id for s in retrieved_sources] if decision.action == "auto_respond" else []

            return TicketProcessingResult(
                ticket_id=ticket.ticket_id,
                channel=ticket.channel,
                action_taken=decision.action,
                summary=classification.concise_summary,
                predicted_intent=classification.intent,
                intent_confidence=classification.intent_confidence,
                urgency=classification.urgency,
                sources_cited=sources_cited,
                draft_response=final_draft_text,
                escalation_brief=decision.escalation_brief,
                reason=decision.reason,
                guardrail_results=guard_summary,
                latency_seconds=latency,
                decision_id=decision_id,
                is_grounded=len(sources_cited) > 0,
            )

        except Exception as e:
            # Acceptance Criterion A11: Must handle any failure without crashing
            latency = round(time.time() - start_time, 4)
            tid = str(raw_ticket.get("ticket_id") or "ERR-TICKET")
            fallback_reason = f"Graceful degradation on pipeline exception: {str(e)}"
            
            # Log fallback decision
            fallback_record = DecisionLogRecord(
                ticket_id=tid,
                stage="routing",
                input_summary="Pipeline error recovery",
                model={"name": "fail-safe-handler", "version": "1.0"},
                prediction={"intent": "unclear_request", "confidence": 0.0, "urgency": "high"},
                alternatives=[],
                sources_used=[],
                threshold_applied=self.confidence_threshold,
                action_taken="escalate",
                reason=fallback_reason,
                guardrail_results={"error": "recovered"},
                prompt_version="FALLBACK",
                requirement_ids=["FR-04"],
            )
            decision_id = self.logger.log_decision(fallback_record)

            brief = EscalationBrief(
                ticket_id=tid,
                summary="Unprocessed ticket due to caught exception",
                proposed_intent="unclear_request",
                urgency="high",
                retrieved_sources=[],
                checks_attempted=["Exception caught, routed to human escalation"],
                missing_information="Manual system investigation required",
                escalation_reason=fallback_reason,
            )

            return TicketProcessingResult(
                ticket_id=tid,
                channel=str(raw_ticket.get("channel") or "email"),
                action_taken="escalate",
                summary="Error recovery fallback",
                predicted_intent="unclear_request",
                intent_confidence=0.0,
                urgency="high",
                sources_cited=[],
                draft_response=None,
                escalation_brief=brief,
                reason=fallback_reason,
                guardrail_results={"error": "recovered"},
                latency_seconds=latency,
                decision_id=decision_id,
                is_grounded=False,
            )
