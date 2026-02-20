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

## User Personas
- **Retail Traders**: Individual investors looking to automate trading strategies
- **Platform Admins**: Administrators managing users, capital, and platform operations

## Core Features Implemented

### P0 - Backtesting Engine ✅
- Candle-by-candle institutional-grade simulation
- Extensive technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Advanced performance metrics (Sharpe, Sortino, Max Drawdown, etc.)
- Rich UI visualizations

### P1 - Deployment Pipeline ✅
- Backend service for strategy deployment
- Frontend page for managing deployments
- Paper trading environment integration

### P2 - Bot Builder ✅
- Visual strategy builder with drag-and-drop
- Pre-built templates
- Technical indicator support
- Strategy validation

### P3 - News & Sentiment ✅
- NewsAPI integration for real news feeds
- AI sentiment analysis (keyword-based fallback when DeepSeek budget exhausted)
- Symbol and sector news feeds
- Sentiment aggregation

### P4 - ML Bot Builder ✅
- 5 pre-built ML templates:
  - Trend Direction Classifier
  - Volatility Predictor
  - Momentum Score Predictor
  - Reversal Pattern Detector
  - Breakout Probability Predictor
- 30+ ML features available
- AutoML, Guided, and Advanced modes
- Model training and evaluation pipeline

### P5 - Admin Terminal ✅
- User management (search, filter, role management)
- Capital allocation
- Platform monitoring (activity stats, deployments)
- Emergency stop functionality

### Market Data ✅
- 200+ NSE stocks via yfinance
- US stocks and Crypto symbols
- Real-time price updates
- 30-day historical data
- WebSocket for live updates

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
- Zustand state management

## API Endpoints

### Authentication
- POST /api/auth/signup
- POST /api/auth/login

### Market Data
- GET /api/market/symbols (200+ symbols)
- GET /api/market/price/{symbol}
- GET /api/market/ohlcv
- GET /api/market/latest_prices
- GET /api/market/nifty50
- GET /api/market/sector/{sector}
- WS /api/market/ws/prices

### Bots & Trading
- POST /api/bots
- GET /api/bots
- POST /api/backtest/run
- GET /api/paper-trading/account

### ML Bot Builder
- GET /api/ml/templates
- GET /api/ml/features
- POST /api/ml/train
- GET /api/ml/models

### News & Sentiment
- GET /api/news/feed
- POST /api/news/analyze
- GET /api/news/trending

### Admin
- GET /api/admin/dashboard
- GET /api/admin/users
- PUT /api/admin/users/{user_id}
- GET /api/admin/monitoring/activity

## Database Collections
- users: User accounts with roles
- bots: Trading bot configurations
- deployments: Live deployments
- market_data_{timeframe}: OHLCV data
- sentiment_analysis: Sentiment results
- ml_models: Trained ML models

## Third-Party Integrations
- yfinance: Real market data
- NewsAPI: Financial news (key: provided)
- DeepSeek: AI sentiment (insufficient balance - using keyword fallback)

## Test Credentials
- Email: admin@test.com
- Password: admin123
- Role: admin

## Known Limitations
1. DeepSeek API has insufficient balance - sentiment analysis uses keyword-based fallback
2. Live exchange trading is explicitly out of scope
3. NewsAPI free tier has rate limits

## Future Enhancements (Backlog)
- [ ] More ML model types (LSTM, Transformer)
- [ ] Strategy marketplace
- [ ] Social trading features
- [ ] Mobile app
- [ ] Advanced risk management tools
- [ ] Multi-asset portfolio optimization

## Session Summary - February 20, 2026
- Integrated P4 (ML Bot Builder) and P5 (Admin Terminal)
- Added DeepSeek API integration (falls back to keyword analysis)
- Fixed ObjectId serialization issue in market data
- Verified all 18 backend endpoints working
- All frontend pages loading correctly
- Testing: 100% backend pass rate, 100% frontend pass rate
