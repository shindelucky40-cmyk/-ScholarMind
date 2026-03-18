"""
ScholarMind — Research Paper Q&A Assistant
A RAG-powered tool for intelligent research paper analysis.
"""
import streamlit as st
import time
import html
from pathlib import Path

# ── Page Config (MUST be first Streamlit call) ─────────────────────────
st.set_page_config(
    page_title="ScholarMind",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.paper_manager import save_paper, list_papers, delete_paper, get_paper_info
from src.rag_chain import get_chat_response


# ── Custom CSS ─────────────────────────────────────────────────────────
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ── Global ── */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ── Hide Streamlit defaults ── */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* ── Sidebar styling ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: #c8ccd4 !important;
        font-size: 0.88rem;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e8ecf4 !important;
    }
    
    /* ── Main content area ── */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* ── Header component ── */
    .app-header {
        text-align: center;
        padding: 1.5rem 0 1rem;
        margin-bottom: 1rem;
    }
    .app-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }
    .app-header .subtitle {
        color: #8b95a5;
        font-size: 0.95rem;
        font-weight: 400;
        letter-spacing: 0.2px;
    }
    
    /* ── Paper card ── */
    .paper-card {
        background: linear-gradient(135deg, rgba(30, 35, 50, 0.8), rgba(25, 30, 45, 0.9));
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    .paper-card:hover {
        border-color: rgba(102, 126, 234, 0.35);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.08);
    }
    .paper-card .paper-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: #e0e4ec;
        margin-bottom: 0.3rem;
        line-height: 1.3;
    }
    .paper-card .paper-meta {
        font-size: 0.75rem;
        color: #6b7280;
        display: flex;
        gap: 1rem;
    }
    .paper-card .paper-meta span {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    /* ── Chat messages ── */
    .chat-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.9rem 1.2rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        max-width: 85%;
        margin-left: auto;
        font-size: 0.92rem;
        line-height: 1.5;
        box-shadow: 0 2px 12px rgba(102, 126, 234, 0.2);
    }
    .chat-assistant {
        background: rgba(30, 35, 50, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        color: #d1d5db;
        padding: 1rem 1.3rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        max-width: 90%;
        font-size: 0.92rem;
        line-height: 1.6;
    }
    
    /* ── Source citation badge ── */
    .source-badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.12);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        margin: 0.3rem 0;
        font-size: 0.8rem;
        color: #9ca3af;
        line-height: 1.4;
    }
    .source-badge .source-score {
        color: #667eea;
        font-weight: 600;
        font-size: 0.72rem;
    }
    
    /* ── Status indicator ── */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.25);
        color: #4ade80;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 3rem 1.5rem;
        color: #6b7280;
    }
    .empty-state .icon {
        font-size: 3rem;
        margin-bottom: 0.75rem;
        opacity: 0.5;
    }
    .empty-state h3 {
        color: #9ca3af;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }
    .empty-state p {
        font-size: 0.88rem;
        line-height: 1.5;
    }
    
    /* ── File uploader refinement ── */
    section[data-testid="stFileUploader"] {
        border-radius: 12px;
    }
    
    /* ── Button refinement ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        letter-spacing: 0.2px;
    }
    
    /* ── Divider ── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.2), transparent);
        margin: 1rem 0;
    }
    
    /* ── Info bar ── */
    .info-bar {
        background: rgba(102, 126, 234, 0.06);
        border: 1px solid rgba(102, 126, 234, 0.12);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        font-size: 0.82rem;
        color: #8b95a5;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(102, 126, 234, 0.2); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(102, 126, 234, 0.4); }
    
    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #8b95a5 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ── Session State Initialization ───────────────────────────────────────
def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_paper" not in st.session_state:
        st.session_state.selected_paper = None
    if "processing" not in st.session_state:
        st.session_state.processing = False


# ── Sidebar ────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo / branding
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 0.5rem;">
            <div style="font-size: 2.2rem; margin-bottom: 0.15rem;">📑</div>
            <div style="font-size: 1.3rem; font-weight: 700; 
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ScholarMind
            </div>
            <div style="font-size: 0.72rem; color: #6b7280; letter-spacing: 1.5px; 
                        text-transform: uppercase; margin-top: 0.15rem;">
                Research Paper AI
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # ── Upload Section ──
        st.markdown("### 📤 Upload Paper")
        uploaded_file = st.file_uploader(
            "Drop a PDF here",
            type=["pdf"],
            help="Upload a research paper in PDF format",
            label_visibility="collapsed",
        )
        
        if uploaded_file is not None:
            if st.button("⚡ Process Paper", use_container_width=True, type="primary"):
                with st.spinner("Extracting text & building index..."):
                    try:
                        paper_info = save_paper(uploaded_file)
                        st.session_state.selected_paper = paper_info["id"]
                        st.session_state.chat_history = []
                        st.success(f"✓ Indexed **{paper_info['filename']}** — {paper_info['chunks']} chunks from {paper_info['pages']} pages")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to process: {e}")
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # ── Papers List ──
        papers = list_papers()
        st.markdown(f"### 📚 Your Papers ({len(papers)})")
        
        if not papers:
            st.markdown("""
            <div style="text-align:center; padding: 1.5rem 0; color: #4b5563; font-size: 0.85rem;">
                <div style="font-size: 1.5rem; opacity: 0.4; margin-bottom: 0.3rem;">📂</div>
                No papers yet.<br>Upload one above.
            </div>
            """, unsafe_allow_html=True)
        else:
            for paper in papers:
                pid = paper["id"]
                is_selected = st.session_state.selected_paper == pid
                
                # Paper card
                border_color = "rgba(102, 126, 234, 0.5)" if is_selected else "rgba(255,255,255,0.06)"
                bg = "rgba(102, 126, 234, 0.08)" if is_selected else "rgba(30, 35, 50, 0.5)"
                
                truncated_name = paper["filename"][:35] + ("..." if len(paper["filename"]) > 35 else "")
                
                st.markdown(f"""
                <div class="paper-card" style="border-color: {border_color}; background: {bg}; cursor: pointer;">
                    <div class="paper-title">{'🔹 ' if is_selected else ''}{truncated_name}</div>
                    <div class="paper-meta">
                        <span>📄 {paper['pages']} pages</span>
                        <span>🧩 {paper['chunks']} chunks</span>
                        <span>💾 {paper['file_size_kb']} KB</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"Select", key=f"sel_{pid}", use_container_width=True,
                                 type="primary" if is_selected else "secondary"):
                        st.session_state.selected_paper = pid
                        st.session_state.chat_history = []
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{pid}", use_container_width=True):
                        delete_paper(pid)
                        if st.session_state.selected_paper == pid:
                            st.session_state.selected_paper = None
                            st.session_state.chat_history = []
                        st.rerun()
        
        # Footer
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; padding: 0.5rem 0; font-size: 0.7rem; color: #4b5563;">
            Built with ❤️ using RAG<br>
            <span style="color: #667eea;">Groq AI</span> · FAISS · Sentence Transformers
        </div>
        """, unsafe_allow_html=True)


# ── Main Chat Area ─────────────────────────────────────────────────────
def render_chat():
    # Header
    st.markdown("""
    <div class="app-header">
        <h1>📑 ScholarMind</h1>
        <div class="subtitle">Ask anything about your research papers — powered by RAG</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if a paper is selected
    if not st.session_state.selected_paper:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🔬</div>
            <h3>No paper selected</h3>
            <p>Upload and select a research paper from the sidebar to start asking questions.<br>
            ScholarMind will analyze the paper and answer your questions using RAG.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick feature overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style="text-align:center; padding: 1.5rem; background: rgba(30,35,50,0.5); 
                        border-radius: 12px; border: 1px solid rgba(255,255,255,0.04);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📤</div>
                <div style="font-weight: 600; color: #e0e4ec; font-size: 0.9rem; margin-bottom: 0.25rem;">Upload</div>
                <div style="color: #6b7280; font-size: 0.78rem;">Drop any research paper PDF</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="text-align:center; padding: 1.5rem; background: rgba(30,35,50,0.5); 
                        border-radius: 12px; border: 1px solid rgba(255,255,255,0.04);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🧠</div>
                <div style="font-weight: 600; color: #e0e4ec; font-size: 0.9rem; margin-bottom: 0.25rem;">Analyze</div>
                <div style="color: #6b7280; font-size: 0.78rem;">AI indexes every section</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div style="text-align:center; padding: 1.5rem; background: rgba(30,35,50,0.5); 
                        border-radius: 12px; border: 1px solid rgba(255,255,255,0.04);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💬</div>
                <div style="font-weight: 600; color: #e0e4ec; font-size: 0.9rem; margin-bottom: 0.25rem;">Ask</div>
                <div style="color: #6b7280; font-size: 0.78rem;">Get cited, accurate answers</div>
            </div>
            """, unsafe_allow_html=True)
        return
    
    # Paper info bar
    paper_info = get_paper_info(st.session_state.selected_paper)
    if paper_info:
        truncated = paper_info["filename"][:50] + ("..." if len(paper_info["filename"]) > 50 else "")
        st.markdown(f"""
        <div class="info-bar">
            <span style="font-size: 1rem;">📄</span>
            <strong style="color: #c8ccd4;">{truncated}</strong>
            <span style="margin-left: auto;">
                {paper_info['pages']} pages · {paper_info['chunks']} chunks
            </span>
            <span class="status-pill">● Ready</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align:center; padding: 2rem 0; color: #6b7280;">
                <div style="font-size: 1.8rem; opacity: 0.4; margin-bottom: 0.5rem;">💭</div>
                <p style="font-size: 0.9rem;">Ask your first question about this paper</p>
                <p style="font-size: 0.78rem; color: #4b5563; margin-top: 0.3rem;">
                    Try: "What is the main contribution of this paper?" or "Summarize the methodology"
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    safe_content = html.escape(msg["content"])
                    st.markdown(f'<div class="chat-user">{safe_content}</div>', unsafe_allow_html=True)
                else:
                    safe_content = msg["content"].replace("<script", "&lt;script").replace("</script", "&lt;/script")
                    st.markdown(f'<div class="chat-assistant">{safe_content}</div>', unsafe_allow_html=True)
                    
                    # Show sources in expander
                    if "sources" in msg and msg["sources"]:
                        with st.expander(f"📎 View {len(msg['sources'])} source excerpts", expanded=False):
                            for i, src in enumerate(msg["sources"], 1):
                                st.markdown(f"""
                                <div class="source-badge">
                                    <span class="source-score">Relevance: {src['relevance']}</span><br>
                                    {src['text'][:250]}{'...' if len(src['text']) > 250 else ''}
                                </div>
                                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    question = st.chat_input("Ask a question about the paper...")
    
    if question:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        # Build chat history for context
        api_history = []
        for msg in st.session_state.chat_history[:-1]:  # Exclude current question
            if msg["role"] == "user":
                api_history.append({"role": "user", "content": msg["content"]})
            else:
                api_history.append({"role": "assistant", "content": msg["content"]})
        
        with st.spinner("🔍 Searching paper & generating answer..."):
            try:
                result = get_chat_response(
                    question=question,
                    paper_id=st.session_state.selected_paper,
                    chat_history=api_history if api_history else None,
                )
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                })
            except Exception as e:
                error_msg = str(e)
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "⏳ Rate limit reached. Please wait a moment and try again.",
                        "sources": [],
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"❌ Something went wrong: {error_msg}",
                        "sources": [],
                    })
        
        st.rerun()


# ── Main App ───────────────────────────────────────────────────────────
def main():
    inject_custom_css()
    init_session_state()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
