"""
Entry point script to run backtesting for the Upstox Stock Selection System.

This script performs backtesting on historical data for the past week.
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.backtester import Backtester
from src.utils.symbols import get_nifty_100_symbols
from src.config.settings import DEFAULT_NSE_JSON_PATH


def check_credentials():
    """Check if credentials are set."""
    api_key = os.getenv('UPSTOX_API_KEY')
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not api_key:
        print("❌ UPSTOX_API_KEY not set")
        return False
    if not access_token:
        print("❌ UPSTOX_ACCESS_TOKEN not set")
        return False
    
    print("✅ Credentials found")
    return True


def check_nse_json():
    """Check if NSE.json exists."""
    nse_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    if os.path.exists(nse_path):
        print(f"✅ NSE.json found at {nse_path}")
        return True
    else:
        print(f"❌ NSE.json not found at {nse_path}")
        return False


async def run_backtest():
    """Run backtest for the past week."""
    print("="*80)
    print("UPSTOX STOCK SELECTION - BACKTEST")
    print("="*80)
    
    # Check credentials (optional for backtesting - only needed for today's data)
    print("\n1. Checking credentials...")
    has_credentials = check_credentials()
    if not has_credentials:
        print("\n⚠️  Upstox credentials not set. Backtest will use Yahoo Finance data only.")
        print("   To include today's data, set credentials:")
        print("   Windows PowerShell:")
        print("   $env:UPSTOX_API_KEY='your_api_key'")
        print("   $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("\n   Continuing with historical data only...")
    
    # Check NSE.json
    print("\n2. Checking NSE.json...")
    if not check_nse_json():
        print("\n⚠️  NSE.json not found. Please create it first:")
        print("   python scripts/fetch_instruments.py")
        return
    
    # Get backtest parameters
    days = int(os.getenv('BACKTEST_DAYS', '7'))  # Default: 1 week
    end_date_str = os.getenv('BACKTEST_END_DATE', None)
    
    if end_date_str:
        try:
            from pytz import timezone
            ist = timezone('Asia/Kolkata')
            end_date = ist.localize(datetime.strptime(end_date_str, '%Y-%m-%d'))
        except:
            print(f"Invalid date format: {end_date_str}. Use YYYY-MM-DD")
            end_date = None
    else:
        end_date = None
    
    print(f"\n3. Running backtest for past {days} days...")
    print("="*80)
    
    try:
        api_key = os.getenv('UPSTOX_API_KEY', '')
        access_token = os.getenv('UPSTOX_ACCESS_TOKEN', '')
        nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
        
        # Initialize backtester (credentials can be empty for Yahoo Finance only)
        backtester = Backtester(api_key or 'dummy', access_token or 'dummy', nse_json_path)
        
        # Get symbols
        symbols = get_nifty_100_symbols(nse_json_path)
        print(f"\n📊 Loaded {len(symbols)} symbols for backtesting")
        
        # Run backtest
        summary_df, alerts_df = await backtester.backtest_symbols(
            symbols, 
            days=days,
            end_date=end_date
        )
        
        # Print results
        backtester.print_backtest_results(summary_df, alerts_df, days=days)
        
        # Save to CSV
        save_csv = os.getenv('SAVE_CSV', 'true').lower() == 'true'
        if save_csv:
            summary_df.to_csv('backtest_summary.csv', index=False)
            alerts_df.to_csv('backtest_alerts.csv', index=False)
            print("\n✅ Backtest results saved to CSV files:")
            print("   - backtest_summary.csv")
            print("   - backtest_alerts.csv")
        
    except Exception as e:
        print(f"\n❌ Error running backtest: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_backtest())

