@echo off
echo Starting Upstox Stock Selection UI...
echo.
echo Checking Python and Streamlit...
python --version
python -m streamlit --version
echo.
echo Starting Streamlit server...
echo The UI will open in your browser at http://localhost:8501
echo.
echo If it doesn't open automatically, copy and paste the URL shown below into your browser.
echo.
echo Press Ctrl+C to stop the server.
echo.
python -m streamlit run app.py --server.port 8501
pause

