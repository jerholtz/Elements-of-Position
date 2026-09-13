#!/usr/bin/env python3
"""
architectural_drawings.py

Source of numbers and drawings for
  The Closed Unit
  Justin Erholtz  ·  09 September 2026

Every integer n shares:
    n * (1/n) = 1
    GM(n, 1/n) = 1
    AM(n, 1/n) = (n + 1/n)/2
    local diameter d = n
    local walk C = n * pi
    half-walk = n * pi / 2
    equal arc = pi
    spoke side = n * sin(pi/n)

Paper start: n = 1, diameter 1, one turn, s = pi.

Usage:
    python3 architectural_drawings.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DRAW = ROOT / "drawings"
DATA.mkdir(exist_ok=True)
DRAW.mkdir(exist_ok=True)

DIAMETER = 1.0
RADIUS = 0.5
PI = math.pi
INV_PI = 1.0 / PI
PHI = (1.0 + math.sqrt(5.0)) / 2.0
INV_PHI = 1.0 / PHI  # = PHI - 1
N_MIN, N_MAX = 1, 16
NS = list(range(N_MIN, N_MAX + 1))

# One ink. Gray is shade. One highlight: the even cut and the lock only.
INK = "#161616"
GRAY = "#8a8a8a"
GRAY_LIGHT = "#d4d4d4"
CUT = "#8c4a56"
CUT_A = 0.88
NAVY = RED = BLUE = ORANGE = GOLD = INK

W_FRONT = 1.85
W_WALK = 0.85
W_CUT = 1.25
W_CONST = 0.40
W_GHOST = 0.25
W_HAIR = 0.25
W_MARK = 18
W_MARK_LOCK = 28

LS_ARRIVED = "-"
LS_CUT = (0, (2.6, 1.8))      # midline / pause — identical everywhere
LS_INVERT = (0, (0.7, 1.5))   # inversion
LS_PAUSE = LS_CUT
LS_LOOK = LS_INVERT

HATCH_OVER = "////"  # only where two streets occupy the same poche

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "grid.color": INK,
        "grid.alpha": 0.12,
        "grid.linewidth": 0.4,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "lines.solid_capstyle": "butt",
        "lines.dash_capstyle": "butt",
    }
)


# ---------------------------------------------------------------------------
# Math
# ---------------------------------------------------------------------------

def am_gm_fixed_sum(x: np.ndarray, total: float):
    other = total - x
    am = np.full_like(x, total / 2.0, dtype=float)
    gm = np.sqrt(np.clip(x * other, 0.0, None))
    return other, am, gm


def inverted_means_on_sum2(x: np.ndarray):
    prod = x * (2.0 - x)
    return 1.0 / prod, 1.0 / np.sqrt(prod)


def row_for_n(n: int) -> dict:
    inv = 1.0 / n
    am = (n + inv) / 2.0
    return {
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


def spiral_curve(nmax: int = N_MAX):
    """Paper turn at n=1, then r = n/2, one turn per integer."""
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


def count_process(nmax: int = N_MAX):
    """Independent process A: main n-count walk. Paper turn, then r = n/2."""
    return spiral_curve(nmax)


FIB = [1, 1, 2, 3, 5, 8, 13]


def phi_process(nmax: int = N_MAX):
    """Independent process B: in-count from the arrived n.

    Built from where the n-count is, walked the other way:
    opposite angle, scale Φ per turn, down toward the base.
    Similar copies can be constructed as n grows; the walk is only
    after arrival, inward.
    """
    u = np.linspace(0.0, float(nmax - 1), 2400)
    depth = u
    n = nmax - u
    th = -2 * PI * depth
    r = (nmax / 2.0) * (INV_PHI ** depth)
    x = r * np.cos(th)
    y = r * np.sin(th)
    dth = np.diff(th, prepend=th[0])
    dth[0] = 0.0
    zA_top = 0.5 * PI * (nmax * nmax + 1)
    z = zA_top - np.cumsum(np.abs(r * dth))
    return n, th, r, x, y, z


def _circle(ax, rad, color=INK, lw=W_WALK, alpha=1.0, ls=LS_ARRIVED):
    t = np.linspace(0, 2 * PI, 360)
    ax.plot(rad * np.cos(t), rad * np.sin(t), color=color, lw=lw, alpha=alpha, ls=ls)


def _ngon(ax, rad, n, color=INK, lw=W_CONST, alpha=1.0):
    if n < 3:
        return
    a = 2 * PI * np.arange(n + 1) / n
    ax.plot(rad * np.cos(a), rad * np.sin(a), color=color, lw=lw, alpha=alpha)


def _midline(ax, half, with_diameter=True, **kw):
    """Even cut. Mauve dashed. Same in every view."""
    ax.axvline(0, color=CUT, ls=LS_CUT, lw=W_CUT, alpha=CUT_A, zorder=5, **kw)
    if with_diameter:
        ax.plot([-half, half], [0, 0], color=INK, lw=W_WALK, zorder=4)


def _lock(ax, x=0.0, y=0.0, s=None):
    ax.scatter([x], [y], c=CUT, s=s or W_MARK_LOCK, zorder=6, alpha=CUT_A, linewidths=0)


def _poche_disk(ax, rad, face=GRAY_LIGHT, alpha=0.55, hatch=None, lw=0.0):
    c = plt.Circle(
        (0, 0),
        rad,
        facecolor=face,
        edgecolor="none" if lw == 0 else INK,
        lw=lw,
        hatch=hatch,
        alpha=alpha,
        zorder=0,
    )
    ax.add_patch(c)


def _poche_poly(ax, xs, ys, face=GRAY, alpha=0.28, hatch=None, lw=0.0):
    ax.fill(xs, ys, facecolor=face, edgecolor="none" if lw == 0 else INK, lw=lw, hatch=hatch, alpha=alpha, zorder=1)


def _poche_semidisk(ax, rad, face=GRAY, alpha=0.28, hatch=None):
    phi = np.linspace(0, PI, 180)
    xs = np.concatenate([[-rad], rad * np.cos(phi), [rad]])
    ys = np.concatenate([[0], rad * np.sin(phi), [0]])
    _poche_poly(ax, xs, ys, face=face, alpha=alpha, hatch=hatch)


def drawing_two_processes() -> None:
    """Overlay process A (n-count) and process B (φ/Φ) on the same drawings."""
    tt = np.linspace(0, 2 * PI, 360)
    nA, thA, rA, xA, yA, zA = count_process()
    nB, thB, rB, xB, yB, zB = phi_process()

    write_csv(
        DATA / "two_processes.csv",
        ["n", "count_radius", "count_half_walk", "phi_radius_in", "phi_diameter_in", "phi_diameter_out"],
        [
            (
                n,
                n / 2.0,
                n * PI / 2.0,
                RADIUS * (INV_PHI ** (n - 1)),
                INV_PHI ** (n - 1),
                PHI ** (n - 1),
            )
            for n in NS
        ],
    )

    # Paper circle + interiors from both processes
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.3))
    ax = axes[0]
    _poche_disk(ax, RADIUS, face=GRAY_LIGHT, alpha=0.45)
    _poche_disk(ax, RADIUS * INV_PHI, face=GRAY, alpha=0.22, hatch=HATCH_OVER)
    _circle(ax, RADIUS, NAVY, 2.2)
    ax.plot([-RADIUS, RADIUS], [0, 0], color=RED, lw=2.0)
    ax.axvline(0, color=CUT, ls=LS_CUT, alpha=CUT_A, lw=1.0)
    ax.plot(RADIUS * np.cos(np.linspace(0, PI, 160)),
            RADIUS * np.sin(np.linspace(0, PI, 160)), color=ORANGE, lw=2.2)
    ax.scatter([0], [0], c=RED, s=28, zorder=6)
    ax.scatter([-RADIUS + INV_PHI], [0], c=GOLD, s=40, zorder=6)
    ax.scatter([-RADIUS + INV_PHI ** 2], [0], c=GOLD, s=40, zorder=6)
    ax.scatter([-RADIUS + INV_PI], [0], c=ORANGE, s=22, zorder=5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"paper  ·  $1/2$ midline  ·  $\Phi,\Phi^{2}$  ·  half-walk")

    ax = axes[1]
    _circle(ax, RADIUS, NAVY, 2.0)
    ax.plot([-RADIUS, RADIUS], [0, 0], color=RED, lw=1.5)
    ax.axvline(0, color=CUT, ls=LS_CUT, alpha=CUT_A, lw=0.8)
    ax.plot(xB, yB, color=GOLD, lw=1.6)
    for n in range(1, 7):
        _circle(ax, RADIUS * (INV_PHI ** (n - 1)), NAVY, 0.6, 0.45)
    _ngon(ax, RADIUS, 5, BLUE, 0.9)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"paper  ·  process B inward + 5-split")
    fig.suptitle("Two processes on the paper circle")
    fig.tight_layout()
    _save(fig, "layer_both_01_paper.png")

    # Local interiors: A = n-gon + half-walk on diameter n; B = Φ marks + inward copy
    fig, axes = plt.subplots(2, 4, figsize=(12.4, 6.4))
    shown = [1, 2, 3, 4, 5, 6, 8, 13]
    for ax, n in zip(axes.ravel(), shown):
        rr = n / 2.0
        _circle(ax, rr, NAVY, 1.4)
        ax.plot(rr * np.cos(np.linspace(0, PI, 140)),
                rr * np.sin(np.linspace(0, PI, 140)), color=ORANGE, lw=1.8)
        ax.plot([-rr, rr], [0, 0], color=RED, lw=1.3)
        ax.axvline(0, color=CUT, ls=LS_CUT, alpha=CUT_A, lw=0.7)
        ax.scatter([0], [0], c=RED, s=12, zorder=5)
        ax.scatter([-rr + n * INV_PHI], [0], c=GOLD, s=22, zorder=6)
        ax.scatter([-rr + n * INV_PHI ** 2], [0], c=GOLD, s=16, zorder=5)
        _ngon(ax, rr, n, BLUE, 0.85)
        _circle(ax, rr * INV_PHI, GOLD, 1.0, 0.85)
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(rf"$n={n}$", fontsize=9)
    fig.suptitle(r"Two processes  ·  $n$-gon and half-walk (A)  ·  $\Phi$ pair and inward copy (B)")
    fig.tight_layout()
    _save(fig, "layer_both_02_interiors.png")

    # Plan overlay
    fig, ax = plt.subplots(figsize=(7.6, 7.6))
    ax.plot(xA, yA, color=NAVY, lw=1.25, label="A  n-count out")
    ax.plot(xB, yB, color=GOLD, lw=1.7, label=r"B  in-count, scale $\Phi$")
    for k in NS:
        _circle(ax, k / 2.0, ORANGE, 0.35, 0.35)
    for k in FIB:
        if k <= N_MAX:
            _circle(ax, k / 2.0, RED, 0.7, 0.7)
    ax.axvline(0, color=CUT, ls=LS_CUT, alpha=CUT_A, lw=0.8)
    ax.set_aspect("equal")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_title(r"Plan  ·  A out  ·  B opposite from arrival  ·  red = Fibonacci $n$")
    _save(fig, "layer_both_03_plan.png")

    # Obliques
    fig = plt.figure(figsize=(12.6, 8.4))
    views = [(18, -50), (22, 30), (8, 88), (46, -24)]
    titles = ["from the paper start", "three-quarter", "side", "over the interiors"]
    for i, ((elev, azim), title) in enumerate(zip(views, titles)):
        ax = fig.add_subplot(2, 2, i + 1, projection="3d")
        ax.plot(xA, yA, zA, color=NAVY, lw=0.95)
        ax.plot(xB, yB, zB, color=GOLD, lw=1.35)
        for k in FIB + [16]:
            if k > N_MAX:
                continue
            rk = k / 2.0
            zk = zA[np.argmin(np.abs(nA - k))]
            ax.plot(rk * np.cos(tt), rk * np.sin(tt), np.full_like(tt, zk),
                    color=ORANGE, lw=0.45, alpha=0.45)
        ax.view_init(elev, azim)
        ax.set_title(title, fontsize=9)
        ax.tick_params(labelsize=5)
    fig.suptitle(r"Obliques  ·  A up  ·  B in-count from arrival, opposite way, scale $\Phi$")
    fig.tight_layout()
    _save(fig, "layer_both_04_obliques.png")

    fig = plt.figure(figsize=(7.6, 6.8))
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    ax.plot(xA, yA, zA, color=NAVY, lw=1.15, label="A")
    ax.plot(xB, yB, zB, color=GOLD, lw=1.5, label="B")
    ax.plot(0.5 * np.cos(tt), 0.5 * np.sin(tt), np.zeros_like(tt), color=RED, lw=1.0, alpha=0.6)
    ax.view_init(18, -46)
    ax.set_title(r"Oblique  ·  A walked up  ·  B walked down from arrival")
    ax.tick_params(labelsize=6)
    fig.tight_layout()
    _save(fig, "layer_both_05_oblique.png")


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def write_csv(path: Path, header, rows) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in rows:
            w.writerow(row)


def export_all_csv() -> None:
    rows = [row_for_n(n) for n in NS]
    keys = list(rows[0].keys())
    write_csv(DATA / "integer_table.csv", keys, ([r[k] for k in keys] for r in rows))

    x = np.linspace(0.0, 2.0, 401)
    other, am, gm = am_gm_fixed_sum(x, 2.0)
    write_csv(DATA / "amgm_sum2.csv", ["x", "other", "AM", "GM"], zip(x, other, am, gm))

    x01 = np.linspace(0.0, 1.0, 401)
    o1, a1, g1 = am_gm_fixed_sum(x01, 1.0)
    write_csv(DATA / "amgm_sum1.csv", ["x", "other", "AM", "GM"], zip(x01, o1, a1, g1))

    xin = np.linspace(0.04, 1.96, 401)
    ami, gmi = inverted_means_on_sum2(xin)
    write_csv(DATA / "amgm_sum2_inverted.csv", ["x", "AM_new", "GM_new"], zip(xin, ami, gmi))

    xs = np.linspace(0.2, 4.2, 401)
    write_csv(DATA / "inversion_curve.csv", ["x", "one_over_x"], zip(xs, 1.0 / xs))

    write_csv(
        DATA / "named_points.csv",
        ["name", "x", "y"],
        [
            ("unit_equal_parts", 1.0, 1.0),
            ("circle_parts_pi_invpi", PI, INV_PI),
            ("paper_half_walk", PI / 2.0, ""),
            ("n2_half_walk", PI, ""),
        ],
    )

    ns = np.linspace(1, N_MAX, 401)
    write_csv(
        DATA / "two_walks.csv",
        ["n", "inverse_walk_n", "interior_walk_1_over_n", "AM_pair", "GM_pair"],
        zip(ns, ns, 1.0 / ns, (ns + 1.0 / ns) / 2.0, np.ones_like(ns)),
    )

    n, th, r, x, y, z = spiral_curve()
    step = 5
    write_csv(
        DATA / "spiral.csv",
        ["n", "theta", "r", "x", "y", "arc"],
        zip(n[::step], th[::step], r[::step], x[::step], y[::step], z[::step]),
    )

    write_csv(
        DATA / "structure_constants.csv",
        ["symbol", "value", "meaning"],
        [
            ("diameter_paper", 1.0, "paper circle"),
            ("radius_paper", 0.5, "half the paper diameter"),
            ("pi", PI, "full walk of diameter 1; ratio of the two halves"),
            ("1/pi", INV_PI, "inverse part of the paper close"),
            ("pi * 1/pi", 1.0, "product of inverse parts"),
            ("GM(pi, 1/pi)", 1.0, "geometric mean of the parts"),
            ("pi/2", PI / 2.0, "half-walk at n=1"),
            ("cone_tan_alpha", 0.5, "r/n = 1/2"),
        ],
    )


def _save(fig: plt.Figure, name: str) -> None:
    fig.savefig(DRAW / name, dpi=145, bbox_inches="tight")
    plt.close(fig)


def drawing_amgm():
    x = np.linspace(0, 2, 500)
    _, am, gm = am_gm_fixed_sum(x, 2.0)
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.plot(x, am, color=CUT, lw=W_CUT, ls=LS_CUT, alpha=CUT_A, label="AM = 1")
    ax.plot(x, gm, color=INK, lw=W_FRONT, ls=LS_ARRIVED, label="GM")
    ax.fill_between(x, gm, am, facecolor=GRAY_LIGHT, edgecolor="none", linewidth=0.0, alpha=0.7)
    _lock(ax, 1, 1)
    ax.set_title("AM–GM on [0, 2]")
    ax.legend(fontsize=8)
    ax.grid(True)
    _save(fig, "drawing_01_amgm_sum2.png")

    x = np.linspace(0, 1, 500)
    _, am, gm = am_gm_fixed_sum(x, 1.0)
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.plot(x, am, color=CUT, lw=W_CUT, ls=LS_CUT, alpha=CUT_A, label="AM = 1/2")
    ax.plot(x, gm, color=INK, lw=W_FRONT, ls=LS_ARRIVED, label="GM")
    ax.fill_between(x, gm, am, facecolor=GRAY_LIGHT, edgecolor="none", linewidth=0.0, alpha=0.7)
    _lock(ax, 0.5, 0.5)
    ax.set_title("AM–GM on [0, 1]")
    ax.legend(fontsize=8)
    ax.grid(True)
    _save(fig, "drawing_02_amgm_sum1.png")


def drawing_inversion():
    x = np.linspace(0, 2, 400)
    _, am, gm = am_gm_fixed_sum(x, 2.0)
    xin = np.linspace(0.05, 1.95, 400)
    ami, gmi = inverted_means_on_sum2(xin)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4))
    axes[0].plot(x, am, color=CUT, lw=W_CUT, ls=LS_CUT, alpha=CUT_A)
    axes[0].plot(x, gm, color=INK, lw=W_FRONT)
    axes[0].fill_between(x, gm, am, facecolor=GRAY_LIGHT, edgecolor="none", alpha=0.7)
    _lock(axes[0], 1, 1)
    axes[0].set_title("Before")
    axes[1].plot(xin, ami, color=CUT, lw=W_CUT, ls=LS_CUT, alpha=CUT_A)
    axes[1].plot(xin, gmi, color=INK, lw=W_WALK, ls=LS_INVERT)
    _lock(axes[1], 1, 1)
    axes[1].set_ylim(0, 8)
    axes[1].set_title("After inversion")
    fig.suptitle("Inversion of the pair")
    fig.tight_layout()
    _save(fig, "drawing_03_inversion.png")


def drawing_paper_circle():
    th = np.linspace(0, 2 * PI, 400)
    fig, ax = plt.subplots(figsize=(5.4, 5.4))
    _poche_disk(ax, RADIUS, face=GRAY_LIGHT, alpha=0.55)
    ax.plot(RADIUS * np.cos(th), RADIUS * np.sin(th), color=INK, lw=W_FRONT)
    _midline(ax, RADIUS)
    _lock(ax, RADIUS, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Diameter 1. Close = one turn.")
    _save(fig, "drawing_04_circle.png")

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    _poche_disk(axes[0], RADIUS, face=GRAY_LIGHT, alpha=0.55)
    axes[0].plot(RADIUS * np.cos(th), RADIUS * np.sin(th), color=INK, lw=W_FRONT)
    _midline(axes[0], RADIUS)
    axes[0].text(0.04, 0.04, "1", ha="left", fontsize=9)
    axes[0].set_aspect("equal")
    axes[0].axis("off")
    axes[0].set_title("Whole = 1")
    xs = np.linspace(0.22, 4.1, 300)
    axes[1].plot(xs, 1 / xs, color=INK, lw=W_WALK, ls=LS_INVERT)
    axes[1].axhline(1, color=CUT, lw=W_CUT, ls=LS_CUT, alpha=CUT_A)
    axes[1].axvline(1, color=GRAY, lw=W_HAIR, ls=LS_CUT)
    _lock(axes[1], 1, 1)
    axes[1].scatter([PI], [INV_PI], facecolors="none", edgecolors=INK, s=36, lw=0.7, zorder=5)
    axes[1].set_title(r"Parts $(\pi,\,1/\pi)$")
    axes[1].grid(True)
    fig.suptitle("Inverse parts of the close")
    fig.tight_layout()
    _save(fig, "drawing_05_parts.png")

    fig, ax = plt.subplots(figsize=(5.6, 5.8))
    _poche_disk(ax, RADIUS, face=GRAY_LIGHT, alpha=0.45)
    _poche_semidisk(ax, RADIUS, face=GRAY, alpha=0.30)
    ax.plot(RADIUS * np.cos(th), RADIUS * np.sin(th), color=INK, lw=W_FRONT)
    phi = np.linspace(0, PI, 200)
    ax.plot(RADIUS * np.cos(phi), RADIUS * np.sin(phi), color=INK, lw=W_WALK)
    _midline(ax, RADIUS)
    ax.text(0, -0.16, "1/2", ha="center", fontsize=9)
    ax.text(0, RADIUS + 0.08, r"$\pi/2$", ha="center", fontsize=9)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Two halves")
    _save(fig, "drawing_06_two_halves.png")


def drawing_walks():
    ns = np.linspace(1, 16, 300)
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.6))
    axes[0].plot(ns, ns, color=INK, lw=W_WALK, label="n")
    axes[0].plot(ns, 1 / ns, color=INK, lw=W_WALK, ls=LS_INVERT, label="1/n")
    axes[0].axhline(1, color=CUT, ls=LS_CUT, lw=W_CUT, alpha=CUT_A, label="common ratio 1")
    axes[0].set_title("Two walks inverted through 1")
    axes[0].legend(fontsize=8); axes[0].grid(True, alpha=0.28)
    axes[1].plot(ns, (ns + 1 / ns) / 2, color=INK, lw=W_WALK, label="AM")
    axes[1].plot(ns, np.ones_like(ns), color=CUT, lw=W_CUT, ls=LS_CUT, alpha=CUT_A, label="GM = 1")
    axes[1].fill_between(ns, 1.0, (ns + 1 / ns) / 2, facecolor=GRAY_LIGHT, edgecolor="none", linewidth=0.0, alpha=0.7)
    axes[1].set_title("Every integer shares GM = 1")
    axes[1].legend(fontsize=8); axes[1].grid(True, alpha=0.28)
    fig.suptitle("Drawing 8  ·  AM and GM as separate walks")
    fig.tight_layout()
    _save(fig, "drawing_08_two_walks.png")


def drawing_half_walk_grid():
    shown = [1, 2, 3, 4, 6, 8]
    fig, axes = plt.subplots(2, 3, figsize=(11.6, 7.8))
    tt = np.linspace(0, 2 * PI, 240)
    semi = np.linspace(0, PI, 160)
    for ax, n in zip(axes.ravel(), shown):
        r = n / 2
        ax.plot(r * np.cos(tt), r * np.sin(tt), color=NAVY, lw=1.5)
        ax.plot(r * np.cos(semi), r * np.sin(semi), color=ORANGE, lw=2.8)
        ax.plot([-r, r], [0, 0], color=RED, lw=1.8)
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(rf"$n={n}$   $n\pi/2={n}\pi/2$", fontsize=9)
    fig.suptitle("Drawing 9  ·  half the local walk at each integer")
    fig.tight_layout()
    _save(fig, "drawing_09_half_walk.png")


def drawing_spiral():
    n, th, r, x, y, z = spiral_curve()
    tt = np.linspace(0, 2 * PI, 200)
    fig = plt.figure(figsize=(12.8, 6.6))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    m = n <= 1.0001
    ax.plot(x[m], y[m], z[m], color=NAVY, lw=2)
    ax.plot(0.5 * np.cos(tt), 0.5 * np.sin(tt), np.zeros_like(tt), color=ORANGE, lw=0.8, alpha=0.6)
    ax.plot([-0.5, 0.5], [0, 0], [0, 0], color=RED, lw=1.5)
    ax.view_init(18, -48)
    ax.set_title("paper start")
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    ax.plot(x, y, z, color=NAVY, lw=1.0)
    for k in (1, 2, 4, 8, 16):
        rr = k / 2
        zk = z[np.argmin(np.abs(n - k))]
        ax.plot(rr * np.cos(tt), rr * np.sin(tt), np.full_like(tt, zk), color=ORANGE, lw=0.7, alpha=0.55)
    ax.view_init(16, -48)
    ax.set_title("same line growing")
    fig.suptitle("Drawing 10  ·  paper helix, then growth")
    fig.tight_layout()
    _save(fig, "drawing_10_spiral.png")

    fig, ax = plt.subplots(figsize=(7.6, 7.6))
    ax.plot(x, y, color=NAVY, lw=1.4)
    for k in NS:
        rr = k / 2
        ax.plot(rr * np.cos(tt), rr * np.sin(tt), color=ORANGE, lw=0.5, alpha=0.55)
        if k >= 2:
            a = 2 * PI * np.arange(k + 1) / k
            ax.plot(rr * np.cos(a), rr * np.sin(a), color=RED, lw=0.6, alpha=0.75)
    ax.set_aspect("equal")
    ax.set_title("Drawing 11  ·  spiral + local circles + n-gons")
    _save(fig, "drawing_11_plan_overlay.png")


def drawing_integer_unit():
    fig, axes = plt.subplots(2, 4, figsize=(11.4, 5.8))
    shown = [1, 2, 3, 4, 5, 6, 8, 16]
    tt = np.linspace(0, 2 * PI, 200)
    for ax, n in zip(axes.ravel(), shown):
        ax.plot(np.cos(tt), np.sin(tt), color=NAVY, lw=1.2)
        ax.plot([-1, 1], [0, 0], color=RED, lw=1.1)
        if n >= 2:
            a = 2 * PI * np.arange(n + 1) / n
            ax.plot(np.cos(a), np.sin(a), color=ORANGE, lw=1.1)
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(rf"$n={n}$,  $1/n={1/n:.4g}$", fontsize=8)
    fig.suptitle("Drawing 7  ·  integer split of the unit circle (diameter held at 1)")
    fig.tight_layout()
    _save(fig, "drawing_07_integer_n.png")


def drawing_obliques():
    n, th, r, x, y, z = spiral_curve()
    tt = np.linspace(0, 2 * PI, 180)
    fig = plt.figure(figsize=(12.6, 8.4))
    views = [(16, -50), (20, 30), (10, 88), (26, 150), (8, -12), (48, -28)]
    titles = ["from the paper start", "three-quarter", "side",
              "from n=16", "along the walk", "over the interiors"]
    for i, ((elev, azim), title) in enumerate(zip(views, titles)):
        ax = fig.add_subplot(2, 3, i + 1, projection="3d")
        ax.plot(x, y, z, color=NAVY, lw=0.9)
        for k in (1, 2, 4, 8, 16):
            rr = k / 2
            zk = z[np.argmin(np.abs(n - k))]
            ax.plot(rr * np.cos(tt), rr * np.sin(tt), np.full_like(tt, zk),
                    color=ORANGE, lw=0.55, alpha=0.55)
        ax.view_init(elev, azim)
        ax.set_title(title, fontsize=8)
        ax.tick_params(labelsize=5)
    fig.suptitle("Drawing 13  ·  obliques of the continuous line")
    fig.tight_layout()
    _save(fig, "drawing_13_obliques.png")


def drawing_triangles():
    fig, axes = plt.subplots(2, 2, figsize=(8.8, 8.6))

    def circle(ax, r):
        t = np.linspace(0, 2 * PI, 240)
        ax.plot(r * np.cos(t), r * np.sin(t), color=NAVY, lw=1.3)
        ax.plot([-r, r], [0, 0], color=RED, lw=1.5)
        ax.scatter([0], [0], c=RED, s=12, zorder=5)

    ax = axes[0, 0]
    r = 0.5
    circle(ax, r)
    ax.plot([-r, 0, r, -r], [0, r, 0, 0], color=ORANGE, lw=1.8)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"$n=1$  Thales", fontsize=9)

    ax = axes[0, 1]
    r = 1.5
    circle(ax, r)
    angs = [0, 2 * PI / 3, 4 * PI / 3, 0]
    ax.plot(r * np.cos(angs), r * np.sin(angs), color=ORANGE, lw=1.8)
    ax.plot([0, r], [0, 0], color=BLUE, lw=1.1)
    ax.plot([0, r * np.cos(2 * PI / 3)], [0, r * np.sin(2 * PI / 3)], color=BLUE, lw=1.1)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"$n=3$  spoke", fontsize=9)

    ax = axes[1, 0]
    r = 2
    circle(ax, r)
    angs = np.array([0, PI / 2, PI, 3 * PI / 2, 0])
    ax.plot(r * np.cos(angs), r * np.sin(angs), color=ORANGE, lw=1.8)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"$n=4$  $45^\circ$", fontsize=9)

    ax = axes[1, 1]
    r = 3
    circle(ax, r)
    angs = np.linspace(0, 2 * PI, 7)
    ax.plot(r * np.cos(angs), r * np.sin(angs), color=ORANGE, lw=1.8)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"$n=6$  equilateral", fontsize=9)

    fig.suptitle("Drawing 14  ·  solved triangles already in the template")
    fig.tight_layout()
    _save(fig, "drawing_14_triangles.png")


def drawing_cone():
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 6.4))
    for n in NS:
        r = n / 2
        axes[0].plot([-r, r], [n, n], color=RED, lw=1.0)
    axes[0].plot([0, -8], [0, 16], color=NAVY, lw=2)
    axes[0].plot([0, 8], [0, 16], color=NAVY, lw=2)
    axes[0].set_aspect("equal")
    axes[0].set_title("Elevation  ·  tan α = 1/2")
    axes[0].set_xlim(-9, 9); axes[0].set_ylim(-0.3, 17)
    axes[1].fill([-8, 0, 8], [16, 0, 16], color="#f4e1b5", alpha=0.5, edgecolor=NAVY, lw=2)
    for n in NS:
        r = n / 2
        axes[1].plot([-r, r], [n, n], color=RED, lw=0.9)
    axes[1].set_aspect("equal")
    axes[1].set_title("Vertical section")
    axes[1].set_xlim(-9, 9); axes[1].set_ylim(-0.3, 17)
    fig.suptitle("Drawing 12  ·  cone of growing diameters")
    fig.tight_layout()
    _save(fig, "drawing_12_cone.png")


def drawing_phi_layer() -> None:
    """Overlay 1/φ and φ on the existing set. New files only."""
    tt = np.linspace(0, 2 * PI, 400)
    write_csv(
        DATA / "phi_layer.csv",
        ["symbol", "value", "meaning"],
        [
            ("phi", PHI, "1 + 1/phi"),
            ("1/phi", INV_PHI, "unique x in (0,1) with 1/x = 1+x"),
            ("phi * 1/phi", 1.0, "inversion through the unit"),
            ("GM(phi, 1/phi)", 1.0, "same hinge as (n,1/n) and (pi,1/pi)"),
            ("AM(phi, 1/phi)", (PHI + INV_PHI) / 2.0, "sqrt(5)/2"),
            ("1/phi^2", INV_PHI * INV_PHI, "smaller part of the unit golden cut"),
        ],
    )

    # L1 — paper circle + unit diameter: even cut and golden cut
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0))
    ax = axes[0]
    ax.plot([-0.5, 0.5], [0, 0], color=RED, lw=2.2)
    ax.plot(0.5 * np.cos(tt), 0.5 * np.sin(tt), color=NAVY, lw=2.0)
    ax.plot([0], [0], "o", color=NAVY, ms=4)
    # half mark and golden mark on diameter [-0.5, 0.5], unit parameter t in [0,1]
    # point at fraction f from left endpoint: x = -0.5 + f
    ax.scatter([-0.5 + 0.5], [0], c=RED, s=36, zorder=5)
    ax.scatter([-0.5 + INV_PHI], [0], c=GOLD, s=42, zorder=6)
    ax.scatter([-0.5 + INV_PHI * INV_PHI], [0], c=ORANGE, s=28, zorder=5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"paper circle  ·  $1/2$ and $1/\varphi$ on the same diameter")

    ax = axes[1]
    xs = np.linspace(0.22, 3.4, 400)
    ax.plot(xs, 1.0 / xs, color=BLUE, lw=1.8)
    ax.axhline(1, color=RED, ls="--", lw=0.8)
    ax.axvline(1, color=RED, ls="--", lw=0.8)
    ax.scatter([1], [1], c=RED, s=40, zorder=5, label="(1,1)")
    ax.scatter([2], [0.5], c=NAVY, s=36, zorder=5, label=r"$(2,1/2)$")
    ax.scatter([PI], [INV_PI], c=ORANGE, s=36, zorder=5, label=r"$(\pi,1/\pi)$")
    ax.scatter([PHI], [INV_PHI], c=GOLD, s=50, zorder=6, label=r"$(\varphi,1/\varphi)$")
    ax.set_xlim(0.2, 3.5); ax.set_ylim(0.15, 2.4)
    ax.set_aspect("equal")
    ax.legend(fontsize=8)
    ax.set_title(r"same inversion $xy=1$")
    fig.suptitle("Layer  ·  $1/\\varphi$ on the paper close and on the inversion")
    fig.tight_layout()
    _save(fig, "layer_phi_01_paper_and_inversion.png")

    # L2 — local diameters n = 1..8 with golden mark (scale is ratio)
    shown = [1, 2, 3, 4, 5, 6, 8]
    fig, axes = plt.subplots(2, 4, figsize=(11.6, 6.0))
    axes = axes.ravel()
    for ax, n in zip(axes, shown):
        r = n / 2.0
        ax.plot(r * np.cos(tt), r * np.sin(tt), color=NAVY, lw=1.4)
        ax.plot([-r, r], [0, 0], color=RED, lw=1.5)
        ax.scatter([0], [0], c=NAVY, s=8, zorder=5)
        ax.scatter([0], [0], c=RED, s=6)
        # marks from left endpoint of diameter
        ax.scatter([-r + n * 0.5], [0], c=RED, s=18, zorder=5)          # midpoint = even cut
        ax.scatter([-r + n * INV_PHI], [0], c=GOLD, s=26, zorder=6)     # golden
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(rf"$n={n}$", fontsize=9)
    axes[-1].axis("off")
    axes[-1].text(0.5, 0.5, r"gold $=n/\varphi$""\n" r"red mid $=n/2$",
                  ha="center", va="center", fontsize=9, transform=axes[-1].transAxes)
    fig.suptitle(r"Layer  ·  same two cuts on every local diameter")
    fig.tight_layout()
    _save(fig, "layer_phi_02_local_diameters.png")

    # L3 — plan spiral already built, plus golden marks on each integer diameter
    n, th, r, x, y, z = spiral_curve()
    fig, ax = plt.subplots(figsize=(7.6, 7.6))
    ax.plot(x, y, color=NAVY, lw=1.3)
    for k in NS:
        rr = k / 2.0
        ax.plot(rr * np.cos(tt), rr * np.sin(tt), color=ORANGE, lw=0.45, alpha=0.5)
        ax.plot([-rr, rr], [0, 0], color=RED, lw=0.5, alpha=0.35)
        ax.scatter([-rr + k * INV_PHI], [0], c=GOLD, s=12, zorder=6)
    ax.set_aspect("equal")
    ax.set_title(r"Layer  ·  $n$-spiral with $n/\varphi$ on each diameter")
    _save(fig, "layer_phi_03_spiral_plan.png")

    # L4 — inward similar copies on the paper circle (finite arrivals)
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    rad = 0.5
    for i in range(7):
        ax.plot(rad * np.cos(tt), rad * np.sin(tt), color=NAVY, lw=1.6 - 0.15 * i, alpha=0.95 - 0.08 * i)
        ax.plot([-rad, rad], [0, 0], color=RED, lw=1.0, alpha=0.55)
        ax.scatter([-rad + 2 * rad * INV_PHI], [0], c=GOLD, s=22, zorder=5)
        rad *= INV_PHI
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"Layer  ·  inward copies of the paper circle, scale $1/\varphi$")
    _save(fig, "layer_phi_04_inward_paper.png")

    # L5 — two walks with phi pair marked
    ns = np.arange(1, N_MAX + 1)
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(ns, ns, color=NAVY, lw=1.8, label=r"inverse walk $n$")
    ax.plot(ns, 1.0 / ns, color=ORANGE, lw=1.8, label=r"interior walk $1/n$")
    ax.axhline(1, color=RED, ls="--", lw=1.0, label="unit")
    ax.axhline(PHI, color=GOLD, ls=":", lw=1.2, label=r"$\varphi$")
    ax.axhline(INV_PHI, color=GOLD, ls=":", lw=1.2)
    ax.scatter([PHI], [INV_PHI], c=GOLD, s=50, zorder=6)
    ax.set_xlim(1, 16); ax.set_ylim(0, 8)
    ax.legend(fontsize=8)
    ax.set_xlabel("n")
    ax.set_title(r"Layer  ·  two walks, with $(\varphi,1/\varphi)$ as a fixed inversion")
    ax.grid(True, alpha=0.28)
    _save(fig, "layer_phi_05_two_walks.png")

    # L6 — paper circle interiors
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2))
    ax = axes[0]
    r = 0.5
    ax.plot(r * np.cos(tt), r * np.sin(tt), color=NAVY, lw=2.2)
    ax.plot([-r, r], [0, 0], color=RED, lw=2.0)
    ax.plot(r * np.cos(np.linspace(0, PI, 180)), r * np.sin(np.linspace(0, PI, 180)),
            color=ORANGE, lw=2.4)
    ax.plot([0, 0], [0, r], color=ORANGE, lw=1.1, ls="--")
    ax.scatter([-r + 0.5], [0], c=RED, s=34, zorder=5)
    ax.scatter([-r + INV_PHI], [0], c=GOLD, s=44, zorder=6)
    ax.scatter([-r + INV_PHI ** 2], [0], c=GOLD, s=22, zorder=5)
    ax.scatter([-r + INV_PI], [0], c=ORANGE, s=28, zorder=5)
    ax.scatter([0], [r], c=ORANGE, s=22, zorder=5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"paper interior  ·  $1/2$, $1/\varphi$, $1/\varphi^{2}$, $1/\pi$, half-walk")

    ax = axes[1]
    r = 0.5
    ax.plot(r * np.cos(tt), r * np.sin(tt), color=NAVY, lw=2.0)
    ax.plot([-r, r], [0, 0], color=RED, lw=1.6)
    rr = r
    for i in range(6):
        ax.plot(rr * np.cos(tt), rr * np.sin(tt), color=NAVY, lw=1.1, alpha=0.8)
        ax.scatter([-rr + 2 * rr * INV_PHI], [0], c=GOLD, s=16, zorder=5)
        rr *= INV_PHI
    a = 2 * PI * np.arange(6) / 5
    ax.plot(r * np.cos(a), r * np.sin(a), color=BLUE, lw=0.9, alpha=0.75)
    for ang in a[:-1]:
        ax.plot([0, r * np.cos(ang)], [0, r * np.sin(ang)], color=BLUE, lw=0.6, alpha=0.55)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"paper interior  ·  inward $1/\varphi$ copies + 5-split")
    fig.suptitle("Layer  ·  paper circle interiors")
    fig.tight_layout()
    _save(fig, "layer_phi_06_paper_interiors.png")

    # L7 — local interiors
    fig, axes = plt.subplots(1, 4, figsize=(12.4, 3.6))
    for ax, n in zip(axes, (1, 2, 3, 5)):
        rr = n / 2.0
        ax.plot(rr * np.cos(tt), rr * np.sin(tt), color=NAVY, lw=1.5)
        ax.plot(rr * np.cos(np.linspace(0, PI, 160)),
                rr * np.sin(np.linspace(0, PI, 160)), color=ORANGE, lw=2.2)
        ax.plot([-rr, rr], [0, 0], color=RED, lw=1.5)
        ax.scatter([-rr + n * 0.5], [0], c=RED, s=22, zorder=5)
        ax.scatter([-rr + n * INV_PHI], [0], c=GOLD, s=30, zorder=6)
        if n >= 3:
            a = 2 * PI * np.arange(n + 1) / n
            ax.plot(rr * np.cos(a), rr * np.sin(a), color=BLUE, lw=0.9)
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(rf"$n={n}$", fontsize=9)
    fig.suptitle(r"Layer  ·  local interiors: $n$-gon, half-walk, $n/\varphi$")
    fig.tight_layout()
    _save(fig, "layer_phi_07_local_interiors.png")

    # L8 — 3D obliques
    n, th, r, x, y, z = spiral_curve()
    fig = plt.figure(figsize=(12.6, 8.4))
    views = [(16, -50), (22, 28), (10, 88), (48, -28)]
    titles = ["from the paper start", "three-quarter", "side", "over the interiors"]
    for i, ((elev, azim), title) in enumerate(zip(views, titles)):
        ax = fig.add_subplot(2, 2, i + 1, projection="3d")
        ax.plot(x, y, z, color=NAVY, lw=0.9)
        for k in NS:
            rk = k / 2.0
            zk = z[np.argmin(np.abs(n - k))]
            ax.plot(rk * np.cos(tt), rk * np.sin(tt), np.full_like(tt, zk),
                    color=ORANGE, lw=0.45, alpha=0.45)
            gx = -rk + k * INV_PHI
            ax.scatter([gx], [0], [zk], c=GOLD, s=12, zorder=6)
        ax.view_init(elev, azim)
        ax.set_title(title, fontsize=9)
        ax.tick_params(labelsize=5)
    fig.suptitle(r"Layer  ·  obliques  ·  gold $=n/\varphi$ at each integer freeze")
    fig.tight_layout()
    _save(fig, "layer_phi_08_obliques.png")

    fig = plt.figure(figsize=(7.4, 6.6))
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    ax.plot(x, y, z, color=NAVY, lw=1.15)
    for k in (1, 2, 3, 5, 8, 13, 16):
        rk = k / 2.0
        zk = z[np.argmin(np.abs(n - k))]
        ax.plot(rk * np.cos(tt), rk * np.sin(tt), np.full_like(tt, zk),
                color=ORANGE, lw=0.7, alpha=0.55)
        gx = -rk + k * INV_PHI
        ax.scatter([gx], [0], [zk], c=GOLD, s=22, zorder=6)
        ax.plot([-rk, rk], [0, 0], [zk, zk], color=RED, lw=0.7, alpha=0.45)
    ax.view_init(18, -46)
    ax.set_title(r"Layer  ·  oblique  ·  walk + freezes + $n/\varphi$")
    ax.tick_params(labelsize=6)
    fig.tight_layout()
    _save(fig, "layer_phi_09_oblique.png")


def drawing_n5_meetings() -> None:
    """n=5: A's spokes compute B. Diagonals, Phi copies, midline."""
    R = 2.5
    tt = np.linspace(0, 2 * PI, 400)
    angs = 2 * PI * np.arange(6) / 5
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.6))
    ax = axes[0]
    ax.plot(R * np.cos(tt), R * np.sin(tt), color=NAVY, lw=2.0)
    ax.plot([-R, R], [0, 0], color=RED, lw=1.6)
    ax.axvline(0, color=CUT, ls=LS_CUT, alpha=CUT_A, lw=0.8)
    ax.plot(R * np.cos(np.linspace(0, PI, 160)),
            R * np.sin(np.linspace(0, PI, 160)), color=ORANGE, lw=2.0)
    for k in range(5):
        ax.plot([0, R * np.cos(2 * PI * k / 5)],
                [0, R * np.sin(2 * PI * k / 5)], color=BLUE, lw=0.7, alpha=0.7)
    ax.plot(R * np.cos(angs), R * np.sin(angs), color=BLUE, lw=1.4)
    for i in range(5):
        j = (i + 2) % 5
        ax.plot([R * np.cos(2 * PI * i / 5), R * np.cos(2 * PI * j / 5)],
                [R * np.sin(2 * PI * i / 5), R * np.sin(2 * PI * j / 5)],
                color=GOLD, lw=1.0, alpha=0.85)
    ax.scatter([0], [0], c=RED, s=22, zorder=5)
    ax.scatter([R * (2 * INV_PHI - 1)], [0], c=GOLD, s=28, zorder=6)
    ax.scatter([R * (2 * INV_PHI ** 2 - 1)], [0], c=GOLD, s=28, zorder=6)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"$n=5$  ·  spokes of A  ·  diagonals  ·  $\Phi,\Phi^{2}$")

    ax = axes[1]
    ax.plot(R * np.cos(tt), R * np.sin(tt), color=NAVY, lw=2.0)
    ax.plot([-R, R], [0, 0], color=RED, lw=1.4)
    ax.axvline(0, color=CUT, ls=LS_CUT, alpha=CUT_A, lw=0.8)
    ax.plot(R * np.cos(angs), R * np.sin(angs), color=BLUE, lw=1.3)
    for i in range(5):
        j = (i + 2) % 5
        ax.plot([R * np.cos(2 * PI * i / 5), R * np.cos(2 * PI * j / 5)],
                [R * np.sin(2 * PI * i / 5), R * np.sin(2 * PI * j / 5)],
                color=GOLD, lw=1.05)
    rin = R * INV_PHI ** 2
    r1 = R * INV_PHI
    ax.plot(rin * np.cos(tt), rin * np.sin(tt), color=ORANGE, lw=1.2, ls="--")
    ax.plot(r1 * np.cos(tt), r1 * np.sin(tt), color=GOLD, lw=1.4)
    ax.scatter([0], [0], c=RED, s=22, zorder=5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"inner pentagon $R\Phi^{2}$  ·  first inward copy $R\Phi$")
    fig.suptitle(r"$n=5$: A's 5-split computes B")
    fig.tight_layout()
    _save(fig, "layer_n5_meetings.png")


