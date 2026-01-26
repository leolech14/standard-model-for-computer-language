# Ghost Exorcism Plan

**Date:** 2026-01-26
**Status:** PHASE 1 COMPLETE
**Agents:** 6 parallel scans completed

## Execution Log

| Phase | Date | Ghosts Fixed | Commit |
|-------|------|--------------|--------|
| 0+1 | 2026-01-26 | G02, G03, G05, G06, G09, G10 | fb80372 |
| 1 (cont) | 2026-01-26 | G04, G07 | (pending) |

---

## Confidence Matrix

| ID | Ghost | Confidence | Severity | Effort | Risk if Ignored |
|----|-------|:----------:|:--------:|:------:|-----------------|
| G01 | Duplicate Atom IDs (16) | 95% | CRITICAL | 2h | Classification breaks |
| G02 | canonical/ → schema/ path | 90% | CRITICAL | 30m | Pattern loading fails |
| G03 | Multi-doc YAML antimatter | 95% | CRITICAL | 15m | Crash on schema load |
| G04 | Event listener leaks (114) | 85% | HIGH | 4h | Memory bloat after 5 reloads |
| G05 | 10 Orphan JS modules | 98% | HIGH | 30m | 2K dead lines in repo |
| G06 | pattern_registry duplicate | 90% | HIGH | 1h | Maintenance confusion |
| G07 | Global shadowing (IS_3D) | 80% | HIGH | 2h | Race conditions |
| G08 | 20 Orphan schema files | 75% | MEDIUM | 1h | Clutter, false trails |
| G09 | runpod_setup.sh broken | 100% | MEDIUM | 5m | Script unusable |
| G10 | Quarantined code (3 files) | 95% | MEDIUM | 30m | Developer confusion |
| G11 | Unused Python classes (10) | 70% | LOW | 2h | Code bloat |
| G12 | Never-called JS exports (12) | 75% | LOW | 1h | Bundle bloat |
| G13 | TODO markers (4) | 100% | LOW | 30m | Tech debt |
| G14 | Temp file cleanup | 60% | LOW | 30m | /tmp accumulation |

---

## Execution Phases

### Phase 0: CRITICAL (Must Fix Now)
**Time:** ~3 hours | **Confidence:** 93% avg

| Step | Ghost | Action | Validation |
|------|-------|--------|------------|
| 0.1 | G03 | Fix antimatter_laws.yaml multi-doc | `python -c "import yaml; yaml.safe_load(open('schema/antimatter_laws.yaml'))"` |
| 0.2 | G02 | Replace `canonical/` with `schema/` in 4 files | `grep -r "canonical/" src/` returns 0 |
| 0.3 | G01 | Generate unique atom IDs | `jq '.[] | .id' schema/fixed/atoms.json | sort | uniq -d` returns 0 |

### Phase 1: HIGH PRIORITY (This Sprint)
**Time:** ~8 hours | **Confidence:** 88% avg

| Step | Ghost | Action | Validation |
|------|-------|--------|------------|
| 1.1 | G05 | Move 10 orphan JS to `archive/viz_orphans/` | Build succeeds, no 404s |
| 1.2 | G06 | Delete pattern_repository.py, keep pattern_registry.py | Tests pass |
| 1.3 | G09 | Fix YOUR_USERNAME in runpod_setup.sh | Script parses without error |
| 1.4 | G04 | Add destroy() to sidebar.js, panel-handlers.js | Manual test: reload 10x, check memory |
| 1.5 | G07 | Centralize IS_3D, GRAPH_MODE in VIS_STATE | `grep "window.IS_3D ="` returns only VIS_STATE |

### Phase 2: MEDIUM PRIORITY (Next Sprint)
**Time:** ~2 hours | **Confidence:** 82% avg

| Step | Ghost | Action | Validation |
|------|-------|--------|------------|
| 2.1 | G10 | Remove quarantined code from 3 files | No `QUARANTINED` comments remain |
| 2.2 | G08 | Audit 20 orphan schemas, archive unused | Document decisions in SCHEMA_AUDIT.md |

### Phase 3: LOW PRIORITY (Backlog)
**Time:** ~4 hours | **Confidence:** 70% avg

