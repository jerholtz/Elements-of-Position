# Inventory — First Order

Every live file classified. Archive scripts are listed only as lineage.

Legend  
**G** generates (the only place that object is made)  
**R** reads tables / imports  
**C** cited by  
**Keep** stay as-is through the fresh run  
**Rebuild** rewrite after the fresh run  
**Park** do not cite; wait for paper consolidation  
**Missing** named in a tex or structure note, not in either zip

---

## 1. Generators (Tier 1 kernels)

| File | G | Outputs | C | Action |
|---|---|---|---|---|
| `kernels/walk/kernel.py` | heading, hits, pair table | `crossings.csv` `pairs.csv` `summary.csv` | papers 01–03; bridge; Main Drawing set; walk_drawings; already-there measure (should import) | **Keep** generator. Fresh run writes a new dated folder. |
| `kernels/ngon/kernel.py` | vertices, rings, gcd structure | `vertices.csv` `rings.csv` `vertex_structure.csv` `summary.csv` | bridge; ngon_drawings | **Keep** generator. Fresh run writes a new dated folder. |

Both still named `kernel.py`. Rename only during paper consolidation.

Current cited walk run: `kernels/walk/runs/2026-09-19_h0.002_n200000/`  
Current ngon run: `kernels/ngon/runs/2026-09-23_n1-60/`

---

## 2. Measures (Tier 1)

| File | G / R | Outputs | C | Action |
|---|---|---|---|---|
| `measures/bridge/bridge_measure.py` | R both kernels; duplicates shear+bind in `raw_trace` | `bridge.csv` | synthesis drawings (not yet written) | **Keep** question. After fresh run, `raw_trace` should call walk internals or stay flagged. |
| `measures/already-there/already_there_measure.py` | R pair arithmetic; **illegal copy of walk()** | Z1 Z2 G1 SB CS tables listed in its README | paper 03 plateboxes; `EOP_IV_Drawings.py` | **Park** until wired to `kernels/walk`. Then **Rebuild** output into `runs/<date>/`. |

---

## 3. Family 1 drawings (Tier 1) — inventory only

| File | Sheets | Reads | C | Action |
|---|---|---|---|---|
| `drawings/Main Drawing set.py` | A0 W1 P1 S1 E1 O1 D1 D2 D3 D4 D5 D6 D7 SCH1 SCH2 | walk CSVs | paper 01 (all except D3) | **Rebuild** after fresh run (drawing pass 1), again after papers (pass 2). |
| `drawings/walk_drawings.py` | A0 W1 D1 | walk CSVs | — | Absorb into the one walk set in pass 1. |
| `drawings/ngon_drawings.py` | A0 P1 P2 E1 D1–D4 SCH1 SCH2 | ngon CSVs | none of the frozen papers yet | **Rebuild** both drawing passes. |
| `drawings/*.pdf` | old products | — | — | Replace; do not upload as current. |

`synthesis_drawings.py` — **Missing**. First tenant is `measures/bridge`. Write in drawing pass 1 if the bridge remains a live claim.

---

## 4. Historical sheets (not published)

`archive/drawing-record/main-kernel-2026-09-19/`

A0 D1–D7 E1 O1 P1 S1 SCH1 SCH2 W1 + `EOP_Set.pdf` + notes.

These match Paper 01 figure names. They were built from the 19 Sept walk tables. They are a record, not the freeze.

---

## 5. Frozen papers (Tier 2) — current names only

Consolidation is allowed later. This table is the *present* citation map.

### 01 Without an Angle (19 Sept 2026)

Reads walk run `h=0.002`, `200000` steps, `127` hits.  
`graphicspath` still `{../set/}` — broken relative to new tree.

| Figure in tex | Exists as historical PNG? | Drawing source |
|---|---|---|
| W1_heading | yes | Main Drawing set |
| D1_lock | yes | Main |
| D2_pair | yes | Main |
| P1_plan | yes | Main |
| D5_four_points | yes | Main |
| SCH1_integers | yes | Main |
| E1_elevation | yes | Main |
| D4_cycle | yes | Main |
| SCH2_bands | yes | Main |
| S1_section | yes | Main |
| O1_oblique | yes | Main |
| D6_kite | yes | Main |
| D7_swap | yes | Main |

D3_short_hit exists historically and is **not cited** by 01.

### 02 Without a Landing (19 Sept 2026)

Same recorded run. Figures are a *different* sheet list. **None of these PNGs were in either zip.**

E1R_residual_elevation, D6R_kite_dirty, K1_kite_stacked, O2_kite_solid, D8_polar, SCH3_stands, P1_pair_leftover_mouth, P2_three_readings, P3_inversion, F1_irreducible_pairs, F3_thales_kinds, P4_new_inners, P5_powers, P6_telescope_factors, F4_nested_closures, F2_pair_monoid.

