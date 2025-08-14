"""
Downloader for MEXC PI/USDT linear perpetual data.
- Prefer official MEXC SDK; fallback to ccxt for klines/funding where needed.
- Cache to backtest/data/cache/ as Parquet/CSV.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import pandas as pd
import ccxt

CACHE_DIR = Path(__file__).resolve().parent / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_klines_ccxt(symbol: str, timeframe: str, since_ms: Optional[int] = None, limit: int = 1000) -> pd.DataFrame:
    ex = ccxt.mexc()
    ex.options = {"defaultType": "swap"}
    all_rows = []
    fetch_since = since_ms
    while True:
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, since=fetch_since, limit=limit, params={"contractType": "PERPETUAL"})
        if not ohlcv:
            break
        all_rows.extend(ohlcv)
        if len(ohlcv) < limit:
            break
        fetch_since = ohlcv[-1][0] + 1
    if not all_rows:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"])    
    df = pd.DataFrame(all_rows, columns=["ts","open","high","low","close","volume"])    
    return df


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)


def load_cached(path: Path) -> Optional[pd.DataFrame]:
    if path.exists():
        if path.suffix == ".parquet":
            return pd.read_parquet(path)
        return pd.read_csv(path)
    return None


def get_or_download_klines(symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
    cache_path = CACHE_DIR / f"{symbol.replace('/','_')}_{timeframe}_{start}_{end}.parquet"
    cached = load_cached(cache_path)
    if cached is not None:
        return cached
    # NOTE: Proper start/end slicing to be added after full SDK integration
    df = fetch_klines_ccxt(symbol, timeframe)
    save_df(df, cache_path)
    return df
