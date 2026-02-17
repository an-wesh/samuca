"""
Market Data API Routes
Provides real-time and historical market data for NSE stocks
"""
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, BackgroundTasks
from database import db, get_current_user
from typing import List, Optional
import asyncio
import json
import logging
from datetime import datetime, timezone

from data.nse_stocks import get_all_symbols, get_sectors, ALL_NSE_STOCKS, US_STOCKS, CRYPTO_SYMBOLS
from services.market_data_service import (
    async_fetch_current_price, fetch_multiple_prices, 
    load_historical_data, refresh_all_prices
)

market_router = APIRouter(prefix="/api/market", tags=["market"])
logger = logging.getLogger(__name__)

# WebSocket connections
active_connections: List[WebSocket] = []

# Cache for prices (to reduce API calls)
price_cache = {}
cache_timestamp = None


@market_router.get("/symbols")
async def get_symbols(
    exchange: Optional[str] = None,
    sector: Optional[str] = None,
    search: Optional[str] = None,
    user=Depends(get_current_user)
):
    """Get all available trading symbols"""
    symbols = get_all_symbols()
    
    # Filter by exchange
    if exchange:
        symbols = [s for s in symbols if s["exchange"].lower() == exchange.lower()]
    
    # Filter by sector
    if sector:
        symbols = [s for s in symbols if s["sector"].lower() == sector.lower()]
    
    # Search filter
    if search:
        search_lower = search.lower()
        symbols = [s for s in symbols if 
                   search_lower in s["symbol"].lower() or 
                   search_lower in s["name"].lower()]
    
    return {
        "symbols": symbols,
        "total": len(symbols)
    }


@market_router.get("/sectors")
async def get_available_sectors(user=Depends(get_current_user)):
    """Get all available sectors"""
    return {
        "sectors": get_sectors(),
        "exchanges": ["NSE", "US", "Crypto"]
    }


@market_router.get("/ohlcv")
async def get_ohlcv(
    symbol: str = "RELIANCE.NS",
    timeframe: str = "1h",
    limit: int = 500,
    user=Depends(get_current_user)
):
    """Get OHLCV data for a symbol"""
    # Validate timeframe
    valid_timeframes = ["5m", "15m", "1h", "1d"]
    if timeframe not in valid_timeframes:
        timeframe = "1h"
    
    # Load data (fetches from Yahoo Finance if needed)
    data = await load_historical_data(db, symbol, timeframe)
    
    # Get last N candles
    data = data[-limit:] if len(data) > limit else data
    
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "data": data,
        "count": len(data)
    }


@market_router.get("/ohlcv/{symbol}")
async def get_symbol_ohlcv(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 500,
    user=Depends(get_current_user)
):
    """Get OHLCV data for a specific symbol"""
    return await get_ohlcv(symbol, timeframe, limit, user)


@market_router.get("/price/{symbol}")
async def get_symbol_price(symbol: str, user=Depends(get_current_user)):
    """Get current price for a symbol"""
    price_data = await async_fetch_current_price(symbol)
    
    if not price_data:
        raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
    
    return {
        "symbol": symbol,
        **price_data
    }


@market_router.get("/latest_prices")
async def get_latest_prices(
    symbols: Optional[str] = None,
    exchange: Optional[str] = None,
    user=Depends(get_current_user)
):
    """Get latest prices for multiple symbols"""
    global price_cache, cache_timestamp
    
    # Determine which symbols to fetch
    if symbols:
        symbol_list = [s.strip() for s in symbols.split(",")]
    elif exchange:
        if exchange.lower() == "nse":
            symbol_list = [s["symbol"] for s in ALL_NSE_STOCKS[:20]]  # Top 20 NSE
        elif exchange.lower() == "us":
            symbol_list = [s["symbol"] for s in US_STOCKS]
        elif exchange.lower() == "crypto":
            symbol_list = [s["symbol"] for s in CRYPTO_SYMBOLS]
        else:
            symbol_list = [s["symbol"] for s in ALL_NSE_STOCKS[:10]]
    else:
        # Default: Top NSE stocks + US + Crypto
        symbol_list = (
            [s["symbol"] for s in ALL_NSE_STOCKS[:10]] +
            [s["symbol"] for s in US_STOCKS[:3]] +
            [s["symbol"] for s in CRYPTO_SYMBOLS]
        )
    
    # Check cache (valid for 30 seconds)
    cache_key = ",".join(sorted(symbol_list))
    now = datetime.now(timezone.utc)
    
    if cache_timestamp and (now - cache_timestamp).total_seconds() < 30:
        if cache_key in price_cache:
            return price_cache[cache_key]
    
    # Fetch fresh prices
    prices = await fetch_multiple_prices(symbol_list)
    
    # Format response
    result = {}
    for sym, data in prices.items():
        display_sym = sym.replace(".NS", "")
        result[display_sym] = {
            "symbol": sym,
            "price": data.get("price", 0),
            "change": data.get("change", 0),
            "change_pct": data.get("change_pct", 0),
            "prev_close": data.get("prev_close", 0)
        }
    
    # Update cache
    price_cache[cache_key] = result
    cache_timestamp = now
    
    return result


