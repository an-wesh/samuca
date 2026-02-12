from fastapi import APIRouter, Depends, HTTPException
from database import db, get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime, timezone

backtest_router = APIRouter(prefix="/api", tags=["backtest"])

class BacktestRequest(BaseModel):
    strategy_id: Optional[str] = None
    strategy: Optional[Dict[str, Any]] = None
    symbol: str = "BTCUSD"
    timeframe: str = "1h"
    initial_capital: float = 100000
    commission_pct: float = 0.1

@backtest_router.post("/backtest/run")
async def run_backtest_endpoint(req: BacktestRequest, user=Depends(get_current_user)):
    strategy = req.strategy
    if req.strategy_id:
        strat_doc = await db.strategies.find_one({"id": req.strategy_id, "user_id": user["id"]}, {"_id": 0})
        if not strat_doc:
            raise HTTPException(status_code=404, detail="Strategy not found")
        strategy = strat_doc
    if not strategy:
        raise HTTPException(status_code=400, detail="Strategy required")

    collection = db[f"market_data_{req.timeframe}"]
    ohlcv_data = await collection.find({"symbol": req.symbol}, {"_id": 0}).sort("timestamp", 1).to_list(2000)

    if len(ohlcv_data) < 50:
        raise HTTPException(status_code=400, detail="Insufficient market data")

    from utils.engines import run_backtest
    result = run_backtest(ohlcv_data, strategy, req.initial_capital, req.commission_pct)

    backtest_doc = {
        "id": str(uuid.uuid4()), "user_id": user["id"],
        "strategy_name": strategy.get("name", "Unnamed"),
        "symbol": req.symbol, "timeframe": req.timeframe,
        "initial_capital": req.initial_capital,
        "commission_pct": req.commission_pct,
        "metrics": result["metrics"],
        "trades_count": len(result["trades"]),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.backtests.insert_one(backtest_doc)
    result["backtest_id"] = backtest_doc["id"]
    return result

@backtest_router.get("/backtests")
async def list_backtests(user=Depends(get_current_user)):
    return await db.backtests.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
