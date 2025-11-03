# POSCO International CRM RAG Chatbot - 설계 문서

**프로젝트명**: POSCO International CRM AI Assistant
**버전**: 1.0.0
**작성일**: 2025-11-03
**작성자**: AI Development Team
**문서 타입**: 시스템 설계 및 아키텍처 명세서

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [문서 구조 및 관리 전략](#3-문서-구조-및-관리-전략)
4. [RAG 파이프라인 설계](#4-rag-파이프라인-설계)
5. [기술 스택](#5-기술-스택)
6. [데이터베이스 스키마](#6-데이터베이스-스키마)
7. [API 설계](#7-api-설계)
8. [보안 및 권한 관리](#8-보안-및-권한-관리)
9. [성능 최적화 전략](#9-성능-최적화-전략)
10. [테스트 전략](#10-테스트-전략)
11. [배포 및 운영](#11-배포-및-운영)
12. [구현 로드맵](#12-구현-로드맵)

---

## 1. 프로젝트 개요

### 1.1 목적
POSCO International 임직원을 위한 CRM 시스템 전용 AI 챗봇 구축
- CRM 매뉴얼 기반 실시간 질의응답
- 다국어 지원 (한국어/영어)
- 컨텍스트 기반 정확한 답변 제공

### 1.2 주요 기능
- ✅ **자연어 질의응답**: CRM 사용법, 문제 해결 가이드
- ✅ **다국어 지원**: 한국어/영어 매뉴얼 자동 선택
- ✅ **컨텍스트 인식**: 대화 이력 기반 맥락 이해
- ✅ **스마트 라우팅**: 질문 유형별 최적 문서 자동 선택
- ✅ **소스 추적**: 답변 출처 명시 (페이지 번호, 섹션)

### 1.3 대상 사용자
- POSCO International 전 임직원
- CRM 시스템 신규 사용자
- CRM 관리자 및 헬프데스크

### 1.4 성공 지표
- **정확도**: 95% 이상 (사용자 만족도 기준)
- **응답 시간**: 평균 2초 이내
- **커버리지**: CRM 전체 기능 100% 포함
- **사용률**: 월 활성 사용자 70% 이상

---

## 2. 시스템 아키텍처

### 2.1 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자 인터페이스                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Web UI   │  │ Teams Bot│  │ Mobile   │  │  API     │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │      API Gateway & Load Balancer      │
        └───────────────────┬───────────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │         챗봇 오케스트레이션 레이어        │
        │  ┌─────────────────────────────────┐  │
        │  │  Query Preprocessor             │  │
        │  │  - 언어 감지                     │  │
        │  │  - 의도 분류                     │  │
        │  │  - 쿼리 정규화                   │  │
        │  └─────────┬───────────────────────┘  │
        │            │                           │
        │  ┌─────────▼───────────────────────┐  │
        │  │  Smart Router                   │  │
        │  │  - 문서 타입 선택                │  │
        │  │  - 검색 전략 결정                │  │
        │  └─────────┬───────────────────────┘  │
        └────────────┼─────────────────────────┘
                     │
        ┌────────────▼─────────────────────────┐
        │         RAG Engine                   │
        │  ┌──────────────┐  ┌──────────────┐ │
        │  │  Retriever   │  │  Generator   │ │
        │  │              │  │              │ │
        │  │  - Hybrid    │  │  - LLM       │ │
        │  │    Search    │  │  - Prompt    │ │
        │  │  - Reranking │  │  - Response  │ │
        │  └──────┬───────┘  └──────▲───────┘ │
        └─────────┼──────────────────┼─────────┘
                  │                  │
        ┌─────────▼──────────────────┼─────────┐
        │      Vector Database       │         │
        │  ┌──────────────────────┐  │         │
        │  │  Account & Contact   │  │         │
        │  │  (KO/EN)             │  │         │
        │  ├──────────────────────┤  │         │
        │  │  Meeting Memo        │  │         │
        │  │  (KO/EN)             │  │         │
        │  ├──────────────────────┤  │         │
        │  │  Order & Fulfillment │  │         │
        │  │  (KO/EN)             │  │         │
        │  ├──────────────────────┤  │         │
        │  │  Common & Master     │  │         │
        │  │  (KO/EN)             │  │         │
        │  └──────────────────────┘  │         │
        └────────────────────────────┘         │
                                                │
        ┌───────────────────────────────────────┘
        │
        │  ┌─────────────────────────────────┐
        └─>│  LLM Service                    │
           │  - GPT-4 / Claude               │
           │  - Embedding Model              │
           └─────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    지원 시스템                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ 로깅     │  │ 모니터링  │  │ 캐싱     │  │ 분석     │    │
│  │ (ELK)    │  │(Grafana) │  │ (Redis)  │  │(Analytics)│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 주요 컴포넌트 설명

#### 2.2.1 API Gateway
- **역할**: 요청 라우팅, 인증, Rate Limiting
- **기술**: FastAPI / Kong
- **기능**:
  - JWT 토큰 검증
  - API 버전 관리
  - 요청/응답 로깅

#### 2.2.2 Query Preprocessor
- **역할**: 사용자 질문 전처리
- **기능**:
  - 언어 감지 (langdetect)
  - 맞춤법 교정
  - 동의어 처리
  - 쿼리 확장

#### 2.2.3 Smart Router
- **역할**: 최적 문서 자동 선택
- **알고리즘**:
  ```python
  def route_query(query, language, context):
      # 1. 키워드 기반 1차 분류
      keywords_map = {
          "account": ["거래선", "연락처", "고객", "account", "contact"],
          "meeting": ["미팅", "메모", "회의", "meeting", "memo"],
          "order": ["주문", "발주", "계약", "order", "fulfillment"],
          "common": ["공통", "설정", "권한", "common", "master"]
      }

      # 2. LLM 기반 의도 분류 (Fallback)
      if no_clear_match:
          intent = llm_classify(query)

      # 3. 메타데이터 필터 생성
      filters = {
          "type": intent,
          "language": language
      }

      return filters
  ```

#### 2.2.4 RAG Engine
- **Retriever**: 하이브리드 검색
  - BM25 (키워드 기반)
  - Vector Search (의미 기반)
  - Fusion Ranking
- **Reranker**: Cross-Encoder 재정렬
- **Generator**: LLM 기반 답변 생성

---

## 3. 문서 구조 및 관리 전략

### 3.1 원본 문서 구조

```
PDF/
├── korean/
│   ├── P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf      [9.9MB]
│   ├── P_INTL_CRM 매뉴얼(국문)_미팅메모.pdf          [9.5MB]
│   ├── P_INTL_CRM 매뉴얼(국문)_Order&Fulfillment.pdf [5.2MB]
│   └── P_INTL_CRM 매뉴얼(국문)_공통&Master.pdf       [3.9MB]
└── english/
    ├── P_INTL_CRM Guide Book(ENG)_Account&Contact.pdf [10.6MB]
    ├── P_INTL_CRM Guide Book(ENG)_Meeting Memo.pdf    [12.9MB]
    ├── P_INTL_CRM Guide Book(ENG)_Order&Fulfillment.pdf [5.5MB]
    └── P_INTL_CRM Guide Book(ENG)_Common&Master.pdf    [4.0MB]
```

### 3.2 문서 메타데이터 스키마

```json
{
  "document_id": "crm_account_ko_v1",
  "type": "account_contact",
  "language": "korean",
  "version": "1.0",
  "last_updated": "2025-11-03",
  "source_file": "P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf",
  "total_pages": 150,
  "sections": [
    {
      "section_id": "1.1",
      "title": "거래선 등록",
      "page_start": 10,
      "page_end": 25,
      "keywords": ["거래선", "등록", "신규", "생성"]
    }
  ],
  "checksum": "sha256:abc123..."
}
```

### 3.3 문서 분리 전략 (권장)

**✅ 선택: 8개 독립 컬렉션 유지**

| 컬렉션 ID | 타입 | 언어 | 용도 |
|----------|------|------|------|
| `crm_account_ko` | 거래선&연락처 | 한국어 | 고객 관리 관련 질문 |
| `crm_account_en` | Account&Contact | 영어 | Customer management |
| `crm_meeting_ko` | 미팅메모 | 한국어 | 회의록 관련 질문 |
| `crm_meeting_en` | Meeting Memo | 영어 | Meeting records |
| `crm_order_ko` | 주문&이행 | 한국어 | 주문 프로세스 |
| `crm_order_en` | Order&Fulfillment | 영어 | Order process |
| `crm_common_ko` | 공통&Master | 한국어 | 공통 기능, 설정 |
| `crm_common_en` | Common&Master | 영어 | Common features |

### 3.4 청킹(Chunking) 전략

#### 옵션 A: 고정 크기 청킹 (Simple)
```python
CHUNK_SIZE = 1000  # 문자 수
CHUNK_OVERLAP = 200  # 중복 영역
```

#### 옵션 B: 의미 단위 청킹 (Recommended)
```python
# 섹션 기반 청킹
- 대제목(H1) → 독립 청크
- 중제목(H2) → 서브 청크
- 표/이미지 → 별도 청크 (캡션 포함)

# 청크 크기 제한
MIN_CHUNK_SIZE = 200
MAX_CHUNK_SIZE = 1500
```

#### 청킹 예시
```python
# Input: PDF 페이지
"""
2.1 거래선 등록 절차

거래선을 등록하려면 다음 단계를 따르세요:
1. CRM 메뉴 > 거래선 관리 클릭
2. [신규 등록] 버튼 클릭
3. 필수 항목 입력:
   - 거래선명
   - 사업자번호
   - 대표자명
4. [저장] 클릭
"""

# Output: 청크 + 메타데이터
{
  "chunk_id": "crm_account_ko_p15_c1",
  "text": "거래선 등록 절차\n\n거래선을 등록하려면...",
  "metadata": {
    "document_id": "crm_account_ko_v1",
    "section": "2.1",
    "section_title": "거래선 등록 절차",
    "page": 15,
    "type": "account_contact",
    "language": "korean",
    "keywords": ["거래선", "등록", "신규"],
    "parent_chunk": null,
    "child_chunks": []
  }
}
```

---

## 4. RAG 파이프라인 설계

### 4.1 전체 플로우

```
사용자 질문
    ↓
[1] Query Preprocessing
    - 언어 감지
    - 오타 교정
    - 쿼리 확장
    ↓
[2] Intent Classification
    - 문서 타입 예측
    - 검색 전략 선택
    ↓
[3] Retrieval (하이브리드 검색)
    - BM25 검색 (Top 20)
    - Vector 검색 (Top 20)
    - Fusion (RRF)
    ↓
[4] Reranking
    - Cross-Encoder 재정렬
    - Top 5 선택
    ↓
[5] Context Building
    - 청크 조합
    - 주변 문맥 추가
    ↓
[6] Generation
    - 프롬프트 구성
    - LLM 호출
    - 답변 생성
    ↓
[7] Post-processing
    - 소스 링크 추가
    - 포맷팅
    ↓
사용자에게 답변 반환
```

### 4.2 하이브리드 검색 알고리즘

#### 4.2.1 BM25 검색 (키워드 기반)
```python
from rank_bm25 import BM25Okapi

def bm25_search(query, documents, k=20):
    """
    BM25 알고리즘으로 키워드 매칭
    - 장점: 정확한 용어 매칭
    - 단점: 동의어 처리 약함
    """
    tokenized_docs = [doc.split() for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    scores = bm25.get_scores(query.split())
    top_k = np.argsort(scores)[-k:][::-1]
    return top_k
```

#### 4.2.2 Vector 검색 (의미 기반)
```python
def vector_search(query, vector_store, k=20):
    """
    임베딩 기반 의미적 유사도 검색
    - 장점: 동의어, 유사 표현 매칭
    - 단점: 정확한 용어 매칭 약함
    """
    query_embedding = embeddings.embed_query(query)
    results = vector_store.similarity_search_by_vector(
        query_embedding,
        k=k,
        filter={"language": detected_lang, "type": predicted_type}
    )
    return results
```

#### 4.2.3 Reciprocal Rank Fusion (RRF)
```python
def reciprocal_rank_fusion(bm25_results, vector_results, k=60):
    """
    두 검색 결과를 융합
    RRF Score = Σ(1 / (k + rank_i))
    """
    scores = {}

    # BM25 점수
    for rank, doc_id in enumerate(bm25_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    # Vector 점수
    for rank, doc_id in enumerate(vector_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    # 정렬
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs
```

### 4.3 Reranking (재정렬)

```python
from sentence_transformers import CrossEncoder

def rerank_results(query, candidates, top_k=5):
    """
    Cross-Encoder로 정밀 재정렬
    모델: ms-marco-MiniLM-L-12-v2
    """
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

    # 쿼리-문서 쌍 생성
    pairs = [(query, doc.page_content) for doc in candidates]

    # 점수 계산
    scores = model.predict(pairs)

    # Top K 선택
    ranked_results = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    return ranked_results
```

### 4.4 프롬프트 엔지니어링

```python
SYSTEM_PROMPT = """
당신은 POSCO International의 CRM 시스템 전문 AI 어시스턴트입니다.

**역할**:
- CRM 매뉴얼을 기반으로 정확한 정보 제공
- 단계별 가이드 제시
- 사용자 친화적 설명

**지침**:
1. 항상 제공된 컨텍스트(매뉴얼)를 기반으로 답변
2. 확실하지 않은 정보는 추측하지 않음
3. 매뉴얼에 없는 내용은 "매뉴얼에서 해당 정보를 찾을 수 없습니다" 명시
4. 단계별 설명 시 번호 매기기 사용
5. 관련 스크린샷이나 그림이 있으면 언급
6. 답변 마지막에 출처(페이지 번호) 명시

**형식**:
- 간결하고 명확한 문장
- 전문 용어 사용 시 괄호로 설명 추가
- 필요시 표 형식 사용
"""

USER_PROMPT_TEMPLATE = """
**질문**: {query}

**관련 매뉴얼 내용**:
{context}

**지시사항**:
위 매뉴얼 내용을 바탕으로 질문에 답변해주세요.
답변 마지막에 [출처: 페이지 X, 섹션 Y] 형식으로 출처를 명시하세요.
"""
```

---

## 5. 기술 스택

### 5.1 백엔드

| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| **Framework** | FastAPI | 0.104+ | API 서버 |
| **Language** | Python | 3.11+ | 주 개발 언어 |
| **LLM Framework** | LangChain | 0.1+ | RAG 파이프라인 |
| **Vector DB** | Qdrant / Weaviate | Latest | 벡터 저장소 |
| **Cache** | Redis | 7.0+ | 응답 캐싱 |
| **Task Queue** | Celery | 5.3+ | 비동기 작업 |

### 5.2 AI/ML

| 구분 | 모델 | 용도 |
|------|------|------|
| **LLM** | GPT-4 / Claude 3.5 Sonnet | 답변 생성 |
| **Embedding** | OpenAI text-embedding-3-large | 벡터 임베딩 |
| **Reranker** | ms-marco-MiniLM-L-12-v2 | 검색 결과 재정렬 |
| **Language Detection** | langdetect / fasttext | 언어 감지 |

### 5.3 프론트엔드 (Optional)

| 구분 | 기술 | 용도 |
|------|------|------|
| **Framework** | React / Next.js | 웹 UI |
| **UI Library** | shadcn/ui | 컴포넌트 |
| **State** | Zustand | 상태 관리 |
| **API Client** | Axios | HTTP 통신 |

### 5.4 인프라

| 구분 | 기술 | 용도 |
|------|------|------|
| **Container** | Docker | 컨테이너화 |
| **Orchestration** | Kubernetes | 오케스트레이션 |
| **CI/CD** | GitHub Actions | 자동 배포 |
| **Monitoring** | Prometheus + Grafana | 모니터링 |
| **Logging** | ELK Stack | 로그 관리 |

---

## 6. 데이터베이스 스키마

### 6.1 Vector Database (Qdrant)

#### Collection 구조
```json
{
  "collection_name": "crm_account_ko",
  "vectors": {
    "size": 1536,  // OpenAI embedding dimension
    "distance": "Cosine"
  },
  "payload_schema": {
    "chunk_id": "string",
    "text": "string",
    "document_id": "string",
    "type": "keyword",      // account/meeting/order/common
    "language": "keyword",  // korean/english
    "section": "string",
    "section_title": "string",
    "page": "integer",
    "keywords": "string[]",
    "created_at": "datetime"
  }
}
```

### 6.2 관계형 DB (PostgreSQL)

#### documents 테이블
```sql
CREATE TABLE documents (
    document_id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(20) NOT NULL,  -- account/meeting/order/common
    language VARCHAR(10) NOT NULL,  -- korean/english
    version VARCHAR(10) NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    total_pages INTEGER,
    checksum VARCHAR(64),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'  -- active/archived
);

CREATE INDEX idx_documents_type_lang ON documents(type, language);
```

#### chunks 테이블
```sql
CREATE TABLE chunks (
    chunk_id VARCHAR(100) PRIMARY KEY,
    document_id VARCHAR(50) REFERENCES documents(document_id),
    text TEXT NOT NULL,
    section VARCHAR(20),
    section_title VARCHAR(200),
    page INTEGER,
    chunk_index INTEGER,
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunks_document ON chunks(document_id);
CREATE INDEX idx_chunks_page ON chunks(page);
```

#### chat_sessions 테이블
```sql
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE INDEX idx_sessions_user ON chat_sessions(user_id);
```

#### chat_messages 테이블
```sql
CREATE TABLE chat_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(session_id),
    role VARCHAR(10) NOT NULL,  -- user/assistant
    content TEXT NOT NULL,
    language VARCHAR(10),
    intent_type VARCHAR(20),  -- classified document type
    source_chunks TEXT[],  -- Array of chunk_ids used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_session ON chat_messages(session_id);
```

#### query_analytics 테이블
```sql
CREATE TABLE query_analytics (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(session_id),
    query TEXT NOT NULL,
    language VARCHAR(10),
    intent_type VARCHAR(20),
    retrieval_time_ms INTEGER,
    generation_time_ms INTEGER,
    total_time_ms INTEGER,
    chunks_retrieved INTEGER,
    user_feedback INTEGER,  -- 1-5 rating, NULL if no feedback
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_created ON query_analytics(created_at);
CREATE INDEX idx_analytics_feedback ON query_analytics(user_feedback);
```

---

## 7. API 설계

### 7.1 엔드포인트 목록

#### 7.1.1 Chat API

**POST /api/v1/chat/query**
```json
// Request
{
  "session_id": "uuid-string",  // optional
  "query": "거래선 등록 방법을 알려주세요",
  "language": "auto",  // auto/korean/english
  "context": {
    "previous_messages": []  // optional, for context
  }
}

// Response
{
  "session_id": "uuid-string",
  "message_id": "uuid-string",
  "answer": "거래선을 등록하려면 다음 단계를 따르세요...",
  "sources": [
    {
      "chunk_id": "crm_account_ko_p15_c1",
      "document": "P_INTL_CRM 매뉴얼(국문)_거래선&연락처",
      "section": "2.1 거래선 등록 절차",
      "page": 15,
      "relevance_score": 0.95
    }
  ],
  "metadata": {
    "language": "korean",
    "intent_type": "account_contact",
    "retrieval_time_ms": 234,
    "generation_time_ms": 1456,
    "total_time_ms": 1690
  }
}
```

**GET /api/v1/chat/sessions/{session_id}/history**
```json
// Response
{
  "session_id": "uuid-string",
  "messages": [
    {
      "message_id": "uuid-1",
      "role": "user",
      "content": "거래선 등록 방법은?",
      "created_at": "2025-11-03T10:00:00Z"
    },
    {
      "message_id": "uuid-2",
      "role": "assistant",
      "content": "거래선을 등록하려면...",
      "sources": [...],
      "created_at": "2025-11-03T10:00:02Z"
    }
  ]
}
```

**POST /api/v1/chat/feedback**
```json
// Request
{
  "message_id": "uuid-string",
  "rating": 5,  // 1-5
  "comment": "매우 도움이 되었습니다"  // optional
}

// Response
{
  "status": "success",
  "message": "피드백이 저장되었습니다"
}
```

#### 7.1.2 Document Management API

**GET /api/v1/documents**
```json
// Response
{
  "documents": [
    {
      "document_id": "crm_account_ko_v1",
      "type": "account_contact",
      "language": "korean",
      "version": "1.0",
      "total_pages": 150,
      "status": "active",
      "last_updated": "2025-11-03T09:00:00Z"
    }
  ]
}
```

**POST /api/v1/documents/upload**
```json
// Request (multipart/form-data)
{
  "file": "<PDF file>",
  "type": "account_contact",
  "language": "korean",
  "version": "1.1"
}

// Response
{
  "document_id": "crm_account_ko_v1_1",
  "status": "processing",
  "estimated_time_minutes": 5
}
```

**POST /api/v1/documents/{document_id}/reindex**
```json
// Response
{
  "status": "started",
  "job_id": "reindex-job-123"
}
```

#### 7.1.3 Analytics API

**GET /api/v1/analytics/usage**
```json
// Query params: ?start_date=2025-11-01&end_date=2025-11-03

// Response
{
  "period": {
    "start": "2025-11-01",
    "end": "2025-11-03"
  },
  "metrics": {
    "total_queries": 1250,
    "unique_users": 456,
    "avg_response_time_ms": 1823,
    "avg_rating": 4.3,
    "queries_by_type": {
      "account_contact": 450,
      "meeting_memo": 320,
      "order_fulfillment": 280,
      "common_master": 200
    },
    "queries_by_language": {
      "korean": 980,
      "english": 270
    }
  }
}
```

**GET /api/v1/analytics/popular-queries**
```json
// Response
{
  "queries": [
    {
      "query": "거래선 등록 방법",
      "count": 45,
      "avg_rating": 4.5
    },
    {
      "query": "미팅메모 작성",
      "count": 38,
      "avg_rating": 4.2
    }
  ]
}
```

---

## 8. 보안 및 권한 관리

### 8.1 인증 (Authentication)

#### JWT 기반 인증
```python
# Token 구조
{
  "sub": "user@poscointl.com",  # User email
  "user_id": "12345",
  "name": "홍길동",
  "department": "영업1팀",
  "role": "user",  # user/admin
  "exp": 1730678400,  # Expiration timestamp
  "iat": 1730592000   # Issued at
}
```

#### SSO 통합 (POSCO 사내 시스템)
- SAML 2.0 / OAuth 2.0 연동
- 기존 EP 시스템 인증 정보 활용

### 8.2 권한 관리 (Authorization)

| 역할 | 권한 |
|------|------|
| **User** | - 챗봇 질문<br>- 대화 이력 조회<br>- 피드백 제출 |
| **Admin** | - User 권한 전체<br>- 문서 업로드/삭제<br>- 분석 대시보드 접근<br>- 시스템 설정 변경 |
| **Super Admin** | - Admin 권한 전체<br>- 사용자 관리<br>- 시스템 재시작 |

### 8.3 데이터 보안

#### 전송 구간 암호화
- **HTTPS/TLS 1.3** 필수
- API 키 암호화 저장 (Vault)

#### 저장 데이터 보호
- **개인정보 마스킹**: 로그에서 이메일, 이름 자동 마스킹
- **데이터 암호화**: DB 컬럼 암호화 (AES-256)
- **백업 암호화**: 백업 파일 암호화 저장

#### 접근 로그
```python
# 모든 API 요청 로깅
{
  "timestamp": "2025-11-03T10:00:00Z",
  "user_id": "12345",
  "ip_address": "192.168.1.100",
  "endpoint": "/api/v1/chat/query",
  "method": "POST",
  "response_time_ms": 1823,
  "status_code": 200
}
```

---

## 9. 성능 최적화 전략

### 9.1 캐싱 전략

#### 9.1.1 Redis 캐시 구조
```python
# 자주 묻는 질문 캐싱
CACHE_KEY = f"query:{hash(query)}:{language}"
CACHE_TTL = 3600  # 1 hour

# 캐시 히트 시 즉시 반환 (< 50ms)
cached_answer = redis.get(CACHE_KEY)
if cached_answer:
    return cached_answer
```

#### 9.1.2 벡터 검색 캐싱
```python
# 임베딩 캐싱
EMBEDDING_CACHE_KEY = f"embedding:{hash(text)}"
EMBEDDING_TTL = 86400  # 24 hours

# 동일 쿼리 반복 시 임베딩 재계산 방지
```

### 9.2 인덱싱 최적화

#### Vector DB 인덱스
```python
# HNSW (Hierarchical Navigable Small World) 인덱스
index_params = {
    "m": 16,        # Number of connections
    "ef_construct": 200,  # Construction time accuracy
    "ef": 100       # Search time accuracy
}
# Trade-off: 정확도 vs 속도
```

### 9.3 배치 처리

```python
# 문서 업로드 시 비동기 처리
@celery.task
def process_document(document_id):
    # 1. PDF 파싱
    # 2. 청킹
    # 3. 임베딩 (배치 처리)
    # 4. 벡터 DB 저장

# 배치 임베딩 (100개 청크씩)
embeddings = openai.Embedding.create(
    input=chunk_texts,  # List of 100 texts
    model="text-embedding-3-large"
)
```

### 9.4 성능 목표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **응답 시간 (P50)** | < 2초 | Prometheus |
| **응답 시간 (P95)** | < 4초 | Prometheus |
| **캐시 히트율** | > 30% | Redis Stats |
| **검색 정확도** | > 95% | 사용자 피드백 |
| **동시 사용자** | 500+ | Load Test |
| **시스템 가용률** | 99.9% | Uptime Monitor |

---

## 10. 테스트 전략

### 10.1 단위 테스트

```python
# tests/test_query_preprocessor.py
def test_language_detection():
    assert detect_language("거래선 등록 방법") == "korean"
    assert detect_language("How to register account") == "english"

def test_intent_classification():
    query = "거래선 담당자를 추가하려면?"
    assert classify_intent(query) == "account_contact"
```

### 10.2 통합 테스트

```python
# tests/test_rag_pipeline.py
def test_end_to_end_query():
    query = "미팅메모 작성 방법"
    response = rag_pipeline.process(query)

    assert response.answer is not None
    assert len(response.sources) > 0
    assert response.metadata.language == "korean"
    assert "미팅" in response.answer
```

### 10.3 성능 테스트

```python
# tests/test_performance.py
def test_response_time():
    query = "거래선 등록 방법"
    start = time.time()
    response = chat_api.query(query)
    elapsed = time.time() - start

    assert elapsed < 2.0  # Must respond within 2 seconds
```

### 10.4 테스트 데이터셋

```json
// tests/fixtures/test_queries.json
[
  {
    "query": "거래선 등록 방법은?",
    "expected_intent": "account_contact",
    "expected_language": "korean",
    "expected_sources": ["crm_account_ko"]
  },
  {
    "query": "How to create a meeting memo?",
    "expected_intent": "meeting_memo",
    "expected_language": "english",
    "expected_sources": ["crm_meeting_en"]
  }
]
```

### 10.5 평가 메트릭

#### Retrieval 품질
```python
# Precision@K
def precision_at_k(retrieved_docs, relevant_docs, k):
    retrieved_k = retrieved_docs[:k]
    relevant_count = sum(1 for doc in retrieved_k if doc in relevant_docs)
    return relevant_count / k

# MRR (Mean Reciprocal Rank)
def mean_reciprocal_rank(results):
    reciprocal_ranks = []
    for result in results:
        for i, doc in enumerate(result.retrieved_docs, 1):
            if doc in result.relevant_docs:
                reciprocal_ranks.append(1 / i)
                break
    return sum(reciprocal_ranks) / len(results)
```

#### Generation 품질
```python
# BLEU Score (참조 답변과 비교)
# ROUGE Score
# BERTScore (의미적 유사도)
```

---

## 11. 배포 및 운영

### 11.1 Docker 구성

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://user:pass@postgres:5432/crm_bot
    depends_on:
      - qdrant
      - redis
      - postgres

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=crm_bot
    volumes:
      - postgres_data:/var/lib/postgresql/data

  celery:
    build: .
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - redis

volumes:
  qdrant_data:
  postgres_data:
```

### 11.3 Kubernetes 배포 (선택사항)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crm-chatbot-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crm-chatbot-api
  template:
    metadata:
      labels:
        app: crm-chatbot-api
    spec:
      containers:
      - name: api
        image: posco/crm-chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

### 11.4 모니터링

#### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

# 메트릭 정의
query_counter = Counter('chatbot_queries_total', 'Total queries')
response_time = Histogram('chatbot_response_seconds', 'Response time')
cache_hits = Counter('chatbot_cache_hits', 'Cache hits')

# 사용
@response_time.time()
def process_query(query):
    query_counter.inc()
    # ... 처리 로직
```

#### Grafana Dashboard
- 실시간 쿼리 수
- 평균 응답 시간
- 캐시 히트율
- 에러율
- 사용자 만족도 (평균 평점)

### 11.5 로깅

```python
# logging_config.py
import logging

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
```

---

## 12. 구현 로드맵

### Phase 1: MVP (2주)
**목표**: 기본 RAG 챗봇 구축

- [ ] **Week 1**: 데이터 준비 및 인프라 설정
  - [ ] PDF 파싱 및 청킹 (2일)
  - [ ] Vector DB 설정 (Qdrant) (1일)
  - [ ] 임베딩 생성 및 인덱싱 (2일)
  - [ ] 기본 API 서버 구축 (FastAPI) (2일)

- [ ] **Week 2**: RAG 파이프라인 구현
  - [ ] 기본 검색 로직 (Vector Search) (2일)
  - [ ] LLM 통합 (OpenAI/Claude) (1일)
  - [ ] 프롬프트 엔지니어링 (1일)
  - [ ] 간단한 웹 UI (Streamlit) (2일)
  - [ ] 내부 테스트 (1일)

**산출물**:
- 작동하는 기본 챗봇
- 한국어 매뉴얼 1개 (Account) 지원
- 간단한 웹 인터페이스

---

### Phase 2: 고도화 (2주)
**목표**: 검색 정확도 향상 및 전체 문서 통합

- [ ] **Week 3**: 검색 개선
  - [ ] 하이브리드 검색 구현 (BM25 + Vector) (2일)
  - [ ] Reranking 추가 (Cross-Encoder) (1일)
  - [ ] 전체 8개 문서 인덱싱 (2일)
  - [ ] 스마트 라우팅 시스템 구현 (2일)

- [ ] **Week 4**: 다국어 및 최적화
  - [ ] 언어 자동 감지 및 처리 (1일)
  - [ ] 의도 분류 개선 (1일)
  - [ ] 캐싱 시스템 (Redis) (1일)
  - [ ] 성능 테스트 및 튜닝 (2일)

**산출물**:
- 전체 8개 문서 지원
- 한/영 자동 전환
- 응답 시간 < 3초

---

### Phase 3: 프로덕션 준비 (2주)
**목표**: 보안, 모니터링, 운영 준비

- [ ] **Week 5**: 보안 및 인증
  - [ ] JWT 인증 구현 (1일)
  - [ ] SSO 연동 (POSCO 사내 시스템) (2일)
  - [ ] API Rate Limiting (1일)
  - [ ] 로깅 시스템 구축 (1일)

- [ ] **Week 6**: 모니터링 및 분석
  - [ ] Prometheus + Grafana 설정 (1일)
  - [ ] 사용자 피드백 시스템 (1일)
  - [ ] 분석 대시보드 (1일)
  - [ ] 부하 테스트 (1일)
  - [ ] 문서화 완성 (1일)

**산출물**:
- 프로덕션 환경 배포 준비 완료
- 모니터링 대시보드
- 운영 매뉴얼

---

### Phase 4: 출시 및 운영 (진행중)
**목표**: 실사용자 피드백 기반 개선

- [ ] **Week 7-8**: 파일럿 운영
  - [ ] 제한된 사용자 그룹 오픈 (10-20명)
  - [ ] 피드백 수집 및 분석
  - [ ] 버그 수정 및 개선
  - [ ] 추가 FAQ 데이터 구축

- [ ] **Week 9+**: 전사 확대
  - [ ] 전체 임직원 오픈
  - [ ] 지속적 모니터링
  - [ ] 정기적 모델 업데이트
  - [ ] 신규 매뉴얼 추가

**산출물**:
- 안정적인 서비스 운영
- 주간 분석 리포트
- 개선 사항 지속 반영

---

### 장기 로드맵 (3-6개월)

#### 추가 기능
- [ ] **음성 인터페이스**: 음성 질문 → 음성 답변
- [ ] **이미지 검색**: 스크린샷 업로드 → 해당 화면 설명
- [ ] **멀티모달**: 매뉴얼 이미지 직접 표시
- [ ] **추천 시스템**: "이 답변이 도움이 되었다면, 이것도 참고하세요"
- [ ] **Slack/Teams 봇**: 메신저 통합
- [ ] **모바일 앱**: iOS/Android 네이티브 앱

#### 고급 기능
- [ ] **Fine-tuning**: CRM 도메인 특화 모델
- [ ] **A/B 테스트**: 프롬프트/모델 성능 비교
- [ ] **자동 업데이트**: 매뉴얼 변경 시 자동 재인덱싱
- [ ] **다국어 확장**: 중국어, 일본어 추가

---

## 13. 위험 관리 및 대응

### 13.1 기술적 위험

| 위험 | 영향 | 확률 | 대응 방안 |
|------|------|------|----------|
| **LLM API 장애** | 높음 | 중간 | Fallback 모델 준비 (Claude ↔ GPT) |
| **벡터 DB 성능 저하** | 중간 | 낮음 | 인덱스 최적화, 샤딩 |
| **메모리 부족** | 중간 | 중간 | 배치 크기 조절, 스트리밍 |
| **임베딩 비용 초과** | 낮음 | 중간 | 캐싱 강화, 배치 처리 |

### 13.2 운영 위험

| 위험 | 영향 | 확률 | 대응 방안 |
|------|------|------|----------|
| **부정확한 답변** | 높음 | 중간 | 피드백 루프, 지속 개선 |
| **매뉴얼 업데이트 미반영** | 중간 | 높음 | 자동 모니터링, 주기적 재인덱싱 |
| **사용자 불만족** | 중간 | 중간 | 피드백 시스템, A/B 테스트 |
| **동시 접속 폭주** | 높음 | 낮음 | Auto-scaling, Queue 시스템 |

---

## 14. 참고 자료

### 14.1 기술 문서
- [LangChain Documentation](https://python.langchain.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### 14.2 논문 및 자료
- **RAG**: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
- **Hybrid Search**: "Combining Lexical and Semantic Search" (Microsoft Research)
- **Chunking Strategy**: "Optimal Chunking for RAG Systems" (Pinecone Blog)

### 14.3 오픈소스 참고
- [LangChain RAG Tutorials](https://github.com/langchain-ai/langchain)
- [Haystack Pipeline](https://github.com/deepset-ai/haystack)
- [LlamaIndex](https://github.com/run-llama/llama_index)

---

## 15. 부록

### 15.1 용어 정의

| 용어 | 설명 |
|------|------|
| **RAG** | Retrieval-Augmented Generation, 검색 증강 생성 |
| **Embedding** | 텍스트를 벡터로 변환한 것 |
| **Chunking** | 문서를 작은 단위로 분할 |
| **Vector DB** | 벡터 임베딩을 저장하는 데이터베이스 |
| **Reranking** | 검색 결과를 재정렬하여 정확도 향상 |
| **BM25** | 키워드 기반 검색 알고리즘 |
| **Cross-Encoder** | 쿼리-문서 쌍의 관련성을 직접 평가하는 모델 |
| **RRF** | Reciprocal Rank Fusion, 여러 검색 결과 융합 |

### 15.2 프로젝트 디렉토리 구조

```
crm-rag-chatbot/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   └── analytics.py
│   │   ├── middleware/
│   │   └── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── rag/
│   │   ├── preprocessor.py
│   │   ├── router.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   └── generator.py
│   ├── services/
│   │   ├── embedding_service.py
│   │   ├── vector_service.py
│   │   └── llm_service.py
│   ├── models/
│   │   ├── database.py
│   │   └── schemas.py
│   └── utils/
│       ├── pdf_parser.py
│       ├── chunker.py
│       └── text_processor.py
├── data/
│   ├── raw/              # 원본 PDF
│   ├── processed/        # 처리된 청크
│   └── embeddings/       # 임베딩 캐시
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/
│   ├── ingest_documents.py
│   ├── create_indexes.py
│   └── benchmark.py
├── config/
│   ├── dev.yaml
│   ├── prod.yaml
│   └── logging.yaml
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── OPERATION.md
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
└── README.md
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0.0 | 2025-11-03 | 초안 작성 | AI Team |

---

## 문의

**프로젝트 담당자**: AI Development Team
**이메일**: ai-team@poscointl.com
**Slack**: #crm-chatbot-dev
