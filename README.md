# 📑 ScholarMind — RAG Research Paper Assistant

> **Ask intelligent questions about your research papers, powered by RAG.**

ScholarMind is an AI-powered research paper analysis tool that lets you upload PDFs and ask questions about them. It uses Retrieval-Augmented Generation (RAG) to provide accurate, cited answers directly from the paper content.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

- **📤 PDF Upload** — Drag-and-drop any research paper
- **🧠 Smart Indexing** — Automatic text extraction, chunking, and vector embedding
- **💬 Chat Interface** — Conversational Q&A with chat history
- **📎 Source Citations** — Every answer shows the exact paper excerpts used
- **⚡ Fast Retrieval** — FAISS vector similarity search for instant chunk matching
- **🔄 Auto-Fallback** — Groq primary → Gemini fallback for uninterrupted service
- **📚 Multi-Paper** — Upload and switch between multiple papers
- **🐳 Docker Ready** — One-command deployment

---

## 🏗️ Architecture

```
User Question
    │
    ▼
┌─────────────────┐
│  Streamlit UI   │  ← Chat interface
└────────┬────────┘
         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ Upload │ │   Question   │
│  PDF   │ │   Pipeline   │
└───┬────┘ └──────┬───────┘
    │              │
    ▼              ▼
┌────────────┐ ┌──────────────────┐
│  PyMuPDF   │ │ Sentence-BERT    │
│  Extract   │ │ Embed Query      │
└─────┬──────┘ └────────┬─────────┘
      │                  │
      ▼                  ▼
┌────────────┐ ┌──────────────────┐
│  Chunk     │ │ FAISS Similarity │
│  Text      │ │ Search (Top-K)   │
└─────┬──────┘ └────────┬─────────┘
      │                  │
      ▼                  ▼
┌────────────┐ ┌──────────────────┐
│ FAISS      │ │ Build Prompt     │
│ Index      │ │ + Context        │
└────────────┘ └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │ Groq LLM (Llama) │
               │ Generate Answer  │
               └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │  Answer + Cited  │
               │  Source Excerpts │
               └──────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| PDF Parsing | PyMuPDF (fitz) |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | FAISS (CPU) |
| LLM (Primary) | Groq API — Llama 3.3 70B |
| LLM (Fallback) | Google Gemini 2.0 Flash |
| Containerization | Docker |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Groq API key from [console.groq.com](https://console.groq.com) (free)
- *(Optional)* Gemini API key from [aistudio.google.com](https://aistudio.google.com) (free)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/scholarmind.git
cd scholarmind

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 5. Run the app
streamlit run app.py
```

The app will open at **http://localhost:8501**

### Docker Setup

```bash
# Build the image
docker build -t scholarmind .

# Run the container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_groq_key \
  -e GEMINI_API_KEY=your_gemini_key \
  scholarmind
```

---

## 📦 Deployment (HuggingFace Spaces)

1. Create a free account at [huggingface.co](https://huggingface.co)
2. Create a new Space → Select **Docker** SDK
3. Push your code to the Space's git repository
4. Set secrets in Space Settings:
   - `GROQ_API_KEY` = your Groq key
   - `GEMINI_API_KEY` = your Gemini key
5. Space will auto-build and deploy

---

## 📁 Project Structure

```
ScholarMind/
├── app.py                  # Streamlit entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Production container
├── .env.example            # Environment template
├── .streamlit/config.toml  # Streamlit theme config
├── src/
│   ├── config.py           # Settings & API key management
│   ├── pdf_processor.py    # PDF text extraction & chunking
│   ├── embeddings.py       # Embedding model & FAISS index
│   ├── rag_chain.py        # RAG pipeline (Groq → Gemini fallback)
│   └── paper_manager.py    # Paper upload/list/delete
└── data/
    ├── papers/             # Uploaded PDFs
    └── indices/            # FAISS index files
```

---

## 💡 Usage

1. **Upload** a research paper PDF using the sidebar
2. **Wait** for processing (text extraction + indexing)
3. **Ask** questions in the chat box, e.g.:
   - *"What is the main contribution of this paper?"*
   - *"Summarize the methodology"*
   - *"What datasets were used?"*
   - *"What are the limitations mentioned?"*
4. **View sources** — expand the citation panel under each answer

---

## 📊 Storage Requirements

| Item | Size |
|------|------|
| Dependencies | ~150 MB |
| Embedding model | ~80 MB |
| Docker image | ~400 MB |
| Per-paper index | ~2–5 MB |
| **Total** | **< 700 MB** |

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

<p align="center">
  Built with ❤️ using RAG · Groq AI · FAISS · Sentence Transformers
</p>
