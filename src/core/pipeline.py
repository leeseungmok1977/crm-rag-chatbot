"""
데이터 파이프라인 오케스트레이터
- PDF → 파싱 → 청킹 → 임베딩 → 벡터DB 전체 플로우 관리
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import asdict

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.pdf_parser import PDFParser, PDFDocument
from src.utils.chunker import DocumentChunker, Chunk
from src.utils.metadata_extractor import MetadataExtractor, DocumentMetadata
from src.services.embedding_service import EmbeddingService
from src.services.vector_store import MultiCollectionVectorStore


class DocumentProcessingPipeline:
    """
    문서 처리 파이프라인

    Pipeline:
    1. PDF 파싱
    2. 메타데이터 추출
    3. 청킹
    4. 임베딩 생성
    5. 벡터 DB 저장
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: MultiCollectionVectorStore,
        output_dir: str = "data/processed"
    ):
        """
        Args:
            embedding_service: 임베딩 서비스
            vector_store: 벡터 스토어
            output_dir: 처리된 데이터 저장 디렉토리
        """
        self.pdf_parser = PDFParser(preserve_layout=True)
        self.metadata_extractor = MetadataExtractor()
        self.chunker = DocumentChunker(
            chunk_size=1000,
            chunk_overlap=200,
            min_chunk_size=100,
            max_chunk_size=2000
        )
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_document(
        self,
        pdf_path: str,
        chunking_strategy: str = "recursive",
        save_intermediate: bool = True
    ) -> Dict:
        """
        단일 문서 처리

        Args:
            pdf_path: PDF 파일 경로
            chunking_strategy: 청킹 전략
            save_intermediate: 중간 결과 저장 여부

        Returns:
            처리 결과 통계
        """
        start_time = time.time()
        pdf_path = Path(pdf_path)

        print(f"\n{'='*60}")
        print(f"📄 Processing: {pdf_path.name}")
        print(f"{'='*60}\n")

        # 1. 메타데이터 추출
        print("1️⃣  Extracting metadata...")
        doc_metadata = self.metadata_extractor.extract_from_filename(str(pdf_path))
        print(f"   - Document ID: {doc_metadata.document_id}")
        print(f"   - Type: {doc_metadata.type}")
        print(f"   - Language: {doc_metadata.language}")

        # 2. PDF 파싱
        print("\n2️⃣  Parsing PDF...")
        pdf_document = self.pdf_parser.parse(str(pdf_path), extract_images=False)
        print(f"   - Pages: {pdf_document.total_pages}")
        print(f"   - Language: {pdf_document.language}")

        # 전체 텍스트 추출
        full_text = "\n\n".join([page.text for page in pdf_document.pages])

        # 메타데이터 보강
        content_metadata = self.metadata_extractor.extract_from_content(
            full_text,
            doc_metadata
        )

        # 3. 청킹
        print(f"\n3️⃣  Chunking with strategy: {chunking_strategy}...")
        base_metadata = {
            "document_id": doc_metadata.document_id,
            "type": doc_metadata.type,
            "language": doc_metadata.language,
            "version": doc_metadata.version,
            "source_file": doc_metadata.source_file,
        }

        chunks = self.chunker.chunk_document(
            text=full_text,
            metadata=base_metadata,
            strategy=chunking_strategy
        )
        print(f"   - Generated {len(chunks)} chunks")
        print(f"   - Avg chunk size: {sum(c.char_count for c in chunks) // len(chunks)} chars")

        # 중간 결과 저장
        if save_intermediate:
            self._save_chunks(doc_metadata.document_id, chunks)

        # 4. 임베딩 생성
        print(f"\n4️⃣  Generating embeddings...")
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_service.embed_batch(
            texts=chunk_texts,
            batch_size=50,
            show_progress=True
        )
        print(f"   - Generated {len(embeddings)} embeddings")

        # 5. 벡터 DB 저장
        print(f"\n5️⃣  Saving to vector database...")

        # 벡터 DB용 데이터 준비
        vector_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            vector_chunk = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "embedding": embedding,
                "metadata": chunk.metadata
            }
            vector_chunks.append(vector_chunk)

        # 문서 타입과 언어에 맞는 컬렉션에 저장
        doc_type_short = doc_metadata.type.replace("_contact", "").replace("_memo", "").replace("_fulfillment", "").replace("_master", "")
        if doc_type_short == "account":
            doc_type_short = "account"
        elif doc_type_short == "meeting":
            doc_type_short = "meeting"
        elif doc_type_short == "order":
            doc_type_short = "order"
        elif doc_type_short == "common":
            doc_type_short = "common"

        lang_code = "ko" if doc_metadata.language == "korean" else "en"

        self.vector_store.add_document_chunks(
            document_type=doc_type_short,
            language=lang_code,
            chunks=vector_chunks,
            batch_size=100
        )

        # 처리 시간
        elapsed_time = time.time() - start_time

        # 결과 통계
        stats = {
            "document_id": doc_metadata.document_id,
            "source_file": doc_metadata.source_file,
            "type": doc_metadata.type,
            "language": doc_metadata.language,
            "total_pages": pdf_document.total_pages,
            "total_chunks": len(chunks),
            "total_chars": len(full_text),
            "processing_time_seconds": round(elapsed_time, 2),
            "collection_name": f"crm_{doc_type_short}_{lang_code}"
        }

        print(f"\n✅ Processing completed in {elapsed_time:.2f}s")
        print(f"   - Saved to collection: crm_{doc_type_short}_{lang_code}")

        return stats

    def process_folder(
        self,
        folder_path: str,
        chunking_strategy: str = "recursive",
        file_pattern: str = "*.pdf"
    ) -> List[Dict]:
        """
        폴더 내 모든 PDF 처리

        Args:
            folder_path: PDF 폴더 경로
            chunking_strategy: 청킹 전략
            file_pattern: 파일 패턴

        Returns:
            각 문서의 처리 결과 통계 리스트
        """
        folder = Path(folder_path)
        pdf_files = list(folder.glob(file_pattern))

        print(f"\n{'='*60}")
        print(f"📁 Processing folder: {folder}")
        print(f"   Found {len(pdf_files)} PDF files")
        print(f"{'='*60}")

        all_stats = []
        errors = []

        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}]")
            try:
                stats = self.process_document(
                    pdf_path=str(pdf_file),
                    chunking_strategy=chunking_strategy,
                    save_intermediate=True
                )
                all_stats.append(stats)
            except Exception as e:
                error_info = {
                    "file": pdf_file.name,
                    "error": str(e)
                }
                errors.append(error_info)
                print(f"\n❌ Error processing {pdf_file.name}: {e}")

        # 최종 요약
        print(f"\n{'='*60}")
        print(f"📊 Processing Summary")
        print(f"{'='*60}")
        print(f"✅ Successfully processed: {len(all_stats)}")
        print(f"❌ Failed: {len(errors)}")
        if all_stats:
            total_chunks = sum(s["total_chunks"] for s in all_stats)
            total_time = sum(s["processing_time_seconds"] for s in all_stats)
            print(f"📦 Total chunks: {total_chunks}")
            print(f"⏱️  Total time: {total_time:.2f}s")

        if errors:
            print(f"\n❌ Errors:")
            for error in errors:
                print(f"   - {error['file']}: {error['error']}")

        # 결과 저장
        self._save_processing_report(all_stats, errors)

        return all_stats

    def _save_chunks(self, document_id: str, chunks: List[Chunk]):
        """청크를 JSON 파일로 저장"""
        output_file = self.output_dir / f"{document_id}_chunks.json"

        chunks_data = []
        for chunk in chunks:
            chunk_data = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "metadata": chunk.metadata,
                "char_count": chunk.char_count,
                "token_count": chunk.token_count
            }
            chunks_data.append(chunk_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)

        print(f"   💾 Saved chunks to: {output_file}")

    def _save_processing_report(self, stats: List[Dict], errors: List[Dict]):
        """처리 리포트 저장"""
        report_file = self.output_dir / "processing_report.json"

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_documents": len(stats) + len(errors),
            "successful": len(stats),
            "failed": len(errors),
            "statistics": stats,
            "errors": errors
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Report saved to: {report_file}")


