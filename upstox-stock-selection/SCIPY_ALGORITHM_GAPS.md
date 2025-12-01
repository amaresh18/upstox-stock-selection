# Missing Features in Scipy Algorithm vs. Trading Guidelines

## Overview

The `scipy.signal.find_peaks` algorithm is excellent for **finding peaks and troughs**, but it **does NOT validate trading pattern requirements** according to Capital.com and Investopedia guidelines. This document lists what's missing.

---

## What Scipy `find_peaks` Does

✅ **Finds local peaks/troughs** using:
- `distance`: Minimum distance between peaks
- `prominence`: How much a peak stands out from baseline
- `width`: Minimum peak width

❌ **Does NOT check** any trading-specific requirements

---

## Missing Features (Per Capital.com & Investopedia Guidelines)

### 1. **Volume Analysis** ❌

**What's Missing:**
- ❌ Volume trend during pattern formation
- ❌ Volume decline on second peak (Double Top pattern)
- ❌ Volume increase on first peak, decrease on second (Double Top)
- ❌ Volume increase during pattern formation (Double/Triple Bottom)
- ❌ Volume spike on neckline breakout/breakdown
- ❌ Volume confirmation for pattern validity

**Guidelines:**
- **Double Top**: Second peak should have **lower volume** than first (weakening buying pressure)
- **Double Bottom**: Volume should **increase** as price rises after second bottom
- **Triple Top**: Volume should **decrease** with each successive peak
- **Triple Bottom**: Volume should **increase** on breakout above neckline
- **Break-Retest**: Volume should **spike** on breakout and retest

**Current Status:** ✅ Partially implemented in pattern detector, but scipy doesn't check this

---

### 2. **RSI Confirmation** ❌

**What's Missing:**
- ❌ RSI overbought (>70) for bearish patterns (Double/Triple Top)
- ❌ RSI oversold (<30) for bullish patterns (Double/Triple Bottom)
- ❌ RSI divergence confirmation
- ❌ RSI trend alignment with pattern

**Guidelines:**
- **Double/Triple Top**: Should occur when RSI is **overbought (>70)**
- **Double/Triple Bottom**: Should occur when RSI is **oversold (<30)**
- **RSI Divergence**: Price and RSI moving in opposite directions

**Current Status:** ✅ Implemented as optional filter in UI, but scipy doesn't check this

---

### 3. **Candlestick Reversal Patterns** ❌

**What's Missing:**
- ❌ Doji pattern detection
- ❌ Hammer pattern detection
- ❌ Shooting star pattern detection
- ❌ Engulfing pattern detection
- ❌ Pin bar detection
- ❌ Reversal confirmation at key levels

**Guidelines:**
- **Break-Retest**: Should have **reversal candlestick** (hammer, doji, pin bar) at retest level
- **Double/Triple Patterns**: Reversal candles at pattern completion points
- **Inverse H&S**: Reversal confirmation at neckline breakout

**Current Status:** ✅ Partially implemented in retest patterns, but scipy doesn't check this

---

### 4. **Peak/Trough Symmetry** ❌

**What's Missing:**
- ❌ Symmetry validation (peaks/troughs at similar levels)
- ❌ Price level tolerance checking (within 2% for double/triple patterns)
- ❌ Pattern structure validation

**Guidelines:**
- **Double Top**: Both peaks should be within **2%** of each other
- **Double Bottom**: Both troughs should be within **2%** of each other
- **Triple Patterns**: All three points should be at similar levels
- **Inverse H&S**: Shoulders should be at similar levels, head lower

**Current Status:** ✅ Implemented in pattern detector, but scipy doesn't validate this

---

### 5. **Time Duration Validation** ❌

