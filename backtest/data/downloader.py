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


def _normalize_swap_symbol(ex: ccxt.Exchange, symbol: str) -> str:
    """Ensure symbol targets swap market (e.g., PI/USDT:USDT)."""
    # Many ccxt implementations expect ":USDT" for linear swaps
    if symbol.endswith(":USDT"):
        return symbol
    if "/USDT" in symbol:
        return symbol + ":USDT"
    return symbol


def fetch_klines_ccxt(symbol: str, timeframe: str, since_ms: Optional[int] = None, end_ms: Optional[int] = None, limit: int = 1000) -> pd.DataFrame:
    ex = ccxt.mexc()
    # Ensure options has required keys to avoid KeyError
    ex.options = {
        **getattr(ex, "options", {}),
        "defaultType": "swap",
        "adjustForTimeDifference": False,
    }
    try:
        ex.load_markets()
    except Exception:
        # proceed; some versions lazy-load on first fetch
        pass
    symbol = _normalize_swap_symbol(ex, symbol)
    all_rows: list[list] = []
    # Reverse paginate using endTime windows (more reliable on MEXC)
    ms_per_candle = 60_000 if timeframe == '1m' else 60_000
    window_ms = limit * ms_per_candle
    cursor_end = end_ms
    if cursor_end is None:
        cursor_end = int(pd.Timestamp.utcnow().timestamp() * 1000)
    while True:
        if cursor_end < (since_ms or 0):
            break
        w_start = max((cursor_end - window_ms + 1), (since_ms or 0))
        params = {"contractType": "PERPETUAL", "endTime": cursor_end}
        # Only include startTime if we have a lower bound; some APIs ignore but safe to send
        if since_ms is not None:
            params["startTime"] = w_start
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, since=None, limit=limit, params=params)
        if ohlcv:
            # Bound and append
            bounded = [row for row in ohlcv if (since_ms is None or row[0] >= since_ms) and (end_ms is None or row[0] <= end_ms)]
            all_rows.extend(bounded)
            first_ts = ohlcv[0][0]
            # Move the window backward from the first candle we just saw
            new_cursor_end = first_ts - 1
            if new_cursor_end >= cursor_end:
                # no progress; break to avoid infinite loop
                break
            cursor_end = new_cursor_end
        else:
            # No data returned; move cursor back by one full window
            cursor_end = w_start - 1
        if cursor_end < (since_ms or 0):
            break
    if not all_rows:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"])    
    # Deduplicate and sort
    df = pd.DataFrame(all_rows, columns=["ts","open","high","low","close","volume"]).drop_duplicates(subset=["ts"]).sort_values("ts").reset_index(drop=True)
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


def get_or_download_klines(symbol: str, timeframe: str, start: str, end: str, force: bool = False) -> pd.DataFrame:
    # Normalize cache filename (avoid ':' in swap symbols)
    safe_symbol = symbol.replace('/', '_').replace(':', '_')
    cache_path = CACHE_DIR / f"{safe_symbol}_{timeframe}_{start}_{end}.parquet"
    cached = load_cached(cache_path)
    if (not force) and (cached is not None):
        return cached
    # Compute ms bounds in UTC
    start_ms = int(pd.Timestamp(start, tz='UTC').timestamp() * 1000)
    # For end, include the whole day: set to end-of-day 23:59:59 if date-only
    end_ts = pd.Timestamp(end)
    if end_ts.tzinfo is None:
        # assume date-only string; take 23:59:59 UTC of that date
        end_ms = int(pd.Timestamp(end + ' 23:59:59', tz='UTC').timestamp() * 1000)
    else:
        end_ms = int(end_ts.tz_convert('UTC').timestamp() * 1000)
    df = fetch_klines_ccxt(symbol, timeframe, since_ms=start_ms, end_ms=end_ms)
    # Final strict bound in case last page overshot
    if not df.empty:
        df = df[(df['ts'] >= start_ms) & (df['ts'] <= end_ms)].reset_index(drop=True)
    save_df(df, cache_path)
    return df


# ------------------------ Funding Rates ------------------------
def fetch_funding_rates_ccxt(symbol: str, since_ms: Optional[int], end_ms: Optional[int], limit: int = 1000) -> pd.DataFrame:
    ex = ccxt.mexc()
    ex.options = {**getattr(ex, "options", {}), "defaultType": "swap", "adjustForTimeDifference": False}
    try:
        ex.load_markets()
    except Exception:
        pass
    market_symbol = _normalize_swap_symbol(ex, symbol)
    all_rows: list[dict] = []
    cursor = since_ms
    while True:
        params = {"contractType": "PERPETUAL"}
        # ccxt signature: fetchFundingRateHistory(symbol=None, since=None, limit=None, params={})
        rows = ex.fetch_funding_rate_history(market_symbol, since=cursor, limit=limit, params=params)
        if not rows:
            break
        for r in rows:
            ts = r.get('timestamp') or r.get('datetime')
            rate = r.get('fundingRate') or r.get('fundingRateDaily') or r.get('info', {}).get('fundingRate')
            if ts is None or rate is None:
                continue
            if end_ms is not None and ts > end_ms:
                continue
            all_rows.append({"ts": ts, "rate": float(rate)})
        last_ts = rows[-1].get('timestamp')
        if last_ts is None:
            break
        if end_ms is not None and last_ts >= end_ms:
            break
        next_cursor = last_ts + 1
        if cursor is not None and next_cursor <= cursor:
            break
        cursor = next_cursor
    if not all_rows:
        return pd.DataFrame(columns=["ts", "rate"])
    df = pd.DataFrame(all_rows).drop_duplicates(subset=["ts"]).sort_values("ts").reset_index(drop=True)
    return df


