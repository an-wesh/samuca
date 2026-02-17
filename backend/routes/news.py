"""
News & Sentiment Analysis Service
Real-time news feeds and AI-powered sentiment analysis
"""
from fastapi import APIRouter, Depends, HTTPException
from database import db, get_current_user, EMERGENT_LLM_KEY
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta

news_router = APIRouter(prefix="/api/news", tags=["news"])
logger = logging.getLogger(__name__)

class NewsAnalysisRequest(BaseModel):
    headlines: List[str]
    symbols: Optional[List[str]] = None

class NewsFeedRequest(BaseModel):
    symbol: Optional[str] = None
    limit: int = 20

# Mock news headlines for demonstration (in production, integrate with news APIs)
MOCK_NEWS = {
    "BTCUSD": [
        {"headline": "Bitcoin Surges Past $100K as Institutional Adoption Accelerates", "source": "CryptoDaily", "sentiment": "bullish"},
        {"headline": "Bitcoin Mining Difficulty Reaches All-Time High", "source": "BlockNews", "sentiment": "neutral"},
        {"headline": "MicroStrategy Adds Another $500M in Bitcoin to Treasury", "source": "CoinDesk", "sentiment": "bullish"},
        {"headline": "Bitcoin ETF Sees Record Inflows This Week", "source": "Bloomberg", "sentiment": "bullish"},
        {"headline": "Regulatory Concerns Mount Over Crypto Exchanges", "source": "Reuters", "sentiment": "bearish"},
        {"headline": "Bitcoin Network Hash Rate Continues Upward Trend", "source": "The Block", "sentiment": "neutral"},
        {"headline": "Whale Alert: Large BTC Transfer to Unknown Wallet", "source": "WhaleAlert", "sentiment": "neutral"},
        {"headline": "Bitcoin Dominance Rises Above 50%", "source": "CoinMarketCap", "sentiment": "bullish"},
    ],
    "ETHUSD": [
        {"headline": "Ethereum 2.0 Staking Yields Attract Institutional Interest", "source": "DeFiPulse", "sentiment": "bullish"},
        {"headline": "Ethereum Gas Fees Drop to Multi-Month Lows", "source": "Etherscan", "sentiment": "bullish"},
        {"headline": "Major DeFi Protocol Announces Ethereum Expansion", "source": "DeFi Weekly", "sentiment": "bullish"},
        {"headline": "Ethereum Foundation Releases Q4 Transparency Report", "source": "ETH News", "sentiment": "neutral"},
        {"headline": "Layer 2 Solutions Drive Ethereum Scalability Forward", "source": "L2Beat", "sentiment": "bullish"},
    ],
    "AAPL": [
        {"headline": "Apple Reports Record Q4 Revenue Driven by iPhone Sales", "source": "WSJ", "sentiment": "bullish"},
        {"headline": "Apple Vision Pro Sales Exceed Analyst Expectations", "source": "Bloomberg", "sentiment": "bullish"},
        {"headline": "Apple Faces Antitrust Scrutiny in EU Markets", "source": "Reuters", "sentiment": "bearish"},
        {"headline": "Apple Services Revenue Continues Double-Digit Growth", "source": "CNBC", "sentiment": "bullish"},
        {"headline": "New MacBook Pro with M4 Chip Receives Strong Reviews", "source": "TechCrunch", "sentiment": "bullish"},
        {"headline": "Apple Supply Chain Faces Challenges in Asia", "source": "Nikkei", "sentiment": "bearish"},
    ],
    "TSLA": [
        {"headline": "Tesla Cybertruck Deliveries Ramp Up Globally", "source": "Electrek", "sentiment": "bullish"},
        {"headline": "Tesla Stock Volatile After Mixed Q4 Earnings", "source": "MarketWatch", "sentiment": "neutral"},
        {"headline": "Elon Musk Announces New Tesla Gigafactory Location", "source": "Bloomberg", "sentiment": "bullish"},
        {"headline": "Tesla FSD v13 Receives Regulatory Approval in More States", "source": "InsideEVs", "sentiment": "bullish"},
        {"headline": "Competition Intensifies in EV Market From Chinese Rivals", "source": "Reuters", "sentiment": "bearish"},
        {"headline": "Tesla Energy Storage Business Posts Record Quarter", "source": "CleanTechnica", "sentiment": "bullish"},
    ],
    "SPY": [
        {"headline": "S&P 500 Hits New Record High Amid Strong Earnings Season", "source": "CNBC", "sentiment": "bullish"},
        {"headline": "Fed Signals Potential Rate Cuts in 2026", "source": "WSJ", "sentiment": "bullish"},
        {"headline": "Tech Sector Leads Market Rally", "source": "Bloomberg", "sentiment": "bullish"},
        {"headline": "Inflation Data Comes In Lower Than Expected", "source": "Reuters", "sentiment": "bullish"},
        {"headline": "Market Volatility Expected Ahead of Jobs Report", "source": "MarketWatch", "sentiment": "neutral"},
        {"headline": "Corporate Earnings Beat Expectations Across Sectors", "source": "Barron's", "sentiment": "bullish"},
    ],
}

