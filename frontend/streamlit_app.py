"""Main Streamlit application for NotebookLM-style RAG chat."""

import sys
from pathlib import Path

import streamlit as st
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services import (
    SessionManager,
    DocumentService,
    ChatService,
)


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="📚 RAG Chat",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

@st.cache_resource
def get_services():
    """Initialize and cache services."""
    manager = SessionManager(sessions_dir="sessions")
    doc_service = DocumentService(manager)
    chat_service = ChatService(manager)
    return manager, doc_service, chat_service


manager, doc_service, chat_service = get_services()

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed" not in st.session_state:
    st.session_state.indexed = False


# ============================================================================
# SIDEBAR - SESSION MANAGEMENT
# ============================================================================

with st.sidebar:
    st.header("📁 Session Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ New Session", use_container_width=True):
            st.session_state.session_id = manager.create_session()
            st.session_state.messages = []
            st.session_state.indexed = False
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Session info
    if st.session_state.session_id:
        st.markdown("---")
        st.subheader("Current Session")
        
        session_id_display = st.session_state.session_id[:12] + "..."
        st.code(session_id_display, language="text")
        
        # Session details
        try:
            context = chat_service.get_session_context(st.session_state.session_id)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", len(context["documents"]))
                st.metric("Chunks", context["indexed_chunks"])
            
            with col2:
                st.metric("Messages", context["messages_count"])
                size_mb = context["total_size_bytes"] / (1024 * 1024)
                st.metric("Size", f"{size_mb:.1f} MB")
            
            # Delete session
            if st.button("🗑️ Delete Session", use_container_width=True):
                manager.delete_session(st.session_state.session_id)
                st.session_state.session_id = None
                st.session_state.messages = []
                st.session_state.indexed = False
                st.rerun()
        
        except Exception as e:
            st.error(f"Error loading session: {e}")
    
    else:
        st.info("👈 Create a new session to get started!")


# ============================================================================
# MAIN CONTENT
# ============================================================================

if not st.session_state.session_id:
    st.title("📚 RAG Chat")
    st.markdown("### Welcome!")
    st.markdown(
        """
        This is a local RAG (Retrieval-Augmented Generation) chat interface.
        
        **Features:**
        - 📄 Upload your own documents (PDF, TXT, MD, HTML)
        - 🔍 Ask questions about your documents
        - 📖 See source citations
        - 💾 Session-based isolation
        - ⚡ Fast local inference with LM Studio
        
        **Getting Started:**
        1. Click "➕ New Session" in the sidebar
        2. Upload documents
        3. Start asking questions!
        """
    )
    st.warning("👈 Create a new session to begin")

else:
    # Main content with two columns
    col_docs, col_chat = st.columns([1, 2])
    
    # ======================================================================
    # LEFT COLUMN - DOCUMENT MANAGEMENT
    # ======================================================================
    
    with col_docs:
        st.subheader("📄 Documents")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=["pdf", "txt", "md", "html"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.session_id}",
        )
        
        if uploaded_files:
            if st.button("⬆️ Upload & Index", use_container_width=True):
                with st.spinner("Uploading and indexing documents..."):
                    try:
                        # Upload
                        upload_result = doc_service.upload_documents(
                            st.session_state.session_id,
                            uploaded_files
                        )
                        
                        if upload_result["errors"]:
                            for error in upload_result["errors"]:
                                st.error(f"Error: {error['error']}")
                        
                        # Index
                        index_result = doc_service.index_session(st.session_state.session_id)
                        
                        if index_result["status"] == "success":
                            st.session_state.indexed = True
                            st.success(
                                f"✅ Indexed {index_result['chunks_indexed']} chunks "
                                f"from {len(index_result['documents_indexed'])} documents"
                            )
                        else:
                            st.error(f"Indexing failed: {index_result['error']}")
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        # Document list
        st.markdown("---")
        st.subheader("Indexed Documents")
        
        try:
            doc_info = doc_service.get_document_info(st.session_state.session_id)
            
            if doc_info["documents"]:
                for doc in doc_info["documents"]:
                    size_kb = doc["size_bytes"] / 1024
                    st.markdown(f"📄 **{doc['filename']}** ({size_kb:.1f} KB)")
                
                st.caption(f"Total: {doc_info['document_count']} files")
            else:
                st.info("No documents uploaded yet")
        
        except Exception as e:
            st.error(f"Error loading documents: {e}")
    
    # ======================================================================
    # RIGHT COLUMN - CHAT INTERFACE
    # ======================================================================
    
    with col_chat:
        st.subheader("💬 Chat")
        
        if not st.session_state.indexed:
            st.warning("⚠️ Upload and index documents first to start chatting")
        
        # Chat messages container
        chat_container = st.container(height=400, border=True)
        
        with chat_container:
            if st.session_state.messages:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        if "sources" in msg and msg["sources"]:
                            with st.expander(f"📖 Sources ({len(msg['sources'])})"):
                                for source in msg["sources"]:
                                    st.caption(f"• {source}")
            else:
                st.info("Start a conversation!")
        
        # Chat input
        st.markdown("---")
        
        if st.session_state.indexed:
            query = st.chat_input(
                "Ask a question about your documents...",
                disabled=False
            )
            
            if query:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": query
                })
                
                with st.spinner("🤔 Thinking..."):
                    try:
                        # Query the RAG pipeline
                        result = chat_service.query(
                            st.session_state.session_id,
                            query
                        )
                        
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            # Add assistant message
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["answer"],
                                "sources": result["sources"]
                            })
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                st.rerun()
        
        else:
            st.chat_input(
                "Upload documents first...",
                disabled=True
            )


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 12px;'>
    Local RAG with LM Studio • Session-based isolation • Powered by ChromaDB & BGE Embeddings
    </div>
    """,
    unsafe_allow_html=True
)
