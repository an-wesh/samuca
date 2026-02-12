from fastapi import APIRouter, Depends, HTTPException
from database import db, get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime, timezone

bots_router = APIRouter(prefix="/api", tags=["bots"])

class BotCreate(BaseModel):
    name: str
    symbol: str
    timeframe: str = "1h"
    strategy_id: Optional[str] = None
    risk_settings: Optional[Dict] = None

class StrategyCreate(BaseModel):
    name: str
    symbol: str = "BTCUSD"
    timeframe: str = "1h"
    entry: Dict[str, Any] = {}
    exit: Dict[str, Any] = {}
    risk: Optional[Dict[str, Any]] = None

@bots_router.get("/bots")
async def list_bots(user=Depends(get_current_user)):
    return await db.bots.find({"user_id": user["id"]}, {"_id": 0}).to_list(100)

@bots_router.post("/bots")
async def create_bot(req: BotCreate, user=Depends(get_current_user)):
    bot = {
        "id": str(uuid.uuid4()), "user_id": user["id"], "name": req.name,
        "symbol": req.symbol, "timeframe": req.timeframe,
        "strategy_id": req.strategy_id,
        "risk_settings": req.risk_settings or {
            "stop_loss_pct": 2.0, "take_profit_pct": 5.0,
            "max_position_size_pct": 10.0, "max_capital_per_trade": 5000,
            "max_daily_loss": 1000, "max_concurrent_trades": 3,
        },
        "status": "stopped", "pnl": 0.0, "win_rate": 0.0,
        "total_trades": 0, "winning_trades": 0, "capital_allocated": 10000,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.bots.insert_one(bot)
    return {k: v for k, v in bot.items() if k != "_id"}

@bots_router.put("/bots/{bot_id}")
async def update_bot(bot_id: str, req: BotCreate, user=Depends(get_current_user)):
    result = await db.bots.update_one(
        {"id": bot_id, "user_id": user["id"]},
        {"$set": {"name": req.name, "symbol": req.symbol, "timeframe": req.timeframe,
                  "strategy_id": req.strategy_id, "risk_settings": req.risk_settings,
                  "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Bot not found")
    return await db.bots.find_one({"id": bot_id}, {"_id": 0})

@bots_router.delete("/bots/{bot_id}")
async def delete_bot(bot_id: str, user=Depends(get_current_user)):
    result = await db.bots.delete_one({"id": bot_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"status": "deleted"}

@bots_router.post("/bots/{bot_id}/start")
async def start_bot(bot_id: str, user=Depends(get_current_user)):
    result = await db.bots.update_one(
        {"id": bot_id, "user_id": user["id"]},
        {"$set": {"status": "running", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"status": "running"}

@bots_router.post("/bots/{bot_id}/stop")
async def stop_bot(bot_id: str, user=Depends(get_current_user)):
    result = await db.bots.update_one(
        {"id": bot_id, "user_id": user["id"]},
        {"$set": {"status": "stopped", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"status": "stopped"}

@bots_router.post("/bots/{bot_id}/clone")
async def clone_bot(bot_id: str, user=Depends(get_current_user)):
    bot = await db.bots.find_one({"id": bot_id, "user_id": user["id"]}, {"_id": 0})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    new_bot = {**bot, "id": str(uuid.uuid4()), "name": f"{bot['name']} (Copy)",
               "status": "stopped", "pnl": 0.0, "total_trades": 0, "winning_trades": 0,
               "created_at": datetime.now(timezone.utc).isoformat()}
    await db.bots.insert_one(new_bot)
    return {k: v for k, v in new_bot.items() if k != "_id"}

@bots_router.get("/strategies")
async def list_strategies(user=Depends(get_current_user)):
    return await db.strategies.find({"user_id": user["id"]}, {"_id": 0}).to_list(100)

@bots_router.post("/strategies")
async def create_strategy(req: StrategyCreate, user=Depends(get_current_user)):
    strategy = {
        "id": str(uuid.uuid4()), "user_id": user["id"], "name": req.name,
        "symbol": req.symbol, "timeframe": req.timeframe,
        "entry": req.entry, "exit": req.exit, "risk": req.risk or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.strategies.insert_one(strategy)
    return {k: v for k, v in strategy.items() if k != "_id"}

@bots_router.put("/strategies/{strategy_id}")
async def update_strategy(strategy_id: str, req: StrategyCreate, user=Depends(get_current_user)):
    result = await db.strategies.update_one(
        {"id": strategy_id, "user_id": user["id"]},
        {"$set": {"name": req.name, "symbol": req.symbol, "timeframe": req.timeframe,
                  "entry": req.entry, "exit": req.exit, "risk": req.risk,
                  "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return await db.strategies.find_one({"id": strategy_id}, {"_id": 0})

@bots_router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: str, user=Depends(get_current_user)):
    result = await db.strategies.delete_one({"id": strategy_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"status": "deleted"}

@bots_router.post("/strategies/compile")
async def compile_strategy(req: StrategyCreate):
    errors = []
    if not req.entry or not req.entry.get("conditions"):
        errors.append("Entry conditions are required")
    if not req.exit or not req.exit.get("conditions"):
        errors.append("Exit conditions are required")
    if errors:
        return {"valid": False, "errors": errors}
    return {"valid": True, "summary": {
        "entry_conditions": len(req.entry.get("conditions", [])),
        "exit_conditions": len(req.exit.get("conditions", [])),
        "has_risk_management": bool(req.risk), "symbol": req.symbol, "timeframe": req.timeframe,
    }}
