"""
Comprehensive Technical Indicators Library
Implements all indicators available on Zerodha Kite platform
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List


def safe_round(val, decimals=4):
    """Safely round values handling NaN/Inf"""
    if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
        return None
    return round(float(val), decimals)


def series_to_list(series: pd.Series, decimals=4) -> List:
    """Convert pandas series to list with safe rounding"""
    return [safe_round(v, decimals) for v in series.tolist()]


# =============================================================================
# TREND INDICATORS
# =============================================================================

def compute_sma(series: pd.Series, period: int = 20) -> pd.Series:
    """Simple Moving Average"""
    return series.rolling(window=period, min_periods=1).mean()


def compute_ema(series: pd.Series, period: int = 20) -> pd.Series:
    """Exponential Moving Average"""
    return series.ewm(span=period, adjust=False).mean()


def compute_wma(series: pd.Series, period: int = 20) -> pd.Series:
    """Weighted Moving Average"""
    weights = np.arange(1, period + 1)
    return series.rolling(window=period).apply(
        lambda x: np.dot(x, weights[-len(x):]) / weights[-len(x):].sum() if len(x) >= period else np.nan,
        raw=True
    )


def compute_dema(series: pd.Series, period: int = 20) -> pd.Series:
    """Double Exponential Moving Average"""
    ema1 = compute_ema(series, period)
    ema2 = compute_ema(ema1, period)
    return 2 * ema1 - ema2


def compute_tema(series: pd.Series, period: int = 20) -> pd.Series:
    """Triple Exponential Moving Average"""
    ema1 = compute_ema(series, period)
    ema2 = compute_ema(ema1, period)
    ema3 = compute_ema(ema2, period)
    return 3 * ema1 - 3 * ema2 + ema3


def compute_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Tuple[pd.Series, pd.Series]:
    """
    SuperTrend Indicator
    Returns: (supertrend_line, supertrend_direction: 1=uptrend, -1=downtrend)
    """
    atr = compute_atr(df, period)
    hl2 = (df['high'] + df['low']) / 2
    
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)
    
    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=float)
    
    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = upper_band.iloc[i]
            direction.iloc[i] = 1
            continue
            
        if df['close'].iloc[i] > supertrend.iloc[i-1]:
            supertrend.iloc[i] = max(lower_band.iloc[i], supertrend.iloc[i-1]) if direction.iloc[i-1] == 1 else lower_band.iloc[i]
            direction.iloc[i] = 1
        else:
            supertrend.iloc[i] = min(upper_band.iloc[i], supertrend.iloc[i-1]) if direction.iloc[i-1] == -1 else upper_band.iloc[i]
            direction.iloc[i] = -1
    
    return supertrend, direction


def compute_ichimoku(df: pd.DataFrame, tenkan: int = 9, kijun: int = 26, senkou_b: int = 52) -> Dict[str, pd.Series]:
    """
    Ichimoku Cloud Indicator
    Returns dict with: tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span
    """
    high = df['high']
    low = df['low']
    close = df['close']
    
    tenkan_sen = (high.rolling(window=tenkan).max() + low.rolling(window=tenkan).min()) / 2
    kijun_sen = (high.rolling(window=kijun).max() + low.rolling(window=kijun).min()) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    senkou_span_b = ((high.rolling(window=senkou_b).max() + low.rolling(window=senkou_b).min()) / 2).shift(kijun)
    chikou_span = close.shift(-kijun)
    
    return {
        'tenkan_sen': tenkan_sen,
        'kijun_sen': kijun_sen,
        'senkou_span_a': senkou_span_a,
        'senkou_span_b': senkou_span_b,
        'chikou_span': chikou_span
    }


def compute_parabolic_sar(df: pd.DataFrame, af_start: float = 0.02, af_step: float = 0.02, af_max: float = 0.2) -> pd.Series:
    """Parabolic SAR"""
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    length = len(df)
    
    psar = np.zeros(length)
    psarbull = np.zeros(length)
    psarbear = np.zeros(length)
    af = af_start
    ep = low[0]
    hp = high[0]
    lp = low[0]
    trend = 1
    
    for i in range(2, length):
        if trend == 1:
            psar[i] = psar[i-1] + af * (hp - psar[i-1])
            psar[i] = min(psar[i], low[i-1], low[i-2])
            
            if high[i] > hp:
                hp = high[i]
                af = min(af + af_step, af_max)
            if low[i] < psar[i]:
                trend = -1
                psar[i] = hp
                lp = low[i]
                af = af_start
        else:
            psar[i] = psar[i-1] + af * (lp - psar[i-1])
            psar[i] = max(psar[i], high[i-1], high[i-2])
            
            if low[i] < lp:
                lp = low[i]
                af = min(af + af_step, af_max)
            if high[i] > psar[i]:
                trend = 1
                psar[i] = lp
                hp = high[i]
                af = af_start
    
    return pd.Series(psar, index=df.index)


def compute_alligator(df: pd.DataFrame, jaw_period: int = 13, teeth_period: int = 8, lips_period: int = 5,
                     jaw_offset: int = 8, teeth_offset: int = 5, lips_offset: int = 3) -> Dict[str, pd.Series]:
    """
    Williams Alligator Indicator
    Returns: jaw (blue), teeth (red), lips (green)
    """
    hl2 = (df['high'] + df['low']) / 2
    
    jaw = compute_sma(hl2, jaw_period).shift(jaw_offset)
    teeth = compute_sma(hl2, teeth_period).shift(teeth_offset)
    lips = compute_sma(hl2, lips_period).shift(lips_offset)
    
    return {'jaw': jaw, 'teeth': teeth, 'lips': lips}


# =============================================================================
# MOMENTUM INDICATORS
# =============================================================================

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100 / (1 + rs))


def compute_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3, smooth_k: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator"""
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    
    stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min + 1e-10)
    stoch_k_smooth = stoch_k.rolling(window=smooth_k).mean()
    stoch_d = stoch_k_smooth.rolling(window=d_period).mean()
    
    return stoch_k_smooth, stoch_d


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Moving Average Convergence Divergence"""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Williams %R"""
    high_max = df['high'].rolling(window=period).max()
    low_min = df['low'].rolling(window=period).min()
    return -100 * (high_max - df['close']) / (high_max - low_min + 1e-10)


