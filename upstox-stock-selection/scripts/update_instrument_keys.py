"""
Script to update instrument keys in NSE.json by fetching fresh data from Upstox API.

This script:
1. Fetches latest instrument keys from Upstox API
2. Updates NSE.json with fresh instrument keys
3. Preserves existing data structure
"""

import os
import sys
import json
import asyncio

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


async def update_instrument_keys():
    """Update instrument keys in NSE.json with fresh data from Upstox API."""
    print("="*80)
    print("UPDATE INSTRUMENT KEYS")
    print("="*80)
    
    # Get access token from environment variable
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not access_token:
        print("\n❌ Error: UPSTOX_ACCESS_TOKEN must be set as environment variable")
        print("\nUsage:")
        print("  Windows PowerShell:")
        print("    $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("    python scripts/update_instrument_keys.py")
        print("\n  Linux/Mac:")
        print("    export UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("    python scripts/update_instrument_keys.py")
        return
    
    # Check if NSE.json exists
    nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    existing_symbols = set()
    existing_instruments = {}
    
    if os.path.exists(nse_json_path):
        print(f"\nFound existing NSE.json at {nse_json_path}")
        try:
            with open(nse_json_path, 'r') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, list):
                    for item in existing_data:
                        if 'tradingsymbol' in item:
                            symbol = item['tradingsymbol']
                            existing_symbols.add(symbol)
                            existing_instruments[symbol] = item
                print(f"   Found {len(existing_symbols)} existing symbols")
        except Exception as e:
            print(f"   ⚠️  Error reading existing NSE.json: {e}")
    else:
        print(f"\nNSE.json not found at {nse_json_path}")
        print("   Will create new file with fetched instruments")
    
    # Fetch instruments from Upstox API
    print("\nFetching instruments from Upstox API...")
    instruments = await fetch_instruments(access_token)
    
    if not instruments:
        print("\n❌ No instruments fetched. Please check your access token.")
        print("   Make sure your access token is valid and has the required permissions.")
        return
    
    print(f"✅ Fetched {len(instruments)} total instruments")
    
    # Get Nifty 100 symbols if available
    nifty100_symbols = None
    try:
        if os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
            with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
                nifty100_symbols = json.load(f)
                print(f"📊 Loaded {len(nifty100_symbols)} Nifty 100 symbols for filtering")
    except:
        pass
    
    # Filter for NSE equity (optionally filtered by Nifty 100)
    print("\nFiltering for NSE equity instruments...")
    if nifty100_symbols:
        print("   Filtering for Nifty 100 stocks only...")
    nse_equity = filter_nse_equity(instruments, nifty100_symbols)
    
    print(f"✅ Found {len(nse_equity)} NSE equity instruments")
    
    # Create mapping of symbol -> instrument_key from fetched data
    fetched_keys = {}
    for inst in nse_equity:
        symbol = inst.get('tradingsymbol')
        instrument_key = inst.get('instrument_key')
        if symbol and instrument_key:
            fetched_keys[symbol] = instrument_key
    
    # Update existing instruments with fresh keys
    updated_count = 0
    new_count = 0
    
    if existing_symbols:
        print(f"\nUpdating instrument keys...")
        for symbol in existing_symbols:
            if symbol in fetched_keys:
                old_key = existing_instruments.get(symbol, {}).get('instrument_key', 'N/A')
                new_key = fetched_keys[symbol]
                if old_key != new_key:
                    existing_instruments[symbol]['instrument_key'] = new_key
                    updated_count += 1
                    print(f"   ✅ Updated {symbol}: {old_key} -> {new_key}")
    
    # Add new instruments that weren't in existing file
    for inst in nse_equity:
        symbol = inst.get('tradingsymbol')
        if symbol and symbol not in existing_instruments:
            existing_instruments[symbol] = inst
            new_count += 1
    
    # Prepare final list
    final_instruments = list(existing_instruments.values())
    
    # Save to JSON
    print(f"\nSaving updated instruments to {nse_json_path}...")
    save_instruments_to_json(final_instruments, nse_json_path)
    
    # Print summary
    print("\n" + "="*80)
    print("UPDATE SUMMARY")
    print("="*80)
    print(f"Total instruments in file: {len(final_instruments)}")
    print(f"Instruments updated: {updated_count}")
    print(f"New instruments added: {new_count}")
    print(f"Existing instruments preserved: {len(existing_symbols) - updated_count}")
    
    # Show sample of updated keys
    if updated_count > 0:
        print("\nSample of updated instrument keys:")
        count = 0
        for symbol, inst in existing_instruments.items():
            if symbol in fetched_keys and count < 5:
                print(f"   {symbol}: {inst.get('instrument_key')}")
                count += 1
    
    print("\n✅ Instrument keys updated successfully!")
    print("   You can now run the backtest again with updated keys.")


if __name__ == "__main__":
    asyncio.run(update_instrument_keys())

