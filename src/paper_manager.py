"""
Paper Manager Module
Handles uploading, listing, deleting, and querying paper metadata.
"""
import json
import uuid
import time
from pathlib import Path
from datetime import datetime

from src.config import PAPERS_DIR, INDICES_DIR
from src.pdf_processor import process_pdf, get_page_count
from src.embeddings import create_index, delete_index, index_exists


METADATA_FILE = PAPERS_DIR / "_metadata.json"


def _load_metadata() -> dict:
    """Load the papers metadata file."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_metadata(metadata: dict):
    """Save the papers metadata file."""
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)


def save_paper(uploaded_file) -> dict:
    """Save an uploaded PDF, process it, and build vector index.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        dict with paper info (id, title, pages, chunks, etc.)
    """
    paper_id = str(uuid.uuid4())[:8]
    filename = uploaded_file.name
    pdf_path = PAPERS_DIR / f"{paper_id}_{filename}"
    
    # Save file to disk
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Process PDF → chunks
    documents = process_pdf(str(pdf_path), paper_id)
    
    # Build FAISS index
    num_chunks = create_index(documents, paper_id)
    
    # Get page count
    pages = get_page_count(str(pdf_path))
    
    # Store metadata
    paper_info = {
        "id": paper_id,
        "filename": filename,
        "filepath": str(pdf_path),
        "pages": pages,
        "chunks": num_chunks,
        "uploaded_at": datetime.now().isoformat(),
        "file_size_kb": round(pdf_path.stat().st_size / 1024, 1),
    }
    
    metadata = _load_metadata()
    metadata[paper_id] = paper_info
    _save_metadata(metadata)
    
    return paper_info


def list_papers() -> list[dict]:
    """Return list of all uploaded papers with metadata."""
    metadata = _load_metadata()
    papers = list(metadata.values())
    # Sort by upload time (newest first)
    papers.sort(key=lambda p: p.get("uploaded_at", ""), reverse=True)
    return papers


def delete_paper(paper_id: str) -> bool:
    """Remove a paper and its FAISS index.
    
    Returns True if successfully deleted.
    """
    metadata = _load_metadata()
    
    if paper_id not in metadata:
        return False
    
    paper_info = metadata[paper_id]
    
    # Delete PDF file
    pdf_path = Path(paper_info["filepath"])
    if pdf_path.exists():
        pdf_path.unlink()
    
    # Delete FAISS index
    delete_index(paper_id)
    
    # Remove from metadata
    del metadata[paper_id]
    _save_metadata(metadata)
    
    return True


def get_paper_info(paper_id: str) -> dict | None:
    """Get metadata for a specific paper."""
    metadata = _load_metadata()
    return metadata.get(paper_id)


def get_paper_count() -> int:
    """Return the number of uploaded papers."""
    return len(_load_metadata())
