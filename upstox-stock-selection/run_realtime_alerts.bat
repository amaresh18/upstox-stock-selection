@echo off
REM Batch file to set credentials and run realtime alerts script

echo Setting Upstox API credentials...
set UPSTOX_API_KEY=e3d3c1d1-5338-4efa-b77f-c83ea604ea43
set UPSTOX_ACCESS_TOKEN=eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTE1NjNjN2MxNTgyZTQ2OGQzNGY4M2QiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MzAwOTQ3OSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYzMDcxMjAwfQ.0N334N0oYJfKDFAqg1tHxisK7UFgsbrM5SRwhHtUdOk

echo.
echo ✅ Credentials set
echo.
echo Starting realtime alerts script...
echo.

REM Check if date argument is provided
if "%1"=="" (
    python scripts/run_realtime_alerts.py
) else (
    python scripts/run_realtime_alerts.py --date %1
)

pause

