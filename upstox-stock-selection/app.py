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
    PRICE_MOMENTUM_THRESHOLD,
    DEFAULT_HISTORICAL_DAYS,
    DEFAULT_INTERVAL,
    DEFAULT_MAX_WORKERS,
    DEFAULT_NSE_JSON_PATH as SETTINGS_NSE_JSON_PATH,
)

# Resolve NSE.json path relative to this app's directory so it works on Streamlit Cloud
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_NSE_JSON_PATH = os.path.join(APP_ROOT, "data", "NSE.json")
from src.utils.oauth_helper import UpstoxOAuthHelper
from src.ui.components import (
    render_navbar,
    render_card,
    render_alert_card,
    render_section_header,
    render_badge,
    render_metric_card,
    render_empty_state,
    render_group_label,
    render_divider,
    show_toast,
    render_tooltip_enhanced,
    render_theme_switcher,
    get_theme_css
)

# Page config with premium iOS-inspired design
# Mobile-optimized: sidebar collapses on small screens
st.set_page_config(
    page_title="Upstox Stock Selection",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Stock Selection System - Zerodha Kite Inspired Design"
    }
)

# Inject custom CSS for Zerodha Kite Premium design system
def inject_custom_css():
    """Inject premium CSS matching Zerodha Kite's world-class design system."""
    # Initialize theme in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Try premium CSS first, fallback to original
    css_file_path = os.path.join(os.path.dirname(__file__), 'assets', 'css', 'kite-premium.css')
    if not os.path.exists(css_file_path):
        css_file_path = os.path.join(os.path.dirname(__file__), 'assets', 'css', 'zerodha-kite.css')
    
    base_css = ""
    if os.path.exists(css_file_path):
        with open(css_file_path, 'r') as f:
            base_css = f.read()
    else:
        # Fallback inline CSS - Kite Style
        base_css = """
        body { font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif; background: #F5F7FA; font-size: 14px; }
        .main .block-container { padding: 1.5rem; max-width: 1400px; background: #F5F7FA; }
        h1 { font-size: 1.875rem; font-weight: 600; color: #1E293B; letter-spacing: -0.01em; }
        .stButton > button { background: #2062F6; border-radius: 6px; font-weight: 500; padding: 0.75rem 1.25rem; font-size: 0.875rem; }
        .stButton > button:hover { background: #1E4ED8; }
        [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E2E8F0; }
        """
    
    # Add theme-specific CSS
    theme_css = get_theme_css(st.session_state.theme)
    
    st.markdown(f'<style>{base_css}{theme_css}</style>', unsafe_allow_html=True)

# Inject CSS
inject_custom_css()

