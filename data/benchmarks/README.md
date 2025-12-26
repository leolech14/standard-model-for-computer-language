# 🧪 Collider Benchmark Dataset (V1)

> **Version:** 1.0 (2025-12-23)
> **Samples:** 500
> **Repositories:** 20 Diverse Python Projects
> **Purpose:** Ground Truth for Collider Algorithm Validation.

## Structure

| Column | Description |
|:---|:---|
| `sample_id` | Unique ID. |
| `name` | Function/Class name. |
| `file` | Relative file path (context). |
| `annotated_role` | **Ground Truth** (Canonical 27-Role). |
| `kind` | Source Type (function, class). |

## Usage
Used by:
- `scripts/validate_annotations.py`: To measure static accuracy.
- `scripts/train_serial.py`: To train the Pattern Discovery engine.

## Taxonomy
Annotations strictly follow `docs/CANONICAL_SCHEMA.md`.
- `Test`
- `Entity`
- `Service`
- `Controller`
- `Utility`
- `Factory`
- ...
