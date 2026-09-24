#!/usr/bin/env python3
"""
Elements of Position — Geometric Kernel

A part and its inverse, bound to a heading.
Shear, bind, walk. Scale is steps over a half-turn the heading counts
by crossing both horizons. No constants loaded into the operators.

Default output folder: <Desktop>/eop_kernel_out/
Override with --out.
"""

from math import sqrt, log, atan, pi, atan2, hypot
from pathlib import Path
from collections import Counter
import csv
import argparse
import os
import sys


def desktop_dir() -> Path:
    """Best-effort Desktop path on Windows, macOS, and Linux."""
    home = Path.home()
    candidates = [
        home / "Desktop",
        home / "OneDrive" / "Desktop",
        home / "OneDrive" / "Bureau",  # some FR Windows OneDrive layouts
        Path(os.path.expandvars("%USERPROFILE%")) / "Desktop" if os.name == "nt" else None,
        Path(os.path.expandvars("%USERPROFILE%")) / "OneDrive" / "Desktop" if os.name == "nt" else None,
    ]
    xdg = os.environ.get("XDG_DESKTOP_DIR")
    if xdg:
        candidates.insert(0, Path(xdg).expanduser())
    for p in candidates:
        if p is not None and p.exists() and p.is_dir():
            return p
    # Last resort: create ~/Desktop if nothing is found
    fallback = home / "Desktop"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


OUT_DEFAULT = desktop_dir() / "eop_kernel_out"


def T_h(x, y, h):
    """Linear shear of the heading."""
    return (x - h * y, y + h * x)


def N(x, y):
    """Bind: put the heading back on the unit circle."""
    n = hypot(x, y)
    return (x / n, y / n)


def step(x, y, h):
    """One kernel move: shear, then bind."""
    return N(*T_h(x, y, h))


def dist(p, q):
    return hypot(p[0] - q[0], p[1] - q[1])


def closed_wedge(N):
    """Leftover of the pair, kiss to N."""
    if N <= 2:
        return 0.0
    return (N * N) / 8.0 + log(N) - N + 1.5 - log(2.0)


def pair_of(k):
    """Two walls at scale k. Product 1. Leftover AM − GM."""
    r_out = k / 2.0
    r_in = 2.0 / k
    gm = sqrt(r_out * r_in)
    am = 0.5 * (r_out + r_in)
    return r_out, r_in, gm, am, am - gm


def walk(h, n_half, write_waterfall_every=0):
    """Walk until n_half horizon hits (up and down)."""
    sheet_leftover = sqrt(1.0 + h * h) - 1.0

    x, y = 1.0, 0.0
    prev_y = y
    j = 0
    crossings = []
    waterfall = []
    last_j = 0
    last_P = (0.0, 0.0)
    path_acc = 0.0
    r_prev = 0.0
    P_prev = None

    while len(crossings) < n_half:
        x, y = step(x, y, h)
        j += 1
        crossed = (prev_y > 0.0 and y <= 0.0) or (prev_y < 0.0 and y >= 0.0)
        if crossed:
            m = len(crossings) + 1
            k = float(m)
            r_out, r_in, gm, am, tens = pair_of(k)
            P = (r_out * x, r_out * y)
            gap = j - last_j if last_j else j
            if m == 1:
                chord = 0.0
                path = 0.0
                c_over_p = 1.0
            else:
                chord = dist(last_P, P)
                path = path_acc
                c_over_p = chord / path if path else 1.0
            crossings.append(
                {
                    "m": m,
                    "j": j,
                    "gap": gap,
                    "side": "down" if prev_y > 0.0 else "up",
                    "k_snap": k,
                    "r_out": r_out,
                    "r_in": r_in,
                    "gm": gm,
                    "am": am,
                    "tension": tens,
                    "hx": x,
                    "hy": y,
                    "atan2": atan2(y, x),
                    "Px": P[0],
                    "Py": P[1],
                    "leg_chord": chord,
                    "leg_path": path,
                    "leg_chord_over_path": c_over_p,
                }
            )
            last_j = j
            last_P = P
            path_acc = 0.0

        k_arm = float(len(crossings)) + (
            (j - last_j) / crossings[-1]["gap"] if crossings and crossings[-1]["gap"] else 0.0
        )
        if k_arm < 1e-12:
            k_arm = j / max(j, 1)
        r_now = k_arm / 2.0
        P_now = (r_now * x, r_now * y)
        if P_prev is not None:
            dr = abs(r_now - r_prev)
            r_mean = 0.5 * (r_now + r_prev)
            path_acc += sqrt((r_mean * h) ** 2 + dr * dr)
        P_prev = P_now
        r_prev = r_now

        if write_waterfall_every and j % write_waterfall_every == 0:
            if k_arm > 0:
                ro, ri, gm, am, tens = pair_of(max(k_arm, 1e-12))
            else:
                ro = ri = gm = am = tens = 0.0
            waterfall.append(
                {
                    "j": j,
                    "k_arm": k_arm,
                    "r_out": ro,
                    "r_in": ri,
                    "gm": gm,
                    "tension": tens,
                    "hx": x,
                    "hy": y,
                }
            )
        prev_y = y

    H0 = crossings[0]["j"]
    x0, y0 = 1.0, 0.0
    x1, y1 = step(x0, y0, h)
    heading_chord = dist((x0, y0), (x1, y1))

    for c in crossings:
        c["k_frozen"] = c["j"] / H0

    wedge = 0.0
    for i in range(1, len(crossings)):
        k0 = crossings[i - 1]["k_snap"]
        k1 = crossings[i]["k_snap"]
        if k1 <= 2.0:
            continue
        a = max(k0, 2.0)
        b = k1

        def F(kv):
            return kv * kv / 8.0 + log(kv) - kv

        wedge += F(b) - F(a)

    return {
        "h": h,
        "H0": H0,
        "n_half": len(crossings),
        "sheet_leftover": sheet_leftover,
        "heading_chord": heading_chord,
        "true_half": pi / atan(h),
        "H0_times_h": H0 * h,
        "wedge_from_crossings": wedge,
        "wedge_closed": closed_wedge(float(len(crossings))),
        "crossings": crossings,
        "waterfall": waterfall,
    }


