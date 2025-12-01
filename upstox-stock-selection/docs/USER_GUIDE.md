# User Guide

This guide consolidates user-facing documentation.

## Quick Start

1. **Installation**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup**
   - Set environment variables (see README.md)
   - Run `python scripts/fetch_instruments.py` to create NSE.json

3. **Run Analysis**
   ```bash
   # Using UI
   streamlit run app.py
   
   # Using CLI
   python scripts/run_stock_selection.py
   ```

## UI Guide

See `docs/UI_GUIDE.md` for detailed UI documentation.

## Features

- **Stock Selection**: Analyze Nifty 100 stocks for trading signals
- **Pattern Detection**: RSI divergence, retest patterns, reversal patterns
- **Backtesting**: Test strategies on historical data
- **Alerts**: Real-time and scheduled alerts via Telegram

## Scheduling

See `docs/HOW_SCHEDULING_WORKS.md` for information about alert scheduling.

## Mobile Access

See `docs/MOBILE_ACCESS.md` for mobile app setup.

