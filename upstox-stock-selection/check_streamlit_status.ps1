# Check Streamlit Status Script

Write-Host "Checking Streamlit status..." -ForegroundColor Cyan
Write-Host ""

# Check if Streamlit is running
$streamlitProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*streamlit*" -or $_.Path -like "*streamlit*"
}

if ($streamlitProcess) {
    Write-Host "✓ Streamlit process found:" -ForegroundColor Green
    $streamlitProcess | Format-Table Id, ProcessName, StartTime
} else {
    Write-Host "✗ No Streamlit process found" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checking port 8501..." -ForegroundColor Cyan
$port8501 = netstat -ano | Select-String ":8501"
if ($port8501) {
    Write-Host "✓ Port 8501 is in use:" -ForegroundColor Green
    $port8501
} else {
    Write-Host "✗ Port 8501 is not in use" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checking port 8502..." -ForegroundColor Cyan
$port8502 = netstat -ano | Select-String ":8502"
if ($port8502) {
    Write-Host "✓ Port 8502 is in use:" -ForegroundColor Green
    $port8502
} else {
    Write-Host "✗ Port 8502 is not in use" -ForegroundColor Red
}

Write-Host ""
Write-Host "To start Streamlit, run:" -ForegroundColor Yellow
Write-Host "  streamlit run app.py" -ForegroundColor White
Write-Host ""
Write-Host "Or use:" -ForegroundColor Yellow
Write-Host "  restart_ui.bat" -ForegroundColor White

