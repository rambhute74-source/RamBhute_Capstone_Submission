"""
src/api.py
FastAPI application serving CloudServe automated customer support.
Provides endpoints for single ticket processing, batch processing, decision auditing,
health monitoring, and operational metrics.
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from src.logging_store import DecisionLogger
from src.pipeline import SupportPipeline, TicketProcessingResult

app = FastAPI(
    title="CloudServe Intelligent Customer Support API",
    description="Automated triage, retrieval, grounding, guardrails, and decision logging.",
    version="1.0.0",
)

pipeline = SupportPipeline()
logger = DecisionLogger()


class TicketInput(BaseModel):
    ticket_id: Optional[str] = None
    channel: str = "email"
    subject: Optional[str] = ""
    body: str
    customer_id: Optional[str] = "CUST-001"
    customer_name: Optional[str] = "Customer"
    customer_tier: Optional[str] = "standard"
    customer_region: Optional[str] = "north_america"
    language_fluency: Optional[str] = "fluent"
    metadata: Optional[Dict[str, Any]] = None


@app.get("/health")
def health_check():
    """Health status and component verification."""
    return {
        "status": "healthy",
        "service": "cloudserve-support-ai",
        "doc_chunks_indexed": len(pipeline.retriever.chunks),
        "total_decisions_logged": logger.count_decisions(),
    }


@app.post("/tickets/process", response_model=TicketProcessingResult)
def process_ticket(ticket: TicketInput):
    """Process a single incoming support ticket end-to-end."""
    try:
        raw_dict = ticket.model_dump()
        result = pipeline.process_ticket(raw_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tickets/batch", response_model=List[TicketProcessingResult])
def process_batch(tickets: List[TicketInput]):
    """Process a batch of tickets sequentially."""
    results = []
    for t in tickets:
        res = pipeline.process_ticket(t.model_dump())
        results.append(res)
    return results


@app.get("/decisions")
def get_decisions(
    ticket_id: Optional[str] = Query(None, description="Filter decisions by ticket ID")
):
    """Query persistent decision logs."""
    if ticket_id:
        return logger.get_decisions_for_ticket(ticket_id)
    return {
        "total_decisions": logger.count_decisions(),
        "database_path": logger.db_path,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=False)
