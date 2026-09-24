#!/usr/bin/env python3
"""
Elements of Position -- IV. Already There -- Drawings.

Reads the tables EOP_IV_Measure.py writes. Does not walk, does not
recompute a single mathematical claim -- the same separation the kernel
and set.py already keep between what measures and what draws.

Palette and title-block conventions copied verbatim from eop_set.py.
"""
import csv, math
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

IN = Path(__file__).resolve().parent / "measure_out"
OUT = Path(__file__).resolve().parent / "drawings_out"
OUT.mkdir(exist_ok=True)

# --- graphic, copied verbatim from eop_set.py ---
PAPER = "#f3f0e8"
INK = "#161616"
DIM = "#8a8680"
RULE = "#c9c4b8"
ACCENT = "#8b3a3a"   # inverse wall / accent one
ACCENT2 = "#6b4c7a"  # accent two, for a second traced path

LW_CON = 0.25
LW_OBJ = 0.55
LW_CUT = 1.15
LW_PROF = 1.55


def read_rows(name):
    with (IN / name).open() as f:
        return list(csv.DictReader(f))


def new_sheet(landscape=True):
    w, h = (11.0, 8.5) if landscape else (8.5, 11.0)
    fig, ax = plt.subplots(figsize=(w, h), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    return fig, ax


def titleblock(fig, code, name, note, footer=""):
    fig.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.08)
    fig.text(0.07, 0.955, "ELEMENTS OF POSITION", fontsize=7, color=DIM, ha="left")
    fig.text(0.07, 0.928, code, fontsize=13, color=INK, ha="left", fontweight="bold")
    fig.text(0.07, 0.902, name, fontsize=9, color=INK, ha="left")
    fig.text(0.97, 0.955, "IV", fontsize=7, color=DIM, ha="right")
    fig.text(0.97, 0.928, note, fontsize=7, color=DIM, ha="right")
    fig.text(0.97, 0.035, footer, fontsize=6.5, color=DIM, ha="right")
    fig.text(0.07, 0.035, "already there", fontsize=6.5, color=DIM, ha="left")


def bare(ax):
    ax.set_aspect("equal")
    ax.axis("off")


def save(fig, name, pdf):
    fig.savefig(OUT / f"{name}.png", dpi=160, facecolor=PAPER)
    pdf.savefig(fig, facecolor=PAPER)
    plt.close(fig)


# ============================================================== A0 index
def sheet_A0(pdf):
    fig, ax = new_sheet()
    bare(ax)
    ax.set_xlim(0, 11); ax.set_ylim(0, 8.5)
    titleblock(fig, "A0", "Index", "already there · one object, five plates")
    ax.text(0.55, 7.3, "Every plate below reads only from the CSVs EOP_IV_Measure.py writes.\n"
                        "Nothing on this page is drawn that was not measured first.",
            fontsize=10, color=INK)
    boxes = [
        (0.55, 4.4, "Z1  DIRICHLET", "tau(n)'s Dirichlet series\nthree poles, three residues"),
        (3.2, 4.4, "Z2  LADDER", "the Bernoulli correction terms\ndescend, then diverge"),
        (5.85, 4.4, "G1  GAP WORD", "predicted vs. walked,\nM=127 and M=129"),
        (8.5, 4.4, "SB1  THE TREE", "boundary spines, phi path,\nsqrt2 path, one random path"),
    ]
    for x, y, h, body in boxes:
        ax.add_patch(Rectangle((x, y), 2.35, 2.0, facecolor="#eeeae1", edgecolor=INK, lw=0.5))
        ax.text(x + 0.12, y + 1.68, h, fontsize=8.5, color=INK, fontweight="bold")
        ax.text(x + 0.12, y + 1.05, body, fontsize=7.5, color=INK, va="top")
    ax.add_patch(Rectangle((0.55, 1.9), 2.35, 2.0, facecolor="#eeeae1", edgecolor=INK, lw=0.5))
    ax.text(0.67, 3.58, "CS1  CASSINI", fontsize=8.5, color=INK, fontweight="bold")
    ax.text(0.67, 2.95, "the Fibonacci matrix,\nits determinant, the\ndocking curve", fontsize=7.5, color=INK, va="top")
    save(fig, "A0_index", pdf)


