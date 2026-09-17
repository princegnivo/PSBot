"""Configuration de Loguru : rotation journalière + sortie console."""
import sys

from loguru import logger

from app.config import settings


def setup_logger() -> "logger":
    logger.remove()
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        sys.stdout,
        level=settings.log_level,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - {message}",
    )
    logger.add(
        settings.log_dir / "bot_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="14 days",
        level=settings.log_level,
        encoding="utf-8",
    )
    return logger


log = setup_logger()
