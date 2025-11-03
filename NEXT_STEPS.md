# 다음 단계 가이드

## 현재 상태

### ✅ 완료된 작업
1. **Gemini 스타일 UI 구현** ([app_gemini.py](app_gemini.py))
   - 깔끔한 웰컴 화면 ("안녕하세요, 송목")
   - 중앙 정렬 검색창
   - 인기 질문 칩 디자인
   - 라이트/다크 모드 자동 지원

2. **인기 질문 통계 기능**
   - 질문 히스토리 자동 저장 (`data/query_history.json`)
   - 통계 업데이트 스크립트 ([scripts/update_popular_queries.py](scripts/update_popular_queries.py))
   - 매일 자정 자동 실행 스케줄러 ([schedule_update.ps1](schedule_update.ps1))

3. **Vercel 배포 준비**
   - [vercel.json](vercel.json) 설정
   - [requirements-vercel.txt](requirements-vercel.txt) 최적화
   - [.gitignore](.gitignore) 보안 설정
   - 배포 가이드 문서

4. **다크 모드 지원**
   - 모든 UI 컴포넌트 다크 모드 최적화
   - 자동 테마 감지 및 적용

---

## 🧪 테스트 방법

### 1. Gemini UI 확인
현재 실행 중: **http://localhost:8501**

#### 확인 사항:
- [ ] 웰컴 화면에 "안녕하세요, 송목" 표시
- [ ] 검색창이 화면 중앙에 위치
- [ ] 인기 질문 칩이 검색창 하단에 표시
- [ ] 칩 클릭 시 검색창에 질문 자동 입력
- [ ] 질문 후 채팅 UI로 전환
- [ ] 답변이 이모지와 함께 구조화되어 표시 (✅, 1️⃣, 💡 등)
- [ ] 소스 출처가 확장 가능한 형태로 표시

#### 테스트 질문:
```
거래선 등록 방법
미팅메모 작성하는 방법
주문 승인 프로세스
```

### 2. 다크 모드 테스트
#### Windows에서:
1. 설정 → 개인 설정 → 색
2. "색 선택" → 어둡게 or 밝게
3. 브라우저 새로고침

#### 확인 사항:
- [ ] 라이트 모드: 흰색 배경, 파란색 강조
- [ ] 다크 모드: 어두운 배경, 밝은 파란색 강조
- [ ] 텍스트 가독성 우수

### 3. 인기 질문 기능 테스트
```powershell
# 수동으로 통계 업데이트 실행
python scripts/update_popular_queries.py

# 결과 확인
cat data/query_stats.json
```

#### 확인 사항:
- [ ] `query_history.json`에 질문 저장
- [ ] `query_stats.json`에 통계 생성
- [ ] UI에서 인기 질문 업데이트 반영

---

## 🚀 배포 준비

### GitHub 저장소 생성

```powershell
# 1. Git 초기화
git init

# 2. 첫 커밋
git add .
git commit -m "feat: Gemini-style CRM RAG Chatbot with popular queries"

# 3. GitHub 저장소 연결 (GitHub에서 먼저 생성)
git remote add origin https://github.com/YOUR_USERNAME/crm-rag-chatbot.git
git branch -M main
git push -u origin main
```

### Vercel 배포

#### Option A: Vercel CLI (권장)
```powershell
# Vercel CLI 설치
npm install -g vercel

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

#### Option B: Vercel Dashboard
1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. "Add New..." → "Project"
3. GitHub 저장소 선택
4. 환경 변수 설정:
   - `OPENAI_API_KEY`: [Your OpenAI API Key]
5. "Deploy" 클릭

### 환경 변수 설정
Vercel Project Settings → Environment Variables:
```
OPENAI_API_KEY=sk-...
```

---

## 📝 스케줄러 등록

매일 자정에 인기 질문 통계를 자동 업데이트하려면:

```powershell
# PowerShell을 관리자 권한으로 실행
.\schedule_update.ps1
```

### 스케줄러 확인
```powershell
# 작업 확인
Get-ScheduledTask -TaskName "CRM_Chatbot_Query_Stats_Update"

