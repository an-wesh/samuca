"""
Admin Terminal API Routes
Full admin control: user management, capital allocation, risk controls, monitoring
"""
from fastapi import APIRouter, Depends, HTTPException
from database import db, get_current_user
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timezone, timedelta
import hashlib

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger(__name__)


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str = "user"  # user, admin, moderator
    initial_capital: float = 100000


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    virtual_capital: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_position_size: Optional[float] = None
    trading_enabled: Optional[bool] = None


class RiskLimitUpdate(BaseModel):
    max_daily_loss_pct: float = 5.0
    max_position_size_pct: float = 20.0
    max_concurrent_positions: int = 5
    max_leverage: float = 1.0


class CapitalAllocation(BaseModel):
    user_id: str
    amount: float
    reason: str


async def verify_admin(user: Dict) -> bool:
    """Verify user has admin privileges"""
    if user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return True


async def get_admin_user(user=Depends(get_current_user)):
    """Dependency to verify admin access"""
    await verify_admin(user)
    return user


# ==================== DASHBOARD ====================

@admin_router.get("/dashboard")
async def get_admin_dashboard(admin=Depends(get_admin_user)):
    """Get admin dashboard overview"""
    # User stats
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": {"$ne": False}})
    
    # Recent signups (last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    new_users = await db.users.count_documents({
        "created_at": {"$gte": week_ago}
    })
    
    # Trading activity
    total_strategies = await db.strategies.count_documents({})
    total_backtests = await db.backtests.count_documents({})
    active_deployments = await db.deployments.count_documents({"status": "active"})
    
    # ML models
    total_models = await db.ml_models.count_documents({})
    
    # Capital stats
    pipeline = [
        {"$group": {
            "_id": None,
            "total_capital": {"$sum": "$virtual_capital"},
            "avg_capital": {"$avg": "$virtual_capital"}
        }}
    ]
    capital_stats = await db.users.aggregate(pipeline).to_list(1)
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "new_this_week": new_users
        },
        "trading": {
            "strategies": total_strategies,
            "backtests": total_backtests,
            "active_deployments": active_deployments,
            "ml_models": total_models
        },
        "capital": {
            "total_allocated": capital_stats[0]["total_capital"] if capital_stats else 0,
            "average_per_user": round(capital_stats[0]["avg_capital"], 2) if capital_stats else 0
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ==================== USER MANAGEMENT ====================

@admin_router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin=Depends(get_admin_user)
):
    """List all users with filters"""
    query = {}
    
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}}
        ]
    
    if role:
        query["role"] = role
    
    if is_active is not None:
        query["is_active"] = is_active
    
    users = await db.users.find(query, {"_id": 0, "hashed_password": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.users.count_documents(query)
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@admin_router.get("/users/{user_id}")
async def get_user(user_id: str, admin=Depends(get_admin_user)):
    """Get detailed user information"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's activity stats
    strategies = await db.strategies.count_documents({"user_id": user_id})
    backtests = await db.backtests.count_documents({"user_id": user_id})
    deployments = await db.deployments.count_documents({"user_id": user_id})
    ml_models = await db.ml_models.count_documents({"user_id": user_id})
    
    # Get recent trades
    recent_trades = await db.deployment_trades.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        **user,
        "activity": {
            "strategies": strategies,
            "backtests": backtests,
            "deployments": deployments,
            "ml_models": ml_models
        },
        "recent_trades": recent_trades
    }


@admin_router.post("/users")
async def create_user(req: UserCreate, admin=Depends(get_admin_user)):
    """Create a new user"""
    import uuid
    
    # Check if email exists
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed = hashlib.sha256(req.password.encode()).hexdigest()
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": req.email,
        "name": req.name,
        "hashed_password": hashed,
        "role": req.role,
        "virtual_capital": req.initial_capital,
        "is_active": True,
        "trading_enabled": True,
        "risk_limits": {
            "max_daily_loss_pct": 5.0,
            "max_position_size_pct": 20.0,
            "max_concurrent_positions": 5,
            "max_leverage": 1.0
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": admin["id"]
    }
    
    await db.users.insert_one(user)
    
    return {"message": "User created", "user_id": user_id}


@admin_router.patch("/users/{user_id}")
async def update_user(user_id: str, req: UserUpdate, admin=Depends(get_admin_user)):
    """Update user details"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        update_data["updated_by"] = admin["id"]
        
        await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    return {"message": "User updated", "updated_fields": list(update_data.keys())}


@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin=Depends(get_admin_user)):
    """Delete a user (soft delete by deactivating)"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting admins
    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    # Soft delete
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "is_active": False,
            "trading_enabled": False,
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "deleted_by": admin["id"]
        }}
    )
    
    # Stop all active deployments
    await db.deployments.update_many(
        {"user_id": user_id, "status": "active"},
        {"$set": {"status": "stopped"}}
    )
    
    return {"message": "User deactivated"}


@admin_router.post("/users/{user_id}/activate")
async def activate_user(user_id: str, admin=Depends(get_admin_user)):
    """Reactivate a deactivated user"""
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "is_active": True,
            "reactivated_at": datetime.now(timezone.utc).isoformat(),
            "reactivated_by": admin["id"]
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User activated"}


# ==================== CAPITAL MANAGEMENT ====================

@admin_router.post("/capital/allocate")
async def allocate_capital(req: CapitalAllocation, admin=Depends(get_admin_user)):
    """Allocate/adjust capital for a user"""
    user = await db.users.find_one({"id": req.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_capital = user.get("virtual_capital", 0)
    new_capital = current_capital + req.amount
    
    if new_capital < 0:
        raise HTTPException(status_code=400, detail="Capital cannot be negative")
    
    # Update user capital
    await db.users.update_one(
        {"id": req.user_id},
        {"$set": {"virtual_capital": new_capital}}
    )
    
    # Log the transaction
    transaction = {
        "user_id": req.user_id,
        "type": "allocation" if req.amount > 0 else "deduction",
        "amount": req.amount,
        "reason": req.reason,
        "previous_capital": current_capital,
        "new_capital": new_capital,
        "admin_id": admin["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.capital_transactions.insert_one(transaction)
    
    return {
        "message": "Capital updated",
        "previous_capital": current_capital,
        "new_capital": new_capital
    }


@admin_router.get("/capital/transactions")
async def get_capital_transactions(
    user_id: Optional[str] = None,
    limit: int = 50,
    admin=Depends(get_admin_user)
):
    """Get capital transaction history"""
    query = {}
    if user_id:
        query["user_id"] = user_id
    
    transactions = await db.capital_transactions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return transactions


# ==================== RISK CONTROLS ====================

@admin_router.get("/risk/limits/{user_id}")
async def get_user_risk_limits(user_id: str, admin=Depends(get_admin_user)):
    """Get user's risk limits"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "risk_limits": user.get("risk_limits", {}),
        "trading_enabled": user.get("trading_enabled", True)
    }


