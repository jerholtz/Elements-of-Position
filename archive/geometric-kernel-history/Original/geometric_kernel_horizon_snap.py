#!/usr/bin/env python3
"""Sample at actual y-crossings of the heading, not at n*H."""

from math import sqrt, atan, pi, atan2
from pathlib import Path
import csv

OUT = Path("/home/workdir/artifacts")


def step(x, y, h):
    nx, ny = x - h * y, y + h * x
    n = sqrt(nx * nx + ny * ny)
    return nx / n, ny / n


def main():
    h = 0.002
    n_cross = 4000  # number of downward horizon crossings to record
    x, y = 1.0, 0.0
    seen_up = False
    j = 0
    crossings = []
    last_j = 0

    while len(crossings) < n_cross:
        x, y = step(x, y, h)
        j += 1
        if y > 0.0:
            seen_up = True
        if seen_up and y <= 0.0:
            gap = j - last_j if last_j else j
            m = len(crossings) + 1
            crossings.append(
                {
                    "m": m,
                    "j": j,
                    "gap": gap,
                    "hx": x,
                    "hy": y,
                    "atan2": atan2(y, x),
                    "k_frozen": j / crossings[0]["j"] if crossings else 1.0,
                }
            )
            seen_up = False
            last_j = j

    H0 = crossings[0]["j"]
    for c in crossings:
        c["k_frozen"] = c["j"] / H0
        c["k_snap"] = float(c["m"])  # one crossing = one half-turn of the heading

    gaps = [c["gap"] for c in crossings]
    print(f"h={h}  crossings={len(crossings)}  first gap H0={H0}")
    print(f"gap min={min(gaps)} max={max(gaps)}")
    from collections import Counter
    print("gap histogram:", dict(sorted(Counter(gaps).items())))
    print(f"mean gap={sum(gaps)/len(gaps):.6f}  pi/atan(h)={pi/atan(h):.6f}")

    print()
    print(f"{'m':>6} {'j':>8} {'gap':>6} {'k_frozen':>10} {'k_snap':>8} {'hx':>10} {'hy':>10}")
    show = list(range(1, 9)) + [10, 20, 50, 100, 500, 1000, 1571, 2000, 3600, 4000]
    by_m = {c["m"]: c for c in crossings}
    for m in show:
        if m not in by_m:
            continue
        c = by_m[m]
        print(
            f"{c['m']:6d} {c['j']:8d} {c['gap']:6d} {c['k_frozen']:10.4f} {c['k_snap']:8.1f} "
            f"{c['hx']:10.6f} {c['hy']:10.6f}"
        )

    path = OUT / "kernel_horizon_snap.csv"
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(crossings[0].keys()))
        w.writeheader()
        w.writerows(crossings)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
