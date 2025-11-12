# Quick Start Guide

## Problem: "API key and access token must be set" Error

If you're getting this error, it means the environment variables are not set in the PowerShell window where you're running the script.

## Solution: Use Batch Files (Easiest)

I've created batch files that automatically set credentials and run the scripts:

### Option 1: Double-Click Batch Files

Just **double-click** these files in Windows Explorer:

- **`run_continuous_alerts.bat`** - Run continuous alerts (24/7 monitoring)
- **`run_realtime_alerts.bat`** - Run real-time alerts for today
- **`run_backtest.bat`** - Run backtest

### Option 2: Run from PowerShell

```powershell
# Run continuous alerts
.\run_continuous_alerts.bat

# Run real-time alerts for specific date
.\run_realtime_alerts.bat 2025-11-10

# Run backtest
.\run_backtest.bat
```

## Alternative: Set Credentials Manually

### Method 1: PowerShell Script

```powershell
# Run the setup script
.\scripts\set_credentials.ps1

# Then run your script
python scripts/run_continuous_alerts.py
```

### Method 2: Manual PowerShell

```powershell
# Set credentials
$env:UPSTOX_API_KEY='e3d3c1d1-5338-4efa-b77f-c83ea604ea43'
$env:UPSTOX_ACCESS_TOKEN='eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTE0MDE1MDY0ZmYzYTViMWM4YTk4NTQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjkxODczNiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyOTg0ODAwfQ.ETjfi9F3QQqCqCtiwypBSsMF_zb_zqfUfifv3t6q7sI'

# Then run your script
python scripts/run_continuous_alerts.py
```

## Why This Happens

**Environment variables in PowerShell are session-specific:**

- ✅ If you set them in PowerShell Window A, they're only available in Window A
- ❌ If you run the script in PowerShell Window B, they won't be set there

**Solution**: 
- Use the batch files (they set credentials in the same process)
- Or set credentials in the same PowerShell window where you run the script

## Verify Credentials Are Set

```powershell
# Check if credentials are set
echo $env:UPSTOX_API_KEY
echo $env:UPSTOX_ACCESS_TOKEN

# Or use Python to check
python -c "import os; print('API Key:', 'SET' if os.getenv('UPSTOX_API_KEY') else 'NOT SET'); print('Access Token:', 'SET' if os.getenv('UPSTOX_ACCESS_TOKEN') else 'NOT SET')"
```

## Recommended Approach

**Use the batch files** - They're the easiest and most reliable:

1. Double-click `run_continuous_alerts.bat` to start monitoring
2. Or double-click `run_realtime_alerts.bat` for one-time alerts
3. Or double-click `run_backtest.bat` for backtesting

The batch files automatically:
- ✅ Set the credentials
- ✅ Run the script
- ✅ Keep the window open to see output

## For Railway Deployment

For Railway, set the credentials in Railway dashboard:
1. Go to Railway → Your Project → Service
2. Click **Variables** tab
3. Add:
   - `UPSTOX_API_KEY` = `e3d3c1d1-5338-4efa-b77f-c83ea604ea43`
   - `UPSTOX_ACCESS_TOKEN` = `eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTE0MDE1MDY0ZmYzYTViMWM4YTk4NTQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjkxODczNiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyOTg0ODAwfQ.ETjfi9F3QQqCqCtiwypBSsMF_zb_zqfUfifv3t6q7sI`

---

**Quick Fix**: Just use the batch files! They handle everything automatically. 🚀

