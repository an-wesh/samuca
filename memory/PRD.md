# AI Trading Bot Builder (TradeForge) - PRD

## Original Problem Statement
Build a production-grade MVP web platform that allows users to create, test, and deploy AI-powered trading bots using a no-code/low-code interface. Features: JWT Auth, Dashboard, Visual Strategy Builder, Chart Terminal, Backtesting Engine, Paper Trading Simulator, Bot Management, Sentiment Analysis (GPT), Fundamentals, Risk Management.

## Architecture
- **Frontend**: React + TailwindCSS + ShadCN UI + Zustand + TradingView Lightweight Charts v5
- **Backend**: FastAPI (Python) with modular route structure
- **Database**: MongoDB (users, bots, strategies, backtests, paper_portfolios, paper_orders, sentiment_data, market_data collections)
- **AI**: OpenAI GPT via Emergent LLM key for sentiment analysis

## User Personas
1. **Beginner Trader** - Uses templates, guided bot creation, educational tooltips
2. **Intermediate Trader** - Combines indicators + patterns, runs backtests
3. **Advanced Trader** - Optimizes risk & execution, ML predictions

## Core Requirements (Static)
- JWT authentication with signup/login
- Real-time candlestick charting with indicator overlays
- Visual no-code strategy builder with configurable blocks
- Backtesting engine with equity curves and performance metrics
- Paper trading simulator with portfolio tracking
- Bot management (CRUD, start/stop/clone)
- AI-driven sentiment analysis
- Risk management (stop loss, take profit, position sizing)

## What's Been Implemented (Feb 2026)

### Backend (11 files)
- `database.py` - MongoDB + JWT auth helper
- `server.py` - FastAPI app, auth routes, CORS, startup
- `routes/market.py` - OHLCV data, WebSocket streaming, latest prices
- `routes/bots.py` - Bot + Strategy CRUD (create, list, update, delete, start/stop/clone)
- `routes/backtest.py` - Backtesting endpoint with full metrics
- `routes/paper_trading.py` - Order placement, portfolio, positions, history, reset
- `routes/ai_services.py` - Sentiment analysis (GPT), fundamentals (mock), indicators
- `utils/market_generator.py` - Mock OHLCV generation (5 symbols, 4 timeframes)
- `utils/engines.py` - Indicator engine (SMA, EMA, RSI, MACD, BB, ATR) + backtest engine

### Frontend (14 files)
- Login/Signup page with password strength
- Dashboard with KPI cards, market overview, active bots, recent trades
- Strategy Builder with visual block palette, entry/exit conditions, risk management
- Chart Terminal with TradingView Lightweight Charts, WebSocket live data, indicator toggles
- Backtest Lab with equity curves, metrics grid, trade list
- Paper Trading terminal with order form, positions, order history
- Bot Management with create/start/stop/clone/delete
- Sidebar navigation + AppLayout

### API Endpoints
- Auth: POST /api/auth/signup, POST /api/auth/login, GET /api/auth/me
- Market: GET /api/market/symbols, GET /api/market/ohlcv, GET /api/market/latest_prices, WS /api/market/ws/{symbol}
- Bots: GET/POST /api/bots, PUT/DELETE /api/bots/{id}, POST /api/bots/{id}/start|stop|clone
- Strategies: GET/POST /api/strategies, PUT/DELETE /api/strategies/{id}, POST /api/strategies/compile
- Backtest: POST /api/backtest/run, GET /api/backtests
- Paper: GET /api/paper/portfolio, POST /api/paper/order, GET /api/paper/orders|positions, POST /api/paper/reset
- AI: POST /api/sentiment/analyze, GET /api/sentiment/latest, GET /api/fundamentals/{symbol}, GET /api/indicators/{symbol}

## Testing Results
- Backend: 95.5% pass rate (21/22)
- Frontend: 90% (all core functionality working)
- Backtest numpy serialization bug: FIXED

## Prioritized Backlog

### P0 (Critical)
- [x] Auth system
- [x] Dashboard
- [x] Chart Terminal
- [x] Strategy Builder
- [x] Backtest Engine
- [x] Paper Trading
- [x] Bot Management

### P1 (Important - Next Phase)
- [ ] Chart pattern detection engine (Double Top/Bottom, Head & Shoulders, Triangles)
- [ ] Sentiment panel UI (gauge meter, news feed)
- [ ] Fundamental analysis panel UI
- [ ] Strategy templates for beginners
- [ ] Trailing stop loss implementation
- [ ] Bot execution simulator (auto paper trading based on strategy signals)

### P2 (Enhancement)
- [ ] Multi-timeframe strategy conditions
- [ ] SuperTrend indicator
- [ ] WebSocket for portfolio live updates
- [ ] Backtest comparison view
- [ ] Strategy optimization (parameter sweep)
- [ ] Export trade history to CSV
- [ ] Real market data integration (Alpha Vantage, exchange APIs)
- [ ] Admin dashboard

## Next Tasks
1. Build Sentiment Panel UI with gauge meter and news feed
2. Add chart pattern detection (rule-based)
3. Implement strategy templates for beginner users
4. Add bot auto-execution (paper trading mode)
5. Real-time P&L ticker via WebSocket
