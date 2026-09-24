#!/usr/bin/env python3
"""Family 1 synthesis plates. Read measures only. Do not walk."""
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

PAPER = "#ffffff"
INK = "#1a1a1a"
GRAY_DARK = "#555555"
GRAY_MID = "#9a9a9a"
GRAY_LIGHT = "#d5d5d5"
INVERSE_RED = "#9c4032"


def titleblock(fig, code, name, note, footer=""):
    fig.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.10)
    fig.text(0.08, 0.955, "ELEMENTS OF POSITION", fontsize=7, color=GRAY_DARK, ha="left")
    fig.text(0.08, 0.928, code, fontsize=13, color=INK, ha="left", fontweight="bold")
    fig.text(0.08, 0.902, name, fontsize=9, color=INK, ha="left")
    fig.text(0.97, 0.955, "synthesis / bridge", fontsize=7, color=GRAY_DARK, ha="right")
    fig.text(0.97, 0.928, note, fontsize=7, color=GRAY_DARK, ha="right")
    fig.text(0.97, 0.03, footer, fontsize=6.5, color=GRAY_MID, ha="right")
    fig.text(0.08, 0.03, "measures/bridge", fontsize=6.5, color=GRAY_MID, ha="left")


def sheet_B1(rows, out_dir, pdf):
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    titleblock(
        fig, "B1", "Bridge  ·  walk step = n-gon vertex",
        "h = tan(2π/n); n=3,4 composed two elementary steps",
        "from bridge.csv  ·  2026-09-24",
    )
    ns = [int(r["n"]) for r in rows]
    err = [float(r["max_error"]) for r in rows]
    method = [r["method"] for r in rows]
    composed = [n for n, m in zip(ns, method) if m == "composed"]
    single = [n for n, m in zip(ns, method) if m == "single_step"]
    c_err = [e for e, m in zip(err, method) if m == "composed"]
    s_err = [e for e, m in zip(err, method) if m == "single_step"]

    ax.semilogy(composed, c_err, "o", color=INVERSE_RED, ms=7, label="composed (n=3,4)")
    ax.semilogy(single, s_err, "o", color=INK, ms=5, label="single elementary step")
    ax.axvline(4.5, color=GRAY_LIGHT, lw=0.6, ls="--")
    ax.text(3.2, 2e-15, "CORDIC ceiling", fontsize=7, color=GRAY_DARK)
    ax.set_xlabel("n", color=GRAY_DARK, fontsize=8)
    ax.set_ylabel("max angular / position error", color=GRAY_DARK, fontsize=8)
    ax.set_xlim(2, 25)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=GRAY_DARK, labelsize=7)
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    fig.savefig(out_dir / "B1_bridge.png", dpi=160, facecolor=PAPER)
    pdf.savefig(fig, facecolor=PAPER)
    plt.close(fig)


def main():
    run = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../measures/bridge/runs/2026-09-24")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("pass1/synthesis")
    out.mkdir(parents=True, exist_ok=True)
    with (run / "bridge.csv").open() as f:
        rows = list(csv.DictReader(f))
    with PdfPages(out / "Bridge_Set.pdf") as pdf:
        sheet_B1(rows, out, pdf)
    print("wrote", out / "Bridge_Set.pdf")


if __name__ == "__main__":
    main()
