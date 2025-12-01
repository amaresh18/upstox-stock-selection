"""Signal detection - breakout and breakdown."""

import pandas as pd
import numpy as np
from typing import List
from datetime import datetime

from ..models.signal import Signal
from ...config.settings import LOOKBACK_SWING, VOL_WINDOW, VOL_MULT, HOLD_BARS


class SignalDetector:
    """Detects breakout and breakdown signals."""
    
    def detect(
        self,
        df: pd.DataFrame,
        symbol: str,
        require_exit_price: bool = False
    ) -> List[Signal]:
        """
        Detect breakout and breakdown signals.
        
        Args:
            df: DataFrame with OHLCV and indicators
            symbol: Trading symbol
            require_exit_price: If True, only detect where exit can be calculated
            
        Returns:
            List of Signal objects
        """
        signals = []
        
        start_i = int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1
        end_i = len(df) - HOLD_BARS if require_exit_price else len(df)
        
        if start_i >= end_i:
            return signals
        
        for i in range(start_i, end_i):
            prev_close = df['close'].iloc[i-1]
            curr_close = df['close'].iloc[i]
            swing_high_prev = df['SwingHigh'].iloc[i-1]
            swing_low_prev = df['SwingLow'].iloc[i-1]
            vol_ratio = df['VolRatio'].iloc[i]
            range_val = df['Range'].iloc[i]
            avg_range = df['AvgRange'].iloc[i]
            curr_open = df['open'].iloc[i]
            timestamp = df['timestamp'].iloc[i] if 'timestamp' in df.columns else df.index[i]
            
            if (pd.isna(swing_high_prev) or pd.isna(swing_low_prev) or 
                pd.isna(vol_ratio) or pd.isna(range_val)):
                continue
            
            strong_bull = (curr_close > curr_open) or (
                range_val > avg_range if not pd.isna(avg_range) else False
            )
            strong_bear = (curr_close < curr_open) or (
                range_val > avg_range if not pd.isna(avg_range) else False
            )
            
            crosses_above = (prev_close <= swing_high_prev) and (curr_close > swing_high_prev)
            crosses_below = (prev_close >= swing_low_prev) and (curr_close < swing_low_prev)
            
            if crosses_above and (vol_ratio >= VOL_MULT) and strong_bull:
                signal = self._create_breakout_signal(
                    df, symbol, i, timestamp, swing_high_prev, vol_ratio, require_exit_price
                )
                if signal:
                    signals.append(signal)
            
            if crosses_below and (vol_ratio >= VOL_MULT) and strong_bear:
                signal = self._create_breakdown_signal(
                    df, symbol, i, timestamp, swing_low_prev, vol_ratio, require_exit_price
                )
                if signal:
                    signals.append(signal)
        
        return signals
    
    def _create_breakout_signal(
        self,
        df: pd.DataFrame,
        symbol: str,
        idx: int,
        timestamp: datetime,
        swing_high: float,
        vol_ratio: float,
        require_exit_price: bool
    ) -> Signal:
        """Create breakout signal."""
        curr_close = df['close'].iloc[idx]
        entry_price = df['open'].iloc[idx+1] if idx + 1 < len(df) else curr_close
        
        exit_price = None
        if require_exit_price and idx + HOLD_BARS < len(df):
            exit_price = df['close'].iloc[idx + HOLD_BARS]
        
        return Signal(
            symbol=symbol,
            signal_type='BREAKOUT',
            price=curr_close,
            swing_level=swing_high,
            vol_ratio=vol_ratio,
            timestamp=timestamp
        )
    
    def _create_breakdown_signal(
        self,
        df: pd.DataFrame,
        symbol: str,
        idx: int,
        timestamp: datetime,
        swing_low: float,
        vol_ratio: float,
        require_exit_price: bool
    ) -> Signal:
        """Create breakdown signal."""
        curr_close = df['close'].iloc[idx]
        entry_price = df['open'].iloc[idx+1] if idx + 1 < len(df) else curr_close
        
        exit_price = None
        if require_exit_price and idx + HOLD_BARS < len(df):
            exit_price = df['close'].iloc[idx + HOLD_BARS]
        
        return Signal(
            symbol=symbol,
            signal_type='BREAKDOWN',
            price=curr_close,
            swing_level=swing_low,
            vol_ratio=vol_ratio,
            timestamp=timestamp
        )

