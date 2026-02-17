"""
Machine Learning Bot Builder Service
AutoML, Guided, and Advanced modes for ML-based trading strategies
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import xgboost as xgb
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import pickle
import base64
import logging
import uuid

logger = logging.getLogger(__name__)


# Pre-trained model templates
MODEL_TEMPLATES = {
    "trend_classifier": {
        "name": "Trend Direction Classifier",
        "description": "Predicts if price will go up or down based on technical indicators",
        "type": "classification",
        "features": ["rsi", "macd", "sma_20", "ema_9", "bb_position", "volume_ratio"],
        "target": "next_direction",
        "model_type": "xgboost",
        "default_params": {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1
        }
    },
    "volatility_predictor": {
        "name": "Volatility Predictor",
        "description": "Predicts high/low volatility periods using ATR and historical volatility",
        "type": "classification",
        "features": ["atr", "historical_vol", "bb_width", "volume_change", "price_range"],
        "target": "high_volatility",
        "model_type": "random_forest",
        "default_params": {
            "n_estimators": 50,
            "max_depth": 8
        }
    },
    "momentum_scorer": {
        "name": "Momentum Score Predictor",
        "description": "Scores momentum strength for entry timing",
        "type": "classification",
        "features": ["rsi", "macd_histogram", "adx", "plus_di", "minus_di", "roc"],
        "target": "strong_momentum",
        "model_type": "gradient_boosting",
        "default_params": {
            "n_estimators": 80,
            "max_depth": 4,
            "learning_rate": 0.1
        }
    },
    "reversal_detector": {
        "name": "Reversal Pattern Detector",
        "description": "Detects potential trend reversal points",
        "type": "classification",
        "features": ["rsi", "stoch_k", "stoch_d", "bb_position", "volume_spike", "candle_pattern"],
        "target": "reversal_signal",
        "model_type": "xgboost",
        "default_params": {
            "n_estimators": 120,
            "max_depth": 6,
            "learning_rate": 0.08
        }
    },
    "breakout_predictor": {
        "name": "Breakout Probability Predictor",
        "description": "Predicts likelihood of price breakouts from consolidation",
        "type": "classification",
        "features": ["bb_squeeze", "volume_ratio", "atr_ratio", "price_compression", "donchian_position"],
        "target": "breakout_soon",
        "model_type": "xgboost",
        "default_params": {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1
        }
    }
}


def compute_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute ML features from OHLCV data"""
    features = pd.DataFrame(index=df.index)
    
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']
    
    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    features['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    features['macd'] = ema_12 - ema_26
    features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
    features['macd_histogram'] = features['macd'] - features['macd_signal']
    
    # Moving Averages
    features['sma_20'] = close.rolling(20).mean()
    features['ema_9'] = close.ewm(span=9, adjust=False).mean()
    features['sma_50'] = close.rolling(50).mean()
    
    # Price vs MA ratio
    features['price_sma20_ratio'] = close / (features['sma_20'] + 1e-10)
    features['price_ema9_ratio'] = close / (features['ema_9'] + 1e-10)
    
    # Bollinger Bands
    bb_sma = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    features['bb_upper'] = bb_sma + 2 * bb_std
    features['bb_lower'] = bb_sma - 2 * bb_std
    features['bb_width'] = (features['bb_upper'] - features['bb_lower']) / (bb_sma + 1e-10)
    features['bb_position'] = (close - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'] + 1e-10)
    features['bb_squeeze'] = features['bb_width'].rolling(20).apply(lambda x: 1 if x.iloc[-1] < x.mean() else 0, raw=False)
    
    # ATR
    high_low = high - low
    high_close = abs(high - close.shift())
    low_close = abs(low - close.shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    features['atr'] = tr.ewm(alpha=1/14, min_periods=14).mean()
    features['atr_ratio'] = features['atr'] / close
    
    # Historical Volatility
    log_returns = np.log(close / close.shift())
    features['historical_vol'] = log_returns.rolling(20).std() * np.sqrt(252)
    
    # Volume features
    features['volume_sma'] = volume.rolling(20).mean()
    features['volume_ratio'] = volume / (features['volume_sma'] + 1e-10)
    features['volume_change'] = volume.pct_change()
    features['volume_spike'] = (features['volume_ratio'] > 2).astype(int)
    
    # ADX
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = pd.Series(np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0), index=df.index)
    minus_dm = pd.Series(np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0), index=df.index)
    
    atr_14 = tr.ewm(alpha=1/14, min_periods=14).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1/14, min_periods=14).mean() / (atr_14 + 1e-10)
    minus_di = 100 * minus_dm.ewm(alpha=1/14, min_periods=14).mean() / (atr_14 + 1e-10)
    
    features['plus_di'] = plus_di
    features['minus_di'] = minus_di
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
    features['adx'] = dx.ewm(alpha=1/14, min_periods=14).mean()
    
    # Stochastic
    low_14 = low.rolling(14).min()
    high_14 = high.rolling(14).max()
    features['stoch_k'] = 100 * (close - low_14) / (high_14 - low_14 + 1e-10)
    features['stoch_d'] = features['stoch_k'].rolling(3).mean()
    
    # ROC
    features['roc'] = close.pct_change(12) * 100
    
    # Price range and compression
    features['price_range'] = (high - low) / close
    features['price_compression'] = features['price_range'].rolling(10).apply(lambda x: 1 if x.iloc[-1] < x.mean() * 0.7 else 0, raw=False)
    
    # Donchian
    features['donchian_upper'] = high.rolling(20).max()
    features['donchian_lower'] = low.rolling(20).min()
    features['donchian_position'] = (close - features['donchian_lower']) / (features['donchian_upper'] - features['donchian_lower'] + 1e-10)
    
    # Candle patterns (simplified)
    body = abs(close - df['open'])
    upper_wick = high - pd.concat([close, df['open']], axis=1).max(axis=1)
    lower_wick = pd.concat([close, df['open']], axis=1).min(axis=1) - low
    features['candle_pattern'] = np.where(body < (upper_wick + lower_wick) * 0.3, 1, 0)  # Doji-like
    
    return features


