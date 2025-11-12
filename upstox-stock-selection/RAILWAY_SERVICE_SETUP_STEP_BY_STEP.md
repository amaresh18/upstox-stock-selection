# Step-by-Step: Railway Service Setup for Telegram Notifications

## Current Situation
You currently have **1 service** (Web UI) running. You need **2 services** to get Telegram notifications:
1. **Service 1**: Web UI (already running) ✅
2. **Service 2**: Continuous Alerts Worker (needs to be created) ❌

---

## 📋 Step-by-Step Instructions

### Step 1: Open Railway Dashboard

1. Go to **https://railway.app**
2. **Sign in** to your account
3. **Click on your project** (the one with your stock selection app)

### Step 2: Check Current Services

1. In your project dashboard, look at the **left sidebar**
2. You should see:
   - **One service** (probably named after your repo or "web")
   - This is your **Web UI service** ✅

### Step 3: Create Second Service (Worker)

1. **Click the "+ New" button** (top right of the dashboard)
2. **Select "Empty Service"** from the dropdown
3. **Name it**: `continuous-alerts` (or any name you prefer)
4. **Click "Add Service"**

### Step 4: Configure the Worker Service

1. **Click on the new service** you just created
2. Go to **Settings** tab (top menu)
3. **IMPORTANT - Set Build Command First**:
   - Scroll to **"Build Command"** section
   - **Leave it EMPTY** (Railway will auto-detect from `requirements.txt`)
   - OR set to: `pip install -r requirements.txt`
4. **Set Start Command**:
   - Scroll to **"Start Command"** section
   - **Enter this command**:
     ```
     python scripts/run_continuous_alerts.py
     ```
5. **Set Build System** (if available):
   - Look for **"Builder"** or **"Build System"** option
   - Select **"Nixpacks"** (NOT Railpack)
   - If you see "Railpack", change it to "Nixpacks"
6. **Click "Save"**

**⚠️ Important**: 
- **DO NOT** set up a cron schedule in Railway
- The script handles scheduling internally (sleeps until next check time)
- It runs continuously and automatically calculates when to check
- Railway cron scheduler is NOT needed
- **If you see "Railpack" errors**, make sure to select "Nixpacks" as the builder

### Step 5: Connect to GitHub (If Not Auto-Connected)

1. In the **Settings** tab of your new service
2. Scroll to **"Source"** section
3. **Click "Connect GitHub"** (if not already connected)
4. **Select your repository**: `upstox-stock-selection`
5. Railway will **auto-deploy** the service

### Step 6: Set Environment Variables (Project Level)

**IMPORTANT**: Set these at **Project level** (not service level) so both services can use them.

1. **Go back to Project Dashboard** (click project name at top)
2. **Click "Variables" tab** (top menu)
3. **Click "New Variable"** button
4. **Add these variables one by one**:

   ```
   Variable Name: UPSTOX_API_KEY
   Value: e3d3c1d1-5338-4efa-b77f-c83ea604ea43
   ```

   ```
   Variable Name: UPSTOX_ACCESS_TOKEN
   Value: eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzUUFSVEoiLCJqdGkiOiI2OTE0MDE1MDY0ZmYzYTViMWM4YTk4NTQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MjkxODczNiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyOTg0ODAwfQ.ETjfi9F3QQqCqCtiwypBSsMF_zb_zqfUfifv3t6q7sI
   ```

   ```
   Variable Name: TELEGRAM_BOT_TOKEN
   Value: 8547171229:AAFgtRVfruDPxC5EyKZ763z6nlSZGx0o9gw
   ```

   ```
   Variable Name: TELEGRAM_CHAT_ID
   Value: 6110429005
   ```

5. **Click "Add"** after each variable
6. **Verify all 4 variables** are listed

### Step 7: Verify Both Services Are Running

1. **Go back to Project Dashboard**
2. You should now see **2 services** in the left sidebar:
   - **Service 1**: Your web UI (Streamlit)
   - **Service 2**: `continuous-alerts` (or whatever you named it)

3. **Click on Service 2** (continuous-alerts)
4. **Go to "Deployments" tab**
5. **Check the logs** - you should see:
   ```
   ⚠️  SCHEDULED TIME SLOTS ONLY - NO CONTINUOUS CHECKING
   This script will ONLY run at scheduled time slots:
     • 9:15:30 AM (checks 9:15 candle)
     • 10:15:30 AM (checks 10:15 candle)
     ...
   ```

6. **Look for Telegram status**:
   - ✅ If you see: `📱 Sending Telegram notifications...` → **Working!**
   - ⚠️ If you see: `⚠️  Telegram notifications disabled` → **Check environment variables**

### Step 8: Test Telegram Notifications

1. **Wait for the next scheduled check time** (see times above)
2. **Check Railway logs** for Service 2
3. **Check your Telegram** for notifications

---

## 🔍 Troubleshooting

### Problem: "I don't see the + New button"

**Solution**: 
- Make sure you're in the **Project Dashboard** (not inside a service)
- Click your project name at the top to go back to project level

### Problem: "Service won't start"

**Solution**:
1. Check **Start Command** is exactly: `python scripts/run_continuous_alerts.py`
2. Check **environment variables** are set at Project level
3. Check **logs** for error messages

### Problem: "Telegram notifications disabled"

**Solution**:
1. Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
2. Make sure they're set at **Project level** (not service level)
3. **Redeploy** the service after adding variables

### Problem: "I only see 1 service"

**Solution**:
- You need to **create the second service** manually (Step 3 above)
- Railway doesn't automatically create it from Procfile
- You need to create it as an "Empty Service" and configure it

---

## ✅ Success Checklist

- [ ] 2 services visible in Railway dashboard
- [ ] Service 2 (continuous-alerts) is running (green status)
- [ ] All 4 environment variables are set at Project level
- [ ] Service 2 logs show scheduled check times
- [ ] Service 2 logs show Telegram is enabled (not disabled)
- [ ] Wait for next scheduled check time
- [ ] Receive Telegram notification (or "no alerts" message)

---

## 📱 What Happens Next

Once both services are running:

1. **Service 1 (Web UI)**: 
   - Accessible via public URL
   - Manual analysis and configuration
   - Real-time results

2. **Service 2 (Continuous Alerts)**:
   - Runs automatically 24/7
   - Checks at scheduled times (9:15, 10:15, 11:15, etc.)
   - Sends Telegram notifications when alerts are detected
   - Sends "no alerts" messages when no signals found

---

**Need more help?** Check the logs in Railway for specific error messages!

