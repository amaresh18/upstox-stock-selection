# Architecture Guide

This document describes the refactored architecture of the Upstox Stock Selection System.

## Overview

The codebase follows a clean, layered architecture with clear separation of concerns:

```
src/
├── domain/          # Pure business logic (no I/O, no external deps)
├── services/        # Business orchestration
├── adapters/        # External integrations
├── infrastructure/  # Data access
├── core/            # Legacy + compatibility
├── config/          # Configuration
└── web/             # UI layer
```

## Architecture Layers

### Domain Layer (`src/domain/`)
Pure business logic with no external dependencies:
- **models/**: Domain entities (Alert, Signal, Pattern)
- **indicators/**: Technical indicators (RSI, Swing, Volume, Momentum)
- **signals/**: Signal detection (Breakout/Breakdown)
- **patterns/**: Pattern detection (RSI divergence, retest, reversal patterns)

### Services Layer (`src/services/`)
Business orchestration that coordinates domain logic and adapters:
- **analysis_service.py**: Main analysis orchestration

### Adapters Layer (`src/adapters/`)
External integrations:
- **api/**: Upstox and Yahoo Finance API clients
- **notifications/**: Telegram notifier
- **oauth/**: OAuth helpers

### Infrastructure Layer (`src/infrastructure/`)
Data access and storage:
- **repositories/**: Instrument and symbol repositories

### Core Layer (`src/core/`)
Legacy code and compatibility wrappers:
- **stock_selector.py**: Original implementation (maintained for compatibility)
- **stock_selector_compat.py**: Compatibility wrapper for new architecture
- **pattern_detector.py**: Pattern detection logic
- **backtester.py**: Backtesting engine

## Key Principles

1. **Separation of Concerns**: Each layer has a clear responsibility
2. **Dependency Inversion**: High-level modules depend on abstractions
3. **Single Responsibility**: Each class/function has one clear purpose
4. **DRY**: Common logic extracted to shared utilities

## Migration Path

The architecture supports gradual migration:
- **Phase 1**: New code uses new structure
- **Phase 2**: Existing code gradually migrated
- **Phase 3**: Legacy code removed once migration complete

## Usage

### Using New Architecture (Recommended)
```python
from src.services.analysis_service import AnalysisService

service = AnalysisService(api_key, access_token)
summary_df, alerts_df = await service.analyze_symbols(symbols)
```

### Using Compatibility Wrapper
```python
from src.core.stock_selector_compat import UpstoxStockSelector

selector = UpstoxStockSelector(api_key, access_token)
# Same interface as original, uses new architecture internally
```

### Using Original (Backward Compatible)
```python
from src.core.stock_selector import UpstoxStockSelector

selector = UpstoxStockSelector(api_key, access_token)
# Works exactly as before
```

## Benefits

1. **Testability**: Pure functions, mockable dependencies
2. **Maintainability**: Clear structure, small focused modules
3. **Extensibility**: Easy to add new features
4. **Backward Compatibility**: All existing code works unchanged

For detailed refactoring information, see `REFACTORING_COMPLETE_GUIDE.md`.

