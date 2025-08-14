#!/usr/bin/env python
from __future__ import annotations
import argparse
from backtest.data.downloader import get_or_download_klines
from config.settings import SETTINGS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=SETTINGS.default_symbol)
    ap.add_argument("--timeframe", default=SETTINGS.default_timeframes[0])
    ap.add_argument("--start", default=SETTINGS.default_start)
    ap.add_argument("--end", default=SETTINGS.default_end)
    args = ap.parse_args()

    df = get_or_download_klines(args.symbol, args.timeframe, args.start, args.end)
    print(f"Downloaded rows: {len(df)} for {args.symbol} {args.timeframe}")

if __name__ == "__main__":
    main()
