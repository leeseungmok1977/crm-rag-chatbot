"""
CRM RAG Chatbot - Streamlit UI
POSCO International CRM Manual Chatbot
"""

import streamlit as st
import sys
import json
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
import os

from src.services.embedding_service import EmbeddingService
from src.services.vector_store import VectorStore, SearchResult
from src.rag.query_processor import QueryProcessor
from src.rag.generator import AnswerGenerator

# Page config
st.set_page_config(
    page_title="CRM Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with dark mode support
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }

    /* Dark mode header */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #64b5f6;
        }
    }

    /* Chat messages - Light mode */
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #1f77b4;
    }

    .assistant-message {
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        border-left: 4px solid #4caf50;
    }

    /* Dark mode chat messages */
    @media (prefers-color-scheme: dark) {
        .chat-message {
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .user-message {
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
            border-left: 4px solid #64b5f6;
        }

        .assistant-message {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            border-left: 4px solid #66bb6a;
        }
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .chat-message {
            padding: 0.8rem;
        }
    }

    /* Streamlit component improvements */
    .stExpander {
        border-radius: 0.5rem;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }

    @media (prefers-color-scheme: dark) {
        .stExpander {
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_services():
    """Initialize all services (cached)"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("❌ OPENAI_API_KEY not found in .env file")
        st.stop()

    # Initialize services
    embedding_service = EmbeddingService(
        model_name="openai/text-embedding-3-large",
        api_key=api_key,
        cache_enabled=True
    )

    vector_store = VectorStore(use_memory=True)
    query_processor = QueryProcessor()
    answer_generator = AnswerGenerator(api_key=api_key, model="gpt-4", temperature=0.3)

    return embedding_service, vector_store, query_processor, answer_generator


@st.cache_data
def load_chunks_from_json(processed_dir: str = "data/processed"):
    """Load chunks from JSON files (cached)"""
    processed_path = Path(processed_dir)
    chunks_by_collection = {}

    with st.spinner("📂 Loading chunks from JSON files..."):
        for json_file in processed_path.glob("*_chunks.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)

            # Extract collection name
            doc_id = json_file.stem.replace('_chunks', '')
            parts = doc_id.split('_')
            if len(parts) >= 4:
                collection_name = f"{parts[0]}_{parts[1]}_{parts[2]}"
            else:
                collection_name = doc_id

            if collection_name not in chunks_by_collection:
                chunks_by_collection[collection_name] = []

            chunks_by_collection[collection_name].extend(chunks)

    return chunks_by_collection


def setup_vector_store(vector_store, embedding_service, chunks_by_collection):
    """Setup vector store with chunks"""
    if 'vector_store_ready' not in st.session_state:
        with st.spinner("🔧 Setting up vector store..."):
            progress_bar = st.progress(0)
            total = len(chunks_by_collection)

            for idx, (collection_name, chunks) in enumerate(chunks_by_collection.items()):
                # Create collection
                vector_store.create_collection(
                    collection_name=collection_name,
                    vector_size=3072,
                    recreate=True
                )

                # Add embeddings
                chunk_texts = [chunk['text'] for chunk in chunks]
                embeddings = embedding_service.embed_batch(chunk_texts, show_progress=False)

                # Prepare data
                vector_chunks = []
                for chunk, embedding in zip(chunks, embeddings):
                    vector_chunk = {
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        "embedding": embedding,
                        "metadata": chunk["metadata"]
                    }
                    vector_chunks.append(vector_chunk)

                # Add to vector store
                vector_store.add_documents(
                    collection_name=collection_name,
                    chunks=vector_chunks,
                    show_progress=False
                )

                progress_bar.progress((idx + 1) / total)

            st.session_state.vector_store_ready = True


def perform_search(query: str, embedding_service, vector_store, query_processor, chunks_by_collection):
    """Perform vector search"""
    # Detect language
    language = query_processor.detect_language(query)
    lang_code = query_processor.get_language_code(language)

    # Generate query embedding
    query_embedding = embedding_service.embed_text(query)

    # Search in relevant collections
    all_results = []
    for collection_name in chunks_by_collection.keys():
        if f"_{lang_code}" in collection_name:
            results = vector_store.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                top_k=3,
                score_threshold=0.5
            )

            for result in results:
                result.metadata["collection"] = collection_name
                all_results.append(result)

    # Sort by score
    all_results.sort(key=lambda x: x.score, reverse=True)
    return all_results[:5], language


def main():
    """Main Streamlit app"""

    # Header
    st.markdown('<div class="main-header">💬 CRM Chatbot</div>', unsafe_allow_html=True)
    st.markdown("**POSCO International CRM Manual Assistant**")

    # Initialize services
    embedding_service, vector_store, query_processor, answer_generator = initialize_services()

    # Load chunks
    chunks_by_collection = load_chunks_from_json()

    # Setup vector store
    setup_vector_store(vector_store, embedding_service, chunks_by_collection)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Model selection
        model = st.selectbox(
            "LLM Model",
            ["gpt-4", "gpt-3.5-turbo"],
            index=0
        )
        answer_generator.model = model

        # Temperature
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
        answer_generator.temperature = temperature

        st.divider()

        # Statistics
        st.header("📊 Statistics")
        total_chunks = sum(len(chunks) for chunks in chunks_by_collection.values())
        st.metric("Total Documents", len(chunks_by_collection))
        st.metric("Total Chunks", total_chunks)

        if 'chat_history' in st.session_state:
            st.metric("Queries", len([m for m in st.session_state.chat_history if m['role'] == 'user']))

        st.divider()

        # Clear chat
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        role = message['role']
        content = message['content']

        if role == 'user':
            st.markdown(f'<div class="chat-message user-message"><b>🙋 You:</b><br>{content}</div>',
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message"><b>🤖 Assistant:</b><br>{content}</div>',
                       unsafe_allow_html=True)

            # Display sources if available
            if 'sources' in message and message['sources']:
                with st.expander("📚 관련 문서 출처", expanded=False):
                    for source in message['sources']:
                        doc_type = source['type'].replace('_', ' ').title()
                        st.markdown(f"""
                        **[문서 {source['index']}]** {doc_type}
                        - 출처: {source['document_id']}
                        - 언어: {source['language']}

                        **내용 미리보기:**
                        > {source['text_preview']}
                        """)
                        st.divider()

    # Chat input
    user_query = st.chat_input("질문을 입력하세요 / Enter your question...")

    if user_query:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })

        # Display user message immediately
        st.markdown(f'<div class="chat-message user-message"><b>🙋 You:</b><br>{user_query}</div>',
                   unsafe_allow_html=True)

        # Perform search
        with st.spinner("🔍 Searching..."):
            search_results, language = perform_search(
                user_query,
                embedding_service,
                vector_store,
                query_processor,
                chunks_by_collection
            )

        if search_results:
            # Generate answer
            with st.spinner("💭 Generating answer..."):
                response = answer_generator.generate_answer(
                    query=user_query,
                    search_results=search_results,
                    language=language
                )

            # Add assistant message
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response['answer'],
                'sources': response['sources']
            })

            # Rerun to update display
            st.rerun()
        else:
            # No results
            no_result_msg = (
                "죄송합니다. 질문과 관련된 내용을 매뉴얼에서 찾을 수 없습니다."
                if language == "korean"
                else "I'm sorry, I couldn't find relevant information in the manuals."
            )

            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': no_result_msg,
                'sources': []
            })

            st.rerun()


if __name__ == "__main__":
    main()
