"""
News & Sentiment Analysis API Routes
Real-time news feeds and AI-powered sentiment analysis using HuggingFace FinBERT
"""
from fastapi import APIRouter, Depends, HTTPException
from database import db, get_current_user
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta

from services.news_service import (
    fetch_news_for_symbol, fetch_news_for_sector, 
    fetch_market_news, fetch_crypto_news, get_mock_news
)

news_router = APIRouter(prefix="/api/news", tags=["news"])
logger = logging.getLogger(__name__)


class NewsAnalysisRequest(BaseModel):
    headlines: List[str]
    symbols: Optional[List[str]] = None


class NewsFeedRequest(BaseModel):
    symbol: Optional[str] = None
    sector: Optional[str] = None
    limit: int = 20


@news_router.get("/feed")
async def get_news_feed(
    symbol: Optional[str] = None,
    sector: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    user=Depends(get_current_user)
):
    """Get latest news feed - real-time from APIs with fallback"""
    articles = []
    
    try:
        if symbol:
            # Fetch news for specific symbol
            articles = await fetch_news_for_symbol(symbol, limit)
        elif sector:
            # Fetch news for sector
            articles = await fetch_news_for_sector(sector, limit)
        elif category == "crypto":
            articles = await fetch_crypto_news(limit)
        else:
            # General market news
            articles = await fetch_market_news(limit)
    except Exception as e:
        logger.error(f"News fetch error: {e}")
    
    # Use mock news if API fails
    if not articles:
        logger.info("Using mock news as fallback")
        articles = get_mock_news(symbol, limit)
    
    # Format response
    news_items = []
    for article in articles[:limit]:
        published_at = article.get("published_at", "")
        if published_at and isinstance(published_at, str):
            try:
                # Parse and reformat timestamp
                dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                published_at = dt.isoformat()
            except (ValueError, TypeError):
                published_at = datetime.now(timezone.utc).isoformat()
        else:
            published_at = datetime.now(timezone.utc).isoformat()
        
        news_items.append({
            "id": article.get("id", str(uuid.uuid4())),
            "headline": article.get("title", ""),
            "description": article.get("description", ""),
            "source": article.get("source", "Unknown"),
            "url": article.get("url", "#"),
            "image": article.get("image"),
            "symbol": article.get("symbol"),
            "display_symbol": article.get("display_symbol"),
            "sector": article.get("sector"),
            "category": article.get("category", "News"),
            "timestamp": published_at,
            "sentiment_hint": article.get("sentiment_hint")
        })
    
    return news_items


@news_router.get("/feed/{symbol}")
async def get_symbol_news(symbol: str, limit: int = 10, user=Depends(get_current_user)):
    """Get news for a specific symbol"""
    return await get_news_feed(symbol=symbol, limit=limit, user=user)


@news_router.get("/sector/{sector}")
async def get_sector_news(sector: str, limit: int = 10, user=Depends(get_current_user)):
    """Get news for a specific sector"""
    return await get_news_feed(sector=sector, limit=limit, user=user)


@news_router.get("/market")
async def get_general_market_news(limit: int = 20, user=Depends(get_current_user)):
    """Get general market news"""
    return await get_news_feed(category="market", limit=limit, user=user)


@news_router.get("/crypto")
async def get_cryptocurrency_news(limit: int = 10, user=Depends(get_current_user)):
    """Get cryptocurrency news"""
    return await get_news_feed(category="crypto", limit=limit, user=user)


