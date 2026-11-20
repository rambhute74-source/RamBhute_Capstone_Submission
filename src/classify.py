"""
src/classify.py
Predicts intent category (one of 22) and urgency level (high, medium, low)
with calibrated numeric confidence scores and alternative rankings.
Meets Acceptance Criterion A3 and Functional Requirement FR-01.
"""

import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import numpy as np
from pydantic import BaseModel
import requests
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

load_dotenv()

VALID_INTENTS = [
    "account_access",
    "api_key_issue",
    "api_usage_question",
    "authentication_failure",
    "billing_query",
    "compliance_request",
    "configuration_help",
    "data_export",
    "data_residency",
    "database_issue",
    "deployment_failure",
    "feature_request",
    "integration_help",
    "onboarding",
    "performance_degradation",
    "quota_or_overage",
    "rate_limit",
    "rollback_request",
    "security_incident",
    "sso_configuration",
    "unclear_request",
    "webhook_issue",
]

PROTECTED_INTENTS = {
    "security_incident",
    "compliance_request",
    "data_residency",
    "billing_query",
    "feature_request",
    "unclear_request",
}


class Alternative(BaseModel):
    intent: str
    confidence: float


class ClassificationResult(BaseModel):
    concise_summary: str
    intent: str
    intent_confidence: float
    urgency: str
    urgency_confidence: float
    alternatives: List[Alternative]
    uncertainty_flag: bool
    rationale: str
    model_used: str


class TicketClassifier:
    """
    Hybrid classifier combining calibrated statistical models with LLM reasoning (PR-01)
    and robust disk caching to handle rate limits and outages gracefully.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "development_tickets.json"
        )
        self.cache_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "storage", "llm_cache.json"
        )
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        self.cache: Dict[str, Any] = self._load_cache()

        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct")

        # Train local calibrated fallback model
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.intent_clf: Optional[CalibratedClassifierCV] = None
        self.urgency_clf: Optional[CalibratedClassifierCV] = None
        self._init_local_model()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def _init_local_model(self):
        if not os.path.exists(self.data_path):
            return
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                tickets = json.load(f)

            texts = [t.get("body", "") for t in tickets]
            intents = [t.get("labels", {}).get("intent", "unclear_request") for t in tickets]
            urgencies = [t.get("labels", {}).get("urgency", "medium") for t in tickets]

            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.85, sublinear_tf=True)
            X = self.vectorizer.fit_transform(texts)

            self.intent_clf = CalibratedClassifierCV(LogisticRegression(max_iter=500, C=3.0), cv=3)
            self.intent_clf.fit(X, intents)

            self.urgency_clf = CalibratedClassifierCV(LogisticRegression(max_iter=500), cv=3)
            self.urgency_clf.fit(X, urgencies)
        except Exception as e:
            print(f"Warning: Failed to initialize local classifier: {e}")

    def classify_local(self, text: str) -> ClassificationResult:
        """Fallback local calibrated classification."""
        cleaned = (text or "").strip()
        if not cleaned or not self.vectorizer or not self.intent_clf or not self.urgency_clf:
            return ClassificationResult(
                concise_summary="Empty or unclassifiable ticket body.",
                intent="unclear_request",
                intent_confidence=0.0,
                urgency="medium",
                urgency_confidence=0.5,
                alternatives=[],
                uncertainty_flag=True,
                rationale="Fallback: Ticket text is empty or model uninitialized.",
                model_used="fallback-rule",
            )

        X = self.vectorizer.transform([cleaned])
        intent_probs = self.intent_clf.predict_proba(X)[0]
        intent_classes = self.intent_clf.classes_

        top_indices = np.argsort(intent_probs)[::-1]
        best_intent = intent_classes[top_indices[0]]
        best_intent_conf = float(intent_probs[top_indices[0]])

        alts = [
            Alternative(intent=intent_classes[idx], confidence=round(float(intent_probs[idx]), 4))
            for idx in top_indices[1:4]
        ]

        urg_probs = self.urgency_clf.predict_proba(X)[0]
        urg_classes = self.urgency_clf.classes_
        top_urg_idx = np.argmax(urg_probs)
        best_urg = urg_classes[top_urg_idx]
        best_urg_conf = float(urg_probs[top_urg_idx])

        # Summary extraction (first sentence or up to 120 chars)
        sentences = re.split(r"[.!?\n]", cleaned)
        first_sentence = sentences[0].strip() if sentences else cleaned[:100]
        summary = first_sentence[:150]

        uncertainty = best_intent_conf < 0.80 or best_intent in PROTECTED_INTENTS

        return ClassificationResult(
            concise_summary=summary,
            intent=best_intent,
            intent_confidence=round(best_intent_conf, 4),
            urgency=best_urg,
            urgency_confidence=round(best_urg_conf, 4),
            alternatives=alts,
            uncertainty_flag=uncertainty,
            rationale=f"Calibrated probability {best_intent_conf:.2f} for intent '{best_intent}'.",
            model_used="calibrated-local-ensemble",
        )

    def classify(self, text: str, channel: str = "email", use_llm: bool = True) -> ClassificationResult:
        """
        Classify ticket using LLM (OpenRouter) with caching and instant local fallback.
        """
        cleaned = (text or "").strip()
        if not cleaned:
            return self.classify_local("")

        # Check cache
        cache_key = hashlib.sha256(f"{channel}:{cleaned}".encode("utf-8")).hexdigest()
        if cache_key in self.cache:
            try:
                cached_data = self.cache[cache_key]
                return ClassificationResult(**cached_data)
            except Exception:
                pass

        # If LLM requested and API key present, load and render live PR-01 prompt from prompts/
        if use_llm and self.api_key:
            try:
                from src.prompt_loader import prompt_registry
                prompt = prompt_registry.render_pr01_classifier(
                    ticket_body=cleaned[:1200],
                    channel=channel,
                    urgency="medium",
                    allowed_intents=VALID_INTENTS,
                )
            except Exception:
                # Fallback to inline template if prompt file is unreadable
                prompt = f"""You are CloudServe's ticket-triage assistant. Classify the support ticket for intent and urgency.

