# AI Trading Bot Builder

Production-grade AI-powered trading bot builder platform with real-time market data, backtesting, and ML capabilities.

## Features
- 📊 Real-time NSE stock data (200+ stocks)
- 🤖 Visual bot builder with technical indicators
- 📈 Institutional-grade backtesting engine
- 🧠 ML Bot Builder with pre-trained templates
- 📰 News & Sentiment analysis
- 👤 Admin terminal for user management

## Tech Stack
- **Frontend**: React 18, TailwindCSS, ShadCN UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Charts**: TradingView Lightweight Charts

## Deployment on Railway

### Quick Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Manual Setup

1. **Fork/Clone this repo to GitHub**

2. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

3. **Create New Project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

4. **Deploy MongoDB**
   - Click "New" → "Database" → "MongoDB"
   - Railway will create a managed MongoDB instance

5. **Deploy Backend**
   - Click "New" → "GitHub Repo" → Select repo
   - Set Root Directory: `backend`
   - Add Environment Variables:
     ```
     MONGO_URL=<copy from MongoDB service>
     DB_NAME=trading_bot_db
     JWT_SECRET=<generate-random-string>
     CORS_ORIGINS=*
     NEWS_API_KEY=your-newsapi-key
     ```

6. **Deploy Frontend**
   - Click "New" → "GitHub Repo" → Select repo
   - Set Root Directory: `frontend`
   - Add Environment Variable:
     ```
     REACT_APP_BACKEND_URL=https://<your-backend>.up.railway.app
     ```

7. **Update CORS**
   - Go to Backend service → Variables
   - Update `CORS_ORIGINS` with your frontend URL

### Pause/Resume
- **Pause**: Project Settings → Remove services (data persists in MongoDB)
- **Resume**: Redeploy from GitHub

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend
cd frontend
yarn install
yarn start
```

## Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=trading_bot_db
JWT_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000
NEWS_API_KEY=your-newsapi-key
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Test Credentials
- Email: admin@test.com
- Password: admin123

## License
MIT
