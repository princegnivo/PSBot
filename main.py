import asyncio

from app.bot import start_bot
from app.logger import log


def main() -> None:
    log.info("Démarrage du bot de signaux Pocket Option...")
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        log.info("Arrêt demandé par l'utilisateur.")


if __name__ == "__main__":
    main()
