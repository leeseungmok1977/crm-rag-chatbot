# PowerShell script to run the CRM Chatbot
# Usage: .\run_chatbot.ps1

Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=" * 59 -ForegroundColor Green
Write-Host "🚀 Starting CRM RAG Chatbot..." -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=" * 59 -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "`n❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "`nExample:" -ForegroundColor Yellow
    Write-Host "OPENAI_API_KEY=sk-..." -ForegroundColor Cyan
    exit 1
}

# Check if processed data exists
if (-not (Test-Path "data\processed\*_chunks.json")) {
    Write-Host "`n⚠️  No processed data found!" -ForegroundColor Yellow
    Write-Host "Running document processing first..." -ForegroundColor Yellow
    python scripts\process_documents.py PDF\
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ Document processing failed!" -ForegroundColor Red
        exit 1
    }
}

# Check if Streamlit is installed
Write-Host "`n📦 Checking Streamlit installation..." -ForegroundColor Yellow
python -c "import streamlit" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Streamlit not found. Installing..." -ForegroundColor Red
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org streamlit
}

Write-Host "`n✅ All checks passed!" -ForegroundColor Green
Write-Host "`n🌐 Starting Streamlit server..." -ForegroundColor Cyan
Write-Host "📍 URL: http://localhost:8501" -ForegroundColor Cyan
Write-Host "`n💡 Tip: Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "`n" + "=" * 60 + "`n" -ForegroundColor Green

# Run Streamlit
streamlit run app.py --server.headless true
