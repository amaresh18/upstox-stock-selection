"""
Backtesting module for Upstox Stock Selection System.

This module provides backtesting functionality to test the stock selection
strategy on historical data.
"""

import os
import json
import urllib.parse
import traceback
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import aiohttp
import pandas as pd
import numpy as np
from pytz import timezone
import yfinance as yfinance

from .stock_selector import UpstoxStockSelector
from ..config.settings import (
    UPSTOX_BASE_URL,
    TIMEZONE,
    DEFAULT_NSE_JSON_PATH,
    DEFAULT_INTERVAL,
    LOOKBACK_SWING,
    VOL_WINDOW,
    VOL_MULT,
    HOLD_BARS,
)


class Backtester:
    """Backtesting engine for stock selection strategy."""
    
    def __init__(self, api_key: str, access_token: str, nse_json_path: str = None):
        """
        Initialize the backtester.
        
        Args:
            api_key: Upstox API key
            access_token: Upstox access token
            nse_json_path: Path to NSE.json file with instrument mappings
        """
        self.selector = UpstoxStockSelector(api_key, access_token, nse_json_path)
        self.ist = timezone(TIMEZONE)
        self.backtest_results = []
        
    async def _fetch_historical_data_from_upstox(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data from Upstox API v3 for a specific period.
        Uses the latest Upstox API v3 endpoint format.
        
        Args:
            symbol: NSE trading symbol
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        try:
            # Get instrument key
            instrument_key = self.selector._get_instrument_key(symbol)
            if not instrument_key:
                print(f"  ⚠️  No instrument key found for {symbol} in NSE.json")
                return None
            
            headers = {
                "Authorization": f"Bearer {self.selector.access_token}",
                "Accept": "application/json"
            }
            
            # Format dates for API
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            # Encode instrument key for URL - need to encode | as %7C
            # Format: NSE_EQ|INE423A01024 -> NSE_EQ%7CINE423A01024
            encoded_instrument_key = urllib.parse.quote(instrument_key, safe='')
            
            # Use Upstox API v3 endpoint for hourly intraday data
            # Format: /historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}
            # For 1-hour data: unit=hours, interval=1
            # Note: to_date comes before from_date in the path
            url = f"{UPSTOX_BASE_URL}/historical-candle/{encoded_instrument_key}/hours/1/{end_str}/{start_str}"
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
                        print(f"  Upstox API error for {symbol}: Status {response.status}")
                        print(f"    Instrument key used: {instrument_key}")
                        print(f"    Error: {error_text[:300]}")
                        
                        # Check if it's an invalid instrument key error
                        if "UDAPI100011" in error_text or "Invalid Instrument key" in error_text:
                            print(f"    ⚠️  Invalid instrument key for {symbol}. The instrument key may be outdated.")
                            print(f"    💡 The stored instrument key '{instrument_key}' is invalid.")
                            print(f"    💡 Please update NSE.json with correct instrument key for {symbol}")
                            # Store this for summary report
                            if not hasattr(self, 'invalid_instrument_keys'):
                                self.invalid_instrument_keys = []
                            self.invalid_instrument_keys.append({
                                'symbol': symbol,
                                'instrument_key': instrument_key,
                                'error': 'Invalid Instrument key'
                            })
            return None
            
        except Exception as e:
            print(f"  Error fetching historical data from Upstox for {symbol}: {e}")
            traceback.print_exc()
            return None
    
    async def _fetch_today_data_from_upstox(
        self,
        symbol: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch today's data from Upstox API.
        
        Args:
            symbol: NSE trading symbol
            
        Returns:
            DataFrame with today's OHLCV data or None if fetch fails
        """
        try:
            # Get instrument key
            instrument_key = self.selector._get_instrument_key(symbol)
            if not instrument_key:
                return None
            
            headers = {
                "Authorization": f"Bearer {self.selector.access_token}",
                "Accept": "application/json"
            }
            
            encoded_instrument_key = urllib.parse.quote(instrument_key, safe='')
            
            # Use Upstox API v3 Intraday Candle Data endpoint
            # Format: /historical-candle/intraday/{instrument_key}/{unit}/{interval}
            # For 1-hour data: unit=hours, interval=1
            # This API automatically returns current trading day data
            # API Documentation: https://upstox.com/developer/api-documentation/v3/get-intra-day-candle-data
            url = f"{UPSTOX_BASE_URL}/historical-candle/intraday/{encoded_instrument_key}/hours/1"
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
            return None
    
    async def _fetch_historical_data_for_period(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime,
        yf_historical_data: Dict[str, pd.DataFrame] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a specific period using Yahoo Finance (from batch) and Upstox API.
        Includes today's data from Upstox API if end_date is today.
        
        Args:
            symbol: NSE trading symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            yf_historical_data: Pre-fetched Yahoo Finance data from batch download
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        try:
            # Check if end_date is today
            today = datetime.now(self.ist).date()
            end_date_only = end_date.date() if hasattr(end_date, 'date') else end_date
            
            # Step 1: Try Upstox API first (if credentials available)
            hist_df = pd.DataFrame()
            today_date = datetime.now(self.ist).date()
            start_date_only = start_date.date() if hasattr(start_date, 'date') else start_date
            
            if self.selector.access_token and self.selector.access_token != 'dummy':
                # Prioritize Upstox API for historical data
                print(f"  Fetching historical data from Upstox API for {symbol}...")
                # Fetch at least 30 days of historical data (needed for VOL_WINDOW calculation)
                # Even though we're backtesting only the last 7 days, we need more data for indicators
                hist_end_date = today - timedelta(days=1) if end_date_only >= today else end_date_only
                # Fetch 60 days before start_date to ensure we have enough data for calculations
                # (VOL_WINDOW = 70 bars = 10 days * 7 bars/day, so we need at least 10 trading days)
                hist_start_date = start_date - timedelta(days=60)
                
                hist_upstox = await self._fetch_historical_data_from_upstox(
                    symbol, 
                    hist_start_date, 
                    datetime.combine(hist_end_date, datetime.max.time()).replace(tzinfo=self.ist)
                )
                if hist_upstox is not None and not hist_upstox.empty:
                    # Keep ALL historical data for calculations (don't filter yet)
                    # We need at least 30 days of data for VOL_WINDOW calculation
                    # We'll filter alerts to backtest period later
                    hist_df = hist_upstox.copy()
                    print(f"  ✅ Got {len(hist_df)} historical bars from Upstox API for {symbol} (full period for calculations)")
            
            # Step 2: Fallback to Yahoo Finance batch data (if Upstox failed and data available)
            # Also use Yahoo Finance if instrument key is invalid
            if hist_df.empty and yf_historical_data and symbol in yf_historical_data:
                hist_df = yf_historical_data[symbol].copy()
                
                # Filter data to the backtest period (last week)
                # Exclude today's data from Yahoo Finance (we'll get today from Upstox)
                hist_df = hist_df[
                    (hist_df.index.date >= start_date_only) & 
                    (hist_df.index.date < today_date)
                ]
                
                if not hist_df.empty:
                    print(f"  ✅ Using Yahoo Finance data for {symbol}: {len(hist_df)} bars (filtered to backtest period)")
            
            # Step 3: If still no data and Upstox failed due to invalid instrument key, try Yahoo Finance
            if hist_df.empty:
                # Check if we have invalid instrument key error stored
                has_invalid_key = hasattr(self, 'invalid_instrument_keys') and any(
                    item['symbol'] == symbol for item in self.invalid_instrument_keys
                )
                
                if has_invalid_key:
                    print(f"  ⚠️  Invalid instrument key for {symbol}, trying Yahoo Finance fallback...")
                    # Try Yahoo Finance as fallback
                    if yf_historical_data and symbol in yf_historical_data:
                        hist_df = yf_historical_data[symbol].copy()
                        # Filter data to the backtest period
                        hist_df = hist_df[
                            (hist_df.index.date >= start_date_only) & 
                            (hist_df.index.date < today_date)
                        ]
                        if not hist_df.empty:
                            print(f"  ✅ Using Yahoo Finance fallback for {symbol}: {len(hist_df)} bars")
                elif not (self.selector.access_token and self.selector.access_token != 'dummy'):
                    print(f"  ⚠️  No data available for {symbol} (Upstox credentials not set)")
            
            # Step 4: Fetch today's data from Upstox API if end_date includes today
            today_df = None
            if end_date_only >= today:
                try:
                    today_df = await self._fetch_today_data_from_upstox(symbol)
                    if today_df is not None and not today_df.empty:
                        print(f"  Got {len(today_df)} bars from Upstox for {symbol} (today)")
                except Exception as e:
                    # If Upstox API fails, continue without today's data
                    print(f"  Warning: Could not fetch today's data from Upstox for {symbol}: {e}")
                    print(f"  Continuing with historical data only...")
            
            # Step 5: Combine historical and today's data
            print(f"  Combining data for {symbol}: Historical={len(hist_df) if not hist_df.empty else 0} bars, Today={len(today_df) if today_df is not None and not today_df.empty else 0} bars")
            
            if hist_df.empty and (today_df is None or today_df.empty):
                print(f"  Error: No data available for {symbol}")
                return None
            
            # Prepare dataframes for combination
            # Ensure both dataframes have timestamp as index
            if not hist_df.empty:
                if hist_df.index.name != 'timestamp' and 'timestamp' in hist_df.columns:
                    hist_df = hist_df.set_index('timestamp')
                elif hist_df.index.name != 'timestamp':
                    # If timestamp is not index and not a column, create it from index
                    hist_df.index.name = 'timestamp'
            
            if today_df is not None and not today_df.empty:
                if today_df.index.name != 'timestamp' and 'timestamp' in today_df.columns:
                    today_df = today_df.set_index('timestamp')
                elif today_df.index.name != 'timestamp':
                    today_df.index.name = 'timestamp'
            
            # Combine dataframes
            if not hist_df.empty and today_df is not None and not today_df.empty:
                # Combine
                df = pd.concat([hist_df, today_df], ignore_index=False)
                print(f"  Combined {len(hist_df)} historical + {len(today_df)} today = {len(df)} total bars")
            elif not hist_df.empty:
                df = hist_df.copy()
                print(f"  Using only historical data: {len(df)} bars")
            elif today_df is not None and not today_df.empty:
                df = today_df.copy()
                print(f"  Using only today's data: {len(df)} bars")
            else:
                print(f"  Error: No valid data to combine for {symbol}")
                return None
            
            # Sort by timestamp and remove duplicates
            df = df.sort_index()
            before_dedup = len(df)
            df = df[~df.index.duplicated(keep='first')]
            after_dedup = len(df)
            if before_dedup != after_dedup:
                print(f"  Removed {before_dedup - after_dedup} duplicate timestamps")
            
            # Add timestamp as column for signal detection (only if not already present)
            if 'timestamp' not in df.columns:
                df['timestamp'] = df.index
            
            print(f"  Final data for {symbol}: {len(df)} bars")
            return df
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            traceback.print_exc()
            return None
    
    async def _backtest_symbol(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime,
        yf_historical_data: Dict[str, pd.DataFrame] = None
    ) -> Tuple[List[Dict], Dict]:
        """
        Backtest a single symbol for the given period.
        
        Args:
            symbol: NSE trading symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            yf_historical_data: Pre-fetched Yahoo Finance data from batch download
            
        Returns:
            Tuple of (alerts list, statistics dict)
        """
        try:
            # Fetch historical data (including today's data from Upstox)
            df = await self._fetch_historical_data_for_period(symbol, start_date, end_date, yf_historical_data)
            
            if df is None or len(df) == 0:
                return [], {}
            
            # Ensure we have enough data
            if len(df) < VOL_WINDOW:
                print(f"Insufficient data for {symbol}: {len(df)} bars (need at least {VOL_WINDOW})")
                return [], {}
            
            # Calculate indicators
            df = self.selector._calculate_indicators(df)
            
            # Detect signals (require exit price for backtesting)
            alerts = self.selector._detect_signals(df, symbol, require_exit_price=True)
            
            # Filter alerts to only include those within the backtest period
            filtered_alerts = []
            for alert in alerts:
                alert_time = alert['timestamp']
                if isinstance(alert_time, str):
                    alert_time = pd.to_datetime(alert_time)
                if start_date <= alert_time <= end_date:
                    filtered_alerts.append(alert)
            
            # Calculate statistics
            stats = self.selector._calculate_statistics(filtered_alerts, symbol)
            
            return filtered_alerts, stats
            
        except Exception as e:
            print(f"Error backtesting {symbol}: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return [], {}
    
    def _batch_download_yahoo_finance(self, symbols: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
        """
        Batch download historical data from Yahoo Finance for all symbols.
        Uses the EXACT same approach as the working reference code.
        
        Args:
            symbols: List of NSE symbols (without .NS suffix)
            days: Number of days of historical data to fetch
            
        Returns:
            Dictionary mapping symbol to DataFrame with historical data
        """
        print(f"⏬ Downloading last {days} days 1H OHLCV in one batch...")
        
        # Convert symbols to Yahoo Finance format (SYMBOL.NS) - EXACT match
        yf_symbols = [f"{symbol}.NS" for symbol in symbols]
        
        try:
            # Batch download - EXACT match to working program
            print(f"   Downloading {len(yf_symbols)} symbols...")
            # Add retry logic for network issues
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    raw = yfinance.download(
                        tickers=" ".join(yf_symbols),
                        interval=DEFAULT_INTERVAL,
                        period=f"{days}d",
                        group_by="ticker",
                        auto_adjust=False,
                        threads=True,
                        progress=False,
                    )
                    break  # Success, exit retry loop
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"   ⚠️  Attempt {attempt + 1} failed: {e}")
                        print(f"   Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        raise  # Re-raise on final attempt
            
            # Debug: Check what we got
            print(f"   ✅ Download completed. Raw type: {type(raw)}")
            if hasattr(raw, 'shape'):
                print(f"   Raw shape: {raw.shape}")
            if hasattr(raw, 'empty'):
                print(f"   Raw empty: {raw.empty}")
            if hasattr(raw, 'columns'):
                print(f"   Columns type: {type(raw.columns)}")
                if isinstance(raw.columns, pd.MultiIndex):
                    tickers = raw.columns.get_level_values(0).unique()
                    print(f"   MultiIndex - tickers: {tickers[:10].tolist()}")
                    print(f"   Total tickers in structure: {len(tickers)}")
            
            # Check if we actually have data (not just structure)
            if raw is None or (hasattr(raw, 'empty') and raw.empty) or (hasattr(raw, 'shape') and raw.shape[0] == 0):
                print(f"   ⚠️  Warning: No data rows returned from Yahoo Finance (only structure)")
                print(f"   This indicates Yahoo Finance API is blocked or rate-limited from your network.")
                return {}
            
            def get_df(t):
                """Return clean df for ticker, IST indexed, or None - EXACT match to working program."""
                try:
                    df = raw[t].dropna().copy()
                except Exception:
                    return None
                
                # Flatten unexpected multiindex
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Ensure numeric
                for c in ["Open", "High", "Low", "Close", "Volume"]:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
                
                df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
                
                if df.empty:
                    return None
                
                # To IST safely (tz-aware or naive) - EXACT match
                try:
                    if df.index.tz is None:
                        df.index = df.index.tz_localize("UTC").tz_convert(self.ist)
                    else:
                        df.index = df.index.tz_convert(self.ist)
                except Exception:
                    pass
                
                return df
            
            # Build a slim dict of only those symbols that actually returned data - EXACT match
            data = {}
            successful = 0
            failed = 0
            
            for t in yf_symbols:
                d = get_df(t)
                if d is not None and len(d) >= max(LOOKBACK_SWING, VOL_WINDOW) + 5:
                    data[t] = d
                    successful += 1
                else:
                    failed += 1
            
            print(f"✅ Got usable data for {len(data)} symbols (successful: {successful}, failed: {failed})")
            
            if len(data) == 0:
                print(f"   ⚠️  No symbols returned usable data.")
                print(f"   This might be due to:")
                print(f"   - Network/firewall blocking Yahoo Finance API")
                print(f"   - Rate limiting from your IP address")
                print(f"   - Temporary Yahoo Finance API issues")
                print(f"   Note: This code works on Google Colab. If it fails locally,")
                print(f"   try using a VPN or running from a different network.")
                print(f"   Trying to inspect raw data structure...")
                if hasattr(raw, 'keys'):
                    print(f"   Raw has keys() method. Keys: {list(raw.keys())[:5]}")
                elif isinstance(raw, pd.DataFrame):
                    print(f"   Raw is DataFrame with shape: {raw.shape}")
                    if isinstance(raw.columns, pd.MultiIndex):
                        available_tickers = raw.columns.get_level_values(0).unique()
                        print(f"   Available tickers in MultiIndex: {available_tickers[:10].tolist()}")
                return {}
            
            # Convert to our format (lowercase columns, extract symbol name)
            historical_data = {}
            for ticker, df_raw in data.items():
                # Extract symbol name (remove .NS)
                symbol_name = ticker.replace(".NS", "")
                
                # Work with a copy
                df = df_raw.copy()
                
                # Rename columns to lowercase
                df.columns = [col.lower() for col in df.columns]
                
                # Select only OHLCV columns
                available_cols = ['open', 'high', 'low', 'close', 'volume']
                cols_to_use = [col for col in available_cols if col in df.columns]
                
                if 'volume' not in cols_to_use:
                    df['volume'] = 0
                    cols_to_use.append('volume')
                
                df = df[cols_to_use].copy()
                
                # Ensure all numeric columns are numeric
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Remove rows with NaN values in OHLC
                df = df.dropna(subset=['open', 'high', 'low', 'close'])
                
                # Set index name
                df.index.name = 'timestamp'
                
                # Keep ALL data (don't filter today here - we'll filter in _fetch_historical_data_for_period)
                historical_data[symbol_name] = df
            
            print(f"✅ Processed {len(historical_data)} symbols with sufficient historical data")
            return historical_data
            
        except Exception as e:
            print(f"❌ Error in batch download from Yahoo Finance: {e}")
            traceback.print_exc()
            return {}
    
    async def backtest_symbols(
        self,
        symbols: List[str],
        days: int = 7,
        end_date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Backtest multiple symbols for the specified number of days.
        
        Args:
            symbols: List of NSE trading symbols
            days: Number of days to backtest (default: 7 for 1 week)
            end_date: End date for backtest (default: today)
            
        Returns:
            Tuple of (summary DataFrame, alerts DataFrame)
        """
        import asyncio
        
        if end_date is None:
            end_date = datetime.now(self.ist)
        else:
            if end_date.tzinfo is None:
                end_date = self.ist.localize(end_date)
        
        start_date = end_date - timedelta(days=days)
        
        print(f"Backtesting {len(symbols)} symbols from {start_date.date()} to {end_date.date()}")
        print(f"Period: {days} days")
        print("="*80)
        
        # Step 1: Try to fetch historical data from Upstox API first (if credentials available)
        print("\n" + "="*80)
        print("STEP 1: Fetching historical data")
        print("="*80)
        
        yf_historical_data = {}
        
        # Check if Upstox credentials are available
        if self.selector.access_token and self.selector.access_token != 'dummy':
            print("✅ Upstox credentials available - will use Upstox API for historical data")
            print("   (Yahoo Finance will be used as fallback if Upstox fails)")
        else:
            print("⚠️  Upstox credentials not set - will try Yahoo Finance first")
            print("   Set UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN to use Upstox API")
            
            # Try Yahoo Finance batch download
            print("\n   Attempting Yahoo Finance batch download...")
            hist_days = max(days, 30)
            yf_historical_data = self._batch_download_yahoo_finance(symbols, days=hist_days)
            
            if not yf_historical_data:
                print("   ⚠️  Yahoo Finance batch download failed (likely network/firewall issue)")
                print("   Please set Upstox API credentials to fetch historical data")
        
        # Always try Yahoo Finance as backup (even if Upstox credentials are set)
        # This ensures we have data even if some instrument keys are invalid
        if not yf_historical_data:
            print("\n   Attempting Yahoo Finance batch download as backup...")
            hist_days = max(days, 30)
            yf_historical_data = self._batch_download_yahoo_finance(symbols, days=hist_days)
            if yf_historical_data:
                print(f"   ✅ Yahoo Finance backup: Got data for {len(yf_historical_data)} symbols")
        
        print("\n" + "="*80)
        print("STEP 2: Backtesting symbols with available data")
        print("="*80)
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(10)
        
        async def backtest_with_semaphore(symbol: str):
            """Backtest symbol with semaphore control."""
            async with semaphore:
                return await self._backtest_symbol(symbol, start_date, end_date, yf_historical_data)
        
        # Create tasks for all symbols
        tasks = [backtest_with_semaphore(symbol) for symbol in symbols]
        
        # Execute tasks
        results = []
        completed = 0
        
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
    
    def print_backtest_results(
        self, 
        summary_df: pd.DataFrame, 
        alerts_df: pd.DataFrame,
        days: int = 7
    ):
        """
        Print formatted backtest results.
        
        Args:
            summary_df: Summary statistics DataFrame
            alerts_df: Alerts DataFrame
            days: Number of days backtested
        """
        print("\n" + "="*80)
        print("BACKTEST RESULTS")
        print("="*80)
        print(f"Backtest Period: {days} days")
        
        if not alerts_df.empty:
            print(f"Backtest Date Range: {alerts_df['timestamp'].min()} to {alerts_df['timestamp'].max()}")
        
        print("\n" + "="*80)
        print("OVERALL PERFORMANCE")
        print("="*80)
        
        if summary_df.empty:
            print("No trades generated during backtest period.")
            return
        
        total_trades = summary_df['trade_count'].sum()
        total_symbols = len(summary_df[summary_df['trade_count'] > 0])
        
        if total_trades > 0:
            # Calculate overall metrics
            all_pnl = []
            for _, row in summary_df.iterrows():
                if row['trade_count'] > 0:
                    # Get P&L values from alerts for this symbol
                    symbol_alerts = alerts_df[alerts_df['symbol'] == row['symbol']]
                    if not symbol_alerts.empty:
                        all_pnl.extend(symbol_alerts['pnl_pct'].tolist())
            
            if all_pnl:
                winning_trades = [pnl for pnl in all_pnl if pnl > 0]
                losing_trades = [pnl for pnl in all_pnl if pnl < 0]
                
                overall_win_rate = (len(winning_trades) / len(all_pnl) * 100) if all_pnl else 0
                overall_avg_pnl = np.mean(all_pnl) if all_pnl else 0
                overall_net_pnl = sum(all_pnl)
                total_profit = sum(winning_trades) if winning_trades else 0
                total_loss = abs(sum(losing_trades)) if losing_trades else 0
                overall_profit_factor = total_profit / total_loss if total_loss > 0 else (float('inf') if total_profit > 0 else 0.0)
                
                print(f"\nTotal Trades: {total_trades}")
                print(f"Symbols with Trades: {total_symbols}")
                print(f"Overall Win Rate: {overall_win_rate:.2f}%")
                print(f"Overall Average P&L: {overall_avg_pnl:.2f}%")
                print(f"Overall Net P&L: {overall_net_pnl:.2f}%")
                print(f"Overall Profit Factor: {overall_profit_factor:.2f}" if overall_profit_factor != float('inf') else f"Overall Profit Factor: ∞")
                print(f"Winning Trades: {len(winning_trades)}")
                print(f"Losing Trades: {len(losing_trades)}")
                print(f"Total Profit: {total_profit:.2f}%")
                print(f"Total Loss: {total_loss:.2f}%")
        
        print("\n" + "="*80)
        print("TOP PERFORMING SYMBOLS")
        print("="*80)
        
        if not summary_df.empty:
            print(f"\nTop 20 symbols by trade count:")
            print(summary_df.head(20).to_string(index=False))
            
            print(f"\n\nTop 20 symbols by net P&L:")
            top_pnl = summary_df.nlargest(20, 'net_pnl_pct')
            print(top_pnl.to_string(index=False))
        
        print("\n" + "="*80)
        print("TRADE BREAKDOWN")
        print("="*80)
        
        if not alerts_df.empty:
            print(f"\nTotal Alerts: {len(alerts_df)}")
            print(f"Breakout Alerts: {len(alerts_df[alerts_df['signal_type'] == 'BREAKOUT'])}")
            print(f"Breakdown Alerts: {len(alerts_df[alerts_df['signal_type'] == 'BREAKDOWN'])}")
            
            # Daily breakdown
            alerts_df['date'] = pd.to_datetime(alerts_df['timestamp']).dt.date
            daily_breakdown = alerts_df.groupby('date').size()
            print(f"\nDaily Trade Count:")
            for date, count in daily_breakdown.items():
                print(f"  {date}: {count} trades")
            
            print(f"\nRecent trades (last 20):")
            print(alerts_df.tail(20).to_string(index=False))
        
        # Print summary of symbols with invalid instrument keys
        if hasattr(self, 'invalid_instrument_keys') and self.invalid_instrument_keys:
            print("\n" + "="*80)
            print("SYMBOLS WITH INVALID INSTRUMENT KEYS")
            print("="*80)
            print(f"\n⚠️  Found {len(self.invalid_instrument_keys)} symbols with invalid instrument keys:")
            print("\nSymbol | Current Instrument Key | Error")
            print("-" * 80)
            for item in self.invalid_instrument_keys:
                print(f"{item['symbol']:15} | {item['instrument_key']:30} | {item['error']}")
            print("\n💡 To fix this issue:")
            print("   1. The instrument keys in NSE.json are outdated for these symbols")
            print("   2. You need to fetch fresh instrument keys from Upstox API")
            print("   3. Try running: python scripts/fetch_instruments.py")
            print("   4. Or manually update NSE.json with correct instrument keys")
            print("   5. You can find correct instrument keys from Upstox API documentation")
        
        print("\n" + "="*80)

