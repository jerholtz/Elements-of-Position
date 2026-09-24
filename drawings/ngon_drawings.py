#!/usr/bin/env python3
"""
Elements of Position -- N-gon Drawings, full set.

Reads kernels/ngon's own CSVs only. No synthesis, no cross-kernel
reference. Same palette and title-block convention as
drawings/walk_drawings.py -- one family, two kernels.

Palette: black / white / gray, with exactly one accent -- the same
dry, oxide red -- used for exactly one thing everywhere it appears in
this file: the inverse locus. For the walk kernel that is Q_m = u_m/m.
Here it is the direct analog: the same n vertices, scaled from radius
R = n/2 down to radius inv = 1/n. `inv` is already a column in
rings.csv; what did not exist before this file is the geometric object
it names. That object is added here, in the drawing layer, as a plain
rescale of already-tabulated vertex directions -- no new kernel column,
no new measurement, just the picture the existing number was owed.
"""
import csv, sys, math
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

PAPER = "#ffffff"
INK = "#1a1a1a"
GRAY_DARK = "#555555"
GRAY_MID = "#9a9a9a"
GRAY_LIGHT = "#d5d5d5"
INVERSE_RED = "#9c4032"   # the one accent. always means: the inverse locus, 1/n.

LW_HAIR = 0.35
LW_LIGHT = 0.6
LW_MED = 0.9
LW_HEAVY = 1.3

PHI = (1.0 + math.sqrt(5.0)) / 2.0


def read_rows(run_dir, name):
    with (Path(run_dir) / name).open() as f:
        return list(csv.DictReader(f))


def new_sheet():
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    return fig, ax


def titleblock(fig, code, name, note, footer=""):
    fig.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.09)
    fig.text(0.07, 0.955, "ELEMENTS OF POSITION", fontsize=7, color=GRAY_DARK, ha="left")
    fig.text(0.07, 0.928, code, fontsize=13, color=INK, ha="left", fontweight="bold")
    fig.text(0.07, 0.902, name, fontsize=9, color=INK, ha="left")
    fig.text(0.97, 0.955, "n-gon / set", fontsize=7, color=GRAY_DARK, ha="right")
    fig.text(0.97, 0.928, note, fontsize=7, color=GRAY_DARK, ha="right")
    fig.text(0.97, 0.03, footer, fontsize=6.5, color=GRAY_MID, ha="right")
    fig.text(0.07, 0.03, "kernels/ngon", fontsize=6.5, color=GRAY_MID, ha="left")


def bare(ax):
    ax.set_aspect("equal")
    ax.axis("off")


def save(fig, out_dir, name, pdf):
    fig.savefig(Path(out_dir) / f"{name}.png", dpi=160, facecolor=PAPER)
    pdf.savefig(fig, facecolor=PAPER)
    plt.close(fig)


def circle_pts(r, n=400):
    theta = [i / n * 2 * math.pi for i in range(n + 1)]
    return [r * math.cos(t) for t in theta], [r * math.sin(t) for t in theta]


