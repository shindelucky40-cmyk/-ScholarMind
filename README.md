# ScholarMind

**A minimalist, AI-powered research assistant.**

ScholarMind lets you upload research papers (PDFs) and ask questions about them. It uses Retrieval-Augmented Generation (RAG) to instantly find relevant excerpts and generate accurate, cited answers.

---

### Stack
- **Frontend**: Streamlit
- **LLM**: Groq (Llama 3.3 70B) & Google Gemini (Fallback)
- **RAG**: LangChain, FAISS, Sentence Transformers
- **Parsing**: PyMuPDF

### Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/shindelucky40-cmyk/-ScholarMind.git
   cd -ScholarMind
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```
   *(Note: You can use your own free Groq API key directly in the app's sidebar).*

### Deployment (Docker)
A production-ready `Dockerfile` is included. It is optimized for size, using a CPU-only PyTorch installation.
```bash
docker build -t scholarmind .
docker run -p 8501:8501 scholarmind
```

---
*Built with RAG, FAISS, and Groq.*
