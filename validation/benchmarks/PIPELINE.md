# Benchmark Iteration Pipeline (How We Improve Every Run)

This is the intended closed loop:

1) **Run suite** (parallel)
2) **Score** against golden specs
3) **Collect unknowns** (new “atoms” / unmapped components)
4) **Update the detector** (new rules / mappings)
5) **Regenerate golden specs if needed** (when canon changes)
6) Repeat with trendable metrics

## 1) Run suite

```bash
python3 spectrometer_v12_minimal/validation/run_benchmark_suite.py \
  --repos-dir spectrometer_v12_minimal/validation/benchmarks/repos \
  --specs-dir spectrometer_v12_minimal/validation/benchmarks/specs \
  --out-dir spectrometer_v12_minimal/validation/benchmarks/runs \
  --workers 6
```

Outputs:

- `suite_summary.md` (high-level health)
- `unknowns.md` (what we failed to classify)
- per-spec `bench.report.json` (full details + detector outputs path)

## 2) Expand the benchmark set (more repos, more truth)

1) Add repo under `benchmarks/repos/<repo_dir>/`
2) Scan for embedded truth sources (docs / architecture-as-code):

```bash
python3 tools/scan_repo_truth_sources.py \
  --repos-dir spectrometer_v12_minimal/validation/benchmarks/repos \
  --out spectrometer_v12_minimal/validation/benchmarks/runs/truth_sources.json
```

3) Create a `*.bench.json` spec under `benchmarks/specs/`:
- Start small (20–50 expected components)
- Prefer “core” components (domain/app/infra/presentation) and stable boundaries

## 3) “New atoms discovered” → how to integrate

The suite’s `unknowns.md` is the feedstock for expanding detection:

- Add new typing rules (e.g., `DependencyInjectionContainer`, `ConfigLoader`, etc.)
- Improve parsing (AST-first instead of regex-first)
- Add language-specific heuristics only when necessary

Once a new rule exists:

1) re-run the suite
2) confirm unknown rate drops and precision/recall stays stable

Rule changes should be paired with:

- a new/updated golden spec (if the expectation changes)
- at least one additional repo that exercises the new rule

