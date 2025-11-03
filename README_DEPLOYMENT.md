# CRM RAG Chatbot - 배포 가이드

## 🚀 Vercel 배포 방법

### 1. 사전 준비

#### 필수 계정
- [GitHub](https://github.com) 계정
- [Vercel](https://vercel.com) 계정 (GitHub으로 로그인 가능)
- OpenAI API 키

### 2. GitHub 저장소 설정

#### Step 1: 저장소 생성
```bash
# 현재 디렉토리를 Git 저장소로 초기화
git init

# .gitignore 파일 확인 (이미 생성됨)
cat .gitignore

# 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: CRM RAG Chatbot"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/crm-rag-chatbot.git
git branch -M main
git push -u origin main
```

#### Step 2: GitHub Secrets 설정
1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. 다음 Secrets 추가:
   - `VERCEL_TOKEN`: Vercel Personal Access Token
   - `VERCEL_ORG_ID`: Vercel Organization ID
   - `VERCEL_PROJECT_ID`: Vercel Project ID

### 3. Vercel 프로젝트 설정

#### Step 1: Vercel 프로젝트 생성
1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. "Add New..." → "Project" 클릭
3. GitHub 저장소 선택 (crm-rag-chatbot)
4. "Import" 클릭

#### Step 2: 환경 변수 설정
**Project Settings → Environment Variables**에서 다음을 추가:

| Name | Value | Environment |
|------|-------|-------------|
| `OPENAI_API_KEY` | sk-... | Production, Preview, Development |

⚠️ **중요**: API 키는 절대 코드에 직접 넣지 마세요!

#### Step 3: 빌드 설정
- **Framework Preset**: Other
- **Build Command**: (비워둠)
- **Output Directory**: (비워둠)
- **Install Command**: `pip install -r requirements-vercel.txt`

### 4. 데이터 파일 처리

#### 옵션 A: GitHub에 포함 (권장하지 않음)
```bash
# .gitignore에서 제외하고 푸시
git add data/processed/*.json
git add data/embeddings/*.json
git commit -m "Add processed data"
git push
```

#### 옵션 B: Vercel Blob Storage 사용 (권장)
```python
# app.py에 추가
from vercel_blob import put, get

# 데이터 업로드
with open('data/processed/file.json', 'rb') as f:
    blob = put('file.json', f, access='public')

# 데이터 로드
data = get('file.json')
```

#### 옵션 C: 외부 스토리지 (S3, GCS 등)
- AWS S3 버킷 사용
- Google Cloud Storage 사용
- 환경 변수로 접근 키 관리

### 5. 배포 확인

#### 자동 배포
- `main` 브랜치에 푸시하면 자동으로 배포됩니다
- GitHub Actions → Vercel 자동 배포

#### 수동 배포
```bash
# Vercel CLI 설치
npm install -g vercel

# 배포
vercel --prod
```

### 6. 배포 URL 확인

배포 완료 후:
- Production URL: `https://your-project.vercel.app`
- Preview URL: 각 PR마다 자동 생성

---

## 🔧 문제 해결

### 1. 빌드 실패

**문제**: `requirements-vercel.txt` 설치 오류
```bash
# 해결: Python 버전 확인
python --version  # 3.11 이상 필요
```

### 2. 메모리 부족

**문제**: Vercel 메모리 제한 (1GB)
```python
# 해결: 데이터 스트리밍 로드
@st.cache_resource
def load_data_streaming():
    # 청크 단위로 로드
    pass
```

### 3. Cold Start 지연

**문제**: 첫 로딩 시간이 길다
```python
# 해결: Vercel Serverless Functions Warm-up
# vercel.json에 추가
{
  "functions": {
    "app.py": {
      "memory": 3008,
      "maxDuration": 60
    }
  }
}
```

### 4. 환경 변수 문제

**문제**: `OPENAI_API_KEY not found`
```bash
# 해결: Vercel Dashboard에서 환경 변수 확인
# Project Settings → Environment Variables
```

---

## 📊 비용 예상

### Vercel 무료 플랜
- **대역폭**: 100GB/월
- **실행 시간**: 100GB-Hrs/월
- **빌드**: 6,000분/월
- **팀원**: 1명

### 유료 플랜 (Pro - $20/월)
- **대역폭**: 1TB/월
- **실행 시간**: 1,000GB-Hrs/월
- **빌드**: 무제한
- **팀원**: 무제한

### OpenAI API 비용
- **임베딩**: ~$0.0001/쿼리
- **GPT-4**: ~$0.03-0.05/쿼리
- **GPT-3.5**: ~$0.002-0.005/쿼리

**예상 월 비용** (1000 쿼리 기준):
- Vercel: 무료 (무료 플랜 내)
- OpenAI: $2-50 (모델에 따라)

---

## 🔐 보안 권장사항

### 1. API 키 보호
```bash
# 절대 하지 말 것
OPENAI_API_KEY=sk-... # ❌ 코드에 직접 입력

# 올바른 방법
# Vercel Environment Variables 사용 ✅
```

### 2. Rate Limiting
```python
# app.py에 추가
from streamlit_rate_limiter import rate_limiter

@rate_limiter(max_calls=10, period=60)  # 1분에 10회
def process_query(query):
    pass
```

### 3. 사용자 인증
```python
# 간단한 패스워드 보호
import streamlit as st

def check_password():
    password = st.text_input("Password", type="password")
    if password == st.secrets["app_password"]:
        return True
    return False

if not check_password():
    st.stop()
```

---

## 📝 체크리스트

배포 전 확인사항:

- [ ] GitHub 저장소 생성
- [ ] .gitignore 확인 (.env 제외)
- [ ] requirements-vercel.txt 확인
- [ ] Vercel 프로젝트 생성
- [ ] 환경 변수 설정 (OPENAI_API_KEY)
- [ ] 데이터 파일 처리 방법 결정
- [ ] 첫 커밋 및 푸시
- [ ] 배포 확인
- [ ] 테스트 쿼리 실행
- [ ] 성능 모니터링 설정

---

## 🎯 다음 단계

배포 후 개선사항:

1. **모니터링**
   - Vercel Analytics 활성화
   - 사용량 추적

2. **최적화**
   - 캐싱 전략 개선
   - 응답 시간 단축

3. **기능 추가**
   - 사용자 피드백 수집
   - 대화 히스토리 저장

4. **보안 강화**
   - Rate limiting
   - 사용자 인증

---

## 📞 지원

문제가 발생하면:
- [Vercel Documentation](https://vercel.com/docs)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- GitHub Issues

---

**Last Updated**: 2025-11-03
**Version**: 1.0.0
