# Elements of Position

One walker. Three tables. Everything else reads.

```
EOP - Kernel.py  →  crossings.csv  pairs.csv  summary.csv
                          ↓
                       set.py          (does not walk)
                          ↓
              sheets + paper measure the same tables
```

## The kernel

`EOP - Kernel.py` is the only place anything moves.

- Dynamics: shear, bind, start `(1,0)`, hit = sign change of `y`.
- Object: pair on the integer `m`.
- Sheet: `π / arctan(h)` after the tables exist.

It is not a drawing program. It is not the paper.

## Recorded run

Produced by:

```bash
python3 "EOP - Kernel.py" 0.002 200000 run
```

- `h = 0.002`
- `200000` steps
- `H0 = 1571`
- `127` crossings
- gaps `1570` and `1571`
- mean gap · h = `3.14160630`

## Rebuild

```bash
python3 "EOP - Kernel.py" 0.002 200000 run
python3 set.py --run run --out set
cd tex && pdflatex EOP_Overview.tex
pdflatex Without_an_Angle.tex && pdflatex Without_an_Angle.tex
```

The set builds `P_m = m u_m` and `Q_m = u_m/m` from the kernel columns. It does not walk.
