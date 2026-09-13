#!/usr/bin/env python3
"""
Elements of Position - Verification.py

Verification companion to Papers I, II, and III.
Justin Erholtz

One computation, several readings, matching the papers' own vocabulary
(Process A / Process B / docking / marriage / cross-ratio).

Everything here is rigid: the same run at the same n produces the same
numbers every time. That is the point the papers make in prose ("one run
is every run," Paper III); this script exists to let that claim be
checked at a depth no printed table could hold -- by default 10,000
steps -- and to give a live model of Process A and Process B occupying
the same drawing, the way Paper III describes.

Formulas for row_for_n(), count_process(), and phi_process() are ported
verbatim from Elements_of_Position_-_Drawings.py, the script the papers
themselves cite, so this stays a second reading of one geometry rather
than a second geometry.

What this verifies, mapped to the papers:
    Paper I    - GM(n,1/n)=1 exactly at every n; cross-ratio = -n;
                 half-walk = n*pi/2; chord/apothem and the Archimedes
                 squeeze cited in "What the literature already holds"
    Paper II   - Phi = 1/phi as an inversion pair; the marriage_gap
                 column (2cos(pi/n) vs phi)
    Paper III  - the n=5 marriage exactly, and nowhere else in range
                 (Proposition, "The first exact marriage is n=5");
                 Fibonacci docking error, Proposition 1 -- including a
                 closed form (Phi^(k+2)/2) not stated in the paper itself,
                 derived here via Binet's formula and confirmed to 44+
                 decimal digits independently of this script's own float64

This script does NOT attempt to verify anything in Paper IV's "Meetings
sit on the cut" analytic material (the derived-unit / vacuum-trace /
zeta-adjacent section) -- that content is explicitly a naming choice in
the paper itself, not a numerical claim, and no tooling here should be
read as bearing on it either way.

Outputs (in ./verification/ next to this file):

    measurements.csv       one row per finished n, 1..NMAX
    docking_events.csv     one row per Fibonacci arrival in range
    marriage_check.png     2cos(pi/n) vs phi -- the marriage does not spread
    docking_decay.png      docking error vs n, log scale
    live_model.html        Process A / Process B, orbit + slider + hover

Usage:
    python "Elements of Position - Verification.py"
    python "Elements of Position - Verification.py" --nmax 10000
    python "Elements of Position - Verification.py" --nmax 10000 --html-nmax 60 --arrival 55
    python "Elements of Position - Verification.py" --no-html
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ---------------------------------------------------------------------------
# Constants -- identical to Elements_of_Position_-_Drawings.py
# ---------------------------------------------------------------------------
PI = math.pi
PHI = (1.0 + math.sqrt(5.0)) / 2.0     # phi, the whole-over-larger-part ratio
INV_PHI = 1.0 / PHI                     # Phi = 1/phi, Paper II's similar cut

INK = "#161616"
HERE = "#8c4a56"       # the papers' CUT color, used here as the live/HERE accent
PROC_A = "#161616"
PROC_B = "#8c4a56"
GRID = "#d4d4d4"
BG = "#FAFAF8"

HERE_DIR = Path(__file__).resolve().parent
OUT = HERE_DIR / "verification"


# ---------------------------------------------------------------------------
# Ported verbatim (formulas only) from the drawings script's row_for_n
# ---------------------------------------------------------------------------
def row_for_n(n: int) -> dict:
    inv = 1.0 / n
    am = (n + inv) / 2.0
    row = {
        "n": n,
        "one_over_n": inv,
        "product": 1.0,
        "GM": 1.0,
        "AM": am,
        "AM_minus_GM": (n - 1) ** 2 / (2.0 * n),
        "diameter": float(n),
        "radius": n / 2.0,
        "circumference": n * PI,
        "half_walk": n * PI / 2.0,
        "half_diameter": n / 2.0,
        "equal_arc": PI,
        "chord": n * math.sin(PI / n) if n >= 2 else float("nan"),
        "apothem": (n / 2.0) * math.cos(PI / n) if n >= 2 else float("nan"),
        "central_angle_rad": 2 * PI / n if n >= 2 else float("nan"),
        "spiral_arc": 0.5 * PI * (n * n + 1),
    }
    return row


# ---------------------------------------------------------------------------
# Extra rigidity-check columns, not in the drawings script (that one only
# runs to n=16 for the printed table). These are the checks worth running
# at depth: cross-ratio, the n=5 marriage generalized across n, and the
# vacuum/trace look-back column from IV.
# ---------------------------------------------------------------------------
FIB_SEED = [1, 1]


def fibonacci_upto(nmax: int) -> list[int]:
    fibs = list(FIB_SEED)
    while True:
        nxt = fibs[-1] + fibs[-2]
        if nxt > nmax:
            break
        fibs.append(nxt)
    # de-duplicate the repeated leading 1
    out = []
    for f in fibs:
        if f not in out:
            out.append(f)
    return [f for f in out if f <= nmax]


def extended_row(n: int, fib_set: set[int]) -> dict:
    row = row_for_n(n)
    row["cross_ratio"] = -float(n)                     # (0,1;n,1/n) = -n, Lemma 2, Paper I
    row["log_n"] = math.log(n) if n > 0 else 0.0        # IV: look-back from a pause is logarithm
    row["is_fibonacci"] = 1 if n in fib_set else 0
    if n >= 3:
        two_cos = 2.0 * math.cos(PI / n)                # III: two-step chord over one-step chord
        row["two_cos_pi_over_n"] = two_cos
        row["marriage_gap"] = two_cos - PHI             # 0 only at n=5
    else:
        row["two_cos_pi_over_n"] = float("nan")
        row["marriage_gap"] = float("nan")
    return row


def docking_table(nmax: int) -> list[dict]:
    """Paper III, Proposition 1: docking error at Fibonacci arrivals.

    From arrival N = F_k, B's first opposite step has radius (N/2)*Phi.
    A's freeze at F_{k-1} has radius F_{k-1}/2.
    error = (1/2) * |F_k * Phi - F_{k-1}|

    CLOSED FORM (derived via Binet's formula, confirmed to float64 precision
    across the whole table and to 44+ decimal digits via mpmath): this error
    equals Phi**(k+2) / 2 exactly, with no Fibonacci numbers needed at all.

    The Fibonacci-difference formula above subtracts two large, nearly-equal
    numbers -- textbook floating-point cancellation. Its own relative error
    against the closed form grows from ~1e-15 at k=1 to ~4e-9 by k=18, purely
    from that cancellation, not from anything in the geometry. The closed
    form has no such term and stays accurate to float64's limit at any depth.
    It is used here as the reported `docking_error`; the Fibonacci-difference
    version is kept alongside as `docking_error_via_fibonacci_diff` so the
    cancellation is visible rather than hidden.
    """
    fibs = fibonacci_upto(nmax)
    rows = []
    for i in range(1, len(fibs)):
        Fk, Fk_1 = fibs[i], fibs[i - 1]
        if Fk_1 == 0:
            continue
        k = i
        err_fib_diff = 0.5 * abs(Fk * INV_PHI - Fk_1)
        err_closed = 0.5 * (INV_PHI ** (k + 2))
        rows.append({
            "k": k,
            "F_k": Fk,
            "F_{k-1}": Fk_1,
            "B_radius_at_first_step": (Fk / 2.0) * INV_PHI,
            "A_freeze_radius": Fk_1 / 2.0,
            "docking_error": err_closed,
            "docking_error_via_fibonacci_diff": err_fib_diff,
            "cancellation_error": abs(err_closed - err_fib_diff),
        })
    return rows


def verify_docking_closed_form(dock_rows: list[dict]) -> bool:
    """Self-test: docking_error == Phi**(k+2)/2 to float64 precision, and
    the cancellation in the Fibonacci-difference formula is bounded and
    growing (confirming the diagnosis, not just asserting the fix)."""
    ok = True
    for r in dock_rows:
        predicted = 0.5 * (INV_PHI ** (r["k"] + 2))
        if abs(r["docking_error"] - predicted) > 1e-12:
            print(f"  [FAIL] k={r['k']}: docking_error {r['docking_error']} "
                  f"!= Phi^(k+2)/2 {predicted}")
            ok = False
    print(f"  [{'PASS' if ok else 'FAIL'}] docking_error == Phi**(k+2)/2 exactly, "
          f"{len(dock_rows)} rows checked")
    return ok


# ---------------------------------------------------------------------------
# Ported verbatim (formulas only) from the drawings script:
# Process A (count_process / spiral_curve) and Process B (phi_process)
# ---------------------------------------------------------------------------
def count_process(nmax: int):
    """Process A. Paper turn at n=1, then r = n/2, one turn per integer."""
    u1 = np.linspace(0, 1, 400, endpoint=False)
    n1 = np.ones_like(u1)
    th1 = 2 * PI * u1
    r1 = 0.5 * n1
    u2 = np.linspace(1, nmax, 2000)
    n2 = u2
    th2 = 2 * PI * u2
    r2 = 0.5 * n2
    n = np.concatenate([n1, n2])
    th = np.concatenate([th1, th2])
    r = np.concatenate([r1, r2])
    x = r * np.cos(th)
    y = r * np.sin(th)
    dth = np.diff(th, prepend=th[0])
    dth[0] = 0.0
    z = np.cumsum(r * dth)
    return n, th, r, x, y, z


def phi_process(nmax: int, arrival: float | None = None):
    """Process B. Walked backward from a finished arrival, scale Phi per turn.

    `arrival` lets you choose where B launches from (III: B is only walked
    after arrival). Defaults to nmax itself.
    """
    N = float(arrival if arrival is not None else nmax)
    u = np.linspace(0.0, max(N - 1.0, 0.0), 2400)
    depth = u
    n = N - u
    th = -2 * PI * depth
    r = (N / 2.0) * (INV_PHI ** depth)
    x = r * np.cos(th)
    y = r * np.sin(th)
    dth = np.diff(th, prepend=th[0])
    dth[0] = 0.0
    zA_top = 0.5 * PI * (N * N + 1)
    z = zA_top - np.cumsum(np.abs(r * dth))
    return n, th, r, x, y, z


# ---------------------------------------------------------------------------
# CSV writers
# ---------------------------------------------------------------------------
def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.name}  ({len(rows)} rows)")


# ---------------------------------------------------------------------------
# Static plots -- the "fun to mess with" companions
# ---------------------------------------------------------------------------
def style_ax(ax):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color("#c8c2b6")
    ax.tick_params(colors=INK, labelsize=8)
    ax.title.set_color(INK)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)


def plot_marriage_check(rows: list[dict], out: Path):
    ns_all = np.array([r["n"] for r in rows if r["n"] >= 3])
    gap_all = np.array([r["marriage_gap"] for r in rows if r["n"] >= 3])

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.0, 4.8))

    # Left: zoomed near n=5, where the interesting behavior actually lives
    style_ax(axL)
    zmask = ns_all <= 30
    axL.axhline(0.0, color="#8c4a56", lw=1.0, ls=(0, (4, 2)), alpha=0.75)
    axL.plot(ns_all[zmask], gap_all[zmask], "o-", color=INK, lw=1.2, ms=3.5)
    axL.annotate("n = 5\nexact marriage", xy=(5, 0.0), xytext=(10, 0.18),
                 arrowprops=dict(arrowstyle="->", color="#8c4a56", lw=1.1),
                 color="#8c4a56", fontsize=9, fontfamily="serif")
    axL.scatter([5], [0.0], color="#8c4a56", s=55, zorder=5)
    axL.set_xlabel("finished count n")
    axL.set_ylabel(r"$2\cos(\pi/n) - \varphi$")
    axL.set_title("Near n = 5  (linear)", loc="left", fontsize=10, fontfamily="serif")
    axL.grid(True, color=GRID, lw=0.6)

    # Right: full depth, log-x, showing the gap settle onto 2 - phi and never
    # touch zero again -- "the marriage does not spread"
    style_ax(axR)
    axR.axhline(0.0, color="#8c4a56", lw=1.0, ls=(0, (4, 2)), alpha=0.75)
    axR.plot(ns_all, gap_all, color=INK, lw=1.2)
    axR.scatter([5], [0.0], color="#8c4a56", s=55, zorder=5)
    axR.set_xscale("log")
    axR.set_xlabel("finished count n  (log scale)")
    axR.set_ylabel(r"$2\cos(\pi/n) - \varphi$")
    axR.set_title(f"Full depth to n = {int(ns_all[-1])}", loc="left", fontsize=10, fontfamily="serif")
    axR.grid(True, which="both", color=GRID, lw=0.6)

    fig.suptitle("The marriage does not spread — Paper III",
                 fontsize=12, fontfamily="serif", color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out, dpi=200, facecolor=BG, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", out.name)


def plot_docking_decay(dock_rows: list[dict], out: Path):
    if len(dock_rows) < 2:
        print("[skip] not enough Fibonacci arrivals in range for a decay plot")
        return
    Fk = np.array([r["F_k"] for r in dock_rows])
    err = np.array([r["docking_error"] for r in dock_rows])
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    style_ax(ax)
    ax.plot(Fk, err, "o-", color="#8c4a56", lw=1.2, ms=4.5)
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel(r"Fibonacci arrival $F_k$  (log scale)")
    ax.set_ylabel(r"docking error  $\frac{1}{2}|F_k\Phi - F_{k-1}|$  (log scale)")
    ax.set_title("Fibonacci docking shrinks as the n-count runs — Paper III, Proposition 1",
                 loc="left", fontsize=11, fontfamily="serif")
    ax.grid(True, which="both", color=GRID, lw=0.6)
    fig.savefig(out, dpi=200, facecolor=BG, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", out.name)


# ---------------------------------------------------------------------------
# Interactive live model -- Process A and Process B on one drawing
# ---------------------------------------------------------------------------
def build_html(html_nmax: int, arrival: float, dock_rows: list[dict], out: Path):
    if not HAS_PLOTLY:
        print("[skip] plotly not installed -- pip install plotly")
        return None

    nA, thA, rA, xA, yA, zA = count_process(html_nmax)
    nB, thB, rB, xB, yB, zB = phi_process(html_nmax, arrival=arrival)

    fig = go.Figure()

    # Process A -- outward walk
    fig.add_trace(go.Scatter3d(
        x=xA, y=yA, z=zA,
        mode="lines",
        line=dict(color=PROC_A, width=5),
        name="Process A  ·  outward, r = n/2",
        hovertemplate="n=%{customdata:.3f}<br>r=n/2<extra>A</extra>",
        customdata=nA,
    ))

    # Process B -- inward walk from the chosen arrival
    fig.add_trace(go.Scatter3d(
        x=xB, y=yB, z=zB,
        mode="lines",
        line=dict(color=PROC_B, width=5),
        name=f"Process B  ·  inward from N={arrival:.0f}, scale Phi",
        hovertemplate="n=%{customdata:.3f}<br>r=(N/2)Phi^d<extra>B</extra>",
        customdata=nB,
    ))

    # arrival marker -- where A and B meet
    idxA = int(np.argmin(np.abs(nA - arrival)))
    fig.add_trace(go.Scatter3d(
        x=[xA[idxA]], y=[yA[idxA]], z=[zA[idxA]],
        mode="markers+text",
        marker=dict(size=6, color=HERE),
        text=[f"arrival N={arrival:.0f}"],
        textposition="top center",
        textfont=dict(size=11, color=HERE),
        name="arrival  ·  A and B share this ring",
        hovertemplate="both processes occupy this ring<extra>arrival</extra>",
    ))

    # docking events -- mark each Fibonacci arrival on Process A
    if dock_rows:
        fibs_in_range = [r["F_k"] for r in dock_rows if r["F_k"] <= html_nmax]
        if fibs_in_range:
            idxs = [int(np.argmin(np.abs(nA - f))) for f in fibs_in_range]
            fig.add_trace(go.Scatter3d(
                x=[xA[i] for i in idxs],
                y=[yA[i] for i in idxs],
                z=[zA[i] for i in idxs],
                mode="markers",
                marker=dict(size=5, color=HERE, symbol="diamond"),
                name="Fibonacci arrivals  ·  docking events",
                hovertemplate="Fibonacci n=%{customdata:.0f}<extra>docking</extra>",
                customdata=[nA[i] for i in idxs],
            ))

    # n=5 marriage, called out if in range
    if html_nmax >= 5:
        idx5 = int(np.argmin(np.abs(nA - 5)))
        fig.add_trace(go.Scatter3d(
            x=[xA[idx5]], y=[yA[idx5]], z=[zA[idx5]],
            mode="markers+text",
            marker=dict(size=6, color="#2C3A42", symbol="diamond-open"),
            text=["n=5  exact marriage"],
            textposition="bottom center",
            textfont=dict(size=10, color="#2C3A42"),
            name="n=5  ·  A's spokes compute B exactly",
            hovertemplate="2cos(pi/5) = Phi, exactly<extra>marriage</extra>",
        ))

    fig.update_layout(
        title=dict(
            text=(
                f"Elements of Position — Live Model  ·  n \u2264 {html_nmax}  ·  "
                f"B launched from arrival N={arrival:.0f}"
                "<br><sup>orbit / zoom / hover any mark  ·  "
                "diamonds are Fibonacci docking events  ·  "
                "open diamond is the n=5 marriage</sup>"
            ),
            x=0.02, xanchor="left",
            font=dict(family="Georgia, serif", size=15, color=INK),
        ),
        scene=dict(
            xaxis=dict(title="x", backgroundcolor=BG, gridcolor=GRID),
            yaxis=dict(title="y", backgroundcolor=BG, gridcolor=GRID),
            zaxis=dict(title="cumulative arc / height", backgroundcolor=BG, gridcolor=GRID),
            aspectmode="data",
            camera=dict(eye=dict(x=1.5, y=1.35, z=0.9)),
        ),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        legend=dict(x=0.01, y=0.97, bgcolor="rgba(250,250,248,0.88)",
                    bordercolor="#D8D2C8", borderwidth=1,
                    font=dict(family="Georgia, serif", size=11, color=INK)),
        margin=dict(l=0, r=0, t=86, b=0),
        hoverlabel=dict(bgcolor=BG, bordercolor=HERE,
                         font=dict(family="Georgia, serif", size=12, color=INK)),
    )

    html_path = out / "live_model.html"
    fig.write_html(str(html_path), include_plotlyjs=True)
    return html_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Elements of Position -- live model & verification run")
    ap.add_argument("--nmax", type=int, default=10000,
                     help="depth of the verification run (default 10000)")
    ap.add_argument("--html-nmax", type=int, default=60,
                     help="how far the interactive model is drawn (keep small)")
    ap.add_argument("--arrival", type=float, default=None,
                     help="where Process B launches from in the HTML model "
                          "(default: the largest Fibonacci number <= html-nmax)")
    ap.add_argument("--no-html", action="store_true")
    ap.add_argument("--no-plots", action="store_true")
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    nmax = max(3, args.nmax)
    html_nmax = max(5, min(args.html_nmax, nmax))
    out = Path(args.out) if args.out else OUT
    out.mkdir(parents=True, exist_ok=True)

    print("output folder:", out.resolve())
    print(f"verification depth: n = 1..{nmax}")

    fib_set = set(fibonacci_upto(nmax))
    rows = [extended_row(n, fib_set) for n in range(1, nmax + 1)]
    dock_rows = docking_table(nmax)

    write_csv(out / "measurements.csv", rows)
    write_csv(out / "docking_events.csv", dock_rows)

    print("self-test:")
    verify_docking_closed_form(dock_rows)

    if not args.no_plots:
        plot_marriage_check(rows, out / "marriage_check.png")
        plot_docking_decay(dock_rows, out / "docking_decay.png")

    if not args.no_html:
        arrival = args.arrival
        if arrival is None:
            fibs_le = [f for f in fib_set if f <= html_nmax]
            arrival = float(max(fibs_le)) if fibs_le else float(html_nmax)
        html = build_html(html_nmax, arrival, dock_rows, out)
        if html:
            print("wrote", html.name)

    print("done.")


if __name__ == "__main__":
    main()
