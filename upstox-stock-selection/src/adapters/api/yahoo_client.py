"""Yahoo Finance API client adapter."""

from datetime import date
from typing import Dict, List
import pandas as pd
import yfinance as yf
from pytz import timezone

from ...config.settings import TIMEZONE


class YahooFinanceClient:
    """Client for Yahoo Finance API."""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize Yahoo Finance client.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.ist = timezone(TIMEZONE)
    
    def batch_download(
        self,
        symbols: List[str],
        days: int,
        interval: str = "1h"
    ) -> Dict[str, pd.DataFrame]:
        """
        Batch download historical data for multiple symbols.
        
        Args:
            symbols: List of NSE symbols (without .NS suffix)
            days: Number of days of historical data
            interval: Time interval
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        yf_symbols = [f"{symbol}.NS" for symbol in symbols]
        historical_data = {}
        
        try:
            raw = yf.download(
                tickers=" ".join(yf_symbols),
                interval=interval,
                period=f"{days}d",
                group_by="ticker",
                auto_adjust=False,
                threads=True,
                progress=False,
            )
            
            for symbol in symbols:
                yf_symbol = f"{symbol}.NS"
                try:
                    df = raw[yf_symbol].dropna().copy()
                    
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    for col in ["Open", "High", "Low", "Close", "Volume"]:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors="coerce")
                    
                    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
                    
                    if df.empty:
                        continue
                    
                    try:
                        if df.index.tz is None:
                            df.index = df.index.tz_localize("UTC").tz_convert(self.ist)
                        else:
                            df.index = df.index.tz_convert(self.ist)
                    except Exception:
                        pass
                    
                    df.columns = [col.lower() for col in df.columns]
                    available_cols = ['open', 'high', 'low', 'close', 'volume']
                    cols_to_use = [col for col in available_cols if col in df.columns]
                    
                    if 'volume' not in cols_to_use:
                        df['volume'] = 0
                        cols_to_use.append('volume')
                    
                    df = df[cols_to_use].copy()
                    df['timestamp'] = df.index
                    df = df.reset_index(drop=True)
                    
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df = df.dropna(subset=['open', 'high', 'low', 'close'])
                    
                    today_date = date.today()
                    df = df[df['timestamp'].dt.date < today_date]
                    
                    if len(df) > 0:
                        historical_data[symbol] = df
                        
                except Exception:
                    continue
            
            return historical_data
            
        except Exception as e:
            if self.verbose:
                print(f"Error in batch download: {e}")
            return {}

