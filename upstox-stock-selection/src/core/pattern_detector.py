"""
Pattern detection module for trading patterns.

This module implements detection for:
1. RSI Bullish Divergence
2. RSI Bearish Divergence
3. Uptrend Retest
4. Downtrend Retest
5. Inverse Head and Shoulders
6. Double Bottom/Top
7. Triple Bottom/Top
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import traceback
from scipy.signal import find_peaks, find_peaks_cwt


class PatternDetector:
    """Detects trading patterns in price data."""
    
    def __init__(self, rsi_period: int = 14, verbose: bool = False):
        """
        Initialize pattern detector.
        
        Args:
            rsi_period: Period for RSI calculation (default: 14)
            verbose: Enable verbose logging
        """
        self.rsi_period = rsi_period
        self.verbose = verbose
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = None) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            df: DataFrame with OHLCV data
            period: RSI period (default: self.rsi_period)
            
        Returns:
            Series with RSI values
        """
        if period is None:
            period = self.rsi_period
        
        if len(df) < period + 1:
            return pd.Series(index=df.index, dtype=float)
        
        # Calculate price changes
        delta = df['close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        # Calculate average gain and loss using Wilder's smoothing method
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50.0)  # Fill NaN with neutral RSI (50)
    
    def find_peaks(self, series: pd.Series, lookback: int = 5, prominence: float = None, distance: int = None) -> List[int]:
        """
        Find local peaks in a series using scipy.signal.find_peaks.
        
        Uses industry-standard algorithm with noise filtering for more reliable
        peak detection compared to simple lookback method.
        
        Args:
            series: Price or RSI series
            lookback: Minimum distance between peaks (default: 5 bars)
            prominence: Minimum prominence of peak (relative to surrounding baseline)
                       If None, uses 1% of series range for price data, 2 for RSI
            distance: Minimum horizontal distance between peaks (default: lookback)
            
        Returns:
            List of indices where peaks occur
        """
        if len(series) < lookback * 2:
            return []
        
        # Remove NaN values and get valid indices
        valid_mask = ~pd.isna(series)
        if not valid_mask.any():
            return []
        
        # Convert to numpy array for scipy
        values = series.values
        valid_indices = np.where(valid_mask)[0]
        
        if len(valid_indices) < lookback * 2:
            return []
        
        # Use only valid values
        valid_values = values[valid_indices]
        
        # Calculate prominence if not provided
        # Prominence measures how much a peak stands out from surrounding baseline
        if prominence is None:
            value_range = np.nanmax(valid_values) - np.nanmin(valid_values)
            if value_range > 0:
                # For price data: 1% of range, for RSI: 2 points
                if np.nanmax(valid_values) > 100:  # Likely price data
                    prominence = value_range * 0.01
                else:  # Likely RSI (0-100)
                    prominence = 2.0
            else:
                prominence = 0.01
        
        # Set distance parameter
        if distance is None:
            distance = lookback
        
        try:
            # Find peaks using scipy (more reliable than custom loop)
            # height: minimum peak height (None = no minimum)
            # distance: minimum distance between peaks
            # prominence: how much peak stands out
            peak_indices, properties = find_peaks(
                valid_values,
                distance=distance,
                prominence=prominence,
                width=1  # Minimum peak width
            )
            
            # Map back to original indices
            if len(peak_indices) > 0:
                original_indices = valid_indices[peak_indices].tolist()
                return sorted(original_indices)
            else:
                return []
                
        except Exception as e:
            if self.verbose:
                print(f"  Error in find_peaks: {e}, falling back to simple method")
            # Fallback to simple method if scipy fails
            return self._find_peaks_simple(series, lookback)
    
    def _find_peaks_simple(self, series: pd.Series, lookback: int = 5) -> List[int]:
        """
        Simple fallback peak detection method.
        
        Args:
            series: Price or RSI series
            lookback: Number of bars on each side to consider for peak
            
        Returns:
            List of indices where peaks occur
        """
        peaks = []
        for i in range(lookback, len(series) - lookback):
            if pd.isna(series.iloc[i]):
                continue
            # Check if current point is higher than surrounding points
            is_peak = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and not pd.isna(series.iloc[j]) and series.iloc[j] >= series.iloc[i]:
                    is_peak = False
                    break
            if is_peak:
                peaks.append(i)
        return peaks
    
    def find_troughs(self, series: pd.Series, lookback: int = 5, prominence: float = None, distance: int = None) -> List[int]:
        """
        Find local troughs (bottoms) in a series using scipy.signal.find_peaks.
        
        Finds troughs by inverting the series and finding peaks.
        Uses industry-standard algorithm with noise filtering.
        
        Args:
            series: Price or RSI series
            lookback: Minimum distance between troughs (default: 5 bars)
            prominence: Minimum prominence of trough (relative to surrounding baseline)
                       If None, uses 1% of series range for price data, 2 for RSI
            distance: Minimum horizontal distance between troughs (default: lookback)
            
        Returns:
            List of indices where troughs occur
        """
        if len(series) < lookback * 2:
            return []
        
        # Remove NaN values and get valid indices
        valid_mask = ~pd.isna(series)
        if not valid_mask.any():
            return []
        
        # Convert to numpy array for scipy
        values = series.values
        valid_indices = np.where(valid_mask)[0]
        
        if len(valid_indices) < lookback * 2:
            return []
        
        # Use only valid values
        valid_values = values[valid_indices]
        
        # Invert series to find troughs as peaks
        # Add offset to ensure all values are positive
        max_val = np.nanmax(valid_values)
        inverted_values = max_val - valid_values
        
        # Calculate prominence if not provided
        if prominence is None:
            value_range = np.nanmax(valid_values) - np.nanmin(valid_values)
            if value_range > 0:
                # For price data: 1% of range, for RSI: 2 points
                if np.nanmax(valid_values) > 100:  # Likely price data
                    prominence = value_range * 0.01
                else:  # Likely RSI (0-100)
                    prominence = 2.0
            else:
                prominence = 0.01
        
        # Set distance parameter
        if distance is None:
            distance = lookback
        
        try:
            # Find peaks in inverted series (which are troughs in original)
            trough_indices, properties = find_peaks(
                inverted_values,
                distance=distance,
                prominence=prominence,
                width=1  # Minimum trough width
            )
            
            # Map back to original indices
            if len(trough_indices) > 0:
                original_indices = valid_indices[trough_indices].tolist()
                return sorted(original_indices)
            else:
                return []
                
        except Exception as e:
            if self.verbose:
                print(f"  Error in find_troughs: {e}, falling back to simple method")
            # Fallback to simple method if scipy fails
            return self._find_troughs_simple(series, lookback)
    
    def _find_troughs_simple(self, series: pd.Series, lookback: int = 5) -> List[int]:
        """
        Simple fallback trough detection method.
        
        Args:
            series: Price or RSI series
            lookback: Number of bars on each side to consider for trough
            
        Returns:
            List of indices where troughs occur
        """
        troughs = []
        for i in range(lookback, len(series) - lookback):
            if pd.isna(series.iloc[i]):
                continue
            # Check if current point is lower than surrounding points
            is_trough = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and not pd.isna(series.iloc[j]) and series.iloc[j] <= series.iloc[i]:
                    is_trough = False
                    break
            if is_trough:
                troughs.append(i)
        return troughs
    
    def detect_rsi_bullish_divergence(
        self, 
        df: pd.DataFrame, 
        symbol: str,
        min_lookback: int = 20,
        max_lookback: int = 100
    ) -> List[Dict]:
        """
        Detect RSI Bullish Divergence.
        
        Bullish divergence occurs when:
        - Price makes lower lows
        - RSI makes higher lows
        - This suggests weakening downward momentum
        
        Args:
            df: DataFrame with OHLCV data and RSI
            symbol: Trading symbol
            min_lookback: Minimum bars to look back for divergence
            max_lookback: Maximum bars to look back for divergence
            
        Returns:
            List of divergence alert dictionaries
        """
        alerts = []
        
        if len(df) < max_lookback + 10:
            return alerts
        
        try:
            # Ensure RSI is calculated
            if 'rsi' not in df.columns:
                df['rsi'] = self.calculate_rsi(df, self.rsi_period)
            
            # Find price troughs (lower lows)
            price_troughs = self.find_troughs(df['low'], lookback=5)
            
            if len(price_troughs) < 2:
                return alerts
            
            # Check for divergence in recent bars
            recent_start = max(0, len(df) - max_lookback)
            
            # Look for two consecutive troughs where:
            # 1. Second price trough is lower than first (lower low)
            # 2. Second RSI trough is higher than first (higher low in RSI)
            for i in range(len(price_troughs) - 1):
                trough1_idx = price_troughs[i]
                trough2_idx = price_troughs[i + 1]
                
                # Only check recent troughs
                if trough2_idx < recent_start:
                    continue
                
                # Get price and RSI values at troughs
                price1 = df['low'].iloc[trough1_idx]
                price2 = df['low'].iloc[trough2_idx]
                rsi1 = df['rsi'].iloc[trough1_idx]
                rsi2 = df['rsi'].iloc[trough2_idx]
                
                # Check for bullish divergence:
                # Price: lower low (price2 < price1)
                # RSI: higher low (rsi2 > rsi1)
                # RSI should be in oversold region (< 30) for stronger signal
                if (price2 < price1 and rsi2 > rsi1 and 
                    not pd.isna(rsi1) and not pd.isna(rsi2) and
                    rsi1 < 30 and rsi2 < 30):  # RSI should be in oversold region (< 30)
                    
                    # Get timestamp of the second trough (confirmation point)
                    timestamp = df.index[trough2_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[trough2_idx]
                    current_price = df['close'].iloc[trough2_idx]
                    current_rsi = rsi2
                    
                    # Calculate divergence strength
                    price_change_pct = ((price2 - price1) / price1) * 100
                    rsi_change = rsi2 - rsi1
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'RSI_BULLISH_DIVERGENCE',
                        'price': float(current_price),
                        'rsi': float(current_rsi),
                        'price_trough1': float(price1),
                        'price_trough2': float(price2),
                        'rsi_trough1': float(rsi1),
                        'rsi_trough2': float(rsi2),
                        'price_change_pct': float(price_change_pct),
                        'rsi_change': float(rsi_change),
                        'divergence_strength': abs(rsi_change) + abs(price_change_pct),
                        'trough1_index': int(trough1_idx),
                        'trough2_index': int(trough2_idx)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ RSI Bullish Divergence detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting RSI bullish divergence for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts
    
    def detect_rsi_bearish_divergence(
        self, 
        df: pd.DataFrame, 
        symbol: str,
        min_lookback: int = 20,
        max_lookback: int = 100
    ) -> List[Dict]:
        """
        Detect RSI Bearish Divergence.
        
        Bearish divergence occurs when:
        - Price makes higher highs
        - RSI makes lower highs
        - This suggests weakening upward momentum
        
        Args:
            df: DataFrame with OHLCV data and RSI
            symbol: Trading symbol
            min_lookback: Minimum bars to look back for divergence
            max_lookback: Maximum bars to look back for divergence
            
        Returns:
            List of divergence alert dictionaries
        """
        alerts = []
        
        if len(df) < max_lookback + 10:
            return alerts
        
        try:
            # Ensure RSI is calculated
            if 'rsi' not in df.columns:
                df['rsi'] = self.calculate_rsi(df, self.rsi_period)
            
            # Find price peaks (higher highs)
            price_peaks = self.find_peaks(df['high'], lookback=5)
            
            if len(price_peaks) < 2:
                return alerts
            
            # Check for divergence in recent bars
            recent_start = max(0, len(df) - max_lookback)
            
            # Look for two consecutive peaks where:
            # 1. Second price peak is higher than first (higher high)
            # 2. Second RSI peak is lower than first (lower high in RSI)
            for i in range(len(price_peaks) - 1):
                peak1_idx = price_peaks[i]
                peak2_idx = price_peaks[i + 1]
                
                # Only check recent peaks
                if peak2_idx < recent_start:
                    continue
                
                # Get price and RSI values at peaks
                price1 = df['high'].iloc[peak1_idx]
                price2 = df['high'].iloc[peak2_idx]
                rsi1 = df['rsi'].iloc[peak1_idx]
                rsi2 = df['rsi'].iloc[peak2_idx]
                
                # Check for bearish divergence:
                # Price: higher high (price2 > price1)
                # RSI: lower high (rsi2 < rsi1)
                # RSI should be in overbought region (> 70) for stronger signal
                if (price2 > price1 and rsi2 < rsi1 and 
                    not pd.isna(rsi1) and not pd.isna(rsi2) and
                    rsi1 > 70 and rsi2 > 70):  # RSI should be in overbought region (> 70)
                    
                    # Get timestamp of the second peak (confirmation point)
                    timestamp = df.index[peak2_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[peak2_idx]
                    current_price = df['close'].iloc[peak2_idx]
                    current_rsi = rsi2
                    
                    # Calculate divergence strength
                    price_change_pct = ((price2 - price1) / price1) * 100
                    rsi_change = rsi1 - rsi2  # Negative change
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'RSI_BEARISH_DIVERGENCE',
                        'price': float(current_price),
                        'rsi': float(current_rsi),
                        'price_peak1': float(price1),
                        'price_peak2': float(price2),
                        'rsi_peak1': float(rsi1),
                        'rsi_peak2': float(rsi2),
                        'price_change_pct': float(price_change_pct),
                        'rsi_change': float(rsi_change),
                        'divergence_strength': abs(rsi_change) + abs(price_change_pct),
                        'peak1_index': int(peak1_idx),
                        'peak2_index': int(peak2_idx)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ RSI Bearish Divergence detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting RSI bearish divergence for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts
    
    def detect_uptrend_retest(
        self, 
        df: pd.DataFrame, 
        symbol: str,
        lookback_swing: int = 12,
        retest_tolerance: float = 0.02  # 2% tolerance for retest
    ) -> List[Dict]:
        """
        Detect Uptrend Retest pattern (Break & Retest - Bullish).
        
        Pattern structure:
        1. Breakout: Price breaks above a resistance level (swing high)
        2. Retest: Price pulls back to the broken resistance level
        3. Reversal: Price bounces from the level (now support) with bullish reversal candle
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            lookback_swing: Bars for swing high calculation
            retest_tolerance: Percentage tolerance for retest level (default: 2%)
            
        Returns:
            List of retest alert dictionaries
        """
        alerts = []
        
        if len(df) < lookback_swing * 3:
            return alerts
        
        try:
            # Calculate swing high (resistance level)
            df['swing_high'] = df['high'].rolling(window=lookback_swing).max() * 0.995
            
            # Look for breakout and retest pattern
            for i in range(lookback_swing * 2, len(df) - 5):
                # Step 1: Find breakout (price breaks above swing high)
                swing_high_level = df['swing_high'].iloc[i - lookback_swing]
                
                if pd.isna(swing_high_level) or swing_high_level == 0:
                    continue
                
                # Check if price broke above this level with momentum and volume
                breakout_idx = None
                breakout_price = 0
                breakout_volume = 0
                for j in range(i - lookback_swing, i):
                    if df['close'].iloc[j] > swing_high_level:
                        # Check for strong momentum (price increase)
                        if j > 0:
                            price_change = ((df['close'].iloc[j] - df['close'].iloc[j-1]) / df['close'].iloc[j-1]) * 100
                        else:
                            price_change = 0
                        
                        # Check for volume confirmation
                        if 'volume' in df.columns and len(df) >= 70:
                            avg_vol = df['volume'].rolling(window=70).mean().iloc[j]
                            current_vol = df['volume'].iloc[j]
                            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
                        else:
                            vol_ratio = 1.0
                        
                        # Breakout should have momentum and volume
                        if price_change > 0 and vol_ratio >= 1.2:
                            breakout_idx = j
                            breakout_price = df['close'].iloc[j]
                            breakout_volume = vol_ratio
                            break
                
                if breakout_idx is None:
                    continue
                
                # Step 2: Look for retest after breakout (within next 10-20 bars)
                retest_window = min(20, len(df) - breakout_idx - 1)
                if retest_window < 5:
                    continue
                
                retest_idx = None
                reversal_candle_high = 0
                for k in range(breakout_idx + 1, breakout_idx + retest_window):
                    # Check if price retested the level (within tolerance)
                    low_price = df['low'].iloc[k]
                    close_price = df['close'].iloc[k]
                    open_price = df['open'].iloc[k]
                    high_price = df['high'].iloc[k]
                    
                    # Retest: price touched or went below the level, then bounced
                    if low_price <= swing_high_level * (1 + retest_tolerance):
                        # Check for bullish reversal candle (hammer, pin bar, engulfing)
                        body_size = abs(close_price - open_price)
                        lower_wick = min(open_price, close_price) - low_price
                        upper_wick = high_price - max(open_price, close_price)
                        
                        # Bullish reversal conditions (per Capital.com):
                        # 1. Long-tailed hammer (lower wick > 1.5x body)
                        # 2. Pin bar (long lower wick, small body)
                        # 3. Engulfing candle (close > open and engulfs previous)
                        # 4. Price bounced from level (close above level)
                        is_bullish_reversal = (
                            (lower_wick > body_size * 1.5 and close_price > swing_high_level) or  # Hammer/pin bar
                            (close_price > open_price and close_price > swing_high_level) or  # Bullish candle above level
                            (close_price > swing_high_level * 0.98)  # Bounced from level
                        )
                        
                        if is_bullish_reversal:
                            # Check that pullback momentum is less than breakout momentum
                            # Calculate pullback momentum (from breakout to retest)
                            pullback_momentum = abs(((low_price - breakout_price) / breakout_price) * 100)
                            breakout_momentum = abs(((breakout_price - swing_high_level) / swing_high_level) * 100)
                            
                            # Pullback should show less momentum than breakout (per Capital.com)
                            if pullback_momentum < breakout_momentum:
                                retest_idx = k
                                reversal_candle_high = high_price
                                break
                
                if retest_idx is not None:
                    # Pattern confirmed: Breakout -> Retest -> Reversal
                    # Per Capital.com guidelines:
                    # Entry: Above the high of the reversal candle (bullish setup)
                    # Stop Loss: Below the reversal pattern AND the broken resistance
                    # Target: Based on risk-to-reward ratio (typically 2x risk)
                    
                    timestamp = df.index[retest_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[retest_idx]
                    current_price = df['close'].iloc[retest_idx]
                    retest_price = df['low'].iloc[retest_idx]
                    
                    # Entry: Above reversal candle high (per Capital.com)
                    entry_price = reversal_candle_high * 1.001  # Slightly above high for safety
                    
                    # Stop Loss: Below reversal pattern AND broken resistance (per Capital.com)
                    stop_loss = min(swing_high_level * 0.98, retest_price * 0.98)
                    
                    # Target: Risk-to-reward ratio of 2:1 (per Capital.com)
                    risk = entry_price - stop_loss
                    target_price = entry_price + (risk * 2)
                    
                    # Calculate volume ratio for confirmation
                    if 'volume' in df.columns and len(df) >= 70:
                        avg_volume = df['volume'].rolling(window=70).mean().iloc[retest_idx]
                        current_volume = df['volume'].iloc[retest_idx]
                        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                    else:
                        vol_ratio = 1.0
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'UPTREND_RETEST',
                        'price': float(current_price),
                        'breakout_price': float(breakout_price),
                        'retest_level': float(swing_high_level),
                        'retest_price': float(retest_price),
                        'breakout_index': int(breakout_idx),
                        'retest_index': int(retest_idx),
                        'bars_after_breakout': int(retest_idx - breakout_idx),
                        'vol_ratio': float(vol_ratio),
                        'entry_price': float(entry_price),  # Entry above reversal candle high
                        'stop_loss': float(stop_loss),  # Stop below reversal pattern AND broken resistance
                        'target_price': float(target_price)  # Target: 2x risk (risk-to-reward)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ Uptrend Retest detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting uptrend retest for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts
    
    def detect_downtrend_retest(
        self, 
        df: pd.DataFrame, 
        symbol: str,
        lookback_swing: int = 12,
        retest_tolerance: float = 0.02  # 2% tolerance for retest
    ) -> List[Dict]:
        """
        Detect Downtrend Retest pattern (Break & Retest - Bearish).
        
        Pattern structure:
        1. Breakdown: Price breaks below a support level (swing low)
        2. Retest: Price pulls back to the broken support level
        3. Reversal: Price rejects from the level (now resistance) with bearish reversal candle
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            lookback_swing: Bars for swing low calculation
            retest_tolerance: Percentage tolerance for retest level (default: 2%)
            
        Returns:
            List of retest alert dictionaries
        """
        alerts = []
        
        if len(df) < lookback_swing * 3:
            return alerts
        
        try:
            # Calculate swing low (support level)
            df['swing_low'] = df['low'].rolling(window=lookback_swing).min() * 1.005
            
            # Look for breakdown and retest pattern
            for i in range(lookback_swing * 2, len(df) - 5):
                # Step 1: Find breakdown (price breaks below swing low)
                swing_low_level = df['swing_low'].iloc[i - lookback_swing]
                
                if pd.isna(swing_low_level) or swing_low_level == 0:
                    continue
                
                # Check if price broke below this level with momentum and volume
                breakdown_idx = None
                breakdown_price = 0
                breakdown_volume = 0
                for j in range(i - lookback_swing, i):
                    if df['close'].iloc[j] < swing_low_level:
                        # Check for strong momentum (price decrease)
                        if j > 0:
                            price_change = ((df['close'].iloc[j] - df['close'].iloc[j-1]) / df['close'].iloc[j-1]) * 100
                        else:
                            price_change = 0
                        
                        # Check for volume confirmation
                        if 'volume' in df.columns and len(df) >= 70:
                            avg_vol = df['volume'].rolling(window=70).mean().iloc[j]
                            current_vol = df['volume'].iloc[j]
                            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
                        else:
                            vol_ratio = 1.0
                        
                        # Breakdown should have momentum and volume
                        if price_change < 0 and vol_ratio >= 1.2:
                            breakdown_idx = j
                            breakdown_price = df['close'].iloc[j]
                            breakdown_volume = vol_ratio
                            break
                
                if breakdown_idx is None:
                    continue
                
                # Step 2: Look for retest after breakdown (within next 10-20 bars)
                retest_window = min(20, len(df) - breakdown_idx - 1)
                if retest_window < 5:
                    continue
                
                retest_idx = None
                reversal_candle_low = float('inf')
                for k in range(breakdown_idx + 1, breakdown_idx + retest_window):
                    # Check if price retested the level (within tolerance)
                    high_price = df['high'].iloc[k]
                    close_price = df['close'].iloc[k]
                    open_price = df['open'].iloc[k]
                    low_price = df['low'].iloc[k]
                    
                    # Retest: price touched or went above the level, then rejected
                    if high_price >= swing_low_level * (1 - retest_tolerance):
                        # Check for bearish reversal candle (shooting star, pin bar, engulfing)
                        body_size = abs(close_price - open_price)
                        upper_wick = high_price - max(open_price, close_price)
                        lower_wick = min(open_price, close_price) - low_price
                        
                        # Bearish reversal conditions (per Capital.com):
                        # 1. Long upper wick (shooting star pattern)
                        # 2. Pin bar (long upper wick, small body)
                        # 3. Engulfing candle (close < open and engulfs previous)
                        # 4. Price rejected from level (close below level)
                        is_bearish_reversal = (
                            (upper_wick > body_size * 1.5 and close_price < swing_low_level) or  # Shooting star/pin bar
                            (close_price < open_price and close_price < swing_low_level) or  # Bearish candle below level
                            (close_price < swing_low_level * 1.02)  # Rejected from level
                        )
                        
                        if is_bearish_reversal:
                            # Check that pullback momentum is less than breakdown momentum
                            # Calculate pullback momentum (from breakdown to retest)
                            pullback_momentum = abs(((high_price - breakdown_price) / breakdown_price) * 100)
                            breakdown_momentum = abs(((swing_low_level - breakdown_price) / breakdown_price) * 100)
                            
                            # Pullback should show less momentum than breakdown (per Capital.com)
                            if pullback_momentum < breakdown_momentum:
                                retest_idx = k
                                reversal_candle_low = low_price
                                break
                
                if retest_idx is not None:
                    # Pattern confirmed: Breakdown -> Retest -> Reversal
                    # Per Capital.com guidelines:
                    # Entry: Below the low of the reversal candle (bearish setup)
                    # Stop Loss: Above the reversal pattern AND the broken support
                    # Target: Based on risk-to-reward ratio (typically 2x risk)
                    
                    timestamp = df.index[retest_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[retest_idx]
                    current_price = df['close'].iloc[retest_idx]
                    retest_price = df['high'].iloc[retest_idx]
                    
                    # Entry: Below reversal candle low (per Capital.com)
                    entry_price = reversal_candle_low * 0.999  # Slightly below low for safety
                    
                    # Stop Loss: Above reversal pattern AND broken support (per Capital.com)
                    stop_loss = max(swing_low_level * 1.02, retest_price * 1.02)
                    
                    # Target: Risk-to-reward ratio of 2:1 (per Capital.com)
                    risk = stop_loss - entry_price
                    target_price = entry_price - (risk * 2)
                    
                    # Calculate volume ratio for confirmation
                    if 'volume' in df.columns and len(df) >= 70:
                        avg_volume = df['volume'].rolling(window=70).mean().iloc[retest_idx]
                        current_volume = df['volume'].iloc[retest_idx]
                        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                    else:
                        vol_ratio = 1.0
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'DOWNTREND_RETEST',
                        'price': float(current_price),
                        'breakdown_price': float(breakdown_price),
                        'retest_level': float(swing_low_level),
                        'retest_price': float(retest_price),
                        'breakdown_index': int(breakdown_idx),
                        'retest_index': int(retest_idx),
                        'bars_after_breakdown': int(retest_idx - breakdown_idx),
                        'vol_ratio': float(vol_ratio),
                        'entry_price': float(entry_price),  # Entry below reversal candle low
                        'stop_loss': float(stop_loss),  # Stop above reversal pattern AND broken support
                        'target_price': float(target_price)  # Target: 2x risk (risk-to-reward)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ Downtrend Retest detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting downtrend retest for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts
    
    def detect_all_patterns(
        self,
        df: pd.DataFrame,
        symbol: str,
        patterns: List[str] = None,
        lookback_swing: int = 12,
        rsi_period: int = 14
    ) -> List[Dict]:
        """
        Detect all specified patterns.
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            patterns: List of patterns to detect. If None, detects all.
                     Options: 'RSI_BULLISH_DIVERGENCE', 'RSI_BEARISH_DIVERGENCE',
                              'UPTREND_RETEST', 'DOWNTREND_RETEST'
            lookback_swing: Bars for swing calculation (for retest patterns)
            rsi_period: Period for RSI calculation
            
        Returns:
            List of all pattern alerts
        """
        if patterns is None:
            patterns = [
                'RSI_BULLISH_DIVERGENCE',
                'RSI_BEARISH_DIVERGENCE',
                'UPTREND_RETEST',
                'DOWNTREND_RETEST',
                'INVERSE_HEAD_SHOULDERS',
                'DOUBLE_BOTTOM',
                'DOUBLE_TOP',
                'TRIPLE_BOTTOM',
                'TRIPLE_TOP'
            ]
        
        all_alerts = []
        
        # Update RSI period if different
        if rsi_period != self.rsi_period:
            self.rsi_period = rsi_period
        
        # Detect each pattern
        if 'RSI_BULLISH_DIVERGENCE' in patterns:
            alerts = self.detect_rsi_bullish_divergence(df, symbol)
            all_alerts.extend(alerts)
        
        if 'RSI_BEARISH_DIVERGENCE' in patterns:
            alerts = self.detect_rsi_bearish_divergence(df, symbol)
            all_alerts.extend(alerts)
        
        if 'UPTREND_RETEST' in patterns:
            alerts = self.detect_uptrend_retest(df, symbol, lookback_swing=lookback_swing)
            all_alerts.extend(alerts)
        
        if 'DOWNTREND_RETEST' in patterns:
            alerts = self.detect_downtrend_retest(df, symbol, lookback_swing=lookback_swing)
            all_alerts.extend(alerts)
        
        if 'INVERSE_HEAD_SHOULDERS' in patterns:
            alerts = self.detect_inverse_head_and_shoulders(df, symbol)
            all_alerts.extend(alerts)
        
        if 'DOUBLE_BOTTOM' in patterns:
            alerts = self.detect_double_bottom(df, symbol)
            all_alerts.extend(alerts)
        
        if 'DOUBLE_TOP' in patterns:
            alerts = self.detect_double_top(df, symbol)
            all_alerts.extend(alerts)
        
        if 'TRIPLE_BOTTOM' in patterns:
            alerts = self.detect_triple_bottom(df, symbol)
            all_alerts.extend(alerts)
        
        if 'TRIPLE_TOP' in patterns:
            alerts = self.detect_triple_top(df, symbol)
            all_alerts.extend(alerts)
        
        return all_alerts
    
    def detect_inverse_head_and_shoulders(
        self,
        df: pd.DataFrame,
        symbol: str,
        min_lookback: int = 30,
        max_lookback: int = 200,
        price_tolerance: float = 0.03,  # 3% tolerance for shoulder levels
        volume_multiplier: float = 1.2  # 20% higher volume on breakout
    ) -> List[Dict]:
        """
        Detect Inverse Head and Shoulders pattern (bullish reversal).
        
        Pattern structure:
        - Left Shoulder: First trough
        - Head: Lower trough (lowest point)
        - Right Shoulder: Third trough (similar level to left shoulder)
        - Neckline: Resistance line connecting peaks between shoulders and head
        - Confirmation: Price breaks above neckline with volume
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            min_lookback: Minimum bars to look back
            max_lookback: Maximum bars to look back
            price_tolerance: Tolerance for shoulder level similarity (default: 3%)
            volume_multiplier: Minimum volume multiplier for breakout (default: 1.2x)
            
        Returns:
            List of pattern alert dictionaries
        """
        alerts = []
        
        if len(df) < max_lookback + 20:
            return alerts
        
        try:
            # Find troughs (bottoms)
            troughs = self.find_troughs(df['low'], lookback=5)
            
            if len(troughs) < 3:
                return alerts
            
            # Find peaks (for neckline)
            peaks = self.find_peaks(df['high'], lookback=5)
            
            if len(peaks) < 2:
                return alerts
            
            # Look for pattern in recent bars
            recent_start = max(0, len(df) - max_lookback)
            
            # Check for Inverse Head and Shoulders pattern
            for i in range(len(troughs) - 2):
                left_shoulder_idx = troughs[i]
                head_idx = troughs[i + 1]
                right_shoulder_idx = troughs[i + 2]
                
                # Only check recent patterns
                if right_shoulder_idx < recent_start:
                    continue
                
                # Get price values
                left_shoulder_price = df['low'].iloc[left_shoulder_idx]
                head_price = df['low'].iloc[head_idx]
                right_shoulder_price = df['low'].iloc[right_shoulder_idx]
                
                # Pattern validation:
                # 1. Head must be lower than both shoulders
                if not (head_price < left_shoulder_price and head_price < right_shoulder_price):
                    continue
                
                # 2. Shoulders should be at similar levels (within tolerance)
                shoulder_diff = abs(left_shoulder_price - right_shoulder_price) / min(left_shoulder_price, right_shoulder_price)
                if shoulder_diff > price_tolerance:
                    continue
                
                # 3. Find neckline (peaks between shoulders and head)
                # Left peak: between left shoulder and head
                left_peak_idx = None
                left_peak_price = 0
                for peak_idx in peaks:
                    if left_shoulder_idx < peak_idx < head_idx:
                        peak_price = df['high'].iloc[peak_idx]
                        if peak_price > left_peak_price:
                            left_peak_price = peak_price
                            left_peak_idx = peak_idx
                
                # Right peak: between head and right shoulder
                right_peak_idx = None
                right_peak_price = 0
                for peak_idx in peaks:
                    if head_idx < peak_idx < right_shoulder_idx:
                        peak_price = df['high'].iloc[peak_idx]
                        if peak_price > right_peak_price:
                            right_peak_price = peak_price
                            right_peak_idx = peak_idx
                
                if left_peak_idx is None or right_peak_idx is None:
                    continue
                
                # Neckline: average of the two peaks (or use the higher one for conservative approach)
                neckline_price = max(left_peak_price, right_peak_price)
                
                # 4. Check for neckline breakout (after right shoulder)
                # Look for breakout in the next 10-20 bars after right shoulder
                breakout_window = min(20, len(df) - right_shoulder_idx - 1)
                if breakout_window < 5:
                    continue
                
                breakout_idx = None
                for k in range(right_shoulder_idx + 1, right_shoulder_idx + breakout_window):
                    close_price = df['close'].iloc[k]
                    high_price = df['high'].iloc[k]
                    
                    # Breakout: close above neckline
                    if close_price > neckline_price:
                        # Check volume confirmation
                        if 'volume' in df.columns and len(df) >= 70:
                            avg_volume = df['volume'].rolling(window=70).mean().iloc[k]
                            current_volume = df['volume'].iloc[k]
                            vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                            
                            if vol_ratio >= volume_multiplier:
                                breakout_idx = k
                                break
                        else:
                            # No volume data, accept breakout
                            breakout_idx = k
                            break
                
                if breakout_idx is not None:
                    # Pattern confirmed
                    timestamp = df.index[breakout_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[breakout_idx]
                    current_price = df['close'].iloc[breakout_idx]
                    
                    # Calculate pattern metrics
                    pattern_height = neckline_price - head_price
                    target_price = neckline_price + pattern_height  # Target = neckline + pattern height
                    stop_loss = head_price * 0.98  # Stop below head
                    
                    # Calculate volume ratio
                    if 'volume' in df.columns and len(df) >= 70:
                        avg_volume = df['volume'].rolling(window=70).mean().iloc[breakout_idx]
                        current_volume = df['volume'].iloc[breakout_idx]
                        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                    else:
                        vol_ratio = 1.0
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'INVERSE_HEAD_SHOULDERS',
                        'price': float(current_price),
                        'neckline': float(neckline_price),
                        'head_price': float(head_price),
                        'left_shoulder_price': float(left_shoulder_price),
                        'right_shoulder_price': float(right_shoulder_price),
                        'pattern_height': float(pattern_height),
                        'vol_ratio': float(vol_ratio),
                        'entry_price': float(current_price),
                        'stop_loss': float(stop_loss),
                        'target_price': float(target_price),
                        'left_shoulder_idx': int(left_shoulder_idx),
                        'head_idx': int(head_idx),
                        'right_shoulder_idx': int(right_shoulder_idx),
                        'breakout_idx': int(breakout_idx)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ Inverse Head and Shoulders detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting Inverse Head and Shoulders for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts
    
    def detect_double_bottom(
        self,
        df: pd.DataFrame,
        symbol: str,
        min_lookback: int = 20,
        max_lookback: int = 150,
        price_tolerance: float = 0.02,  # 2% tolerance for bottom levels
        volume_multiplier: float = 1.2
    ) -> List[Dict]:
        """
        Detect Double Bottom pattern (bullish reversal).
        
        Pattern structure:
        - First Bottom: First trough
        - Peak: Peak between the two bottoms
        - Second Bottom: Second trough at similar level to first
        - Neckline: Resistance at the peak
        - Confirmation: Price breaks above neckline with volume
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            min_lookback: Minimum bars to look back
            max_lookback: Maximum bars to look back
            price_tolerance: Tolerance for bottom level similarity (default: 2%)
            volume_multiplier: Minimum volume multiplier for breakout (default: 1.2x)
            
        Returns:
            List of pattern alert dictionaries
        """
        alerts = []
        
        if len(df) < max_lookback + 20:
            return alerts
        
        try:
            # Find troughs (bottoms)
            troughs = self.find_troughs(df['low'], lookback=5)
            
            if len(troughs) < 2:
                return alerts
            
            # Find peaks (for neckline)
            peaks = self.find_peaks(df['high'], lookback=5)
            
            if len(peaks) < 1:
                return alerts
            
            # Look for pattern in recent bars
            recent_start = max(0, len(df) - max_lookback)
            
            # Check for Double Bottom pattern
            for i in range(len(troughs) - 1):
                first_bottom_idx = troughs[i]
                second_bottom_idx = troughs[i + 1]
                
                # Only check recent patterns
                if second_bottom_idx < recent_start:
                    continue
                
                # Get price values
                first_bottom_price = df['low'].iloc[first_bottom_idx]
                second_bottom_price = df['low'].iloc[second_bottom_idx]
                
                # Pattern validation:
                # 1. Both bottoms should be at similar levels (within tolerance)
                bottom_diff = abs(first_bottom_price - second_bottom_price) / min(first_bottom_price, second_bottom_price)
                if bottom_diff > price_tolerance:
                    continue
                
                # 2. Find peak between the two bottoms (neckline)
                neckline_idx = None
                neckline_price = 0
                for peak_idx in peaks:
                    if first_bottom_idx < peak_idx < second_bottom_idx:
                        peak_price = df['high'].iloc[peak_idx]
                        if peak_price > neckline_price:
                            neckline_price = peak_price
                            neckline_idx = peak_idx
                
                if neckline_idx is None:
                    continue
                
                # 3. Check for neckline breakout (after second bottom)
                breakout_window = min(20, len(df) - second_bottom_idx - 1)
                if breakout_window < 5:
                    continue
                
                breakout_idx = None
                for k in range(second_bottom_idx + 1, second_bottom_idx + breakout_window):
                    close_price = df['close'].iloc[k]
                    
                    # Breakout: close above neckline
                    if close_price > neckline_price:
                        # Check volume confirmation
                        if 'volume' in df.columns and len(df) >= 70:
                            avg_volume = df['volume'].rolling(window=70).mean().iloc[k]
                            current_volume = df['volume'].iloc[k]
                            vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                            
                            if vol_ratio >= volume_multiplier:
                                breakout_idx = k
                                break
                        else:
                            breakout_idx = k
                            break
                
                if breakout_idx is not None:
                    # Pattern confirmed
                    timestamp = df.index[breakout_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[breakout_idx]
                    current_price = df['close'].iloc[breakout_idx]
                    
                    # Calculate pattern metrics
                    avg_bottom = (first_bottom_price + second_bottom_price) / 2
                    pattern_height = neckline_price - avg_bottom
                    target_price = neckline_price + pattern_height
                    stop_loss = avg_bottom * 0.98
                    
                    # Calculate volume ratio
                    if 'volume' in df.columns and len(df) >= 70:
                        avg_volume = df['volume'].rolling(window=70).mean().iloc[breakout_idx]
                        current_volume = df['volume'].iloc[breakout_idx]
                        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                    else:
                        vol_ratio = 1.0
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'DOUBLE_BOTTOM',
                        'price': float(current_price),
                        'neckline': float(neckline_price),
                        'first_bottom_price': float(first_bottom_price),
                        'second_bottom_price': float(second_bottom_price),
                        'pattern_height': float(pattern_height),
                        'vol_ratio': float(vol_ratio),
                        'entry_price': float(current_price),
                        'stop_loss': float(stop_loss),
                        'target_price': float(target_price),
                        'first_bottom_idx': int(first_bottom_idx),
                        'second_bottom_idx': int(second_bottom_idx),
                        'breakout_idx': int(breakout_idx)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ Double Bottom detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting Double Bottom for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts
    
    def detect_double_top(
        self,
        df: pd.DataFrame,
        symbol: str,
        min_lookback: int = 20,
        max_lookback: int = 150,
        price_tolerance: float = 0.02,
        volume_multiplier: float = 1.2
    ) -> List[Dict]:
        """
        Detect Double Top pattern (bearish reversal).
        
        Pattern structure:
        - First Top: First peak
        - Trough: Trough between the two tops
        - Second Top: Second peak at similar level to first
        - Neckline: Support at the trough
        - Confirmation: Price breaks below neckline with volume
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            min_lookback: Minimum bars to look back
            max_lookback: Maximum bars to look back
            price_tolerance: Tolerance for top level similarity (default: 2%)
            volume_multiplier: Minimum volume multiplier for breakdown (default: 1.2x)
            
        Returns:
            List of pattern alert dictionaries
        """
        alerts = []
        
        if len(df) < max_lookback + 20:
            return alerts
        
        try:
            # Find peaks (tops)
            peaks = self.find_peaks(df['high'], lookback=5)
            
            if len(peaks) < 2:
                return alerts
            
            # Find troughs (for neckline)
            troughs = self.find_troughs(df['low'], lookback=5)
            
            if len(troughs) < 1:
                return alerts
            
            # Look for pattern in recent bars
            recent_start = max(0, len(df) - max_lookback)
            
            # Check for Double Top pattern
            for i in range(len(peaks) - 1):
                first_top_idx = peaks[i]
                second_top_idx = peaks[i + 1]
                
                # Only check recent patterns
                if second_top_idx < recent_start:
                    continue
                
                # Get price values
                first_top_price = df['high'].iloc[first_top_idx]
                second_top_price = df['high'].iloc[second_top_idx]
                
                # Pattern validation:
                # 1. Both tops should be at similar levels (within tolerance)
                top_diff = abs(first_top_price - second_top_price) / min(first_top_price, second_top_price)
                if top_diff > price_tolerance:
                    continue
                
                # 2. Find trough between the two tops (neckline)
                neckline_idx = None
                neckline_price = float('inf')
                for trough_idx in troughs:
                    if first_top_idx < trough_idx < second_top_idx:
                        trough_price = df['low'].iloc[trough_idx]
                        if trough_price < neckline_price:
                            neckline_price = trough_price
                            neckline_idx = trough_idx
                
                if neckline_idx is None:
                    continue
                
                # 3. Check for neckline breakdown (after second top)
                breakdown_window = min(20, len(df) - second_top_idx - 1)
                if breakdown_window < 5:
                    continue
                
                breakdown_idx = None
                for k in range(second_top_idx + 1, second_top_idx + breakdown_window):
                    close_price = df['close'].iloc[k]
                    
                    # Breakdown: close below neckline
                    if close_price < neckline_price:
                        # Check volume confirmation
                        if 'volume' in df.columns and len(df) >= 70:
                            avg_volume = df['volume'].rolling(window=70).mean().iloc[k]
                            current_volume = df['volume'].iloc[k]
                            vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                            
                            if vol_ratio >= volume_multiplier:
                                breakdown_idx = k
                                break
                        else:
                            breakdown_idx = k
                            break
                
                if breakdown_idx is not None:
                    # Pattern confirmed
                    timestamp = df.index[breakdown_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[breakdown_idx]
                    current_price = df['close'].iloc[breakdown_idx]
                    
                    # Calculate pattern metrics
                    avg_top = (first_top_price + second_top_price) / 2
                    pattern_height = avg_top - neckline_price
                    target_price = neckline_price - pattern_height
                    stop_loss = avg_top * 1.02
                    
                    # Calculate volume ratio
                    if 'volume' in df.columns and len(df) >= 70:
                        avg_volume = df['volume'].rolling(window=70).mean().iloc[breakdown_idx]
                        current_volume = df['volume'].iloc[breakdown_idx]
                        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                    else:
                        vol_ratio = 1.0
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'DOUBLE_TOP',
                        'price': float(current_price),
                        'neckline': float(neckline_price),
                        'first_top_price': float(first_top_price),
                        'second_top_price': float(second_top_price),
                        'pattern_height': float(pattern_height),
                        'vol_ratio': float(vol_ratio),
                        'entry_price': float(current_price),
                        'stop_loss': float(stop_loss),
                        'target_price': float(target_price),
                        'first_top_idx': int(first_top_idx),
                        'second_top_idx': int(second_top_idx),
                        'breakdown_idx': int(breakdown_idx)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ Double Top detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting Double Top for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts
    
    def detect_triple_bottom(
        self,
        df: pd.DataFrame,
        symbol: str,
        min_lookback: int = 30,
        max_lookback: int = 200,
        price_tolerance: float = 0.02,
        volume_multiplier: float = 1.2
    ) -> List[Dict]:
        """
        Detect Triple Bottom pattern (bullish reversal).
        
        Pattern structure:
        - First Bottom: First trough
        - First Peak: Peak after first bottom
        - Second Bottom: Second trough at similar level
        - Second Peak: Peak after second bottom
        - Third Bottom: Third trough at similar level
        - Neckline: Resistance at the highest peak
        - Confirmation: Price breaks above neckline with volume
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            min_lookback: Minimum bars to look back
            max_lookback: Maximum bars to look back
            price_tolerance: Tolerance for bottom level similarity (default: 2%)
            volume_multiplier: Minimum volume multiplier for breakout (default: 1.2x)
            
        Returns:
            List of pattern alert dictionaries
        """
        alerts = []
        
        if len(df) < max_lookback + 20:
            return alerts
        
        try:
            # Find troughs (bottoms)
            troughs = self.find_troughs(df['low'], lookback=5)
            
            if len(troughs) < 3:
                return alerts
            
            # Find peaks (for neckline)
            peaks = self.find_peaks(df['high'], lookback=5)
            
            if len(peaks) < 2:
                return alerts
            
            # Look for pattern in recent bars
            recent_start = max(0, len(df) - max_lookback)
            
            # Check for Triple Bottom pattern
            for i in range(len(troughs) - 2):
                first_bottom_idx = troughs[i]
                second_bottom_idx = troughs[i + 1]
                third_bottom_idx = troughs[i + 2]
                
                # Only check recent patterns
                if third_bottom_idx < recent_start:
                    continue
                
                # Get price values
                first_bottom_price = df['low'].iloc[first_bottom_idx]
                second_bottom_price = df['low'].iloc[second_bottom_idx]
                third_bottom_price = df['low'].iloc[third_bottom_idx]
                
                # Pattern validation:
                # 1. All three bottoms should be at similar levels (within tolerance)
                bottoms = [first_bottom_price, second_bottom_price, third_bottom_price]
                min_bottom = min(bottoms)
                max_bottom = max(bottoms)
                bottom_diff = (max_bottom - min_bottom) / min_bottom
                if bottom_diff > price_tolerance:
                    continue
                
                # 2. Find peaks between bottoms (for neckline)
                neckline_price = 0
                neckline_idx = None
                
                # Find highest peak between first and third bottom
                for peak_idx in peaks:
                    if first_bottom_idx < peak_idx < third_bottom_idx:
                        peak_price = df['high'].iloc[peak_idx]
                        if peak_price > neckline_price:
                            neckline_price = peak_price
                            neckline_idx = peak_idx
                
                if neckline_idx is None:
                    continue
                
                # 3. Check for neckline breakout (after third bottom)
                breakout_window = min(20, len(df) - third_bottom_idx - 1)
                if breakout_window < 5:
                    continue
                
                breakout_idx = None
                for k in range(third_bottom_idx + 1, third_bottom_idx + breakout_window):
                    close_price = df['close'].iloc[k]
                    
                    # Breakout: close above neckline
                    if close_price > neckline_price:
                        # Check volume confirmation
                        if 'volume' in df.columns and len(df) >= 70:
                            avg_volume = df['volume'].rolling(window=70).mean().iloc[k]
                            current_volume = df['volume'].iloc[k]
                            vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                            
                            if vol_ratio >= volume_multiplier:
                                breakout_idx = k
                                break
                        else:
                            breakout_idx = k
                            break
                
                if breakout_idx is not None:
                    # Pattern confirmed
                    timestamp = df.index[breakout_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[breakout_idx]
                    current_price = df['close'].iloc[breakout_idx]
                    
                    # Calculate pattern metrics
                    avg_bottom = (first_bottom_price + second_bottom_price + third_bottom_price) / 3
                    pattern_height = neckline_price - avg_bottom
                    target_price = neckline_price + pattern_height
                    stop_loss = avg_bottom * 0.98
                    
                    # Calculate volume ratio
                    if 'volume' in df.columns and len(df) >= 70:
                        avg_volume = df['volume'].rolling(window=70).mean().iloc[breakout_idx]
                        current_volume = df['volume'].iloc[breakout_idx]
                        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                    else:
                        vol_ratio = 1.0
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'TRIPLE_BOTTOM',
                        'price': float(current_price),
                        'neckline': float(neckline_price),
                        'first_bottom_price': float(first_bottom_price),
                        'second_bottom_price': float(second_bottom_price),
                        'third_bottom_price': float(third_bottom_price),
                        'pattern_height': float(pattern_height),
                        'vol_ratio': float(vol_ratio),
                        'entry_price': float(current_price),
                        'stop_loss': float(stop_loss),
                        'target_price': float(target_price),
                        'first_bottom_idx': int(first_bottom_idx),
                        'second_bottom_idx': int(second_bottom_idx),
                        'third_bottom_idx': int(third_bottom_idx),
                        'breakout_idx': int(breakout_idx)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ Triple Bottom detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting Triple Bottom for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts
    
    def detect_triple_top(
        self,
        df: pd.DataFrame,
        symbol: str,
        min_lookback: int = 30,
        max_lookback: int = 200,
        price_tolerance: float = 0.02,
        volume_multiplier: float = 1.2
    ) -> List[Dict]:
        """
        Detect Triple Top pattern (bearish reversal).
        
        Pattern structure:
        - First Top: First peak
        - First Trough: Trough after first top
        - Second Top: Second peak at similar level
        - Second Trough: Trough after second top
        - Third Top: Third peak at similar level
        - Neckline: Support at the lowest trough
        - Confirmation: Price breaks below neckline with volume
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            min_lookback: Minimum bars to look back
            max_lookback: Maximum bars to look back
            price_tolerance: Tolerance for top level similarity (default: 2%)
            volume_multiplier: Minimum volume multiplier for breakdown (default: 1.2x)
            
        Returns:
            List of pattern alert dictionaries
        """
        alerts = []
        
        if len(df) < max_lookback + 20:
            return alerts
        
        try:
            # Find peaks (tops)
            peaks = self.find_peaks(df['high'], lookback=5)
            
            if len(peaks) < 3:
                return alerts
            
            # Find troughs (for neckline)
            troughs = self.find_troughs(df['low'], lookback=5)
            
            if len(troughs) < 2:
                return alerts
            
            # Look for pattern in recent bars
            recent_start = max(0, len(df) - max_lookback)
            
            # Check for Triple Top pattern
            for i in range(len(peaks) - 2):
                first_top_idx = peaks[i]
                second_top_idx = peaks[i + 1]
                third_top_idx = peaks[i + 2]
                
                # Only check recent patterns
                if third_top_idx < recent_start:
                    continue
                
                # Get price values
                first_top_price = df['high'].iloc[first_top_idx]
                second_top_price = df['high'].iloc[second_top_idx]
                third_top_price = df['high'].iloc[third_top_idx]
                
                # Pattern validation:
                # 1. All three tops should be at similar levels (within tolerance)
                tops = [first_top_price, second_top_price, third_top_price]
                min_top = min(tops)
                max_top = max(tops)
                top_diff = (max_top - min_top) / min_top
                if top_diff > price_tolerance:
                    continue
                
                # 2. Find troughs between tops (for neckline)
                neckline_price = float('inf')
                neckline_idx = None
                
                # Find lowest trough between first and third top
                for trough_idx in troughs:
                    if first_top_idx < trough_idx < third_top_idx:
                        trough_price = df['low'].iloc[trough_idx]
                        if trough_price < neckline_price:
                            neckline_price = trough_price
                            neckline_idx = trough_idx
                
                if neckline_idx is None:
                    continue
                
                # 3. Check for neckline breakdown (after third top)
                breakdown_window = min(20, len(df) - third_top_idx - 1)
                if breakdown_window < 5:
                    continue
                
                breakdown_idx = None
                for k in range(third_top_idx + 1, third_top_idx + breakdown_window):
                    close_price = df['close'].iloc[k]
                    
                    # Breakdown: close below neckline
                    if close_price < neckline_price:
                        # Check volume confirmation
                        if 'volume' in df.columns and len(df) >= 70:
                            avg_volume = df['volume'].rolling(window=70).mean().iloc[k]
                            current_volume = df['volume'].iloc[k]
                            vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                            
                            if vol_ratio >= volume_multiplier:
                                breakdown_idx = k
                                break
                        else:
                            breakdown_idx = k
                            break
                
                if breakdown_idx is not None:
                    # Pattern confirmed
                    timestamp = df.index[breakdown_idx] if isinstance(df.index, pd.DatetimeIndex) else df['timestamp'].iloc[breakdown_idx]
                    current_price = df['close'].iloc[breakdown_idx]
                    
                    # Calculate pattern metrics
                    avg_top = (first_top_price + second_top_price + third_top_price) / 3
                    pattern_height = avg_top - neckline_price
                    target_price = neckline_price - pattern_height
                    stop_loss = avg_top * 1.02
                    
                    # Calculate volume ratio
                    if 'volume' in df.columns and len(df) >= 70:
                        avg_volume = df['volume'].rolling(window=70).mean().iloc[breakdown_idx]
                        current_volume = df['volume'].iloc[breakdown_idx]
                        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                    else:
                        vol_ratio = 1.0
                    
                    alerts.append({
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'pattern_type': 'TRIPLE_TOP',
                        'price': float(current_price),
                        'neckline': float(neckline_price),
                        'first_top_price': float(first_top_price),
                        'second_top_price': float(second_top_price),
                        'third_top_price': float(third_top_price),
                        'pattern_height': float(pattern_height),
                        'vol_ratio': float(vol_ratio),
                        'entry_price': float(current_price),
                        'stop_loss': float(stop_loss),
                        'target_price': float(target_price),
                        'first_top_idx': int(first_top_idx),
                        'second_top_idx': int(second_top_idx),
                        'third_top_idx': int(third_top_idx),
                        'breakdown_idx': int(breakdown_idx)
                    })
                    
                    if self.verbose:
                        print(f"  ✓ Triple Top detected for {symbol} at {timestamp}")
        
        except Exception as e:
            if self.verbose:
                print(f"  Error detecting Triple Top for {symbol}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        return alerts

