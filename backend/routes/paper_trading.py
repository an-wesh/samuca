from fastapi import APIRouter, Depends, HTTPException
from database import db, get_current_user
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timezone

paper_router = APIRouter(prefix="/api/paper", tags=["paper_trading"])

class OrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"
    limit_price: Optional[float] = None

@paper_router.get("/portfolio")
async def get_portfolio(user=Depends(get_current_user)):
    portfolio = await db.paper_portfolios.find_one({"user_id": user["id"]}, {"_id": 0})
    if not portfolio:
        portfolio = {"user_id": user["id"], "cash": 100000.0, "initial_capital": 100000.0,
                     "positions": {}, "created_at": datetime.now(timezone.utc).isoformat()}
        await db.paper_portfolios.insert_one(portfolio)
        portfolio.pop("_id", None)

    total_value = portfolio["cash"]
    position_details = []
    for symbol, pos in portfolio.get("positions", {}).items():
        last_doc = await db.market_data_1h.find_one({"symbol": symbol}, {"_id": 0}, sort=[("timestamp", -1)])
        current_price = last_doc["close"] if last_doc else pos["avg_price"]
        mkt_val = pos["quantity"] * current_price
        unrealized = (current_price - pos["avg_price"]) * pos["quantity"]
        total_value += mkt_val
        position_details.append({
            "symbol": symbol, "quantity": pos["quantity"], "avg_price": pos["avg_price"],
            "current_price": round(current_price, 2), "market_value": round(mkt_val, 2),
            "unrealized_pnl": round(unrealized, 2),
            "pnl_pct": round((current_price / pos["avg_price"] - 1) * 100, 2) if pos["avg_price"] > 0 else 0,
        })
    return {
        "cash": round(portfolio["cash"], 2), "total_value": round(total_value, 2),
        "initial_capital": portfolio["initial_capital"],
        "total_pnl": round(total_value - portfolio["initial_capital"], 2),
        "total_pnl_pct": round((total_value / portfolio["initial_capital"] - 1) * 100, 2),
        "positions": position_details,
    }

@paper_router.post("/order")
async def place_order(req: OrderRequest, user=Depends(get_current_user)):
    last_doc = await db.market_data_1h.find_one({"symbol": req.symbol}, {"_id": 0}, sort=[("timestamp", -1)])
    if not last_doc:
        raise HTTPException(status_code=400, detail=f"No market data for {req.symbol}")
    price = req.limit_price if req.order_type == "limit" and req.limit_price else last_doc["close"]

    portfolio = await db.paper_portfolios.find_one({"user_id": user["id"]})
    if not portfolio:
        portfolio = {"user_id": user["id"], "cash": 100000.0, "initial_capital": 100000.0,
                     "positions": {}, "created_at": datetime.now(timezone.utc).isoformat()}
        await db.paper_portfolios.insert_one(portfolio)

    positions = portfolio.get("positions", {})
    cost = price * req.quantity

    if req.side == "buy":
        if portfolio["cash"] < cost:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        new_cash = portfolio["cash"] - cost
        if req.symbol in positions:
            old = positions[req.symbol]
            new_qty = old["quantity"] + req.quantity
            new_avg = (old["quantity"] * old["avg_price"] + req.quantity * price) / new_qty
            positions[req.symbol] = {"quantity": round(new_qty, 6), "avg_price": round(new_avg, 2)}
        else:
            positions[req.symbol] = {"quantity": round(req.quantity, 6), "avg_price": round(price, 2)}
        await db.paper_portfolios.update_one({"user_id": user["id"]}, {"$set": {"cash": new_cash, "positions": positions}})

    elif req.side == "sell":
        if req.symbol not in positions or positions[req.symbol]["quantity"] < req.quantity:
            raise HTTPException(status_code=400, detail="Insufficient position")
        new_cash = portfolio["cash"] + cost
        positions[req.symbol]["quantity"] = round(positions[req.symbol]["quantity"] - req.quantity, 6)
        if positions[req.symbol]["quantity"] <= 0:
            del positions[req.symbol]
        await db.paper_portfolios.update_one({"user_id": user["id"]}, {"$set": {"cash": new_cash, "positions": positions}})

    order = {
        "id": str(uuid.uuid4()), "user_id": user["id"], "symbol": req.symbol,
        "side": req.side, "quantity": req.quantity, "price": round(price, 2),
        "order_type": req.order_type, "status": "filled",
        "filled_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.paper_orders.insert_one(order)
    return {k: v for k, v in order.items() if k != "_id"}

@paper_router.get("/orders")
async def get_orders(user=Depends(get_current_user)):
    return await db.paper_orders.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)

@paper_router.get("/positions")
async def get_positions(user=Depends(get_current_user)):
    portfolio = await db.paper_portfolios.find_one({"user_id": user["id"]}, {"_id": 0})
    if not portfolio:
        return []
    positions = []
    for symbol, pos in portfolio.get("positions", {}).items():
        last_doc = await db.market_data_1h.find_one({"symbol": symbol}, {"_id": 0}, sort=[("timestamp", -1)])
        current_price = last_doc["close"] if last_doc else pos["avg_price"]
        positions.append({
            "symbol": symbol, "quantity": pos["quantity"], "avg_price": pos["avg_price"],
            "current_price": round(current_price, 2),
            "market_value": round(pos["quantity"] * current_price, 2),
            "unrealized_pnl": round((current_price - pos["avg_price"]) * pos["quantity"], 2),
        })
    return positions

@paper_router.post("/reset")
async def reset_portfolio(user=Depends(get_current_user)):
    await db.paper_portfolios.delete_one({"user_id": user["id"]})
    await db.paper_orders.delete_many({"user_id": user["id"]})
    return {"status": "reset"}
