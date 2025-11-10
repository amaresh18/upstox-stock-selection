"""
Script to get all 100 instrument keys for Nifty 100 stocks.

This script tries multiple approaches:
1. Download Upstox instruments JSON file (if available)
2. Fetch ISINs from NSE and construct instrument keys
3. Test instrument keys using Upstox API
"""

import os
import sys
import json
import asyncio
import aiohttp
import pandas as pd
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
    """Test if an instrument key is valid."""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        ist = timezone(TIMEZONE)
        end_date = datetime.now(ist)
        start_date = end_date - timedelta(days=2)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        encoded_key = urllib.parse.quote(instrument_key, safe='')
        url = f"{UPSTOX_BASE_URL}/historical-candle/{encoded_key}/hours/1/{end_str}/{start_str}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
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


async def download_upstox_instruments_file(access_token: str) -> dict:
    """
    Try to download Upstox instruments JSON file.
    
    According to Upstox documentation, there should be an instruments file available.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Try different URLs for instruments file
    urls = [
        "https://assets.upstox.com/market-quote/v2/instruments.json",
        "https://assets.upstox.com/instruments.json",
        "https://api.upstox.com/v2/market-quote/instruments",
        "https://api.upstox.com/v3/market-quote/instruments",
    ]
    
    for url in urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        if 'json' in content_type:
                            data = await response.json()
                            print(f"✅ Successfully downloaded instruments from: {url}")
                            return data
                        else:
                            # Might be a file download
                            text = await response.text()
                            try:
                                data = json.loads(text)
                                print(f"✅ Successfully downloaded instruments from: {url}")
                                return data
                            except:
                                pass
        except Exception as e:
            continue
    
    return None


def get_isin_from_nse(symbol: str) -> str:
    """
    Get ISIN for a symbol from NSE website.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        ISIN code or None
    """
    try:
        # Try to fetch from NSE Nifty 100 list (which includes ISIN)
        nse_url = "https://archives.nseindia.com/content/indices/ind_nifty100list.csv"
        n100 = pd.read_csv(nse_url)
        
        # Find the symbol
        row = n100[n100["Symbol"].str.strip() == symbol]
        if not row.empty:
            isin = row["ISIN Code"].iloc[0] if "ISIN Code" in row.columns else None
            return str(isin).strip() if pd.notna(isin) else None
    except:
        pass
    
    return None


async def get_all_instrument_keys():
    """Get all instrument keys for Nifty 100 stocks."""
    print("="*80)
    print("GET ALL INSTRUMENT KEYS FOR NIFTY 100")
    print("="*80)
    
    # Get access token
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ Error: UPSTOX_ACCESS_TOKEN must be set")
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
    
    # Create a map
    instruments_map = {item['tradingsymbol']: item for item in nse_data}
    
    print(f"✅ Loaded {len(instruments_map)} instruments from NSE.json")
    
    # Step 3: Try to download Upstox instruments file
    print("\nStep 3: Attempting to download Upstox instruments file...")
    print("-" * 80)
    
    upstox_instruments = await download_upstox_instruments_file(access_token)
    
    if upstox_instruments:
        print(f"✅ Downloaded Upstox instruments file")
        
        # Parse instruments
        if isinstance(upstox_instruments, dict):
            if 'data' in upstox_instruments:
                instruments_list = upstox_instruments['data']
            elif 'instruments' in upstox_instruments:
                instruments_list = upstox_instruments['instruments']
            else:
                instruments_list = []
        elif isinstance(upstox_instruments, list):
            instruments_list = upstox_instruments
        else:
            instruments_list = []
        
        print(f"   Found {len(instruments_list)} instruments in file")
        
        # Create mapping: symbol -> instrument_key
        symbol_to_key = {}
        for inst in instruments_list:
            if isinstance(inst, dict):
                symbol = inst.get('tradingsymbol') or inst.get('symbol') or inst.get('trading_symbol')
                key = inst.get('instrument_key') or inst.get('instrumentKey') or inst.get('instrument_key')
                
                if symbol and key:
                    symbol_to_key[symbol] = key
        
        print(f"   Mapped {len(symbol_to_key)} symbols to instrument keys")
        
        # Update NSE.json with found keys
        updated_count = 0
        for symbol in nifty100_symbols:
            if symbol in symbol_to_key:
                key = symbol_to_key[symbol]
                if symbol in instruments_map:
                    old_key = instruments_map[symbol].get('instrument_key')
                    if old_key != key:
                        instruments_map[symbol]['instrument_key'] = key
                        updated_count += 1
                        print(f"   ✅ {symbol}: {old_key or 'None'} -> {key}")
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
                    print(f"   ✅ {symbol}: Added -> {key}")
        
        print(f"\n✅ Updated {updated_count} instrument keys from Upstox file")
        
        # Save updated NSE.json
        updated_instruments = list(instruments_map.values())
        updated_instruments.sort(key=lambda x: x.get('tradingsymbol', ''))
        
        with open(nse_json_path, 'w') as f:
            json.dump(updated_instruments, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved updated NSE.json")
    
    else:
        print("⚠️  Could not download Upstox instruments file")
        print("   Trying alternative approach: Fetch ISINs from NSE...")
        
        # Step 4: Fetch ISINs from NSE and construct instrument keys
        print("\nStep 4: Fetching ISINs from NSE and constructing instrument keys...")
        print("-" * 80)
        
        try:
            nse_url = "https://archives.nseindia.com/content/indices/ind_nifty100list.csv"
            print(f"Fetching from: {nse_url}")
            n100 = pd.read_csv(nse_url)
            
            # Create symbol -> ISIN mapping
            symbol_to_isin = {}
            for _, row in n100.iterrows():
                symbol = str(row["Symbol"]).strip()
                isin = str(row.get("ISIN Code", "")).strip() if pd.notna(row.get("ISIN Code")) else None
                if symbol and isin and isin != "nan":
                    symbol_to_isin[symbol] = isin
            
            print(f"✅ Fetched ISINs for {len(symbol_to_isin)} symbols")
            
            # Construct instrument keys: NSE_EQ|{ISIN}
            constructed_keys = {}
            for symbol, isin in symbol_to_isin.items():
                if isin:
                    constructed_keys[symbol] = f"NSE_EQ|{isin}"
            
            print(f"✅ Constructed {len(constructed_keys)} instrument keys from ISINs")
            
            # Test constructed keys
            print("\nStep 5: Testing constructed instrument keys...")
            print("-" * 80)
            print("This may take a few minutes...")
            
            valid_keys = {}
            invalid_keys = []
            
            # Use semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(5)
            
            async def test_key(symbol, key):
                async with semaphore:
                    print(f"  Testing {symbol}...", end=' ')
                    is_valid = await test_instrument_key(access_token, key)
                    if is_valid:
                        print("✅ Valid")
                        return symbol, key
                    else:
                        print("❌ Invalid")
                        return symbol, None
            
            # Test all constructed keys
            tasks = [test_key(symbol, key) for symbol, key in constructed_keys.items()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    continue
                symbol, key = result
                if key:
                    valid_keys[symbol] = key
                else:
                    invalid_keys.append(symbol)
            
            print(f"\n✅ Found {len(valid_keys)} valid instrument keys")
            print(f"❌ {len(invalid_keys)} invalid instrument keys")
            
            # Update NSE.json with valid keys
            if valid_keys:
                print("\nStep 6: Updating NSE.json with valid instrument keys...")
                print("-" * 80)
                
                updated_count = 0
                for symbol, key in valid_keys.items():
                    if symbol in instruments_map:
                        old_key = instruments_map[symbol].get('instrument_key')
                        if old_key != key:
                            instruments_map[symbol]['instrument_key'] = key
                            instruments_map[symbol]['isin'] = symbol_to_isin.get(symbol)
                            updated_count += 1
                            print(f"   ✅ {symbol}: {old_key or 'None'} -> {key}")
                    else:
                        instruments_map[symbol] = {
                            'tradingsymbol': symbol,
                            'instrument_key': key,
                            'exchange': 'NSE',
                            'instrument_type': 'EQ',
                            'name': symbol,
                            'isin': symbol_to_isin.get(symbol)
                        }
                        updated_count += 1
                        print(f"   ✅ {symbol}: Added -> {key}")
                
                # Save updated NSE.json
                updated_instruments = list(instruments_map.values())
                updated_instruments.sort(key=lambda x: x.get('tradingsymbol', ''))
                
                with open(nse_json_path, 'w') as f:
                    json.dump(updated_instruments, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Updated {updated_count} instrument keys in NSE.json")
            
        except Exception as e:
            print(f"❌ Error fetching ISINs from NSE: {e}")
            import traceback
            traceback.print_exc()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    # Count symbols with keys
    symbols_with_keys = sum(1 for item in instruments_map.values() if item.get('instrument_key'))
    symbols_without_keys = len(nifty100_symbols) - symbols_with_keys
    
    print(f"Total Nifty 100 symbols: {len(nifty100_symbols)}")
    print(f"Symbols with instrument keys: {symbols_with_keys}")
    print(f"Symbols without instrument keys: {symbols_without_keys}")
    
    if symbols_without_keys > 0:
        missing = [s for s in nifty100_symbols if s not in instruments_map or not instruments_map[s].get('instrument_key')]
        print(f"\n⚠️  Still need instrument keys for {len(missing)} symbols:")
        for symbol in sorted(missing)[:20]:
            print(f"  - {symbol}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
        
        print("\n💡 To get remaining instrument keys:")
        print("   1. Check Upstox dashboard for each symbol")
        print("   2. Use Upstox API documentation")
        print("   3. Contact Upstox support")
    else:
        print("\n✅ All 100 Nifty 100 symbols have instrument keys!")
    
    print("\n✅ Process completed!")


if __name__ == "__main__":
    asyncio.run(get_all_instrument_keys())

