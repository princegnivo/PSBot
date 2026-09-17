"""
Implémentation "maison" des indicateurs techniques nécessaires,
en numpy pur (pas de dépendance TA-Lib, plus simple à installer sur Termux).
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np

from app.models import Candle


def to_heikin_ashi(candles: Sequence[Candle]) -> List[Candle]:
    """Convertit une série de bougies classiques en bougies Heikin Ashi."""
    if not candles:
        return []

    ha_candles: List[Candle] = []
    prev_ha_open = (candles[0].open + candles[0].close) / 2
    prev_ha_close = (candles[0].open + candles[0].high + candles[0].low + candles[0].close) / 4

    for i, c in enumerate(candles):
        ha_close = (c.open + c.high + c.low + c.close) / 4
        if i == 0:
            ha_open = prev_ha_open
        else:
            ha_open = (prev_ha_open + prev_ha_close) / 2
        ha_high = max(c.high, ha_open, ha_close)
        ha_low = min(c.low, ha_open, ha_close)

        ha_candles.append(
            Candle(timestamp=c.timestamp, open=ha_open, high=ha_high, low=ha_low, close=ha_close, volume=c.volume)
        )
        prev_ha_open, prev_ha_close = ha_open, ha_close

    return ha_candles


def sma(values: Sequence[float], period: int) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if len(values) < period:
        return np.full(len(values), np.nan)
    kernel = np.ones(period) / period
    result = np.convolve(values, kernel, mode="valid")
    pad = np.full(period - 1, np.nan)
    return np.concatenate([pad, result])


def ema(values: Sequence[float], period: int) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    alpha = 2 / (period + 1)
    result = np.empty(len(values))
    result[:] = np.nan
    if len(values) == 0:
        return result
    result[0] = values[0]
    for i in range(1, len(values)):
        result[i] = alpha * values[i] + (1 - alpha) * result[i - 1]
    return result


def bollinger_bands(values: Sequence[float], period: int = 20, deviation: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=float)
    middle = sma(values, period)
    std = np.full(len(values), np.nan)
    for i in range(period - 1, len(values)):
        std[i] = np.std(values[i - period + 1 : i + 1], ddof=0)
    upper = middle + deviation * std
    lower = middle - deviation * std
    return upper, middle, lower


def rsi(values: Sequence[float], period: int = 8) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    result = np.full(len(values), np.nan)
    if len(values) <= period:
        return result

    deltas = np.diff(values)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    for i in range(period, len(values)):
        if i > period:
            avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else np.inf
        result[i] = 100 - (100 / (1 + rs))

    return result


def macd(values: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    ema_fast = ema(values, fast)
    ema_slow = ema(values, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def crossed_above(fast: np.ndarray, slow: np.ndarray) -> bool:
    """True si `fast` vient de croiser `slow` vers le haut sur la dernière bougie close."""
    if len(fast) < 2 or np.isnan(fast[-2]) or np.isnan(slow[-2]):
        return False
    return fast[-2] <= slow[-2] and fast[-1] > slow[-1]


def crossed_below(fast: np.ndarray, slow: np.ndarray) -> bool:
    if len(fast) < 2 or np.isnan(fast[-2]) or np.isnan(slow[-2]):
        return False
    return fast[-2] >= slow[-2] and fast[-1] < slow[-1]


def williams_r(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14) -> np.ndarray:
    """
    Williams %R : oscillateur de momentum, échelle de 0 à -100.
    -80 = survente (zone basse), -20 = surachat (zone haute).
    """
    highs = np.asarray(highs, dtype=float)
    lows = np.asarray(lows, dtype=float)
    closes = np.asarray(closes, dtype=float)
    n = len(closes)
    result = np.full(n, np.nan)

    for i in range(period - 1, n):
        highest_high = np.max(highs[i - period + 1 : i + 1])
        lowest_low = np.min(lows[i - period + 1 : i + 1])
        rng = highest_high - lowest_low
        if rng == 0:
            result[i] = -50.0
        else:
            result[i] = (highest_high - closes[i]) / rng * -100.0

    return result
