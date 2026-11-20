"""
src/ingest.py
Normalise support tickets from all four channels (email, chat, docs_comment, forum)
into a unified internal representation.
Meets Acceptance Criterion A2 and Functional Requirement FR-01.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NormalizedTicket(BaseModel):
    ticket_id: str
    channel: str  # email, chat, docs_comment, forum
    subject: str = ""
    body: str
    cleaned_text: str
    received_at: str
    customer_id: str = "UNKNOWN"
    customer_name: str = "Anonymous"
    customer_tier: str = "standard"  # enterprise, business, standard
    customer_region: str = "north_america"  # north_america, europe, asia_pacific, latin_america
    language_fluency: str = "fluent"  # fluent, non_fluent
    labels: Optional[Dict[str, Any]] = None
    history: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


def normalize_channel(channel: Optional[str]) -> str:
    """Normalize and validate incoming channel string."""
    if not channel:
        return "email"
    c = str(channel).strip().lower()
    mapping = {
        "email": "email",
        "mail": "email",
        "chat": "chat",
        "livechat": "chat",
        "live_chat": "chat",
        "docs_comment": "docs_comment",
        "docs": "docs_comment",
        "documentation": "docs_comment",
        "forum": "forum",
        "community": "forum",
        "community_forum": "forum",
    }
    return mapping.get(c, "email")


def clean_ticket_body(body: Optional[str], subject: Optional[str] = "") -> str:
    """Clean and combine subject + body into normalized textual input."""
    b = (body or "").strip()
    s = (subject or "").strip()
    if s and b:
        # If body doesn't start with subject, prepend it
        if not b.lower().startswith(s.lower()):
            return f"{s}\n\n{b}"
    return b or s or "[No content provided]"


def ingest_ticket(raw: Dict[str, Any]) -> NormalizedTicket:
    """
    Ingests a raw ticket dictionary and normalizes it into a NormalizedTicket.
    Handles missing fields, unusual characters, and empty bodies safely.
    """
    ticket_id = str(raw.get("ticket_id") or f"TICK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}")
    channel = normalize_channel(raw.get("channel"))
    subject = str(raw.get("subject") or "").strip()
    body = str(raw.get("body") or "").strip()
    cleaned_text = clean_ticket_body(body, subject)
    
    received_at = str(raw.get("received_at") or datetime.now(timezone.utc).isoformat())
    customer_id = str(raw.get("customer_id") or "UNKNOWN")
    customer_name = str(raw.get("customer_name") or "Anonymous")
    
    # Customer tier validation
    tier = str(raw.get("customer_tier") or "standard").strip().lower()
    if tier not in {"enterprise", "business", "standard"}:
        tier = "standard"
        
    # Customer region validation
    region = str(raw.get("customer_region") or "north_america").strip().lower()
    if region not in {"north_america", "europe", "asia_pacific", "latin_america"}:
        region = "north_america"
        
    # Language fluency validation
    fluency = str(raw.get("language_fluency") or "fluent").strip().lower()
    if fluency not in {"fluent", "non_fluent"}:
        fluency = "fluent"
        
    labels = raw.get("labels")
    history = raw.get("history")
    
    metadata = {
        "raw_channel": raw.get("channel"),
        "body_length": len(body),
        "has_subject": bool(subject),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return NormalizedTicket(
        ticket_id=ticket_id,
        channel=channel,
        subject=subject,
        body=body,
        cleaned_text=cleaned_text,
        received_at=received_at,
        customer_id=customer_id,
        customer_name=customer_name,
        customer_tier=tier,
        customer_region=region,
        language_fluency=fluency,
        labels=labels,
        history=history,
        metadata=metadata,
    )


def ingest_tickets(raw_tickets: List[Dict[str, Any]]) -> List[NormalizedTicket]:
    """Ingest a list of raw tickets."""
    return [ingest_ticket(t) for t in raw_tickets]
