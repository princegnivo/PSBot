"""
Client de données de marché.

IMPORTANT — ce module NE contient aucune automatisation de connexion ni
contournement de CAPTCHA. Il part du principe que tu t'es connecté toi-même,
manuellement, sur pocketoption.com dans un navigateur, et que tu as copié
ton SSID/session token (PO_SSID dans .env) depuis les DevTools.

Le WebSocket utilisé ici est celui qu'utilise déjà ton navigateur une fois
connecté : ce module se contente d'écouter les mêmes messages, avec ta
session déjà authentifiée — comme le ferait n'importe quel client léger
("SSID-based API"), une pratique courante et documentée dans plusieurs
projets communautaires open-source.

À toi de vérifier que cet usage respecte les conditions d'utilisation de
ta plateforme avant de l'utiliser en continu.
"""
from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Callable, Deque, Dict, List

import websockets
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.logger import log
from app.models import Candle

# Endpoints WebSocket connus (susceptibles de changer côté plateforme ;
# à adapter si Pocket Option modifie son infrastructure).
REGION_ENDPOINTS = {
    "EU": "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket",
    "US": "wss://api-us.po.market/socket.io/?EIO=4&transport=websocket",
    "ASIA": "wss://api-asia.po.market/socket.io/?EIO=4&transport=websocket",
}


class MarketDataProvider(ABC):
    """Interface générique — permet de brancher une autre source de données
    (ex: un flux forex classique) sans toucher au reste du bot."""

    @abstractmethod
    async def run(self, on_candle: Callable[[str, int, Candle], None]) -> None: ...

    @abstractmethod
    def get_payout(self, pair: str) -> float | None: ...


class PocketOptionWSClient(MarketDataProvider):
    """
    Se connecte au WebSocket de Pocket Option en utilisant une session déjà
    authentifiée (PO_SSID), s'abonne aux paires configurées et reconstruit
    des bougies par timeframe à partir du flux de ticks.
    """

    def __init__(self) -> None:
        self.region = settings.po_region.upper()
        self.ssid = settings.po_ssid
        self.pairs = settings.pairs
        self.timeframes = settings.timeframes  # en secondes (ex: 10, 60, 120, 300)
        self._buffers: Dict[str, Dict[int, Deque[Candle]]] = defaultdict(
            lambda: {tf: deque(maxlen=200) for tf in self.timeframes}
        )
        self._current_candle: Dict[str, Dict[int, Candle]] = defaultdict(dict)
        self._payouts: Dict[str, float] = {}
        self._ws = None

    def get_payout(self, pair: str) -> float | None:
        return self._payouts.get(pair)

    def get_candles(self, pair: str, timeframe: int) -> List[Candle]:
        return list(self._buffers[pair][timeframe])

    @retry(wait=wait_exponential(multiplier=2, min=2, max=60), stop=stop_after_attempt(1000))
    async def run(self, on_candle: Callable[[str, int, Candle], None]) -> None:
        url = REGION_ENDPOINTS.get(self.region, REGION_ENDPOINTS["EU"])
        log.info(f"Connexion WebSocket ({self.region})...")

        async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
            self._ws = ws
            await self._authenticate(ws)
            await self._subscribe(ws)
            log.success("Connecté et abonné aux paires configurées.")

            async for raw_message in ws:
                try:
                    await self._handle_message(raw_message, on_candle)
                except Exception as exc:  # noqa: BLE001
                    log.warning(f"Message ignoré (erreur de parsing): {exc}")

    async def _authenticate(self, ws) -> None:
        """Envoie le SSID déjà obtenu manuellement pour authentifier la session."""
        auth_payload = {"session": self.ssid, "isDemo": int(settings.po_is_demo)}
        await ws.send(f'42["auth",{json.dumps(auth_payload)}]')
        await asyncio.sleep(1)

    async def _subscribe(self, ws) -> None:
        for pair in self.pairs:
            await ws.send(f'42["subscribeCandles",{json.dumps({"asset": pair})}]')
            await asyncio.sleep(0.2)

    async def _handle_message(self, raw_message: str, on_candle: Callable[[str, int, Candle], None]) -> None:
        # Le protocole Socket.IO préfixe les messages par un code numérique.
        if not raw_message.startswith("42"):
            return

        payload = json.loads(raw_message[2:])
        event, data = payload[0], payload[1] if len(payload) > 1 else {}

        if event == "payoutUpdate":
            self._payouts[data["asset"]] = float(data["payout"])
            return

        if event == "tick":
            pair = data["asset"]
            price = float(data["price"])
            ts = datetime.now(timezone.utc)
            for tf in self.timeframes:
                self._update_candle(pair, tf, price, ts, on_candle)

    def _update_candle(
        self, pair: str, timeframe: int, price: float, ts: datetime, on_candle: Callable
    ) -> None:
        # `timeframe` est désormais exprimé directement en secondes
        # (ex: 10, 60, 120, 300) — supporte donc aussi bien le S10 que le M1/M2/M5.
        bucket_seconds = timeframe
        bucket_start = int(ts.timestamp() // bucket_seconds) * bucket_seconds

        current = self._current_candle[pair].get(timeframe)
        if current is None or int(current.timestamp.timestamp()) != bucket_start:
            if current is not None:
                self._buffers[pair][timeframe].append(current)
                on_candle(pair, timeframe, current)
            self._current_candle[pair][timeframe] = Candle(
                timestamp=datetime.fromtimestamp(bucket_start, tz=timezone.utc),
                open=price,
                high=price,
                low=price,
                close=price,
            )
        else:
            current.high = max(current.high, price)
            current.low = min(current.low, price)
            current.close = price
