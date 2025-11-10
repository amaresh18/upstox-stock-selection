# Railway Monitoring Guide

This guide explains how to verify that your script is running correctly on Railway and checking for alerts at the scheduled times (9:15:30, 10:15:30, etc.).

## How to Monitor Railway Logs

### Step 1: Access Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Log in to your account
3. Click on your project: `upstox-stock-selection`
4. Click on your service (the deployed app)

### Step 2: View Real-Time Logs

1. Click on the **"Deployments"** tab
2. Click on the **latest deployment** (top of the list)
3. Click on the **"Logs"** tab
4. You'll see real-time output from your script

### Step 3: What to Look For

#### ✅ Script Started Successfully

When the script starts, you should see:

```
================================================================================
CONTINUOUS REAL-TIME ALERT MONITORING
================================================================================
✅ Credentials found

Initializing stock selector...
Loading symbols...
✅ Loaded 100 symbols

================================================================================
MONITORING CONFIGURATION
================================================================================
🚀 Script started at: 2025-01-15 09:10:00 IST
Check strategy: 30 seconds after each hour completes (9:15:30, 10:15:30, 11:15:30, etc.)
   This ensures we check right after hourly candles are available
   Maximum delay: ~30 seconds after hour completes for faster alerts

📅 Scheduled check times today:
   • 09:15:30
   • 10:15:30
   • 11:15:30
   • 12:15:30
   • 13:15:30
   • 14:15:30
   • 15:15:30
Symbols monitored: 100
Market hours: 9:15 AM - 3:30 PM IST
Press Ctrl+C to stop
================================================================================
```

#### ✅ Status Checks

Every time the script checks the market status, you'll see:

```
================================================================================
📊 STATUS CHECK: 2025-01-15 09:15:00 IST
   Market Status: OPEN (Closes in 375 minutes)
================================================================================
```

#### ✅ Alert Checks at Scheduled Times

At each scheduled time (9:15:30, 10:15:30, etc.), you should see:

```
================================================================================
⏰ CHECK TIME: 2025-01-15 09:15:30 IST
================================================================================
[09:15:30] Starting alert check...

Starting analysis of 100 symbols with 10 workers...

================================================================================
STEP 1: Batch downloading historical data from Yahoo Finance
================================================================================
...
```

#### ✅ Waiting Between Checks

While waiting for the next check time, you'll see:

```
⏰ Next check at: 10:15:30 (in 59 minutes)
   (Press Ctrl+C to stop)
💤 Waiting until 10:15:30...

   💓 Heartbeat: Still waiting... 54m 30s until next check at 10:15:30
   💓 Heartbeat: Still waiting... 49m 30s until next check at 10:15:30
   💓 Heartbeat: Still waiting... 44m 30s until next check at 10:15:30
   ...
```

**Heartbeat messages appear every 5 minutes** to confirm the script is still running.

## Verifying Check Times

### Method 1: Check Logs for Timestamps

1. Open Railway logs
2. Search for `CHECK TIME:` in the logs
3. Verify timestamps match scheduled times:
   - `09:15:30` ✅
   - `10:15:30` ✅
   - `11:15:30` ✅
   - etc.

### Method 2: Check for Heartbeat Messages

1. Look for `💓 Heartbeat` messages in logs
2. These appear every 5 minutes while waiting
3. If you see heartbeats, the script is running

### Method 3: Check for Alert Check Messages

1. Look for `Starting alert check...` messages
2. These should appear at:
   - `09:15:30`
   - `10:15:30`
   - `11:15:30`
   - `12:15:30`
   - `13:15:30`
   - `14:15:30`
   - `15:15:30`

## Expected Log Pattern

During a typical day, you should see:

```
09:10:00 - Script starts
09:10:00 - Shows scheduled check times
09:15:00 - Status check (market opening)
09:15:30 - ⏰ CHECK TIME: 09:15:30
09:15:30 - Starting alert check...
09:20:00 - Check complete, waiting for next check
09:20:00 - 💓 Heartbeat (every 5 minutes)
10:15:00 - Status check
10:15:30 - ⏰ CHECK TIME: 10:15:30
10:15:30 - Starting alert check...
... (continues for each hour)
15:15:30 - ⏰ CHECK TIME: 15:15:30
15:15:30 - Starting alert check...
15:30:00 - Market closes
```

