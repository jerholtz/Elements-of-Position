#!/usr/bin/env python3
"""
Elements of Position - Local Circle Models.py

Verification companion to Papers I, III, and IV.
Justin Erholtz

Three readings of one geometry, per Paper IV's own plan/section/elevation
split (Section "Street, unit, THERE": "Plan: the axis... Section: the
local circle... Elevation: inversion through 1").

  MODEL 1  Local circle      One n-gon at a time, built raw from the
                              master sequence: radius, spoke triangle,
                              chord, apothem, central angle, all measured.
                              Generalizes Paper III's n=5 worked example
                              (Section 3, "Solved triangles in the
                              five-disk") to any finished n.

  MODEL 2  Plan overlay      All local circles overlaid concentrically,
                              same center -- the flat nesting Paper III
                              describes ("Scale does not matter... inside
                              a circle of diameter 10000 there is a
                              similar five-disk").

  MODEL 3  Elevation stack   The same n-gons stacked by height n/2 instead
                              of flattened to one plane, so a vertical
                              section through the tower shows what plan
                              view alone hides.

Height convention for Model 3 is n/2, not arbitrary: Paper I's own cone
construction already lifts the own-origin to height n/2, forming the
45-45-90 triangle (0,0), (n,0), (n/2,n/2) (Paper I, "The closed unit").
That means the vertex line straight down the elevation stack (theta=0) IS
that triangle's hypotenuse, already proved there. The section cut at the
mid-edge angle traces the apothem (n/2)cos(pi/n), which converges onto
that same line as n grows -- a picture of the Archimedes squeeze
n sin(pi/n) < pi < n tan(pi/n) that Paper I cites in its literature
review ("What the literature already holds") but never draws.

All formulas here are elementary (school geometry, matching every paper's
own stated standard) and are checked against exact predictions by the
self-test at the end of every run -- see verify_findings().

Outputs (in ./local_circle_models/ next to this file):

    ngon_measurements.csv          raw run, one row per n, Model 1's math
    vertex_structure_sample.csv    full vertex enumeration for a few curated n
    model1_single/n{N}_ngon.png    one drawing per curated n
    model2_plan_overlay.png        all n-gons, concentric, one drawing
    model3_vertical_section.png    the Archimedes-squeeze convergence plot
    model3_elevation_stack.html    interactive 3D tower, orbit/zoom/hover

Usage:
    python "Elements of Position - Local Circle Models.py"
    python "Elements of Position - Local Circle Models.py" --nmax 2000 --stack-nmax 60
    python "Elements of Position - Local Circle Models.py" --height-mode half_walk
"""

from __future__ import annotations

import argparse
import csv
import math
from math import gcd
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from sympy import totient as sympy_totient

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

PI = math.pi
INK = "#161616"
HERE = "#8c4a56"
BLUE = "#2C3A42"
GRID = "#d4d4d4"
BG = "#FAFAF8"

HERE_DIR = Path(__file__).resolve().parent
OUT = HERE_DIR / "local_circle_models"


# =============================================================================
# Shared math -- the raw stock every model reads from
# =============================================================================
def ngon_vertices(n: int, r: float, closed: bool = True):
    """Vertex 0 sits at (r, 0) -- the wood/x-axis convention used throughout
    the drawings. theta_k = 2 pi k / n."""
    k = np.arange(n + 1 if closed else n)
    th = 2 * PI * k / n
    return r * np.cos(th), r * np.sin(th), th


def divisor_gon_of_vertex(n: int, k: int) -> int:
    """Vertex k of the n-gon belongs to the d-gon, d = n / gcd(n,k), for
    every proper divisor d of n. Smallest such d (other than n itself,
    k=0 excluded as trivial) says how 'reducible' that vertex is -- the
    same grammar as Paper II's 1/n = (1/a)(1/b), read geometrically."""
    if k == 0:
        return 1  # every n-gon shares its k=0 vertex with the "1-gon" (the point itself)
    g = gcd(n, k)
    return n // g


