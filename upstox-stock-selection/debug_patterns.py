"""Debug script to check if patterns are being detected."""

import os
import sys
import asyncio
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.core.stock_selector import UpstoxStockSelector
from src.config.settings import DEFAULT_NSE_JSON_PATH

async def debug_patterns():
    """Debug pattern detection."""
    api_key = os.getenv('UPSTOX_API_KEY')
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not api_key or not access_token:
        print("❌ Credentials not set")
        return
    
    selector = UpstoxStockSelector(api_key, access_token, DEFAULT_NSE_JSON_PATH, verbose=True)
    
    # Test with a single symbol
    test_symbol = "RELIANCE"  # Change to any symbol you want to test
    
    print(f"\n🔍 Testing pattern detection for {test_symbol}...")
    
    alerts, stats = await selector._analyze_symbol(test_symbol, days=30)
    
    print(f"\n📊 Total alerts: {len(alerts)}")
    
    # Check for patterns
    pattern_alerts = [a for a in alerts if 'pattern_type' in a]
    print(f"📈 Pattern alerts: {len(pattern_alerts)}")
    
    if pattern_alerts:
        print("\n✅ Patterns detected:")
        for alert in pattern_alerts:
            print(f"  - {alert.get('symbol')}: {alert.get('pattern_type')} at {alert.get('timestamp')}")
    else:
        print("\n❌ No patterns detected")
        print("\nChecking all alerts:")
        for alert in alerts[:5]:
            print(f"  - {alert.get('symbol')}: {alert.get('signal_type', 'N/A')} / {alert.get('pattern_type', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(debug_patterns())

