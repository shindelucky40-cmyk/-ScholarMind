"""
RAG Chain Module
Retrieval-Augmented Generation pipeline.
Primary LLM: Groq (Llama 3.3 70B) — fast & free.
Fallback LLM: Google Gemini — if Groq hits rate limits.
"""
import google.generativeai as genai
from openai import OpenAI
from src.config import (
    GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL,
    GEMINI_API_KEY, GEMINI_MODEL, TOP_K,
)
from src.embeddings import similarity_search


# ── System Prompt ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are ScholarMind, an expert research paper analyst. Your job is to answer questions about uploaded research papers accurately and insightfully.

Rules:
1. ONLY answer based on the provided context from the paper. Do not use your own knowledge.
2. If the context doesn't contain enough information to answer, say: "I couldn't find enough information in this paper to answer that question. Try rephrasing or asking about a different aspect."
3. When referencing information, mention the page number if available (e.g., "According to Page 3...").
4. Be concise but thorough. Use bullet points for complex answers.
5. If the question asks for a summary, provide a structured summary with key findings, methodology, and conclusions.
6. Use academic tone but keep it accessible.
"""


def _build_context(chunks) -> str:
    """Format retrieved chunks into a context string."""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        page_info = ""
        content = chunk.page_content
        if content.startswith("[Page"):
            parts = content.split("]\n", 1)
            if len(parts) > 1:
                page_info = f" ({parts[0]}])"
                content = parts[1]

        score = chunk.metadata.get("relevance_score", 0)
        context_parts.append(
            f"--- Excerpt {i}{page_info} (relevance: {score:.2f}) ---\n{content}"
        )
    return "\n\n".join(context_parts)


def _build_user_message(question: str, context: str) -> str:
    return f"""Context from the research paper:

{context}

---

Question: {question}

Please provide a clear, well-structured answer based on the context above."""


def _call_groq(messages: list, user_api_key: str = None) -> str:
    """Call Groq API (OpenAI-compatible)."""
    active_key = user_api_key if user_api_key else GROQ_API_KEY
    if not active_key:
        raise ValueError("No Groq API key found. Please provide one in the sidebar.")
        
    client = OpenAI(
        api_key=active_key,
        base_url=GROQ_BASE_URL,
    )
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=1500,
    )
    return response.choices[0].message.content


def _call_gemini(messages: list) -> str:
    """Call Google Gemini API as fallback."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    # Convert OpenAI-style messages to Gemini format
    prompt_parts = []
    for msg in messages:
        if msg["role"] == "system":
            prompt_parts.append(f"System Instructions:\n{msg['content']}\n\n")
        elif msg["role"] == "user":
            prompt_parts.append(f"User: {msg['content']}\n\n")
        elif msg["role"] == "assistant":
            prompt_parts.append(f"Assistant: {msg['content']}\n\n")

    full_prompt = "".join(prompt_parts)
    response = model.generate_content(full_prompt)
    return response.text


def _call_llm(messages: list, user_api_key: str = None) -> tuple[str, str]:
    """Try Groq first, fall back to Gemini. Returns (answer, provider_name)."""
    # Try Groq first (faster, higher limits)
    active_groq_key = user_api_key if user_api_key else GROQ_API_KEY
    
    if active_groq_key:
        try:
            answer = _call_groq(messages, user_api_key=active_groq_key)
            return answer, f"Groq ({GROQ_MODEL})"
        except Exception as e:
            err = str(e)
            # If rate limited, fall through to Gemini (only if NOT using a custom API key, custom keys shouldn't arbitrarily fallback without user awareness)
            if ("rate_limit" not in err.lower() and "429" not in err) or user_api_key:
                raise  # Re-raise non-rate-limit errors OR if using custom key

    # Fallback to Gemini
    if GEMINI_API_KEY:
        try:
            answer = _call_gemini(messages)
            return answer, f"Gemini ({GEMINI_MODEL})"
        except Exception:
            raise

    raise ValueError("No working LLM API key configured. Set GROQ_API_KEY or GEMINI_API_KEY in .env")


def ask_question(question: str, paper_id: str, top_k: int = TOP_K) -> dict:
    """Full RAG pipeline: retrieve → prompt → LLM → structured answer."""

    chunks = similarity_search(question, paper_id, top_k)

    if not chunks:
        return {
            "answer": "No relevant information found in the paper for this question.",
            "sources": [],
            "model": "N/A",
        }

    context = _build_context(chunks)
    user_message = _build_user_message(question, context)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    answer, model_used = _call_llm(messages)

    sources = []
    for chunk in chunks:
        sources.append({
            "text": chunk.page_content[:300] + ("..." if len(chunk.page_content) > 300 else ""),
            "relevance": round(chunk.metadata.get("relevance_score", 0), 3),
            "chunk_index": chunk.metadata.get("chunk_index", -1),
        })

    return {"answer": answer, "sources": sources, "model": model_used}


def get_chat_response(question: str, paper_id: str, chat_history: list = None, top_k: int = TOP_K, user_api_key: str = None) -> dict:
    """Conversational RAG with chat history context."""

    chunks = similarity_search(question, paper_id, top_k)

    if not chunks:
        return {
            "answer": "No relevant information found in the paper for this question.",
            "sources": [],
            "model": "N/A",
        }

    context = _build_context(chunks)
    user_message = _build_user_message(question, context)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    answer, model_used = _call_llm(messages, user_api_key=user_api_key)

    sources = []
    for chunk in chunks:
        sources.append({
            "text": chunk.page_content[:300] + ("..." if len(chunk.page_content) > 300 else ""),
            "relevance": round(chunk.metadata.get("relevance_score", 0), 3),
            "chunk_index": chunk.metadata.get("chunk_index", -1),
        })

    return {"answer": answer, "sources": sources, "model": model_used}