**What's Missing:**
- ❌ Minimum time between pattern formation points
- ❌ Pattern maturity validation
- ❌ Time span checking (patterns shouldn't form too quickly)

**Guidelines:**
- **Retest Patterns**: At least **3-5 bars** between breakout and retest
- **Double Patterns**: At least **5-10 bars** between first and second point
- **Triple Patterns**: At least **5-10 bars** between each point
- **Inverse H&S**: At least **10-20 bars** between shoulders

**Current Status:** ✅ Implemented as optional filter in UI, but scipy doesn't check this

---

### 6. **Neckline Breakout Confirmation** ❌

**What's Missing:**
- ❌ Neckline level identification
- ❌ Breakout/breakdown confirmation
- ❌ Volume spike on neckline break
- ❌ Price target projection from neckline

**Guidelines:**
- **Double/Triple Patterns**: Must break **neckline** with **volume** to confirm
- **Inverse H&S**: Must break **above neckline** with **volume** to confirm
- **Price Target**: Project pattern height from neckline breakout

**Current Status:** ✅ Implemented in pattern detector, but scipy doesn't check this

---

### 7. **Retest Validation** ❌

**What's Missing:**
- ❌ Retest tolerance checking (price must retest within 1-2%)
- ❌ Retest without breaching level
- ❌ Reversal confirmation at retest

**Guidelines:**
- **Break-Retest**: Price must retest level within **1-2% tolerance**
- **Retest**: Price should **not breach** the level (support/resistance holds)
- **Reversal**: Must have **reversal candlestick** at retest

**Current Status:** ✅ Implemented in pattern detector, but scipy doesn't check this

---

### 8. **Pattern Structure Validation** ❌

**What's Missing:**
- ❌ Pattern sequence validation (breakout → retest → reversal)
- ❌ Pattern completion confirmation
- ❌ Multiple point alignment checking

**Guidelines:**
- **Break-Retest**: Must follow sequence: **Breakout → Retest → Reversal**
- **Double/Triple**: Must have proper structure (two/three points + neckline)
- **Inverse H&S**: Must have left shoulder → head → right shoulder structure

**Current Status:** ✅ Implemented in pattern detector, but scipy doesn't validate this

---

### 9. **Risk-to-Reward Calculation** ❌

**What's Missing:**
- ❌ Entry price calculation
- ❌ Stop loss placement
- ❌ Target price projection
- ❌ Risk-to-reward ratio validation

**Guidelines:**
- **Entry**: Above reversal candle high (bullish) or below reversal candle low (bearish)
- **Stop Loss**: Below pattern AND broken level (bullish) or above pattern AND broken level (bearish)
- **Target**: Typically **2:1 risk-to-reward ratio**

**Current Status:** ✅ Implemented in pattern detector, but scipy doesn't calculate this

---

### 10. **Momentum Validation** ❌

**What's Missing:**
- ❌ Price momentum during breakout
- ❌ Momentum comparison (breakout vs. pullback)
- ❌ Trend alignment

**Guidelines:**
- **Break-Retest**: Breakout momentum should be **stronger** than pullback momentum
- **Patterns**: Should align with overall trend direction

**Current Status:** ✅ Partially implemented in retest patterns, but scipy doesn't check this

---

## Summary

### What Scipy Does Well ✅
- Finds peaks and troughs reliably
- Filters noise using prominence and distance
- Handles edge cases (NaN values, insufficient data)

### What Scipy Doesn't Do ❌
- **Volume analysis** (trends, spikes, confirmation)
- **RSI validation** (overbought/oversold conditions)
- **Candlestick patterns** (reversal confirmation)
- **Symmetry validation** (price level matching)
- **Time duration** (pattern maturity)
- **Neckline breakout** (confirmation with volume)
- **Retest validation** (tolerance, no breach)
- **Pattern structure** (sequence, completion)
- **Risk management** (entry, stop, target)
- **Momentum validation** (trend alignment)

---

## Current Implementation Status

### ✅ Implemented in Pattern Detector
- Volume confirmation (partial)
- Peak/trough symmetry
- Neckline breakout
- Retest validation
- Risk-to-reward calculation
- Pattern structure validation

### ✅ Implemented as Optional Filters in UI
- Volume confirmation (checkbox)
- Volume spike on breakout (checkbox)
- RSI overbought/oversold (checkbox)
- Candlestick reversal (checkbox) - **Now implemented**
- Peak symmetry (checkbox)
- Time duration (checkbox) - **Now implemented**
- Retest tolerance (checkbox)
- Retest no breach (checkbox)

### ✅ Now Implemented (All Metrics Functional)
- ✅ Volume trend analysis during pattern formation
- ✅ Advanced candlestick pattern detection (doji, hammer, engulfing, etc.)
- ✅ RSI divergence detection (fully implemented with confirmation)
- ✅ Momentum trend alignment

---

## Conclusion

**Scipy `find_peaks` is a tool for finding peaks/troughs, NOT for validating trading patterns.**

The pattern detector implements most requirements from Capital.com and Investopedia, but these are **separate from scipy's algorithm**. The UI checkboxes allow users to apply additional filters that scipy doesn't check.

**All 13 pattern metric checkboxes are now functional**, providing comprehensive validation beyond what scipy offers:

### Basic Metrics (9)
1. Volume Confirmation
2. Volume Spike on Breakout
3. RSI Overbought (>70)
4. RSI Oversold (<30)
5. Candlestick Reversal
6. Peak/Trough Symmetry
7. Time Duration
8. Strict Retest Tolerance
9. Retest No Breach

### Advanced Metrics (4)
10. Volume Trend Confirmation
11. Advanced Candlestick Patterns (doji, hammer, engulfing)
12. RSI Divergence Confirmation
13. Momentum Trend Alignment

