from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.pairs_display import display_pair


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


class Direction(str, Enum):
    CALL = "CALL"
    PUT = "PUT"


class Signal(BaseModel):
    pair: str
    direction: Direction
    timeframe_seconds: int
    entry_time: datetime
    payout: Optional[float] = None
    confidence: float
    entry_price: float
    rsi: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    sma_fast: Optional[float] = None
    sma_slow: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    williams_r: Optional[float] = None
    strategy_name: str = ""
    reasons: list[str] = []

    def _expiration_label(self) -> str:
        if self.timeframe_seconds % 60 == 0:
            return f"{self.timeframe_seconds}s ({self.timeframe_seconds // 60}min)"
        return f"{self.timeframe_seconds}s"

    def to_message(self) -> str:
        emoji = "🟢" if self.direction == Direction.CALL else "🔴"
        label = "ACHAT (CALL)" if self.direction == Direction.CALL else "VENTE (PUT)"
        rsi_emoji = "🟢" if self.direction == Direction.CALL else "🔴"
        payout_str = f"{self.payout:.0f}%" if self.payout is not None else "N/A"

        lines = [
            f"{emoji} SIGNAL {label}",
            "=" * 40,
            "",
            f"📊 ACTIF: {display_pair(self.pair)}",
            f"🕘 HEURE D'ENTRÉE: {self.entry_time.strftime('%H:%M:%S')}",
            f"⏳ EXPIRATION: {self._expiration_label()}",
            f"💰 PAYOUT: {payout_str}",
            f"🧠 Stratégie: {self.strategy_name}",
            "",
            f"🔮 Direction: {self.direction.value}",
            f"📊 Confiance: {self.confidence:.0f}%",
            f"💵 Prix d'entrée: {self.entry_price:.5f}",
            "",
            "Indicateurs:",
        ]
        if self.rsi is not None:
            lines.append(f"• RSI ({rsi_emoji}): {self.rsi:.2f}")
        if self.bb_upper is not None and self.bb_lower is not None:
            lines.append(f"• BB Upper: {self.bb_upper:.5f}")
            lines.append(f"• BB Lower: {self.bb_lower:.5f}")
        if self.sma_fast is not None and self.sma_slow is not None:
            lines.append(f"• SMA rapide: {self.sma_fast:.5f}")
            lines.append(f"• SMA lente: {self.sma_slow:.5f}")
        if self.macd is not None and self.macd_signal is not None:
            lines.append(f"• MACD: {self.macd:.5f}")
            lines.append(f"• Signal MACD: {self.macd_signal:.5f}")
        if self.williams_r is not None:
            lines.append(f"• Williams %R: {self.williams_r:.2f}")

        if self.reasons:
            lines.append("")
            lines.append("Conditions validées:")
            for reason in self.reasons:
                lines.append(f"  ✓ {reason}")

        lines.append("")
        lines.append("⚠️ Signal informatif uniquement, aucune exécution automatique.")
        return "\n".join(lines)
