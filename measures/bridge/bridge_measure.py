#!/usr/bin/env python3
"""
Elements of Position -- Bridge Measure.

Not a kernel. Imports both kernels, re-implements neither. Answers one
question: at what setting are the walk kernel and the n-gon kernel the
same object, and where exactly does that setting break down.

Claim: set h = tan(2*pi/n) in the walk kernel. One elementary step then
rotates by exactly atan(h) = 2*pi/n (an identity of the shear+bind map,
see kernels/walk/README.md). n such steps should trace the same n
angular positions as the n-gon kernel's ngon(n).

This holds exactly for n >= 5. It cannot hold as stated for n=3 or n=4,
because atan(h) is confined to (-90, 90) degrees for every real h, and
2*pi/3 = 120 degrees, 2*pi/4 = 90 degrees both exceed or meet that
ceiling. This is not a bug to route around quietly -- it is the
classical CORDIC constraint (elementary rotations under 90 degrees,
composed for larger angles), and this script measures it explicitly
rather than only reporting the cases that were guaranteed to work.
"""
import sys, csv, math
from pathlib import Path
import importlib.util

# Both kernels are named `kernel.py` in sibling folders -- exactly the naming
# collision flagged earlier. Loaded explicitly via importlib rather than
# sys.path, which would silently pick whichever one Python happens to find
# first. This IS the reason the two kernels should not both be called
# `kernel.py` if either is ever imported from, rather than just run.
_root = Path(__file__).resolve().parents[2]

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

walk_kernel = _load("walk_kernel", _root / "kernels" / "walk" / "kernel.py")
ngon_kernel = _load("ngon_kernel", _root / "kernels" / "ngon" / "kernel.py")


def raw_trace(h, steps):
    """Every step's raw heading, not just hits. Same shear+bind as the walk
    kernel's walk(), duplicated here ONLY because the walk kernel's own
    walk() records hits, not every step -- this measure needs every step.
    The shear+bind lines themselves must stay byte-identical to
    kernels/walk/kernel.py; if that file changes, this must change with it."""
    x, y = 1.0, 0.0
    pts = [(x, y)]
    for _ in range(steps):
        x, y = x - h * y, y + h * x
        r = math.sqrt(x * x + y * y)
        x, y = x / r, y / r
        pts.append((x, y))
    return pts


def single_step_bridge(n):
    """n >= 5 only. One elementary step per vertex."""
    h = math.tan(2 * math.pi / n)
    trace = raw_trace(h, n)
    walk_angles = [math.atan2(y, x) % (2 * math.pi) for x, y in trace[:n]]
    ng_verts = ngon_kernel.ngon(n, rot=0.0)  # radius n/2; only the angle is compared
    ng_angles = [math.atan2(y, x) % (2 * math.pi) for x, y in ng_verts]
    diffs = [abs((a - b + math.pi) % (2 * math.pi) - math.pi) for a, b in zip(walk_angles, ng_angles)]
    x0, y0 = trace[0]
    xn, yn = trace[n]
    closes = math.hypot(xn - x0, yn - y0)
    return h, max(diffs), closes


def composed_step_bridge(n, micro):
    """n < 5 case. `micro` elementary steps compose to one vertex-angle."""
    h = math.tan(2 * math.pi / n / micro)
    trace = raw_trace(h, n * micro)
    verts = trace[::micro][:n]
    ng_verts = ngon_kernel.ngon(n, rot=0.0)
    R = n / 2.0
    ng_unit = [(x / R, y / R) for x, y in ng_verts]  # normalize to unit circle for comparison
    err = max(math.hypot(vx - gx, vy - gy) for (vx, vy), (gx, gy) in zip(verts, ng_unit))
    return h, err, micro


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("run")
    out.mkdir(parents=True, exist_ok=True)
    n_max = int(sys.argv[2]) if len(sys.argv) > 2 else 24

    rows = []

    # n=3, n=4: single elementary step cannot reach the required vertex angle
    # (120 deg and 90 deg respectively; the ceiling is under 90 deg). Composed.
    for n in (3, 4):
        h, err, micro = composed_step_bridge(n, micro=2)
        rows.append([n, h, "composed", micro, err, ""])

    # n>=5: single elementary step reaches the vertex angle directly.
    for n in range(5, n_max + 1):
        h, max_err, closes = single_step_bridge(n)
        rows.append([n, h, "single_step", 1, max_err, closes])

    with (out / "bridge.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "h", "method", "elementary_steps_per_vertex", "max_error", "closing_distance"])
        w.writerows(rows)

    print(f"{'n':>3} {'method':>12} {'steps/vertex':>13} {'max_error':>12}")
    for n, h, method, micro, err, closes in rows:
        print(f"{n:>3} {method:>12} {micro:>13} {err:>12.2e}")
    print(f"\nwrote {out/'bridge.csv'}")


if __name__ == "__main__":
    main()
