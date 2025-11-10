"""
Script to map instrument keys from UpstocksNiftyMapping.csv.xlsx file.

This script reads the Excel file and updates NSE.json with the instrument keys.
"""

import os
import sys
import json
import pandas as pd

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH


def map_from_upstox_file():
    """Map instrument keys from UpstocksNiftyMapping.csv.xlsx file."""
    print("="*80)
    print("MAP INSTRUMENT KEYS FROM UPSTOX FILE")
    print("="*80)
    
    # Check if file exists
    excel_file = "UpstocksNiftyMapping.csv.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ File not found: {excel_file}")
        print("   Please ensure the file is in the project root directory")
        return
    
    print(f"✅ Found file: {excel_file}")
    
    # Read Excel file
    print("\nReading Excel file...")
    try:
        df = pd.read_excel(excel_file)
        print(f"✅ Read {len(df)} rows from Excel file")
        print(f"\nColumns: {df.columns.tolist()}")
        print(f"\nFirst few rows:")
        print(df.head(10))
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Identify columns
    # Common column names: symbol, tradingsymbol, instrument_key, instrumentkey, etc.
    symbol_col = None
    instrument_key_col = None
    
    for col in df.columns:
        col_lower = str(col).lower()
        if 'symbol' in col_lower or 'trading' in col_lower:
            symbol_col = col
        if 'instrument' in col_lower or 'key' in col_lower:
            instrument_key_col = col
    
    if not symbol_col:
        print("\n⚠️  Could not identify symbol column")
        print("   Available columns:", df.columns.tolist())
        print("   Please check the file structure")
        return
    
    if not instrument_key_col:
        print("\n⚠️  Could not identify instrument_key column")
        print("   Available columns:", df.columns.tolist())
        print("   Please check the file structure")
        return
    
    print(f"\n✅ Using columns:")
    print(f"   Symbol: {symbol_col}")
    print(f"   Instrument Key: {instrument_key_col}")
    
    # Create mapping
    mapping = {}
    for _, row in df.iterrows():
        symbol = str(row[symbol_col]).strip()
        instrument_key = str(row[instrument_key_col]).strip()
        
        if symbol and instrument_key and instrument_key.lower() != 'nan':
            mapping[symbol] = instrument_key
    
    print(f"\n✅ Created mapping for {len(mapping)} symbols")
    
    # Load NSE.json
    nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    
    if not os.path.exists(nse_json_path):
        print(f"❌ {nse_json_path} not found")
        return
    
    with open(nse_json_path, 'r') as f:
        nse_data = json.load(f)
    
    # Create a map
    instruments_map = {item['tradingsymbol']: item for item in nse_data}
    
    # Update with mapped keys
    print("\nUpdating NSE.json with mapped instrument keys...")
    updated_count = 0
    new_count = 0
    not_found = []
    
    for symbol, instrument_key in mapping.items():
        if symbol in instruments_map:
            old_key = instruments_map[symbol].get('instrument_key')
            if old_key != instrument_key:
                instruments_map[symbol]['instrument_key'] = instrument_key
                updated_count += 1
                print(f"  ✅ Updated {symbol}: {old_key or 'None'} -> {instrument_key}")
        else:
            instruments_map[symbol] = {
                'tradingsymbol': symbol,
                'instrument_key': instrument_key,
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'name': symbol,
                'isin': None
            }
            new_count += 1
            print(f"  ✅ Added {symbol}: -> {instrument_key}")
    
    # Check for Nifty 100 symbols that are still missing
    if os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
        with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
            nifty100_symbols = json.load(f)
        
        for symbol in nifty100_symbols:
            if symbol not in mapping:
                if symbol not in instruments_map or not instruments_map[symbol].get('instrument_key'):
                    not_found.append(symbol)
    
    # Save updated NSE.json
    updated_instruments = list(instruments_map.values())
    updated_instruments.sort(key=lambda x: x.get('tradingsymbol', ''))
    
    with open(nse_json_path, 'w') as f:
        json.dump(updated_instruments, f, indent=2, ensure_ascii=False)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Updated {updated_count} instrument keys")
    print(f"✅ Added {new_count} new instruments")
    
    if not_found:
        print(f"\n⚠️  {len(not_found)} Nifty 100 symbols still missing instrument keys:")
        for symbol in sorted(not_found)[:20]:
            print(f"  - {symbol}")
        if len(not_found) > 20:
            print(f"  ... and {len(not_found) - 20} more")
    else:
        print("\n✅ All Nifty 100 symbols have instrument keys!")
    
    # Count total
    symbols_with_keys = sum(1 for item in updated_instruments if item.get('instrument_key'))
    print(f"\nTotal instruments with keys: {symbols_with_keys}")
    print(f"✅ Saved to {nse_json_path}")
    
    print("\n✅ Process completed!")


if __name__ == "__main__":
    map_from_upstox_file()