def compute_cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Commodity Channel Index"""
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return (tp - sma_tp) / (0.015 * mad + 1e-10)


def compute_momentum(series: pd.Series, period: int = 10) -> pd.Series:
    """Price Momentum"""
    return series - series.shift(period)


def compute_roc(series: pd.Series, period: int = 12) -> pd.Series:
    """Rate of Change"""
    return ((series - series.shift(period)) / (series.shift(period) + 1e-10)) * 100


def compute_tsi(series: pd.Series, long_period: int = 25, short_period: int = 13) -> pd.Series:
    """True Strength Index"""
    diff = series.diff()
    
    double_smoothed_pc = diff.ewm(span=long_period, adjust=False).mean().ewm(span=short_period, adjust=False).mean()
    double_smoothed_abs_pc = diff.abs().ewm(span=long_period, adjust=False).mean().ewm(span=short_period, adjust=False).mean()
    
    return 100 * double_smoothed_pc / (double_smoothed_abs_pc + 1e-10)


def compute_ultimate_oscillator(df: pd.DataFrame, period1: int = 7, period2: int = 14, period3: int = 28) -> pd.Series:
    """Ultimate Oscillator"""
    bp = df['close'] - df[['low', 'close']].shift(1).min(axis=1)
    tr = df[['high', 'close']].shift(1).max(axis=1) - df[['low', 'close']].shift(1).min(axis=1)
    
    avg1 = bp.rolling(period1).sum() / tr.rolling(period1).sum()
    avg2 = bp.rolling(period2).sum() / tr.rolling(period2).sum()
    avg3 = bp.rolling(period3).sum() / tr.rolling(period3).sum()
    
    return 100 * (4 * avg1 + 2 * avg2 + avg3) / 7


def compute_aroon(df: pd.DataFrame, period: int = 25) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Aroon Indicator"""
    aroon_up = 100 * df['high'].rolling(period + 1).apply(lambda x: x.argmax(), raw=True) / period
    aroon_down = 100 * df['low'].rolling(period + 1).apply(lambda x: x.argmin(), raw=True) / period
    aroon_osc = aroon_up - aroon_down
    return aroon_up, aroon_down, aroon_osc


