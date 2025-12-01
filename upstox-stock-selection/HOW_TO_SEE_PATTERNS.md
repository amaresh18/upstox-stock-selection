# How to See Pattern Matches in the UI

## Quick Fix for Not Seeing Patterns

The most common reason patterns don't show is the **time filter is too restrictive**.

### Solution 1: View All Patterns (Recommended)

1. **In the sidebar**, scroll to "Results Scope"
2. **Uncheck** ✅ "Show only selected recent closed candle"
3. **Check** ✅ "Include historical results (entire period)"
4. Click **"🚀 Run Analysis"** again

This will show **all patterns detected** across the entire analysis period, not just the selected candle.

### Solution 2: Check Pattern Detection is Enabled

1. **In the sidebar**, scroll to "Pattern Detection" section
2. Make sure the patterns you want are **checked** ✅:
   - ✅ RSI Bullish Divergence
   - ✅ RSI Bearish Divergence
   - ✅ Uptrend Retest
   - ✅ Downtrend Retest
   - ✅ Inverse Head and Shoulders
   - ✅ Double Bottom/Top
   - ✅ Triple Bottom/Top

### Solution 3: Try Different Time Intervals

Patterns may appear more frequently in certain intervals:

- **1h, 2h, 4h**: Good for most patterns
- **1d**: Best for reversal patterns (Head & Shoulders, Double/Triple patterns)
- **15m, 30m**: May have fewer patterns (too short timeframe)

### Solution 4: Check What's Being Displayed

After running analysis, look for:

1. **"🎯 Pattern Alerts"** section - This shows all detected patterns
2. **"📊 Breakout/Breakdown Alerts"** section - This shows regular signals

If you see "Pattern Alerts" section with 0 matches, it means:
- No patterns were detected with current settings
- Try different time intervals
- Try enabling "Include historical results"

## What Each Pattern Shows

When patterns are detected, you'll see:

- **Symbol**: Stock name
- **Pattern Type**: Which pattern was detected
- **Entry Price**: Recommended entry
- **Stop Loss**: Risk management level
- **Target Price**: Profit target
- **Volume Ratio**: Volume confirmation
- **Pattern-Specific Info**: 
  - RSI values for divergences
  - Neckline for reversal patterns
  - Retest levels for retest patterns

## Troubleshooting Checklist

- [ ] Pattern detection checkboxes are enabled in sidebar
- [ ] "Include historical results" is checked
- [ ] Analysis has completed (wait for spinner to finish)
- [ ] Using appropriate time interval (1h, 2h, 4h, or 1d recommended)
- [ ] Sufficient historical data (30+ days)
- [ ] Credentials are set correctly

## Still Not Seeing Patterns?

Patterns may genuinely not be present in the current market conditions. Try:

1. **Different time intervals** - Patterns form over different timeframes
2. **More historical data** - Increase "Historical Days" to 60 or 90
3. **Different symbols** - Some stocks may not have patterns forming
4. **Check the CSV download** - Patterns might be in the data but filtered by UI

The patterns are detected using strict criteria to ensure reliability, so fewer false signals means fewer but higher-quality patterns.

