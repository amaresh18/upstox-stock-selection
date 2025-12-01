@echo off
setlocal enabledelayedexpansion
REM ============================================
REM Restart Streamlit Service on Port 8501
REM Kills any existing process on the port and restarts
REM ============================================

echo.
echo ============================================
echo   Restarting Streamlit Service (Port 8501)
echo ============================================
echo.

REM Step 1: Find and kill process using port 8501
echo [1/3] Checking for processes on port 8501...
echo.

set PORT=8501
set FOUND=0

REM Find and kill all processes using the port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    set PID=%%a
    if defined PID (
        echo Found process with PID: !PID!
        echo Killing process...
        taskkill /PID !PID! /F >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo [OK] Process !PID! killed successfully
            set FOUND=1
        ) else (
            echo [WARNING] Could not kill process !PID! (may already be stopped)
        )
    )
)

REM Alternative method: Kill by process name
if !FOUND! EQU 0 (
    echo [INFO] No process found on port %PORT% via netstat
)

REM Step 2: Also try to kill any streamlit.exe processes (backup method)
echo.
echo [2/3] Checking for any Streamlit processes...
taskkill /F /IM streamlit.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Streamlit processes terminated
) else (
    echo [INFO] No Streamlit processes found
)

REM Step 3: Wait a moment for port to be released
echo.
echo [3/3] Waiting for port to be released...
timeout /t 2 /nobreak >nul

REM Step 4: Start the service
echo.
echo ============================================
echo   Starting Streamlit Service...
echo ============================================
echo.
echo The UI will be available at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server.
echo.
echo ============================================
echo.

REM Start Streamlit
python -m streamlit run app.py --server.port 8501 --server.headless true

REM If we get here, the service stopped
echo.
echo ============================================
echo   Service stopped
echo ============================================
pause
