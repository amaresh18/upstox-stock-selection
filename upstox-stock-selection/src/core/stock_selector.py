"""
Core stock selection module using Upstox API v3.

This module implements the main UpstoxStockSelector class that analyzes stocks
for breakout and breakdown signals based on swing high/low, volume analysis, and candle patterns.
"""

import json
import os
import urllib.parse
import traceback
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple

import aiohttp
import pandas as pd
import numpy as np
from pytz import timezone
import yfinance as yf

from ..config import settings
from ..config.settings import (
    UPSTOX_BASE_URL,
    DEFAULT_HISTORICAL_DAYS,
    DEFAULT_INTERVAL,
    DEFAULT_MAX_WORKERS,
    TIMEZONE,
    DEFAULT_NSE_JSON_PATH,
)


class UpstoxStockSelector:
    """Stock selection system using Upstox API v3."""
    
    def __init__(self, api_key: str, access_token: str, nse_json_path: str = None):
        """
        Initialize the stock selector.
        
        Args:
            api_key: Upstox API key
            access_token: Upstox access token
            nse_json_path: Path to NSE.json file with instrument mappings
        """
        self.api_key = api_key
        self.access_token = access_token
        self.nse_json_path = nse_json_path or DEFAULT_NSE_JSON_PATH
        self.ist = timezone(TIMEZONE)
        self.instrument_map = self._load_instrument_map()
        self.alerts = []
        self.summary_stats = []
        self.yf_historical_data = {}  # Cache for Yahoo Finance batch downloaded data
    
    def _interval_to_upstox_format(self, interval: str) -> Tuple[str, int]:
        """
        Convert interval string to Upstox API format (unit, interval_value).
        
        Args:
            interval: Interval string like "1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d"
            
        Returns:
            Tuple of (unit, interval_value) where unit is "minutes" or "hours" or "day"
        """
        interval = interval.lower().strip()
        
        if interval.endswith('m'):
            # Minutes: 1m, 5m, 10m, 15m, 30m
            minutes = int(interval[:-1])
            return ("minutes", minutes)
        elif interval.endswith('h'):
            # Hours: 1h, 2h, 4h
            hours = int(interval[:-1])
            return ("hours", hours)
        elif interval.endswith('d'):
            # Days: 1d
            days = int(interval[:-1])
            return ("day", days)
        else:
            # Default to 1 hour
            return ("hours", 1)
        
    def _load_instrument_map(self) -> Dict[str, str]:
        """
        Load NSE symbol to Upstox instrument key mapping from NSE.json.
        
        Returns:
            Dictionary mapping NSE symbols to Upstox instrument keys
        """
        try:
            if not os.path.exists(self.nse_json_path):
                raise FileNotFoundError(
                    f"NSE.json file not found at {self.nse_json_path}. "
                    "Please create this file with instrument mappings."
                )
            
            with open(self.nse_json_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # If it's a list of instruments
                instrument_map = {}
                for item in data:
                    if 'tradingsymbol' in item and 'instrument_key' in item:
                        symbol = item['tradingsymbol']
                        instrument_key = item['instrument_key']
                        instrument_map[symbol] = instrument_key
                return instrument_map
            elif isinstance(data, dict):
                # If it's a dictionary with symbol -> instrument_key mapping
                return data
            else:
                raise ValueError("Invalid NSE.json format")
                
        except Exception as e:
            print(f"Error loading instrument map: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {}
    
    def _get_instrument_key(self, symbol: str) -> Optional[str]:
        """
        Get Upstox instrument key for an NSE symbol.
        
        Args:
            symbol: NSE trading symbol
            
        Returns:
            Upstox instrument key or None if not found
        """
        # Try exact match first
        if symbol in self.instrument_map:
            return self.instrument_map[symbol]
        
        # Try with NSE exchange suffix
        nse_symbol = f"NSE_EQ|{symbol}"
        if nse_symbol in self.instrument_map:
            return self.instrument_map[nse_symbol]
        
        # Try case-insensitive match
        for key, value in self.instrument_map.items():
            if key.upper() == symbol.upper():
                return value
        
        return None
    
    def _batch_download_yahoo_finance(self, symbols: List[str], days: int = None) -> Dict[str, pd.DataFrame]:
        """
        Batch download historical data from Yahoo Finance for all symbols.
        Uses yf.download() for efficient batch downloading.
        
        Args:
            symbols: List of NSE symbols (without .NS suffix)
            days: Number of days of historical data to fetch
            
        Returns:
            Dictionary mapping symbol to DataFrame with historical data
        """
        if days is None:
            days = DEFAULT_HISTORICAL_DAYS
        
        # Get interval from settings (read fresh each time)
        yf_interval = settings.DEFAULT_INTERVAL
        print(f"Batch downloading historical data from Yahoo Finance for {len(symbols)} symbols...")
        print(f"  Using interval: {yf_interval}, days: {days}")
        
        # Convert symbols to Yahoo Finance format (SYMBOL.NS)
        yf_symbols = [f"{symbol}.NS" for symbol in symbols]
        
        try:
            # Batch download using yf.download() - more efficient than individual downloads
            raw = yf.download(
                tickers=" ".join(yf_symbols),
                interval=yf_interval,
                period=f"{days}d",
                group_by="ticker",
                auto_adjust=False,
                threads=True,
                progress=False,
            )
            
            # Process each symbol's data
            historical_data = {}
            
            for symbol in symbols:
                yf_symbol = f"{symbol}.NS"
                try:
                    df = raw[yf_symbol].dropna().copy()
                    
                    # Flatten unexpected multiindex
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    # Ensure numeric
                    for c in ["Open", "High", "Low", "Close", "Volume"]:
                        if c in df.columns:
                            df[c] = pd.to_numeric(df[c], errors="coerce")
                    
                    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
                    
                    if df.empty:
                        continue
                    
                    # Convert to IST timezone
                    try:
                        if df.index.tz is None:
                            df.index = df.index.tz_localize("UTC").tz_convert(self.ist)
                        else:
                            df.index = df.index.tz_convert(self.ist)
                    except Exception:
                        pass
                    
                    # Rename columns to lowercase
                    df.columns = [col.lower() for col in df.columns]
                    
                    # Select only OHLCV columns
                    available_cols = ['open', 'high', 'low', 'close', 'volume']
                    cols_to_use = [col for col in available_cols if col in df.columns]
                    
                    if 'volume' not in cols_to_use:
                        df['volume'] = 0
                        cols_to_use.append('volume')
                    
                    df = df[cols_to_use].copy()
                    df['timestamp'] = df.index
                    df = df.reset_index(drop=True)
                    
                    # Ensure all numeric columns are numeric
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Remove rows with NaN values in OHLC
                    df = df.dropna(subset=['open', 'high', 'low', 'close'])
                    
                    # Filter to only include data before today (to avoid duplicates with Upstox)
                    today_date = datetime.now(self.ist).date()
                    df = df[df['timestamp'].dt.date < today_date]
                    
                    if len(df) > 0:
                        historical_data[symbol] = df
                        print(f"  Got {len(df)} bars from Yahoo Finance for {symbol} (excluding today)")
                    
                except Exception as e:
                    # Symbol not found in batch download, skip it
                    continue
            
            print(f"Successfully downloaded historical data for {len(historical_data)} symbols")
            return historical_data
            
        except Exception as e:
            print(f"Error in batch download from Yahoo Finance: {e}")
            traceback.print_exc()
            return {}
    
    async def _fetch_historical_data(
        self, 
        instrument_key: str, 
        symbol: str,
        days: int = None,
        target_date: date = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch 1-hour OHLCV historical data using hybrid approach:
        - Historical data (30 days) from Yahoo Finance (from batch download cache)
        - Current day data from Upstox API (or specific date if target_date provided)
        
        Args:
            instrument_key: Upstox instrument key
            symbol: Trading symbol (for reference)
            days: Number of days of historical data to fetch
            target_date: Specific date to analyze. If None, uses current date.
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        if days is None:
            days = DEFAULT_HISTORICAL_DAYS
        
        print(f"  Fetching historical data for {symbol} with {days} days of history")
            
        try:
            # Use target_date if provided, otherwise use current date
            if target_date:
                # Use target date at market close time (3:30 PM)
                end_date = self.ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=15, minute=30)))
            else:
                end_date = datetime.now(self.ist)
            
            # Step 1: Get historical data from Yahoo Finance (from batch download cache)
            # Note: The batch download should have used the same 'days' parameter
            hist_df = pd.DataFrame()
            if symbol in self.yf_historical_data:
                hist_df = self.yf_historical_data[symbol].copy()
                print(f"  Using cached Yahoo Finance data for {symbol}: {len(hist_df)} bars (requested {days} days)")
            else:
                print(f"  Warning: No Yahoo Finance data found for {symbol} in cache")
            
            # Step 2: Fetch historical data from Upstox API (if Yahoo Finance failed or not available)
            if hist_df.empty and self.access_token and self.access_token != 'dummy':
                print(f"  Fetching historical data from Upstox API for {symbol} (last {days} days)...")
                try:
                    start_date = end_date - timedelta(days=days)
                    hist_upstox = await self._fetch_historical_data_from_upstox_api(
                        instrument_key, symbol, start_date, end_date
                    )
                    if hist_upstox is not None and not hist_upstox.empty:
                        # Exclude today's data (will fetch separately)
                        today_date = end_date.date()
                        hist_upstox = hist_upstox[hist_upstox.index.date < today_date]
                        if not hist_upstox.empty:
                            hist_df = hist_upstox.copy()
                            print(f"Got {len(hist_df)} historical bars from Upstox API for {symbol}")
                except Exception as e:
                    print(f"Error fetching historical data from Upstox for {symbol}: {e}")
            
            # Step 3: Fetch current day data from Upstox API (or specific date)
            today_df = None
            if self.access_token and self.access_token != 'dummy':
                if target_date:
                    print(f"Fetching data for {target_date.strftime('%Y-%m-%d')} from Upstox for {symbol}...")
                else:
                    print(f"Fetching current day data from Upstox for {symbol}...")
                try:
                    today_df = await self._fetch_today_data_from_upstox_api(instrument_key, symbol, target_date=target_date)
                    if today_df is not None and not today_df.empty:
                        if target_date:
                            print(f"Got {len(today_df)} bars from Upstox for {symbol} ({target_date.strftime('%Y-%m-%d')})")
                        else:
                            print(f"Got {len(today_df)} bars from Upstox for {symbol} (today)")
                except Exception as e:
                    print(f"Error fetching data from Upstox for {symbol}: {e}")
                    today_df = None
            
            # Step 4: Combine historical and current day data
            if hist_df.empty and (today_df is None or today_df.empty):
                print(f"No data available for {symbol}")
                return None
            
            # Ensure both dataframes have timestamp as index (not column) for consistency
            if not hist_df.empty:
                if 'timestamp' in hist_df.columns:
                    hist_df = hist_df.set_index('timestamp')
                elif hist_df.index.name != 'timestamp':
                    hist_df.index.name = 'timestamp'
            
            if today_df is not None and not today_df.empty:
                if 'timestamp' in today_df.columns:
                    today_df = today_df.set_index('timestamp')
                elif today_df.index.name != 'timestamp':
                    today_df.index.name = 'timestamp'
            
            # Combine dataframes
            if not hist_df.empty and today_df is not None and not today_df.empty:
                # Remove today's data from historical (if any) to avoid duplicates
                today_date = end_date.date()
                hist_df = hist_df[hist_df.index.date < today_date]
                
                # Combine
                df = pd.concat([hist_df, today_df], ignore_index=False)
            elif not hist_df.empty:
                df = hist_df.copy()
            elif today_df is not None and not today_df.empty:
                df = today_df.copy()
            else:
                return None
            
            # Sort by timestamp index and remove duplicates
            df = df.sort_index()
            before_dedup = len(df)
            df = df[~df.index.duplicated(keep='first')]
            after_dedup = len(df)
            if before_dedup != after_dedup:
                print(f"  Removed {before_dedup - after_dedup} duplicate timestamps for {symbol}")
            
            # Filter out incomplete candles (current hour's candle that hasn't completed yet)
            # A candle at hour H completes at hour H+1 (e.g., 9:15 candle completes at 10:15)
            # So if current time is 10:15:30, we should exclude the 10:15 candle (still forming)
            if not target_date:  # Only for real-time (not historical backtesting)
                now = datetime.now(self.ist)
                current_hour = now.hour
                current_minute = now.minute
                current_second = now.second
                
                # Market hours: 9:15 AM - 3:30 PM IST
                market_hours = [9, 10, 11, 12, 13, 14, 15]
                
                # Determine the cutoff time for incomplete candles
                # If it's 10:15:30, exclude candles >= 10:15 (current hour)
                # If it's 10:20, exclude candles >= 10:15 (current hour)
                if current_hour in market_hours:
                    # Exclude current hour's candle (it's still forming)
                    cutoff_time = now.replace(minute=15, second=0, microsecond=0)
                    # Only filter if we're past 15 minutes of current hour
                    if current_minute > 15 or (current_minute == 15 and current_second >= 30):
                        before_filter = len(df)
                        df = df[df.index < cutoff_time]
                        after_filter = len(df)
                        if before_filter != after_filter:
                            print(f"  Filtered out {before_filter - after_filter} incomplete candle(s) for {symbol} (current hour: {current_hour}:15)")
            
            # Ensure we have enough data points (at least 70 bars for calculations)
            if len(df) < settings.VOL_WINDOW:
                print(f"Insufficient data for {symbol}: {len(df)} bars (need at least {settings.VOL_WINDOW})")
                return None
            
            # Ensure timestamp is the index
            if df.index.name != 'timestamp':
                df.index.name = 'timestamp'
            
            # Add timestamp as column for _detect_signals method (only if not already present)
            if 'timestamp' not in df.columns:
                df['timestamp'] = df.index
            
            print(f"Combined data for {symbol}: {len(df)} bars (Historical: {len(hist_df) if not hist_df.empty else 0}, Today: {len(today_df) if today_df is not None and not today_df.empty else 0})")
            return df
                        
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def _fetch_historical_data_from_upstox_api(
        self,
        instrument_key: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data from Upstox API v3 for a specific period.
        Uses the latest Upstox API v3 endpoint format.
        
        Args:
            instrument_key: Upstox instrument key
            symbol: Trading symbol (for reference)
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
            
            # Format dates for API
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            # Encode instrument key for URL
            encoded_instrument_key = urllib.parse.quote(instrument_key, safe='')
            
            # Use Upstox API v3 endpoint with configured interval
            # Format: /historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}
            # Note: to_date comes before from_date in the path
            # Read interval fresh from settings
            current_interval = settings.DEFAULT_INTERVAL
            unit, interval_value = self._interval_to_upstox_format(current_interval)
            print(f"  Fetching historical data for {symbol} with interval: {current_interval} ({unit}/{interval_value})")
            url = f"{UPSTOX_BASE_URL}/historical-candle/{encoded_instrument_key}/{unit}/{interval_value}/{end_str}/{start_str}"
            params = {}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Handle different response structures
                        candles = None
                        if 'data' in data:
                            if 'candles' in data['data']:
                                candles = data['data']['candles']
                            elif isinstance(data['data'], list):
                                candles = data['data']
                        elif isinstance(data, list):
                            candles = data
                        
                        if candles and len(candles) > 0:
                            # Convert to DataFrame
                            # Upstox API returns: [timestamp, open, high, low, close, volume, oi]
                            hist_df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
                            
                            # Convert timestamp (can be in milliseconds or ISO format)
                            try:
                                # Try parsing as ISO string first
                                hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'], errors='coerce')
                                # If that fails, try milliseconds
                                if hist_df['timestamp'].isna().any():
                                    hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'], unit='ms', errors='coerce')
                            except:
                                # Fallback to milliseconds
                                hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'], unit='ms', errors='coerce')
                            
                            # Ensure timezone is IST
                            if hist_df['timestamp'].dt.tz is None:
                                hist_df['timestamp'] = hist_df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(self.ist)
                            else:
                                hist_df['timestamp'] = hist_df['timestamp'].dt.tz_convert(self.ist)
                            
                            # Convert OHLCV to float
                            for col in ['open', 'high', 'low', 'close', 'volume']:
                                hist_df[col] = pd.to_numeric(hist_df[col], errors='coerce')
                            
                            # Remove rows with NaN values in OHLC
                            hist_df = hist_df.dropna(subset=['open', 'high', 'low', 'close'])
                            
                            if hist_df.empty:
                                return None
                            
                            # Set timestamp as index
                            hist_df = hist_df.set_index('timestamp')
                            hist_df.index.name = 'timestamp'
                            
                            # Select only OHLCV columns
                            hist_df = hist_df[['open', 'high', 'low', 'close', 'volume']].copy()
                            
                            return hist_df
                    else:
                        error_text = await response.text()
                        print(f"  Upstox API error for {symbol}: Status {response.status}, {error_text[:200]}")
            return None
            
        except Exception as e:
            print(f"  Error fetching historical data from Upstox for {symbol}: {e}")
            traceback.print_exc()
            return None
    
    async def _fetch_today_data_from_upstox_api(
        self,
        instrument_key: str,
        symbol: str,
        target_date: date = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch today's data from Upstox API v3 using Intraday Candle Data API.
        
        This uses the dedicated Intraday API endpoint which automatically returns
        current trading day data without requiring date parameters.
        
        For specific dates, uses the historical candle API with date parameters.
        
        API Documentation: https://upstox.com/developer/api-documentation/v3/get-intra-day-candle-data
        
        Args:
            instrument_key: Upstox instrument key
            symbol: Trading symbol (for reference)
            target_date: Specific date to fetch. If None, fetches current day.
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            encoded_instrument_key = urllib.parse.quote(instrument_key, safe='')
            
            # Get interval from settings (read fresh each time)
            current_interval = settings.DEFAULT_INTERVAL
            unit, interval_value = self._interval_to_upstox_format(current_interval)
            
            # Check if target_date is today
            today = datetime.now(self.ist).date()
            is_today = target_date is None or target_date == today
            
            if target_date and not is_today:
                # For historical dates (not today), use historical candle API with date range
                # Format: /historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}
                date_str = target_date.strftime("%Y-%m-%d")
                print(f"  Fetching data for {symbol} on {date_str} with interval: {current_interval} ({unit}/{interval_value})")
                url = f"{UPSTOX_BASE_URL}/historical-candle/{encoded_instrument_key}/{unit}/{interval_value}/{date_str}/{date_str}"
            else:
                # Use Upstox API v3 Intraday Candle Data endpoint for current day
                # Format: /historical-candle/intraday/{instrument_key}/{unit}/{interval}
                # This API automatically returns current trading day data
                if target_date:
                    print(f"  Fetching intraday data for {symbol} (today: {target_date.strftime('%Y-%m-%d')}) with interval: {current_interval} ({unit}/{interval_value})")
                else:
                    print(f"  Fetching intraday data for {symbol} with interval: {current_interval} ({unit}/{interval_value})")
                url = f"{UPSTOX_BASE_URL}/historical-candle/intraday/{encoded_instrument_key}/{unit}/{interval_value}"
            
            params = {}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Handle different response structures
                        candles = None
                        if 'data' in data:
                            if 'candles' in data['data']:
                                candles = data['data']['candles']
                            elif isinstance(data['data'], list):
                                candles = data['data']
                        elif isinstance(data, list):
                            candles = data
                        
                        if candles and len(candles) > 0:
                            # Convert to DataFrame
                            today_df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
                            
                            # Convert timestamp
                            try:
                                today_df['timestamp'] = pd.to_datetime(today_df['timestamp'], errors='coerce')
                                if today_df['timestamp'].isna().any():
                                    today_df['timestamp'] = pd.to_datetime(today_df['timestamp'], unit='ms', errors='coerce')
                            except:
                                today_df['timestamp'] = pd.to_datetime(today_df['timestamp'], unit='ms', errors='coerce')
                            
                            # Ensure timezone is IST
                            if today_df['timestamp'].dt.tz is None:
                                today_df['timestamp'] = today_df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(self.ist)
                            else:
                                today_df['timestamp'] = today_df['timestamp'].dt.tz_convert(self.ist)
                            
                            # Convert OHLCV to float
                            for col in ['open', 'high', 'low', 'close', 'volume']:
                                today_df[col] = pd.to_numeric(today_df[col], errors='coerce')
                            
                            # Remove rows with NaN values in OHLC
                            today_df = today_df.dropna(subset=['open', 'high', 'low', 'close'])
                            
                            if today_df.empty:
                                return None
                            
                            # Set timestamp as index
                            today_df = today_df.set_index('timestamp')
                            today_df.index.name = 'timestamp'
                            
                            # Select only OHLCV columns
                            today_df = today_df[['open', 'high', 'low', 'close', 'volume']].copy()
                            
                            return today_df
                    else:
                        error_text = await response.text()
                        print(f"  Upstox API error for {symbol} (today): Status {response.status}, {error_text[:200]}")
            return None
            
        except Exception as e:
            print(f"Error fetching today's data from Upstox for {symbol}: {e}")
            traceback.print_exc()
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all derived indicators needed for stock selection.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with calculated indicators
        """
        # Get current settings values (dynamically from settings module)
        # Read fresh each time to ensure we get the latest values
        lookback_swing = settings.LOOKBACK_SWING
        vol_window = settings.VOL_WINDOW
        print(f"  Calculating indicators with Lookback Swing: {lookback_swing}, Volume Window: {vol_window}")
        
        # Swing High = rolling max High over lookback_swing bars * 0.995
        # Match reference: no min_periods (uses all available data)
        df['SwingHigh'] = df['high'].rolling(window=lookback_swing).max() * 0.995
        
        # Swing Low = rolling min Low over lookback_swing bars * 1.005
        # Match reference: no min_periods (uses all available data)
        df['SwingLow'] = df['low'].rolling(window=lookback_swing).min() * 1.005
        
        # Average volume over vol_window bars
        # Match reference: no min_periods (uses all available data)
        df['AvgVol10d'] = df['volume'].rolling(window=vol_window).mean()
        
        # Volume ratio
        df['VolRatio'] = df['volume'] / df['AvgVol10d']
        
        # Range = High - Low
        df['Range'] = df['high'] - df['low']
        
        # Average range (rolling mean over lookback_swing bars)
        # Match reference: no min_periods (uses all available data)
        df['AvgRange'] = df['Range'].rolling(window=lookback_swing).mean()
        
        return df
    
    def _detect_signals(self, df: pd.DataFrame, symbol: str, require_exit_price: bool = False) -> List[Dict]:
        """
        Detect breakout and breakdown signals.
        
        Uses PREVIOUS bar's swing high/low for comparison (not current bar).
        Start index = max(LOOKBACK_SWING, VOL_WINDOW) + 1 = max(12, 70) + 1 = 71
        
        Args:
            df: DataFrame with OHLCV and calculated indicators
            symbol: Trading symbol
            require_exit_price: If True, only detect signals where exit price can be calculated (for backtesting).
                               If False, detect all signals including real-time (for live alerts).
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Get current settings values (dynamically from settings module)
        # Read fresh each time to ensure we get the latest values
        lookback_swing = settings.LOOKBACK_SWING
        vol_window = settings.VOL_WINDOW
        vol_mult = settings.VOL_MULT
        hold_bars = settings.HOLD_BARS
        
        print(f"  Detecting signals with Lookback Swing: {lookback_swing}, Volume Window: {vol_window}, Volume Multiplier: {vol_mult}, Hold Bars: {hold_bars}")
        
        # Start index: max(LOOKBACK_SWING, VOL_WINDOW) + 1
        # Match reference: int(max(LOOKBACK_SWING, VOL_WINDOW)) + 1
        start_i = int(max(lookback_swing, vol_window)) + 1
        
        # End index: 
        # - For backtesting: len(df) - HOLD_BARS to ensure we have enough bars for exit price
        # - For real-time: len(df) to allow checking all bars (exit price optional)
        if require_exit_price:
            end_i = len(df) - hold_bars
        else:
            end_i = len(df)  # Allow checking all bars for real-time alerts
        
        if start_i >= end_i:
            return alerts  # Not enough data
        
        for i in range(start_i, end_i):
            prev_close = df['close'].iloc[i-1]
            curr_close = df['close'].iloc[i]
            
            # CRITICAL: Use PREVIOUS bar's swing high/low (matches reference code)
            swing_high_prev = df['SwingHigh'].iloc[i-1]
            swing_low_prev = df['SwingLow'].iloc[i-1]
            
            vol_ratio = df['VolRatio'].iloc[i]
            range_val = df['Range'].iloc[i]
            avg_range = df['AvgRange'].iloc[i]
            curr_open = df['open'].iloc[i]
            timestamp = df['timestamp'].iloc[i]
            
            # Skip if we don't have valid indicator values
            if (pd.isna(swing_high_prev) or pd.isna(swing_low_prev) or 
                pd.isna(vol_ratio) or pd.isna(range_val)):
                continue
            
            # Strong bullish candle: (close > open) OR (range > avg_range with NaN check)
            strong_bull = (curr_close > curr_open) or (
                range_val > avg_range if not pd.isna(avg_range) else False
            )
            
            # Strong bearish candle: (close < open) OR (range > avg_range with NaN check)
            strong_bear = (curr_close < curr_open) or (
                range_val > avg_range if not pd.isna(avg_range) else False
            )
            
            # Breakout condition: crosses above PREVIOUS bar's swing high
            crosses_above = (prev_close <= swing_high_prev) and (curr_close > swing_high_prev)
            
            if crosses_above and (vol_ratio >= vol_mult) and strong_bull:
                # Entry: next bar's open (i+1) if available, else current close
                if i + 1 < len(df):
                    entry_price = df['open'].iloc[i+1]
                else:
                    entry_price = curr_close
                
                # Exit price and P&L calculation
                if require_exit_price:
                    # For backtesting: exit price is required
                    exit_price = df['close'].iloc[i+hold_bars]
                    pnl_pct = ((exit_price - entry_price) / entry_price) * 100.0
                else:
                    # For real-time alerts: exit price not required, set to None
                    if i + hold_bars < len(df):
                        exit_price = df['close'].iloc[i+hold_bars]
                        pnl_pct = ((exit_price - entry_price) / entry_price) * 100.0
                    else:
                        # Not enough bars for exit - this is fine for real-time alerts
                        exit_price = None
                        pnl_pct = None
                
                alerts.append({
                    'symbol': symbol,
                    'timestamp': timestamp,
                    'signal_type': 'BREAKOUT',
                    'price': curr_close,
                    'swing_high': swing_high_prev,
                    'swing_low': swing_low_prev,
                    'vol_ratio': vol_ratio,
                    'range': range_val,
                    'avg_range': avg_range,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl_pct': pnl_pct,
                    'bars_after': hold_bars
                })
            
            # Breakdown condition: crosses below PREVIOUS bar's swing low
            crosses_below = (prev_close >= swing_low_prev) and (curr_close < swing_low_prev)
            
            if crosses_below and (vol_ratio >= vol_mult) and strong_bear:
                # Entry: next bar's open (i+1) if available, else current close
                if i + 1 < len(df):
                    entry_price = df['open'].iloc[i+1]
                else:
                    entry_price = curr_close
                
                # Exit price and P&L calculation
                if require_exit_price:
                    # For backtesting: exit price is required
                    exit_price = df['close'].iloc[i+hold_bars]
                    # For breakdown: (entry - exit) / entry * 100
                    pnl_pct = ((entry_price - exit_price) / entry_price) * 100.0
                else:
                    # For real-time alerts: exit price not required, set to None
                    if i + hold_bars < len(df):
                        exit_price = df['close'].iloc[i+hold_bars]
                        # For breakdown: (entry - exit) / entry * 100
                        pnl_pct = ((entry_price - exit_price) / entry_price) * 100.0
                    else:
                        # Not enough bars for exit - this is fine for real-time alerts
                        exit_price = None
                        pnl_pct = None
                
                alerts.append({
                    'symbol': symbol,
                    'timestamp': timestamp,
                    'signal_type': 'BREAKDOWN',
                    'price': curr_close,
                    'swing_high': swing_high_prev,
                    'swing_low': swing_low_prev,
                    'vol_ratio': vol_ratio,
                    'range': range_val,
                    'avg_range': avg_range,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl_pct': pnl_pct,
                    'bars_after': hold_bars
                })
        
        return alerts
    
    def _calculate_statistics(self, alerts: List[Dict], symbol: str) -> Dict:
        """
        Calculate aggregate statistics for a symbol.
        
        Args:
            alerts: List of alerts for the symbol
            symbol: Trading symbol
            
        Returns:
            Dictionary with statistics
        """
        if not alerts:
            return {
                'symbol': symbol,
                'trade_count': 0,
                'win_rate': 0.0,
                'avg_gain_pct': 0.0,
                'net_pnl_pct': 0.0,
                'profit_factor': 0.0
            }
        
        # Filter out alerts without P&L (real-time alerts without exit price)
        # Only include alerts with valid P&L values for statistics
        pnl_values = [alert.get('pnl_pct') for alert in alerts if alert.get('pnl_pct') is not None and isinstance(alert.get('pnl_pct'), (int, float))]
        
        if not pnl_values:
            # No valid P&L values (all are real-time alerts without exit price)
            return {
                'symbol': symbol,
                'trade_count': len(alerts),
                'win_rate': 0.0,
                'avg_gain_pct': 0.0,
                'net_pnl_pct': 0.0,
                'profit_factor': 0.0
            }
        
        winning_trades = [pnl for pnl in pnl_values if pnl > 0]
        losing_trades = [pnl for pnl in pnl_values if pnl < 0]
        
        trade_count = len(alerts)
        win_rate = (len(winning_trades) / trade_count * 100) if trade_count > 0 else 0.0
        avg_gain_pct = np.mean(pnl_values) if pnl_values else 0.0
        net_pnl_pct = sum(pnl_values)
        
        # Profit factor = sum of winning trades / abs(sum of losing trades)
        total_profit = sum(winning_trades) if winning_trades else 0
        total_loss = abs(sum(losing_trades)) if losing_trades else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else (float('inf') if total_profit > 0 else 0.0)
        
        return {
            'symbol': symbol,
            'trade_count': trade_count,
            'win_rate': round(win_rate, 2),
            'avg_gain_pct': round(avg_gain_pct, 2),
            'net_pnl_pct': round(net_pnl_pct, 2),
            'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 999.99
        }
    
    async def _analyze_symbol(self, symbol: str, target_date: date = None, days: int = None) -> Tuple[List[Dict], Dict]:
        """
        Analyze a single symbol for signals and statistics.
        
        Args:
            symbol: NSE trading symbol
            target_date: Specific date to analyze. If None, uses current date.
            days: Number of days of historical data to fetch
            
        Returns:
            Tuple of (alerts list, statistics dict)
        """
        try:
            # Get instrument key
            instrument_key = self._get_instrument_key(symbol)
            if not instrument_key:
                print(f"Instrument key not found for {symbol}")
                return [], {}
            
            # Fetch historical data with days parameter
            df = await self._fetch_historical_data(instrument_key, symbol, days=days, target_date=target_date)
            if df is None or len(df) == 0:
                return [], {}
            
            # Calculate indicators
            df = self._calculate_indicators(df)
            
            # Detect signals
            alerts = self._detect_signals(df, symbol)
            
            # Calculate statistics
            stats = self._calculate_statistics(alerts, symbol)
            
            return alerts, stats
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return [], {}
    
    async def analyze_symbols(
        self, 
        symbols: List[str], 
        max_workers: int = None, 
        days: int = None,
        target_date: date = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Analyze multiple symbols in parallel using semaphore for concurrency control.
        
        Args:
            symbols: List of NSE trading symbols
            max_workers: Maximum number of parallel workers
            days: Number of days of historical data to fetch
            target_date: Specific date to analyze (YYYY-MM-DD format). If None, uses current date.
            
        Returns:
            Tuple of (summary DataFrame, alerts DataFrame)
        """
        import asyncio
        
        if max_workers is None:
            max_workers = DEFAULT_MAX_WORKERS
        if days is None:
            days = DEFAULT_HISTORICAL_DAYS
        
        # Store target date for use in data fetching
        self.target_date = target_date
        
        print(f"Starting analysis of {len(symbols)} symbols with {max_workers} workers...")
        print(f"Historical days requested: {days}")
        
        # Step 1: Batch download historical data from Yahoo Finance
        print("\n" + "="*80)
        print(f"STEP 1: Batch downloading historical data from Yahoo Finance ({days} days)")
        print("="*80)
        self.yf_historical_data = self._batch_download_yahoo_finance(symbols, days=days)
        
        if not self.yf_historical_data:
            print("Warning: No historical data downloaded from Yahoo Finance. Continuing with Upstox data only...")
        
        print("\n" + "="*80)
        print("STEP 2: Analyzing symbols with Upstox current day data")
        print("="*80)
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_workers)
        
        async def analyze_with_semaphore(symbol: str):
            """Analyze symbol with semaphore control."""
            async with semaphore:
                return await self._analyze_symbol(symbol, target_date=target_date, days=days)
        
        # Create tasks for all symbols
        tasks = [analyze_with_semaphore(symbol) for symbol in symbols]
        
        # Execute tasks with concurrency limit
        results = []
        completed = 0
        
        # Process tasks as they complete
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                results.append(result)
                completed += 1
                if completed % 10 == 0:
                    print(f"Completed {completed}/{len(symbols)} symbols...")
            except Exception as e:
                print(f"Task failed with exception: {e}")
                results.append(([], {}))
                completed += 1
        
        # Aggregate results
        all_alerts = []
        all_stats = []
        
        for alerts, stats in results:
            all_alerts.extend(alerts)
            if stats:
                all_stats.append(stats)
        
        # Create DataFrames
        if all_alerts:
            alerts_df = pd.DataFrame(all_alerts)
            alerts_df = alerts_df.sort_values('timestamp').reset_index(drop=True)
        else:
            alerts_df = pd.DataFrame()
        
        if all_stats:
            summary_df = pd.DataFrame(all_stats)
            summary_df = summary_df.sort_values(['trade_count', 'net_pnl_pct'], ascending=[False, False]).reset_index(drop=True)
        else:
            summary_df = pd.DataFrame()
        
        return summary_df, alerts_df
    
    def print_results(self, summary_df: pd.DataFrame, alerts_df: pd.DataFrame):
        """
        Print formatted results.
        
        Args:
            summary_df: Summary statistics DataFrame
            alerts_df: Alerts DataFrame
        """
        print("\n" + "="*80)
        print("STOCK SELECTION SUMMARY STATISTICS")
        print("="*80)
        
        if summary_df.empty:
            print("No statistics available.")
        else:
            print(f"\nTotal symbols analyzed: {len(summary_df)}")
            print(f"Total trades: {summary_df['trade_count'].sum()}")
            print(f"\nTop 20 symbols by trade count:")
            print(summary_df.head(20).to_string(index=False))
            
            print(f"\n\nTop 20 symbols by net P&L:")
            top_pnl = summary_df.nlargest(20, 'net_pnl_pct')
            print(top_pnl.to_string(index=False))
        
        print("\n" + "="*80)
        print("ALERTS (Sorted by timestamp)")
        print("="*80)
        
        if alerts_df.empty:
            print("No alerts generated.")
        else:
            print(f"\nTotal alerts: {len(alerts_df)}")
            print(f"\nBreakout alerts: {len(alerts_df[alerts_df['signal_type'] == 'BREAKOUT'])}")
            print(f"Breakdown alerts: {len(alerts_df[alerts_df['signal_type'] == 'BREAKDOWN'])}")
            print(f"\nRecent alerts (last 20):")
            print(alerts_df.tail(20).to_string(index=False))
        
        print("\n" + "="*80)