# =================================================================== Z1
def sheet_Z1(pdf):
    rows = read_rows("z1_tau_dirichlet.csv")
    resid = read_rows("z1_residues.csv")
    special = read_rows("z1_special_values.csv")

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    titleblock(fig, "Z1", "The leftover's Dirichlet series",
               "T(s) = (1/2)z(s-1) - z(s) + (1/2)z(s+1)",
               "grows out of: Without an Angle, wedge_closed")

    xs = [float(r["s"]) for r in rows]
    ys = [float(r["T_s"]) for r in rows]
    # split at poles so the plotted curve does not draw a false connecting line
    segs = [[]]
    for x, y in zip(xs, ys):
        if segs[-1] and x - segs[-1][-1][0] > 0.06:
            segs.append([])
        segs[-1].append((x, y))
    for seg in segs:
        if len(seg) > 1:
            sx, sy = zip(*seg)
            ax.plot(sx, sy, color=INK, lw=LW_PROF)

    label_y = {0: 12.5, 1: -12.5, 2: 12.5}
    for r in resid:
        s0 = float(r["pole"])
        ax.axvline(s0, color=RULE, lw=0.8, ls=":")
        ax.annotate(
            f"pole s={int(s0)}\nresidue {float(r['measured_residue']):.3f}",
            (s0, label_y[int(s0)]), fontsize=7.5, color=ACCENT, ha="left",
        )
    ax.axhline(0, color=RULE, lw=0.6)
    ax.set_ylim(-15, 15)
    ax.set_xlabel("s", color=DIM, fontsize=8)
    ax.set_ylabel("T(s)", color=DIM, fontsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(RULE)
    ax.tick_params(colors=DIM, labelsize=7)

    t_m1 = [s["T_s"] for s in special if s["s"] == "-1"][0]
    ax.text(0.07, 0.15,
            f"T(-1) = {float(t_m1):.6f}  =  -1/6 exactly\n"
            f"(the analytic continuation's value; not a claim about the divergent sum)",
            transform=fig.transFigure, fontsize=8, color=INK)

    save(fig, "Z1_dirichlet", pdf)


# =================================================================== Z2
def sheet_Z2(pdf):
    rows = read_rows("z2_bernoulli_ladder.csv")
    ks = [int(r["k"]) for r in rows]
    terms = [float(r["abs_term_N10"]) for r in rows]
    kmin = ks[terms.index(min(terms))]

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    titleblock(fig, "Z2", "The ladder does not converge",
               "|Bernoulli correction term| at fixed N=10, log scale",
               "grows out of: Without an Angle, gamma/2 - 1/4")

    ax.semilogy(ks, terms, color=INK, lw=LW_PROF, marker="o", ms=2.4)
    ax.axvline(kmin, color=ACCENT, lw=0.8, ls=":")
    ax.annotate(f"minimum near k={kmin}", (kmin, min(terms)),
                xytext=(kmin + 4, min(terms) * 1e6), fontsize=8, color=ACCENT)
    ax.set_xlabel("k  (order of Bernoulli correction, B_2k)", color=DIM, fontsize=8)
    ax.set_ylabel("|term|  at N=10", color=DIM, fontsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(RULE)
    ax.tick_params(colors=DIM, labelsize=7)
    ax.set_ylim(1e-32, 1e50)
    ax.text(0.12, 0.72,
            "Descends for thirty orders, then grows without bound.\n"
            "A genuine asymptotic series: exact-feeling up to its optimum, destructive past it.",
            transform=fig.transFigure, fontsize=8, color=INK)
    save(fig, "Z2_ladder", pdf)


# =================================================================== G1
def sheet_G1(pdf):
    rows = read_rows("g1_gap_word.csv")
    summary = read_rows("g1_summary.csv")
    pred = "".join(r["predicted"] for r in rows)
    act = "".join(r["actual"] for r in rows)
    match = all(r["match"] == "True" for r in rows)

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    bare(ax)
    ax.set_xlim(0, 11); ax.set_ylim(0, 8.5)
    titleblock(fig, "G1", "The gap word, predicted before it was walked",
               "three-distance theorem vs. the extended kernel run",
               "grows out of: Without an Angle, Sheet SCH1")

    def wrap(word, y, label, color):
        ax.text(0.55, y + 0.35, label, fontsize=8, color=DIM)
        for i in range(0, len(word), 64):
            ax.text(0.55, y, word[i:i + 64], fontsize=9, color=color, family="monospace")
            y -= 0.30
        return y

    y = 6.6
    y = wrap(pred[:127], y, "predicted, M=127 (from the continued fraction of f alone)", INK)
    y -= 0.3
    y = wrap(act[:127], y, "actual, M=127 (the recorded kernel run)", ACCENT)
    y -= 0.5
    y = wrap(pred, y, "predicted, M=129 (before the walk was extended)", INK)
    y -= 0.3
    y = wrap(act, y, "actual, M=129 (the walk, extended, run afterward)", ACCENT)

    ax.text(0.55, y - 0.5,
            f"every letter agrees: {match}\n"
            f"M=127: {[s for s in summary if s['quantity']=='long_actual'][0]['at_M127']} long, "
            f"{[s for s in summary if s['quantity']=='short_actual'][0]['at_M127']} short   |   "
            f"M=129: {[s for s in summary if s['quantity']=='long_actual'][0]['at_M129']} long, "
            f"{[s for s in summary if s['quantity']=='short_actual'][0]['at_M129']} short",
            fontsize=9, color=INK)
    save(fig, "G1_gap_word", pdf)


# =================================================================== SB1
def sheet_SB1(pdf):
    tree = read_rows("sb1_full_tree.csv")
    paths = read_rows("sb1_tree_paths.csv")
    node = {int(r["node_id"]): (int(r["p"]), int(r["q"]), int(r["depth"])) for r in tree}
    parent = {int(r["node_id"]): int(r["parent_id"]) for r in tree}

    def rank_x(node_id, depth):
        # evenly spaced by structural position at this depth (standard binary-tree
        # layout), independent of the node's numeric value -- the value is kept
        # only as a label, so the tree's actual shape stays readable.
        return (node_id - 2 ** depth + 0.5) / 2 ** depth

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    bare(ax)
    titleblock(fig, "SB1", "One tree underneath both processes",
               "boundary spines = n and 1/n · interior paths = phi and sqrt2",
               "grows out of: The Closed Unit, The Other Walk, Meetings")

    DEPTH_MAX = max(d for (_, _, d) in node.values())
    for nid, (p, q, depth) in node.items():
        if nid == 1:
            continue
        pid = parent[nid]
        x0, x1 = rank_x(pid, depth - 1), rank_x(nid, depth)
        ax.plot([x0, x1], [depth - 1, depth], color=RULE, lw=LW_CON, zorder=1)

    for nid, (p, q, depth) in node.items():
        ax.plot(rank_x(nid, depth), depth, "o", color=DIM, ms=2.0, zorder=2)

    def draw_path(label, color, lw):
        pts = [(int(r["node_id"]), int(r["depth"]), int(r["p"]), int(r["q"])) for r in paths if r["path"] == label]
        pts = [pt for pt in pts if pt[1] <= DEPTH_MAX]
        xs = [rank_x(nid, depth) for nid, depth, p, q in pts]
        ys = [depth for nid, depth, p, q in pts]
        ax.plot(xs, ys, color=color, lw=lw, zorder=4)
        for x, y in zip(xs, ys):
            ax.plot(x, y, "o", color=color, ms=4.5, zorder=5)
        return pts, xs, ys

    right_pts, right_xs, right_ys = draw_path("right_spine_n", INK, 1.8)
    left_pts, left_xs, left_ys = draw_path("left_spine_1_over_n", INK, 1.8)
    phi_pts, phi_xs, phi_ys = draw_path("phi_path", ACCENT, 1.6)
    s2_pts, s2_xs, s2_ys = draw_path("sqrt2_path", ACCENT2, 1.6)

    ax.text(right_xs[-1] + 0.015, right_ys[-1], f"n = {right_pts[-1][2]}", fontsize=8, color=INK, va="center")
    ax.text(left_xs[-1] - 0.015, left_ys[-1], f"1/n = 1/{left_pts[-1][3]}", fontsize=8, color=INK, va="center", ha="right")
    ax.text(phi_xs[-1] - 0.05, phi_ys[-1] - 0.55, f"phi path: {phi_pts[-1][2]}/{phi_pts[-1][3]}",
            fontsize=8, color=ACCENT, ha="right")
    ax.text(s2_xs[-1] + 0.05, s2_ys[-1] + 0.55, f"sqrt2 path: {s2_pts[-1][2]}/{s2_pts[-1][3]}",
            fontsize=8, color=ACCENT2, ha="left")

    ax.text(0.5, -0.6, "root  1/1", fontsize=8, color=INK, ha="center")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(DEPTH_MAX + 1.0, -1.0)  # root at top, depth increasing downward
    save(fig, "SB1_tree", pdf)


# =================================================================== CS1
def sheet_CS1(pdf):
    rows = read_rows("cs1_fibonacci_matrix.csv")
    check = read_rows("cs1_meetings_check.csv")
    ks = [int(r["k"]) for r in rows]
    dets = [int(r["det"]) for r in rows]
    dock = [float(r["docking_error_1_over_2phik"]) for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5), facecolor=PAPER)
    for a in (ax1, ax2):
        a.set_facecolor(PAPER)
    fig.subplots_adjust(top=0.85, bottom=0.12, wspace=0.35)
    titleblock(fig, "CS1", "Cassini, and why it generalizes",
               "det(M^k) alternates; docking decays as 1/(2 phi^k)",
               "grows out of: Meetings, the docking-error proposition")

    ax1.bar(ks, dets, color=[INK if d > 0 else ACCENT for d in dets], width=0.6)
    ax1.axhline(0, color=RULE, lw=0.6)
    ax1.set_xlabel("k", color=DIM, fontsize=8)
    ax1.set_ylabel("det(M^k)", color=DIM, fontsize=8)
    ax1.set_yticks([-1, 0, 1])
    for spine in ("top", "right"):
        ax1.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax1.spines[spine].set_color(RULE)
    ax1.tick_params(colors=DIM, labelsize=7)

    ax2.semilogy(ks, dock, color=INK, lw=LW_PROF, marker="o", ms=3)
    ax2.set_ylim(5e-4, 3)
    for r in check:
        k0 = int(r["k"])
        ax2.plot(k0, float(r["predicted"]), "o", color=ACCENT, ms=6, zorder=5)
        xytext = (k0 - 4.5, float(r["predicted"]) * 6) if k0 < 10 else (k0 - 8.5, float(r["predicted"]) * 5)
        ax2.annotate(f"N={r['N']}\nMeetings quotes ~{r['meetings_quoted']}",
                      (k0, float(r["predicted"])), xytext=xytext,
                      fontsize=7, color=ACCENT)
    ax2.set_xlim(0, 14.5)
    ax2.set_xlabel("k  (Fibonacci arrival index)", color=DIM, fontsize=8)
    ax2.set_ylabel("docking error = 1/(2 phi^k)", color=DIM, fontsize=8)
    for spine in ("top", "right"):
        ax2.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax2.spines[spine].set_color(RULE)
    ax2.tick_params(colors=DIM, labelsize=7)

    save(fig, "CS1_cassini", pdf)


def main():
    pdf_path = OUT / "EOP_IV_Set.pdf"
    with PdfPages(pdf_path) as pdf:
        sheet_A0(pdf)
        sheet_Z1(pdf)
        sheet_Z2(pdf)
        sheet_G1(pdf)
        sheet_SB1(pdf)
        sheet_CS1(pdf)
    print("wrote", pdf_path)


if __name__ == "__main__":
    main()
