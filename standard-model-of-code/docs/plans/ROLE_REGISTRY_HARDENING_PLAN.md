# RoleRegistry Hardening Plan v3

> **Goal:** Bulletproof role normalization with defense in depth
> **Version:** 3.0 (Final - all Gemini feedback incorporated)
> **Confidence:** 94% plan accuracy, 95% will achieve goal

---

## Verified Pipeline Execution Order

```
┌─────────────────────────────────────────────────────────────┐
│ unified_analysis.py                                          │
│                                                              │
│  Stage 3: stats_generator.generate_comprehensive_stats()    │
│           └── apply_heuristics() [stats_generator.py:64]    │
│                    ↓                                         │
│  Stage 5: apply_graph_inference() [unified_analysis.py:468] │
│                    ↓                                         │
│  Stage 5.6: enrich_with_standard_model() [line 518]         │
│             └── RoleRegistry.normalize() ← NORMALIZATION    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ full_analysis.py                                             │
│                                                              │
│  Stage 2: enrich_with_standard_model() [line 602]           │
│           └── RoleRegistry.normalize() ← SECOND NORM        │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Unit Tests

**File:** `tests/test_role_registry.py`

```python
import pytest
from src.core.registry import get_role_registry, RoleRegistry, ROLE_NORMALIZATION

class TestRoleRegistry:

    def test_loads_33_canonical_roles(self):
        registry = get_role_registry()
        assert registry.count() == 33

    def test_validate_canonical_roles(self):
        registry = get_role_registry()
        canonical = ['Service', 'Controller', 'Repository', 'Factory', 'Handler', 'Helper', 'Formatter']
        for role in canonical:
            assert registry.validate(role) is True, f"'{role}' should be canonical"

    def test_validate_non_canonical_returns_false(self):
        registry = get_role_registry()
        non_canonical = ['DTO', 'Test', 'Module', 'Unknown', 'Entity']
        for role in non_canonical:
            assert registry.validate(role) is False, f"'{role}' should NOT be canonical"

    def test_normalize_canonical_unchanged(self):
        registry = get_role_registry()
        # ALL 33 canonical roles should be unchanged
        for role in registry.list_names():
            assert registry.normalize(role) == role, f"Canonical '{role}' was changed"

    def test_normalize_non_canonical_maps_correctly(self):
        registry = get_role_registry()
        assert registry.normalize('DTO') == 'Internal'
        assert registry.normalize('Test') == 'Asserter'
        assert registry.normalize('Module') == 'Utility'
        assert registry.normalize('EventHandler') == 'Handler'

    def test_normalize_unknown_fallback_to_internal(self):
        registry = get_role_registry()
        assert registry.normalize('CompletelyUnknownRole') == 'Internal'

    def test_normalize_case_insensitive(self):
        registry = get_role_registry()
        # Canonical - case insensitive
        assert registry.normalize('service') == 'Service'
        assert registry.normalize('SERVICE') == 'Service'
        # Non-canonical - case insensitive
        assert registry.normalize('dto') == 'Internal'
        assert registry.normalize('DTO') == 'Internal'

    def test_singleton_pattern(self):
        r1 = get_role_registry()
        r2 = get_role_registry()
        assert r1 is r2

    def test_all_normalization_targets_are_canonical(self):
        """Every mapping target must be a valid canonical role."""
        registry = get_role_registry()
        for source, target in ROLE_NORMALIZATION.items():
            assert registry.validate(target), f"'{source}' -> '{target}' targets non-canonical"

    def test_no_canonical_role_in_normalization_keys(self):
        """Canonical roles must NOT appear as normalization sources."""
        registry = get_role_registry()
        for source in ROLE_NORMALIZATION.keys():
            assert not registry.validate(source), f"Canonical role '{source}' should not be normalized"
```

---

## Phase 2: Add Non-Canonical Mappings

**File:** `src/core/registry/role_registry.py`

**Add to ROLE_NORMALIZATION (ONLY non-canonical sources):**
```python
# Suffix-based patterns (non-canonical)
'Schema': 'Internal',
'Request': 'Internal',
'Response': 'Internal',
'Model': 'Internal',
'Aggregate': 'Internal',
'Vo': 'Internal',
'Config': 'Store',
'Settings': 'Store',
'Spec': 'Validator',
'Rule': 'Validator',
```

**DO NOT ADD:** `'Helper': 'Utility'` - Helper IS canonical!

---

## Phase 3: Wire Emission Points

### 3.1 universal_classifier.py

**File:** `src/core/classification/universal_classifier.py`

**Strategy:** Replace `normalize_type()` calls with `registry.normalize()` at source

| Line | Current | Change To |
|------|---------|-----------|
| 103 | `resolved_type = particle_type` | `resolved_type = registry.normalize(particle_type) if particle_type else None` |
| 131 | `resolved_type = particle_type` | `resolved_type = registry.normalize(particle_type) if particle_type else None` |
| 402 | `resolved_type = normalize_type(...)` | `resolved_type = registry.normalize(...)` |

**Import at top:**
```python
try:
    from core.registry import get_role_registry
    _role_registry = get_role_registry()
