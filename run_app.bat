@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   CRM AI Chatbot 시작
echo ========================================
echo.

REM UTF-8 인코딩 설정
set PYTHONIOENCODING=utf-8

REM 작업 디렉토리 설정
cd /d "%~dp0"

REM 가상환경 확인
if not exist "venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 없습니다!
    echo 먼저 가상환경을 생성하세요: python -m venv venv
    pause
    exit /b 1
)

REM 가상환경 활성화
echo [단계 1/3] 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM .env 파일 확인
if not exist ".env" (
    echo [오류] .env 파일이 없습니다!
    echo .env.example을 복사하여 .env 파일을 만들고 API 키를 설정하세요.
    pause
    exit /b 1
)

echo [단계 2/3] 환경 설정 완료
echo.
echo [단계 3/3] Streamlit 앱 시작...
echo.
echo ========================================
echo   접속 URL: http://localhost:8501
echo ========================================
echo.
echo 종료하려면 Ctrl+C를 누르세요
echo.

REM Streamlit 실행
streamlit run app_gemini.py --server.port 8501

pause
