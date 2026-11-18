"""Dip Rider: a selective deep-dip recovery bot for the make.fun BTC race.

Long only. Buys ONLY a deep dip that has started to turn: the close is at
least 1.5% below the 60-bar high AND the last two closes ticked up (the
fall has paused and price is recovering). It does not chase every oversold
wiggle — in a falling market most of those keep falling. Sells on a profit
target, a stop, or a max hold. Deterministic: no wall clock, no network,
no unseeded random; all decisions are pure functions of the bars seen so far.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# ---- Strategy parameters ----
HI_BARS = 60            # lookback for the reference high
DIP_BPS = 150           # entry only >= 1.50% below the HI_BARS high
POSITION_FRAC_BPS = 10000  # buy 100% of equity per signal
TAKE_PROFIT_BPS = 150   # sell at +1.50% over entry
STOP_LOSS_BPS = 100      # sell at -1.00% under entry
MAX_HOLD_BARS = 90       # sell after this many bars held
MAX_SLIPPAGE_BPS = 100   # 1% past the close decided on


class Series:
    """Per-symbol state: closes, entry bookkeeping."""

    def __init__(self):
        self.closes = []
        self.entry_price = None
        self.hold_bars = 0

    def push(self, close):
        self.closes.append(close)

    def high(self, n):
        """Highest close of the last n bars (excluding the current one)."""
        if len(self.closes) < 2:
            return None
        window = self.closes[-n - 1:-1] if len(self.closes) > n else self.closes[:-1]
        return max(window) if window else None


SERIES = Series()


def on_batch(state, batch):
    """Decide the orders for this batch. Returns a list of order dicts."""
    bar = state.latest.get(SYMBOL)
    if bar is not None:
        SERIES.push(int(bar["c"]))
        if state.positions.get(SYMBOL) is not None:
            SERIES.hold_bars += 1
    if state.warming_up:
        return []
    close = state.close(SYMBOL)
    if close is None:
        return []
    held = state.positions.get(SYMBOL)
    orders = []

    if held is not None:
        sell = False
        if SERIES.entry_price is not None:
            if close * 10000 >= SERIES.entry_price * (10000 + TAKE_PROFIT_BPS):
                sell = True
            if close * 10000 <= SERIES.entry_price * (10000 - STOP_LOSS_BPS):
                sell = True
        if SERIES.hold_bars >= MAX_HOLD_BARS:
            sell = True
        if sell:
            orders.append({
                "side": "sell",
                "symbol": SYMBOL,
                "qty": held.qty,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            })
            SERIES.entry_price = None
            SERIES.hold_bars = 0
        return orders

    # --- Entry: deep dip (>= DIP_BPS below the HI_BARS high) that has
    # started to turn: last two closes both ticked up. ---
    if len(SERIES.closes) < HI_BARS + 2:
        return []
    hi = SERIES.high(HI_BARS)
    if hi is None:
        return []
    deep = close * 10000 < hi * (10000 - DIP_BPS)
    turning = (
        SERIES.closes[-1] > SERIES.closes[-2]
        and SERIES.closes[-2] > SERIES.closes[-3]
    )
    if deep and turning:
        room = state.weight_room(SYMBOL)
        stake = state.equity * POSITION_FRAC_BPS // 10000
        amount = stake if stake < room else room
        if amount > state.cash:
            amount = state.cash
        min_notional = int(state.hello["fees"]["min_notional_quote_units"])
        if amount >= min_notional and amount > 0:
            orders.append({
                "side": "buy",
                "symbol": SYMBOL,
                "notional_quote_units": amount,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            })
            SERIES.entry_price = close
            SERIES.hold_bars = 0
    return orders


makefun_bars.run(on_batch)
