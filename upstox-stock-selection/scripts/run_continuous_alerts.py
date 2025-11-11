"""
Continuous real-time alert monitoring script.

This script runs continuously during market hours and checks for alerts every few minutes.
It will notify you immediately when new alerts are generated.

Usage:
    python scripts/run_continuous_alerts.py

The script will:
- Run continuously during market hours (9:15 AM - 3:30 PM IST)
- Check for alerts 30 seconds after each hour completes (9:15:30, 10:15:30, etc.)
- Display new alerts immediately
- Save all alerts to CSV files
- Stop automatically when market closes

Press Ctrl+C to stop the script manually.
"""

import os
import sys
import asyncio
import json
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
from pathlib import Path

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


class ContinuousAlertMonitor:
    """Continuous alert monitoring system."""
    
    def __init__(self, check_after_hour=True):
        """
        Initialize the monitor.
        
        Args:
            check_after_hour: If True, check right after each hour completes (9:16, 10:16, etc.)
                             If False, use fixed interval (default: True for hourly candles)
        """
        self.check_after_hour = check_after_hour
        self.check_interval = None  # Will be set if using fixed interval
        self.ist = timezone(TIMEZONE)
        self.seen_alerts = set()  # Track alerts we've already seen
        self.all_alerts = []  # Store all alerts
        self.selector = None
        self.symbols = []
        self.telegram = TelegramNotifier()
        
    def is_market_open(self) -> bool:
        """Check if market is currently open."""
        now = datetime.now(self.ist)
        weekday = now.weekday()
        
        # Market is closed on weekends
        if weekday >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Market hours: 9:15 AM - 3:30 PM IST
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def get_market_status(self) -> str:
        """Get current market status."""
        now = datetime.now(self.ist)
        weekday = now.weekday()
        
        if weekday >= 5:
            return "CLOSED (Weekend)"
        
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        if now < market_open:
            time_until_open = market_open - now
            minutes = int(time_until_open.total_seconds() / 60)
            return f"PRE-MARKET (Opens in {minutes} minutes)"
        elif now > market_close:
            return "CLOSED (Market closed for today)"
        else:
            time_until_close = market_close - now
            minutes = int(time_until_close.total_seconds() / 60)
            return f"OPEN (Closes in {minutes} minutes)"
    
    def get_next_check_time(self) -> datetime:
        """
        Get the next time to check for alerts.
        For hourly candles, check 30 seconds after each hour completes (9:15:30, 10:15:30, etc.)
        """
        now = datetime.now(self.ist)
        
        if self.check_after_hour:
            # Check at 9:15:30, 10:15:30, 11:15:30, 12:15:30, 13:15:30, 14:15:30, 15:15:30
            # (30 seconds after each hour to ensure hourly candle is complete and catch stocks on time)
            current_hour = now.hour
            current_minute = now.minute
            current_second = now.second
            
            # Market hours: 9:15 AM - 3:30 PM IST
            market_hours = [9, 10, 11, 12, 13, 14, 15]
            
            # Find next check time
            if current_hour < 9:
                # Before market opens, check at 9:15:30
                next_check = now.replace(hour=9, minute=15, second=30, microsecond=0)
            elif current_hour > 15 or (current_hour == 15 and current_minute >= 30):
                # After market closes, check tomorrow at 9:15:30
                next_check = (now + timedelta(days=1)).replace(hour=9, minute=15, second=30, microsecond=0)
            elif current_minute < 15 or (current_minute == 15 and current_second < 30):
                # Current hour hasn't completed yet, check at :15:30 of current hour
                next_check = now.replace(minute=15, second=30, microsecond=0)
            else:
                # Current hour has completed, check at :15:30 of next hour
                next_hour = current_hour + 1
                if next_hour in market_hours:
                    next_check = now.replace(hour=next_hour, minute=15, second=30, microsecond=0)
                else:
                    # Market closed, check tomorrow
                    next_check = (now + timedelta(days=1)).replace(hour=9, minute=15, second=30, microsecond=0)
            
            return next_check
        else:
            # Use fixed interval (fallback)
            if hasattr(self, 'check_interval') and self.check_interval:
                return now + self.check_interval
            else:
                return now + timedelta(minutes=5)
    
    def get_alert_key(self, alert) -> str:
        """Generate a unique key for an alert to track if we've seen it."""
        # Use symbol + timestamp + signal_type as unique key
        symbol = alert.get('symbol', '')
        timestamp = alert.get('timestamp', '')
        signal_type = alert.get('signal_type', '')
        return f"{symbol}|{timestamp}|{signal_type}"
    
    def save_alerts(self, alerts_df):
        """Save alerts to CSV file."""
        if not alerts_df.empty:
            alerts_df.to_csv('stock_selection_alerts.csv', index=False)
    
    async def check_for_alerts(self):
        """Check for new alerts."""
        try:
            check_time = datetime.now(self.ist)
            print(f"\n{'='*80}")
            print(f"⏰ CHECK TIME: {check_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"{'='*80}")
            print(f"[{check_time.strftime('%H:%M:%S')}] Starting alert check...")
            
            # Determine the most recent completed candle
            # A candle at hour H completes at hour H+1 (e.g., 9:15 candle completes at 10:15)
            current_hour = check_time.hour
            current_minute = check_time.minute
            current_second = check_time.second
            market_hours = [9, 10, 11, 12, 13, 14, 15]
            
            if current_hour < 9:
                print(f"   ⚪ Market hasn't opened yet")
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
                print(f"   ⚪ Current hour ({current_hour}:{current_minute:02d}) hasn't completed yet")
                print(f"   The {current_hour-1}:15 candle will complete at {current_hour}:15")
                return
            else:
                print(f"   ⚪ It's too early (before 9:15 AM)")
                return
            
            if most_recent_candle_hour not in market_hours:
                print(f"   ⚪ Invalid candle hour: {most_recent_candle_hour}")
                return
            
            print(f"   📊 Checking for alerts in {most_recent_candle_hour}:15 candle (completed at {completed_at})")
            
            # Run analysis
            summary_df, alerts_df = await self.selector.analyze_symbols(
                self.symbols, 
                max_workers=int(os.getenv('MAX_WORKERS', DEFAULT_MAX_WORKERS)),
                days=int(os.getenv('HISTORICAL_DAYS', DEFAULT_HISTORICAL_DAYS))
            )
            
            if alerts_df.empty:
                print(f"   ⚪ No alerts at this time")
                return
            
            # Filter alerts to only include the most recent completed candle
            candle_start_time = check_time.replace(hour=most_recent_candle_hour, minute=15, second=0, microsecond=0)
            # For the last candle (15:15), it ends at 15:30, not 16:15
            if most_recent_candle_hour == 15:
                candle_end_time = check_time.replace(hour=15, minute=30, second=0, microsecond=0)
            else:
                candle_end_time = check_time.replace(hour=most_recent_candle_hour+1, minute=15, second=0, microsecond=0)
            
            # Convert timestamp column to datetime if needed
            if 'timestamp' in alerts_df.columns:
                alerts_df['alert_time'] = pd.to_datetime(alerts_df['timestamp'])
                
                # Ensure timezone-aware comparison (convert alert_time to IST if needed)
                if alerts_df['alert_time'].dt.tz is None:
                    # If alerts are timezone-naive, assume they're in IST
                    alerts_df['alert_time'] = alerts_df['alert_time'].dt.tz_localize(self.ist)
                else:
                    # Convert to IST if in different timezone
                    alerts_df['alert_time'] = alerts_df['alert_time'].dt.tz_convert(self.ist)
                
                # Filter to only the most recent completed candle
                recent_alerts_df = alerts_df[
                    (alerts_df['alert_time'] >= candle_start_time) & 
                    (alerts_df['alert_time'] < candle_end_time)
                ].copy()
                
                if recent_alerts_df.empty:
                    print(f"   ⚪ No alerts for {most_recent_candle_hour}:15 candle")
                    
                    # Send Telegram notification for no alerts
                    if self.telegram.enabled:
                        no_alerts_msg = f"⚪ *No Alerts Detected*\n\n"
                        no_alerts_msg += f"📊 Candle: {most_recent_candle_hour}:15\n"
                        no_alerts_msg += f"⏰ Completed at: {completed_at}\n"
                        no_alerts_msg += f"📅 Date: {check_time.strftime('%Y-%m-%d')}\n\n"
                        no_alerts_msg += f"No stocks met the selection criteria for this candle."
                        await self.telegram.send_message(no_alerts_msg)
                        print(f"   📱 Sent 'no alerts' notification to Telegram")
                    
                    return
                
                print(f"   ✅ Found {len(recent_alerts_df)} alert(s) for {most_recent_candle_hour}:15 candle")
                alerts_df = recent_alerts_df.drop(columns=['alert_time'])
            
            # Find new alerts (from the filtered recent candle only)
            new_alerts = []
            new_alert_dicts = []  # For Telegram
            for _, alert in alerts_df.iterrows():
                alert_key = self.get_alert_key(alert)
                if alert_key not in self.seen_alerts:
                    self.seen_alerts.add(alert_key)
                    new_alerts.append(alert)
                    new_alert_dicts.append(alert.to_dict())
            
            if new_alerts:
                # Convert to DataFrame for sorting
                new_alerts_df = pd.DataFrame(new_alerts)
                
                # Sort alerts by volume ratio (highest first)
                new_alerts_df_sorted = new_alerts_df.sort_values('vol_ratio', ascending=False)
                
                # Update new_alert_dicts to match sorted order
                new_alert_dicts = [row.to_dict() for _, row in new_alerts_df_sorted.iterrows()]
                
                print(f"\n🔔 NEW ALERTS DETECTED: {len(new_alerts)} alerts (sorted by volume ratio - highest first)")
                print("="*80)
                
                for _, alert in new_alerts_df_sorted.iterrows():
                    timestamp = alert.get('timestamp', 'N/A')
                    symbol = alert.get('symbol', 'N/A')
                    signal_type = alert.get('signal_type', 'N/A')
                    price = alert.get('price', 0)
                    vol_ratio = alert.get('vol_ratio', 0)
                    swing_high = alert.get('swing_high', 0)
                    swing_low = alert.get('swing_low', 0)
                    
                    if signal_type == 'BREAKOUT':
                        level = swing_high
                        direction = "ABOVE"
                    else:
                        level = swing_low
                        direction = "BELOW"
                    
                    print(f"\n🚨 {symbol} - {signal_type}")
                    print(f"   Time: {timestamp}")
                    print(f"   Price: ₹{price:.2f}")
                    print(f"   Level: ₹{level:.2f} ({direction})")
                    print(f"   Volume: {vol_ratio:.2f}x average")
                    print("-" * 80)
                
                # Send Telegram notifications (in sorted order)
                if self.telegram.enabled:
                    print(f"\n📱 Sending Telegram notifications...")
                    sent_count = await self.telegram.send_alerts_batch(new_alert_dicts, max_alerts=10)
                    if sent_count > 0:
                        print(f"   ✅ Sent {sent_count} alert(s) to Telegram (sorted by volume ratio)")
                    else:
                        print(f"   ⚠️  Failed to send Telegram notifications")
                
                # Save all alerts
                self.save_alerts(alerts_df)
                print(f"\n💾 All alerts saved to stock_selection_alerts.csv")
            else:
                print(f"   ✅ No new alerts (total: {len(alerts_df)} alerts seen)")
            
        except Exception as e:
            print(f"   ❌ Error checking for alerts: {e}")
            import traceback
            traceback.print_exc()
    
    async def run(self):
        """Run continuous monitoring."""
        print("="*80)
        print("CONTINUOUS REAL-TIME ALERT MONITORING")
        print("="*80)
        
        # Check credentials
        api_key = os.getenv('UPSTOX_API_KEY')
        access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
        
        if not api_key or not access_token:
            print("❌ Error: UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN must be set")
            print("\nUsage:")
            print("  Windows PowerShell:")
            print("    $env:UPSTOX_API_KEY='your_api_key'")
            print("    $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
            print("    python scripts/run_continuous_alerts.py")
            return
        
        print("✅ Credentials found")
        
        # Initialize selector
        print("\nInitializing stock selector...")
        self.selector = UpstoxStockSelector(api_key, access_token)
        
        # Load symbols
        print("Loading symbols...")
        import json
        nse_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
        
        if not os.path.exists(nse_path):
            print(f"❌ NSE.json not found at {nse_path}")
            return
        
        with open(nse_path, 'r') as f:
            nse_data = json.load(f)
        
        self.symbols = [item.get('tradingsymbol') for item in nse_data if item.get('tradingsymbol')]
        self.symbols = [s for s in self.symbols if s]
        
        print(f"✅ Loaded {len(self.symbols)} symbols")
        
        # Display list of symbols being monitored
        print(f"\n📋 Stocks being monitored ({len(self.symbols)} symbols):")
        # Display in columns for better readability
        symbols_sorted = sorted(self.symbols)
        cols = 5  # Number of columns
        for i in range(0, len(symbols_sorted), cols):
            row_symbols = symbols_sorted[i:i+cols]
            # Format with padding for alignment
            formatted_row = "  ".join(f"{symbol:12s}" for symbol in row_symbols)
            print(f"   {formatted_row}")
        
        # Display configuration
        startup_time = datetime.now(self.ist)
        print("\n" + "="*80)
        print("MONITORING CONFIGURATION")
        
        # Determine the most recent completed hour slot and run immediate check
        # Note: A 9:15 candle runs from 9:15 to 10:15 (completes at 10:15)
        # So if current time is 10:20, the most recent completed candle is 9:15 (not 10:15)
        if self.check_after_hour:
            current_hour = startup_time.hour
            current_minute = startup_time.minute
            current_second = startup_time.second
            
            # Market hours: 9:15 AM - 3:30 PM IST
            market_hours = [9, 10, 11, 12, 13, 14, 15]
            
            # Find the most recent completed hour slot
            # A candle at hour H completes at hour H+1 (e.g., 9:15 candle completes at 10:15)
            if current_hour < 9:
                # Before market opens, no check needed
                most_recent_slot = None
            elif current_hour > 15 or (current_hour == 15 and current_minute >= 30):
                # After market closes, check the last slot (15:15:30, which completed at 15:30)
                most_recent_slot = startup_time.replace(hour=15, minute=15, second=30, microsecond=0)
            elif current_minute > 15 or (current_minute == 15 and current_second >= 30):
                # Current hour has passed 15 minutes, so previous hour's candle has completed
                # Example: If it's 10:20, the 9:15 candle (which completed at 10:15) is the most recent
                prev_hour = current_hour - 1
                if prev_hour in market_hours:
                    most_recent_slot = startup_time.replace(hour=prev_hour, minute=15, second=30, microsecond=0)
                else:
                    most_recent_slot = None
            elif current_hour > 9:
                # Current hour hasn't reached 15 minutes yet, check previous hour
                # Example: If it's 10:10, the 9:15 candle (which completed at 10:15) hasn't completed yet
                # But if it's 10:14, we're very close, so check 9:15 slot
                prev_hour = current_hour - 1
                if prev_hour in market_hours:
                    most_recent_slot = startup_time.replace(hour=prev_hour, minute=15, second=30, microsecond=0)
                else:
                    most_recent_slot = None
            else:
                # It's 9:15 or earlier, no previous slot
                most_recent_slot = None
            
            # Run immediate check for most recent slot if it exists and is within last hour
            if most_recent_slot:
                time_since_slot = startup_time - most_recent_slot
                if time_since_slot.total_seconds() <= 3600:  # Within last hour
                    print(f"\n🚀 Running immediate check for most recent completed time slot: {most_recent_slot.strftime('%H:%M:%S')}")
                    print(f"   (This candle completed at {(most_recent_slot + timedelta(hours=1)).strftime('%H:%M')})")
                    print("="*80)
                    await self.check_for_alerts()
                    print("\n" + "="*80)
                    print("✅ Immediate check completed. Continuing with scheduled checks...")
                    print("="*80)
        
        print("="*80)
        print(f"🚀 Script started at: {startup_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        if self.check_after_hour:
            print("Check strategy: 30 seconds after each hour completes (9:15:30, 10:15:30, 11:15:30, etc.)")
            print("   This ensures we check right after hourly candles are available")
            print("   Maximum delay: ~30 seconds after hour completes for faster alerts")
            print(f"\n📅 Scheduled check times today:")
            market_hours = [9, 10, 11, 12, 13, 14, 15]
            for hour in market_hours:
                check_time = startup_time.replace(hour=hour, minute=15, second=30, microsecond=0)
                if check_time >= startup_time:
                    print(f"   • {check_time.strftime('%H:%M:%S')}")
        else:
            print(f"Check interval: {int(self.check_interval.total_seconds() / 60)} minutes")
        print(f"Symbols monitored: {len(self.symbols)}")
        print(f"Market hours: 9:15 AM - 3:30 PM IST")
        print(f"Press Ctrl+C to stop")
        print("="*80)
        
        # Main monitoring loop
        try:
            while True:
                now = datetime.now(self.ist)
                status = self.get_market_status()
                
                print(f"\n{'='*80}")
                print(f"📊 STATUS CHECK: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   Market Status: {status}")
                print(f"{'='*80}")
                
                if self.is_market_open():
                    # Market is open - check for alerts
                    await self.check_for_alerts()
                    
                    # Calculate next check time
                    next_check = self.get_next_check_time()
                    wait_seconds = (next_check - now).total_seconds()
                    
                    if wait_seconds > 0:
                        if wait_seconds < 60:
                            print(f"\n⏰ Next check at: {next_check.strftime('%H:%M:%S')} (in {int(wait_seconds)} seconds)")
                        else:
                            print(f"\n⏰ Next check at: {next_check.strftime('%H:%M:%S')} (in {int(wait_seconds/60)} minutes)")
                        print("   (Press Ctrl+C to stop)")
                        print(f"💤 Waiting until {next_check.strftime('%H:%M:%S')}...")
                        
                        # Show periodic heartbeat while waiting (every 5 minutes)
                        wait_start = datetime.now(self.ist)
                        last_heartbeat = 0
                        while True:
                            elapsed = (datetime.now(self.ist) - wait_start).total_seconds()
                            remaining = wait_seconds - elapsed
                            
                            if remaining <= 0:
                                break
                            
                            # Show heartbeat every 5 minutes
                            if int(elapsed) >= last_heartbeat + 300 and elapsed > 0:
                                last_heartbeat = int(elapsed)
                                mins_remaining = int(remaining / 60)
                                secs_remaining = int(remaining % 60)
                                print(f"   💓 Heartbeat: Still waiting... {mins_remaining}m {secs_remaining}s until next check at {next_check.strftime('%H:%M:%S')}")
                            
                            # Sleep in smaller chunks to allow for early wake-up
                            sleep_time = min(30, remaining)  # Check every 30 seconds
                            if sleep_time > 0:
                                await asyncio.sleep(sleep_time)
                            else:
                                break
                    else:
                        # Next check time is in the past (shouldn't happen), wait 1 minute
                        await asyncio.sleep(60)
                else:
                    # Market is closed - wait and check again
                    if "Weekend" in status:
                        print("   Market is closed for the weekend")
                        print("   Waiting 1 hour before checking again...")
                        await asyncio.sleep(3600)  # Wait 1 hour
                    elif "PRE-MARKET" in status:
                        # Calculate time until market opens
                        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
                        wait_seconds = (market_open - now).total_seconds()
                        if wait_seconds > 0:
                            print(f"   Waiting for market to open...")
                            # Wait until 9:15:30 (first check time)
                            first_check = now.replace(hour=9, minute=15, second=30, microsecond=0)
                            wait_seconds = (first_check - now).total_seconds()
                            if wait_seconds > 0:
                                await asyncio.sleep(min(wait_seconds, 300))  # Wait max 5 minutes
                    else:
                        # Market closed for today
                        print("   Market closed for today")
                        print("   Monitoring will resume tomorrow at 9:15:30 AM")
                        print("   (Press Ctrl+C to stop)")
                        # Wait until tomorrow 9:15:30
                        tomorrow = (now + timedelta(days=1)).replace(hour=9, minute=15, second=30, microsecond=0)
                        wait_seconds = (tomorrow - now).total_seconds()
                        await asyncio.sleep(min(wait_seconds, 3600))  # Wait max 1 hour
                        
        except KeyboardInterrupt:
            print("\n\n" + "="*80)
            print("MONITORING STOPPED BY USER")
            print("="*80)
            print(f"Total alerts detected: {len(self.seen_alerts)}")
            print("✅ All alerts saved to stock_selection_alerts.csv")
            print("="*80)
        except Exception as e:
            print(f"\n❌ Error in monitoring loop: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main function."""
    # Check if user wants fixed interval instead of hourly checks
    use_fixed_interval = os.getenv('USE_FIXED_INTERVAL', 'false').lower() == 'true'
    
    if use_fixed_interval:
        # Use fixed interval (for testing or custom schedules)
        check_interval_seconds = os.getenv('ALERT_CHECK_INTERVAL_SECONDS')
        if check_interval_seconds:
            check_interval = int(check_interval_seconds) / 60  # Convert seconds to minutes
        else:
            check_interval = int(os.getenv('ALERT_CHECK_INTERVAL_MINUTES', '5'))  # Default: 5 minutes
        
        # Create monitor with fixed interval
        monitor = ContinuousAlertMonitor(check_after_hour=False)
        monitor.check_interval = timedelta(minutes=check_interval)
    else:
        # Use hourly check strategy (default - most efficient for hourly candles)
        monitor = ContinuousAlertMonitor(check_after_hour=True)
    
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())

