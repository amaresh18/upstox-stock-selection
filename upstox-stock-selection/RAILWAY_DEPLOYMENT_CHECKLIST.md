# Railway Deployment Checklist

## ✅ Prerequisites Completed

- [x] Code pushed to GitHub: https://github.com/amaresh18/upstox-stock-selection
- [x] Railway configuration files ready (`railway.json`, `Procfile`)
- [x] All dependencies in `requirements.txt`

## 🚀 Deployment Steps

### Step 1: Sign Up / Login to Railway

1. Go to: **https://railway.app**
2. Click **"Start a New Project"** or **"Login"**
3. Sign up with **GitHub** (recommended)
4. Authorize Railway to access your GitHub account

### Step 2: Create New Project

1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: **`upstox-stock-selection`**
4. Railway will automatically detect it's a Python project

### Step 3: Set Environment Variables

**IMPORTANT**: Set these in Railway dashboard:

1. Click on your project → service
2. Go to **"Variables"** tab
3. Click **"New Variable"** and add:

```
UPSTOX_API_KEY = e3d3c1d1-5338-4efa-b77f-c83ea604ea43
UPSTOX_ACCESS_TOKEN = eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTE1NjNjN2MxNTgyZTQ2OGQzNGY4M2QiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MzAwOTQ3OSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYzMDcxMjAwfQ.0N334N0oYJfKDFAqg1tHxisK7UFgsbrM5SRwhHtUdOk
```

**Optional (for Telegram notifications)**:
```
TELEGRAM_BOT_TOKEN = 8547171229:AAFgtRVfruDPxC5EyKZ763z6nlSZGx0o9gw
TELEGRAM_CHAT_ID = 6110429005
```

**Optional (configuration)**:
```
MAX_WORKERS = 10
HISTORICAL_DAYS = 30
```

**Note**: No quotes needed around values in Railway

### Step 4: Verify Start Command

1. Go to **Settings** tab
2. Check **"Start Command"** is set to:
   ```
   python scripts/run_continuous_alerts.py
   ```
3. This should be auto-detected from `railway.json`

### Step 5: Deploy

1. Railway will automatically start deploying
2. Watch **"Deployments"** tab for progress
3. Wait for deployment to complete (1-2 minutes)

### Step 6: Verify It's Running

1. Go to **"Deployments"** tab
2. Click on latest deployment
3. Go to **"Logs"** tab
4. You should see:
   ```
   ================================================================================
   CONTINUOUS REAL-TIME ALERT MONITORING
   ================================================================================
   ✅ Credentials found
   ✅ Loaded 100 symbols
   🚀 Script started at: ...
   📅 Scheduled check times today:
      • 09:15:30
      • 10:15:30
      ...
   ```

## 📊 Monitoring

- **View Logs**: Railway dashboard → Deployments → Latest → Logs
- **Check Status**: Railway dashboard → Service → Status
- **See Metrics**: Railway dashboard → Service → Metrics

## 🔍 Verify Checks Are Happening

Look for these in logs at scheduled times:
- `⏰ CHECK TIME: 09:15:30 IST`
- `⏰ CHECK TIME: 10:15:30 IST`
- etc.

See [Railway Monitoring Guide](docs/RAILWAY_MONITORING.md) for details.

## ✅ Success Indicators

- [ ] Deployment completed successfully
- [ ] Logs show "Script started at..."
- [ ] Logs show scheduled check times
- [ ] No error messages in logs
- [ ] Heartbeat messages appear every 5 minutes
- [ ] Check messages appear at scheduled times (9:15:30, 10:15:30, etc.)

## 🆘 Troubleshooting

### Deployment Fails

1. Check logs for error messages
2. Verify all environment variables are set
3. Check `requirements.txt` is correct
4. Verify Python version compatibility

### Script Not Running

1. Check logs for errors
2. Verify environment variables are set correctly
3. Check Start Command in Settings
4. Verify API credentials are valid

### No Alerts

1. Check if market is open (9:15 AM - 3:30 PM IST)
2. Verify Telegram credentials if using notifications
3. Check logs for any errors

---

**Ready to deploy?** Follow the steps above and your script will run 24/7 on Railway! 🚀

