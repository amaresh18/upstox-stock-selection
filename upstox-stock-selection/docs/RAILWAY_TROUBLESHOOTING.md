# Railway Troubleshooting Guide

## Issue: No Telegram Alerts Received

If you're not receiving Telegram alerts (including "no alerts" messages), check the following:

### 1. Check Railway Logs

Go to Railway Dashboard → Your Project → Service → **Logs** tab

Look for:
- `⏰ CHECK TIME: 2025-XX-XX 10:15:30 IST` (for 9:15 candle check)
- `📱 Sent 'no alerts' notification to Telegram`
- `⚠️  Telegram notifications disabled`

### 2. Verify Telegram Credentials

In Railway Dashboard → **Variables** tab, ensure you have:
```
TELEGRAM_BOT_TOKEN = your_bot_token
TELEGRAM_CHAT_ID = your_chat_id
```

**Important**: 
- No quotes around values
- Values must match exactly (no extra spaces)
- Both variables must be set

### 3. Check Script is Running

In Railway logs, you should see:
```
================================================================================
CONTINUOUS REAL-TIME ALERT MONITORING
================================================================================
✅ Credentials found
✅ Loaded 100 symbols
🚀 Script started at: ...
```

If you don't see this, the script might have crashed or not started.

### 4. Verify Scheduled Check Times

The script checks at:
- **10:15:30** (checks 9:15 candle - completes at 10:15)
- **11:15:30** (checks 10:15 candle - completes at 11:15)
- **12:15:30** (checks 11:15 candle - completes at 12:15)
- **13:15:30** (checks 12:15 candle - completes at 13:15)
- **14:15:30** (checks 13:15 candle - completes at 14:15)
- **15:15:30** (checks 14:15 candle - completes at 15:15)
- **15:30:00** (checks 15:15 candle - completes at 15:30)

**Note**: The 9:15 candle is checked at **10:15:30**, not 9:15:30!

### 5. Check Timezone

Railway uses UTC by default. The script converts to IST, but verify:
- Logs should show `IST` timezone
- Check times should match IST market hours (9:15 AM - 3:30 PM)

### 6. Test Telegram Bot

Test your Telegram bot manually:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

Should return:
```json
{"ok":true,"result":{"id":...,"is_bot":true,"first_name":"..."}}
```

### 7. Check for Errors

Look for these in Railway logs:
- `❌ Error in monitoring loop: ...`
- `⚠️  Telegram notifications disabled`
- `401 Unauthorized` (Telegram API error)
- `403 Forbidden` (Telegram API error)

### 8. Verify API Credentials

Ensure these are set in Railway:
```
UPSTOX_API_KEY = your_api_key
UPSTOX_ACCESS_TOKEN = your_access_token
```

### 9. Check Market Status

The script only runs during market hours (9:15 AM - 3:30 PM IST, Mon-Fri).

If it's outside market hours, you'll see:
```
Market is closed for today
Monitoring will resume tomorrow at 9:15:30 AM
```

### 10. Force Restart

If nothing works:
1. Go to Railway Dashboard → Your Service
2. Click **Settings** → **Restart**
3. Watch the logs for startup messages

## Common Issues

### Issue: "Telegram notifications disabled"

**Solution**: Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in Railway Variables

### Issue: Script not checking at scheduled times

**Solution**: 
- Check Railway logs for "CHECK TIME" messages
- Verify script is running (not crashed)
- Check timezone settings

### Issue: No "no alerts" message

**Possible causes**:
1. Telegram credentials not set
2. Script crashed before sending notification
3. Check happened but notification failed silently

**Solution**: Check Railway logs for error messages

### Issue: Wrong candle being checked

**Note**: The 9:15 candle completes at 10:15, so it's checked at 10:15:30, not 9:15:30.

This is correct behavior - candles are checked 30 seconds after they complete.

## Debugging Steps

1. **Check Railway Logs** (most important)
   - Look for "CHECK TIME" messages
   - Look for "Sent 'no alerts' notification"
   - Look for errors

2. **Verify Environment Variables**
   - Railway Dashboard → Variables tab
   - Ensure all required variables are set

3. **Test Telegram Bot**
   - Use curl or Telegram app to test bot
   - Verify chat_id is correct

4. **Check Script Status**
   - Railway Dashboard → Service → Status
   - Should show "Running"

5. **Review Recent Deployments**
   - Railway Dashboard → Deployments
   - Check if latest deployment succeeded

## Getting Help

If issues persist:
1. Copy relevant log lines from Railway
2. Check all environment variables are set
3. Verify Telegram bot is working
4. Check script is running (not crashed)

---

**Last Updated**: Troubleshooting guide for Railway deployment issues

