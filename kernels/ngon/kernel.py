#!/usr/bin/env python3
"""
Elements of Position -- N-gon Kernel, minimal.

Three layers, kept in three places, not one, the same split as the walk kernel:

  VERTICES    ngon(n)              the only place any angle appears. n points,
              equally spaced, radius n/2 -- diameter n, same convention as the
              walk kernel's D1: "radius already 1/2" at n=1.
  INTERIOR    ring(n)              pure arithmetic on the integer n. true for
              n=1,2,3,... whether or not any vertex was ever placed. the two
              golden-ratio nests, the apothem, the diagonal/side ratio.
  NUMBER      vertex_structure(n)  which vertices double as vertices of some
              smaller d-gon, d|n. computed from gcd only. compared to Euler's
              totient AFTER the table exists -- a named comparison, not an
              assumption the table is built to match.
"""
import csv, math
from pathlib import Path

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV = PHI - 1.0  # = 1/PHI


# ------------------------------------------------------------------ VERTICES
def ngon(n, rot=math.pi / 2):
    """n vertices on a circle of radius n/2. The only angle in this file."""
    R = n / 2.0
    return [
        (R * math.cos(rot + 2 * math.pi * k / n), R * math.sin(rot + 2 * math.pi * k / n))
        for k in range(n)
    ]


# ------------------------------------------------------------------- INTERIOR
def ring(n):
    """Pure arithmetic on n. No vertex list needed; true independent of ngon()."""
    R = n / 2.0
    return dict(
        n=n,
        R=R,
        inv=1.0 / n,
        lock=1.0,
        mid=R / 2.0,
        B1=R * PHI_INV,        # first inward copy, radius R*Phi
        B2=R * PHI_INV ** 2,   # second inward copy, radius R*Phi^2
        apothem=R * math.cos(math.pi / n) if n >= 3 else float("nan"),
        side=n * math.sin(math.pi / n) if n >= 2 else float("nan"),
        twocos=2.0 * math.cos(math.pi / n) if n >= 2 else float("nan"),  # = PHI exactly at n=5
        half_walk=math.pi * R,  # same object as the walk kernel's arc length, at this n's radius
    )


# --------------------------------------------------------------------- NUMBER
def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def totient(n):
    result = n
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


def vertex_structure(n):
    """For k=1..n-1: gcd(n,k) > 1 iff vertex k is shared with some d-gon, d|n, d<n."""
    return [(n, k, math.gcd(n, k), int(math.gcd(n, k) > 1)) for k in range(1, n)]


# ----------------------------------------------------------------------- MAIN
def main():
    import sys

    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("ngon_kernel_out")
    out.mkdir(parents=True, exist_ok=True)

    with (out / "vertices.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "k", "x", "y"])
        for n in range(1, n_max + 1):
            for k, (x, y) in enumerate(ngon(max(n, 1))):
                w.writerow([n, k, x, y])

    rings = [ring(n) for n in range(1, n_max + 1)]
    with (out / "rings.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(list(rings[0].keys()) + ["is_prime"])
        for r in rings:
            w.writerow(list(r.values()) + [int(is_prime(r["n"]))])

    with (out / "vertex_structure.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "k", "gcd", "reducible"])
        for n in range(2, n_max + 1):
            w.writerows(vertex_structure(n))

    # sheet reading: totient used ONLY here, as a named comparison, after the
    # gcd-based table already exists -- same discipline as lambda in the walk
    # kernel, which uses math.pi/math.atan only after the hit table exists.
    with (out / "summary.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "reducible_count", "totient_predicted", "match", "twocos", "is_prime"])
        for n in range(2, n_max + 1):
            reducible = sum(1 for k in range(1, n) if math.gcd(n, k) > 1)
            predicted = (n - 1) - totient(n)
            r = ring(n)
            w.writerow([n, reducible, predicted, int(reducible == predicted), r["twocos"], int(is_prime(n))])

    print(f"n=1..{n_max}  wrote vertices.csv, rings.csv, vertex_structure.csv, summary.csv  ->  {out}")
    print(f"twocos(5) = {ring(5)['twocos']:.6f}   PHI = {PHI:.6f}")


if __name__ == "__main__":
    main()
