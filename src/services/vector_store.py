"""
벡터 DB 연동 모듈
- Qdrant 벡터 데이터베이스 인터페이스
- CRUD 작업
- 검색 기능
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams,
)
from tqdm import tqdm


@dataclass
class SearchResult:
    """검색 결과"""
    chunk_id: str
    text: str
    score: float
    metadata: Dict


class VectorStore:
    """
    Qdrant 벡터 스토어 클래스

    Features:
    - 컬렉션 생성/삭제
    - 벡터 저장
    - 유사도 검색
    - 메타데이터 필터링
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        use_memory: bool = False
    ):
        """
        Args:
            host: Qdrant 호스트
            port: Qdrant 포트
            api_key: API 키 (클라우드 사용 시)
            use_memory: 메모리 모드 (테스트용)
        """
        if use_memory:
            self.client = QdrantClient(":memory:")
            print("✅ Vector store initialized (in-memory mode)")
        else:
            self.client = QdrantClient(
                host=host,
                port=port,
                api_key=api_key
            )
            print(f"✅ Vector store connected to {host}:{port}")

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
        recreate: bool = False
    ):
        """
        컬렉션 생성

        Args:
            collection_name: 컬렉션 이름
            vector_size: 벡터 차원
            distance: 거리 메트릭 (Cosine, Euclid, Dot)
            recreate: 기존 컬렉션 삭제 후 재생성
        """
        # 거리 메트릭 매핑
        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclid": Distance.EUCLID,
            "Dot": Distance.DOT,
        }

        if recreate and self.collection_exists(collection_name):
            self.client.delete_collection(collection_name)
            print(f"🗑️  Deleted existing collection: {collection_name}")

        if not self.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, Distance.COSINE)
                )
            )
            print(f"✅ Created collection: {collection_name} (dim={vector_size})")
        else:
            print(f"ℹ️  Collection already exists: {collection_name}")

    def collection_exists(self, collection_name: str) -> bool:
        """컬렉션 존재 여부 확인"""
        collections = self.client.get_collections().collections
        return any(c.name == collection_name for c in collections)

    def add_documents(
        self,
        collection_name: str,
        chunks: List[Dict],  # {chunk_id, text, embedding, metadata}
        batch_size: int = 100,
        show_progress: bool = True
    ):
        """
        문서 청크 추가

        Args:
            collection_name: 컬렉션 이름
            chunks: 청크 리스트
            batch_size: 배치 크기
            show_progress: 진행률 표시
        """
        if not chunks:
            print("⚠️  No chunks to add")
            return

        print(f"📥 Adding {len(chunks)} chunks to {collection_name}")

        # 배치 처리
        batches = [
            chunks[i:i + batch_size]
            for i in range(0, len(chunks), batch_size)
        ]

        iterator = tqdm(batches, desc="Uploading") if show_progress else batches

        for batch in iterator:
            points = []
            for chunk in batch:
                point = PointStruct(
                    id=str(uuid.uuid4()),  # 고유 ID
                    vector=chunk["embedding"],
                    payload={
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        **chunk.get("metadata", {})
                    }
                )
                points.append(point)

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )

        print(f"✅ Added {len(chunks)} chunks")

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict] = None,
        score_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        벡터 유사도 검색

        Args:
            collection_name: 컬렉션 이름
            query_vector: 쿼리 벡터
            top_k: 상위 K개 결과
            filters: 메타데이터 필터 (예: {"type": "account_contact"})
            score_threshold: 최소 유사도 점수

        Returns:
            검색 결과 리스트
        """
        # 필터 생성
        query_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            query_filter = Filter(must=conditions)

        # 검색
        search_result = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False
        )

        # 결과 변환
        results = []
        for hit in search_result:
            payload = hit.payload
            result = SearchResult(
                chunk_id=payload.get("chunk_id", ""),
                text=payload.get("text", ""),
                score=hit.score,
                metadata={k: v for k, v in payload.items()
                         if k not in ["chunk_id", "text"]}
            )
            results.append(result)

        return results

    def search_by_filters(
        self,
        collection_name: str,
        filters: Dict,
        limit: int = 100
    ) -> List[Dict]:
        """
        메타데이터 필터로 검색 (벡터 검색 없이)

        Args:
            collection_name: 컬렉션 이름
            filters: 메타데이터 필터
            limit: 최대 결과 수

        Returns:
            문서 리스트
        """
        conditions = []
        for key, value in filters.items():
            conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )

        query_filter = Filter(must=conditions)

        results = self.client.scroll(
            collection_name=collection_name,
            scroll_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        documents = []
        for point in results[0]:
            documents.append(point.payload)

        return documents

    def delete_documents(
        self,
        collection_name: str,
        filters: Dict
    ):
        """
        메타데이터 필터로 문서 삭제

        Args:
            collection_name: 컬렉션 이름
            filters: 메타데이터 필터
        """
        conditions = []
        for key, value in filters.items():
            conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )

        query_filter = Filter(must=conditions)

        self.client.delete(
            collection_name=collection_name,
            points_selector=query_filter
        )
        print(f"🗑️  Deleted documents matching filters: {filters}")

    def get_collection_info(self, collection_name: str) -> Dict:
        """컬렉션 정보 조회"""
        info = self.client.get_collection(collection_name)
        return {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
            "config": {
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.name
            }
        }

    def list_collections(self) -> List[str]:
        """모든 컬렉션 이름 조회"""
        collections = self.client.get_collections().collections
        return [c.name for c in collections]

    def delete_collection(self, collection_name: str):
        """컬렉션 삭제"""
        self.client.delete_collection(collection_name)
        print(f"🗑️  Deleted collection: {collection_name}")


class MultiCollectionVectorStore:
    """
    여러 컬렉션을 관리하는 벡터 스토어

    CRM 매뉴얼의 경우 8개 컬렉션 관리:
    - crm_account_ko, crm_account_en
    - crm_meeting_ko, crm_meeting_en
    - crm_order_ko, crm_order_en
    - crm_common_ko, crm_common_en
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None
    ):
        self.store = VectorStore(host=host, port=port, api_key=api_key)

    def initialize_crm_collections(
        self,
        vector_size: int,
        recreate: bool = False
    ):
        """
        CRM 매뉴얼용 8개 컬렉션 초기화

        Args:
            vector_size: 벡터 차원
            recreate: 기존 컬렉션 삭제 후 재생성
        """
        doc_types = ["account", "meeting", "order", "common"]
        languages = ["ko", "en"]

        print(f"🏗️  Initializing CRM collections (vector_size={vector_size})")

        for doc_type in doc_types:
            for lang in languages:
                collection_name = f"crm_{doc_type}_{lang}"
                self.store.create_collection(
                    collection_name=collection_name,
                    vector_size=vector_size,
                    distance="Cosine",
                    recreate=recreate
                )

    def add_document_chunks(
        self,
        document_type: str,  # account, meeting, order, common
        language: str,       # ko, en
        chunks: List[Dict],
        batch_size: int = 100
    ):
        """
        특정 문서 타입/언어의 청크 추가

        Args:
            document_type: 문서 타입
            language: 언어
            chunks: 청크 리스트
            batch_size: 배치 크기
        """
        collection_name = f"crm_{document_type}_{language}"
        self.store.add_documents(
            collection_name=collection_name,
            chunks=chunks,
            batch_size=batch_size
        )

    def search_all_collections(
        self,
        query_vector: List[float],
        top_k: int = 5,
        language: Optional[str] = None,
        doc_type: Optional[str] = None
    ) -> List[SearchResult]:
        """
        여러 컬렉션에서 검색 후 결합

        Args:
            query_vector: 쿼리 벡터
            top_k: 컬렉션당 상위 K개 (총 결과는 더 많을 수 있음)
            language: 언어 필터 (None이면 모든 언어)
            doc_type: 문서 타입 필터 (None이면 모든 타입)

        Returns:
            통합 검색 결과 (점수 순 정렬)
        """
        all_results = []

        # 검색할 컬렉션 결정
        doc_types = [doc_type] if doc_type else ["account", "meeting", "order", "common"]
        languages = [language] if language else ["ko", "en"]

        for dt in doc_types:
            for lang in languages:
                collection_name = f"crm_{dt}_{lang}"

                if self.store.collection_exists(collection_name):
                    results = self.store.search(
                        collection_name=collection_name,
                        query_vector=query_vector,
                        top_k=top_k
                    )
                    all_results.extend(results)

        # 점수 순 정렬
        all_results.sort(key=lambda x: x.score, reverse=True)

        return all_results[:top_k * 2]  # 최종 상위 결과 반환

    def get_all_stats(self) -> Dict[str, Dict]:
        """모든 컬렉션 통계"""
        stats = {}

        for collection_name in self.store.list_collections():
            if collection_name.startswith("crm_"):
                try:
                    stats[collection_name] = self.store.get_collection_info(collection_name)
                except:
                    stats[collection_name] = {"error": "Failed to get info"}

        return stats


