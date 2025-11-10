"""
Script to import instrument keys from a CSV file.

CSV format:
symbol,instrument_key
RELIANCE,NSE_EQ|INE002A01018
TCS,NSE_EQ|INE467B01029
...

This makes it easy to bulk import instrument keys.
"""

import os
import sys
import json
import csv

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH


def import_from_csv(csv_file_path: str):
    """Import instrument keys from CSV file."""
    print("="*80)
    print("IMPORT INSTRUMENT KEYS FROM CSV")
    print("="*80)
    
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        print("\nCSV format should be:")
        print("symbol,instrument_key")
        print("RELIANCE,NSE_EQ|INE002A01018")
        print("TCS,NSE_EQ|INE467B01029")
        return
    
    # Load NSE.json
    nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    
    if not os.path.exists(nse_json_path):
        print(f"❌ {nse_json_path} not found")
        return
    
    with open(nse_json_path, 'r') as f:
        nse_data = json.load(f)
    
    # Create a map
    instruments_map = {item['tradingsymbol']: item for item in nse_data}
    
    # Read CSV
    print(f"\nReading CSV file: {csv_file_path}")
    imported_keys = {}
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get('symbol', '').strip()
                instrument_key = row.get('instrument_key', '').strip()
                
                if symbol and instrument_key:
                    imported_keys[symbol] = instrument_key
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return
    
    print(f"✅ Read {len(imported_keys)} instrument keys from CSV")
    
    # Update NSE.json
    print("\nUpdating NSE.json...")
    updated_count = 0
    new_count = 0
    
    for symbol, key in imported_keys.items():
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
            new_count += 1
            print(f"  ✅ Added {symbol}: -> {key}")
    
    # Save updated NSE.json
    updated_instruments = list(instruments_map.values())
    updated_instruments.sort(key=lambda x: x.get('tradingsymbol', ''))
    
    with open(nse_json_path, 'w') as f:
        json.dump(updated_instruments, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {updated_count} instrument keys")
    print(f"✅ Added {new_count} new instruments")
    print(f"✅ Saved to {nse_json_path}")


def create_template_csv():
    """Create a template CSV file for manual input."""
    print("="*80)
    print("CREATE TEMPLATE CSV FOR INSTRUMENT KEYS")
    print("="*80)
    
    # Load Nifty 100 symbols
    if not os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
        print(f"❌ {DEFAULT_NIFTY100_JSON_PATH} not found")
        return
    
    with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
        nifty100_symbols = json.load(f)
    
    # Load NSE.json to find missing keys
    nse_json_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    
    if os.path.exists(nse_json_path):
        with open(nse_json_path, 'r') as f:
            nse_data = json.load(f)
        instruments_map = {item['tradingsymbol']: item for item in nse_data}
        missing_symbols = [
            symbol for symbol in nifty100_symbols
            if symbol not in instruments_map or not instruments_map[symbol].get('instrument_key')
        ]
    else:
        missing_symbols = nifty100_symbols
    
    # Create template CSV
    template_file = "instrument_keys_template.csv"
    
    with open(template_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['symbol', 'instrument_key'])
        
        for symbol in sorted(missing_symbols):
            writer.writerow([symbol, ''])
    
    print(f"✅ Created template CSV: {template_file}")
    print(f"   Contains {len(missing_symbols)} symbols without instrument keys")
    print("\nInstructions:")
    print("1. Open the CSV file in Excel or a text editor")
    print("2. Fill in the instrument_key column for each symbol")
    print("3. Format: NSE_EQ|INE1234567890")
    print("4. Save the file")
    print("5. Run: python scripts/import_instrument_keys_from_csv.py instrument_keys_template.csv")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        import_from_csv(csv_file)
    else:
        print("="*80)
        print("IMPORT INSTRUMENT KEYS FROM CSV")
        print("="*80)
        print("\nUsage:")
        print("  python scripts/import_instrument_keys_from_csv.py <csv_file>")
        print("\nOr create a template CSV:")
        print("  python scripts/import_instrument_keys_from_csv.py --create-template")
        print("\nCSV format:")
        print("  symbol,instrument_key")
        print("  RELIANCE,NSE_EQ|INE002A01018")
        print("  TCS,NSE_EQ|INE467B01029")
        
        if len(sys.argv) > 1 and sys.argv[1] == '--create-template':
            create_template_csv()


if __name__ == "__main__":
    main()

