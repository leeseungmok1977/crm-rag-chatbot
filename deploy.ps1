# Vercel 간단 배포 스크립트
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Vercel 배포 스크립트" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check Vercel CLI
Write-Host "`n[1/4] Vercel CLI 확인 중..." -ForegroundColor Yellow
$vercelCmd = Get-Command vercel -ErrorAction SilentlyContinue

if (-not $vercelCmd) {
    Write-Host "❌ Vercel CLI가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "다음 명령어로 설치하세요:" -ForegroundColor Yellow
    Write-Host "  npm install -g vercel" -ForegroundColor Cyan
    exit 1
}
Write-Host "✅ Vercel CLI 설치됨" -ForegroundColor Green

# Login
Write-Host "`n[2/4] Vercel 로그인..." -ForegroundColor Yellow
Write-Host "브라우저가 열립니다. GitHub으로 로그인하세요." -ForegroundColor Gray
vercel login

# Read API Key
Write-Host "`n[3/4] API 키 설정..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $content = Get-Content ".env" -Raw
    if ($content -match "OPENAI_API_KEY\s*=\s*(.+)") {
        $apiKey = $matches[1].Trim()
        $preview = $apiKey.Substring(0, 20) + "..."
        Write-Host "✅ .env에서 API 키 발견: $preview" -ForegroundColor Green

        # Set environment variables
        Write-Host "Vercel 환경 변수 설정 중..." -ForegroundColor Gray
        $apiKey | vercel env add OPENAI_API_KEY production --force
        $apiKey | vercel env add OPENAI_API_KEY preview --force
        $apiKey | vercel env add OPENAI_API_KEY development --force
        Write-Host "✅ 환경 변수 설정 완료" -ForegroundColor Green
    }
}

# Deploy
Write-Host "`n[4/4] 프로덕션 배포 중..." -ForegroundColor Yellow
Write-Host "이 작업은 2-3분 소요됩니다..." -ForegroundColor Gray
vercel --prod

Write-Host "`n=================================" -ForegroundColor Green
Write-Host "✅ 완료!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
