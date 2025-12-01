"""Symbol repository for accessing symbol lists."""

import json
import os
from typing import List, Optional

from ...config.settings import DEFAULT_NIFTY100_JSON_PATH


class SymbolRepository:
    """Repository for symbol list access."""
    
    def __init__(self, nifty100_json_path: str = None):
        """
        Initialize repository.
        
        Args:
            nifty100_json_path: Path to nifty100_symbols.json file
        """
        self.nifty100_json_path = nifty100_json_path or DEFAULT_NIFTY100_JSON_PATH
        self._cache: Optional[List[str]] = None
    
    def get_nifty100_symbols(self) -> List[str]:
        """
        Get list of Nifty 100 symbols.
        
        Returns:
            List of symbol strings
        """
        if self._cache is None:
            self._cache = self._load_symbols()
        
        return self._cache.copy()
    
    def _load_symbols(self) -> List[str]:
        """Load symbols from JSON file."""
        try:
            if not os.path.exists(self.nifty100_json_path):
                return []
            
            with open(self.nifty100_json_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'symbols' in data:
                return data['symbols']
            else:
                return []
                
        except Exception as e:
            print(f"Error loading symbols: {e}")
            return []

