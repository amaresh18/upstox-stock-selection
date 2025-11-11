# Stock Selection Logic Verification

This document verifies that our implementation matches the reference program exactly.

## Reference Program Logic

```python
# Swing levels
df["SwingHigh"] = df["High"].rolling(LOOKBACK_SWING).max() * 0.995
df["SwingLow"] = df["Low"].rolling(LOOKBACK_SWING).min() * 1.005

# Volume analysis
df["AvgVol10d"] = df["Volume"].rolling(VOL_WINDOW).mean()
df["VolRatio"] = df["Volume"] / df["AvgVol10d"]

# Range analysis
df["Range"] = df["High"] - df["Low"]
df["AvgRange"] = df["Range"].rolling(LOOKBACK_SWING).mean()

# Start index
start_i = int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1

# Signal detection loop
for i in range(start_i, len(df) - HOLD_BARS):
    prev_c = df["Close"].iloc[i-1]
    cur_c = df["Close"].iloc[i]
    hh = df["SwingHigh"].iloc[i-1]  # PREVIOUS bar's swing high
    ll = df["SwingLow"].iloc[i-1]   # PREVIOUS bar's swing low
    vr = df["VolRatio"].iloc[i]
    rng = df["Range"].iloc[i]
    arng = df["AvgRange"].iloc[i]
    o = df["Open"].iloc[i]
    
    strong_bull = (cur_c > o) or (rng > arng if not np.isnan(arng) else False)
    strong_bear = (cur_c < o) or (rng > arng if not np.isnan(arng) else False)
    
    crosses_above = (prev_c <= hh) and (cur_c > hh)
    crosses_below = (prev_c >= ll) and (cur_c < ll)
    
    # Breakout
    if crosses_above and (vr >= VOL_MULT) and strong_bull:
        # Generate alert
    
    # Breakdown
    if crosses_below and (vr >= VOL_MULT) and strong_bear:
        # Generate alert
```

## Our Implementation Verification

### ✅ Indicator Calculations (src/core/stock_selector.py:577-609)

| Reference | Our Implementation | Match |
|-----------|-------------------|-------|
| `df["SwingHigh"] = df["High"].rolling(LOOKBACK_SWING).max() * 0.995` | `df['SwingHigh'] = df['high'].rolling(window=LOOKBACK_SWING).max() * 0.995` | ✅ |
| `df["SwingLow"] = df["Low"].rolling(LOOKBACK_SWING).min() * 1.005` | `df['SwingLow'] = df['low'].rolling(window=LOOKBACK_SWING).min() * 1.005` | ✅ |
| `df["AvgVol10d"] = df["Volume"].rolling(VOL_WINDOW).mean()` | `df['AvgVol10d'] = df['volume'].rolling(window=VOL_WINDOW).mean()` | ✅ |
| `df["VolRatio"] = df["Volume"] / df["AvgVol10d"]` | `df['VolRatio'] = df['volume'] / df['AvgVol10d']` | ✅ |
| `df["Range"] = df["High"] - df["Low"]` | `df['Range'] = df['high'] - df['low']` | ✅ |
| `df["AvgRange"] = df["Range"].rolling(LOOKBACK_SWING).mean()` | `df['AvgRange'] = df['Range'].rolling(window=LOOKBACK_SWING).mean()` | ✅ |

### ✅ Start Index (src/core/stock_selector.py:631)

| Reference | Our Implementation | Match |
|-----------|-------------------|-------|
| `start_i = int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1` | `start_i = int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1` | ✅ |

### ✅ Signal Detection (src/core/stock_selector.py:644-676)

| Reference | Our Implementation | Match |
|-----------|-------------------|-------|
| `prev_c = df["Close"].iloc[i-1]` | `prev_close = df['close'].iloc[i-1]` | ✅ |
| `cur_c = df["Close"].iloc[i]` | `curr_close = df['close'].iloc[i]` | ✅ |
| `hh = df["SwingHigh"].iloc[i-1]` | `swing_high_prev = df['SwingHigh'].iloc[i-1]` | ✅ |
| `ll = df["SwingLow"].iloc[i-1]` | `swing_low_prev = df['SwingLow'].iloc[i-1]` | ✅ |
| `vr = df["VolRatio"].iloc[i]` | `vol_ratio = df['VolRatio'].iloc[i]` | ✅ |
| `rng = df["Range"].iloc[i]` | `range_val = df['Range'].iloc[i]` | ✅ |
| `arng = df["AvgRange"].iloc[i]` | `avg_range = df['AvgRange'].iloc[i]` | ✅ |
| `o = df["Open"].iloc[i]` | `curr_open = df['open'].iloc[i]` | ✅ |

### ✅ Strong Candle Logic (src/core/stock_selector.py:668-676)

| Reference | Our Implementation | Match |
|-----------|-------------------|-------|
| `strong_bull = (cur_c > o) or (rng > arng if not np.isnan(arng) else False)` | `strong_bull = (curr_close > curr_open) or (range_val > avg_range if not pd.isna(avg_range) else False)` | ✅ |
| `strong_bear = (cur_c < o) or (rng > arng if not np.isnan(arng) else False)` | `strong_bear = (curr_close < curr_open) or (range_val > avg_range if not pd.isna(avg_range) else False)` | ✅ |

### ✅ Cross Detection (src/core/stock_selector.py:679, 728)

| Reference | Our Implementation | Match |
|-----------|-------------------|-------|
| `crosses_above = (prev_c <= hh) and (cur_c > hh)` | `crosses_above = (prev_close <= swing_high_prev) and (curr_close > swing_high_prev)` | ✅ |
| `crosses_below = (prev_c >= ll) and (cur_c < ll)` | `crosses_below = (prev_close >= swing_low_prev) and (curr_close < swing_low_prev)` | ✅ |

### ⚠️ Volume Threshold (MODIFICATION FOR REAL-TIME ALERTS)

| Reference | Our Implementation | Note |
|-----------|-------------------|------|
| `vr >= VOL_MULT` (always 1.6x) | `vol_ratio >= vol_threshold_breakout` | For real-time alerts on current bar, uses 1.2x (75% of 1.6x) to catch signals on incomplete candles. For backtesting, uses 1.6x as per reference. |

## Configuration Values

| Parameter | Reference | Our Implementation | Match |
|-----------|-----------|-------------------|-------|
| `LOOKBACK_SWING` | 12 | 12 | ✅ |
| `VOL_WINDOW` | 70 (10 * 7) | 70 | ✅ |
| `VOL_MULT` | 1.6 | 1.6 | ✅ |
| `HOLD_BARS` | 3 | 3 | ✅ |

## Summary

✅ **All core logic matches the reference program exactly**

The only modification is:
- **Real-time alerts**: Uses 1.2x volume threshold (instead of 1.6x) for the current/last bar to catch signals on incomplete candles
- **Backtesting**: Uses 1.6x volume threshold exactly as per reference program

This modification is intentional and documented to handle real-time scenarios where the current hour's candle volume is still accumulating.

