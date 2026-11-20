"""
src/api.py
FastAPI application serving CloudServe automated customer support.
Provides endpoints for single ticket processing, batch processing, decision auditing,
health monitoring, and operational metrics.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel
from src.logging_store import DecisionLogger
from src.pipeline import SupportPipeline, TicketProcessingResult
from src.monitoring import get_latest_metrics, CONTENT_TYPE_LATEST, start_metrics_server

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Prometheus scrape server on port 8001 (Setup Guide Section 06) if enabled
    if os.getenv("START_METRICS_SERVER", "false").lower() in {"true", "1", "yes"}:
        metrics_port = int(os.getenv("METRICS_PORT", "8001"))
        start_metrics_server(metrics_port)
    yield


app = FastAPI(
    title="CloudServe Intelligent Customer Support API",
    description="Automated triage, retrieval, grounding, guardrails, decision logging, and Prometheus monitoring.",
    version="1.0.0",
    lifespan=lifespan,
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
        "confidence_threshold": pipeline.confidence_threshold,
        "retrieval_top_k": pipeline.top_k,
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


@app.get("/metrics")
def get_prometheus_metrics():
    """Expose Prometheus metrics for scraping (Setup Guide Section 06)."""
    return Response(content=get_latest_metrics(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=False)