def ngon_measurements(n: int) -> dict:
    r = n / 2.0
    central = 2 * PI / n
    side = n * math.sin(PI / n)          # = 2 r sin(pi/n) -- Archimedes' INSCRIBED bound
    circumscribed = n * math.tan(PI / n)  # Archimedes' CIRCUMSCRIBED bound: n sin < pi < n tan
    apothem = r * math.cos(PI / n)
    base_angle = PI / 2.0 - PI / n        # base angles of the isosceles spoke triangle
    diag2 = n * math.sin(2 * PI / n)      # skip-one diagonal
    diag2_over_side = diag2 / side if side != 0 else float("nan")

    reducible = 0
    smallest_proper = n
    for k in range(1, n):
        d = divisor_gon_of_vertex(n, k)
        if d < n:
            reducible += 1
            smallest_proper = min(smallest_proper, d)
    is_irreducible_n = 1 if reducible == 0 else 0  # true iff n is prime (or 1)

    phi_n = int(sympy_totient(n))  # Euler's totient -- see note below

    return {
        "n": n,
        "radius": r,
        "central_angle_rad": central,
        "central_angle_deg": math.degrees(central),
        "side_chord": side,
        "circumscribed_side": circumscribed,
        "apothem": apothem,
        "spoke_base_angle_deg": math.degrees(base_angle),
        "diag2": diag2,
        "diag2_over_side": diag2_over_side,          # = 2 cos(pi/n)
        "apothem_over_radius": apothem / r,           # -> 1 as n grows: the squeeze
        "vertices_shared_with_smaller_dgon": reducible,
        "smallest_proper_divisor_gon": smallest_proper if reducible else n,
        "n_is_prime_like": is_irreducible_n,
        "euler_totient": phi_n,                       # phi(n): count of vertices coprime to n
        "predicted_shared_from_totient": (n - 1) - phi_n,  # exact identity, see verify_findings
    }


def vertex_structure_rows(n: int) -> list[dict]:
    rows = []
    for k in range(n):
        d = divisor_gon_of_vertex(n, k)
        rows.append({"n": n, "k": k, "angle_deg": math.degrees(2 * PI * k / n),
                     "shared_with_dgon": d, "is_new_to_n": 1 if d == n else 0})
    return rows


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.name}  ({len(rows)} rows)")


def style_ax(ax, equal=True):
    ax.set_facecolor(BG)
    if equal:
        ax.set_aspect("equal")
    ax.axis("off")


