"""
Configuration centralisée du bot, chargée depuis les variables d'environnement
ou un fichier .env (voir .env.example).
"""
from __future__ import annotations

from pathlib import Path
from typing import Annotated, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Telegram ---
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    allowed_chat_ids: Annotated[List[int], NoDecode] = Field(default_factory=list, alias="ALLOWED_CHAT_IDS")

    # --- Session Pocket Option (obtenue manuellement par l'utilisateur) ---
    po_ssid: str = Field(..., alias="PO_SSID")
    po_uid: int = Field(..., alias="PO_UID")
    po_is_demo: bool = Field(True, alias="PO_IS_DEMO")
    po_region: str = Field("EU", alias="PO_REGION")

    # --- Scan ---
    pairs: Annotated[List[str], NoDecode] = Field(default_factory=list, alias="PAIRS")
    min_payout: int = Field(87, alias="MIN_PAYOUT")
    timeframes: Annotated[List[int], NoDecode] = Field(
        default_factory=lambda: [10, 60, 120, 300], alias="TIMEFRAMES"
    )
    scan_interval_seconds: int = Field(5, alias="SCAN_INTERVAL_SECONDS")

    # --- Logs ---
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_dir: Path = Field(Path("./logs"), alias="LOG_DIR")

    @field_validator("allowed_chat_ids", "pairs", "timeframes", mode="before")
    @classmethod
    def _split_csv(cls, v):
        if isinstance(v, str):
            items = [x.strip() for x in v.split(",") if x.strip()]
            return items
        return v


settings = Settings()