def compute_ml_targets(df: pd.DataFrame, lookahead: int = 5) -> pd.DataFrame:
    """Compute ML targets (what we want to predict)"""
    targets = pd.DataFrame(index=df.index)
    
    close = df['close']
    
    # Next direction (1 = up, 0 = down)
    future_return = close.shift(-lookahead) / close - 1
    targets['next_direction'] = (future_return > 0).astype(int)
    
    # Strong momentum (1 = strong up momentum)
    targets['strong_momentum'] = (future_return > 0.02).astype(int)
    
    # High volatility period
    returns = close.pct_change()
    vol = returns.rolling(20).std()
    future_vol = vol.shift(-lookahead)
    targets['high_volatility'] = (future_vol > vol.rolling(50).mean()).astype(int)
    
    # Reversal signal
    # Simple: direction changes within lookahead
    direction = np.sign(close.diff())
    future_direction = np.sign(close.shift(-lookahead) - close)
    targets['reversal_signal'] = (direction != future_direction).astype(int)
    
    # Breakout soon
    high_20 = df['high'].rolling(20).max()
    low_20 = df['low'].rolling(20).min()
    future_high = df['high'].shift(-lookahead).rolling(lookahead).max()
    future_low = df['low'].shift(-lookahead).rolling(lookahead).min()
    targets['breakout_soon'] = ((future_high > high_20) | (future_low < low_20)).astype(int)
    
    return targets


