# Railway Deployment Guide - Step by Step

This guide will walk you through deploying the Upstox Stock Selection system to Railway so it runs 24/7 in the cloud.

## What is Railway?

Railway is a cloud platform that makes it easy to deploy and run applications. It automatically:
- Detects your Python project
- Installs dependencies from `requirements.txt`
- Runs your script continuously
- Restarts if it crashes
- Provides logs and monitoring

## Prerequisites

1. **GitHub Account** (free) - Railway connects via GitHub
2. **Railway Account** (free) - Sign up at [railway.app](https://railway.app)
3. **Your code on GitHub** - Push your project to GitHub first

## Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

If you haven't already:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/yourusername/upstox-stock-selection.git
git branch -M main
git push -u origin main
```

### Step 2: Sign Up for Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"** or **"Login"**
3. Sign up with **GitHub** (recommended - easiest)
4. Authorize Railway to access your GitHub account

### Step 3: Create a New Project

1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `upstox-stock-selection`
4. Railway will automatically detect it's a Python project

### Step 4: Configure Environment Variables

1. Click on your project in Railway dashboard
2. Click on the **service** (your app)
3. Go to **"Variables"** tab
4. Click **"New Variable"** and add each one:

```
UPSTOX_API_KEY = your_api_key_here
UPSTOX_ACCESS_TOKEN = your_access_token_here
TELEGRAM_BOT_TOKEN = your_bot_token_here (optional)
TELEGRAM_CHAT_ID = your_chat_id_here (optional)
MAX_WORKERS = 10
HISTORICAL_DAYS = 30
```

**Important**: 
- Replace `your_api_key_here` with your actual Upstox API key
- Replace `your_access_token_here` with your actual access token
- No quotes needed around values
- Click "Add" after each variable

### Step 5: Configure the Start Command

1. In your service settings, go to **"Settings"** tab
2. Scroll to **"Start Command"**
3. Set it to:
   ```
   python scripts/run_continuous_alerts.py
   ```
4. Railway will use this command to start your script

### Step 6: Deploy

1. Railway will automatically start deploying when you:
   - Push code to GitHub, OR
   - Click **"Deploy"** button
2. Watch the **"Deployments"** tab to see the build progress
3. Wait for deployment to complete (usually 1-2 minutes)

### Step 7: Verify It's Running

1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Go to **"Logs"** tab
4. You should see output like:
   ```
   ================================================================================
   CONTINUOUS REAL-TIME ALERT MONITORING
   ================================================================================
   ✅ Loaded 100 symbols
   🚀 Script started at: 2025-01-15 09:10:00 IST
   📅 Scheduled check times today:
      • 09:15:30
      • 10:15:30
      • 11:15:30
      ...
   ⏰ Next check at: 09:15:30 (in 5 minutes)
   ```

**📖 For detailed monitoring instructions**, see [Railway Monitoring Guide](RAILWAY_MONITORING.md)

## How It Runs on Railway

### Continuous Execution

Railway runs your script as a **long-running process**:

1. **Starts**: When deployment completes, Railway runs:
   ```bash
   python scripts/run_continuous_alerts.py
   ```

2. **Runs Continuously**: The script enters its main loop:
   ```python
   while True:
       # Check if market is open
       if is_market_open():
           # Check for alerts
           await check_for_alerts()
           # Wait until next hour (9:16, 10:16, etc.)
           await asyncio.sleep(wait_seconds)
       else:
           # Wait if market is closed
           await asyncio.sleep(3600)
   ```

3. **Never Stops**: Railway keeps the process running 24/7

4. **Auto-Restart**: If the script crashes, Railway automatically restarts it

### Resource Usage

Railway provides:
- **CPU**: Shared CPU resources
- **Memory**: 512MB RAM (free tier)
- **Network**: Full internet access for API calls
- **Storage**: Ephemeral (resets on redeploy)

### Logs and Monitoring

**View Logs:**
1. Go to your service in Railway dashboard
2. Click **"Deployments"** tab
3. Click on latest deployment
4. Click **"Logs"** tab
5. See real-time output from your script

**What You'll See:**
```
================================================================================
⏰ CHECK TIME: 2025-01-15 09:15:30 IST
================================================================================
[09:15:30] Starting alert check...
Starting analysis of 100 symbols with 10 workers...

STEP 1: Batch downloading historical data from Yahoo Finance
✅ Got usable data for 95 symbols.

STEP 2: Analyzing symbols with Upstox current day data
Fetching current day data from Upstox for RELIANCE...
Got 5 bars from Upstox for RELIANCE (today)

🔔 NEW ALERTS DETECTED: 3 alerts
🚨 RELIANCE - BREAKOUT
   Time: 2025-01-15 10:30:00
   Price: ₹2450.50
   Level: ₹2440.00 (ABOVE)
   Volume: 2.5x average

📱 Sending Telegram notifications...
   ✅ Sent 3 alert(s) to Telegram

⏰ Next check at: 10:15:30 (in 59 minutes)
💤 Waiting until 10:15:30...
   💓 Heartbeat: Still waiting... 54m 30s until next check at 10:15:30
```

**📖 For detailed monitoring and verification**, see [Railway Monitoring Guide](RAILWAY_MONITORING.md)

## Railway Free Tier Limits

- **500 hours/month** of runtime
- **$5 credit** per month
- **512MB RAM**
- **Shared CPU**

**For 24/7 operation:**
- 24 hours/day × 30 days = 720 hours/month
- Free tier: 500 hours/month
- **You'll need to upgrade** to Hobby plan ($5/month) for true 24/7

**OR** use free tier strategically:
- Run only during market hours (9:15 AM - 3:30 PM IST)
- That's ~6 hours/day × 30 days = 180 hours/month ✅ (fits in free tier!)

## Troubleshooting

### Script Not Starting

1. **Check Logs**: Look for error messages
2. **Check Environment Variables**: Ensure all required variables are set
3. **Check Start Command**: Should be `python scripts/run_continuous_alerts.py`

### Script Crashes

1. **Check Logs**: Look for Python errors
2. **Check API Credentials**: Ensure Upstox API key and token are valid
3. **Check Network**: Railway has internet access, but verify API endpoints

### No Alerts Being Sent

1. **Check Telegram Variables**: Ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
2. **Check Logs**: Look for "Telegram notifications disabled" message
3. **Test Locally**: Run script locally first to verify Telegram works

### High Memory Usage

1. **Reduce Workers**: Set `MAX_WORKERS=5` instead of 10
2. **Reduce Symbols**: Process fewer symbols at once
3. **Upgrade Plan**: Railway Hobby plan has more RAM

## Updating Your Code

When you push changes to GitHub:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update code"
   git push
   ```

2. **Railway Auto-Deploys**: Railway detects the push and automatically:
   - Pulls latest code
   - Rebuilds the application
   - Restarts the script

3. **Monitor Deployment**: Watch the "Deployments" tab for progress

## Cost Management

### Free Tier Strategy

To stay within 500 hours/month free tier:

1. **Run Only During Market Hours**:
   - Modify script to stop after market closes
   - Restart before market opens (use Railway cron or scheduled tasks)

2. **Or Upgrade to Hobby** ($5/month):
   - True 24/7 operation
   - More resources
   - Better reliability

### Monitoring Usage

1. Go to Railway dashboard
2. Click on your project
3. See usage in **"Usage"** tab
4. Track hours consumed vs. free tier limit

## Best Practices

1. **Keep Secrets Safe**: Never commit API keys to GitHub
2. **Monitor Logs**: Check logs regularly to ensure script is running
3. **Test Locally First**: Always test changes locally before deploying
4. **Use Telegram**: Set up Telegram notifications to know when alerts are detected
5. **Backup Data**: Important data (like NSE.json) should be backed up

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Verify it's running (check logs)
3. ✅ Test Telegram notifications
4. ✅ Monitor for alerts
5. ✅ Enjoy 24/7 automated alerts!

## Support

If you encounter issues:
1. Check Railway logs for error messages
2. Verify all environment variables are set
3. Test the script locally first
4. Check Railway status page: [status.railway.app](https://status.railway.app)

---

**That's it!** Your script will now run 24/7 in the cloud on Railway, checking for alerts every hour and sending Telegram notifications when detected. 🚀

