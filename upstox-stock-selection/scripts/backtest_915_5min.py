"""
Backtest script for 9:15 candle shortlisted stocks with 5-minute holding period.

This script:
1. Gets stocks shortlisted at 9:15 candle
2. Backtests them with 5-minute holding period
3. Uses 5-minute candles from Upstox API
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timedelta, date
from pytz import timezone

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import aiohttp
import urllib.parse
from src.config.settings import UPSTOX_BASE_URL, TIMEZONE, DEFAULT_NSE_JSON_PATH, LOOKBACK_SWING, VOL_WINDOW, VOL_MULT
from src.core.stock_selector import UpstoxStockSelector


# For 5-minute candles, adjust parameters
# Since we only have today's data (44 bars), use smaller windows
# VOL_WINDOW = 70 bars for hourly = 10 days * 7 bars/day
# For 5-minute with single day: Use 30 bars (about 2.5 hours) for volume average
VOL_WINDOW_5MIN = 30  # 30 bars = ~2.5 hours of 5-minute candles
LOOKBACK_SWING_5MIN = 12  # 12 bars = 1 hour of 5-minute candles
HOLD_BARS_5MIN = 1  # Hold for 1 bar = 5 minutes


async def fetch_5min_candles(access_token: str, instrument_key: str, symbol: str, target_date: date = None):
    """Fetch 5-minute candles from Upstox API."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    ist = timezone(TIMEZONE)
    
    # Encode instrument key for URL (| needs to be encoded as %7C)
    encoded_instrument_key = urllib.parse.quote(instrument_key, safe='')
    
    # Use intraday API for 5-minute candles (only works for current trading day)
    # Format: /historical-candle/intraday/{instrument_key}/minutes/{interval}
    url = f"{UPSTOX_BASE_URL}/historical-candle/intraday/{encoded_instrument_key}/minutes/5"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response_text = await response.text()
                if response.status == 200:
                    try:
                        data = await response.json()
                    except:
                        print(f"  ⚠️  Failed to parse JSON response: {response_text[:200]}")
                        return None
                    
                    # Handle different response structures
                    candles = None
                    if 'data' in data:
                        if 'candles' in data['data']:
                            candles = data['data']['candles']
                        elif isinstance(data['data'], list):
                            candles = data['data']
                    elif isinstance(data, list):
                        candles = data
                    
                    if candles and len(candles) > 0:
                            # Convert to DataFrame
                            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
                            
                            # Convert timestamp (try different formats)
                            try:
                                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                                if df['timestamp'].isna().any():
                                    # Try milliseconds
                                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
                            except:
                                # Try seconds
                                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
                            
                            df.set_index('timestamp', inplace=True)
                            # Convert to IST (assuming timestamp is in UTC)
                            if df.index.tz is None:
                                df.index = df.index.tz_localize('UTC')
                            df.index = df.index.tz_convert(ist)
                            
                            # Convert to numeric
                            for col in ['open', 'high', 'low', 'close', 'volume', 'oi']:
                                df[col] = pd.to_numeric(df[col], errors='coerce')
                            
                            df = df.dropna()
                            return df
                    else:
                        print(f"  ⚠️  Unexpected response format: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        print(f"  Response: {str(data)[:500]}")
                else:
                    error_text = await response.text()
                    print(f"  ⚠️  API error: Status {response.status}")
                    print(f"  Error details: {error_text[:500]}")
                    print(f"  URL: {url}")
        return None
    except Exception as e:
        print(f"  Error fetching 5-min candles for {symbol}: {e}")
        return None


def calculate_indicators_5min(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate indicators for 5-minute candles."""
    # Swing high/low (using LOOKBACK_SWING_5MIN)
    df['swing_high'] = df['high'].rolling(LOOKBACK_SWING_5MIN).max() * 0.995
    df['swing_low'] = df['low'].rolling(LOOKBACK_SWING_5MIN).min() * 1.005
    
    # Volume average (using VOL_WINDOW_5MIN)
    df['avg_vol'] = df['volume'].rolling(VOL_WINDOW_5MIN).mean()
    df['vol_ratio'] = df['volume'] / df['avg_vol']
    
    # Range
    df['range'] = df['high'] - df['low']
    df['avg_range'] = df['range'].rolling(LOOKBACK_SWING_5MIN).mean()
    
    return df


def detect_signals_5min(df: pd.DataFrame, symbol: str) -> list:
    """Detect signals for 5-minute candles with 5-minute holding period."""
    alerts = []
    
    start_i = int(max(LOOKBACK_SWING_5MIN, VOL_WINDOW_5MIN)) + 1
    end_i = len(df) - HOLD_BARS_5MIN  # Hold for 1 bar (5 minutes)
    
    if start_i >= end_i:
        return alerts
    
    for i in range(start_i, end_i):
        prev_close = df['close'].iloc[i-1]
        curr_close = df['close'].iloc[i]
        swing_high_prev = df['swing_high'].iloc[i-1]
        swing_low_prev = df['swing_low'].iloc[i-1]
        vol_ratio = df['vol_ratio'].iloc[i]
        range_val = df['range'].iloc[i]
        avg_range = df['avg_range'].iloc[i]
        curr_open = df['open'].iloc[i]
        timestamp = df.index[i]
        
        # Strong candle conditions
        strong_bull = (curr_close > curr_open) or (range_val > avg_range if not pd.isna(avg_range) else False)
        strong_bear = (curr_close < curr_open) or (range_val > avg_range if not pd.isna(avg_range) else False)
        
        # Breakout: crosses above previous swing high
        crosses_above = (prev_close <= swing_high_prev) and (curr_close > swing_high_prev)
        
        if crosses_above and (vol_ratio >= VOL_MULT) and strong_bull:
            # Entry: next bar's open
            if i + 1 < len(df):
                entry_price = df['open'].iloc[i+1]
            else:
                entry_price = curr_close
            
            # Exit: after 1 bar (5 minutes)
            exit_price = df['close'].iloc[i + HOLD_BARS_5MIN]
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100.0
            
            alerts.append({
                'symbol': symbol,
                'timestamp': timestamp,
                'signal_type': 'BREAKOUT',
                'price': curr_close,
                'swing_high': swing_high_prev,
                'swing_low': swing_low_prev,
                'vol_ratio': vol_ratio,
                'range': range_val,
                'avg_range': avg_range,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl_pct': pnl_pct,
                'bars_after': HOLD_BARS_5MIN
            })
        
        # Breakdown: crosses below previous swing low
        crosses_below = (prev_close >= swing_low_prev) and (curr_close < swing_low_prev)
        
        if crosses_below and (vol_ratio >= VOL_MULT) and strong_bear:
            # Entry: next bar's open
            if i + 1 < len(df):
                entry_price = df['open'].iloc[i+1]
            else:
                entry_price = curr_close
            
            # Exit: after 1 bar (5 minutes)
            exit_price = df['close'].iloc[i + HOLD_BARS_5MIN]
            pnl_pct = ((entry_price - exit_price) / entry_price) * 100.0
            
            alerts.append({
                'symbol': symbol,
                'timestamp': timestamp,
                'signal_type': 'BREAKDOWN',
                'price': curr_close,
                'swing_high': swing_high_prev,
                'swing_low': swing_low_prev,
                'vol_ratio': vol_ratio,
                'range': range_val,
                'avg_range': avg_range,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl_pct': pnl_pct,
                'bars_after': HOLD_BARS_5MIN
            })
    
    return alerts


async def backtest_915_stocks():
    """Backtest stocks shortlisted at 9:15 candle with 5-minute holding period.
    
    Logic:
    1. Use hourly candles to detect 9:15 signal (completes at 10:15)
    2. Entry: 10:15 (when signal is detected/alert received)
    3. Exit: 10:20 (5 minutes later)
    """
    print("="*80)
    print("BACKTEST: 9:15 CANDLE STOCKS WITH 5-MINUTE HOLDING PERIOD")
    print("="*80)
    
    # Stocks shortlisted at 9:15 (from earlier run)
    stocks_915 = [
        'BRITANNIA', 'BAJAJFINSV', 'BAJFINANCE', 'SOLARINDS', 'ONGC', 
        'BEL', 'HAVELLS', 'PFC', 'TMPV', 'BAJAJHFL', 'MAZDOCK', 
        'ADANIPOWER', 'IRFC'
    ]
    
    print(f"\n📊 Stocks to backtest: {len(stocks_915)}")
    print(f"   {', '.join(stocks_915)}")
    
    # Check credentials
    api_key = os.getenv('UPSTOX_API_KEY')
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not api_key or not access_token:
        print("\n❌ Error: UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN must be set")
        return
    
    # Load instrument map
    nse_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    if not os.path.exists(nse_path):
        print(f"\n❌ NSE.json not found at {nse_path}")
        return
    
    with open(nse_path, 'r') as f:
        nse_data = json.load(f)
    
    instrument_map = {}
    for item in nse_data:
        symbol = item.get('tradingsymbol', '')
        instrument_key = item.get('instrument_key')
        if symbol and instrument_key:
            instrument_map[symbol] = instrument_key
    
    # Use today's date
    ist = timezone(TIMEZONE)
    today = datetime.now(ist).date()
    target_date = today
    
    print(f"\n📅 Backtesting for date: {target_date}")
    print(f"📊 Step 1: Detect 9:15 hourly candle signals (completes at 10:15)")
    print(f"📊 Step 2: Entry at 10:15, Exit at 10:20 (5 minutes later)")
    print(f"⏰ Holding period: 5 minutes")
    print("="*80)
    
    # Initialize stock selector for hourly candle detection
    selector = UpstoxStockSelector(api_key, access_token, nse_path)
    
    # Step 1: Detect signals using hourly candles (like the main system)
    print(f"\n📊 Step 1: Detecting 9:15 hourly candle signals...")
    summary_df, alerts_df = await selector.analyze_symbols(
        stocks_915,
        max_workers=10,
        days=30
    )
    
    if alerts_df.empty:
        print("\n⚠️  No alerts found from hourly candle system")
        return
    
    # Filter to only 9:15 candle alerts (9:15 to 10:15)
    candle_start = ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=9, minute=15)))
    candle_end = ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=15)))
    
    alerts_df['alert_time'] = pd.to_datetime(alerts_df['timestamp'])
    if alerts_df['alert_time'].dt.tz is None:
        alerts_df['alert_time'] = alerts_df['alert_time'].dt.tz_localize(ist)
    else:
        alerts_df['alert_time'] = alerts_df['alert_time'].dt.tz_convert(ist)
    
    hourly_alerts = alerts_df[
        (alerts_df['alert_time'] >= candle_start) & 
        (alerts_df['alert_time'] < candle_end)
    ].copy()
    
    if hourly_alerts.empty:
        print("\n⚠️  No alerts found in 9:15 hourly candle")
        return
    
    print(f"\n✅ Found {len(hourly_alerts)} alert(s) in 9:15 hourly candle")
    
    # Step 2: Use 5-minute candles to get exact entry (10:15) and exit (10:20) prices
    print(f"\n📊 Step 2: Getting entry/exit prices from 5-minute candles...")
    print("="*80)
    
    all_alerts = []
    
    for _, hourly_alert in hourly_alerts.iterrows():
        symbol = hourly_alert['symbol']
        
        if symbol not in instrument_map:
            print(f"\n⚠️  {symbol}: Instrument key not found, skipping")
            continue
        
        instrument_key = instrument_map[symbol]
        print(f"\n📈 Processing {symbol}...")
        
        # Fetch 5-minute candles
        df_5min = await fetch_5min_candles(access_token, instrument_key, symbol, target_date)
        
        if df_5min is None or df_5min.empty:
            print(f"  ⚠️  No 5-minute data for {symbol}, skipping")
            continue
        
        # Find entry price at 10:15 (when 9:15 candle completes and alert is received)
        # 5-minute candles are at: 9:15, 9:20, 9:25, 9:30, 9:35, 9:40, 9:45, 9:50, 9:55, 10:00, 10:05, 10:10, 10:15, 10:20, ...
        entry_time_start = ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=15)))
        entry_time_end = ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=20)))
        exit_time_start = ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=20)))
        exit_time_end = ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=25)))
        
        # Get entry price (10:15 candle's open)
        # Look for candle that starts at 10:15 (within 10:15 to 10:20 range)
        entry_candle = df_5min[(df_5min.index >= entry_time_start) & (df_5min.index < entry_time_end)]
        
        if entry_candle.empty:
            print(f"  ⚠️  No entry candle found at 10:15 for {symbol}")
            print(f"     Available candles around 10:15: {df_5min[(df_5min.index >= ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=10)))) & (df_5min.index < ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=25))))].index.tolist()}")
            continue
        
        # Use the first candle in the 10:15-10:20 range (the 10:15 candle)
        entry_price = entry_candle.iloc[0]['open']
        entry_timestamp = entry_candle.index[0]
        
        # Get exit price at 10:20 (5 minutes later)
        # Look for candle that starts at 10:20 (within 10:20 to 10:25 range)
        exit_candle = df_5min[(df_5min.index >= exit_time_start) & (df_5min.index < exit_time_end)]
        
        if exit_candle.empty:
            print(f"  ⚠️  No exit candle found at 10:20 for {symbol}")
            print(f"     Available candles around 10:20: {df_5min[(df_5min.index >= ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=15)))) & (df_5min.index < ist.localize(datetime.combine(target_date, datetime.min.time().replace(hour=10, minute=30))))].index.tolist()}")
            continue
        
        # Use the first candle in the 10:20-10:25 range (the 10:20 candle)
        exit_price = exit_candle.iloc[0]['close']  # Use close price of 10:20 candle
        exit_timestamp = exit_candle.index[0]
        
        # Calculate P&L
        signal_type = hourly_alert['signal_type']
        if signal_type == 'BREAKOUT':
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100.0
        else:  # BREAKDOWN
            pnl_pct = ((entry_price - exit_price) / entry_price) * 100.0
        
        print(f"  ✅ Entry: {entry_timestamp.strftime('%H:%M')} @ ₹{entry_price:.2f}")
        print(f"     Exit: {exit_timestamp.strftime('%H:%M')} @ ₹{exit_price:.2f}")
        print(f"     P&L: {pnl_pct:.2f}%")
        
        # Create alert with correct entry/exit
        alert = {
            'symbol': symbol,
            'timestamp': hourly_alert['timestamp'],  # Keep original 9:15 signal timestamp
            'signal_type': signal_type,
            'price': hourly_alert['price'],
            'swing_high': hourly_alert['swing_high'],
            'swing_low': hourly_alert['swing_low'],
            'vol_ratio': hourly_alert['vol_ratio'],
            'range': hourly_alert.get('range', 0),
            'avg_range': hourly_alert.get('avg_range', 0),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_time': entry_timestamp,
            'exit_time': exit_timestamp,
            'pnl_pct': pnl_pct,
            'bars_after': 1  # 1 bar = 5 minutes
        }
        
        all_alerts.append(alert)
    
    # Display results
    print("\n" + "="*80)
    print("BACKTEST RESULTS")
    print("="*80)
    
    if not all_alerts:
        print("\n⚠️  No alerts found for 9:15 candle with 5-minute holding period")
        return
    
    alerts_df = pd.DataFrame(all_alerts)
    
    # Sort by volume ratio
    alerts_df = alerts_df.sort_values('vol_ratio', ascending=False)
    
    print(f"\n✅ Total alerts: {len(alerts_df)}")
    
    breakouts = alerts_df[alerts_df['signal_type'] == 'BREAKOUT']
    breakdowns = alerts_df[alerts_df['signal_type'] == 'BREAKDOWN']
    
    print(f"   Breakouts: {len(breakouts)}")
    print(f"   Breakdowns: {len(breakdowns)}")
    
    # Calculate statistics
    pnl_values = alerts_df['pnl_pct'].tolist()
    winning = [p for p in pnl_values if p > 0]
    losing = [p for p in pnl_values if p <= 0]
    
    print(f"\n📊 Performance (5-minute holding period):")
    print(f"   Total trades: {len(pnl_values)}")
    print(f"   Winning trades: {len(winning)}")
    print(f"   Losing trades: {len(losing)}")
    print(f"   Win rate: {len(winning)/len(pnl_values)*100:.2f}%")
    print(f"   Average P&L: {sum(pnl_values)/len(pnl_values):.2f}%")
    print(f"   Net P&L: {sum(pnl_values):.2f}%")
    
    if losing:
        total_profit = sum(winning) if winning else 0
        total_loss = abs(sum(losing))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        print(f"   Profit factor: {profit_factor:.2f}")
    
    # Show all alerts
    print(f"\n📋 All Alerts (sorted by volume ratio):")
    for _, alert in alerts_df.iterrows():
        # Signal timestamp (9:15 candle)
        signal_timestamp = alert['timestamp']
        if isinstance(signal_timestamp, str):
            signal_timestamp = pd.to_datetime(signal_timestamp)
        signal_str = signal_timestamp.strftime('%H:%M:%S')
        
        # Entry and exit times
        entry_time = alert.get('entry_time', None)
        exit_time = alert.get('exit_time', None)
        
        if entry_time:
            if isinstance(entry_time, str):
                entry_time = pd.to_datetime(entry_time)
            entry_str = entry_time.strftime('%H:%M')
        else:
            entry_str = "N/A"
        
        if exit_time:
            if isinstance(exit_time, str):
                exit_time = pd.to_datetime(exit_time)
            exit_str = exit_time.strftime('%H:%M')
        else:
            exit_str = "N/A"
        
        print(f"\n   Signal: {signal_str} | {alert['symbol']:15} | {alert['signal_type']:10}")
        print(f"      Entry: {entry_str} @ ₹{alert['entry_price']:.2f} | Exit: {exit_str} @ ₹{alert['exit_price']:.2f} | P&L: {alert['pnl_pct']:.2f}%")
        print(f"      Volume: {alert['vol_ratio']:.2f}x")
    
    # Save to CSV (handle file permission error)
    try:
        alerts_df.to_csv('backtest_915_5min.csv', index=False)
        print(f"\n💾 Results saved to backtest_915_5min.csv")
    except PermissionError:
        print(f"\n⚠️  Could not save CSV (file may be open). Results displayed above.")
    
    print("\n" + "="*80)
    print("✅ Backtest completed!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(backtest_915_stocks())

