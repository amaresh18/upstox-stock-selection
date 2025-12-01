"""Pattern detector - refactored from core/pattern_detector.py."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from scipy.signal import find_peaks

from ..models.pattern import Pattern, PatternType
from ..indicators.rsi import calculate_rsi
from ...config.settings import LOOKBACK_SWING


class PatternDetector:
    """Detects trading patterns in price data."""
    
    def __init__(self, rsi_period: int = 14, verbose: bool = False):
        """Initialize pattern detector."""
        self.rsi_period = rsi_period
        self.verbose = verbose
    
    def detect_all_patterns(
        self,
        df: pd.DataFrame,
        symbol: str,
        patterns: List[str] = None,
        lookback_swing: int = None,
        rsi_period: int = 14
    ) -> List[Dict]:
        """
        Detect all patterns - compatibility method that returns dicts like legacy.
        
        This method maintains backward compatibility with existing code.
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
        
        if lookback_swing is None:
            lookback_swing = LOOKBACK_SWING
        
        # Ensure RSI is calculated using domain indicator
        if 'rsi' not in df.columns:
            df = df.copy()
            df['rsi'] = calculate_rsi(df['close'], period=rsi_period)
        
        # Use legacy detector for now (maintains all complex logic)
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(rsi_period=rsi_period, verbose=self.verbose)
        return legacy.detect_all_patterns(df, symbol, patterns, lookback_swing, rsi_period)
    
    def detect_all(
        self,
        df: pd.DataFrame,
        symbol: str,
        patterns: List[PatternType] = None,
        lookback_swing: int = None
    ) -> List[Pattern]:
        """
        Detect all specified patterns.
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            patterns: List of patterns to detect (None = all)
            lookback_swing: Bars for swing calculation
            
        Returns:
            List of Pattern objects
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
        
        if lookback_swing is None:
            lookback_swing = LOOKBACK_SWING
        
        all_patterns = []
        
        if 'RSI_BULLISH_DIVERGENCE' in patterns:
            all_patterns.extend(self._detect_rsi_bullish_divergence(df, symbol))
        
        if 'RSI_BEARISH_DIVERGENCE' in patterns:
            all_patterns.extend(self._detect_rsi_bearish_divergence(df, symbol))
        
        if 'UPTREND_RETEST' in patterns:
            all_patterns.extend(self._detect_uptrend_retest(df, symbol, lookback_swing))
        
        if 'DOWNTREND_RETEST' in patterns:
            all_patterns.extend(self._detect_downtrend_retest(df, symbol, lookback_swing))
        
        if 'INVERSE_HEAD_SHOULDERS' in patterns:
            all_patterns.extend(self._detect_inverse_head_shoulders(df, symbol))
        
        if 'DOUBLE_BOTTOM' in patterns:
            all_patterns.extend(self._detect_double_bottom(df, symbol))
        
        if 'DOUBLE_TOP' in patterns:
            all_patterns.extend(self._detect_double_top(df, symbol))
        
        if 'TRIPLE_BOTTOM' in patterns:
            all_patterns.extend(self._detect_triple_bottom(df, symbol))
        
        if 'TRIPLE_TOP' in patterns:
            all_patterns.extend(self._detect_triple_top(df, symbol))
        
        return all_patterns
    
    def _find_peaks(self, series: pd.Series, lookback: int = 5, prominence: float = None, distance: int = None) -> List[int]:
        """Find local peaks using scipy."""
        if len(series) < lookback * 2:
            return []
        
        valid_mask = ~pd.isna(series)
        if not valid_mask.any():
            return []
        
        values = series.values
        valid_indices = np.where(valid_mask)[0]
        
        if len(valid_indices) < lookback * 2:
            return []
        
        valid_values = values[valid_indices]
        
        if prominence is None:
            value_range = np.nanmax(valid_values) - np.nanmin(valid_values)
            if value_range > 0:
                prominence = value_range * 0.01 if np.nanmax(valid_values) > 100 else 2.0
            else:
                prominence = 0.01
        
        if distance is None:
            distance = lookback
        
        try:
            peak_indices, _ = find_peaks(valid_values, distance=distance, prominence=prominence, width=1)
            if len(peak_indices) > 0:
                return sorted(valid_indices[peak_indices].tolist())
            return []
        except Exception:
            return self._find_peaks_simple(series, lookback)
    
    def _find_troughs(self, series: pd.Series, lookback: int = 5, prominence: float = None, distance: int = None) -> List[int]:
        """Find local troughs using scipy."""
        if len(series) < lookback * 2:
            return []
        
        valid_mask = ~pd.isna(series)
        if not valid_mask.any():
            return []
        
        values = series.values
        valid_indices = np.where(valid_mask)[0]
        
        if len(valid_indices) < lookback * 2:
            return []
        
        valid_values = values[valid_indices]
        max_val = np.nanmax(valid_values)
        inverted_values = max_val - valid_values
        
        if prominence is None:
            value_range = np.nanmax(valid_values) - np.nanmin(valid_values)
            if value_range > 0:
                prominence = value_range * 0.01 if np.nanmax(valid_values) > 100 else 2.0
            else:
                prominence = 0.01
        
        if distance is None:
            distance = lookback
        
        try:
            trough_indices, _ = find_peaks(inverted_values, distance=distance, prominence=prominence, width=1)
            if len(trough_indices) > 0:
                return sorted(valid_indices[trough_indices].tolist())
            return []
        except Exception:
            return self._find_troughs_simple(series, lookback)
    
    def _find_peaks_simple(self, series: pd.Series, lookback: int = 5) -> List[int]:
        """Simple fallback peak detection."""
        peaks = []
        for i in range(lookback, len(series) - lookback):
            if pd.isna(series.iloc[i]):
                continue
            is_peak = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and not pd.isna(series.iloc[j]) and series.iloc[j] >= series.iloc[i]:
                    is_peak = False
                    break
            if is_peak:
                peaks.append(i)
        return peaks
    
    def _find_troughs_simple(self, series: pd.Series, lookback: int = 5) -> List[int]:
        """Simple fallback trough detection."""
        troughs = []
        for i in range(lookback, len(series) - lookback):
            if pd.isna(series.iloc[i]):
                continue
            is_trough = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and not pd.isna(series.iloc[j]) and series.iloc[j] <= series.iloc[i]:
                    is_trough = False
                    break
            if is_trough:
                troughs.append(i)
        return troughs
    
    def _detect_rsi_bullish_divergence(self, df: pd.DataFrame, symbol: str) -> List[Pattern]:
        """Detect RSI bullish divergence using domain indicators."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        
        # Ensure RSI is calculated using domain indicator
        if 'rsi' not in df.columns:
            df = df.copy()
            df['rsi'] = calculate_rsi(df['close'], period=self.rsi_period)
        
        legacy = LegacyDetector(rsi_period=self.rsi_period, verbose=self.verbose)
        alerts = legacy.detect_rsi_bullish_divergence(df, symbol)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _detect_rsi_bearish_divergence(self, df: pd.DataFrame, symbol: str) -> List[Pattern]:
        """Detect RSI bearish divergence - delegate to existing implementation."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(rsi_period=self.rsi_period, verbose=self.verbose)
        alerts = legacy.detect_rsi_bearish_divergence(df, symbol)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _detect_uptrend_retest(self, df: pd.DataFrame, symbol: str, lookback_swing: int) -> List[Pattern]:
        """Detect uptrend retest - delegate to existing implementation."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(verbose=self.verbose)
        alerts = legacy.detect_uptrend_retest(df, symbol, lookback_swing)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _detect_downtrend_retest(self, df: pd.DataFrame, symbol: str, lookback_swing: int) -> List[Pattern]:
        """Detect downtrend retest - delegate to existing implementation."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(verbose=self.verbose)
        alerts = legacy.detect_downtrend_retest(df, symbol, lookback_swing)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _detect_inverse_head_shoulders(self, df: pd.DataFrame, symbol: str) -> List[Pattern]:
        """Detect inverse head and shoulders - delegate to existing implementation."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(verbose=self.verbose)
        alerts = legacy.detect_inverse_head_and_shoulders(df, symbol)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _detect_double_bottom(self, df: pd.DataFrame, symbol: str) -> List[Pattern]:
        """Detect double bottom - delegate to existing implementation."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(verbose=self.verbose)
        alerts = legacy.detect_double_bottom(df, symbol)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _detect_double_top(self, df: pd.DataFrame, symbol: str) -> List[Pattern]:
        """Detect double top - delegate to existing implementation."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(verbose=self.verbose)
        alerts = legacy.detect_double_top(df, symbol)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _detect_triple_bottom(self, df: pd.DataFrame, symbol: str) -> List[Pattern]:
        """Detect triple bottom - delegate to existing implementation."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(verbose=self.verbose)
        alerts = legacy.detect_triple_bottom(df, symbol)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _detect_triple_top(self, df: pd.DataFrame, symbol: str) -> List[Pattern]:
        """Detect triple top - delegate to existing implementation."""
        from ...core.pattern_detector import PatternDetector as LegacyDetector
        legacy = LegacyDetector(verbose=self.verbose)
        alerts = legacy.detect_triple_top(df, symbol)
        return [self._alert_to_pattern(a) for a in alerts]
    
    def _alert_to_pattern(self, alert: Dict) -> Pattern:
        """Convert alert dict to Pattern object."""
        timestamp = alert.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        
        return Pattern(
            symbol=alert['symbol'],
            pattern_type=alert['pattern_type'],
            price=alert['price'],
            timestamp=timestamp,
            entry_price=alert.get('entry_price', alert['price']),
            stop_loss=alert.get('stop_loss', 0),
            target_price=alert.get('target_price', 0),
            vol_ratio=alert.get('vol_ratio')
        )