def save(fig, path: Path):
    fig.savefig(path, dpi=200, facecolor=BG, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    print("wrote", path.name)


# =============================================================================
# MODEL 1 -- local circle, one n-gon at a time
# =============================================================================
def draw_single_ngon(n: int, out: Path):
    m = ngon_measurements(n)
    r = m["radius"]
    xs, ys, th = ngon_vertices(n, r)

    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    style_ax(ax)

    tt = np.linspace(0, 2 * PI, 400)
    ax.plot(r * np.cos(tt), r * np.sin(tt), color=INK, lw=0.6, ls=(0, (2, 2)), alpha=0.55)

    ax.plot(xs, ys, color=INK, lw=1.5)
    ax.fill(xs, ys, color=INK, alpha=0.05)

    ax.plot([-r, r], [0, 0], color=HERE, lw=1.1, alpha=0.85)

    v0 = (xs[0], ys[0])
    v1 = (xs[1], ys[1])
    ax.plot([0, v0[0], v1[0], 0], [0, v0[1], v1[1], 0], color=HERE, lw=1.8)
    ax.scatter([0], [0], color=HERE, s=30, zorder=6)

    mx, my = (v0[0] + v1[0]) / 2.0, (v0[1] + v1[1]) / 2.0
    ax.plot([0, mx], [0, my], color=BLUE, lw=1.1, ls=(0, (3, 2)))
    ax.scatter([mx], [my], color=BLUE, s=18, zorder=6)

    ax.scatter(xs[:-1], ys[:-1], color=INK, s=14, zorder=5)

    label = (
        f"n = {n}\n"
        f"radius = n/2 = {r:.4f}\n"
        f"chord = n sin(pi/n) = {m['side_chord']:.4f}\n"
        f"apothem = (n/2)cos(pi/n) = {m['apothem']:.4f}\n"
        f"central angle = 2pi/n = {m['central_angle_deg']:.2f} deg\n"
        f"spoke base angle = {m['spoke_base_angle_deg']:.2f} deg"
    )
    ax.text(1.28 * r, 0.0, label, fontsize=9, fontfamily="monospace",
            color=INK, va="center", ha="left")

    lim = r * 2.6
    ax.set_xlim(-r * 1.3, lim)
    ax.set_ylim(-r * 1.35, r * 1.35)
    ax.set_title(f"Model 1  ·  local circle  ·  n = {n}", loc="left",
                 fontsize=11, fontfamily="serif", color=INK, pad=8)
    save(fig, out / f"n{n:03d}_ngon.png")
    return m


# =============================================================================
# MODEL 2 -- plan overlay, all n-gons concentric
# =============================================================================
def draw_plan_overlay(n_list: list[int], out: Path):
    fig, ax = plt.subplots(figsize=(9.5, 9.5))
    style_ax(ax)

    nmax = max(n_list)
    for n in n_list:
        r = n / 2.0
        xs, ys, _ = ngon_vertices(n, r)
        fade = 0.15 + 0.7 * (1.0 - n / nmax)
        lw = max(0.35, 1.4 * (1.0 - 0.55 * n / nmax))
        ax.plot(xs, ys, color=INK, lw=lw, alpha=min(1.0, fade + 0.15))

    n_top = nmax
    r_top = n_top / 2.0
    xs, ys, _ = ngon_vertices(n_top, r_top, closed=False)
    shared_x, shared_y, new_x, new_y = [], [], [], []
    for k in range(n_top):
        d = divisor_gon_of_vertex(n_top, k)
        (shared_x if d < n_top else new_x).append(xs[k])
        (shared_y if d < n_top else new_y).append(ys[k])
    ax.scatter(shared_x, shared_y, color=BLUE, s=22, zorder=6,
               label=f"shared with a smaller d | {n_top}")
    ax.scatter(new_x, new_y, color=HERE, s=22, zorder=6,
               label=f"new to {n_top} (irreducible)")

    ax.scatter([0], [0], color=HERE, s=30, zorder=7)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    lim = nmax / 2.0 * 1.12
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_title(f"Model 2  ·  plan overlay  ·  n = {min(n_list)}..{nmax}, concentric",
                 loc="left", fontsize=12, fontfamily="serif", color=INK, pad=10)
    save(fig, out / "model2_plan_overlay.png")


# =============================================================================
# MODEL 3 -- elevation stack + the vertical section
# =============================================================================
def height_of(n: float, mode: str) -> float:
    if mode == "n_half":
        return n / 2.0
    if mode == "half_walk":
        return n * PI / 2.0
    if mode == "n":
        return float(n)
    raise ValueError(mode)


def draw_vertical_section(nmax: int, height_mode: str, out: Path):
    """The picture Paper I never drew: the vertex line (proved, 45-45-90)
    and the apothem line converging onto it -- Archimedes' squeeze, in
    elevation."""
    ns = np.arange(3, nmax + 1)
    h = np.array([height_of(n, height_mode) for n in ns])
    vertex_x = ns / 2.0                                   # theta=0: exact, proved in I
    apothem_x = (ns / 2.0) * np.cos(PI / ns)               # mid-edge cut

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.0, 5.4))

    zmask = ns <= 30
    axL.set_facecolor(BG)
    for s in axL.spines.values():
        s.set_color("#c8c2b6")
    axL.tick_params(colors=INK, labelsize=8)
    axL.plot(h[zmask], vertex_x[zmask], color=HERE, lw=1.8, marker="o", ms=3.5,
              label=r"vertex line, $\theta=0$: $n/2$ (proved, Paper I)")
    axL.plot(h[zmask], apothem_x[zmask], color=BLUE, lw=1.5, ls=(0, (4, 2)), marker="o", ms=3.5,
              label=r"apothem line, mid-edge: $(n/2)\cos(\pi/n)$")
    axL.set_xlabel(f"height ({height_mode})", color=INK)
    axL.set_ylabel("radial position", color=INK)
    axL.set_title("Near n = 3..30, where the gap is visible", loc="left",
                  fontsize=10, fontfamily="serif", color=INK)
    axL.legend(frameon=False, fontsize=8, loc="upper left")
    axL.grid(True, color=GRID, lw=0.6)

    axR.set_facecolor(BG)
    for s in axR.spines.values():
        s.set_color("#c8c2b6")
    axR.tick_params(colors=INK, labelsize=8)
    gap = vertex_x - apothem_x
    axR.plot(ns, gap, color=INK, lw=1.4)
    axR.set_xscale("log")
    axR.set_yscale("log")
    axR.set_xlabel("n  (log)", color=INK)
    axR.set_ylabel(r"$n/2 - (n/2)\cos(\pi/n)$  (log)", color=INK)
    axR.set_title(f"Full depth to n = {nmax}", loc="left",
                  fontsize=10, fontfamily="serif", color=INK)
    axR.grid(True, which="both", color=GRID, lw=0.6)

    fig.suptitle("Model 3  ·  vertical section  ·  the elevation Paper I named but never drew",
                 fontsize=12, fontfamily="serif", color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save(fig, out / "model3_vertical_section.png")


def build_elevation_html(n_list: list[int], height_mode: str, out: Path):
    if not HAS_PLOTLY:
        print("[skip] plotly not installed")
        return None

    fig = go.Figure()
    nmax = max(n_list)

    for n in n_list:
        r = n / 2.0
        xs, ys, _ = ngon_vertices(n, r)
        z = np.full_like(xs, height_of(n, height_mode))
        fade = 0.25 + 0.65 * (1.0 - n / nmax)
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=z,
            mode="lines",
            line=dict(color=f"rgba(22,22,22,{fade:.2f})", width=3),
            name=f"n={n}",
            showlegend=False,
            hovertemplate=f"n={n}<br>radius={r:.3f}<br>height=%{{z:.3f}}<extra></extra>",
        ))

    ns_fine = np.arange(3, nmax + 1)
    h_fine = np.array([height_of(n, height_mode) for n in ns_fine])
    vertex_x = ns_fine / 2.0
    apothem_x = (ns_fine / 2.0) * np.cos(PI / ns_fine)

    fig.add_trace(go.Scatter3d(
        x=vertex_x, y=np.zeros_like(vertex_x), z=h_fine,
        mode="lines", line=dict(color=HERE, width=6),
        name="vertex line theta=0  ·  n/2  (proved, Paper I)",
        hovertemplate="n/2=%{x:.3f}<br>height=%{z:.3f}<extra>vertex line</extra>",
    ))
    fig.add_trace(go.Scatter3d(
        x=apothem_x, y=np.zeros_like(apothem_x), z=h_fine,
        mode="lines", line=dict(color=BLUE, width=6, dash="dash"),
        name="apothem line, mid-edge  ·  (n/2)cos(pi/n)",
        hovertemplate="apothem=%{x:.3f}<br>height=%{z:.3f}<extra>apothem line</extra>",
    ))

    fig.update_layout(
        title=dict(
            text=(
                f"Elements of Position — Elevation Stack  ·  n = {min(n_list)}..{nmax}  ·  "
                f"height = {height_mode}"
                "<br><sup>orbit / zoom / hover any ring  ·  "
                "solid = vertex line (proved)  ·  dashed = apothem line (the squeeze)</sup>"
            ),
            x=0.02, xanchor="left",
            font=dict(family="Georgia, serif", size=15, color=INK),
        ),
        scene=dict(
            xaxis=dict(title="x", backgroundcolor=BG, gridcolor=GRID),
            yaxis=dict(title="y", backgroundcolor=BG, gridcolor=GRID),
            zaxis=dict(title=f"height ({height_mode})", backgroundcolor=BG, gridcolor=GRID),
            aspectmode="data",
            camera=dict(eye=dict(x=1.6, y=0.15, z=0.35)),
        ),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        legend=dict(x=0.01, y=0.97, bgcolor="rgba(250,250,248,0.88)",
                    bordercolor="#D8D2C8", borderwidth=1,
                    font=dict(family="Georgia, serif", size=11, color=INK)),
        margin=dict(l=0, r=0, t=90, b=0),
        hoverlabel=dict(bgcolor=BG, bordercolor=HERE,
                         font=dict(family="Georgia, serif", size=12, color=INK)),
    )

    html_path = out / "model3_elevation_stack.html"
    fig.write_html(str(html_path), include_plotlyjs=True)
    return html_path


