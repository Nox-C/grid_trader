"""
Exchange specs normalization for MEXC linear perpetuals.
- Fetches and stores: tick size, lot size, min notional, risk tiers (maintenance margin rates/amounts), contract multiplier.
- Provides helpers to round price/qty, validate orders, and compute maintenance margin.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RiskTier:
    notional_cap: float
    maintenance_margin_rate: float
    maintenance_amount: float

@dataclass
class ContractSpecs:
    symbol: str  # e.g., PI_USDT_PERP
    tick_size: float
    lot_size: float
    min_notional: float
    multiplier: float  # contract size per 1 qty, for linear USDT-margined often 1
    risk_tiers: List[RiskTier]

    def round_price(self, price: float) -> float:
        ts = self.tick_size
        return round((price // ts) * ts, 8)

    def round_qty(self, qty: float) -> float:
        ls = self.lot_size
        return round((qty // ls) * ls, 8)

    def valid_notional(self, price: float, qty: float) -> bool:
        return (price * qty) >= self.min_notional

    def tier_for_notional(self, notional: float) -> RiskTier:
        tiers = sorted(self.risk_tiers, key=lambda t: t.notional_cap)
        for t in tiers:
            if notional <= t.notional_cap:
                return t
        return tiers[-1]

# Placeholder registry to be populated by downloader/adapters
_SPECS_REGISTRY: dict[str, ContractSpecs] = {}

def register_specs(specs: ContractSpecs) -> None:
    _SPECS_REGISTRY[specs.symbol] = specs

def get_specs(symbol: str) -> Optional[ContractSpecs]:
    return _SPECS_REGISTRY.get(symbol)