These are drawing pass 1 work, then pass 2 captions.

### 03 Already There (22 Sept 2026) — header still says “IV.”

Plateboxes only, no `\includegraphics`: Z1 Z2 G1 SB1 CS1.  
Reader: `exploratory/visual-sketchbook/EOP_IV_Drawings.py`.  
Tables: `measures/already-there`.  
Cites exploratory Parts I–III by name (*Closed Unit*, *Other Walk*, *Meetings*).

---

## 6. Exploratory (Tier 3)

| Path | What | Figures named | Action |
|---|---|---|---|
| `closed-unit-track/01-the-closed-unit` | Part I | drawing_01..06, 08 | Park. Figure PNGs **Missing**. |
| `closed-unit-track/02-the-other-walk` | Part II | layer_primes_rate, layer_phi_10/11, layer_both_01..05 | Park. PNGs **Missing**. |
| `closed-unit-track/03-meetings` | Part III | layer_both_*, layer_n5_meetings | Park. PNGs **Missing**. |
| `granted-power/` | tilt / equal weight | GP1–GP3 | Park with its own `runs/` scripts and `path_G.csv` `path_L.csv`. |
| `the-elevation/` | labeled VI in header | layer_e01..e04 | Park. PNGs **Missing**. |
| `visual-sketchbook/eop_drawings.py` | Family 3 | drawing_* functions | Park. Duplicate of `eop_set_full.py`. |
| `visual-sketchbook/EOP_IV_Drawings.py` | Z1–CS1 | measure CSVs | Rebuild in drawing passes if 03 survives consolidation. |
| `visual-sketchbook/EOP_IV_Set.pdf` | old product | — | Record only. |

Closed-unit / Other Walk / Meetings / Elevation figure files were never in the dumps. Family 3 is the likely generator (`eop_drawings.py`). Do not invent those PNGs during First Order.

---

## 7. Narrative / companions

| Path | Status |
|---|---|
| `narrative/the-room-would-not-sit-still` | Have tex+pdf. No kernel. |
| `companions/verification-and-models/companion.tex` | Have. Describes Family 2. |
| `verification.py` | **Missing** |
| `local_circle_models.py` | **Missing** |
| `measurements.csv` `docking_events.csv` `live_model.html` model PNGs | **Missing** |

Family 2 ports formulas from the old drawings script (Process A/B, marriage at n=5), not from `kernels/walk`. Decision deferred: supply, rebuild from the tex after papers, or retire.

---

## 8. Archive (do not cite)

| Path | What |
|---|---|
| `geometric-kernel-history/Original/` | first generator + vary-h + N3600 |
| `EOP_Geometric_Kernel_minimal.py` and Geometric Kernel.py variants | middle generation |
| `eop_kernel_out/` | early crossings/pairs/summary |
| `EOP - Kernel.py` | predecessor of live walk kernel (same length, not byte-identical) |
| `main-kernel-run-snapshot/` | **identical** to live 2026-09-19 walk tables |
| `drawing-record/main-kernel-2026-09-19/` | Paper 01 sheet PNGs |

Empty prefinal folders with no files: `drawing sets/n-gons kernel`, `post kernel`, `The Closed Unit drawings`.

---

## 9. Sheet-code collisions to resolve in drawing pass 2

The same code does not mean the same plate across families.

| Code | Walk Main | N-gon | Paper 02 | IV set |
|---|---|---|---|---|
| A0 | index | index | — | index |
| P1 | plan of P and Q | n-gon plan | leftover / mouth | — |
| E1 | elevation m·hy | n-gon elevation | — | — |
| E1R | — | — | residual elevation | — |
| D1 | lock | n-gon D1 | — | — |
| SCH1 | two-integer gaps | n-gon schedule | — | — |

Paper 02 reused P1–P6 for pair-readings. That is a naming collision with walk P1 plan. Pass 2 either namespaces (`W-P1` vs `L-P1`) or retitles after paper consolidation.

---

## 10. What the fresh run must produce

Walk, same parameters the papers already quote (unless a paper pass later changes them):

```
h = 0.002
steps = 200000
```

Expected if the generator is unchanged: `H0=1571`, `127` hits, gaps `1570`/`1571`, mean-gap·h `3.14160630`.

N-gon: `n_max = 60` (or higher if we want totient checks deeper; 60 is the current table).

Bridge: `n_max = 24`.

Already-there measure: after wiring, extend the walk to `400000` steps only inside that measure if G1 still needs `M=129` (the 200000-step run already has 127 hits; 129 hits need more steps). That extension is a **new dated walk run**, not an edit of the recorded 200000-step folder.

---

## 11. Open only after papers, not now

- Combining 01–03 with closed-unit I–III / Granted Power / Elevation
- Header “IV.”
- Renaming `kernel.py`
- Whether Family 2 is rebuilt or retired
- Final sheet codes