def train_model(
    features: pd.DataFrame,
    targets: pd.Series,
    model_type: str = "xgboost",
    params: Dict[str, Any] = None
) -> Tuple[Any, Dict[str, float], Any]:
    """Train a machine learning model"""
    
    # Clean data
    valid_idx = features.notna().all(axis=1) & targets.notna()
    X = features[valid_idx].values
    y = targets[valid_idx].values
    
    if len(X) < 100:
        raise ValueError("Insufficient data for training (need at least 100 samples)")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Initialize model
    params = params or {}
    
    if model_type == "xgboost":
        model = xgb.XGBClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 5),
            learning_rate=params.get("learning_rate", 0.1),
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
    elif model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 8),
            random_state=42
        )
    elif model_type == "gradient_boosting":
        model = GradientBoostingClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 5),
            learning_rate=params.get("learning_rate", 0.1),
            random_state=42
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Train
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    
    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }
    
    # Cross-validation score
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
    metrics["cv_accuracy_mean"] = round(cv_scores.mean(), 4)
    metrics["cv_accuracy_std"] = round(cv_scores.std(), 4)
    
    return model, metrics, scaler


def serialize_model(model: Any, scaler: Any, feature_names: List[str]) -> str:
    """Serialize model to base64 string for storage"""
    model_data = {
        "model": model,
        "scaler": scaler,
        "feature_names": feature_names,
        "version": "1.0"
    }
    pickled = pickle.dumps(model_data)
    return base64.b64encode(pickled).decode('utf-8')


def deserialize_model(model_str: str) -> Tuple[Any, Any, List[str]]:
    """Deserialize model from base64 string"""
    pickled = base64.b64decode(model_str.encode('utf-8'))
    model_data = pickle.loads(pickled)
    return model_data["model"], model_data["scaler"], model_data["feature_names"]


def predict_with_model(
    model: Any,
    scaler: Any,
    features: pd.DataFrame,
    feature_names: List[str]
) -> Tuple[np.ndarray, np.ndarray]:
    """Make predictions with a trained model"""
    # Select only the features used in training
    X = features[feature_names].iloc[-1:].values
    X_scaled = scaler.transform(X)
    
    prediction = model.predict(X_scaled)[0]
    probabilities = model.predict_proba(X_scaled)[0]
    
    return prediction, probabilities


