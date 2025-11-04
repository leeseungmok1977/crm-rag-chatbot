# CRM AI Chatbot 실행 스크립트
# UTF-8 인코딩 설정 포함

Write-Host "🚀 CRM AI Chatbot 시작 중..." -ForegroundColor Cyan
Write-Host ""

# UTF-8 인코딩 설정
$env:PYTHONIOENCODING="utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 작업 디렉토리 확인
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "📁 작업 디렉토리: $scriptPath" -ForegroundColor Green
Write-Host ""

# 가상환경 활성화 확인
if (-Not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ 가상환경이 없습니다. 먼저 가상환경을 생성하세요:" -ForegroundColor Red
    Write-Host "   python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# 가상환경 활성화
Write-Host "🔧 가상환경 활성화 중..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# .env 파일 확인
if (-Not (Test-Path ".env")) {
    Write-Host "❌ .env 파일이 없습니다!" -ForegroundColor Red
    Write-Host "   .env.example을 복사하여 .env 파일을 만들고 API 키를 설정하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 환경 설정 완료" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Streamlit 앱 시작..." -ForegroundColor Cyan
Write-Host "   접속 URL: http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  종료하려면 Ctrl+C를 누르세요" -ForegroundColor Yellow
Write-Host ""

# Streamlit 실행
streamlit run app_gemini.py --server.port 8501
