# Walk Kernel

One walker. Three tables. Everything else reads.

```
kernel.py  -->  crossings.csv  pairs.csv  summary.csv
```

## What it generates

A point starts at `(1,0)` and takes discrete steps of shear-then-bind:

```
shear:  (x,y) -> (x - h*y,  y + h*x)
bind:   (x,y) -> (x,y) / sqrt(x^2+y^2)
```

Each step rotates the point by exactly `atan(h)` radians -- this is an
exact identity of the shear+bind map, not an approximation, and it is
the classical CORDIC elementary-rotation construction (Volder, 1959).
No trigonometric function is called to produce the motion; `atan` and
`pi` appear exactly once in this file, in `main()`, as a comparison
computed *after* the walk's own tables already exist.

A **hit** is recorded every time the heading's y-coordinate changes
sign -- i.e. every half-turn. `crossings.csv` is the list of hits.

## What it does not generate

`pair(m)` is pure arithmetic on the integer `m` -- `(m, 1/m)`, their
means, their gap `tau = AM - GM = (m-1)^2/(2m)`. It does not use the
walk at all, and is true for every `m` whether or not `walk()` ever
ran. `pairs.csv` is this table, computed for `m = 1..N` where `N` is
however many hits the walk produced.

## One structural limit worth knowing before extending this file

A single elementary step can never rotate by 90 degrees or more --
`atan(h)` is confined to `(-90, 90)` for every real `h`, no matter how
large. This is not a bug; it's the reason CORDIC composes several
elementary rotations for large angles instead of using one. Any script
that tries to reach a per-step angle of 90 degrees or more (for
example, replicating a square or triangle's vertex angle in a single
step) needs to compose multiple `walk()` steps per target angle, not
find a larger `h`.

## Rebuild

```bash
python3 kernel.py 0.002 200000 runs/2026-09-19_h0.002_n200000
```

- `h = 0.002`
- `200000` steps
- `H0 = 1571` (first hit)
- `127` hits total
- gaps take exactly two values: `1570` and `1571`
- `mean gap * h = 3.14160630`

This run is checked into `runs/2026-09-19_h0.002_n200000/` so any paper
citing these exact numbers can be verified against a table that
actually exists, not just against the number printed in the paper.

## Discipline

- Every claim provable from `pair()` or `wedge_closed()` is proved as
  an identity, independent of `h` and of any specific run.
- Every claim that is only a count (a gap value, a hit index, a
  histogram) is reported *from the tables*, named as a count, and
  never smuggled in as if it were an identity.
- A length or ratio that only appears meaningful after the tables
  exist (`lambda = pi/atan(h)`, the wall chord, the gap word) is named
  as a comparison, computed once, after the fact -- never inserted
  into `walk()` itself.

This file is not a drawing program and does not import anything that
draws. See `drawings/` for the scripts that read its output.