class MLBotBuilder:
    """
    Machine Learning Bot Builder
    Supports AutoML, Guided, and Advanced modes
    """
    
    def __init__(self, db):
        self.db = db
    
    async def automl_train(
        self,
        ohlcv_data: List[Dict[str, Any]],
        target_type: str = "next_direction",
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        AutoML mode: Automatically select best model and parameters
        """
        df = pd.DataFrame(ohlcv_data)
        features = compute_ml_features(df)
        targets = compute_ml_targets(df)
        
        if target_type not in targets.columns:
            raise ValueError(f"Unknown target type: {target_type}")
        
        target = targets[target_type]
        
        # Try multiple model types
        results = []
        best_model = None
        best_metrics = None
        best_scaler = None
        best_type = None
        
        for model_type in ["xgboost", "random_forest", "gradient_boosting"]:
            try:
                model, metrics, scaler = train_model(features, target, model_type)
                results.append({
                    "model_type": model_type,
                    "metrics": metrics
                })
                
                # Track best model by CV accuracy
                if best_metrics is None or metrics["cv_accuracy_mean"] > best_metrics["cv_accuracy_mean"]:
                    best_model = model
                    best_metrics = metrics
                    best_scaler = scaler
                    best_type = model_type
            except Exception as e:
                logger.warning(f"Failed to train {model_type}: {e}")
        
        if best_model is None:
            raise ValueError("All model training attempts failed")
        
        # Serialize and store
        feature_names = list(features.columns)
        model_str = serialize_model(best_model, best_scaler, feature_names)
        
        model_id = str(uuid.uuid4())
        model_doc = {
            "id": model_id,
            "user_id": user_id,
            "name": f"AutoML {target_type.replace('_', ' ').title()}",
            "mode": "automl",
            "model_type": best_type,
            "target_type": target_type,
            "metrics": best_metrics,
            "feature_names": feature_names,
            "model_data": model_str,
            "all_results": results,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.ml_models.insert_one(model_doc)
        
        return {
            "model_id": model_id,
            "best_model_type": best_type,
            "metrics": best_metrics,
            "all_results": results
        }
    
    async def guided_train(
        self,
        ohlcv_data: List[Dict[str, Any]],
        template_id: str,
        custom_params: Dict[str, Any] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Guided mode: Use pre-configured templates with optional customization
        """
        if template_id not in MODEL_TEMPLATES:
            raise ValueError(f"Unknown template: {template_id}")
        
        template = MODEL_TEMPLATES[template_id]
        
        df = pd.DataFrame(ohlcv_data)
        features = compute_ml_features(df)
        targets = compute_ml_targets(df)
        
        # Select features from template
        available_features = [f for f in template["features"] if f in features.columns]
        if not available_features:
            raise ValueError("No valid features found for this template")
        
        feature_subset = features[available_features]
        target = targets[template["target"]]
        
        # Merge default params with custom
        params = {**template["default_params"], **(custom_params or {})}
        
        model, metrics, scaler = train_model(
            feature_subset,
            target,
            template["model_type"],
            params
        )
        
        # Serialize and store
        model_str = serialize_model(model, scaler, available_features)
        
        model_id = str(uuid.uuid4())
        model_doc = {
            "id": model_id,
            "user_id": user_id,
            "name": template["name"],
            "description": template["description"],
            "mode": "guided",
            "template_id": template_id,
            "model_type": template["model_type"],
            "target_type": template["target"],
            "params": params,
            "metrics": metrics,
            "feature_names": available_features,
            "model_data": model_str,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.ml_models.insert_one(model_doc)
        
        return {
            "model_id": model_id,
            "name": template["name"],
            "metrics": metrics,
            "features_used": available_features
        }
    
    async def advanced_train(
        self,
        ohlcv_data: List[Dict[str, Any]],
        model_type: str,
        target_type: str,
        feature_list: List[str],
        params: Dict[str, Any],
        name: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Advanced mode: Full control over model configuration
        """
        df = pd.DataFrame(ohlcv_data)
        features = compute_ml_features(df)
        targets = compute_ml_targets(df)
        
        # Validate features
        available_features = [f for f in feature_list if f in features.columns]
        if not available_features:
            raise ValueError("No valid features specified")
        
        if target_type not in targets.columns:
            raise ValueError(f"Unknown target type: {target_type}")
        
        feature_subset = features[available_features]
        target = targets[target_type]
        
        model, metrics, scaler = train_model(feature_subset, target, model_type, params)
        
        # Serialize and store
        model_str = serialize_model(model, scaler, available_features)
        
        model_id = str(uuid.uuid4())
        model_doc = {
            "id": model_id,
            "user_id": user_id,
            "name": name,
            "mode": "advanced",
            "model_type": model_type,
            "target_type": target_type,
            "params": params,
            "metrics": metrics,
            "feature_names": available_features,
            "model_data": model_str,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.ml_models.insert_one(model_doc)
        
        return {
            "model_id": model_id,
            "name": name,
            "metrics": metrics,
            "features_used": available_features
        }
    
    async def predict(
        self,
        model_id: str,
        ohlcv_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Make prediction using trained model
        """
        model_doc = await self.db.ml_models.find_one({"id": model_id}, {"_id": 0})
        if not model_doc:
            raise ValueError(f"Model not found: {model_id}")
        
        # Deserialize model
        model, scaler, feature_names = deserialize_model(model_doc["model_data"])
        
        # Compute features
        df = pd.DataFrame(ohlcv_data)
        features = compute_ml_features(df)
        
        # Make prediction
        prediction, probabilities = predict_with_model(model, scaler, features, feature_names)
        
        return {
            "model_id": model_id,
            "prediction": int(prediction),
            "prediction_label": "Positive" if prediction == 1 else "Negative",
            "confidence": float(max(probabilities)),
            "probabilities": {
                "negative": float(probabilities[0]),
                "positive": float(probabilities[1])
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