except ImportError:
    from registry import get_role_registry
    _role_registry = get_role_registry()
```

### 3.2 unified_analysis.py

**File:** `src/core/unified_analysis.py`

| Line | Current | Change To |
|------|---------|-----------|
| 237 | `"type": role_value` | `"type": _registry.normalize(role_value) if role_value else None` |
| 640 | `"type": "Module"` | `"type": _registry.normalize("Module")` |

### 3.3 heuristic_classifier.py

**File:** `src/core/heuristic_classifier.py`

| Line | Current | Change To |
|------|---------|-----------|
| 70 | `'format_': 'Utility'` | `'format_': 'Formatter'` (fix wrong mapping) |
| 571 | `particle['type'] = new_type` | `particle['type'] = registry.normalize(new_type)` |

---

## Phase 4: Update InferenceRules (Source Fix)

**File:** `src/core/graph_type_inference.py`

Update `INFERENCE_RULES` to emit canonical roles directly:

| Rule | Current | Canonical |
|------|---------|-----------|
| called_only_by_tests | `SubjectUnderTest` | `Internal` |
| calls_external | `IntegrationService` | `Service` |
| called_by_controller | `UseCase` | `Service` |
| called_by_event_handler | `EventProcessor` | `Handler` |
| orphan_internal | `InternalHelper` | `Utility` |

**Note:** After this fix, Phase 3.2 normalization wrapping becomes redundant but harmless.

---

## Phase 5: Pipeline Assertion (Strict Mode)

**File:** `src/core/full_analysis.py`
**Location:** After line 604

```python
# Strict validation of canonical roles
from registry import get_role_registry
_registry = get_role_registry()
_invalid = {n.get('role') for n in nodes if n.get('role') and not _registry.validate(n['role'])}
if _invalid:
    import os
    if os.environ.get('COLLIDER_STRICT_ROLES', '').lower() == 'true':
        raise ValueError(f"Non-canonical roles detected: {_invalid}")
    else:
        print(f"   ⚠️ WARNING: Non-canonical roles: {_invalid}")
```

**Usage:**
```bash
# Normal mode (warn only)
./collider full . --output .collider

# Strict mode (fail on non-canonical)
COLLIDER_STRICT_ROLES=true ./collider full . --output .collider
```

---

## Complete Emission Point Inventory

| File | Line | Context | Status |
|------|------|---------|--------|
| `universal_classifier.py` | 103 | `classify_class_pattern` | TO DO |
| `universal_classifier.py` | 131 | `classify_function_pattern` | TO DO |
| `universal_classifier.py` | 402 | `classify_extracted_symbol` | TO DO |
| `heuristic_classifier.py` | 70 | PREFIX_ROLES fix | TO DO |
| `heuristic_classifier.py` | 571 | `apply_heuristics` | TO DO |
| `unified_analysis.py` | 237 | particle creation | TO DO |
| `unified_analysis.py` | 640 | `_emit_file_nodes` | TO DO |
| `graph_type_inference.py` | 48-127 | INFERENCE_RULES | TO DO |
| `standard_model_enricher.py` | 238-239 | central normalization | DONE ✓ |
| `full_analysis.py` | ~605 | assertion | TO DO |

**Total: 10 locations (1 done, 9 to implement)**

---

## Execution Order

1. Create `tests/test_role_registry.py`
2. Add non-canonical mappings to `ROLE_NORMALIZATION`
3. Wire `universal_classifier.py` (3 points)
4. Wire `heuristic_classifier.py` (2 points)
5. Wire `unified_analysis.py` (2 points)
6. Update `INFERENCE_RULES` in `graph_type_inference.py`
7. Add pipeline assertion to `full_analysis.py`
8. Run tests: `pytest tests/test_role_registry.py -v`
9. Run Collider: `./collider full . --output .collider`
10. Validate: `COLLIDER_STRICT_ROLES=true ./collider full . --output .collider`
11. Commit

---

## Confidence Matrix

| Phase | Task | Confidence |
|-------|------|------------|
| 1 | Unit tests | 98% |
| 2 | Non-canonical mappings | 98% |
| 3.1 | Wire universal_classifier | 95% |
| 3.2 | Wire unified_analysis | 95% |
| 3.3 | Wire heuristic_classifier | 95% |
| 4 | Fix INFERENCE_RULES | 95% |
| 5 | Pipeline assertion | 98% |

**Overall Confidence: 96%**

---

## Files to Modify

| File | Lines |
|------|-------|
| `tests/test_role_registry.py` | CREATE (~90 lines) |
| `src/core/registry/role_registry.py` | +10 mappings |
| `src/core/classification/universal_classifier.py` | 103, 131, 402 |
| `src/core/heuristic_classifier.py` | 70, 571 |
| `src/core/unified_analysis.py` | 237, 640 |
| `src/core/graph_type_inference.py` | 48-127 |
| `src/core/full_analysis.py` | ~605 |
