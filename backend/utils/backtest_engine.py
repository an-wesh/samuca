"""
Institutional-Grade Backtesting Engine
Candle-by-candle simulation with realistic costs, slippage, and advanced metrics
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
import logging

from utils.indicators import (
    compute_all_indicators,
    compute_sma, compute_ema, compute_rsi, compute_macd,
    compute_bollinger_bands, compute_supertrend, compute_stochastic,
    compute_adx, compute_atr, compute_vwap, compute_cci,
    compute_williams_r, compute_mfi, compute_aroon
)

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """Single trade record"""
    id: str
    type: str  # BUY or SELL
    timestamp: str
    price: float
    quantity: float
    value: float
    commission: float
    slippage: float
    total_cost: float
    capital_after: float
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    reason: Optional[str] = None
    holding_period: Optional[int] = None
    entry_price: Optional[float] = None


@dataclass
class EquityPoint:
    """Single equity curve data point"""
    timestamp: str
    equity: float
    cash: float
    positions_value: float
    drawdown: float
    drawdown_pct: float
    high_watermark: float


@dataclass
class BacktestMetrics:
    """Comprehensive backtest metrics"""
    # Returns
    total_return: float
    total_return_pct: float
    cagr: float
    
    # Risk-Adjusted Returns
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Drawdown
    max_drawdown: float
    max_drawdown_duration: int
    avg_drawdown: float
    
    # Trade Statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # P&L Metrics
    gross_profit: float
    gross_loss: float
    net_profit: float
    profit_factor: float
    
    # Average Metrics
    avg_win: float
    avg_loss: float
    avg_trade: float
    largest_win: float
    largest_loss: float
    
    # Risk Metrics
    expectancy: float
    payoff_ratio: float
    recovery_factor: float
    
    # Time Metrics
    avg_holding_period: float
    max_holding_period: int
    
    # Execution Metrics
    total_commission: float
    total_slippage: float
    total_costs: float
    
    # Final Values
    initial_capital: float
    final_equity: float


class BacktestEngine:
    """
    Institutional-grade backtesting engine with:
    - Candle-by-candle simulation
    - Realistic slippage modeling
    - Transaction costs
    - Multiple position management
    - Advanced risk metrics
    """
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission_pct: float = 0.1,
        slippage_pct: float = 0.05,
        position_sizing: str = "fixed_pct",  # fixed_pct, fixed_amount, risk_pct
        max_positions: int = 1,
        leverage: float = 1.0
    ):
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct / 100
        self.slippage_pct = slippage_pct / 100
        self.position_sizing = position_sizing
        self.max_positions = max_positions
        self.leverage = leverage
        
        # State
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        self.high_watermark = initial_capital
        
    def reset(self):
        """Reset engine state for new backtest"""
        self.capital = self.initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        self.high_watermark = self.initial_capital
        
    def calculate_slippage(self, price: float, side: str, volatility: float = 0.02) -> float:
        """
        Calculate realistic slippage based on:
        - Base slippage percentage
        - Market volatility
        - Order side (buys slip up, sells slip down)
        """
        # Add volatility-adjusted slippage
        effective_slippage = self.slippage_pct * (1 + volatility)
        
        if side == "BUY":
            return price * (1 + effective_slippage)
        else:
            return price * (1 - effective_slippage)
    
    def calculate_commission(self, value: float) -> float:
        """Calculate transaction commission"""
        return value * self.commission_pct
    
    def calculate_position_size(
        self,
        capital: float,
        price: float,
        risk: Dict[str, Any],
        atr: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on strategy
        """
        max_position_pct = risk.get("max_position_size_pct", 100) / 100
        max_capital_per_trade = risk.get("max_capital_per_trade", capital)
        
        available_capital = min(
            capital * max_position_pct,
            max_capital_per_trade
        ) * self.leverage
        
        if self.position_sizing == "risk_pct" and atr:
            # Risk-based position sizing using ATR
            risk_per_trade = capital * (risk.get("risk_per_trade_pct", 1) / 100)
            stop_distance = atr * 2  # 2x ATR stop
            quantity = risk_per_trade / stop_distance
        else:
            # Fixed percentage or amount sizing
            quantity = available_capital / price
            
        return quantity
    
    def open_position(
        self,
        timestamp: str,
        price: float,
        quantity: float,
        reason: str = "Signal"
    ) -> Optional[TradeRecord]:
        """Open a new position"""
        if len(self.positions) >= self.max_positions:
            return None
            
        # Calculate execution price with slippage
        exec_price = self.calculate_slippage(price, "BUY")
        value = exec_price * quantity
        commission = self.calculate_commission(value)
        slippage_cost = (exec_price - price) * quantity
        total_cost = value + commission
        
        if total_cost > self.capital:
            # Adjust quantity if not enough capital
            quantity = (self.capital - commission) / exec_price
            value = exec_price * quantity
            commission = self.calculate_commission(value)
            total_cost = value + commission
            
        if quantity <= 0 or total_cost > self.capital:
            return None
            
        self.capital -= total_cost
        
        trade = TradeRecord(
            id=f"T{len(self.trades)+1:04d}",
            type="BUY",
            timestamp=timestamp,
            price=exec_price,
            quantity=quantity,
            value=value,
            commission=commission,
            slippage=slippage_cost,
            total_cost=total_cost,
            capital_after=self.capital,
            reason=reason
        )
        
        self.positions.append({
            "entry_time": timestamp,
            "entry_price": exec_price,
            "quantity": quantity,
            "trade_id": trade.id
        })
        
        self.trades.append(trade)
        return trade
    
    def close_position(
        self,
        position_idx: int,
        timestamp: str,
        price: float,
        reason: str = "Signal"
    ) -> Optional[TradeRecord]:
        """Close an existing position"""
        if position_idx >= len(self.positions):
            return None
            
        pos = self.positions[position_idx]
        
        # Calculate execution price with slippage
        exec_price = self.calculate_slippage(price, "SELL")
        value = exec_price * pos["quantity"]
        commission = self.calculate_commission(value)
        slippage_cost = (price - exec_price) * pos["quantity"]
        proceeds = value - commission
        
        # Calculate P&L
        entry_value = pos["entry_price"] * pos["quantity"]
        pnl = proceeds - entry_value
        pnl_pct = (exec_price - pos["entry_price"]) / pos["entry_price"] * 100
        
        # Calculate holding period
        entry_ts = pos["entry_time"]
        if isinstance(entry_ts, str):
            entry_dt = datetime.fromisoformat(entry_ts.replace("Z", "+00:00"))
        else:
            entry_dt = datetime.fromtimestamp(float(entry_ts), tz=timezone.utc)
        
        if isinstance(timestamp, str):
            exit_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            exit_dt = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
        holding_period = int((exit_dt - entry_dt).total_seconds() / 3600)  # hours
        
        self.capital += proceeds
        
        trade = TradeRecord(
            id=f"T{len(self.trades)+1:04d}",
            type="SELL",
            timestamp=timestamp,
            price=exec_price,
            quantity=pos["quantity"],
            value=value,
            commission=commission,
            slippage=slippage_cost,
            total_cost=commission,
            capital_after=self.capital,
            pnl=pnl,
            pnl_pct=pnl_pct,
            reason=reason,
            holding_period=holding_period,
            entry_price=pos["entry_price"]
        )
        
        self.positions.pop(position_idx)
        self.trades.append(trade)
        return trade
    
    def update_equity(self, timestamp: str, current_price: float):
        """Update equity curve with current state"""
        positions_value = sum(p["quantity"] * current_price for p in self.positions)
        equity = self.capital + positions_value
        
        self.high_watermark = max(self.high_watermark, equity)
        drawdown = equity - self.high_watermark
        drawdown_pct = (drawdown / self.high_watermark) * 100 if self.high_watermark > 0 else 0
        
        self.equity_curve.append(EquityPoint(
            timestamp=timestamp,
            equity=equity,
            cash=self.capital,
            positions_value=positions_value,
            drawdown=drawdown,
            drawdown_pct=drawdown_pct,
            high_watermark=self.high_watermark
        ))
    
    def evaluate_condition(
        self,
        indicators: Dict[str, Any],
        idx: int,
        condition: Dict[str, Any],
        closes: List[float]
    ) -> bool:
        """Evaluate a single condition"""
        ctype = condition.get("type", "")
        
        def get_val(key: str) -> Optional[float]:
            vals = indicators.get(key, [])
            return vals[idx] if idx < len(vals) and vals[idx] is not None else None
        
        if ctype == "RSI":
            val = get_val("rsi_14")
            if val is None:
                return False
            op = condition.get("operator", "<")
            target = float(condition.get("value", 30))
            return (val < target) if op == "<" else (val > target)
            
        elif ctype == "MACD":
            hist = indicators.get("macd_histogram", [])
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
            period = condition.get("period", 20 if ctype == "SMA" else 50)
            key = f"{ctype.lower()}_{period}"
            ind_val = get_val(key) or get_val(f"sma_{period}") or get_val(f"ema_{period}")
            close_val = closes[idx] if idx < len(closes) else None
            if ind_val is None or close_val is None:
                return False
            op = condition.get("operator", "above")
            return (close_val > ind_val) if op == "above" else (close_val < ind_val)
            
        elif ctype == "BB":
            bb_u = get_val("bb_upper")
            bb_l = get_val("bb_lower")
            close_val = closes[idx] if idx < len(closes) else None
            if close_val is None or bb_u is None or bb_l is None:
                return False
            cond = condition.get("condition", "below_lower")
            return (close_val < bb_l) if cond == "below_lower" else (close_val > bb_u)
            
        elif ctype == "SUPERTREND":
            direction = get_val("supertrend_direction")
            supertrend = get_val("supertrend")
            close_val = closes[idx] if idx < len(closes) else None
            if direction is None or close_val is None:
                return False
            cond = condition.get("condition", "uptrend")
            if cond == "uptrend":
                return direction == 1
            elif cond == "downtrend":
                return direction == -1
            elif cond == "crossover_up":
                prev_dir = indicators.get("supertrend_direction", [None] * (idx + 1))[idx - 1] if idx > 0 else None
                return prev_dir == -1 and direction == 1
            elif cond == "crossover_down":
                prev_dir = indicators.get("supertrend_direction", [None] * (idx + 1))[idx - 1] if idx > 0 else None
                return prev_dir == 1 and direction == -1
                
        elif ctype == "STOCHASTIC":
            stoch_k = get_val("stoch_k")
            stoch_d = get_val("stoch_d")
            if stoch_k is None or stoch_d is None:
                return False
            cond = condition.get("condition", "oversold")
            if cond == "oversold":
                return stoch_k < 20
            elif cond == "overbought":
                return stoch_k > 80
            elif cond == "bullish_crossover":
                prev_k = indicators.get("stoch_k", [None] * (idx + 1))[idx - 1] if idx > 0 else None
                prev_d = indicators.get("stoch_d", [None] * (idx + 1))[idx - 1] if idx > 0 else None
                return prev_k is not None and prev_d is not None and prev_k <= prev_d and stoch_k > stoch_d
            elif cond == "bearish_crossover":
                prev_k = indicators.get("stoch_k", [None] * (idx + 1))[idx - 1] if idx > 0 else None
                prev_d = indicators.get("stoch_d", [None] * (idx + 1))[idx - 1] if idx > 0 else None
                return prev_k is not None and prev_d is not None and prev_k >= prev_d and stoch_k < stoch_d
                
        elif ctype == "ADX":
            adx = get_val("adx")
            plus_di = get_val("plus_di")
            minus_di = get_val("minus_di")
            if adx is None:
                return False
            cond = condition.get("condition", "strong_trend")
            threshold = condition.get("threshold", 25)
            if cond == "strong_trend":
                return adx > threshold
            elif cond == "weak_trend":
                return adx < threshold
            elif cond == "bullish":
                return plus_di is not None and minus_di is not None and plus_di > minus_di
            elif cond == "bearish":
                return plus_di is not None and minus_di is not None and minus_di > plus_di
                
        elif ctype == "VWAP":
            vwap = get_val("vwap")
            close_val = closes[idx] if idx < len(closes) else None
            if vwap is None or close_val is None:
                return False
            op = condition.get("operator", "above")
            return (close_val > vwap) if op == "above" else (close_val < vwap)
            
        elif ctype == "CCI":
            cci = get_val("cci")
            if cci is None:
                return False
            cond = condition.get("condition", "oversold")
            if cond == "oversold":
                return cci < -100
            elif cond == "overbought":
                return cci > 100
                
        elif ctype == "WILLIAMS_R":
            wr = get_val("williams_r")
            if wr is None:
                return False
            cond = condition.get("condition", "oversold")
            if cond == "oversold":
                return wr < -80
            elif cond == "overbought":
                return wr > -20
                
        elif ctype == "MFI":
            mfi = get_val("mfi")
            if mfi is None:
                return False
            cond = condition.get("condition", "oversold")
            if cond == "oversold":
                return mfi < 20
            elif cond == "overbought":
                return mfi > 80
                
        elif ctype == "AROON":
            aroon_up = get_val("aroon_up")
            aroon_down = get_val("aroon_down")
            if aroon_up is None or aroon_down is None:
                return False
            cond = condition.get("condition", "bullish")
            if cond == "bullish":
                return aroon_up > aroon_down and aroon_up > 70
            elif cond == "bearish":
                return aroon_down > aroon_up and aroon_down > 70
                
        return False
    
    def evaluate_conditions(
        self,
        indicators: Dict[str, Any],
        idx: int,
        section: Dict[str, Any],
        closes: List[float]
    ) -> bool:
        """Evaluate multiple conditions with AND/OR logic"""
        conditions = section.get("conditions", [])
        logic = section.get("logic", "AND")
        
        if not conditions:
            return False
            
        results = [self.evaluate_condition(indicators, idx, c, closes) for c in conditions]
        return all(results) if logic == "AND" else any(results)
    
    def check_risk_exit(
        self,
        position: Dict[str, Any],
        current_price: float,
        risk: Dict[str, Any],
        atr: Optional[float] = None
    ) -> Tuple[bool, str]:
        """Check if position should be closed due to risk rules"""
        entry_price = position["entry_price"]
        pnl_pct = (current_price - entry_price) / entry_price * 100
        
        # Stop Loss
        sl_pct = risk.get("stop_loss_pct", 5.0)
        if pnl_pct <= -sl_pct:
            return True, "Stop Loss"
            
        # Take Profit
        tp_pct = risk.get("take_profit_pct", 10.0)
        if pnl_pct >= tp_pct:
            return True, "Take Profit"
            
        # Trailing Stop (if implemented)
        trailing_stop = risk.get("trailing_stop_pct")
        if trailing_stop and hasattr(position, "highest_price"):
            trailing_level = position["highest_price"] * (1 - trailing_stop / 100)
            if current_price < trailing_level:
                return True, "Trailing Stop"
                
        return False, ""
    
    def calculate_metrics(self) -> BacktestMetrics:
        """Calculate comprehensive backtest metrics"""
        if not self.equity_curve:
            return self._empty_metrics()
            
        # Extract equity values
        equities = [e.equity for e in self.equity_curve]
        timestamps = [e.timestamp for e in self.equity_curve]
        
        final_equity = equities[-1]
        total_return = final_equity - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # CAGR calculation
        try:
            start_dt = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
            years = (end_dt - start_dt).total_seconds() / (365.25 * 24 * 3600)
            years = max(years, 1/365)  # Minimum 1 day
            cagr = ((final_equity / self.initial_capital) ** (1 / years) - 1) * 100
        except:
            cagr = total_return_pct
            
        # Daily returns for Sharpe/Sortino
        returns = []
        for i in range(1, len(equities)):
            if equities[i-1] > 0:
                returns.append((equities[i] - equities[i-1]) / equities[i-1])
                
        returns = np.array(returns) if returns else np.array([0])
        
        # Risk metrics
        avg_return = np.mean(returns)
        std_return = np.std(returns) if len(returns) > 1 else 0.001
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0.001
        
        # Annualization factor (assuming hourly data)
        ann_factor = np.sqrt(24 * 365)
        
        sharpe = (avg_return / std_return * ann_factor) if std_return > 0 else 0
        sortino = (avg_return / downside_std * ann_factor) if downside_std > 0 else 0
        
        # Drawdown analysis
        drawdowns = [e.drawdown_pct for e in self.equity_curve]
        max_dd = min(drawdowns) if drawdowns else 0
        avg_dd = np.mean([d for d in drawdowns if d < 0]) if any(d < 0 for d in drawdowns) else 0
        
        # Calculate max drawdown duration
        max_dd_duration = 0
        current_dd_duration = 0
        for e in self.equity_curve:
            if e.drawdown < 0:
                current_dd_duration += 1
                max_dd_duration = max(max_dd_duration, current_dd_duration)
            else:
                current_dd_duration = 0
                
        calmar = abs(total_return_pct / max_dd) if max_dd != 0 else 0
        
        # Trade analysis
        sells = [t for t in self.trades if t.type == "SELL"]
        wins = [t for t in sells if (t.pnl or 0) > 0]
        losses = [t for t in sells if (t.pnl or 0) <= 0]
        
        total_trades = len(sells)
        winning_trades = len(wins)
        losing_trades = len(losses)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        gross_profit = sum(t.pnl for t in wins if t.pnl)
        gross_loss = abs(sum(t.pnl for t in losses if t.pnl))
        net_profit = gross_profit - gross_loss
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 999
        
        avg_win = (gross_profit / winning_trades) if winning_trades > 0 else 0
        avg_loss = (gross_loss / losing_trades) if losing_trades > 0 else 0
        avg_trade = (net_profit / total_trades) if total_trades > 0 else 0
        
        largest_win = max((t.pnl for t in wins if t.pnl), default=0)
        largest_loss = abs(min((t.pnl for t in losses if t.pnl), default=0))
        
        # Expectancy and payoff
        expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * avg_loss)
        payoff_ratio = (avg_win / avg_loss) if avg_loss > 0 else 999
        
        # Recovery factor
        recovery_factor = abs(net_profit / max_dd) if max_dd != 0 else 0
        
        # Holding periods
        holding_periods = [t.holding_period for t in sells if t.holding_period is not None]
        avg_holding = np.mean(holding_periods) if holding_periods else 0
        max_holding = max(holding_periods, default=0)
        
        # Costs
        total_commission = sum(t.commission for t in self.trades)
        total_slippage = sum(t.slippage for t in self.trades)
        total_costs = total_commission + total_slippage
        
        return BacktestMetrics(
            total_return=round(total_return, 2),
            total_return_pct=round(total_return_pct, 2),
            cagr=round(cagr, 2),
            sharpe_ratio=round(float(sharpe), 2),
            sortino_ratio=round(float(sortino), 2),
            calmar_ratio=round(calmar, 2),
            max_drawdown=round(max_dd, 2),
            max_drawdown_duration=max_dd_duration,
            avg_drawdown=round(avg_dd, 2),
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=round(win_rate, 2),
            gross_profit=round(gross_profit, 2),
            gross_loss=round(gross_loss, 2),
            net_profit=round(net_profit, 2),
            profit_factor=round(min(profit_factor, 999), 2),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            avg_trade=round(avg_trade, 2),
            largest_win=round(largest_win, 2),
            largest_loss=round(largest_loss, 2),
            expectancy=round(expectancy, 2),
            payoff_ratio=round(min(payoff_ratio, 999), 2),
            recovery_factor=round(recovery_factor, 2),
            avg_holding_period=round(avg_holding, 1),
            max_holding_period=max_holding,
            total_commission=round(total_commission, 2),
            total_slippage=round(total_slippage, 2),
            total_costs=round(total_costs, 2),
            initial_capital=self.initial_capital,
            final_equity=round(final_equity, 2)
        )
    
    def _empty_metrics(self) -> BacktestMetrics:
        """Return empty metrics"""
        return BacktestMetrics(
            total_return=0, total_return_pct=0, cagr=0,
            sharpe_ratio=0, sortino_ratio=0, calmar_ratio=0,
            max_drawdown=0, max_drawdown_duration=0, avg_drawdown=0,
            total_trades=0, winning_trades=0, losing_trades=0, win_rate=0,
            gross_profit=0, gross_loss=0, net_profit=0, profit_factor=0,
            avg_win=0, avg_loss=0, avg_trade=0, largest_win=0, largest_loss=0,
            expectancy=0, payoff_ratio=0, recovery_factor=0,
            avg_holding_period=0, max_holding_period=0,
            total_commission=0, total_slippage=0, total_costs=0,
            initial_capital=self.initial_capital, final_equity=self.initial_capital
        )
    
    def run(
        self,
        ohlcv_data: List[Dict[str, Any]],
        strategy: Dict[str, Any],
        warmup_period: int = 50
    ) -> Dict[str, Any]:
        """
        Run candle-by-candle backtest simulation
        """
        self.reset()
        
        if len(ohlcv_data) < warmup_period + 10:
            return {"error": "Insufficient data for backtest"}
            
        # Convert to DataFrame and compute indicators
        df = pd.DataFrame(ohlcv_data)
        indicators = compute_all_indicators(df, include_advanced=True)
        closes = df["close"].tolist()
        
        # Extract strategy components
        entry_section = strategy.get("entry", {})
        exit_section = strategy.get("exit", {})
        risk = strategy.get("risk", {})
        
        # Simulation loop
        for i in range(warmup_period, len(df)):
            row = df.iloc[i]
            price = row["close"]
            timestamp = row["timestamp"]
            atr_val = indicators.get("atr_14", [None] * (i + 1))[i]
            
            # Update position high prices for trailing stops
            for pos in self.positions:
                if "highest_price" not in pos:
                    pos["highest_price"] = pos["entry_price"]
                pos["highest_price"] = max(pos["highest_price"], price)
            
            # Check existing positions for risk exits
            positions_to_close = []
            for idx, pos in enumerate(self.positions):
                should_exit, reason = self.check_risk_exit(pos, price, risk, atr_val)
                if should_exit:
                    positions_to_close.append((idx, reason))
                elif self.evaluate_conditions(indicators, i, exit_section, closes):
                    positions_to_close.append((idx, "Signal"))
            
            # Close positions (reverse order to maintain indices)
            for idx, reason in reversed(positions_to_close):
                self.close_position(idx, timestamp, price, reason)
            
            # Check for entry signals
            if len(self.positions) < self.max_positions:
                if self.evaluate_conditions(indicators, i, entry_section, closes):
                    quantity = self.calculate_position_size(self.capital, price, risk, atr_val)
                    if quantity > 0:
                        self.open_position(timestamp, price, quantity, "Signal")
            
            # Update equity curve
            self.update_equity(timestamp, price)
        
        # Close any remaining positions at end
        while self.positions:
            last_price = df.iloc[-1]["close"]
            last_ts = df.iloc[-1]["timestamp"]
            self.close_position(0, last_ts, last_price, "End of Test")
        
        # Calculate final metrics
        metrics = self.calculate_metrics()
        
        return {
            "equity_curve": [
                {
                    "timestamp": e.timestamp,
                    "equity": round(e.equity, 2),
                    "cash": round(e.cash, 2),
                    "positions_value": round(e.positions_value, 2),
                    "drawdown": round(e.drawdown, 2),
                    "drawdown_pct": round(e.drawdown_pct, 2),
                    "high_watermark": round(e.high_watermark, 2)
                }
                for e in self.equity_curve
            ],
            "trades": [
                {
                    "id": t.id,
                    "type": t.type,
                    "timestamp": t.timestamp,
                    "price": round(t.price, 2),
                    "quantity": round(t.quantity, 6),
                    "value": round(t.value, 2),
                    "commission": round(t.commission, 2),
                    "slippage": round(t.slippage, 2),
                    "pnl": round(t.pnl, 2) if t.pnl else None,
                    "pnl_pct": round(t.pnl_pct, 2) if t.pnl_pct else None,
                    "reason": t.reason,
                    "holding_period": t.holding_period,
                    "capital_after": round(t.capital_after, 2)
                }
                for t in self.trades
            ],
            "metrics": {
                "total_return": metrics.total_return,
                "total_return_pct": metrics.total_return_pct,
                "cagr": metrics.cagr,
                "sharpe_ratio": metrics.sharpe_ratio,
                "sortino_ratio": metrics.sortino_ratio,
                "calmar_ratio": metrics.calmar_ratio,
                "max_drawdown": metrics.max_drawdown,
                "max_drawdown_duration": metrics.max_drawdown_duration,
                "avg_drawdown": metrics.avg_drawdown,
                "total_trades": metrics.total_trades,
                "winning_trades": metrics.winning_trades,
                "losing_trades": metrics.losing_trades,
                "win_rate": metrics.win_rate,
                "gross_profit": metrics.gross_profit,
                "gross_loss": metrics.gross_loss,
                "net_profit": metrics.net_profit,
                "profit_factor": metrics.profit_factor,
                "avg_win": metrics.avg_win,
                "avg_loss": metrics.avg_loss,
                "avg_trade": metrics.avg_trade,
                "largest_win": metrics.largest_win,
                "largest_loss": metrics.largest_loss,
                "expectancy": metrics.expectancy,
                "payoff_ratio": metrics.payoff_ratio,
                "recovery_factor": metrics.recovery_factor,
                "avg_holding_period": metrics.avg_holding_period,
                "max_holding_period": metrics.max_holding_period,
                "total_commission": metrics.total_commission,
                "total_slippage": metrics.total_slippage,
                "total_costs": metrics.total_costs,
                "initial_capital": metrics.initial_capital,
                "final_equity": metrics.final_equity
            }
        }


def run_backtest(
    ohlcv_data: List[Dict[str, Any]],
    strategy: Dict[str, Any],
    initial_capital: float = 100000,
    commission_pct: float = 0.1,
    slippage_pct: float = 0.05
) -> Dict[str, Any]:
    """
    Convenience function to run a backtest
    """
    engine = BacktestEngine(
        initial_capital=initial_capital,
        commission_pct=commission_pct,
        slippage_pct=slippage_pct
    )
    return engine.run(ohlcv_data, strategy)
