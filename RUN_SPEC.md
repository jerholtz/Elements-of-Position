# Fresh run specification

First Order is closed. This is the next act. Do not run until the conversation says run.

## Purpose

One conversation-owned object. Every later drawing pass and every paper freeze cites these folders, not the 19 Sept snapshots.

## Commands (from repository root)

```bash
STAMP=$(date +%Y-%m-%d)   # expected 2026-09-24 in this conversation

python3 kernels/walk/kernel.py 0.002 200000 \
  kernels/walk/runs/${STAMP}_h0.002_n200000

python3 kernels/ngon/kernel.py 60 \
  kernels/ngon/runs/${STAMP}_n1-60

python3 measures/bridge/bridge_measure.py \
  measures/bridge/runs/${STAMP} 24
```

Do **not** run `already_there_measure.py` until `walk()` is removed from it and it imports `kernels/walk`. G1’s 129th hit, if still required, is a second walk:

```bash
python3 kernels/walk/kernel.py 0.002 400000 \
  kernels/walk/runs/${STAMP}_h0.002_n400000
```

That folder is extra depth for one measure. It does not replace the 200000-step object the drawings first pass reads.

## Acceptance

Walk `summary.csv` must be compared to `kernels/walk/runs/2026-09-19_h0.002_n200000/summary.csv`.

If the generator is unchanged, expect:

| key | value |
|---|---|
| n_hits | 127 |
| H0 | 1571 |
| gap_min / gap_max | 1570 / 1571 |
| mean_gap_times_h | 3.1416062992125986 |
| tau_sum_minus_trapezoid | ~0.038605 |

N-gon: every `summary.csv` row `match=1`; `twocos` at n=5 equals φ to six decimals.

Bridge: n=3,4 method `composed`; n≥5 `single_step`; max_error ~1e-15.

If the walk summary **differs**, stop. The generator changed, or the environment did. Do not silently treat the new table as the same object the current papers quote.

## After a successful run

1. Point `drawings/Main Drawing set.py` and `ngon_drawings.py` at the new folders (drawing pass 1).
2. Leave 2026-09-19 in place as the run the *current* tex still quotes, until papers are rewritten.

## Not part of this run

- Drawing scripts
- Papers
- Family 2
- Archive
- Granted-power paths


## Run log — 2026-09-24

Executed in this conversation.

- `kernels/walk/runs/2026-09-24_h0.002_n200000/` — summary **byte-identical** to 2026-09-19.
- `kernels/ngon/runs/2026-09-24_n1-60/` — 59 rows n=2..60, all `match=1`, twocos(5)=φ.
- `measures/bridge/runs/2026-09-24/bridge.csv` — n=3,4 composed ~1e-16; n≥5 single_step ~1e-15.

Bridge importer root corrected to `parents[2]` (repo root). First attempt used `parents[3]` and looked in `/home/workdir/artifacts/kernels/`.

Acceptance passed. Drawing pass 1 may point at the 2026-09-24 folders.