## Troubleshooting

### ❌ No Logs Appearing

**Problem**: No logs in Railway dashboard

**Solutions**:
1. Check if deployment completed successfully
2. Verify the start command is correct: `python scripts/run_continuous_alerts.py`
3. Check if the service is running (should show "Active" status)
4. Try redeploying the service

### ❌ Script Not Checking at Scheduled Times

**Problem**: Logs show script running but no check messages at scheduled times

**Solutions**:
1. Check the timezone - Railway uses UTC by default, but script converts to IST
2. Verify the script is waiting correctly (look for heartbeat messages)
3. Check if market is open (script only checks during market hours)
4. Look for errors in logs

### ❌ Script Crashes or Restarts

**Problem**: Script keeps restarting

**Solutions**:
1. Check logs for error messages
2. Verify all environment variables are set correctly
3. Check API credentials (Upstox API key and token)
4. Check memory usage (Railway free tier has 512MB limit)
5. Reduce `MAX_WORKERS` if memory issues

### ❌ No Heartbeat Messages

**Problem**: Script starts but no heartbeat messages appear

**Solutions**:
1. Check if script is actually waiting (look for "Waiting until..." messages)
2. Verify the wait logic is working
3. Check if there are any errors preventing the wait loop

## Monitoring Best Practices

### 1. Check Logs Daily

- Check Railway logs at least once per day
- Verify at least one check happened during market hours
- Look for any error messages

### 2. Set Up Alerts

- Use Telegram notifications to know when alerts are detected
- This also confirms the script is running and checking

### 3. Monitor Resource Usage

1. Go to Railway dashboard
2. Click on your service
3. Check **"Metrics"** tab
4. Monitor:
   - CPU usage
   - Memory usage
   - Network usage

### 4. Verify Check Times

Once per day, verify that checks happened at the correct times:
- Morning: Check logs for `09:15:30` check
- Afternoon: Check logs for `15:15:30` check
- If both appear, script is working correctly

## Quick Verification Checklist

Use this checklist to verify everything is working:

- [ ] Script starts successfully (see startup messages)
- [ ] Scheduled check times are displayed correctly
- [ ] Status checks appear periodically
- [ ] Alert checks happen at scheduled times (9:15:30, 10:15:30, etc.)
- [ ] Heartbeat messages appear every 5 minutes while waiting
- [ ] No error messages in logs
- [ ] Telegram notifications are received (if configured)
- [ ] Service status shows "Active" in Railway dashboard

## Example: Verifying Today's Checks

To verify checks happened today:

1. Open Railway logs
2. Search for today's date: `2025-01-15`
3. Search for `CHECK TIME:`
4. Count how many checks happened
5. Verify times match:
   - `09:15:30` ✅
   - `10:15:30` ✅
   - `11:15:30` ✅
   - `12:15:30` ✅
   - `13:15:30` ✅
   - `14:15:30` ✅
   - `15:15:30` ✅

**Expected**: 7 checks per day (one for each hour during market hours)

## Advanced: Export Logs

To analyze logs offline:

1. In Railway dashboard, go to **"Deployments"** tab
2. Click on a deployment
3. Click **"Logs"** tab
4. Copy the log output
5. Save to a file for analysis

## Summary

✅ **Script is working correctly if you see:**
- Startup messages with scheduled check times
- Status checks every hour
- Alert checks at 9:15:30, 10:15:30, etc.
- Heartbeat messages every 5 minutes
- No error messages

❌ **Script has issues if you see:**
- No logs at all
- Error messages
- Script keeps restarting
- No checks at scheduled times
- Missing heartbeat messages

---

**Need Help?**
- Check Railway logs for error messages
- Verify all environment variables are set
- Test the script locally first
- Check Railway status: [status.railway.app](https://status.railway.app)

