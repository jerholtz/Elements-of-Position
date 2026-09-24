# Principles

Extracted from the kernel and measure READMEs. Not new doctrine — the checklist the files already enforce.

## Two kinds of claim

1. **Identity.** Forced by the operators or by arithmetic on the integer. True for every admissible kick and every start on the diameter. Proved. Independent of `h` and of any specific run.
2. **Count / comparison.** A gap, a hit index, a histogram, a length that only becomes meaningful after a table exists. Reported *from the tables*, named as a count or as a comparison, never smuggled in as an identity.

A later part does not explain an earlier one. It stands on it.

## Three layers, kept in three places

Every kernel keeps the same split:

| Layer | Walk | N-gon | Rule |
|---|---|---|---|
| Motion / placement | `walk()` — shear then bind. No trig. | `ngon(n)` — the only angle in the file. | The only place anything is made. |
| Object | `pair(m)`, `wedge_closed()` | `ring(n)` | Pure arithmetic on the integer. True whether the generator ever ran. |
| Sheet | `λ = π / arctan(h)` in `main()`, after the tables exist | totient vs gcd-reducible count, in `main()`, after the table exists | Named comparison. Never fed back into the generator. |

A drawing script reads tables. It does not walk. A measure may import kernels; it does not draw.

## Generate once, check twice

A number does not stand until it has been produced twice, by two different routes, and the two routes agree. A claim proved on paper and a claim read off a table are different kinds of claim.

Where a name was reached for before the check was finished, that was a mistake and is not repeated.

## What is not put in the step

- No angle is an argument of the shear or the bind.
- `π` and `atan` appear in the walk kernel exactly once, in a comparison computed after the tables exist.
- A running total is never trusted over its own closed form.
- `is_prime` means primality. A narrower “full web” condition, if wanted later, arrives as a second named column, not a redefinition.
- Archimedes’ sandwich and the `π²/(2n²)` squeeze are claims *about* the n-gon kernel, not part of generating it. They belong in `measures/`.

## Naming

- Shear `T_h`, bind `N`, step, hit, pair, lock, leftover `τ`.
- Outer point `P_m = m u_m`. Inverse point `Q_m = u_m / m`.
- Accent in Family 1 drawings: one dry oxide red, always the inverse locus.
- Both kernels are still named `kernel.py`. Scripts that import both must load by full path (`importlib`), not by `sys.path`. That collision is kept visible on purpose until the kernels themselves are renamed.

## Runs are records

The recorded walk cited by the frozen papers:

```
h = 0.002
steps = 200000
H0 = 1571
hits = 127
gaps = 1570 and 1571
mean gap · h = 3.14160630
```

lives at `kernels/walk/runs/2026-09-19_h0.002_n200000/`.

A different kick, or a longer run, writes a new dated folder. It does not revise an identity. Papers cite a folder that actually exists.

## What this repository is not

- The kernel is not a drawing program.
- A drawing is not a proof.
- Exploratory work is public and timestamped; it is not Tier 2.
- Archive is provenance. Live papers do not cite it.
