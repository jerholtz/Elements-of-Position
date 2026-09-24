#!/usr/bin/env python3
"""
Elements of Position — Geometric Kernel

Shear, bind, stand on a diameter, count crossings.
No angle is an input to the operators.

Scale is the hit count m.
A part and its inverse bound to the heading: r = m, 1/r = 1/m.
Path of the outward wall is the actual displacement of P = r u.

Trigonometry is not used in the walk. It may appear only as a
named comparison after the tables exist.

Default output folder: <Desktop>/eop_kernel_out/
Override with --out.
"""

from math import sqrt, log, hypot, atan, pi
from pathlib import Path
from collections import Counter
import csv
import argparse
import os
import sys


def desktop_dir() -> Path:
    home = Path.home()
    candidates = [
        home / "Desktop",
        home / "OneDrive" / "Desktop",
        home / "OneDrive" / "Bureau",
        Path(os.path.expandvars("%USERPROFILE%")) / "Desktop" if os.name == "nt" else None,
        Path(os.path.expandvars("%USERPROFILE%")) / "OneDrive" / "Desktop" if os.name == "nt" else None,
    ]
    xdg = os.environ.get("XDG_DESKTOP_DIR")
    if xdg:
        candidates.insert(0, Path(xdg).expanduser())
    for p in candidates:
        if p is not None and p.exists() and p.is_dir():
            return p
    fallback = home / "Desktop"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


OUT_DEFAULT = desktop_dir() / "eop_kernel_out"


def T_h(x, y, h):
    """Equal opposite mix. Quarter-turn generator, not an angle."""
    return (x - h * y, y + h * x)


def N(x, y):
    """Bind: restore x^2 + y^2 = 1."""
    n = hypot(x, y)
    return (x / n, y / n)


def step(x, y, h):
    return N(*T_h(x, y, h))


def heading_walk(h, max_steps):
    """
    Station: start on the diameter (1, 0).
    Event: the heading crosses y = 0.
    Returns every bound heading and the hit list.
    """
    x, y = 1.0, 0.0
    prev_y = y
    headings = [(x, y)]
    hits = []
    last_j = 0
    for j in range(1, max_steps + 1):
        x, y = step(x, y, h)
        headings.append((x, y))
        crossed = (prev_y > 0.0 and y <= 0.0) or (prev_y < 0.0 and y >= 0.0)
        if crossed:
            hits.append(
                {
                    "m": len(hits) + 1,
                    "j": j,
                    "gap": j - last_j if last_j else j,
                    "side": "down" if prev_y > 0.0 else "up",
                    "hx": x,
                    "hy": y,
                }
            )
            last_j = j
        prev_y = y
    return headings, hits


def attach_pair(headings, hits):
    """
    Pair layer after the walk.
    r = m, 1/r = 1/m.
    P = r * heading at the hit.
    Path = summed |ΔP| along the leg, radius linear in this leg's own gap.
    """
    if not hits:
        return hits
    H0 = hits[0]["j"]
    last_P = None
    cursor = 0
    for i, c in enumerate(hits):
        m = c["m"]
        r = float(m)
        rin = 1.0 / r
        u = (c["hx"], c["hy"])
        P = (r * u[0], r * u[1])
        if i == 0:
            path = 0.0
            chord = 0.0
        else:
            prev = hits[i - 1]
            gap = c["gap"]
            r0 = float(prev["m"])
            path = 0.0
            P_prev = last_P
            for s in range(1, gap + 1):
                j = prev["j"] + s
                ux, uy = headings[j]
                rr = r0 + (r - r0) * (s / gap)
                P_now = (rr * ux, rr * uy)
                path += hypot(P_now[0] - P_prev[0], P_now[1] - P_prev[1])
                P_prev = P_now
            chord = hypot(P[0] - last_P[0], P[1] - last_P[1])
        gm = sqrt(r * rin)
        am = 0.5 * (r + rin)
        gap_kind = ""
        if i == 0:
            gap_kind = "first"
        elif c["gap"] == H0:
            gap_kind = "long"
        elif c["gap"] == H0 - 1:
            gap_kind = "short"
        else:
            gap_kind = "other"
        c.update(
            {
                "k_snap": r,
                "k_frozen": c["j"] / H0,
                "r_out": r,
                "r_in": rin,
                "gm": gm,
                "am": am,
                "tension": am - gm,
                "Px": P[0],
                "Py": P[1],
                "leg_chord": chord,
                "leg_path": path,
                "leg_chord_over_path": (chord / path) if path else 1.0,
                "gap_kind": gap_kind,
                "hy_over_m": abs(c["hy"]) / r,
            }
        )
        last_P = P
        cursor = c["j"]
    return hits


