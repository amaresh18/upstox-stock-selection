# Stock Selection Logic Comparison

This document compares our implementation with the reference program to ensure exact matching.

## ✅ Fixed Differences

### 1. Rolling Window Calculations
**Reference:**
```python
df["SwingHigh"] = df["High"].rolling(LOOKBACK_SWING).max() * 0.995
df["SwingLow"] = df["Low"].rolling(LOOKBACK_SWING).min() * 1.005
df["AvgVol10d"] = df["Volume"].rolling(VOL_WINDOW).mean()
df["AvgRange"] = df["Range"].rolling(LOOKBACK_SWING).mean()
```

**Our Code (FIXED):**
```python
df['SwingHigh'] = df['high'].rolling(window=LOOKBACK_SWING).max() * 0.995
df['SwingLow'] = df['low'].rolling(window=LOOKBACK_SWING).min() * 1.005
df['AvgVol10d'] = df['volume'].rolling(window=VOL_WINDOW).mean()
df['AvgRange'] = df['Range'].rolling(window=LOOKBACK_SWING).mean()
```

**Status:** ✅ Fixed - Removed `min_periods` to match reference

### 2. Start Index Calculation
**Reference:**
```python
start_i = int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1
```

**Our Code (FIXED):**
```python
start_i = int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1
```

**Status:** ✅ Fixed - Added `int()` cast to match reference

## ✅ Already Matching

### 3. Swing High/Low Calculation
- ✅ Both use `0.995` multiplier for SwingHigh
- ✅ Both use `1.005` multiplier for SwingLow
- ✅ Both use `LOOKBACK_SWING = 12`

### 4. Volume Calculation
- ✅ Both use `VOL_WINDOW = 70` (10 days * 7 bars/day)
- ✅ Both calculate `VolRatio = Volume / AvgVol10d`
- ✅ Both use `VOL_MULT = 1.6` threshold

### 5. Range Calculation
- ✅ Both calculate `Range = High - Low`
- ✅ Both calculate `AvgRange = Range.rolling(LOOKBACK_SWING).mean()`

### 6. Strong Bull/Bear Logic
**Reference:**
```python
strong_bull = (cur_c > o) or (rng > arng if not np.isnan(arng) else False)
strong_bear = (cur_c < o) or (rng > arng if not np.isnan(arng) else False)
```

**Our Code:**
```python
strong_bull = (curr_close > curr_open) or (
    range_val > avg_range if not pd.isna(avg_range) else False
)
strong_bear = (curr_close < curr_open) or (
    range_val > avg_range if not pd.isna(avg_range) else False
)
```

**Status:** ✅ Already matching

### 7. Cross Detection
**Reference:**
```python
def crosses_above(prev_close, curr_close, level):
    return (prev_close <= level) and (curr_close > level)

def crosses_below(prev_close, curr_close, level):
    return (prev_close >= level) and (curr_close < level)
```

**Our Code:**
```python
crosses_above = (prev_close <= swing_high_prev) and (curr_close > swing_high_prev)
crosses_below = (prev_close >= swing_low_prev) and (curr_close < swing_low_prev)
```

**Status:** ✅ Already matching

### 8. Swing High/Low Usage
**Reference:**
```python
hh = df["SwingHigh"].iloc[i-1]  # use prev bar level
ll = df["SwingLow"].iloc[i-1]
```

**Our Code:**
```python
swing_high_prev = df['SwingHigh'].iloc[i-1]
swing_low_prev = df['SwingLow'].iloc[i-1]
```

**Status:** ✅ Already matching - Both use previous bar's swing high/low

### 9. Entry/Exit Logic
**Reference:**
```python
entry_t = df.index[i+1]
entry_p = df["Open"].iloc[i+1]
exit_t = df.index[i+HOLD_BARS]
exit_p = df["Close"].iloc[i+HOLD_BARS]
```

**Our Code:**
```python
entry_price = df['open'].iloc[i+1]
exit_price = df['close'].iloc[i+HOLD_BARS]
```

**Status:** ✅ Already matching

### 10. P&L Calculation
**Reference (Breakout):**
```python
pnl = (exit_p - entry_p) / entry_p * 100.0
```

**Reference (Breakdown):**
```python
pnl = (entry_p - exit_p) / entry_p * 100.0
```

**Our Code (Breakout):**
```python
pnl_pct = ((exit_price - entry_price) / entry_price) * 100.0
```

**Our Code (Breakdown):**
```python
pnl_pct = ((entry_price - exit_price) / entry_price) * 100.0
```

**Status:** ✅ Already matching

### 11. Loop Range
**Reference:**
```python
start_i = int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1
for i in range(start_i, len(df) - HOLD_BARS):
```

**Our Code:**
```python
start_i = int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1
end_i = len(df) - HOLD_BARS
for i in range(start_i, end_i):
```

**Status:** ✅ Already matching

### 12. Signal Conditions
**Reference (Breakout):**
```python
if crosses_above(prev_c, cur_c, hh) and (vr >= VOL_MULT) and strong_bull:
```

**Reference (Breakdown):**
```python
if crosses_below(prev_c, cur_c, ll) and (vr >= VOL_MULT) and strong_bear:
```

**Our Code (Breakout):**
```python
if crosses_above and (vol_ratio >= VOL_MULT) and strong_bull:
```

**Our Code (Breakdown):**
```python
if crosses_below and (vol_ratio >= VOL_MULT) and strong_bear:
```

**Status:** ✅ Already matching

## Summary

All critical logic now matches the reference program:
- ✅ Rolling window calculations (removed min_periods)
- ✅ Start index calculation (added int() cast)
- ✅ Swing high/low calculation
- ✅ Volume calculation
- ✅ Range calculation
- ✅ Strong bull/bear logic
- ✅ Cross detection
- ✅ Entry/exit logic
- ✅ P&L calculation
- ✅ Loop range
- ✅ Signal conditions

The implementation should now produce identical results to the reference program.

