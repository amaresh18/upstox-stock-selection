# Quick Start: Railway Dual Services Setup

## ✅ Current Configuration

Your project is already configured for dual services:

### `Procfile` (Both Services Defined)
```
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
worker: python scripts/run_continuous_alerts.py
```

### `railway.json` (Primary Service - Web UI)
```json
{
  "deploy": {
    "startCommand": "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"
  }
}
```

## 🚀 Setup Steps (5 Minutes)

### Step 1: Create Second Service in Railway

1. **Go to Railway Dashboard**: https://railway.app
2. **Open your project**
3. **Click "+ New"** (top right) → **"Empty Service"**
4. **Name it**: `continuous-alerts` (or any name)

### Step 2: Configure Second Service

1. **In the new service**, go to **Settings** tab
2. **Set Start Command**:
   ```
   python scripts/run_continuous_alerts.py
   ```
3. **Connect to GitHub**:
   - Settings → Source → Connect to your GitHub repo
   - Railway will auto-deploy

### Step 3: Set Environment Variables (Project Level - Recommended)

**Set once, both services use them:**

1. Railway Dashboard → **Project Settings** (not service settings)
2. **Variables** tab → **New Variable**
3. Add these (no quotes):
   ```
   UPSTOX_API_KEY = e3d3c1d1-5338-4efa-b77f-c83ea604ea43
   UPSTOX_ACCESS_TOKEN = eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTE0MDE1MDY0ZmYzYTViMWM4YTk4NTQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjkxODczNiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyOTg0ODAwfQ.ETjfi9F3QQqCqCtiwypBSsMF_zb_zqfUfifv3t6q7sI
   TELEGRAM_BOT_TOKEN = 8547171229:AAFgtRVfruDPxC5EyKZ763z6nlSZGx0o9gw
   TELEGRAM_CHAT_ID = 6110429005
   ```

### Step 4: Verify Both Services

**Service 1 (Web UI):**
- Status: ✅ Active (green)
- Logs show: `You can now view your Streamlit app`
- Public URL available in Settings → Domains

**Service 2 (Continuous Alerts):**
- Status: ✅ Active (green)
- Logs show: `CONTINUOUS REAL-TIME ALERT MONITORING`
- Logs show: `📅 Scheduled check times today:`

### Step 5: Test

1. **Web UI**: Open the public URL from Service 1
2. **Alerts**: Wait for next scheduled check (10:15:30, 11:15:30, etc.)
3. **Telegram**: You should receive notifications

## 📊 What You Get

### Service 1: Web UI
- ✅ Public web interface
- ✅ Manual analysis and configuration
- ✅ Real-time results
- ✅ OAuth login for Upstox
- ✅ Accessible from anywhere

### Service 2: Continuous Alerts
- ✅ Automated scheduled checks
- ✅ Telegram notifications
- ✅ "No alerts" messages
- ✅ Runs 24/7 in background
- ✅ No manual intervention needed

## 💰 Cost

**Free Tier**: 500 hours/month
- 1 service 24/7 = 720 hours/month (exceeds free tier)
- 2 services 24/7 = 1,440 hours/month (need paid plan)

**Recommendation**:
- Keep alerts service running 24/7
- Pause web UI when not using it
- Or upgrade to $5/month for unlimited hours

## 🔧 Troubleshooting

### Service Not Starting?
- Check logs for errors
- Verify environment variables are set
- Check start command is correct

### No Telegram Alerts?
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
- Check continuous alerts service logs
- Look for "CHECK TIME" messages in logs

### UI Not Accessible?
- Check web UI service is running
- Verify public domain is assigned
- Check logs for port binding errors

## 📝 Next Steps

1. ✅ Push current code to GitHub (if not already)
2. ✅ Create second service in Railway
3. ✅ Set environment variables
4. ✅ Verify both services running
5. ✅ Test web UI and wait for alerts

---

**That's it! You now have both services running simultaneously! 🎉**

For detailed documentation, see: `docs/RAILWAY_DUAL_SERVICE_SETUP.md`

