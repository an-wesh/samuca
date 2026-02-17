import pandas as pd
import numpy as np

def compute_sma(series, period=20):
    return series.rolling(window=period, min_periods=1).mean()

def compute_ema(series, period=20):
    return series.ewm(span=period, adjust=False).mean()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def compute_bollinger_bands(series, period=20, std_dev=2):
    sma = series.rolling(window=period, min_periods=1).mean()
    rolling_std = series.rolling(window=period, min_periods=1).std().fillna(0)
    return sma + (rolling_std * std_dev), sma, sma - (rolling_std * std_dev)

def compute_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period, min_periods=1).mean()

def compute_volume_ma(df, period=20):
    return df['volume'].rolling(window=period, min_periods=1).mean()

def _safe_round(val, decimals=2):
    if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
        return None
    return round(float(val), decimals)

def compute_all_indicators(df):
    close = df['close']
    sma_20 = compute_sma(close, 20)
    ema_50 = compute_ema(close, 50)
    rsi_14 = compute_rsi(close, 14)
    macd_line, signal_line, macd_hist = compute_macd(close)
    bb_upper, bb_mid, bb_lower = compute_bollinger_bands(close)
    atr_14 = compute_atr(df, 14)
    vol_ma = compute_volume_ma(df, 20)
    timestamps = df['timestamp'].tolist()
    return {
        "timestamps": timestamps,
        "sma_20": [_safe_round(v) for v in sma_20.tolist()],
        "ema_50": [_safe_round(v) for v in ema_50.tolist()],
        "rsi_14": [_safe_round(v) for v in rsi_14.tolist()],
        "macd_line": [_safe_round(v, 4) for v in macd_line.tolist()],
        "macd_signal": [_safe_round(v, 4) for v in signal_line.tolist()],
        "macd_histogram": [_safe_round(v, 4) for v in macd_hist.tolist()],
        "bb_upper": [_safe_round(v) for v in bb_upper.tolist()],
        "bb_middle": [_safe_round(v) for v in bb_mid.tolist()],
        "bb_lower": [_safe_round(v) for v in bb_lower.tolist()],
        "atr_14": [_safe_round(v) for v in atr_14.tolist()],
        "volume_ma_20": [_safe_round(v) for v in vol_ma.tolist()],
    }

def evaluate_condition(indicator_data, idx, condition):
    ctype = condition.get("type", "")
    if ctype == "RSI":
        val = indicator_data.get("rsi_14", [None])[idx] if idx < len(indicator_data.get("rsi_14", [])) else None
        if val is None:
            return False
        op = condition.get("operator", "<")
        target = float(condition.get("value", 30))
        return (val < target) if op == "<" else (val > target) if op == ">" else False
    elif ctype == "MACD":
        hist = indicator_data.get("macd_histogram", [])
        if idx < 1 or idx >= len(hist) or hist[idx] is None or hist[idx - 1] is None:
            return False
        cond = condition.get("condition", "bullish_crossover")
        if cond == "bullish_crossover":
            return hist[idx] > 0 and hist[idx - 1] <= 0
        elif cond == "bearish_crossover":
            return hist[idx] < 0 and hist[idx - 1] >= 0
        elif cond == "positive":
            return hist[idx] > 0
        elif cond == "negative":
            return hist[idx] < 0
    elif ctype in ("SMA", "EMA"):
        key = "sma_20" if ctype == "SMA" else "ema_50"
        ind_val = indicator_data.get(key, [None])[idx] if idx < len(indicator_data.get(key, [])) else None
        close_val = indicator_data.get("_closes", [None])[idx] if idx < len(indicator_data.get("_closes", [])) else None
        if ind_val is None or close_val is None:
            return False
        op = condition.get("operator", "above")
        return (close_val > ind_val) if op == "above" else (close_val < ind_val)
    elif ctype == "BB":
        closes = indicator_data.get("_closes", [])
        bb_u = indicator_data.get("bb_upper", [])
        bb_l = indicator_data.get("bb_lower", [])
        if idx >= len(closes) or idx >= len(bb_u) or bb_u[idx] is None:
            return False
        cond = condition.get("condition", "below_lower")
        return (closes[idx] < bb_l[idx]) if cond == "below_lower" else (closes[idx] > bb_u[idx])
    return False

def evaluate_conditions(indicator_data, idx, section):
    conditions = section.get("conditions", [])
    logic = section.get("logic", "AND")
    if not conditions:
        return False
    results = [evaluate_condition(indicator_data, idx, c) for c in conditions]
    return all(results) if logic == "AND" else any(results)

