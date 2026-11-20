"""
scripts/build_vector_store.py
Builds and persists the local Chroma vector store from data/documentation.json
as specified in Section 04 of Inputs/03_Reference/Setup_Guide.docx.
"""

import json
import os
import sys

# Ensure root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def build_chroma_store(
    doc_path: str = "data/documentation.json",
    persist_dir: str = "storage/chroma",
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
):
    doc_path = os.path.join(ROOT_DIR, doc_path)
    persist_dir = os.path.join(ROOT_DIR, persist_dir)

    print(f"Loading documentation from: {doc_path}")
    with open(doc_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    texts = []
    metadatas = []

    for doc in documents:
        doc_id = doc.get("doc_id") or doc.get("id")
        title = doc.get("title", "")
        category = doc.get("category", "")
        content = doc.get("content", "")

        chunks = splitter.split_text(content)
        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({
                "doc_id": doc_id,
                "title": title,
                "category": category,
            })

    print(f"Prepared {len(texts)} chunks across {len(documents)} approved articles.")
    print(f"Initializing embedding model: {model_name}...")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    print(f"Embedding and persisting chunks to Chroma at: {persist_dir}...")
    os.makedirs(persist_dir, exist_ok=True)
    store = Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    store.persist()
    print(f"Successfully stored and indexed {len(texts)} passages in Chroma vector store!")
    return store


if __name__ == "__main__":
    build_chroma_store()
