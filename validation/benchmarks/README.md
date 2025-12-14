# Benchmarks (Known-Truth Suite)

This folder defines an **offline-friendly benchmark pipeline** for validating:

- component extraction (what symbols we find)
- component typing (what roles we assign)
- dependency extraction (imports → internal/external edges)
- unknown handling (what we *can’t* map yet)

The goal is to evolve toward your DoD claims (coverage + fallback) with **measurable, repeatable** metrics.

## Folder layout

- `repos/` (not committed): local clones / copies of benchmark repos
- `specs/`: golden truth specs (machine-readable)
- `runs/`: generated outputs (safe to delete/archive)

## Quick start (offline)

1) Put repos under `spectrometer_v12_minimal/validation/benchmarks/repos/<repo_name>/`

2) Add a spec under `spectrometer_v12_minimal/validation/benchmarks/specs/<repo_name>.bench.json`

3) Run the suite:

```bash
python3 spectrometer_v12_minimal/validation/run_benchmark_suite.py \
  --repos-dir spectrometer_v12_minimal/validation/benchmarks/repos \
  --specs-dir spectrometer_v12_minimal/validation/benchmarks/specs \
  --out-dir spectrometer_v12_minimal/validation/benchmarks/runs \
  --workers 6
```

## Truth sources (how to get “golden”)

In practice, “golden truth” can come from one of these sources:

1) **Architecture-as-code** inside the repo (best independence):
   - ArchUnit rules (Java), eslint boundaries (TS), dependency-cruiser, etc.
2) **Docs/diagrams** inside the repo (good, but may be partial):
   - `ARCHITECTURE.md`, `docs/architecture/*`, C4/Structurizr DSL, ADRs.
3) **Manual benchmark specs** (most controllable, most labor):
   - small curated repos + synthetic fixtures with explicit, audited component lists.

To identify repos that likely contain (1) or (2), run:

```bash
python3 tools/scan_repo_truth_sources.py \
  --repos-dir spectrometer_v12_minimal/validation/benchmarks/repos \
  --out spectrometer_v12_minimal/validation/benchmarks/runs/truth_sources.json
```

## Spec format (v1)

Each `*.bench.json` is a **repo-level** spec. Minimal fields:

- `name`: friendly name
- `repo_dir`: repo folder name under `repos/`
- `scored_types`: list of types we score (others ignored)
- `expected_components`: list of expected components (`rel_file`, `symbol`, `type`)

See `spectrometer_v12_minimal/validation/benchmarks/specs/_SCHEMA.md`.

