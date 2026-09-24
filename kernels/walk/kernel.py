#!/usr/bin/env python3
"""
Elements of Position -- Walk Kernel, minimal.

Three layers, kept in three places, not one:

  DYNAMICS  walk()          the only place anything moves. no trig.
  OBJECT    pair(), wedge_closed()   pure arithmetic on the integer m.
            true for m=1,2,3,... whether or not any walk ever ran.
  SHEET     everything in main() below "sheet reading"   depends on h.

Trig (math.atan, math.pi) appears exactly once, in a comparison
computed AFTER the tables exist. It is never called inside walk().
"""
import csv, sys, math
from pathlib import Path

# ---------------------------------------------------------------- DYNAMICS
def walk(h, steps):
    """Shear + bind. Station (1,0). Hit = heading crosses y=0.
    Returns list of (m, j, gap, side, hx, hy)."""
    x, y = 1.0, 0.0
    prev_y = 0.0
    hits = []
    last_j = 0
    m = 0
    for j in range(1, steps + 1):
        x, y = x - h*y, y + h*x        # shear: equal-opposite mix, no angle
        r = math.sqrt(x*x + y*y)
        x, y = x/r, y/r                # bind: restore length 1
        if (prev_y > 0.0 and y <= 0.0) or (prev_y < 0.0 and y >= 0.0):
            m += 1
            hits.append((m, j, j - last_j, "down" if prev_y > 0 else "up", x, y))
            last_j = j
        prev_y = y
    return hits

# ------------------------------------------------------------------ OBJECT
def pair(m):
    """r=m, 1/r=1/m. No walk data used. True for any positive integer m."""
    r = float(m)
    rin = 1.0 / r
    am = 0.5 * (r + rin)
    gm = math.sqrt(r * rin)          # == 1 always; left explicit, not assumed
    tau = am - gm                    # (m-1)^2 / (2m)
    return r, rin, am, gm, tau

def wedge_closed(N):
    """Integral_1^N tau(k) dk, closed form."""
    if N <= 1:
        return 0.0
    return (N*N - 1) / 4.0 + 0.5 * math.log(N) - (N - 1)

# ------------------------------------------------------------------- MAIN
def main():
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.002
    steps = int(float(sys.argv[2])) if len(sys.argv) > 2 else 200_000
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("run")
    out.mkdir(parents=True, exist_ok=True)

    hits = walk(h, steps)
    N = len(hits)

    # object table: pure arithmetic, independent of the walk, computed for 1..N
    obj = [pair(m) for m in range(1, N + 1)]

    with (out / "crossings.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["m", "j", "gap", "side", "hx", "hy"])
        w.writerows(hits)

    with (out / "pairs.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["m", "r", "r_in", "am", "gm", "tau"])
        for m, (r, rin, am, gm, tau) in enumerate(obj, start=1):
            w.writerow([m, r, rin, am, gm, tau])

    gaps = [g for (_, _, g, _, _, _) in hits]
    tau_sum = sum(t for (_, _, _, _, t) in obj)
    closed = wedge_closed(float(N))
    trap = closed + 0.5 * (obj[0][4] + obj[-1][4]) if N else 0.0

    # sheet reading: trig used here ONLY, as a named comparison, after tables exist
    lam = math.pi / math.atan(h)

    summary = {
        "h": h, "steps": steps, "n_hits": N,
        "H0": hits[0][1] if hits else "",
        "gap_min": min(gaps) if gaps else "", "gap_max": max(gaps) if gaps else "",
        "mean_gap": sum(gaps)/N if N else "",
        "mean_gap_times_h": (sum(gaps)/N)*h if N else "",
        "lambda_pi_over_atan_h": lam,
        "lambda_frac": lam - math.floor(lam),
        "tau_sum": tau_sum, "wedge_closed": closed, "wedge_trapezoid": trap,
        "tau_sum_minus_trapezoid": tau_sum - trap if N else "",
    }
    with (out / "summary.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value"])
        for k, v in summary.items():
            w.writerow([k, v])

    print(f"h={h} steps={steps:,}  hits={N:,}  H0={summary['H0']}")
    print(f"gaps {summary['gap_min']}..{summary['gap_max']}  mean*h={summary['mean_gap_times_h']}")
    print(f"lambda={lam:.6f}  {{lambda}}={summary['lambda_frac']:.6f}")
    print(f"tau_sum={tau_sum:.6f}  closed={closed:.6f}  trap={trap:.6f}  diff={summary['tau_sum_minus_trapezoid']:.6f}")

if __name__ == "__main__":
    main()
