# Circuit Breaker Reconnaissance Report

**Date**: 2026-01-20
**Status**: FINDINGS COMPLETE
**Tool**: local_analyze.py (Gemini 2.5 Pro)
**Cost**: $0.19

## Executive Summary

The codebase is in a **transitional state** with half-finished refactoring from monolithic `app.js` to modules. This has created:

1. **Dueling State Managers**: Legacy `APPEARANCE_STATE` coexists with newer `VIS_STATE`
2. **Redundant Controls**: Duplicate sliders bound by different logic paths
3. **Broken Control Chains**: UI controls mutate state but never trigger visual updates
4. **Circular Overrides**: Modules compete for same Graph properties, silently overwriting each other

---

## BRANCH 1: Control Binding Integrity

### Working Chain Example (edge-opacity)
```
template.html:1150 (#cfg-edge-opacity)
    ↓ app.js:2178 (bindSlider)
    ↓ app.js:2179 (APPEARANCE_STATE.edgeOpacity = val)
    ↓ app.js:2181 (applyEdgeMode())
    ↓ edge-system.js:397 (Graph.linkOpacity(func))
    ↓ VISUAL EFFECT ✓
```

### BROKEN CHAINS

| Control | DOM Location | State Updated | Effect Trigger | Result |
|---------|--------------|---------------|----------------|--------|
| `cfg-toggle-pulse` | template.html:1123 | APPEARANCE_STATE.pulseAnimation | **NONE** (only console.log) | NON-FUNCTIONAL |
| `cfg-toggle-depth` | template.html:1127 | APPEARANCE_STATE.depthShading | **NONE** (only console.log) | NON-FUNCTIONAL |
| `physics-charge` | sidebar.js:681 | Calls Graph directly, NOT PHYSICS_STATE | Test validates wrong state | TEST WILL FAIL |

---

## BRANCH 2: State vs Effect Disconnect

### Dead State Properties (Set but never read)
| Property | Set At | Read At | Status |
|----------|--------|---------|--------|
| `APPEARANCE_STATE.pulseAnimation` | app.js:2153 | NOWHERE | DEAD |
| `APPEARANCE_STATE.depthShading` | app.js:2159 | NOWHERE | DEAD |
| `APPEARANCE_STATE.amplifierTarget` | app.js:294 | NOWHERE | DEAD |
| `PHYSICS_STATE` object | app.js:3332 | sidebar.js bypasses it | STALE |

---

## BRANCH 3: Race Conditions & Timing

### Acceptable
- Deferred UI init via `Promise.resolve().then()` - brief non-interactive window
- `_deferredViewMode` in sidebar.js - correctly handles startup race

### PROBLEMATIC
- **Animation Re-entry**: `popBoundaries` and `restoreBoundaries` have no locks
  - Rapid clicks cause visual glitches
  - Animations not atomic

---

## BRANCH 4: Dead Code & Unreachable Handlers

| Item | Location | Issue |
|------|----------|-------|
| Starfield toggle binding | sidebar.js:788 | HTML commented out (template.html:1280) |
| `btn-report` handlers | app.js:2351, 3570 | THREE redundant bindings |
| `btn-color-mode` test | circuit-breaker.js:173 | Element doesn't exist in template |
| `buildFileGraph` shim | app.js:1953 | Confusing: old function still exists at 1956 |

---

## BRANCH 5: Circular Overrides (THE SILENT KILLER)

### `Graph.linkOpacity()` - HIGHLY CONFLICTED
```
USER SLIDER → applyEdgeMode() → EDGE.apply() → Graph.linkOpacity(func)
                                                    ↑
EDGE STYLE BUTTONS → applyEdgeStyle() → Graph.linkOpacity(STATIC_VALUE)
                                        ↑ DESTROYS dynamic function!
```
**Impact**: Clicking 'solid' button breaks file-dimming until slider moved again

### `Graph.nodeColor()` - ARCHITECTURAL DISCONNECT
```
COLOR PRESETS → ColorOrchestrator → node.color
                        ↑
SELECTION SYSTEM → updateSelectionVisuals → node.color (BYPASSES ORCHESTRATOR)
```
**Impact**: Selection completely bypasses "SINGLE SOURCE OF TRUTH" ColorOrchestrator

### `Graph.linkWidth()` - CONFLICTED
```
USER SLIDER → EDGE.apply() → Graph.linkWidth(func with APPEARANCE_STATE.edgeWidth)
                                    ↑
FLOW MODE → applyFlowVisualization() → Graph.linkWidth(markov_weight_func)
                                       ↑ OVERWRITES user setting
```
**Impact**: Flow mode breaks width slider until moved again

---

## GAPS IDENTIFIED

### Controls with NO binding
- `#btn-dimension` (tested in circuit-breaker.js:194) - **ELEMENT DOESN'T EXIST**
- Actual button is `#btn-2d` at template.html:1316

### Invalid Circuit Breaker Tests
| Test Name | Issue |
|-----------|-------|
| `toggle-arrows` | Validation always returns true (boolean !== undefined) |
| `btn-color-mode` | Element doesn't exist |
| `dimension-toggle` | Wrong element ID |
| `physics-charge` | Validates PHYSICS_STATE which isn't updated |

---

## Recommendations

### Immediate Fixes (Circuit Breaker)
1. Fix `toggle-arrows` validation: `el.classList.contains('active')` not `!== undefined`
2. Remove `btn-color-mode` test - element doesn't exist
3. Fix `dimension-toggle` to use correct element ID `#btn-2d`
4. Fix `physics-charge` to call Graph API directly, not check stale state

### Architectural Fixes
1. **Single State Source**: Consolidate `APPEARANCE_STATE` + `PHYSICS_STATE` + `VIS_STATE`
2. **Effect Bus**: All Graph method calls go through single orchestrator
3. **Lock Animations**: Prevent re-entry during pop/restore
4. **Remove Dead Code**: Delete `pulseAnimation`, `depthShading`, `amplifierTarget`

### Testing Strategy
1. Auto-discover controls from template.html DOM
2. Spy on Graph methods to validate effect, not just state
3. Add per-test timeout (500ms default)
4. Visual regression testing with screenshots

---

## Files Referenced

| File | Purpose |
|------|---------|
| `template.html` | All control element IDs |
| `app.js` | Legacy bindings, APPEARANCE_STATE |
| `sidebar.js` | New modular bindings |
| `edge-system.js` | EDGE module, linkOpacity/linkWidth |
| `circuit-breaker.js` | Self-test module (this analysis target) |

---

## Next Session

1. Fix critical circuit-breaker.js bugs
2. Implement Graph method spying
3. Auto-generate test suite from template.html
