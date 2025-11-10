"""
Script to help manually input instrument keys for Nifty 100 symbols.

This script:
1. Shows which symbols need instrument keys
2. Allows you to input instrument keys one by one
3. Updates NSE.json with the input keys
"""

import os
import sys
import json

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH


def show_missing_keys():
    """Show which symbols are missing instrument keys."""
    print("="*80)
    print("MANUAL INPUT INSTRUMENT KEYS")
    print("="*80)
    
    # Load Nifty 100 symbols
    if not os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
        print(f"❌ {DEFAULT_NIFTY100_JSON_PATH} not found")
        return
    
    with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
        nifty100_symbols = json.load(f)
    
    # Load NSE.json
    nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    
    if not os.path.exists(nse_json_path):
        print(f"❌ {nse_json_path} not found")
        return
    
    with open(nse_json_path, 'r') as f:
        nse_data = json.load(f)
    
    # Find symbols without instrument keys
    instruments_map = {item['tradingsymbol']: item for item in nse_data}
    missing_symbols = [
        symbol for symbol in nifty100_symbols
        if symbol not in instruments_map or not instruments_map[symbol].get('instrument_key')
    ]
    
    print(f"\nTotal Nifty 100 symbols: {len(nifty100_symbols)}")
    print(f"Symbols with instrument keys: {len(nifty100_symbols) - len(missing_symbols)}")
    print(f"Symbols without instrument keys: {len(missing_symbols)}")
    
    if not missing_symbols:
        print("\n✅ All symbols have instrument keys!")
        return
    
    print(f"\n⚠️  {len(missing_symbols)} symbols need instrument keys:")
    print("\nSymbols without instrument keys:")
    for i, symbol in enumerate(sorted(missing_symbols), 1):
        print(f"  {i:3}. {symbol}")
    
    print("\n" + "="*80)
    print("INSTRUCTIONS")
    print("="*80)
    print("\nTo get instrument keys:")
    print("1. Log in to Upstox dashboard: https://account.upstox.com/")
    print("2. Go to Developer section: https://account.upstox.com/developer/apps")
    print("3. Use the Upstox API documentation to get instrument keys")
    print("4. Or use the Upstox Python SDK:")
    print("   pip install upstox-python-sdk")
    print("   python scripts/get_instrument_keys_upstox_sdk.py")
    print("\n5. Or manually update NSE.json with instrument keys in format:")
    print("   NSE_EQ|INE1234567890")
    print("\n6. You can also create a CSV file with symbol,instrument_key pairs")
    print("   and use the import script: python scripts/import_instrument_keys_from_csv.py")
    
    # Ask if user wants to input keys now
    print("\n" + "="*80)
    response = input("\nDo you want to input instrument keys now? (y/n): ").strip().lower()
    
    if response == 'y':
        input_keys_interactively(instruments_map, missing_symbols, nse_json_path)
    else:
        print("\n✅ You can update NSE.json manually or use the import script later.")


def input_keys_interactively(instruments_map, missing_symbols, nse_json_path):
    """Allow user to input instrument keys interactively."""
    print("\n" + "="*80)
    print("INPUT INSTRUMENT KEYS")
    print("="*80)
    print("\nEnter instrument keys for each symbol.")
    print("Format: NSE_EQ|INE1234567890")
    print("Press Enter to skip a symbol.")
    print("Type 'done' to finish.\n")
    
    updated_count = 0
    
    for symbol in sorted(missing_symbols):
        while True:
            user_input = input(f"{symbol}: ").strip()
            
            if user_input.lower() == 'done':
                break
            
            if not user_input:
                # Skip this symbol
                break
            
            # Validate format (should be NSE_EQ|INE...)
            if user_input.startswith('NSE_EQ|') and len(user_input) > 10:
                # Update instrument
                if symbol in instruments_map:
                    instruments_map[symbol]['instrument_key'] = user_input
                else:
                    instruments_map[symbol] = {
                        'tradingsymbol': symbol,
                        'instrument_key': user_input,
                        'exchange': 'NSE',
                        'instrument_type': 'EQ',
                        'name': symbol,
                        'isin': None
                    }
                updated_count += 1
                print(f"  ✅ Updated {symbol}")
                break
            else:
                print(f"  ⚠️  Invalid format. Expected: NSE_EQ|INE1234567890")
                retry = input(f"  Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    break
        
        if user_input.lower() == 'done':
            break
    
    # Save updated NSE.json
    if updated_count > 0:
        updated_instruments = list(instruments_map.values())
        updated_instruments.sort(key=lambda x: x.get('tradingsymbol', ''))
        
        with open(nse_json_path, 'w') as f:
            json.dump(updated_instruments, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Updated {updated_count} instrument keys in NSE.json")
    else:
        print("\n⚠️  No instrument keys were updated")


def main():
    """Main function."""
    show_missing_keys()


if __name__ == "__main__":
    main()

