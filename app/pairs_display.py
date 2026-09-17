"""
Table de correspondance entre le ticker technique utilisé par l'API
Pocket Option (ex: "EURUSD_otc") et son affichage lisible avec drapeaux
(ex: "🇪🇺 EUR/USD 🇺🇸 OTC"), utilisée uniquement dans les messages Telegram.

Le ticker technique (clé) est ce qui doit rester dans PAIRS= du .env.
Cette table ne sert qu'à l'affichage — rien à changer côté logique de scan.
"""

PAIR_DISPLAY = {
    # --- Majors / Cross ---
    "EURUSD_otc": "🇪🇺 EUR/USD 🇺🇸 OTC",
    "USDJPY_otc": "🇺🇸 USD/JPY 🇯🇵 OTC",
    "GBPUSD_otc": "🇬🇧 GBP/USD 🇺🇸 OTC",
    "USDCAD_otc": "🇺🇸 USD/CAD 🇨🇦 OTC",
    "USDCHF_otc": "🇺🇸 USD/CHF 🇨🇭 OTC",
    "AUDUSD_otc": "🇦🇺 AUD/USD 🇺🇸 OTC",
    "NZDUSD_otc": "🇳🇿 NZD/USD 🇺🇸 OTC",
    "EURGBP_otc": "🇪🇺 EUR/GBP 🇬🇧 OTC",
    "EURJPY_otc": "🇪🇺 EUR/JPY 🇯🇵 OTC",
    "EURCAD_otc": "🇪🇺 EUR/CAD 🇨🇦 OTC",
    "EURCHF_otc": "🇪🇺 EUR/CHF 🇨🇭 OTC",
    "EURNZD_otc": "🇪🇺 EUR/NZD 🇳🇿 OTC",
    "EURHUF_otc": "🇪🇺 EUR/HUF 🇭🇺 OTC",
    "EURTRY_otc": "🇪🇺 EUR/TRY 🇹🇷 OTC",
    "EURRUB_otc": "🇪🇺 EUR/RUB 🇷🇺 OTC",
    "GBPJPY_otc": "🇬🇧 GBP/JPY 🇯🇵 OTC",
    "GBPCAD_otc": "🇬🇧 GBP/CAD 🇨🇦 OTC",
    "GBPCHF_otc": "🇬🇧 GBP/CHF 🇨🇭 OTC",
    "GBPAUD_otc": "🇬🇧 GBP/AUD 🇦🇺 OTC",
    "AUDCAD_otc": "🇦🇺 AUD/CAD 🇨🇦 OTC",
    "AUDCHF_otc": "🇦🇺 AUD/CHF 🇨🇭 OTC",
    "AUDJPY_otc": "🇦🇺 AUD/JPY 🇯🇵 OTC",
    "AUDNZD_otc": "🇦🇺 AUD/NZD 🇳🇿 OTC",
    "CADCHF_otc": "🇨🇦 CAD/CHF 🇨🇭 OTC",
    "CADJPY_otc": "🇨🇦 CAD/JPY 🇯🇵 OTC",
    "CHFJPY_otc": "🇨🇭 CHF/JPY 🇯🇵 OTC",
    "CHFNOK_otc": "🇨🇭 CHF/NOK 🇳🇴 OTC",
    "NZDJPY_otc": "🇳🇿 NZD/JPY 🇯🇵 OTC",

    # --- Exotiques (base USD) ---
    "USDCNH_otc": "🇺🇸 USD/CNH 🇨🇳 OTC",
    "USDINR_otc": "🇺🇸 USD/INR 🇮🇳 OTC",
    "USDBRL_otc": "🇺🇸 USD/BRL 🇧🇷 OTC",
    "USDRUB_otc": "🇺🇸 USD/RUB 🇷🇺 OTC",
    "USDTRY_otc": "🇺🇸 USD/TRY 🇹🇷 OTC",
    "USDMXN_otc": "🇺🇸 USD/MXN 🇲🇽 OTC",
    "USDEGP_otc": "🇺🇸 USD/EGP 🇪🇬 OTC",
    "USDPHP_otc": "🇺🇸 USD/PHP 🇵🇭 OTC",
    "USDPKR_otc": "🇺🇸 USD/PKR 🇵🇰 OTC",
    "USDIDR_otc": "🇺🇸 USD/IDR 🇮🇩 OTC",
    "USDMYR_otc": "🇺🇸 USD/MYR 🇲🇾 OTC",
    "USDTHB_otc": "🇺🇸 USD/THB 🇹🇭 OTC",
    "USDZAR_otc": "🇺🇸 USD/ZAR 🇿🇦 OTC",
    "USDARS_otc": "🇺🇸 USD/ARS 🇦🇷 OTC",
    "USDCOP_otc": "🇺🇸 USD/COP 🇨🇴 OTC",
    "USDCLP_otc": "🇺🇸 USD/CLP 🇨🇱 OTC",
    "USDBDT_otc": "🇺🇸 USD/BDT 🇧🇩 OTC",
    "USDVND_otc": "🇺🇸 USD/VND 🇻🇳 OTC",
    "USDDZD_otc": "🇺🇸 USD/DZD 🇩🇿 OTC",
    "USDSGD_otc": "🇺🇸 USD/SGD 🇸🇬 OTC",

    # --- Inversées (devise locale / USD) ---
    "UAHUSD_otc": "🇺🇦 UAH/USD 🇺🇸 OTC",
    "NGNUSD_otc": "🇳🇬 NGN/USD 🇺🇸 OTC",
    "MADUSD_otc": "🇲🇦 MAD/USD 🇺🇸 OTC",
    "ZARUSD_otc": "🇿🇦 ZAR/USD 🇺🇸 OTC",
    "YERUSD_otc": "🇾🇪 YER/USD 🇺🇸 OTC",
    "LBPUSD_otc": "🇱🇧 LBP/USD 🇺🇸 OTC",
    "KESUSD_otc": "🇰🇪 KES/USD 🇺🇸 OTC",
    "TNDUSD_otc": "🇹🇳 TND/USD 🇺🇸 OTC",

    # --- Asie / Moyen-Orient (cross CNY) ---
    "AEDCNY_otc": "🇦🇪 AED/CNY 🇨🇳 OTC",
    "OMRCNY_otc": "🇴🇲 OMR/CNY 🇨🇳 OTC",
    "SARCNY_otc": "🇸🇦 SAR/CNY 🇨🇳 OTC",
    "QARCNY_otc": "🇶🇦 QAR/CNY 🇨🇳 OTC",
    "JODCNY_otc": "🇯🇴 JOD/CNY 🇨🇳 OTC",
    "BHDCNY_otc": "🇧🇭 BHD/CNY 🇨🇳 OTC",
}


def display_pair(ticker: str) -> str:
    """Retourne le nom avec drapeaux si connu, sinon le ticker brut tel quel."""
    return PAIR_DISPLAY.get(ticker, ticker)
