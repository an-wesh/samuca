# AI Trading Bot Builder (TradeForge) - PRD

## Original Problem Statement
Build a production-grade, AI-powered trading bot builder platform with institutional-grade backtesting, strategy deployment, news sentiment analysis, and comprehensive technical indicators (all Zerodha Kite indicators).

## Tech Stack
- **Frontend:** React, TailwindCSS, ShadCN UI, Zustand, TradingView Lightweight Charts, Recharts
- **Backend:** FastAPI, Python, WebSockets
- **Database:** MongoDB
- **AI/LLM:** OpenAI GPT via Emergent LLM Key

## Core Requirements (P0-P5)
- ✅ **P0:** Institutional-grade backtesting engine with 30+ indicators
- ✅ **P1:** Strategy-to-Paper-Trading deployment pipeline
- ✅ **P2:** Advanced Bot Creation UX (templates + visual builder)
- ✅ **P3:** News Feed & Sentiment Engine (AI-powered)
- ⏳ **P4:** Machine Learning Bot Builder (Future)
- ⏳ **P5:** Admin Terminal (Future)

---

## What's Been Implemented

### Phase 1: Foundation (Complete - Previous Session)
- JWT Authentication (signup/login)
- MongoDB integration
- Dashboard with KPIs
- Chart Terminal with TradingView Lightweight Charts
- Mock Market Data with WebSocket streaming
- Basic Paper Trading

### Phase 2: P0-P3 Implementation (Complete - Current Session)

#### P0: Institutional-Grade Backtesting Engine ✅
**Date:** February 17, 2026

**Backend:**
- `/app/backend/utils/indicators.py` - 30+ technical indicators:
  - **Trend:** SMA, EMA, WMA, DEMA, TEMA, SuperTrend, Ichimoku Cloud, Parabolic SAR, Williams Alligator
  - **Momentum:** RSI, MACD, Stochastic, CCI, Williams %R, MFI, Aroon, Ultimate Oscillator, TSI, ROC
  - **Volatility:** Bollinger Bands, ATR, Keltner Channels, Donchian Channels, Historical Volatility
  - **Volume:** VWAP, OBV, Chaikin Money Flow, Accumulation/Distribution, Volume Price Trend
  - **Trend Strength:** ADX, TRIX
  - **Pivot Points:** Standard Pivots, CPR

- `/app/backend/utils/backtest_engine.py` - Candle-by-candle simulation:
  - Realistic slippage modeling
  - Transaction costs (commission)
  - Multiple position management
  - Advanced metrics: Sharpe Ratio, Sortino Ratio, Calmar Ratio, Max Drawdown, Win Rate, Profit Factor, Expectancy, Payoff Ratio, Recovery Factor

- `/app/backend/routes/backtest.py` - Backtest API endpoints:
  - `POST /api/backtest/run` - Run institutional backtest
  - `GET /api/backtests` - List backtest history
  - `GET /api/backtest/indicators` - List available indicators

**Frontend:**
- `/app/frontend/src/pages/BacktestLabPage.js`:
  - Configuration panel (strategy, symbol, capital, fees, slippage)
  - Key metrics cards (Total Return, CAGR, Sharpe, Sortino, Max Drawdown, Win Rate)
  - Equity Curve chart with Recharts
  - Drawdown chart
  - Trade P&L distribution
  - Detailed trade history table
  - Tabs: Overview, Performance, Risk Analysis, Trades

#### P1: Strategy Deployment Pipeline ✅
**Date:** February 17, 2026

**Backend:**
- `/app/backend/routes/deployment.py`:
  - `POST /api/deploy/create` - Deploy strategy to paper trading
  - `GET /api/deploy/list` - List all deployments
  - `GET /api/deploy/{id}` - Get deployment details
  - `POST /api/deploy/{id}/start` - Resume deployment
  - `POST /api/deploy/{id}/pause` - Pause deployment
  - `POST /api/deploy/{id}/stop` - Stop and close positions
  - `GET /api/deploy/{id}/signals` - Check current signals
  - `POST /api/deploy/{id}/execute` - Manual trade execution
  - `GET /api/deploy/{id}/trades` - Trade history

**Frontend:**
- `/app/frontend/src/pages/DeploymentsPage.js`:
  - Deployment list with status badges
  - Create deployment modal
  - Deployment controls (Start/Pause/Stop/Delete)
  - Stats cards (Capital, P&L, Win Rate, Trades)
  - Current position panel
  - Signal checking panel
  - Trade history table

#### P2: Advanced Bot Creation UX ✅
**Date:** February 17, 2026

**Frontend:**
- `/app/frontend/src/pages/BotBuilderPage.js`:
  - Mode switcher: Templates / Visual Builder
  - 5 Pre-built strategy templates:
    - RSI Mean Reversion
    - MACD Momentum
    - SuperTrend Follower
    - Bollinger Squeeze
    - Multi-Indicator Confirm
  - Indicator palette with categories:
    - Trend (SMA, EMA, SuperTrend, Ichimoku, PSAR, Alligator)
    - Momentum (RSI, MACD, Stochastic, CCI, Williams %R, MFI, Aroon)
    - Volatility (Bollinger Bands, Keltner, Donchian, ATR)
    - Volume (VWAP, OBV, CMF, Volume MA)
    - Trend Strength (ADX, TRIX)
  - Entry/Exit condition builder with AND/OR logic
  - Risk Management panel (Stop Loss, Take Profit, Position Size sliders)

