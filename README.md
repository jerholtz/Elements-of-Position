# Elements of Position

A series of short works treating **position** — location, placement,
standing — as a single concept running underneath geometry, physics,
architecture, sound, and philosophy. The founding parts build one rigid
geometric object from first principles, using only elementary, provable
steps; later parts put that object to work.

Full framing in [`Elements of Position . Overview`](<Elements of Position . Overview>).

## Contents

```
Elements of Position . Overview     series index, framing, posture
I . Papers/                         Parts I–V (.tex sources + compiled PDFs)
II . Drawings, Models, Data/        the code: figures, verification, generated data
III . Other Material/               exploratory work outside the papers' claims
```

| Part | Title | Covers |
|---|---|---|
| — | Overview | Series index, framing, posture |
| I | The Closed Unit | The unit, inversion, the paper circle |
| II | The Other Walk | Φ, the second process, irreducible arrivals |
| III | Meetings | Where the two processes meet; the n=5 marriage |
| IV | The Cut | Plan / section / elevation; the midline |
| V | Where 1 Is | Closing reflection |

All five are in `I . Papers/`.

## II . Drawings, Models, Data

Three scripts, in order of dependency:

- **`Elements of Position - Drawings.py`** — the source of every figure in
  Papers I–V. Cited by name in each paper.
- **`Elements of Position - Verification.py`** — runs the master sequence
  to n=10,000 (configurable) and checks the rigidity, docking, and
  marriage claims in Papers I–III at a depth no printed table can show.
- **`Elements of Position - Local Circle Models.py`** — three models
  (local circle / plan overlay / elevation stack) giving concrete visual
  form to the plan-section-elevation reading Paper IV names but doesn't
  itself draw.

Both verification scripts print a `self-test:` block on every run. A run
that doesn't print all `PASS` lines shouldn't be trusted, and neither
should any figure it produced. Full methodology in this same folder's
`Companion_Verification_and_Models.pdf`.

Generated outputs (CSVs, PNGs, interactive HTML models) also live in this
folder, alongside the scripts that produce them.

### Running it

```bash
pip install numpy matplotlib sympy plotly

cd "II . Drawings, Models, Data"
python "Elements of Position - Verification.py" --nmax 10000
python "Elements of Position - Local Circle Models.py" --nmax 1000
```

Each writes its outputs to a folder next to itself. Outputs aren't
tracked in this repo (see `.gitignore`) — regenerate them by running the
scripts.

## III . Other Material

Structure found while building the verification code that isn't part of
any paper's argument — among it a connection to Euler's totient function
and a resonance with cyclotomic polynomials. Real, checked, and
documented, but kept separate deliberately: it supports nothing written
in the papers, and folding it in would blur a distinction the papers
themselves are careful about elsewhere.

## License

- **Code** (`.py` files, in `II . Drawings, Models, Data/`): [MIT](LICENSE)
- **Written content** (the Overview, Papers I–V, and the companion
  document): [CC BY 4.0](LICENSE-CONTENT.md)

## Citation

See [`CITATION.cff`](CITATION.cff), or use GitHub's "Cite this repository"
button in the sidebar.

## Author

Justin Erholtz
