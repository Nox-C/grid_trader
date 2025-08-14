from __future__ import annotations
import pandas as pd


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    df = df.drop_duplicates(subset=["ts"]).sort_values("ts")
    # Coerce types
    for c in ["open","high","low","close","volume"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    return df