# =============================================================================
# Self-test -- run on every execution, not a one-off check
# =============================================================================
def verify_findings(ngon_rows: list[dict]) -> bool:
    ok = True

    # shared vertices == (n-1) - phi(n), exactly -- follows directly from
    # the definition of Euler's totient; included as a standing check, not
    # a claim from the papers.
    mismatches = sum(1 for r in ngon_rows
                      if r["vertices_shared_with_smaller_dgon"] != r["predicted_shared_from_totient"])
    d_ok = mismatches == 0
    print(f"  [{'PASS' if d_ok else 'FAIL'}] shared vertices == (n-1)-phi(n) exactly, "
          f"{len(ngon_rows)} rows, {mismatches} mismatches")
    ok &= d_ok

    # relative squeeze ~ pi^2/(2n^2), spot-checked at large n -- confirms
    # the apothem/radius convergence rate underlying Model 3's vertical
    # section, and Paper I's cited Archimedes inequality.
    big = [r for r in ngon_rows if r["n"] >= 500]
    if big:
        rel_errs = [abs((1 - r["apothem_over_radius"]) - (PI**2 / 2) / r["n"]**2)
                    / ((PI**2 / 2) / r["n"]**2) for r in big]
        f_ok = max(rel_errs) < 0.01
        print(f"  [{'PASS' if f_ok else 'FAIL'}] relative squeeze matches pi^2/(2n^2) "
              f"within 1% for n>=500 ({len(big)} rows checked)")
        ok &= f_ok

    # Archimedes squeeze both sides, all n: inscribed <= pi <= circumscribed
    squeeze_ok = all(r["side_chord"] <= PI + 1e-9 <= r["circumscribed_side"] + 1e-9
                      for r in ngon_rows)
    print(f"  [{'PASS' if squeeze_ok else 'FAIL'}] inscribed <= pi <= circumscribed "
          f"for every n (Paper I's cited Archimedes inequality)")
    ok &= squeeze_ok

    return ok


