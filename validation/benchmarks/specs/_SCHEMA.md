# Benchmark Spec Schema (v1)

These specs define **golden truth** for a repo in a way the suite can score deterministically.

## File naming

- `*.bench.json` under `spectrometer_v12_minimal/validation/benchmarks/specs/`

## Shape (v1)

```json
{
  "version": 1,
  "name": "example_repo_v1",
  "repo_dir": "example_repo",
  "scored_types": ["Entity", "ValueObject", "UseCase"],
  "ignore_path_globs": ["**/tests/**"],
  "expected_components": [
    {
      "rel_file": "src/domain/user.py",
      "symbol": "User",
      "symbol_kind": "class",
      "type": "Entity",
      "notes": "Optional human note"
    }
  ]
}
```

## Fields

- `version` (int): must be `1`
- `name` (string): unique identifier for reporting
- `repo_dir` (string): directory name under `benchmarks/repos/`
- `scored_types` (string[]): types included in metrics (everything else is ignored)
- `ignore_path_globs` (string[], optional): file globs to ignore in scoring + unknown discovery
- `expected_components` (object[]): expected components
  - `rel_file` (string): file path relative to repo root
  - `symbol` (string): class/function/module symbol name
  - `symbol_kind` (string, optional): `class|function|module|file` (used only for reporting)
  - `type` (string): expected taxonomy label
  - `notes` (string, optional): freeform

## Matching rules

The scorer matches `expected_components` to detector output by:

- `rel_file` and `symbol` (case-sensitive), after normalizing paths to POSIX separators.
