# Benchmark Repo Candidates (Seed + Selection Method)

Goal: maintain a **diverse** set of open-source repositories (size + purpose + language) and a corresponding set of **golden truth** specs that we can score against.

Important constraint: a repo is only “benchmark-grade” if we can point to a truth source:

- Architecture-as-code (best): boundary rules/tests/config
- Architecture docs/diagrams (good): C4/Structurizr/ADR/architecture docs
- Manual spec (always possible, but labor)

## Seed list (evidence-based)

This workspace already contains an extracted list of repos that were used/mentioned during iterations:

- `spectrometer_v12_minimal/validation/iteration_test_repos.md`

Use that list as the initial candidate pool so we’re not inventing targets.

## Recommended benchmark tiers

### Tier A — Small repos with full golden specs (highest ROI)

These are ideal because we can maintain accurate, independent ground truth.

- Start with the local fixture already present:
  - `spectrometer_v12_minimal/validation/dddpy_real` (origin in `iteration_test_repos.md`)

Add more Tier A repos by selecting small DDD/Clean reference projects from `iteration_test_repos.md`, cloning them into `benchmarks/repos/`, then writing a `*.bench.json` spec.

### Tier B — Medium repos with internal architecture declarations

We prefer repos that include one or more of:

- C4 / Structurizr DSL
- ArchUnit rules
- dependency-cruiser / eslint boundaries rules
- explicit module boundary docs

We do **not** assume these exist without checking. Use the scanner below to verify.

### Tier C — Large repos (stress tests)

Large repos are useful for performance + “unknown” discovery, but golden truth is usually partial unless they ship architecture-as-code.

Use them to:
- measure extraction throughput
- measure unknown rate and unknown clustering quality
- discover missing artifact detectors (Docker/K8s/CI/etc.)

## How to select repos with “golden truth” signals (automated)

Once repos are present locally under `benchmarks/repos/`, run:

```bash
python3 tools/scan_repo_truth_sources.py \
  --repos-dir spectrometer_v12_minimal/validation/benchmarks/repos \
  --out spectrometer_v12_minimal/validation/benchmarks/runs/truth_sources.json
```

Then promote repos that score well on “truth sources” into Tier A/B and write specs for them.

## Suggested initial subset from the seed list (to verify locally)

From `iteration_test_repos.md`, these *appear* aligned to DDD/CQRS/Clean experiments and are good first candidates to scan once cloned:

- `iktakahiro/dddpy` (already vendored as `dddpy_real`)
- `pgorecki/python-ddd`
- `ledmonster/ddd-python-inject`
- `kgrzybek/modular-monolith-with-ddd`
- `fuinorg/ddd-cqrs-4-java-example`
- `amaljoyc/cqrs-spring-kafka`
- `meysamhadeli/booking-microservices-java-spring-boot`
- `spring-projects/spring-boot`

For “purpose diversity” stress tests (also in `iteration_test_repos.md`):

- infra: `hashicorp/terraform`, `docker/docker`, `kubernetes/kubernetes`
- web frameworks: `django/django`, `pallets/flask`, `fastapi/fastapi`
- frontend: `facebook/react`, `vercel/next.js`, `vuejs/vue`, `sveltejs/svelte`, `angular/angular`
- ML/data: `numpy/numpy`, `pandas-dev/pandas`, `scikit-learn/scikit-learn`, `tensorflow/tensorflow`, `pytorch/pytorch`

Again: treat these as *candidates* until scanned locally.

