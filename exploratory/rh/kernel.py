#!/usr/bin/env python3
"""
Elements of Position -- RH reading kernel.

Not a third walk. The heading already moved in kernels/walk.
This file writes the stock The Cut actually uses:

  OBJECT   stations, weights of complementary interiors
  SHEET    dated product and dual sum on a (sigma, t) grid

Trig (log, cos, sin) appears only in the sheet, after the station list exists.
It is not a search for ordinates. Zeros are not written.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path


# ---------------------------------------------------------------- OBJECT
def sieve_primes(n_max: int) -> list[int]:
    if n_max < 2:
        return []
    mark = [True] * (n_max + 1)
    mark[0] = mark[1] = False
    p = 2
    while p * p <= n_max:
        if mark[p]:
            step = p
            start = p * p
            mark[start : n_max + 1 : step] = [False] * len(mark[start : n_max + 1 : step])
        p += 1
    return [i for i in range(2, n_max + 1) if mark[i]]


def station(n: int) -> dict:
    return {
        "n": n,
        "origin": n / 2.0,
        "inv": 1.0 / n,
        "is_prime": 1 if n >= 2 and all(n % d for d in range(2, int(n**0.5) + 1)) else 0,
    }


def weights(n: int, sigma: float) -> tuple[float, float, float, float]:
    """Complementary pair {n^{-sigma}, n^{-(1-sigma)}}. GM = n^{-1/2}."""
    if n <= 1:
        return 1.0, 1.0, 1.0, 0.0
    left = n ** (-sigma)
    right = n ** (-(1.0 - sigma))
    gm = math.sqrt(left * right)  # == n**(-0.5)
    ratio = left / right if right else float("inf")  # n**(1-2sigma)
    return left, right, gm, ratio


def dual_real(n_max: int, sigma: float) -> float:
    """Sum of the two ends, t = 0."""
    return sum(n ** (-sigma) + n ** (-(1.0 - sigma)) for n in range(2, n_max + 1))


# ---------------------------------------------------------------- SHEET
def dated_product(primes: list[int], sigma: float, t: float, p_cut: int) -> complex:
    """Finite Euler product through primes <= p_cut. Sheet reading."""
    s_real = sigma
    acc = 1 + 0j
    log = math.log
    for q in primes:
        if q > p_cut:
            break
        # q^{-s} = exp(-s log q)
        ang = -t * log(q)
        mag = q ** (-s_real)
        q_to_minus_s = mag * complex(math.cos(ang), math.sin(ang))
        acc *= 1.0 / (1.0 - q_to_minus_s)
    return acc


def dual_height(n_max: int, sigma: float, t: float) -> complex:
    """Sum_n (n^{-s} + n^{-(1-s)}), n=2..n_max. Sheet reading."""
    acc = 0j
    log = math.log
    for n in range(2, n_max + 1):
        ln = log(n)
        left = n ** (-sigma) * complex(math.cos(-t * ln), math.sin(-t * ln))
        right = n ** (-(1.0 - sigma)) * complex(math.cos(t * ln), math.sin(t * ln))
        acc += left + right
    return acc


# ---------------------------------------------------------------- MAIN
def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("run")
    out.mkdir(parents=True, exist_ok=True)

    primes = sieve_primes(n_max)
    stations = [station(n) for n in range(1, n_max + 1)]
    # prime flag from sieve, cheaper and exact
    pset = set(primes)
    for row in stations:
        row["is_prime"] = 1 if row["n"] in pset else 0

    sigmas = [0.2, 0.35, 0.5, 0.65, 0.8]
    ts = [0.0, 5.0, 14.0, 25.0, 40.0]

    with (out / "stations.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "origin", "inv", "is_prime"])
        for row in stations:
            w.writerow([row["n"], row["origin"], row["inv"], row["is_prime"]])

    with (out / "weights.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "sigma", "left", "right", "gm", "left_over_right"])
        sample_n = [2, 3, 4, 5, 10, 13, 25, 50, n_max]
        for n in sample_n:
            if n > n_max:
                continue
            for sig in sigmas:
                left, right, gm, ratio = weights(n, sig)
                w.writerow([n, sig, left, right, gm, ratio])

    with (out / "dual_real.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_max", "sigma", "sum_ends"])
        for sig in sigmas:
            w.writerow([n_max, sig, dual_real(n_max, sig)])

    with (out / "dated_product.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["p_cut", "sigma", "t", "re", "im", "abs"])
        cuts = [p for p in (5, 13, 31, 97, n_max) if p <= n_max]
        if primes:
            cuts.append(primes[-1])
        cuts = sorted(set(cuts))
        for p_cut in cuts:
            for sig in sigmas:
                for t in ts:
                    z = dated_product(primes, sig, t, p_cut)
                    w.writerow([p_cut, sig, t, z.real, z.imag, abs(z)])

    with (out / "dual_height.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_max", "sigma", "t", "re", "im", "abs"])
        for sig in sigmas:
            for t in ts:
                z = dual_height(n_max, sig, t)
                w.writerow([n_max, sig, t, z.real, z.imag, abs(z)])

    # chi proxy: |left/right| = n^{1-2sigma}, equals 1 iff sigma=1/2
    with (out / "one_centre.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "sigma", "abs_chi_proxy", "on_cut"])
        for n in (5, 13, 97, n_max):
            if n > n_max:
                continue
            for sig in sigmas:
                _, _, _, ratio = weights(n, sig)
                w.writerow([n, sig, abs(ratio), 1 if abs(sig - 0.5) < 1e-12 else 0])

    real_at_half = dual_real(n_max, 0.5)
    real_off = dual_real(n_max, 0.2)
    with (out / "summary.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value"])
        w.writerows(
            [
                ("n_max", n_max),
                ("n_primes", len(primes)),
                ("dual_real_sigma_0.5", real_at_half),
                ("dual_real_sigma_0.2", real_off),
                ("dual_real_ratio_off_over_cut", real_off / real_at_half if real_at_half else ""),
                ("note", "weights.gm is n^(-1/2); chi proxy is 1 iff sigma=1/2"),
            ]
        )

    print(f"n=1..{n_max}  primes={len(primes)}")
    print(f"dual_real  σ=1/2 {real_at_half:.6f}   σ=0.2 {real_off:.6f}")
    print("wrote", out)


if __name__ == "__main__":
    main()
