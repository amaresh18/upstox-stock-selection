"""Test script to check if Streamlit can start."""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing imports...")
    import streamlit as st
    print(f"✓ Streamlit imported: {st.__version__}")
    
    from src.core.stock_selector import UpstoxStockSelector
    print("✓ UpstoxStockSelector imported")
    
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
    print("✓ Settings imported")
    print(f"  LOOKBACK_SWING: {LOOKBACK_SWING}")
    print(f"  VOL_WINDOW: {VOL_WINDOW}")
    print(f"  VOL_MULT: {VOL_MULT}")
    print(f"  HOLD_BARS: {HOLD_BARS}")
    
    print("\n✓ All imports successful!")
    print("\nYou can now run: streamlit run app.py")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