def run_backtest(ohlcv_data, strategy, initial_capital=100000, commission_pct=0.1):
    df = pd.DataFrame(ohlcv_data)
    indicators = compute_all_indicators(df)
    indicators["_closes"] = df["close"].tolist()

    capital = initial_capital
    position = 0
    entry_price = 0
    trades = []
    equity_curve = []
    max_equity = initial_capital

    risk = strategy.get("risk", {})
    sl_pct = risk.get("stop_loss_pct", 5.0)
    tp_pct = risk.get("take_profit_pct", 10.0)
    max_pos_pct = risk.get("max_position_size_pct", 100.0)

    entry_section = strategy.get("entry", {})
    exit_section = strategy.get("exit", {})

    for i in range(50, len(df)):
        row = df.iloc[i]
        price = row["close"]
        ts = row["timestamp"]

        if position == 0:
            if evaluate_conditions(indicators, i, entry_section):
                max_invest = capital * (max_pos_pct / 100)
                qty = max_invest / price
                cost = qty * price * (1 + commission_pct / 100)
                if cost <= capital:
                    capital -= cost
                    position = qty
                    entry_price = price
                    trades.append({"type": "BUY", "price": round(price, 2), "quantity": round(qty, 6), "timestamp": ts, "capital_after": round(capital, 2)})
        elif position > 0:
            pnl_pct = (price - entry_price) / entry_price * 100
            should_exit = False
            reason = ""
            if pnl_pct <= -sl_pct:
                should_exit, reason = True, "Stop Loss"
            elif pnl_pct >= tp_pct:
                should_exit, reason = True, "Take Profit"
            elif evaluate_conditions(indicators, i, exit_section):
                should_exit, reason = True, "Signal"
            if should_exit:
                proceeds = position * price * (1 - commission_pct / 100)
                pnl = (price - entry_price) * position
                capital += proceeds
                trades.append({"type": "SELL", "price": round(price, 2), "quantity": round(position, 6), "timestamp": ts, "pnl": round(pnl, 2), "pnl_pct": round(pnl_pct, 2), "reason": reason, "capital_after": round(capital, 2)})
                position = 0
                entry_price = 0

        equity = capital + position * price
        max_equity = max(max_equity, equity)
        equity_curve.append({"timestamp": ts, "equity": round(equity, 2), "drawdown": round((equity - max_equity) / max_equity * 100, 2)})

    if position > 0:
        capital += position * df.iloc[-1]["close"] * (1 - commission_pct / 100)

    metrics = _compute_metrics(trades, equity_curve, initial_capital)
    return {"equity_curve": _sanitize(equity_curve), "trades": _sanitize(trades), "metrics": _sanitize(metrics)}

def _sanitize(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def _compute_metrics(trades, equity_curve, initial_capital):
    if not equity_curve:
        return {"total_return": 0, "sharpe_ratio": 0, "max_drawdown": 0, "win_rate": 0, "total_trades": 0}
    final_eq = equity_curve[-1]["equity"]
    total_ret = (final_eq - initial_capital) / initial_capital * 100
    sells = [t for t in trades if t["type"] == "SELL"]
    wins = [t for t in sells if t.get("pnl", 0) > 0]
    losses = [t for t in sells if t.get("pnl", 0) <= 0]
    win_rate = len(wins) / len(sells) * 100 if sells else 0
    gross_profit = sum(t.get("pnl", 0) for t in wins)
    gross_loss = abs(sum(t.get("pnl", 0) for t in losses))
    pf = gross_profit / gross_loss if gross_loss > 0 else 999
    max_dd = min(e["drawdown"] for e in equity_curve) if equity_curve else 0
    returns = []
    for i in range(1, len(equity_curve)):
        returns.append((equity_curve[i]["equity"] - equity_curve[i - 1]["equity"]) / equity_curve[i - 1]["equity"])
    avg_r = np.mean(returns) if returns else 0
    std_r = np.std(returns) if returns else 1
    sharpe = (avg_r / std_r * np.sqrt(252)) if std_r > 0 else 0
    downside = [r for r in returns if r < 0]
    ds_std = np.std(downside) if downside else 0.001
    sortino = (avg_r / ds_std * np.sqrt(252)) if ds_std > 0 else 0
    num_days = max(len(equity_curve) / 24, 1)
    cagr = ((final_eq / initial_capital) ** (365 / num_days) - 1) * 100

    return {
        "total_return": round(total_ret, 2), "cagr": round(cagr, 2),
        "sharpe_ratio": round(float(sharpe), 2), "sortino_ratio": round(float(sortino), 2),
        "max_drawdown": round(max_dd, 2), "win_rate": round(win_rate, 2),
        "profit_factor": round(min(pf, 999), 2), "total_trades": len(sells),
        "winning_trades": len(wins), "losing_trades": len(losses),
        "gross_profit": round(gross_profit, 2), "gross_loss": round(gross_loss, 2),
        "avg_win": round(gross_profit / len(wins), 2) if wins else 0,
        "avg_loss": round(gross_loss / len(losses), 2) if losses else 0,
        "final_equity": round(float(final_eq), 2), "initial_capital": initial_capital,
    }
