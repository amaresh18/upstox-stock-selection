# Streamlit Troubleshooting Guide

## Connection Error Fix

If you see "Connection error - Is Streamlit still running?", follow these steps:

### Quick Fix

1. **Stop any running Streamlit processes:**
   ```powershell
   # Find and stop Streamlit
   Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force
   ```

2. **Restart Streamlit:**
   ```bash
   streamlit run app.py
   ```

   Or use the batch file:
   ```bash
   restart_ui.bat
   ```

### Manual Steps

1. **Close the browser tab** showing the error

2. **Open a new terminal/PowerShell window**

3. **Navigate to project directory:**
   ```bash
   cd "C:\Users\dell\Documents\Amaresh\Auto-trading-\upstox-stock-selection"
   ```

4. **Start Streamlit:**
   ```bash
   streamlit run app.py
   ```

5. **Wait for the message:**
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   ```

6. **Open the URL** in your browser (or it should open automatically)

### Alternative: Use Different Port

If port 8501 is busy, use a different port:

```bash
streamlit run app.py --server.port 8502
```

Then open: `http://localhost:8502`

### Check if Streamlit is Running

```powershell
# Check if port 8501 is in use
netstat -ano | findstr :8501
```

### Common Issues

1. **Port Already in Use:**
   - Solution: Use `--server.port 8502` or kill the process using port 8501

2. **Python Module Not Found:**
   - Solution: Install dependencies: `pip install -r requirements.txt`

3. **Import Errors:**
   - Solution: Make sure you're in the project root directory

4. **Browser Not Opening:**
   - Solution: Manually open `http://localhost:8501` in your browser

### Verify Installation

```bash
# Check Streamlit version
streamlit --version

# Check Python
python --version

# Check if all dependencies are installed
pip list | findstr streamlit
```

### Still Having Issues?

1. **Check the terminal output** for error messages
2. **Verify credentials are set:**
   ```powershell
   $env:UPSTOX_API_KEY
   $env:UPSTOX_ACCESS_TOKEN
   ```
3. **Check if NSE.json exists:**
   ```bash
   dir data\NSE.json
   ```

If NSE.json doesn't exist, create it:
```bash
python scripts/fetch_instruments.py
```

