"""
src/retrieve.py
Searches the approved CloudServe documentation corpus (29 articles)
and returns traceable, ranked source passages with confidence scores.
Meets Acceptance Criterion A4, Functional Requirement FR-02, and Setup Guide Section 04.

Supports two retrieval engines:
1. Chroma Vector Store with 'all-MiniLM-L6-v2' dense embeddings (Setup Guide Section 04)
2. Calibrated Sublinear TF-IDF + n-gram cosine matching (high-speed deterministic fallback)
"""

import argparse
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
    Supports persistent Chroma vector store with sentence-transformers embeddings,
    with automatic fallback to calibrated TF-IDF + n-gram vectorization.
    """

    def __init__(
        self,
        doc_path: Optional[str] = None,
        chroma_dir: Optional[str] = None,
        use_chroma: Optional[bool] = None,
        min_threshold: float = 0.08,
    ):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.doc_path = doc_path or os.path.join(base_dir, "data", "documentation.json")
        self.chroma_dir = chroma_dir or os.path.join(base_dir, "storage", "chroma")
        self.min_threshold = min_threshold

        # Determine whether to use Chroma embeddings
        if use_chroma is not None:
            self.use_chroma = use_chroma
        else:
            # Default to Chroma if USE_CHROMA env var is set or if chroma storage exists
            env_val = os.getenv("USE_CHROMA_RETRIEVAL", "").lower()
            if env_val in {"true", "1", "yes"}:
                self.use_chroma = True
            else:
                self.use_chroma = False

        self.documents: Dict[str, Dict[str, Any]] = {}
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.chunk_vectors = None
        self.chroma_store = None

        # Always initialize deterministic TF-IDF baseline
        self._load_and_index_tfidf()

        # Initialize Chroma if requested or storage present
        if self.use_chroma:
            self._init_chroma()

    def _load_and_index_tfidf(self):
        """Build in-memory chunk index and sublinear TF-IDF vectorizer."""
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

    def _init_chroma(self):
        """Initialize connection to local Chroma vector store with embeddings."""
        try:
            from langchain_community.vectorstores import Chroma
            from langchain_community.embeddings import HuggingFaceEmbeddings

            if os.path.exists(self.chroma_dir) and os.path.exists(
                os.path.join(self.chroma_dir, "chroma.sqlite3")
            ):
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                self.chroma_store = Chroma(
                    persist_directory=self.chroma_dir,
                    embedding_function=embeddings,
                )
        except Exception:
            self.chroma_store = None

    def _retrieve_chroma(
        self, query: str, top_k: int = 5, min_score: float = 0.08
    ) -> List[RetrievedSource]:
        """Query Chroma vector store using dense sentence embeddings."""
        if not self.chroma_store:
            return []

        results = self.chroma_store.similarity_search_with_relevance_scores(
            query, k=top_k * 2
        )
        sources: List[RetrievedSource] = []
        seen_keys = set()

        for doc, score in results:
            if score < min_score:
                continue
            meta = doc.metadata or {}
            doc_id = meta.get("doc_id", "DOC-UNKNOWN")
            title = meta.get("title", "")
            category = meta.get("category", "")
            passage = doc.page_content.strip()

            key = (doc_id, passage[:60])
            if key in seen_keys:
                continue
            seen_keys.add(key)

            sources.append(
                RetrievedSource(
                    doc_id=doc_id,
                    title=title,
                    category=category,
                    passage=passage,
                    score=round(float(score), 4),
                )
            )
            if len(sources) >= top_k:
                break

        return sources

    def retrieve(
        self, query: str, top_k: int = 5, min_score: Optional[float] = None
    ) -> List[RetrievedSource]:
        """
        Retrieves top_k passages relevant to the query.
        Uses Chroma dense embeddings if active, with automatic TF-IDF fallback.
        Returns empty list if top score is below threshold (fail-closed).
        """
        threshold = min_score if min_score is not None else self.min_threshold
        q = (query or "").strip()
        if not q:
            return []

        # 1. Try Chroma semantic retrieval if enabled
        if self.use_chroma and self.chroma_store is not None:
            try:
                chroma_results = self._retrieve_chroma(q, top_k=top_k, min_score=threshold)
                if chroma_results:
                    return chroma_results
            except Exception:
                pass

        # 2. Fast, calibrated TF-IDF retrieval
        if self.chunk_vectors is None or self.vectorizer is None:
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CloudServe Knowledge Retrieval Engine")
    parser.add_argument("--query", type=str, default="Cannot reset password with MFA", help="Search query")
    parser.add_argument("--mode", type=str, choices=["chroma", "tfidf"], default="chroma", help="Engine mode")
    parser.add_argument("--top_k", type=int, default=3, help="Number of results")
    args = parser.parse_args()

    use_chroma = args.mode == "chroma"
    retriever = DocRetriever(use_chroma=use_chroma)
    print(f"\n--- Running retrieval with mode: {args.mode.upper()} ---")
    print(f"Query: '{args.query}'\n")
    matches = retriever.retrieve(args.query, top_k=args.top_k)
    for i, m in enumerate(matches, 1):
        print(f"{i}. [{m.score:.4f}] {m.doc_id} - {m.title}")
        print(f"   Passage: {m.passage[:120].strip()}...\n")
