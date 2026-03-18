"""
Embeddings & FAISS Vector Store Module
Manages embedding model loading, index creation, and similarity search.
"""
import os
import pickle
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

from src.config import EMBEDDING_MODEL, INDICES_DIR, TOP_K

# ── Singleton Embedding Model ──────────────────────────────────────────
_model = None

def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model (cached singleton)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts into vectors."""
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return np.array(embeddings, dtype="float32")


# ── Index Management ───────────────────────────────────────────────────

def _index_path(paper_id: str) -> Path:
    return INDICES_DIR / f"{paper_id}.faiss"

def _docs_path(paper_id: str) -> Path:
    return INDICES_DIR / f"{paper_id}_docs.pkl"


def create_index(documents: list[Document], paper_id: str) -> int:
    """Build a FAISS index from document chunks and save to disk.
    Returns the number of vectors indexed."""
    texts = [doc.page_content for doc in documents]
    embeddings = embed_texts(texts)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product (cosine sim with normalized vecs)
    index.add(embeddings)
    
    # Save index
    faiss.write_index(index, str(_index_path(paper_id)))
    
    # Save document texts + metadata alongside
    with open(_docs_path(paper_id), "wb") as f:
        pickle.dump(documents, f)
    
    return len(texts)


def load_index(paper_id: str):
    """Load a FAISS index and its documents from disk."""
    idx_path = _index_path(paper_id)
    doc_path = _docs_path(paper_id)
    
    if not idx_path.exists() or not doc_path.exists():
        raise FileNotFoundError(f"No index found for paper '{paper_id}'")
    
    index = faiss.read_index(str(idx_path))
    with open(doc_path, "rb") as f:
        documents = pickle.load(f)
    
    return index, documents


def delete_index(paper_id: str) -> bool:
    """Remove index files for a paper."""
    removed = False
    for path in [_index_path(paper_id), _docs_path(paper_id)]:
        if path.exists():
            path.unlink()
            removed = True
    return removed


def index_exists(paper_id: str) -> bool:
    """Check if an index exists for the given paper."""
    return _index_path(paper_id).exists() and _docs_path(paper_id).exists()


def similarity_search(query: str, paper_id: str, top_k: int = TOP_K) -> list[Document]:
    """Retrieve the most relevant chunks for a query."""
    index, documents = load_index(paper_id)
    
    query_embedding = embed_texts([query])
    scores, indices = index.search(query_embedding, min(top_k, len(documents)))
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(documents) and idx >= 0:
            doc = documents[idx]
            doc.metadata["relevance_score"] = float(score)
            results.append(doc)
    
    return results
