# Project Structure Documentation

This document describes the reorganized project structure for the Upstox Stock Selection System.

## Project Organization

The project has been reorganized following Python best practices and industry standards for maintainability and scalability.

### Directory Structure

```
upstox-stock-selection/
├── src/                          # Source code package
│   ├── __init__.py              # Package initialization
│   ├── core/                    # Core business logic
│   │   ├── __init__.py
│   │   └── stock_selector.py    # Main stock selection algorithm
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── instruments.py       # Instrument fetching utilities
│   │   └── symbols.py           # Symbol management utilities
│   └── config/                  # Configuration
│       ├── __init__.py
│       └── settings.py          # Configuration settings
├── scripts/                     # Entry point scripts
│   ├── fetch_instruments.py     # Script to fetch instrument mappings
│   └── run_stock_selection.py   # Main entry point script
├── data/                        # Data files
│   ├── NSE.json                 # Instrument mappings (generated)
│   ├── NSE.json.example         # Example template
│   └── nifty100_symbols.json   # Nifty 100 symbols (generated)
├── requirements.txt             # Python dependencies
├── README.md                    # Main documentation
├── .gitignore                   # Git ignore file
└── PROJECT_STRUCTURE.md         # This file
```

## Module Descriptions

### `src/core/stock_selector.py`

The main stock selection engine. Contains the `UpstoxStockSelector` class that:
- Fetches historical data from Yahoo Finance and Upstox API
- Calculates technical indicators (Swing High/Low, Volume Ratio, etc.)
- Detects breakout and breakdown signals
- Calculates P&L and statistics
- Analyzes multiple symbols in parallel

### `src/utils/instruments.py`

Utility functions for fetching and managing Upstox instruments:
- `fetch_instruments()`: Fetches instruments from Upstox API
- `filter_nse_equity()`: Filters for NSE equity instruments
- `save_instruments_to_json()`: Saves instruments to JSON file

### `src/utils/symbols.py`

Utility functions for managing stock symbols:
- `get_nifty_100_symbols()`: Gets Nifty 100 symbols from various sources

### `src/config/settings.py`

Centralized configuration settings:
- API endpoints
- Trading parameters (LOOKBACK_SWING, VOL_WINDOW, etc.)
- Default values
- File paths

### `scripts/fetch_instruments.py`

Entry point script to fetch instrument mappings from Upstox API and create NSE.json file.

### `scripts/run_stock_selection.py`

Main entry point script that:
- Checks for credentials
- Creates NSE.json if needed
- Runs stock selection analysis
- Displays results and saves to CSV

## Changes Made

### Files Removed

1. **Test Files** (10 files):
   - `test_api.py`
   - `test_batch_download.py`
   - `test_daily_endpoint.py`
   - `test_daily_historical.py`
   - `test_day_interval.py`
   - `test_extended_range.py`
   - `test_historical_api.py`
   - `test_hybrid_approach.py`
   - `test_yf_download_structure.py`
   - `test_yfinance_symbols.py`

2. **Debug Files**:
   - `debug_api_response.py`

3. **Redundant Helper Scripts**:
   - `create_minimal_nse.py`
   - `create_nse_from_isins.py`
   - `create_nse_from_testing.py`
   - `fetch_historical_batch.py`
   - `fetch_instruments_rest.py`
   - `fetch_instruments_sdk.py`
   - `fetch_instruments.py` (old version)
   - `fetch_nifty100.py`
   - `get_instrument_keys_from_api.py`
   - `get_instrument_keys.py`
   - `get_nifty100_symbols.py` (old version)

4. **Unused Features**:
   - `websocket_data_collector.py`

5. **Redundant Entry Points**:
   - `setup_and_run.py`
   - `run_stock_selection.py` (old version)
   - `upstox_stock_selection.py` (old version)

6. **Development Documentation** (9 files):
   - `API_LIMITATION_EXPLANATION.md`
   - `ENSURE_EXACT_MATCH_PROMPT.md`
   - `EXACT_LOGIC_MATCH.md`
   - `FIXES_APPLIED.md`
   - `HYBRID_APPROACH.md`
   - `HYBRID_DATA_SOURCE.md`
   - `QUICK_START.md`
   - `RUN_STOCK_SELECTION.md`
   - `WHY_ONLY_7_BARS.md`

### Files Created

1. **New Module Structure**:
   - `src/__init__.py`
   - `src/core/__init__.py`
   - `src/core/stock_selector.py`
   - `src/utils/__init__.py`
   - `src/utils/instruments.py`
   - `src/utils/symbols.py`
   - `src/config/__init__.py`
   - `src/config/settings.py`

2. **New Entry Points**:
   - `scripts/fetch_instruments.py`
   - `scripts/run_stock_selection.py`

3. **Configuration**:
   - `.gitignore`

4. **Documentation**:
   - Updated `README.md`
   - `PROJECT_STRUCTURE.md` (this file)

### Files Reorganized

1. **Data Files**:
   - Moved `NSE.json` → `data/NSE.json`
   - Moved `NSE.json.example` → `data/NSE.json.example`
   - Moved `nifty100_symbols.json` → `data/nifty100_symbols.json`

## Benefits of New Structure

1. **Modularity**: Code is organized into logical modules (core, utils, config)
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Scalability**: Easy to add new features without cluttering
4. **Reusability**: Utility functions can be reused across the project
5. **Testability**: Clear separation of concerns makes testing easier
6. **Professional**: Follows Python best practices and industry standards
7. **Documentation**: Clear structure makes it easier to understand and contribute

## Usage

### Running the Application

1. **Fetch Instruments** (First Time):
   ```bash
   python scripts/fetch_instruments.py
   ```

2. **Run Stock Selection**:
   ```bash
   python scripts/run_stock_selection.py
   ```

### Development

When adding new features:

1. **Core Logic**: Add to `src/core/`
2. **Utilities**: Add to `src/utils/`
3. **Configuration**: Update `src/config/settings.py`
4. **Entry Points**: Add to `scripts/`

## Migration Notes

If you have existing code that imports from the old structure:

- `from upstox_stock_selection import UpstoxStockSelector`
  → `from src.core.stock_selector import UpstoxStockSelector`

- `from fetch_instruments import ...`
  → `from src.utils.instruments import ...`

- `from get_nifty100_symbols import ...`
  → `from src.utils.symbols import ...`

## Future Enhancements

The new structure makes it easy to add:

1. **Testing**: Add `tests/` directory with unit tests
2. **Logging**: Add logging configuration in `src/config/`
3. **Database**: Add database models in `src/models/`
4. **API**: Add API endpoints in `src/api/`
5. **CLI**: Add CLI interface in `src/cli/`

