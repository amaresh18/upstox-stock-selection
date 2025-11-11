# Quick Start - Streamlit UI

## If you're getting "This site can't be reached" error:

### Option 1: Run the batch file
```bash
run_ui.bat
```

### Option 2: Run directly in terminal
```bash
python -m streamlit run app.py
```

### Option 3: Run with explicit port
```bash
python -m streamlit run app.py --server.port 8501
```

## Troubleshooting

1. **Check if Streamlit is installed:**
   ```bash
   python -m streamlit --version
   ```
   If not installed: `pip install streamlit`

2. **Check if port 8501 is available:**
   - Close any other Streamlit apps
   - Try a different port: `--server.port 8502`

3. **Check for errors:**
   - Look at the terminal output when starting
   - Common issues:
     - Missing dependencies
     - Port already in use
     - Firewall blocking

4. **Manual browser access:**
   - After running, look for a message like:
     ```
     You can now view your Streamlit app in your browser.
     Local URL: http://localhost:8501
     ```
   - Copy that URL and paste it in your browser

5. **Check firewall:**
   - Windows Firewall might be blocking
   - Allow Python through firewall if prompted

## Expected Output

When Streamlit starts successfully, you should see:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

Then your browser should automatically open to that URL.

## Still having issues?

1. Check the terminal for error messages
2. Try running: `python test_streamlit.py` to verify imports
3. Make sure you're in the project root directory
4. Check that `app.py` exists in the current directory