# =============================================================== A0 index
def sheet_A0(n_max, out_dir, pdf):
    fig, ax = new_sheet()
    bare(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    titleblock(fig, "A0", "Index", "one generator, views and details of the same vertices")
    ax.text(0.55, 7.5,
            "n equally spaced vertices, radius n/2. Outer locus in ink.\n"
            "The dry red is the inverse locus, always: the same vertices at radius 1/n.\n"
            "Nothing is drawn that is not a vertex or a ring of this kernel.",
            fontsize=10, color=INK)
    boxes = [
        (0.55, 4.85, "P1  PLAN", "one n-gon\nouter, apothem, inverse locus"),
        (3.20, 4.85, "P2  OVERLAY", "every n, concentric\nouter in ink, inverse in red"),
        (5.85, 4.85, "E1  ELEVATION", "Archimedes squeeze\ninscribed / circumscribed on pi"),
        (8.50, 4.85, "D1  THE RING", "apothem, B1, B2, inverse\nvs n"),
    ]
    for x, y, title, body in boxes:
        ax.add_patch(plt.Rectangle((x, y), 2.35, 1.85, facecolor="#f7f7f7", edgecolor=INK, lw=LW_LIGHT))
        ax.text(x + 0.12, y + 1.55, title, fontsize=8.5, color=INK, fontweight="bold")
        ax.text(x + 0.12, y + 0.95, body, fontsize=7.3, color=GRAY_DARK, va="top")
    fig.text(0.07, 0.455, "D2 lock  n=1      D3 marriage  n=5      D4 vertex structure  n=12",
              fontsize=8, color=INK, ha="left")
    fig.text(0.07, 0.418, "SCH1 totient schedule      SCH2 reducible density",
              fontsize=8, color=INK, ha="left")
    ax.text(0.55, 3.6, f"this run: n = 1..{n_max}", fontsize=8, color=GRAY_DARK)
    save(fig, out_dir, "A0_index", pdf)


# =================================================================== P1 plan
def sheet_P1(run_dir, out_dir, pdf, n_freeze=10):
    rings = {int(r["n"]): r for r in read_rows(run_dir, "rings.csv")}
    verts = [r for r in read_rows(run_dir, "vertices.csv") if int(r["n"]) == n_freeze]
    ring = rings[n_freeze]

    R = float(ring["R"])
    inv = float(ring["inv"])
    apo = float(ring["apothem"])
    B1 = float(ring["B1"])
    B2 = float(ring["B2"])

    fig, ax = new_sheet()
    bare(ax)
    titleblock(fig, "P1", f"Plan  ·  freeze n={n_freeze}", "outer ring, apothem, two Phi-nests, inverse locus")

    def circle(r, color, lw, ls="-"):
        xs, ys = circle_pts(r)
        ax.plot(xs, ys, color=color, lw=lw, ls=ls)

    circle(R, INK, LW_MED)
    circle(apo, GRAY_DARK, LW_LIGHT, "--")
    circle(B1, GRAY_MID, LW_LIGHT)
    circle(B2, GRAY_MID, LW_HAIR)
    circle(1.0, GRAY_LIGHT, LW_HAIR, ":")   # the lock, plain reference now, not accented
    circle(inv, INVERSE_RED, LW_MED)        # the inverse locus

    xs = [float(v["x"]) for v in verts]
    ys = [float(v["y"]) for v in verts]
    xs2, ys2 = xs + [xs[0]], ys + [ys[0]]
    ax.plot(xs2, ys2, color=INK, lw=LW_MED)
    ax.plot(xs, ys, "o", color=INK, ms=3.5)

    # the inverse n-gon: same directions, scaled to radius inv -- not a new
    # kernel measurement, just vertices.csv's own directions rescaled.
    ixs = [x / R * inv for x in xs]
    iys = [y / R * inv for y in ys]
    ixs2, iys2 = ixs + [ixs[0]], iys + [iys[0]]
    ax.plot(ixs2, iys2, color=INVERSE_RED, lw=LW_MED)
    ax.plot(ixs, iys, "o", color=INVERSE_RED, ms=3)

    lim = R * 1.25
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.text(lim * 0.97, 0.12, "R", fontsize=7.5, color=INK, ha="right")
    ax.text(inv + 0.06 * lim, 0.10, "inverse locus, 1/n", fontsize=7.5, color=INVERSE_RED, ha="left")

    save(fig, out_dir, "P1_plan", pdf)


# ============================================================ P2 plan overlay
def sheet_P2(run_dir, out_dir, pdf, n_lo=3, n_hi=40):
    rings = {int(r["n"]): r for r in read_rows(run_dir, "rings.csv")}
    all_verts = read_rows(run_dir, "vertices.csv")
    ns = [n for n in rings if n_lo <= n <= n_hi]
    ns.sort()

    fig, ax = new_sheet()
    bare(ax)
    titleblock(fig, "P2", f"Plan  ·  overlay, n={n_lo}..{n_hi}", "outer locus in ink, inverse locus in the one accent")

    by_n = {}
    for v in all_verts:
        n = int(v["n"])
        if n in by_n:
            by_n[n].append(v)
        else:
            by_n[n] = [v]

    for n in ns:
        R = float(rings[n]["R"])
        inv = float(rings[n]["inv"])
        verts = by_n.get(n, [])
        if not verts:
            continue
        xs = [float(v["x"]) for v in verts]
        ys = [float(v["y"]) for v in verts]
        xs2, ys2 = xs + [xs[0]], ys + [ys[0]]
        ax.plot(xs2, ys2, color=INK, lw=LW_HAIR, alpha=0.7)
        ixs = [x / R * inv for x in xs]
        iys = [y / R * inv for y in ys]
        ixs2, iys2 = ixs + [ixs[0]], iys + [iys[0]]
        ax.plot(ixs2, iys2, color=INVERSE_RED, lw=LW_HAIR, alpha=0.7)

    Rmax = float(rings[n_hi]["R"])
    ax.set_xlim(-Rmax * 1.05, Rmax * 1.05)
    ax.set_ylim(-Rmax * 1.05, Rmax * 1.05)
    ax.text(Rmax * 0.98, -Rmax * 1.0, f"outer: n={n_hi}, R={Rmax:.1f}", fontsize=7.5, color=INK, ha="right")
    ax.text(Rmax * 0.98, -Rmax * 1.08, "inverse: same n, radius 1/n", fontsize=7.5, color=INVERSE_RED, ha="right")

    save(fig, out_dir, "P2_overlay", pdf)


# ==================================================================== E1 elevation
def sheet_E1(run_dir, out_dir, pdf):
    rows = read_rows(run_dir, "rings.csv")
    ns = [int(r["n"]) for r in rows if int(r["n"]) >= 3]
    side = [float(r["side"]) for r in rows if int(r["n"]) >= 3]
    apo = [float(r["apothem"]) for r in rows if int(r["n"]) >= 3]
    # circumscribed bound, derived from existing columns only: n*tan(pi/n) = n*side/(2*apothem)
    circ = [n * s / (2 * a) for n, s, a in zip(ns, side, apo)]

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    titleblock(fig, "E1", "Elevation", "Archimedes' squeeze: inscribed and circumscribed on pi", f"n = 3..{ns[-1]}")

    ax.plot(ns, side, color=INK, lw=LW_MED, label="n sin(pi/n)  (inscribed)")
    ax.plot(ns, circ, color=GRAY_DARK, lw=LW_MED, label="n tan(pi/n)  (circumscribed)")
    ax.axhline(math.pi, color=GRAY_MID, lw=LW_LIGHT, ls="--")
    ax.text(ns[-1], math.pi + 0.05, "pi", fontsize=8, color=GRAY_DARK, ha="right")

    ax.set_xlabel("n", color=GRAY_DARK, fontsize=8)
    ax.set_ylabel("perimeter / diameter", color=GRAY_DARK, fontsize=8)
    ax.set_xlim(0, ns[-1] * 1.05)
    ax.set_ylim(2.5, min(6, max(circ)))
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRAY_LIGHT)
    ax.tick_params(colors=GRAY_DARK, labelsize=7)
    ax.legend(loc="upper right", fontsize=7.5, frameon=False)

    save(fig, out_dir, "E1_elevation", pdf)


