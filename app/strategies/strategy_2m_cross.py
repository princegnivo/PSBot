from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

import numpy as np

from app.indicators.ta import bollinger_bands, macd, to_heikin_ashi
from app.models import Candle, Direction, Signal


def analyze_2m_cross(pair: str, candles: List[Candle], payout: Optional[float] = None) -> Optional[Signal]:
    """
    Stratégie M2 "Croisement MACD" :
      - Heikin Ashi
      - Bollinger Bands (6, 1.3)
      - MACD (6, 19, 6)

    HIGHER (CALL) :
      1. MACD croise Signal vers le haut, EN DESSOUS de la ligne zéro
      2. Bougie HA proche/dépasse la bande supérieure de Bollinger
      3. Bougie HA haussière forte (corps plein, mèche haute quasi absente)

    LOWER (PUT) : conditions symétriques (croisement au-dessus de zéro,
    bande inférieure, bougie baissière forte).
    """
    if len(candles) < 30:
        return None

    ha = to_heikin_ashi(candles)
    closes = [c.close for c in ha]

    bb_upper, _, bb_lower = bollinger_bands(closes, period=6, deviation=1.3)
    macd_line, signal_line, _ = macd(closes, fast=6, slow=19, signal=6)

    if np.isnan(bb_upper[-1]) or np.isnan(macd_line[-2]) or np.isnan(signal_line[-2]):
        return None

    last = ha[-1]
    body = last.close - last.open
    rng = max(1e-9, last.high - last.low)
    body_ratio = abs(body) / rng
    strong_candle = body_ratio > 0.6
    upper_wick_ratio = (last.high - max(last.open, last.close)) / rng
    lower_wick_ratio = (min(last.open, last.close) - last.low) / rng

    macd_cross_up = macd_line[-2] <= signal_line[-2] and macd_line[-1] > signal_line[-1]
    macd_cross_down = macd_line[-2] >= signal_line[-2] and macd_line[-1] < signal_line[-1]

    # Position du croisement par rapport à la ligne zéro (moyenne des 2 lignes
    # au moment du croisement, comme repère de la zone où il se produit).
    cross_level = (macd_line[-1] + signal_line[-1]) / 2
    cross_below_zero = cross_level < 0
    cross_above_zero = cross_level > 0

    near_upper_band = last.high >= bb_upper[-1] * 0.999
    near_lower_band = last.low <= bb_lower[-1] * 1.001

    if (
        macd_cross_up
        and cross_below_zero
        and near_upper_band
        and body > 0
        and strong_candle
        and upper_wick_ratio < 0.15
    ):
        return Signal(
            pair=pair,
            direction=Direction.CALL,
            timeframe_seconds=120,
            entry_time=datetime.now(timezone.utc),
            payout=payout,
            confidence=min(95.0, 65 + 20 * body_ratio),
            entry_price=closes[-1],
            rsi=50.0,  # non utilisé dans cette stratégie, valeur neutre
            bb_upper=bb_upper[-1],
            bb_lower=bb_lower[-1],
            macd=macd_line[-1],
            macd_signal=signal_line[-1],
            strategy_name="M2 - Croisement MACD",
            reasons=[
                "MACD croise Signal à la hausse, sous la ligne zéro",
                "Bougie HA proche/dépasse la bande supérieure de Bollinger",
                "Bougie HA haussière forte et stable",
            ],
        )

    if (
        macd_cross_down
        and cross_above_zero
        and near_lower_band
        and body < 0
        and strong_candle
        and lower_wick_ratio < 0.15
    ):
        return Signal(
            pair=pair,
            direction=Direction.PUT,
            timeframe_seconds=120,
            entry_time=datetime.now(timezone.utc),
            payout=payout,
            confidence=min(95.0, 65 + 20 * body_ratio),
            entry_price=closes[-1],
            rsi=50.0,
            bb_upper=bb_upper[-1],
            bb_lower=bb_lower[-1],
            macd=macd_line[-1],
            macd_signal=signal_line[-1],
            strategy_name="M2 - Croisement MACD",
            reasons=[
                "MACD croise Signal à la baisse, au-dessus de la ligne zéro",
                "Bougie HA proche/dépasse la bande inférieure de Bollinger",
                "Bougie HA baissière forte et stable",
            ],
        )

    return None
