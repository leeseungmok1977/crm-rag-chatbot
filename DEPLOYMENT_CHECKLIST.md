# ✅ 배포 체크리스트

## 🔧 사전 준비

### 계정 생성
- [ ] GitHub 계정 생성/로그인
- [ ] Vercel 계정 생성 (GitHub으로 로그인)
- [ ] OpenAI API 키 발급

### 로컬 환경 확인
- [ ] Python 3.11+ 설치 확인
- [ ] Git 설치 확인
- [ ] Node.js 설치 (Vercel CLI 사용 시)

---

## 📂 프로젝트 준비

### 파일 확인
- [ ] `.gitignore` 존재 확인
- [ ] `.env` 파일이 Git에 포함되지 않는지 확인
- [ ] `requirements-vercel.txt` 존재 확인
- [ ] `vercel.json` 존재 확인

### 데이터 처리
- [ ] `data/processed/` 폴더에 청크 JSON 파일 존재
- [ ] `data/embeddings/` 폴더에 임베딩 캐시 존재
- [ ] 데이터 파일 Git 포함 여부 결정
  - [ ] Option A: GitHub에 포함 (간단)
  - [ ] Option B: 배포 시 자동 생성
  - [ ] Option C: 외부 스토리지 사용

### 환경 변수
- [ ] 로컬 `.env` 파일에 `OPENAI_API_KEY` 설정
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인

---

## 🐙 GitHub 저장소 설정

### 저장소 생성
- [ ] GitHub에서 새 저장소 생성
- [ ] 저장소 이름 기록: `______________________`
- [ ] Public/Private 선택

### Git 초기화 및 푸시
```bash
# 체크리스트를 따라 실행
- [ ] git init
- [ ] git add .
- [ ] git commit -m "Initial commit: CRM RAG Chatbot"
- [ ] git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
- [ ] git branch -M main
- [ ] git push -u origin main
```

### GitHub Secrets 설정 (CI/CD 사용 시)
- [ ] Repository Settings → Secrets 이동
- [ ] `VERCEL_TOKEN` 추가
- [ ] `VERCEL_ORG_ID` 추가
- [ ] `VERCEL_PROJECT_ID` 추가

---

## 🚀 Vercel 배포

### 프로젝트 생성
- [ ] [vercel.com](https://vercel.com) 접속
- [ ] GitHub으로 로그인
- [ ] "Add New..." → "Project" 클릭
- [ ] GitHub 저장소 선택
- [ ] "Import" 클릭

### 빌드 설정 확인
- [ ] Framework Preset: Other
- [ ] Build Command: (비워둠)
- [ ] Output Directory: (비워둠)
- [ ] Install Command: `pip install -r requirements-vercel.txt`
- [ ] Root Directory: `./` (기본값)

### 환경 변수 설정
- [ ] Project Settings → Environment Variables 이동
- [ ] `OPENAI_API_KEY` 추가
  - Name: `OPENAI_API_KEY`
  - Value: `sk-...` (실제 API 키)
  - Environments: ✅ Production, ✅ Preview, ✅ Development

### 배포 실행
- [ ] "Deploy" 버튼 클릭
- [ ] 빌드 로그 확인
- [ ] 배포 성공 확인 ✅

---

## 🧪 배포 후 테스트

### 기능 테스트
- [ ] 배포 URL 접속: `https://______________________.vercel.app`
- [ ] 페이지 로드 확인
- [ ] 데이터 로드 확인 (통계 표시)
- [ ] 테스트 질문 입력:
  - [ ] "거래선 등록 방법"
  - [ ] "미팅메모 작성"
- [ ] 답변 생성 확인
- [ ] 소스 출처 표시 확인

### 다크모드 테스트
- [ ] 브라우저 다크모드 설정
- [ ] UI 색상 변경 확인
- [ ] 가독성 확인

### 모바일 테스트
- [ ] 모바일 브라우저 접속
- [ ] 반응형 디자인 확인
- [ ] 터치 인터페이스 작동 확인

---

## 📊 모니터링 설정

### Vercel Analytics
- [ ] Project Settings → Analytics 활성화
- [ ] 사용량 모니터링 설정

### 성능 확인
- [ ] 첫 로딩 시간 측정: _____ 초
- [ ] 쿼리 응답 시간 측정: _____ 초
- [ ] Cold Start 시간 확인: _____ 초

---

## 🔐 보안 체크

### API 키 보안
- [ ] `.env` 파일이 Git에 포함되지 않음
- [ ] GitHub에 API 키가 노출되지 않음
- [ ] Vercel Environment Variables만 사용

### 접근 제어 (선택)
- [ ] 패스워드 보호 추가 (필요 시)
- [ ] Rate Limiting 설정 (필요 시)
- [ ] IP 화이트리스트 (필요 시)

---

## 📝 문서화

### 내부 문서
- [ ] 배포 URL 기록
- [ ] 환경 변수 목록 기록
- [ ] 팀원과 공유

### 사용자 가이드
- [ ] README 업데이트
- [ ] 사용 방법 문서화
- [ ] 예시 질문 목록 작성

---

## 🎯 완료 확인

### 최종 체크
- [ ] ✅ 배포 URL 작동
- [ ] ✅ 모든 기능 정상 작동
- [ ] ✅ 다크모드 지원
- [ ] ✅ 모바일 반응형
- [ ] ✅ 보안 설정 완료
- [ ] ✅ 문서화 완료

### 배포 정보 기록

```
배포일: 2025-___-___
배포 URL: https://________________________.vercel.app
GitHub Repo: https://github.com/____________/____________
Vercel Project: ________________________
```

---

## 🔄 다음 단계

배포 후 개선사항:
- [ ] 사용자 피드백 수집
- [ ] 성능 최적화
- [ ] 추가 기능 개발
- [ ] 정기 모니터링 설정

---

**배포 담당자**: ________________
**배포 완료일**: ________________
**검증자**: ________________

✅ **모든 체크리스트 완료 시 배포 성공!**
