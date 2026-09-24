# File structure (working)

September consolidation. Status of this pass is marked.

```
elements-of-position/
│
├── README.md
├── OVERVIEW.tex / .pdf
├── PRINCIPLES.md
├── LICENSE
├── CITATION.cff
├── .gitignore
├── FILE_STRUCTURE.md                 this file
├── FILE_STRUCTURE.original.txt       the September planning note, kept
│
├── kernels/
│   ├── walk/
│   │   ├── kernel.py
│   │   ├── README.md
│   │   └── runs/2026-09-19_h0.002_n200000/
│   │       crossings.csv  pairs.csv  summary.csv
│   └── ngon/
│       ├── kernel.py
│       ├── README.md
│       └── runs/2026-09-23_n1-60/
│           vertices.csv  rings.csv  vertex_structure.csv  summary.csv
│
├── measures/
│   └── bridge/
│       ├── bridge_measure.py         parents[3] = repo root
│       ├── README.md
│       └── runs/2026-09-23/bridge.csv
│
├── drawings/                         Family 1. Two walk scripts still coexist.
│   ├── walk_drawings.py              minimal two-sheet set
│   ├── Main Drawing set.py / .pdf    full architectural walk set
│   ├── ngon_drawings.py
│   ├── Ngon_Set.pdf
│   └── Walk_Set.pdf
│
├── papers/
│   ├── 01-without-an-angle/paper.tex|.pdf
│   ├── 02-without-a-landing/paper.tex|.pdf
│   └── 03-already-there/paper.tex|.pdf
│
├── companions/verification-and-models/
│   ├── companion.tex
│   └── README.md                         source .py / runs not in either zip
├── narrative/
│   └── the-room-would-not-sit-still.tex|.pdf
├── exploratory/
│   ├── README.md
│   ├── granted-power/                    paper + runs/ verify, figures, path_G/L
│   ├── closed-unit-track/01..03
│   ├── the-elevation/
│   └── visual-sketchbook/                eop_drawings.py == eop_set_full.py
└── archive/geometric-kernel-history/     see its README for lineage
```

## Done

Pass 1 — root, kernels, measures nesting, paper rename.
Pass 2 — exploratory / narrative / companions tex / archive filled from prefinal.

## Still open

- Two walk drawing scripts (decision 1).
- Both kernels still named `kernel.py` (decision 2).
- Already There header still says “IV.” (decision 3).
- `EOP_IV_Measure.py` still in the sketchbook, not yet `measures/already-there/` (decision 4).
- Family 2 Python/HTML/PNG still missing from both zips.
- `eop_drawings.py` and `eop_set_full.py` are byte-identical; one can be dropped.
- Main-kernel PNG sheets not yet copied into `drawings/sheets/`.

## Pass 3 — First Order closed

Added: `INVENTORY.md`, `RUN_SPEC.md`, `rebuild_kernels.sh`,
`kernels/README.md`, `measures/README.md`, `drawings/README.md`,
`measures/already-there/` (parked IV measure, walk() still inside),
`archive/drawing-record/main-kernel-2026-09-19/` (historical Paper 01 PNGs).

Ready for the fresh run. Do not start drawing pass 1 until `RUN_SPEC.md` acceptance passes.

## Deposit freeze — 24 September 2026
README, CITATION.cff, LICENSE, ZENODO.md, .zenodo.json, papers I–V with pass-2 plates.
