# MOMENTUM SEQUENCE  — A-020
## Written 2026-09-05, BEFORE any result exists. Nothing below may change.

Source: user-supplied Pine v6, "Momentum Sequence Strategy ". Rules read
from the code, not from a description.

## THE RULE, AS THE PINE WRITES IT

With the signal bar at index k and `followingCandles` N = 5 (Pine default):

    MAIN candle    bar k-5 must be BEARISH        close[k-5] < open[k-5]
    SEQUENCE       bars k-4 .. k, all five:
                     (i)   bullish                close[i] > open[i]
                     (ii)  low[i] > low[k-5]      never breaches the main low
                     (iii) close[i] > close[i-1]  each closes above the last
    ENTRY          market at the signal bar's close -> fills NEXT bar's OPEN
    STOP           low[k-5]  (the main bearish candle's low)
    TARGET         close[k] + 1.5 * (close[k] - low[k-5])
    LONG ONLY      the Pine ships `enableShortTrades = false`

## THREE PROPERTIES OF THE SOURCE THAT SHAPE THE TEST

**1. The bracket is priced off the SIGNAL CLOSE, but the fill is the NEXT OPEN.**
`stopLossPrice` and `takeProfitPrice` are both computed from `close` on the signal
bar, while `strategy.entry` is a market order that fills at the next bar's open. So
the REALISED reward/risk is `(TP - fill) / (fill - stop)` and is **not 1.5** unless
the open equals the previous close. This is reproduced exactly, and the realised R
multiple is measured and reported rather than assumed. The exact barrier breakeven
is therefore computed per trade, not fixed at 1/(1+1.5) = 40%.

**2. There is no time stop.** The Pine holds until stop or target, indefinitely. A
vertical barrier of 500 bars is added **solely to bound computation**; the number of
trades reaching it is reported, and if it is material the result is qualified.

**3. Short trades are OFF by default** and are left off. Testing the short leg would
be testing a configuration the file does not ship.

## SPEC GAPS — declared, not guessed

The Pine pins **neither instrument nor timeframe**. Its commission
(`cash_per_contract`, $2.50) and `margin_long/short = 5` indicate index futures, and
`initial_capital = 50000` with 1 contract is consistent with NQ.

    TIMEFRAME    15-minute. Declared as a mid-range default, NOT swept. 5m/1h/1d
                 are not run; a different timeframe requires its own preregistration
                 and counts as a separate trial.
    INSTRUMENTS  pooled across SIX instruments with verified true 24h M1 coverage:
                 USTEC (MT5 export, real per-bar spread), EURUSD, GBPUSD, USDJPY,
                 GBPJPY, BTCUSD.

**The pooled result is PRIMARY, not a single instrument.** This is a pure
candle-pattern rule with no session, instrument or session-clock logic anywhere in
it, so if it is real it must be broadly real. Transfer is built into the primary
rather than bolted on afterwards — the mistake that cost the BTC sleeve.

## COSTS

Entry is a market order and pays spread plus slippage; the exit is a stop or limit
and pays slippage.

    USTEC     real per-bar SPREAD from the MT5 export (points x 0.01)
    EURUSD 1.39bp | GBPUSD 1.48bp | USDJPY 1.25bp | GBPJPY 1.95bp | BTCUSD 3.09bp
    plus 1.0bp per side slippage

**C10 pre-check:** the stop is the main bearish candle's low, so risk is roughly one
candle's range plus the sequence's advance — on 15m that is tens of bp, and cost_R
should land well under 0.1R. The measured stop-distance distribution is reported
BEFORE the primary. If the median stop is under ~10bp the study is cost-bound and
that is stated rather than discovered.

## PRIMARY METRIC AND NULL

    PRIMARY  pooled net expectancy in R per trade (1R = that trade's own risk)
    NULL     H0: a bearish candle followed by five rising bullish candles carries no
             directional information. Expectancy <= 0.

## REJECTION CRITERIA — ALL must hold

    (a) sample     >= 300 pooled trades
    (b) primary    pooled net expectancy > 0 with t >= 2.0
    (c) race       win rate exceeds the sample's own realised breakeven,
                   p < 0.05 one-sided binomial
    (d) placebo    beats a matched random-entry placebo at the 95th percentile
                   (same instrument, same risk distribution, same cost, long-only)
    (e) economics  pooled net expectancy > 0 at 2x cost
    (f) time       POSITIVE expectancy in both chronological halves
    (g) transfer   POSITIVE expectancy on >= 4 of the 6 instruments

Criteria (c), (f) and (g) state the sign explicitly.

## MANDATORY CONSISTENCY CHECK (Protocol Amendment 7), RUN FIRST

STOP outcomes == exactly -1.000R; TARGET outcomes == exactly their own realised +R;
the exact identity (sum of outcome R)/n reconciles to the reported mean gross to
1e-9, including vertical exits. A geometry guard requires `stop < fill < target`,
because the next-open fill can land beyond either level — the defect that hit both
Silver Bullet and London IB.

## STOPPING RULE

If (a)-(g) do not all hold, A-020 is recorded as FAILED and **no variant is
attempted** — no other `followingCandles` value (2/3/4 are NOT swept), no other
take-profit multiple (0.5R/1R/2R are NOT swept), no enabling of shorts, no other
timeframe, no instrument subset, no session filter.

**The Pine exposes four sequence lengths and four take-profit multiples = 16
configurations. Exactly one is tested: the shipped default (5 candles, 1.5R, long
only). Sweeping that grid after a failure would be a 16-trial search presented as
one, and is forbidden.**

## BUG PROTOCOL

Stop, document, assess prior impact, fix, rerun only affected tests, log
before/after.
