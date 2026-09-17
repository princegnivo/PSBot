from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

import numpy as np

from app.indicators.ta import bollinger_bands, crossed_above, crossed_below, rsi, sma, to_heikin_ashi
from app.models import Candle, Direction, Signal

# NOTE: les règles précises de la stratégie M5 n'ont pas été fournies
# (le brief s'arrête à "POUR SIGNAUX DE 5minute"). Ce module reprend donc
# une combinaison Bollinger + SMA + RSI similaire à la M1 mais avec des
# périodes plus larges, à ajuster librement selon ta propre stratégie M5.


def analyze_5m(pair: str, candles: List[Candle], payout: Optional[float] = None) -> Optional[Signal]:
    if len(candles) < 30:
        return None

    ha = to_heikin_ashi(candles)
    closes = [c.close for c in ha]

    bb_upper, _, bb_lower = bollinger_bands(closes, period=20, deviation=2.0)
    sma_fast = sma(closes, period=5)
    sma_slow = sma(closes, period=10)
    rsi_vals = rsi(closes, period=14)

    if np.isnan(bb_upper[-1]) or np.isnan(sma_slow[-1]) or np.isnan(rsi_vals[-1]):
        return None

    last = ha[-1]
    bull_cross = crossed_above(sma_fast, sma_slow)
    bear_cross = crossed_below(sma_fast, sma_slow)

    if last.low <= bb_lower[-1] * 1.0007 and bull_cross and rsi_vals[-1] < 55:
        return Signal(
            pair=pair,
            direction=Direction.CALL,
            timeframe_seconds=300,
            entry_time=datetime.now(timezone.utc),
            payout=payout,
            confidence=65.0,
            entry_price=closes[-1],
            rsi=rsi_vals[-1],
            bb_upper=bb_upper[-1],
            bb_lower=bb_lower[-1],
            sma_fast=sma_fast[-1],
            sma_slow=sma_slow[-1],
        )

    if last.high >= bb_upper[-1] * 0.9993 and bear_cross and rsi_vals[-1] > 45:
        return Signal(
            pair=pair,
            direction=Direction.PUT,
            timeframe_seconds=300,
            entry_time=datetime.now(timezone.utc),
            payout=payout,
            confidence=65.0,
            entry_price=closes[-1],
            rsi=rsi_vals[-1],
            bb_upper=bb_upper[-1],
            bb_lower=bb_lower[-1],
            sma_fast=sma_fast[-1],
            sma_slow=sma_slow[-1],
        )

    return None
