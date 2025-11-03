# CRM RAG Chatbot - Data Pipeline

POSCO International CRM 매뉴얼 전용 RAG 챗봇의 데이터 처리 파이프라인

## 📋 개요

이 프로젝트는 CRM 매뉴얼 PDF 문서를 파싱하고, 청킹하고, 임베딩하여 벡터 데이터베이스에 저장하는 전체 파이프라인을 제공합니다.

### 주요 기능

- ✅ **PDF 파싱**: 텍스트, 표, 이미지 추출
- ✅ **지능형 청킹**: 다양한 청킹 전략 지원
- ✅ **임베딩 생성**: OpenAI/로컬 모델 지원
- ✅ **벡터 DB 저장**: Qdrant 기반 다중 컬렉션 관리
- ✅ **메타데이터 관리**: 자동 문서 분류 및 태깅
- ✅ **캐싱**: 임베딩 캐싱으로 비용 절감

## 🏗️ 아키텍처

```
PDF 문서
    ↓
[PDF Parser] → 텍스트 추출
    ↓
[Metadata Extractor] → 문서 정보 추출
    ↓
[Chunker] → 의미 단위 분할
    ↓
[Embedding Service] → 벡터 변환 (캐싱)
    ↓
[Vector Store] → Qdrant DB 저장
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 OPENAI_API_KEY 설정
```

### 2. Qdrant 실행

**옵션 A: Docker 사용 (권장)**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**옵션 B: 로컬 설치**
```bash
# https://qdrant.tech/documentation/quick-start/ 참고
```

### 3. 문서 처리

**단일 파일 처리**
```bash
python scripts/process_documents.py "PDF/P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf"
```

**폴더 전체 처리**
```bash
python scripts/process_documents.py PDF/
```

**옵션 사용**
```bash
# 청킹 전략 변경
python scripts/process_documents.py PDF/ --strategy semantic

# 컬렉션 재생성 (기존 데이터 삭제)
python scripts/process_documents.py PDF/ --recreate-collections

# 캐시 비활성화
python scripts/process_documents.py PDF/ --no-cache

# 배치 크기 조정
python scripts/process_documents.py PDF/ --batch-size 50
```

## 📂 프로젝트 구조

```
.
├── src/
│   ├── core/
│   │   ├── config.py              # 설정 관리
│   │   └── pipeline.py            # 파이프라인 오케스트레이터
│   ├── services/
│   │   ├── embedding_service.py   # 임베딩 서비스
│   │   └── vector_store.py        # 벡터 DB 인터페이스
│   └── utils/
│       ├── pdf_parser.py          # PDF 파싱
│       ├── chunker.py             # 문서 청킹
│       └── metadata_extractor.py  # 메타데이터 추출
├── scripts/
│   └── process_documents.py       # 문서 처리 스크립트
├── data/
│   ├── raw/                       # 원본 PDF (미포함)
│   ├── processed/                 # 처리된 청크 (JSON)
│   └── embeddings/                # 임베딩 캐시
├── PDF/                           # CRM 매뉴얼 PDF 폴더
├── requirements.txt               # 의존성
├── .env.example                   # 환경 변수 예시
└── README.md
```

## 🔧 모듈별 상세 설명

### PDF Parser

**기능**:
- PyMuPDF와 pdfplumber를 사용한 고품질 텍스트 추출
- 표 추출 (마크다운 형식 변환)
- 이미지 메타데이터 추출
- 언어 자동 감지

**사용 예시**:
```python
from src.utils.pdf_parser import PDFParser

parser = PDFParser(preserve_layout=True)
document = parser.parse("manual.pdf", extract_images=False)

print(f"Pages: {document.total_pages}")
print(f"Language: {document.language}")
print(f"First page: {document.pages[0].text[:200]}")
```

### Chunker

**청킹 전략**:
1. **Fixed**: 고정 크기 청킹
2. **Recursive**: 재귀적 분할 (권장)
3. **Semantic**: 섹션 기반 의미 단위 청킹
4. **Token**: 토큰 수 기반 청킹

**사용 예시**:
```python
from src.utils.chunker import DocumentChunker

chunker = DocumentChunker(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = chunker.chunk_document(
    text=text,
    metadata={"document_id": "doc123"},
    strategy="recursive"
)

print(f"Generated {len(chunks)} chunks")
```

### Embedding Service

**지원 모델**:
- OpenAI: text-embedding-3-large (3072 dim)
- OpenAI: text-embedding-3-small (1536 dim)
- Local: sentence-transformers 모델

**캐싱**:
- 로컬 파일 기반 캐싱
- 중복 임베딩 방지로 비용 절감

**사용 예시**:
```python
from src.services.embedding_service import EmbeddingService

service = EmbeddingService(
    model_name="openai/text-embedding-3-large",
    api_key="your_key",
    cache_enabled=True
)

# 단일 텍스트
embedding = service.embed_text("거래선 등록 방법")

# 배치 처리
embeddings = service.embed_batch(["text1", "text2", "text3"])
```

