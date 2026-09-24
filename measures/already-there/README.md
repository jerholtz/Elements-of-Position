# Already-There measure

Not a kernel. Questions asked of the pair and of the walk after both exist.

Source: parked from `exploratory/visual-sketchbook/EOP_IV_Measure.py` (written alongside *Already There*).

## What it generates

| File | Question |
|---|---|
| `z2_bernoulli_ladder.csv` | Stirling/Bernoulli term sizes at fixed \(N=10\) |
| `g1_gap_word.csv` | predicted vs actual L/S word to \(M=129\) |
| `g1_summary.csv` | long/short counts at 127 and 129 |
| `sb1_tree_paths.csv` | Stern–Brocot spines and \(\varphi\) path |
| `sb1_unimodularity.csv` | consecutive determinants |
| `sb1_full_tree.csv` | modest-depth tree |
| `cs1_fibonacci_matrix.csv` | Cassini / docking \(1/(2\varphi^k)\) |
| `cs1_meetings_check.csv` | against Meetings quoted figures |

## What it must not keep

It currently contains a verbatim copy of `walk()`. After wiring, hits come from `kernels/walk`. Gap-word comparison reads `crossings.csv`.

## Rebuild (after wiring)

Not run during First Order. Needs `mpmath`. Output destination will be a dated folder under `runs/`.

## Cited by

Part V plates G1 and SB1. Cassini tables belong with Part IV.
