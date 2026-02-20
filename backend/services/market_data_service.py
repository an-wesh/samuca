"""
Real-time Market Data Service
Fetches live prices from Yahoo Finance for NSE stocks
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool for blocking yfinance calls
executor = ThreadPoolExecutor(max_workers=10)


def fetch_ticker_data(symbol: str, period: str = "30d", interval: str = "1h") -> Optional[pd.DataFrame]:
    """Fetch historical data for a single ticker"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return None
        df.reset_index(inplace=True)
        df.columns = [c.lower() for c in df.columns]
        if 'datetime' in df.columns:
            df.rename(columns={'datetime': 'timestamp'}, inplace=True)
        elif 'date' in df.columns:
            df.rename(columns={'date': 'timestamp'}, inplace=True)
        return df
    except Exception as e:
        logger.warning(f"Failed to fetch data for {symbol}: {e}")
        return None


def fetch_current_price(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch current price for a ticker"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        
        current_price = info.get('lastPrice') or info.get('regularMarketPrice', 0)
        prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose', current_price)
        
        if current_price == 0:
            # Fallback to history
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Open'].iloc[0]
        
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close > 0 else 0
        
        return {
            "price": round(current_price, 2),
            "prev_close": round(prev_close, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.warning(f"Failed to fetch price for {symbol}: {e}")
        return None


async def async_fetch_ticker_data(symbol: str, period: str = "30d", interval: str = "1h") -> Optional[pd.DataFrame]:
    """Async wrapper for ticker data fetch"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, fetch_ticker_data, symbol, period, interval)


async def async_fetch_current_price(symbol: str) -> Optional[Dict[str, Any]]:
    """Async wrapper for current price fetch"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, fetch_current_price, symbol)


async def fetch_multiple_prices(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch prices for multiple symbols concurrently"""
    tasks = [async_fetch_current_price(sym) for sym in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    prices = {}
    for sym, result in zip(symbols, results):
        if isinstance(result, dict):
            prices[sym] = result
        else:
            prices[sym] = {"price": 0, "change_pct": 0, "error": str(result)}
    
    return prices


def generate_mock_ohlcv(symbol: str, days: int = 30, interval_hours: int = 1) -> List[Dict[str, Any]]:
    """Generate mock OHLCV data when real data unavailable"""
    base_prices = {
        "RELIANCE.NS": 2500, "TCS.NS": 3800, "HDFCBANK.NS": 1600, "INFY.NS": 1800,
        "ICICIBANK.NS": 1100, "HINDUNILVR.NS": 2400, "SBIN.NS": 800, "BHARTIARTL.NS": 1500,
        "BTCUSD": 95000, "ETHUSD": 3200, "AAPL": 180, "TSLA": 250, "SPY": 500
    }
    
    base_price = base_prices.get(symbol, 1000)
    volatility = 0.02
    
    data = []
    current_time = datetime.now(timezone.utc) - timedelta(days=days)
    current_price = base_price
    
    total_candles = days * 24 // interval_hours
    
    for i in range(total_candles):
        # Random walk
        change = np.random.randn() * volatility * current_price
        open_price = current_price
        close_price = current_price + change
        high_price = max(open_price, close_price) * (1 + abs(np.random.randn()) * 0.005)
        low_price = min(open_price, close_price) * (1 - abs(np.random.randn()) * 0.005)
        volume = int(np.random.uniform(100000, 1000000))
        
        data.append({
            "timestamp": int(current_time.timestamp()),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume,
            "symbol": symbol
        })
        
        current_price = close_price
        current_time += timedelta(hours=interval_hours)
    
    return data


async def load_historical_data(db, symbol: str, timeframe: str = "1h", force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Load historical data into database"""
    collection = db[f"market_data_{timeframe}"]
    
    # Check if data exists and is recent
    if not force_refresh:
        latest = await collection.find_one(
            {"symbol": symbol},
            sort=[("timestamp", -1)]
        )
        if latest:
            latest_time = datetime.fromtimestamp(latest["timestamp"], tz=timezone.utc)
            if datetime.now(timezone.utc) - latest_time < timedelta(hours=1):
                # Data is fresh enough
                return await collection.find({"symbol": symbol}, {"_id": 0}).sort("timestamp", 1).to_list(2000)
    
    # Fetch fresh data
    period = "30d"
    interval = "1h" if timeframe in ["1h", "1H"] else "1d" if timeframe in ["1d", "1D"] else "15m"
    
    df = await async_fetch_ticker_data(symbol, period, interval)
    
    if df is not None and not df.empty:
        # Clear old data
        await collection.delete_many({"symbol": symbol})
        
        # Insert new data
        records = []
        for _, row in df.iterrows():
            ts = row['timestamp']
            if hasattr(ts, 'timestamp'):
                ts_val = int(ts.timestamp())
            else:
                ts_val = int(pd.Timestamp(ts).timestamp())
            
            records.append({
                "timestamp": ts_val,
                "open": round(float(row.get('open', 0)), 2),
                "high": round(float(row.get('high', 0)), 2),
                "low": round(float(row.get('low', 0)), 2),
                "close": round(float(row.get('close', 0)), 2),
                "volume": int(row.get('volume', 0)),
                "symbol": symbol
            })
        
        if records:
            await collection.insert_many(records)
            logger.info(f"Loaded {len(records)} candles for {symbol}")
            # Return data without _id field
            return await collection.find({"symbol": symbol}, {"_id": 0}).sort("timestamp", 1).to_list(2000)
    
    # Fallback to mock data
    logger.warning(f"Using mock data for {symbol}")
    mock_data = generate_mock_ohlcv(symbol, days=30)
    await collection.delete_many({"symbol": symbol})
    await collection.insert_many(mock_data)
    # Return data without _id field
    return await collection.find({"symbol": symbol}, {"_id": 0}).sort("timestamp", 1).to_list(2000)


async def refresh_all_prices(db, symbols: List[str]) -> Dict[str, Any]:
    """Refresh prices for all symbols and store in DB"""
    prices = await fetch_multiple_prices(symbols)
    
    # Store in database
    for symbol, price_data in prices.items():
        if "error" not in price_data:
            await db.latest_prices.update_one(
                {"symbol": symbol},
                {"$set": {**price_data, "symbol": symbol}},
                upsert=True
            )
    
    return prices