def create_pipeline(
    openai_api_key: str,
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333,
    vector_size: int = 3072,
    use_memory: bool = False
) -> DocumentProcessingPipeline:
    """
    파이프라인 생성 헬퍼 함수

    Args:
        openai_api_key: OpenAI API 키
        qdrant_host: Qdrant 호스트
        qdrant_port: Qdrant 포트
        vector_size: 벡터 차원
        use_memory: 메모리 모드 사용 (Docker 없을 때)

    Returns:
        DocumentProcessingPipeline 인스턴스
    """
    # 임베딩 서비스 초기화
    embedding_service = EmbeddingService(
        model_name="openai/text-embedding-3-large",
        api_key=openai_api_key,
        cache_enabled=True
    )

    # 벡터 스토어 초기화 (자동으로 연결 시도)
    try:
        if use_memory:
            raise ConnectionError("Memory mode requested")

        vector_store = MultiCollectionVectorStore(
            host=qdrant_host,
            port=qdrant_port
        )
        print("✅ Connected to Qdrant server")
    except Exception as e:
        print(f"⚠️  Cannot connect to Qdrant server: {e}")
        print("⚠️  Using in-memory mode (data will not persist)")
        from src.services.vector_store import VectorStore
        # 메모리 모드로 폴백
        vector_store_memory = VectorStore(use_memory=True)
        # MultiCollectionVectorStore 인터페이스로 래핑
        class MemoryMultiCollectionVectorStore:
            def __init__(self, store):
                self.store = store
                self.collections = {}

            def initialize_crm_collections(self, vector_size, recreate=False):
                for doc_type in ["account", "meeting", "order", "common"]:
                    for lang in ["ko", "en"]:
                        collection_name = f"crm_{doc_type}_{lang}"
                        self.store.create_collection(
                            collection_name=collection_name,
                            vector_size=vector_size,
                            recreate=recreate
                        )
                        self.collections[collection_name] = True

            def add_document_chunks(self, document_type, language, chunks, batch_size=100):
                collection_name = f"crm_{document_type}_{language}"
                self.store.add_documents(
                    collection_name=collection_name,
                    chunks=chunks,
                    batch_size=batch_size
                )

        vector_store = MemoryMultiCollectionVectorStore(vector_store_memory)

    # 컬렉션 생성
    vector_store.initialize_crm_collections(
        vector_size=vector_size,
        recreate=False  # 기존 데이터 유지
    )

    # 파이프라인 생성
    pipeline = DocumentProcessingPipeline(
        embedding_service=embedding_service,
        vector_store=vector_store
    )

    return pipeline


if __name__ == "__main__":
    # 테스트 코드
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        exit(1)

    # 파이프라인 생성
    pipeline = create_pipeline(
        openai_api_key=api_key,
        qdrant_host="localhost",
        qdrant_port=6333
    )

    # 테스트: 단일 파일 처리
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if Path(pdf_path).is_file():
            stats = pipeline.process_document(pdf_path)
            print(f"\n✅ Processing complete!")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        elif Path(pdf_path).is_dir():
            stats = pipeline.process_folder(pdf_path)
        else:
            print(f"❌ Path not found: {pdf_path}")
    else:
        print("Usage: python pipeline.py <pdf_file_or_folder>")
