from __future__ import annotations
from pydantic import BaseModel, Field

class GridParams(BaseModel):
    grid_levels: int = Field(ge=2)
    grid_spacing_pct: float = Field(gt=0)
    position_size_usdt: float = Field(gt=0)
    take_profit_pct: float = Field(gt=0)
    stop_loss_pct: float = Field(gt=0)
    post_only: bool = Field(default=True)

# Placeholder strategy implementation will be added later.