# =================================================================== D1 ring
def sheet_D1(run_dir, out_dir, pdf):
    rows = read_rows(run_dir, "rings.csv")
    ns = [int(r["n"]) for r in rows]
    apo = [float(r["apothem"]) for r in rows if r["n"] not in ("1", "2")]
    ns_apo = [int(r["n"]) for r in rows if r["n"] not in ("1", "2")]
    B1 = [float(r["B1"]) for r in rows]
    B2 = [float(r["B2"]) for r in rows]
    inv = [float(r["inv"]) for r in rows]

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    titleblock(fig, "D1", "The ring", "apothem, the two Phi-nests, and the inverse locus, from rings.csv", f"n = 1..{ns[-1]}")

    ax.semilogy(ns_apo, apo, color=INK, lw=LW_MED, label="apothem")
    ax.semilogy(ns, B1, color=GRAY_DARK, lw=LW_MED, label="B1 = R * Phi")
    ax.semilogy(ns, B2, color=GRAY_MID, lw=LW_LIGHT, label="B2 = R * Phi^2")
    ax.semilogy(ns, inv, color=INVERSE_RED, lw=LW_MED, label="inv = 1/n  (inverse locus)")
    ax.axhline(1.0, color=GRAY_LIGHT, lw=LW_LIGHT, ls=":")
    ax.text(ns[-1], 1.15, "the lock", fontsize=7.5, color=GRAY_DARK, ha="right")
    ax.set_ylim(0.005, 40)

    ax.set_xlabel("n", color=GRAY_DARK, fontsize=8)
    ax.set_ylabel("length (log scale)", color=GRAY_DARK, fontsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRAY_LIGHT)
    ax.tick_params(colors=GRAY_DARK, labelsize=7)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False)

    save(fig, out_dir, "D1_ring", pdf)