# =============================================================================
# VOLATILITY INDICATORS
# =============================================================================

def compute_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands"""
    sma = series.rolling(window=period, min_periods=1).mean()
    rolling_std = series.rolling(window=period, min_periods=1).std().fillna(0)
    upper = sma + (rolling_std * std_dev)
    lower = sma - (rolling_std * std_dev)
    return upper, sma, lower


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range"""
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.ewm(alpha=1/period, min_periods=period).mean()


def compute_keltner_channels(df: pd.DataFrame, ema_period: int = 20, atr_period: int = 10, multiplier: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Keltner Channels"""
    middle = compute_ema(df['close'], ema_period)
    atr = compute_atr(df, atr_period)
    upper = middle + (multiplier * atr)
    lower = middle - (multiplier * atr)
    return upper, middle, lower


def compute_donchian_channels(df: pd.DataFrame, period: int = 20) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Donchian Channels"""
    upper = df['high'].rolling(window=period).max()
    lower = df['low'].rolling(window=period).min()
    middle = (upper + lower) / 2
    return upper, middle, lower


def compute_standard_deviation(series: pd.Series, period: int = 20) -> pd.Series:
    """Standard Deviation"""
    return series.rolling(window=period).std()


def compute_historical_volatility(series: pd.Series, period: int = 20) -> pd.Series:
    """Historical Volatility (Annualized)"""
    log_returns = np.log(series / series.shift(1))
    return log_returns.rolling(window=period).std() * np.sqrt(252) * 100


# =============================================================================
# VOLUME INDICATORS
# =============================================================================

def compute_vwap(df: pd.DataFrame) -> pd.Series:
    """Volume Weighted Average Price"""
    tp = (df['high'] + df['low'] + df['close']) / 3
    cumulative_tp_vol = (tp * df['volume']).cumsum()
    cumulative_vol = df['volume'].cumsum()
    return cumulative_tp_vol / (cumulative_vol + 1e-10)


def compute_obv(df: pd.DataFrame) -> pd.Series:
    """On Balance Volume"""
    obv = pd.Series(index=df.index, dtype=float)
    obv.iloc[0] = df['volume'].iloc[0]
    
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    return obv


def compute_volume_ma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Volume Moving Average"""
    return df['volume'].rolling(window=period, min_periods=1).mean()


def compute_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Money Flow Index"""
    tp = (df['high'] + df['low'] + df['close']) / 3
    mf = tp * df['volume']
    
    positive_mf = pd.Series(np.where(tp > tp.shift(1), mf, 0), index=df.index)
    negative_mf = pd.Series(np.where(tp < tp.shift(1), mf, 0), index=df.index)
    
    mfr = positive_mf.rolling(period).sum() / (negative_mf.rolling(period).sum() + 1e-10)
    return 100 - (100 / (1 + mfr))


def compute_chaikin_mf(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Chaikin Money Flow"""
    mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-10)
    mfv = mfm * df['volume']
    return mfv.rolling(period).sum() / (df['volume'].rolling(period).sum() + 1e-10)


def compute_accumulation_distribution(df: pd.DataFrame) -> pd.Series:
    """Accumulation/Distribution Line"""
    mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-10)
    return (mfm * df['volume']).cumsum()


def compute_vpt(df: pd.DataFrame) -> pd.Series:
    """Volume Price Trend"""
    roc = (df['close'] - df['close'].shift(1)) / (df['close'].shift(1) + 1e-10)
    return (roc * df['volume']).cumsum()


# =============================================================================
# TREND STRENGTH INDICATORS
# =============================================================================

def compute_adx(df: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Average Directional Index"""
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    
    plus_dm = pd.Series(np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0), index=df.index)
    minus_dm = pd.Series(np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0), index=df.index)
    
    atr = compute_atr(df, period)
    
    plus_di = 100 * plus_dm.ewm(alpha=1/period, min_periods=period).mean() / (atr + 1e-10)
    minus_di = 100 * minus_dm.ewm(alpha=1/period, min_periods=period).mean() / (atr + 1e-10)
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
    adx = dx.ewm(alpha=1/period, min_periods=period).mean()
    
    return adx, plus_di, minus_di


