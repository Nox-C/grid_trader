"""
MEXC-parity exchange simulator (linear USDT perpetuals).
- Order types: LIMIT/MARKET, post-only, TIF (GTC/IOC/FOK)
- Constraints: tick/lot/minNotional
- Margin: isolated/cross, leverage up to 125x
- PnL: mark-price based unrealized/realized
- Funding: applied at funding timestamps
- Liquidation: maintenance tiers, liq/bankruptcy price
This is a skeleton; methods will be implemented incrementally.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, List, Dict

Side = Literal["buy", "sell"]
OrderType = Literal["limit", "market"]
TIF = Literal["GTC", "IOC", "FOK"]

@dataclass
class Order:
    id: str
    side: Side
    type: OrderType
    price: Optional[float]
    qty: float
    tif: TIF = "GTC"
    post_only: bool = False

@dataclass
class Position:
    qty: float = 0.0
    entry_price: float = 0.0

class ExchangeSim:
    def __init__(self, symbol: str, margin_mode: str = "isolated", leverage: int = 125):
        self.symbol = symbol
        self.margin_mode = margin_mode
        self.leverage = leverage
        self.balance_usdt: float = 0.0
        self.position = Position()
        self.open_orders: Dict[str, Order] = {}

    def on_bar(self, o: float, h: float, l: float, c: float, ts: int) -> None:
        """Advance one candle. Will implement matching, funding, liq checks."""
        pass

    def place_order(self, order: Order) -> str:
        """Validate/normalize then accept order. Returns order id."""
        oid = order.id
        self.open_orders[oid] = order
        return oid

    def cancel_order(self, order_id: str) -> None:
        self.open_orders.pop(order_id, None)

    def equity(self, mark_price: float) -> float:
        """Cash + position value(mark)."""
        pnl = (mark_price - self.position.entry_price) * self.position.qty if self.position.qty else 0.0
        return self.balance_usdt + pnl
