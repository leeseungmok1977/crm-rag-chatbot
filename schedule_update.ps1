# PowerShell script to schedule daily query statistics update
# 매일 자정에 실행되도록 Windows 작업 스케줄러 등록

Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=" * 59 -ForegroundColor Green
Write-Host "📅 Scheduling Query Statistics Update" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=" * 59 -ForegroundColor Green

# Get Python path
$pythonPath = (Get-Command python).Source
$scriptPath = Join-Path $PSScriptRoot "scripts\update_popular_queries.py"
$workingDir = $PSScriptRoot

Write-Host "`n📍 Python: $pythonPath" -ForegroundColor Cyan
Write-Host "📍 Script: $scriptPath" -ForegroundColor Cyan
Write-Host "📍 Working Directory: $workingDir" -ForegroundColor Cyan

# Create task action
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument $scriptPath `
    -WorkingDirectory $workingDir

# Create trigger (daily at midnight)
$trigger = New-ScheduledTaskTrigger -Daily -At "00:00"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive

# Register task
$taskName = "CRM_Chatbot_Query_Stats_Update"

try {
    # Remove existing task if exists
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

    # Register new task
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "CRM Chatbot 인기 질문 통계 업데이트 (매일 자정 실행)"

    Write-Host "`n✅ Task scheduled successfully!" -ForegroundColor Green
    Write-Host "`nTask Details:" -ForegroundColor Yellow
    Write-Host "  Name: $taskName" -ForegroundColor White
    Write-Host "  Schedule: Daily at 00:00 (midnight)" -ForegroundColor White
    Write-Host "  Status: Ready" -ForegroundColor White

    Write-Host "`n💡 To view the task:" -ForegroundColor Yellow
    Write-Host "  taskschd.msc" -ForegroundColor Cyan
    Write-Host "  or" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Cyan

    Write-Host "`n💡 To manually run the task:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Cyan

    Write-Host "`n💡 To unregister the task:" -ForegroundColor Yellow
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor Cyan

} catch {
    Write-Host "`n❌ Failed to schedule task!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "`nPlease run PowerShell as Administrator" -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 60 + "`n" -ForegroundColor Green
