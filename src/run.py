"""
MOMENTUM SEQUENCE STRATEGY  — A-020.
Pine v6 -> Python. 15m signal, M1 barrier resolution, six instruments pooled.
Frozen per PREREGISTRATION.md. Shipped defaults only: N=5, TP=1.5R, LONG ONLY.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
N_FOLLOW = 5
RR = 1.5
VERTICAL = 500          # bounds computation only; the Pine has no time stop
TF = "15min"            # set by --tf; AMENDMENT 02 adds 1h and 4h
TF_MIN = 15
SLIP_BP = 1.0
CAP = "2026-05-21"

SPREAD_BP = {"EUR_USD": 1.39, "GBP_USD": 1.48, "USD_JPY": 1.25,
             "GBP_JPY": 1.95, "BTC_USD": 3.09}
MT5_USTEC = ("C:/Users/Admin/Downloads/Telegram Desktop/"
             "USTEC_M1_201801020000_202605221059.csv")


def load(sym):
    """Returns M1 with a 'spread' column in PRICE units (0 where not served)."""
    if sym == "USTEC":
        d = pd.read_csv(MT5_USTEC, sep="\t")
        d.columns = [c.strip("<> ") for c in d.columns]
        d["dt"] = pd.to_datetime(d["DATE"] + " " + d["TIME"],
                                 format="%Y.%m.%d %H:%M:%S")
        d = d.set_index("dt").sort_index()
        d = d[~d.index.duplicated(keep="first")]
        i = d.index.tz_localize("Europe/Athens", ambiguous="NaT", nonexistent="NaT")
        d = d[i.notna()]
        d.index = i[i.notna()].tz_convert("UTC")
        d = d.rename(columns={"OPEN": "open", "HIGH": "high", "LOW": "low",
                              "CLOSE": "close", "SPREAD": "spread"})
        d["spread"] = d["spread"] * 0.01           # points -> price
        return d[["open", "high", "low", "close", "spread"]].loc[:CAP]

    p = (REPO / "eth_transfer" / "data" / f"{sym}_m1.pkl" if sym == "BTC_USD"
         else REPO / "fx_transfer" / "data" / f"{sym}_m1.pkl")
    d = pd.read_pickle(p).rename(columns=str.lower)
    d = d[["open", "high", "low", "close"]].dropna().sort_index()
    d = d[~d.index.duplicated(keep="first")]
    if d.index.tz is None:
        d.index = d.index.tz_localize("UTC")
    else:
        d.index = d.index.tz_convert("UTC")
    d["spread"] = SPREAD_BP[sym] * 1e-4 * d["close"]
    return d.loc[:CAP]


def run_symbol(sym, m1):
    m15 = m1.resample(TF).agg({"open": "first", "high": "max", "low": "min",
                                    "close": "last", "spread": "last"}).dropna()
    o = m15["open"].to_numpy(float)
    h = m15["high"].to_numpy(float)
    l = m15["low"].to_numpy(float)
    c = m15["close"].to_numpy(float)
    spr = m15["spread"].to_numpy(float)
    idx = m15.index
    n = len(c)
    N = N_FOLLOW

    m1h = m1["high"].to_numpy(float)
    m1l = m1["low"].to_numpy(float)
    m1c = m1["close"].to_numpy(float)
    m1i = m1.index

    bull = c > o
    trades = []
    busy_until = pd.Timestamp.min.tz_localize("UTC")

    for k in range(N + 1, n - 1):
        if idx[k] <= busy_until:
            continue
        m = k - N            # AMENDMENT 01: main candle is ADJACENT to the
                             # sequence (Pine [followingCandles]), not k-N-1
        if not (c[m] < o[m]):                          # mainBearish
            continue
        seq = slice(k - N + 1, k + 1)                  # the N following bars
        if not bull[seq].all():
            continue
        if not (l[seq] > l[m]).all():
            continue
        if not (np.diff(c[k - N + 1:k + 1]) > 0).all():
            continue

        # entry: market on the signal close -> fills the NEXT bar's open
        fill = o[k + 1]
        t_fill = idx[k + 1]
        stop = l[m]
        # NOTE: the Pine prices the target off the SIGNAL CLOSE, not the fill
        tgt = c[k] + RR * (c[k] - stop)
        # geometry guard (Protocol Amendment 7)
        if not (stop < fill < tgt):
            continue
        risk = fill - stop
        reward = tgt - fill
        if risk <= 0 or reward <= 0:
            continue

        j0 = m1i.searchsorted(t_fill)
        outcome, exit_px, exit_j = None, None, None
        jmax = min(j0 + VERTICAL * TF_MIN, len(m1c))
        for j in range(j0, jmax):
            if m1l[j] <= stop:
                outcome, exit_px, exit_j = "STOP", stop, j
                break
            if m1h[j] >= tgt:
                outcome, exit_px, exit_j = "TARGET", tgt, j
                break
        if outcome is None:
            exit_j = min(jmax - 1, len(m1c) - 1)
            outcome, exit_px = "VERTICAL", m1c[exit_j]

        gross = (exit_px - fill) / risk
        cost_r = (spr[k] + 2 * SLIP_BP * 1e-4 * fill) / risk
        trades.append(dict(symbol=sym, sig_time=idx[k], entry_time=t_fill,
                           fill=fill, stop=stop, target=tgt, risk=risk,
                           risk_bp=1e4 * risk / fill, rr=reward / risk,
                           outcome=outcome, R_gross=gross, cost_r=cost_r,
                           R=gross - cost_r))
        busy_until = m1i[exit_j]
    return pd.DataFrame(trades)


def main():
    global TF, TF_MIN
    if len(sys.argv) > 1:
        TF = sys.argv[1]
        TF_MIN = {"15min": 15, "1h": 60, "4h": 240}[TF]
    print(f"TIMEFRAME {TF}  (vertical {VERTICAL} bars = {VERTICAL*TF_MIN/60:.0f}h)")
    syms = ["USTEC", "EUR_USD", "GBP_USD", "USD_JPY", "GBP_JPY", "BTC_USD"]
    books = {}
    for s in syms:
        m1 = load(s)
        b = run_symbol(s, m1)
        books[s] = b
        print(f"  {s:<9} M1 {len(m1):>9,}  trades {len(b):>5}", flush=True)
        del m1

    ALL = pd.concat(books.values(), ignore_index=True)
    ALL.to_csv(HERE / f"trades_{TF}.csv", index=False)
    R = ALL.R.to_numpy()
    tt = R.mean() / R.std(ddof=1) * np.sqrt(len(R))

    print("\n" + "=" * 94)
    print("  MANDATORY CONSISTENCY CHECK (Protocol Amendment 7)")
    print("=" * 94)
    print(ALL.groupby("outcome").R_gross.agg(n="size", mean="mean",
                                             worst="min", best="max").round(4).to_string())
    st = ALL[ALL.outcome == "STOP"]
    tg = ALL[ALL.outcome == "TARGET"]
    ok_s = (abs(st.R_gross + 1.0).max() < 1e-9) if len(st) else True
    ok_t = (abs(tg.R_gross - tg.rr).max() < 1e-9) if len(tg) else True
    ident = abs(ALL.R_gross.sum() / len(ALL) - ALL.R_gross.mean()) < 1e-9
    nv = int((ALL.outcome == "VERTICAL").sum())
    print(f"\n  STOP == -1.000 exactly          : {ok_s}")
    print(f"  TARGET == its own realised R    : {ok_t}")
    print(f"  identity reconciles             : {ident}")
    print(f"  vertical exits (Pine has none)  : {nv} = {100*nv/len(ALL):.2f}% of trades")
    print(f"  realised reward/risk  mean {ALL.rr.mean():.3f}  median {ALL.rr.median():.3f}"
          f"   (the Pine's nominal is 1.500)")
    if not (ok_s and ok_t and ident):
        print("\n  *** CONSISTENCY CHECK FAILED — criteria NOT scored ***")
        return

    print("\n" + "=" * 94)
    print("  COST PRE-CHECK")
    print("=" * 94)
    print(f"  stop distance: median {ALL.risk_bp.median():.1f}bp  "
          f"p10 {ALL.risk_bp.quantile(.1):.1f}  p90 {ALL.risk_bp.quantile(.9):.1f}")
    print(f"  cost_R:        median {ALL.cost_r.median():.4f}R  mean {ALL.cost_r.mean():.4f}R")

    print("\n" + "=" * 94)
    print("  RESULT")
    print("=" * 94)
    print(f"  {'symbol':<10}{'n':>7}{'win%':>8}{'gross':>10}{'cost':>9}{'NET':>10}{'t':>8}{'totR':>9}")
    for s in syms:
        b = books[s]
        if not len(b):
            continue
        r = b.R.to_numpy()
        t2 = r.mean() / r.std(ddof=1) * np.sqrt(len(r)) if len(r) > 2 else np.nan
        print(f"  {s:<10}{len(r):>7}{100*(r>0).mean():>7.1f}%{b.R_gross.mean():>10.4f}"
              f"{b.cost_r.mean():>9.4f}{r.mean():>10.4f}{t2:>8.2f}{r.sum():>9.1f}")
    print(f"  {'POOLED':<10}{len(R):>7}{100*(R>0).mean():>7.1f}%{ALL.R_gross.mean():>10.4f}"
          f"{ALL.cost_r.mean():>9.4f}{R.mean():>10.4f}{tt:>8.2f}{R.sum():>9.1f}")
    ALL["y"] = ALL.sig_time.dt.year
    print("\n  yearly net: " + " | ".join(f"{int(y)}:{g.R.sum():+.0f}"
                                          for y, g in ALL.groupby("y")))

    # placebo: random long entries, same instrument, matched risk + rr + cost
    rng = np.random.default_rng(23)
    sims = []
    cache = {}
    for s in syms:
        m1 = load(s)
        m15 = m1.resample(TF).agg({"open": "first", "high": "max",
                                   "low": "min", "close": "last"}).dropna()
        cache[s] = (m15["open"].to_numpy(float), m1["high"].to_numpy(float),
                    m1["low"].to_numpy(float), m1["close"].to_numpy(float),
                    m1.index, m15.index)
        del m1
    for _ in range(200):
        tot, cnt = 0.0, 0
        for s in syms:
            b = books[s]
            if not len(b):
                continue
            o15, hh, ll, cc, mi, xi = cache[s]
            picks = rng.integers(10, len(o15) - 5, len(b))
            for k, rb, rr_, cs in zip(picks, b.risk_bp.to_numpy(),
                                      b.rr.to_numpy(), b.cost_r.to_numpy()):
                fill = o15[k]
                risk = rb * 1e-4 * fill
                stop = fill - risk
                tgt = fill + rr_ * risk
                j0 = mi.searchsorted(xi[k])
                out = None
                for j in range(j0, min(j0 + VERTICAL * TF_MIN, len(cc))):
                    if ll[j] <= stop:
                        out = -1.0
                        break
                    if hh[j] >= tgt:
                        out = rr_
                        break
                if out is None:
                    continue
                tot += out - cs
                cnt += 1
        sims.append(tot / max(cnt, 1))
    sims = np.array(sims)
    pct = 100 * (sims < R.mean()).mean()

    dec = ALL[ALL.outcome != "VERTICAL"]
    nw = int((dec.outcome == "TARGET").sum())
    nd = len(dec)
    be = 1 / (1 + ALL.rr.mean())
    pbin = sps.binomtest(nw, nd, be, alternative="greater").pvalue
    R2 = (ALL.R_gross - 2 * ALL.cost_r).to_numpy()
    mid = ALL.sig_time.median()
    h1 = ALL[ALL.sig_time <= mid].R.mean()
    h2 = ALL[ALL.sig_time > mid].R.mean()
    pos = [s for s in syms if len(books[s]) and books[s].R.mean() > 0]

    print("\n" + "=" * 94)
    print("  PREREGISTERED CRITERIA")
    print("=" * 94)
    res = [
        ("a  >= 300 pooled trades", f"{len(R)}", len(R) >= 300),
        ("b  pooled net exp > 0 and t >= 2.0", f"exp {R.mean():+.4f}  t {tt:.2f}",
         (R.mean() > 0) and (tt >= 2.0)),
        ("c  win rate > realised breakeven",
         f"{100*nw/nd:.2f}% vs {100*be:.2f}%  p={pbin:.4f}",
         (nw / nd > be) and (pbin < 0.05)),
        ("d  beats placebo at 95th pct",
         f"actual {R.mean():+.4f} vs placebo {sims.mean():+.4f}, rank {pct:.1f}", pct >= 95),
        ("e  net > 0 at 2x cost", f"{R2.mean():+.4f}R", R2.mean() > 0),
        ("f  POSITIVE both halves", f"H1 {h1:+.4f} | H2 {h2:+.4f}", (h1 > 0) and (h2 > 0)),
        ("g  POSITIVE on >= 4 of 6", f"{len(pos)}: {', '.join(pos) or 'none'}", len(pos) >= 4),
    ]
    for nm, val, okk in res:
        print(f"  [{'PASS' if okk else 'FAIL'}] {nm:<36} {val}")
    npass = sum(1 for _, _, x in res if x)
    print(f"\n  {npass} / {len(res)} criteria passed")
    print("  VERDICT: " + ("CONFIRMED" if npass == len(res)
                           else "FAILED — stopping rule applies, no variants"))


if __name__ == "__main__":
    main()
