# Quick Fix: No Telegram Alerts Issue

## Immediate Checks

### 1. Check Railway Logs (MOST IMPORTANT)

Go to Railway Dashboard → Your Project → Service → **Logs** tab

Look for these messages around **10:15:30 IST** (when 9:15 candle is checked):

✅ **Good signs:**
```
⏰ CHECK TIME: 2025-XX-XX 10:15:30 IST
📊 Checking for alerts in 9:15 candle (completed at 10:15)
📱 Sent 'no alerts' notification to Telegram
```

❌ **Problem signs:**
```
⚠️  Telegram notifications disabled
❌ Error in monitoring loop: ...
```

### 2. Verify Telegram Credentials in Railway

Railway Dashboard → Your Service → **Variables** tab

**MUST HAVE:**
```
TELEGRAM_BOT_TOKEN = your_bot_token_here
TELEGRAM_CHAT_ID = your_chat_id_here
```

**Important:**
- No quotes around values
- No extra spaces
- Both must be set

### 3. Verify Script is Running

In Railway logs, look for:
```
================================================================================
CONTINUOUS REAL-TIME ALERT MONITORING
================================================================================
✅ Credentials found
✅ Loaded 100 symbols
🚀 Script started at: ...
```

If you don't see this, the script might have crashed.

### 4. Important: 9:15 Candle Check Time

**The 9:15 candle is checked at 10:15:30 IST, NOT 9:15:30!**

- 9:15 candle runs from 9:15 AM to 10:15 AM
- It completes at 10:15 AM
- Script checks at 10:15:30 AM (30 seconds after completion)

So if you're looking for 9:15 candle alerts, check logs at **10:15:30 IST**.

## Common Issues & Fixes

### Issue 1: "Telegram notifications disabled"

**Fix:** Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in Railway Variables

### Issue 2: Script not running

**Fix:**
1. Railway Dashboard → Service → **Settings** → **Restart**
2. Check logs for startup messages
3. Verify `UPSTOX_API_KEY` and `UPSTOX_ACCESS_TOKEN` are set

### Issue 3: No logs at 10:15:30

**Possible causes:**
- Script crashed before check time
- Script not started
- Timezone mismatch

**Fix:**
- Check Railway logs for errors
- Restart the service
- Verify script is running

### Issue 4: Check happened but no notification

**Check logs for:**
- `📱 Sent 'no alerts' notification to Telegram` - Notification was sent
- `⚠️  Telegram notifications disabled` - Credentials missing
- `❌ Error sending Telegram message` - API error

## Test Your Telegram Bot

Test if your bot is working:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

Should return:
```json
{"ok":true,"result":{"id":...,"is_bot":true,"first_name":"..."}}
```

## Next Steps

1. **Check Railway Logs** - Most important step
2. **Verify Telegram Variables** - Both must be set
3. **Restart Service** - If script not running
4. **Check at 10:15:30** - That's when 9:15 candle is checked

## Still Not Working?

1. Copy relevant log lines from Railway
2. Verify all environment variables are set
3. Test Telegram bot manually
4. Check script status in Railway dashboard

---

**Remember:** The 9:15 candle is checked at **10:15:30 IST**, not 9:15:30!