def drawing_appendix_d() -> None:
    """Appendix D: where 1 is. Infinity inside the unit. HERE / THERE."""
    # D1 — (0,1) already endless
    fig, ax = plt.subplots(figsize=(10.2, 2.6))
    ax.plot([0, 1], [0, 0], color=INK, lw=W_FRONT, solid_capstyle="butt")
    ax.scatter([0, 1], [0, 0], c=INK, s=W_MARK, zorder=5)
    ax.text(0, 0.12, r"$0$", ha="center", fontsize=10)
    ax.text(1, 0.12, r"$1$", ha="center", fontsize=10)
    _lock(ax, 0.5, 0)
    ax.text(0.5, 0.12, r"$1/2$", ha="center", color=CUT, fontsize=10)
    pts = [0.25, 0.75, 0.125, 0.375, 0.625, 0.875]
    ax.scatter(pts, [0] * len(pts), c=INK, s=10, zorder=4)
    more = np.linspace(0.05, 0.95, 17)
    ax.scatter(more, np.zeros_like(more), c=GRAY, s=4, alpha=0.45, zorder=3)
    ax.text(0.5, -0.28, r"the endless is already interior to the unit", ha="center", fontsize=9, color=NAVY)
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.45, 0.35)
    ax.axis("off")
    ax.set_title(r"$D1$  ·  between $0$ and $1$ the marks do not finish")
    fig.tight_layout()
    _save(fig, "layer_d01_interior_endless.png")

    # D2 — HERE / THERE
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    th = np.linspace(0, 2 * PI, 400)
    _poche_disk(ax, 1.0, face=GRAY_LIGHT, alpha=0.50)
    ax.plot(np.cos(th), np.sin(th), color=INK, lw=W_FRONT)
    ax.plot([-1, 1], [0, 0], color=INK, lw=W_WALK)
    ax.axvline(0, color=CUT, ls=LS_CUT, lw=W_CUT, alpha=CUT_A)
    _lock(ax, 0, 0)
    ax.scatter([1], [0], c=INK, s=W_MARK, zorder=5)
    ax.scatter([-1], [0], facecolors="none", edgecolors=INK, s=22, lw=0.6, zorder=5)
    ax.annotate("", xy=(1, 0), xytext=(0.15, 0.55),
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.6))
    ax.text(0.22, 0.62, r"THERE  $=1$", color=INK, fontsize=10)
    ax.text(0.06, -0.22, r"HERE", color=INK, fontsize=10)
    ax.text(0, -1.28, r"arrive at THERE and you are HERE", ha="center", fontsize=10)
    ax.set_aspect("equal")
    ax.set_xlim(-1.35, 1.45)
    ax.set_ylim(-1.45, 1.35)
    ax.axis("off")
    ax.set_title(r"$D2$  ·  $1$ is THERE  ·  the pause is HERE")
    fig.tight_layout()
    _save(fig, "layer_d02_here_there.png")

    # D3 — every tick the same package
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.6))
    tt = np.linspace(0, 2 * PI, 300)
    for ax, n in zip(axes, (2, 8, 16)):
        R = n / 2.0
        _poche_disk(ax, R, face=GRAY_LIGHT, alpha=0.40)
        ax.plot(R * np.cos(tt), R * np.sin(tt), color=INK, lw=W_FRONT)
        ax.plot([-R, R], [0, 0], color=INK, lw=W_WALK)
        ax.axvline(0, color=CUT, ls=LS_CUT, lw=W_CUT, alpha=CUT_A)
        _lock(ax, 0, 0, s=16)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(r"$n=%d$" % n, fontsize=10)
    fig.suptitle(r"$D3$  ·  every tick is the same package  ·  labels change")
    fig.tight_layout()
    _save(fig, "layer_d03_every_tick.png")

    # D4 — 0 and infinity as poles of 1
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    th = np.linspace(0.12, 2 * PI - 0.12, 400)
    ax.plot(np.cos(th), np.sin(th), color=NAVY, lw=1.7)
    ax.plot([-1, 1], [0, 0], color=NAVY, lw=1.3)
    ax.scatter([1], [0], c=NAVY, s=44, zorder=6)
    ax.scatter([-1], [0], c=BLUE, s=28, zorder=5)
    ax.annotate("", xy=(1.55, 0.55), xytext=(1.08, 0.18),
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.3))
    ax.text(1.58, 0.62, r"$\infty$  THERE", color=ORANGE, fontsize=11)
    ax.text(-1.0, -0.28, r"$0$", ha="center", fontsize=11)
    ax.text(1.0, -0.28, r"$1$", ha="center", fontsize=11)
    ax.text(0, 1.18, r"$x\mapsto 1/x$", ha="center", color=BLUE, fontsize=10)
    ax.text(0, -1.32, r"infinity is the other pole of $1$, not a later integer", ha="center", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(-1.7, 2.15)
    ax.set_ylim(-1.5, 1.4)
    ax.axis("off")
    ax.set_title(r"$D4$  ·  $0\leftrightarrow\infty$ through the lock")
    fig.tight_layout()
    _save(fig, "layer_d04_poles.png")

    # D5 — zoom does not change the cut
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.2))
    windows = [(0.0, 1.0, r"$[0,1]$"), (0.0, 0.5, r"$[0,1/2]$"), (0.25, 0.5, r"$[1/4,1/2]$")]
    for ax, (a, b, lab) in zip(axes, windows):
        ax.plot([a, b], [0, 0], color=NAVY, lw=2.0)
        m = 0.5 * (a + b)
        ax.scatter([a, b], [0, 0], c=NAVY, s=28, zorder=5)
        ax.scatter([m], [0], c=RED, s=36, zorder=6)
        ax.text(m, 0.08, r"$1/2$", ha="center", color=RED, fontsize=9)
        ax.set_xlim(a - 0.06 * (b - a), b + 0.06 * (b - a))
        ax.set_ylim(-0.22, 0.22)
        ax.axis("off")
        ax.set_title(lab, fontsize=10)
    fig.suptitle(r"$D5$  ·  zoom is the same cut asked again")
    fig.tight_layout()
    _save(fig, "layer_d05_zoom.png")

    # D6 — inversion line: every tick the same, infinity not a last stop
    fig, ax = plt.subplots(figsize=(10.2, 3.6))
    xs = np.linspace(0.15, 6.0, 400)
    ax.plot(xs, 1.0 / xs, color=BLUE, lw=1.6)
    ax.axhline(1.0, color=NAVY, lw=0.8, ls=":")
    ax.axvline(1.0, color=NAVY, lw=0.8, ls=":")
    ax.axhline(0.5, color=CUT, lw=W_CUT, ls=LS_CUT, alpha=CUT_A)
    ax.scatter([1], [1], c=NAVY, s=40, zorder=5)
    ax.scatter([2], [0.5], c=ORANGE, s=28, zorder=5)
    ax.scatter([0.5], [2], c=ORANGE, s=28, zorder=5)
    ax.text(1.12, 1.12, r"$1$", fontsize=10)
    ax.text(2.12, 0.38, r"$2=1/(1/2)$", fontsize=9)
    ax.text(0.18, 2.12, r"$1/2$", fontsize=9)
    ax.set_xlim(0, 6.2)
    ax.set_ylim(0, 3.2)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$1/x$")
    ax.set_title(r"$D6$  ·  inversion through the lock  ·  no last index on the axis")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "layer_d06_inversion.png")