# =================================================================== D2 lock
def sheet_D2(run_dir, out_dir, pdf):
    rings = {int(r["n"]): r for r in read_rows(run_dir, "rings.csv")}
    ring = rings[1]
    fig, ax = new_sheet()
    bare(ax)
    titleblock(fig, "D2", "Detail  ·  lock, n=1", "the outer locus and the inverse locus start at the same point")

    R = float(ring["R"])       # 0.5
    inv = float(ring["inv"])   # 1.0

    circle_R_x, circle_R_y = circle_pts(R)
    ax.plot(circle_R_x, circle_R_y, color=INK, lw=LW_MED)
    circle_inv_x, circle_inv_y = circle_pts(inv)
    ax.plot(circle_inv_x, circle_inv_y, color=INVERSE_RED, lw=LW_MED)
    ax.plot(0, 0, "o", color=INK, ms=5)
    ax.plot(R, 0, "o", color=INK, ms=5)
    ax.plot(inv, 0, "o", color=INVERSE_RED, ms=5)
    ax.annotate("R = 0.5", (R, 0), xytext=(R + 0.08, 0.12), fontsize=8, color=INK)
    ax.annotate("inv = 1.0", (inv, 0), xytext=(inv + 0.08, -0.18), fontsize=8, color=INVERSE_RED)

    ax.text(0, -1.4, "at n=1, the outer diameter is 1 and the inverse locus is\n"
                       "also exactly 1 -- the one place the two loci coincide.",
            fontsize=9, color=INK, ha="center")

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.7, 1.5)
    save(fig, out_dir, "D2_lock", pdf)


# =================================================================== D3 marriage
def sheet_D3(run_dir, out_dir, pdf):
    rings = {int(r["n"]): r for r in read_rows(run_dir, "rings.csv")}
    verts = [r for r in read_rows(run_dir, "vertices.csv") if int(r["n"]) == 5]
    ring = rings[5]
    R = float(ring["R"])
    inv = float(ring["inv"])
    twocos = float(ring["twocos"])

    fig, ax = new_sheet()
    bare(ax)
    titleblock(fig, "D3", "Detail  ·  the marriage, n=5", "2 cos(pi/5) = Phi, exactly -- not approached, met")

    xs = [float(v["x"]) for v in verts]
    ys = [float(v["y"]) for v in verts]
    xs2, ys2 = xs + [xs[0]], ys + [ys[0]]
    ax.plot(xs2, ys2, color=INK, lw=LW_MED)
    ax.plot(xs, ys, "o", color=INK, ms=5)

    ax.plot([xs[0], xs[2]], [ys[0], ys[2]], color=GRAY_DARK, lw=LW_LIGHT)
    ax.plot([xs[0], xs[3]], [ys[0], ys[3]], color=GRAY_DARK, lw=LW_LIGHT)

    circle_inv_x, circle_inv_y = circle_pts(inv)
    ax.plot(circle_inv_x, circle_inv_y, color=INVERSE_RED, lw=LW_LIGHT)

    ax.text(0, -R * 1.4,
            f"2 cos(pi/5) = {twocos:.10f}\nPhi           = {PHI:.10f}\n"
            f"diff          = {abs(twocos - PHI):.2e}",
            fontsize=9, color=INK, ha="center", family="monospace")

    lim = R * 1.3
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim * 1.3, lim)
    save(fig, out_dir, "D3_marriage", pdf)


# =================================================================== D4 vertex structure
def sheet_D4(run_dir, out_dir, pdf, n_freeze=12):
    vs = [r for r in read_rows(run_dir, "vertex_structure.csv") if int(r["n"]) == n_freeze]
    rings = {int(r["n"]): r for r in read_rows(run_dir, "rings.csv")}
    R = float(rings[n_freeze]["R"])

    fig, ax = new_sheet()
    bare(ax)
    titleblock(fig, "D4", f"Detail  ·  vertex structure, n={n_freeze}",
               "filled = shared with a smaller d-gon, hollow = new to n")

    circle_x, circle_y = circle_pts(R)
    ax.plot(circle_x, circle_y, color=GRAY_LIGHT, lw=LW_HAIR)

    pts = [(R * math.cos(2 * math.pi * int(r["k"]) / n_freeze),
            R * math.sin(2 * math.pi * int(r["k"]) / n_freeze),
            int(r["gcd"]) > 1) for r in vs]
    pts.append((R, 0.0, True))  # k=0 vertex, shared with every divisor gon

    xs2 = [p[0] for p in pts] + [pts[0][0]]
    ys2 = [p[1] for p in pts] + [pts[0][1]]
    ax.plot(xs2, ys2, color=INK, lw=LW_LIGHT)

    for x, y, reducible in pts:
        if reducible:
            ax.plot(x, y, "o", color=INK, ms=7, mfc=INK)
        else:
            ax.plot(x, y, "o", color=INK, ms=7, mfc="white", mec=INK, mew=LW_MED)

    n_new = sum(1 for _, _, r in pts if not r)
    ax.text(0, -R * 1.25, f"{n_new} of {n_freeze} vertices are new to n={n_freeze}", fontsize=9, color=INK, ha="center")

    lim = R * 1.2
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim * 1.25, lim)
    save(fig, out_dir, "D4_vertex_structure", pdf)


