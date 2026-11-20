"""
tests/test_query_enhancer.py
Verifies that query enhancement prompt PR-02b is linked from `prompts/`
and that QueryEnhancer correctly expands domain terminology for retrieval.
"""

import os
import pytest
from src.prompt_loader import prompt_registry
from src.query_enhancer import QueryEnhancer, EnhancedQuery
from src.retrieve import DocRetriever


def test_pr02b_prompt_exists_in_prompts_folder():
    """Verify that PR-02b prompt file exists in prompts/build/ and has real content."""
    prompt_path = prompt_registry.get_prompt_path("PR-02b")
    assert os.path.exists(prompt_path), f"PR-02b prompt file not found at {prompt_path}"
    assert "build" in prompt_path, f"PR-02b must be in dedicated 'build' subfolder: {prompt_path}"
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "PR-02b" in content
    assert "ROLE" in content
    assert "TASK" in content
    assert "dense_semantic_query" in content


def test_prompt_registry_renders_pr02b():
    """Verify that prompt_registry loads and renders PR-02b template with inputs."""
    ticket = "Cannot log into console using MFA device"
    rendered = prompt_registry.render_pr02b_query_enhancer(
        ticket_body=ticket,
        channel="chat",
        detected_intent="authentication_issue",
    )
    assert ticket in rendered
    assert "chat" in rendered
    assert "authentication_issue" in rendered
    assert "ROLE" in rendered
    assert "TASK" in rendered


def test_query_enhancer_domain_expansion():
    """Verify that QueryEnhancer expands domain acronyms and removes pleasantries."""
    enhancer = QueryEnhancer()
    ticket = "Hello team, my MFA code is failing with 401 on login. Please help asap! Bob"
    enhanced = enhancer.enhance(ticket, channel="email", intent="authentication_issue")

    assert isinstance(enhanced, EnhancedQuery)
    # Check acronym expansion
    assert "multi-factor authentication" in enhanced.expanded_synonyms or "TOTP" in enhanced.expanded_synonyms
    # Check error code extraction
    assert "401" in enhanced.extracted_error_codes
    # Check denoising (pleasantries removed from start of dense query)
    assert not enhanced.dense_semantic_query.lower().startswith("hello team")
    assert enhanced.prompt_version == prompt_registry.get_prompt_version("PR-02b")


def test_retriever_integrates_query_enhancement():
    """Verify that DocRetriever successfully retrieves using query enhancement."""
    retriever = DocRetriever(use_chroma=False)
    results = retriever.retrieve(
        query="hi, my SSO login keeps erroring out with 403, please advise",
        top_k=3,
        enhance_query=True,
    )
    assert len(results) > 0
    # Top result should be related to authentication / SSO
    top_doc_ids = [r.doc_id for r in results]
    assert any("AUTH" in doc_id or "SEC" in doc_id for doc_id in top_doc_ids)
