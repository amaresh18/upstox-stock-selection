# 15-Minute Volume Spike Alert Feature

## Overview

This feature adds an **additional alert system** to catch stocks quickly within 15 minutes by detecting volume spikes. It works alongside the existing breakout/breakdown alert system.

## How It Works

### Logic
1. **Fetches 15-minute candle data** for the current trading day
2. **Fetches 1-hour candle data** for the past 70 candles (approximately 3 days of trading data)
3. **Calculates average volume** of past 70 1-hour candles
4. **Compares current 15-minute candle volume** with the average
5. **Triggers alert** if: `15-minute volume >= average of past 70 1-hour candles`

### Example
- Past 70 1-hour candles average volume: **1000 quantity**
- Current 15-minute candle volume: **1200 quantity**
- **Alert triggered** ✅ (1200 >= 1000)

## Alert Details

### Alert Type
- **Signal Type**: `VOLUME_SPIKE_15M`
- **Alert Source**: `15min_volume_comparison`

### Alert Data
- `symbol`: Stock symbol
- `timestamp`: Alert timestamp
- `price`: Current price
- `current_15m_volume`: Volume of the 15-minute candle
- `avg_1h_volume`: Average volume of past 70 1-hour candles
- `vol_ratio`: Ratio of 15m volume to avg 1h volume
- `alert_source`: "15min_volume_comparison"

## UI Display

### Visual Styling
- **Badge Color**: Blue (#2196F3) - Different from breakout (green) and breakdown (red)
- **Badge Text**: "VOLUME SPIKE 15M"
- **Alert Class**: `kite-alert-primary`

### Display Information
- Stock symbol
- Price
- Volume ratio (15m / avg 1h)
- 15-minute volume
- Average 1-hour volume
- Timestamp

## Integration

### Where It's Called
- Integrated into `_analyze_symbol()` method
- Runs **in addition to** existing breakout/breakdown alerts
- Both alert types are combined and returned together

### Code Flow
```
_analyze_symbol()
  ├── _detect_signals() → Existing breakout/breakdown alerts
  ├── _detect_15min_volume_alerts() → New 15-minute volume alerts
  └── Combine both alert types
```

## Benefits

1. **Faster Detection**: Catches volume spikes within 15 minutes instead of waiting for hourly candles
2. **Early Entry**: Allows traders to enter positions earlier when momentum is building
3. **Additional Signal**: Works alongside existing alerts, providing more opportunities
4. **Volume-Based**: Focuses purely on volume spikes, independent of price breakouts

## Technical Details

### Data Fetching
- **15-minute data**: Fetched from Upstox API for current day
- **1-hour data**: Fetched from Upstox API for past 5 days (ensures at least 70 candles)
- Uses dedicated interval parameter in `_fetch_historical_data()`

### Comparison Logic
- Uses **last 70 1-hour candles** (excluding the most recent incomplete candle)
- Compares with **most recent completed 15-minute candle**
- Simple comparison: `current_15m_volume >= avg_1h_volume`

### Performance
- Runs in parallel with existing analysis
- Minimal overhead (one additional API call per symbol)
- Efficient volume calculation using NumPy

## Usage

The feature is **automatically enabled** and runs alongside existing alerts. No configuration needed!

### When Alerts Are Generated
- During regular analysis runs
- For each symbol analyzed
- Only if 15-minute volume >= average of past 70 1-hour candles

### Alert Display
- Shown in the same alert list as breakout/breakdown alerts
- Clearly marked with "VOLUME SPIKE 15M" badge
- Includes all relevant volume and price information

## Future Enhancements (Optional)

1. **Configurable Threshold**: Allow users to set custom volume multiplier
2. **Time Filter**: Only check during specific market hours (e.g., 9:15 AM - 11:00 AM)
3. **Price Direction**: Add price direction filter (only alert on up moves, down moves, or both)
4. **Multiple Intervals**: Support for 5-minute, 10-minute comparisons
5. **Volume Profile**: Compare against volume profile instead of simple average

## Notes

- This is an **additional alert system** - existing alerts continue to work as before
- Volume spike alerts are **independent** of breakout/breakdown alerts
- Both alert types can trigger for the same symbol at different times
- The system is designed to catch **early momentum** before it becomes a full breakout

