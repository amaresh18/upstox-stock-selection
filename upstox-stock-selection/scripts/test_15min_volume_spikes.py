"""
Test script to check for 15-minute volume spikes that meet or exceed
the average of past 70 1-hour candles.

This helps verify if the new alert feature would trigger in real market conditions.
"""

import os
import sys
import asyncio
from datetime import datetime, date
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.stock_selector import UpstoxStockSelector
from src.config.settings import DEFAULT_NSE_JSON_PATH

# Get credentials from environment
API_KEY = os.getenv('UPSTOX_API_KEY')
ACCESS_TOKEN = os.getenv('UPSTOX_ACCESS_TOKEN')

if not API_KEY or not ACCESS_TOKEN:
    print("❌ Error: UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN must be set")
    print("Run: .\\scripts\\set_credentials.ps1")
    sys.exit(1)

# Test with a few popular stocks
TEST_SYMBOLS = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
    "HINDUNILVR",
    "SBIN",
    "BHARTIARTL",
    "ITC",
    "KOTAKBANK",
    "LT",
    "AXISBANK",
    "ASIANPAINT",
    "MARUTI",
    "TITAN",
    "NESTLEIND",
    "ULTRACEMCO",
    "BAJFINANCE",
    "WIPRO",
    "ONGC"
]


async def test_15min_volume_spikes():
    """Test for 15-minute volume spikes."""
    print("=" * 80)
    print("Testing 15-Minute Volume Spike Detection")
    print("=" * 80)
    print(f"\nChecking {len(TEST_SYMBOLS)} stocks...")
    print(f"Condition: 15-min candle volume >= average of past 70 1-hour candles\n")
    
    selector = UpstoxStockSelector(
        api_key=API_KEY,
        access_token=ACCESS_TOKEN,
        nse_json_path=DEFAULT_NSE_JSON_PATH,
        verbose=True
    )
    
    results = []
    found_spikes = []
    
    for symbol in TEST_SYMBOLS:
        print(f"\n{'='*80}")
        print(f"Checking {symbol}...")
        print(f"{'='*80}")
        
        try:
            # Use the new method to detect 15-min volume alerts
            alerts = await selector._detect_15min_volume_alerts(symbol, target_date=None)
            
            if alerts:
                found_spikes.append({
                    'symbol': symbol,
                    'alerts': alerts
                })
                print(f"✅ Found {len(alerts)} volume spike(s) for {symbol}")
                for alert in alerts:
                    print(f"   - Volume: {alert['current_15m_volume']:.0f} (15m) vs {alert['avg_1h_volume']:.0f} (avg 1h)")
                    print(f"   - Ratio: {alert['vol_ratio']:.2f}x")
                    print(f"   - Timestamp: {alert['timestamp']}")
                    print(f"   - Price: ₹{alert['price']:.2f}")
            else:
                print(f"   No volume spikes detected for {symbol}")
            
            results.append({
                'symbol': symbol,
                'has_spike': len(alerts) > 0,
                'alert_count': len(alerts)
            })
            
        except Exception as e:
            print(f"   ❌ Error checking {symbol}: {e}")
            results.append({
                'symbol': symbol,
                'has_spike': False,
                'alert_count': 0,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_checked = len(results)
    total_with_spikes = sum(1 for r in results if r.get('has_spike', False))
    total_alerts = sum(r.get('alert_count', 0) for r in results)
    
    print(f"\nTotal stocks checked: {total_checked}")
    print(f"Stocks with volume spikes: {total_with_spikes}")
    print(f"Total alerts found: {total_alerts}")
    
    if found_spikes:
        print(f"\n✅ Found volume spikes in {len(found_spikes)} stock(s):")
        print("\n" + "-" * 80)
        for item in found_spikes:
            symbol = item['symbol']
            alerts = item['alerts']
            print(f"\n{symbol}:")
            for alert in alerts:
                print(f"  • 15m Volume: {alert['current_15m_volume']:,.0f}")
                print(f"  • Avg 1h Volume: {alert['avg_1h_volume']:,.0f}")
                print(f"  • Ratio: {alert['vol_ratio']:.2f}x")
                print(f"  • Price: ₹{alert['price']:.2f}")
                print(f"  • Time: {alert['timestamp']}")
    else:
        print("\n[!] No volume spikes found in the tested stocks.")
        print("   This could mean:")
        print("   - Market is currently quiet")
        print("   - No significant volume spikes occurred recently")
        print("   - The condition is quite strict (15-min >= avg of 70 hours)")
        print("\n   Note: This condition is designed to catch significant volume spikes,")
        print("   so it's normal if it doesn't trigger frequently.")
    
    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_15min_volume_spikes())

