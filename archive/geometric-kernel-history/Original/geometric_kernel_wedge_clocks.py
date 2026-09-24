#!/usr/bin/env python3
"""
Wedge from k=2 to N (discrete sum vs closed form).
Two clocks on the same heading: stride H and stride H±1.
Record j where both sit on the horizon.
"""

from math import sqrt, log
from pathlib import Path
import csv

OUT = Path("/home/workdir/artifacts")


def T_h(x, y, h):
    return (x - h * y, y + h * x)


def N(x, y):
    n = sqrt(x * x + y * y)
    return (x / n, y / n)


def step(x, y, h):
    return N(*T_h(x, y, h))


def measure_horizon(h):
    x, y = 1.0, 0.0
    seen_up = False
    m = 0
    while True:
        x, y = step(x, y, h)
        m += 1
        if y > 0.0:
            seen_up = True
        if seen_up and y <= 0.0:
            return m


def closed_wedge(N):
    return (N * N) / 8.0 + log(N) - N + 1.5 - log(2.0)


def main():
    h = 0.002
    n_max = 36
    H = measure_horizon(h)
    print(f"h={h}  H={H}  n_max={n_max}")

    x, y = 1.0, 0.0
    j_max = n_max * H
    # discrete wedge: sum tension * dk, dk = 1/H, from k=2 to k=n_max
    wedge_sum = 0.0
    horizon = []  # j where |y| small after a step
    for j in range(1, j_max + 1):
        x, y = step(x, y, h)
        k = j / H
        if k >= 2.0:
            tens = k / 4.0 + 1.0 / k - 1.0
            wedge_sum += tens / H  # dk = 1/H
        if abs(y) < 0.01:
            horizon.append((j, k, x, y))

    closed = closed_wedge(float(n_max))
    print()
    print("WEDGE k=2 .. N")
    print(f"  discrete sum tension dk = {wedge_sum:.8f}")
    print(f"  closed N^2/8 + ln N - N + 3/2 - ln 2 = {closed:.8f}")
    print(f"  difference = {wedge_sum - closed:.8f}")

    # two clocks: events at multiples of H (half-turns) and of p
    print()
    print("HORIZON crossings (|y|<0.01) count:", len(horizon))
    print("first/last horizon j,k,x,y:")
    if horizon:
        print(" ", horizon[0])
        print(" ", horizon[-1])

    for p in (H - 1, H + 1):
        # clock A: j multiple of H
        # clock B: j multiple of p
        # lock: j multiple of both = lcm(H,p) = H*p since gcd=1
        lcm = H * p
        print()
        print(f"CLOCKS stride {H} and {p}   gcd=1  lcm={lcm}")
        locks = []
        j = lcm
        while j <= j_max:
            k = j / H
            locks.append(j)
            j += lcm
        print(f"  locks in range: {locks if locks else '(none — lcm > j_max)'}")
        # also: A on horizon at j=mH, B ticks at those j if mH % p == 0
        a_on_b = [m * H for m in range(1, n_max + 1) if (m * H) % p == 0]
        print(f"  half-turn indices also multiple of p: {a_on_b if a_on_b else '(none)'}")

    path = OUT / "kernel_wedge.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["N", "discrete_wedge", "closed_wedge", "diff"])
        # also report partial N
        # recompute partials quickly from formula + one more walk for discrete
        x, y = 1.0, 0.0
        acc = 0.0
        partial = {}
        for j in range(1, j_max + 1):
            x, y = step(x, y, h)
            k = j / H
            if k >= 2.0:
                acc += (k / 4.0 + 1.0 / k - 1.0) / H
            if j % H == 0 and j // H >= 2:
                n = j // H
                partial[n] = acc
        for n in range(2, n_max + 1):
            c = closed_wedge(float(n))
            d = partial[n]
            w.writerow([n, d, c, d - c])
            if n in (2, 3, 4, 8, 16, 36):
                print(f"  N={n:2d}  discrete={d:.6f}  closed={c:.6f}  diff={d-c:.6f}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
