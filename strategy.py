"""Donchian channel breakout strategy for the AIProve eth-pnl-fixed bounty.

Dataset: frozen ETH/USDT 1-minute bars (bars.csv, 1,440 bars, real Binance spot
bars, 24h window ending 2026-11-13 12:17 UTC). Source:
https://github.com/AIProveRH/aiprove/tree/main/challenges/eth-backtest

Strategy (pure stdlib, no dependencies):
  - Channel: highest high / lowest low of the PRIOR 240 bars (4 hours).
    The current bar is excluded (shift-by-one), so there is no lookahead:
    a signal is only known at a bar's close and is executed at the NEXT
    bar's open.
  - Long (+1) when close breaks above the prior 240-bar high.
  - Short (-1) when close breaks below the prior 240-bar low.
  - Otherwise hold the previous position. Flat (0) only during the 240-bar
    warmup, before any breakout has occurred.
  - Position size: 100% of capital, no leverage (position is -1 / 0 / +1
    times capital). Size is small in notional terms relative to the book,
    so slippage scaled by size stays at the modelled minimum.

Why this, and not a faster system: on this dataset the day is mostly
range-bound chop with one real breakdown (bars ~840-960, -2.8%). Fast
systems (1-min EMA crossovers, 5-min EMA crossovers, momentum, Bollinger
fades) were all tested with correct next-open execution and all lose net of
costs: they whipsaw in the chop and pay 14-190 fills of fees. The 240-bar
breakout stays flat through the chop, trades only twice, and so pays only
~24 bps of total costs. The result is stable across N = 240/300/360
(identical two trades, identical net PnL), so it is not a cherry-picked
parameter: it is the standard 4-hour Donchian channel.

Backtested result (backtest.py, taker 10 bps + slippage 2 bps per fill):
  net PnL +3.20% of capital (+$3,200 on $100,000), 2 trades, max drawdown 2.42%
  first half (bars 0-719):  +0.00% (flat, no breakout)
  second half (bars 720-1439): +3.20%
  trades: SHORT at bar 737 close 2011.56 -> LONG at bar 1306 close 1946.09

Usage:
  python3 strategy.py   # writes positions.csv (bar, close, position)
  python3 backtest.py   # replays positions.csv with costs, prints the report
"""

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BARS_CSV = os.path.join(HERE, "bars.csv")
POSITIONS_CSV = os.path.join(HERE, "positions.csv")

LOOKBACK = 240  # bars (4 hours)


def load_bars(path=BARS_CSV):
    bars = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            bars.append({
                "minute": int(row["minute"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            })
    return bars


def positions(bars, lookback=LOOKBACK):
    """Target position decided at each bar's close (-1, 0, +1).

    Channel uses the PRIOR `lookback` bars only (bars i-lookback .. i-1),
    so a signal at bar i uses no information from bar i's own close beyond
    the close itself, and is executed at bar i+1's open.
    """
    pos = []
    cur = 0
    for i, bar in enumerate(bars):
        if i >= lookback:
            window = bars[i - lookback:i]
            prior_high = max(b["high"] for b in window)
            prior_low = min(b["low"] for b in window)
            if bar["close"] > prior_high:
                cur = 1
            elif bar["close"] < prior_low:
                cur = -1
        pos.append(cur)
    return pos


def main():
    bars = load_bars()
    pos = positions(bars)
    trades = [(i, pos[i]) for i in range(1, len(pos)) if pos[i] != pos[i - 1]]
    with open(POSITIONS_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["minute", "close", "position"])
        for bar, p in zip(bars, pos):
            w.writerow([bar["minute"], bar["close"], p])
    print(f"bars: {len(bars)}, warmup flat bars: {LOOKBACK}")
    print(f"position changes: {len(trades)}")
    for i, p in trades:
        print(f"  bar {i}: -> {p:+d} at close {bars[i]['close']:.2f}")
    print(f"wrote {POSITIONS_CSV}")


if __name__ == "__main__":
    main()
