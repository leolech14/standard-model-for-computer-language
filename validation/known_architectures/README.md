# Known-Architecture Benchmarks

These specs define “ground truth” for repositories that have a **known, documented architecture** (DDD / Onion / Clean / Ports&Adapters, etc.).

They are used to validate whether Spectrometer can correctly label components (e.g., `Entity`, `ValueObject`, `UseCase`, `Repository`, `Controller`, `DTO`) so we can reverse-engineer structure from code.

## What’s included

- `dddpy_real_onion_v1.json`: Local benchmark repo `validation/dddpy_real` (Python, FastAPI + Onion Architecture).

## Run validation

- Single spec:
  - `python3 spectrometer_v12_minimal/validation/validate_known_architecture.py --spec spectrometer_v12_minimal/validation/known_architectures/dddpy_real_onion_v1.json --write-json`

- All specs in this folder:
  - `python3 spectrometer_v12_minimal/validation/run_known_arch_suite.py --write-json`

## Spec format (v1)

Minimal fields:
- `name`
- `language` (currently only `python`)
- `repo_path` (path to the repo in this workspace)
- `scored_types` (component types to score)
- `ignore_path_globs`
- `rules[]`:
  - `type` (expected label)
  - `path_glob` (evaluated via `Path.glob`, supports `**`)
  - optional `name_regex`

Notes:
- Rules are applied in order; first match wins.
- This is meant to validate architectural *component typing*, not the full 96-hadron catalog yet.

