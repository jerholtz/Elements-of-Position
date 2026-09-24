#!/usr/bin/env python3
"""Sheets for The Cut. Read the RH kernel tables. Do not hunt roots."""
import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs/2026-09-24_n200"
OUT = ROOT / "drawings"
OUT.mkdir(parents=True, exist_ok=True)

PAPER, INK, DIM, ACCENT = "#f3f0e8", "#161616", "#8a8680", "#8b3a3a"


def rows(name):
    return list(csv.DictReader(open(RUN / name)))


def title(fig, code, name, note=""):
    fig.subplots_adjust(left=0.10, right=0.96, top=0.88, bottom=0.12)
    fig.text(0.10, 0.955, "ELEMENTS OF POSITION  ·  EXPLORATORY", fontsize=7, color=DIM)
    fig.text(0.10, 0.928, code, fontsize=13, color=INK, fontweight="bold")
    fig.text(0.10, 0.902, name, fontsize=9, color=INK)
    fig.text(0.96, 0.955, note, fontsize=7, color=DIM, ha="right")
    fig.text(0.10, 0.03, "kernel run 2026-09-24  n=200", fontsize=6.5, color=DIM)


def save(fig, name):
    fig.savefig(OUT / name, dpi=160, facecolor=PAPER)
    plt.close(fig)
    print("wrote", name)


def C1():
    st = rows("stations.csv")[:16]
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "C1", "Stations on the ruler", "origin n/2  ·  inverse 1/n")
    ns = [int(r["n"]) for r in st]
    ax.plot([0, 16], [0, 0], color=INK, lw=0.8)
    for r in st:
        n = int(r["n"])
        ax.plot([n], [0], "o", color=ACCENT if int(r["is_prime"]) else INK, ms=6 if n in (1, 2, 5) else 4)
    ax.text(1, 0.18, "lock", ha="center", fontsize=8, color=INK)
    ax.text(2, -0.22, "2", ha="center", fontsize=8, color=INK)
    ax.text(5, 0.18, "five", ha="center", fontsize=8, color=ACCENT)
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.6, 0.6)
    ax.axis("off")
    save(fig, "C1_stations.png")


def C2():
    w = [r for r in rows("weights.csv") if r["n"] == "5"]
    sig = [float(r["sigma"]) for r in w]
    left = [float(r["left"]) for r in w]
    right = [float(r["right"]) for r in w]
    gm = [float(r["gm"]) for r in w]
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "C2", "Complementary interiors at n=5", "GM = 5^{-1/2}")
    ax.plot(sig, left, color=INK, marker="o", label="n^{-σ}")
    ax.plot(sig, right, color=ACCENT, marker="o", label="n^{-(1-σ)}")
    ax.plot(sig, gm, color=DIM, ls="--", label="GM")
    ax.axvline(0.5, color=DIM, lw=0.4)
    ax.legend(frameon=False, fontsize=8)
    ax.set_xlabel("σ")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "C2_weights.png")


def C3():
    d = rows("dual_real.csv")
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "C3", "Dual sum at height 0", "floor is Σ 2 n^{-1/2}")
    ax.plot([float(r["sigma"]) for r in d], [float(r["sum_ends"]) for r in d], color=INK, marker="o")
    ax.axvline(0.5, color=ACCENT, lw=0.5)
    ax.set_xlabel("σ")
    ax.set_ylabel("sum of ends")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "C3_dual_real.png")


def C4():
    o = rows("one_centre.csv")
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "C4", "One centre  ·  |left/right| = n^{1-2σ}", "equals 1 only on the cut")
    for n in sorted({int(r["n"]) for r in o}):
        chunk = [r for r in o if int(r["n"]) == n]
        ax.semilogy(
            [float(r["sigma"]) for r in chunk],
            [float(r["abs_chi_proxy"]) for r in chunk],
            marker="o",
            label=f"n={n}",
        )
    ax.axhline(1, color=DIM, lw=0.4)
    ax.axvline(0.5, color=ACCENT, lw=0.5)
    ax.legend(frameon=False, fontsize=8)
    ax.set_xlabel("σ")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "C4_one_centre.png")


def C5():
    dh = rows("dual_height.csv")
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "C5", "Dual sum with height", "|S(σ,t)| = |S(1-σ,t)|")
    ts = sorted({float(r["t"]) for r in dh})
    for t in ts:
        chunk = [r for r in dh if float(r["t"]) == t]
        chunk = sorted(chunk, key=lambda r: float(r["sigma"]))
        ax.plot(
            [float(r["sigma"]) for r in chunk],
            [float(r["abs"]) for r in chunk],
            marker="o",
            label=f"t={t:g}",
        )
    ax.axvline(0.5, color=DIM, lw=0.4)
    ax.legend(frameon=False, fontsize=8)
    ax.set_xlabel("σ")
    ax.set_ylabel("|S|")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "C5_dual_height.png")


def C6():
    dp = [r for r in rows("dated_product.csv") if float(r["t"]) == 0.0]
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    title(fig, "C6", "Dated product at t=0", "never zero  ·  grows with depth")
    for sig in (0.2, 0.5, 0.8):
        chunk = [r for r in dp if abs(float(r["sigma"]) - sig) < 1e-12]
        chunk = sorted(chunk, key=lambda r: int(r["p_cut"]))
        ax.semilogy(
            [int(r["p_cut"]) for r in chunk],
            [float(r["abs"]) for r in chunk],
            marker="o",
            label=f"σ={sig}",
        )
    ax.legend(frameon=False, fontsize=8)
    ax.set_xlabel("p_cut")
    ax.set_ylabel("|P|")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "C6_dated_product.png")


if __name__ == "__main__":
    C1()
    C2()
    C3()
    C4()
    C5()
    C6()
    print("->", OUT)
