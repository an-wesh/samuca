"""
Machine Learning Bot Builder API Routes
AutoML, Guided, and Advanced modes for ML-based trading strategies
"""
from fastapi import APIRouter, Depends, HTTPException
from database import db, get_current_user
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from services.ml_service import (
    MLBotBuilder, MODEL_TEMPLATES, compute_ml_features, compute_ml_targets
)
from services.market_data_service import load_historical_data

ml_router = APIRouter(prefix="/api/ml", tags=["machine_learning"])
logger = logging.getLogger(__name__)


class AutoMLRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    target_type: str = "next_direction"


class GuidedTrainRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    template_id: str
    custom_params: Optional[Dict[str, Any]] = None


class AdvancedTrainRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    name: str
    model_type: str  # xgboost, random_forest, gradient_boosting
    target_type: str
    features: List[str]
    params: Dict[str, Any]


class PredictRequest(BaseModel):
    model_id: str
    symbol: str
    timeframe: str = "1h"


@ml_router.get("/templates")
async def get_model_templates(user=Depends(get_current_user)):
    """Get available pre-trained model templates"""
    return {
        "templates": [
            {
                "id": tid,
                "name": t["name"],
                "description": t["description"],
                "type": t["type"],
                "model_type": t["model_type"],
                "features": t["features"],
                "target": t["target"],
                "default_params": t["default_params"]
            }
            for tid, t in MODEL_TEMPLATES.items()
        ]
    }


@ml_router.get("/features")
async def get_available_features(user=Depends(get_current_user)):
    """Get list of all available ML features"""
    return {
        "features": [
            # RSI
            {"name": "rsi", "category": "Momentum", "description": "Relative Strength Index (14)"},
            # MACD
            {"name": "macd", "category": "Momentum", "description": "MACD Line"},
            {"name": "macd_signal", "category": "Momentum", "description": "MACD Signal Line"},
            {"name": "macd_histogram", "category": "Momentum", "description": "MACD Histogram"},
            # Moving Averages
            {"name": "sma_20", "category": "Trend", "description": "20-period SMA"},
            {"name": "ema_9", "category": "Trend", "description": "9-period EMA"},
            {"name": "sma_50", "category": "Trend", "description": "50-period SMA"},
            {"name": "price_sma20_ratio", "category": "Trend", "description": "Price/SMA20 Ratio"},
            {"name": "price_ema9_ratio", "category": "Trend", "description": "Price/EMA9 Ratio"},
            # Bollinger Bands
            {"name": "bb_upper", "category": "Volatility", "description": "Upper Bollinger Band"},
            {"name": "bb_lower", "category": "Volatility", "description": "Lower Bollinger Band"},
            {"name": "bb_width", "category": "Volatility", "description": "Bollinger Band Width"},
            {"name": "bb_position", "category": "Volatility", "description": "Price position within BB (0-1)"},
            {"name": "bb_squeeze", "category": "Volatility", "description": "BB Squeeze indicator (0/1)"},
            # ATR & Volatility
            {"name": "atr", "category": "Volatility", "description": "Average True Range (14)"},
            {"name": "atr_ratio", "category": "Volatility", "description": "ATR/Price Ratio"},
            {"name": "historical_vol", "category": "Volatility", "description": "20-day Historical Volatility"},
            # Volume
            {"name": "volume_sma", "category": "Volume", "description": "20-period Volume SMA"},
            {"name": "volume_ratio", "category": "Volume", "description": "Volume/Average Volume Ratio"},
            {"name": "volume_change", "category": "Volume", "description": "Volume Change %"},
            {"name": "volume_spike", "category": "Volume", "description": "Volume Spike indicator (0/1)"},
            # ADX
            {"name": "adx", "category": "Trend Strength", "description": "Average Directional Index"},
            {"name": "plus_di", "category": "Trend Strength", "description": "+DI"},
            {"name": "minus_di", "category": "Trend Strength", "description": "-DI"},
            # Stochastic
            {"name": "stoch_k", "category": "Momentum", "description": "Stochastic %K"},
            {"name": "stoch_d", "category": "Momentum", "description": "Stochastic %D"},
            # ROC
            {"name": "roc", "category": "Momentum", "description": "Rate of Change (12)"},
            # Price Range
            {"name": "price_range", "category": "Volatility", "description": "High-Low Range / Close"},
            {"name": "price_compression", "category": "Volatility", "description": "Price Compression (0/1)"},
            # Donchian
            {"name": "donchian_upper", "category": "Trend", "description": "20-day Donchian Upper"},
            {"name": "donchian_lower", "category": "Trend", "description": "20-day Donchian Lower"},
            {"name": "donchian_position", "category": "Trend", "description": "Price position in Donchian (0-1)"},
            # Candle
            {"name": "candle_pattern", "category": "Pattern", "description": "Doji-like pattern (0/1)"},
        ],
        "targets": [
            {"name": "next_direction", "description": "Predict if price goes up (1) or down (0) in next N candles"},
            {"name": "strong_momentum", "description": "Predict if strong upward momentum (>2% gain)"},
            {"name": "high_volatility", "description": "Predict high volatility period"},
            {"name": "reversal_signal", "description": "Predict trend reversal"},
            {"name": "breakout_soon", "description": "Predict breakout from consolidation"},
        ],
        "model_types": [
            {"name": "xgboost", "description": "XGBoost - Best for most cases, handles imbalanced data well"},
            {"name": "random_forest", "description": "Random Forest - Good for high-dimensional data"},
            {"name": "gradient_boosting", "description": "Gradient Boosting - Similar to XGBoost, slightly different algorithm"},
        ]
    }


