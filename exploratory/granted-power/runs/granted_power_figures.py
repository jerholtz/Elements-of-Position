#!/usr/bin/env python3
"""Figures and checks for On a Granted Power.

Recomputes the increment paths and the frozen-s growth table.
Inner is 1/m.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("/home/workdir/artifacts")
PAPER = "#f3f0e8"
INK = "#161616"
DIM = "#8a8680"
RULE = "#c9c4b8"
ACCENT = "#8b3a3a"


def B_dB(s: complex, logs: np.ndarray):
    a = np.exp(-s * logs)
    b = np.exp(-(1 - s) * logs)
    return np.sum(a - b), np.sum(-logs * a - logs * b)


def newton(s0: complex, logs: np.ndarray, steps: int = 40):
    s = complex(s0)
    for _ in range(steps):
        v, d = B_dB(s, logs)
        if abs(d) < 1e-18:
            break
        s2 = s - v / d
        if abs(s2 - s) < 1e-13:
            s = s2
            break
        s = s2
    v, _ = B_dB(s, logs)
    return s, abs(v)


def absB(s: complex, N: int) -> float:
    m = np.arange(1, N + 1, dtype=float)
    return float(abs(np.sum(m ** (-s) - m ** (-(1 - s)))))


def path(s0: complex, n0: int, n1: int):
    s = complex(s0)
    rows = []
    for N in range(n0, n1 + 1):
        logs = np.log(np.arange(1, N + 1, dtype=float))
        z, res = newton(s, logs)
        rows.append((N, z.real, z.imag, abs(z.real - 0.5), res))
        s = z
    return rows


def sheet(fig, code, title, foot_l="", foot_r=""):
    fig.text(0.07, 0.955, "ELEMENTS OF POSITION", fontsize=7, color=DIM)
    fig.text(0.07, 0.928, code, fontsize=13, color=INK, fontweight="bold")
    fig.text(0.07, 0.902, title, fontsize=9, color=INK)
    fig.text(0.97, 0.955, "sheet", fontsize=7, color=DIM, ha="right")
    fig.text(0.07, 0.035, foot_l, fontsize=6.5, color=DIM)
    fig.text(0.97, 0.035, foot_r, fontsize=6.5, color=DIM, ha="right")


def style(ax):
    ax.set_facecolor(PAPER)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(RULE)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(colors=DIM, labelsize=7)


def main():
    print("recompute path L  N=128..180  start 0.80267+19.398j")
    L = path(0.80267 + 19.398j, 128, 180)
    print("  N=128", L[0])
    print("  land", next(r for r in L if r[3] < 1e-4))

    print("recompute path G  N=96..180  start 0.65487+17.2563j")
    G = path(0.65487 + 17.2563j, 96, 180)
    print("  N=96", G[0])
    print("  land", next(r for r in G if r[3] < 1e-4))

    with open(OUT / "path_L.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["N", "sigma", "t", "dist", "residual"])
        w.writerows(L)
    with open(OUT / "path_G.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["N", "sigma", "t", "dist", "residual"])
        w.writerows(G)

    # GP1 real part vs N
    fig = plt.figure(figsize=(11, 8.5), facecolor=PAPER)
    ax = fig.add_axes([0.10, 0.12, 0.84, 0.74])
    style(ax)
    ax.plot([r[0] for r in G], [r[1] for r in G], color=ACCENT, lw=1.3, label="G")
    ax.plot([r[0] for r in L], [r[1] for r in L], color=INK, lw=1.2, label="L")
    ax.axhline(0.5, color=RULE, lw=0.6)
    ax.set_xlabel("hit N", fontsize=8, color=DIM)
    ax.set_ylabel("Re(s)", fontsize=8, color=DIM)
    ax.legend(frameon=False, fontsize=8)
    sheet(fig, "GP1", "Paths G and L     real part of the tilt",
          "G away twenty hits then in", "land at 173 and 164")
    fig.savefig(OUT / "GP1_paths_sigma.png", dpi=170, facecolor=PAPER)
    plt.close()

    # GP2 s-plane
    fig = plt.figure(figsize=(11, 8.5), facecolor=PAPER)
    ax = fig.add_axes([0.10, 0.12, 0.84, 0.74])
    style(ax)
    ax.plot([r[1] for r in G], [r[2] for r in G], color=ACCENT, lw=1.3, label="G")
    ax.plot([r[1] for r in L], [r[2] for r in L], color=INK, lw=1.2, label="L")
    ax.axvline(0.5, color=RULE, lw=0.6)
    ax.plot(G[0][1], G[0][2], "o", color=ACCENT, ms=6)
    ax.plot(L[0][1], L[0][2], "o", color=INK, ms=6)
    ax.set_xlabel("Re(s)", fontsize=8, color=DIM)
    ax.set_ylabel("Im(s)", fontsize=8, color=DIM)
    ax.legend(frameon=False, fontsize=8)
    sheet(fig, "GP2", "Same paths in the plane of the granted power",
          "vertical rule is equal weight", "dots are the starting hits")
    fig.savefig(OUT / "GP2_plane.png", dpi=170, facecolor=PAPER)
    plt.close()

    # GP3 growth
    Ns = np.array([32, 64, 128, 256, 512, 1024, 2048])
    on = np.array([absB(0.5 + 18j, int(n)) for n in Ns])
    off = np.array([absB(0.8 + 18j, int(n)) for n in Ns])
    fig = plt.figure(figsize=(11, 8.5), facecolor=PAPER)
    ax = fig.add_axes([0.10, 0.12, 0.84, 0.74])
    style(ax)
    ax.plot(Ns, on / np.sqrt(Ns), color=INK, lw=1.25, label="σ=1/2    |B|/√N")
    ax.plot(Ns, off / Ns ** 0.8, color=ACCENT, lw=1.25, label="σ=0.8    |B|/N^0.8")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("hit N", fontsize=8, color=DIM)
    ax.set_ylabel("scaled |B_N|", fontsize=8, color=DIM)
    ax.legend(frameon=False, fontsize=8)
    sheet(fig, "GP3", "Frozen s     on-line rate against the faster writing",
          "t=18", "α(σ)=max(σ,1−σ)")
    fig.savefig(OUT / "GP3_growth.png", dpi=170, facecolor=PAPER)
    plt.close()

    print("wrote GP1 GP2 GP3 and path csv")
    print("increment check L at N=128: leftover equals new term")
    logs = np.log(np.arange(1, 129, dtype=float))
    s128, _ = newton(0.80267 + 19.398j, logs)
    term = 129 ** (-s128) - 129 ** (-(1 - s128))
    m = np.arange(1, 130, dtype=float)
    Bnext = np.sum(m ** (-s128) - m ** (-(1 - s128)))
    print("  |term|", abs(term), " |B_129(s_128)|", abs(Bnext), " diff", abs(Bnext - term))


if __name__ == "__main__":
    main()
