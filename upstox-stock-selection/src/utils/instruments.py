"""
Utility functions for fetching and managing Upstox instruments.
"""

import json
import os
import aiohttp
from typing import Dict, List, Optional
from ..config.settings import UPSTOX_V2_BASE_URL, DEFAULT_NSE_JSON_PATH, DEFAULT_NIFTY100_JSON_PATH


async def fetch_instruments(access_token: str) -> List[Dict]:
    """
    Fetch all instruments from Upstox API.
    
    Args:
        access_token: Upstox access token
        
    Returns:
        List of instrument dictionaries
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Try different endpoints in order (v3 and v2)
    # Based on Upstox API documentation, try these endpoints:
    endpoints = [
        f"https://api.upstox.com/v3/instruments/NSE",  # NSE instruments (v3) - recommended
        f"https://api.upstox.com/v3/instruments/NSE_EQ",  # NSE Equity instruments (v3)
        f"https://api.upstox.com/v3/market-quote/instruments/NSE_EQ",  # NSE Equity instruments (v3)
        f"{UPSTOX_V2_BASE_URL}/market-quote/instruments/NSE_EQ",  # NSE Equity instruments (v2)
        f"{UPSTOX_V2_BASE_URL}/market-quote/instruments",  # All instruments (v2)
        f"{UPSTOX_V2_BASE_URL}/instruments",  # Direct instruments endpoint (v2)
    ]
    
    for url in endpoints:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse response
                        if 'data' in data:
                            instruments = data['data']
                            print(f"Successfully fetched instruments from: {url}")
                            return instruments
                        elif isinstance(data, list):
                            print(f"Successfully fetched instruments from: {url}")
                            return data
                        else:
                            print(f"Unexpected response format from {url}: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                            continue
                    else:
                        error_text = await response.text()
                        print(f"API error from {url}: Status {response.status}")
                        continue
                        
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
            continue
    
    print("All instrument endpoints failed. Please check API documentation.")
    return []


def filter_nse_equity(instruments: List[Dict], nifty100_symbols: Optional[List[str]] = None) -> List[Dict]:
    """
    Filter instruments for NSE equity instruments, optionally filtered by Nifty 100.
    
    Args:
        instruments: List of all instruments
        nifty100_symbols: Optional list of Nifty 100 symbols to filter
        
    Returns:
        List of filtered NSE equity instruments
    """
    # Load Nifty 100 symbols if not provided
    if nifty100_symbols is None:
        try:
            if os.path.exists(DEFAULT_NIFTY100_JSON_PATH):
                with open(DEFAULT_NIFTY100_JSON_PATH, 'r') as f:
                    nifty100_symbols = json.load(f)
        except:
            nifty100_symbols = None
    
    nse_equity = []
    
    for instrument in instruments:
        # Check if it's NSE equity
        if (instrument.get('exchange') == 'NSE' and 
            instrument.get('instrument_type') == 'EQ'):
            
            tradingsymbol = instrument.get('tradingsymbol', '')
            
            # If Nifty 100 filter is provided, only include those symbols
            if nifty100_symbols and tradingsymbol not in nifty100_symbols:
                continue
            
            nse_equity.append({
                'tradingsymbol': tradingsymbol,
                'instrument_key': instrument.get('instrument_key'),
                'exchange': instrument.get('exchange'),
                'instrument_type': instrument.get('instrument_type'),
                'name': instrument.get('name', ''),
                'isin': instrument.get('isin', '')
            })
    
    return nse_equity


def save_instruments_to_json(instruments: List[Dict], output_path: str = None) -> None:
    """
    Save instruments to JSON file.
    
    Args:
        instruments: List of instrument dictionaries
        output_path: Output file path (defaults to DEFAULT_NSE_JSON_PATH)
    """
    if output_path is None:
        output_path = DEFAULT_NSE_JSON_PATH
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(instruments, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(instruments)} NSE equity instruments to {output_path}")

