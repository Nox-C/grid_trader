#!/usr/bin/env python
from __future__ import annotations
import argparse
from backtest.exchange_sim import ExchangeSim
from config.settings import SETTINGS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=SETTINGS.default_contract)
    ap.add_argument("--timeframe", default=SETTINGS.default_timeframes[0])
    ap.add_argument("--margin", default=SETTINGS.default_margin_mode)
    ap.add_argument("--leverage", type=int, default=125)
    args = ap.parse_args()

    sim = ExchangeSim(symbol=args.symbol, margin_mode=args.margin, leverage=args.leverage)
    print(f"Initialized simulator for {args.symbol} {args.margin} x{args.leverage}")

if __name__ == "__main__":
    main()