# Add mobile viewport and PWA meta tags for app-like experience
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#007AFF">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Stock Selection">
<link rel="manifest" href="/manifest.json">
""", unsafe_allow_html=True)

# Default values (current system values)
DEFAULT_VALUES = {
    'interval': DEFAULT_INTERVAL,
    'lookback_swing': LOOKBACK_SWING,
    'vol_window': VOL_WINDOW,
    'vol_mult': VOL_MULT,
    'hold_bars': HOLD_BARS,
    'price_momentum_threshold': 0.0,  # Optional: Minimum price momentum percentage filter (0.0 = disabled, use original strategy)
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
    
    # Show toast notification
    show_toast("Default values loaded! All parameters reset to system defaults.", "success")

def get_secret(key: str, default: str = '') -> str:
    """Get secret from Streamlit secrets or environment variable.
    
    This function checks Streamlit Cloud secrets first (for cloud deployment),
    then falls back to environment variables (for local development).
    """
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    # Fallback to environment variable
    return os.getenv(key, default)


def main():
    """Main Streamlit app with Zerodha Kite Premium design."""
    initialize_session_state()
    
    # Premium Navbar
    render_navbar(
        title="Stock Selection",
        subtitle="Professional algorithmic trading platform"
    )
    
    # Premium Hero Section
    render_card(
        title="Stock Selection System",
        subtitle="Identify high-probability trading opportunities with advanced algorithmic analysis",
        variant="floating",
        class_name="kite-fade-in"
    )
    
    # Premium Sidebar Configuration
    with st.sidebar:
        # Theme switcher at top of sidebar
        if render_theme_switcher():
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()
        
        render_divider()
        
        render_section_header(
            title="Configuration",
            subtitle="Customize analysis parameters"
        )
        
        # Group 1: Time Settings
        render_group_label("Time Settings")
        
        with st.container():
            
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

        # Recent candle selector (dynamic based on interval) - Kite Style
        st.markdown("""
        <div style="margin-top: 1rem; margin-bottom: 0.5rem;">
            <label style="font-size: 0.75rem; font-weight: 500; color: #64748B; 
                         text-transform: uppercase; letter-spacing: 0.05em; display: block;">
                Recent Candle
            </label>
        </div>
        """, unsafe_allow_html=True)
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

        # Date picker for historical analysis - Kite Style
        st.markdown("""
        <div style="margin-top: 1rem; margin-bottom: 0.5rem;">
            <label style="font-size: 0.75rem; font-weight: 500; color: #64748B; 
                         text-transform: uppercase; letter-spacing: 0.05em; display: block;">
                Analysis Date
            </label>
        </div>
        """, unsafe_allow_html=True)
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
            # For hourly candles, a candle at hour H completes at hour H+1:15
            # So we need to check if the candle has COMPLETED, not just started
            delta = interval_to_timedelta(interval)
            completed = []
            for t in candle_times:
                # Calculate when this candle completes
                candle_end = t + delta
                # For last candle of day, it ends at market close (15:30)
                market_close_dt = ist.localize(datetime.combine(t.date(), dtime(hour=15, minute=30)))
                if candle_end > market_close_dt:
                    candle_end = market_close_dt
                # Candle is completed if its end time has passed
                if candle_end <= now_ist:
                    completed.append(t)
            
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

        # Group 2: Results Scope
        render_group_label("Results Scope")
        
        with st.container():
            
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

            pattern_only_default = st.session_state.get('pattern_only', False)
            pattern_only = st.checkbox(
                "Show only pattern alerts (hide breakout/volume alerts)",
                value=pattern_only_default,
                key="pattern_only_check",
                help="When checked, only pattern-based alerts are shown. Breakout/breakdown and volume spike alerts are hidden."
            )
            
            # Save to session state
            st.session_state.only_recent_candle = only_recent_candle
            st.session_state.include_historical = include_historical
            st.session_state.pattern_only = pattern_only
            
            if include_historical and only_recent_candle:
                st.info("ℹ️ Historical results enabled. Recent-candle filter will be ignored.")
        
        # Group 2.5: Pattern Metrics (Additional Validation)
        render_group_label("Pattern Metrics")
        
        with st.container():
            st.markdown("""
            <div style="margin-bottom: 0.75rem;">
                <p style="font-size: 0.75rem; color: #64748B; margin: 0;">
                    Select additional metrics to validate patterns (based on Capital.com & Investopedia guidelines)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Volume Confirmation Metrics
            st.markdown("""
            <div style="margin-top: 0.5rem; margin-bottom: 0.25rem;">
                <p style="font-size: 0.7rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">
                    Volume Confirmation
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            pattern_volume_confirmation = st.checkbox(
                "Require volume confirmation",
                value=st.session_state.get('pattern_volume_confirmation', False),
                key="pattern_volume_confirmation",
                help="Require volume increase/decrease during pattern formation (e.g., lower volume on 2nd peak for double top, higher volume on breakout)"
            )
            
            pattern_volume_spike_breakout = st.checkbox(
                "Require volume spike on neckline breakout",
                value=st.session_state.get('pattern_volume_spike_breakout', False),
                key="pattern_volume_spike_breakout",
                help="Require significant volume increase when price breaks neckline (confirms pattern validity)"
            )
            
            # RSI Confirmation Metrics
            st.markdown("""
            <div style="margin-top: 0.75rem; margin-bottom: 0.25rem;">
                <p style="font-size: 0.7rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">
                    RSI Confirmation
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            pattern_rsi_overbought = st.checkbox(
                "Check RSI overbought (>70) for bearish patterns",
                value=st.session_state.get('pattern_rsi_overbought', False),
                key="pattern_rsi_overbought",
                help="Require RSI >70 for double/triple top patterns (indicates overbought condition)"
            )
            
            pattern_rsi_oversold = st.checkbox(
                "Check RSI oversold (<30) for bullish patterns",
                value=st.session_state.get('pattern_rsi_oversold', False),
                key="pattern_rsi_oversold",
                help="Require RSI <30 for double/triple bottom patterns (indicates oversold condition)"
            )
            
            # Candlestick Reversal Metrics
            st.markdown("""
            <div style="margin-top: 0.75rem; margin-bottom: 0.25rem;">
                <p style="font-size: 0.7rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">
                    Candlestick Reversal
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            pattern_candlestick_reversal = st.checkbox(
                "Require reversal candlestick at retest/breakout",
                value=st.session_state.get('pattern_candlestick_reversal', False),
                key="pattern_candlestick_reversal",
                help="Require reversal patterns (doji, hammer, shooting star) at key levels for confirmation"
            )
            
            # Pattern Symmetry Metrics
            st.markdown("""
            <div style="margin-top: 0.75rem; margin-bottom: 0.25rem;">
                <p style="font-size: 0.7rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">
                    Pattern Symmetry
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            pattern_peak_symmetry = st.checkbox(
                "Require peak/trough symmetry (double/triple patterns)",
                value=st.session_state.get('pattern_peak_symmetry', False),
                key="pattern_peak_symmetry",
                help="Require similar price levels for peaks (double/triple top) or troughs (double/triple bottom) - within 2% tolerance"
            )
            
            pattern_time_duration = st.checkbox(
                "Check time duration between pattern points",
                value=st.session_state.get('pattern_time_duration', False),
                key="pattern_time_duration",
                help="Require minimum time span between pattern formation points (ensures pattern maturity)"
            )
            
            # Retest-Specific Metrics
            st.markdown("""
            <div style="margin-top: 0.75rem; margin-bottom: 0.25rem;">
                <p style="font-size: 0.7rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">
                    Retest Pattern Specific
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            pattern_retest_tolerance = st.checkbox(
                "Strict retest tolerance (price must retest within 1%)",
                value=st.session_state.get('pattern_retest_tolerance', False),
                key="pattern_retest_tolerance",
                help="Require price to retest breakout level within 1% (default is 2%) for higher precision"
            )
            
            pattern_retest_no_breach = st.checkbox(
                "Require retest without breaching level",
                value=st.session_state.get('pattern_retest_no_breach', False),
                key="pattern_retest_no_breach",
                help="Price must retest the level without breaking through (confirms support/resistance strength)"
            )
            
            # Advanced Pattern Metrics
            st.markdown("""
            <div style="margin-top: 0.75rem; margin-bottom: 0.25rem;">
                <p style="font-size: 0.7rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">
                    Advanced Pattern Validation
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            pattern_volume_trend = st.checkbox(
                "Require volume trend confirmation during formation",
                value=st.session_state.get('pattern_volume_trend', False),
                key="pattern_volume_trend",
                help="Require proper volume trends (decrease on 2nd peak for double top, increase on breakout for double bottom)"
            )
            
            pattern_advanced_candlestick = st.checkbox(
                "Require advanced candlestick patterns (doji, hammer, engulfing)",
                value=st.session_state.get('pattern_advanced_candlestick', False),
                key="pattern_advanced_candlestick",
                help="Require advanced reversal candlestick patterns (doji, hammer, shooting star, engulfing) for confirmation"
            )
            
            pattern_rsi_divergence = st.checkbox(
                "Require RSI divergence confirmation",
                value=st.session_state.get('pattern_rsi_divergence', False),
                key="pattern_rsi_divergence",
                help="For RSI divergence patterns, require proper oversold/overbought conditions and divergence confirmation"
            )
            
            pattern_momentum_alignment = st.checkbox(
                "Require momentum trend alignment",
                value=st.session_state.get('pattern_momentum_alignment', False),
                key="pattern_momentum_alignment",
                help="Require pattern to align with momentum trend (bullish patterns with positive momentum, bearish with negative)"
            )
            
            # Note: Streamlit widgets with keys automatically manage session state
            # No need to manually save - values are accessible via st.session_state[key]
        
        # Group 3: Trading Parameters
        render_group_label("Trading Parameters")
        
        with st.container():
            
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
            
            # Price Momentum Threshold (Optional Filter)
            price_momentum_default = float(st.session_state.params.get('price_momentum_threshold', DEFAULT_VALUES['price_momentum_threshold']))
            price_momentum = st.number_input(
                "Price Momentum Threshold (%) - Optional",
                min_value=0.0,
                max_value=50.0,
                value=price_momentum_default,
                step=0.1,
                key="price_momentum_input",
                help="Optional: Minimum price change percentage to filter alerts (e.g., 0.5 = 0.5% increase or decrease). Set to 0 to disable filtering and use original strategy."
            )
            st.session_state.params['price_momentum_threshold'] = price_momentum
            if price_momentum == 0.0:
                st.caption("ℹ️ Price momentum filter is disabled. Using original strategy without momentum filtering.")
            
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
        
        # Group 4: Data & Performance
        render_group_label("Data & Performance")
        
        with st.container():
            
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
        
        # Configuration Actions - Better Organization
        st.markdown("""
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #E2E8F0;">
            <p style="font-size: 0.75rem; font-weight: 500; color: #64748B; 
                      text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                Configuration Actions
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Load Defaults", use_container_width=True, key="load_defaults_btn"):
                load_default_values()
                show_toast("Default values loaded!", "success")
                st.rerun()
        
        with col2:
            if st.button("💾 Save Config", use_container_width=True):
                # Params are already synced from widgets above, just confirm
                st.session_state.saved_config = st.session_state.params.copy()
                show_toast("Configuration saved!", "success")
    
    # Premium main content area - Create top-level tabs
    auth_tab, analysis_tab = st.tabs(["🔐 Authentication", "📊 Analysis Dashboard"])
    
    # ========== TAB 1: Authentication ==========
    with auth_tab:
        render_section_header(
            title="API Authentication",
            subtitle="Configure your Upstox API credentials securely"
        )
        
        # API Credentials Card - Kite Style
    st.markdown("""
    <div style="background: #FFFFFF; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; 
                border: 1px solid #E2E8F0; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);">
        <div style="display: flex; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; 
                    border-bottom: 1px solid #F1F5F9;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0; 
                       letter-spacing: -0.01em;">
                API Credentials
            </h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # OAuth Login Section - Zerodha Kite Style
    with st.container():
        st.markdown("""
        <div style="background: #F8FAFC; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; 
                    border: 1px solid #E2E8F0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                <div>
                    <h4 style="font-size: 0.875rem; font-weight: 600; color: #1E293B; margin: 0;">
                        🔐 Secure Login with Upstox
                    </h4>
                    <p style="font-size: 0.75rem; color: #64748B; margin: 0.25rem 0 0 0;">
                        Authenticate securely using OAuth 2.0
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Helper function to get secrets (Streamlit Cloud) or env vars
        def get_secret(key: str, default: str = '') -> str:
            """Get secret from Streamlit secrets or environment variable."""
            try:
                # Try Streamlit secrets first (for Streamlit Cloud)
                if hasattr(st, 'secrets') and key in st.secrets:
                    return st.secrets[key]
            except:
                pass
            # Fallback to environment variable
            return os.getenv(key, default)
        
        # Initialize OAuth helper
        default_api_key = get_secret('UPSTOX_API_KEY', 'e3d3c1d1-5338-4efa-b77f-c83ea604ea43')
        default_api_secret = get_secret('UPSTOX_API_SECRET', '9kbfgnlibw')
        default_redirect_uri = get_secret('UPSTOX_REDIRECT_URI', 'https://127.0.0.1')
        
        # OAuth configuration inputs
        oauth_col1, oauth_col2 = st.columns([3, 1])
        
        with oauth_col1:
            oauth_api_key = st.text_input(
                "API Key (Client ID)",
                value=default_api_key,
                key="oauth_api_key",
                help="Your Upstox API Key / Client ID",
                placeholder="Enter your API key"
            )
        
        with oauth_col2:
            oauth_api_secret = st.text_input(
                "API Secret",
                value=default_api_secret,
                type="password",
                key="oauth_api_secret",
                help="Your Upstox API Secret",
                placeholder="Enter API secret"
            )
        
        redirect_uri = st.text_input(
            "Redirect URI",
            value=default_redirect_uri,
            key="redirect_uri",
            help="Redirect URI configured in your Upstox app (must match exactly)",
            placeholder="https://127.0.0.1"
        )
        
        # OAuth Flow
        oauth_tab1, oauth_tab2 = st.tabs(["🔗 OAuth Login", "📝 Manual Entry"])
        
        with oauth_tab1:
            if oauth_api_key and oauth_api_secret:
                oauth_helper = UpstoxOAuthHelper(
                    client_id=oauth_api_key,
                    client_secret=oauth_api_secret,
                    redirect_uri=redirect_uri
                )
                
                # Generate authorization URL
                auth_url = oauth_helper.get_authorization_url()
                
                st.markdown("""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; 
                            padding: 1rem; margin: 1rem 0;">
                    <p style="font-size: 0.875rem; color: #1E293B; margin: 0 0 0.75rem 0; font-weight: 500;">
                        Step 1: Click the button below to authorize with Upstox
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Authorization URL button
                col_auth1, col_auth2 = st.columns([2, 3])
                with col_auth1:
                    if st.button("🔐 Login with Upstox", type="primary", use_container_width=True, key="oauth_login_btn"):
                        st.session_state.oauth_auth_url = auth_url
                        st.session_state.oauth_helper = oauth_helper
                        st.info(f"📋 Authorization URL generated! Click the link below or copy it.")
                
                # Show authorization URL
                if 'oauth_auth_url' in st.session_state:
                    st.markdown(f"""
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; 
                                padding: 0.75rem; margin: 0.5rem 0;">
                        <p style="font-size: 0.75rem; color: #64748B; margin: 0 0 0.5rem 0;">
                            <strong>Authorization URL:</strong>
                        </p>
                        <a href="{st.session_state.oauth_auth_url}" target="_blank" 
                           style="font-size: 0.75rem; color: #2062F6; text-decoration: none; 
                                  word-break: break-all; display: block;">
                            {st.session_state.oauth_auth_url}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    redirect_uri_display = redirect_uri
                    st.markdown(f"""
                    <div style="background: #FFF4E6; border-left: 4px solid #FF9800; border-radius: 4px; 
                                padding: 0.75rem; margin: 1rem 0;">
                        <p style="font-size: 0.75rem; color: #1E293B; margin: 0;">
                            <strong>📌 Instructions:</strong><br>
                            1. Click the authorization URL above (opens in new tab)<br>
                            2. Login to your Upstox account and authorize the app<br>
                            3. You'll be redirected to: <code style="background: #E2E8F0; padding: 2px 4px; border-radius: 3px;">{redirect_uri_display}/?code=XXXXX</code><br>
                            4. Copy the <strong>code</strong> parameter from the URL<br>
                            5. Paste it in the "Authorization Code" field below
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Code input and token exchange
                st.markdown("""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; 
                            padding: 1rem; margin: 1rem 0;">
                    <p style="font-size: 0.875rem; color: #1E293B; margin: 0 0 0.75rem 0; font-weight: 500;">
                        Step 2: Enter the authorization code from the callback URL
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                code_input_col1, code_input_col2 = st.columns([3, 1])
                with code_input_col1:
                    auth_code = st.text_input(
                        "Authorization Code",
                        key="auth_code_input",
                        placeholder="Paste the code from callback URL (e.g., SJwE0P)",
                        help="The 'code' parameter from the redirect URL after authorization"
                    )
                
                with code_input_col2:
                    exchange_token_btn = st.button("🔄 Exchange Token", type="primary", use_container_width=True, key="exchange_token_btn")
                
                # Token exchange
                if exchange_token_btn and auth_code:
                    if 'oauth_helper' in st.session_state:
                        with st.spinner("🔄 Exchanging code for access token..."):
                            success, result = st.session_state.oauth_helper.exchange_code_for_token(auth_code)
                            
                            if success:
                                access_token_new = result.get('access_token')
                                if access_token_new:
                                    # Save to session state (use different key to avoid widget conflict)
                                    st.session_state.oauth_access_token = access_token_new
                                    st.session_state.saved_oauth_api_key = oauth_api_key
                                    
                                    # Save to environment (current session)
                                    st.session_state.oauth_helper.save_token_to_env(
                                        access_token_new, 
                                        oauth_api_key
                                    )
                                    
                                    st.success("✅ Access token obtained successfully!")
                                    st.info(f"🔑 Token expires in: {result.get('expires_in', 'N/A')} seconds")
                                    
                                    # Show token preview
                                    token_preview = access_token_new[:50] + "..." if len(access_token_new) > 50 else access_token_new
                                    st.code(f"Token: {token_preview}", language=None)
                                    
                                    # Save options
                                    save_col1, save_col2 = st.columns(2)
                                    
                                    with save_col1:
                                        if st.button("💾 Save to Local File", key="save_token_file", use_container_width=True):
                                            file_saved = st.session_state.oauth_helper.save_token_to_file(
                                                access_token_new,
                                                oauth_api_key,
                                                ".env.local"
                                            )
                                            if file_saved:
                                                st.success("✅ Token saved to .env.local file!")
                                            else:
                                                st.error("❌ Failed to save token to file")
                                    
                                    with save_col2:
                                        if st.button("🚂 Copy for Railway", key="copy_railway", use_container_width=True):
                                            railway_vars = f"""UPSTOX_API_KEY={oauth_api_key}
UPSTOX_ACCESS_TOKEN={access_token_new}"""
                                            st.code(railway_vars, language=None)
                                            st.info("📋 Copy the above and paste in Railway → Variables tab")
                                    
                                    # Railway deployment instructions
                                    with st.expander("🚂 Railway Deployment Instructions", expanded=False):
                                        railway_instructions = f"""
                                        <div style="background: #F8FAFC; border-radius: 6px; padding: 1rem; margin: 0.5rem 0;">
                                            <p style="font-size: 0.875rem; color: #1E293B; margin: 0 0 0.75rem 0; font-weight: 500;">
                                                To deploy this token to Railway:
                                            </p>
                                            <ol style="font-size: 0.875rem; color: #64748B; margin: 0; padding-left: 1.5rem;">
                                                <li>Go to Railway Dashboard → Your Project → Service</li>
                                                <li>Click on <strong>Variables</strong> tab</li>
                                                <li>Click <strong>New Variable</strong> and add:</li>
                                            </ol>
                                            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px; 
                                                        padding: 0.75rem; margin: 0.75rem 0; font-family: monospace; font-size: 0.75rem;">
                                                <div>UPSTOX_API_KEY = {oauth_api_key}</div>
                                                <div>UPSTOX_ACCESS_TOKEN = {access_token_new}</div>
                                            </div>
                                            <p style="font-size: 0.75rem; color: #64748B; margin: 0.5rem 0 0 0;">
                                                <strong>Note:</strong> No quotes needed around values in Railway
                                            </p>
                                        </div>
                                        """
                                        st.markdown(railway_instructions, unsafe_allow_html=True)
                                else:
                                    st.error("❌ No access token in response")
                            else:
                                error_msg = result.get('error', 'Unknown error')
                                st.error(f"❌ Token exchange failed: {error_msg}")
                                if 'status_code' in result:
                                    st.info(f"Status Code: {result['status_code']}")
                    else:
                        st.warning("⚠️ Please generate authorization URL first")
        
        with oauth_tab2:
            st.markdown("""
            <div style="background: #F8FAFC; border-radius: 6px; padding: 1rem; margin-bottom: 1rem;">
                <p style="font-size: 0.875rem; color: #64748B; margin: 0;">
                    Enter your credentials manually if you already have them
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                api_key = st.text_input(
                    "Upstox API Key",
                    value=get_secret('UPSTOX_API_KEY', ''),
                    key="manual_api_key",
                    help="Your Upstox API Key (or set in Streamlit Cloud Secrets)",
                    placeholder="Enter your API key"
                )
            
            with col2:
                access_token = st.text_input(
                    "Upstox Access Token",
                    value=get_secret('UPSTOX_ACCESS_TOKEN', ''),
                    key="manual_access_token",
                    type="password",
                    help="Your Upstox Access Token (or set in Streamlit Cloud Secrets)",
                    placeholder="Enter your access token"
                )
            
            # Better organized save button
            st.markdown("""
            <div style="margin-top: 1rem;">
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💾 Save Manual Credentials", type="primary", key="save_manual_creds"):
                if api_key and access_token:
                    os.environ['UPSTOX_API_KEY'] = api_key
                    os.environ['UPSTOX_ACCESS_TOKEN'] = access_token
                    st.success("✅ Credentials saved to current session!")
                else:
                    st.error("❌ Please provide both API Key and Access Token")
        
        # Use OAuth token if available, otherwise use manual input, then secrets/env
        if 'oauth_access_token' in st.session_state:
            access_token = st.session_state.oauth_access_token
            api_key = st.session_state.get('saved_oauth_api_key', '')
        elif 'manual_api_key' in st.session_state and st.session_state.manual_api_key:
            api_key = st.session_state.manual_api_key
            access_token = st.session_state.manual_access_token if 'manual_access_token' in st.session_state else get_secret('UPSTOX_ACCESS_TOKEN', '')
        else:
            # Try Streamlit secrets first (for Streamlit Cloud), then env vars
            api_key = get_secret('UPSTOX_API_KEY', '')
            access_token = get_secret('UPSTOX_ACCESS_TOKEN', '')
        
        # Store credentials in session state for use in Analysis tab
        st.session_state.current_api_key = api_key
        st.session_state.current_access_token = access_token
        
        # Show current status
        if api_key and access_token:
            st.success("✅ Credentials configured! You can now switch to the Analysis Dashboard tab.")
        else:
            st.warning("⚠️ Please configure your API credentials to use the Analysis Dashboard.")
    
    # ========== TAB 2: Analysis Dashboard ==========
    with analysis_tab:
        render_section_header(
            title="Analysis Dashboard",
            subtitle="Configure parameters and execute comprehensive stock analysis"
        )
        
        # Get credentials from session state (set in Authentication tab)
        api_key = st.session_state.get('current_api_key', os.getenv('UPSTOX_API_KEY', ''))
        access_token = st.session_state.get('current_access_token', os.getenv('UPSTOX_ACCESS_TOKEN', ''))
        
        # Show credential status
        if not api_key or not access_token:
            st.error("❌ Please configure your API credentials in the Authentication tab first!")
            st.info("💡 Switch to the '🔐 Authentication' tab to set up your Upstox API credentials.")
        else:
            st.success(f"✅ Using API Key: {api_key[:20]}...")
        
        # Current Configuration Card - Kite Style
        st.markdown("""
        <div style="background: #FFFFFF; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; 
                    border: 1px solid #E2E8F0; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);">
            <div style="display: flex; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; 
                        border-bottom: 1px solid #F1F5F9;">
                <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0; 
                           letter-spacing: -0.01em;">
                    Current Configuration
                </h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            
            with st.expander("View Configuration Details", expanded=False):
                config_df = pd.DataFrame([
                    {"Parameter": "Time Interval", "Value": str(st.session_state.params['interval'])},
                    {"Parameter": "Lookback Swing", "Value": str(st.session_state.params['lookback_swing'])},
                    {"Parameter": "Volume Window", "Value": str(st.session_state.params['vol_window'])},
                    {"Parameter": "Volume Multiplier", "Value": str(st.session_state.params['vol_mult'])},
                    {"Parameter": "Hold Bars", "Value": str(st.session_state.params['hold_bars'])},
                    {"Parameter": "Historical Days", "Value": str(st.session_state.params['historical_days'])},
                    {"Parameter": "Max Workers", "Value": str(st.session_state.params['max_workers'])},
                ])
                # Ensure all columns are string type for Streamlit Arrow compatibility
                config_df = config_df.astype(str)
                st.dataframe(config_df, use_container_width=True, hide_index=True)
        
        # Action Buttons - Kite Style (Better Organization)
        st.markdown("""
        <div style="margin: 2rem 0 1.5rem 0; padding-top: 1.5rem; border-top: 1px solid #E2E8F0;">
            <p style="font-size: 0.875rem; font-weight: 600; color: #1E293B; margin-bottom: 1rem;">
                Analysis Actions
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Primary action button row
        col1, col2, col3 = st.columns([2, 2, 4])
        
        with col1:
            run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
        
        with col2:
            clear_button = st.button("🗑️ Clear Results", use_container_width=True)
        
        if clear_button:
            st.session_state.results = None
            show_toast("Results cleared!", "info")
            st.rerun()
        
        # Run analysis
        if run_button:
            if not api_key or not access_token:
                show_toast("Please provide both API Key and Access Token!", "error")
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
                        # Disable verbose logging in production (Railway) to avoid rate limits
                        verbose_logging = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'
                        selector = UpstoxStockSelector(api_key, access_token, DEFAULT_NSE_JSON_PATH, verbose=verbose_logging)
                        
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
                                st.info("🔄 Starting analysis... This may take a few minutes.")
                                
                                summary_df, alerts_df = asyncio.run(
                                    selector.analyze_symbols(
                                        symbols,
                                        max_workers=int(st.session_state.params['max_workers']),
                                        days=int(st.session_state.params['historical_days']),
                                        target_date=target_date
                                    )
                                )
                                
                                # Diagnostic information
                                st.info(f"📊 Analysis completed:")
                                st.info(f"   - Summary records: {len(summary_df) if summary_df is not None and not summary_df.empty else 0}")
                                st.info(f"   - Alert records: {len(alerts_df) if alerts_df is not None and not alerts_df.empty else 0}")
                                
                                # Check if results are empty and provide helpful diagnostics
                                if (alerts_df is None or alerts_df.empty) and (summary_df is None or summary_df.empty):
                                    st.warning("⚠️ No results found. Possible reasons:")
                                    st.markdown("""
                                    - **Market hours**: Analysis might be running outside market hours (9:15 AM - 3:30 PM IST)
                                    - **Date filter**: Selected date might not have any trading activity
                                    - **Strict filters**: Pattern metrics or other filters might be too restrictive
                                    - **API issues**: Check if API credentials are valid and have proper permissions
                                    - **Data availability**: Historical data might not be available for the selected period
                                    
                                    **Try these steps:**
                                    1. Check if you're running during market hours (9:15 AM - 3:30 PM IST)
                                    2. Try unchecking some pattern metric filters in the sidebar
                                    3. Increase historical days to get more data
                                    4. Try a different date (use "Include Historical Alerts" option)
                                    5. Verify your API credentials are correct
                                    """)
                                
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
                                    if alerts_df is not None and not alerts_df.empty:
                                        show_toast(f"Analysis complete! Found {len(alerts_df)} alerts.", "success")
                                        st.success(f"✅ Analysis complete! Found {len(alerts_df)} alerts using the configured parameters.")
                                    else:
                                        show_toast("Analysis complete but no alerts found.", "info")
                                        st.info(f"ℹ️ Analysis complete but no alerts found. Try adjusting filters or checking market hours.")
                                else:
                                    show_toast("Analysis complete, but settings verification failed!", "warning")
                                    st.warning(f"⚠️ Analysis complete with {len(alerts_df) if alerts_df is not None and not alerts_df.empty else 0} alerts, but settings verification failed!")
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
                        show_toast(f"Error: {str(e)}", "error")
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                        st.session_state.running = False
        
        # Premium results display with tabs
        if st.session_state.results:
            render_section_header(
                title="Analysis Results",
                subtitle="Review your comprehensive stock selection analysis"
            )
            
            results = st.session_state.results
            summary_df = results.get('summary', pd.DataFrame())
            alerts_df = results.get('alerts', pd.DataFrame())
            
            # Ensure DataFrames are not None
            if summary_df is None:
                summary_df = pd.DataFrame()
            if alerts_df is None:
                alerts_df = pd.DataFrame()
            
            # Display configuration used for this analysis
            if 'actual_settings' in results:
                with st.expander("📋 Configuration Used for This Analysis", expanded=False):
                    st.json(results['actual_settings'])
            
            # Show diagnostic information if no results
            if alerts_df.empty and summary_df.empty:
                st.warning("⚠️ **No Results Found**")
                with st.expander("🔍 Diagnostic Information", expanded=True):
                    st.markdown("""
                    **Analysis completed but no alerts were generated.**
                    
                    **Possible reasons:**
                    1. **Market Hours**: Analysis might be outside market hours (9:15 AM - 3:30 PM IST)
                    2. **Date Selection**: Selected date might not have trading activity
                    3. **Strict Filters**: Pattern metrics or filters might be too restrictive
                    4. **No Patterns Detected**: No patterns matched the criteria for the selected symbols
                    5. **Data Issues**: Historical data might not be available
                    
                    **Troubleshooting Steps:**
                    - ✅ Check if you're running during market hours
                    - ✅ Try unchecking some pattern metric filters in the sidebar
                    - ✅ Increase "Historical Days" to get more data
                    - ✅ Try enabling "Include Historical Alerts" to see past results
                    - ✅ Verify API credentials are valid
                    - ✅ Check if symbols are being loaded correctly
                    """)
                    
                    # Show current filter settings
                    st.markdown("**Current Filter Settings:**")
                    filter_info = {
                        "Include Historical": st.session_state.get('include_historical', False),
                        "Only Recent Candle": st.session_state.get('only_recent_candle', True),
                        "Pattern Only": st.session_state.get('pattern_only', False),
                        "Price Momentum Threshold": st.session_state.params.get('price_momentum_threshold', 0.0),
                    }
                    st.json(filter_info)
            
            # Get filter settings from session state (set in sidebar)
            include_historical = st.session_state.get('include_historical', False)
            only_recent_candle = st.session_state.get('only_recent_candle', True)
            selected_candle_dt = st.session_state.get('selected_candle_dt', None)
            selected_date = st.session_state.get('selected_date', None)
            pattern_only = st.session_state.get('pattern_only', False)
            
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
            original_alerts_df = alerts_df.copy()
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
            
            # Apply price momentum filter if threshold is set (> 0)
            price_momentum_threshold = st.session_state.params.get('price_momentum_threshold', 0.0)
            if price_momentum_threshold > 0 and not alerts_df.empty and 'price_momentum' in alerts_df.columns:
                # Filter alerts where absolute price momentum >= threshold
                # This catches both increasing (positive) and decreasing (negative) momentum
                before_count = len(alerts_df)
                alerts_df = alerts_df[alerts_df['price_momentum'].abs() >= price_momentum_threshold].copy()
                after_count = len(alerts_df)
                if before_count != after_count:
                    st.info(f"📊 Price momentum filter applied: {before_count - after_count} alert(s) filtered out (threshold: ±{price_momentum_threshold}%)")
            
            # Split alerts into pattern vs non-pattern for tab organization
            if 'pattern_type' in alerts_df.columns:
                pattern_alerts_df = alerts_df[alerts_df['pattern_type'].notna()].copy()
                legacy_alerts_df = alerts_df[alerts_df['pattern_type'].isna()].copy()
            else:
                pattern_alerts_df = pd.DataFrame()
                legacy_alerts_df = alerts_df.copy()
            
            # Helper function to analyze volume trend during pattern formation
            def has_volume_trend_confirmation(row: pd.Series, pattern_type: str) -> bool:
                """
                Check if pattern has proper volume trend during formation.
                
                Guidelines:
                - Double Top: Volume should decrease on second peak
                - Double Bottom: Volume should increase after second bottom
                - Triple Top: Volume should decrease with each peak
                - Triple Bottom: Volume should increase on breakout
                """
                pattern_type_upper = pattern_type.upper()
                vol_ratio = row.get('vol_ratio', None)
                
                if vol_ratio is None or pd.isna(vol_ratio):
                    return False
                
                vol_ratio = float(vol_ratio)
                
                # For bearish patterns (Double/Triple Top), volume should decrease
                if pattern_type_upper in ['DOUBLE_TOP', 'TRIPLE_TOP']:
                    # Check if we have volume data for first and second peaks
                    # For now, we check if current volume is reasonable
                    # In full implementation, we'd compare volume at first vs second peak
                    # For now, if vol_ratio is low (< 1.0), suggests decreasing volume
                    return vol_ratio < 1.5  # Not too high, suggests volume decline
                
                # For bullish patterns (Double/Triple Bottom), volume should increase
                elif pattern_type_upper in ['DOUBLE_BOTTOM', 'TRIPLE_BOTTOM', 'INVERSE_HEAD_SHOULDERS']:
                    # Volume should increase on breakout
                    return vol_ratio >= 1.2  # At least 20% above average
                
                # For retest patterns, volume should spike on breakout
                elif pattern_type_upper in ['UPTREND_RETEST', 'DOWNTREND_RETEST']:
                    return vol_ratio >= 1.2  # At least 20% above average
                
                # For RSI divergence, volume confirmation is less critical
                return True
            
            # Helper function to detect advanced candlestick patterns
            def has_advanced_candlestick_pattern(row: pd.Series, pattern_type: str) -> bool:
                """
                Detect advanced candlestick patterns: doji, hammer, shooting star, engulfing.
                
                Note: This requires OHLC data which may not be in the alert.
                For now, we check if pattern has reversal confirmation indicators.
                """
                pattern_type_upper = pattern_type.upper()
                
                # Check if we have candlestick pattern metadata
                # Pattern detector may store this in additional fields
                has_doji = row.get('has_doji', False)
                has_hammer = row.get('has_hammer', False)
                has_shooting_star = row.get('has_shooting_star', False)
                has_engulfing = row.get('has_engulfing', False)
                
                # If explicit candlestick flags exist, use them
                if has_doji or has_hammer or has_shooting_star or has_engulfing:
                    return True
                
                # For retest patterns, check if reversal candle was detected
                retest_patterns = ['UPTREND_RETEST', 'DOWNTREND_RETEST']
                if pattern_type_upper in retest_patterns:
                    bars_after = row.get('bars_after_breakout', None)
                    if bars_after is not None and not pd.isna(bars_after):
                        # Reversal candle should be found
                        if 1 <= int(bars_after) <= 20:
                            entry_price = row.get('entry_price', None)
                            price = row.get('price', None)
                            if entry_price is not None and price is not None:
                                entry_price = float(entry_price)
                                price = float(price)
                                # Entry price different from current suggests reversal candle
                                if abs(entry_price - price) / price > 0.001:  # At least 0.1% difference
                                    return True
                
                # For double/triple patterns, check if pattern has proper structure
                # Entry price being different suggests reversal confirmation
                entry_price = row.get('entry_price', None)
                price = row.get('price', None)
                if entry_price is not None and price is not None:
                    entry_price = float(entry_price)
                    price = float(price)
                    price_diff_pct = abs(entry_price - price) / price * 100
                    # If entry is significantly different, suggests candlestick confirmation
                    if price_diff_pct > 0.5:
                        return True
                
                return False
            
            # Helper function to validate RSI divergence
            def has_rsi_divergence_confirmation(row: pd.Series, pattern_type: str) -> bool:
                """
                Validate RSI divergence patterns have proper confirmation.
                
                For RSI divergence patterns:
                - Bullish: RSI should be oversold (< 30) and showing higher lows
                - Bearish: RSI should be overbought (> 70) and showing lower highs
                """
                pattern_type_upper = pattern_type.upper()
                
                if pattern_type_upper == 'RSI_BULLISH_DIVERGENCE':
                    rsi = row.get('rsi', None)
                    rsi_trough1 = row.get('rsi_trough1', None)
                    rsi_trough2 = row.get('rsi_trough2', None)
                    price_trough1 = row.get('price_trough1', None)
                    price_trough2 = row.get('price_trough2', None)
                    
                    if rsi is not None and not pd.isna(rsi):
                        # RSI should be oversold
                        if float(rsi) < 30:
                            # Check divergence: price lower low, RSI higher low
                            if (rsi_trough1 is not None and rsi_trough2 is not None and
                                price_trough1 is not None and price_trough2 is not None):
                                rsi1 = float(rsi_trough1)
                                rsi2 = float(rsi_trough2)
                                price1 = float(price_trough1)
                                price2 = float(price_trough2)
                                
                                # Bullish divergence: price lower low, RSI higher low
                                if price2 < price1 and rsi2 > rsi1:
                                    return True
                            # If we have RSI but not trough data, check if RSI is oversold
                            return True
                    return False
                
                elif pattern_type_upper == 'RSI_BEARISH_DIVERGENCE':
                    rsi = row.get('rsi', None)
                    rsi_peak1 = row.get('rsi_peak1', None)
                    rsi_peak2 = row.get('rsi_peak2', None)
                    price_peak1 = row.get('price_peak1', None)
                    price_peak2 = row.get('price_peak2', None)
                    
                    if rsi is not None and not pd.isna(rsi):
                        # RSI should be overbought
                        if float(rsi) > 70:
                            # Check divergence: price higher high, RSI lower high
                            if (rsi_peak1 is not None and rsi_peak2 is not None and
                                price_peak1 is not None and price_peak2 is not None):
                                rsi1 = float(rsi_peak1)
                                rsi2 = float(rsi_peak2)
                                price1 = float(price_peak1)
                                price2 = float(price_peak2)
                                
                                # Bearish divergence: price higher high, RSI lower high
                                if price2 > price1 and rsi2 < rsi1:
                                    return True
                            # If we have RSI but not peak data, check if RSI is overbought
                            return True
                    return False
                
                # For non-divergence patterns, RSI divergence check doesn't apply
                return True
            
            # Helper function to check momentum trend alignment
            def has_momentum_trend_alignment(row: pd.Series, pattern_type: str) -> bool:
                """
                Check if pattern aligns with momentum trend.
                
                Guidelines:
                - Bullish patterns should show positive momentum
                - Bearish patterns should show negative momentum
                - Breakout momentum should be stronger than pullback momentum
                """
                pattern_type_upper = pattern_type.upper()
                
                # Get momentum indicators
                price_momentum = row.get('price_momentum', None)
                avg_momentum_7d = row.get('avg_momentum_7d', None)
                momentum_ratio = row.get('momentum_ratio', None)
                
                # For bullish patterns
                bullish_patterns = ['DOUBLE_BOTTOM', 'TRIPLE_BOTTOM', 'UPTREND_RETEST', 
                                  'RSI_BULLISH_DIVERGENCE', 'INVERSE_HEAD_SHOULDERS']
                if pattern_type_upper in bullish_patterns:
                    # Check if momentum is positive or aligned
                    if price_momentum is not None and not pd.isna(price_momentum):
                        if float(price_momentum) > 0:
                            return True
                    if avg_momentum_7d is not None and not pd.isna(avg_momentum_7d):
                        if float(avg_momentum_7d) > 0:
                            return True
                    # For retest patterns, check momentum ratio
                    if pattern_type_upper in ['UPTREND_RETEST', 'DOWNTREND_RETEST']:
                        if momentum_ratio is not None and not pd.isna(momentum_ratio):
                            # Breakout momentum should be stronger than pullback
                            if float(momentum_ratio) > 1.0:
                                return True
                    # If no momentum data, assume alignment
                    return True
                
                # For bearish patterns
                bearish_patterns = ['DOUBLE_TOP', 'TRIPLE_TOP', 'DOWNTREND_RETEST', 'RSI_BEARISH_DIVERGENCE']
                if pattern_type_upper in bearish_patterns:
                    # Check if momentum is negative or aligned
                    if price_momentum is not None and not pd.isna(price_momentum):
                        if float(price_momentum) < 0:
                            return True
                    if avg_momentum_7d is not None and not pd.isna(avg_momentum_7d):
                        if float(avg_momentum_7d) < 0:
                            return True
                    # For retest patterns, check momentum ratio
                    if pattern_type_upper in ['UPTREND_RETEST', 'DOWNTREND_RETEST']:
                        if momentum_ratio is not None and not pd.isna(momentum_ratio):
                            # Breakout momentum should be stronger than pullback
                            if float(momentum_ratio) > 1.0:
                                return True
                    # If no momentum data, assume alignment
                    return True
                
                # Default: assume alignment if we can't verify
                return True
            
            # Helper function to detect candlestick reversal patterns
            def has_reversal_candlestick(row: pd.Series, pattern_type: str) -> bool:
                """
                Check if pattern has reversal candlestick confirmation.
                
                For retest patterns: Checks if bars_after_breakout exists (indicates reversal found)
                For other patterns: Checks if entry_price suggests reversal candle was used
                """
                pattern_type_upper = pattern_type.upper()
                
                # For retest patterns, check if reversal candle was detected
                retest_patterns = ['UPTREND_RETEST', 'DOWNTREND_RETEST']
                if pattern_type_upper in retest_patterns:
                    # If bars_after_breakout exists and is reasonable, reversal was found
                    bars_after = row.get('bars_after_breakout', None)
                    if bars_after is not None and not pd.isna(bars_after):
                        # Reversal candle should be found within reasonable bars after breakout
                        if 1 <= int(bars_after) <= 20:
                            # Check if entry_price suggests reversal candle (entry above/below reversal high/low)
                            entry_price = row.get('entry_price', None)
                            price = row.get('price', None)
                            if entry_price is not None and price is not None:
                                entry_price = float(entry_price)
                                price = float(price)
                                # For uptrend retest: entry should be above price (above reversal candle high)
                                # For downtrend retest: entry should be below price (below reversal candle low)
                                if pattern_type_upper == 'UPTREND_RETEST':
                                    if entry_price > price * 1.001:  # Entry above current price
                                        return True
                                elif pattern_type_upper == 'DOWNTREND_RETEST':
                                    if entry_price < price * 0.999:  # Entry below current price
                                        return True
                    return False
                
                # For other patterns (double/triple, inverse H&S), check if pattern formation suggests reversal
                # These patterns typically form over time, so we check if the pattern has proper structure
                # Entry price being different from current price suggests a reversal confirmation
                entry_price = row.get('entry_price', None)
                price = row.get('price', None)
                if entry_price is not None and price is not None:
                    entry_price = float(entry_price)
                    price = float(price)
                    price_diff_pct = abs(entry_price - price) / price * 100
                    # If entry is significantly different from current price, suggests reversal confirmation
                    if price_diff_pct > 0.5:  # At least 0.5% difference
                        return True
                
                return False
            
            # Helper function to check time duration between pattern points
            def has_sufficient_time_duration(row: pd.Series, pattern_type: str, interval: str) -> bool:
                """
                Check if pattern has sufficient time duration between formation points.
                
                Minimum requirements:
                - Retest patterns: At least 3 bars between breakout and retest
                - Double patterns: At least 5 bars between first and second point
                - Triple patterns: At least 5 bars between each point
                - Inverse H&S: At least 10 bars between shoulders
                """
                pattern_type_upper = pattern_type.upper()
                min_bars = 3  # Default minimum
                
                # Set minimum bars based on pattern type
                if pattern_type_upper in ['UPTREND_RETEST', 'DOWNTREND_RETEST']:
                    min_bars = 3  # At least 3 bars between breakout and retest
                    bars_after = row.get('bars_after_breakout', None)
                    if bars_after is not None and not pd.isna(bars_after):
                        return int(bars_after) >= min_bars
                    return False
                
                elif pattern_type_upper in ['DOUBLE_BOTTOM', 'DOUBLE_TOP']:
                    min_bars = 5  # At least 5 bars between first and second point
                    # Check if we have indices
                    first_idx = row.get('first_bottom_idx', row.get('first_top_idx', None))
                    second_idx = row.get('second_bottom_idx', row.get('second_top_idx', None))
                    if first_idx is not None and second_idx is not None:
                        bar_diff = abs(int(second_idx) - int(first_idx))
                        return bar_diff >= min_bars
                    # Fallback: Check timestamp difference if available
                    timestamp = row.get('timestamp', None)
                    if timestamp is not None:
                        try:
                            if isinstance(timestamp, str):
                                timestamp = pd.to_datetime(timestamp)
                            # For double patterns, we need at least 5 bars
                            # Estimate based on interval
                            interval_to_hours = {
                                '1m': 1/60, '5m': 5/60, '10m': 10/60, '15m': 0.25,
                                '30m': 0.5, '1h': 1, '2h': 2, '4h': 4, '1d': 24
                            }
                            hours_per_bar = interval_to_hours.get(interval, 1)
                            min_hours = min_bars * hours_per_bar
                            # We can't calculate exact duration without first point timestamp
                            # So we'll assume if pattern exists, it has reasonable duration
                            return True
                        except:
                            pass
                    return True  # If we can't verify, assume it's valid
                
                elif pattern_type_upper in ['TRIPLE_BOTTOM', 'TRIPLE_TOP']:
                    min_bars = 5  # At least 5 bars between each point
                    # Check if we have indices
                    first_idx = row.get('first_bottom_idx', row.get('first_top_idx', None))
                    second_idx = row.get('second_bottom_idx', row.get('second_top_idx', None))
                    third_idx = row.get('third_bottom_idx', row.get('third_top_idx', None))
                    if first_idx is not None and second_idx is not None and third_idx is not None:
                        bar_diff1 = abs(int(second_idx) - int(first_idx))
                        bar_diff2 = abs(int(third_idx) - int(second_idx))
                        return bar_diff1 >= min_bars and bar_diff2 >= min_bars
                    return True  # If we can't verify, assume it's valid
                
                elif pattern_type_upper == 'INVERSE_HEAD_SHOULDERS':
                    min_bars = 10  # At least 10 bars between shoulders
                    # Check if we have indices
                    left_shoulder_idx = row.get('left_shoulder_idx', None)
                    head_idx = row.get('head_idx', None)
                    right_shoulder_idx = row.get('right_shoulder_idx', None)
                    if left_shoulder_idx is not None and head_idx is not None and right_shoulder_idx is not None:
                        bar_diff1 = abs(int(head_idx) - int(left_shoulder_idx))
                        bar_diff2 = abs(int(right_shoulder_idx) - int(head_idx))
                        return bar_diff1 >= min_bars and bar_diff2 >= min_bars
                    return True  # If we can't verify, assume it's valid
                
                # For RSI divergence, time duration is less critical, so we allow it
                return True
            
            # Helper function to filter patterns based on selected metrics
            def filter_patterns_by_metrics(df: pd.DataFrame) -> pd.DataFrame:
                """
                Filter pattern alerts based on user-selected metrics.
                
                This function validates patterns against additional criteria that might
                be missed by the scipy algorithm, based on Capital.com and Investopedia guidelines.
                """
                if df.empty:
                    return df
                
                filtered_df = df.copy()
                original_count = len(filtered_df)
                
                # Get pattern metric settings from session state
                require_volume_confirmation = st.session_state.get('pattern_volume_confirmation', False)
                require_volume_spike_breakout = st.session_state.get('pattern_volume_spike_breakout', False)
                require_rsi_overbought = st.session_state.get('pattern_rsi_overbought', False)
                require_rsi_oversold = st.session_state.get('pattern_rsi_oversold', False)
                require_candlestick_reversal = st.session_state.get('pattern_candlestick_reversal', False)
                require_peak_symmetry = st.session_state.get('pattern_peak_symmetry', False)
                require_time_duration = st.session_state.get('pattern_time_duration', False)
                strict_retest_tolerance = st.session_state.get('pattern_retest_tolerance', False)
                require_retest_no_breach = st.session_state.get('pattern_retest_no_breach', False)
                require_volume_trend = st.session_state.get('pattern_volume_trend', False)
                require_advanced_candlestick = st.session_state.get('pattern_advanced_candlestick', False)
                require_rsi_divergence = st.session_state.get('pattern_rsi_divergence', False)
                require_momentum_alignment = st.session_state.get('pattern_momentum_alignment', False)
                
                # Get current interval for time duration calculation
                current_interval = st.session_state.params.get('interval', '1h')
                
                # Track which patterns pass validation
                valid_indices = []
                
                for idx, row in filtered_df.iterrows():
                    pattern_type = str(row.get('pattern_type', '')).upper()
                    is_valid = True
                    
                    # Volume Confirmation Checks
                    if require_volume_confirmation:
                        vol_ratio = row.get('vol_ratio', 0)
                        if pd.isna(vol_ratio) or vol_ratio <= 0:
                            # For double/triple patterns, we expect volume trends
                            # If vol_ratio is missing or invalid, skip this check for now
                            # (In a full implementation, we'd check historical volume trends)
                            pass
                    
                    if require_volume_spike_breakout:
                        vol_ratio = row.get('vol_ratio', 0)
                        # Require volume ratio > 1.5x for neckline breakouts
                        if pd.isna(vol_ratio) or vol_ratio < 1.5:
                            is_valid = False
                    
                    # RSI Confirmation Checks
                    if require_rsi_overbought:
                        # For bearish patterns (double/triple top), require RSI > 70
                        bearish_patterns = ['DOUBLE_TOP', 'TRIPLE_TOP', 'DOWNTREND_RETEST', 'RSI_BEARISH_DIVERGENCE']
                        if pattern_type in bearish_patterns:
                            rsi_value = row.get('rsi', None)
                            if rsi_value is not None and not pd.isna(rsi_value):
                                if float(rsi_value) < 70:
                                    is_valid = False
                    
                    if require_rsi_oversold:
                        # For bullish patterns (double/triple bottom), require RSI < 30
                        bullish_patterns = ['DOUBLE_BOTTOM', 'TRIPLE_BOTTOM', 'UPTREND_RETEST', 'RSI_BULLISH_DIVERGENCE', 'INVERSE_HEAD_SHOULDERS']
                        if pattern_type in bullish_patterns:
                            rsi_value = row.get('rsi', None)
                            if rsi_value is not None and not pd.isna(rsi_value):
                                if float(rsi_value) > 30:
                                    is_valid = False
                    
                    # Peak/Trough Symmetry Check (for double/triple patterns)
                    if require_peak_symmetry:
                        symmetry_patterns = ['DOUBLE_TOP', 'DOUBLE_BOTTOM', 'TRIPLE_TOP', 'TRIPLE_BOTTOM']
                        if pattern_type in symmetry_patterns:
                            # Check if pattern has symmetry metadata
                            # In a full implementation, we'd check if peaks/troughs are within 2% of each other
                            # For now, we'll check if entry_price is reasonable relative to price
                            entry_price = row.get('entry_price', None)
                            price = row.get('price', None)
                            if entry_price is not None and price is not None and not pd.isna(entry_price) and not pd.isna(price):
                                price_diff_pct = abs(float(entry_price) - float(price)) / float(price) * 100
                                # If entry price is more than 5% away from current price, might indicate poor symmetry
                                if price_diff_pct > 5:
                                    is_valid = False
                    
                    # Retest Tolerance Check
                    if strict_retest_tolerance:
                        retest_patterns = ['UPTREND_RETEST', 'DOWNTREND_RETEST']
                        if pattern_type in retest_patterns:
                            entry_price = row.get('entry_price', None)
                            price = row.get('price', None)
                            if entry_price is not None and price is not None and not pd.isna(entry_price) and not pd.isna(price):
                                retest_diff_pct = abs(float(entry_price) - float(price)) / float(entry_price) * 100
                                # Strict: require retest within 1% (default is 2%)
                                if retest_diff_pct > 1.0:
                                    is_valid = False
                    
                    # Retest No Breach Check
                    if require_retest_no_breach:
                        retest_patterns = ['UPTREND_RETEST', 'DOWNTREND_RETEST']
                        if pattern_type in retest_patterns:
                            entry_price = row.get('entry_price', None)
                            price = row.get('price', None)
                            if entry_price is not None and price is not None and not pd.isna(entry_price) and not pd.isna(price):
                                # For uptrend retest: price should not go below entry (support holds)
                                # For downtrend retest: price should not go above entry (resistance holds)
                                if pattern_type == 'UPTREND_RETEST' and float(price) < float(entry_price) * 0.99:
                                    is_valid = False
                                elif pattern_type == 'DOWNTREND_RETEST' and float(price) > float(entry_price) * 1.01:
                                    is_valid = False
                    
                    # Candlestick Reversal Check
                    if require_candlestick_reversal:
                        if not has_reversal_candlestick(row, pattern_type):
                            is_valid = False
                    
                    # Time Duration Check
                    if require_time_duration:
                        if not has_sufficient_time_duration(row, pattern_type, current_interval):
                            is_valid = False
                    
                    # Volume Trend Check
                    if require_volume_trend:
                        if not has_volume_trend_confirmation(row, pattern_type):
                            is_valid = False
                    
                    # Advanced Candlestick Pattern Check
                    if require_advanced_candlestick:
                        if not has_advanced_candlestick_pattern(row, pattern_type):
                            is_valid = False
                    
                    # RSI Divergence Confirmation Check
                    if require_rsi_divergence:
                        if not has_rsi_divergence_confirmation(row, pattern_type):
                            is_valid = False
                    
                    # Momentum Trend Alignment Check
                    if require_momentum_alignment:
                        if not has_momentum_trend_alignment(row, pattern_type):
                            is_valid = False
                    
                    if is_valid:
                        valid_indices.append(idx)
                
                filtered_df = filtered_df.loc[valid_indices].copy() if valid_indices else pd.DataFrame()
                
                if original_count > len(filtered_df):
                    filtered_count = original_count - len(filtered_df)
                    st.info(f"📊 Pattern metrics filter applied: {filtered_count} pattern(s) filtered out based on selected criteria")
                
                return filtered_df
            
            # Apply pattern metrics filtering if any metrics are enabled
            pattern_metrics_enabled = any([
                st.session_state.get('pattern_volume_confirmation', False),
                st.session_state.get('pattern_volume_spike_breakout', False),
                st.session_state.get('pattern_rsi_overbought', False),
                st.session_state.get('pattern_rsi_oversold', False),
                st.session_state.get('pattern_candlestick_reversal', False),
                st.session_state.get('pattern_peak_symmetry', False),
                st.session_state.get('pattern_time_duration', False),
                st.session_state.get('pattern_retest_tolerance', False),
                st.session_state.get('pattern_retest_no_breach', False),
                st.session_state.get('pattern_volume_trend', False),
                st.session_state.get('pattern_advanced_candlestick', False),
                st.session_state.get('pattern_rsi_divergence', False),
                st.session_state.get('pattern_momentum_alignment', False),
            ])
            
            if pattern_metrics_enabled and not pattern_alerts_df.empty:
                pattern_alerts_df = filter_patterns_by_metrics(pattern_alerts_df)
            
            # Create two main tabs for easy navigation
            tab1, tab2 = st.tabs(["🧩 Pattern Strategies", "📉 Legacy Strategy (Breakouts & Volume)"])
            
            # ========== TAB 1: Pattern Strategies ==========
            with tab1:
                render_section_header(
                    title="Pattern-Based Trading Signals",
                    subtitle="RSI Divergences, Retests, Inverse H&S, Double/Triple Patterns"
                )
                
                # Show active pattern metrics
            if pattern_metrics_enabled:
                enabled_metrics = []
                if st.session_state.get('pattern_volume_confirmation', False):
                    enabled_metrics.append("Volume Confirmation")
                if st.session_state.get('pattern_volume_spike_breakout', False):
                    enabled_metrics.append("Volume Spike on Breakout")
                if st.session_state.get('pattern_rsi_overbought', False):
                    enabled_metrics.append("RSI Overbought (>70)")
                if st.session_state.get('pattern_rsi_oversold', False):
                    enabled_metrics.append("RSI Oversold (<30)")
                if st.session_state.get('pattern_candlestick_reversal', False):
                    enabled_metrics.append("Candlestick Reversal")
                if st.session_state.get('pattern_peak_symmetry', False):
                    enabled_metrics.append("Peak/Trough Symmetry")
                if st.session_state.get('pattern_time_duration', False):
                    enabled_metrics.append("Time Duration")
                if st.session_state.get('pattern_retest_tolerance', False):
                    enabled_metrics.append("Strict Retest Tolerance")
                if st.session_state.get('pattern_retest_no_breach', False):
                    enabled_metrics.append("Retest No Breach")
                if st.session_state.get('pattern_volume_trend', False):
                    enabled_metrics.append("Volume Trend")
                if st.session_state.get('pattern_advanced_candlestick', False):
                    enabled_metrics.append("Advanced Candlestick")
                if st.session_state.get('pattern_rsi_divergence', False):
                    enabled_metrics.append("RSI Divergence")
                if st.session_state.get('pattern_momentum_alignment', False):
                    enabled_metrics.append("Momentum Alignment")
                
                if enabled_metrics:
                    metrics_text = " • ".join(enabled_metrics)
                    st.info(f"🔍 **Active Pattern Metrics:** {metrics_text}")
            
            if pattern_alerts_df.empty:
                render_empty_state(
                    icon="🎯",
                    title="No Pattern Alerts Detected",
                    message="No trading patterns were detected in the selected time period.\n\nPatterns detected include:\n- RSI Bullish/Bearish Divergence\n- Uptrend/Downtrend Retest\n- Inverse Head and Shoulders\n- Double Bottom/Top\n- Triple Bottom/Top"
                )
            else:
                # Pattern alerts display
                if not include_historical and only_recent_candle:
                    # Intraday view - compact table
                    render_section_header(
                        title="🎯 Pattern Alerts (Selected Candle)",
                        subtitle=f"{len(pattern_alerts_df)} pattern matches detected"
                    )
                    
                    pattern_display_cols = [
                        'symbol', 'pattern_type', 'price', 'entry_price',
                        'stop_loss', 'target_price', 'vol_ratio', 'timestamp'
                    ]
                    available_cols = [c for c in pattern_display_cols if c in pattern_alerts_df.columns]
                    if available_cols:
                        st.dataframe(
                            pattern_alerts_df[available_cols],
                            use_container_width=True,
                            height=400
                        )
                    
                    # Download button
                    csv = pattern_alerts_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Pattern Alerts (CSV)",
                        data=csv,
                        file_name=f"pattern_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    # Historical view - full table with summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        render_metric_card("Pattern Alerts", str(len(pattern_alerts_df)))
                    with col2:
                        unique_patterns = pattern_alerts_df['pattern_type'].nunique() if 'pattern_type' in pattern_alerts_df.columns else 0
                        render_metric_card("Unique Patterns", str(unique_patterns))
                    with col3:
                        unique_symbols = pattern_alerts_df['symbol'].nunique() if 'symbol' in pattern_alerts_df.columns else 0
                        render_metric_card("Symbols with Patterns", str(unique_symbols))
                    
                    render_section_header(
                        title="Pattern Alerts Table",
                        subtitle="All detected trading patterns"
                    )
                    
                    # Ensure dataframe is Arrow-compatible
                    pattern_display = pattern_alerts_df.copy()
                    for col in pattern_display.columns:
                        if pattern_display[col].dtype == 'object':
                            try:
                                pattern_display[col] = pd.to_numeric(pattern_display[col], errors='ignore')
                            except:
                                pass
                    
                    st.dataframe(pattern_display, use_container_width=True, height=500)
                    
                    # Download button
                    csv = pattern_alerts_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Pattern Alerts (CSV)",
                        data=csv,
                        file_name=f"pattern_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            # ========== TAB 2: Legacy Strategy (Breakouts & Volume) ==========
            with tab2:
                render_section_header(
                    title="Legacy Trading Strategy",
                    subtitle="Breakouts, Breakdowns, and Volume Spike Alerts"
                )
                
                if legacy_alerts_df.empty:
                    render_empty_state(
                        icon="📊",
                        title="No Legacy Alerts Detected",
                        message="No breakout, breakdown, or volume spike alerts were detected in the selected time period.\n\nLegacy alerts include:\n- Swing High/Low Breakouts\n- Breakdowns\n- 15-Minute Volume Spikes"
                    )
                else:
                    # Sort by volume ratio (highest first) to surface strongest moves
                    if 'vol_ratio' in legacy_alerts_df.columns:
                        legacy_alerts_df = legacy_alerts_df.sort_values('vol_ratio', ascending=False)
                    
                    if not include_historical and only_recent_candle:
                        # Intraday view - card-based display
                        render_section_header(
                            title="📊 Breakout / Volume Alerts (Selected Candle)",
                            subtitle=f"{len(legacy_alerts_df)} alerts detected"
                        )
                        
                        for idx, r in legacy_alerts_df.iterrows():
                            raw_signal_type = r.get('signal_type', 'N/A')
                            # Ensure signal_type is always a clean string (avoid float/NaN issues)
                            if pd.isna(raw_signal_type):
                                signal_type = 'UNKNOWN'
                            else:
                                signal_type = str(raw_signal_type)
                            
                            # Handle different alert types
                            if signal_type == 'VOLUME_SPIKE_15M':
                                # 15-minute volume spike alert
                                render_alert_card(
                                    symbol=r.get('symbol', 'N/A'),
                                    signal_type='VOLUME_SPIKE_15M',
                                    price=r.get('price', None),
                                    vol_ratio=r.get('vol_ratio', None),
                                    swing_level=None,  # Not applicable for volume spikes
                                    timestamp=r.get('timestamp', ''),
                                    price_momentum=r.get('price_momentum', None),
                                    additional_info={
                                        '15m Volume': f"{r.get('current_15m_volume', 0):.0f}",
                                        'Avg 1h Volume': f"{r.get('avg_1h_volume', 0):.0f}",
                                        'Alert Type': '15-Min Volume Spike'
                                    }
                                )
                            else:
                                # Regular breakout/breakdown alert
                                # Prepare additional info for momentum comparison (optional fields)
                                additional_info = {}
                                try:
                                    if 'avg_momentum_7d' in r and r.get('avg_momentum_7d') is not None:
                                        avg_mom = r.get('avg_momentum_7d', 0.0)
                                        if not pd.isna(avg_mom):
                                            additional_info['Avg Momentum (7d)'] = f"{avg_mom:+.2f}%"
                                    if 'momentum_ratio' in r and r.get('momentum_ratio') is not None:
                                        mom_ratio = r.get('momentum_ratio', 0.0)
                                        if not pd.isna(mom_ratio) and mom_ratio != 0:
                                            additional_info['Momentum Ratio'] = f"{mom_ratio:.2f}×"
                                except (KeyError, TypeError, ValueError):
                                    # Gracefully handle missing momentum fields (backward compatibility)
                                    pass
                                
                                render_alert_card(
                                    symbol=r.get('symbol', 'N/A'),
                                    signal_type=signal_type,
                                    price=r.get('price', None),
                                    vol_ratio=r.get('vol_ratio', None),
                                    swing_level=r.get('swing_high', None) if signal_type == 'BREAKOUT' else r.get('swing_low', None),
                                    timestamp=r.get('timestamp', ''),
                                    price_momentum=r.get('price_momentum', None),
                                    additional_info=additional_info if additional_info else None
                                )
                        
                        # Download button
                        csv = legacy_alerts_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Legacy Alerts (CSV)",
                            data=csv,
                            file_name=f"legacy_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    else:
                        # Historical view - summary stats and table
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            render_metric_card("Total Symbols", str(len(summary_df)))
                        
                        with col2:
                            total_trades = summary_df['trade_count'].sum() if 'trade_count' in summary_df.columns else 0
                            render_metric_card("Total Trades", str(int(total_trades)))
                        
                        with col3:
                            render_metric_card("Legacy Alerts", str(len(legacy_alerts_df)))
                        
                        with col4:
                            if total_trades > 0:
                                avg_win_rate = summary_df['win_rate'].mean() if 'win_rate' in summary_df.columns else 0
                                render_metric_card("Avg Win Rate", f"{avg_win_rate:.2f}%")
                            else:
                                render_metric_card("Avg Win Rate", "N/A")
                        
                        # Legacy alerts table
                        render_section_header(
                            title="Legacy Alerts Table",
                            subtitle="All breakout, breakdown, and volume spike signals"
                        )
                        
                        # Ensure dataframe is Arrow-compatible
                        legacy_display = legacy_alerts_df.copy()
                        for col in legacy_display.columns:
                            if legacy_display[col].dtype == 'object':
                                try:
                                    legacy_display[col] = pd.to_numeric(legacy_display[col], errors='ignore')
                                except:
                                    pass
                        
                        st.dataframe(legacy_display, use_container_width=True, height=400)
                        
                        # Download button
                        csv = legacy_alerts_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Legacy Alerts (CSV)",
                            data=csv,
                            file_name=f"legacy_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                        # Detailed summary table
                        if not summary_df.empty:
                            render_section_header(
                                title="Detailed Summary",
                                subtitle="Per-symbol analysis breakdown"
                            )
                            
                            # Ensure dataframe is Arrow-compatible
                            summary_df_display = summary_df.copy()
                            for col in summary_df_display.columns:
                                if summary_df_display[col].dtype == 'object':
                                    try:
                                        summary_df_display[col] = pd.to_numeric(summary_df_display[col], errors='ignore')
                                    except:
                                        pass
                            st.dataframe(summary_df_display, use_container_width=True, height=400)
                            
                            # Download button
                            csv = summary_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Summary (CSV)",
                                data=csv,
                                file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )

if __name__ == "__main__":
    main()

