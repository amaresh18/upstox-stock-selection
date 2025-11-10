"""Quick script to check Nifty 100 status in NSE.json"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH

# Load Nifty 100 symbols
with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
    nifty100 = json.load(f)

# Load NSE.json
with open(DEFAULT_NSE_JSON_PATH, 'r') as f:
    nse_data = json.load(f)

# Get symbols from NSE.json
nse_symbols = {item['tradingsymbol'] for item in nse_data}
nse_with_keys = {item['tradingsymbol'] for item in nse_data if item.get('instrument_key')}
nse_without_keys = {item['tradingsymbol'] for item in nse_data if not item.get('instrument_key')}

# Check coverage
missing_from_nse = set(nifty100) - nse_symbols
extra_in_nse = nse_symbols - set(nifty100)

print("="*80)
print("NIFTY 100 STATUS CHECK")
print("="*80)
print(f"\nTotal Nifty 100 symbols: {len(nifty100)}")
print(f"Symbols in NSE.json: {len(nse_symbols)}")
print(f"Symbols with instrument keys: {len(nse_with_keys)}")
print(f"Symbols without instrument keys: {len(nse_without_keys)}")
print(f"Missing from NSE.json: {len(missing_from_nse)}")
print(f"Extra symbols in NSE.json (not in Nifty 100): {len(extra_in_nse)}")

if missing_from_nse:
    print(f"\n⚠️  Missing symbols from NSE.json:")
    for symbol in sorted(list(missing_from_nse))[:10]:
        print(f"  - {symbol}")
    if len(missing_from_nse) > 10:
        print(f"  ... and {len(missing_from_nse) - 10} more")

if extra_in_nse:
    print(f"\n⚠️  Extra symbols in NSE.json (not in Nifty 100):")
    for symbol in sorted(list(extra_in_nse))[:10]:
        print(f"  - {symbol}")
    if len(extra_in_nse) > 10:
        print(f"  ... and {len(extra_in_nse) - 10} more")

if nse_without_keys:
    print(f"\n⚠️  Symbols without instrument keys:")
    for symbol in sorted(list(nse_without_keys))[:15]:
        print(f"  - {symbol}")
    if len(nse_without_keys) > 15:
        print(f"  ... and {len(nse_without_keys) - 15} more")

print("\n" + "="*80)
print("✅ Status check completed!")