def compute_trix(series: pd.Series, period: int = 15) -> pd.Series:
    """TRIX Indicator"""
    ema1 = compute_ema(series, period)
    ema2 = compute_ema(ema1, period)
    ema3 = compute_ema(ema2, period)
    return 10000 * (ema3 - ema3.shift(1)) / (ema3.shift(1) + 1e-10)


# =============================================================================
# PIVOT POINTS
# =============================================================================

def compute_pivot_points(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Standard Pivot Points"""
    pivot = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
    
    r1 = 2 * pivot - df['low'].shift(1)
    s1 = 2 * pivot - df['high'].shift(1)
    r2 = pivot + (df['high'].shift(1) - df['low'].shift(1))
    s2 = pivot - (df['high'].shift(1) - df['low'].shift(1))
    r3 = df['high'].shift(1) + 2 * (pivot - df['low'].shift(1))
    s3 = df['low'].shift(1) - 2 * (df['high'].shift(1) - pivot)
    
    return {
        'pivot': pivot,
        'r1': r1, 's1': s1,
        'r2': r2, 's2': s2,
        'r3': r3, 's3': s3
    }


def compute_cpr(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Central Pivot Range"""
    pivot = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
    bc = (df['high'].shift(1) + df['low'].shift(1)) / 2
    tc = (pivot - bc) + pivot
    
    return {
        'pivot': pivot,
        'tc': tc,
        'bc': bc
    }


# =============================================================================
# MASTER FUNCTION
# =============================================================================

def compute_all_indicators(df: pd.DataFrame, include_advanced: bool = True) -> Dict[str, Any]:
    """
    Compute all technical indicators for a given DataFrame
    Returns a dictionary with all indicator values
    """
    close = df['close']
    
    # Moving Averages
    sma_9 = compute_sma(close, 9)
    sma_20 = compute_sma(close, 20)
    sma_50 = compute_sma(close, 50)
    sma_200 = compute_sma(close, 200)
    ema_9 = compute_ema(close, 9)
    ema_20 = compute_ema(close, 20)
    ema_50 = compute_ema(close, 50)
    
    # MACD
    macd_line, macd_signal, macd_hist = compute_macd(close)
    
    # RSI
    rsi_14 = compute_rsi(close, 14)
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = compute_bollinger_bands(close)
    
    # ATR
    atr_14 = compute_atr(df, 14)
    
    # Volume MA
    vol_ma = compute_volume_ma(df, 20)
    
    # Stochastic
    stoch_k, stoch_d = compute_stochastic(df)
    
    # SuperTrend
    supertrend, supertrend_dir = compute_supertrend(df)
    
    # ADX
    adx, plus_di, minus_di = compute_adx(df)
    
    # VWAP
    vwap = compute_vwap(df)
    
    result = {
        "timestamps": df['timestamp'].tolist(),
        # Moving Averages
        "sma_9": series_to_list(sma_9),
        "sma_20": series_to_list(sma_20),
        "sma_50": series_to_list(sma_50),
        "sma_200": series_to_list(sma_200),
        "ema_9": series_to_list(ema_9),
        "ema_20": series_to_list(ema_20),
        "ema_50": series_to_list(ema_50),
        # MACD
        "macd_line": series_to_list(macd_line),
        "macd_signal": series_to_list(macd_signal),
        "macd_histogram": series_to_list(macd_hist),
        # RSI
        "rsi_14": series_to_list(rsi_14),
        # Bollinger Bands
        "bb_upper": series_to_list(bb_upper),
        "bb_middle": series_to_list(bb_middle),
        "bb_lower": series_to_list(bb_lower),
        # ATR
        "atr_14": series_to_list(atr_14),
        # Volume
        "volume_ma_20": series_to_list(vol_ma),
        "vwap": series_to_list(vwap),
        # Stochastic
        "stoch_k": series_to_list(stoch_k),
        "stoch_d": series_to_list(stoch_d),
        # SuperTrend
        "supertrend": series_to_list(supertrend),
        "supertrend_direction": series_to_list(supertrend_dir),
        # ADX
        "adx": series_to_list(adx),
        "plus_di": series_to_list(plus_di),
        "minus_di": series_to_list(minus_di),
    }
    
    if include_advanced:
        # Williams %R
        williams_r = compute_williams_r(df)
        
        # CCI
        cci = compute_cci(df)
        
        # ROC
        roc = compute_roc(close)
        
        # MFI
        mfi = compute_mfi(df)
        
        # OBV
        obv = compute_obv(df)
        
        # Aroon
        aroon_up, aroon_down, aroon_osc = compute_aroon(df)
        
        # Ichimoku
        ichimoku = compute_ichimoku(df)
        
        # Keltner Channels
        kc_upper, kc_middle, kc_lower = compute_keltner_channels(df)
        
        # Donchian Channels
        dc_upper, dc_middle, dc_lower = compute_donchian_channels(df)
        
        # TRIX
        trix = compute_trix(close)
        
        # Parabolic SAR
        psar = compute_parabolic_sar(df)
        
        # Alligator
        alligator = compute_alligator(df)
        
        # Pivot Points
        pivots = compute_pivot_points(df)
        cpr = compute_cpr(df)
        
        # Chaikin Money Flow
        cmf = compute_chaikin_mf(df)
        
        # A/D Line
        ad_line = compute_accumulation_distribution(df)
        
        # Historical Volatility
        hv = compute_historical_volatility(close)
        
        result.update({
            # Additional Momentum
            "williams_r": series_to_list(williams_r),
            "cci": series_to_list(cci),
            "roc": series_to_list(roc),
            "mfi": series_to_list(mfi),
            # Volume
            "obv": series_to_list(obv),
            "cmf": series_to_list(cmf),
            "ad_line": series_to_list(ad_line),
            # Aroon
            "aroon_up": series_to_list(aroon_up),
            "aroon_down": series_to_list(aroon_down),
            "aroon_osc": series_to_list(aroon_osc),
            # Ichimoku
            "ichimoku_tenkan": series_to_list(ichimoku['tenkan_sen']),
            "ichimoku_kijun": series_to_list(ichimoku['kijun_sen']),
            "ichimoku_senkou_a": series_to_list(ichimoku['senkou_span_a']),
            "ichimoku_senkou_b": series_to_list(ichimoku['senkou_span_b']),
            # Keltner Channels
            "keltner_upper": series_to_list(kc_upper),
            "keltner_middle": series_to_list(kc_middle),
            "keltner_lower": series_to_list(kc_lower),
            # Donchian Channels
            "donchian_upper": series_to_list(dc_upper),
            "donchian_middle": series_to_list(dc_middle),
            "donchian_lower": series_to_list(dc_lower),
            # TRIX
            "trix": series_to_list(trix),
            # Parabolic SAR
            "parabolic_sar": series_to_list(psar),
            # Alligator
            "alligator_jaw": series_to_list(alligator['jaw']),
            "alligator_teeth": series_to_list(alligator['teeth']),
            "alligator_lips": series_to_list(alligator['lips']),
            # Pivot Points
            "pivot": series_to_list(pivots['pivot']),
            "pivot_r1": series_to_list(pivots['r1']),
            "pivot_s1": series_to_list(pivots['s1']),
            "pivot_r2": series_to_list(pivots['r2']),
            "pivot_s2": series_to_list(pivots['s2']),
            # CPR
            "cpr_pivot": series_to_list(cpr['pivot']),
            "cpr_tc": series_to_list(cpr['tc']),
            "cpr_bc": series_to_list(cpr['bc']),
            # Volatility
            "historical_volatility": series_to_list(hv),
        })
    
    return result
