"""
Configuration settings for Upstox Stock Selection System.
"""

# API Configuration
UPSTOX_BASE_URL = "https://api.upstox.com/v3"
UPSTOX_V2_BASE_URL = "https://api.upstox.com/v2"

# Trading Configuration
LOOKBACK_SWING = 12  # Bars for swing high/low calculation
VOL_WINDOW = 70  # Bars for volume average (10 days * 7 bars/day)
VOL_MULT = 1.6  # Volume multiplier threshold
HOLD_BARS = 3  # Bars to hold position for P&L calculation

# Data Configuration
DEFAULT_HISTORICAL_DAYS = 30  # Default days of historical data
DEFAULT_INTERVAL = "1h"  # Default interval for candles
DEFAULT_MAX_WORKERS = 10  # Default number of parallel workers

# Timezone
TIMEZONE = "Asia/Kolkata"

# File Paths
DEFAULT_NSE_JSON_PATH = "data/NSE.json"
DEFAULT_NIFTY100_JSON_PATH = "data/nifty100_symbols.json"

