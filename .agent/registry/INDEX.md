# Agent Task Registry - Dashboard

> Quick view of all tasks and opportunities.
> **Updated:** 2026-01-25
> **Concerns:** See `standard-model-of-code/docs/OPEN_CONCERNS.md`

---

## Quick Stats

```
Inbox:      59 opportunities (50 imported from legacy + 9 new)
Active:     9 tasks (6 original + 3 Phase 10)
Batches:    1 (BATCH-010 Survey)
Archived:   1 task
Sprints:    1 active (SPRINT-001)
Legacy:     10 registries CONSOLIDATED into unified system
```

---

## 4D Confidence Scoring (Unified)

All tasks now use the unified 4D scoring system:

| Dimension | Question |
|-----------|----------|
| **Factual** | Is my understanding of current state correct? |
| **Alignment** | Does this serve the project's mission? |
| **Current** | Does this fit codebase as it exists? |
| **Onwards** | Does this fit where we're heading? |

**Formula:** `Overall = min(Factual, Alignment, Current, Onwards)`

**Verdict:**
- `>= 75%` → ACCEPT (ready to execute)
- `50-74%` → DEFER (needs work)
- `< 50%` → REJECT

**Tool:** `.agent/tools/confidence_validator.py TASK-XXX`

---

## Active Tasks

| ID | Title | Status | Confidence | Sprint |
|----|-------|--------|------------|--------|
| TASK-001 | Bootstrap agent coordination system | COMPLETE | 100% | SPRINT-001 |
| TASK-002 | Deep comparison with LangGraph architecture | DISCOVERY | 70% | - |
| TASK-003 | Fix promote_opportunity.sh multiline bug | COMPLETE | 100% | SPRINT-001 |
| TASK-004 | Execute CUTTING_PLAN: Bulk to Lean | READY | 95% | - |
| TASK-005 | Perplexity research tool | SCOPED | 85% | - |
| TASK-006 | Socratic audit misalignment fixes | SCOPED | 90% | - |
| **TASK-010-001** | **Create survey.py module** | **COMPLETE** | **100%** | **-** |
| **TASK-010-002** | **Directory pattern detector** | **COMPLETE** | **100%** | **-** |
| **TASK-010-003** | **Exclusion patterns config** | **COMPLETE** | **100%** | **-** |

---

## Discovery Inbox (59 opportunities)

### High Priority (>= 90% confidence)

| ID | Title | Category | Confidence |
|----|-------|----------|------------|
| OPP-023 | Define BaseStage Abstract Class | PIPELINE | 97% |
| OPP-024 | Extend Existing CodebaseState | PIPELINE | 100% |
| OPP-025 | Define PipelineManager | PIPELINE | 97% |
| OPP-026 | Create Pipeline Package Structure | PIPELINE | 95% |
| OPP-027 | Refactor run_full_analysis() | PIPELINE | 95% |
| OPP-013 | Create index.js | VISUALIZATION | 94% |
| OPP-014 | Update template.html | VISUALIZATION | 99% |
| **OPP-058** | **Fix FILES view toggle - data not switching** | **VISUALIZATION** | **85%** |
| **OPP-059** | **Fix ATOMS view toggle - data not restored** | **VISUALIZATION** | **85%** |

### Medium Priority (75-89%)

| ID | Title | Category | Confidence |
|----|-------|----------|------------|
| OPP-008 | Create scales.js | VISUALIZATION | 85% |
| OPP-009 | Create endpoints.js | VISUALIZATION | 90% |
| OPP-011 | Create bindings.js | VISUALIZATION | 88% |
| OPP-012 | Create blenders.js | VISUALIZATION | 87% |
| OPP-010 | Create presets.yaml | VISUALIZATION | 82% |
| OPP-018-022 | UPB Phase 6 tasks | VISUALIZATION | 85-92% |

### By Category

| Category | Count | Avg Confidence |
|----------|------:|---------------:|
| PIPELINE | 10 | 95% |
| VISUALIZATION | 24 | 85% |
| TOKEN_SYSTEM | 8 | 70% |
| TREE_SITTER | 1 | 80% |
| MODULARIZATION | 13 | 70% |
| SIDEBAR | 3 | 70% |

---

## Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `import_legacy_tasks.py` | Import from legacy registries | `./import_legacy_tasks.py scan` |
| `promote_opportunity.py` | Inbox → Active | `./promote_opportunity.py OPP-008` |
| `confidence_validator.py` | AI confidence assessment | `./confidence_validator.py TASK-002` |
| `task_store.py` | Task CRUD operations | `./task_store.py list` |
| `sprint.py` | Sprint management | `./sprint.py status` |

---

## Task Batches (Roadmap-Linked)

| Batch | Phase | Title | Status | Tasks |
|-------|-------|-------|--------|-------|
| BATCH-010 | 10 | Adaptive Intelligence Layer (SURVEY) | PLANNING | 23 |

### BATCH-010 Sub-Batches

| Sub | Title | Complexity | Status | Tasks |
|-----|-------|------------|--------|-------|
| 10.1 | Pattern-based exclusions | LOW | READY | 4 |
| 10.2 | Minification heuristics | LOW | READY | 4 |
| 10.3 | CLI --exclude flag | LOW | READY | 3 |
| 10.4 | Interactive survey mode | MEDIUM | BLOCKED | 4 |
| 10.5 | AI-powered classification | MEDIUM | BLOCKED | 4 |
| 10.6 | Auto-survey by default | LOW | BLOCKED | 4 |

**Start with:** 10.1, 10.2, 10.3 (parallel, no dependencies)

---

## Execution Priority

```
READY NOW (>= 95%):
  1. OPP-024  Extend CodebaseState        [100%] ← Already exists!
  2. OPP-023  Define BaseStage            [97%]
  3. OPP-025  Define PipelineManager      [97%]
  4. OPP-026  Pipeline Package Structure  [95%]
  5. OPP-027  Refactor run_full_analysis  [95%]
  6. OPP-014  Update template.html        [99%]

FILE VIZ BUGS (COMPLETE):
  ✓ OPP-058  Fix FILES toggle - data not switching  [FIXED]
  ✓ OPP-059  Fix ATOMS toggle - data not restored   [FIXED]

PHASE 10 SURVEY (COMPLETE - Sub-batch 10.1):
  ✓ TASK-010-001  Create survey.py module           [DONE] 620 LOC
  ✓ TASK-010-002  Directory pattern detector        [DONE] Integrated
  ✓ TASK-010-003  Default exclusion patterns config [DONE] exclusions.yaml

INTEGRATION VERIFIED:
  - survey.py integrated into full_analysis.py as Stage 0
  - CLI flags: --no-survey, --exclude <path>
  - BEFORE survey: 4,342 nodes (viz/assets)
  - AFTER survey:    795 nodes (82% reduction!)

BATCH PROMOTE:
  ./promote_opportunity.py OPP-023 OPP-024 OPP-025 OPP-026 OPP-027
```

---

## Legacy Source Files (Reference Only)

These files are now **read-only reference**. All tasks have been migrated:

| Registry | Path | Tasks Imported |
|----------|------|---------------:|
| UPB | `standard-model-of-code/docs/specs/UPB_TASK_REGISTRY.md` | 15 |
| Pipeline | `standard-model-of-code/docs/specs/PIPELINE_REFACTOR_TASK_REGISTRY.md` | 10 |
| Tree-sitter | `standard-model-of-code/docs/specs/TREE_SITTER_TASK_REGISTRY.md` | 1 |
| Token System | `standard-model-of-code/docs/reports/TOKEN_SYSTEM_TASK_REGISTRY.md` | 8 |
| Sidebar | `standard-model-of-code/docs/reports/SIDEBAR_REFACTOR_TASK_REGISTRY.md` | 3 |
| Modularization | `standard-model-of-code/docs/reports/MODULARIZATION_TASKS.md` | 13 |

---

## Archive

| ID | Title | Final Status | Archived |
|----|-------|--------------|----------|
| TASK-000 | Bootstrap agent coordination | COMPLETE | 2026-01-23 |

---

## Version

| Field | Value |
|-------|-------|
| Registry Version | 3.0.1 |
| Last Updated | 2026-01-23 |
| Consolidation | COMPLETE |
| Tasks Imported | 50 |
| Total Opportunities | 59 |
| Total Active Tasks | 6 |
