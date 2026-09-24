#!/usr/bin/env python3
"""
Geometric kernel — expanded sampling.
Layers 1–3 unchanged. Every step j is a state.
Sheet gauges (depend on h) vs object gauges (depend on k = j/H).
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


def walk(h, n_max, write_every=1):
    """Walk n_max half-turns. Record every write_every steps."""
    H = measure_horizon(h)
    sheet_L = sqrt(1.0 + h * h)
    sheet_leftover = sheet_L - 1.0

    x, y = 1.0, 0.0
    j = 0
    k = 0.0
    r_out = 0.0
    P = (0.0, 0.0)
    rows = []
    storey_rows = []

    j_max = n_max * H
    heading_chord_sheet = None

    while j < j_max:
        x_n, y_n = step(x, y, h)
        j += 1
        k = j / H
        r_out_n = k / 2.0
        r_in_n = 2.0 / k
        gm = sqrt(r_out_n * r_in_n)
        am = 0.5 * (r_out_n + r_in_n)
        tension = am - gm
        P_n = (r_out_n * x_n, r_out_n * y_n)

        u_chord = dist((x, y), (x_n, y_n))
        if heading_chord_sheet is None:
            heading_chord_sheet = u_chord

        if j == 1:
            arm_chord = 0.0
            arm_path = 0.0
            chord_over_path = 1.0
        else:
            arm_chord = dist(P, P_n)
            # path this step: radial rise plus heading travel at mean radius
            # heading travel on the unit circle measured as the raw kick h
            r_mean = 0.5 * (r_out + r_out_n)
            dr = abs(r_out_n - r_out)
            arm_path = sqrt((r_mean * h) ** 2 + dr * dr)
            chord_over_path = arm_chord / arm_path if arm_path else 1.0

        rec = {
            "j": j,
            "k": k,
            "r_out": r_out_n,
            "r_in": r_in_n,
            "gm": gm,
            "am": am,
            "tension": tension,
            "arm_chord": arm_chord,
            "arm_path": arm_path,
            "chord_over_path": chord_over_path,
            "heading_x": x_n,
            "heading_y": y_n,
        }

        if write_every == 1 or j % write_every == 0 or abs(k - round(k)) < 1e-12:
            rows.append(rec)
        if abs(k - round(k)) < 0.5 / H and abs(k - max(1, round(k))) < 0.5 / H:
            if round(k) >= 1 and (not storey_rows or storey_rows[-1]["n"] != int(round(k))):
                rec_s = dict(rec)
                rec_s["n"] = int(round(k))
                storey_rows.append(rec_s)

        x, y = x_n, y_n
        r_out = r_out_n
        P = P_n

    meta = {
        "h": h,
        "H": H,
        "sheet_L": sheet_L,
        "sheet_leftover": sheet_leftover,
        "sheet_heading_chord": heading_chord_sheet,
        "j_max": j_max,
        "n_max": n_max,
    }
    return meta, rows, storey_rows


def main():
    n_max = 36
    # full-j CSV only for the coarser sheet; finer h compared at storeys
    runs = []
    for h, tag, every in ((0.002, "h002", 1), (0.0005, "h0005", 8)):
        print(f"walking h={h} ...", flush=True)
        meta, rows, storeys = walk(h, n_max, write_every=every)
        runs.append((tag, meta, rows, storeys))
        path = OUT / f"kernel_expand_{tag}.csv"
        fields = list(rows[0].keys())
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(
            f"  H={meta['H']}  leftover={meta['sheet_leftover']:.8f}  "
            f"heading_chord={meta['sheet_heading_chord']:.8f}  "
            f"rows={len(rows)}  wrote {path.name}",
            flush=True,
        )

    print()
    print("SHEET (changes with h)")
    print(f"{'h':>8} {'H':>8} {'L-1 leftover':>16} {'heading chord':>16}")
    for tag, meta, _, _ in runs:
        print(
            f"{meta['h']:8.4f} {meta['H']:8d} "
            f"{meta['sheet_leftover']:16.8f} {meta['sheet_heading_chord']:16.8f}"
        )

    print()
    print("OBJECT at integer storeys (should lock across h)")
    print(
        f"{'n':>4} {'k':>8} {'GM a':>10} {'GM b':>10} "
        f"{'tens a':>10} {'tens b':>10} {'c/p a':>10} {'c/p b':>10}"
    )
    a_store = {s["n"]: s for s in runs[0][3]}
    b_store = {s["n"]: s for s in runs[1][3]}
    for n in range(1, n_max + 1):
        if n not in a_store or n not in b_store:
            continue
        a, b = a_store[n], b_store[n]
        print(
            f"{n:4d} {a['k']:8.3f} {a['gm']:10.6f} {b['gm']:10.6f} "
            f"{a['tension']:10.6f} {b['tension']:10.6f} "
            f"{a['chord_over_path']:10.6f} {b['chord_over_path']:10.6f}"
        )

    # early waterfall, first 8 steps of coarse run
    print()
    print("WATERFALL first steps (h=0.002), tension before first storey completes")
    print(f"{'j':>6} {'k':>12} {'r_out':>12} {'r_in':>12} {'GM':>10} {'tension':>12}")
    for rec in runs[0][2][:8]:
        print(
            f"{rec['j']:6d} {rec['k']:12.6f} {rec['r_out']:12.6f} "
            f"{rec['r_in']:12.6f} {rec['gm']:10.6f} {rec['tension']:12.6f}"
        )


if __name__ == "__main__":
    main()
