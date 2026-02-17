"""
Deployment Management Service
Handles deploying strategies to paper trading and live execution
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from database import db, get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime, timezone
import logging
import asyncio

deploy_router = APIRouter(prefix="/api/deploy", tags=["deployment"])
logger = logging.getLogger(__name__)

# In-memory store for active deployments (in production, use Redis)
active_deployments = {}

class DeploymentRequest(BaseModel):
    strategy_id: str
    symbol: str
    timeframe: str = "1h"
    initial_capital: float = 10000
    max_position_size_pct: float = 10
    mode: str = "paper"  # paper or live
    auto_trade: bool = True

class DeploymentUpdate(BaseModel):
    status: Optional[str] = None
    auto_trade: Optional[bool] = None
    max_position_size_pct: Optional[float] = None

@deploy_router.post("/create")
async def create_deployment(req: DeploymentRequest, user=Depends(get_current_user)):
    """Deploy a strategy for paper trading"""
    
    # Validate strategy exists
    strategy = await db.strategies.find_one({"id": req.strategy_id, "user_id": user["id"]}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Check for existing active deployment with same strategy
    existing = await db.deployments.find_one({
        "user_id": user["id"],
        "strategy_id": req.strategy_id,
        "status": {"$in": ["active", "paused"]}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Strategy already deployed. Stop existing deployment first.")
    
    deployment_id = str(uuid.uuid4())
    deployment = {
        "id": deployment_id,
        "user_id": user["id"],
        "strategy_id": req.strategy_id,
        "strategy_name": strategy.get("name", "Unnamed"),
        "symbol": req.symbol,
        "timeframe": req.timeframe,
        "mode": req.mode,
        "initial_capital": req.initial_capital,
        "current_capital": req.initial_capital,
        "max_position_size_pct": req.max_position_size_pct,
        "auto_trade": req.auto_trade,
        "status": "active",
        "position": None,
        "total_trades": 0,
        "total_pnl": 0,
        "win_rate": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_signal_at": None,
        "last_trade_at": None,
        "entry_conditions": strategy.get("entry", {}),
        "exit_conditions": strategy.get("exit", {}),
        "risk_settings": strategy.get("risk", {})
    }
    
    await db.deployments.insert_one(deployment)
    
    # Start monitoring in background (in production, use Celery/Redis)
    active_deployments[deployment_id] = {"running": True, "user_id": user["id"]}
    
    return {
        "message": "Strategy deployed successfully",
        "deployment_id": deployment_id,
        "status": "active",
        "deployment": {k: v for k, v in deployment.items() if k != "_id"}
    }

@deploy_router.get("/list")
async def list_deployments(user=Depends(get_current_user)):
    """List all user deployments"""
    deployments = await db.deployments.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return deployments

@deploy_router.get("/{deployment_id}")
async def get_deployment(deployment_id: str, user=Depends(get_current_user)):
    """Get deployment details"""
    deployment = await db.deployments.find_one(
        {"id": deployment_id, "user_id": user["id"]},
        {"_id": 0}
    )
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

@deploy_router.patch("/{deployment_id}")
async def update_deployment(deployment_id: str, update: DeploymentUpdate, user=Depends(get_current_user)):
    """Update deployment settings"""
    deployment = await db.deployments.find_one({"id": deployment_id, "user_id": user["id"]})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if update_data:
        await db.deployments.update_one(
            {"id": deployment_id},
            {"$set": update_data}
        )
    
    return {"message": "Deployment updated", "updated_fields": list(update_data.keys())}

@deploy_router.post("/{deployment_id}/start")
async def start_deployment(deployment_id: str, user=Depends(get_current_user)):
    """Resume a paused deployment"""
    deployment = await db.deployments.find_one({"id": deployment_id, "user_id": user["id"]})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    if deployment["status"] == "active":
        raise HTTPException(status_code=400, detail="Deployment already active")
    
    await db.deployments.update_one(
        {"id": deployment_id},
        {"$set": {"status": "active"}}
    )
    active_deployments[deployment_id] = {"running": True, "user_id": user["id"]}
    
    return {"message": "Deployment started", "status": "active"}

@deploy_router.post("/{deployment_id}/pause")
async def pause_deployment(deployment_id: str, user=Depends(get_current_user)):
    """Pause a deployment (keeps position open)"""
    deployment = await db.deployments.find_one({"id": deployment_id, "user_id": user["id"]})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    await db.deployments.update_one(
        {"id": deployment_id},
        {"$set": {"status": "paused"}}
    )
    if deployment_id in active_deployments:
        active_deployments[deployment_id]["running"] = False
    
    return {"message": "Deployment paused", "status": "paused"}

@deploy_router.post("/{deployment_id}/stop")
async def stop_deployment(deployment_id: str, user=Depends(get_current_user)):
    """Stop deployment and close any open positions"""
    deployment = await db.deployments.find_one({"id": deployment_id, "user_id": user["id"]})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Close any open position
    if deployment.get("position"):
        # Get current price
        collection = db[f"market_data_{deployment['timeframe']}"]
        latest = await collection.find_one(
            {"symbol": deployment["symbol"]},
            {"_id": 0},
            sort=[("timestamp", -1)]
        )
        if latest:
            position = deployment["position"]
            exit_price = latest["close"]
            pnl = (exit_price - position["entry_price"]) * position["quantity"]
            
            # Record the closing trade
            trade = {
                "id": str(uuid.uuid4()),
                "deployment_id": deployment_id,
                "user_id": user["id"],
                "type": "SELL",
                "symbol": deployment["symbol"],
                "price": exit_price,
                "quantity": position["quantity"],
                "pnl": pnl,
                "reason": "Deployment Stopped",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.deployment_trades.insert_one(trade)
    
    await db.deployments.update_one(
        {"id": deployment_id},
        {"$set": {"status": "stopped", "position": None, "stopped_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if deployment_id in active_deployments:
        del active_deployments[deployment_id]
    
    return {"message": "Deployment stopped", "status": "stopped"}

@deploy_router.delete("/{deployment_id}")
async def delete_deployment(deployment_id: str, user=Depends(get_current_user)):
    """Delete a stopped deployment"""
    deployment = await db.deployments.find_one({"id": deployment_id, "user_id": user["id"]})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    if deployment["status"] not in ["stopped", "error"]:
        raise HTTPException(status_code=400, detail="Stop deployment before deleting")
    
    await db.deployments.delete_one({"id": deployment_id})
    await db.deployment_trades.delete_many({"deployment_id": deployment_id})
    
    return {"message": "Deployment deleted"}

@deploy_router.get("/{deployment_id}/trades")
async def get_deployment_trades(deployment_id: str, user=Depends(get_current_user)):
    """Get trade history for a deployment"""
    deployment = await db.deployments.find_one({"id": deployment_id, "user_id": user["id"]})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    trades = await db.deployment_trades.find(
        {"deployment_id": deployment_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return trades

@deploy_router.get("/{deployment_id}/signals")
async def check_signals(deployment_id: str, user=Depends(get_current_user)):
    """Check current signals for a deployment (manual trigger)"""
    deployment = await db.deployments.find_one({"id": deployment_id, "user_id": user["id"]}, {"_id": 0})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    if deployment["status"] != "active":
        return {"signal": None, "message": "Deployment not active"}
    
    # Get latest market data
    collection = db[f"market_data_{deployment['timeframe']}"]
    ohlcv = await collection.find(
        {"symbol": deployment["symbol"]},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(500)
    
    if len(ohlcv) < 50:
        return {"signal": None, "message": "Insufficient data"}
    
    # Compute indicators
    import pandas as pd
    from utils.indicators import compute_all_indicators
    
    df = pd.DataFrame(ohlcv)
    indicators = compute_all_indicators(df, include_advanced=True)
    
    # Check entry/exit conditions
    from utils.backtest_engine import BacktestEngine
    engine = BacktestEngine()
    
    idx = len(df) - 1
    closes = df["close"].tolist()
    
    entry_signal = engine.evaluate_conditions(indicators, idx, deployment.get("entry_conditions", {}), closes)
    exit_signal = engine.evaluate_conditions(indicators, idx, deployment.get("exit_conditions", {}), closes)
    
    current_price = closes[-1]
    position = deployment.get("position")
    
    signal_result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_price": current_price,
        "has_position": position is not None,
        "entry_signal": entry_signal,
        "exit_signal": exit_signal,
        "recommended_action": None
    }
    
    if position is None and entry_signal:
        signal_result["recommended_action"] = "BUY"
    elif position is not None:
        # Check risk rules
        pnl_pct = (current_price - position["entry_price"]) / position["entry_price"] * 100
        risk = deployment.get("risk_settings", {})
        
        if pnl_pct <= -risk.get("stop_loss_pct", 5):
            signal_result["recommended_action"] = "SELL (Stop Loss)"
        elif pnl_pct >= risk.get("take_profit_pct", 10):
            signal_result["recommended_action"] = "SELL (Take Profit)"
        elif exit_signal:
            signal_result["recommended_action"] = "SELL (Exit Signal)"
        
        signal_result["position_pnl_pct"] = round(pnl_pct, 2)
    
    # Update last signal check
    await db.deployments.update_one(
        {"id": deployment_id},
        {"$set": {"last_signal_at": signal_result["timestamp"]}}
    )
    
    return signal_result

@deploy_router.post("/{deployment_id}/execute")
async def execute_trade(deployment_id: str, action: str, user=Depends(get_current_user)):
    """Manually execute a trade for deployment"""
    deployment = await db.deployments.find_one({"id": deployment_id, "user_id": user["id"]})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    if deployment["status"] != "active":
        raise HTTPException(status_code=400, detail="Deployment not active")
    
    # Get current price
    collection = db[f"market_data_{deployment['timeframe']}"]
    latest = await collection.find_one(
        {"symbol": deployment["symbol"]},
        {"_id": 0},
        sort=[("timestamp", -1)]
    )
    
    if not latest:
        raise HTTPException(status_code=400, detail="No market data available")
    
    current_price = latest["close"]
    position = deployment.get("position")
    
    if action.upper() == "BUY":
        if position:
            raise HTTPException(status_code=400, detail="Already have open position")
        
        # Calculate position size
        capital = deployment["current_capital"]
        max_pct = deployment["max_position_size_pct"] / 100
        invest_amount = capital * max_pct
        quantity = invest_amount / current_price
        
        # Create position
        new_position = {
            "entry_price": current_price,
            "quantity": quantity,
            "entry_time": datetime.now(timezone.utc).isoformat(),
            "value": invest_amount
        }
        
        # Record trade
        trade = {
            "id": str(uuid.uuid4()),
            "deployment_id": deployment_id,
            "user_id": user["id"],
            "type": "BUY",
            "symbol": deployment["symbol"],
            "price": current_price,
            "quantity": quantity,
            "value": invest_amount,
            "reason": "Manual",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.deployment_trades.insert_one(trade)
        
        # Update deployment
        await db.deployments.update_one(
            {"id": deployment_id},
            {
                "$set": {
                    "position": new_position,
                    "current_capital": capital - invest_amount,
                    "last_trade_at": trade["created_at"]
                },
                "$inc": {"total_trades": 1}
            }
        )
        
        return {
            "message": "Buy order executed",
            "trade": {k: v for k, v in trade.items() if k != "_id"},
            "position": new_position
        }
    
    elif action.upper() == "SELL":
        if not position:
            raise HTTPException(status_code=400, detail="No open position to sell")
        
        # Calculate P&L
        pnl = (current_price - position["entry_price"]) * position["quantity"]
        pnl_pct = (current_price - position["entry_price"]) / position["entry_price"] * 100
        proceeds = current_price * position["quantity"]
        
        # Record trade
        trade = {
            "id": str(uuid.uuid4()),
            "deployment_id": deployment_id,
            "user_id": user["id"],
            "type": "SELL",
            "symbol": deployment["symbol"],
            "price": current_price,
            "quantity": position["quantity"],
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "reason": "Manual",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.deployment_trades.insert_one(trade)
        
        # Update statistics
        trades = await db.deployment_trades.find({"deployment_id": deployment_id, "type": "SELL"}, {"_id": 0}).to_list(1000)
        wins = len([t for t in trades if t.get("pnl", 0) > 0])
        total = len(trades)
        win_rate = (wins / total * 100) if total > 0 else 0
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        
        # Update deployment
        await db.deployments.update_one(
            {"id": deployment_id},
            {
                "$set": {
                    "position": None,
                    "current_capital": deployment["current_capital"] + proceeds,
                    "total_pnl": total_pnl,
                    "win_rate": win_rate,
                    "last_trade_at": trade["created_at"]
                },
                "$inc": {"total_trades": 1}
            }
        )
        
        return {
            "message": "Sell order executed",
            "trade": {k: v for k, v in trade.items() if k != "_id"},
            "pnl": pnl,
            "pnl_pct": round(pnl_pct, 2)
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use BUY or SELL")
