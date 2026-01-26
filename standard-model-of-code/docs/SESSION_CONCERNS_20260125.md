# Session Concerns Consolidation (2026-01-25)

**Session ID:** UI Control Expansion + Gatekeeper System
**Commits:** 4 (`7477e0f`, `1ab140f`, `95e147b`, `1d2da26`)
**Validator:** Perplexity (8-agent consensus)
**Status:** ACTIONABLE

---

## Executive Summary

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Controls | 33 | 90 | +57 |
| Target | 82 | 82 | - |
| Coverage | 40% | 110% | +70% |
| Gatekeeper | None | CONTROL_REGISTRY.yaml | NEW |

---

## Prioritized Concerns

### C1. Handler Wiring Gap
| Attribute | Value |
|-----------|-------|
| **Severity** | 9/10 |
| **Confidence** | 95% |
| **Risk** | Orphaned controls (visible but non-functional) |
| **Blocking** | No, but degraded UX |

**Steps (5):**
1. Extract all control IDs from `template.html` → `control_ids.txt`
2. Extract all handler bindings from `panel-handlers.js` → `handler_ids.txt`
3. Diff: `comm -23 control_ids.txt handler_ids.txt` → orphans
4. For each orphan: add handler or remove control
5. Add to validator: `--check-handlers` mode

**Validation:**
```bash
grep -oP 'id="[^"]+"' src/core/viz/assets/template.html | sort -u > /tmp/controls.txt
grep -oP "getElementById\(['\"]([^'\"]+)" src/core/viz/assets/modules/panel-handlers.js | sort -u > /tmp/handlers.txt
comm -23 /tmp/controls.txt /tmp/handlers.txt
```

---

### C2. Registry-Template Mismatch
| Attribute | Value |
|-----------|-------|
| **Severity** | 8/10 |
| **Confidence** | 90% |
| **Risk** | False positives in validation |
| **Blocking** | No |

**Root Cause:** Validator flags structural IDs as unauthorized.

**Structural IDs (16):** `3d-graph`, `header`, `loader`, `toast`, `control-bar-container`, `filtering`, `selection`, `camera`, `accessibility`, `export`, `analysis`, `layout-phys`, `view-modes`, `panel-settings`, `node-appear`, `edge-appear`

**Steps (3):**
1. Add `STRUCTURAL_IDS` allowlist to `validate_control_registry.py`
2. Filter allowlist from audit comparison
3. Re-run audit → expect 0 unauthorized

**Code Change:**
```python
STRUCTURAL_IDS = {
    '3d-graph', 'header', 'loader', 'toast', 'control-bar-container',
    'filtering', 'selection', 'camera', 'accessibility', 'export',
    'analysis', 'layout-phys', 'view-modes', 'panel-settings',
    'node-appear', 'edge-appear'
}

# In audit_template():
unauthorized = template_ids - authorized - STRUCTURAL_IDS
```

---

### C3. Pre-commit Hook Not Wired
| Attribute | Value |
|-----------|-------|
| **Severity** | 7/10 |
| **Confidence** | 85% |
| **Risk** | Unregistered controls can still be added |
| **Blocking** | No |

**Steps (4):**
1. Add hook to `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: control-registry
      name: UI Control Registry Check
      entry: python tools/validate_control_registry.py --audit
      language: system
      files: template\.html$
      pass_filenames: false
```
2. Run `pre-commit install`
3. Test: `pre-commit run control-registry --all-files`
4. Document bypass in README: `git commit --no-verify`

---

### C4. Controls Untested
| Attribute | Value |
|-----------|-------|
| **Severity** | 6/10 |
| **Confidence** | 80% |
| **Risk** | Broken controls ship to users |
| **Blocking** | No |

**Steps (3):**
1. Regenerate HTML: `./collider full . --output .collider`
2. Open in browser, manually click through each panel
3. Log failures in `docs/QA_CONTROL_CHECKLIST.md`

**Minimum Viable QA:**
- [ ] All sliders move and update graph
- [ ] All toggles change state visually
- [ ] All buttons trigger actions
- [ ] No console errors on interaction

---

### C5. Plan File Stale
| Attribute | Value |
|-----------|-------|
| **Severity** | 3/10 |
| **Confidence** | 100% |
| **Risk** | Confusion in future sessions |
| **Blocking** | No |

**Steps (2):**
1. Update `.claude/plans/generic-questing-zebra.md` status to COMPLETE
2. Add "Exceeded target: 90/82 controls" note

---

### C6. Gatekeeper Pattern Validation
| Attribute | Value |
|-----------|-------|
| **Severity** | 6/10 (informational) |
| **Confidence** | 85% |
| **Risk** | Pattern may not scale |
| **Blocking** | No |

**Perplexity Verdict:** Pattern is SOUND.

**Enhancements (optional):**
1. Add YAML schema validation for CONTROL_REGISTRY.yaml
2. Add risk-tiering (high-risk controls need approval)
3. Consider GitHub Actions for workflow enforcement

---

## Action Matrix

| ID | Concern | Severity | Steps | Time Est. | Owner |
|----|---------|:--------:|:-----:|-----------|-------|
| C1 | Handler Wiring | 9 | 5 | 30min | Agent |
| C2 | Registry Mismatch | 8 | 3 | 10min | Agent |
| C3 | Pre-commit Hook | 7 | 4 | 15min | Agent |
| C4 | QA Testing | 6 | 3 | 20min | Human |
| C5 | Plan Update | 3 | 2 | 5min | Agent |
| C6 | Pattern Review | 6 | 0 | Done | - |

**Total Steps:** 17
**Agent Steps:** 14
**Human Steps:** 3 (QA testing)

---

## Recommended Execution Order

```
C2 (10min) → C1 (30min) → C3 (15min) → C5 (5min) → C4 (Human)
```

**Rationale:**
1. C2 fixes validator first (unblocks C1)
2. C1 is highest severity
3. C3 prevents future regressions
4. C5 is housekeeping
5. C4 requires human interaction

---

## Confidence Scores Summary

| Concern | Severity | Confidence | Validated By |
|---------|:--------:|:----------:|--------------|
| C1 Handler Wiring | 9/10 | 95% | Perplexity + Logic |
| C2 Registry Mismatch | 8/10 | 90% | Audit output |
| C3 Pre-commit | 7/10 | 85% | Perplexity |
| C4 QA Testing | 6/10 | 80% | Best practice |
| C5 Plan Stale | 3/10 | 100% | Direct observation |
| C6 Pattern | 6/10 | 85% | Perplexity |

---

## Session Artifacts

| Artifact | Path |
|----------|------|
| Control Registry | `schema/viz/controls/CONTROL_REGISTRY.yaml` |
| Validator Script | `tools/validate_control_registry.py` |
| Perplexity Research | `docs/research/perplexity/docs/20260125_220611_*.md` |
| This Document | `docs/SESSION_CONCERNS_20260125.md` |

---

## Definition of Done

- [ ] C1: `--audit` shows 0 unwired handlers
- [ ] C2: `--audit` shows 0 unauthorized (after filter)
- [ ] C3: Pre-commit hook blocks unregistered controls
- [ ] C4: All 90 controls manually verified
- [ ] C5: Plan file marked COMPLETE
