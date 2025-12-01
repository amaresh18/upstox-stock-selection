"""Instrument repository for accessing instrument mappings."""

import json
import os
from typing import Dict, Optional

from ...config.settings import DEFAULT_NSE_JSON_PATH


class InstrumentRepository:
    """Repository for instrument key lookups."""
    
    def __init__(self, nse_json_path: str = None):
        """
        Initialize repository.
        
        Args:
            nse_json_path: Path to NSE.json file
        """
        self.nse_json_path = nse_json_path or DEFAULT_NSE_JSON_PATH
        self._cache: Optional[Dict[str, str]] = None
    
    def get_instrument_key(self, symbol: str) -> Optional[str]:
        """
        Get instrument key for symbol.
        
        Args:
            symbol: NSE trading symbol
            
        Returns:
            Instrument key or None
        """
        if self._cache is None:
            self._cache = self._load_instrument_map()
        
        if symbol in self._cache:
            return self._cache[symbol]
        
        nse_symbol = f"NSE_EQ|{symbol}"
        if nse_symbol in self._cache:
            return self._cache[nse_symbol]
        
        for key, value in self._cache.items():
            if key.upper() == symbol.upper():
                return value
        
        return None
    
    def _load_instrument_map(self) -> Dict[str, str]:
        """Load instrument map from JSON file."""
        try:
            if not os.path.exists(self.nse_json_path):
                return {}
            
            with open(self.nse_json_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                instrument_map = {}
                for item in data:
                    if 'tradingsymbol' in item and 'instrument_key' in item:
                        symbol = item['tradingsymbol']
                        instrument_key = item['instrument_key']
                        instrument_map[symbol] = instrument_key
                return instrument_map
            elif isinstance(data, dict):
                return data
            else:
                return {}
                
        except Exception as e:
            print(f"Error loading instrument map: {e}")
            return {}

