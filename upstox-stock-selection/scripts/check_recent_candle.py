"""
Quick script to check alerts for the most recent completed candle.

This script:
1. Gets current time
2. Determines the most recent completed candle
3. Runs a one-time check for that candle
4. Shows results and exits
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pytz import timezone

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.stock_selector import UpstoxStockSelector
from src.config.settings import TIMEZONE, DEFAULT_NSE_JSON_PATH, DEFAULT_MAX_WORKERS, DEFAULT_HISTORICAL_DAYS
from src.utils.telegram_notifier import TelegramNotifier


async def check_recent_candle():
    """Check alerts for the most recent completed candle."""
    print("="*80)
    print("CHECKING MOST RECENT COMPLETED CANDLE")
    print("="*80)
    
    # Get current time
    ist = timezone(TIMEZONE)
    now = datetime.now(ist)
    current_hour = now.hour
    current_minute = now.minute
    current_second = now.second
    
    print(f"\nCurrent Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Market hours: 9:15 AM - 3:30 PM IST
    market_hours = [9, 10, 11, 12, 13, 14, 15]
    
    # Check for specific candle hour (9:15) if requested via command line
    import sys
    check_specific_hour = None
    if len(sys.argv) > 1:
        try:
            check_specific_hour = int(sys.argv[1])
            print(f"\n📌 Checking specific candle hour: {check_specific_hour}:15")
        except ValueError:
            pass
    
    # Find the most recent completed candle
    # A candle at hour H completes at hour H+1 (e.g., 9:15 candle completes at 10:15)
    if check_specific_hour is not None:
        # User specified a candle hour to check
        most_recent_candle_hour = check_specific_hour
        completed_at = f"{check_specific_hour + 1}:15"
    elif current_hour < 9:
        print("\n⚠️  Market hasn't opened yet (opens at 9:15 AM)")
        return
    elif current_hour > 15 or (current_hour == 15 and current_minute >= 30):
        # After market closes, check the last slot (15:15, which completed at 15:30)
        most_recent_candle_hour = 15
        completed_at = "15:30"
    elif current_minute > 15 or (current_minute == 15 and current_second >= 30):
        # Current hour has passed 15 minutes, so previous hour's candle has completed
        # Example: If it's 10:20, the 9:15 candle (which completed at 10:15) is the most recent
        most_recent_candle_hour = current_hour - 1
        completed_at = f"{current_hour}:15"
    elif current_hour > 9:
        # Current hour hasn't reached 15 minutes yet
        # Example: If it's 10:10, the 9:15 candle hasn't completed yet (completes at 10:15)
        print(f"\n⚠️  Current hour ({current_hour}:{current_minute:02d}) hasn't completed yet")
        print(f"   The {current_hour-1}:15 candle will complete at {current_hour}:15")
        print(f"   Please wait until {current_hour}:15:30 to check")
        return
    else:
        print("\n⚠️  It's too early (before 9:15 AM)")
        return
    
    if most_recent_candle_hour not in market_hours:
        print(f"\n⚠️  Invalid candle hour: {most_recent_candle_hour}")
        return
    
    print(f"\n✅ Most recent completed candle: {most_recent_candle_hour}:15")
    print(f"   (This candle completed at {completed_at})")
    print(f"   Checking for alerts in this candle...")
    print("="*80)
    
    # Check credentials
    api_key = os.getenv('UPSTOX_API_KEY')
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not api_key or not access_token:
        print("❌ Error: UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN must be set")
        return
    
    # Initialize selector
    print("\nInitializing stock selector...")
    selector = UpstoxStockSelector(api_key, access_token)
    
    # Load symbols
    print("Loading symbols...")
    nse_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    
    if not os.path.exists(nse_path):
        print(f"❌ NSE.json not found at {nse_path}")
        return
    
    with open(nse_path, 'r') as f:
        nse_data = json.load(f)
    
    symbols = [item.get('tradingsymbol') for item in nse_data if item.get('tradingsymbol')]
    symbols = [s for s in symbols if s]
    
    print(f"✅ Loaded {len(symbols)} symbols")
    
    # Initialize Telegram notifier
    telegram = TelegramNotifier()
    
    # Run analysis (will automatically filter to most recent completed candle)
    print("\n" + "="*80)
    print("RUNNING ANALYSIS")
    print("="*80)
    
    summary_df, alerts_df = await selector.analyze_symbols(
        symbols,
        max_workers=int(os.getenv('MAX_WORKERS', DEFAULT_MAX_WORKERS)),
        days=int(os.getenv('HISTORICAL_DAYS', DEFAULT_HISTORICAL_DAYS))
    )
    
    # Filter alerts to show only the most recent completed candle
    if not alerts_df.empty and 'timestamp' in alerts_df.columns:
        # Filter to alerts from the most recent completed candle hour
        candle_start_time = now.replace(hour=most_recent_candle_hour, minute=15, second=0, microsecond=0)
        # For the last candle (15:15), it ends at 15:30, not 16:15
        if most_recent_candle_hour == 15:
            candle_end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
        else:
            candle_end_time = now.replace(hour=most_recent_candle_hour+1, minute=15, second=0, microsecond=0)
        
        alerts_df['alert_time'] = pd.to_datetime(alerts_df['timestamp'])
        
        # Ensure timezone-aware comparison (convert alert_time to IST if needed)
        if alerts_df['alert_time'].dt.tz is None:
            # If alerts are timezone-naive, assume they're in IST
            alerts_df['alert_time'] = alerts_df['alert_time'].dt.tz_localize(ist)
        else:
            # Convert to IST if in different timezone
            alerts_df['alert_time'] = alerts_df['alert_time'].dt.tz_convert(ist)
        
        recent_alerts = alerts_df[
            (alerts_df['alert_time'] >= candle_start_time) & 
            (alerts_df['alert_time'] < candle_end_time)
        ].copy()
        
        if not recent_alerts.empty:
            alerts_df = recent_alerts.drop(columns=['alert_time'])
            print(f"\n📅 Alerts for {most_recent_candle_hour}:15 candle: {len(alerts_df)} alerts")
        else:
            print(f"\n⚠️  No alerts for {most_recent_candle_hour}:15 candle")
            alerts_df = pd.DataFrame()
            
            # Send Telegram notification for no alerts
            if telegram.enabled:
                no_alerts_msg = f"⚪ *No Alerts Detected*\n\n"
                no_alerts_msg += f"📊 Candle: {most_recent_candle_hour}:15\n"
                no_alerts_msg += f"⏰ Completed at: {completed_at}\n"
                no_alerts_msg += f"📅 Date: {now.strftime('%Y-%m-%d')}\n\n"
                no_alerts_msg += f"No stocks met the selection criteria for this candle."
                await telegram.send_message(no_alerts_msg)
                print(f"   📱 Sent 'no alerts' notification to Telegram")
    
    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    if alerts_df.empty:
        print("\n⚠️  No alerts generated for the most recent completed candle")
    else:
        print(f"\n✅ Generated {len(alerts_df)} alerts")
        
        # Group by signal type
        breakouts = alerts_df[alerts_df['signal_type'] == 'BREAKOUT']
        breakdowns = alerts_df[alerts_df['signal_type'] == 'BREAKDOWN']
        
        print(f"   Breakout alerts: {len(breakouts)}")
        print(f"   Breakdown alerts: {len(breakdowns)}")
        
        # Sort alerts by volume ratio (highest first) - for both Telegram and display
        alerts_df_sorted = alerts_df.sort_values('vol_ratio', ascending=False)
        
        # Send Telegram notifications (in sorted order)
        if telegram.enabled:
            print(f"\n📱 Sending Telegram notifications...")
            alert_dicts = [row.to_dict() for _, row in alerts_df_sorted.iterrows()]
            sent_count = await telegram.send_alerts_batch(alert_dicts, max_alerts=20)
            if sent_count > 0:
                print(f"   ✅ Sent {sent_count} alert(s) to Telegram (sorted by volume ratio)")
        
        # Show all alerts
        print("\n📊 All Alerts (sorted by volume ratio - highest first):")
        for _, alert in alerts_df_sorted.iterrows():
            timestamp = alert.get('timestamp', 'N/A')
            symbol = alert.get('symbol', 'N/A')
            signal_type = alert.get('signal_type', 'N/A')
            price = alert.get('price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            print(f"   {timestamp} | {symbol:15} | {signal_type:10} | ₹{price:8.2f} | Vol: {vol_ratio:.2f}x")
    
    print("\n" + "="*80)
    print("✅ Check completed!")
    print("="*80)


if __name__ == "__main__":
    import pandas as pd
    asyncio.run(check_recent_candle())

