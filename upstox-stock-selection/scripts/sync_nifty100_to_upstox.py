"""
Script to sync Nifty 100 stocks with Upstox instrument keys.

This script:
1. Fetches official Nifty 100 list from NSE
2. Updates NSE.json to only include Nifty 100 symbols
3. Validates existing instrument keys by testing the Upstox API
4. Provides a clean NSE.json with only Nifty 100 instruments
"""

import os
import sys
import json
import asyncio
import pandas as pd
import aiohttp
from datetime import datetime, timedelta
from pytz import timezone

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH, UPSTOX_BASE_URL, TIMEZONE


async def test_instrument_key(access_token: str, instrument_key: str) -> bool:
    """
    Test if an instrument key is valid by trying to fetch historical data.
    
    Args:
        access_token: Upstox access token
        instrument_key: Instrument key to test
        
    Returns:
        True if instrument key is valid, False otherwise
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        # Test with a recent date range (last 2 days)
        ist = timezone(TIMEZONE)
        end_date = datetime.now(ist)
        start_date = end_date - timedelta(days=2)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Encode instrument key
        import urllib.parse
        encoded_key = urllib.parse.quote(instrument_key, safe='')
        
        # Try to fetch historical data
        url = f"{UPSTOX_BASE_URL}/historical-candle/{encoded_key}/hours/1/{end_str}/{start_str}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    return True
                elif response.status == 400:
                    error_text = await response.text()
                    if "UDAPI100011" in error_text or "Invalid Instrument key" in error_text:
                        return False
                return False
    except:
        return False


async def sync_nifty100_instruments():
    """Sync Nifty 100 stocks with Upstox instrument keys."""
    print("="*80)
    print("SYNC NIFTY 100 STOCKS WITH UPSTOX INSTRUMENTS")
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
        
        # Clean duplicates
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
    
    # Step 2: Load existing NSE.json
    print("\nStep 2: Loading existing NSE.json...")
    print("-" * 80)
    
    nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    existing_instruments = {}
    
    if os.path.exists(nse_json_path):
        try:
            with open(nse_json_path, 'r') as f:
                existing_data = json.load(f)
            
            if isinstance(existing_data, list):
                for item in existing_data:
                    symbol = item.get('tradingsymbol')
                    if symbol:
                        existing_instruments[symbol] = item
                print(f"✅ Loaded {len(existing_instruments)} existing instruments from {nse_json_path}")
            else:
                print(f"⚠️  NSE.json has unexpected format")
        except Exception as e:
            print(f"⚠️  Error loading NSE.json: {e}")
    else:
        print(f"⚠️  NSE.json not found at {nse_json_path}")
    
    # Step 3: Filter existing instruments to only Nifty 100
    print("\nStep 3: Filtering instruments to Nifty 100 only...")
    print("-" * 80)
    
    nifty100_instruments = []
    symbols_with_keys = set()
    symbols_without_keys = set()
    
    for symbol in symbols:
        if symbol in existing_instruments:
            inst = existing_instruments[symbol]
            if inst.get('instrument_key'):
                nifty100_instruments.append(inst)
                symbols_with_keys.add(symbol)
            else:
                # Symbol exists but no instrument key
                symbols_without_keys.add(symbol)
        else:
            # Symbol not in existing instruments
            symbols_without_keys.add(symbol)
    
    print(f"✅ Found instrument keys for: {len(symbols_with_keys)} symbols")
    print(f"⚠️  Missing instrument keys for: {len(symbols_without_keys)} symbols")
    
    # Step 4: Validate instrument keys (optional, if access token available)
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if access_token:
        print("\nStep 4: Validating instrument keys with Upstox API...")
        print("-" * 80)
        print("This may take a few minutes...")
        
        valid_keys = []
        invalid_keys = []
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(5)
        
        async def validate_key(inst):
            async with semaphore:
                symbol = inst.get('tradingsymbol')
                instrument_key = inst.get('instrument_key')
                if instrument_key:
                    is_valid = await test_instrument_key(access_token, instrument_key)
                    return symbol, instrument_key, is_valid
                return symbol, None, False
        
        # Validate all instrument keys
        tasks = [validate_key(inst) for inst in nifty100_instruments]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                continue
            symbol, instrument_key, is_valid = result
            if is_valid:
                valid_keys.append(symbol)
            else:
                invalid_keys.append(symbol)
        
        print(f"✅ Valid instrument keys: {len(valid_keys)}")
        print(f"❌ Invalid instrument keys: {len(invalid_keys)}")
        
        if invalid_keys:
            print(f"\nSymbols with invalid instrument keys:")
            for symbol in sorted(invalid_keys)[:10]:
                print(f"  - {symbol}")
            if len(invalid_keys) > 10:
                print(f"  ... and {len(invalid_keys) - 10} more")
        
        # Keep all instruments, but mark invalid ones (don't remove them)
        # We'll keep them with null instrument_key so user can update later
        for inst in nifty100_instruments:
            symbol = inst.get('tradingsymbol')
            if symbol in invalid_keys:
                # Mark as invalid by setting instrument_key to null
                inst['instrument_key'] = None
                print(f"  ⚠️  {symbol}: Invalid instrument key, setting to null")
    else:
        print("\nStep 4: Skipping validation (UPSTOX_ACCESS_TOKEN not set)")
        print("-" * 80)
        print("⚠️  To validate instrument keys, set UPSTOX_ACCESS_TOKEN environment variable")
    
    # Step 5: Add placeholders for symbols without instrument keys
    print("\nStep 5: Adding placeholders for symbols without instrument keys...")
    print("-" * 80)
    
    for symbol in symbols_without_keys:
        nifty100_instruments.append({
            'tradingsymbol': symbol,
            'instrument_key': None,  # Placeholder - needs to be filled manually
            'exchange': 'NSE',
            'instrument_type': 'EQ',
            'name': symbol,
            'isin': None
        })
    
    # Sort by symbol
    nifty100_instruments.sort(key=lambda x: x.get('tradingsymbol', ''))
    
    # Step 6: Save updated NSE.json
    print("\nStep 6: Saving updated NSE.json...")
    print("-" * 80)
    
    os.makedirs(os.path.dirname(nse_json_path), exist_ok=True)
    with open(nse_json_path, 'w') as f:
        json.dump(nifty100_instruments, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(nifty100_instruments)} instruments to {nse_json_path}")
    
    # Step 7: Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Nifty 100 symbols: {len(symbols)}")
    print(f"Instruments with valid keys: {len([inst for inst in nifty100_instruments if inst.get('instrument_key')])}")
    print(f"Instruments without keys: {len([inst for inst in nifty100_instruments if not inst.get('instrument_key')])}")
    
    if symbols_without_keys:
        print(f"\n⚠️  {len(symbols_without_keys)} symbols need instrument keys:")
        print("   You need to manually update NSE.json with correct instrument keys for these symbols.")
        print("   You can get instrument keys from:")
        print("   1. Upstox API documentation")
        print("   2. Upstox dashboard")
        print("   3. Upstox support")
    
    print("\n✅ Process completed!")
    print(f"   Nifty 100 symbols: {DEFAULT_NIFTY100_JSON_PATH}")
    print(f"   Updated instruments: {nse_json_path}")


if __name__ == "__main__":
    asyncio.run(sync_nifty100_instruments())

