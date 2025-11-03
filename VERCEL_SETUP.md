# Vercel 배포 가이드

## 🚀 빠른 배포 (5분)

### 1단계: Vercel 프로젝트 생성

1. **https://vercel.com/dashboard** 접속
2. "Add New..." → "Project" 클릭
3. "Import Git Repository" 선택
4. **leeseungmok1977/crm-rag-chatbot** 검색 후 선택
5. "Import" 클릭

### 2단계: 환경 변수 설정 (중요!)

**프로젝트 설정 페이지에서:**

#### 환경 변수 추가
1. "Environment Variables" 섹션 찾기
2. 다음 정보 입력:

| Field | Value |
|-------|-------|
| **Name** | `OPENAI_API_KEY` |
| **Value** | `sk-proj-K8iV4DD0-8wZ7w7WZDWx...` (당신의 API 키) |
| **Environment** | Production, Preview, Development 모두 체크 |

3. "Add" 버튼 클릭

### 3단계: 배포

1. "Deploy" 버튼 클릭
2. 빌드 진행 상황 확인 (2-3분 소요)
3. 배포 완료 후 URL 확인

---

## 🔧 빌드 설정

Vercel이 자동으로 감지하지만, 필요시 수동 설정:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Other |
| **Build Command** | (비워둠) |
| **Output Directory** | (비워둠) |
| **Install Command** | `pip install -r requirements-vercel.txt` |

---

## ⚠️ 중요 체크리스트

배포 전 확인:

- [x] GitHub에 코드 푸시 완료
- [ ] OpenAI API 키 준비 (`sk-proj-...` 형식)
- [ ] Vercel 계정 생성 (GitHub으로 로그인 가능)
- [ ] 환경 변수 설정 완료

---

## 🎯 배포 후 확인사항

### 1. 앱 접속 테스트
배포 완료 후 제공된 URL 접속:
```
https://your-project.vercel.app
```

### 2. 확인할 기능
- [ ] 웰컴 화면 표시 ("안녕하세요, 송목")
- [ ] 인기 질문 칩 표시
- [ ] 질문 입력 및 답변 생성
- [ ] 소스 출처 표시
- [ ] 다크 모드 전환

### 3. 오류 발생 시
Vercel Dashboard → Project → Logs에서 확인

---

## 🔐 보안 주의사항

### ✅ 올바른 방법
```
Vercel Dashboard → Environment Variables
OPENAI_API_KEY = sk-proj-...
```

### ❌ 절대 하지 말 것
```python
# app.py 파일에 직접 입력 금지!
OPENAI_API_KEY = "sk-proj-..."  # ❌ 위험!
```

### GitHub에 API 키가 노출되지 않았는지 확인
```powershell
# .env 파일이 .gitignore에 포함되어 있는지 확인
cat .gitignore | Select-String ".env"

# GitHub에 .env가 푸시되지 않았는지 확인
git ls-files | Select-String ".env"
```

**결과가 없으면 안전합니다!** ✅

---

## 📊 비용 안내

### Vercel 무료 플랜
- **대역폭**: 100GB/월
- **실행 시간**: 100GB-Hrs/월
- **빌드**: 6,000분/월
- **비용**: $0

### OpenAI API 비용 (예상)
- **임베딩**: ~$0.0001/쿼리
- **GPT-4**: ~$0.03-0.05/쿼리

**100 쿼리/일 기준 월 예상 비용**:
- Vercel: $0 (무료 플랜)
- OpenAI: $3-5

---

## 🛠️ 문제 해결

### 문제 1: "OPENAI_API_KEY not found"
**원인**: 환경 변수가 설정되지 않음

**해결**:
1. Vercel Dashboard → 프로젝트 선택
2. Settings → Environment Variables
3. `OPENAI_API_KEY` 추가
4. "Redeploy" 클릭

### 문제 2: "Module not found"
**원인**: requirements-vercel.txt 설치 실패

**해결**:
1. [requirements-vercel.txt](requirements-vercel.txt) 확인
2. Python 버전 확인 (3.11 필요)
3. Vercel Logs에서 상세 오류 확인

### 문제 3: "Cold Start 느림"
**원인**: Serverless 함수 초기 로딩

**해결**: 정상입니다. 첫 접속은 느릴 수 있습니다 (5-10초)
- 이후 접속은 빠름 (1-2초)
- Pro 플랜으로 업그레이드하면 개선됨

---

## 📱 도메인 설정 (선택사항)

### 커스텀 도메인 연결
1. Vercel Dashboard → 프로젝트 → Settings → Domains
2. "Add" 클릭
3. 도메인 입력 (예: `crm.yourdomain.com`)
4. DNS 설정 안내에 따라 CNAME 레코드 추가

---

## 🔄 업데이트 배포

코드 수정 후:
```powershell
# Git 커밋 및 푸시
git add .
git commit -m "update: 기능 개선"
git push

# Vercel이 자동으로 새 버전 배포!
```

---

## 💡 추가 최적화

### 1. Analytics 활성화
Vercel Dashboard → Project → Analytics → Enable

### 2. 성능 모니터링
- 응답 시간 추적
- 오류율 모니터링
- 사용량 통계

### 3. 캐싱 전략
```python
# app.py에 추가
@st.cache_resource(ttl=3600)  # 1시간 캐시
def load_vector_store():
    # 벡터 스토어 로딩
    pass
```

---

## ✅ 배포 완료 체크리스트

- [ ] Vercel 프로젝트 생성
- [ ] 환경 변수 설정 (`OPENAI_API_KEY`)
- [ ] 첫 배포 완료
- [ ] 배포 URL 테스트
- [ ] 질문/답변 기능 확인
- [ ] 다크 모드 확인
- [ ] Analytics 활성화
- [ ] 팀원과 URL 공유

---

**배포 성공하면 여기에 URL 적어두세요:**
```
🌐 Production URL: https://__________________.vercel.app
```

---

**준비 완료! 이제 "Deploy" 버튼만 누르면 됩니다!** 🚀
