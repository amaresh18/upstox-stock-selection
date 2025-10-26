# Stock Trading Marketplace App - Directory Structure

```
trading-marketplace/
├── mobile-app/                          # React Native Frontend
│   ├── src/
│   │   ├── screens/                     # Screen components
│   │   │   ├── auth/
│   │   │   │   ├── LoginScreen.tsx
│   │   │   │   ├── RegisterScreen.tsx
│   │   │   │   └── ForgotPasswordScreen.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardScreen.tsx
│   │   │   │   ├── PortfolioScreen.tsx
│   │   │   │   └── WatchlistScreen.tsx
│   │   │   ├── trading/
│   │   │   │   ├── TradingScreen.tsx
│   │   │   │   ├── OrderScreen.tsx
│   │   │   │   ├── OrderHistoryScreen.tsx
│   │   │   │   └── PositionScreen.tsx
│   │   │   ├── formulas/
│   │   │   │   ├── FormulaBuilderScreen.tsx
│   │   │   │   ├── FormulaLibraryScreen.tsx
│   │   │   │   └── FormulaBacktestScreen.tsx
│   │   │   ├── market/
│   │   │   │   ├── MarketDataScreen.tsx
│   │   │   │   ├── StockDetailScreen.tsx
│   │   │   │   └── NewsScreen.tsx
│   │   │   ├── settings/
│   │   │   │   ├── SettingsScreen.tsx
│   │   │   │   ├── BrokerSettingsScreen.tsx
│   │   │   │   └── NotificationSettingsScreen.tsx
│   │   │   └── profile/
│   │   │       ├── ProfileScreen.tsx
│   │   │       └── AccountScreen.tsx
│   │   ├── components/                  # Reusable UI components
│   │   │   ├── common/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   ├── trading/
│   │   │   │   ├── OrderForm.tsx
│   │   │   │   ├── PositionCard.tsx
│   │   │   │   ├── PnLChart.tsx
│   │   │   │   └── OrderBook.tsx
│   │   │   ├── market/
│   │   │   │   ├── StockCard.tsx
│   │   │   │   ├── PriceChart.tsx
│   │   │   │   ├── MarketDepth.tsx
│   │   │   │   └── NewsCard.tsx
│   │   │   ├── formulas/
│   │   │   │   ├── FormulaCard.tsx
│   │   │   │   ├── FormulaBuilder.tsx
│   │   │   │   ├── IndicatorSelector.tsx
│   │   │   │   └── BacktestResults.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       ├── TabBar.tsx
│   │   │       ├── Drawer.tsx
│   │   │       └── SafeAreaWrapper.tsx
│   │   ├── services/                    # API clients and integrations
│   │   │   ├── api/
│   │   │   │   ├── client.ts
│   │   │   │   ├── auth.ts
│   │   │   │   ├── trading.ts
│   │   │   │   ├── market.ts
│   │   │   │   └── formulas.ts
│   │   │   ├── brokers/                 # Broker integrations
│   │   │   │   ├── base/
│   │   │   │   │   ├── BrokerInterface.ts
│   │   │   │   │   └── BrokerConfig.ts
│   │   │   │   ├── alpaca/
│   │   │   │   │   ├── AlpacaBroker.ts
│   │   │   │   │   └── AlpacaConfig.ts
│   │   │   │   ├── interactive-brokers/
│   │   │   │   │   ├── IBBroker.ts
│   │   │   │   │   └── IBConfig.ts
│   │   │   │   └── td-ameritrade/
│   │   │   │       ├── TDAmeritradeBroker.ts
│   │   │   │       └── TDConfig.ts
│   │   │   ├── websocket/
│   │   │   │   ├── WebSocketClient.ts
│   │   │   │   ├── MarketDataStream.ts
│   │   │   │   └── OrderUpdatesStream.ts
│   │   │   └── storage/
│   │   │       ├── SecureStorage.ts
│   │   │       ├── AsyncStorage.ts
│   │   │       └── CacheManager.ts
│   │   ├── state/                       # Global state management
│   │   │   ├── context/
│   │   │   │   ├── AuthContext.tsx
│   │   │   │   ├── TradingContext.tsx
│   │   │   │   ├── MarketContext.tsx
│   │   │   │   └── AppContext.tsx
│   │   │   ├── reducers/
│   │   │   │   ├── authReducer.ts
│   │   │   │   ├── tradingReducer.ts
│   │   │   │   └── marketReducer.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useAuth.ts
│   │   │   │   ├── useTrading.ts
│   │   │   │   ├── useMarketData.ts
│   │   │   │   ├── useFormulas.ts
│   │   │   │   └── useWebSocket.ts
│   │   │   └── store/
│   │   │       ├── store.ts
│   │   │       └── middleware.ts
│   │   ├── notifications/               # Push notifications
│   │   │   ├── NotificationService.ts
│   │   │   ├── NotificationHandler.ts
│   │   │   ├── PushTokenManager.ts
│   │   │   └── types.ts
│   │   ├── theme/                       # Design system
│   │   │   ├── colors.ts
│   │   │   ├── typography.ts
│   │   │   ├── spacing.ts
│   │   │   ├── breakpoints.ts
│   │   │   ├── shadows.ts
│   │   │   └── index.ts
│   │   ├── assets/                      # Static assets
│   │   │   ├── images/
│   │   │   │   ├── logos/
│   │   │   │   └── backgrounds/
│   │   │   ├── icons/
│   │   │   │   ├── trading/
│   │   │   │   ├── market/
│   │   │   │   └── common/
│   │   │   └── svgs/
│   │   │       ├── charts/
│   │   │       └── illustrations/
│   │   ├── utilities/                   # Helper functions
│   │   │   ├── formatters/
│   │   │   │   ├── currency.ts
│   │   │   │   ├── date.ts
│   │   │   │   └── number.ts
│   │   │   ├── validators/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── trading.ts
│   │   │   │   └── forms.ts
│   │   │   ├── calculations/
│   │   │   │   ├── pnl.ts
│   │   │   │   ├── risk.ts
│   │   │   │   └── indicators.ts
│   │   │   ├── constants/
│   │   │   │   ├── api.ts
│   │   │   │   ├── trading.ts
│   │   │   │   └── app.ts
│   │   │   └── helpers/
│   │   │       ├── navigation.ts
│   │   │       ├── permissions.ts
│   │   │       └── device.ts
│   │   ├── types/                       # TypeScript type definitions
│   │   │   ├── api.ts
│   │   │   ├── trading.ts
│   │   │   ├── market.ts
│   │   │   ├── auth.ts
│   │   │   └── common.ts
│   │   └── navigation/                  # Navigation configuration
│   │       ├── AppNavigator.tsx
│   │       ├── AuthNavigator.tsx
│   │       ├── TabNavigator.tsx
│   │       └── types.ts
│   ├── android/                         # Android-specific files
│   ├── ios/                             # iOS-specific files
│   ├── __tests__/                       # Test files
│   │   ├── components/
│   │   ├── screens/
│   │   ├── services/
│   │   ├── utils/
│   │   └── __mocks__/
│   ├── docs/                            # Documentation
│   │   ├── api/
│   │   ├── components/
│   │   ├── setup/
│   │   └── deployment/
│   ├── package.json
│   ├── tsconfig.json
│   ├── metro.config.js
│   ├── babel.config.js
│   └── app.json
├── backend/                             # FastAPI Backend
│   ├── app/
│   │   ├── api/                         # API routes
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── trading.py
│   │   │   │   ├── market.py
│   │   │   │   ├── formulas.py
│   │   │   │   ├── users.py
│   │   │   │   └── notifications.py
│   │   │   └── dependencies.py
│   │   ├── models/                      # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── trading.py
│   │   │   ├── market.py
│   │   │   ├── formulas.py
│   │   │   └── notifications.py
│   │   ├── schemas/                     # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── trading.py
│   │   │   ├── market.py
│   │   │   ├── formulas.py
│   │   │   └── common.py
│   │   ├── services/                    # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── trading_service.py
│   │   │   ├── market_service.py
│   │   │   ├── formula_service.py
│   │   │   ├── notification_service.py
│   │   │   └── broker_service.py
│   │   ├── tasks/                       # Scheduled jobs
│   │   │   ├── __init__.py
│   │   │   ├── market_data.py
│   │   │   ├── formula_execution.py
│   │   │   ├── risk_monitoring.py
│   │   │   └── cleanup.py
│   │   ├── auth/                        # Authentication
│   │   │   ├── __init__.py
│   │   │   ├── jwt_handler.py
│   │   │   ├── password_handler.py
│   │   │   ├── oauth_handler.py
│   │   │   └── permissions.py
│   │   ├── config/                      # Configuration
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   ├── database.py
│   │   │   ├── redis.py
│   │   │   └── celery.py
│   │   ├── core/                        # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── exceptions.py
│   │   │   └── middleware.py
│   │   ├── utils/                       # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── formatters.py
│   │   │   ├── validators.py
│   │   │   ├── calculations.py
│   │   │   └── helpers.py
│   │   └── main.py                      # FastAPI app entry point
│   ├── tests/                           # Test files
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── test_models.py
│   │   │   ├── test_services.py
│   │   │   └── test_utils.py
│   │   ├── integration/
│   │   │   ├── test_api.py
│   │   │   └── test_auth.py
│   │   └── e2e/
│   │       └── test_trading_flow.py
│   ├── docs/                            # Documentation
│   │   ├── api/
│   │   ├── deployment/
│   │   ├── development/
│   │   └── architecture/
│   ├── migrations/                      # Database migrations
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── docker-compose.yml
├── shared/                              # Shared code between frontend/backend
│   ├── types/                           # Shared TypeScript types
│   ├── constants/                       # Shared constants
│   └── utils/                           # Shared utility functions
├── infrastructure/                      # Infrastructure as Code
│   ├── terraform/
│   ├── kubernetes/
│   └── docker/
├── scripts/                             # Build and deployment scripts
│   ├── build.sh
│   ├── deploy.sh
│   └── setup.sh
├── .github/                             # GitHub workflows
│   └── workflows/
├── .gitignore
├── README.md
└── docker-compose.yml
```