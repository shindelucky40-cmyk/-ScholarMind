# 📑 ScholarMind

A RAG-powered research paper Q&A assistant. Upload a PDF, ask questions, and get answers grounded strictly in the paper's content — with source excerpts and relevance scores.

---

## Features

- Upload research papers as PDFs and auto-index them
- Conversational Q&A with multi-turn chat history
- Every answer includes cited source excerpts with relevance scores
- Powered by **Groq (Llama 3.3 70B)** — free and fast
- Bring your own Groq API key via the sidebar at runtime

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| PDF Parsing | PyMuPDF (fitz) |
| Chunking | LangChain `RecursiveCharacterTextSplitter` |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` |
| Vector Store | FAISS (CPU) |
| LLM | Groq — `llama-3.3-70b-versatile` |

---

## Project Structure

```
scholar mind/
├── app.py                  # Streamlit UI — sidebar, chat, paper management
├── src/
│   ├── config.py           # Paths, API keys, model and chunking settings
│   ├── pdf_processor.py    # PDF text extraction and chunk splitting
│   ├── embeddings.py       # FAISS index creation, storage, and similarity search
│   ├── paper_manager.py    # Upload, list, delete papers + JSON metadata store
│   └── rag_chain.py        # RAG pipeline — retrieval, prompt building, LLM call
├── data/
│   ├── papers/             # Uploaded PDFs and _metadata.json
│   └── indices/            # FAISS .faiss and .pkl files per paper
├── requirements.txt
└── .env.example
```

---

## Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/shindelucky40-cmyk/-ScholarMind
cd "scholar mind"
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

> Uses CPU-only PyTorch to keep the install size small.

**3. Set up your API key**
```bash
cp .env.example .env
```

Open `.env` and add your key:
```
GROQ_API_KEY=your_groq_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

**4. Run**
```bash
streamlit run app.py
```

---

## How It Works

```
Upload PDF  →  Extract text (PyMuPDF)  →  Split into chunks  →  Embed + store in FAISS
                                                                          ↓
Ask question  →  Embed query  →  Top-5 similarity search  →  Build prompt  →  Groq LLM  →  Answer + sources
```

- Chunks: 1000 characters with 200-character overlap
- Embeddings: cosine similarity via FAISS `IndexFlatIP` on normalized vectors
- LLM context: up to last 6 messages of chat history included per request
- LLM is instructed to answer **only** from retrieved context — no hallucination from general knowledge
