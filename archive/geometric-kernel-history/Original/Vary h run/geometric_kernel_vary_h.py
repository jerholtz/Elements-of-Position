#!/usr/bin/env python3
"""Same walk at several h. Object quantities vs sheet quantities."""

from math import sqrt, log, atan, pi, atan2
from pathlib import Path
import csv
import time

OUT = Path("/home/workdir/artifacts")


def step(x, y, h):
    nx, ny = x - h * y, y + h * x
    n = sqrt(nx * nx + ny * ny)
    return nx / n, ny / n


def measure_horizon(h):
    x, y = 1.0, 0.0
    seen_up = False
    m = 0
    while True:
        x, y = step(x, y, h)
        m += 1
        if y > 0.0:
            seen_up = True
        if seen_up and y <= 0.0:
            return m


def closed_wedge(N):
    return (N * N) / 8.0 + log(N) - N + 1.5 - log(2.0)


def run(h, n_max):
    H = measure_horizon(h)
    ang = atan(h)
    residual = H * ang - pi
    wrap = abs(2 * pi / residual) if abs(residual) > 1e-18 else float("inf")
    sheet_L = sqrt(1.0 + h * h) - 1.0
    x, y = 1.0, 0.0
    x0, y0 = x, y
    x, y = step(x, y, h)
    heading_chord = sqrt((x - x0) ** 2 + (y - y0) ** 2)
    # reset and walk
    x, y = 1.0, 0.0
    wedge = 0.0
    snap = {}
    for j in range(1, n_max * H + 1):
        x, y = step(x, y, h)
        k = j / H
        if k >= 2.0:
            wedge += (k / 4.0 + 1.0 / k - 1.0) / H
        if j % H == 0:
            n = j // H
            if n in (1, 2, 4, 10, n_max):
                tens = k / 4.0 + 1.0 / k - 1.0
                snap[n] = {
                    "hx": x,
                    "hy": y,
                    "atan2": atan2(y, x),
                    "tension": tens,
                    "wedge": wedge if n >= 2 else 0.0,
                }
    return {
        "h": h,
        "H": H,
        "true_half": pi / ang,
        "residual": residual,
        "wrap_N": wrap,
        "sheet_leftover": sheet_L,
        "heading_chord": heading_chord,
        "H_times_h": H * h,
        "wedge": wedge,
        "closed": closed_wedge(float(n_max)),
        "snap": snap,
    }


def main():
    n_max = 2000
    hs = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]
    print(f"n_max={n_max}")
    print(
        f"{'h':>8} {'H':>8} {'H*h':>10} {'true_half':>10} {'resid':>10} "
        f"{'wrap_N':>10} {'L-1':>12} {'wed_diff':>10}"
    )
    rows = []
    t0 = time.perf_counter()
    for h in hs:
        r = run(h, n_max)
        wd = r["wedge"] - r["closed"]
        print(
            f"{r['h']:8.4f} {r['H']:8d} {r['H_times_h']:10.6f} {r['true_half']:10.4f} "
            f"{r['residual']:10.6f} {r['wrap_N']:10.1f} {r['sheet_leftover']:12.8f} {wd:10.4f}"
        )
        s2 = r["snap"][2]
        sN = r["snap"][n_max]
        rows.append(
            {
                "h": r["h"],
                "H": r["H"],
                "H_h": r["H_times_h"],
                "true_half": r["true_half"],
                "residual": r["residual"],
                "wrap_N": r["wrap_N"],
                "sheet_leftover": r["sheet_leftover"],
                "heading_chord": r["heading_chord"],
                "tens_n2": s2["tension"],
                "hx_n2": s2["hx"],
                "hy_n2": s2["hy"],
                "tens_nN": sN["tension"],
                "hx_nN": sN["hx"],
                "hy_nN": sN["hy"],
                "wedge": r["wedge"],
                "closed": r["closed"],
                "wedge_diff": wd,
            }
        )
    print(f"elapsed {time.perf_counter()-t0:.1f}s")
    print()
    print("n=2 tension (must lock) and heading")
    print(f"{'h':>8} {'tension':>10} {'hx':>10} {'hy':>10}")
    for r in rows:
        print(f"{r['h']:8.4f} {r['tens_n2']:10.6f} {r['hx_n2']:10.6f} {r['hy_n2']:10.6f}")
    print()
    print(f"n={n_max} tension (must lock) and heading (sheet drift)")
    print(f"{'h':>8} {'tension':>10} {'hx':>10} {'hy':>10}")
    for r in rows:
        print(f"{r['h']:8.4f} {r['tens_nN']:10.6f} {r['hx_nN']:10.6f} {r['hy_nN']:10.6f}")

    path = OUT / "kernel_vary_h.csv"
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
