# Stock Selection UI - Summary

## ✅ What's Been Created

1. **`app.py`** - Main Streamlit UI application
2. **`run_ui.bat`** - Windows batch file to launch the UI
3. **`docs/UI_GUIDE.md`** - Complete user guide

## 🎯 Features Implemented

### ✅ All Parameters Configurable
- **Time Interval**: 1m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 1d
- **Lookback Swing**: Number of bars for swing high/low (default: 12)
- **Volume Window**: Number of bars for average volume (default: 70)
- **Volume Multiplier**: Volume spike threshold (default: 1.6)
- **Hold Bars**: Bars to hold for P&L (default: 3)
- **Historical Days**: Days of historical data (default: 30)
- **Max Workers**: Parallel workers (default: 10)

### ✅ Default Values Button
- Remembers all current system values
- Pre-populates all input fields when clicked
- Current defaults:
  - Interval: 1h
  - Lookback Swing: 12
  - Volume Window: 70
  - Volume Multiplier: 1.6
  - Hold Bars: 3
  - Historical Days: 30
  - Max Workers: 10

### ✅ Run Button
- Takes all values from UI
- Applies them to the stock selection logic
- **Does NOT change the core logic** - only applies parameters
- Displays results with download options

## 🔧 How It Works

1. **Parameter Override**: When you click "Run Analysis", the system:
   - Temporarily overrides `src.config.settings` module values
   - Runs the analysis with your UI parameters
   - Restores original settings after completion

2. **Stock Selection Logic**: **UNCHANGED**
   - Same breakout/breakdown detection
   - Same volume analysis
   - Same swing high/low calculation
   - Only the parameters are configurable

## 🚀 How to Use

### Quick Start
```bash
# Option 1: Use batch file
run_ui.bat

# Option 2: Direct command
streamlit run app.py
```

### Steps
1. Launch the UI (opens in browser)
2. Enter API credentials (or set environment variables)
3. Adjust parameters in sidebar (optional)
4. Click "🔄 Load Defaults" to reset to system defaults
5. Click "🚀 Run Analysis" to run
6. View results and download CSV files

## 📋 Current Default Values (System)

These are the values that get loaded when you click "Load Defaults":

| Parameter | Value | Description |
|-----------|-------|-------------|
| Time Interval | 1h | Hourly candles |
| Lookback Swing | 12 | Bars for swing calculation |
| Volume Window | 70 | Bars for volume average (10 days × 7 bars) |
| Volume Multiplier | 1.6 | 1.6× average volume threshold |
| Hold Bars | 3 | Hold for 3 bars for P&L |
| Historical Days | 30 | Fetch 30 days of data |
| Max Workers | 10 | 10 parallel workers |

## ⚠️ Important Notes

1. **Logic Unchanged**: The core stock selection algorithm is **exactly the same**. Only parameters are configurable.

2. **Settings Override**: Parameters are temporarily applied to the settings module during analysis, then restored.

3. **Session State**: Configuration persists during your Streamlit session.

4. **Default Values**: The "Load Defaults" button uses the current system configuration values from `src/config/settings.py`.

## 📁 Files Created

- `app.py` - Main UI application (Streamlit)
- `run_ui.bat` - Launch script for Windows
- `docs/UI_GUIDE.md` - Detailed user guide
- `UI_SUMMARY.md` - This file

## 🔄 Next Steps

1. Install Streamlit: `pip install streamlit` (already done)
2. Run the UI: `streamlit run app.py` or `run_ui.bat`
3. Test with default values
4. Adjust parameters as needed
5. Run analysis and review results

## ✨ UI Features

- **Sidebar Configuration**: All parameters in one place
- **Default Values Button**: One-click reset to system defaults
- **Save Config Button**: Save current configuration
- **Current Configuration Display**: See all current values
- **Results Display**: Tables with alerts and summary
- **CSV Download**: Download results for further analysis
- **Error Handling**: Clear error messages
- **Progress Indicators**: Visual feedback during analysis

