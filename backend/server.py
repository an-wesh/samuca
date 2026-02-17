from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import uuid
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from pathlib import Path
from pydantic import BaseModel
from database import db, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_HOURS, get_current_user, client

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI(title="AI Trading Bot Builder", version="1.0.0")

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

auth_router_prefix = "/api/auth"

@app.post(f"{auth_router_prefix}/signup")
async def signup(req: SignupRequest):
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    user = {
        "id": str(uuid.uuid4()),
        "email": req.email,
        "name": req.name,
        "password_hash": hashed,
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "portfolio_value": 100000.0,
    }
    await db.users.insert_one(user)
    token = jwt.encode(
        {"user_id": user["id"], "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)},
        JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    return {"token": token, "user": {k: v for k, v in user.items() if k not in ["password_hash", "_id"]}}

@app.post(f"{auth_router_prefix}/login")
async def login(req: LoginRequest):
    user = await db.users.find_one({"email": req.email}, {"_id": 0})
    if not user or not bcrypt.checkpw(req.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode(
        {"user_id": user["id"], "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)},
        JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    return {"token": token, "user": {k: v for k, v in user.items() if k != "password_hash"}}

@app.get("/api/auth/me")
async def get_me(user=Depends(get_current_user)):
    return {k: v for k, v in user.items() if k != "password_hash"}

from routes.market import market_router
from routes.bots import bots_router
from routes.backtest import backtest_router
from routes.paper_trading import paper_router
from routes.ai_services import ai_router
from routes.deployment import deploy_router
from routes.news import news_router
from routes.ml_bot import ml_router
from routes.admin import admin_router

app.include_router(market_router)
app.include_router(bots_router)
app.include_router(backtest_router)
app.include_router(paper_router)
app.include_router(ai_router)
app.include_router(deploy_router)
app.include_router(news_router)
app.include_router(ml_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    from utils.market_generator import generate_market_data
    await generate_market_data(db)
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    for tf in ["5m", "15m", "1h", "1d"]:
        await db[f"market_data_{tf}"].create_index([("symbol", 1), ("timestamp", 1)])
    await db.bots.create_index("user_id")
    await db.strategies.create_index("user_id")
    logger.info("AI Trading Bot Builder initialized")

@app.on_event("shutdown")
async def shutdown():
    client.close()
