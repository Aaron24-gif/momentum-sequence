# MOMENTUM SEQUENCE  (A-020) — RESULT: FAILED (2/7)

Run 2026-09-05 against `PREREGISTRATION.md`, **corrected per `AMENDMENT_01.md`**.
15m signal / M1 resolution, six instruments pooled, 2018 -> 2026-05-21, 4,516 trades.
Shipped defaults only (N=5, TP=1.5R, long only). Holdout untouched.

## THIS SUPERSEDES A VOID FIRST RUN

The first run anchored the main candle at k-6 instead of k-5, leaving the true main
candle unconstrained and taking the stop from the wrong low. See `AMENDMENT_01.md`.
**The correction moved every headline in the strategy's FAVOUR** — gross +0.0272 ->
+0.0409, race p 0.0208 -> 0.0121, placebo rank 58.5 -> 82.5, n 4016 -> 4516. Stated
explicitly so the fix cannot be read as burying an inconvenient result.

Corroboration that the fix is right: realised reward/risk tightened from 1.539 to
**1.503** against the Pine's nominal 1.500, which is what a correctly-placed stop
should do.

## CONSISTENCY CHECK (Amendment 7) — PASSED FIRST TIME

    outcome      n    mean   worst    best
    STOP      2625 -1.0000 -1.0000 -1.0000
    TARGET    1871 +1.4995 +0.1797 +2.8953
    VERTICAL    20 +0.1967 -0.7328 +1.2851

    vertical exits 20 = 0.44%  -> the Pine's missing time stop is IMMATERIAL
    realised reward/risk mean 1.503, median 1.500 vs nominal 1.500

## RESULT

    symbol        n    win%    gross     cost      NET       t     totR
    USTEC      1144   45.5%  +0.1364   0.1041  +0.0323   +0.87    +36.9
    EUR_USD     576   38.5%  -0.0456   0.2449  -0.2904   -5.69   -167.3
    GBP_USD     599   37.6%  -0.0563   0.2287  -0.2850   -5.74   -170.7
    USD_JPY     695   44.2%  +0.1019   0.2037  -0.1019   -2.16    -70.8
    GBP_JPY     681   40.7%  +0.0154   0.2145  -0.1991   -4.21   -135.6
    BTC_USD     821   40.4%  +0.0088   0.0708  -0.0619   -1.45    -50.9
    POOLED     4516   41.7%  +0.0409   0.1645  -0.1236   -6.70   -558.3

    yearly net  2018:-0 2019:+1 2020:+14 2021:-63 2022:-70 2023:-81
                2024:-147 2025:-125 2026:-88

    [PASS] a  >= 300 pooled trades              4516
    [FAIL] b  pooled net exp > 0 and t >= 2.0   exp -0.1236  t -6.70
    [PASS] c  win rate > realised breakeven     41.61% vs 39.95%  p=0.0121
    [FAIL] d  beats placebo at 95th pct         -0.1236 vs placebo -0.1417, rank 82.5
    [FAIL] e  net > 0 at 2x cost                -0.2881R
    [FAIL] f  POSITIVE both halves              H1 -0.0724 | H2 -0.1748
    [FAIL] g  POSITIVE on >= 4 of 6             1 (USTEC only)

**2/7. VERDICT: FAILED.**

## WHAT IT SAYS

**The pattern carries a weak but real gross signal.** The race beats its own realised
breakeven at p = 0.0121, and gross is positive on 4 of 6 instruments. A bearish candle
followed by five rising bullish candles is not nothing.

**Cost is 4x the gross.** Pooled gross +0.0409R against 0.1645R of cost.

**Only USTEC survives net, and not convincingly** — +0.0323R at t = 0.87 on the one
instrument with both the tightest cost model (real per-bar spread, 0.104R) and the
strongest gross (+0.1364R). At t = 0.87 that is noise, and promoting a single
instrument out of six would be exactly the selection this preregistration was written
to prevent.

**Placebo rank 82.5.** Closer than the void run's 58.5 but still short of the 95 bar:
the NET result is not distinguishable from matched random long entries. The gross race
is significant while the net is not, and cost is what separates them — the same shape
as A-018 London IB, at a weaker significance (p 0.0121 vs 0.0011).

The yearly net worsens steadily, which is not a regime story so much as trade count
rising while per-trade expectancy stays negative.

## THE MULTIPLICITY TRAP, CLOSED IN ADVANCE

The Pine exposes **4 sequence lengths x 4 take-profit multiples = 16 configurations**
plus a short toggle. Exactly one was tested: the shipped default. With a positive
pooled gross and one net-positive instrument, sweeping that grid would very likely
manufacture a winner. The stopping rule forbids it and this paragraph exists so the
temptation is on the record.

The author's own description says it plainly: *"Users are encouraged to evaluate
different configurations across sufficiently large datasets rather than selecting
parameters solely because they produced favorable historical results."* Selecting the
best of 16 after seeing all 16 is precisely that error.

## STOPPING RULE

No variants. No other sequence length (2/3/4 NOT swept), no other take-profit multiple
(0.5R/1R/2R NOT swept), no enabling shorts, no other timeframe, no instrument subset,
no session filter.
