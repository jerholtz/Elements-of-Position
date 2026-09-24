# Bridge Measure

Not a kernel. Reads no CSVs -- imports both kernels directly (via
`importlib`, since both are named `kernel.py` in sibling folders; see
"a naming collision, kept" below) and asks one question of them
together: at what setting are they the same object.

## The claim

Set `h = tan(2*pi/n)` in the walk kernel. Since one elementary
shear+bind step rotates by exactly `atan(h)` (an identity, proved in
`kernels/walk/README.md`), this makes each step exactly `2*pi/n` --
so `n` steps should land on the same `n` angular positions as the
n-gon kernel's `ngon(n)`.

## Where it holds, and where it structurally cannot

Checked directly against both kernels, `n=3` through `n=24`:

```
n   method       steps/vertex   max_error
3   composed     2              1.57e-16
4   composed     2              2.87e-16
5   single_step  1              4.44e-16
...
24  single_step  1              8.88e-16
```

For `n >= 5` a single elementary step reaches the vertex angle
directly. For `n=3` and `n=4` it cannot: `atan(h)` is confined to
under 90 degrees for every real `h`, and a triangle needs 120 degrees
per vertex, a square exactly 90 -- both out of reach for one step, at
any `h`, including the limit. This is the classical CORDIC constraint
(elementary rotations composed for angles a single one can't reach),
not a bug in either kernel. Composing two elementary steps per vertex
(`h = tan(2*pi/n/2)`) reaches machine precision for both `n=3` and
`n=4` just as cleanly as the single-step case does for `n >= 5`.

## A naming collision, kept deliberately visible

Both kernels are called `kernel.py`. This script cannot `import
kernel` the ordinary way -- Python will silently load whichever one
it finds first on `sys.path`, which is exactly the kind of quiet bug
this whole project's discipline exists to catch. It's worked around
here with `importlib.util.spec_from_file_location`, loading each
kernel by its full path under an unambiguous name
(`walk_kernel`, `ngon_kernel`). The workaround is correct, but the
underlying collision is still there and will bite the next script
that imports both less carefully. Renaming one or both kernel files
(e.g. `walk_kernel.py` / `ngon_kernel.py`) removes the need for this
workaround entirely; left as `kernel.py` here only because that
decision belongs with the kernels, not with this measure.

## Rebuild

```bash
python3 bridge_measure.py runs/2026-09-23 24   # from measures/bridge/
```

## Discipline

This measure imports; it does not reimplement. The n-gon vertices
compared against come from `ngon_kernel.ngon(n)` directly, not from a
second hand-written formula that happens to agree -- if `ngon()`
changes, this measure's comparison changes with it, on purpose.

The one exception, and it's named as one: `raw_trace()` duplicates the
walk kernel's shear+bind lines rather than calling `walk()`, because
the walk kernel's own `walk()` records only hits (y-sign changes), and
this measure needs every step's position, not just the hits. If
`kernels/walk/kernel.py`'s shear or bind changes, this function must
change with it by hand -- it is not protected by import the way the
n-gon comparison is. Flagged here so that risk is visible rather than
silent.