# =============================================================================
# Main
# =============================================================================
def main():
    ap = argparse.ArgumentParser(description="Elements of Position -- Local Circle Models")
    ap.add_argument("--nmax", type=int, default=1000,
                     help="depth of the raw measurement run (Model 1's math), default 1000")
    ap.add_argument("--stack-nmax", type=int, default=40,
                     help="how many n-gons the plan overlay / elevation stack draw, default 40")
    ap.add_argument("--singles", type=int, nargs="*", default=[3, 4, 5, 6, 7, 8, 10, 12, 16, 20],
                     help="which n get their own Model 1 drawing")
    ap.add_argument("--vertex-sample", type=int, nargs="*", default=[12, 15, 20, 30],
                     help="which n get a full vertex-structure enumeration")
    ap.add_argument("--height-mode", choices=["n_half", "half_walk", "n"], default="n_half",
                     help="elevation convention: n/2 (default, matches Paper I's cone), "
                          "half_walk (n*pi/2, the walked-arc elevation), or raw n")
    ap.add_argument("--no-html", action="store_true")
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    out = Path(args.out) if args.out else OUT
    out.mkdir(parents=True, exist_ok=True)
    singles_dir = out / "model1_single"
    singles_dir.mkdir(exist_ok=True)

    print("output folder:", out.resolve())

    nmax = max(3, args.nmax)
    print(f"Model 1 raw run: n = 3..{nmax}")
    rows = [ngon_measurements(n) for n in range(3, nmax + 1)]
    write_csv(out / "ngon_measurements.csv", rows)

    vs_rows = []
    for n in args.vertex_sample:
        vs_rows.extend(vertex_structure_rows(n))
    write_csv(out / "vertex_structure_sample.csv", vs_rows)

    print("Model 1 single drawings:", args.singles)
    for n in args.singles:
        draw_single_ngon(n, singles_dir)

    stack_list = list(range(3, args.stack_nmax + 1))
    print(f"Model 2 plan overlay: n = 3..{args.stack_nmax}")
    draw_plan_overlay(stack_list, out)

    print(f"Model 3 vertical section: n = 3..{nmax}, height mode = {args.height_mode}")
    draw_vertical_section(nmax, args.height_mode, out)

    if not args.no_html:
        print(f"Model 3 elevation stack html: n = 3..{args.stack_nmax}")
        html = build_elevation_html(stack_list, args.height_mode, out)
        if html:
            print("wrote", html.name)

    print("self-test:")
    verify_findings(rows)

    print("done.")


if __name__ == "__main__":
    main()
