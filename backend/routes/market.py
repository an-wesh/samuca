from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from database import db
import asyncio
import random
from datetime import datetime, timezone

market_router = APIRouter(prefix="/api/market", tags=["market"])

SYMBOLS = ["BTCUSD", "ETHUSD", "AAPL", "TSLA", "SPY"]
TIMEFRAMES = ["5m", "15m", "1h", "1d"]

@market_router.get("/symbols")
async def get_symbols():
    return {"symbols": SYMBOLS, "timeframes": TIMEFRAMES}

@market_router.get("/ohlcv")
async def get_ohlcv(
    symbol: str = "BTCUSD",
    timeframe: str = "1h",
    limit: int = Query(default=500, le=2000)
):
    collection = db[f"market_data_{timeframe}"]
    cursor = collection.find({"symbol": symbol}, {"_id": 0}).sort("timestamp", 1).limit(limit)
    return await cursor.to_list(limit)

@market_router.get("/latest_prices")
async def get_latest_prices():
    prices = {}
    for symbol in SYMBOLS:
        doc = await db.market_data_1h.find_one({"symbol": symbol}, {"_id": 0}, sort=[("timestamp", -1)])
        if doc:
            # Get previous candle for change calc
            prev = await db.market_data_1h.find({"symbol": symbol}, {"_id": 0}).sort("timestamp", -1).skip(1).limit(1).to_list(1)
            prev_close = prev[0]["close"] if prev else doc["open"]
            prices[symbol] = {
                "price": doc["close"],
                "open": doc["open"],
                "high": doc["high"],
                "low": doc["low"],
                "volume": doc["volume"],
                "change": round(doc["close"] - prev_close, 2),
                "change_pct": round((doc["close"] - prev_close) / prev_close * 100, 2) if prev_close else 0,
            }
    return prices

@market_router.websocket("/ws/{symbol}")
async def market_websocket(websocket: WebSocket, symbol: str):
    await websocket.accept()
    try:
        last_doc = await db.market_data_1h.find_one({"symbol": symbol}, {"_id": 0}, sort=[("timestamp", -1)])
        if not last_doc:
            await websocket.close()
            return
        price = last_doc["close"]
        while True:
            change_pct = random.gauss(0, 0.002)
            price *= (1 + change_pct)
            high = price * (1 + abs(random.gauss(0, 0.001)))
            low = price * (1 - abs(random.gauss(0, 0.001)))
            tick = {
                "symbol": symbol,
                "timestamp": int(datetime.now(timezone.utc).timestamp()),
                "open": round(price * (1 - change_pct / 2), 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(price, 2),
                "volume": round(random.uniform(100, 10000), 2),
            }
            await websocket.send_json(tick)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
