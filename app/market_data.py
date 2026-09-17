"""
Client de données de marché basé sur le SDK `pocket-option`
(lordralinc/pocket_option, MIT, https://pypi.org/project/pocket-option) au
lieu d'un protocole Socket.IO deviné à la main.

IMPORTANT — lecture seule, aucune exécution de trade :
Ce wrapper n'utilise QUE les fonctionnalités de marché du SDK (bougies,
payout). Il n'importe jamais `client.deals` pour ouvrir un ordre, et ne doit
JAMAIS être étendu pour le faire dans ce projet — voir la limite posée dès
le départ de ce bot ("pas de trading automatique").

Comme pour l'ancienne implémentation (voir market_data_legacy.py), ce
wrapper part du principe que TOI tu t'es connecté manuellement sur
pocketoption.com dans un navigateur, et que tu as copié ton SSID/UID de
session depuis les DevTools. Aucune automatisation de connexion ici.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

from pocket_option import PocketOptionClient
from pocket_option.constants import Regions
from pocket_option.contrib.default_init import default_init
from pocket_option.models import Asset, AuthorizationData

from app.config import settings
from app.logger import log
from app.models import Candle

# Mapping des régions "courtes" utilisées dans .env vers les régions du SDK.
REGION_MAP = {
    "EU": Regions.EUROPA,
    "US": Regions.UNITED_STATES_NORTH,
    "US_SOUTH": Regions.UNITED_STATES_SOUTH,
    "ASIA": Regions.ASIA,
    "DEMO": Regions.DEMO,
    "DEMO2": Regions.DEMO_2,
    "FRANCE": Regions.FRANCE_1,
    "RUSSIA": Regions.RUSSIA,
    "INDIA": Regions.INDIA,
    "HONGKONG": Regions.HONGKONG,
}


class PocketOptionSDKClient:
    """
    Fournisseur de données de marché en lecture seule, basé sur le SDK
    `pocket-option`. Interface volontairement proche de l'ancien client
    (get_candles / get_payout / run) pour limiter les changements côté bot.
    """

    def __init__(self) -> None:
        self.region = REGION_MAP.get(settings.po_region.upper(), Regions.EUROPA)

        # Traduit les tickers bruts du .env (ex: "EURUSD_otc") vers l'enum
        # Asset du SDK. Les tickers inconnus du SDK sont ignorés avec un
        # avertissement plutôt que de faire planter le bot (utile pour les
        # paires exotiques qui n'existent pas forcément côté Pocket Option).
        self.asset_map: Dict[str, Asset] = {}
        for ticker in settings.pairs:
            asset = getattr(Asset, ticker, None)
            if asset is None:
                log.warning(f"Paire inconnue du SDK pocket-option, ignorée: {ticker}")
                continue
            self.asset_map[ticker] = asset

        self.client = PocketOptionClient(logger=False)
        default_init(
            self.client,
            authorization=AuthorizationData.model_validate(
                {
                    "session": settings.po_ssid,
                    "isDemo": int(settings.po_is_demo),
                    "uid": settings.po_uid,
                    "platform": 2,
                    "isFastHistory": True,
                    "isOptimized": True,
                }
            ),
            sub_assets=list(self.asset_map.values()),
            # Période de souscription initiale (secondes) : la plus fine de
            # celles configurées, pour avoir le maximum de granularité.
            sub_period=min(settings.timeframes) if settings.timeframes else 60,
        )

    async def get_payout(self, ticker: str) -> Optional[float]:
        asset = self.asset_map.get(ticker)
        if asset is None:
            return None
        item = await self.client.assets.get_asset(assset=asset)
        return float(item.payout) if item is not None else None

    async def get_candles(self, ticker: str, timeframe_seconds: int, count: int = 200) -> List[Candle]:
        asset = self.asset_map.get(ticker)
        if asset is None:
            return []
        try:
            sdk_candles = await self.client.candles.get_candles(
                asset, timeframe=timeframe_seconds, count=count
            )
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Échec récupération bougies {ticker} {timeframe_seconds}s: {exc}")
            return []

        candles = [
            Candle(
                timestamp=c.timestamp,
                open=c.open,
                high=c.high,
                low=c.low,
                close=c.close,
            )
            for c in sdk_candles
        ]
        candles.sort(key=lambda c: c.timestamp)
        return candles

    async def run(self, on_candle: Optional[Callable[[str, int, Candle], None]] = None) -> None:
        """
        Se connecte au serveur Pocket Option et reste connecté. La
        réception des données se fait en tâche de fond via le SDK
        (reconnexion automatique incluse) — `on_candle` n'est pas utilisé
        par ce backend (les bougies sont lues à la demande via
        get_candles), gardé uniquement pour compatibilité d'interface.
        """
        log.info(f"Connexion au SDK pocket-option (région: {self.region.name})...")
        await self.client.connect(self.region, wait=True, retry=True)
        log.success("Connecté via le SDK pocket-option.")
        await self.client.wait_for_authorization(timeout=30)
        log.success("Authentification réussie.")

        # Le SDK gère la boucle de lecture/reconnexion en tâches de fond ;
        # on garde juste ce coroutine vivant.
        try:
            while True:
                await self.client.sleep(3600)
        finally:
            await self.client.disconnect()
