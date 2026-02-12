from fastapi import APIRouter, Depends, HTTPException
from database import db, get_current_user, EMERGENT_LLM_KEY
from pydantic import BaseModel
from typing import List
import uuid
import json
import logging
import pandas as pd
from datetime import datetime, timezone

ai_router = APIRouter(prefix="/api", tags=["ai"])
logger = logging.getLogger(__name__)

class SentimentRequest(BaseModel):
    headlines: List[str]

FUNDAMENTALS = {
    "AAPL": {"pe_ratio": 28.5, "roe": 147.5, "eps_growth": 12.3, "revenue_growth": 8.1, "fundamental_score": 78, "valuation": "Fair Valued", "bias": "Bullish", "market_cap": "2.8T", "sector": "Technology"},
    "TSLA": {"pe_ratio": 72.3, "roe": 23.8, "eps_growth": -15.2, "revenue_growth": 3.5, "fundamental_score": 45, "valuation": "Overvalued", "bias": "Neutral", "market_cap": "780B", "sector": "Automotive"},
    "SPY": {"pe_ratio": 22.1, "roe": 18.5, "eps_growth": 9.8, "revenue_growth": 5.2, "fundamental_score": 72, "valuation": "Fair Valued", "bias": "Bullish", "market_cap": "N/A", "sector": "Index"},
    "BTCUSD": {"hash_rate": "600 EH/s", "active_addresses": "1.2M", "nvt_ratio": 45.2, "fundamental_score": 82, "valuation": "Fair", "bias": "Bullish", "market_cap": "1.3T", "sector": "Crypto"},
    "ETHUSD": {"tvl": "52B", "active_addresses": "500K", "gas_fees": "12 gwei", "fundamental_score": 75, "valuation": "Fair", "bias": "Bullish", "market_cap": "420B", "sector": "Crypto"},
}

def _keyword_sentiment(headline):
    positive = ["surge", "rally", "gain", "bull", "up", "high", "growth", "profit", "record", "strong", "buy", "soar", "boost", "rise"]
    negative = ["crash", "drop", "fall", "bear", "down", "low", "loss", "decline", "weak", "sell", "fear", "plunge", "dump", "risk"]
    text = headline.lower()
    pos_count = sum(1 for w in positive if w in text)
    neg_count = sum(1 for w in negative if w in text)
    if pos_count > neg_count:
        score = min(0.3 + pos_count * 0.15, 1.0)
        return {"headline": headline, "score": round(score, 3), "label": "Bullish", "confidence": min(60 + pos_count * 10, 95)}
    elif neg_count > pos_count:
        score = max(-0.3 - neg_count * 0.15, -1.0)
        return {"headline": headline, "score": round(score, 3), "label": "Bearish", "confidence": min(60 + neg_count * 10, 95)}
    return {"headline": headline, "score": 0.0, "label": "Neutral", "confidence": 50}

@ai_router.post("/sentiment/analyze")
async def analyze_sentiment(req: SentimentRequest, user=Depends(get_current_user)):
    if not req.headlines:
        raise HTTPException(status_code=400, detail="Headlines required")

    results = []
    try:
        if EMERGENT_LLM_KEY:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"sentiment-{uuid.uuid4()}",
                system_message="You are a financial sentiment analyzer. For each headline, return ONLY a JSON array with objects having: score (float -1 to 1), label (Bullish/Bearish/Neutral), confidence (int 0-100). No other text."
            )
            headlines_text = "\n".join([f"{i+1}. {h}" for i, h in enumerate(req.headlines)])
            response = await chat.send_message(UserMessage(text=f"Analyze:\n{headlines_text}"))
            response_text = response.strip()
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            parsed = json.loads(response_text)
            if isinstance(parsed, list):
                for i, item in enumerate(parsed):
                    results.append({
                        "headline": req.headlines[i] if i < len(req.headlines) else "",
                        "score": float(item.get("score", 0)),
                        "label": item.get("label", "Neutral"),
                        "confidence": float(item.get("confidence", 50)),
                    })
    except Exception as e:
        logger.warning(f"LLM sentiment failed, using keyword fallback: {e}")
        results = []

    if not results:
        results = [_keyword_sentiment(h) for h in req.headlines]

    for r in results:
        r["id"] = str(uuid.uuid4())
        r["user_id"] = user["id"]
        r["analyzed_at"] = datetime.now(timezone.utc).isoformat()

    if results:
        await db.sentiment_data.insert_many([{**r} for r in results])

    avg_score = sum(r["score"] for r in results) / len(results) if results else 0
    return {
        "results": [{k: v for k, v in r.items() if k != "_id"} for r in results],
        "aggregate": {
            "avg_score": round(avg_score, 3),
            "label": "Bullish" if avg_score > 0.2 else "Bearish" if avg_score < -0.2 else "Neutral",
            "count": len(results),
        },
    }

@ai_router.get("/sentiment/latest")
async def get_latest_sentiment(user=Depends(get_current_user)):
    return await db.sentiment_data.find({"user_id": user["id"]}, {"_id": 0}).sort("analyzed_at", -1).to_list(20)

@ai_router.get("/fundamentals/{symbol}")
async def get_fundamentals(symbol: str):
    data = FUNDAMENTALS.get(symbol)
    if not data:
        raise HTTPException(status_code=404, detail=f"No fundamental data for {symbol}")
    return {"symbol": symbol, **data}

@ai_router.get("/indicators/{symbol}")
async def get_indicators(symbol: str, timeframe: str = "1h"):
    collection = db[f"market_data_{timeframe}"]
    data = await collection.find({"symbol": symbol}, {"_id": 0}).sort("timestamp", 1).to_list(500)
    if len(data) < 30:
        return {"error": "Insufficient data"}
    from utils.engines import compute_all_indicators
    df = pd.DataFrame(data)
    indicators = compute_all_indicators(df)
    return {"symbol": symbol, "timeframe": timeframe, "indicators": indicators, "count": len(data)}
