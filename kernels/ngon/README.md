# N-gon Kernel

One generator. Four tables. Everything else reads.

```
kernel.py  -->  vertices.csv  rings.csv  vertex_structure.csv  summary.csv
```

## What it generates

`n` equally spaced points on a circle of radius `n/2` -- diameter `n`.
This is the only place any angle is used in this file. At `n=1` the
diameter is exactly `1`.

## What it does not generate

`ring(n)` is pure arithmetic on the bare integer `n` -- the two
golden-ratio inward nests (`B1 = R*Phi`, `B2 = R*Phi^2`), the apothem,
`twocos = 2*cos(pi/n)` (equal to the golden ratio exactly and only at
`n=5`), and `half_walk = pi*R`. None of it needs a vertex list to
compute, and all of it is true independent of `ngon()` ever being
called.

`vertex_structure(n)` records, for each `k = 1..n-1`, whether
`gcd(n,k) > 1` -- i.e. whether vertex `k` is also a vertex of some
smaller `d`-gon, `d | n`. Euler's totient is brought in only in
`main()`, once the gcd-based table already exists, as a named
comparison: `reducible_count` should equal `(n-1) - totient(n)`. This
is checked, not assumed -- `summary.csv`'s `match` column is `1` on
every row from `n=2` to whatever `n_max` was run.

`is_prime` in `summary.csv` is plain primality, checked directly (no
totient, no gcd shortcut) -- see note below.

## A decision worth recording, not just making

An earlier version of this kernel considered a narrower "full web"
condition (`is_fw`) instead of plain primality, which would have
gated on something more specific than "no smaller d-gon shares any
vertex." That narrower condition was never pinned down precisely
enough to implement, so this kernel defaults to plain primality --
correctly named as exactly that, `is_prime`, with no implied claim
to anything narrower. If a "full web" condition distinct from
primality is wanted later, it should arrive as a second, separately
named column, not a redefinition of this one.

## Rebuild

```bash
python3 kernel.py 60 runs/2026-09-23_n1-60
```

Self-check printed to a table, not just to the console: every row of
`summary.csv` from `n=2` to `n_max` has `match=1` -- the gcd-based
reducible-vertex count agrees with Euler's totient prediction on
every single row, with zero exceptions. `twocos` at `n=5` prints
`1.618034`, matching the golden ratio to six decimals.

## Discipline

Same split as the walk kernel: VERTICES is the only layer with an
angle in it; INTERIOR is arithmetic on `n` alone, true with or without
a vertex list; NUMBER brings in a named external comparison (Euler's
totient) only after its own table already exists, exactly the same
role `lambda = pi/atan(h)` plays in the walk kernel.

Not included here, deliberately: the Archimedes inscribed/circumscribed
sandwich and the `pi^2/(2n^2)` asymptotic squeeze. Both are true and
checked, but they are claims *about* this kernel's output, not part of
generating it -- they belong in a `measures/` script that reads these
CSVs, not in the kernel itself.

This file is not a drawing program and does not import anything that
draws. See `drawings/` for the scripts that read its output.
