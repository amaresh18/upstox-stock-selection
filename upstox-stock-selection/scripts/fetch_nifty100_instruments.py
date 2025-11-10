"""
Script to fetch Nifty 100 stocks and map them to Upstox instrument keys.

This script:
1. Fetches official Nifty 100 list from NSE
2. Attempts to fetch instrument keys from Upstox API
3. Updates NSE.json with Nifty 100 instruments
"""

import os
import sys
import json
import asyncio
import pandas as pd

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.instruments import fetch_instruments, filter_nse_equity, save_instruments_to_json
from src.utils.symbols import get_nifty_100_symbols
from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH


async def fetch_nifty100_instruments():
    """Fetch Nifty 100 stocks and their Upstox instrument keys."""
    print("="*80)
    print("FETCH NIFTY 100 INSTRUMENTS FOR UPSTOX")
    print("="*80)
    
    # Step 1: Fetch Nifty 100 symbols from NSE
    print("\nStep 1: Fetching Nifty 100 symbols from NSE...")
    print("-" * 80)
    
    try:
        nse_url = "https://archives.nseindia.com/content/indices/ind_nifty100list.csv"
        print(f"Fetching from: {nse_url}")
        n100 = pd.read_csv(nse_url)
        symbols = n100["Symbol"].astype(str).str.strip().tolist()
        symbols = sorted(set(symbols))
        
        # Clean duplicates and any accidental leftovers
        symbols = [s for s in symbols if s and "DUMMY" not in s.upper()]
        
        print(f"✅ Successfully fetched {len(symbols)} Nifty 100 symbols from NSE")
        
        # Save to nifty100_symbols.json
        os.makedirs(os.path.dirname(DEFAULT_NIFTY100_JSON_PATH), exist_ok=True)
        with open(DEFAULT_NIFTY100_JSON_PATH, 'w') as f:
            json.dump(symbols, f, indent=2)
        print(f"✅ Saved to {DEFAULT_NIFTY100_JSON_PATH}")
        
    except Exception as e:
        print(f"❌ Error fetching Nifty 100 from NSE: {e}")
        print("Trying to load from existing file...")
        
        if os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
            with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
                symbols = json.load(f)
            print(f"✅ Loaded {len(symbols)} symbols from {DEFAULT_NIFTY100_JSON_PATH}")
        else:
            print("❌ Could not fetch or load Nifty 100 symbols")
            return
    
    # Step 2: Get access token
    print("\nStep 2: Checking Upstox API credentials...")
    print("-" * 80)
    
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ Error: UPSTOX_ACCESS_TOKEN must be set as environment variable")
        print("\nUsage:")
        print("  Windows PowerShell:")
        print("    $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("    python scripts/fetch_nifty100_instruments.py")
        print("\n  Linux/Mac:")
        print("    export UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("    python scripts/fetch_nifty100_instruments.py")
        print("\nNote: Without access token, we can only save the Nifty 100 symbol list.")
        print("      You'll need to manually update instrument keys in NSE.json later.")
        return
    
    print("✅ Access token found")
    
    # Step 3: Try to fetch instruments from Upstox API
    print("\nStep 3: Fetching instruments from Upstox API...")
    print("-" * 80)
    
    instruments = await fetch_instruments(access_token)
    
    if not instruments:
        print("⚠️  Could not fetch instruments from Upstox API.")
        print("   This might be because:")
        print("   1. Upstox API doesn't provide a public instruments endpoint")
        print("   2. The endpoint format has changed")
        print("   3. Your access token doesn't have required permissions")
        print("\n   Alternative approach:")
        print("   1. Get instrument keys from Upstox dashboard/API documentation")
        print("   2. Manually update NSE.json with correct instrument keys")
        print("   3. Or use the update_instrument_keys.py script if you have a working endpoint")
        
        # Still save the Nifty 100 symbols list
        print(f"\n✅ Saved {len(symbols)} Nifty 100 symbols to {DEFAULT_NIFTY100_JSON_PATH}")
        print("   You can now manually update NSE.json with instrument keys for these symbols")
        return
    
    print(f"✅ Fetched {len(instruments)} total instruments from Upstox API")
    
    # Step 4: Filter for NSE equity instruments matching Nifty 100
    print("\nStep 4: Filtering for NSE equity instruments (Nifty 100 only)...")
    print("-" * 80)
    
    nse_equity = filter_nse_equity(instruments, nifty100_symbols=symbols)
    
    print(f"✅ Found {len(nse_equity)} NSE equity instruments matching Nifty 100 symbols")
    
    # Step 5: Check which symbols have instrument keys
    print("\nStep 5: Checking symbol coverage...")
    print("-" * 80)
    
    found_symbols = {inst['tradingsymbol'] for inst in nse_equity if inst.get('instrument_key')}
    missing_symbols = set(symbols) - found_symbols
    
    print(f"✅ Found instrument keys for: {len(found_symbols)} symbols")
    if missing_symbols:
        print(f"⚠️  Missing instrument keys for: {len(missing_symbols)} symbols")
        print(f"   Missing symbols: {sorted(list(missing_symbols))[:10]}{'...' if len(missing_symbols) > 10 else ''}")
    
    # Step 6: Save to NSE.json
    print("\nStep 6: Saving instruments to NSE.json...")
    print("-" * 80)
    
    output_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    save_instruments_to_json(nse_equity, output_path)
    
    # Step 7: Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Nifty 100 symbols: {len(symbols)}")
    print(f"Instruments found: {len(nse_equity)}")
    print(f"Symbols with instrument keys: {len(found_symbols)}")
    print(f"Symbols missing instrument keys: {len(missing_symbols)}")
    
    if nse_equity:
        print("\nSample instruments (first 10):")
        for inst in nse_equity[:10]:
            print(f"  {inst['tradingsymbol']:15} -> {inst.get('instrument_key', 'N/A')}")
    
    if missing_symbols:
        print(f"\n⚠️  {len(missing_symbols)} symbols are missing instrument keys.")
        print("   You may need to:")
        print("   1. Check if these symbols are available on Upstox")
        print("   2. Get instrument keys from Upstox dashboard")
        print("   3. Manually update NSE.json with correct instrument keys")
    
    print("\n✅ Process completed!")
    print(f"   Nifty 100 symbols saved to: {DEFAULT_NIFTY100_JSON_PATH}")
    print(f"   Instruments saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(fetch_nifty100_instruments())

