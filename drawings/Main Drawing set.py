#!/usr/bin/env python3
"""
Elements of Position — drawing set.

Reads the three CSVs the kernel writes. Does not walk.
The spiral is the hit vertices: P_m = m u_m, Q_m = u_m / m.
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle

PAPER = "#f3f0e8"
INK = "#161616"
DIM = "#8a8680"
RULE = "#c9c4b8"
ACCENT = "#8b3a3a"

LW_CON = 0.25
LW_OBJ = 0.55
LW_CUT = 1.15
LW_PROF = 1.55


def read_dicts(path: Path):
    with path.open() as f:
        return list(csv.DictReader(f))


def read_summary(path: Path):
    out = {}
    with path.open() as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) >= 2:
                out[row[0]] = row[1]
    return out


def derive(hits_raw, pairs_raw, summary):
    """Build the model from the kernel tables only."""
    pairs = {int(float(p["m"])): p for p in pairs_raw}
    H0 = int(float(summary["H0"]))
    hits = []
    for raw in hits_raw:
        m = int(float(raw["m"]))
        hx, hy = float(raw["hx"]), float(raw["hy"])
        gap = int(float(raw["gap"]))
        pr = pairs[m]
        if m == 1:
            gap_kind = "first"
        elif gap == H0:
            gap_kind = "long"
        elif gap == H0 - 1:
            gap_kind = "short"
        else:
            gap_kind = "other"
        r = float(pr["r"])
        rin = float(pr["r_in"])
        hits.append(
            {
                "m": m,
                "j": int(float(raw["j"])),
                "gap": gap,
                "side": raw["side"],
                "gap_kind": gap_kind,
                "hx": hx,
                "hy": hy,
                "r": r,
                "r_in": rin,
                "am": float(pr["am"]),
                "gm": 1.0,
                "tau": float(pr["tau"]),
                "Px": r * hx,
                "Py": r * hy,
                "Qx": rin * hx,
                "Qy": rin * hy,
                "z": float(m),
                "hy_over_m": abs(hy) / m,
            }
        )

    hist = Counter(c["gap"] for c in hits)
    kinds = Counter(c["gap_kind"] for c in hits)
    word = "".join(
        "." if c["gap_kind"] == "first" else ("S" if c["gap_kind"] == "short" else "L")
        for c in hits
    )
    h = float(summary["h"])
    wall_1 = math.hypot(hits[0]["hx"] - 1.0, hits[0]["hy"])
    wall_12 = math.hypot(hits[1]["hx"] - hits[0]["hx"], hits[1]["hy"] - hits[0]["hy"])

    summary["_h"] = h
    summary["_H0"] = H0
    summary["_n"] = int(float(summary["n_hits"]))
    summary["_steps"] = int(float(summary["steps"]))
    summary["_mean_h"] = float(summary["mean_gap_times_h"])
    summary["count_gap_H0"] = str(hist.get(H0, 0))
    summary["count_gap_H0m1"] = str(hist.get(H0 - 1, 0))
    summary["n_short"] = str(kinds.get("short", 0))
    summary["n_long"] = str(kinds.get("long", 0))
    summary["gap_word"] = word
    summary["H0_times_h"] = str(H0 * h)
    summary["wall_chord_start_to_m1"] = f"{wall_1:.10f}"
    summary["wall_chord_m1_to_m2"] = f"{wall_12:.10f}"
    return hits, summary


def new_sheet(landscape=True):
    w, ht = (11.0, 8.5) if landscape else (8.5, 11.0)
    fig, ax = plt.subplots(figsize=(w, ht), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    return fig, ax


def titleblock(fig, code, name, note, summary):
    fig.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.08)
    fig.text(0.07, 0.955, "ELEMENTS OF POSITION", fontsize=7, color=DIM, ha="left")
    fig.text(0.07, 0.928, code, fontsize=13, color=INK, ha="left", fontweight="bold")
    fig.text(0.07, 0.902, name, fontsize=9, color=INK, ha="left")
    fig.text(0.97, 0.955, "set", fontsize=7, color=DIM, ha="right")
    fig.text(0.97, 0.928, note, fontsize=7, color=DIM, ha="right")
    fig.text(
        0.97,
        0.035,
        f"h = {summary['h']}    steps = {summary['_steps']}    "
        f"H0 = {summary['_H0']}    hits = {summary['_n']}",
        fontsize=6.5,
        color=DIM,
        ha="right",
    )
    fig.text(0.07, 0.035, "cut is y = 0", fontsize=6.5, color=DIM, ha="left")


def bare(ax):
    ax.set_aspect("equal")
    ax.axis("off")


def scale_bar(ax, x0, y0, length=1.0):
    ax.plot([x0, x0 + length], [y0, y0], color=INK, lw=0.7, solid_capstyle="butt", zorder=6)
    ax.plot([x0, x0], [y0 - 0.08 * length, y0 + 0.08 * length], color=INK, lw=0.7, zorder=6)
    ax.plot(
        [x0 + length, x0 + length],
        [y0 - 0.08 * length, y0 + 0.08 * length],
        color=INK,
        lw=0.7,
        zorder=6,
    )


def save(fig, out: Path, pdf: PdfPages):
    fig.savefig(out, dpi=170, facecolor=PAPER)
    pdf.savefig(fig, facecolor=PAPER)
    plt.close(fig)


def J(hx, hy):
    return (-hy, hx)


def kite_points(c):
    m = c["m"]
    ux, uy = c["hx"], c["hy"]
    t = math.sqrt(max(0.0, 1.0 - 1.0 / (m * m)))
    jx, jy = J(ux, uy)
    return (ux / m + t * jx, uy / m + t * jy), (ux / m - t * jx, uy / m - t * jy)


def sheet_A0(out, pdf, summary, hits):
    fig, ax = new_sheet()
    bare(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    titleblock(fig, "A0", "Index", "one model · views and details of the same vertices", summary)
    ax.text(
        0.55,
        7.20,
        "Shear, bind, stand on the diameter, count.\n"
        "The model is the walk stood up: z = count.",
        fontsize=10,
        color=INK,
    )
    boxes = [
        (0.55, 4.55, "P1  PLAN", "look down z\nouter r = z\ninverse r = 1/z"),
        (3.20, 4.55, "S1  SECTION", "cut y = 0\nevery hit lies here\nouter z = |x|"),
        (5.85, 4.55, "E1  ELEVATION", "face off the cut\ny of the outer point\nis m · hy"),
        (8.50, 4.55, "O1  OBLIQUE", "the same vertices\nun-cut"),
    ]
    for x, y, h, body in boxes:
        ax.add_patch(
            plt.Rectangle((x, y), 2.35, 2.05, fill=True, facecolor="#eeeae1", edgecolor=INK, lw=0.5)
        )
        ax.text(x + 0.12, y + 1.72, h, fontsize=8.5, color=INK, fontweight="bold")
        ax.text(x + 0.12, y + 1.05, body, fontsize=7, color=INK, va="top")
    fig.text(
        0.07,
        0.455,
        "D1 lock  m = 1      D2 pair  m = 2      D3 short hit      D4 one LLLLS cycle",
        fontsize=8,
        color=INK,
        ha="left",
    )
    fig.text(
        0.07,
        0.418,
        "D5 four points      D6 kite on OP      D7 inversion swap      W1 heading on the bind",
        fontsize=8,
        color=INK,
        ha="left",
    )
    fig.text(0.07, 0.355, "Outer locus in ink.", fontsize=8, color=INK, ha="left")
    fig.text(0.225, 0.355, "Inverse locus", fontsize=8, color=ACCENT, ha="left")
    fig.text(0.338, 0.355, "in the one accent.", fontsize=8, color=INK, ha="left")
    fig.text(
        0.07,
        0.318,
        "Nothing is drawn that is not a vertex or a cut of this model.",
        fontsize=8,
        color=INK,
        ha="left",
    )
    ax.text(
        0.55,
        1.45,
        f"H0 = {summary['_H0']}     mean gap · h = {summary['_mean_h']:.8f}\n"
        f"gaps {summary['gap_min']} and {summary['gap_max']}     "
        f"{summary['count_gap_H0']} long, {summary['count_gap_H0m1']} short\n"
        f"wall chord start→1 = {float(summary['wall_chord_start_to_m1']):.8f}     "
        f"1→2 = {float(summary['wall_chord_m1_to_m2']):.8f}",
        fontsize=8,
        color=INK,
    )
    save(fig, out / "A0_index.png", pdf)


def sheet_W1(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "W1", "Heading", "the bind, the cut, the stations the kernel recorded", summary)
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=INK, lw=LW_PROF))
    ax.plot([-1.25, 1.25], [0, 0], color=INK, lw=LW_CUT, zorder=3)
    ax.plot(1.0, 0.0, "o", color=DIM, ms=4)
    ax.annotate("start", (1.0, 0.0), textcoords="offset points", xytext=(6, 5), fontsize=7, color=DIM)
    ax.scatter([c["hx"] for c in hits], [c["hy"] for c in hits], s=8, c=INK, zorder=4, linewidths=0)
    ax.plot(hits[0]["hx"], hits[0]["hy"], "o", color=INK, ms=5)
    ax.annotate(
        "1",
        (hits[0]["hx"], hits[0]["hy"]),
        textcoords="offset points",
        xytext=(-10, -11),
        fontsize=7,
        color=INK,
    )
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    bare(ax)
    save(fig, out / "W1_heading.png", pdf)


def sheet_P1(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "P1", "Plan", "look down the count · spiral of the recorded vertices", summary)
    ax.plot([c["Px"] for c in hits], [c["Py"] for c in hits], color=INK, lw=LW_OBJ, solid_capstyle="round")
    ax.plot([c["Qx"] for c in hits], [c["Qy"] for c in hits], color=ACCENT, lw=LW_OBJ, solid_capstyle="round")
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=DIM, lw=LW_CUT))
    Rmax = max(c["r"] for c in hits)
    ax.plot([-Rmax, Rmax], [0, 0], color=INK, lw=LW_CUT, zorder=3)
    ax.scatter([c["Px"] for c in hits], [c["Py"] for c in hits], s=8, c=INK, zorder=4, linewidths=0)
    ax.scatter([c["Qx"] for c in hits], [c["Qy"] for c in hits], s=8, c=ACCENT, zorder=4, linewidths=0)
    ax.plot(hits[0]["Px"], hits[0]["Py"], "o", color=INK, ms=4.5)
    ax.annotate("1", (hits[0]["Px"], hits[0]["Py"]), textcoords="offset points", xytext=(-8, -10), fontsize=7, color=INK)
    if len(hits) >= 2:
        ax.annotate("2", (hits[1]["Px"], hits[1]["Py"]), textcoords="offset points", xytext=(5, -10), fontsize=7, color=INK)
        ax.annotate("1/2", (hits[1]["Qx"], hits[1]["Qy"]), textcoords="offset points", xytext=(5, 4), fontsize=7, color=ACCENT)
    pad = Rmax * 0.12
    ax.set_xlim(-Rmax - pad, Rmax + pad)
    ax.set_ylim(-Rmax - pad, Rmax + pad)
    bare(ax)
    save(fig, out / "P1_plan.png", pdf)


def sheet_S1(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "S1", "Section  y = 0", "the cut contains every hit", summary)
    n = hits[-1]["m"]
    xs = np.linspace(0.2, n * 1.02, 400)
    ax.plot(xs, xs, color=RULE, lw=LW_CON, ls=":")
    ax.plot(-xs, xs, color=RULE, lw=LW_CON, ls=":")
    ax.plot(xs, 1.0 / xs, color=RULE, lw=LW_CON, ls=":")
    ax.plot(-xs, 1.0 / xs, color=RULE, lw=LW_CON, ls=":")
    ax.plot([0, 0], [0, n], color=INK, lw=LW_CUT)
    left = [c for c in hits if c["Px"] < 0]
    right = [c for c in hits if c["Px"] >= 0]
    for group in (left, right):
        ax.plot([c["Px"] for c in group], [c["z"] for c in group], color=INK, lw=LW_OBJ, marker="o", ms=2.0)
        ax.plot([c["Qx"] for c in group], [c["z"] for c in group], color=ACCENT, lw=LW_OBJ, marker="o", ms=2.0)
    ax.plot(hits[0]["Px"], hits[0]["z"], "o", color=INK, ms=5)
    ax.annotate("1", (hits[0]["Px"], hits[0]["z"]), textcoords="offset points", xytext=(-12, 3), fontsize=7, color=INK)
    if len(hits) >= 2:
        ax.annotate("2", (hits[1]["Px"], hits[1]["z"]), textcoords="offset points", xytext=(5, 3), fontsize=7, color=INK)
        ax.annotate("1/2", (hits[1]["Qx"], hits[1]["z"]), textcoords="offset points", xytext=(5, -10), fontsize=7, color=ACCENT)
    ax.set_xlim(-n * 1.08, n * 1.08)
    ax.set_ylim(-0.4, n + 2)
    scale_bar(ax, 0.0, 0.0, 1.0)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    save(fig, out / "S1_section.png", pdf)


def sheet_E1(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "E1", "Elevation", "thickness off the cut · y = m hy", summary)
    m = np.array([c["m"] for c in hits])
    yout = np.array([c["m"] * c["hy"] for c in hits])
    yin = np.array([c["r_in"] * c["hy"] for c in hits])
    ax.axhline(0, color=INK, lw=LW_CUT)
    ax.plot(m, yout, color=INK, lw=LW_OBJ)
    ax.plot(m, yin, color=ACCENT, lw=LW_CON)
    for c, yo in zip(hits, yout):
        col = ACCENT if c["gap_kind"] == "short" else INK
        ax.plot(c["m"], yo, "o", color=col, ms=3.2 if c["gap_kind"] == "short" else 2.0)
    ax.set_xlim(0, hits[-1]["m"] + 2)
    ymax = max(abs(yout.max()), abs(yout.min()), 0.02) * 1.25
    ax.set_ylim(-ymax, ymax)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(RULE)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(colors=DIM, labelsize=7)
    ax.set_xlabel("m", fontsize=7, color=DIM)
    ax.set_ylabel("m · hy", fontsize=7, color=DIM)
    save(fig, out / "E1_elevation.png", pdf)


def sheet_O1(out, pdf, summary, hits):
    fig = plt.figure(figsize=(11, 8.5), facecolor=PAPER)
    ax = fig.add_subplot(111, projection="3d", facecolor=PAPER)
    titleblock(fig, "O1", "Oblique", "same vertices, un-cut", summary)
    ax.plot([c["Px"] for c in hits], [c["Py"] for c in hits], [c["z"] for c in hits], color=INK, lw=0.7)
    ax.plot([c["Qx"] for c in hits], [c["Qy"] for c in hits], [c["z"] for c in hits], color=ACCENT, lw=0.7)
    ax.plot([c["Px"] for c in hits], [c["Py"] for c in hits], [c["z"] for c in hits], "o", color=INK, ms=2.0)
    ax.plot([c["Qx"] for c in hits], [c["Qy"] for c in hits], [c["z"] for c in hits], "o", color=ACCENT, ms=2.0)
    ax.plot([0, 0], [0, 0], [0, hits[-1]["z"]], color=INK, lw=0.6)
    ax.view_init(elev=18, azim=-62)
    ax.set_facecolor(PAPER)
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor(PAPER)
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_axis_off()
    try:
        ax.set_box_aspect((1, 1, 1.05))
    except Exception:
        pass
    save(fig, out / "O1_oblique.png", pdf)


def sheet_D1(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "D1", "Detail  ·  lock", "m = 1  ·  the bind is the pair", summary)
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=INK, lw=LW_PROF))
    ax.plot([-1.35, 1.35], [0, 0], color=INK, lw=LW_CUT)
    ax.plot([0, 0], [-1.35, 1.35], color=RULE, lw=LW_CON)
    ax.plot(hits[0]["Px"], hits[0]["Py"], "o", color=INK, ms=7)
    ax.plot(1.0, 0.0, "o", color=DIM, ms=4)
    ax.annotate("start", (1.0, 0.0), textcoords="offset points", xytext=(6, 4), fontsize=7, color=DIM)
    ax.annotate("(1,1)", (hits[0]["Px"], hits[0]["Py"]), textcoords="offset points", xytext=(-22, -12), fontsize=8, color=INK)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    scale_bar(ax, 0.0, -1.28, 1.0)
    bare(ax)
    save(fig, out / "D1_lock.png", pdf)


def sheet_D2(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "D2", "Detail  ·  pair", "m = 2  ·  (2, 1/2) on the home wall", summary)
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=DIM, lw=LW_CON))
    ax.plot([-0.4, 2.6], [0, 0], color=INK, lw=LW_CUT)
    c = hits[1]
    ax.plot([0, c["Px"]], [0, c["Py"]], color=INK, lw=LW_OBJ)
    ax.plot(c["Px"], c["Py"], "o", color=INK, ms=6)
    ax.plot(c["Qx"], c["Qy"], "o", color=ACCENT, ms=6)
    ax.annotate("2", (c["Px"], c["Py"]), textcoords="offset points", xytext=(6, 4), fontsize=8, color=INK)
    ax.annotate("1/2", (c["Qx"], c["Qy"]), textcoords="offset points", xytext=(6, 4), fontsize=8, color=ACCENT)
    ax.set_xlim(-0.5, 2.7)
    ax.set_ylim(-1.2, 1.2)
    scale_bar(ax, 0.0, -0.85, 1.0)
    bare(ax)
    save(fig, out / "D2_pair.png", pdf)


def sheet_D3(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "D3", "Detail  ·  short hit", "heading reset to the cut", summary)
    shorts = [c for c in hits if c["gap_kind"] == "short"]
    c = next((s for s in shorts if int(s["m"]) == 25), shorts[len(shorts) // 2])
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=DIM, lw=LW_CON))
    ax.plot([-1.4, 1.4], [0, 0], color=INK, lw=LW_CUT)
    ax.plot([0, c["hx"] * 1.15], [0, c["hy"] * 1.15], color=INK, lw=LW_OBJ)
    ax.plot(c["hx"], c["hy"], "o", color=ACCENT, ms=6)
    ax.annotate(
        f"m = {int(c['m'])}\nhy = {c['hy']:.6e}",
        (c["hx"], c["hy"]),
        textcoords="offset points",
        xytext=(8, 8),
        fontsize=7,
        color=INK,
    )
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    bare(ax)
    save(fig, out / "D3_short_hit.png", pdf)


def sheet_D4(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "D4", "Detail  ·  one cycle", "LLLLS in hy", summary)
    cycle = [c for c in hits if 1 <= c["m"] <= 5]
    m = [c["m"] for c in cycle]
    y = [c["m"] * c["hy"] for c in cycle]
    ax.axhline(0, color=INK, lw=LW_CUT)
    ax.plot(m, y, color=INK, lw=LW_PROF)
    for c, yo in zip(cycle, y):
        col = ACCENT if c["gap_kind"] == "short" else INK
        ax.plot(c["m"], yo, "o", color=col, ms=6)
        label = "S" if c["gap_kind"] == "short" else "L"
        ax.annotate(label, (c["m"], yo), textcoords="offset points", xytext=(0, 8), fontsize=7, color=col, ha="center")
    ax.set_xlim(0.5, 5.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(RULE)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(colors=DIM, labelsize=7)
    ax.set_xlabel("m", fontsize=7, color=DIM)
    ax.set_ylabel("m · hy", fontsize=7, color=DIM)
    save(fig, out / "D4_cycle.png", pdf)


def sheet_D5(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "D5", "Detail  ·  four points", "harmonic four of the pair  ·  generator ladder", summary)
    m = 10
    ax.plot([-1.4, 11.2], [1.6, 1.6], color=INK, lw=LW_CUT)
    for x, lab in [(-1, "-1"), (1 / m, "1/m"), (1, "1"), (m, "m")]:
        ax.plot(x, 1.6, "o", color=INK, ms=6)
        ax.annotate(lab, (x, 1.6), textcoords="offset points", xytext=(0, 10), fontsize=8, color=INK, ha="center")
    ax.annotate("pair  (1/m, m ; 1, −1) = −1", (4.5, 2.15), fontsize=8, color=INK, ha="center")
    ax.plot([-1.4, 11.2], [0.0, 0.0], color=INK, lw=LW_CUT)
    for x, lab in [(m - 2, "m−2"), (m - 1, "m−1"), (m, "m"), (m + 1, "m+1"), (m + 2, "m+2")]:
        ax.plot(x, 0.0, "o", color=INK, ms=6)
        ax.annotate(lab, (x, 0.0), textcoords="offset points", xytext=(0, -16), fontsize=8, color=INK, ha="center")
    ax.annotate("ladder  (m−2, m+2 ; m−1, m+1) = 1/9", (5.0, -0.85), fontsize=8, color=INK, ha="center")
    ax.set_xlim(-2.2, 13.0)
    ax.set_ylim(-1.6, 3.0)
    bare(ax)
    save(fig, out / "D5_four_points.png", pdf)


def sheet_D6(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "D6", "Detail  ·  kite on OP", "circle on OP meets the bind; the foot is Q", summary)
    c = hits[1]
    m = c["m"]
    Px, Py = c["Px"], c["Py"]
    Qx, Qy = c["Qx"], c["Qy"]
    Xp, Xm = kite_points(c)
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=DIM, lw=LW_CON))
    ax.add_patch(Circle((Px / 2, Py / 2), m / 2, fill=False, edgecolor=INK, lw=LW_OBJ))
    ax.plot([-0.4, Px * 1.08], [0, 0], color=INK, lw=LW_CUT)
    ax.plot([0, Px], [0, Py], color=INK, lw=LW_OBJ)
    ax.plot([0, Xp[0]], [0, Xp[1]], color=RULE, lw=LW_CON)
    ax.plot([0, Xm[0]], [0, Xm[1]], color=RULE, lw=LW_CON)
    ax.plot([Xp[0], Px], [Xp[1], Py], color=INK, lw=LW_OBJ)
    ax.plot([Xm[0], Px], [Xm[1], Py], color=INK, lw=LW_OBJ)
    ax.plot(Px, Py, "o", color=INK, ms=6)
    ax.plot(Qx, Qy, "o", color=ACCENT, ms=6)
    ax.plot(Xp[0], Xp[1], "o", color=INK, ms=4)
    ax.plot(Xm[0], Xm[1], "o", color=INK, ms=4)
    ax.annotate("P", (Px, Py), textcoords="offset points", xytext=(6, 4), fontsize=8, color=INK)
    ax.annotate("Q", (Qx, Qy), textcoords="offset points", xytext=(6, 4), fontsize=8, color=ACCENT)
    ax.annotate("X+", Xp, textcoords="offset points", xytext=(4, 4), fontsize=7, color=INK)
    ax.annotate("X−", Xm, textcoords="offset points", xytext=(4, -10), fontsize=7, color=INK)
    ax.set_xlim(-1.35, 2.55)
    ax.set_ylim(-1.55, 1.55)
    bare(ax)
    save(fig, out / "D6_kite.png", pdf)


def sheet_D7(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "D7", "Detail  ·  swap", "inversion of a collinear diameter  ·  same-wall pair m, m+2", summary)
    a, b = hits[1], hits[3]
    ox = 0.5 * (a["Px"] + b["Px"])
    oy = 0.5 * (a["Py"] + b["Py"])
    orad = 0.5 * math.hypot(b["Px"] - a["Px"], b["Py"] - a["Py"])
    ix = 0.5 * (a["Qx"] + b["Qx"])
    iy = 0.5 * (a["Qy"] + b["Qy"])
    irad = 0.5 * math.hypot(b["Qx"] - a["Qx"], b["Qy"] - a["Qy"])
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=DIM, lw=LW_CON))
    ax.add_patch(Circle((ox, oy), orad, fill=False, edgecolor=INK, lw=LW_OBJ))
    ax.add_patch(Circle((ix, iy), irad, fill=False, edgecolor=ACCENT, lw=LW_OBJ))
    ax.plot([-0.5, max(a["Px"], b["Px"]) * 1.05], [0, 0], color=INK, lw=LW_CUT)
    ax.plot(a["Px"], a["Py"], "o", color=INK, ms=6)
    ax.plot(b["Px"], b["Py"], "o", color=INK, ms=6)
    ax.plot(a["Qx"], a["Qy"], "o", color=ACCENT, ms=6)
    ax.plot(b["Qx"], b["Qy"], "o", color=ACCENT, ms=6)
    ax.annotate("P2", (a["Px"], a["Py"]), textcoords="offset points", xytext=(5, 5), fontsize=8, color=INK)
    ax.annotate("P4", (b["Px"], b["Py"]), textcoords="offset points", xytext=(5, 5), fontsize=8, color=INK)
    ax.annotate("Q2", (a["Qx"], a["Qy"]), textcoords="offset points", xytext=(5, 5), fontsize=8, color=ACCENT)
    ax.annotate("Q4", (b["Qx"], b["Qy"]), textcoords="offset points", xytext=(5, -12), fontsize=8, color=ACCENT)
    ax.set_xlim(-1.6, 5.0)
    ax.set_ylim(-2.2, 2.2)
    bare(ax)
    save(fig, out / "D7_swap.png", pdf)


def sheet_SCH1(out, pdf, summary, hits):
    fig, ax = new_sheet()
    bare(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    titleblock(fig, "SCH1", "Schedule  ·  two integers", "the count pays with neighbors", summary)
    word = summary["gap_word"].replace(".", "L")
    ax.text(0.55, 7.1, "gap word   (first hit written as L)", fontsize=8, color=DIM)
    y = 6.65
    for i in range(0, len(word), 64):
        ax.text(0.55, y, word[i : i + 64], fontsize=8, color=INK, family="monospace")
        y -= 0.28
    ax.text(0.55, 4.55, f"{summary['gap_max']}  ×  {summary['count_gap_H0']}", fontsize=14, color=INK)
    ax.text(0.55, 4.10, f"{summary['gap_min']}  ×  {summary['count_gap_H0m1']}", fontsize=14, color=INK)
    ax.text(0.55, 3.35, f"mean gap · h   =  {float(summary['mean_gap_times_h']):.8f}", fontsize=10, color=INK)
    ax.text(0.55, 2.95, f"H0 · h         =  {float(summary['H0_times_h']):.8f}", fontsize=10, color=DIM)
    ax.text(0.55, 2.55, f"λ = π / arctan h   =  {float(summary['lambda_pi_over_atan_h']):.6f}", fontsize=10, color=DIM)
    ax.text(
        0.55,
        1.85,
        "Twenty-five copies of LLLLS, then LL.\n"
        "The five is the convergent 1/5 of the short-gap frequency.\n"
        "The step budget ended mid-word.",
        fontsize=8,
        color=INK,
    )
    save(fig, out / "SCH1_integers.png", pdf)


def sheet_SCH2(out, pdf, summary, hits):
    fig, ax = new_sheet()
    titleblock(fig, "SCH2", "Schedule  ·  two bands", "chord / first-order path of one half-turn of P", summary)
    H0 = float(summary["H0"])
    h = float(summary["h"])
    ms_s, cp_s, ms_l, cp_l = [], [], [], []
    for i in range(1, len(hits)):
        a, b = hits[i - 1], hits[i]
        ch = math.hypot(b["Px"] - a["Px"], b["Py"] - a["Py"])
        rmean = b["m"] - 0.5
        pathlen = rmean * b["gap"] * h
        ratio = ch / pathlen if pathlen else 0
        if b["gap_kind"] == "short":
            ms_s.append(b["m"])
            cp_s.append(ratio)
        else:
            ms_l.append(b["m"])
            cp_l.append(ratio)
    ax.scatter(ms_s, cp_s, s=16, c=ACCENT, zorder=3)
    ax.scatter(ms_l, cp_l, s=10, c=INK, zorder=2)
    ax.axhline(2.0 / (H0 * h), color=INK, lw=0.6, ls=":")
    ax.axhline(2.0 / ((H0 - 1) * h), color=ACCENT, lw=0.6, ls=":")
    ax.axhline(2.0 / math.pi, color=DIM, lw=0.7, ls="--")
    ax.set_xlim(0, hits[-1]["m"] + 2)
    vals = cp_s + cp_l
    lo, hi = min(vals), max(vals)
    pad = 0.25 * (hi - lo) if hi > lo else 0.01
    ax.set_ylim(lo - pad, hi + pad)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(RULE)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(colors=DIM, labelsize=7)
    ax.set_xlabel("m", fontsize=7, color=DIM)
    ax.set_ylabel("chord / (r_mean · gap · h)", fontsize=7, color=DIM)
    save(fig, out / "SCH2_bands.png", pdf)


def write_notes(out: Path, summary, hits):
    text = f"""ELEMENTS OF POSITION
