"""
Streamlit UI for Upstox Stock Selection System

This UI allows users to configure all parameters and run stock selection analysis.
"""

import streamlit as st
import asyncio
import os
import sys
from datetime import datetime, date, timedelta, time as dtime
import pandas as pd
from pytz import timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.core.stock_selector import UpstoxStockSelector
from src.config.settings import (
    LOOKBACK_SWING,
    VOL_WINDOW,
    VOL_MULT,
    HOLD_BARS,
    DEFAULT_HISTORICAL_DAYS,
    DEFAULT_INTERVAL,
    DEFAULT_MAX_WORKERS,
    DEFAULT_NSE_JSON_PATH,
)

# Page config
st.set_page_config(
    page_title="Upstox Stock Selection",
    page_icon="📈",
    layout="wide"
)

# Default values (current system values)
DEFAULT_VALUES = {
    'interval': DEFAULT_INTERVAL,
    'lookback_swing': LOOKBACK_SWING,
    'vol_window': VOL_WINDOW,
    'vol_mult': VOL_MULT,
    'hold_bars': HOLD_BARS,
    'historical_days': DEFAULT_HISTORICAL_DAYS,
    'max_workers': DEFAULT_MAX_WORKERS,
}

# Available intervals
INTERVALS = ['1m', '5m', '10m', '15m', '30m', '1h', '2h', '4h', '1d']

def initialize_session_state():
    """Initialize session state with default values."""
    if 'params' not in st.session_state:
        st.session_state.params = DEFAULT_VALUES.copy()
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'running' not in st.session_state:
        st.session_state.running = False

def load_default_values():
    """Load default values into session state."""
    from datetime import date as _date
    st.session_state.params = DEFAULT_VALUES.copy()

    # Reset widget states so UI reflects defaults after rerun
    st.session_state['interval_select'] = DEFAULT_VALUES['interval']
    st.session_state['lookback_swing_input'] = int(DEFAULT_VALUES['lookback_swing'])
    st.session_state['vol_window_input'] = int(DEFAULT_VALUES['vol_window'])
    st.session_state['vol_mult_input'] = float(DEFAULT_VALUES['vol_mult'])
    st.session_state['hold_bars_input'] = int(DEFAULT_VALUES['hold_bars'])
    st.session_state['historical_days_input'] = int(DEFAULT_VALUES['historical_days'])
    st.session_state['max_workers_input'] = int(DEFAULT_VALUES['max_workers'])

    # Reset analysis scope controls
    st.session_state['use_specific_date_check'] = False
    st.session_state['selected_date'] = _date.today()
    st.session_state['only_recent_candle_check'] = True
    st.session_state['include_historical_check'] = False

    # Let recent candle time recompute based on defaults
    st.session_state['recent_candle_select'] = None
    st.session_state['selected_candle_dt'] = None

    st.success("Default values loaded!")

