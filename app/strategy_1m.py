from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from app.indicators.ta import bollinger_bands, crossed_above, crossed_below, rsi, sma, to_heikin_ashi
from app.models import Candle, Direction, Signal


def analyze_1m(pair: str, candles: List[Candle], payout: Optional[float] = None) -> Optional[Signal]:
    """
    Stratégie M1 :
      - Heikin Ashi
      - Bollinger Bands (20, 2)
      - SMA(2) / SMA(5)
      - RSI(8), zones 30/70
    """
    if len(candles) < 25:
        return None

    ha = to_heikin_ashi(candles)
    closes = [c.close for c in ha]

    bb_upper, _, bb_lower = bollinger_bands(closes, period=20, deviation=2.0)
    sma_fast = sma(closes, period=2)
    sma_slow = sma(closes, period=5)
    rsi_vals = rsi(closes, period=8)

    if any(map(lambda a: len(a) == 0 or np_isnan_last(a), [bb_upper, bb_lower, sma_fast, sma_slow, rsi_vals])):
        return None

    last_close = closes[-1]
    last_low = ha[-1].low
    last_high = ha[-1].high
    last_rsi = rsi_vals[-1]

    near_lower_band = last_low <= bb_lower[-1] * 1.0005
    near_upper_band = last_high >= bb_upper[-1] * 0.9995

    bull_cross = crossed_above(sma_fast, sma_slow)
    bear_cross = crossed_below(sma_fast, sma_slow)

    rsi_turning_up = rsi_vals[-1] > rsi_vals[-2] and last_rsi < 55
    rsi_turning_down = rsi_vals[-1] < rsi_vals[-2] and last_rsi > 45

    if near_lower_band and bull_cross and rsi_turning_up:
        confidence = _confidence(last_rsi, target=35, cross=True)
        return Signal(
            pair=pair,
            direction=Direction.CALL,
            timeframe_seconds=60,
            entry_time=datetime.now(timezone.utc),
            payout=payout,
            confidence=confidence,
            entry_price=last_close,
            rsi=last_rsi,
            bb_upper=bb_upper[-1],
            bb_lower=bb_lower[-1],
            sma_fast=sma_fast[-1],
            sma_slow=sma_slow[-1],
        )

    if near_upper_band and bear_cross and rsi_turning_down:
        confidence = _confidence(last_rsi, target=65, cross=True)
        return Signal(
            pair=pair,
            direction=Direction.PUT,
            timeframe_seconds=60,
            entry_time=datetime.now(timezone.utc),
            payout=payout,
            confidence=confidence,
            entry_price=last_close,
            rsi=last_rsi,
            bb_upper=bb_upper[-1],
            bb_lower=bb_lower[-1],
            sma_fast=sma_fast[-1],
            sma_slow=sma_slow[-1],
        )

    return None


def _confidence(rsi_val: float, target: float, cross: bool) -> float:
    base = 60.0
    base += 15.0 if cross else 0.0
    base += max(0.0, 10.0 - abs(rsi_val - target) / 3)
    return min(95.0, base)


def np_isnan_last(arr) -> bool:
    import numpy as np

    return bool(np.isnan(arr[-1]))
