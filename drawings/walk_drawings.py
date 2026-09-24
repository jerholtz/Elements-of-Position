#!/usr/bin/env python3
"""
Elements of Position -- Walk Drawings, minimal.

Reads kernels/walk's own CSVs only. No synthesis, no cross-kernel
reference. Draws nothing that is not a value already sitting in a
table -- the same separation the kernel keeps from this drawing set.

Palette: black / white / gray, with exactly one accent -- a dry,
oxide red -- used for exactly one thing everywhere it appears: the
lock. GM=1 is what the bind enforces every step; it is the one
invariant this kernel never lets go of, so it is the one thing drawn
in the one color that is not gray.
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
INVERSE_RED = "#9c4032"    # the one accent. always means: the inverse locus, 1/m.

LW_HAIR = 0.35
LW_LIGHT = 0.6
LW_MED = 0.9
LW_HEAVY = 1.3


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
    fig.text(0.97, 0.955, "walk / minimal", fontsize=7, color=GRAY_DARK, ha="right")
    fig.text(0.97, 0.928, note, fontsize=7, color=GRAY_DARK, ha="right")
    fig.text(0.97, 0.03, footer, fontsize=6.5, color=GRAY_MID, ha="right")
    fig.text(0.07, 0.03, "kernels/walk", fontsize=6.5, color=GRAY_MID, ha="left")


def bare(ax):
    ax.set_aspect("equal")
    ax.axis("off")


def save(fig, out_dir, name, pdf):
    fig.savefig(Path(out_dir) / f"{name}.png", dpi=160, facecolor=PAPER)
    pdf.savefig(fig, facecolor=PAPER)
    plt.close(fig)


# =============================================================== A0 index
def sheet_A0(run_dir, summary, out_dir, pdf):
    fig, ax = new_sheet()
    bare(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    titleblock(fig, "A0", "Index", "minimal set: two sheets, nothing synthesized")
    ax.text(0.6, 7.3,
            "Both sheets below read only kernels/walk's own three CSVs.\n"
            "The dry red always means the same thing: the inverse locus, Q = u/m.",
            fontsize=10, color=INK)
    boxes = [(0.6, 4.6, "W1  HEADING", "the walk on the unit circle\nhits marked from crossings.csv"),
             (3.4, 4.6, "D1  THE PAIR", "r, 1/r, AM, GM, tau vs m\nfrom pairs.csv")]
    for x, y, title, body in boxes:
        ax.add_patch(plt.Rectangle((x, y), 2.4, 1.9, facecolor="#f7f7f7", edgecolor=INK, lw=LW_LIGHT))
        ax.text(x + 0.12, y + 1.6, title, fontsize=8.5, color=INK, fontweight="bold")
        ax.text(x + 0.12, y + 1.0, body, fontsize=7.5, color=GRAY_DARK, va="top")
    h = summary.get("h", "")
    steps = summary.get("steps", "")
    H0 = summary.get("H0", "")
    n_hits = summary.get("n_hits", "")
    ax.text(0.6, 3.9, f"this run:  h = {h}   steps = {steps}   H0 = {H0}   hits = {n_hits}",
            fontsize=8, color=GRAY_DARK)
    save(fig, out_dir, "A0_index", pdf)


# ================================================================ W1 heading
def sheet_W1(run_dir, summary, out_dir, pdf):
    hits = read_rows(run_dir, "crossings.csv")
    fig, ax = new_sheet()
    bare(ax)
    titleblock(fig, "W1", "Heading", "the bind, and the inverse locus it carries", f"h={summary.get('h','')}  hits={len(hits)}")

    # the bind: |heading| = 1 on every step, without exception. plain ink --
    # it is shared ground for both the outer and inverse readings, not itself
    # the inverse locus.
    theta = [i / 400 * 2 * math.pi for i in range(401)]
    cx = [math.cos(t) for t in theta]
    cy = [math.sin(t) for t in theta]
    ax.plot(cx, cy, color=INK, lw=LW_MED)

    # the cut, y=0
    ax.plot([-1.15, 1.15], [0, 0], color=GRAY_MID, lw=LW_HAIR)

    hx = [float(r["hx"]) for r in hits]
    hy = [float(r["hy"]) for r in hits]
    ms = [int(r["m"]) for r in hits]
    ax.plot(hx, hy, "o", color=INK, ms=2.6, mfc=INK, mec="none")
    if hits:
        ax.plot(hx[0], hy[0], "o", color=INK, ms=5, mfc="none", mec=INK, mew=LW_MED)
        ax.text(hx[0] + 0.04, hy[0] + 0.05, "first hit", fontsize=7, color=GRAY_DARK)

    # the inverse locus: Q_m = u_m / m. Same headings, scaled inward. This is
    # the one thing dry red means, drawn directly rather than implied.
    qx = [hxi / m for hxi, m in zip(hx, ms)]
    qy = [hyi / m for hyi, m in zip(hy, ms)]
    ax.plot(qx, qy, "o", color=INVERSE_RED, ms=2.2, mfc=INVERSE_RED, mec="none", zorder=4)
    if hits:
        ax.annotate("Q = u/m  (inverse locus)", (qx[0], qy[0]), xytext=(0.15, -0.22),
                     fontsize=7.5, color=INVERSE_RED,
                     arrowprops=dict(arrowstyle="-", color=INVERSE_RED, lw=0.5))

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    save(fig, out_dir, "W1_heading", pdf)


# ================================================================= D1 pair
def sheet_D1(run_dir, summary, out_dir, pdf):
    rows = read_rows(run_dir, "pairs.csv")
    ms = [int(r["m"]) for r in rows]
    r_out = [float(r["r"]) for r in rows]
    r_in = [float(r["r_in"]) for r in rows]
    am = [float(r["am"]) for r in rows]
    gm = [float(r["gm"]) for r in rows]
    tau = [float(r["tau"]) for r in rows]

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    titleblock(fig, "D1", "The pair", "r = m, 1/r = 1/m, from pairs.csv", f"m = 1..{ms[-1] if ms else 0}")

    ax.semilogy(ms, r_out, color=INK, lw=LW_MED, label="r  (outer)")
    ax.semilogy(ms, r_in, color=INVERSE_RED, lw=LW_MED, label="1/r  (inverse locus)")
    ax.semilogy(ms, am, color=GRAY_MID, lw=LW_LIGHT, ls="--", label="AM")
    ax.semilogy(ms, tau, color=INK, lw=LW_HAIR, ls=":", label="tau = AM - GM")
    ax.axhline(1.0, color=GRAY_DARK, lw=LW_LIGHT, ls=":")
    ax.text(ms[-1] if ms else 1, 1.15, "GM = 1", fontsize=7.5, color=GRAY_DARK, ha="right")

    ax.set_xlabel("m", color=GRAY_DARK, fontsize=8)
    ax.set_ylabel("length (log scale)", color=GRAY_DARK, fontsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRAY_LIGHT)
    ax.tick_params(colors=GRAY_DARK, labelsize=7)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False)

    save(fig, out_dir, "D1_pair", pdf)


def main():
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../kernels/walk/runs/2026-09-24_h0.002_n200000")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = read_rows(run_dir, "summary.csv")
    summary = {r["key"]: r["value"] for r in summary_rows}

    with PdfPages(out_dir / "Walk_Set.pdf") as pdf:
        sheet_A0(run_dir, summary, out_dir, pdf)
        sheet_W1(run_dir, summary, out_dir, pdf)
        sheet_D1(run_dir, summary, out_dir, pdf)

    print(f"wrote {out_dir/'Walk_Set.pdf'}")


if __name__ == "__main__":
    main()
