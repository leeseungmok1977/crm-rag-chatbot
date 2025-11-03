# Streamlit Chatbot UI Guide

## 개요

POSCO International CRM 매뉴얼 기반 RAG 챗봇의 Streamlit 웹 인터페이스입니다.

## 주요 기능

### 1. 대화형 인터페이스
- 실시간 채팅 UI
- 질문 및 답변 히스토리 유지
- 한국어/영어 자동 감지 및 처리

### 2. 검색 결과 표시
- 관련 문서 자동 검색
- 유사도 점수 표시
- 출처 문서 정보 제공

### 3. LLM 답변 생성
- GPT-4 / GPT-3.5 Turbo 지원
- 프롬프트 템플릿 기반 답변
- 컨텍스트 기반 정확한 응답

### 4. 소스 출처 표시
- 답변 근거가 된 문서 청크 표시
- 문서 타입 및 ID 표시
- 관련도 점수 표시

## 실행 방법

### 1. 환경 준비

```powershell
# 가상환경 활성화
.\venv\Scripts\Activate.ps1

# .env 파일에 API 키 확인
# OPENAI_API_KEY가 설정되어 있어야 함
```

### 2. Streamlit 앱 실행

```powershell
# 기본 실행
streamlit run app.py

# 포트 지정
streamlit run app.py --server.port 8501

# 자동 브라우저 열기 비활성화
streamlit run app.py --server.headless true
```

### 3. 웹 브라우저 접속

- 기본 URL: http://localhost:8501
- 앱이 자동으로 브라우저를 열어줍니다

## UI 구성

### 메인 화면

```
┌─────────────────────────────────────┐
│        💬 CRM Chatbot               │
│   POSCO International CRM Manual    │
├─────────────────────────────────────┤
│                                     │
│  [채팅 메시지 영역]                   │
│                                     │
│  🙋 You: 질문...                    │
│  🤖 Assistant: 답변...               │
│     📚 Sources: [출처 문서들]        │
│                                     │
├─────────────────────────────────────┤
│  💬 질문을 입력하세요...              │
└─────────────────────────────────────┘
```

### 사이드바

```
⚙️ Settings
├─ LLM Model (GPT-4 / GPT-3.5)
└─ Temperature (0.0 - 1.0)

📊 Statistics
├─ Total Documents: 8
├─ Total Chunks: 355
└─ Queries: N

🗑️ Clear Chat History
```

## 사용 예시

### 예시 1: 한국어 질문

**질문:**
```
거래선 등록은 어떻게 하나요?
```

**답변:**
```
거래선(Account) 등록 방법은 다음과 같습니다:

1. CRM 메뉴에서 "거래선 관리" 선택
2. "신규 등록" 버튼 클릭
3. 필수 정보 입력:
   - 거래선명
   - 사업자등록번호
   - 주소
   - 담당자 정보
4. "저장" 버튼 클릭

[출처: crm_account_ko - P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf]
```

### 예시 2: 영어 질문

**질문:**
```
How do I create a meeting memo?
```

**답변:**
```
To create a meeting memo in the CRM system:

1. Navigate to "Meeting Memo" section
2. Click "New Memo" button
3. Fill in required fields:
   - Meeting date and time
   - Participants
   - Meeting location
   - Discussion topics
4. Save the memo

[Source: crm_meeting_en - P_INTL_CRM Manual(EN)_Meeting Memo.pdf]
```

## 기능 설명

### 1. 언어 자동 감지

```python
# 질문 언어를 자동으로 감지
"거래선 등록" → 한국어 감지 → 한국어 문서 검색
"How to create" → 영어 감지 → 영어 문서 검색
```

### 2. 벡터 검색

```python
# 쿼리와 가장 관련성 높은 문서 청크 검색
Top 5 results:
1. Score: 0.72 - crm_account_ko
2. Score: 0.68 - crm_account_ko
3. Score: 0.65 - crm_common_ko
...
```

### 3. LLM 답변 생성

```python
# 검색된 문서를 기반으로 GPT-4가 답변 생성
System Prompt: "당신은 CRM 전문가입니다..."
Context: [검색된 문서들]
User Query: "거래선 등록 방법"
→ 답변 생성
```

