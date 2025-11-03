# 🚀 빠른 배포 가이드 (5분)

## Step 1: GitHub 저장소 생성 (1분)

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit: CRM RAG Chatbot"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/crm-rag-chatbot.git
git push -u origin main
```

---

## Step 2: Vercel 배포 (2분)

### 방법 A: Vercel Dashboard (추천)

1. [vercel.com](https://vercel.com) 접속 및 GitHub 로그인
2. "Add New..." → "Project" 클릭
3. 방금 만든 GitHub 저장소 선택
4. "Import" 클릭

### 방법 B: Vercel CLI

```bash
# Vercel CLI 설치
npm install -g vercel

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

---

## Step 3: 환경 변수 설정 (2분)

**Vercel Dashboard → Project Settings → Environment Variables**

추가할 변수:

| Name | Value |
|------|-------|
| `OPENAI_API_KEY` | `sk-your-api-key-here` |

✅ **Environments 선택**: Production, Preview, Development 모두 체크

---

## 🎉 완료!

배포 URL: `https://your-project.vercel.app`

---

## ⚠️ 주의사항

### 1. 데이터 파일 처리

현재 `data/processed/` 파일들이 `.gitignore`에 포함되어 있어 배포 시 업로드되지 않습니다.

**해결 방법 3가지:**

#### 옵션 A: GitHub에 포함 (간단)
```bash
# .gitignore에서 제거
# data/processed/*.json
# data/embeddings/*.json

git add data/
git commit -m "Add processed data"
git push
```

#### 옵션 B: 배포 시 자동 처리 (권장)
```python
# app.py 시작 시 데이터 체크 및 처리
if not Path("data/processed").exists():
    process_documents()  # 자동 처리
```

#### 옵션 C: 외부 스토리지 사용 (프로덕션)
- AWS S3
- Google Cloud Storage
- Vercel Blob Storage

### 2. 메모리 제한

Vercel 무료 플랜: 1GB 메모리
- 큰 데이터는 스트리밍 로드 권장

### 3. Cold Start

첫 로딩 시간이 길 수 있음 (10-30초)
- 워밍업 설정 필요

---

## 📊 비용 (예상)

**무료 플랜으로 시작 가능!**

| 항목 | 무료 플랜 | 예상 비용 |
|------|----------|----------|
| Vercel Hosting | 100GB 대역폭/월 | $0 |
| OpenAI API | 종량제 | $2-50/월 (사용량에 따라) |

---

## 🔧 문제 해결

### "Module not found" 오류
```bash
# requirements-vercel.txt 확인
cat requirements-vercel.txt

# Vercel 재배포
vercel --prod
```

### "OPENAI_API_KEY not found" 오류
```bash
# Vercel Dashboard → Environment Variables 확인
# 재배포 필요 (환경 변수 변경 후)
```

### 데이터 파일 없음
```bash
# data/ 폴더를 Git에 포함
git add data/processed/*.json
git push
```

---

## 📞 지원

- [상세 배포 가이드](README_DEPLOYMENT.md)
- [Vercel 문서](https://vercel.com/docs)
- GitHub Issues

---

**배포 시간**: ~5분
**난이도**: ⭐⭐☆☆☆ (초급)
