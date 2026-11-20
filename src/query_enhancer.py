"""
src/query_enhancer.py
Reformulates raw customer support tickets into high-precision technical queries
for semantic (Chroma) and lexical (TF-IDF) document retrieval.
Implements Functional Requirement FR-02 and dynamically loads prompt PR-02b.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
import requests

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.prompt_loader import prompt_registry

load_dotenv()

# CloudServe Technical Acronym and Domain Taxonomy Map
DOMAIN_SYNONYM_MAP: Dict[str, List[str]] = {
    r"\bmfa\b": ["multi-factor authentication", "TOTP", "authenticator app", "clock drift", "recovery codes"],
    r"\bsso\b": ["single sign-on", "SAML", "identity provider", "IdP", "assertion consumer service", "Okta"],
    r"\biam\b": ["identity and access management", "roles", "permissions", "team members", "access control"],
    r"\bapi\b": ["API endpoint", "authentication header", "bearer token", "rate limit", "CLI", "SDK"],
    r"\bvpn\b": ["virtual private network", "gateway", "tunnel", "MTU size", "handshake error"],
    r"\bvpc\b": ["virtual private cloud", "subnet", "route table", "security group", "peering"],
    r"\bssl\b|\btls\b": ["SSL certificate", "TLS handshake", "cipher suite", "certificate expiration"],
    r"\bcredential(s)?\b|\blogin\b|\bpassword\b": ["invalid credentials", "login failure", "account locked", "session cookie"],
    r"\bbilling\b|\binvoice\b": ["billing dispute", "invoice line item", "payment method", "subscription tier"],
    r"\bbackup(s)?\b|\bsnapshot(s)?\b": ["automated snapshot", "point-in-time recovery", "retention policy"],
    r"\blatency\b|\bslow\b|\btimeout\b": ["response latency", "504 gateway timeout", "throttling", "p95"],
}

# Conversational Noise Patterns to Strip
CONVERSATIONAL_NOISE = [
    r"^(?:hello|hi|hey|dear|greetings|good\s+(?:morning|afternoon|evening))[\s,!.?-]*",
    r"(?:please\s+help|urgent(?:ly)?|asap|any\s+idea|kindly\s+advise)[\s,!.?-]*",
    r"(?:thanks|thank\s+you|best\s+regards|cheers|sincerely)[\s\S]*$",
]


class EnhancedQuery(BaseModel):
    original_query: str
    dense_semantic_query: str
    sparse_keyword_query: str
    extracted_error_codes: List[str]
    expanded_synonyms: List[str]
    intent_focus: str
    prompt_version: str = "PR-02b v1.0"


class QueryEnhancer:
    """
    Expands and reformulates user ticket text into dense semantic queries
    and sparse lexical keywords for optimal retrieval across Chroma and TF-IDF.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        cache_file: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model_name or os.getenv(
            "MODEL_NAME", "meta-llama/llama-3.1-8b-instruct"
        )
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.cache_file = cache_file or os.path.join(
            base_dir, "storage", "llm_cache.json"
        )
        self.cache: Dict[str, Any] = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def enhance(
        self,
        ticket_text: str,
        channel: str = "email",
        intent: str = "general_inquiry",
        use_llm: bool = False,
    ) -> EnhancedQuery:
        """
        Produce dense semantic query and sparse keyword representations from ticket text.
        Loads and renders prompt PR-02b directly from the prompt library.
        """
        raw = (ticket_text or "").strip()
        if not raw:
            return EnhancedQuery(
                original_query="",
                dense_semantic_query="",
                sparse_keyword_query="",
                extracted_error_codes=[],
                expanded_synonyms=[],
                intent_focus=intent,
            )

        # Check Cache
        cache_key = hashlib.sha256(f"qe:{channel}:{raw}".encode("utf-8")).hexdigest()
        if cache_key in self.cache:
            try:
                return EnhancedQuery(**self.cache[cache_key])
            except Exception:
                pass

        # 1. Try LLM Enhancement with Prompt PR-02b
        if use_llm and self.api_key:
            try:
                prompt = prompt_registry.render_pr02b_query_enhancer(
                    ticket_body=raw[:1000],
                    channel=channel,
                    detected_intent=intent,
                )
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
                    if content.startswith("```"):
                        content = re.sub(r"^```(?:json)?\s*", "", content)
                        content = re.sub(r"\s*```$", "", content)
                    parsed = json.loads(content)
                    result = EnhancedQuery(
                        original_query=raw,
                        dense_semantic_query=parsed.get("dense_semantic_query", raw),
                        sparse_keyword_query=parsed.get("sparse_keyword_query", raw),
                        extracted_error_codes=parsed.get("extracted_error_codes", []),
                        expanded_synonyms=parsed.get("expanded_synonyms", []),
                        intent_focus=parsed.get("intent_focus", intent),
                        prompt_version=prompt_registry.get_prompt_version("PR-02b"),
                    )
                    self.cache[cache_key] = result.model_dump()
                    self._save_cache()
                    return result
            except Exception:
                pass

        # 2. High-Precision Deterministic Fallback Engine
        return self._enhance_deterministic(raw, intent, cache_key)

    def _enhance_deterministic(
        self, raw: str, intent: str, cache_key: Optional[str] = None
    ) -> EnhancedQuery:
        """Deterministic domain keyword expansion and conversational denoising."""
        cleaned = raw
        for pattern in CONVERSATIONAL_NOISE:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Extract Error Codes
        error_patterns = [
            r"\b[A-Z]{3,4}-[A-Z0-9]{2,5}-\d{2,4}\b",
            r"\b(?:error|status|code|http)\s*[-_:]?\s*(\d{3})\b",
            r"\b[A-Za-z]+(?:Exception|Error|Failure|Timeout)\b",
            r"\b4\d{2}\b|\b5\d{2}\b",
        ]
        extracted_errors = []
        for pat in error_patterns:
            matches = re.findall(pat, raw, flags=re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    m = m[0]
                if m not in extracted_errors:
                    extracted_errors.append(m)

        # Synonym and Domain Expansion
        synonyms = []
        lower_raw = raw.lower()
        for regex_pat, expansions in DOMAIN_SYNONYM_MAP.items():
            if re.search(regex_pat, lower_raw):
                for exp in expansions:
                    if exp not in synonyms:
                        synonyms.append(exp)

        # Construct Dense Semantic Query
        dense_query = f"{cleaned} {' '.join(synonyms[:4])}".strip()

        # Construct Sparse Lexical Query (Keywords + Errors)
        keyword_tokens = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", cleaned.lower())
        unique_tokens = []
        stop_words = {"the", "and", "for", "that", "this", "with", "have", "from", "when", "into"}
        for t in keyword_tokens:
            if t not in stop_words and t not in unique_tokens:
                unique_tokens.append(t)

        sparse_query = " ".join(unique_tokens + extracted_errors + synonyms[:6])

        result = EnhancedQuery(
            original_query=raw,
            dense_semantic_query=dense_query,
            sparse_keyword_query=sparse_query,
            extracted_error_codes=extracted_errors,
            expanded_synonyms=synonyms,
            intent_focus=intent,
            prompt_version=prompt_registry.get_prompt_version("PR-02b"),
        )

        if cache_key:
            self.cache[cache_key] = result.model_dump()
            self._save_cache()

        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CloudServe Technical Query Enhancer")
    parser.add_argument(
        "--ticket",
        type=str,
        default="Hi team, my MFA authenticator code is failing on login with 401. Please help asap! Bob",
        help="Raw support ticket text",
    )
    parser.add_argument("--channel", type=str, default="email", help="Ticket channel")
    parser.add_argument("--intent", type=str, default="authentication_issue", help="Detected intent")
    parser.add_argument("--use-llm", action="store_true", help="Use OpenRouter LLM enhancement")
    args = parser.parse_args()

    enhancer = QueryEnhancer()
    print("\n--- Enhancing Query with Prompt PR-02b ---")
    enhanced = enhancer.enhance(
        args.ticket, channel=args.channel, intent=args.intent, use_llm=args.use_llm
    )
    print(f"Original Ticket: {enhanced.original_query}\n")
    print(f"Prompt Version:  {enhanced.prompt_version}")
    print(f"Dense Query:     {enhanced.dense_semantic_query}")
    print(f"Sparse Query:    {enhanced.sparse_keyword_query}")
    print(f"Error Codes:     {enhanced.extracted_error_codes}")
    print(f"Synonyms:        {enhanced.expanded_synonyms}")
