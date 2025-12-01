"""Swing high/low indicator calculation."""

import pandas as pd
import numpy as np


def calculate_swing_levels(
    df: pd.DataFrame,
    lookback: int,
    high_col: str = 'high',
    low_col: str = 'low'
) -> pd.DataFrame:
    """
    Calculate swing high and swing low levels.
    
    Args:
        df: DataFrame with OHLCV data
        lookback: Number of bars for swing calculation
        high_col: Column name for high prices
        low_col: Column name for low prices
        
    Returns:
        DataFrame with added 'SwingHigh' and 'SwingLow' columns
    """
    result = df.copy()
    
    result['SwingHigh'] = result[high_col].rolling(window=lookback).max() * 0.995
    result['SwingLow'] = result[low_col].rolling(window=lookback).min() * 1.005
    
    return result