def main():
    """Main Streamlit app."""
    initialize_session_state()
    
    st.title("📈 Upstox Stock Selection System")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Time Interval
        interval_index = INTERVALS.index(st.session_state.params['interval']) if st.session_state.params['interval'] in INTERVALS else 5
        interval = st.selectbox(
            "Time Interval",
            options=INTERVALS,
            index=interval_index,
            key="interval_select",
            help="Candle interval for analysis (1m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 1d)"
        )

        # Recent candle selector (dynamic based on interval)
        st.markdown("### 🕒 Recent Candle (Today)")
        from datetime import timedelta, time as dtime
        from pytz import timezone as tz
        ist = tz("Asia/Kolkata")

        def interval_to_timedelta(iv: str) -> timedelta:
            if iv.endswith("m"):
                return timedelta(minutes=int(iv[:-1]))
            if iv.endswith("h"):
                return timedelta(hours=int(iv[:-1]))
            if iv.endswith("d"):
                return timedelta(days=int(iv[:-1]))
            # default to 1h
            return timedelta(hours=1)

        def generate_candle_times(iv: str, analysis_date: date = None):
            """Generate candle start times during market hours [09:15, 15:30) for the given date."""
            market_open = dtime(hour=9, minute=15)
            market_close = dtime(hour=15, minute=30)
            delta = interval_to_timedelta(iv)

            # Use selected date or today
            if analysis_date is None:
                analysis_date = date.today()
            
            # Build times for the selected date in IST
            start_dt = ist.localize(datetime.combine(analysis_date, market_open))
            end_dt = ist.localize(datetime.combine(analysis_date, market_close))

            # For 1d interval, only one candle at 09:15
            if iv.endswith("d"):
                return [start_dt]

            times = []
            t = start_dt
            while t < end_dt:
                times.append(t)
                t = t + delta
            # ensure not past close
            times = [t for t in times if t < end_dt]
            return times

        # Date picker for historical analysis (comes first so candle times can use it)
        st.markdown("### 📅 Analysis Date")
        use_specific_date = st.checkbox(
            "Use specific date (for historical analysis)",
            value=st.session_state.get('use_specific_date', False),
            key="use_specific_date_check",
            help="Check to analyze a specific past date instead of today"
        )
        
        # Save to session state
        st.session_state.use_specific_date = use_specific_date
        
        selected_date = None
        if use_specific_date:
            # Default to today, but allow past dates
            max_date = date.today()
            min_date = date(2020, 1, 1)  # Reasonable minimum
            default_date = st.session_state.get('selected_date', max_date)
            selected_date = st.date_input(
                "Select date",
                value=default_date,
                min_value=min_date,
                max_value=max_date,
                key="analysis_date_picker",
                help="Select the date to analyze (must be a trading day)"
            )
        else:
            selected_date = date.today()
        
        # Save to session state
        st.session_state.selected_date = selected_date
        
        # Build dropdown options like "09:15", "10:15", etc. (based on selected date)
        candle_times = generate_candle_times(interval, selected_date)
        
        # Find most recent completed candle by comparing with now
        now_ist = datetime.now(ist)
        # Only filter by "now" if analyzing today
        if selected_date == date.today():
            completed = [t for t in candle_times if t <= now_ist]
            default_time = completed[-1] if completed else (candle_times[-1] if candle_times else None)
        else:
            # For historical dates, use the last candle
            default_time = candle_times[-1] if candle_times else None

        def fmt_time(t: datetime) -> str:
            return t.strftime("%H:%M")

        candle_label_to_dt = {fmt_time(t): t for t in candle_times}
        candle_labels = list(candle_label_to_dt.keys()) or ["09:15"]
        default_index = candle_labels.index(fmt_time(default_time)) if default_time and fmt_time(default_time) in candle_labels else 0

        date_label = selected_date.strftime('%Y-%m-%d') if use_specific_date else "today"
        selected_candle_label = st.selectbox(
            f"Select recent candle time ({date_label})",
            options=candle_labels,
            index=default_index,
            key="recent_candle_select",
            help="Choose the recent closed candle to display results for"
        )
        selected_candle_dt = candle_label_to_dt.get(selected_candle_label, None)
        
        # Save to session state
        st.session_state.selected_candle_dt = selected_candle_dt

        # Controls for output scope
        st.markdown("### 📊 Results Scope")
        only_recent_candle = st.checkbox(
            "Show only selected recent closed candle",
            value=True,
            key="only_recent_candle_check",
            help="When checked, results are filtered to the chosen recent candle only"
        )
        include_historical = st.checkbox(
            "Include historical results (entire period)",
            value=False,
            key="include_historical_check",
            help="When checked, shows all alerts across the selected historical period"
        )
        
        # Save to session state
        st.session_state.only_recent_candle = only_recent_candle
        st.session_state.include_historical = include_historical
        
        if include_historical and only_recent_candle:
            st.info("Historical results enabled. Recent-candle filter will be ignored.")
        
        # Lookback Swing
        lookback_swing = st.number_input(
            "Lookback Swing (Bars)",
            min_value=1,
            max_value=100,
            value=int(st.session_state.params['lookback_swing']),
            key="lookback_swing_input",
            help="Number of bars for swing high/low calculation"
        )
        
        # Volume Window
        vol_window = st.number_input(
            "Volume Window (Bars)",
            min_value=1,
            max_value=500,
            value=int(st.session_state.params['vol_window']),
            key="vol_window_input",
            help="Number of bars for average volume calculation (e.g., 70 = 10 days * 7 bars/day for 1h)"
        )
        
        # Volume Multiplier
        vol_mult = st.number_input(
            "Volume Multiplier",
            min_value=0.1,
            max_value=10.0,
            value=float(st.session_state.params['vol_mult']),
            step=0.1,
            key="vol_mult_input",
            help="Volume spike threshold (e.g., 1.6 = 1.6x average volume)"
        )
        
        # Hold Bars
        hold_bars = st.number_input(
            "Hold Bars",
            min_value=1,
            max_value=100,
            value=int(st.session_state.params['hold_bars']),
            key="hold_bars_input",
            help="Number of bars to hold position for P&L calculation"
        )
        
        # Historical Days
        historical_days = st.number_input(
            "Historical Days",
            min_value=1,
            max_value=365,
            value=int(st.session_state.params['historical_days']),
            key="historical_days_input",
            help="Number of days of historical data to fetch"
        )
        
        # Max Workers
        max_workers = st.number_input(
            "Max Workers (Parallel)",
            min_value=1,
            max_value=50,
            value=int(st.session_state.params['max_workers']),
            key="max_workers_input",
            help="Number of parallel workers for analysis"
        )
        
        st.markdown("---")
        
        # Buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Load Defaults", use_container_width=True, key="load_defaults_btn"):
                load_default_values()
                st.rerun()
        
        with col2:
            if st.button("💾 Save Config", use_container_width=True):
                st.session_state.params = {
                    'interval': interval,
                    'lookback_swing': lookback_swing,
                    'vol_window': vol_window,
                    'vol_mult': vol_mult,
                    'hold_bars': hold_bars,
                    'historical_days': historical_days,
                    'max_workers': max_workers,
                }
                st.success("Configuration saved!")
    
    # Main content area
    st.header("📊 Stock Selection Analysis")
    
    # API Credentials
    st.subheader("🔑 API Credentials")
    col1, col2 = st.columns(2)
    
    with col1:
        api_key = st.text_input(
            "Upstox API Key",
            value=os.getenv('UPSTOX_API_KEY', ''),
            type="default",
            help="Your Upstox API Key"
        )
    
    with col2:
        access_token = st.text_input(
            "Upstox Access Token",
            value=os.getenv('UPSTOX_ACCESS_TOKEN', ''),
            type="default",
            help="Your Upstox Access Token"
        )
    
    # Update session state with current UI values
    st.session_state.params = {
        'interval': interval,
        'lookback_swing': lookback_swing,
        'vol_window': vol_window,
        'vol_mult': vol_mult,
        'hold_bars': hold_bars,
        'historical_days': historical_days,
        'max_workers': max_workers,
    }
    
    # Display current configuration
    with st.expander("📋 Current Configuration", expanded=False):
        config_df = pd.DataFrame([
            {"Parameter": "Time Interval", "Value": st.session_state.params['interval']},
            {"Parameter": "Lookback Swing", "Value": st.session_state.params['lookback_swing']},
            {"Parameter": "Volume Window", "Value": st.session_state.params['vol_window']},
            {"Parameter": "Volume Multiplier", "Value": st.session_state.params['vol_mult']},
            {"Parameter": "Hold Bars", "Value": st.session_state.params['hold_bars']},
            {"Parameter": "Historical Days", "Value": st.session_state.params['historical_days']},
            {"Parameter": "Max Workers", "Value": st.session_state.params['max_workers']},
        ])
        st.dataframe(config_df, use_container_width=True, hide_index=True)
    
    # Run button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear Results", use_container_width=True)
    
    if clear_button:
        st.session_state.results = None
        st.success("Results cleared!")
        st.rerun()
    
    # Run analysis
    if run_button:
        if not api_key or not access_token:
            st.error("❌ Please provide both API Key and Access Token!")
        else:
            st.session_state.running = True
            st.session_state.results = None
            
            with st.spinner("🔄 Running analysis... This may take a few minutes."):
                try:
                    # Create selector
                    selector = UpstoxStockSelector(api_key, access_token, DEFAULT_NSE_JSON_PATH)
                    
                    # Load symbols from NSE.json
                    import json
                    with open(DEFAULT_NSE_JSON_PATH, 'r') as f:
                        nse_data = json.load(f)
                    symbols = [item.get('tradingsymbol', '') for item in nse_data if item.get('tradingsymbol')]
                    symbols = [s for s in symbols if s]  # Remove empty
                    
                    if not symbols:
                        st.error("❌ No symbols found in NSE.json!")
                        st.session_state.running = False
                    else:
                        st.info(f"📊 Analyzing {len(symbols)} symbols...")
                        
                        # Temporarily override settings
                        import src.config.settings as settings
                        original_lookback = settings.LOOKBACK_SWING
                        original_vol_window = settings.VOL_WINDOW
                        original_vol_mult = settings.VOL_MULT
                        original_hold_bars = settings.HOLD_BARS
                        original_interval = settings.DEFAULT_INTERVAL
                        
                        # Override settings with UI values
                        settings.LOOKBACK_SWING = int(st.session_state.params['lookback_swing'])
                        settings.VOL_WINDOW = int(st.session_state.params['vol_window'])
                        settings.VOL_MULT = float(st.session_state.params['vol_mult'])
                        settings.HOLD_BARS = int(st.session_state.params['hold_bars'])
                        settings.DEFAULT_INTERVAL = st.session_state.params['interval']
                        
                        try:
                            # Get target date from session state (if specified)
                            target_date = st.session_state.get('selected_date', None)
                            
                            # Run analysis
                            summary_df, alerts_df = asyncio.run(
                                selector.analyze_symbols(
                                    symbols,
                                    max_workers=int(st.session_state.params['max_workers']),
                                    days=int(st.session_state.params['historical_days']),
                                    target_date=target_date
                                )
                            )
                            
                            # Store results
                            st.session_state.results = {
                                'summary': summary_df,
                                'alerts': alerts_df,
                                'params': st.session_state.params.copy()
                            }
                            
                            st.success(f"✅ Analysis complete! Found {len(alerts_df)} alerts.")
                            
                        finally:
                            # Restore original settings
                            settings.LOOKBACK_SWING = original_lookback
                            settings.VOL_WINDOW = original_vol_window
                            settings.VOL_MULT = original_vol_mult
                            settings.HOLD_BARS = original_hold_bars
                            settings.DEFAULT_INTERVAL = original_interval
                        
                        st.session_state.running = False
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.session_state.running = False
    
    # Display results
    if st.session_state.results:
        st.markdown("---")
        st.header("📊 Results")
        
        results = st.session_state.results
        summary_df = results['summary']
        alerts_df = results['alerts']
        
        # Get filter settings from session state (set in sidebar)
        include_historical = st.session_state.get('include_historical', False)
        only_recent_candle = st.session_state.get('only_recent_candle', True)
        selected_candle_dt = st.session_state.get('selected_candle_dt', None)
        selected_date = st.session_state.get('selected_date', None)
        
        # Import timezone for filtering
        from src.config.settings import TIMEZONE
        ist = timezone(TIMEZONE)
        
        # Helper function for interval to timedelta
        def interval_to_timedelta(iv: str) -> timedelta:
            """Convert interval string to timedelta."""
            if iv.endswith('m'):
                return timedelta(minutes=int(iv[:-1]))
            elif iv.endswith('h'):
                return timedelta(hours=int(iv[:-1]))
            elif iv.endswith('d'):
                return timedelta(days=int(iv[:-1]))
            return timedelta(hours=1)  # default
        
        # Filter to selected recent candle if requested and data present
        if not include_historical and only_recent_candle and selected_candle_dt is not None and not alerts_df.empty and 'timestamp' in alerts_df.columns:
            # Determine candle window [start, end)
            delta = interval_to_timedelta(st.session_state.params['interval'])
            candle_start = selected_candle_dt
            # Market close cap for intraday windows
            market_close_dt = ist.localize(datetime.combine(selected_candle_dt.date(), dtime(hour=15, minute=30)))
            candle_end_candidate = candle_start + delta
            candle_end = candle_end_candidate if candle_end_candidate <= market_close_dt else market_close_dt

            # Parse and localize timestamps
            alerts_df['alert_time'] = pd.to_datetime(alerts_df['timestamp'], errors='coerce')
            if alerts_df['alert_time'].dt.tz is None:
                alerts_df['alert_time'] = alerts_df['alert_time'].dt.tz_localize(ist)
            else:
                alerts_df['alert_time'] = alerts_df['alert_time'].dt.tz_convert(ist)

            filtered_alerts = alerts_df[(alerts_df['alert_time'] >= candle_start) & (alerts_df['alert_time'] < candle_end)].copy()
            # Drop temp column for display
            if 'alert_time' in filtered_alerts.columns:
                filtered_alerts = filtered_alerts.drop(columns=['alert_time'])

            date_str = selected_date.strftime('%Y-%m-%d') if selected_date else 'today'
            st.caption(f"Showing alerts for candle {candle_start.strftime('%H:%M')} - {candle_end.strftime('%H:%M')} IST ({date_str})")
            alerts_df = filtered_alerts
        
        # If user wants only the recent closed candle (intraday decision view),
        # show a compact, trader-focused panel like Telegram notifications
        if not include_historical and only_recent_candle:
            st.subheader("🔔 Intraday Alerts (Recent Closed Candle)")
            
            if alerts_df.empty:
                st.info("No alerts for the selected candle.")
            else:
                # Sort by volume ratio (highest first) to surface strongest moves
                if 'vol_ratio' in alerts_df.columns:
                    alerts_df = alerts_df.sort_values('vol_ratio', ascending=False)

                # Render compact notification-style lines
                for _, r in alerts_df.iterrows():
                    symbol = r.get('symbol', 'N/A')
                    signal_type = r.get('signal_type', 'N/A')
                    price = r.get('price', None)
                    vol_ratio = r.get('vol_ratio', None)
                    swing_high = r.get('swing_high', None)
                    swing_low = r.get('swing_low', None)
                    ts = r.get('timestamp', '')
                    
                    # Build a concise line
                    if signal_type == 'BREAKOUT':
                        line = f"🟢 {symbol}: Breakout + Volume Spike — above ₹{swing_high:.2f}"
                    else:
                        line = f"🔴 {symbol}: Breakdown + Volume Spike — below ₹{swing_low:.2f}"
                    
                    sub = []
                    if isinstance(price, (int, float)):
                        sub.append(f"Price: ₹{price:.2f}")
                    if isinstance(vol_ratio, (int, float)):
                        sub.append(f"Vol: {vol_ratio:.2f}×")
                    if ts:
                        sub.append(f"Time: {ts}")
                    
                    st.markdown(f"- {line}  \n  {' | '.join(sub)}")

                # Download current-candle alerts
                csv = alerts_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download These Alerts (CSV)",
                    data=csv,
                    file_name=f"recent_candle_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            # Full analytical view (includes historical if selected)
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Symbols", len(summary_df))
            
            with col2:
                total_trades = summary_df['trade_count'].sum() if 'trade_count' in summary_df.columns else 0
                st.metric("Total Trades", int(total_trades))
            
            with col3:
                total_alerts = len(alerts_df)
                st.metric("Total Alerts", total_alerts)
            
            with col4:
                if total_trades > 0:
                    avg_win_rate = summary_df['win_rate'].mean() if 'win_rate' in summary_df.columns else 0
                    st.metric("Avg Win Rate", f"{avg_win_rate:.2f}%")
            
            # Alerts table
            if not alerts_df.empty:
                st.subheader("🔔 Alerts")
                st.dataframe(alerts_df, use_container_width=True, height=400)
                
                # Download button
                csv = alerts_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Alerts (CSV)",
                    data=csv,
                    file_name=f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Summary table
            if not summary_df.empty:
                st.subheader("📈 Summary Statistics")
                st.dataframe(summary_df, use_container_width=True, height=400)
                
                # Download button
                csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Summary (CSV)",
                    data=csv,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()

