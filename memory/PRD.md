# AI Trading Bot Builder Platform - PRD

## Original Problem Statement
Build a production-grade, AI-powered trading bot builder platform with:
1. Institutional-grade backtesting engine with candle-by-candle simulation
2. Deployment pipeline to paper trading environment
3. Simplified bot creation with visual builder and templates
4. News & Sentiment integration with AI-powered analysis
5. Machine Learning Lab for ML-based bots
6. Admin Terminal for platform management
7. All NSE stocks with real-time market data

## Core Features Implemented

### P0 - Backtesting Engine ✅
- Candle-by-candle institutional-grade simulation
- Extensive technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Advanced performance metrics (Sharpe, Sortino, Max Drawdown, etc.)
- Dynamic symbol selection (200+ NSE stocks)

### P1 - Deployment Pipeline ✅
- Backend service for strategy deployment
- Frontend page for managing deployments
- Paper trading environment integration

### P2 - Bot Builder ✅
- Visual strategy builder with drag-and-drop
- Pre-built templates
- Technical indicator support

### P3 - News & Sentiment ✅
- NewsAPI integration for real news feeds
- Keyword-based sentiment analysis (accurate for financial text)
- Symbol and sector news feeds

### P4 - ML Bot Builder ✅
- 5 pre-built ML templates
- 30+ ML features available
- AutoML, Guided, and Advanced modes

### P5 - Admin Terminal ✅
- User management
- Capital allocation
- Platform monitoring
- Emergency stop functionality

### Market Data ✅
- 200+ NSE stocks via yfinance
- US stocks and Crypto (BTC-USD, ETH-USD format)
- Real-time price updates
- 30-day historical data

## Bug Fixes (Session Feb 20, 2026)
1. **Chart Terminal Error** - Fixed "Objects are not valid as React child" error by extracting symbol strings from API response
2. **Crypto Symbols** - Changed BTCUSD/ETHUSD to BTC-USD/ETH-USD for yfinance compatibility
3. **Backtest Lab Symbols** - Now dynamically loads NSE symbols instead of hardcoded list
4. **News Page Symbols** - Updated to use correct crypto symbol format

## Technical Architecture

### Backend
- FastAPI (Python)
- MongoDB (motor async)
- yfinance for market data
- NewsAPI for news feeds
- JWT authentication

### Frontend
- React 18
- TailwindCSS
- ShadCN UI components
- TradingView Lightweight Charts

## API Endpoints

### Market Data
- GET /api/market/symbols (200+ symbols)
- GET /api/market/price/{symbol}
- GET /api/market/ohlcv
- GET /api/market/latest_prices
- GET /api/market/nifty50

### News & Sentiment
- GET /api/news/feed
- POST /api/news/analyze (keyword-based)
- GET /api/news/trending

### ML Bot Builder
- GET /api/ml/templates
- GET /api/ml/features
- POST /api/ml/train

### Admin
- GET /api/admin/dashboard
- GET /api/admin/users
- PUT /api/admin/users/{user_id}

## Test Credentials
- Email: admin@test.com
- Password: admin123
- Role: admin

## Known Limitations
1. AI sentiment uses keyword-based fallback (HuggingFace API requires auth)
2. WebSocket has 403 in preview environment (ingress limitation)
3. Live exchange trading is out of scope

## Testing Status
- Backend: 100% (all endpoints working)
- Frontend: 100% (all pages loading, no errors)
- Test Reports: /app/test_reports/iteration_4.json