### Vector Store

**Qdrant 기반 벡터 데이터베이스**

**컬렉션 구조**:
- `crm_account_ko`: 거래선&연락처 (한국어)
- `crm_account_en`: Account&Contact (영어)
- `crm_meeting_ko`: 미팅메모 (한국어)
- `crm_meeting_en`: Meeting Memo (영어)
- `crm_order_ko`: 주문&이행 (한국어)
- `crm_order_en`: Order&Fulfillment (영어)
- `crm_common_ko`: 공통&Master (한국어)
- `crm_common_en`: Common&Master (영어)

**사용 예시**:
```python
from src.services.vector_store import MultiCollectionVectorStore

store = MultiCollectionVectorStore(
    host="localhost",
    port=6333
)

# 검색
results = store.search_all_collections(
    query_vector=embedding,
    top_k=5,
    language="ko",
    doc_type="account"
)
```

### Metadata Extractor

**자동 추출 정보**:
- 문서 타입 (account/meeting/order/common)
- 언어 (korean/english)
- 버전
- 키워드

**파일명 패턴 지원**:
- `P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf`
- `P_INTL_CRM Guide Book(ENG)_Account&Contact.pdf`

## ⚙️ 설정

### 환경 변수 (.env)

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Embedding
EMBEDDING_MODEL=openai/text-embedding-3-large
EMBEDDING_DIMENSION=3072

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHUNKING_STRATEGY=recursive

# Cache
CACHE_ENABLED=true
CACHE_DIR=data/embeddings
```

### config.py 사용

```python
from src.core.config import get_settings

settings = get_settings()
print(settings.chunk_size)  # 1000
```

## 📊 처리 결과

처리 완료 후 다음 파일들이 생성됩니다:

1. **청크 JSON**: `data/processed/{document_id}_chunks.json`
   ```json
   [
     {
       "chunk_id": "crm_account_ko_v1_0_chunk_0001",
       "text": "거래선 등록 절차...",
       "metadata": {...},
       "char_count": 850,
       "token_count": 425
     }
   ]
   ```

2. **처리 리포트**: `data/processed/processing_report.json`
   ```json
   {
     "timestamp": "2025-11-03 10:30:00",
     "total_documents": 8,
     "successful": 8,
     "failed": 0,
     "statistics": [...]
   }
   ```

3. **임베딩 캐시**: `data/embeddings/{hash}.json`

## 🧪 테스트

각 모듈은 독립적으로 테스트 가능합니다:

```bash
# PDF Parser 테스트
python src/utils/pdf_parser.py "PDF/sample.pdf"

# Chunker 테스트
python src/utils/chunker.py

# Embedding Service 테스트
python src/services/embedding_service.py

# Vector Store 테스트
python src/services/vector_store.py

# Metadata Extractor 테스트
python src/utils/metadata_extractor.py "PDF/"
```

## 📈 성능

### 처리 속도 (예상)

| 문서 | 페이지 | 청크 수 | 임베딩 시간 | 총 시간 |
|------|--------|---------|------------|---------|
| 거래선&연락처 (국문) | 150 | ~300 | ~60초 | ~2분 |
| Meeting Memo (ENG) | 180 | ~360 | ~72초 | ~2.5분 |

**전체 8개 문서**: 약 15-20분 (캐시 없음 기준)

### 비용 추정

**OpenAI Embedding API**:
- 모델: text-embedding-3-large
- 가격: $0.00013 / 1K tokens
- 전체 문서 (약 2,400 청크 × 500 tokens): **~$0.16**

**캐싱 효과**:
- 재처리 시: **$0** (캐시 사용)

## 🔍 문제 해결

### Qdrant 연결 실패
```bash
# Qdrant 실행 확인
docker ps | grep qdrant

# 포트 확인
netstat -an | grep 6333
```

### 임베딩 에러
```bash
# API 키 확인
echo $OPENAI_API_KEY

# 할당량 확인
# https://platform.openai.com/account/usage
```

### 메모리 부족
```python
# 배치 크기 줄이기
python scripts/process_documents.py PDF/ --batch-size 50
```

## 📚 다음 단계

1. **RAG 엔진 구현** ([설계 문서](CRM_RAG_CHATBOT_DESIGN.md) 참고)
   - Query Preprocessor
   - Smart Router
   - Retriever & Reranker
   - Generator

2. **API 서버 구축**
   - FastAPI 기반 REST API
   - 챗봇 인터페이스

3. **프론트엔드 개발**
   - Streamlit / React
   - 채팅 UI

## 📝 라이선스

Internal Use Only - POSCO International

## 👥 기여자

AI Development Team

## 📞 문의

- Email: ai-team@poscointl.com
- Slack: #crm-chatbot-dev
