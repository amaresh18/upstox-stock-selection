"""
Pattern-specific backtesting module.

This module provides backtesting functionality specifically for trading patterns.
"""

import os
import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from pytz import timezone

from .stock_selector import UpstoxStockSelector
from ..config.settings import (
    TIMEZONE,
    DEFAULT_NSE_JSON_PATH,
    DEFAULT_INTERVAL,
    LOOKBACK_SWING,
)


class PatternBacktester:
    """Backtesting engine specifically for trading patterns."""
    
    def __init__(self, api_key: str, access_token: str, nse_json_path: str = None, verbose: bool = False):
        """
        Initialize pattern backtester.
        
        Args:
            api_key: Upstox API key
            access_token: Upstox access token
            nse_json_path: Path to NSE.json file
            verbose: Enable verbose logging
        """
        self.selector = UpstoxStockSelector(api_key, access_token, nse_json_path, verbose=verbose)
        self.ist = timezone(TIMEZONE)
        self.verbose = verbose
        self.backtest_results = []
    
    async def backtest_patterns(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date,
        patterns: List[str] = None,
        interval: str = None,
        max_workers: int = 10
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Backtest patterns for given symbols and date range.
        
        Args:
            symbols: List of NSE symbols
            start_date: Start date for backtest
            end_date: End date for backtest
            patterns: List of patterns to backtest (None = all)
            interval: Time interval
            max_workers: Maximum parallel workers
            
        Returns:
            Tuple of (pattern_results DataFrame, summary DataFrame)
        """
        if interval is None:
            interval = DEFAULT_INTERVAL
        
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
        
        print(f"Backtesting patterns: {', '.join(patterns)}")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Interval: {interval}")
        
        # Validate symbols before processing
        valid_symbols = []
        invalid_symbols = []
        for symbol in symbols:
            if not symbol or not isinstance(symbol, str):
                invalid_symbols.append(symbol)
                continue
            instrument_key = self.selector._get_instrument_key(symbol)
            if instrument_key:
                valid_symbols.append(symbol)
            else:
                invalid_symbols.append(symbol)
                if self.verbose:
                    print(f"  ⚠️  Skipping {symbol}: No instrument key found")
        
        if not valid_symbols:
            print("❌ No valid symbols with instrument keys found!")
            return pd.DataFrame(), pd.DataFrame()
        
        if invalid_symbols and self.verbose:
            print(f"⚠️  Skipped {len(invalid_symbols)} invalid symbols: {invalid_symbols[:10]}")
        
        print(f"✅ Processing {len(valid_symbols)} valid symbols")
        
        # Batch download historical data
        days = (end_date - start_date).days + 30  # Extra days for indicators
        self.selector.yf_historical_data = self.selector._batch_download_yahoo_finance(valid_symbols, days=days)
        
        # Override interval setting
        import src.config.settings as settings
        original_interval = settings.DEFAULT_INTERVAL
        settings.DEFAULT_INTERVAL = interval
        
        semaphore = asyncio.Semaphore(max_workers)
        
        async def backtest_symbol(symbol: str):
            """Backtest patterns for a single symbol."""
            async with semaphore:
                return await self._backtest_symbol_patterns(
                    symbol, start_date, end_date, patterns, interval
                )
        
        tasks = [backtest_symbol(s) for s in valid_symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Restore original interval
        settings.DEFAULT_INTERVAL = original_interval
        
        # Aggregate results
        all_pattern_results = []
        pattern_summary = {}
        
        for result in results:
            if isinstance(result, Exception):
                continue
            pattern_alerts, pattern_stats = result
            all_pattern_results.extend(pattern_alerts)
            
            # Aggregate statistics by pattern type
            for alert in pattern_alerts:
                pattern_type = alert.get('pattern_type', 'UNKNOWN')
                if pattern_type not in pattern_summary:
                    pattern_summary[pattern_type] = {
                        'pattern_type': pattern_type,
                        'count': 0,
                        'wins': 0,
                        'losses': 0,
                        'total_pnl': 0.0,
                        'avg_pnl': 0.0,
                        'win_rate': 0.0
                    }
                
                pattern_summary[pattern_type]['count'] += 1
                
                # Calculate P&L if entry/exit available
                entry = alert.get('entry_price')
                target = alert.get('target_price')
                stop = alert.get('stop_loss')
                price = alert.get('price', 0)
                
                if entry and target and stop:
                    # Simulate trade: entry -> target (win) or entry -> stop (loss)
                    # For bullish patterns: target > entry, stop < entry
                    # For bearish patterns: target < entry, stop > entry
                    is_bullish = pattern_type in [
                        'RSI_BULLISH_DIVERGENCE', 'UPTREND_RETEST',
                        'INVERSE_HEAD_SHOULDERS', 'DOUBLE_BOTTOM', 'TRIPLE_BOTTOM'
                    ]
                    
                    if is_bullish:
                        # Bullish: check if price reached target before stop
                        # Simplified: if current price > entry, assume win
                        if price >= target:
                            pattern_summary[pattern_type]['wins'] += 1
                            pnl = ((target - entry) / entry) * 100
                            pattern_summary[pattern_type]['total_pnl'] += pnl
                        elif price <= stop:
                            pattern_summary[pattern_type]['losses'] += 1
                            pnl = ((stop - entry) / entry) * 100
                            pattern_summary[pattern_type]['total_pnl'] += pnl
                    else:
                        # Bearish: target < entry, stop > entry
                        if price <= target:
                            pattern_summary[pattern_type]['wins'] += 1
                            pnl = ((entry - target) / entry) * 100
                            pattern_summary[pattern_type]['total_pnl'] += pnl
                        elif price >= stop:
                            pattern_summary[pattern_type]['losses'] += 1
                            pnl = ((entry - stop) / entry) * 100
                            pattern_summary[pattern_type]['total_pnl'] += pnl
        
        # Calculate final statistics
        summary_list = []
        for pattern_type, stats in pattern_summary.items():
            count = stats['count']
            wins = stats['wins']
            losses = stats['losses']
            total_pnl = stats['total_pnl']
            
            win_rate = (wins / count * 100) if count > 0 else 0.0
            avg_pnl = (total_pnl / count) if count > 0 else 0.0
            
            summary_list.append({
                'pattern_type': pattern_type,
                'total_signals': count,
                'wins': wins,
                'losses': losses,
                'win_rate': round(win_rate, 2),
                'avg_pnl_pct': round(avg_pnl, 2),
                'total_pnl_pct': round(total_pnl, 2)
            })
        
        pattern_results_df = pd.DataFrame(all_pattern_results) if all_pattern_results else pd.DataFrame()
        summary_df = pd.DataFrame(summary_list) if summary_list else pd.DataFrame()
        
        if not pattern_results_df.empty and 'timestamp' in pattern_results_df.columns:
            pattern_results_df['timestamp'] = pd.to_datetime(pattern_results_df['timestamp'], errors='coerce')
            pattern_results_df = pattern_results_df.sort_values('timestamp').reset_index(drop=True)
            pattern_results_df['timestamp'] = pattern_results_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        if not summary_df.empty:
            summary_df = summary_df.sort_values('total_signals', ascending=False).reset_index(drop=True)
        
        return pattern_results_df, summary_df
    
    async def _backtest_symbol_patterns(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        patterns: List[str],
        interval: str
    ) -> Tuple[List[Dict], Dict]:
        """
        Backtest patterns for a single symbol.
        
        Args:
            symbol: NSE trading symbol
            start_date: Start date
            end_date: End date
            patterns: List of patterns to test
            interval: Time interval
            
        Returns:
            Tuple of (pattern alerts list, statistics dict)
        """
        try:
            instrument_key = self.selector._get_instrument_key(symbol)
            if not instrument_key:
                if self.verbose:
                    print(f"  ⚠️  No instrument key found for {symbol}")
                return [], {}
            
            # Fetch data for the period
            days = (end_date - start_date).days + 30
            
            # Use batch downloaded data if available
            if symbol in self.selector.yf_historical_data:
                df = self.selector.yf_historical_data[symbol].copy()
                # Filter to date range
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    df = df.set_index('timestamp')
                if isinstance(df.index, pd.DatetimeIndex):
                    start_dt = datetime.combine(start_date, datetime.min.time())
                    end_dt = datetime.combine(end_date, datetime.max.time())
                    df = df[(df.index >= start_dt) & (df.index <= end_dt)]
            else:
                # Fallback to fetching from API
                df = await self.selector._fetch_historical_data(
                    instrument_key, symbol, days=days, target_date=None
                )
            
            if df is None or len(df) == 0:
                return [], {}
            
            # Calculate indicators
            df = self.selector._calculate_indicators(df)
            
            # Detect patterns
            pattern_alerts = self.selector.pattern_detector.detect_all_patterns(
                df,
                symbol,
                patterns=patterns,
                lookback_swing=LOOKBACK_SWING,
                rsi_period=14
            )
            
            # Filter to backtest period
            filtered_alerts = []
            for alert in pattern_alerts:
                alert_time = alert.get('timestamp')
                if isinstance(alert_time, str):
                    alert_time = pd.to_datetime(alert_time)
                
                if isinstance(alert_time, pd.Timestamp):
                    alert_date = alert_time.date()
                    if start_date <= alert_date <= end_date:
                        filtered_alerts.append(alert)
            
            return filtered_alerts, {}
            
        except Exception as e:
            if self.verbose:
                print(f"Error backtesting patterns for {symbol}: {e}")
            return [], {}
    
    def print_results(self, pattern_results_df: pd.DataFrame, summary_df: pd.DataFrame):
        """Print backtest results."""
        print("\n" + "="*80)
        print("PATTERN BACKTEST SUMMARY")
        print("="*80)
        
        if summary_df.empty:
            print("No pattern backtest results.")
        else:
            print(f"\nPattern Performance Summary:")
            print(summary_df.to_string(index=False))
        
        print("\n" + "="*80)
        print("PATTERN BACKTEST DETAILS")
        print("="*80)
        
        if pattern_results_df.empty:
            print("No pattern signals detected in backtest period.")
        else:
            print(f"\nTotal pattern signals: {len(pattern_results_df)}")
            print("\nPattern signals by type:")
            
            if 'pattern_type' in pattern_results_df.columns:
                pattern_counts = pattern_results_df['pattern_type'].value_counts()
                for pattern, count in pattern_counts.items():
                    print(f"  {pattern}: {count}")
            
            print("\nFirst 20 pattern signals:")
            print(pattern_results_df.head(20).to_string(index=False))

