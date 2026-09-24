#!/usr/bin/env python3
"""Drawing pass 2. Plates the frozen papers cite. Reads tables. Does not walk."""
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle

ROOT = Path(__file__).resolve().parents[1]
WALK = ROOT / "kernels/walk/runs/2026-09-24_h0.002_n200000"
NGON = ROOT / "kernels/ngon/runs/2026-09-24_n1-60"
OUT = Path(__file__).resolve().parent / "pass2"
OUT.mkdir(parents=True, exist_ok=True)

PAPER, INK, DIM, ACCENT = "#f3f0e8", "#161616", "#8a8680", "#8b3a3a"
PHI = (1 + 5**0.5) / 2


def title(fig, code, name, note=""):
    fig.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.10)
    fig.text(0.08, 0.955, "ELEMENTS OF POSITION", fontsize=7, color=DIM)
    fig.text(0.08, 0.928, code, fontsize=13, color=INK, fontweight="bold")
    fig.text(0.08, 0.902, name, fontsize=9, color=INK)
    fig.text(0.96, 0.955, note, fontsize=7, color=DIM, ha="right")
    fig.text(0.08, 0.03, "24 September 2026 run", fontsize=6.5, color=DIM)


def save(fig, name):
    fig.savefig(OUT / name, dpi=160, facecolor=PAPER)
    plt.close(fig)
    print("wrote", name)


def sheet_CU1():
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "CU1", "The pair on the unit", "Part I")
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([-2.3, 2.3], [0, 0], color=INK, lw=0.8)
    ax.add_patch(Circle((0, 0), 1, fill=False, ec=INK, lw=1.1))
    for x, lab, col in [(-1, "-1", INK), (1, "1", INK), (2, "2", INK), (0.5, "1/2", ACCENT)]:
        ax.plot([x], [0], "o", color=col, ms=6)
        ax.text(x, -0.22, lab, ha="center", fontsize=9, color=col)
    ax.plot([1], [0], "o", color=INK, ms=8)
    ax.text(0, 1.08, "bind", ha="center", fontsize=8, color=DIM)
    ax.text(2, 0.18, "outer", ha="center", fontsize=8, color=INK)
    ax.text(0.5, 0.18, "primary cut", ha="center", fontsize=8, color=ACCENT)
    save(fig, "CU1_pair.png")


def sheet_L1():
    hits = list(csv.DictReader(open(WALK / "crossings.csv")))
    m = [int(r["m"]) for r in hits]
    hy = [float(r["hy"]) for r in hits]
    y = [mi * hi for mi, hi in zip(m, hy)]
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "L1", "Residual elevation  ·  m · h_y", "Part III")
    ax.plot(m, y, color=INK, lw=0.9)
    ax.axhline(0, color=DIM, lw=0.4)
    ax.set_xlabel("m", color=DIM)
    ax.set_ylabel("m · h_y", color=DIM)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "L1_residual.png")


def sheet_L2():
    pairs = list(csv.DictReader(open(WALK / "pairs.csv")))
    m = [int(r["m"]) for r in pairs]
    tau = [float(r["tau"]) for r in pairs]
    mouth = [2 * math.sqrt(max(0, 1 - 1 / mi**2)) if mi else 0 for mi in m]
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "L2", "Leftover and mouth", "Part III")
    ax.plot(m, tau, color=INK, lw=1.0, label="τ(m)")
    ax.plot(m, mouth, color=ACCENT, lw=1.0, label="mouth  2√(1-1/m²)")
    ax.axhline(2, color=DIM, lw=0.4, ls=":")
    ax.legend(frameon=False, fontsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "L2_mouth.png")


def sheet_M1():
    verts = []
    for k in range(5):
        t = math.pi / 2 + 2 * math.pi * k / 5
        verts.append((2.5 * math.cos(t), 2.5 * math.sin(t)))
    inv = [(x / 25 * 1, y / 25 * 1) for x, y in [(5 * vx / 2.5, 5 * vy / 2.5) for vx, vy in verts]]
    # inverse locus radius 1/5
    inv = [(0.2 * math.cos(math.pi / 2 + 2 * math.pi * k / 5),
            0.2 * math.sin(math.pi / 2 + 2 * math.pi * k / 5)) for k in range(5)]
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "M1", "Marriage at five", "Part IV  ·  twocos(5)=φ")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Circle((0, 0), 2.5, fill=False, ec=INK, lw=0.8))
    ax.add_patch(Circle((0, 0), 2.5 / PHI, fill=False, ec=DIM, lw=0.6, ls="--"))
    ax.add_patch(Circle((0, 0), 0.2, fill=False, ec=ACCENT, lw=0.9))
    xs, ys = zip(*(verts + verts[:1]))
    ax.plot(xs, ys, color=INK, lw=1.2)
    ix, iy = zip(*(inv + inv[:1]))
    ax.plot(ix, iy, color=ACCENT, lw=1.0)
    ax.text(0, -3.05, "diameter 5  ·  inverse radius 1/5  ·  dashed R/φ", ha="center", fontsize=8, color=DIM)
    save(fig, "M1_marriage.png")


def sheet_M2():
    ks = list(range(2, 16))
    err = [1 / (2 * PHI**k) for k in ks]
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "M2", "Docking error  1/(2 φ^k)", "Part IV")
    ax.semilogy(ks, err, color=INK, lw=1.1, marker="o", ms=4)
    ax.axhline(0.0172209, color=ACCENT, lw=0.4, ls=":")
    ax.text(7.1, 0.017, "k=7", fontsize=8, color=ACCENT)
    ax.set_xlabel("k", color=DIM)
    ax.set_ylabel("error", color=DIM)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "M2_docking.png")


def sheet_G1():
    hits = list(csv.DictReader(open(WALK / "crossings.csv")))
    H0 = int(hits[0]["gap"])
    word = ["L" if int(r["gap"]) == H0 else "S" for r in hits]
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "G1", "Gap word  ·  25 × LLLLS + LL", "Part V")
    ax.set_xlim(0, 128)
    ax.set_ylim(-1.2, 1.6)
    ax.axis("off")
    for i, ch in enumerate(word, start=1):
        ax.add_patch(plt.Rectangle((i - 0.45, 0), 0.9, 0.9 if ch == "L" else 0.45,
                                   facecolor=INK if ch == "L" else ACCENT, edgecolor="none"))
    ax.text(64, 1.25, "L = 1571   S = 1570", ha="center", fontsize=9, color=DIM)
    save(fig, "G1_word.png")


def sheet_SB1():
    def path(steps):
        lo, hi, node = (0, 1), (1, 0), (1, 1)
        pts = [node]
        for s in steps:
            if s == "R":
                lo = node
            else:
                hi = node
            node = (lo[0] + hi[0], lo[1] + hi[1])
            pts.append(node)
        return pts

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "SB1", "Stern–Brocot spines", "Part V  ·  the pair")
    right = path("R" * 8)
    left = path("L" * 8)
    ax.plot([p[0] / p[1] for p in right], range(len(right)), color=INK, marker="o", ms=4, label="right  n")
    ax.plot([p[0] / p[1] for p in left], range(len(left)), color=ACCENT, marker="o", ms=4, label="left  1/n")
    ax.set_xlabel("value", color=DIM)
    ax.set_ylabel("depth", color=DIM)
    ax.legend(frameon=False, fontsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "SB1_spines.png")


if __name__ == "__main__":
    sheet_CU1()
    sheet_L1()
    sheet_L2()
    sheet_M1()
    sheet_M2()
    sheet_G1()
    sheet_SB1()
    print("pass2 ->", OUT)
