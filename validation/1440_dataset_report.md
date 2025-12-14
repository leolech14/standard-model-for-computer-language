# 1440 Dataset Validation Report

- Dataset: `1440_csv.csv`
- Canon table: `HADRONS_96_FULL.md`

## What “1440” Means

`1440_csv.csv` contains the full RPBL axis grid:
- Responsibility: 12
- Purity: 4
- Boundary: 6
- Lifecycle: 5

So the RPBL coordinate space is `12 × 4 × 6 × 5 = 1440`.

The file itself contains **3,888 rows**, because it lists *hadron-specific allowed RPBL combinations* (not the full 96×1440 cartesian product).

## Coverage

- Hadrons present: **96/96**
- Base hadron vs hadron_subtipo mismatches: **0**
- RPBL combos present (unique responsibility×purity×boundary×lifecycle): **1440/1440**
- Rows per hadron: min=18, max=144; histogram:
  - 18 → 61 hadrons
  - 19 → 18 hadrons
  - 144 → 17 hadrons

## Impossible Rows

- Impossible rows: **81**
- Unique reasons: **4**
  - 72: Immutable cannot have mutating operations
  - 4: Entity has state, cannot be pure
  - 3: ValueObject is immutable
  - 2: Immutable cannot handle commands

## Canon Alignment Notes

- `ABTestRouter` in the CSV corresponds to `A/B Test Router` in `HADRONS_96_FULL.md`.
- `LocalVar` continent differs:
  - CSV: `Foundations / Variables`
  - `HADRONS_96_FULL.md`: `Data Foundations / Variables`

## Next Steps (Validation-Oriented)

1) Treat `1440_csv.csv` as the current “truth table” for RPBL×hadron possibilities; derive:
   - `possible_subhadrons.csv` (all rows where `is_impossible=False`)
   - `impossible_subhadrons.csv` (all rows where `is_impossible=True`)
2) Decide the reduction rule for the “most important mapped set” (likely `96 × 4 = 384`), ideally chosen by empirical frequency from real repos.
3) Build a repo-corpus runner that maps extracted components → (hadron_subtipo, RPBL) and reports:
   - coverage against the table
   - “new” combos not represented
   - clusters of Unknowns that need new hadrons or better rules