@market_router.post("/refresh")
async def refresh_market_data(
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    """Trigger market data refresh"""
    symbols = [s["symbol"] for s in ALL_NSE_STOCKS[:50]]  # Refresh top 50
    
    async def refresh_task():
        await refresh_all_prices(db, symbols)
    
    background_tasks.add_task(refresh_task)
    
    return {"message": "Market data refresh initiated", "symbols_count": len(symbols)}


@market_router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    days: int = 30,
    interval: str = "1h",
    user=Depends(get_current_user)
):
    """Get historical data for a symbol"""
    # Load fresh data
    data = await load_historical_data(db, symbol, interval, force_refresh=True)
    
    return {
        "symbol": symbol,
        "interval": interval,
        "data": data,
        "count": len(data)
    }


@market_router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket for real-time price updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Initial symbols to track
        tracked_symbols = [s["symbol"] for s in ALL_NSE_STOCKS[:10]]
        
        while True:
            # Check for client messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                msg = json.loads(data)
                if msg.get("action") == "subscribe":
                    tracked_symbols = msg.get("symbols", tracked_symbols)
            except asyncio.TimeoutError:
                pass
            
            # Fetch and send prices
            prices = await fetch_multiple_prices(tracked_symbols[:20])  # Limit to 20
            
            await websocket.send_json({
                "type": "prices",
                "data": prices,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            await asyncio.sleep(10)  # Update every 10 seconds
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@market_router.get("/nifty50")
async def get_nifty50_prices(user=Depends(get_current_user)):
    """Get prices for all NIFTY 50 stocks"""
    from data.nse_stocks import NIFTY_50
    symbols = [s["symbol"] for s in NIFTY_50]
    prices = await fetch_multiple_prices(symbols)
    
    result = []
    for stock in NIFTY_50:
        price_data = prices.get(stock["symbol"], {})
        result.append({
            "symbol": stock["symbol"],
            "display_symbol": stock["symbol"].replace(".NS", ""),
            "name": stock["name"],
            "sector": stock["sector"],
            "price": price_data.get("price", 0),
            "change": price_data.get("change", 0),
            "change_pct": price_data.get("change_pct", 0)
        })
    
    return {"stocks": result, "count": len(result)}


@market_router.get("/sector/{sector}")
async def get_sector_stocks(sector: str, user=Depends(get_current_user)):
    """Get all stocks in a sector with prices"""
    from data.nse_stocks import STOCK_BY_SECTOR
    
    sector_stocks = STOCK_BY_SECTOR.get(sector, [])
    if not sector_stocks:
        raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found")
    
    symbols = [s["symbol"] for s in sector_stocks]
    prices = await fetch_multiple_prices(symbols)
    
    result = []
    for stock in sector_stocks:
        price_data = prices.get(stock["symbol"], {})
        result.append({
            "symbol": stock["symbol"],
            "display_symbol": stock["symbol"].replace(".NS", ""),
            "name": stock["name"],
            "sector": stock["sector"],
            "price": price_data.get("price", 0),
            "change": price_data.get("change", 0),
            "change_pct": price_data.get("change_pct", 0)
        })
    
    return {"sector": sector, "stocks": result, "count": len(result)}