# =================================================================== SCH1
def sheet_SCH1(run_dir, out_dir, pdf):
    rows = read_rows(run_dir, "summary.csv")
    mism = [r for r in rows if r["match"] == "0"]
    n_max = max(int(r["n"]) for r in rows)

    fig, ax = new_sheet()
    bare(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    titleblock(fig, "SCH1", "Schedule  ·  totient", "the gcd-based count pays Euler's totient exactly")

    ax.text(0.55, 7.1, "reducible_count(n)  vs  (n-1) - totient(n)", fontsize=9, color=GRAY_DARK)
    ax.text(0.55, 6.5, f"checked, n = 2..{n_max}:  {len(rows)} rows,  {len(mism)} mismatches", fontsize=13, color=INK)

    sample = [r for r in rows if int(r["n"]) in (5, 6, 10, 12, 17, 24, 30)]
    y = 5.3
    ax.text(0.55, y + 0.4, f"{'n':>4} {'reducible':>10} {'totient predicts':>18}", fontsize=8, color=GRAY_DARK, family="monospace")
    for r in sample:
        ax.text(0.55, y, f"{r['n']:>4} {r['reducible_count']:>10} {r['totient_predicted']:>18}",
                 fontsize=8, color=INK, family="monospace")
        y -= 0.32

    save(fig, out_dir, "SCH1_totient", pdf)


# =================================================================== SCH2
def sheet_SCH2(run_dir, out_dir, pdf):
    rows = read_rows(run_dir, "summary.csv")
    ns = [int(r["n"]) for r in rows]
    density = [float(r["reducible_count"]) / int(r["n"]) for r in rows]

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    titleblock(fig, "SCH2", "Schedule  ·  reducible density", "reducible_count(n) / n, from summary.csv", f"n = 2..{ns[-1]}")

    is_prime = [r["is_prime"] == "1" for r in rows]
    ax.plot(ns, density, color=GRAY_MID, lw=LW_HAIR)
    prime_ns = [n for n, p in zip(ns, is_prime) if p]
    prime_d = [d for d, p in zip(density, is_prime) if p]
    other_ns = [n for n, p in zip(ns, is_prime) if not p]
    other_d = [d for d, p in zip(density, is_prime) if not p]
    ax.plot(other_ns, other_d, "o", color=INK, ms=2.5, alpha=0.6, label="not prime")
    ax.plot(prime_ns, prime_d, "o", color=INK, ms=2.5, mfc="white", mec=INK, mew=0.6, label="prime  (density = 0)")

    ax.set_xlabel("n", color=GRAY_DARK, fontsize=8)
    ax.set_ylabel("reducible_count(n) / n", color=GRAY_DARK, fontsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRAY_LIGHT)
    ax.tick_params(colors=GRAY_DARK, labelsize=7)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False)

    save(fig, out_dir, "SCH2_density", pdf)


def main():
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../kernels/ngon/runs/2026-09-24_n1-60")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_rows(run_dir, "rings.csv")
    n_max = max(int(r["n"]) for r in rows)

    with PdfPages(out_dir / "Ngon_Set.pdf") as pdf:
        sheet_A0(n_max, out_dir, pdf)
        sheet_P1(run_dir, out_dir, pdf, n_freeze=10)
        sheet_P2(run_dir, out_dir, pdf, n_lo=3, n_hi=min(40, n_max))
        sheet_E1(run_dir, out_dir, pdf)
        sheet_D1(run_dir, out_dir, pdf)
        sheet_D2(run_dir, out_dir, pdf)
        sheet_D3(run_dir, out_dir, pdf)
        sheet_D4(run_dir, out_dir, pdf, n_freeze=12)
        sheet_SCH1(run_dir, out_dir, pdf)
        sheet_SCH2(run_dir, out_dir, pdf)

    print(f"wrote {out_dir/'Ngon_Set.pdf'}  (10 sheets)")


if __name__ == "__main__":
    main()
