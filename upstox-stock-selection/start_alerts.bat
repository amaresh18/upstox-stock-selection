@echo off
REM Continuous Alert Monitoring Startup Script
REM This script starts the continuous alert monitoring system

cd /d "%~dp0"

echo ================================================================================
echo STARTING CONTINUOUS ALERT MONITORING
echo ================================================================================
echo.

REM Check if credentials are set
if "%UPSTOX_API_KEY%"=="" (
    echo ERROR: UPSTOX_API_KEY not set
    echo Please set it using:
    echo   set UPSTOX_API_KEY=your_api_key
    pause
    exit /b 1
)

if "%UPSTOX_ACCESS_TOKEN%"=="" (
    echo ERROR: UPSTOX_ACCESS_TOKEN not set
    echo Please set it using:
    echo   set UPSTOX_ACCESS_TOKEN=your_access_token
    pause
    exit /b 1
)

echo Starting continuous monitoring...
echo Press Ctrl+C to stop
echo.

python scripts/run_continuous_alerts.py

pause