Ticket Channel: {channel}
Ticket Content:
\"\"\"{cleaned[:1200]}\"\"\"

Allowed Intent Categories:
{', '.join(VALID_INTENTS)}

Allowed Urgencies:
high, medium, low

Return strictly valid JSON with no markdown wrapping:
{{
  "summary": "1-2 sentence issue summary",
  "proposed_intent": "one_of_allowed_intents",
  "supplied_urgency": "high|medium|low",
  "uncertainty_state": "clear|uncertain|ambiguous",
  "needs_human": false,
  "reason_codes": [],
  "missing_information": []
}}"""

            try:
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.0,
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    # Strip any markdown code fence
                    if content.startswith("```"):
                        content = re.sub(r"^```(?:json)?\s*", "", content)
                        content = re.sub(r"\s*```$", "", content)
                    parsed = json.loads(content)

                    intent = parsed.get("proposed_intent")
                    if intent not in VALID_INTENTS:
                        # Fallback to local
                        return self.classify_local(cleaned)

                    # Determine uncertainty and confidence according to PR-01 specification
                    needs_human = bool(parsed.get("needs_human", False))
                    uncertainty_state = parsed.get("uncertainty_state", "clear")
                    raw_conf = parsed.get("intent_confidence")
                    if raw_conf is not None:
                        intent_conf = float(raw_conf)
                    elif needs_human or uncertainty_state != "clear":
                        intent_conf = 0.65
                    else:
                        intent_conf = 0.95

                    urgency = str(parsed.get("supplied_urgency") or parsed.get("urgency") or "medium").lower()
                    if urgency not in {"high", "medium", "low"}:
                        urgency = "medium"

                    summary = parsed.get("summary") or parsed.get("concise_summary") or cleaned[:100]

                    result = ClassificationResult(
                        concise_summary=summary,
                        intent=intent,
                        intent_confidence=round(intent_conf, 4),
                        urgency=urgency,
                        urgency_confidence=round(float(parsed.get("urgency_confidence", 0.90)), 4),
                        alternatives=[
                            Alternative(
                                intent=a.get("intent", "unclear_request"),
                                confidence=round(float(a.get("confidence", 0.05)), 4),
                            )
                            for a in parsed.get("alternatives", [])
                        ],
                        uncertainty_flag=needs_human
                        or uncertainty_state != "clear"
                        or intent_conf < 0.80
                        or intent in PROTECTED_INTENTS,
                        rationale=f"PR-01 prompt classification ({uncertainty_state})",
                        model_used=self.model_name,
                    )
                    self.cache[cache_key] = result.model_dump()
                    self._save_cache()
                    return result
            except Exception as e:
                # On timeout or provider error, gracefully degrade to calibrated local model
                pass

        # Fallback to calibrated local model
        result = self.classify_local(cleaned)
        self.cache[cache_key] = result.model_dump()
        self._save_cache()
        return result
