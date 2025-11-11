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
    
    # Update params - widgets will read from this on next render
    st.session_state.params = DEFAULT_VALUES.copy()
    
    # Reset analysis scope controls (these can be set before widgets are created)
    st.session_state['use_specific_date'] = False
    st.session_state['selected_date'] = _date.today()
    st.session_state['only_recent_candle'] = True
    st.session_state['include_historical'] = False
    
    # Clear ALL widget keys so they reset on next render
    # This ensures widgets use their default values from params
    widget_keys_to_reset = [
        'interval_select',
        'lookback_swing_input',
        'vol_window_input',
        'vol_mult_input',
        'hold_bars_input',
        'historical_days_input',
        'max_workers_input',
        'use_specific_date_check',
        'analysis_date_picker',
        'recent_candle_select',
        'only_recent_candle_check',
        'include_historical_check'
    ]
    for key in widget_keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    
    # Also clear any cached widget state that might interfere
    # Clear running state
    st.session_state.running = False
    
    # Clear results
    st.session_state.results = None
    
    st.success("✅ Default values loaded! All parameters reset to system defaults.")

def main():
    """Main Streamlit app."""
    initialize_session_state()
    
    st.title("📈 Upstox Stock Selection System")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Time Interval
        # Get current interval from params (will be updated by Load Defaults)
        current_interval = st.session_state.params.get('interval', DEFAULT_VALUES['interval'])
        interval_index = INTERVALS.index(current_interval) if current_interval in INTERVALS else 5
        interval = st.selectbox(
            "Time Interval",
            options=INTERVALS,
            index=interval_index,
            key="interval_select",
            help="Candle interval for analysis (1m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 1d)"
        )
        # Update params with widget value (sync back)
        st.session_state.params['interval'] = interval

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
        # Get default value from session state (set by Load Defaults)
        use_specific_date_default = st.session_state.get('use_specific_date', False)
        use_specific_date = st.checkbox(
            "Use specific date (for historical analysis)",
            value=use_specific_date_default,
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
        # Get default values from session state (set by Load Defaults)
        only_recent_candle_default = st.session_state.get('only_recent_candle', True)
        only_recent_candle = st.checkbox(
            "Show only selected recent closed candle",
            value=only_recent_candle_default,
            key="only_recent_candle_check",
            help="When checked, results are filtered to the chosen recent candle only"
        )
        
        include_historical_default = st.session_state.get('include_historical', False)
        include_historical = st.checkbox(
            "Include historical results (entire period)",
            value=include_historical_default,
            key="include_historical_check",
            help="When checked, shows all alerts across the selected historical period"
        )
        
        # Save to session state
        st.session_state.only_recent_candle = only_recent_candle
        st.session_state.include_historical = include_historical
        
        if include_historical and only_recent_candle:
            st.info("Historical results enabled. Recent-candle filter will be ignored.")
        
        # Lookback Swing
        lookback_swing_default = int(st.session_state.params.get('lookback_swing', DEFAULT_VALUES['lookback_swing']))
        lookback_swing = st.number_input(
            "Lookback Swing (Bars)",
            min_value=1,
            max_value=100,
            value=lookback_swing_default,
            key="lookback_swing_input",
            help="Number of bars for swing high/low calculation"
        )
        st.session_state.params['lookback_swing'] = lookback_swing
        
        # Volume Window
        vol_window_default = int(st.session_state.params.get('vol_window', DEFAULT_VALUES['vol_window']))
        vol_window = st.number_input(
            "Volume Window (Bars)",
            min_value=1,
            max_value=500,
            value=vol_window_default,
            key="vol_window_input",
            help="Number of bars for average volume calculation (e.g., 70 = 10 days * 7 bars/day for 1h)"
        )
        st.session_state.params['vol_window'] = vol_window
        
        # Volume Multiplier
        vol_mult_default = float(st.session_state.params.get('vol_mult', DEFAULT_VALUES['vol_mult']))
        vol_mult = st.number_input(
            "Volume Multiplier",
            min_value=0.1,
            max_value=10.0,
            value=vol_mult_default,
            step=0.1,
            key="vol_mult_input",
            help="Volume spike threshold (e.g., 1.6 = 1.6x average volume)"
        )
        st.session_state.params['vol_mult'] = vol_mult
        
        # Hold Bars
        hold_bars_default = int(st.session_state.params.get('hold_bars', DEFAULT_VALUES['hold_bars']))
        hold_bars = st.number_input(
            "Hold Bars",
            min_value=1,
            max_value=100,
            value=hold_bars_default,
            key="hold_bars_input",
            help="Number of bars to hold position for P&L calculation"
        )
        st.session_state.params['hold_bars'] = hold_bars
        
        # Historical Days
        historical_days_default = int(st.session_state.params.get('historical_days', DEFAULT_VALUES['historical_days']))
        historical_days = st.number_input(
            "Historical Days",
            min_value=1,
            max_value=365,
            value=historical_days_default,
            key="historical_days_input",
            help="Number of days of historical data to fetch"
        )
        st.session_state.params['historical_days'] = historical_days
        
        # Max Workers
        max_workers_default = int(st.session_state.params.get('max_workers', DEFAULT_VALUES['max_workers']))
        max_workers = st.number_input(
            "Max Workers (Parallel)",
            min_value=1,
            max_value=50,
            value=max_workers_default,
            key="max_workers_input",
            help="Number of parallel workers for analysis"
        )
        st.session_state.params['max_workers'] = max_workers
        
        st.markdown("---")
        
        # Buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Load Defaults", use_container_width=True, key="load_defaults_btn"):
                load_default_values()
                st.rerun()
        
        with col2:
            if st.button("💾 Save Config", use_container_width=True):
                # Params are already synced from widgets above, just confirm
                st.success("✅ Configuration saved! All parameters are ready to use.")
    
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
    
    # Note: params are already updated in sidebar widgets above
    # This ensures params are always in sync with UI values
    
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
                    # Temporarily override settings BEFORE creating selector
                    # This ensures all methods use the correct settings
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
                    
                    # Create selector AFTER settings are overridden
                    selector = UpstoxStockSelector(api_key, access_token, DEFAULT_NSE_JSON_PATH)
                    
                    # Clear any cached data to ensure fresh analysis
                    selector.yf_historical_data = {}
                    
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
                        # Display configuration being used
                        st.info(f"📊 Analyzing {len(symbols)} symbols with configuration:")
                        config_text = f"""
- **Interval**: {settings.DEFAULT_INTERVAL}
- **Lookback Swing**: {settings.LOOKBACK_SWING} bars
- **Volume Window**: {settings.VOL_WINDOW} bars  
- **Volume Multiplier**: {settings.VOL_MULT}x
- **Hold Bars**: {settings.HOLD_BARS} bars
- **Historical Days**: {st.session_state.params['historical_days']} days
- **Max Workers**: {st.session_state.params['max_workers']} parallel workers
                        """
                        st.markdown(config_text)
                        
                        # Also print to console for debugging
                        print(f"\n{'='*80}")
                        print(f"ANALYSIS CONFIGURATION:")
                        print(f"  Interval: {settings.DEFAULT_INTERVAL}")
                        print(f"  Lookback Swing: {settings.LOOKBACK_SWING}")
                        print(f"  Volume Window: {settings.VOL_WINDOW}")
                        print(f"  Volume Multiplier: {settings.VOL_MULT}")
                        print(f"  Hold Bars: {settings.HOLD_BARS}")
                        print(f"  Historical Days: {st.session_state.params['historical_days']}")
                        print(f"  Max Workers: {st.session_state.params['max_workers']}")
                        print(f"{'='*80}\n")
                        
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
                            
                            # Verify settings were actually used (read them back)
                            actual_settings = {
                                'interval': settings.DEFAULT_INTERVAL,
                                'lookback_swing': settings.LOOKBACK_SWING,
                                'vol_window': settings.VOL_WINDOW,
                                'vol_mult': settings.VOL_MULT,
                                'hold_bars': settings.HOLD_BARS,
                            }
                            
                            # Store results with both requested and actual settings
                            st.session_state.results = {
                                'summary': summary_df,
                                'alerts': alerts_df,
                                'params': st.session_state.params.copy(),
                                'actual_settings': actual_settings
                            }
                            
                            # Verify settings match
                            settings_match = (
                                actual_settings['interval'] == st.session_state.params['interval'] and
                                actual_settings['lookback_swing'] == st.session_state.params['lookback_swing'] and
                                actual_settings['vol_window'] == st.session_state.params['vol_window'] and
                                actual_settings['vol_mult'] == st.session_state.params['vol_mult'] and
                                actual_settings['hold_bars'] == st.session_state.params['hold_bars']
                            )
                            
                            if settings_match:
                                st.success(f"✅ Analysis complete! Found {len(alerts_df)} alerts using the configured parameters.")
                            else:
                                st.warning(f"⚠️ Analysis complete with {len(alerts_df)} alerts, but settings verification failed!")
                                st.warning(f"Requested: {st.session_state.params}")
                                st.warning(f"Actual: {actual_settings}")
                            
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
        
        # Display configuration used for this analysis
        if 'actual_settings' in results:
            with st.expander("📋 Configuration Used for This Analysis", expanded=False):
                st.json(results['actual_settings'])
        
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