def pair_rows(hits):
    """The involution is the formula r ↔ 1/r. No integer partner table."""
    return [
        {
            "m": c["m"],
            "r": c["r_out"],
            "r_in": c["r_in"],
            "am": c["am"],
            "gm": c["gm"],
            "tau": c["tension"],
        }
        for c in hits
    ]


def closed_wedge(N):
    """∫_1^N ((k + 1/k)/2 - 1) dk."""
    if N <= 1:
        return 0.0
    return (N * N - 1) / 4.0 + 0.5 * log(N) - (N - 1)


def _mean(xs):
    return sum(xs) / len(xs) if xs else ""


def summarize(h, max_steps, headings, hits):
    H0 = hits[0]["j"] if hits else 0
    gaps = [c["gap"] for c in hits] if hits else []
    n = len(hits)
    wedge = sum(c["tension"] for c in hits) if hits else 0.0
    closed = closed_wedge(float(n)) if n else 0.0
    trap = closed + 0.5 * (hits[0]["tension"] + hits[-1]["tension"]) if n else 0.0
    u0 = headings[0]
    u1 = headings[1] if len(headings) > 1 else u0
    sheet = sqrt(1.0 + h * h) - 1.0
    shorts = [c for c in hits if c.get("gap_kind") == "short"]
    longs = [c for c in hits if c.get("gap_kind") == "long"]
    word = "".join(
        "S" if c.get("gap_kind") == "short" else ("L" if c.get("gap_kind") == "long" else ".")
        for c in hits
    )
    alpha = _mean([c["hy_over_m"] for c in shorts]) if shorts else ""
    frozen_drift = (hits[-1]["m"] - hits[-1]["k_frozen"]) if n else ""
    n_short = len(shorts)
    return {
        "h": h,
        "max_steps": max_steps,
        "steps_run": len(headings) - 1,
        "H0": H0,
        "n_hits": n,
        "n_short": n_short,
        "n_long": len(longs),
        "sheet_leftover": sheet,
        "heading_chord": hypot(u1[0] - u0[0], u1[1] - u0[1]),
        "wall_chord_m1": (
            hypot(hits[0]["hx"] - 1.0, hits[0]["hy"] - 0.0) if hits else ""
        ),
        "wall_chord_m1_to_m2": (
            hypot(hits[1]["hx"] - hits[0]["hx"], hits[1]["hy"] - hits[0]["hy"])
            if n >= 2
            else ""
        ),
        "mean_gap": (sum(gaps) / n) if n else "",
        "mean_gap_times_h": (sum(gaps) / n * h) if n else "",
        "H0_times_h": H0 * h if H0 else "",
        "gap_min": min(gaps) if gaps else "",
        "gap_max": max(gaps) if gaps else "",
        "gap_histogram": dict(Counter(gaps)) if gaps else {},
        "gap_word": word,
        "frozen_drift": frozen_drift,
        "frozen_drift_as_n_short_over_H0": (n_short / H0) if H0 else "",
        "hy_over_m_on_short": alpha,
        "cp_short_mean": _mean([c["leg_chord_over_path"] for c in shorts]),
        "cp_short_last": shorts[-1]["leg_chord_over_path"] if shorts else "",
        "cp_long_mean": _mean([c["leg_chord_over_path"] for c in longs]),
        "cp_long_last": longs[-1]["leg_chord_over_path"] if longs else "",
        "cp_all_legs_mean": _mean(
            [c["leg_chord_over_path"] for c in hits if c["m"] >= 2]
        ),
        "wedge_sum": wedge,
        "wedge_closed": closed,
        "wedge_trapezoid": trap,
        "wedge_sum_minus_trapezoid": (wedge - trap) if n else "",
        "m1_pair": f"{hits[0]['r_out']},{hits[0]['r_in']}" if n else "",
        "m2_pair": f"{hits[1]['r_out']},{hits[1]['r_in']}" if n >= 2 else "",
        "comparison_pi_over_atan_h": pi / atan(h),
        "comparison_pi": pi,
        "comparison_two_over_pi": 2.0 / pi,
    }