def write_csvs(run, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    crosses = run["crossings"]
    p_cross = out_dir / "eop_crossings.csv"
    with p_cross.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(crosses[0].keys()))
        w.writeheader()
        w.writerows(crosses)

    n = run["n_half"]
    by_m = {c["m"]: c for c in crosses}
    pairs = []
    for c in crosses:
        k = c["k_snap"]
        m_p = int(round(4.0 / k))
        if m_p < 1 or m_p > n:
            continue
        b = by_m[m_p]
        pairs.append(
            {
                "m": c["m"],
                "k": k,
                "m_part": b["m"],
                "k_part": b["k_snap"],
                "tens": c["tension"],
                "tens_part": b["tension"],
                "r_out": c["r_out"],
                "r_in": c["r_in"],
                "r_out_part": b["r_out"],
                "r_in_part": b["r_in"],
                "heading_dot": c["hx"] * b["hx"] + c["hy"] * b["hy"],
            }
        )
    p_pairs = out_dir / "eop_pairs.csv"
    with p_pairs.open("w", newline="") as f:
        if pairs:
            w = csv.DictWriter(f, fieldnames=list(pairs[0].keys()))
            w.writeheader()
            w.writerows(pairs)
        else:
            w = csv.writer(f)
            w.writerow(
                [
                    "m",
                    "k",
                    "m_part",
                    "k_part",
                    "tens",
                    "tens_part",
                    "r_out",
                    "r_in",
                    "r_out_part",
                    "r_in_part",
                    "heading_dot",
                ]
            )

    p_sum = out_dir / "eop_summary.csv"
    gaps = [c["gap"] for c in crosses]
    hist = Counter(gaps)
    with p_sum.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value"])
        for key in (
            "h",
            "H0",
            "n_half",
            "sheet_leftover",
            "heading_chord",
            "true_half",
            "H0_times_h",
            "wedge_from_crossings",
            "wedge_closed",
        ):
            w.writerow([key, run[key]])
        w.writerow(["mean_gap", sum(gaps) / len(gaps)])
        w.writerow(["gap_min", min(gaps)])
        w.writerow(["gap_max", max(gaps)])
        w.writerow(["gap_histogram", dict(hist)])
        w.writerow(["wedge_diff", run["wedge_from_crossings"] - run["wedge_closed"]])

    written = [p_cross, p_pairs, p_sum]
    if run["waterfall"]:
        p_w = out_dir / "eop_waterfall.csv"
        with p_w.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(run["waterfall"][0].keys()))
            w.writeheader()
            w.writerows(run["waterfall"])
        written.append(p_w)
    return written


def print_report(run):
    C = run["crossings"]
    print("Elements of Position — Geometric Kernel")
    print(f"h={run['h']}  H0={run['H0']}  half-turns={run['n_half']}")
    print(f"true half-turn steps={run['true_half']:.6f}  H0*h={run['H0_times_h']:.6f}")
    print(f"sheet leftover={run['sheet_leftover']:.8e}  heading chord={run['heading_chord']:.8f}")
    gaps = [c["gap"] for c in C]
    print(f"gaps {min(gaps)}..{max(gaps)}  mean={sum(gaps)/len(gaps):.6f}  hist={dict(Counter(gaps))}")
    print(
        f"wedge={run['wedge_from_crossings']:.6f}  "
        f"closed={run['wedge_closed']:.6f}  "
        f"diff={run['wedge_from_crossings']-run['wedge_closed']:.6f}"
    )
    print()
    print(f"{'m':>5} {'side':<5} {'j':>8} {'gap':>6} {'k_frz':>8} {'tens':>10} {'hx':>9} {'hy':>9} {'c/p':>8}")
    show = {1, 2, 3, 4, 5, 8, 10, 20, 50, 100}
    show |= {run["n_half"]}
    for c in C:
        if c["m"] not in show:
            continue
        print(
            f"{c['m']:5d} {c['side']:<5} {c['j']:8d} {c['gap']:6d} {c['k_frozen']:8.3f} "
            f"{c['tension']:10.6f} {c['hx']:9.5f} {c['hy']:9.5f} {c['leg_chord_over_path']:8.5f}"
        )


def main():
    ap = argparse.ArgumentParser(description="Elements of Position — Geometric Kernel")
    ap.add_argument("--h", type=float, default=0.002, help="shear size")
    ap.add_argument("--n", type=int, default=400, help="half-turn crossings")
    ap.add_argument("--waterfall-every", type=int, default=0, help="write between-hit rows every N steps")
    ap.add_argument(
        "--out",
        type=Path,
        default=OUT_DEFAULT,
        help=f"output folder for CSV files (default: {OUT_DEFAULT})",
    )
    args = ap.parse_args()
    out_dir = args.out.expanduser().resolve()
    print(
        f"Elements of Position — Geometric Kernel   h={args.h}  n={args.n}",
        flush=True,
    )
    print(f"output folder: {out_dir}", flush=True)
    run = walk(args.h, args.n, write_waterfall_every=args.waterfall_every)
    print_report(run)
    paths = write_csvs(run, out_dir)
    print("wrote:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        sys.exit(130)