def generate_mock_timestamp():
    """Generate realistic recent timestamps"""
    now = datetime.now(timezone.utc)
    offset = timedelta(hours=float(uuid.uuid4().int % 48))
    return (now - offset).isoformat()

@news_router.get("/feed")
async def get_news_feed(symbol: Optional[str] = None, limit: int = 20, user=Depends(get_current_user)):
    """Get latest news feed, optionally filtered by symbol"""
    news_items = []
    
    symbols = [symbol] if symbol else list(MOCK_NEWS.keys())
    
    for sym in symbols:
        if sym in MOCK_NEWS:
            for item in MOCK_NEWS[sym]:
                news_items.append({
                    "id": str(uuid.uuid4()),
                    "symbol": sym,
                    "headline": item["headline"],
                    "source": item["source"],
                    "timestamp": generate_mock_timestamp(),
                    "sentiment_hint": item["sentiment"]
                })
    
    # Sort by timestamp descending and limit
    news_items.sort(key=lambda x: x["timestamp"], reverse=True)
    return news_items[:limit]

@news_router.get("/feed/{symbol}")
async def get_symbol_news(symbol: str, limit: int = 10, user=Depends(get_current_user)):
    """Get news for a specific symbol"""
    symbol = symbol.upper()
    if symbol not in MOCK_NEWS:
        return []
    
    news_items = []
    for item in MOCK_NEWS[symbol][:limit]:
        news_items.append({
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "headline": item["headline"],
            "source": item["source"],
            "timestamp": generate_mock_timestamp(),
            "sentiment_hint": item["sentiment"]
        })
    
    return news_items