# 유틸리티 함수
def setup_crm_vector_store(
    host: str = "localhost",
    port: int = 6333,
    vector_size: int = 3072,  # OpenAI text-embedding-3-large
    recreate: bool = False
) -> MultiCollectionVectorStore:
    """
    CRM RAG 챗봇용 벡터 스토어 셋업

    Args:
        host: Qdrant 호스트
        port: Qdrant 포트
        vector_size: 벡터 차원
        recreate: 기존 컬렉션 삭제 후 재생성

    Returns:
        MultiCollectionVectorStore 인스턴스
    """
    store = MultiCollectionVectorStore(host=host, port=port)
    store.initialize_crm_collections(vector_size=vector_size, recreate=recreate)
    return store


if __name__ == "__main__":
    # 테스트 코드
    print("=== Vector Store Test ===\n")

    # 메모리 모드로 테스트
    store = VectorStore(use_memory=True)

    # 컬렉션 생성
    store.create_collection(
        collection_name="test_collection",
        vector_size=768,
        recreate=True
    )

    # 테스트 데이터
    test_chunks = [
        {
            "chunk_id": "chunk_001",
            "text": "거래선 등록 방법을 설명합니다.",
            "embedding": [0.1] * 768,
            "metadata": {
                "type": "account_contact",
                "language": "korean",
                "page": 10
            }
        },
        {
            "chunk_id": "chunk_002",
            "text": "미팅메모 작성 가이드입니다.",
            "embedding": [0.2] * 768,
            "metadata": {
                "type": "meeting_memo",
                "language": "korean",
                "page": 25
            }
        }
    ]

    # 문서 추가
    store.add_documents(
        collection_name="test_collection",
        chunks=test_chunks,
        show_progress=False
    )

    # 검색 테스트
    query_vector = [0.15] * 768
    results = store.search(
        collection_name="test_collection",
        query_vector=query_vector,
        top_k=2,
        filters={"language": "korean"}
    )

    print("\n=== Search Results ===")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result.score:.4f}")
        print(f"   Chunk ID: {result.chunk_id}")
        print(f"   Text: {result.text}")
        print(f"   Metadata: {result.metadata}")

    # 컬렉션 정보
    info = store.get_collection_info("test_collection")
    print(f"\n=== Collection Info ===")
    print(f"Points: {info['points_count']}")
    print(f"Vector size: {info['config']['vector_size']}")
