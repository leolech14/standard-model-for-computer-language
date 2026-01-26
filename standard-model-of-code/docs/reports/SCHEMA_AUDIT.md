# Schema Audit Report

**Date:** 2026-01-26
**Phase:** Ghost Exorcism Phase 2 (G08)
**Status:** COMPLETE

## Summary

| Category | Count | Action |
|----------|-------|--------|
| **KEEP** (code-loaded) | 10 | Retain - actively used by pipeline |
| **DOCUMENTATION** (doc-referenced) | 20 | Retain - referenced in specs/docs |
| **ORPHAN** (unreferenced) | 0 | None found |
| **Total** | 30 | No deletions required |

## Audit Methodology

1. Listed all files in `schema/` directory
2. Searched for code references (Python imports, YAML loads)
3. Searched for documentation references
4. Categorized based on reference type

## KEEP: Actively Code-Loaded (10 files)

These files are loaded by Python code at runtime:

| File | Loaded By | Purpose |
|------|-----------|---------|
| `antimatter_laws.yaml` | `src/core/violation_detector.py` | Code smell detection rules |
| `classification.yaml` | `src/patterns/atom_classifier.py` | Atom classification schema |
| `constants.yaml` | Multiple | Single source of truth for counts |
| `context.yaml` | `src/core/atom_loader.py` | Context extraction rules |
| `family_relationships.yaml` | `src/core/family_classifier.py` | Edge family taxonomy |
| `fixed/atoms.json` | `src/core/atom_loader.py` | Canonical atom definitions |
| `fixed/roles.json` | `src/core/topology_reasoning.py` | 33 canonical roles |
| `fixed/dimensions.json` | `src/patterns/atom_classifier.py` | 8 classification dimensions |
| `fixed/scales.json` | `src/core/scale_classifier.py` | 16-level scale hierarchy |
| `viz/tokens/theme.tokens.json` | `tools/visualize_graph_webgl.py` | UI color tokens |

## DOCUMENTATION: Referenced in Specs (20 files)

These files are referenced in documentation and specifications:

| File | Referenced In | Purpose |
|------|---------------|---------|
| `edge_families.yaml` | `docs/specs/EDGE_TAXONOMY.md` | Edge type definitions |
| `lifecycle.yaml` | `docs/MODEL.md` | Node lifecycle states |
| `file_roles.yaml` | `docs/specs/FILE_ROLES_SPEC.md` | File-level role taxonomy |
| `purpose_ontology.yaml` | `docs/specs/PURPOSE_ONTOLOGY.md` | Purpose classification |
| `trust_model.yaml` | `docs/specs/TRUST_MODEL.md` | Security trust levels |
| `effect_model.yaml` | `docs/MODEL.md` | Side effect taxonomy |
| `boundary_model.yaml` | `docs/MODEL.md` | System boundary definitions |
| `state_model.yaml` | `docs/MODEL.md` | Statefulness classification |
| `layer_model.yaml` | `docs/MODEL.md` | Architectural layers |
| `pattern_registry.yaml` | `docs/specs/PATTERN_REGISTRY.md` | Pattern definitions |
| `pipeline_stages.yaml` | `docs/COLLIDER.md` | Pipeline documentation |
| `viz/panel_defaults.yaml` | `docs/specs/VISUALIZATION_UI_SPEC.md` | Panel configuration |
| `viz/layout_presets.yaml` | `docs/specs/VISUALIZATION_UI_SPEC.md` | Layout templates |
| `viz/filter_presets.yaml` | `docs/specs/VISUALIZATION_UI_SPEC.md` | Filter configurations |
| `viz/color_schemes.yaml` | `docs/specs/VISUALIZATION_UI_SPEC.md` | Color palette definitions |
| `fixed/families.json` | `docs/specs/EDGE_TAXONOMY.md` | Edge family constants |
| `fixed/layers.json` | `docs/MODEL.md` | Layer definitions |
| `fixed/tiers.json` | `docs/MODEL.md` | Atom tier definitions |
| `fixed/phases.json` | `docs/COLLIDER.md` | Pipeline phases |
| `fixed/metrics.json` | `docs/specs/METRICS_SPEC.md` | Health metric definitions |

## Orphan Analysis

**Finding:** No true orphans exist.

All 30 schema files are either:
1. Actively loaded by Python code (10 files), OR
2. Referenced in documentation/specifications (20 files)

The "documentation" files serve as the authoritative source for specs and model documentation. They are not dead weight - they are the single source of truth that documentation references.

## Data Integrity Issue Fixed

During audit, discovered inconsistent atom counts:

| Location | Before | After |
|----------|--------|-------|
| `schema/constants.yaml` | 3,616 | 3,525 |
| `CLAUDE.md` (Identity) | 3,644 | 3,525 |
| `CLAUDE.md` (T2 row) | 3,531 | 3,445 |

**Verified counts:**
- TIER0 (core): 42
- TIER1 (stdlib): 21
- TIER2 (base): 17
- T2 mined: 3,445
- **Total: 3,525** (80 core + 3,445 T2 mined)

## Recommendations

1. **No archival needed** - All files have valid references
2. **Maintain constants.yaml** - Use as single source of truth
3. **Consider schema consolidation** - 20 documentation schemas could potentially be merged into fewer files for easier maintenance

## Validation Commands

```bash
# Verify code-loaded schemas
grep -r "schema/" src/ --include="*.py" | grep -E "\.yaml|\.json"

# Verify documentation references
grep -r "schema/" docs/ --include="*.md"

# Verify atom counts
grep -c "^  - id:" src/patterns/ATOMS_TIER*.yaml
```

---

**Conclusion:** G08 audit complete. Zero orphan schemas found. All files retained with documented purpose.
