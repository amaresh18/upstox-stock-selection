@echo off
echo Stopping any existing Streamlit processes...
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq streamlit*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Streamlit UI...
echo.
echo The UI will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server.
echo.

python -m streamlit run app.py --server.port 8501 --server.headless false

pause

