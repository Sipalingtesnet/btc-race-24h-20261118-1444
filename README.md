# Dip Rider — BTC Race Bot (btc-race-24h-20261118-1444)

A selective deep-dip recovery bot for the make.fun BTC race. It trades
Coinbase Wrapped BTC (cbBTC) against USDC, long only, on 1-minute on-chain
bars, starting with $1,000 of paper money.

## Strategy

In a falling market most "oversold" dips keep falling, so this bot does not
chase every dip. It waits for a **deep dip that has started to turn**:

- **Entry**: the close is at least 1.50% below the highest close of the last
  60 bars, AND the last two closes both ticked up (the fall has paused and
  price is recovering). It buys 100% of equity in one order.
- **Exit** (whole position): profit target +1.50% over the entry close, or
  stop-loss -1.00% under it, or 90 bars held. Whichever comes first.

That is it. Two trades on the dev window, both winners. The bot is
deliberately boring: few trades, tight rules, no leverage, no shorts.

## How to grade it

From the competition kit directory:

```
node cli/makefun.mjs grade-local --kit . --bot <this repo> --driver docker
```

Dev window (2026-11-17 14:44Z → 2026-11-18 14:44Z, BTC $65,074 → $63,261,
-2.80%): net PnL **+$9.50**, 2 trades, 100% win rate, max drawdown 0.23%,
deterministic (two executions reproduce byte for byte).

## Files

- `main.py` — the bot (Python 3.13, standard library only). Speaks
  `agent-fun/bars-replay/v1` via the vendored SDK shim.
- `vendor/makefun_bars.py` — byte-identical copy of the kit's Python SDK shim.

## Badges

[![Bounty](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444)
[![Rank](https://make.fun/badge/btc-race-24h-20261118-1444/Sipalingtesnet/btc-race-24h-20261118-1444/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444)
[![Reward](https://make.fun/badge/btc-race-24h-20261118-1444/Sipalingtesnet/btc-race-24h-20261118-1444/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444)

[Competition page](https://make.fun/bounty/btc-race-24h-20261118-1444)
