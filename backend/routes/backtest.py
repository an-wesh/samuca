from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from database import db, get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime, timezone
import logging

backtest_router = APIRouter(prefix="/api", tags=["backtest"])
logger = logging.getLogger(__name__)

class BacktestRequest(BaseModel):
    strategy_id: Optional[str] = None
    strategy: Optional[Dict[str, Any]] = None
    symbol: str = "BTCUSD"
    timeframe: str = "1h"
    initial_capital: float = 100000
    commission_pct: float = 0.1
    slippage_pct: float = 0.05

class BacktestResult(BaseModel):
    backtest_id: str
    status: str
    equity_curve: Optional[List[Dict[str, Any]]] = None
    trades: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@backtest_router.post("/backtest/run")
async def run_backtest_endpoint(req: BacktestRequest, user=Depends(get_current_user)):
    """Run institutional-grade backtest with comprehensive metrics"""
    strategy = req.strategy
    
    # Load strategy from database if ID provided
    if req.strategy_id:
        strat_doc = await db.strategies.find_one({"id": req.strategy_id, "user_id": user["id"]}, {"_id": 0})
        if not strat_doc:
            raise HTTPException(status_code=404, detail="Strategy not found")
        strategy = strat_doc
    
    if not strategy:
        raise HTTPException(status_code=400, detail="Strategy required")

    # Fetch market data
    collection = db[f"market_data_{req.timeframe}"]
    ohlcv_data = await collection.find({"symbol": req.symbol}, {"_id": 0}).sort("timestamp", 1).to_list(2000)

    if len(ohlcv_data) < 100:
        raise HTTPException(status_code=400, detail="Insufficient market data (need at least 100 candles)")

    # Run backtest using institutional engine
    try:
        from utils.backtest_engine import run_backtest
        result = run_backtest(
            ohlcv_data, 
            strategy, 
            req.initial_capital, 
            req.commission_pct,
            req.slippage_pct
        )
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail=f"Backtest execution failed: {str(e)}")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Store backtest result
    backtest_id = str(uuid.uuid4())
    backtest_doc = {
        "id": backtest_id,
        "user_id": user["id"],
        "strategy_name": strategy.get("name", "Unnamed"),
        "strategy_id": req.strategy_id,
        "symbol": req.symbol,
        "timeframe": req.timeframe,
        "initial_capital": req.initial_capital,
        "commission_pct": req.commission_pct,
        "slippage_pct": req.slippage_pct,
        "metrics": result["metrics"],
        "trades_count": len(result["trades"]),
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.backtests.insert_one(backtest_doc)
    
    result["backtest_id"] = backtest_id
    result["status"] = "completed"
    return result

@backtest_router.get("/backtests")
async def list_backtests(user=Depends(get_current_user), limit: int = 50):
    """List user's backtest history"""
    return await db.backtests.find(
        {"user_id": user["id"]}, 
        {"_id": 0}
    ).sort("created_at", -1).to_list(limit)

@backtest_router.get("/backtests/{backtest_id}")
async def get_backtest(backtest_id: str, user=Depends(get_current_user)):
    """Get specific backtest details"""
    bt = await db.backtests.find_one(
        {"id": backtest_id, "user_id": user["id"]},
        {"_id": 0}
    )
    if not bt:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return bt

@backtest_router.delete("/backtests/{backtest_id}")
async def delete_backtest(backtest_id: str, user=Depends(get_current_user)):
    """Delete a backtest"""
    result = await db.backtests.delete_one({"id": backtest_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return {"message": "Backtest deleted"}

@backtest_router.get("/backtest/indicators")
async def get_available_indicators():
    """List all available indicators for strategy building"""
    return {
        "trend": [
            {"id": "SMA", "name": "Simple Moving Average", "params": ["period"], "defaults": {"period": 20}},
            {"id": "EMA", "name": "Exponential Moving Average", "params": ["period"], "defaults": {"period": 20}},
            {"id": "SUPERTREND", "name": "SuperTrend", "params": ["period", "multiplier"], "defaults": {"period": 10, "multiplier": 3}},
            {"id": "ICHIMOKU", "name": "Ichimoku Cloud", "params": ["tenkan", "kijun", "senkou_b"], "defaults": {"tenkan": 9, "kijun": 26, "senkou_b": 52}},
            {"id": "PARABOLIC_SAR", "name": "Parabolic SAR", "params": ["af_start", "af_max"], "defaults": {"af_start": 0.02, "af_max": 0.2}},
            {"id": "ALLIGATOR", "name": "Williams Alligator", "params": ["jaw", "teeth", "lips"], "defaults": {"jaw": 13, "teeth": 8, "lips": 5}},
        ],
        "momentum": [
            {"id": "RSI", "name": "Relative Strength Index", "params": ["period"], "defaults": {"period": 14}},
            {"id": "MACD", "name": "MACD", "params": ["fast", "slow", "signal"], "defaults": {"fast": 12, "slow": 26, "signal": 9}},
            {"id": "STOCHASTIC", "name": "Stochastic Oscillator", "params": ["k_period", "d_period"], "defaults": {"k_period": 14, "d_period": 3}},
            {"id": "CCI", "name": "Commodity Channel Index", "params": ["period"], "defaults": {"period": 20}},
            {"id": "WILLIAMS_R", "name": "Williams %R", "params": ["period"], "defaults": {"period": 14}},
            {"id": "MFI", "name": "Money Flow Index", "params": ["period"], "defaults": {"period": 14}},
            {"id": "AROON", "name": "Aroon Indicator", "params": ["period"], "defaults": {"period": 25}},
        ],
        "volatility": [
            {"id": "BB", "name": "Bollinger Bands", "params": ["period", "std_dev"], "defaults": {"period": 20, "std_dev": 2}},
            {"id": "ATR", "name": "Average True Range", "params": ["period"], "defaults": {"period": 14}},
            {"id": "KELTNER", "name": "Keltner Channels", "params": ["ema_period", "atr_period", "multiplier"], "defaults": {"ema_period": 20, "atr_period": 10, "multiplier": 2}},
            {"id": "DONCHIAN", "name": "Donchian Channels", "params": ["period"], "defaults": {"period": 20}},
        ],
        "volume": [
            {"id": "VWAP", "name": "VWAP", "params": [], "defaults": {}},
            {"id": "OBV", "name": "On Balance Volume", "params": [], "defaults": {}},
            {"id": "CMF", "name": "Chaikin Money Flow", "params": ["period"], "defaults": {"period": 20}},
            {"id": "AD", "name": "Accumulation/Distribution", "params": [], "defaults": {}},
        ],
        "trend_strength": [
            {"id": "ADX", "name": "Average Directional Index", "params": ["period"], "defaults": {"period": 14}},
            {"id": "TRIX", "name": "TRIX", "params": ["period"], "defaults": {"period": 15}},
        ]
    }
