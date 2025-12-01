# Refactoring Complete Guide

This document provides a comprehensive overview of the refactored architecture.

## Architecture Overview

The codebase has been refactored to a world-class, layered architecture:

```
src/
├── domain/          # Pure business logic
├── services/        # Business orchestration  
├── adapters/        # External integrations
├── infrastructure/  # Data access
├── core/            # Legacy + compatibility
└── web/             # UI layer
```

## Key Components

### Domain Layer
- **Models**: Alert, Signal, Pattern entities
- **Indicators**: RSI, Swing, Volume, Momentum calculations
- **Signals**: Breakout/breakdown detection
- **Patterns**: Pattern detection (RSI divergence, retest, reversal)

### Services Layer
- **AnalysisService**: Main analysis orchestration

### Adapters Layer
- **UpstoxClient**: Upstox API client
- **YahooFinanceClient**: Yahoo Finance client
- **TelegramNotifier**: Telegram notifications

### Infrastructure Layer
- **InstrumentRepository**: Instrument key lookups
- **SymbolRepository**: Symbol list management

## Migration

The refactoring maintains 100% backward compatibility. See `ARCHITECTURE.md` for details.

