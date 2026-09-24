#!/usr/bin/env python3
"""
Kernel walk plus two measurements:
  1) pair each state k with 4/k
  2) integer-to-integer chord vs summed micro-path
Layers T_h, N, step, horizon unchanged.
"""

from math import sqrt
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


def dist(p, q):
    return sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


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


def walk(h, n_max):
    H = measure_horizon(h)
    x, y = 1.0, 0.0
    states = []  # index 0 unused; j starts at 1
    states.append(None)
    P_prev = None
    r_prev = 0.0
    path_from_last_int = 0.0
    last_int_j = 0
    last_int_P = (0.0, 0.0)
    int_legs = []

    j_max = n_max * H
    for j in range(1, j_max + 1):
        x, y = step(x, y, h)
        k = j / H
        r_out = k / 2.0
        r_in = 2.0 / k
        gm = sqrt(r_out * r_in)
        am = 0.5 * (r_out + r_in)
        P = (r_out * x, r_out * y)
        if j == 1:
            arm_path = 0.0
            arm_chord = 0.0
        else:
            arm_chord = dist(P_prev, P)
            r_mean = 0.5 * (r_prev + r_out)
            dr = abs(r_out - r_prev)
            arm_path = sqrt((r_mean * h) ** 2 + dr * dr)
            path_from_last_int += arm_path
        states.append(
            {
                "j": j,
                "k": k,
                "r_out": r_out,
                "r_in": r_in,
                "gm": gm,
                "am": am,
                "tension": am - gm,
                "hx": x,
                "hy": y,
                "Px": P[0],
                "Py": P[1],
                "arm_path": arm_path,
            }
        )
        # integer arrivals
        n_here = j // H
        if j == n_here * H and n_here >= 1:
            if last_int_j > 0:
                chord = dist(last_int_P, P)
                int_legs.append(
                    {
                        "n0": n_here - 1 if last_int_j == (n_here - 1) * H else n_here,
                        "n1": n_here,
                        "j0": last_int_j,
                        "j1": j,
                        "chord": chord,
                        "path": path_from_last_int,
                        "chord_over_path": chord / path_from_last_int if path_from_last_int else 1.0,
                    }
                )
            last_int_j = j
            last_int_P = P
            path_from_last_int = 0.0
        P_prev = P
        r_prev = r_out
    return H, states, int_legs


def pair_rows(H, states, n_max):
    """For selected k, nearest j' with k' ~= 4/k."""
    j_max = n_max * H
    out = []
    # sample: all integers n, plus a few non-integers
    targets = [n for n in range(1, n_max + 1)]
    targets += [0.25, 0.5, 0.8, 1.5, 2.5, 3.2, 6.4]
    seen = set()
    for k in sorted(targets):
        j = max(1, min(j_max, int(round(k * H))))
        if j in seen:
            continue
        seen.add(j)
        k_act = states[j]["k"]
        k_part = 4.0 / k_act
        j_part = max(1, min(j_max, int(round(k_part * H))))
        a = states[j]
        b = states[j_part]
        # heading dot product
        hdot = a["hx"] * b["hx"] + a["hy"] * b["hy"]
        # inversion of P through unit circle along same heading as a:
        # inv_a = r_in(a) * heading(a); compare radius to partner r_out
        out.append(
            {
                "j": a["j"],
                "k": a["k"],
                "j_part": b["j"],
                "k_part": b["k"],
                "k_part_target": k_part,
                "tens": a["tension"],
                "tens_part": b["tension"],
                "r_out": a["r_out"],
                "r_in": a["r_in"],
                "r_out_part": b["r_out"],
                "r_in_part": b["r_in"],
                "heading_dot": hdot,
            }
        )
    return out


def main():
    h = 0.002
    n_max = 36
    print(f"walk h={h} n_max={n_max}", flush=True)
    H, states, legs = walk(h, n_max)
    print(f"H={H}  states={len(states)-1}  integer legs={len(legs)}")

    pairs = pair_rows(H, states, n_max)

    print()
    print("PAIR k <-> 4/k")
    print(
        f"{'k':>8} {'k_part':>8} {'tens':>10} {'tens_p':>10} "
        f"{'r_out':>8} {'r_in_p':>8} {'r_in':>8} {'r_out_p':>8} {'h·h_p':>9}"
    )
    for p in pairs:
        print(
            f"{p['k']:8.3f} {p['k_part']:8.3f} {p['tens']:10.6f} {p['tens_part']:10.6f} "
            f"{p['r_out']:8.3f} {p['r_in_part']:8.3f} {p['r_in']:8.3f} {p['r_out_part']:8.3f} "
            f"{p['heading_dot']:9.4f}"
        )

    print()
    print("INTEGER n to n+1  chord vs summed path")
    print(f"{'n0-n1':>8} {'chord':>12} {'path':>12} {'chord/path':>12}")
    for L in legs:
        print(
            f"{L['n0']:2d}-{L['n1']:<2d} {L['chord']:12.6f} {L['path']:12.6f} {L['chord_over_path']:12.8f}"
        )

    path_p = OUT / "kernel_pairs.csv"
    with path_p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pairs[0].keys()))
        w.writeheader()
        w.writerows(pairs)
    path_l = OUT / "kernel_int_legs.csv"
    with path_l.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(legs[0].keys()))
        w.writeheader()
        w.writerows(legs)
    print(f"\nwrote {path_p}")
    print(f"wrote {path_l}")


if __name__ == "__main__":
    main()
