"""
PDF Processing Module
Extracts text from PDFs and splits into overlapping chunks.
"""
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text_parts = []
    for page_num, page in enumerate(doc, 1):
        page_text = page.get_text("text")
        if page_text.strip():
            text_parts.append(f"[Page {page_num}]\n{page_text}")
    doc.close()
    return "\n\n".join(text_parts)


def get_page_count(pdf_path: str) -> int:
    """Return the number of pages in a PDF."""
    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count


def chunk_text(text: str, metadata: dict = None) -> list[Document]:
    """Split text into overlapping chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    chunks = splitter.split_text(text)
    documents = []
    for i, chunk in enumerate(chunks):
        doc_metadata = {"chunk_index": i, "total_chunks": len(chunks)}
        if metadata:
            doc_metadata.update(metadata)
        documents.append(Document(page_content=chunk, metadata=doc_metadata))
    
    return documents


def process_pdf(pdf_path: str, paper_id: str = None) -> list[Document]:
    """Full pipeline: extract text → chunk → return Document objects."""
    text = extract_text(pdf_path)
    if not text.strip():
        raise ValueError("Could not extract any text from the PDF. The file may be scanned/image-based.")
    
    metadata = {"source": pdf_path}
    if paper_id:
        metadata["paper_id"] = paper_id
    
    return chunk_text(text, metadata)
