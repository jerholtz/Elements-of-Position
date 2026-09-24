#!/usr/bin/env python3
"""Identities used in On a Granted Power. Run as a check, not as a search."""
import numpy as np


def B(s, N):
    m = np.arange(1, N + 1, dtype=float)
    return np.sum(m ** (-s) - m ** (-(1 - s)))


def H(N):
    return sum(1.0 / m for m in range(1, N + 1))


def main():
    print("B_N(1/2) = 0")
    for N in (1, 2, 10, 127):
        print(f"  N={N}  {B(0.5, N)}")

    print("B_N(1-s) = -B_N(s)")
    for s in (0.2, 0.8 + 3j, 2.0):
        a, b = B(s, 40), B(1 - s, 40)
        print(f"  s={s}  sum={a+b}")

    print("B_N(1) = H_N - N")
    for N in (1, 2, 10, 127, 400):
        print(f"  N={N}  B={B(1, N):.10f}  H-N={H(N)-N:.10f}")

    print("increment at a recorded L start")
    s = 0.80267 + 19.398j
    leftover = B(s, 129) - B(s, 128)
    term = 129 ** (-s) - 129 ** (-(1 - s))
    print(f"  leftover {leftover}  term {term}  diff {leftover-term}")

    print("alpha")
    for sig in (0.2, 0.5, 0.8):
        print(f"  max({sig}, {1-sig}) = {max(sig, 1-sig)}")


if __name__ == "__main__":
    main()
