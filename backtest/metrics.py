"""
Metrics computation for backtests.
Skeleton: converts equity curve to stats (total return, sharpe, max drawdown, win rate, profit factor, funding sum, liq count).
"""
from __future__ import annotations
from typing import List, Dict
import math


def compute_metrics(equity_curve: List[Dict]) -> Dict:
    if not equity_curve:
        return {"total_return": 0, "sharpe_ratio": 0, "max_drawdown": 0, "win_rate": 0, "profit_factor": 0}
    totals = [row["total"] for row in equity_curve if "total" in row]
    if not totals:
        return {"total_return": 0, "sharpe_ratio": 0, "max_drawdown": 0, "win_rate": 0, "profit_factor": 0}
    start, end = totals[0], totals[-1]
    total_return = (end - start) / start if start else 0.0
    # Simple dd
    peak, max_dd = totals[0], 0.0
    for v in totals:
        peak = max(peak, v)
        dd = (peak - v) / peak if peak else 0.0
        max_dd = max(max_dd, dd)
    # Placeholder sharpe/pf/win until trades wired
    return {
        "total_return": total_return,
        "sharpe_ratio": 0.0,
        "max_drawdown": max_dd,
        "win_rate": 0.0,
        "profit_factor": 0.0,
    }
