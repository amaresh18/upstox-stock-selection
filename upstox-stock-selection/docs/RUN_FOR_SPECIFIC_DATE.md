# Running Alerts for a Specific Date

This guide explains how to run stock selection alerts for a specific date (e.g., November 10, 2025).

## Quick Start

### Method 1: Using Command Line Argument (Recommended)

```bash
python scripts/run_realtime_alerts.py --date 2025-11-10
```

### Method 2: Using Environment Variable

**Windows PowerShell:**
```powershell
$env:ALERT_DATE='2025-11-10'
python scripts/run_realtime_alerts.py
```

**Linux/Mac:**
```bash
export ALERT_DATE='2025-11-10'
python scripts/run_realtime_alerts.py
```

## Date Format

- **Format**: `YYYY-MM-DD`
- **Examples**:
  - `2025-11-10` (November 10, 2025)
  - `2025-11-11` (November 11, 2025)
  - `2025-01-15` (January 15, 2025)

## How It Works

When you specify a date:

1. **Fetches Historical Data**: Gets 30 days of historical data before the target date
2. **Fetches Target Date Data**: Gets all hourly candles for the specified date from Upstox API
3. **Analyzes Signals**: Runs the stock selection logic on the combined data
4. **Generates Alerts**: Detects breakout/breakdown signals for that date
5. **Sends Telegram Notifications**: Sends alerts to your Telegram (if configured)

## Example: Get Alerts for Nov 10, 2025

```bash
# Set your Upstox credentials
$env:UPSTOX_API_KEY='your_api_key'
$env:UPSTOX_ACCESS_TOKEN='your_access_token'

# Set Telegram credentials (optional)
$env:TELEGRAM_BOT_TOKEN='your_bot_token'
$env:TELEGRAM_CHAT_ID='your_chat_id'

# Run for Nov 10, 2025
python scripts/run_realtime_alerts.py --date 2025-11-10
```

## What You'll See

```
================================================================================
REAL-TIME STOCK SELECTION ALERTS
================================================================================

📅 Analyzing for date: Monday, November 10, 2025
   Using market close time: 2025-11-10 15:30:00 IST+05:30

✅ Market is open (9:15 AM - 3:30 PM IST)
   Current time: 15:30:00
   Fetching real-time data...

1. Checking credentials...
✅ Credentials found

2. Initializing stock selector...
✅ Loaded 100 symbols

4. Running real-time analysis...
================================================================================
STEP 1: Batch downloading historical data from Yahoo Finance
================================================================================
...

STEP 2: Analyzing symbols with Upstox current day data
================================================================================
Fetching data for 2025-11-10 from Upstox for RELIANCE...
Got 6 bars from Upstox for RELIANCE (2025-11-10)

...

🔔 NEW ALERTS DETECTED: 5 alerts
📱 Sending Telegram notifications...
   ✅ Sent 5 alert(s) to Telegram
```

## Telegram Notifications

If you've configured Telegram, you'll receive messages like:

```
🟢 BREAKOUT - RELIANCE

⏰ Time: 2025-11-10 10:30:00
💰 Price: ₹2450.50
📊 Level: ₹2440.00 (ABOVE)
📈 Volume: 2.5x average
```

## Important Notes

### 1. Date Must Be in the Past or Today

- **Past Dates**: Can analyze any past trading day
- **Today**: Can analyze current day
- **Future Dates**: Will fail (no data available)

### 2. Market Hours

- The script analyzes data for the entire trading day (9:15 AM - 3:30 PM IST)
- Even if you run it after market hours, it will fetch all hourly candles for that date

### 3. Weekend/Holiday Dates

- If the date is a weekend or holiday, the script will:
  - Show a warning
  - Still attempt to fetch data (may return empty)
  - Continue with analysis if data is available

### 4. Data Availability

- **Upstox API**: Provides data for past trading days
- **Yahoo Finance**: May not have data for very recent dates
- The script prioritizes Upstox API for specific dates

## Troubleshooting

### Problem: "No data available for symbol"

**Possible Causes:**
1. **Date is a holiday**: Markets were closed on that date
2. **Date is too far in the past**: Upstox API may not have data
3. **Invalid instrument key**: Symbol's instrument key may be outdated

**Solution:**
- Check if the date was a trading day
- Try a more recent date
- Update instrument keys using `scripts/sync_nifty100_to_upstox.py`

### Problem: "Invalid date format"

**Solution:**
- Use format: `YYYY-MM-DD` (e.g., `2025-11-10`)
- Don't use slashes or other formats
- Ensure date is valid (e.g., not `2025-13-40`)

### Problem: "No alerts generated"

**Possible Causes:**
1. **No signals met criteria**: No stocks had breakout/breakdown signals on that date
2. **Insufficient data**: Not enough historical data for calculations
3. **Market was closed**: No trading happened on that date

**Solution:**
- This is normal - not every day has alerts
- Check the CSV files for detailed results
- Try a different date

## Examples

### Analyze Yesterday's Data

```bash
# Get yesterday's date (Windows PowerShell)
$yesterday = (Get-Date).AddDays(-1).ToString('yyyy-MM-dd')
python scripts/run_realtime_alerts.py --date $yesterday
```

### Analyze Last Week's Data

```bash
# Get last Monday's date (Windows PowerShell)
$lastMonday = (Get-Date).AddDays(-(Get-Date).DayOfWeek.value__ - 6).ToString('yyyy-MM-dd')
python scripts/run_realtime_alerts.py --date $lastMonday
```

### Analyze Specific Date

```bash
# Analyze Nov 10, 2025
python scripts/run_realtime_alerts.py --date 2025-11-10
```

## Output Files

The script saves results to CSV files:

- **`stock_selection_summary.csv`**: Summary statistics per symbol
- **`stock_selection_alerts.csv`**: All alerts for the specified date

## Next Steps

1. ✅ Run the script for Nov 10, 2025
2. ✅ Check Telegram for notifications
3. ✅ Review CSV files for detailed results
4. ✅ Analyze the alerts and signals

---

**That's it!** You can now get alerts for any specific date. 🚀

