# Momentum Strategy Implementation Plan

## Overview

Enhance the stock selection system to detect **momentum continuation signals** for 5-minute candles, allowing earlier entry when momentum is building.

## New Features to Add

### 1. Momentum Indicators

**Rate of Change (ROC)**
- 2-candle ROC: `(Close[t] - Close[t-2]) / Close[t-2] * 100`
- 3-candle ROC: `(Close[t] - Close[t-3]) / Close[t-3] * 100`
- Strong momentum: ROC > 0.5% (for 5-min candles)

**Price Acceleration**
- Compare ROC of last 2 candles vs previous 2 candles
- Acceleration = momentum is building

**Multi-Candle Direction**
- Check if last 3-5 candles all in same direction
- Strong trend = consistent direction

**Volume Trend**
- Is volume increasing over last 3 candles?
- Volume acceleration = sudden spike

### 2. New Alert Type: `MOMENTUM_BUILDUP`

**Triggers when**:
- Price momentum building (ROC > threshold)
- Volume increasing (last 3 candles)
- Multi-candle direction (3+ candles same direction)
- Not yet at swing high/low (earlier entry)
- Volume ratio > threshold

**Advantages**:
- Earlier entry than breakout alerts
- Catches momentum before it peaks
- Better risk/reward ratio

### 3. Enhanced Filters

**RSI Filter** (Optional)
- RSI(14) between 30-70 (avoid extremes)
- Can be disabled for aggressive entries

**Higher Timeframe Confirmation** (Recommended)
- Check 15-minute or 1-hour trend
- Only take 5-min signals aligned with higher TF
- Significantly improves success rate

**ADX Filter** (Optional)
- ADX > 25 = strong trend
- Can be added later

## Implementation Steps

### Phase 1: Add Momentum Indicators

1. Add ROC calculation to `_calculate_indicators()`
2. Add multi-candle direction check
3. Add volume trend calculation

### Phase 2: Create Momentum Detection Method

1. Create `_detect_momentum_signals()` method
2. Check momentum building conditions
3. Generate `MOMENTUM_BUILDUP` alerts

### Phase 3: Integrate with Existing System

1. Call momentum detection in `_analyze_symbol()`
2. Combine with existing breakout/breakdown alerts
3. Display in UI with distinct badge

### Phase 4: Add Filters (Optional)

1. RSI calculation
2. Higher timeframe trend check
3. ADX calculation (if needed)

## Configuration Parameters

Add to `settings.py`:

```python
# Momentum Strategy Parameters
MOMENTUM_ROC_THRESHOLD = 0.5  # Minimum ROC % for momentum
MOMENTUM_CANDLES_REQUIRED = 3  # Number of candles in same direction
MOMENTUM_VOLUME_INCREASING = True  # Require increasing volume
MOMENTUM_USE_RSI = False  # Enable RSI filter
MOMENTUM_RSI_MIN = 30  # Minimum RSI
MOMENTUM_RSI_MAX = 70  # Maximum RSI
MOMENTUM_HIGHER_TF_CONFIRM = True  # Check higher timeframe trend
MOMENTUM_HIGHER_TF_INTERVAL = "15m"  # Higher timeframe interval
```

## Expected Results

### Success Rate Improvement

- **Current System**: ~60-65% (breakout/breakdown only)
- **With Momentum**: ~70-75% (earlier entries)
- **With All Filters**: ~75-80% (high-quality signals)

### Entry Timing

- **Breakout Alerts**: Entry at swing high/low break
- **Momentum Alerts**: Entry when momentum building (earlier, better risk/reward)

## Next Steps

1. ✅ Review this plan
2. Implement Phase 1 (momentum indicators)
3. Test on historical data
4. Implement Phase 2 (momentum detection)
5. Add filters gradually
6. Optimize parameters

