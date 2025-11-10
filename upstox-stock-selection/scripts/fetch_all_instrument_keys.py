"""
Script to fetch instrument keys for all Nifty 100 symbols by testing Upstox API.

This script attempts to find instrument keys by:
1. Testing common instrument key formats
2. Using ISIN if available
3. Testing historical candle API with different formats
"""

import os
import sys
import json
import asyncio
import aiohttp
import urllib.parse
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
        encoded_key = urllib.parse.quote(instrument_key, safe='')
        
        # Try to fetch historical data
        url = f"{UPSTOX_BASE_URL}/historical-candle/{encoded_key}/hours/1/{end_str}/{start_str}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if we got valid data
                    candles = None
                    if 'data' in data:
                        if 'candles' in data['data']:
                            candles = data['data']['candles']
                        elif isinstance(data['data'], list):
                            candles = data['data']
                    elif isinstance(data, list):
                        candles = data
                    
                    if candles and len(candles) > 0:
                        return True
                elif response.status == 400:
                    error_text = await response.text()
                    if "UDAPI100011" in error_text or "Invalid Instrument key" in error_text:
                        return False
                return False
    except:
        return False


async def find_instrument_key_by_symbol(access_token: str, symbol: str, isin: str = None) -> str:
    """
    Try to find instrument key for a symbol by testing different formats.
    
    Args:
        access_token: Upstox access token
        symbol: Trading symbol
        isin: ISIN code (optional)
        
    Returns:
        Instrument key if found, None otherwise
    """
    # Common instrument key formats to try:
    # Format 1: NSE_EQ|{ISIN} (if ISIN available)
    # Format 2: NSE_EQ|{SYMBOL} (less common)
    # Format 3: NSE|{SYMBOL} (less common)
    
    test_keys = []
    
    # If ISIN is available, try that first
    if isin:
        test_keys.append(f"NSE_EQ|{isin}")
    
    # Try common formats (these are less likely but worth trying)
    # Note: Most instrument keys use ISIN format
    
    # Test all possible keys
    for test_key in test_keys:
        if await test_instrument_key(access_token, test_key):
            return test_key
    
    return None


async def fetch_all_instrument_keys():
    """Fetch instrument keys for all Nifty 100 symbols."""
    print("="*80)
    print("FETCH ALL INSTRUMENT KEYS FOR NIFTY 100")
    print("="*80)
    
    # Get access token
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ Error: UPSTOX_ACCESS_TOKEN must be set as environment variable")
        print("\nUsage:")
        print("  Windows PowerShell:")
        print("    $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("    python scripts/fetch_all_instrument_keys.py")
        return
    
    print("✅ Access token found")
    
    # Load Nifty 100 symbols
    print("\nStep 1: Loading Nifty 100 symbols...")
    print("-" * 80)
    
    if not os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
        print(f"❌ {DEFAULT_NIFTY100_JSON_PATH} not found")
        print("   Run: python scripts/sync_nifty100_to_upstox.py first")
        return
    
    with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
        nifty100_symbols = json.load(f)
    
    print(f"✅ Loaded {len(nifty100_symbols)} Nifty 100 symbols")
    
    # Load existing NSE.json
    print("\nStep 2: Loading existing NSE.json...")
    print("-" * 80)
    
    nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    
    if not os.path.exists(nse_json_path):
        print(f"❌ {nse_json_path} not found")
        return
    
    with open(nse_json_path, 'r') as f:
        nse_data = json.load(f)
    
    # Create a map of symbol -> instrument
    instruments_map = {item['tradingsymbol']: item for item in nse_data}
    
    print(f"✅ Loaded {len(instruments_map)} instruments from NSE.json")
    
    # Find symbols without instrument keys
    symbols_without_keys = [
        symbol for symbol in nifty100_symbols 
        if symbol not in instruments_map or not instruments_map[symbol].get('instrument_key')
    ]
    
    print(f"\nStep 3: Finding instrument keys for {len(symbols_without_keys)} symbols...")
    print("-" * 80)
    print("⚠️  Note: This script can only test known formats.")
    print("   For symbols without ISIN, you may need to get instrument keys manually from Upstox.")
    
    # Try to find instrument keys
    found_keys = {}
    not_found = []
    
    # Use semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(5)
    
    async def find_key_for_symbol(symbol):
        async with semaphore:
            inst = instruments_map.get(symbol, {})
            isin = inst.get('isin')
            
            print(f"  Testing {symbol}...", end=' ')
            key = await find_instrument_key_by_symbol(access_token, symbol, isin)
            
            if key:
                print(f"✅ Found: {key}")
                return symbol, key
            else:
                print("❌ Not found")
                return symbol, None
    
    # Process all symbols
    tasks = [find_key_for_symbol(symbol) for symbol in symbols_without_keys]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, Exception):
            continue
        symbol, key = result
        if key:
            found_keys[symbol] = key
        else:
            not_found.append(symbol)
    
    # Update NSE.json with found keys
    if found_keys:
        print(f"\nStep 4: Updating NSE.json with {len(found_keys)} found instrument keys...")
        print("-" * 80)
        
        for symbol, key in found_keys.items():
            if symbol in instruments_map:
                instruments_map[symbol]['instrument_key'] = key
            else:
                instruments_map[symbol] = {
                    'tradingsymbol': symbol,
                    'instrument_key': key,
                    'exchange': 'NSE',
                    'instrument_type': 'EQ',
                    'name': symbol,
                    'isin': None
                }
        
        # Save updated NSE.json
        updated_instruments = list(instruments_map.values())
        updated_instruments.sort(key=lambda x: x.get('tradingsymbol', ''))
        
        with open(nse_json_path, 'w') as f:
            json.dump(updated_instruments, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated NSE.json with {len(found_keys)} new instrument keys")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Nifty 100 symbols: {len(nifty100_symbols)}")
    print(f"Instrument keys found: {len(found_keys)}")
    print(f"Instrument keys still missing: {len(not_found)}")
    
    if found_keys:
        print(f"\n✅ Found instrument keys for:")
        for symbol in sorted(list(found_keys.keys()))[:10]:
            print(f"  - {symbol}: {found_keys[symbol]}")
        if len(found_keys) > 10:
            print(f"  ... and {len(found_keys) - 10} more")
    
    if not_found:
        print(f"\n⚠️  Still need instrument keys for {len(not_found)} symbols:")
        print("   You need to get these manually from Upstox:")
        for symbol in sorted(not_found)[:15]:
            print(f"  - {symbol}")
        if len(not_found) > 15:
            print(f"  ... and {len(not_found) - 15} more")
        
        print("\n💡 To get instrument keys manually:")
        print("   1. Log in to Upstox dashboard")
        print("   2. Search for each symbol")
        print("   3. Get the instrument key from the API or dashboard")
        print("   4. Update NSE.json with the correct instrument keys")
    
    print("\n✅ Process completed!")


if __name__ == "__main__":
    asyncio.run(fetch_all_instrument_keys())