def drawing_finite_weight() -> None:
    """|D_16(1/2+it)| on the even cut. Finite object, not zeta."""
    N = 16

    def D(t):
        s = 0.5 + 1j * t
        acc = 0j
        for n in range(1, N + 1):
            acc += n ** (-s)
        return abs(acc)

    ts = np.linspace(0.2, 40.0, 1600)
    ys = np.array([D(t) for t in ts])
    fig, ax = plt.subplots(figsize=(10.4, 3.6))
    ax.plot(ts, ys, color=NAVY, lw=1.2)
    ax.set_xlabel(r"$t$")
    ax.set_ylabel(r"$|D_{16}(1/2+it)|$")
    ax.set_title(r"Finite interiors with a weight, $N=16$, even cut $\sigma=1/2$")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "layer_finite_D16.png")


def main() -> None:
    export_all_csv()
    drawing_amgm()
    drawing_inversion()
    drawing_paper_circle()
    drawing_integer_unit()
    drawing_walks()
    drawing_half_walk_grid()
    drawing_spiral()
    drawing_cone()
    drawing_obliques()
    drawing_triangles()
    drawing_phi_layer()
    drawing_two_processes()
    drawing_n5_meetings()
    drawing_finite_weight()
    drawing_appendix_d()
    print("CSV ->", DATA)
    print("drawings ->", DRAW)
    print("integers", NS)


if __name__ == "__main__":
    main()
