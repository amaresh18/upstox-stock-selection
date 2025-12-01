"""
Compatibility wrapper for UpstoxStockSelector.

This module provides backward compatibility while allowing gradual migration
to the new service-based architecture.
"""

from typing import List, Tuple
from datetime import date
import pandas as pd

from ..services.analysis_service import AnalysisService
from ..config.settings import DEFAULT_MAX_WORKERS, DEFAULT_HISTORICAL_DAYS


class UpstoxStockSelector:
    """
    Compatibility wrapper for UpstoxStockSelector.
    
    This class maintains the same interface as the original UpstoxStockSelector
    but delegates to the new AnalysisService internally.
    """
    
    def __init__(self, api_key: str, access_token: str, nse_json_path: str = None, verbose: bool = None):
        """
        Initialize stock selector (compatibility wrapper).
        
        Args:
            api_key: Upstox API key
            access_token: Upstox access token
            nse_json_path: Path to NSE.json file
            verbose: Enable verbose logging
        """
        self._service = AnalysisService(
            api_key=api_key,
            access_token=access_token,
            nse_json_path=nse_json_path,
            verbose=verbose if verbose is not None else False
        )
        self.api_key = api_key
        self.access_token = access_token
        self.nse_json_path = nse_json_path
        self.verbose = verbose if verbose is not None else False
        self.alerts = []
        self.summary_stats = []
        # Expose pattern_detector for compatibility with app.py
        from ...core.pattern_detector import PatternDetector
        self.pattern_detector = PatternDetector(verbose=self.verbose)
        # Expose yf_historical_data for compatibility
        self.yf_historical_data = {}
    
    async def analyze_symbols(
        self,
        symbols: List[str],
        max_workers: int = None,
        days: int = None,
        target_date: date = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Analyze multiple symbols (compatibility method).
        
        Args:
            symbols: List of NSE symbols
            max_workers: Maximum parallel workers
            days: Historical days
            target_date: Target date
            
        Returns:
            Tuple of (summary DataFrame, alerts DataFrame)
        """
        summary_df, alerts_df = await self._service.analyze_symbols(
            symbols=symbols,
            max_workers=max_workers,
            days=days,
            target_date=target_date
        )
        
        # Store for compatibility
        if not alerts_df.empty:
            self.alerts = alerts_df.to_dict('records')
        if not summary_df.empty:
            self.summary_stats = summary_df.to_dict('records')
        
        return summary_df, alerts_df
    
    def print_results(self, summary_df: pd.DataFrame, alerts_df: pd.DataFrame):
        """
        Print formatted results (compatibility method).
        
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
            print(alerts_df.to_string(index=False))

