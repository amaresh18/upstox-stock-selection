"""
Entry point script to fetch Upstox instrument keys and create NSE.json file.

This script fetches all instruments from Upstox API and filters for NSE equity instruments,
then saves them to data/NSE.json for use with the stock selection script.
"""

import os
import sys
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.instruments import fetch_instruments, filter_nse_equity, save_instruments_to_json
from src.utils.symbols import get_nifty_100_symbols
from src.config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH


async def main():
    """Main execution function."""
    # Get access token from environment variable
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if not access_token:
        print("Error: UPSTOX_ACCESS_TOKEN must be set as environment variable")
        print("\nUsage:")
        print("  Windows PowerShell:")
        print("    $env:UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("    python scripts/fetch_instruments.py")
        print("\n  Linux/Mac:")
        print("    export UPSTOX_ACCESS_TOKEN='your_access_token'")
        print("    python scripts/fetch_instruments.py")
        return
    
    print("Fetching instruments from Upstox API...")
    instruments = await fetch_instruments(access_token)
    
    if not instruments:
        print("No instruments fetched. Please check your access token.")
        return
    
    print(f"Fetched {len(instruments)} total instruments")
    
    # Get Nifty 100 symbols if available
    nifty100_symbols = None
    try:
        if os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
            import json
            with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
                nifty100_symbols = json.load(f)
                print(f"Loaded {len(nifty100_symbols)} Nifty 100 symbols for filtering")
    except:
        pass
    
    # Filter for NSE equity (optionally filtered by Nifty 100)
    print("Filtering for NSE equity instruments...")
    if nifty100_symbols:
        print("Filtering for Nifty 100 stocks only...")
    nse_equity = filter_nse_equity(instruments, nifty100_symbols)
    
    print(f"Found {len(nse_equity)} NSE equity instruments")
    
    # Save to JSON
    output_path = os.getenv('NSE_JSON_PATH', DEFAULT_NSE_JSON_PATH)
    save_instruments_to_json(nse_equity, output_path)
    
    # Print sample
    if nse_equity:
        print("\nSample instruments:")
        for inst in nse_equity[:5]:
            print(f"  {inst['tradingsymbol']} -> {inst['instrument_key']}")


if __name__ == "__main__":
    asyncio.run(main())

