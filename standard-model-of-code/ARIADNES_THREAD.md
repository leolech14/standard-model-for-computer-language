# ARIADNE'S THREAD - Active Work Tracker

> **Purpose:** Don't get lost in the labyrinth. This file tracks ALL active work streams.
> **Last Updated:** 2026-01-19
> **Session:** Architecture Investigation + Sidebar Refactor

---

## CURRENT POSITION

**We are HERE:** Completed architecture anti-pattern investigation. Discovered Collider cannot analyze its own JavaScript visualization layer (0 edges, 100% Unknown roles). Root cause: `body_source` not extracted for JS.

**Immediate blocker:** None. Investigation complete. Awaiting decision on next priority.

---

## WORK STREAMS (Priority Order)

### 1. ARCHITECTURE INVESTIGATION [COMPLETE]
- **Doc:** `docs/reports/ARCHITECTURE_ANTI_PATTERN_INVESTIGATION.md`
- **Finding 1:** Implicit Global State Machine (13+ globals, 95+ mutations)
- **Finding 2:** Collider JS analysis broken (empty `body_source`)
- **Recommendation:** Facade pattern (Option B) for viz layer
- **Status:** DONE - Awaiting product decisions

### 2. SIDEBAR REFACTOR [READY - 12 tasks]
- **Doc:** `docs/reports/SIDEBAR_REFACTOR_TASK_REGISTRY.md`
- **Depends on:** Architecture decision (Facade pattern approval)
- **S001:** DONE (template.html created)
- **S002-S013:** READY (90%+ confidence)
- **Status:** BLOCKED on architecture decision

### 3. OBSERVABILITY LAYER [PARTIAL - Plan approved]
- **Plan:** `~/.claude/plans/cryptic-percolating-beaver.md`
- **Created:** `src/core/observability.py` (11KB)
- **TODO:** Integration into `full_analysis.py`
- **TODO:** CLI flags (`--timing`, `--verbose-timing`)
- **TODO:** Brain Download PERFORMANCE section
- **Status:** 30% complete

### 4. DOCS IMPROVEMENT [TODO - 9 tasks]
- **Doc:** `docs/reports/DOCS_IMPROVEMENT_TASK_REGISTRY.md`
- **T-DOC-001 to T-DOC-009:** All TODO
- **T-DOC-010:** COMPLETE (mirror config)
- **Status:** Not started (lower priority)

### 5. PRODUCT GAPS [DISCOVERED - Need roadmap decision]
| Gap | Impact | Fix |
|-----|--------|-----|
| JS body_source empty | 0 edges for JS | tree-sitter change |
| Manager suffix missing | DataManager not detected | 1-line heuristics fix |

---

## UNCOMMITTED CHANGES

```
MUST COMMIT:
- docs/reports/ARCHITECTURE_ANTI_PATTERN_INVESTIGATION.md (NEW)
- docs/reports/SIDEBAR_REFACTOR_TASK_REGISTRY.md (NEW)
- src/core/observability.py (NEW)
- src/core/viz/assets/template.html (MODIFIED)

REVIEW NEEDED:
- cli.py (MODIFIED)
- src/core/full_analysis.py (MODIFIED)
- src/core/brain_download.py (MODIFIED)
- src/core/viz/assets/app.js (MODIFIED)
```

---

## DECISION POINTS NEEDED

1. **Sidebar Refactor:** Proceed with Facade pattern (Option B)?
   - YES → Execute S002-S013
   - NO → Document and shelve

2. **Observability Layer:** Complete integration?
   - YES → Wire into full_analysis.py + CLI
   - NO → Keep observability.py as standalone

3. **JS Body Extraction:** Priority for Collider roadmap?
   - YES → Create task, estimate effort
   - NO → Document as known limitation

4. **Quick Win:** Add `'Manager': 'Service'` to heuristics?
   - 1-line change in `src/core/heuristic_classifier.py:74`

---

## NAVIGATION

| If you want to... | Go to... |
|-------------------|----------|
| Understand the anti-pattern | `docs/reports/ARCHITECTURE_ANTI_PATTERN_INVESTIGATION.md` |
| Execute sidebar refactor | `docs/reports/SIDEBAR_REFACTOR_TASK_REGISTRY.md` |
| Complete observability | `~/.claude/plans/cryptic-percolating-beaver.md` |
| Improve docs | `docs/reports/DOCS_IMPROVEMENT_TASK_REGISTRY.md` |
| See all task registries | `docs/reports/*_TASK_REGISTRY.md` |

---

## SESSION LOG

| Date | Action | Outcome |
|------|--------|---------|
| 2026-01-19 | Sidebar refactor started | Discovered architecture anti-pattern |
| 2026-01-19 | Deep research on VIS_FILTERS | Mapped 55+ reads, 40+ writes |
| 2026-01-19 | Ran Collider self-analysis | Found JS edge extraction broken |
| 2026-01-19 | Root cause analysis | `body_source` empty for JS |
| 2026-01-19 | Created investigation doc | Complete with remediation options |
| 2026-01-19 | Created this tracking file | Context preserved |

---

## QUICK RESUME COMMAND

```bash
# Read this file first
cat ARIADNES_THREAD.md

# Then check current git state
git status --short

# Then decide: commit, continue, or pivot
```

---

*"The thread that leads out of the labyrinth."*
