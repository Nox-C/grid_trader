from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List

MarginMode = Literal["isolated", "cross"]

class DataRange(BaseModel):
    start: str  # YYYY-MM-DD
    end: str    # YYYY-MM-DD

class BacktestConfig(BaseModel):
    symbol: str = Field(default="PI_USDT_PERP")
    timeframe: str = Field(default="1m")
    margin_mode: MarginMode = Field(default="isolated")
    leverage: int = Field(default=125, ge=1, le=125)
    start: str = Field(default="2024-01-01")
    end: str = Field(default="2024-12-31")
    fees_bps: float = Field(default=0.0)  # zero for PI/USDT
    use_mark_price: bool = True

class GridParams(BaseModel):
    grid_levels: int = Field(ge=2)
    grid_spacing_pct: float = Field(gt=0)
    position_size_usdt: float = Field(gt=0)
    take_profit_pct: float = Field(gt=0)
    stop_loss_pct: float = Field(gt=0)
    post_only: bool = Field(default=True)

class OptimizeMatrix(BaseModel):
    grid_levels: List[int]
    grid_spacing_pct: List[float]
    position_size_usdt: List[float]
    take_profit_pct: List[float]
    stop_loss_pct: List[float]
    leverage: List[int]
