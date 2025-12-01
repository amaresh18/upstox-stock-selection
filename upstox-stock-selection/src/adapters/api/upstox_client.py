"""Upstox API client adapter."""

import urllib.parse
from datetime import datetime, date
from typing import Optional, Tuple
import pandas as pd
import aiohttp
from pytz import timezone

from ...config.settings import UPSTOX_BASE_URL, TIMEZONE


class UpstoxClient:
    """Client for Upstox API v3."""
    
    def __init__(self, api_key: str, access_token: str, verbose: bool = False):
        """
        Initialize Upstox client.
        
        Args:
            api_key: Upstox API key
            access_token: Upstox access token
            verbose: Enable verbose logging
        """
        self.api_key = api_key
        self.access_token = access_token
        self.verbose = verbose
        self.ist = timezone(TIMEZONE)
    
    def _interval_to_upstox_format(self, interval: str) -> Tuple[str, int]:
        """Convert interval string to Upstox API format."""
        interval = interval.lower().strip()
        
        if interval.endswith('m'):
            return ("minutes", int(interval[:-1]))
        elif interval.endswith('h'):
            return ("hours", int(interval[:-1]))
        elif interval.endswith('d'):
            return ("day", int(interval[:-1]))
        else:
            return ("hours", 1)
    
    async def fetch_historical_data(
        self,
        instrument_key: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data from Upstox API.
        
        Args:
            instrument_key: Upstox instrument key
            start_date: Start date
            end_date: End date
            interval: Time interval
            
        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
            
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            encoded_key = urllib.parse.quote(instrument_key, safe='')
            unit, interval_value = self._interval_to_upstox_format(interval)
            
            url = f"{UPSTOX_BASE_URL}/historical-candle/{encoded_key}/{unit}/{interval_value}/{end_str}/{start_str}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        candles = self._extract_candles(data)
                        
                        if candles:
                            return self._candles_to_dataframe(candles)
            
            return None
            
        except Exception as e:
            if self.verbose:
                print(f"Error fetching historical data: {e}")
            return None
    
    async def fetch_intraday_data(
        self,
        instrument_key: str,
        target_date: date = None,
        interval: str = "1h"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch intraday data from Upstox API.
        
        Args:
            instrument_key: Upstox instrument key
            target_date: Target date (None for today)
            interval: Time interval
            
        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            encoded_key = urllib.parse.quote(instrument_key, safe='')
            unit, interval_value = self._interval_to_upstox_format(interval)
            
            today = datetime.now(self.ist).date()
            is_today = target_date is None or target_date == today
            
            if target_date and not is_today:
                date_str = target_date.strftime("%Y-%m-%d")
                url = f"{UPSTOX_BASE_URL}/historical-candle/{encoded_key}/{unit}/{interval_value}/{date_str}/{date_str}"
            else:
                url = f"{UPSTOX_BASE_URL}/historical-candle/intraday/{encoded_key}/{unit}/{interval_value}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        candles = self._extract_candles(data)
                        
                        if candles:
                            return self._candles_to_dataframe(candles)
            
            return None
            
        except Exception as e:
            if self.verbose:
                print(f"Error fetching intraday data: {e}")
            return None
    
    def _extract_candles(self, data: dict) -> Optional[list]:
        """Extract candles from API response."""
        if 'data' in data:
            if 'candles' in data['data']:
                return data['data']['candles']
            elif isinstance(data['data'], list):
                return data['data']
        elif isinstance(data, list):
            return data
        return None
    
    def _candles_to_dataframe(self, candles: list) -> pd.DataFrame:
        """Convert candles list to DataFrame."""
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
        
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            if df['timestamp'].isna().any():
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
        except:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
        
        if df['timestamp'].dt.tz is None:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(self.ist)
        else:
            df['timestamp'] = df['timestamp'].dt.tz_convert(self.ist)
        
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        if df.empty:
            return pd.DataFrame()
        
        df = df.set_index('timestamp')
        df.index.name = 'timestamp'
        return df[['open', 'high', 'low', 'close', 'volume']].copy()

