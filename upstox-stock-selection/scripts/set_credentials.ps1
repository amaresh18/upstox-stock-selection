# PowerShell script to set Upstox API credentials
# Run this script before running any other scripts
# Usage: .\scripts\set_credentials.ps1

Write-Host "Setting Upstox API credentials..." -ForegroundColor Green

# Set API Key
$env:UPSTOX_API_KEY = 'e3d3c1d1-5338-4efa-b77f-c83ea604ea43'

# Set Access Token
$env:UPSTOX_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTE0MDE1MDY0ZmYzYTViMWM4YTk4NTQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjkxODczNiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyOTg0ODAwfQ.ETjfi9F3QQqCqCtiwypBSsMF_zb_zqfUfifv3t6q7sI'

# Note: API Secret is not currently used by the scripts
# API Secret: '9kbfgnlibw'

Write-Host "✅ Credentials set successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "API Key: $($env:UPSTOX_API_KEY.Substring(0,20))..." -ForegroundColor Cyan
Write-Host "Access Token: $($env:UPSTOX_ACCESS_TOKEN.Substring(0,30))..." -ForegroundColor Cyan
Write-Host ""

# Verify credentials are set
if ($env:UPSTOX_API_KEY -and $env:UPSTOX_ACCESS_TOKEN) {
    Write-Host "✅ Verification: Both credentials are set correctly" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run:" -ForegroundColor Yellow
    Write-Host "  python scripts/run_continuous_alerts.py" -ForegroundColor Cyan
    Write-Host "  python scripts/run_realtime_alerts.py --date 2025-11-10" -ForegroundColor Cyan
    Write-Host "  python scripts/run_backtest.py" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use the batch files:" -ForegroundColor Yellow
    Write-Host "  .\run_continuous_alerts.bat" -ForegroundColor Cyan
    Write-Host "  .\run_realtime_alerts.bat" -ForegroundColor Cyan
    Write-Host "  .\run_backtest.bat" -ForegroundColor Cyan
} else {
    Write-Host "❌ Error: Credentials were not set correctly" -ForegroundColor Red
}

Write-Host ""
Write-Host "Note: These credentials are set for the current PowerShell session only." -ForegroundColor Yellow
Write-Host "To make them permanent, set them in Windows Environment Variables." -ForegroundColor Yellow

