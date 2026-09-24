#!/usr/bin/env python3
"""
THE GEOMETRIC KERNEL
The irreducible computational engine of the rigid continuum.
Constructs, measures, and balances space from primitive vector operations.
"""

from math import sqrt

def T_h(x, y, h):
    """Layer 1: The Infinitesimal Linear Shear Step"""
    return (x - h * y, y + h * x)

def N(x, y):
    """Layer 1: The Radial Normalization Constraint"""
    n = sqrt(x * x + y * y)
    return (x / n, y / n)

def step(x, y, h):
    """The Integrated Differential Rotation Operator"""
    return N(*T_h(x, y, h))

def dist(p, q):
    """Pure Euclidean Distance Matrix Tracker"""
    return sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

def measure_horizon(h):
    """Layer 2: The Self-Measurement Horizon Counter (Extracts H)"""
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

def execute_kernel(n_max=36, h_param=0.002):
    """Layer 3: The Multiplicative vs. Additive Balance Matrix"""
    H = measure_horizon(h_param)
    print(f"KERNEL INITIALIZED: h={h_param} | Self-Measured Half-Turn Baseline H={H} steps")
    print("-" * 90)
    print(f"{'n':<4} | {'j (steps)':<9} | {'r_out (Linear)':<15} | {'r_in (Inverse)':<15} | {'GM (Axle)':<10} | {'AM-GM (Tension)':<15}")
    print("-" * 90)
    
    for n in range(1, n_max + 1):
        k = float(n)
        j = n * H
        
        # Dual trajectories branching away from the kernel core
        r_out = k / 2.0
        r_in = 2.0 / k
        
        # Invariant checks
        gm = sqrt(r_out * r_in)  # Rigid structural axle (always 1.0)
        am = 0.5 * (r_out + r_in)
        tension = am - gm       # Scale entropy back-pressure
        
        print(f"{n:<4d} | {j:<9d} | {r_out:<15.6f} | {r_in:<15.6f} | {gm:<10.6f} | {tension:<15.6f}")
    print("-" * 90)

if __name__ == "__main__":
    execute_kernel(n_max=36, h_param=0.002)