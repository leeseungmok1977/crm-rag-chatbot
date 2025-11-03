# 빠른 시작 가이드 (Windows)

## 1단계: 가상환경 생성 및 활성화

```powershell
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화 (PowerShell)
.\venv\Scripts\Activate.ps1

# 또는 CMD 사용 시
# venv\Scripts\activate.bat
```

**실행 정책 오류가 발생하는 경우**:
```powershell
# 현재 세션에서만 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 그 후 다시 활성화
.\venv\Scripts\Activate.ps1
```

가상환경이 활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다:
```
(venv) PS D:\work\2025_workspace\2025_newCRM_AI RAG bot>
```

## 2단계: 의존성 설치

```powershell
pip install -r requirements.txt
```

**설치 시간**: 약 2-3분 소요

## 3단계: 환경 변수 설정

```powershell
# .env 파일 생성
Copy-Item .env.example .env

# .env 파일을 편집기로 열기
notepad .env
```

**.env 파일에서 수정해야 할 내용**:
```env
OPENAI_API_KEY=sk-your_actual_api_key_here  # 여기에 실제 API 키 입력
```

OpenAI API 키 발급: https://platform.openai.com/api-keys

## 4단계: Qdrant Vector Database 실행

**옵션 A: Docker 사용 (권장)**
```powershell
# Docker Desktop이 설치되어 있어야 함
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant

# 실행 확인
docker ps
```

**옵션 B: Docker 없이 테스트**
```powershell
# 메모리 모드로 테스트 (영구 저장 안됨)
# 코드에서 use_memory=True 옵션 사용
```

## 5단계: 문서 처리 실행

### 5-1. 테스트 실행 (단일 파일)

```powershell
# 한 개 파일로 먼저 테스트
python scripts/process_documents.py "PDF/P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf"
```

**예상 출력**:
```
============================================================
🚀 CRM Document Processing Pipeline
============================================================
Input: PDF/P_INTL_CRM 매뉴얼(국문)_거래선&연락처.pdf
Strategy: recursive
...
✅ Processing completed!
   - Document ID: crm_account_ko_v1_0
   - Chunks: 285
   - Time: 125.34s
```

### 5-2. 전체 문서 처리

```powershell
# PDF 폴더의 모든 파일 처리
python scripts/process_documents.py PDF/

# 또는 청킹 전략 변경
python scripts/process_documents.py PDF/ --strategy semantic

# 컬렉션 재생성 (기존 데이터 삭제 후 재처리)
python scripts/process_documents.py PDF/ --recreate-collections
```

**전체 처리 시간**: 약 15-20분 (8개 파일, 캐시 없음 기준)

## 6단계: 결과 확인

### 처리된 파일 확인
```powershell
# 청크 JSON 파일
dir data/processed/*.json

# 처리 리포트
cat data/processed/processing_report.json
```

### Qdrant 데이터 확인
```powershell
# Qdrant 웹 UI 접속
# 브라우저에서: http://localhost:6333/dashboard

# 또는 Python으로 확인
python -c "from src.services.vector_store import MultiCollectionVectorStore; store = MultiCollectionVectorStore(); print(store.get_all_stats())"
```

## 🔍 문제 해결

### 1. ModuleNotFoundError
```powershell
# 가상환경이 활성화되었는지 확인
# 프롬프트에 (venv)가 표시되어야 함

# 의존성 재설치
pip install -r requirements.txt
```

### 2. OpenAI API 오류
```powershell
# API 키 확인
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('OPENAI_API_KEY')[:20] + '...')"

# .env 파일이 올바른 위치에 있는지 확인
dir .env
```

### 3. Qdrant 연결 오류
```powershell
# Docker 컨테이너 실행 확인
docker ps | findstr qdrant

# Qdrant 재시작
docker restart qdrant

# 또는 메모리 모드로 테스트 (임시)
# pipeline.py에서 use_memory=True 옵션 사용
```

### 4. 메모리 부족
```powershell
# 배치 크기 줄이기
python scripts/process_documents.py PDF/ --batch-size 50

# 또는 한 번에 한 파일씩 처리
python scripts/process_documents.py "PDF/파일1.pdf"
python scripts/process_documents.py "PDF/파일2.pdf"
```

### 5. 한글 인코딩 오류
```powershell
# PowerShell 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING="utf-8"

# 재실행
python scripts/process_documents.py PDF/
```

## 📊 비용 안내

### OpenAI Embedding API 비용
- **모델**: text-embedding-3-large
- **가격**: $0.00013 / 1K tokens
- **전체 8개 문서**: 약 $0.15 ~ $0.20

### 캐싱 효과
- **첫 처리**: ~$0.20
- **재처리**: $0 (캐시 사용)

## ✅ 다음 단계

데이터 파이프라인이 완료되면:

1. **RAG 엔진 구현** - 검색 및 답변 생성
2. **API 서버 구축** - FastAPI 기반
3. **채팅 인터페이스** - Streamlit/React

## 📚 상세 문서

- [전체 README](README.md)
- [설계 문서](CRM_RAG_CHATBOT_DESIGN.md)

## 💡 유용한 명령어

```powershell
# 가상환경 비활성화
deactivate

# 특정 모듈 테스트
python src/utils/pdf_parser.py "PDF/sample.pdf"
python src/utils/metadata_extractor.py "PDF/"

# 캐시 삭제 (재처리 전)
Remove-Item -Recurse data/embeddings/*

# 처리 결과 삭제
Remove-Item -Recurse data/processed/*

# Qdrant 데이터 삭제 (컬렉션 재생성)
python scripts/process_documents.py PDF/ --recreate-collections
```

## 🆘 도움말

```powershell
# 스크립트 도움말
python scripts/process_documents.py --help
```

**출력**:
```
usage: process_documents.py [-h] [--strategy {fixed,recursive,semantic,token}]
                           [--recreate-collections] [--no-cache]
                           [--batch-size BATCH_SIZE]
                           input_path

CRM Manual Document Processing Pipeline

positional arguments:
  input_path            PDF file or folder path

optional arguments:
  -h, --help            show this help message and exit
  --strategy {fixed,recursive,semantic,token}
                        Chunking strategy (default: recursive)
  --recreate-collections
                        Recreate vector collections (delete existing data)
  --no-cache            Disable embedding cache
  --batch-size BATCH_SIZE
                        Batch size for embedding (default: 100)
```
