# Stock Selection UI Guide

## Overview

The Streamlit UI provides an interactive interface to configure and run the Upstox Stock Selection System. You can adjust all parameters without modifying code.

## Running the UI

### Option 1: Using the batch file (Windows)
```bash
run_ui.bat
```

### Option 2: Using Streamlit directly
```bash
streamlit run app.py
```

The UI will open in your default web browser at `http://localhost:8501`

## Features

### 1. Configuration Panel (Sidebar)

All parameters can be adjusted in the sidebar:

#### Time Interval
- **Options**: 1m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 1d
- **Default**: 1h
- **Description**: Candle interval for analysis

#### Lookback Swing (Bars)
- **Default**: 12
- **Description**: Number of bars for swing high/low calculation

#### Volume Window (Bars)
- **Default**: 70
- **Description**: Number of bars for average volume calculation
- **Note**: For 1h candles, 70 bars = 10 days × 7 bars/day

#### Volume Multiplier
- **Default**: 1.6
- **Description**: Volume spike threshold (e.g., 1.6 = 1.6× average volume)

#### Hold Bars
- **Default**: 3
- **Description**: Number of bars to hold position for P&L calculation

#### Historical Days
- **Default**: 30
- **Description**: Number of days of historical data to fetch

#### Max Workers (Parallel)
- **Default**: 10
- **Description**: Number of parallel workers for analysis

### 2. Buttons

#### 🔄 Load Defaults
- Resets all parameters to the system's default values
- Current default values:
  - Time Interval: 1h
  - Lookback Swing: 12
  - Volume Window: 70
  - Volume Multiplier: 1.6
  - Hold Bars: 3
  - Historical Days: 30
  - Max Workers: 10

#### 💾 Save Config
- Saves current configuration to session state
- Configuration persists during the session

### 3. API Credentials

Enter your Upstox API credentials:
- **API Key**: Your Upstox API Key
- **Access Token**: Your Upstox Access Token

**Note**: Credentials can also be set via environment variables:
- `UPSTOX_API_KEY`
- `UPSTOX_ACCESS_TOKEN`

### 4. Run Analysis

Click the **🚀 Run Analysis** button to:
1. Load symbols from `data/NSE.json`
2. Apply your configured parameters
3. Run the stock selection analysis
4. Display results

### 5. Results Display

After analysis completes, you'll see:

#### Summary Statistics
- Total symbols analyzed
- Total trades
- Total alerts
- Average win rate

#### Alerts Table
- All detected breakout/breakdown signals
- Entry/exit prices
- P&L percentages
- Volume ratios

#### Summary Table
- Per-symbol statistics
- Trade counts
- Win rates
- Profit factors

#### Download Options
- Download alerts as CSV
- Download summary as CSV

## Important Notes

1. **Stock Selection Logic**: The core stock selection logic is **NOT changed**. Only the parameters are made configurable.

2. **Default Values**: The default values match the current system configuration:
   - `LOOKBACK_SWING = 12`
   - `VOL_WINDOW = 70`
   - `VOL_MULT = 1.6`
   - `HOLD_BARS = 3`
   - `DEFAULT_INTERVAL = "1h"`
   - `DEFAULT_HISTORICAL_DAYS = 30`
   - `DEFAULT_MAX_WORKERS = 10`

3. **Parameter Override**: When you click "Run Analysis", the system temporarily overrides the settings module values with your UI inputs, runs the analysis, then restores the original values.

4. **Session State**: Your configuration is saved in Streamlit's session state, so it persists during your session.

## Troubleshooting

### UI doesn't start
- Make sure Streamlit is installed: `pip install streamlit`
- Check that `app.py` is in the project root

### No symbols found
- Ensure `data/NSE.json` exists and contains valid instrument mappings
- Run `scripts/sync_nifty100_to_upstox.py` to populate instrument keys

### API errors
- Verify your API credentials are correct
- Check that your access token hasn't expired
- Ensure you have internet connectivity

### Analysis takes too long
- Reduce the number of symbols (filter `NSE.json`)
- Reduce `Historical Days`
- Reduce `Max Workers` (though this may slow things down)

## Example Workflow

1. Open the UI: `streamlit run app.py`
2. Enter your API credentials
3. (Optional) Adjust parameters in the sidebar
4. Click "🔄 Load Defaults" to reset to system defaults
5. Click "🚀 Run Analysis"
6. Review results in the main panel
7. Download results as CSV if needed