@news_router.post("/analyze")
async def analyze_news_sentiment(req: NewsAnalysisRequest, user=Depends(get_current_user)):
    """
    Analyze sentiment of news headlines using AI
    Returns scores from -1 (very bearish) to +1 (very bullish)
    """
    if not req.headlines:
        raise HTTPException(status_code=400, detail="Headlines required")
    
    results = []
    
    try:
        if EMERGENT_LLM_KEY:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"sentiment-{uuid.uuid4()}",
                system_message="""You are an expert financial sentiment analyzer. 
For each headline provided, analyze the market sentiment and return ONLY a JSON array.
Each object must have exactly these fields:
- "score": float from -1.0 (extremely bearish) to 1.0 (extremely bullish)
- "label": exactly one of "Strong Bullish", "Bullish", "Neutral", "Bearish", "Strong Bearish"
- "confidence": integer from 0-100 representing certainty
- "key_factors": array of 1-3 key words/phrases that influenced the analysis

Return ONLY the JSON array, no other text or explanation."""
            ).with_model("openai", "gpt-5.2")
            
            headlines_text = "\n".join([f"{i+1}. {h}" for i, h in enumerate(req.headlines)])
            response = await chat.send_message(UserMessage(text=f"Analyze these financial headlines:\n{headlines_text}"))
            
            # Parse response
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
                        "confidence": int(item.get("confidence", 50)),
                        "key_factors": item.get("key_factors", []),
                        "ai_analyzed": True
                    })
    except Exception as e:
        logger.warning(f"LLM sentiment analysis failed, using fallback: {e}")
        results = []
    
    # Fallback to keyword-based analysis
    if not results or len(results) != len(req.headlines):
        results = []
        for headline in req.headlines:
            results.append(_keyword_sentiment_enhanced(headline))
    
    # Store results
    for r in results:
        r["id"] = str(uuid.uuid4())
        r["user_id"] = user["id"]
        r["analyzed_at"] = datetime.now(timezone.utc).isoformat()
        if req.symbols:
            r["symbols"] = req.symbols
    
    if results:
        await db.sentiment_analysis.insert_many([{**r} for r in results])
    
    # Calculate aggregate sentiment
    scores = [r["score"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Determine overall label
    if avg_score >= 0.5:
        overall_label = "Strong Bullish"
    elif avg_score >= 0.2:
        overall_label = "Bullish"
    elif avg_score <= -0.5:
        overall_label = "Strong Bearish"
    elif avg_score <= -0.2:
        overall_label = "Bearish"
    else:
        overall_label = "Neutral"
    
    return {
        "results": [{k: v for k, v in r.items() if k not in ["_id", "user_id"]} for r in results],
        "aggregate": {
            "avg_score": round(avg_score, 3),
            "label": overall_label,
            "bullish_count": len([r for r in results if r["score"] > 0.2]),
            "bearish_count": len([r for r in results if r["score"] < -0.2]),
            "neutral_count": len([r for r in results if -0.2 <= r["score"] <= 0.2]),
            "total": len(results)
        }
    }

def _keyword_sentiment_enhanced(headline: str) -> dict:
    """Enhanced keyword-based sentiment analysis fallback"""
    text = headline.lower()
    
    strong_positive = ["surge", "soar", "record", "breakthrough", "rally", "boom", "skyrocket"]
    positive = ["gain", "rise", "growth", "bull", "profit", "strong", "up", "beat", "exceed", "optimistic"]
    strong_negative = ["crash", "plunge", "collapse", "crisis", "dump", "tank", "plummet"]
    negative = ["drop", "fall", "bear", "loss", "decline", "weak", "down", "miss", "concern", "fear", "risk"]
    
    sp = sum(1 for w in strong_positive if w in text) * 2
    p = sum(1 for w in positive if w in text)
    sn = sum(1 for w in strong_negative if w in text) * 2
    n = sum(1 for w in negative if w in text)
    
    pos_score = sp + p
    neg_score = sn + n
    
    if pos_score > neg_score:
        raw_score = min(0.2 + (pos_score - neg_score) * 0.15, 1.0)
        if sp > 0:
            label = "Strong Bullish"
        else:
            label = "Bullish"
        confidence = min(50 + pos_score * 10, 90)
    elif neg_score > pos_score:
        raw_score = max(-0.2 - (neg_score - pos_score) * 0.15, -1.0)
        if sn > 0:
            label = "Strong Bearish"
        else:
            label = "Bearish"
        confidence = min(50 + neg_score * 10, 90)
    else:
        raw_score = 0.0
        label = "Neutral"
        confidence = 50
    
    # Extract key factors
    factors = []
    for w in strong_positive + positive:
        if w in text:
            factors.append(w)
            if len(factors) >= 3:
                break
    for w in strong_negative + negative:
        if w in text:
            factors.append(w)
            if len(factors) >= 3:
                break
    
    return {
        "headline": headline,
        "score": round(raw_score, 3),
        "label": label,
        "confidence": confidence,
        "key_factors": factors[:3],
        "ai_analyzed": False
    }

@news_router.get("/sentiment/history")
async def get_sentiment_history(symbol: Optional[str] = None, limit: int = 50, user=Depends(get_current_user)):
    """Get historical sentiment analysis results"""
    query = {"user_id": user["id"]}
    if symbol:
        query["symbols"] = symbol.upper()
    
    results = await db.sentiment_analysis.find(query, {"_id": 0}).sort("analyzed_at", -1).to_list(limit)
    return results

@news_router.get("/sentiment/aggregate/{symbol}")
async def get_symbol_sentiment_aggregate(symbol: str, hours: int = 24, user=Depends(get_current_user)):
    """Get aggregated sentiment for a symbol over time period"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Get recent sentiment data
    results = await db.sentiment_analysis.find({
        "symbols": symbol.upper(),
        "analyzed_at": {"$gte": cutoff.isoformat()}
    }, {"_id": 0}).to_list(100)
    
    if not results:
        # Return mock aggregate if no data
        return {
            "symbol": symbol.upper(),
            "period_hours": hours,
            "avg_score": 0.2,  # Slightly bullish default
            "label": "Neutral",
            "sample_size": 0,
            "trend": "stable"
        }
    
    scores = [r["score"] for r in results]
    avg_score = sum(scores) / len(scores)
    
    # Calculate trend
    if len(scores) >= 4:
        first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
        second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
        if second_half - first_half > 0.1:
            trend = "improving"
        elif first_half - second_half > 0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    # Determine label
    if avg_score >= 0.5:
        label = "Strong Bullish"
    elif avg_score >= 0.2:
        label = "Bullish"
    elif avg_score <= -0.5:
        label = "Strong Bearish"
    elif avg_score <= -0.2:
        label = "Bearish"
    else:
        label = "Neutral"
    
    return {
        "symbol": symbol.upper(),
        "period_hours": hours,
        "avg_score": round(avg_score, 3),
        "label": label,
        "sample_size": len(results),
        "trend": trend
    }
