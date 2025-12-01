"""Analysis service - orchestrates stock analysis."""

import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from pytz import timezone

from ..domain.indicators import (
    calculate_rsi,
    calculate_swing_levels,
    calculate_volume_indicators,
    calculate_momentum_indicators
)
from ..domain.signals.detector import SignalDetector
from ..domain.patterns.detector import PatternDetector
from ..adapters.api.upstox_client import UpstoxClient
from ..adapters.api.yahoo_client import YahooFinanceClient
from ..infrastructure.repositories.instrument_repository import InstrumentRepository
from ..config.settings import (
    TIMEZONE,
    DEFAULT_HISTORICAL_DAYS,
    DEFAULT_INTERVAL,
    DEFAULT_MAX_WORKERS,
    LOOKBACK_SWING,
    VOL_WINDOW,
    VOL_MULT,
    HOLD_BARS
)


class AnalysisService:
    """Service for analyzing stocks and generating alerts."""
    
    def __init__(
        self,
        api_key: str,
        access_token: str,
        nse_json_path: str = None,
        verbose: bool = False
    ):
        """
        Initialize analysis service.
        
        Args:
            api_key: Upstox API key
            access_token: Upstox access token
            nse_json_path: Path to NSE.json file
            verbose: Enable verbose logging
        """
        self.upstox_client = UpstoxClient(api_key, access_token, verbose)
        self.yahoo_client = YahooFinanceClient(verbose)
        self.instrument_repo = InstrumentRepository(nse_json_path)
        self.signal_detector = SignalDetector()
        self.pattern_detector = LegacyPatternDetector(verbose=verbose)
        self.ist = timezone(TIMEZONE)
        self.verbose = verbose
        self.yf_historical_data = {}
    
    async def analyze_symbol(
        self,
        symbol: str,
        target_date: date = None,
        days: int = None,
        interval: str = None
    ) -> Tuple[List[Dict], Dict]:
        """
        Analyze a single symbol.
        
        Args:
            symbol: NSE trading symbol
            target_date: Specific date to analyze
            days: Number of days of historical data
            interval: Time interval
            
        Returns:
            Tuple of (alerts list, statistics dict)
        """
        if days is None:
            days = DEFAULT_HISTORICAL_DAYS
        if interval is None:
            interval = DEFAULT_INTERVAL
        
        try:
            instrument_key = self.instrument_repo.get_instrument_key(symbol)
            if not instrument_key:
                if self.verbose:
                    print(f"Instrument key not found for {symbol}")
                return [], {}
            
            df = await self._fetch_historical_data(
                instrument_key, symbol, days, target_date, interval
            )
            
            if df is None or len(df) == 0:
                return [], {}
            
            df = self._calculate_all_indicators(df, interval)
            
            signals = self.signal_detector.detect(df, symbol)
            pattern_alerts = self.pattern_detector.detect_all_patterns(
                df, symbol, patterns=None, lookback_swing=LOOKBACK_SWING, rsi_period=14
            )
            
            alerts = [self._signal_to_dict(s, df) for s in signals] + pattern_alerts
            stats = self._calculate_statistics(signals, symbol)
            
            return alerts, stats
            
        except Exception as e:
            if self.verbose:
                print(f"Error analyzing {symbol}: {e}")
            return [], {}
    
    async def analyze_symbols(
        self,
        symbols: List[str],
        max_workers: int = None,
        days: int = None,
        target_date: date = None,
        interval: str = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Analyze multiple symbols in parallel.
        
        Args:
            symbols: List of NSE symbols
            max_workers: Maximum parallel workers
            days: Historical days
            target_date: Target date
            interval: Time interval
            
        Returns:
            Tuple of (summary DataFrame, alerts DataFrame)
        """
        if max_workers is None:
            max_workers = DEFAULT_MAX_WORKERS
        if days is None:
            days = DEFAULT_HISTORICAL_DAYS
        if interval is None:
            interval = DEFAULT_INTERVAL
        
        self.yf_historical_data = self.yahoo_client.batch_download(
            symbols, days, interval
        )
        
        semaphore = asyncio.Semaphore(max_workers)
        
        async def analyze_with_semaphore(symbol: str):
            async with semaphore:
                return await self.analyze_symbol(symbol, target_date, days, interval)
        
        tasks = [analyze_with_semaphore(s) for s in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_alerts = []
        all_stats = []
        
        for result in results:
            if isinstance(result, Exception):
                continue
            alerts, stats = result
            all_alerts.extend(alerts)
            if stats:
                all_stats.append(stats)
        
        summary_df = pd.DataFrame(all_stats) if all_stats else pd.DataFrame()
        alerts_df = pd.DataFrame(all_alerts) if all_alerts else pd.DataFrame()
        
        if not alerts_df.empty and 'timestamp' in alerts_df.columns:
            alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'], errors='coerce')
            alerts_df = alerts_df.dropna(subset=['timestamp'])
            alerts_df = alerts_df.sort_values('timestamp').reset_index(drop=True)
            alerts_df['timestamp'] = alerts_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        if not summary_df.empty:
            summary_df = summary_df.sort_values(
                ['trade_count', 'net_pnl_pct'], ascending=[False, False]
            ).reset_index(drop=True)
        
        return summary_df, alerts_df
    
    async def _fetch_historical_data(
        self,
        instrument_key: str,
        symbol: str,
        days: int,
        target_date: date,
        interval: str
    ) -> Optional[pd.DataFrame]:
        """Fetch and combine historical data from multiple sources."""
        end_date = datetime.now(self.ist)
        if target_date:
            end_date = self.ist.localize(
                datetime.combine(target_date, datetime.min.time().replace(hour=15, minute=30))
            )
        
        hist_df = pd.DataFrame()
        
        if symbol in self.yf_historical_data and interval == "1h":
            hist_df = self.yf_historical_data[symbol].copy()
        
        if hist_df.empty:
            start_date = end_date - timedelta(days=days)
            hist_df = await self.upstox_client.fetch_historical_data(
                instrument_key, start_date, end_date, interval
            )
            if hist_df is not None:
                today_date = end_date.date()
                hist_df = hist_df[hist_df.index.date < today_date]
        
        today_df = await self.upstox_client.fetch_intraday_data(
            instrument_key, target_date, interval
        )
        
        if hist_df.empty and (today_df is None or today_df.empty):
            return None
        
        if not hist_df.empty and today_df is not None and not today_df.empty:
            df = pd.concat([hist_df, today_df], ignore_index=False)
        elif not hist_df.empty:
            df = hist_df.copy()
        elif today_df is not None and not today_df.empty:
            df = today_df.copy()
        else:
            return None
        
        df = df.sort_index()
        df = df[~df.index.duplicated(keep='first')]
        
        if 'timestamp' not in df.columns:
            df['timestamp'] = df.index
        
        return df
    
    def _calculate_all_indicators(self, df: pd.DataFrame, interval: str) -> pd.DataFrame:
        """Calculate all technical indicators."""
        df = calculate_swing_levels(df, LOOKBACK_SWING)
        df = calculate_volume_indicators(df, VOL_WINDOW)
        df['Range'] = df['high'] - df['low']
        df['AvgRange'] = df['Range'].rolling(window=LOOKBACK_SWING).mean()
        df = calculate_momentum_indicators(df, interval)
        return df
    
    def _signal_to_dict(self, signal, df: pd.DataFrame) -> Dict:
        """Convert Signal object to dict format."""
        return {
            'symbol': signal.symbol,
            'timestamp': signal.timestamp,
            'signal_type': signal.signal_type,
            'price': signal.price,
            'swing_high': signal.swing_level if signal.is_breakout() else None,
            'swing_low': signal.swing_level if signal.is_breakdown() else None,
            'vol_ratio': signal.vol_ratio
        }
    
    def _calculate_statistics(self, signals: List, symbol: str) -> Dict:
        """Calculate statistics for signals."""
        if not signals:
            return {
                'symbol': symbol,
                'trade_count': 0,
                'win_rate': 0.0,
                'avg_gain_pct': 0.0,
                'net_pnl_pct': 0.0,
                'profit_factor': 0.0
            }
        
        pnl_values = [
            s.pnl_pct for s in signals
            if hasattr(s, 'pnl_pct') and s.pnl_pct is not None
        ]
        
        if not pnl_values:
            return {
                'symbol': symbol,
                'trade_count': len(signals),
                'win_rate': 0.0,
                'avg_gain_pct': 0.0,
                'net_pnl_pct': 0.0,
                'profit_factor': 0.0
            }
        
        winning = [p for p in pnl_values if p > 0]
        losing = [p for p in pnl_values if p < 0]
        
        win_rate = (len(winning) / len(pnl_values) * 100) if pnl_values else 0.0
        avg_gain = np.mean(pnl_values) if pnl_values else 0.0
        net_pnl = sum(pnl_values)
        
        total_profit = sum(winning) if winning else 0
        total_loss = abs(sum(losing)) if losing else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else (
            float('inf') if total_profit > 0 else 0.0
        )
        
        return {
            'symbol': symbol,
            'trade_count': len(signals),
            'win_rate': round(win_rate, 2),
            'avg_gain_pct': round(avg_gain, 2),
            'net_pnl_pct': round(net_pnl, 2),
            'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 999.99
        }

