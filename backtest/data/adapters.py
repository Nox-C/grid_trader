"""
Adapters to unify data from MEXC SDK and ccxt.
"""
from __future__ import annotations
from typing import Any, Dict
import pandas as pd


def ccxt_ohlcv_to_df(rows: list[list[Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"])    
    return pd.DataFrame(rows, columns=["ts","open","high","low","close","volume"])    
