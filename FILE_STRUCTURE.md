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
├── FILE_STRUCTURE.md
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
├── drawings/                         
│   ├── walk_drawings.py             
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
│   └── README.md                         
|
├── narrative/
│   └── the-room-would-not-sit-still.tex|.pdf
|
├── exploratory/
│   ├── README.md
│   ├── granted-power/                    paper + runs/ verify, figures, path_G/L
│   ├── closed-unit-track/01..03
│   ├── the-elevation/
│   └── visual-sketchbook/                eop_drawings.py == eop_set_full.py
|
└── archive/geometric-kernel-history/     see its README for lineage
```