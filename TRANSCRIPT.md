# Build transcript — eth-pnl-fixed (agent ZephyrCircuit)

Session: 2026-11-14 ~18:37-18:50 WIB. All commands run locally; no secrets
involved (no keys, no tokens in this transcript).

## 1. Dataset + bounty spec

- `GET /api/bounties/eth-pnl-fixed` (200): "Highest backtest PnL on the
  fixed ETH dataset", 2,000,000 PROVE, AutoGrade, metric "Net PnL after
  costs", 125 subs / 177 agents, closes Nov 20, 2026 13:49 UTC. Brief:
  frozen published ETH 1-min dataset, maker/taker fees + slippage scaled
  by size, highest net PnL wins, ties break on lower max drawdown, submit
  repo at one commit + transcript, sandbox replays with no phantom fills.
- `git clone https://github.com/AIProveRH/aiprove.git` (depth 1):
  `challenges/eth-backtest/` contains README.md + bars.csv (1,440 bars).
- `GET /skill.md` (repo): code/strategy submissions use
  `{"repoUrl", "commit", "transcript", "handle"}`.

## 2. Strategy research (all with correct next-open execution)

Tested, at taker 10 bps + slippage 2 bps per fill:
- 1-min EMA crossovers 8/21..50/120: -18.65% .. -1.65% (whipsaw in chop)
- 5-min EMA 6/18, first draft: +3.26% — then found a LOOKAHEAD BUG (the
  5-min signal was applied to 1-min bars before the 5-min bar closed).
  Corrected timing: -1.15%. Discarded, not submitted.
- Momentum 60/120/240/360: -14.71% .. -5.70%
- Bollinger fades 20/2.0, 60/2.0, 20/1.5: -10.20%, -6.50%, -15.60%
- Donchian N=120/180/240/300/360/480: -0.08%, +2.41%, +3.20%, +3.20%,
  +3.20%, +1.69% — stable plateau at 240-360, identical two trades.
- Short-and-hold: +3.16% (1 trade) — rejected as a naked directional bet
  on one sample; the challenge warns a held-out tail punishes overfitting.

Selected: Donchian 240 (4-hour channel), 100% capital, no leverage.

## 3. Final run (verbatim)

```
$ python3 strategy.py
bars: 1440, warmup flat bars: 240
position changes: 2
  bar 738: -> -1 at close 2006.03
  bar 1307: -> +1 at close 1948.26
wrote positions.csv

$ python3 backtest.py
=== eth-pnl-fixed backtest (Donchian 240, next-open execution) ===
bars: 1440  first close 2028.68  last close 1960.59  buy-and-hold -3.36%
costs: taker 10 bps + slippage 2 bps per fill, capital $100,000
net PnL:  +3.20%  ($+3,204.71)
trades:   2 position changes
max DD:   2.42%
first half (bars 0-719):   +0.00%
second half (bars 720+):   +3.20%
final equity: $103,204.71
--- fee sensitivity (same positions) ---
  taker  5 bps + slip 1 bps: net +3.38%  maxDD 2.30%
  taker 10 bps + slip 2 bps: net +3.20%  maxDD 2.42%
  taker 20 bps + slip 5 bps: net +2.81%  maxDD 2.67%
```

## 4. Commit

```
$ git init && git add -A && git commit -m "Donchian 240 breakout: backtested net +3.20%, 2 trades, max DD 2.42%"
0608795e678f119ad85f388442289f57e82ee33f
```

## 5. Submission status

- Entered the bounty via `POST /api/bounties/eth-pnl-fixed/enter` (see
  group-6 report for the entry id).
- SUBMIT BLOCKED: the submit shape needs a public `repoUrl` + commit.
  This sandbox has no GitHub login (`gh auth status`: not logged into any
  GitHub hosts; no GitHub token in the environment), so the repo cannot be
  published from here. The repo is complete and committed locally at
  `~/workspace/aiprove-all/eth-pnl-fixed/` (commit
  0608795e678f119ad85f388442289f57e82ee33f). To finish: create a public
  GitHub repo, push this directory to it, then
  `POST /api/bounties/eth-pnl-fixed/submit` with
  `{"repoUrl": "<public repo URL>", "commit": "0608795e678f119ad85f388442289f57e82ee33f",
    "transcript": "<this transcript, secrets stripped>", "handle": "ZephyrCircuit"}`.
  No placeholder/bogus repoUrl was submitted.
