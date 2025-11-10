# Telegram Notifications Setup Guide

This guide will walk you through setting up Telegram notifications for the Upstox Stock Selection system. Once configured, you'll receive instant alerts on your phone when stock signals are detected.

## Why Telegram Notifications?

- ✅ **Instant Alerts**: Get notified immediately when alerts are detected
- ✅ **Mobile Access**: Receive notifications on your phone anywhere
- ✅ **Free**: Telegram is completely free
- ✅ **Reliable**: Telegram has high uptime and delivery rates
- ✅ **Easy Setup**: Takes only 5 minutes to configure

## Prerequisites

1. **Telegram Account**: Download Telegram app on your phone
   - [Android](https://play.google.com/store/apps/details?id=org.telegram.messenger)
   - [iOS](https://apps.apple.com/app/telegram/id686449807)
   - [Desktop](https://desktop.telegram.org/)

2. **Telegram Username**: You need a Telegram account (can be anonymous)

## Step-by-Step Setup

### Step 1: Create a Telegram Bot

1. **Open Telegram** on your phone or desktop

2. **Search for BotFather**:
   - In Telegram search bar, type: `@BotFather`
   - Click on the official BotFather (verified with blue checkmark)

3. **Start a conversation**:
   - Click "Start" button
   - You'll see a welcome message with commands

4. **Create a new bot**:
   - Send this command: `/newbot`
   - BotFather will ask: "Alright, a new bot. How are we going to call it? Please choose a name for your bot."
   - **Reply with a name** (e.g., "Upstox Stock Alerts" or "My Stock Alerts")
   - BotFather will ask: "Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot."
   - **Reply with a username** ending in `bot` (e.g., "upstox_alerts_bot" or "mystockalerts_bot")
   - ⚠️ **Important**: The username must be unique and end with `bot`

5. **Get your Bot Token**:
   - BotFather will reply with a message like:
     ```
     Done! Congratulations on your new bot. You will find it at t.me/your_bot_username. 
     Use this token to access the HTTP API:
     
     123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
     
     Keep your token secure and store it safely, it can be used by anyone to control your bot.
     ```
   - **Copy the token** (the long string of numbers and letters)
   - ⚠️ **Important**: Keep this token secret! Don't share it publicly.

**Example Bot Token:**
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

### Step 2: Get Your Chat ID

You need to get your Telegram Chat ID so the bot knows where to send messages.

#### Method 1: Using @userinfobot (Easiest)

1. **Search for @userinfobot** in Telegram
2. **Start a conversation** with @userinfobot
3. **Click "Start"** button
4. The bot will reply with your information, including your **Chat ID**
5. **Copy your Chat ID** (it's a number like `123456789`)

**Example Response:**
```
Your ID: 123456789
First Name: Your Name
Username: @yourusername
```

#### Method 2: Using @getidsbot

1. **Search for @getidsbot** in Telegram
2. **Start a conversation** and click "Start"
3. The bot will show your Chat ID

#### Method 3: Using Telegram Web (For Groups)

If you want to send alerts to a **group** instead of personal chat:

1. **Create a Telegram group** (or use existing)
2. **Add your bot to the group**:
   - In group settings, click "Add Members"
   - Search for your bot username (e.g., `@upstox_alerts_bot`)
   - Add the bot to the group
3. **Get group Chat ID**:
   - Send a message in the group
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Replace `<YOUR_BOT_TOKEN>` with your actual bot token
   - Look for `"chat":{"id":-123456789}` in the response
   - The group Chat ID will be a **negative number** (e.g., `-123456789`)

**Example Group Chat ID:**
```
-123456789
```

### Step 3: Test Your Bot

Before configuring the script, test that your bot works:

1. **Find your bot**:
   - In Telegram search, type your bot username (e.g., `@upstox_alerts_bot`)
   - Click on your bot

2. **Start a conversation**:
   - Click "Start" button
   - Your bot should respond (if you've set up a welcome message)

3. **Send a test message**:
   - Send any message to your bot
   - The bot should receive it (even if it doesn't reply yet)

### Step 4: Configure Environment Variables

Now you need to set the bot token and chat ID as environment variables.

#### For Local Testing (Windows PowerShell)

```powershell
# Set Telegram bot token
$env:TELEGRAM_BOT_TOKEN='123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890'

# Set Telegram chat ID
$env:TELEGRAM_CHAT_ID='123456789'

# Verify they're set
echo $env:TELEGRAM_BOT_TOKEN
echo $env:TELEGRAM_CHAT_ID
```

#### For Local Testing (Windows CMD)

```cmd
set TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
set TELEGRAM_CHAT_ID=123456789
```

#### For Local Testing (Linux/Mac)

```bash
export TELEGRAM_BOT_TOKEN='123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890'
export TELEGRAM_CHAT_ID='123456789'

# Verify they're set
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

#### For Cloud Deployment (Railway/Render/etc.)

1. **Go to your cloud platform dashboard**
2. **Navigate to Environment Variables** section
3. **Add new variables**:
   - `TELEGRAM_BOT_TOKEN` = `123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890`
   - `TELEGRAM_CHAT_ID` = `123456789`
4. **Save** the variables

**Important Notes:**
- Replace the example values with your actual bot token and chat ID
- No quotes needed around values in cloud platforms
- Make sure there are no extra spaces

### Step 5: Test the Integration

1. **Run the script**:
   ```bash
   python scripts/run_realtime_alerts.py
   ```

2. **Check the output**:
   - You should see: `📱 Sending Telegram notifications...`
   - Then: `✅ Sent X alert(s) to Telegram`

3. **Check your Telegram**:
   - Open Telegram app
   - Go to your bot chat
   - You should see alert messages like:
     ```
     🟢 BREAKOUT - RELIANCE
     
     ⏰ Time: 2025-01-15 10:30:00
     💰 Price: ₹2450.50
     📊 Level: ₹2440.00 (ABOVE)
     📈 Volume: 2.5x average
     ```

### Step 6: Verify Continuous Alerts

For continuous monitoring:

1. **Run the continuous alerts script**:
   ```bash
   python scripts/run_continuous_alerts.py
   ```

2. **Check the output**:
   - You should see: `⚠️  Telegram notifications disabled` if NOT configured
   - OR: `📱 Sending Telegram notifications...` if configured correctly

3. **Wait for alerts**:
   - The script checks every hour (9:16, 10:16, etc.)
   - When alerts are detected, you'll receive Telegram notifications

## Troubleshooting

### Problem: "Telegram notifications disabled"

**Solution:**
- Check that both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
- Verify environment variables are set correctly
- Restart the script after setting variables

### Problem: "Failed to send Telegram notifications"

**Possible Causes:**
1. **Invalid Bot Token**:
   - Verify your bot token is correct
   - Make sure there are no extra spaces
   - Token should look like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

2. **Invalid Chat ID**:
   - Verify your chat ID is correct
   - For personal chat: positive number (e.g., `123456789`)
   - For group chat: negative number (e.g., `-123456789`)
   - Make sure you've started a conversation with the bot

3. **Bot Not Started**:
   - Go to Telegram
   - Find your bot
   - Click "Start" button
   - Send a test message

4. **Network Issues**:
   - Check your internet connection
   - Verify Telegram API is accessible
   - Check firewall settings

### Problem: "Telegram API error: Status 401"

**Solution:**
- This means your bot token is invalid
- Double-check the token from BotFather
- Make sure you copied the entire token (no spaces)

### Problem: "Telegram API error: Status 400"

**Solution:**
- This usually means the chat ID is invalid
- Verify you've started a conversation with the bot
- For groups, make sure the bot is added to the group

### Problem: No messages received

**Checklist:**
1. ✅ Bot token is set correctly
2. ✅ Chat ID is set correctly
3. ✅ You've started a conversation with the bot
4. ✅ Script is running and detecting alerts
5. ✅ Check script logs for error messages

### Problem: Messages delayed

**Solution:**
- This is normal - messages are sent when alerts are detected
- The script checks every hour (9:16, 10:16, etc.)
- Alerts are only sent when signals are detected
- If no alerts, no messages (this is expected)

## Security Best Practices

1. **Keep Bot Token Secret**:
   - Never commit bot token to GitHub
   - Don't share it publicly
   - Use environment variables (not hardcoded)

2. **Use Environment Variables**:
   - Always use environment variables for sensitive data
   - Never put tokens in code files
   - Use `.env` file for local development (and add to `.gitignore`)

3. **Rotate Tokens**:
   - If token is compromised, revoke it in BotFather
   - Create a new bot and update environment variables

4. **Limit Bot Access**:
   - Only share bot with trusted people
   - Use personal chat (not public groups) for sensitive alerts

## Advanced Configuration

### Sending to Multiple Chats

Currently, the script sends to one chat ID. To send to multiple chats:

1. **Create a Telegram group**
2. **Add all recipients to the group**
3. **Add your bot to the group**
4. **Use the group Chat ID** (negative number)

### Customizing Message Format

The message format is defined in `src/utils/telegram_notifier.py`. You can customize:
- Emojis used
- Message structure
- Information included

### Rate Limiting

Telegram has rate limits:
- **30 messages per second** per bot
- The script includes delays to avoid rate limiting
- If you send too many messages, Telegram may temporarily block your bot

## Testing Checklist

Before deploying to production:

- [ ] Bot created successfully
- [ ] Bot token copied correctly
- [ ] Chat ID obtained (personal or group)
- [ ] Environment variables set
- [ ] Test message sent manually (bot receives it)
- [ ] Script runs without errors
- [ ] Telegram notifications appear in chat
- [ ] Alerts formatted correctly
- [ ] Multiple alerts work (batch sending)

## Example Alert Message

When an alert is detected, you'll receive a message like this:

```
🟢 BREAKOUT - RELIANCE

⏰ Time: 2025-01-15 10:30:00
💰 Price: ₹2450.50
📊 Level: ₹2440.00 (ABOVE)
📈 Volume: 2.5x average
```

Or for breakdown:

```
🔴 BREAKDOWN - TCS

⏰ Time: 2025-01-15 11:45:00
💰 Price: ₹3450.25
📊 Level: ₹3460.00 (BELOW)
📈 Volume: 1.8x average
```

## Quick Reference

### Bot Token Format
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

### Chat ID Format
- **Personal Chat**: `123456789` (positive number)
- **Group Chat**: `-123456789` (negative number)

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Test Command
```bash
# Test locally
python scripts/run_realtime_alerts.py

# Test continuous
python scripts/run_continuous_alerts.py
```

## Support

If you encounter issues:

1. **Check BotFather**: Verify bot is active
2. **Check Chat ID**: Verify you've started conversation
3. **Check Logs**: Look for error messages in script output
4. **Test Manually**: Send a message to your bot in Telegram
5. **Verify Variables**: Ensure environment variables are set correctly

## Next Steps

After setting up Telegram:

1. ✅ Test notifications locally
2. ✅ Verify alerts are received
3. ✅ Deploy to cloud (Railway/Render/etc.)
4. ✅ Set environment variables in cloud platform
5. ✅ Monitor for alerts 24/7

---

**That's it!** You're now set up to receive instant Telegram notifications when stock alerts are detected. 🚀

