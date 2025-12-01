# Project Structure

Clean, organized structure for the Upstox Stock Selection System.

```
upstox-stock-selection/
├── app.py                      # Main Streamlit UI
├── Procfile                    # Railway deployment config
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version
├── railway.json                # Railway configuration
├── manifest.json               # PWA manifest
├── README.md                   # Main documentation
├── ARCHITECTURE.md             # Architecture guide
├── REFACTORING_COMPLETE_GUIDE.md  # Refactoring guide
├── CLEANUP_SUMMARY.md          # Cleanup summary
│
├── src/                        # Source code
│   ├── domain/                 # Pure business logic
│   │   ├── models/             # Domain entities
│   │   ├── indicators/         # Technical indicators
│   │   ├── signals/             # Signal detection
│   │   └── patterns/            # Pattern detection
│   ├── services/               # Business orchestration
│   ├── adapters/                # External integrations
│   │   ├── api/                 # API clients
│   │   ├── notifications/      # Notification adapters
│   │   └── oauth/               # OAuth adapters
│   ├── infrastructure/          # Data access
│   │   └── repositories/       # Data repositories
│   ├── core/                    # Legacy + compatibility
│   ├── config/                  # Configuration
│   ├── utils/                   # Utilities
│   └── ui/                      # UI components
│
├── scripts/                     # Essential scripts
│   ├── run_stock_selection.py   # Main entry point
│   ├── run_backtest.py          # Backtesting
│   ├── run_continuous_alerts.py # Scheduled alerts
│   ├── run_realtime_alerts.py   # Real-time alerts
│   ├── fetch_instruments.py     # Setup script
│   ├── run_today_default.py     # Quick analysis
│   ├── set_credentials.ps1      # Windows utility
│   └── README.md                # Scripts documentation
│
├── docs/                        # Documentation
│   ├── README.md                # Documentation index
│   ├── USER_GUIDE.md            # User guide
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── UI_GUIDE.md              # UI documentation
│   ├── API_CREDENTIALS.md       # API setup
│   ├── TELEGRAM_SETUP.md        # Telegram setup
│   ├── OAUTH_LOGIN_GUIDE.md     # OAuth setup
│   ├── RAILWAY_DEPLOYMENT.md    # Railway deployment
│   ├── RAILWAY_TROUBLESHOOTING.md  # Railway troubleshooting
│   ├── RAILWAY_MONITORING.md    # Railway monitoring
│   ├── CLOUD_DEPLOYMENT.md      # Cloud deployment
│   ├── HOW_SCHEDULING_WORKS.md  # Scheduling details
│   ├── RUN_FOR_SPECIFIC_DATE.md # Date-specific runs
│   └── MOBILE_ACCESS.md         # Mobile setup
│
├── data/                        # Data files
│   ├── NSE.json.example         # Template
│   └── nifty100_symbols.json    # Symbol list
│
├── assets/                      # Static assets
│   └── css/                     # CSS files
│
└── run_ui.bat                   # Windows UI launcher
```

## Key Directories

### `src/domain/`
Pure business logic with no external dependencies:
- Models, indicators, signals, patterns

### `src/services/`
Business orchestration:
- Analysis service

### `src/adapters/`
External integrations:
- API clients, notifications, OAuth

### `src/infrastructure/`
Data access:
- Repositories

### `scripts/`
Essential scripts for running the application

### `docs/`
Organized documentation

## File Organization

- **Core code**: `src/` directory
- **Scripts**: `scripts/` directory
- **Documentation**: `docs/` directory
- **Data**: `data/` directory
- **Assets**: `assets/` directory
- **Config**: Root level (Procfile, requirements.txt, etc.)

