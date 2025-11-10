"""
Script to run real-time stock selection alerts.

This script:
1. Fetches current day data from Upstox API
2. Analyzes all Nifty 100 stocks
3. Generates alerts for breakout/breakdown signals
4. Saves results to CSV files

Usage:
    python scripts/run_realtime_alerts.py
    
    # For a specific date (e.g., Nov 10, 2025):
    python scripts/run_realtime_alerts.py --date 2025-11-10
    
    # Or using environment variable:
    ALERT_DATE=2025-11-10 python scripts/run_realtime_alerts.py
"""

import os
import sys
import asyncio
import argparse
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
from src.config.settings import TIMEZONE
from src.utils.telegram_notifier import TelegramNotifier


async def run_realtime_alerts(target_date: date = None):
    """
    Run real-time stock selection alerts.
    
    Args:
        target_date: Specific date to analyze (YYYY-MM-DD format). 
                     If None, uses current date.
    """
    print("="*80)
    print("REAL-TIME STOCK SELECTION ALERTS")
    print("="*80)
    
    # Get target date/time
    ist = timezone(TIMEZONE)
    if target_date:
        # Use specified date at market close time (3:30 PM)
        current_time = ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=15, minute=30)))
        print(f"\n📅 Analyzing for date: {target_date.strftime('%A, %B %d, %Y')}")
        print(f"   Using market close time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        # Use current date/time
        current_time = datetime.now(ist)
        print(f"\nCurrent Date/Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Date: {current_time.strftime('%A, %B %d, %Y')}")
    
    # Check if it's a trading day (Monday-Friday)
    weekday = current_time.weekday()
    if weekday >= 5:  # Saturday = 5, Sunday = 6
        if target_date:
            print(f"\n⚠️  Warning: {target_date.strftime('%A, %B %d, %Y')} is a {current_time.strftime('%A')} - Markets are closed")
            print("   However, continuing with analysis for historical data...")
        else:
            print(f"\n⚠️  Warning: Today is {current_time.strftime('%A')} - Markets are closed")
            print("   Real-time alerts are only available on trading days (Monday-Friday)")
            return
    
    # Check if it's during market hours (9:15 AM - 3:30 PM IST)
    market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
    
    if current_time < market_open:
        print(f"\n⏰ Market opens at 9:15 AM IST")
        print(f"   Current time: {current_time.strftime('%H:%M:%S')}")
        print("   Waiting for market to open...")
    elif current_time > market_close:
        print(f"\n⏰ Market closed at 3:30 PM IST")
        print(f"   Current time: {current_time.strftime('%H:%M:%S')}")
        print("   Running analysis on today's completed data...")
    else:
        print(f"\n✅ Market is open (9:15 AM - 3:30 PM IST)")
        print(f"   Current time: {current_time.strftime('%H:%M:%S')}")
        print("   Fetching real-time data...")
    
    # Check credentials
    print("\n1. Checking credentials...")
    api_key = os.getenv('UPSTOX_API_KEY')
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not api_key or not access_token:
        print("❌ Error: UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN must be set")
        print("\nUsage:")
        print("  Windows PowerShell:")
        print("    $env:UPSTOX_API_KEY='your_api_key'")
        print("    $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("    python scripts/run_realtime_alerts.py")
        return
    
    print("✅ Credentials found")
    
    # Initialize stock selector
    print("\n2. Initializing stock selector...")
    selector = UpstoxStockSelector(api_key, access_token)
    
    # Load symbols
    print("\n3. Loading symbols...")
    # Get symbols from NSE.json
    from src.utils.symbols import get_nifty_100_symbols
    from src.config.settings import DEFAULT_NSE_JSON_PATH
    import json
    
    nse_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    if not os.path.exists(nse_path):
        print(f"❌ NSE.json not found at {nse_path}")
        return
    
    with open(nse_path, 'r') as f:
        nse_data = json.load(f)
    
    symbols = [item.get('tradingsymbol') for item in nse_data if item.get('tradingsymbol')]
    symbols = [s for s in symbols if s]  # Remove None values
    
    if not symbols:
        print("❌ No symbols loaded")
        return
    
    print(f"✅ Loaded {len(symbols)} symbols")
    
    # Run analysis
    print("\n4. Running real-time analysis...")
    print("="*80)
    
    # Get configuration
    from src.config.settings import DEFAULT_MAX_WORKERS, DEFAULT_HISTORICAL_DAYS
    max_workers = int(os.getenv('MAX_WORKERS', DEFAULT_MAX_WORKERS))
    days = int(os.getenv('HISTORICAL_DAYS', DEFAULT_HISTORICAL_DAYS))
    
    # Initialize Telegram notifier
    telegram = TelegramNotifier()
    
    # Set target date for analysis (if specified)
    if target_date:
        # Override the selector's date handling for specific date
        selector.target_date = target_date
    
    # Analyze symbols - returns (summary_df, alerts_df)
    summary_df, alerts_df = await selector.analyze_symbols(symbols, max_workers=max_workers, days=days, target_date=target_date)
    
    # Display results
    print("\n" + "="*80)
    print("REAL-TIME ALERTS SUMMARY")
    print("="*80)
    
    if alerts_df.empty:
        print("\n⚠️  No alerts generated at this time")
        print("   This could mean:")
        print("   1. No signals met the criteria")
        print("   2. Market is closed or pre-market")
        print("   3. Insufficient data available")
    else:
        print(f"\n✅ Generated {len(alerts_df)} alerts")
        
        # Group by signal type
        breakouts = alerts_df[alerts_df['signal_type'] == 'BREAKOUT']
        breakdowns = alerts_df[alerts_df['signal_type'] == 'BREAKDOWN']
        
        print(f"   Breakout alerts: {len(breakouts)}")
        print(f"   Breakdown alerts: {len(breakdowns)}")
        
        # Send Telegram notifications
        if telegram.enabled:
            print(f"\n📱 Sending Telegram notifications...")
            alert_dicts = [row.to_dict() for _, row in alerts_df.iterrows()]
            sent_count = await telegram.send_alerts_batch(alert_dicts, max_alerts=20)
            if sent_count > 0:
                print(f"   ✅ Sent {sent_count} alert(s) to Telegram")
            else:
                print(f"   ⚠️  Failed to send Telegram notifications")
        
        # Show recent alerts
        print("\n📊 Recent Alerts (last 10):")
        recent_alerts = alerts_df.tail(10)
        for _, alert in recent_alerts.iterrows():
            timestamp = alert.get('timestamp', 'N/A')
            symbol = alert.get('symbol', 'N/A')
            signal_type = alert.get('signal_type', 'N/A')
            price = alert.get('price', 0)
            vol_ratio = alert.get('vol_ratio', 0)
            print(f"   {timestamp} | {symbol:15} | {signal_type:10} | ₹{price:8.2f} | Vol: {vol_ratio:.2f}x")
    
    # Display statistics
    if not summary_df.empty:
        print("\n" + "="*80)
        print("STATISTICS")
        print("="*80)
        
        total_trades = summary_df['trade_count'].sum()
        symbols_with_trades = len(summary_df[summary_df['trade_count'] > 0])
        
        print(f"Total symbols analyzed: {len(symbols)}")
        print(f"Symbols with alerts: {symbols_with_trades}")
        print(f"Total alerts: {int(total_trades)}")
        
        if symbols_with_trades > 0:
            # Top performers
            top_symbols = summary_df[summary_df['trade_count'] > 0].nlargest(10, 'trade_count')
            
            print("\nTop 10 symbols by alert count:")
            for i, (_, row) in enumerate(top_symbols.iterrows(), 1):
                symbol = row.get('symbol', 'N/A')
                count = int(row.get('trade_count', 0))
                win_rate = row.get('win_rate', 0)
                net_pnl = row.get('net_pnl_pct', 0)
                print(f"   {i:2}. {symbol:15} | {count:2} alerts | Win: {win_rate:5.1f}% | P&L: {net_pnl:6.2f}%")
    
    print("\n" + "="*80)
    print("✅ Real-time alerts completed!")
    print("="*80)
    
    # Save results
    save_csv = os.getenv('SAVE_CSV', 'true').lower() == 'true'
    if save_csv:
        summary_df.to_csv('stock_selection_summary.csv', index=False)
        alerts_df.to_csv('stock_selection_alerts.csv', index=False)
        print("\n💾 Results saved to CSV files:")
        print("   - stock_selection_summary.csv")
        print("   - stock_selection_alerts.csv")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run real-time stock selection alerts')
    parser.add_argument(
        '--date',
        type=str,
        help='Specific date to analyze (YYYY-MM-DD format, e.g., 2025-11-10)',
        default=None
    )
    args = parser.parse_args()
    
    # Get date from command line or environment variable
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ Error: Invalid date format '{args.date}'. Use YYYY-MM-DD format (e.g., 2025-11-10)")
            sys.exit(1)
    elif os.getenv('ALERT_DATE'):
        try:
            target_date = datetime.strptime(os.getenv('ALERT_DATE'), '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ Error: Invalid date format in ALERT_DATE environment variable. Use YYYY-MM-DD format")
            sys.exit(1)
    
    asyncio.run(run_realtime_alerts(target_date=target_date))

