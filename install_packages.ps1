# PowerShell script to install packages with SSL workaround
# Run this script: .\install_packages.ps1

Write-Host "Installing packages with SSL certificate bypass..." -ForegroundColor Green

# Trusted hosts
$trustedHosts = "--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org"

# 1. Upgrade pip
Write-Host "`n[1/6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip $trustedHosts.Split()

# 2. Core packages (use pre-compiled wheels)
Write-Host "`n[2/6] Installing core packages..." -ForegroundColor Yellow
pip install $trustedHosts.Split() `
    python-dotenv==1.0.0 `
    "pydantic>=2.0,<3.0" `
    "pydantic-settings>=2.0,<3.0"

# 3. PDF processing
Write-Host "`n[3/6] Installing PDF processing..." -ForegroundColor Yellow
pip install $trustedHosts.Split() `
    "pypdf>=4.0.0" `
    pdfplumber==0.10.3

# 4. Text processing
Write-Host "`n[4/6] Installing text processing..." -ForegroundColor Yellow
pip install $trustedHosts.Split() `
    langdetect==1.0.9

# 5. LangChain & LLM
Write-Host "`n[5/6] Installing LangChain & OpenAI..." -ForegroundColor Yellow
pip install $trustedHosts.Split() `
    "openai>=1.6.0" `
    "langchain>=0.1.0" `
    "langchain-openai>=0.0.2"

# 6. Vector store & utilities
Write-Host "`n[6/6] Installing vector store & utilities..." -ForegroundColor Yellow
pip install $trustedHosts.Split() `
    "qdrant-client>=1.7.0" `
    "tqdm>=4.66.0"

Write-Host "`n✅ Installation completed!" -ForegroundColor Green
Write-Host "`nVerifying installation..." -ForegroundColor Yellow

# Verify
python -c "import openai; import langchain; import qdrant_client; print('✅ All packages imported successfully!')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n🎉 Ready to process documents!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some packages may have issues. Check the output above." -ForegroundColor Red
}
