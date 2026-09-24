#!/usr/bin/env python3
"""Wedge + two-clock locks at N=3600, h=0.002."""

from math import sqrt, log
from pathlib import Path
import csv

OUT = Path("/home/workdir/artifacts")


def T_h(x, y, h):
    return (x - h * y, y + h * x)


def N(x, y):
    n = sqrt(x * x + y * y)
    return (x / n, y / n)


def step(x, y, h):
    return N(*T_h(x, y, h))


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


def main():
    h = 0.002
    n_max = 3600
    print("measuring H...", flush=True)
    H = measure_horizon(h)
    j_max = n_max * H
    print(f"h={h} H={H} n_max={n_max} j_max={j_max}", flush=True)

    p_list = (H - 1, H + 1)
    lcms = {p: H * p for p in p_list}
    locks = {p: [] for p in p_list}

    x, y = 1.0, 0.0
    wedge = 0.0
    partial = {}
    report_n = set(range(2, 21)) | {50, 100, 200, 500, 1000, 2000, 3600}

    for j in range(1, j_max + 1):
        x, y = step(x, y, h)
        k = j / H
        if k >= 2.0:
            wedge += (k / 4.0 + 1.0 / k - 1.0) / H
        if j % H == 0:
            n = j // H
            if n >= 2:
                partial[n] = wedge
            if n in report_n or n % 200 == 0:
                print(f"  n={n}  wedge={wedge:.6f}  heading=({x:.6f},{y:.6f})", flush=True)
        for p in p_list:
            if j % lcms[p] == 0:
                locks[p].append((j, k, x, y))

    closed = closed_wedge(float(n_max))
    print()
    print(f"WEDGE N={n_max}")
    print(f"  discrete = {wedge:.8f}")
    print(f"  closed   = {closed:.8f}")
    print(f"  diff     = {wedge - closed:.8f}")

    print()
    for p in p_list:
        print(f"CLOCKS H={H} and p={p}  lcm={lcms[p]}  locks={len(locks[p])}")
        for j, k, hx, hy in locks[p]:
            print(f"  j={j}  k={k:.6f}  heading=({hx:.8f},{hy:.8f})")

    path = OUT / "kernel_N3600.csv"
    marks = sorted(n for n in partial if n in report_n or n % 100 == 0)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["N", "discrete_wedge", "closed_wedge", "diff"])
        for n in marks:
            c = closed_wedge(float(n))
            w.writerow([n, partial[n], c, partial[n] - c])
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
