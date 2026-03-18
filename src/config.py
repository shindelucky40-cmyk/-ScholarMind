"""
ScholarMind Configuration
Centralized settings, API keys, and directory management.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Base Paths ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PAPERS_DIR = DATA_DIR / "papers"
INDICES_DIR = DATA_DIR / "indices"

# Create runtime directories
for d in [PAPERS_DIR, INDICES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── API Keys ────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── LLM Settings ────────────────────────────────────────────────────────
# Primary: Groq (fast, free, OpenAI-compatible)
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Fallback: Google Gemini
GEMINI_MODEL = "gemini-2.0-flash"

# ── Embedding Settings ─────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ── Chunking Settings ──────────────────────────────────────────────────
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ── Retrieval Settings ─────────────────────────────────────────────────
TOP_K = 5