def write_csvs(hits, pairs, summary, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    p_cross = out_dir / "eop_crossings.csv"
    fields = [
        "m",
        "j",
        "gap",
        "side",
        "k_snap",
        "k_frozen",
        "r_out",
        "r_in",
        "gm",
        "am",
        "tension",
        "hx",
        "hy",
        "hy_over_m",
        "gap_kind",
        "Px",
        "Py",
        "leg_chord",
        "leg_path",
        "leg_chord_over_path",
    ]
    with p_cross.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(hits)
    p_pairs = out_dir / "eop_pairs.csv"
    with p_pairs.open("w", newline="") as f:
        if pairs:
            w = csv.DictWriter(f, fieldnames=list(pairs[0].keys()))
            w.writeheader()
            w.writerows(pairs)
        else:
            f.write("m,r,r_in,tau,r_partner,m_partner,tau_partner,heading_dot\n")
    p_sum = out_dir / "eop_summary.csv"
    with p_sum.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value"])
        for k, v in summary.items():
            w.writerow([k, v])
    return [p_cross, p_pairs, p_sum]


def print_report(summary, hits):
    print("Elements of Position — Geometric Kernel")
    print(
        f"h={summary['h']}  steps={summary['steps_run']}  hits={summary['n_hits']}  H0={summary['H0']}"
    )
    print(
        f"sheet leftover={summary['sheet_leftover']:.8e}  "
        f"one-kick heading chord={summary['heading_chord']:.8f}"
    )
    print(
        f"far-wall chord={summary['wall_chord_m1']}  "
        f"wall-to-wall={summary['wall_chord_m1_to_m2']}"
    )
    print(
        f"gaps {summary['gap_min']}..{summary['gap_max']}  "
        f"mean={summary['mean_gap']}  mean*h={summary['mean_gap_times_h']}"
    )
    print(f"H0*h={summary['H0_times_h']}  hist={summary['gap_histogram']}")
    print(
        f"shorts={summary['n_short']}  longs={summary['n_long']}  "
        f"word={summary['gap_word']}"
    )
    print(
        f"c/p short last={summary['cp_short_last']}  "
        f"c/p long last={summary['cp_long_last']}"
    )
    print(
        f"|hy|/m on short={summary['hy_over_m_on_short']}  "
        f"frozen drift={summary['frozen_drift']}  "
        f"n_short/H0={summary['frozen_drift_as_n_short_over_H0']}"
    )
    print(
        f"wedge_sum={summary['wedge_sum']:.6f}  "
        f"closed={summary['wedge_closed']:.6f}  "
        f"trapezoid={summary['wedge_trapezoid']:.6f}  "
        f"sum-trap={summary['wedge_sum_minus_trapezoid']}"
    )
    print(
        f"comparison after the tables (sits between the two bands / two integers): "
        f"pi={summary['comparison_pi']:.8f}  "
        f"pi/atan(h)={summary['comparison_pi_over_atan_h']:.6f}  "
        f"2/pi={summary['comparison_two_over_pi']:.8f}"
    )
    if not hits:
        return
    print()
    print(
        f"{'m':>5} {'side':<5} {'j':>8} {'gap':>6} {'r':>6} {'1/r':>10} "
        f"{'tau':>10} {'c/p':>8}"
    )
    show = {1, 2, 3, 4, 5, 8, 10, 20, 50, 100}
    show |= {hits[-1]["m"]}
    for c in hits:
        if c["m"] not in show:
            continue
        print(
            f"{c['m']:5d} {c['side']:<5} {c['j']:8d} {c['gap']:6d} "
            f"{c['r_out']:6.0f} {c['r_in']:10.6f} {c['tension']:10.6f} "
            f"{c['leg_chord_over_path']:8.5f}"
        )


def main():
    ap = argparse.ArgumentParser(description="Elements of Position — Geometric Kernel")
    ap.add_argument("--h", type=float, default=0.002, help="shear size")
    ap.add_argument(
        "--steps",
        type=int,
        default=200000,
        help="maximum operator steps (default 200000)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=OUT_DEFAULT,
        help=f"output folder for CSV files (default: {OUT_DEFAULT})",
    )
    args = ap.parse_args()
    out_dir = args.out.expanduser().resolve()
    print(
        f"Elements of Position — Geometric Kernel   h={args.h}  steps={args.steps}",
        flush=True,
    )
    print(f"output folder: {out_dir}", flush=True)
    headings, hits = heading_walk(args.h, args.steps)
    attach_pair(headings, hits)
    pairs = pair_rows(hits)
    summary = summarize(args.h, args.steps, headings, hits)
    print_report(summary, hits)
    paths = write_csvs(hits, pairs, summary, out_dir)
    print("wrote:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        sys.exit(130)
