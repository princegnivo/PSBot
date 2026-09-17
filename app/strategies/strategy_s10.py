from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

import numpy as np

from app.indicators.ta import crossed_above, crossed_below, sma, williams_r
from app.models import Candle, Direction, Signal

# Période de la SMA lente : 21 par défaut, 33 selon certaines variantes du
# graphique (paramètre exposé ici pour ajustement facile).
SMA_SLOW_PERIOD = 21


def analyze_s10(pair: str, candles: List[Candle], payout: Optional[float] = None) -> Optional[Signal]:
    """
    Stratégie S10 (bougies 10 secondes) :
      - SMA(5) / SMA(21 ou 33)
      - Williams %R(14), niveaux -20 (surachat) / -80 (survente)
      - Expiration : 10 secondes

    Pas de bougies Heikin Ashi ici (bougies classiques, comme indiqué dans le brief).

    CALL (HIGHER) :
      1. SMA 5 croise SMA lente vers le haut
      2. Williams %R franchit -80 vers le haut (ou forte impulsion haussière
         en sortie de survente)
      3. Bougie de clôture verte, pleine et stable

    PUT (LOWER) : conditions symétriques sur -20 / bougie rouge.
    """
    min_len = max(SMA_SLOW_PERIOD, 14) + 5
    if len(candles) < min_len:
        return None

    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]

    sma_fast = sma(closes, period=5)
    sma_slow = sma(closes, period=SMA_SLOW_PERIOD)
    wr = williams_r(highs, lows, closes, period=14)

    if np.isnan(sma_slow[-1]) or np.isnan(wr[-2]):
        return None

    last = candles[-1]
    body = last.close - last.open
    rng = max(1e-9, last.high - last.low)
    body_ratio = abs(body) / rng
    strong_candle = body_ratio > 0.55

    bull_cross = crossed_above(sma_fast, sma_slow)
    bear_cross = crossed_below(sma_fast, sma_slow)

    # Sortie de survente vers le haut : WR était sous -80 récemment et
    # remonte au-dessus, ou impulsion haussière nette même sans franchir le
    # seuil exact.
    wr_exiting_oversold = wr[-2] <= -80 and wr[-1] > wr[-2]
    wr_bull_impulse = (wr[-1] - wr[-2]) > 15 and wr[-1] < -20

    # Symétrique côté surachat.
    wr_exiting_overbought = wr[-2] >= -20 and wr[-1] < wr[-2]
    wr_bear_impulse = (wr[-2] - wr[-1]) > 15 and wr[-1] > -80

    if bull_cross and (wr_exiting_oversold or wr_bull_impulse) and body > 0 and strong_candle:
        return Signal(
            pair=pair,
            direction=Direction.CALL,
            timeframe_seconds=10,
            entry_time=datetime.now(timezone.utc),
            payout=payout,
            confidence=min(95.0, 60 + 20 * body_ratio + 10),
            entry_price=closes[-1],
            sma_fast=sma_fast[-1],
            sma_slow=sma_slow[-1],
            williams_r=wr[-1],
            strategy_name="S10 - SMA + Williams %R",
            reasons=[
                f"SMA 5 croise SMA {SMA_SLOW_PERIOD} à la hausse",
                "Williams %R sort de la zone de survente (-80) avec momentum haussier",
                "Bougie verte pleine et stable",
            ],
        )

    if bear_cross and (wr_exiting_overbought or wr_bear_impulse) and body < 0 and strong_candle:
        return Signal(
            pair=pair,
            direction=Direction.PUT,
            timeframe_seconds=10,
            entry_time=datetime.now(timezone.utc),
            payout=payout,
            confidence=min(95.0, 60 + 20 * body_ratio + 10),
            entry_price=closes[-1],
            sma_fast=sma_fast[-1],
            sma_slow=sma_slow[-1],
            williams_r=wr[-1],
            strategy_name="S10 - SMA + Williams %R",
            reasons=[
                f"SMA 5 croise SMA {SMA_SLOW_PERIOD} à la baisse",
                "Williams %R sort de la zone de surachat (-20) avec momentum baissier",
                "Bougie rouge franche et marquée",
            ],
        )

    return None
