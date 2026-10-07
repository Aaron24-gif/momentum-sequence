# MOMENTUM SEQUENCE — THREE TIMEFRAMES (A-020, Amendment 02)
## All three reported together. VERDICT: FAILED on all three.

Sidak correction for 3 trials: criterion (c) requires **p < 0.0170**, not 0.05.

    TF    n     med stop   cost_R    gross      NET       t     race p   placebo  criteria
    15m  4516    27.0bp    0.1645   +0.0409   -0.1236   -6.70   0.0121     82.5     2/7
    1h   1304    54.3bp    0.0815   +0.0071   -0.0744   -2.19   0.4531      8.0     1/7
    4h    360   124.0bp    0.0382   +0.1552   +0.1171   +1.79   0.0097     78.5     5/7

## THE COST PREDICTION HELD — that half of Amendment 02 was right

Predicted before running, from the fact that the stop is the main candle's low (which
scales with bar range) while spread does not:

    1h  predicted cost_R 0.06-0.09   ->  ACTUAL 0.0815   correct
    4h  predicted cost_R 0.03-0.05   ->  ACTUAL 0.0382   correct

Median stop went 27.0 -> 54.3 -> 124.0bp, and cost_R fell 4.3x from 15m to 4h exactly
as the mechanism requires. **Cost is not what kills this at 4h.**

## THE GROSS IS INCOHERENT — and that is the finding

    gross:  15m +0.0409   ->   1h +0.0071   ->   4h +0.1552

**At 1h the signal does not weaken, it VANISHES.** Race p = 0.4531 is the null
exactly. A real mechanism does not disappear at 1h and reappear 22x larger at 4h.
Non-monotone with a collapse in the middle is the signature of noise sampling
differently at different bar sizes.

This is precisely the falsification condition Amendment 02 declared in advance:

> *"if cost_R falls as predicted but GROSS also collapses, the pattern is
> timeframe-specific and there is nothing to rescue."*

It collapsed at 1h. The condition fired.

## THE 4h RESULT LOOKS BEST AND IS NOT PROMOTABLE

5/7 is the best score in the family, and it fails the two criteria that matter most:

    (b) t = 1.79 on n = 360   - underpowered, not significant
    (d) placebo rank 78.5     - and this is the decisive one

**The 4h placebo returns +0.0689R.** Random long entries with matched risk, matched
cost and the same 1.5R geometry make money at 4h, because the tape trended up over
the sample and a long-only 1.5R bracket harvests that. Of the strategy's +0.1171R
net, the majority is drift the placebo already captures. The strategy beats it at the
78.5th percentile, well short of 95.

So the 4h "edge" is mostly long-only beta, measured and priced by its own control.

## WHY ALL THREE WERE RUN, AND WHY THAT MATTERED

Had only 4h been run it would read "5/7, promising, worth a forward test." Running
the middle timeframe is what exposed it: a mechanism that is absent at 1h cannot be
present at 15m and 4h. **Selecting 4h because it scored best of three is exactly what
Amendment 02 forbids, and this section exists so that temptation is on the record.**

## VERDICT

FAILED on 15m, 1h and 4h. The family is closed. No further timeframes, and the 16-cell
sequence-length x take-profit grid remains unswept and forbidden.
