# Railway Dual Service Setup Guide

## Overview

This guide explains how to run **both** the Streamlit UI and the Continuous Alerts script simultaneously on Railway using **two separate services**.

## Why Two Services?

- ✅ **Streamlit UI Service**: Web interface for manual analysis and configuration
- ✅ **Continuous Alerts Service**: Automated Telegram notifications at scheduled times
- ✅ **Both run independently**: One can restart without affecting the other
- ✅ **Shared environment variables**: Both services use the same credentials

## Step-by-Step Setup

### Step 1: Current Service (Keep as Streamlit UI)

Your current Railway service should run the **Streamlit UI**:

**Configuration:**
- **Service Name**: `web-ui` (or keep existing name)
- **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
- **Type**: `web` service (gets a public URL)

**Files already configured:**
- `railway.json` → Points to Streamlit
- `Procfile` → Has `web:` entry for Streamlit

### Step 2: Create Second Service (Continuous Alerts)

1. **Go to Railway Dashboard**
   - Open your project
   - Click **"+ New"** button (top right)
   - Select **"Empty Service"**

2. **Configure the Service**
   - **Service Name**: `continuous-alerts` (or any name you prefer)
   - **Settings** → **Start Command**: 
     ```
     python scripts/run_continuous_alerts.py
     ```
   - **Type**: `worker` service (no public URL needed)

3. **Link to Same GitHub Repo**
   - In the new service, go to **Settings** → **Source**
   - Connect to the same GitHub repository
   - Railway will auto-deploy from the same codebase

### Step 3: Set Environment Variables

**Important**: Set environment variables for **BOTH services**:

1. **For Web UI Service:**
   - Railway Dashboard → `web-ui` service → **Variables** tab
   - Add:
     ```
     UPSTOX_API_KEY = your_api_key
     UPSTOX_ACCESS_TOKEN = your_access_token
     TELEGRAM_BOT_TOKEN = your_bot_token (optional)
     TELEGRAM_CHAT_ID = your_chat_id (optional)
     ```

2. **For Continuous Alerts Service:**
   - Railway Dashboard → `continuous-alerts` service → **Variables** tab
   - Add the **same variables**:
     ```
     UPSTOX_API_KEY = your_api_key
     UPSTOX_ACCESS_TOKEN = your_access_token
     TELEGRAM_BOT_TOKEN = your_bot_token (required for alerts)
     TELEGRAM_CHAT_ID = your_chat_id (required for alerts)
     ```

**Tip**: Railway allows you to set variables at the **project level** so both services inherit them:
- Railway Dashboard → **Project Settings** → **Variables**
- Add variables here, and both services will use them automatically

### Step 4: Verify Both Services Are Running

1. **Check Service Status:**
   - Railway Dashboard → Both services should show **"Active"** status
   - Green indicator = Running

2. **Check Logs:**

   **Web UI Service Logs:**
   ```
   You can now view your Streamlit app in your browser.
   Network URL: http://0.0.0.0:PORT
   ```

   **Continuous Alerts Service Logs:**
   ```
   ================================================================================
   CONTINUOUS REAL-TIME ALERT MONITORING
   ================================================================================
   ✅ Credentials found
   ✅ Loaded 100 symbols
   🚀 Script started at: ...
   📅 Scheduled check times today:
      • 10:15:30 (checks 9:15 candle)
      • 11:15:30 (checks 10:15 candle)
      ...
   ```

3. **Access Web UI:**
   - Railway Dashboard → `web-ui` service → **Settings** → **Domains**
   - Copy the public URL (e.g., `https://your-app.railway.app`)
   - Open in browser to access the Streamlit UI

### Step 5: Monitor Both Services

**Web UI Service:**
- Access via public URL
- Use for manual analysis and configuration
- Can be paused/stopped without affecting alerts

**Continuous Alerts Service:**
- Runs in background
- Sends Telegram notifications automatically
- Should run 24/7 for alerts

## Service Configuration Summary

### Service 1: Web UI
```
Name: web-ui
Type: web
Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
Public URL: Yes (automatically assigned)
Purpose: Manual analysis, configuration, testing
```

### Service 2: Continuous Alerts
```
Name: continuous-alerts
Type: worker
Start Command: python scripts/run_continuous_alerts.py
Public URL: No (runs in background)
Purpose: Automated Telegram notifications
```

## Cost Considerations

**Railway Free Tier:**
- 500 hours/month total across all services
- If both services run 24/7:
  - 2 services × 24 hours × 30 days = 1,440 hours/month
  - **Exceeds free tier** (need paid plan ~$5/month)

**Options:**
1. **Run only alerts service** (saves hours)
2. **Run UI only when needed** (pause when not using)
3. **Upgrade to paid plan** ($5/month for unlimited hours)

## Troubleshooting

### Service Not Starting

**Check Logs:**
- Railway Dashboard → Service → **Logs** tab
- Look for error messages

**Common Issues:**
- Missing environment variables → Add in Variables tab
- Import errors → Check `requirements.txt` has all dependencies
- Port conflicts → Only web services need `$PORT`

### Alerts Not Working

1. **Check Continuous Alerts Service:**
   - Is it running? (green status)
   - Check logs for "CHECK TIME" messages
   - Verify Telegram credentials are set

2. **Check Telegram Bot:**
   - Test bot token manually
   - Verify chat ID is correct

### UI Not Accessible

1. **Check Web UI Service:**
   - Is it running? (green status)
   - Check logs for "Network URL" message
   - Verify public domain is assigned

2. **Check URL:**
   - Railway Dashboard → Service → Settings → Domains
   - Copy the correct URL

## Quick Reference

### Start/Stop Services

**Pause a Service:**
- Railway Dashboard → Service → **Settings** → **Pause**

**Resume a Service:**
- Railway Dashboard → Service → **Settings** → **Resume**

**Restart a Service:**
- Railway Dashboard → Service → **Deployments** → **Redeploy**

### View Logs

- Railway Dashboard → Service → **Logs** tab
- Real-time log streaming
- Search/filter logs

### Update Code

1. Push changes to GitHub
2. Railway auto-deploys both services
3. Or manually trigger: Service → **Deployments** → **Redeploy**

## Next Steps

1. ✅ Create second service in Railway
2. ✅ Configure start command for alerts script
3. ✅ Set environment variables for both services
4. ✅ Verify both services are running
5. ✅ Test web UI access
6. ✅ Wait for next scheduled alert check
7. ✅ Monitor Telegram for notifications

---

**You now have both services running! 🎉**
- Web UI for manual analysis
- Continuous alerts for automated notifications

