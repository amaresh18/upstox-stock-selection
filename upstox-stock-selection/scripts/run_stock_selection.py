"""
Entry point script to run the Upstox Stock Selection System.

This script provides a user-friendly interface to run stock selection analysis.
"""

import os
import sys
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.stock_selector import UpstoxStockSelector
from src.utils.symbols import get_nifty_100_symbols
from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_MAX_WORKERS, DEFAULT_HISTORICAL_DAYS


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


async def setup_and_run():
    """Setup and run the stock selection."""
    print("="*80)
    print("UPSTOX STOCK SELECTION - SETUP & RUN")
    print("="*80)
    
    # Check credentials
    print("\n1. Checking credentials...")
    if not check_credentials():
        print("\n⚠️  Please set your Upstox credentials:")
        print("   Windows PowerShell:")
        print("   $env:UPSTOX_API_KEY='your_api_key'")
        print("   $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("\n   Linux/Mac:")
        print("   export UPSTOX_API_KEY='your_api_key'")
        print("   export UPSTOX_ACCESS_TOKEN='your_access_token'")
        return
    
    # Check NSE.json
    print("\n2. Checking NSE.json...")
    if not check_nse_json():
        print("\n⚠️  NSE.json not found. Creating it now...")
        print("   Running fetch_instruments.py...")
        
        try:
            from scripts.fetch_instruments import main as fetch_main
            await fetch_main()
            
            nse_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
            if not os.path.exists(nse_path):
                print("❌ Failed to create NSE.json. Please run manually:")
                print("   python scripts/fetch_instruments.py")
                return
        except Exception as e:
            print(f"❌ Error creating NSE.json: {e}")
            print("   Please run manually: python scripts/fetch_instruments.py")
            return
    
    # Run stock selection
    print("\n3. Running stock selection...")
    print("="*80)
    
    try:
        api_key = os.getenv('UPSTOX_API_KEY')
        access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
        nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
        
        # Initialize selector
        selector = UpstoxStockSelector(api_key, access_token, nse_json_path)
        
        # Get symbols
        symbols = get_nifty_100_symbols(nse_json_path)
        print(f"\n📊 Loaded {len(symbols)} symbols for analysis")
        
        # Get configuration
        max_workers = int(os.getenv('MAX_WORKERS', DEFAULT_MAX_WORKERS))
        days = int(os.getenv('HISTORICAL_DAYS', DEFAULT_HISTORICAL_DAYS))
        
        # Analyze symbols
        summary_df, alerts_df = await selector.analyze_symbols(symbols, max_workers=max_workers, days=days)
        
        # Print results
        selector.print_results(summary_df, alerts_df)
        
        # Save to CSV
        save_csv = os.getenv('SAVE_CSV', 'true').lower() == 'true'
        if save_csv:
            summary_df.to_csv('stock_selection_summary.csv', index=False)
            alerts_df.to_csv('stock_selection_alerts.csv', index=False)
            print("\n✅ Results saved to CSV files:")
            print("   - stock_selection_summary.csv")
            print("   - stock_selection_alerts.csv")
        
    except Exception as e:
        print(f"\n❌ Error running stock selection: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(setup_and_run())