@ml_router.post("/automl/train")
async def automl_train(req: AutoMLRequest, user=Depends(get_current_user)):
    """
    AutoML Training Mode
    Automatically selects the best model and parameters
    """
    # Load market data
    data = await load_historical_data(db, req.symbol, req.timeframe)
    
    if len(data) < 200:
        raise HTTPException(status_code=400, detail="Insufficient data for training (need at least 200 candles)")
    
    try:
        builder = MLBotBuilder(db)
        result = await builder.automl_train(
            data,
            req.target_type,
            user["id"]
        )
        return result
    except Exception as e:
        logger.error(f"AutoML training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_router.post("/guided/train")
async def guided_train(req: GuidedTrainRequest, user=Depends(get_current_user)):
    """
    Guided Training Mode
    Uses pre-configured templates with optional customization
    """
    if req.template_id not in MODEL_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown template: {req.template_id}")
    
    # Load market data
    data = await load_historical_data(db, req.symbol, req.timeframe)
    
    if len(data) < 200:
        raise HTTPException(status_code=400, detail="Insufficient data for training")
    
    try:
        builder = MLBotBuilder(db)
        result = await builder.guided_train(
            data,
            req.template_id,
            req.custom_params,
            user["id"]
        )
        return result
    except Exception as e:
        logger.error(f"Guided training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_router.post("/advanced/train")
async def advanced_train(req: AdvancedTrainRequest, user=Depends(get_current_user)):
    """
    Advanced Training Mode
    Full control over model configuration
    """
    valid_models = ["xgboost", "random_forest", "gradient_boosting"]
    if req.model_type not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model type. Choose from: {valid_models}")
    
    # Load market data
    data = await load_historical_data(db, req.symbol, req.timeframe)
    
    if len(data) < 200:
        raise HTTPException(status_code=400, detail="Insufficient data for training")
    
    try:
        builder = MLBotBuilder(db)
        result = await builder.advanced_train(
            data,
            req.model_type,
            req.target_type,
            req.features,
            req.params,
            req.name,
            user["id"]
        )
        return result
    except Exception as e:
        logger.error(f"Advanced training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_router.post("/predict")
async def make_prediction(req: PredictRequest, user=Depends(get_current_user)):
    """
    Make prediction using trained model
    """
    # Verify model ownership
    model = await db.ml_models.find_one({"id": req.model_id, "user_id": user["id"]}, {"_id": 0})
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Load latest market data
    data = await load_historical_data(db, req.symbol, req.timeframe)
    
    if len(data) < 50:
        raise HTTPException(status_code=400, detail="Insufficient data for prediction")
    
    try:
        builder = MLBotBuilder(db)
        result = await builder.predict(req.model_id, data)
        result["symbol"] = req.symbol
        result["model_name"] = model["name"]
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_router.get("/models")
async def list_models(user=Depends(get_current_user)):
    """List all user's trained models"""
    models = await db.ml_models.find(
        {"user_id": user["id"]},
        {"_id": 0, "model_data": 0}  # Exclude heavy model data
    ).sort("created_at", -1).to_list(50)
    return models


@ml_router.get("/models/{model_id}")
async def get_model(model_id: str, user=Depends(get_current_user)):
    """Get model details"""
    model = await db.ml_models.find_one(
        {"id": model_id, "user_id": user["id"]},
        {"_id": 0, "model_data": 0}
    )
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@ml_router.delete("/models/{model_id}")
async def delete_model(model_id: str, user=Depends(get_current_user)):
    """Delete a trained model"""
    result = await db.ml_models.delete_one({"id": model_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model deleted"}


@ml_router.get("/models/{model_id}/backtest")
async def backtest_model(
    model_id: str,
    symbol: str,
    timeframe: str = "1h",
    user=Depends(get_current_user)
):
    """
    Backtest a trained model on historical data
    """
    import pandas as pd
    from services.ml_service import deserialize_model, compute_ml_features
    
    # Get model
    model_doc = await db.ml_models.find_one({"id": model_id, "user_id": user["id"]}, {"_id": 0})
    if not model_doc:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Load data
    data = await load_historical_data(db, symbol, timeframe)
    if len(data) < 200:
        raise HTTPException(status_code=400, detail="Insufficient data")
    
    # Deserialize model
    model, scaler, feature_names = deserialize_model(model_doc["model_data"])
    
    # Compute features
    df = pd.DataFrame(data)
    features = compute_ml_features(df)
    
    # Make predictions for all data points
    valid_idx = features.notna().all(axis=1)
    X = features.loc[valid_idx, feature_names].values
    X_scaled = scaler.transform(X)
    
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    
    # Calculate backtest results
    closes = df.loc[valid_idx, 'close'].values
    timestamps = df.loc[valid_idx, 'timestamp'].values
    
    trades = []
    position = None
    total_pnl = 0
    wins = 0
    losses = 0
    
    for i in range(len(predictions) - 5):  # Leave 5 for forward-looking
        pred = predictions[i]
        prob = max(probabilities[i])
        
        if position is None and pred == 1 and prob > 0.6:  # Buy signal
            position = {
                "entry_idx": i,
                "entry_price": closes[i],
                "entry_time": int(timestamps[i])
            }
        elif position is not None:
            # Check exit conditions
            hold_time = i - position["entry_idx"]
            pnl_pct = (closes[i] - position["entry_price"]) / position["entry_price"] * 100
            
            exit_signal = (
                pred == 0 or  # Sell signal
                pnl_pct >= 3 or  # Take profit
                pnl_pct <= -2 or  # Stop loss
                hold_time >= 20  # Max hold time
            )
            
            if exit_signal:
                pnl = (closes[i] - position["entry_price"]) * 1  # Assume 1 unit
                total_pnl += pnl
                
                if pnl > 0:
                    wins += 1
                else:
                    losses += 1
                
                trades.append({
                    "entry_time": position["entry_time"],
                    "entry_price": round(position["entry_price"], 2),
                    "exit_time": int(timestamps[i]),
                    "exit_price": round(closes[i], 2),
                    "pnl": round(pnl, 2),
                    "pnl_pct": round(pnl_pct, 2),
                    "hold_candles": hold_time
                })
                position = None
    
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    return {
        "model_id": model_id,
        "symbol": symbol,
        "timeframe": timeframe,
        "metrics": {
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "avg_pnl_per_trade": round(total_pnl / total_trades, 2) if total_trades > 0 else 0
        },
        "trades": trades[-20:]  # Last 20 trades
    }
