"""
src/retrieve.py
Searches the approved CloudServe documentation corpus (29 articles)
and returns traceable, ranked source passages with confidence scores.
Meets Acceptance Criterion A4 and Functional Requirement FR-02.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RetrievedSource(BaseModel):
    doc_id: str
    title: str
    category: str
    passage: str
    score: float


class DocRetriever:
    """
    Retrieval engine for CloudServe approved documentation.
    Splits articles into coherent passages and uses sublinear TF-IDF + n-gram vectorization.
    """

    def __init__(self, doc_path: Optional[str] = None, min_threshold: float = 0.08):
        self.doc_path = doc_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "documentation.json"
        )
        self.min_threshold = min_threshold
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.chunk_vectors = None
        self._load_and_index()

    def _load_and_index(self):
        if not os.path.exists(self.doc_path):
            raise FileNotFoundError(f"Documentation file not found at: {self.doc_path}")

        with open(self.doc_path, "r", encoding="utf-8") as f:
            docs_list = json.load(f)

        self.documents = {d["doc_id"]: d for d in docs_list}
        self.chunks = []

        # Systematically chunk each document
        for doc in docs_list:
            doc_id = doc["doc_id"]
            title = doc.get("title", "")
            category = doc.get("category", "")
            content = doc.get("content", "")

            # Split content by markdown section headers or double newlines
            sections = re.split(r"\n(?=#{1,3}\s)", content)
            for sec in sections:
                sec = sec.strip()
                if not sec:
                    continue
                # If section is longer than 750 characters, split into smaller blocks
                if len(sec) > 750:
                    sub_paras = sec.split("\n\n")
                    curr_block = ""
                    for p in sub_paras:
                        p = p.strip()
                        if not p:
                            continue
                        if len(curr_block) + len(p) < 650:
                            curr_block += "\n\n" + p if curr_block else p
                        else:
                            if curr_block:
                                self.chunks.append({
                                    "doc_id": doc_id,
                                    "title": title,
                                    "category": category,
                                    "passage": curr_block,
                                })
                            curr_block = p
                    if curr_block:
                        self.chunks.append({
                            "doc_id": doc_id,
                            "title": title,
                            "category": category,
                            "passage": curr_block,
                        })
                else:
                    self.chunks.append({
                        "doc_id": doc_id,
                        "title": title,
                        "category": category,
                        "passage": sec,
                    })

        # Fit TF-IDF Vectorizer
        corpus = [
            f"{c['title']} {c['category']} {c['passage']}"
            for c in self.chunks
        ]
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
            max_df=0.90,
            min_df=1,
        )
        self.chunk_vectors = self.vectorizer.fit_transform(corpus)

    def retrieve(
        self, query: str, top_k: int = 5, min_score: Optional[float] = None
    ) -> List[RetrievedSource]:
        """
        Retrieves top_k passages relevant to the query.
        Returns empty list if top score is below threshold (fail-closed).
        """
        threshold = min_score if min_score is not None else self.min_threshold
        q = (query or "").strip()
        if not q or self.chunk_vectors is None or self.vectorizer is None:
            return []

        q_vec = self.vectorizer.transform([q])
        sims = cosine_similarity(q_vec, self.chunk_vectors)[0]

        top_indices = np.argsort(sims)[::-1]
        results: List[RetrievedSource] = []
        seen_doc_sections = set()

        for idx in top_indices:
            score = float(sims[idx])
            if score < threshold:
                break
            chunk = self.chunks[idx]
            key = (chunk["doc_id"], chunk["passage"][:60])
            if key in seen_doc_sections:
                continue
            seen_doc_sections.add(key)

            results.append(
                RetrievedSource(
                    doc_id=chunk["doc_id"],
                    title=chunk["title"],
                    category=chunk["category"],
                    passage=chunk["passage"],
                    score=round(score, 4),
                )
            )
            if len(results) >= top_k:
                break

        return results

    def get_doc(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Return full document metadata by doc_id."""
        return self.documents.get(doc_id)

    def is_valid_doc_id(self, doc_id: str) -> bool:
        """Check if doc_id exists in approved 29-article corpus."""
        return doc_id in self.documents
