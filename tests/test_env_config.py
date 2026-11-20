"""
tests/test_env_config.py
Verifies that retrieval top_k and confidence threshold are loaded from .env file
and properly control DocRetriever, Router, and SupportPipeline.
"""

import os
import pytest
from dotenv import load_dotenv

from src.classify import ClassificationResult
from src.guardrails import GuardrailCheckResult
from src.pipeline import SupportPipeline
from src.retrieve import DocRetriever, RetrievedSource
from src.route import Router


def test_env_file_contains_confidence_and_top_k():
    """Verify that root .env defines CONFIDENCE_THRESHOLD and RETRIEVAL_TOP_K."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    assert os.path.exists(env_path), ".env file must exist in project root"
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "CONFIDENCE_THRESHOLD" in content, ".env must contain CONFIDENCE_THRESHOLD"
    assert "RETRIEVAL_TOP_K" in content, ".env must contain RETRIEVAL_TOP_K"


def test_router_uses_env_confidence_threshold(monkeypatch):
    """Verify Router picks up CONFIDENCE_THRESHOLD from environment variable."""
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.85")
    router_env = Router()
    assert router_env.threshold == 0.85

    # Explicit parameter overrides environment variable
    router_custom = Router(confidence_threshold=0.75)
    assert router_custom.threshold == 0.75


def test_doc_retriever_uses_env_top_k(monkeypatch):
    """Verify DocRetriever picks up RETRIEVAL_TOP_K from environment variable."""
    monkeypatch.setenv("RETRIEVAL_TOP_K", "4")
    retriever_env = DocRetriever(use_chroma=False)
    assert retriever_env.top_k == 4

    results = retriever_env.retrieve("invalid credentials login error", min_score=0.01)
    assert len(results) <= 4

    # Explicit top_k argument overrides default
    results_2 = retriever_env.retrieve("invalid credentials login error", top_k=2, min_score=0.01)
    assert len(results_2) <= 2


def test_support_pipeline_uses_env_settings(monkeypatch):
    """Verify SupportPipeline loads and propagates both values from .env."""
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.82")
    monkeypatch.setenv("RETRIEVAL_TOP_K", "6")

    pipeline = SupportPipeline()
    assert pipeline.confidence_threshold == 0.82
    assert pipeline.top_k == 6
    assert pipeline.router.threshold == 0.82
    assert pipeline.retriever.top_k == 6


def test_kill_switch_activation_via_env(monkeypatch):
    """Verify kill switch: setting CONFIDENCE_THRESHOLD=1.00 forces all auto_respond candidates to escalate."""
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "1.00")
    router_kill = Router()
    assert router_kill.threshold == 1.00

    high_conf_cls = ClassificationResult(
        intent="general_inquiry",
        intent_confidence=0.95,
        urgency="low",
        urgency_confidence=0.90,
        concise_summary="Inquiry about product features",
        model_used="test-rule",
        alternatives=[],
        uncertainty_flag=False,
        rationale="High confidence mock classification",
    )
    mock_source = [
        RetrievedSource(
            doc_id="DOC-GEN-001",
            title="Overview",
            category="general",
            passage="Standard features overview passage.",
            score=0.90,
        )
    ]
    mock_guard = GuardrailCheckResult(
        passed=True,
        blocked=False,
        details="Clean ticket passed inbound checks",
        checks={"pii": "pass", "injection": "pass"},
    )

    decision = router_kill.route("TEST-KILL-01", high_conf_cls, mock_source, mock_guard)
    assert decision.action == "escalate"
    assert "Confidence floor not met" in decision.reason
    assert decision.threshold_applied == 1.00