@admin_router.put("/risk/limits/{user_id}")
async def update_user_risk_limits(user_id: str, req: RiskLimitUpdate, admin=Depends(get_admin_user)):
    """Update user's risk limits"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    risk_limits = {
        "max_daily_loss_pct": req.max_daily_loss_pct,
        "max_position_size_pct": req.max_position_size_pct,
        "max_concurrent_positions": req.max_concurrent_positions,
        "max_leverage": req.max_leverage
    }
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "risk_limits": risk_limits,
            "risk_updated_at": datetime.now(timezone.utc).isoformat(),
            "risk_updated_by": admin["id"]
        }}
    )
    
    return {"message": "Risk limits updated", "risk_limits": risk_limits}


@admin_router.post("/risk/disable-trading/{user_id}")
async def disable_user_trading(user_id: str, reason: str = "", admin=Depends(get_admin_user)):
    """Disable trading for a user"""
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "trading_enabled": False,
            "trading_disabled_reason": reason,
            "trading_disabled_at": datetime.now(timezone.utc).isoformat(),
            "trading_disabled_by": admin["id"]
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Stop all active deployments
    await db.deployments.update_many(
        {"user_id": user_id, "status": "active"},
        {"$set": {"status": "paused"}}
    )
    
    return {"message": "Trading disabled for user"}


@admin_router.post("/risk/enable-trading/{user_id}")
async def enable_user_trading(user_id: str, admin=Depends(get_admin_user)):
    """Enable trading for a user"""
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "trading_enabled": True,
            "trading_enabled_at": datetime.now(timezone.utc).isoformat(),
            "trading_enabled_by": admin["id"]
        },
        "$unset": {"trading_disabled_reason": ""}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Trading enabled for user"}


# ==================== MONITORING ====================

@admin_router.get("/monitoring/activity")
async def get_platform_activity(
    hours: int = 24,
    admin=Depends(get_admin_user)
):
    """Get platform activity over time"""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    # Recent backtests
    backtests = await db.backtests.find(
        {"created_at": {"$gte": cutoff}},
        {"_id": 0, "equity_curve": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    # Recent deployments
    deployments = await db.deployments.find(
        {"created_at": {"$gte": cutoff}},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    # Recent trades
    trades = await db.deployment_trades.find(
        {"created_at": {"$gte": cutoff}},
        {"_id": 0}
    ).sort("created_at", -1).limit(100).to_list(100)
    
    # Calculate P&L
    total_pnl = sum(t.get("pnl", 0) for t in trades if t.get("pnl"))
    
    return {
        "period_hours": hours,
        "backtests": {
            "count": len(backtests),
            "recent": backtests[:10]
        },
        "deployments": {
            "count": len(deployments),
            "recent": deployments[:10]
        },
        "trades": {
            "count": len(trades),
            "total_pnl": round(total_pnl, 2),
            "recent": trades[:20]
        }
    }


@admin_router.get("/monitoring/active-deployments")
async def get_active_deployments(admin=Depends(get_admin_user)):
    """Get all active deployments across platform"""
    deployments = await db.deployments.find(
        {"status": "active"},
        {"_id": 0}
    ).to_list(200)
    
    # Group by user
    by_user = {}
    for d in deployments:
        uid = d.get("user_id")
        if uid not in by_user:
            by_user[uid] = []
        by_user[uid].append(d)
    
    return {
        "total_active": len(deployments),
        "unique_users": len(by_user),
        "deployments": deployments,
        "by_user": by_user
    }


@admin_router.get("/monitoring/errors")
async def get_recent_errors(limit: int = 50, admin=Depends(get_admin_user)):
    """Get recent error logs"""
    errors = await db.error_logs.find(
        {},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return errors


# ==================== BULK OPERATIONS ====================

@admin_router.post("/bulk/stop-all-trading")
async def stop_all_trading(reason: str, admin=Depends(get_admin_user)):
    """Emergency: Stop all trading platform-wide"""
    # Stop all active deployments
    result = await db.deployments.update_many(
        {"status": "active"},
        {"$set": {
            "status": "paused",
            "paused_reason": f"Admin emergency stop: {reason}",
            "paused_at": datetime.now(timezone.utc).isoformat(),
            "paused_by": admin["id"]
        }}
    )
    
    # Log the action
    await db.admin_actions.insert_one({
        "action": "emergency_stop",
        "reason": reason,
        "admin_id": admin["id"],
        "affected_deployments": result.modified_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "message": "All trading stopped",
        "deployments_stopped": result.modified_count
    }


@admin_router.post("/bulk/reset-daily-limits")
async def reset_daily_limits(admin=Depends(get_admin_user)):
    """Reset daily loss limits for all users"""
    result = await db.users.update_many(
        {},
        {"$set": {"daily_loss_used": 0, "daily_reset_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "message": "Daily limits reset",
        "users_affected": result.modified_count
    }
