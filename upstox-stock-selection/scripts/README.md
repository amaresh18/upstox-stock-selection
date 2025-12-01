# Scripts Directory

Essential scripts for the Upstox Stock Selection System.

## Main Scripts

### `run_stock_selection.py`
Main entry point for stock selection analysis.
```bash
python scripts/run_stock_selection.py
```

### `run_backtest.py`
Run backtesting on historical data.
```bash
python scripts/run_backtest.py
```

### `run_continuous_alerts.py`
Scheduled alert monitoring (used by Railway worker).
```bash
python scripts/run_continuous_alerts.py
```

### `run_realtime_alerts.py`
Real-time alert monitoring.
```bash
python scripts/run_realtime_alerts.py
```

### `fetch_instruments.py`
Fetch instrument mappings from Upstox API and create NSE.json.
```bash
python scripts/fetch_instruments.py
```

### `run_today_default.py`
Quick script to run today's analysis with default settings.
```bash
python scripts/run_today_default.py
```

## Utility Scripts

### `set_credentials.ps1`
PowerShell script to set environment variables (Windows only).

