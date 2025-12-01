# Quick Pattern Analysis Guide

## Option 1: Using Streamlit UI (Recommended)

The easiest way to see pattern matches with various time filters is through the Streamlit UI:

```bash
streamlit run app.py
```

### Steps:
1. **Set Credentials** (if not already set):
   ```powershell
   $env:UPSTOX_API_KEY='your_api_key'
   $env:UPSTOX_ACCESS_TOKEN='your_access_token'
   ```

2. **Launch UI**:
   ```bash
   streamlit run app.py
   ```

3. **Configure Pattern Detection**:
   - In the sidebar, go to "Pattern Detection" section
   - Enable the patterns you want to detect:
     - ✅ RSI Bullish Divergence
     - ✅ RSI Bearish Divergence
     - ✅ Uptrend Retest
     - ✅ Downtrend Retest
     - ✅ Inverse Head and Shoulders
     - ✅ Double Bottom/Top
     - ✅ Triple Bottom/Top

4. **Set Time Interval**:
   - Select from: 1m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 1d
   - Different intervals will show different pattern matches

5. **Run Analysis**:
   - Click "🚀 Run Analysis"
   - Results will show pattern matches with:
     - Symbol name
     - Pattern type
     - Entry price
     - Stop loss
     - Target price
     - Volume confirmation

## Option 2: Using CLI Script

```bash
# Set credentials first
$env:UPSTOX_API_KEY='your_api_key'
$env:UPSTOX_ACCESS_TOKEN='your_access_token'

# Run pattern analysis with multiple intervals
python scripts/run_pattern_analysis.py
```

This will analyze stocks across multiple time intervals (15m, 30m, 1h, 2h, 4h, 1d) and show pattern matches for each.

## Pattern Types Detected

1. **RSI Bullish Divergence**: Price makes lower lows, RSI makes higher lows
2. **RSI Bearish Divergence**: Price makes higher highs, RSI makes lower highs
3. **Uptrend Retest**: Price breaks resistance, retests, then bounces
4. **Downtrend Retest**: Price breaks support, retests, then rejects
5. **Inverse Head and Shoulders**: Bullish reversal with 3 troughs
6. **Double Bottom**: Bullish reversal with 2 similar troughs
7. **Double Top**: Bearish reversal with 2 similar peaks
8. **Triple Bottom**: Strong bullish reversal with 3 similar troughs
9. **Triple Top**: Strong bearish reversal with 3 similar peaks

## Time Filter Notes

- **Shorter intervals (15m, 30m)**: More signals, faster patterns, higher noise
- **Medium intervals (1h, 2h)**: Balanced signals, good for day trading
- **Longer intervals (4h, 1d)**: Fewer but stronger signals, better for swing trading

Each interval will show different pattern matches based on the timeframe's characteristics.

