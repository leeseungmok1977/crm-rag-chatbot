# Streamlit Cloud 배포 가이드

## 🚀 Streamlit Cloud 배포 (권장)

Streamlit Cloud는 Streamlit 앱 배포에 최적화되어 있으며 무료입니다!

### 1단계: Streamlit Cloud 계정 생성

1. **https://share.streamlit.io** 접속
2. GitHub 계정으로 로그인

### 2단계: 앱 배포

1. "New app" 클릭
2. 설정:
   - **Repository**: `leeseungmok1977/crm-rag-chatbot`
   - **Branch**: `main`
   - **Main file path**: `app_gemini.py`
3. "Advanced settings" 클릭
4. **Secrets** 추가:
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```
5. "Deploy!" 클릭

### 3단계: 완료!

배포 완료 후 URL이 제공됩니다:
```
https://your-app-name.streamlit.app
```

---

## ⚙️ requirements.txt 확인

Streamlit Cloud가 다음 파일을 자동으로 감지합니다:

**requirements.txt** (이미 있음)
```
python-dotenv==1.0.0
pydantic==2.5.0
...
```

---

## 🔧 문제 해결

### 1. 배포 실패 시
- Streamlit Cloud 로그 확인
- `requirements.txt`의 패키지 버전 확인
- Python 버전 호환성 확인

### 2. API 키 오류 시
- Secrets 설정 확인
- 앱 재시작 (Reboot app)

### 3. 메모리 부족 시
- 무료 플랜: 1GB RAM
- 데이터 크기 최적화 필요

---

## 💰 비용

**무료 플랜:**
- 공개 앱: 무제한
- 비공개 앱: 1개
- 1GB RAM
- 1GB 스토리지

**완벽하게 충분합니다!**

---

## 🎯 배포 URL

배포 후 여기에 URL을 기록하세요:
```
🌐 Production URL: https://__________________.streamlit.app
```

---

## 📱 공유

배포 후 URL을 팀원들과 공유하면 됩니다!

- 별도 설치 불필요
- 브라우저에서 바로 접속
- 모바일에서도 작동

---

**Streamlit Cloud가 Vercel보다 훨씬 쉽고 빠릅니다!** 🎉
