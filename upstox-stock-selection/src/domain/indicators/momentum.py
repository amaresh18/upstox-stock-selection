"""Momentum indicator calculations."""

import pandas as pd
import numpy as np


def calculate_momentum_indicators(
    df: pd.DataFrame,
    interval: str,
    close_col: str = 'close'
) -> pd.DataFrame:
    """
    Calculate momentum-based indicators.
    
    Args:
        df: DataFrame with OHLCV data
        interval: Time interval string (e.g., '1h', '15m')
        close_col: Column name for close prices
        
    Returns:
        DataFrame with added momentum indicator columns
    """
    result = df.copy()
    
    result['PriceMomentum'] = result[close_col].pct_change() * 100.0
    
    candles_per_day = _calculate_candles_per_day(interval)
    momentum_window = max(1, candles_per_day * 7)
    
    if len(result) >= momentum_window:
        result['AvgPriceMomentum7d'] = result['PriceMomentum'].rolling(window=momentum_window).mean()
    else:
        result['AvgPriceMomentum7d'] = np.nan
    
    result['MomentumRatio'] = result['PriceMomentum'] / result['AvgPriceMomentum7d'].replace(0, np.nan)
    result['MomentumRatio'] = result['MomentumRatio'].replace([np.inf, -np.inf], np.nan)
    
    return result


def _calculate_candles_per_day(interval: str) -> int:
    """Calculate number of candles per trading day for given interval."""
    interval = interval.lower().strip()
    
    if interval.endswith('m'):
        minutes = int(interval[:-1])
        return int(375 / minutes) if minutes > 0 else 7
    elif interval.endswith('h'):
        hours = int(interval[:-1])
        return 7 if hours == 1 else max(1, int(6.25 / hours))
    elif interval.endswith('d'):
        return 1
    else:
        return 7

