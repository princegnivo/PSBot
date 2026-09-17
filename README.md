# PO Signal Bot — Bot Telegram de signaux (informatifs)

Bot Telegram asynchrone (aiogram) qui analyse des paires OTC selon 4
stratégies basées sur Heikin Ashi, Bollinger Bands, SMA, RSI et MACD, puis
envoie des **signaux informatifs** dans Telegram.

**Ce bot n'exécute aucun trade.** Il ne fait qu'analyser et notifier — c'est
toi qui décides et places l'ordre manuellement sur Pocket Option si le
signal te convient.

## ⚠️ Ce que ce projet ne fait PAS

Ce bot ne contient **aucune automatisation de connexion / CAPTCHA**, et
**n'exécute aucun trade automatiquement**. Il ne se connecte pas à ta place
sur Pocket Option. Tu dois :

1. Te connecter toi-même, manuellement, dans un navigateur, sur ton compte
   (démo ou réel).
2. Récupérer ton `SSID` et ton `UID` de session (DevTools → onglet Network →
   WS → payload d'authentification `42["auth",...]`).
3. Les coller dans ton fichier `.env` (`PO_SSID=...`, `PO_UID=...`).

Le bot utilise le SDK communautaire open-source
[`pocket-option`](https://pypi.org/project/pocket-option) (MIT, non
affilié à Pocket Option) pour la connexion et la lecture des données de
marché. Ce SDK sait aussi passer des ordres (`client.deals.open_deal`),
mais **ce bot n'utilise jamais cette partie** — voir `app/market_data.py`,
qui n'importe que les fonctionnalités de lecture (bougies, payout).

Vérifie que cet usage respecte les conditions d'utilisation de ta
plateforme avant de faire tourner le bot en continu — c'est une API non
officielle (reverse-engineered), comme la plupart des projets communautaires
équivalents.

## Stratégies incluses

| Timeframe | Nom | Logique |
|---|---|---|
| S10 (10s) | SMA + Williams %R | SMA(5) croise SMA(21) + Williams %R(14) qui sort de zone extrême (-80/-20) + bougie forte |
| M1 | Bollinger + SMA + RSI | Retest de bande + croisement SMA(2)/SMA(5) + RSI(8) qui sort de zone extrême |
| M2 | Croisement MACD | MACD(6,19,6) qui croise sa ligne de signal du bon côté de la ligne zéro + retest de bande Bollinger(6,1.3) + bougie forte |
| M5 | Bollinger + SMA + RSI | Version M5 du même principe que M1 (paramètres à ajuster librement) |

Chaque timeframe peut avoir plusieurs stratégies actives en parallèle (le
code le permet), mais actuellement chacun n'en a qu'une seule branchée.

## Structure

```
po-signal-bot/
├── app/
│   ├── config.py                    # Config via variables d'environnement (pydantic)
│   ├── logger.py                    # Loguru, rotation journalière
│   ├── models.py                    # Candle, Signal (pydantic)
│   ├── market_data.py               # Client basé sur le SDK pocket-option (lecture seule)
│   ├── market_data_legacy.py        # Ancien client WebSocket "fait maison" (fallback)
│   ├── pairs_display.py             # Correspondance ticker -> affichage avec drapeaux
│   ├── bot.py                       # Bot Telegram (aiogram) + menu à boutons
│   ├── indicators/
│   │   └── ta.py                    # Heikin Ashi, Bollinger, SMA, EMA, RSI, MACD
│   └── strategies/
│       ├── strategy_s10.py          # S10 - SMA(5)/SMA(21) + Williams %R
│       ├── strategy_1m.py
│       ├── strategy_2m_cross.py     # M2 - croisement MACD relatif à la ligne zéro
│       └── strategy_5m.py           # règles à ajuster (non précisées dans le brief initial)
├── main.py
├── requirements.txt
├── install.sh                       # Linux / macOS
├── install.ps1                      # Windows
├── install-termux.sh                # Termux (Android)
├── .env.example
└── README.md
```

## Installation

### Linux / macOS

```bash
git clone <ton-repo>
cd po-signal-bot
chmod +x install.sh
./install.sh
```

### Windows (PowerShell)

```powershell
git clone <ton-repo>
cd po-signal-bot
powershell -ExecutionPolicy Bypass -File install.ps1
```

Si Python n'est pas installé : télécharge-le depuis
[python.org](https://www.python.org/downloads/) en cochant bien
**"Add python.exe to PATH"** pendant l'installation.

### Termux (Android)

```bash
pkg install git -y
git clone <ton-repo>
cd po-signal-bot
chmod +x install-termux.sh
./install-termux.sh
```

Notes spécifiques à Termux :
- Android tue les processus en arrière-plan : lance `termux-wake-lock` avant
  de démarrer le bot, et désactive l'optimisation de batterie pour Termux
  dans les paramètres Android.
- Pour garder le bot actif même en changeant d'application, installe et
  utilise `tmux` (`pkg install tmux`).
- Termux n'est pas fait pour un usage 24/7 fiable — pour un hébergement
  stable en continu, un petit VPS (Hetzner, Oracle Cloud Free Tier, OVH...)
  est recommandé.

## Lancement

```bash
# Linux/macOS : source venv/bin/activate d'abord
# Windows : .\venv\Scripts\Activate.ps1 d'abord
python main.py
```

## Configuration (.env)

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token obtenu via @BotFather |
| `ALLOWED_CHAT_IDS` | IDs Telegram autorisés à recevoir les signaux |
| `PO_SSID` | Session récupérée manuellement (voir plus haut) |
| `PO_UID` | UID numérique récupéré au même endroit que le SSID |
| `PAIRS` | Liste de paires OTC à surveiller (tickers bruts, sans drapeaux) |
| `MIN_PAYOUT` | Payout minimum pour générer un signal (%) |
| `TIMEFRAMES` | Timeframes dont les buffers de bougies sont maintenus, **en secondes** (10=S10, 60=M1, 120=M2, 300=M5) |
| `SCAN_INTERVAL_SECONDS` | Fréquence de recalcul des indicateurs |

Les drapeaux des paires sont ajoutés automatiquement dans les messages de
signal (`app/pairs_display.py`) — pas besoin de les mettre dans `.env`.

## Utilisation

1. `/start` dans Telegram → menu avec boutons.
2. "▶️ Démarrer le scan" active l'analyse en continu.
3. Coche/décoche les timeframes individuellement (✅/⬜️) : S10 / M1 / M2 / M5.
4. "📊 Statut" affiche l'état courant et les paires suivies.
5. Le bot envoie un message formaté dès qu'un signal valide est détecté,
   avec la stratégie à l'origine du signal et les conditions validées.

## Dépannage installation

**Conflit de dépendances `aiohttp` entre `aiogram` et `pocket-option`** :
`pocket-option` exige `aiohttp>=3.13`, alors que certaines versions
d'`aiogram` exigent `aiohttp<3.11`. Si `pip install -r requirements.txt`
échoue avec un message de conflit :

```bash
pip install --upgrade aiogram
pip install -r requirements.txt
```

Si le conflit persiste, regarde le message d'erreur de pip : il indique
généralement quelle version d'`aiogram` accepter pour satisfaire les deux
contraintes. Ouvre une issue si tu bloques dessus, ou repasse temporairement
sur l'ancien client (`app/market_data_legacy.py`, qui n'a pas cette
contrainte) en important `PocketOptionWSClient` à la place de
`PocketOptionSDKClient` dans `app/bot.py`.

## Avertissement

Le trading d'options binaires est à très haut risque et n'est pas autorisé
ou est fortement réglementé dans de nombreux pays. Ce projet est fourni à
titre éducatif/informatif, ne constitue pas un conseil financier, et
n'automatise aucune prise de position réelle.
