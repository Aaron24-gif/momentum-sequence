# Momentum sequence — tested at three bar sizes, killed at all three

One bearish candle, then five rising candles, then buy. From a public Pine script; the author isn't
named and their code isn't redistributed. This is my implementation of the rules, the
pre-registration, and every trade.

**Result: negative at 15 minutes and 1 hour. Positive at 4 hours, where random entries made almost
as much.**

| Bar size | Trades | Gross | Net of costs | Reading |
|---|---|---|---|---|
| 15-minute | 4,516 | +0.0409R | **−0.1236R** (t −6.70) | cost 4× the gross edge |
| 1-hour | 1,304 | +0.0071R | **−0.0744R** (t −2.19) | the signal disappears: race p = 0.4531, exactly the null |
| 4-hour | 360 | +0.1552R | **+0.1171R** (t +1.79) | random long entries with the same geometry return **+0.0689R** |

The middle case is the finding. A real effect does not vanish at 1 hour and come back 22× larger at
4 hours; non-monotone with a hole in the middle is what noise looks like when you sample it at
different sizes. And at 4 hours most of what's left is long-only drift, which the placebo already
captures: the strategy beats its control at the 78.5th percentile, short of the 95th it needed.

The cost prediction did hold: median stop widened 27 → 54 → 124bp and cost per trade fell 4.3×,
exactly as the mechanism requires. Slower trading fixes the cost problem. It doesn't create
direction.

## Rules as tested

With the signal bar at k and five following candles: bar k−5 bearish, bars k−4…k all bullish and
each closing above the previous close. Long only, stop at the main candle's low, target 1.5R off the
signal close. Shipped defaults, one configuration, six instruments pooled, 2018 → 2026-05-21.

The first run was void: I anchored the main candle one bar too early. The correction moved every
headline in the strategy's favour and is documented in `PREREG.md` and `results/RESULT.md`.

## Running it

```bash
pip install numpy pandas scipy
python src/run.py
```

**Data is not included** (licensed feed). You need 15-minute, 1-hour and 4-hour OHLC with per-bar
spread for six instruments. The three trade files let you check everything without it:

```python
import pandas as pd
for f in ['trades.csv', 'trades_1h.csv', 'trades_4h.csv']:
    d = pd.read_csv('results/' + f)
    print(f, len(d), round(d.R.mean(), 4))   # 4516 -0.1236 | 1304 -0.0744 | 360 +0.1171
```

## What would change my mind

- A 4-hour result that beats its own random-entry control, not just zero.
- An explanation for the 1-hour collapse that isn't noise.
- A different number of following candles, specified in advance rather than chosen after seeing
  these results. Sweeping the 16 available configurations after a failure manufactures a winner,
  so I won't do it.

Open an issue and I'll rerun it.

MIT licensed. One of a series: popular strategies, tested properly, published whatever happens.
