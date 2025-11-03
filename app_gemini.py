"""
CRM RAG Chatbot - Gemini Style UI
POSCO International CRM Manual Chatbot
"""

import streamlit as st
import sys
import json
from pathlib import Path
from typing import List, Dict
from collections import Counter
import time
from datetime import datetime

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
    initial_sidebar_state="collapsed"
)

# Gemini-style CSS
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container */
    .main {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Welcome screen */
    .welcome-screen {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem 1rem 1rem;
        margin-top: 5vh;
    }

    .welcome-title {
        font-size: 2.5rem;
        font-weight: 400;
        color: #4285f4;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .welcome-subtitle {
        font-size: 1.1rem;
        color: #80868b;
        margin-bottom: 2rem;
        text-align: center;
    }

    /* Search box */
    .stTextInput > div > div > input {
        border-radius: 2rem !important;
        padding: 1.2rem 2rem !important;
        font-size: 1.1rem !important;
        border: 1px solid #dadce0 !important;
        box-shadow: 0 1px 6px rgba(32,33,36,.28) !important;
        min-width: 500px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #4285f4 !important;
        box-shadow: 0 1px 6px rgba(66,133,244,.3) !important;
    }

    /* Popular queries */
    .popular-queries {
        margin-top: 1.5rem;
        padding: 0 1rem;
        max-width: 900px;
        width: 100%;
    }

    .popular-queries-title {
        font-size: 0.9rem;
        color: #5f6368;
        margin-bottom: 0.8rem;
        font-weight: 500;
        text-align: center;
    }

    .query-chip {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        margin: 0.4rem 0.4rem;
        border-radius: 2rem;
        border: 1px solid #dadce0;
        background: #ffffff;
        color: #202124;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.9rem;
    }

    .query-chip:hover {
        background: #f8f9fa;
        border-color: #4285f4;
        box-shadow: 0 1px 3px rgba(60,64,67,.3);
    }

    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .welcome-title {
            color: #8ab4f8;
        }

        .welcome-subtitle {
            color: #9aa0a6;
        }

        .query-chip {
            background: #303134;
            color: #e8eaed;
            border-color: #5f6368;
        }

        .query-chip:hover {
            background: #3c4043;
            border-color: #8ab4f8;
        }

        .stTextInput > div > div > input {
            background: #303134 !important;
            color: #e8eaed !important;
            border-color: #5f6368 !important;
        }
    }

    /* Chat messages */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        max-width: 800px;
    }

    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        margin-left: auto;
        border-left: 4px solid #4285f4;
    }

    .assistant-message {
        background: #f8f9fa;
        border-left: 4px solid #34a853;
    }

    @media (prefers-color-scheme: dark) {
        .user-message {
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
            border-left-color: #8ab4f8;
        }

        .assistant-message {
            background: #303134;
            border-left-color: #81c995;
        }
    }

    /* Compact header */
    .compact-header {
        padding: 1rem 2rem;
        border-bottom: 1px solid #e8eaed;
        margin-bottom: 1rem;
    }

    @media (prefers-color-scheme: dark) {
        .compact-header {
            border-bottom-color: #3c4043;
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

    for json_file in processed_path.glob("*_chunks.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

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


def get_popular_queries():
    """Get top 5 popular queries from history"""
    history_file = Path("data/query_history.json")

    if not history_file.exists():
        return [
            "거래선 등록 방법",
            "미팅메모 작성하는 방법",
            "주문 승인 프로세스",
            "연락처 관리 방법",
            "계약 정보 입력"
        ]

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

        query_counts = Counter(history.get('queries', []))
        popular = [query for query, count in query_counts.most_common(5)]

        if len(popular) < 5:
            defaults = ["거래선 등록 방법", "미팅메모 작성하는 방법", "주문 승인 프로세스", "연락처 관리 방법", "계약 정보 입력"]
            popular.extend(defaults[:5-len(popular)])

        return popular[:5]
    except:
        return ["거래선 등록 방법", "미팅메모 작성하는 방법", "주문 승인 프로세스", "연락처 관리 방법", "계약 정보 입력"]


def save_query_history(query: str):
    """Save query to history for statistics"""
    history_file = Path("data/query_history.json")
    history_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {'queries': [], 'timestamps': []}

        history['queries'].append(query)
        history['timestamps'].append(time.strftime('%Y-%m-%d %H:%M:%S'))

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving query history: {e}")


def setup_vector_store(vector_store, embedding_service, chunks_by_collection):
    """Setup vector store with chunks"""
    if 'vector_store_ready' not in st.session_state:
        with st.spinner("🔧 초기화 중..."):
            for collection_name, chunks in chunks_by_collection.items():
                vector_store.create_collection(
                    collection_name=collection_name,
                    vector_size=3072,
                    recreate=True
                )

                chunk_texts = [chunk['text'] for chunk in chunks]
                embeddings = embedding_service.embed_batch(chunk_texts, show_progress=False)

                vector_chunks = []
                for chunk, embedding in zip(chunks, embeddings):
                    vector_chunk = {
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        "embedding": embedding,
                        "metadata": chunk["metadata"]
                    }
                    vector_chunks.append(vector_chunk)

                vector_store.add_documents(
                    collection_name=collection_name,
                    chunks=vector_chunks,
                    show_progress=False
                )

            st.session_state.vector_store_ready = True


def perform_search(query: str, embedding_service, vector_store, query_processor, chunks_by_collection):
    """Perform vector search"""
    language = query_processor.detect_language(query)
    lang_code = query_processor.get_language_code(language)

    query_embedding = embedding_service.embed_text(query)

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

    all_results.sort(key=lambda x: x.score, reverse=True)
    return all_results[:5], language


def main():
    """Main Streamlit app"""

    # Initialize services
    embedding_service, vector_store, query_processor, answer_generator = initialize_services()
    chunks_by_collection = load_chunks_from_json()
    setup_vector_store(vector_store, embedding_service, chunks_by_collection)

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Show welcome screen or chat mode
    if len(st.session_state.chat_history) == 0:
        # Welcome screen
        st.markdown("""
        <div class="welcome-screen">
            <h1 class="welcome-title">안녕하세요. CRM AI chatbot 입니다.</h1>
            <p class="welcome-subtitle">무엇을 도와드릴까요?</p>
        </div>
        """, unsafe_allow_html=True)

        # Search box (centered)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            user_query = st.text_input(
                "질문을 입력하세요",
                placeholder="CRM에 대해 물어보세요...",
                label_visibility="collapsed",
                key="welcome_search"
            )

        # Popular queries
        st.markdown('<div class="popular-queries" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<p class="popular-queries-title">💡 인기 질문</p>', unsafe_allow_html=True)

        popular_queries = get_popular_queries()

        # Display as chips
        cols = st.columns(len(popular_queries))
        for idx, (col, query) in enumerate(zip(cols, popular_queries)):
            with col:
                if st.button(query, key=f"popular_{idx}", use_container_width=True):
                    user_query = query

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Chat mode - compact header
        st.markdown("""
        <div class="compact-header">
            <h2 style="margin: 0; color: #4285f4;">💬 CRM Chatbot</h2>
        </div>
        """, unsafe_allow_html=True)

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

                if 'sources' in message and message['sources']:
                    with st.expander("📚 관련 문서 출처"):
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
        user_query = st.chat_input("질문을 입력하세요...")

    # Process query
    if user_query:
        # Save query history
        save_query_history(user_query)

        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })

        # Perform search
        with st.spinner("🔍 검색 중..."):
            search_results, language = perform_search(
                user_query,
                embedding_service,
                vector_store,
                query_processor,
                chunks_by_collection
            )

        if search_results:
            # Generate answer
            with st.spinner("💭 답변 생성 중..."):
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
        else:
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
