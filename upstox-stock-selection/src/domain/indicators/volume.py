"""Volume indicator calculations."""

import pandas as pd


def calculate_volume_indicators(
    df: pd.DataFrame,
    vol_window: int,
    volume_col: str = 'volume'
) -> pd.DataFrame:
    """
    Calculate volume-based indicators.
    
    Args:
        df: DataFrame with OHLCV data
        vol_window: Window for average volume calculation
        volume_col: Column name for volume
        
    Returns:
        DataFrame with added volume indicator columns
    """
    result = df.copy()
    
    result['AvgVol10d'] = result[volume_col].rolling(window=vol_window).mean()
    result['VolRatio'] = result[volume_col] / result['AvgVol10d']
    
    return result

