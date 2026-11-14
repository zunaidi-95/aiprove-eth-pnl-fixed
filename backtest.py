"""Backtest the Donchian strategy in strategy.py against bars.csv.

Execution model (no phantom fills):
  - A position decided at bar i's close is executed at bar i+1's open.
  - P&L accrues from open to open while the position is held.
  - Costs per fill: taker fee 10 bps + slippage 2 bps = 12 bps of the
    notional traded (Binance standard spot taker; slippage at the modelled
    minimum because size is 1x capital, no leverage).
  - Starting capital: $100,000 (reported PnL is also given as % of capital,
    which is capital-independent).

Run: python3 backtest.py
"""

import csv
import os

from strategy import load_bars, positions

HERE = os.path.dirname(os.path.abspath(__file__))
CAPITAL = 100_000.0
TAKER_BPS = 10.0
SLIPPAGE_BPS = 2.0


def backtest(bars, pos, taker_bps=TAKER_BPS, slippage_bps=SLIPPAGE_BPS):
    n = len(bars)
    opens = [b["open"] for b in bars]
    equity = CAPITAL
    peak = CAPITAL
    max_dd = 0.0
    trades = 0
    cur = 0.0
    equity_curve = [CAPITAL]
    cost_per_fill = (taker_bps + slippage_bps) / 10_000.0
    for i in range(n - 2):
        target = float(pos[i])
        if target != cur:
            # cost is charged on the notional actually traded
            equity -= abs(target - cur) * cost_per_fill * CAPITAL
            trades += 1
            cur = target
        equity += cur * CAPITAL * (opens[i + 2] - opens[i + 1]) / opens[i + 1]
        equity_curve.append(equity)
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak)
    net_pct = (equity - CAPITAL) / CAPITAL * 100.0
    half = equity_curve[720] if len(equity_curve) > 720 else float("nan")
    h1 = (half - CAPITAL) / CAPITAL * 100.0
    h2 = (equity - half) / half * 100.0
    return {
        "net_pct": net_pct,
        "net_usd": equity - CAPITAL,
        "trades": trades,
        "max_dd_pct": max_dd * 100.0,
        "h1_pct": h1,
        "h2_pct": h2,
        "final_equity": equity,
    }


def main():
    bars = load_bars()
    pos = positions(bars)
    r = backtest(bars, pos)
    print("=== eth-pnl-fixed backtest (Donchian 240, next-open execution) ===")
    print(f"bars: {len(bars)}  first close {bars[0]['close']:.2f}  "
          f"last close {bars[-1]['close']:.2f}  "
          f"buy-and-hold {(bars[-1]['close'] / bars[0]['close'] - 1) * 100:+.2f}%")
    print(f"costs: taker {TAKER_BPS:.0f} bps + slippage {SLIPPAGE_BPS:.0f} bps "
          f"per fill, capital ${CAPITAL:,.0f}")
    print(f"net PnL:  {r['net_pct']:+.2f}%  (${r['net_usd']:+,.2f})")
    print(f"trades:   {r['trades']} position changes")
    print(f"max DD:   {r['max_dd_pct']:.2f}%")
    print(f"first half (bars 0-719):   {r['h1_pct']:+.2f}%")
    print(f"second half (bars 720+):   {r['h2_pct']:+.2f}%")
    print(f"final equity: ${r['final_equity']:,.2f}")
    print("--- fee sensitivity (same positions) ---")
    for taker, slip in [(5, 1), (10, 2), (20, 5)]:
        rr = backtest(bars, pos, taker, slip)
        print(f"  taker {taker:>2} bps + slip {slip} bps: "
              f"net {rr['net_pct']:+.2f}%  maxDD {rr['max_dd_pct']:.2f}%")


if __name__ == "__main__":
    main()
