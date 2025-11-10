"""
Utility functions for fetching and managing stock symbols.
"""

import json
import os
import pandas as pd
from typing import List
from ..config.settings import DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH


def get_nifty_100_symbols(nse_json_path: str = None) -> List[str]:
    """
    Get list of Nifty 100 symbols.
    
    Priority:
    1. Load from NSE.json (if available)
    2. Load from nifty100_symbols.json (if available)
    3. Fetch from NSE website
    4. Use fallback list
    
    Args:
        nse_json_path: Path to NSE.json file
        
    Returns:
        List of NSE trading symbols
    """
    nse_path = nse_json_path or DEFAULT_NSE_JSON_PATH
    
    # Try to load from NSE.json if available
    if os.path.exists(nse_path):
        try:
            with open(nse_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                # Extract symbols from instrument list
                symbols = [item.get('tradingsymbol') for item in data if item.get('tradingsymbol')]
                if symbols:
                    print(f"Loaded {len(symbols)} symbols from {nse_path}")
                    return symbols
        except Exception as e:
            print(f"Error loading symbols from {nse_path}: {e}")
    
    # Try to load from nifty100_symbols.json
    if os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
        try:
            with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
                symbols = json.load(f)
                if symbols:
                    print(f"Loaded {len(symbols)} symbols from {DEFAULT_NIFTY100_JSON_PATH}")
                    return symbols
        except Exception as e:
            print(f"Error loading symbols from {DEFAULT_NIFTY100_JSON_PATH}: {e}")
    
    # Try to fetch from NSE website
    try:
        nse_url = "https://archives.nseindia.com/content/indices/ind_nifty100list.csv"
        print("Fetching Nifty 100 symbols from NSE...")
        n100 = pd.read_csv(nse_url)
        symbols = n100["Symbol"].astype(str).str.strip().tolist()
        symbols = sorted(set(symbols))
        print(f"Fetched {len(symbols)} Nifty 100 symbols from NSE")
        
        # Save for future use
        os.makedirs(os.path.dirname(DEFAULT_NIFTY100_JSON_PATH), exist_ok=True)
        with open(DEFAULT_NIFTY100_JSON_PATH, 'w') as f:
            json.dump(symbols, f, indent=2)
        
        return symbols
    except Exception as e:
        print(f"Error fetching from NSE: {e}")
        print("Using fallback list...")
    
    # Fallback: Common Nifty 100 symbols
    print("Warning: Using placeholder Nifty 100 symbols. Please update with complete list.")
    nifty_100 = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR', 'ICICIBANK',
        'BHARTIARTL', 'SBIN', 'BAJFINANCE', 'LICI', 'ITC', 'KOTAKBANK',
        'LT', 'HCLTECH', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'TITAN',
        'SUNPHARMA', 'ULTRACEMCO', 'NTPC', 'WIPRO', 'ONGC', 'NESTLEIND',
        'POWERGRID', 'ADANIENT', 'JSWSTEEL', 'BAJAJFINSV', 'TATAMOTORS',
        'ADANIPORTS', 'TATASTEEL', 'COALINDIA', 'DIVISLAB', 'HDFCLIFE',
        'SBILIFE', 'GRASIM', 'M&M', 'TECHM', 'CIPLA', 'APOLLOHOSP',
        'EICHERMOT', 'BRITANNIA', 'HEROMOTOCO', 'DRREDDY', 'INDUSINDBK',
        'ADANIGREEN', 'HINDALCO', 'BPCL', 'GODREJCP', 'DABUR', 'MARICO',
        'VEDL', 'PIDILITIND', 'DLF', 'HAVELLS', 'SIEMENS', 'BANKBARODA',
        'TATACONSUM', 'ICICIPRULI', 'SHREECEM', 'BERGEPAINT', 'TORNTPHARM',
        'AMBUJACEM', 'NAUKRI', 'ZOMATO', 'BAJAJHLDNG', 'INDIGO', 'MCDOWELL-N',
        'CANBK', 'UNIONBANK', 'PNB', 'IOB', 'CENTRALBK', 'UCOBANK',
        'BANDHANBNK', 'IDFCFIRSTB', 'FEDERALBNK', 'RBLBANK', 'YESBANK',
        'SOUTHBANK', 'JKBANK', 'CSBBANK', 'DCBBANK'
    ]
    
    return list(set(nifty_100))