@news_router.post("/analyze")
async def analyze_news_sentiment(req: NewsAnalysisRequest, user=Depends(get_current_user)):
    """
    Analyze sentiment of news headlines using HuggingFace free AI API
    Returns scores from -1 (very bearish) to +1 (very bullish)
    """
    if not req.headlines:
        raise HTTPException(status_code=400, detail="Headlines required")
    
    results = []
    
    # Try HuggingFace free inference API (no API key needed)
    HF_API_URL = "https://router.huggingface.co/hf-inference/models/ProsusAI/finbert"
    
    async with aiohttp.ClientSession() as session:
        for headline in req.headlines:
            ai_result = None
            
            # Try up to 2 times (model may need to wake up)
            for attempt in range(2):
                try:
                    async with session.post(
                        HF_API_URL,
                        headers={"Content-Type": "application/json"},
                        json={"inputs": headline},
                        timeout=aiohttp.ClientTimeout(total=20)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # FinBERT returns: [[{"label": "positive/negative/neutral", "score": 0.xx}]]
                            if isinstance(data, list) and len(data) > 0:
                                # Handle nested list format
                                sentiments = data[0] if isinstance(data[0], list) else data
                                
                                if isinstance(sentiments, list) and len(sentiments) > 0:
                                    # Find the highest scoring sentiment
                                    best_sentiment = max(sentiments, key=lambda x: x.get("score", 0))
                                    label = best_sentiment.get("label", "neutral").lower()
                                    confidence = int(best_sentiment.get("score", 0.5) * 100)
                                    
                                    # Convert to score (-1 to 1)
                                    if label == "positive":
                                        score = best_sentiment.get("score", 0.5)
                                        display_label = "Bullish" if score > 0.7 else "Slightly Bullish"
                                    elif label == "negative":
                                        score = -best_sentiment.get("score", 0.5)
                                        display_label = "Bearish" if score < -0.7 else "Slightly Bearish"
                                    else:
                                        score = 0.0
                                        display_label = "Neutral"
                                    
                                    ai_result = {
                                        "headline": headline,
                                        "score": round(score, 3),
                                        "label": display_label,
                                        "confidence": confidence,
                                        "key_factors": [label],
                                        "market_impact": "high" if abs(score) > 0.7 else "medium" if abs(score) > 0.3 else "low",
                                        "ai_analyzed": True
                                    }
                                    break
                        elif response.status == 503:
                            # Model is loading, wait and retry
                            error_data = await response.json()
                            wait_time = error_data.get("estimated_time", 10)
                            logger.info(f"HuggingFace model loading, waiting {wait_time}s...")
                            await asyncio.sleep(min(wait_time, 15))
                        else:
                            error_text = await response.text()
                            logger.warning(f"HuggingFace API error {response.status}: {error_text[:100]}")
                            break
                except asyncio.TimeoutError:
                    logger.warning(f"HuggingFace API timeout (attempt {attempt+1})")
                except Exception as e:
                    logger.warning(f"HuggingFace API error: {e}")
                    break
            
            # Use AI result or fallback to keyword analysis
            if ai_result:
                results.append(ai_result)
            else:
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
    """Enhanced keyword-based sentiment analysis with Indian market terms"""
    text = headline.lower()
    
    # Indian market specific terms
    strong_positive = [
        "surge", "soar", "record", "breakthrough", "rally", "boom", "skyrocket",
        "blockbuster", "stellar", "outperform", "beat estimates", "upgrade",
        "all-time high", "ath", "bullish breakout"
    ]
    positive = [
        "gain", "rise", "growth", "bull", "profit", "strong", "up", "beat", "exceed",
        "optimistic", "recovery", "rebound", "accumulate", "buy", "outpace",
        "expansion", "dividend", "bonus", "fii buying"
    ]
    strong_negative = [
        "crash", "plunge", "collapse", "crisis", "dump", "tank", "plummet",
        "bloodbath", "meltdown", "sell-off", "circuit breaker"
    ]
    negative = [
        "drop", "fall", "bear", "loss", "decline", "weak", "down", "miss", "concern",
        "fear", "risk", "slowdown", "downgrade", "sell", "fii selling", "outflow"
    ]
    
    sp = sum(1 for w in strong_positive if w in text) * 2
    p = sum(1 for w in positive if w in text)
    sn = sum(1 for w in strong_negative if w in text) * 2
    n = sum(1 for w in negative if w in text)
    
    pos_score = sp + p
    neg_score = sn + n
    
    if pos_score > neg_score:
        raw_score = min(0.2 + (pos_score - neg_score) * 0.15, 1.0)
        label = "Strong Bullish" if sp > 0 else "Bullish"
        confidence = min(50 + pos_score * 10, 90)
        impact = "high" if sp > 0 else "medium"
    elif neg_score > pos_score:
        raw_score = max(-0.2 - (neg_score - pos_score) * 0.15, -1.0)
        label = "Strong Bearish" if sn > 0 else "Bearish"
        confidence = min(50 + neg_score * 10, 90)
        impact = "high" if sn > 0 else "medium"
    else:
        raw_score = 0.0
        label = "Neutral"
        confidence = 50
        impact = "low"
    
    # Extract key factors
    factors = []
    for w in strong_positive + positive + strong_negative + negative:
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
        "market_impact": impact,
        "ai_analyzed": False
    }


@news_router.get("/sentiment/history")
async def get_sentiment_history(
    symbol: Optional[str] = None,
    limit: int = 50,
    user=Depends(get_current_user)
):
    """Get historical sentiment analysis results"""
    query = {"user_id": user["id"]}
    if symbol:
        query["symbols"] = symbol.upper()
    
    results = await db.sentiment_analysis.find(query, {"_id": 0}).sort("analyzed_at", -1).to_list(limit)
    return results


@news_router.get("/sentiment/aggregate/{symbol}")
async def get_symbol_sentiment_aggregate(
    symbol: str,
    hours: int = 24,
    user=Depends(get_current_user)
):
    """Get aggregated sentiment for a symbol over time period"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Get recent sentiment data
    results = await db.sentiment_analysis.find({
        "symbols": symbol.upper(),
        "analyzed_at": {"$gte": cutoff.isoformat()}
    }, {"_id": 0}).to_list(100)
    
    if not results:
        # Return default neutral if no data
        return {
            "symbol": symbol.upper(),
            "period_hours": hours,
            "avg_score": 0.1,  # Slightly positive default
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


@news_router.get("/trending")
async def get_trending_topics(user=Depends(get_current_user)):
    """Get trending market topics"""
    # Aggregate recent sentiment by symbol
    recent = await db.sentiment_analysis.find(
        {"analyzed_at": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()}},
        {"_id": 0}
    ).to_list(500)
    
    symbol_scores = {}
    for r in recent:
        symbols = r.get("symbols", [])
        for sym in symbols:
            if sym not in symbol_scores:
                symbol_scores[sym] = {"scores": [], "count": 0}
            symbol_scores[sym]["scores"].append(r["score"])
            symbol_scores[sym]["count"] += 1
    
    trending = []
    for sym, data in symbol_scores.items():
        if data["count"] >= 2:
            avg = sum(data["scores"]) / len(data["scores"])
            trending.append({
                "symbol": sym,
                "avg_sentiment": round(avg, 3),
                "mentions": data["count"],
                "trend": "bullish" if avg > 0.2 else "bearish" if avg < -0.2 else "neutral"
            })
    
    trending.sort(key=lambda x: x["mentions"], reverse=True)
    return trending[:10]