# 수동 실행 테스트
Start-ScheduledTask -TaskName "CRM_Chatbot_Query_Stats_Update"

# 작업 삭제 (필요시)
Unregister-ScheduledTask -TaskName "CRM_Chatbot_Query_Stats_Update"
```

---

## 🔄 기존 앱과 교체 (선택사항)

Gemini UI를 메인으로 사용하려면:

```powershell
# 백업
Copy-Item app.py app_backup.py

# 교체
Copy-Item app_gemini.py app.py

# Git 커밋
git add .
git commit -m "feat: Replace main app with Gemini UI"
git push
```

---

## 📊 모니터링

### Vercel Analytics
배포 후 자동으로 활성화됨:
- 방문자 수
- 응답 시간
- 오류율

### Query Statistics
정기적으로 확인:
```powershell
# 통계 확인
python scripts/update_popular_queries.py

# 히스토리 확인
cat data/query_history.json | ConvertFrom-Json | ForEach-Object { $_.queries.Count }
```

---

## 🛠️ 문제 해결

### 포트 충돌 시
여러 Streamlit 인스턴스가 실행 중이면:
```powershell
# 실행 중인 프로세스 확인
Get-Process | Where-Object { $_.ProcessName -eq "streamlit" }

# 프로세스 종료
Stop-Process -Name streamlit -Force

# 다시 실행
streamlit run app_gemini.py
```

### 모듈 오류 시
```powershell
# 의존성 재설치
pip install -r requirements.txt

# 캐시 클리어
streamlit cache clear
```

### Vercel 배포 실패 시
1. [vercel.json](vercel.json:1-18) 확인
2. [requirements-vercel.txt](requirements-vercel.txt) 확인
3. 환경 변수 확인
4. 로그 확인: `vercel logs`

---

## 📚 참고 문서

- **[GEMINI_UI_COMPLETE.md](GEMINI_UI_COMPLETE.md)**: Gemini UI 구현 상세 가이드
- **[README_DEPLOYMENT.md](README_DEPLOYMENT.md)**: 배포 전체 가이드
- **[DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)**: 5분 퀵스타트
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**: 체크리스트

---

## ✅ 최종 체크리스트

### 로컬 테스트
- [ ] Gemini UI 정상 작동 (http://localhost:8501)
- [ ] 인기 질문 칩 클릭 작동
- [ ] 질문/답변 정상 표시
- [ ] 다크 모드 정상 전환
- [ ] 소스 출처 정상 표시

### 배포 전
- [ ] GitHub 저장소 생성
- [ ] `.gitignore` 확인 (`.env`, `secrets.toml` 제외)
- [ ] 환경 변수 문서화
- [ ] README 업데이트

### Vercel 배포
- [ ] Vercel 프로젝트 생성
- [ ] 환경 변수 설정 (`OPENAI_API_KEY`)
- [ ] 첫 배포 성공
- [ ] 배포 URL 테스트
- [ ] Analytics 확인

### 운영
- [ ] 스케줄러 등록
- [ ] 통계 업데이트 테스트
- [ ] 사용자 피드백 수집
- [ ] 모니터링 설정

---

## 💡 추가 개선 아이디어

### 단기 (1-2주)
1. **사용자 피드백 수집**: 답변 만족도 버튼 추가
2. **응답 시간 최적화**: 캐싱 전략 개선
3. **모바일 UX 개선**: 터치 제스처 추가

### 중기 (1-2개월)
1. **대화 히스토리 저장**: 사용자별 세션 관리
2. **고급 검색**: 필터링 및 정렬 옵션
3. **관리자 대시보드**: 통계 시각화

### 장기 (3-6개월)
1. **다국어 지원**: 영어/한국어 자동 감지
2. **음성 입력**: STT 통합
3. **API 제공**: REST API 엔드포인트

---

**현재 상태**: 모든 기능 구현 완료, 로컬 테스트 준비 완료 ✅

**다음 액션**:
1. http://localhost:8501 에서 Gemini UI 테스트
2. 만족하면 GitHub에 푸시
3. Vercel에 배포