def get_or_download_funding(symbol: str, start: str, end: str, force: bool = False) -> pd.DataFrame:
    safe_symbol = symbol.replace('/', '_').replace(':', '_')
    cache_path = CACHE_DIR / f"{safe_symbol}_funding_{start}_{end}.parquet"
    cached = load_cached(cache_path)
    if (not force) and (cached is not None):
        return cached
    start_ms = int(pd.Timestamp(start, tz='UTC').timestamp() * 1000)
    end_ts = pd.Timestamp(end)
    if end_ts.tzinfo is None:
        end_ms = int(pd.Timestamp(end + ' 23:59:59', tz='UTC').timestamp() * 1000)
    else:
        end_ms = int(end_ts.tz_convert('UTC').timestamp() * 1000)
    df = fetch_funding_rates_ccxt(symbol, start_ms, end_ms)
    save_df(df, cache_path)
    return df


# ------------------------ Mark Price OHLCV ------------------------
def fetch_mark_ohlcv_ccxt(symbol: str, timeframe: str, since_ms: Optional[int], end_ms: Optional[int], limit: int = 1000) -> pd.DataFrame:
    ex = ccxt.mexc()
    ex.options = {**getattr(ex, "options", {}), "defaultType": "swap", "adjustForTimeDifference": False}
    try:
        ex.load_markets()
    except Exception:
        pass
    market_symbol = _normalize_swap_symbol(ex, symbol)
    all_rows: list[list] = []
    # Some exchanges implement fetchMarkOHLCV; ccxt exposes unified method name
    has_mark = getattr(ex, 'has', {}).get('fetchMarkOHLCV', False)
    if not has_mark:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"])  # graceful fallback
    ms_per_candle = 60_000 if timeframe == '1m' else 60_000
    window_ms = limit * ms_per_candle
    cursor_end = end_ms or int(pd.Timestamp.utcnow().timestamp() * 1000)
    while True:
        if cursor_end < (since_ms or 0):
            break
        w_start = max((cursor_end - window_ms + 1), (since_ms or 0))
        params = {"contractType": "PERPETUAL", "endTime": cursor_end}
        if since_ms is not None:
            params["startTime"] = w_start
        ohlcv = ex.fetch_mark_ohlcv(market_symbol, timeframe=timeframe, since=None, limit=limit, params=params)
        if ohlcv:
            bounded = [row for row in ohlcv if (since_ms is None or row[0] >= since_ms) and (end_ms is None or row[0] <= end_ms)]
            all_rows.extend(bounded)
            first_ts = ohlcv[0][0]
            new_cursor_end = first_ts - 1
            if new_cursor_end >= cursor_end:
                break
            cursor_end = new_cursor_end
        else:
            cursor_end = w_start - 1
        if cursor_end < (since_ms or 0):
            break
    if not all_rows:
        return pd.DataFrame(columns=["ts","open","high","low","close","volume"])    
    df = pd.DataFrame(all_rows, columns=["ts","open","high","low","close","volume"]).drop_duplicates(subset=["ts"]).sort_values("ts").reset_index(drop=True)
    return df


def get_or_download_mark(symbol: str, timeframe: str, start: str, end: str, force: bool = False) -> pd.DataFrame:
    safe_symbol = symbol.replace('/', '_').replace(':', '_')
    cache_path = CACHE_DIR / f"{safe_symbol}_mark_{timeframe}_{start}_{end}.parquet"
    cached = load_cached(cache_path)
    if (not force) and (cached is not None):
        return cached
    start_ms = int(pd.Timestamp(start, tz='UTC').timestamp() * 1000)
    end_ts = pd.Timestamp(end)
    if end_ts.tzinfo is None:
        end_ms = int(pd.Timestamp(end + ' 23:59:59', tz='UTC').timestamp() * 1000)
    else:
        end_ms = int(end_ts.tz_convert('UTC').timestamp() * 1000)
    df = fetch_mark_ohlcv_ccxt(symbol, timeframe, start_ms, end_ms)
    save_df(df, cache_path)
    return df
