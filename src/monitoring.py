"""
src/monitoring.py
Production Prometheus telemetry and metrics instrumentation.
Meets Setup Guide Section 06 (Monitoring - Prometheus and Grafana).
"""

import os
from typing import Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    start_http_server,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)

# Core Telemetry Metrics (Setup Guide Table 12)
TICKETS_PROCESSED = Counter(
    "tickets_processed_total",
    "Total tickets processed split by channel and outcome",
    ["channel", "outcome"],
)

RESPONSE_LATENCY = Histogram(
    "response_seconds",
    "End-to-end response time in seconds",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0],
)

GUARDRAIL_BLOCKS = Counter(
    "guardrail_blocks_total",
    "Total responses or requests blocked by safety guardrails",
    ["guardrail"],
)

# Advanced Observability for Model Drift (Setup Guide Paragraph 65)
CONFIDENCE_SCORES = Histogram(
    "intent_confidence_score",
    "Distribution of intent classification confidence scores for drift monitoring",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

RETRIEVAL_SCORES = Histogram(
    "retrieval_relevance_score",
    "Distribution of documentation passage retrieval relevance scores",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

ACTIVE_KILL_SWITCH = Gauge(
    "kill_switch_active",
    "Gauge indicating whether manual containment / kill switch is engaged (1 for active, 0 for normal)",
)

_server_started = False


def start_metrics_server(port: int = 8001):
    """
    Starts standalone Prometheus metrics scrape server on port 8001 (Setup Guide Section 06).
    Safe against multiple invocations.
    """
    global _server_started
    if not _server_started:
        try:
            start_http_server(port)
            _server_started = True
            print(f"[Monitoring] Prometheus metrics server started on port {port}")
        except Exception:
            pass


def get_latest_metrics() -> bytes:
    """Returns raw Prometheus exposition bytes for FastAPI /metrics endpoint."""
    return generate_latest(REGISTRY)
