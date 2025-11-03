"""
처리된 청크 데이터로 간단한 검색 테스트
메모리 모드로 작동 (JSON 파일에서 로드)
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import os
from src.services.embedding_service import EmbeddingService
from src.services.vector_store import VectorStore

def load_chunks_from_json(processed_dir: str = "data/processed"):
    """JSON 파일에서 청크 로드"""
    processed_path = Path(processed_dir)
    chunks_by_collection = {}

    print("📂 Loading chunks from JSON files...")

    for json_file in processed_path.glob("*_chunks.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        # 문서 ID에서 컬렉션 이름 추출
        doc_id = json_file.stem.replace('_chunks', '')

        # 컬렉션 이름 생성 (예: crm_account_ko_v1_0 -> crm_account_ko)
        parts = doc_id.split('_')
        if len(parts) >= 4:
            collection_name = f"{parts[0]}_{parts[1]}_{parts[2]}"
        else:
            collection_name = doc_id

        if collection_name not in chunks_by_collection:
            chunks_by_collection[collection_name] = []

        chunks_by_collection[collection_name].extend(chunks)
        print(f"  ✓ {json_file.name}: {len(chunks)} chunks -> {collection_name}")

    return chunks_by_collection

def test_search(query: str, language: str = "auto"):
    """검색 테스트"""

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return

    # 언어 자동 감지
    if language == "auto":
        from langdetect import detect
        try:
            detected = detect(query)
            language = "korean" if detected == "ko" else "english"
        except:
            language = "korean"  # 기본값

    print(f"\n{'='*60}")
    print(f"🔍 Search Test")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Language: {language} (auto-detected)")
    print(f"{'='*60}\n")

    # 임베딩 서비스 초기화
    print("1️⃣  Initializing embedding service...")
    embedding_service = EmbeddingService(
        model_name="openai/text-embedding-3-large",
        api_key=api_key,
        cache_enabled=True
    )

    # 벡터 스토어 초기화 (메모리 모드)
    print("2️⃣  Initializing vector store (in-memory)...")
    vector_store = VectorStore(use_memory=True)

    # 청크 로드
    print("\n3️⃣  Loading chunks from JSON files...")
    chunks_by_collection = load_chunks_from_json()

    total_chunks = sum(len(chunks) for chunks in chunks_by_collection.values())
    print(f"\n✅ Loaded {total_chunks} chunks from {len(chunks_by_collection)} collections")

    # 컬렉션 생성 및 데이터 추가
    print("\n4️⃣  Creating collections and adding data...")
    for collection_name, chunks in chunks_by_collection.items():
        # 컬렉션 생성
        vector_store.create_collection(
            collection_name=collection_name,
            vector_size=3072,
            recreate=True
        )

        # 청크에 임베딩 추가 (캐시에서 로드 또는 새로 생성)
        print(f"\n   Processing {collection_name}...")
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = embedding_service.embed_batch(chunk_texts, show_progress=False)

        # 벡터 스토어용 데이터 준비
        vector_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            vector_chunk = {
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "embedding": embedding,
                "metadata": chunk["metadata"]
            }
            vector_chunks.append(vector_chunk)

        # 데이터 추가
        vector_store.add_documents(
            collection_name=collection_name,
            chunks=vector_chunks,
            show_progress=False
        )
        print(f"   ✓ Added {len(vector_chunks)} chunks to {collection_name}")

    # 쿼리 임베딩 생성
    print(f"\n5️⃣  Generating query embedding...")
    query_embedding = embedding_service.embed_text(query)

    # 언어에 따른 컬렉션 필터
    lang_code = "ko" if language == "korean" else "en"

    # 모든 관련 컬렉션에서 검색
    print(f"\n6️⃣  Searching in collections (language: {lang_code})...")
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

            if results:
                print(f"   ✓ {collection_name}: {len(results)} results")

    # 점수 순 정렬
    all_results.sort(key=lambda x: x.score, reverse=True)
    top_results = all_results[:5]

    # 결과 출력
    print(f"\n{'='*60}")
    print(f"🎯 Search Results (Top {len(top_results)})")
    print(f"{'='*60}\n")

    if not top_results:
        print("❌ No results found")
        return

    for i, result in enumerate(top_results, 1):
        print(f"[{i}] Score: {result.score:.4f}")
        print(f"    Collection: {result.metadata.get('collection', 'N/A')}")
        print(f"    Chunk ID: {result.chunk_id}")
        print(f"    Document: {result.metadata.get('document_id', 'N/A')}")
        print(f"    Type: {result.metadata.get('type', 'N/A')}")
        print(f"    Text Preview: {result.text[:200]}...")
        print()

    print(f"{'='*60}")
    print("✅ Search test completed!")

if __name__ == "__main__":
    # 테스트 쿼리
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        test_search(query)
    else:
        print("Usage: python test_search.py <query>")
        print("\nExample queries:")
        print("  python test_search.py 거래선 등록 방법")
        print("  python test_search.py 미팅메모 작성")
        print("  python test_search.py 주문 승인")
