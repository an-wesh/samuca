import numpy as np
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

SYMBOLS = {
    "BTCUSD": {"base_price": 65000, "volatility": 0.02, "drift": 0.0001},
    "ETHUSD": {"base_price": 3500, "volatility": 0.025, "drift": 0.00008},
    "AAPL": {"base_price": 185, "volatility": 0.012, "drift": 0.00005},
    "TSLA": {"base_price": 245, "volatility": 0.025, "drift": 0.00003},
    "SPY": {"base_price": 520, "volatility": 0.008, "drift": 0.00004},
}

def generate_ohlcv(base_price, volatility, drift, num_candles, interval_minutes):
    np.random.seed(42)
    prices = [base_price]
    data = []
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=interval_minutes * num_candles)

    for i in range(num_candles):
        price = prices[-1]
        regime = np.sin(i / 50) * 0.5
        vol_cluster = 1 + 0.5 * abs(np.sin(i / 30))
        change = np.random.normal(drift + regime * 0.0005, volatility * vol_cluster)
        close = price * (1 + change)
        intra_vol = volatility * 0.7
        high = close * (1 + abs(np.random.normal(0, intra_vol)))
        low = close * (1 - abs(np.random.normal(0, intra_vol)))
        open_price = price * (1 + np.random.normal(0, intra_vol * 0.3))
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        base_volume = 1000 + abs(change) * 50000
        volume_spike = 5.0 if np.random.random() < 0.05 else 1.0
        volume = base_volume * np.random.uniform(0.5, 2.0) * volume_spike
        timestamp = int((start_time + timedelta(minutes=interval_minutes * i)).timestamp())
        data.append({
            "timestamp": timestamp, "open": round(open_price, 2),
            "high": round(high, 2), "low": round(low, 2),
            "close": round(close, 2), "volume": round(volume, 2),
        })
        prices.append(close)
    return data

def aggregate_to_timeframe(data_5m, target_minutes):
    candles_per_bar = target_minutes // 5
    aggregated = []
    for i in range(0, len(data_5m), candles_per_bar):
        chunk = data_5m[i:i + candles_per_bar]
        if not chunk:
            break
        aggregated.append({
            "timestamp": chunk[0]["timestamp"], "open": chunk[0]["open"],
            "high": max(c["high"] for c in chunk), "low": min(c["low"] for c in chunk),
            "close": chunk[-1]["close"], "volume": round(sum(c["volume"] for c in chunk), 2),
        })
    return aggregated

async def generate_market_data(db):
    count = await db.market_data_1h.count_documents({})
    if count > 0:
        logger.info("Market data already exists, skipping generation")
        return
    logger.info("Generating mock market data...")
    for symbol, config in SYMBOLS.items():
        data_5m = generate_ohlcv(config["base_price"], config["volatility"], config["drift"], 8640, 5)
        for d in data_5m:
            d["symbol"] = symbol
        await db.market_data_5m.insert_many(data_5m)

        data_15m = aggregate_to_timeframe(data_5m, 15)
        for d in data_15m:
            d["symbol"] = symbol
        await db.market_data_15m.insert_many(data_15m)

        data_1h = aggregate_to_timeframe(data_5m, 60)
        for d in data_1h:
            d["symbol"] = symbol
        await db.market_data_1h.insert_many(data_1h)

        data_1d = aggregate_to_timeframe(data_5m, 1440)
        for d in data_1d:
            d["symbol"] = symbol
        await db.market_data_1d.insert_many(data_1d)

        logger.info(f"Generated data for {symbol}: {len(data_5m)} 5m, {len(data_1h)} 1h, {len(data_1d)} 1d")
    logger.info("Market data generation complete")