| Step | Ghost | Action | Validation |
|------|-------|--------|------------|
| 3.1 | G11 | Delete unused Python classes | Tests pass, no import errors |
| 3.2 | G12 | Remove never-called JS exports | Bundle size decreases |
| 3.3 | G13 | Resolve 4 TODO markers | `grep -r "TODO\|FIXME" src/` returns 0 |
| 3.4 | G14 | Add temp file cleanup to tests | No /tmp/*.js after test run |

---

## Detailed Actions

### G01: Duplicate Atom IDs (CRITICAL)

**Problem:** 16 atom IDs map to multiple names (e.g., `DAT.PRM.A` → 10 different atoms)

**Current:**
```json
{ "id": "DAT.PRM.A", "name": "Boolean" },
{ "id": "DAT.PRM.A", "name": "Integer" },
{ "id": "DAT.PRM.A", "name": "Float" },
```

**Fix:**
```json
{ "id": "DAT.PRM.BOOL", "name": "Boolean" },
{ "id": "DAT.PRM.INT", "name": "Integer" },
{ "id": "DAT.PRM.FLT", "name": "Float" },
```

**Files:** `schema/fixed/atoms.json`

**Validation:**
```bash
jq -r '.[].id' schema/fixed/atoms.json | sort | uniq -d
# Should return empty (no duplicates)
```

---

### G02: Path Mismatch (CRITICAL)

**Problem:** Code looks for `canonical/` but schemas are in `schema/`

**Files to fix:**
1. `src/core/registry/pattern_repository.py`
2. `src/core/registry/pattern_registry.py`
3. `src/scripts/run_benchmark.py`
4. `src/scripts/extract_patterns.py`

**Search:** `grep -rn "canonical/" src/`

**Replace:** `canonical/` → `schema/`

---

### G03: Multi-doc YAML (CRITICAL)

**Problem:** `schema/antimatter_laws.yaml` has `---` separators creating multiple YAML documents

**Fix Option A:** Remove `---` separators (keep as single doc)
**Fix Option B:** Use `yaml.safe_load_all()` in loader

**Recommended:** Option A (simpler)

---

### G04: Event Listener Leaks (HIGH)

**Problem:** 114 listeners added, only 2 removed

**Fix Pattern:**
```javascript
// Add to sidebar.js
const SIDEBAR = (function() {
    const _listeners = [];

    function _addListener(el, event, handler) {
        el.addEventListener(event, handler);
        _listeners.push({ el, event, handler });
    }

    function destroy() {
        _listeners.forEach(({ el, event, handler }) => {
            el.removeEventListener(event, handler);
        });
        _listeners.length = 0;
    }

    return { ..., destroy };
})();
```

**Files:** sidebar.js, panel-handlers.js, panel-system.js, selection.js

---

### G05: Orphan JS Modules (HIGH)

**Modules to archive:**
```
AxialLayout.js
HolarchyMapper.js
InteractionManager.js
TowerRenderer.js
CodomeHUD.js
SettingsPanel.js
unlit-nodes.js
pipeline-navigator.js
file-tree-layout.js
hardware-info.js
```

**Command:**
```bash
mkdir -p archive/viz_modules_orphaned
mv src/core/viz/assets/modules/{AxialLayout,HolarchyMapper,InteractionManager,TowerRenderer,CodomeHUD,SettingsPanel,unlit-nodes,pipeline-navigator,file-tree-layout,hardware-info}.js archive/viz_modules_orphaned/
```

---

### G06: Duplicate Pattern Files (HIGH)

**Problem:** `pattern_registry.py` and `pattern_repository.py` have identical functions

**Decision:** Keep `pattern_registry.py`, delete `pattern_repository.py`

**Validation:**
```bash
diff src/core/registry/pattern_registry.py src/core/registry/pattern_repository.py
# Review differences, merge if needed
```

---

### G07: Global Shadowing (HIGH)

**Problem:** Multiple modules write to `window.IS_3D`, `window.GRAPH_MODE`

**Fix:** Centralize in VIS_STATE:
```javascript
// vis-state.js
const VIS_STATE = {
    _is3D: true,
    _graphMode: 'atoms',

    get is3D() { return this._is3D; },
    set is3D(val) {
        this._is3D = val;
        EVENT_BUS.emit('dimension:changed', val);
    },
    // ...
};
```

**Then replace:**
- `window.IS_3D = x` → `VIS_STATE.is3D = x`
- `window.IS_3D` (read) → `VIS_STATE.is3D`

---

## Risk Assessment

| Phase | Risk Level | Mitigation |
|-------|------------|------------|
| Phase 0 | LOW | Schema changes, no runtime impact |
| Phase 1 | MEDIUM | JS changes need browser testing |
| Phase 2 | LOW | Cleanup only, no behavior change |
| Phase 3 | LOW | Optional, can defer indefinitely |

---

## Success Criteria

### Phase 0 Complete When:
- [ ] `yaml.safe_load(antimatter_laws.yaml)` succeeds
- [ ] `grep -r "canonical/" src/` returns 0 matches
- [ ] `jq '.[].id' atoms.json | sort | uniq -d` returns empty

### Phase 1 Complete When:
- [ ] 10 orphan modules moved to archive
- [ ] pattern_repository.py deleted
- [ ] runpod_setup.sh has valid repo URL
- [ ] sidebar.js has destroy() method
- [ ] VIS_STATE owns all global state

### Phase 2 Complete When:
- [ ] No `QUARANTINED` comments in codebase
- [ ] SCHEMA_AUDIT.md documents all schema decisions

### Phase 3 Complete When:
- [ ] `grep -r "TODO\|FIXME" src/` returns only intentional markers
- [ ] All unused classes documented or removed

---

## Execution Order

```
Phase 0 (3h) ─────────────────────────────────────────►
              │
              ▼
         Phase 1 (8h) ───────────────────────────────►
                        │
                        ▼
                   Phase 2 (2h) ─────────────────────►
                                 │
                                 ▼
                            Phase 3 (4h) ───────────►
```

**Total Estimated Time:** 17 hours
**Minimum Viable:** Phase 0 + Phase 1 = 11 hours
**Critical Path:** Phase 0 = 3 hours

---

## Confidence Summary

| Metric | Value |
|--------|-------|
| Ghosts identified | 14 |
| Confidence range | 60-100% |
| Average confidence | 84% |
| Critical issues | 3 |
| High priority | 5 |
| Medium priority | 2 |
| Low priority | 4 |

---

**Status:** Plan ready for execution
**Next:** Approve and proceed with Phase 0
