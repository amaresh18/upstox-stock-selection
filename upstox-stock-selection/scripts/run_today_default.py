"""
Quick script to run today's analysis with default configuration.

This script runs the stock selection analysis for today using all default settings:
- Lookback Swing: 12
- Volume Window: 70
- Volume Multiplier: 1.6
- Hold Bars: 3
- Historical Days: 30
- Interval: 1h
- Max Workers: 10

Usage:
    python scripts/run_today_default.py
"""

import os
import sys
import asyncio
import pandas as pd
from datetime import datetime, date
from pytz import timezone

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.stock_selector import UpstoxStockSelector
from src.config.settings import (
    TIMEZONE, DEFAULT_NSE_JSON_PATH, DEFAULT_MAX_WORKERS, 
    DEFAULT_HISTORICAL_DAYS, DEFAULT_INTERVAL,
    LOOKBACK_SWING, VOL_WINDOW, VOL_MULT, HOLD_BARS
)
from src.utils.telegram_notifier import TelegramNotifier


async def run_today_default():
    """Run today's analysis with default configuration."""
    print("="*80)
    print("TODAY'S ANALYSIS WITH DEFAULT CONFIGURATION")
    print("="*80)
    
    # Get current date/time
    ist = timezone(TIMEZONE)
    current_time = datetime.now(ist)
    today = current_time.date()
    
    print(f"\n📅 Date: {today.strftime('%A, %B %d, %Y')}")
    print(f"⏰ Current Time: {current_time.strftime('%H:%M:%S %Z')}")
    
    # Display default configuration
    print("\n📊 Default Configuration:")
    print(f"   • Lookback Swing: {LOOKBACK_SWING} bars")
    print(f"   • Volume Window: {VOL_WINDOW} bars")
    print(f"   • Volume Multiplier: {VOL_MULT}x")
    print(f"   • Hold Bars: {HOLD_BARS} bars")
    print(f"   • Historical Days: {DEFAULT_HISTORICAL_DAYS} days")
    print(f"   • Interval: {DEFAULT_INTERVAL}")
    print(f"   • Max Workers: {DEFAULT_MAX_WORKERS}")
    
    # Check credentials
    print("\n1. Checking credentials...")
    api_key = os.getenv('UPSTOX_API_KEY')
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not api_key or not access_token:
        print("❌ Error: UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN must be set")
        print("   Set them using:")
        print("   Windows PowerShell: $env:UPSTOX_API_KEY='your_key'")
        print("   Linux/Mac: export UPSTOX_API_KEY='your_key'")
        return
    
    print("✅ Credentials found")
    
    # Load symbols
    print("\n2. Loading symbols...")
    if not os.path.exists(DEFAULT_NSE_JSON_PATH):
        print(f"❌ Error: {DEFAULT_NSE_JSON_PATH} not found")
        return
    
    with open(DEFAULT_NSE_JSON_PATH, 'r') as f:
        import json
        nse_data = json.load(f)
    
    # Extract symbols - try both 'symbol' and 'tradingsymbol' keys
    symbols = []
    for item in nse_data:
        if 'symbol' in item:
            symbols.append(item['symbol'])
        elif 'tradingsymbol' in item:
            symbols.append(item['tradingsymbol'])
    
    print(f"✅ Loaded {len(symbols)} symbols")
    
    # Initialize selector with default settings
    print("\n3. Initializing stock selector with default settings...")
    selector = UpstoxStockSelector(
        api_key=api_key,
        access_token=access_token,
        nse_json_path=DEFAULT_NSE_JSON_PATH
    )
    
    # Override settings to ensure defaults are used
    import src.config.settings as settings
    settings.LOOKBACK_SWING = LOOKBACK_SWING
    settings.VOL_WINDOW = VOL_WINDOW
    settings.VOL_MULT = VOL_MULT
    settings.HOLD_BARS = HOLD_BARS
    settings.DEFAULT_HISTORICAL_DAYS = DEFAULT_HISTORICAL_DAYS
    settings.DEFAULT_INTERVAL = DEFAULT_INTERVAL
    settings.DEFAULT_MAX_WORKERS = DEFAULT_MAX_WORKERS
    
    print("✅ Selector initialized")
    
    # Determine which candles to check
    print("\n4. Determining candles to analyze...")
    
    # For today, check all completed hourly candles
    market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
    
    # Generate candle times for today
    from datetime import timedelta, time as dtime
    
    candle_times = []
    current_candle = market_open
    while current_candle <= market_close:
        candle_times.append(current_candle)
        current_candle += timedelta(hours=1)
        if current_candle > market_close:
            break
    
    # Filter to completed candles only
    completed_candles = [ct for ct in candle_times if ct < current_time]
    
    if not completed_candles:
        print("⚠️  No completed candles yet today")
        print(f"   Market opens at: {market_open.strftime('%H:%M:%S')}")
        print(f"   Current time: {current_time.strftime('%H:%M:%S')}")
        return
    
    print(f"✅ Found {len(completed_candles)} completed candles today")
    print(f"   Candles: {', '.join([ct.strftime('%H:%M') for ct in completed_candles])}")
    
    # Analyze for the most recent completed candle
    target_candle = completed_candles[-1]
    print(f"\n5. Analyzing for candle: {target_candle.strftime('%H:%M')} IST")
    
    # Run analysis
    print("\n6. Running analysis...")
    print("   This may take a few minutes...")
    
    try:
        # Note: analyze_symbols analyzes for the target_date, not a specific time
        # The selector will check all completed candles up to the current time
        results = await selector.analyze_symbols(
            symbols=symbols,
            target_date=today,
            days=DEFAULT_HISTORICAL_DAYS,
            max_workers=DEFAULT_MAX_WORKERS
        )
        
        # Process results
        print("\n7. Processing results...")
        
        # analyze_symbols returns (summary_df, alerts_df) tuple
        if isinstance(results, tuple):
            summary_df, alerts_df = results
        else:
            alerts_df = results.get('alerts', pd.DataFrame()) if isinstance(results, dict) else pd.DataFrame()
        
        if alerts_df.empty:
            print("\n" + "="*80)
            print("📊 RESULTS: NO ALERTS DETECTED")
            print("="*80)
            print(f"\nNo stocks met the selection criteria for candle {target_candle.strftime('%H:%M')} IST")
            print("\nThis could mean:")
            print("  • No breakouts/breakdowns occurred in this candle")
            print("  • Volume thresholds were not met")
            print("  • Swing levels were not breached")
            
            # Send Telegram notification if configured
            telegram_notifier = TelegramNotifier()
            if telegram_notifier.enabled:
                message = f"📊 **No Alerts for {target_candle.strftime('%H:%M')} Candle**\n\n"
                message += f"Date: {today.strftime('%B %d, %Y')}\n"
                message += f"Candle: {target_candle.strftime('%H:%M')} IST\n"
                message += f"Config: Swing={LOOKBACK_SWING}, Vol={VOL_WINDOW}, Mult={VOL_MULT}x"
                telegram_notifier.send_message(message)
                print("\n✅ Sent 'no alerts' notification to Telegram")
        else:
            print("\n" + "="*80)
            print(f"📊 RESULTS: {len(alerts_df)} ALERTS DETECTED")
            print("="*80)
            
            # Display alerts
            print("\n📈 ALERTS:")
            for idx, row in alerts_df.iterrows():
                signal_type = row.get('signal_type', 'UNKNOWN')
                symbol = row.get('symbol', 'UNKNOWN')
                price = row.get('price', 0)
                volume_ratio = row.get('vol_ratio', row.get('volume_ratio', 0))  # Try both keys
                
                print(f"\n  {idx + 1}. {symbol}")
                print(f"     Signal: {signal_type}")
                print(f"     Price: ₹{price:.2f}")
                print(f"     Volume Ratio: {volume_ratio:.2f}x")
            
            # Save to CSV
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = target_candle.strftime('%Y%m%d_%H%M')
            csv_path = os.path.join(output_dir, f"alerts_{timestamp}.csv")
            alerts_df.to_csv(csv_path, index=False)
            print(f"\n✅ Results saved to: {csv_path}")
            
            # Send Telegram notification if configured
            telegram_notifier = TelegramNotifier()
            if telegram_notifier.enabled:
                message = f"🚨 **{len(alerts_df)} Alert(s) Detected**\n\n"
                message += f"Date: {today.strftime('%B %d, %Y')}\n"
                message += f"Candle: {target_candle.strftime('%H:%M')} IST\n\n"
                
                for idx, row in alerts_df.head(10).iterrows():  # Limit to 10 for Telegram
                    symbol = row.get('symbol', 'UNKNOWN')
                    signal_type = row.get('signal_type', 'UNKNOWN')
                    price = row.get('price', 0)
                    message += f"• {symbol}: {signal_type} @ ₹{price:.2f}\n"
                
                if len(alerts_df) > 10:
                    message += f"\n... and {len(alerts_df) - 10} more"
                
                telegram_notifier.send_message(message)
                print("✅ Sent alerts notification to Telegram")
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    asyncio.run(run_today_default())