### 4. 출처 표시

```python
📚 Sources
[1] account_contact - Score: 0.72
    - Document: crm_account_ko_v1_0
    - Language: korean
    - Preview: 거래선 등록은 다음과 같은 절차로...
```

## 설정 옵션

### LLM 모델 선택

- **GPT-4**: 더 정확하지만 느리고 비용 높음
  - 복잡한 질문에 적합
  - 추론 능력 우수

- **GPT-3.5 Turbo**: 빠르고 비용 저렴
  - 간단한 질문에 적합
  - 응답 속도 빠름

### Temperature 설정

- **0.0 - 0.3**: 매우 일관적이고 정확한 답변 (권장)
- **0.4 - 0.7**: 약간의 창의성 추가
- **0.8 - 1.0**: 창의적이지만 일관성 낮음

## 성능 최적화

### 1. 캐싱 활용

```python
@st.cache_resource  # 서비스는 한 번만 초기화
@st.cache_data      # 데이터는 캐시에서 로드
```

### 2. 배치 처리

```python
# 여러 청크를 한 번에 임베딩
embeddings = embedding_service.embed_batch(chunk_texts)
```

### 3. 메모리 모드

```python
# Qdrant 메모리 모드로 빠른 검색
vector_store = VectorStore(use_memory=True)
```

## 문제 해결

### 1. "OPENAI_API_KEY not found"

**.env 파일 확인**
```powershell
cat .env
# OPENAI_API_KEY=sk-...
```

### 2. "No chunks found"

**데이터 처리 실행**
```powershell
python scripts/process_documents.py PDF\
```

### 3. "Connection refused"

**정상 동작 - 메모리 모드 사용 중**
```
⚠️ Cannot connect to Qdrant server
⚠️ Using in-memory mode
```

### 4. 느린 응답 속도

**원인:**
- GPT-4 사용 시 10-20초 소요
- 임베딩 캐시 미적중

**해결:**
- GPT-3.5 Turbo 사용 (5-10초)
- 임베딩 캐시 확인: `ls data/embeddings`

## 비용 예상

### 검색 비용 (OpenAI Embeddings)

- **쿼리당**: ~$0.0001 (캐시 히트 시 $0)
- **월 1000 쿼리**: ~$0.10

### LLM 비용 (OpenAI GPT)

**GPT-4:**
- **쿼리당**: ~$0.03 - $0.05
- **월 1000 쿼리**: ~$30 - $50

**GPT-3.5 Turbo:**
- **쿼리당**: ~$0.002 - $0.005
- **월 1000 쿼리**: ~$2 - $5

## 보안 고려사항

### 1. API 키 보호

```powershell
# .env 파일을 절대 Git에 커밋하지 마세요
# .gitignore에 포함되어 있는지 확인
cat .gitignore | Select-String ".env"
```

### 2. 접근 제어

```python
# 프로덕션 배포 시 인증 추가
# Streamlit Cloud의 경우 Secrets 사용
st.secrets["OPENAI_API_KEY"]
```

## 배포 옵션

### 1. 로컬 실행 (현재)

```powershell
streamlit run app.py
```

### 2. Streamlit Cloud (무료)

```powershell
# GitHub에 푸시 후
# share.streamlit.io에서 연결
```

### 3. Docker 컨테이너

```dockerfile
FROM python:3.13
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

### 4. 클라우드 서버

- AWS EC2
- Google Cloud Run
- Azure Web Apps

## 다음 단계

1. **사용자 피드백 수집**
   - 답변 평가 기능 (👍/👎)
   - 피드백 저장

2. **고급 기능 추가**
   - 대화 컨텍스트 유지
   - 다중 턴 대화
   - 파일 업로드 (PDF 직접 검색)

3. **프로덕션 배포**
   - 인증 시스템
   - 사용량 모니터링
   - 로깅 및 분석

## 참고 자료

- [Streamlit Documentation](https://docs.streamlit.io)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation)

---

**Last Updated**: 2025-11-03
**Version**: 1.0.0
