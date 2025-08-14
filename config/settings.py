from __future__ import annotations
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AppSettings:
    env: str = os.getenv("APP_ENV", "offline")  # offline|testnet|production
    api_key: str | None = os.getenv("MEXC_API_KEY")
    api_secret: str | None = os.getenv("MEXC_API_SECRET")

    default_symbol: str = os.getenv("DEFAULT_SYMBOL", "PI/USDT")
    default_contract: str = os.getenv("DEFAULT_CONTRACT", "PI_USDT_PERP")
    default_timeframes: list[str] = field(default_factory=lambda: os.getenv("DEFAULT_TIMEFRAMES", "1m").split(","))
    default_margin_mode: str = os.getenv("DEFAULT_MARGIN_MODE", "isolated")  # isolated|cross

    default_start: str = os.getenv("DEFAULT_START", "2024-01-01")
    default_end: str = os.getenv("DEFAULT_END", "2024-12-31")

SETTINGS = AppSettings()
