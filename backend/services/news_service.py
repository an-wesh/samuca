"""
Real News API Service
Fetches financial news from multiple sources
"""
import aiohttp
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Free News APIs
NEWS_APIS = {
    "gnews": {
        "base_url": "https://gnews.io/api/v4/search",
        "key_env": "GNEWS_API_KEY"
    },
    "newsapi": {
        "base_url": "https://newsapi.org/v2/everything",
        "key_env": "NEWS_API_KEY"
    }
}

# Default API key (GNews free tier)
DEFAULT_GNEWS_KEY = "demo"  # Will be replaced with actual key

# Topic mappings for stock symbols
SYMBOL_TOPICS = {
    # NSE Stocks
    "RELIANCE.NS": ["Reliance Industries", "Mukesh Ambani", "Jio"],
    "TCS.NS": ["TCS", "Tata Consultancy Services"],
    "HDFCBANK.NS": ["HDFC Bank", "HDFC"],
    "INFY.NS": ["Infosys", "Narayana Murthy"],
    "ICICIBANK.NS": ["ICICI Bank"],
    "SBIN.NS": ["SBI", "State Bank of India"],
    "BHARTIARTL.NS": ["Bharti Airtel", "Airtel"],
    "TATAMOTORS.NS": ["Tata Motors", "Tata Cars"],
    "TATASTEEL.NS": ["Tata Steel"],
    "WIPRO.NS": ["Wipro"],
    "HCLTECH.NS": ["HCL Tech", "HCL Technologies"],
    "MARUTI.NS": ["Maruti Suzuki", "Maruti"],
    "SUNPHARMA.NS": ["Sun Pharma", "Sun Pharmaceutical"],
    "AXISBANK.NS": ["Axis Bank"],
    "KOTAKBANK.NS": ["Kotak Mahindra Bank", "Kotak Bank"],
    "ADANIENT.NS": ["Adani", "Adani Enterprises", "Gautam Adani"],
    "BAJFINANCE.NS": ["Bajaj Finance"],
    "TITAN.NS": ["Titan Company", "Titan Watch"],
    "ASIANPAINT.NS": ["Asian Paints"],
    "LT.NS": ["Larsen Toubro", "L&T"],
    # Crypto
    "BTCUSD": ["Bitcoin", "BTC", "cryptocurrency"],
    "ETHUSD": ["Ethereum", "ETH", "crypto"],
    # US Stocks
    "AAPL": ["Apple", "iPhone", "Tim Cook"],
    "TSLA": ["Tesla", "Elon Musk", "Electric Vehicle"],
    "GOOGL": ["Google", "Alphabet", "Sundar Pichai"],
    "MSFT": ["Microsoft", "Satya Nadella", "Azure"],
    "AMZN": ["Amazon", "AWS", "Jeff Bezos"],
    "NVDA": ["NVIDIA", "Jensen Huang", "GPU"],
    "META": ["Meta", "Facebook", "Mark Zuckerberg"],
    "SPY": ["S&P 500", "US Stock Market", "Wall Street"],
}

# Sector news topics
SECTOR_TOPICS = {
    "Banking": ["RBI", "interest rates", "Indian banks", "banking sector"],
    "IT": ["IT sector", "tech stocks India", "software services"],
    "Pharma": ["pharma sector", "drug approval", "FDA India"],
    "Automobile": ["auto sector India", "EV India", "vehicle sales"],
    "FMCG": ["FMCG India", "consumer goods"],
    "Metal": ["steel prices", "metal sector India", "commodity prices"],
    "Energy": ["oil prices", "ONGC", "energy sector India"],
    "Real Estate": ["real estate India", "property market"],
    "Telecom": ["telecom India", "5G India"],
    "Power": ["power sector", "renewable energy India"],
}