#### P3: News Feed & Sentiment Engine ✅
**Date:** February 17, 2026

**Backend:**
- `/app/backend/routes/news.py`:
  - `GET /api/news/feed` - Get news feed (all symbols)
  - `GET /api/news/feed/{symbol}` - Get symbol-specific news
  - `POST /api/news/analyze` - AI sentiment analysis
  - `GET /api/news/sentiment/history` - Sentiment history
  - `GET /api/news/sentiment/aggregate/{symbol}` - Aggregated sentiment

**Features:**
- Mock news headlines for BTCUSD, ETHUSD, AAPL, TSLA, SPY
- AI sentiment analysis using OpenAI GPT (via Emergent LLM Key)
- Keyword-based fallback when LLM unavailable
- Sentiment scores: -1 (Strong Bearish) to +1 (Strong Bullish)
- Key factors extraction
- Confidence percentage

**Frontend:**
- `/app/frontend/src/pages/NewsSentimentPage.js`:
  - Symbol sentiment overview with gauges
  - News feed with source and timestamp
  - Individual headline analysis
  - Custom headline analyzer (textarea)
  - Results panel with aggregate metrics
  - Bullish/Neutral/Bearish counts

---

## Architecture

```
/app
├── backend/
│   ├── .env                    # Environment config
│   ├── requirements.txt        # Python dependencies
│   ├── database.py            # MongoDB connection
│   ├── server.py              # FastAPI app, routes
│   ├── routes/
│   │   ├── ai_services.py     # AI bot generation (stub)
│   │   ├── backtest.py        # Backtest endpoints
│   │   ├── bots.py            # Bot CRUD
│   │   ├── deployment.py      # Strategy deployment
│   │   ├── market.py          # Market data + WebSocket
│   │   ├── news.py            # News & Sentiment
│   │   └── paper_trading.py   # Paper trading
│   └── utils/
│       ├── backtest_engine.py # Institutional backtest
│       ├── engines.py         # Legacy (basic indicators)
│       ├── indicators.py      # 30+ technical indicators
│       └── market_generator.py # Mock data generator
└── frontend/
    ├── package.json
    └── src/
        ├── App.js              # Router + Auth
        ├── index.css           # Global styles
        ├── components/
        │   ├── layout/
        │   │   ├── AppLayout.js
        │   │   └── Sidebar.js
        │   └── ui/             # ShadCN components
        ├── lib/
        │   ├── api.js          # Axios instance
        │   └── store.js        # Zustand state
        └── pages/
            ├── BacktestLabPage.js
            ├── BotBuilderPage.js
            ├── BotManagementPage.js
            ├── ChartTerminalPage.js
            ├── DashboardPage.js
            ├── DeploymentsPage.js
            ├── LoginPage.js
            ├── NewsSentimentPage.js
            └── PaperTradingPage.js
```

---

## Database Schema

### Collections:
- `users` - User accounts
- `strategies` - Saved trading strategies
- `backtests` - Backtest history
- `deployments` - Active deployments
- `deployment_trades` - Deployment trade records
- `sentiment_analysis` - Sentiment history
- `market_data_{timeframe}` - OHLCV data

---

## API Endpoints

### Authentication
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Strategies
- `GET /api/strategies`
- `POST /api/strategies`
- `DELETE /api/strategies/{id}`

### Backtesting
- `POST /api/backtest/run`
- `GET /api/backtests`
- `GET /api/backtests/{id}`
- `GET /api/backtest/indicators`

### Deployments
- `POST /api/deploy/create`
- `GET /api/deploy/list`
- `GET /api/deploy/{id}`
- `POST /api/deploy/{id}/start`
- `POST /api/deploy/{id}/pause`
- `POST /api/deploy/{id}/stop`
- `GET /api/deploy/{id}/signals`
- `POST /api/deploy/{id}/execute`

### News & Sentiment
- `GET /api/news/feed`
- `GET /api/news/feed/{symbol}`
- `POST /api/news/analyze`
- `GET /api/news/sentiment/aggregate/{symbol}`

### Market Data
- `GET /api/market/ohlcv`
- `GET /api/market/latest_prices`
- `WS /ws/market`

---

## Remaining Work (Backlog)

### P4: Machine Learning Bot Builder
- AutoML mode for beginners
- Guided mode with model selection
- Advanced mode for custom models
- XGBoost/LSTM integration
- Feature engineering pipeline
- Model training dashboard
- Inference endpoints

### P5: Admin Terminal
- User management (CRUD)
- Virtual capital allocation
- Platform activity monitoring
- Risk controls enforcement
- RBAC middleware
- Admin-only routes

### Future Enhancements
- Real news API integration (replace mocks)
- Live trading integration (exchange APIs)
- Strategy marketplace
- Social trading features
- Advanced charting (candlestick patterns)
- Multi-asset portfolio optimization
- Backtesting with multiple instruments
- Walk-forward optimization

---

## Test Credentials
- Email: `backtest@test.com`
- Password: `Test123!`

## Known Limitations
- News data is MOCKED (static headlines)
- AI Sentiment falls back to keyword analysis when LLM budget exceeded
- Market data is simulated (mock OHLCV generator)
- Paper trading only (no live exchange integration)

---

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial MVP tests
- `/app/test_reports/iteration_2.json` - P0-P3 feature tests (100% pass rate)