Notes to the set
19 September 2026

The model is built from the kernel tables.
The kernel walked. This set did not.

Shear T_h(x,y) = (x − h y, y + h x).
Bind N restores x² + y² = 1.
Station: start (1,0). Hit: y changes sign.
Height in the model is the hit index m.
Outer point: P = m u at z = m. Then r = z.
Inverse point: Q = (1/m) u at z = m. Then r = 1/z.
The unit circle is the bind. The plane y = 0 is the cut.

h = {summary['h']}
steps = {summary['_steps']}
H0 = {summary['_H0']}
hits = {summary['_n']}
mean gap · h = {float(summary['mean_gap_times_h']):.8f}
"""
    (out / "NOTES_to_the_set.txt").write_text(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=Path("../kernels/walk/runs/2026-09-24_h0.002_n200000"))
    ap.add_argument("--out", type=Path, default=Path("pass1/walk"))
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    hits_raw = read_dicts(args.run / "crossings.csv")
    pairs_raw = read_dicts(args.run / "pairs.csv")
    summary = read_summary(args.run / "summary.csv")
    hits, summary = derive(hits_raw, pairs_raw, summary)
    write_notes(out, summary, hits)
    pdf_path = out / "EOP_Set.pdf"
    with PdfPages(pdf_path) as pdf:
        sheet_A0(out, pdf, summary, hits)
        sheet_W1(out, pdf, summary, hits)
        sheet_P1(out, pdf, summary, hits)
        sheet_S1(out, pdf, summary, hits)
        sheet_E1(out, pdf, summary, hits)
        sheet_O1(out, pdf, summary, hits)
        sheet_D1(out, pdf, summary, hits)
        sheet_D2(out, pdf, summary, hits)
        sheet_D3(out, pdf, summary, hits)
        sheet_D4(out, pdf, summary, hits)
        sheet_D5(out, pdf, summary, hits)
        sheet_D6(out, pdf, summary, hits)
        sheet_D7(out, pdf, summary, hits)
        sheet_SCH1(out, pdf, summary, hits)
        sheet_SCH2(out, pdf, summary, hits)
    print("hits", len(hits), "from kernel tables only")
    print("wrote", out)
    print("pdf", pdf_path)


if __name__ == "__main__":
    main()
