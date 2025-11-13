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
        .stButton > button { background: #2962FF; border-radius: 6px; font-weight: 500; padding: 0.75rem 1.25rem; font-size: 0.875rem; }
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
            
            # Save to session state
            st.session_state.only_recent_candle = only_recent_candle
            st.session_state.include_historical = include_historical
            
            if include_historical and only_recent_candle:
                st.info("ℹ️ Historical results enabled. Recent-candle filter will be ignored.")
        
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
        
        # Action Buttons - iOS Style
        st.markdown("""
        <div style="margin-top: 2rem; margin-bottom: 1rem;">
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Load Defaults", use_container_width=True, key="load_defaults_btn"):
                load_default_values()
                st.rerun()
        
        with col2:
            if st.button("💾 Save Config", use_container_width=True):
                # Params are already synced from widgets above, just confirm
                show_toast("Configuration saved! All parameters are ready to use.", "success")
    
    # Premium main content area
    render_section_header(
        title="Analysis Dashboard",
        subtitle="Configure parameters and execute comprehensive stock analysis"
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
        
        # Initialize OAuth helper
        default_api_key = os.getenv('UPSTOX_API_KEY', 'e3d3c1d1-5338-4efa-b77f-c83ea604ea43')
        default_api_secret = os.getenv('UPSTOX_API_SECRET', '9kbfgnlibw')
        default_redirect_uri = os.getenv('UPSTOX_REDIRECT_URI', 'https://127.0.0.1')
        
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
                           style="font-size: 0.75rem; color: #2962FF; text-decoration: none; 
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
                    value=os.getenv('UPSTOX_API_KEY', ''),
                    key="manual_api_key",
                    help="Your Upstox API Key",
                    placeholder="Enter your API key"
                )
            
            with col2:
                access_token = st.text_input(
                    "Upstox Access Token",
                    value=os.getenv('UPSTOX_ACCESS_TOKEN', ''),
                    key="manual_access_token",
                    type="password",
                    help="Your Upstox Access Token",
                    placeholder="Enter your access token"
                )
            
            if st.button("💾 Save Manual Credentials", key="save_manual_creds"):
                if api_key and access_token:
                    os.environ['UPSTOX_API_KEY'] = api_key
                    os.environ['UPSTOX_ACCESS_TOKEN'] = access_token
                    st.success("✅ Credentials saved to current session!")
                else:
                    st.error("❌ Please provide both API Key and Access Token")
        
        # Use OAuth token if available, otherwise use manual input
        if 'oauth_access_token' in st.session_state:
            access_token = st.session_state.oauth_access_token
            api_key = st.session_state.get('saved_oauth_api_key', '')
        elif 'manual_api_key' in st.session_state and st.session_state.manual_api_key:
            api_key = st.session_state.manual_api_key
            access_token = st.session_state.manual_access_token if 'manual_access_token' in st.session_state else os.getenv('UPSTOX_ACCESS_TOKEN', '')
        else:
            api_key = os.getenv('UPSTOX_API_KEY', '')
            access_token = os.getenv('UPSTOX_ACCESS_TOKEN', '')
    
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
    
    # Action Buttons - Kite Style
    st.markdown("""
    <div style="margin: 1.5rem 0;">
    </div>
    """, unsafe_allow_html=True)
    
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
                                show_toast(f"Analysis complete! Found {len(alerts_df)} alerts.", "success")
                                st.success(f"✅ Analysis complete! Found {len(alerts_df)} alerts using the configured parameters.")
                            else:
                                show_toast("Analysis complete, but settings verification failed!", "warning")
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
                    show_toast(f"Error: {str(e)}", "error")
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.session_state.running = False
    
    # Premium results display
    if st.session_state.results:
        render_section_header(
            title="Analysis Results",
            subtitle="Review your comprehensive stock selection analysis"
        )
        
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
        # show premium Kite-style alerts
        if not include_historical and only_recent_candle:
            render_section_header(
                title="Intraday Alerts",
                subtitle="Recent closed candle alerts sorted by volume ratio (highest first)"
            )
            
            if alerts_df.empty:
                # Premium empty state
                candle_info = f"candle {selected_candle_dt.strftime('%H:%M')} - {candle_end.strftime('%H:%M')} IST" if selected_candle_dt else "selected candle"
                render_empty_state(
                    icon="📊",
                    title="No Alerts Detected",
                    message=f"No stocks met the selection criteria for the {candle_info}.\n\nThis could mean:\n- No breakouts/breakdowns occurred in this candle\n- Volume thresholds were not met\n- Swing levels were not breached"
                )
            else:
                # Sort by volume ratio (highest first) to surface strongest moves
                if 'vol_ratio' in alerts_df.columns:
                    alerts_df = alerts_df.sort_values('vol_ratio', ascending=False)

                # Render premium alert cards using component
                for idx, r in alerts_df.iterrows():
                    render_alert_card(
                        symbol=r.get('symbol', 'N/A'),
                        signal_type=r.get('signal_type', 'N/A'),
                        price=r.get('price', None),
                        vol_ratio=r.get('vol_ratio', None),
                        swing_level=r.get('swing_high', None) if r.get('signal_type') == 'BREAKOUT' else r.get('swing_low', None),
                        timestamp=r.get('timestamp', '')
                    )

                # Download button - iOS Style
                csv = alerts_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download These Alerts (CSV)",
                    data=csv,
                    file_name=f"recent_candle_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            # Full analytical view (includes historical if selected)
            # Premium summary statistics
            render_section_header(
                title="Summary Statistics",
                subtitle="Comprehensive analysis overview"
            )
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                render_metric_card("Total Symbols", str(len(summary_df)))
            
            with col2:
                total_trades = summary_df['trade_count'].sum() if 'trade_count' in summary_df.columns else 0
                render_metric_card("Total Trades", str(int(total_trades)))
            
            with col3:
                total_alerts = len(alerts_df)
                render_metric_card("Total Alerts", str(total_alerts))
            
            with col4:
                if total_trades > 0:
                    avg_win_rate = summary_df['win_rate'].mean() if 'win_rate' in summary_df.columns else 0
                    render_metric_card("Avg Win Rate", f"{avg_win_rate:.2f}%")
                else:
                    render_metric_card("Avg Win Rate", "N/A")
            
            # Premium alerts table
            if not alerts_df.empty:
                render_section_header(
                    title="Alerts",
                    subtitle="All detected trading signals"
                )
                
                # Ensure dataframe is Arrow-compatible by converting mixed types
                alerts_df_display = alerts_df.copy()
                # Convert numeric columns that might have NaN to float, then to string for display
                for col in alerts_df_display.columns:
                    if alerts_df_display[col].dtype == 'object':
                        # Try to convert to numeric, keep as string if fails
                        try:
                            alerts_df_display[col] = pd.to_numeric(alerts_df_display[col], errors='ignore')
                        except:
                            pass
                st.dataframe(alerts_df_display, use_container_width=True, height=400)
                
                # Download button - iOS Style
                csv = alerts_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Alerts (CSV)",
                    data=csv,
                    file_name=f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Premium summary table
            if not summary_df.empty:
                render_section_header(
                    title="Detailed Summary",
                    subtitle="Per-symbol analysis breakdown"
                )
                
                # Ensure dataframe is Arrow-compatible by converting mixed types
                summary_df_display = summary_df.copy()
                # Convert numeric columns that might have NaN to float
                for col in summary_df_display.columns:
                    if summary_df_display[col].dtype == 'object':
                        # Try to convert to numeric, keep as string if fails
                        try:
                            summary_df_display[col] = pd.to_numeric(summary_df_display[col], errors='ignore')
                        except:
                            pass
                st.dataframe(summary_df_display, use_container_width=True, height=400)
                
                # Download button - iOS Style
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

