# UI Corpus v1

Generated: 2026-01-25
Source: Exhaustive codebase scan + Gemini forensic audit

## Purpose

Complete UI control inventory for task generation. Documents what exists, what's broken, and what should be added.

## Artifacts

| File | Contents |
|------|----------|
| `ui_control_inventory.json` | **60 controls** across 5 health categories (current state) |
| `ui_controls_schema.json` | **82 controls** full professional schema (target state) |
| `findings.json` | Critical fixes with file:line locations |
| `ui_layout_model.json` | 9-square semantic grid, containers |
| `ui_tokens.json` | CSS variables, design tokens |

**Full spec:** `docs/specs/UI_CONTROLS_SCHEMA.md`

## Control Health Summary

| Category | Count | Status |
|----------|-------|--------|
| 1. Verified Working | 9 | Circuit Breaker tested |
| 2. Likely Working | 20 | Has binding, untested |
| 3. Broken Chain | 13 | Orphaned/empty/missing |
| 4. Infrastructure Ready | 5 | Code exists, no UI |
| 5. Missing (MUST) | 4 | Core functionality gaps |
| 5. Missing (SHOULD) | 5 | Expected features |
| 5. Missing (COULD) | 4 | Nice-to-have |
| **Total Ideal** | **60** | Target state |

## Task Generation Priority

| Phase | Action | Effort | Impact |
|-------|--------|--------|--------|
| 1 | Fix 3 empty handlers | LOW | HIGH |
| 2 | Wire 3 orphaned controls | LOW | MEDIUM |
| 3 | Add 4 missing HTML elements | MEDIUM | MEDIUM |
| 4 | Remove 3 duplicate legacy IDs | LOW | LOW |
| 5 | Add 5 infrastructure UIs | MEDIUM | HIGH |
| 6 | Implement 4 MUST controls | HIGH | HIGH |
| 7 | Implement 5 SHOULD controls | HIGH | MEDIUM |
| 8 | Expand Circuit Breaker to 25+ | MEDIUM | HIGH |

## P0 Fixes (Empty Handlers)

1. **cfg-label-size** → sidebar.js:L831
2. **cfg-toggle-highlight** → sidebar.js:L787
3. **cfg-toggle-depth** → sidebar.js:L797

## P1 Fixes (Orphaned Controls)

1. **cfg-toggle-edge-hover** → needs addEventListener
2. **cfg-toggle-codome** → needs addEventListener
3. **[data-edge-style]** → needs click handler for Solid/Dashed/Particle

## MUST-Add Controls

1. **undo-action** - No way to undo camera/selection
2. **export-selection** - Can't export selected subgraph
3. **help-overlay** - No keyboard shortcut discoverability
4. **loading-indicator** - No feedback during computation

## Next Phase

Phase 2: Manual verification of corpus against actual template.html line numbers.
