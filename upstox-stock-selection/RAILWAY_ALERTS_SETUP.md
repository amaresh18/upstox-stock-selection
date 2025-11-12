# Railway Setup for Continuous Alerts & Telegram Notifications

## ✅ Configuration Updated

The Railway configuration has been updated to run the **continuous alerts script** instead of the Streamlit UI.

## What Changed

### `railway.json`
- **Before**: `streamlit run app.py` (UI)
- **After**: `python scripts/run_continuous_alerts.py` (Continuous alerts)

### `Procfile`
- **Before**: `web: streamlit run app.py` (UI)
- **After**: `worker: python scripts/run_continuous_alerts.py` (Continuous alerts)

## What This Means

✅ **You'll get:**
- Automated scheduled checks at 9:15:30, 10:15:30, 11:15:30, etc.
- Telegram notifications for alerts
- "No alerts" messages when no signals detected
- Automatic monitoring 24/7

❌ **You won't have:**
- Web UI access (Streamlit app)
- Manual analysis runs

## Next Steps

### 1. Push Changes to GitHub
```bash
git add railway.json Procfile
git commit -m "Switch Railway to run continuous alerts script for Telegram notifications"
git push origin main
```

### 2. Verify Railway Configuration

After pushing, Railway will auto-deploy. Verify:

1. **Railway Dashboard** → Your Service → **Settings**
2. Check **"Start Command"** shows: `python scripts/run_continuous_alerts.py`
3. If not, manually set it in Railway dashboard

### 3. Verify Environment Variables

Railway Dashboard → **Variables** tab, ensure you have:

```
UPSTOX_API_KEY = your_api_key
UPSTOX_ACCESS_TOKEN = your_access_token
TELEGRAM_BOT_TOKEN = your_bot_token
TELEGRAM_CHAT_ID = your_chat_id
```

### 4. Check Logs

After deployment, Railway Dashboard → **Logs** tab, you should see:

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

### 5. Wait for Next Check

The script will check at the next scheduled time:
- If it's before 10:15:30 IST, it will check at 10:15:30 (for 9:15 candle)
- If it's after 10:15:30, it will check at the next scheduled time

## If You Want BOTH UI and Alerts

You have two options:

### Option 1: Two Railway Services (Recommended)
1. **Service 1**: Run Streamlit UI (`streamlit run app.py`)
2. **Service 2**: Run Continuous Alerts (`python scripts/run_continuous_alerts.py`)

Create a second service in Railway and configure it separately.

### Option 2: Switch Back to UI
If you prefer the UI, revert the changes:
- Update `railway.json` back to `streamlit run app.py`
- Push to GitHub

## Troubleshooting

### No Telegram Notifications
1. Check Railway logs for `⚠️ Telegram notifications disabled`
2. Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
3. Test your bot token manually

### Script Not Running
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Check Railway service status (should be "Running")

### No Scheduled Checks
1. Check logs for "CHECK TIME" messages
2. Verify script started successfully
3. Check timezone (should show IST in logs)

---

**After pushing these changes, Railway will automatically deploy and start running the continuous alerts script!**