async def fetch_gnews(query: str, max_results: int = 10, api_key: str = None) -> List[Dict[str, Any]]:
    """Fetch news from GNews API"""
    api_key = api_key or os.environ.get("GNEWS_API_KEY", DEFAULT_GNEWS_KEY)
    
    url = f"https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "max": min(max_results, 10),
        "apikey": api_key
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get("articles", [])
                    
                    return [{
                        "title": a.get("title", ""),
                        "description": a.get("description", ""),
                        "source": a.get("source", {}).get("name", "Unknown"),
                        "url": a.get("url", ""),
                        "published_at": a.get("publishedAt", ""),
                        "image": a.get("image", "")
                    } for a in articles]
                else:
                    logger.warning(f"GNews API error: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"GNews fetch error: {e}")
        return []


async def fetch_newsapi(query: str, max_results: int = 10, api_key: str = None) -> List[Dict[str, Any]]:
    """Fetch news from NewsAPI.org"""
    api_key = api_key or os.environ.get("NEWS_API_KEY")
    
    if not api_key:
        return []
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": min(max_results, 20),
        "apiKey": api_key
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get("articles", [])
                    
                    return [{
                        "title": a.get("title", ""),
                        "description": a.get("description", ""),
                        "source": a.get("source", {}).get("name", "Unknown"),
                        "url": a.get("url", ""),
                        "published_at": a.get("publishedAt", ""),
                        "image": a.get("urlToImage", "")
                    } for a in articles]
                else:
                    logger.warning(f"NewsAPI error: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"NewsAPI fetch error: {e}")
        return []


async def fetch_news_for_symbol(symbol: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Fetch news for a specific stock symbol"""
    topics = SYMBOL_TOPICS.get(symbol, [symbol.replace(".NS", "")])
    query = " OR ".join(topics[:3])  # Use up to 3 topics
    
    # Try GNews first
    articles = await fetch_gnews(query, max_results)
    
    # Fallback to NewsAPI if GNews fails
    if not articles:
        articles = await fetch_newsapi(query, max_results)
    
    # Add symbol to each article
    for article in articles:
        article["symbol"] = symbol
        article["display_symbol"] = symbol.replace(".NS", "")
    
    return articles


async def fetch_news_for_sector(sector: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Fetch news for a sector"""
    topics = SECTOR_TOPICS.get(sector, [sector])
    query = " OR ".join(topics[:3])
    
    articles = await fetch_gnews(query, max_results)
    
    if not articles:
        articles = await fetch_newsapi(query, max_results)
    
    for article in articles:
        article["sector"] = sector
    
    return articles


async def fetch_market_news(max_results: int = 20) -> List[Dict[str, Any]]:
    """Fetch general market news"""
    queries = [
        "Indian stock market",
        "NSE BSE Sensex Nifty",
        "RBI monetary policy"
    ]
    
    all_articles = []
    for query in queries:
        articles = await fetch_gnews(query, max_results // len(queries))
        all_articles.extend(articles)
    
    # Deduplicate by title
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        if article["title"] not in seen_titles:
            seen_titles.add(article["title"])
            article["category"] = "Market"
            unique_articles.append(article)
    
    return unique_articles[:max_results]


async def fetch_crypto_news(max_results: int = 10) -> List[Dict[str, Any]]:
    """Fetch cryptocurrency news"""
    articles = await fetch_gnews("cryptocurrency Bitcoin Ethereum", max_results)
    
    for article in articles:
        article["category"] = "Crypto"
    
    return articles


# Fallback mock news when APIs fail
MOCK_NEWS_TEMPLATES = {
    "RELIANCE.NS": [
        {"title": "Reliance Industries announces major investment in green energy", "source": "Economic Times", "sentiment": "bullish"},
        {"title": "Jio's 5G rollout accelerates across India", "source": "Business Standard", "sentiment": "bullish"},
        {"title": "RIL Q4 results beat street expectations", "source": "Moneycontrol", "sentiment": "bullish"},
    ],
    "TCS.NS": [
        {"title": "TCS wins multi-billion dollar deal from global bank", "source": "Economic Times", "sentiment": "bullish"},
        {"title": "TCS expands AI capabilities with new innovation hub", "source": "Business Standard", "sentiment": "bullish"},
        {"title": "IT sector faces headwinds as global spending slows", "source": "Mint", "sentiment": "bearish"},
    ],
    "HDFCBANK.NS": [
        {"title": "HDFC Bank reports strong loan growth in Q4", "source": "Moneycontrol", "sentiment": "bullish"},
        {"title": "RBI maintains status quo on rates, banks rally", "source": "Economic Times", "sentiment": "bullish"},
        {"title": "HDFC Bank completes merger integration successfully", "source": "Business Standard", "sentiment": "bullish"},
    ],
    "default": [
        {"title": "Nifty hits new all-time high as FIIs turn buyers", "source": "Economic Times", "sentiment": "bullish"},
        {"title": "Indian markets outperform global peers", "source": "Mint", "sentiment": "bullish"},
        {"title": "RBI signals accommodative stance to support growth", "source": "Business Standard", "sentiment": "bullish"},
        {"title": "Market volatility increases amid global uncertainty", "source": "Moneycontrol", "sentiment": "neutral"},
        {"title": "India GDP growth exceeds expectations", "source": "Economic Times", "sentiment": "bullish"},
    ]
}


def get_mock_news(symbol: str = None, count: int = 5) -> List[Dict[str, Any]]:
    """Get mock news when APIs unavailable"""
    import uuid
    from datetime import datetime, timezone, timedelta
    import random
    
    templates = MOCK_NEWS_TEMPLATES.get(symbol, MOCK_NEWS_TEMPLATES["default"])
    
    news = []
    for i, template in enumerate(templates[:count]):
        hours_ago = random.randint(1, 48)
        timestamp = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()
        
        news.append({
            "id": str(uuid.uuid4()),
            "title": template["title"],
            "description": f"Latest news update about {symbol or 'Indian markets'}. " + template["title"],
            "source": template["source"],
            "url": "#",
            "published_at": timestamp,
            "image": None,
            "symbol": symbol,
            "display_symbol": symbol.replace(".NS", "") if symbol else None,
            "sentiment_hint": template.get("sentiment", "neutral")
        })
    
    return news
