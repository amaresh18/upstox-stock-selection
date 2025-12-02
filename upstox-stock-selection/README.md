# Upstox Stock Selection System

A professional Python application for stock selection and alert generation using Upstox API v3. This tool analyzes Nifty 100 stocks to identify breakouts and breakdowns based on swing high/low, volume analysis, and candle patterns.

## Features

- **Swing High/Low Detection**: Calculates swing high and swing low using rolling windows
- **Volume Analysis**: Identifies volume spikes using volume ratio
- **Breakout/Breakdown Detection**: Detects price breakouts and breakdowns with volume confirmation
- **P&L Calculation**: Calculates hypothetical P&L for each signal
- **Parallel Processing**: Analyzes multiple symbols concurrently using asyncio
- **Statistics Aggregation**: Generates comprehensive statistics including win rate, profit factor, etc.
- **Hybrid Data Source**: Uses Yahoo Finance for historical data and Upstox API for current day data

## Requirements

1. **Python 3.8+**
2. **Upstox API Credentials**:
   - `UPSTOX_API_KEY`: Your Upstox API key
   - `UPSTOX_ACCESS_TOKEN`: Your Upstox access token

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd upstox-stock-selection
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get Upstox API Credentials

1. Log in to your Upstox account
2. Go to [Developer Dashboard](https://account.upstox.com/developer/apps)
3. Create an API application
4. Get your API key and generate an access token

## Quick Start

### 1. Set Environment Variables

**Windows PowerShell:**
```powershell
$env:UPSTOX_API_KEY='your_api_key'
$env:UPSTOX_ACCESS_TOKEN='your_access_token'
```

**Linux/Mac:**
```bash
export UPSTOX_API_KEY='your_api_key'
export UPSTOX_ACCESS_TOKEN='your_access_token'
```

### 2. Create NSE.json File (First Time Only)

Run the helper script to fetch instrument mappings:

```bash
python scripts/fetch_instruments.py
```

This creates `data/NSE.json` with all NSE equity instruments.

### 3. Run Stock Selection

```bash
python scripts/run_stock_selection.py
```

The script will:
- Check for credentials
- Create NSE.json if it doesn't exist
- Analyze all Nifty 100 symbols
- Display results and save to CSV files

## Usage

### Basic Usage

```bash
python scripts/run_stock_selection.py
```

### Backtesting

Run backtesting on historical data for the past week:

```bash
python scripts/run_backtest.py
```

This will:
- Backtest all Nifty 100 symbols for the past 7 days
- Calculate performance metrics (win rate, profit factor, etc.)
- Display detailed backtest results
- Save results to CSV files

#### Customize Backtest Period

You can customize the backtest period using environment variables:

```bash
# Backtest for past 14 days
$env:BACKTEST_DAYS='14'  # Windows PowerShell
export BACKTEST_DAYS='14'  # Linux/Mac
python scripts/run_backtest.py

# Backtest up to a specific date
$env:BACKTEST_END_DATE='2024-01-15'  # Windows PowerShell
export BACKTEST_END_DATE='2024-01-15'  # Linux/Mac
python scripts/run_backtest.py
```

### Save Results to CSV

By default, results are saved to CSV files. To disable:

```bash
$env:SAVE_CSV='false'  # Windows PowerShell
export SAVE_CSV='false'  # Linux/Mac
python scripts/run_stock_selection.py
```

This creates:
- `stock_selection_summary.csv` - Summary statistics per symbol
- `stock_selection_alerts.csv` - All alerts sorted by timestamp

### Telegram Notifications Setup (Optional)

To receive instant Telegram notifications when alerts are detected:

**📖 Detailed Guide**: See [Telegram Setup Guide](docs/TELEGRAM_SETUP.md) for complete step-by-step instructions.

**Quick Setup:**
1. **Create a Telegram Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow the instructions
   - Copy the bot token

2. **Get Your Chat ID:**
   - Search for `@userinfobot` on Telegram
   - Start a conversation to get your chat ID

3. **Set Environment Variables:**

   **Windows PowerShell:**
   ```powershell
   $env:TELEGRAM_BOT_TOKEN='your_bot_token'
   $env:TELEGRAM_CHAT_ID='your_chat_id'
   ```

   **Linux/Mac:**
   ```bash
   export TELEGRAM_BOT_TOKEN='your_bot_token'
   export TELEGRAM_CHAT_ID='your_chat_id'
   ```

4. **Test Notifications:**
   ```bash
   python scripts/run_realtime_alerts.py
   ```

**Note:** Telegram notifications are automatically enabled when both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set. If not set, the scripts will run normally without Telegram notifications.

### Continuous Monitoring Setup

**For Windows (Run at Startup):**

1. Create a batch file `start_alerts.bat`:
```batch
@echo off
cd /d "C:\Users\dell\Documents\Amaresh\Auto-trading-\upstox-stock-selection"
set UPSTOX_API_KEY=your_api_key
set UPSTOX_ACCESS_TOKEN=your_access_token
set TELEGRAM_BOT_TOKEN=your_bot_token
set TELEGRAM_CHAT_ID=your_chat_id
python scripts/run_continuous_alerts.py
pause
```

2. Add to Windows Startup:
   - Press `Win + R`, type `shell:startup`
   - Copy `start_alerts.bat` to the startup folder
   - The script will run automatically when Windows starts

**For Linux/Mac (Run as Service):**

Create a systemd service or use `screen`/`tmux`:
```bash
# Using screen
screen -S alerts
cd /path/to/project
export UPSTOX_API_KEY='your_api_key'
export UPSTOX_ACCESS_TOKEN='your_access_token'
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'
python scripts/run_continuous_alerts.py

# Detach: Press Ctrl+A then D
# Reattach: screen -r alerts
```

**How It Works:**
- Checks for alerts right after each hour completes (9:16, 10:16, 11:16, etc.)
- This ensures we check immediately after hourly candles are available
- Maximum delay: ~1-2 minutes after hour completes
- Sends Telegram notifications instantly when new alerts are detected

**Scheduling One-Time Alerts**

To automatically run alerts on a specific date (e.g., Nov 11, 2025):

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create a new task
3. Set trigger to "On a schedule" → "One time" → Nov 11, 2025 at 9:15 AM
4. Set action to run: `python scripts/run_realtime_alerts.py`
5. Set working directory to your project folder
6. Add environment variables in the task settings

**Linux/Mac Cron:**
```bash
# Edit crontab
crontab -e

# Add line to run at 9:15 AM on Nov 11, 2025
15 9 11 11 * cd /path/to/project && export TELEGRAM_BOT_TOKEN='token' && export TELEGRAM_CHAT_ID='id' && python scripts/run_realtime_alerts.py
```

### Advanced Configuration

You can customize the analysis using environment variables:

```bash
# Set custom NSE.json path
$env:NSE_JSON_PATH='data/NSE.json'

# Set number of parallel workers
$env:MAX_WORKERS='20'

# Set historical data days
$env:HISTORICAL_DAYS='60'

# Run analysis
python scripts/run_stock_selection.py
```

## Stock Selection Logic

### Indicators Calculated

1. **Swing High**: Rolling max of High over 12 bars * 0.995
2. **Swing Low**: Rolling min of Low over 12 bars * 1.005
3. **AvgVol10d**: Average volume over 70 bars (10 days * 7 bars/day)
4. **VolRatio**: Current Volume / AvgVol10d
5. **Range**: High - Low
6. **AvgRange**: Rolling mean of Range over 12 bars

### Breakout Signal

A breakout is detected when:
- Previous close was below Swing High
- Current close crosses above Swing High
- Volume spike (VolRatio >= 1.6)
- Strong bullish candle (Close > Open OR Range > AvgRange)

### Breakdown Signal

A breakdown is detected when:
- Previous close was above Swing Low
- Current close crosses below Swing Low
- Volume spike (VolRatio >= 1.6)
- Strong bearish candle (Close < Open OR Range > AvgRange)

### P&L Calculation

- **Entry**: Next bar's open price
- **Exit**: Close price after 3 bars
- **P&L %**: Calculated as percentage gain/loss

### Statistics Calculated

- **Trade Count**: Number of signals generated
- **Win Rate**: Percentage of profitable trades
- **Avg Gain %**: Average P&L percentage
- **Net P&L %**: Sum of all P&L percentages
- **Profit Factor**: Sum of winning trades / abs(sum of losing trades)

## Project Structure

```
upstox-stock-selection/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── stock_selector.py      # Main stock selection logic
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── instruments.py         # Instrument fetching utilities
│   │   └── symbols.py             # Symbol management utilities
│   └── config/
│       ├── __init__.py
│       └── settings.py            # Configuration settings
├── scripts/
│   ├── fetch_instruments.py       # Script to fetch instrument mappings
│   ├── run_stock_selection.py     # Main entry point script
│   └── run_backtest.py            # Backtesting script
├── data/
│   ├── NSE.json                    # Instrument mappings (generated)
│   ├── NSE.json.example            # Example template
│   └── nifty100_symbols.json     # Nifty 100 symbols (generated)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── .gitignore                      # Git ignore file
```

## Environment Variables

- `UPSTOX_API_KEY`: Your Upstox API key (required)
- `UPSTOX_ACCESS_TOKEN`: Your Upstox access token (required)
- `NSE_JSON_PATH`: Path to NSE.json file (optional, defaults to `data/NSE.json`)
- `SAVE_CSV`: Set to `'true'` to save results to CSV files (optional, default: `'true'`)
- `MAX_WORKERS`: Number of parallel workers (optional, default: `10`)
- `HISTORICAL_DAYS`: Number of days of historical data (optional, default: `30`)
- `BACKTEST_DAYS`: Number of days to backtest (optional, default: `7`)
- `BACKTEST_END_DATE`: End date for backtest in YYYY-MM-DD format (optional, default: today)
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (optional, for notifications)
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID (optional, for notifications)

## Nifty 100 Stocks Setup

The system is configured to work with Nifty 100 stocks. To set up Nifty 100 instruments:

### Quick Setup: Map from Upstox Excel File

If you have an Upstox instruments Excel file (e.g., `UpstocksNiftyMapping.csv.xlsx`), this is the fastest way to get all instrument keys:

```bash
python scripts/map_from_upstox_file.py
```

This will automatically map all 100 Nifty 100 instrument keys from the Excel file.

### Alternative: Fetch and Sync Nifty 100 Instruments

Run the sync script to:
1. Fetch official Nifty 100 list from NSE
2. Update NSE.json with all Nifty 100 symbols
3. Validate existing instrument keys
4. Add placeholders for missing instrument keys

```bash
python scripts/sync_nifty100_to_upstox.py
```

This script will:
- ✅ Fetch all 100 Nifty 100 symbols from NSE
- ✅ Validate existing instrument keys using Upstox API
- ✅ Update NSE.json to include all Nifty 100 symbols
- ✅ Add placeholders for symbols without instrument keys

### Check Nifty 100 Status

To check the current status of Nifty 100 symbols in NSE.json:

```bash
python scripts/check_nifty100_status.py
```

## Updating Instrument Keys

If you encounter "Invalid Instrument key" errors during backtesting, you need to update the instrument keys in `data/NSE.json`. 

### Option 1: Map from Upstox Excel File (Recommended)

If you have an Upstox instruments Excel file (e.g., `UpstocksNiftyMapping.csv.xlsx`), you can automatically map all instrument keys:

```bash
python scripts/map_from_upstox_file.py
```

This script will:
- ✅ Read the Excel file from the project root
- ✅ Automatically identify symbol and instrument_key columns
- ✅ Update `data/NSE.json` with all instrument keys
- ✅ Ensure all 100 Nifty 100 symbols have valid instrument keys

### Option 2: Manual Update

1. Get the correct instrument keys from Upstox API documentation or dashboard
2. Update `data/NSE.json` with the correct instrument keys for the failing symbols

### Option 3: Using Update Script

Try running the update script (note: this may fail if Upstox doesn't provide a public instruments endpoint):

```bash
python scripts/update_instrument_keys.py
```

### Option 4: Yahoo Finance Fallback

The system automatically falls back to Yahoo Finance for symbols with invalid instrument keys. This ensures backtesting continues even if some instrument keys are outdated.

## Troubleshooting

### Invalid Instrument Keys

If you see "Invalid Instrument key" errors for some symbols:

1. **Check the backtest summary**: The backtest will show which symbols have invalid instrument keys
2. **Update NSE.json**: Manually update the instrument keys for those symbols
3. **Yahoo Finance fallback**: The system will automatically use Yahoo Finance for symbols with invalid keys
4. **Run update script**: Try `python scripts/update_instrument_keys.py` (may not work if Upstox doesn't provide public endpoint)

### Data Fetching Issues

- **Upstox API errors**: Check your API credentials and ensure they're valid
- **Yahoo Finance failures**: May be due to network/firewall issues. The system will try both sources automatically
- **Insufficient data**: Ensure you're fetching at least 30 days of historical data for proper indicator calculations

## Troubleshooting

### Error: Instrument key not found
- Run `python scripts/fetch_instruments.py` to create NSE.json
- Check that your NSE.json file contains the symbol
- Verify the symbol name matches exactly

### Error: API authentication failed
- Verify your API_KEY and ACCESS_TOKEN are correct
- Check that your access token hasn't expired
- Ensure you have proper API permissions

### Error: Insufficient data
- The script needs at least 70 bars (1-hour candles) of data
- Check that the symbol has sufficient trading history
- Verify the date range covers at least 30 days

### Error: Timezone issues
- The script uses IST (Asia/Kolkata) timezone
- Ensure your system timezone is set correctly
- Upstox API returns timestamps in UTC, which are converted to IST

### Error: Module not found
- Make sure you're running scripts from the project root directory
- Verify that all dependencies are installed: `pip install -r requirements.txt`
- Check that the `src` directory is in the Python path

## Development

### Project Architecture

The project follows a modular architecture:

- **`src/core/`**: Core business logic (stock selection algorithm)
- **`src/utils/`**: Utility functions (instrument fetching, symbol management)
- **`src/config/`**: Configuration settings
- **`scripts/`**: Entry point scripts for end users
- **`data/`**: Data files (JSON mappings, CSV outputs)

### Adding New Features

1. Core logic should go in `src/core/`
2. Utility functions should go in `src/utils/`
3. Configuration should go in `src/config/settings.py`
4. Entry points should go in `scripts/`

## Notes

- The script uses 1-hour candles for analysis
- Historical data is fetched for the last 30 days (configurable)
- All calculations assume sufficient data (at least 70 bars)
- P&L calculations are hypothetical and for backtesting purposes only
- The system uses a hybrid approach: Yahoo Finance for historical data and Upstox API for current day data

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All functions have proper docstrings
- Tests are added for new features
- Documentation is updated

## Cloud Deployment

### 🚀 Streamlit Cloud (Recommended - FREE & Easiest for UI)

**Perfect for deploying the Streamlit UI app!**

**Quick Start:**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app" → Select your repo → Set main file: `app.py`
5. Add secrets (API credentials) in Settings → Secrets
6. Deploy! Your app will be live at `https://your-app.streamlit.app`

**Detailed Guide**: See [Streamlit Cloud Deployment Guide](STREAMLIT_CLOUD_DEPLOYMENT.md) for complete instructions.

**Quick Reference**: See [Streamlit Cloud Quick Start](STREAMLIT_CLOUD_QUICK_START.md) for a 5-minute setup.

### 📊 Other Deployment Options (For Scheduled Scripts)

Want to run scheduled alert scripts 24/7? See **[Cloud Deployment Guide](docs/CLOUD_DEPLOYMENT.md)** for deploying backend scripts to:
- **Railway** (Free tier available - for scheduled scripts)
- **Render** (Free tier available)
- **Fly.io** (Free tier available)
- **AWS EC2** (Free tier for 12 months)
- **Google Cloud Run** (Pay per use)
- **Heroku** (Paid - $7/month)

**Railway Guide**: See [Railway Deployment Guide](docs/RAILWAY_DEPLOYMENT.md) for step-by-step instructions (useful for running scheduled alert scripts).

**Note**: Streamlit Cloud is perfect for the interactive UI app. For 24/7 scheduled alert monitoring, Railway or other services are better suited.

## Support

For issues and questions, please open an issue on the repository.
