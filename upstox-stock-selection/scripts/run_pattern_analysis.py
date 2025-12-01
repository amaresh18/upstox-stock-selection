"""
Run pattern analysis with multiple time intervals and display results.

This script analyzes stocks for pattern matches across different time frames.
"""

import os
import sys
import asyncio
import pandas as pd
from datetime import date, datetime
from typing import Dict, List

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.stock_selector import UpstoxStockSelector
from src.utils.symbols import get_nifty_100_symbols
from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_MAX_WORKERS, DEFAULT_HISTORICAL_DAYS
import src.config.settings as settings


def check_credentials():
    """Check if credentials are set."""
    api_key = os.getenv('UPSTOX_API_KEY')
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not api_key:
        print("❌ UPSTOX_API_KEY not set")
        return False, None, None
    if not access_token:
        print("❌ UPSTOX_ACCESS_TOKEN not set")
        return False, None, None
    
    print("✅ Credentials found")
    return True, api_key, access_token


def filter_pattern_alerts(alerts: List[Dict]) -> List[Dict]:
    """Filter alerts to show only pattern-based alerts."""
    pattern_types = [
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
    
    return [
        alert for alert in alerts
        if alert.get('pattern_type') in pattern_types or 
           (alert.get('signal_type') == 'VOLUME_SPIKE_15M')
    ]


def display_pattern_results(interval: str, alerts_df: pd.DataFrame):
    """Display pattern results for a specific interval."""
    if alerts_df.empty:
        print(f"\n   No pattern matches found for {interval}")
        return
    
    pattern_alerts = filter_pattern_alerts(alerts_df.to_dict('records'))
    
    if not pattern_alerts:
        print(f"\n   No pattern matches found for {interval}")
        return
    
    print(f"\n   📊 Found {len(pattern_alerts)} pattern matches for {interval}:")
    print("   " + "="*70)
    
    # Group by pattern type
    pattern_groups: Dict[str, List[Dict]] = {}
    for alert in pattern_alerts:
        pattern_type = alert.get('pattern_type', alert.get('signal_type', 'UNKNOWN'))
        if pattern_type not in pattern_groups:
            pattern_groups[pattern_type] = []
        pattern_groups[pattern_type].append(alert)
    
    # Display by pattern type
    for pattern_type, alerts in sorted(pattern_groups.items()):
        print(f"\n   🔹 {pattern_type} ({len(alerts)} matches):")
        for alert in alerts[:5]:  # Show first 5 per pattern
            symbol = alert.get('symbol', 'N/A')
            price = alert.get('price', 0)
            timestamp = alert.get('timestamp', 'N/A')
            vol_ratio = alert.get('vol_ratio', 0)
            
            # Pattern-specific info
            entry = alert.get('entry_price', 'N/A')
            stop = alert.get('stop_loss', 'N/A')
            target = alert.get('target_price', 'N/A')
            
            print(f"      • {symbol:10} | Price: ₹{price:8.2f} | Vol: {vol_ratio:.2f}x")
            if entry != 'N/A' and stop != 'N/A' and target != 'N/A':
                print(f"        Entry: ₹{entry:.2f} | Stop: ₹{stop:.2f} | Target: ₹{target:.2f}")
        
        if len(alerts) > 5:
            print(f"      ... and {len(alerts) - 5} more")


async def run_pattern_analysis():
    """Run pattern analysis with multiple time intervals."""
    print("="*80)
    print("PATTERN ANALYSIS - MULTIPLE TIME INTERVALS")
    print("="*80)
    
    # Check credentials
    print("\n1. Checking credentials...")
    creds_ok, api_key, access_token = check_credentials()
    if not creds_ok:
        print("\n⚠️  Please set your Upstox credentials:")
        print("   Windows PowerShell:")
        print("   $env:UPSTOX_API_KEY='your_api_key'")
        print("   $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
        return
    
    # Check NSE.json
    nse_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    if not os.path.exists(nse_path):
        print(f"\n❌ NSE.json not found at {nse_path}")
        print("   Please run: python scripts/fetch_instruments.py")
        return
    
    print(f"\n✅ NSE.json found at {nse_path}")
    
    # Initialize selector
    print("\n2. Initializing stock selector...")
    selector = UpstoxStockSelector(api_key, access_token, nse_path, verbose=False)
    
    # Get symbols (limit to first 20 for demo, remove limit for full analysis)
    symbols = get_nifty_100_symbols(nse_path)
    print(f"📊 Loaded {len(symbols)} symbols")
    
    # Limit symbols for faster demo (remove this line for full analysis)
    symbols = symbols[:20]
    print(f"🔍 Analyzing first {len(symbols)} symbols for demonstration...")
    
    # Time intervals to test
    intervals = ['15m', '30m', '1h', '2h', '4h', '1d']
    
    print("\n3. Running pattern analysis across multiple time intervals...")
    print("="*80)
    
    all_results = {}
    
    for interval in intervals:
        print(f"\n⏱️  Analyzing with {interval} interval...")
        
        try:
            # Override interval setting
            original_interval = settings.DEFAULT_INTERVAL
            settings.DEFAULT_INTERVAL = interval
            
            # Run analysis
            summary_df, alerts_df = await selector.analyze_symbols(
                symbols=symbols,
                max_workers=5,  # Reduced for demo
                days=30,
                target_date=None
            )
            
            # Store results
            all_results[interval] = {
                'summary': summary_df,
                'alerts': alerts_df
            }
            
            # Display pattern results
            display_pattern_results(interval, alerts_df)
            
            # Restore original interval
            settings.DEFAULT_INTERVAL = original_interval
            
        except Exception as e:
            print(f"   ❌ Error analyzing {interval}: {e}")
            continue
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY - PATTERN MATCHES BY INTERVAL")
    print("="*80)
    
    for interval, results in all_results.items():
        alerts_df = results['alerts']
        if not alerts_df.empty:
            pattern_alerts = filter_pattern_alerts(alerts_df.to_dict('records'))
            print(f"\n{interval:>6}: {len(pattern_alerts):>3} pattern matches")
        else:
            print(f"\n{interval:>6}: {0:>3} pattern matches")
    
    print("\n" + "="*80)
    print("✅ Analysis complete!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(run_pattern_analysis())

