"""
Script to get all instrument keys using Upstox Python SDK.

This script uses the Upstox Python SDK to get instrument keys for all Nifty 100 symbols.
If SDK is not available, it provides instructions for manual input.
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

from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH


def get_instrument_keys_with_sdk():
    """Try to get instrument keys using Upstox Python SDK."""
    try:
        # Try to import Upstox SDK
        try:
            from upstox_api.api import Upstox
            print("✅ Upstox SDK found")
        except ImportError:
            print("❌ Upstox SDK not installed")
            print("\nTo install Upstox SDK:")
            print("  pip install upstox-python-sdk")
            print("\nOr use the manual input script instead.")
            return None
        
        # Get credentials
        api_key = os.getenv('UPSTOX_API_KEY')
        access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
        
        if not api_key or not access_token:
            print("❌ UPSTOX_API_KEY and UPSTOX_ACCESS_TOKEN must be set")
            return None
        
        print("✅ Credentials found")
        
        # Initialize Upstox session
        print("\nInitializing Upstox session...")
        u = Upstox(api_key, access_token)
        
        # Load master contract for NSE equities
        print("Loading master contract for NSE equities...")
        u.get_master_contract('NSE_EQ')
        
        # Load Nifty 100 symbols
        if not os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
            print(f"❌ {DEFAULT_NIFTY100_JSON_PATH} not found")
            return None
        
        with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
            nifty100_symbols = json.load(f)
        
        print(f"✅ Loaded {len(nifty100_symbols)} Nifty 100 symbols")
        
        # Get instrument keys
        print("\nFetching instrument keys for all symbols...")
        print("This may take a few minutes...")
        
        instrument_keys = {}
        failed_symbols = []
        
        for i, symbol in enumerate(nifty100_symbols, 1):
            try:
                print(f"  [{i}/{len(nifty100_symbols)}] Fetching {symbol}...", end=' ')
                instrument = u.get_instrument_by_symbol('NSE_EQ', symbol)
                if instrument and hasattr(instrument, 'instrument_key'):
                    instrument_keys[symbol] = instrument.instrument_key
                    print(f"✅ {instrument.instrument_key}")
                else:
                    print("❌ Not found")
                    failed_symbols.append(symbol)
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                failed_symbols.append(symbol)
        
        print(f"\n✅ Found instrument keys for {len(instrument_keys)} symbols")
        print(f"❌ Failed to get keys for {len(failed_symbols)} symbols")
        
        if failed_symbols:
            print(f"\nFailed symbols:")
            for symbol in failed_symbols[:10]:
                print(f"  - {symbol}")
            if len(failed_symbols) > 10:
                print(f"  ... and {len(failed_symbols) - 10} more")
        
        return instrument_keys
        
    except Exception as e:
        print(f"❌ Error using Upstox SDK: {e}")
        import traceback
        traceback.print_exc()
        return None


def update_nse_json_with_keys(instrument_keys: dict):
    """Update NSE.json with found instrument keys."""
    nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    
    if not os.path.exists(nse_json_path):
        print(f"❌ {nse_json_path} not found")
        return
    
    with open(nse_json_path, 'r') as f:
        nse_data = json.load(f)
    
    # Create a map
    instruments_map = {item['tradingsymbol']: item for item in nse_data}
    
    # Update with found keys
    updated_count = 0
    for symbol, key in instrument_keys.items():
        if symbol in instruments_map:
            old_key = instruments_map[symbol].get('instrument_key')
            if old_key != key:
                instruments_map[symbol]['instrument_key'] = key
                updated_count += 1
                print(f"  ✅ Updated {symbol}: {old_key or 'None'} -> {key}")
        else:
            instruments_map[symbol] = {
                'tradingsymbol': symbol,
                'instrument_key': key,
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'name': symbol,
                'isin': None
            }
            updated_count += 1
            print(f"  ✅ Added {symbol}: -> {key}")
    
    # Save updated NSE.json
    updated_instruments = list(instruments_map.values())
    updated_instruments.sort(key=lambda x: x.get('tradingsymbol', ''))
    
    with open(nse_json_path, 'w') as f:
        json.dump(updated_instruments, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {updated_count} instrument keys in NSE.json")


def main():
    """Main function."""
    print("="*80)
    print("GET INSTRUMENT KEYS USING UPSTOX SDK")
    print("="*80)
    
    # Try to get instrument keys using SDK
    instrument_keys = get_instrument_keys_with_sdk()
    
    if instrument_keys:
        print("\n" + "="*80)
        print("UPDATING NSE.JSON")
        print("="*80)
        
        update_nse_json_with_keys(instrument_keys)
        
        # Final summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"✅ Found instrument keys for {len(instrument_keys)} symbols")
        
        # Check how many we still need
        with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
            nifty100_symbols = json.load(f)
        
        nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
        with open(nse_json_path, 'r') as f:
            nse_data = json.load(f)
        
        symbols_with_keys = sum(1 for item in nse_data if item.get('instrument_key'))
        symbols_without_keys = len(nifty100_symbols) - symbols_with_keys
        
        print(f"Total Nifty 100 symbols: {len(nifty100_symbols)}")
        print(f"Symbols with instrument keys: {symbols_with_keys}")
        print(f"Symbols without instrument keys: {symbols_without_keys}")
        
        if symbols_without_keys > 0:
            missing = [s for s in nifty100_symbols 
                      if s not in {item['tradingsymbol'] for item in nse_data} 
                      or not next((item for item in nse_data if item['tradingsymbol'] == s), {}).get('instrument_key')]
            print(f"\n⚠️  Still need instrument keys for {len(missing)} symbols")
            print("   Run this script again or use manual input script")
    else:
        print("\n" + "="*80)
        print("ALTERNATIVE APPROACHES")
        print("="*80)
        print("\nSince SDK is not available, try these alternatives:")
        print("\n1. Install Upstox SDK:")
        print("   pip install upstox-python-sdk")
        print("\n2. Use manual input script:")
        print("   python scripts/manual_input_instrument_keys.py")
        print("\n3. Get instrument keys from Upstox dashboard:")
        print("   - Log in to Upstox dashboard")
        print("   - Search for each symbol")
        print("   - Get the instrument key from the API or dashboard")
        print("   - Update NSE.json manually")
    
    print("\n✅ Process completed!")


if __name__ == "__main__":
    main()

