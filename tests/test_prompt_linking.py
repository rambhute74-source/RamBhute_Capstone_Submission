"""
tests/test_prompt_linking.py
Verifies that prompt files in `prompts/` are the active single source of truth,
not static or dummy files, and that runtime components dynamically link to them.
"""

import os
import pytest
from src.prompt_loader import prompt_registry, PROMPT_FILE_MAP
from src.classify import TicketClassifier, VALID_INTENTS
from src.generate import DraftGenerator
from src.retrieve import RetrievedSource
from src.pipeline import SupportPipeline


def test_prompt_files_exist_and_non_empty():
    """Verify that all 13 prompt registry files exist on disk in their dedicated folders."""
    for pid, expected_path in PROMPT_FILE_MAP.items():
        assert os.path.exists(expected_path), f"Prompt file missing for {pid} at {expected_path}"
        # Assert path is inside dedicated subdirectory
        assert any(sub in expected_path for sub in ["specification", "build", "evaluation", "review"])
        with open(expected_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content.strip()) > 300, f"Prompt file {pid} has insufficient content ({len(content)} chars)"
        assert "ROLE" in content, f"Prompt {pid} missing ROLE section"
        assert "TASK" in content, f"Prompt {pid} missing TASK section"


def test_no_loose_prompt_files_in_root():
    """Verify that no prompt text files exist loose in prompts root folder (must be in subdirectories)."""
    prompts_root = prompt_registry.prompts_dir
    loose_txt_files = [f for f in os.listdir(prompts_root) if f.endswith(".txt")]
    assert len(loose_txt_files) == 0, f"Found loose prompt files in root: {loose_txt_files}"


def test_prompt_registry_renders_pr01_classifier():
    """Verify that PR-01 is dynamically loaded and interpolated with ticket variables."""
    ticket_body = "User cannot connect to VPN gateway with error 800"
    rendered = prompt_registry.render_pr01_classifier(
        ticket_body=ticket_body,
        channel="chat",
        urgency="high",
        allowed_intents=VALID_INTENTS,
    )
    assert ticket_body in rendered
    assert "vpn" in rendered.lower()
    assert "allowed_intents" in rendered.lower() or "allowed intent" in rendered.lower() or "intent_taxonomy" in rendered.lower()
    assert "ROLE" in rendered
    assert "TASK" in rendered


def test_prompt_registry_renders_pr04_draft():
    """Verify that PR-04 is dynamically loaded and interpolated with retrieved documentation."""
    passages = [
        {
            "doc_id": "KB-NET-01",
            "title": "VPN Troubleshooting",
            "passage": "Restart the virtual network adapter and check MTU settings.",
        }
    ]
    rendered = prompt_registry.render_pr04_draft(
        ticket_text="My VPN is down",
        customer_name="Alice Smith",
        channel="email",
        retrieved_passages=passages,
        intent="network_issue",
    )
    assert "KB-NET-01" in rendered
    assert "Restart the virtual network adapter" in rendered
    assert "My VPN is down" in rendered
    assert "Alice Smith" in rendered


def test_prompt_registry_renders_pr05_escalation():
    """Verify that PR-05 is dynamically loaded for escalation handoffs."""
    rendered = prompt_registry.render_pr05_escalation(
        ticket_text="Billing overcharge on account 9912",
        ticket_id="TICKET-1234",
        channel="email",
        urgency="high",
        intent="billing_query",
        escalation_reason="Protected class billing dispute",
        retrieved_docs=["KB-BILL-01"],
    )
    assert "TICKET-1234" in rendered
    assert "billing_query" in rendered
    assert "Protected class billing dispute" in rendered


def test_components_use_live_prompt_versions():
    """Verify that pipeline and logger record dynamic prompt version from registry."""
    pipeline = SupportPipeline()
    res = pipeline.process_ticket(
        {
            "ticket_id": "TEST-PR-LINK",
            "channel": "email",
            "body": "How do I configure SSO integration with Okta?",
            "customer_name": "Bob",
        }
    )
    assert res.decision_id is not None
    # Verify decision logged contains the registered PR-03 version
    logged = pipeline.logger.get_decisions_for_ticket("TEST-PR-LINK")
    assert len(logged) > 0
    assert logged[0]["prompt_version"] == prompt_registry.get_prompt_version("PR-03")
