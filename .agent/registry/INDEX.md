# Agent Task Registry - Dashboard

> Quick view of all tasks and opportunities.
> **Updated:** 2026-01-23 (Post-Consolidation)

---

## Quick Stats

```
Inbox:      57 opportunities (50 imported from legacy + 7 original)
Active:     6 tasks
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

**Tool:** `.agent/tools/boost_confidence.py TASK-XXX`

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

---

## Discovery Inbox (57 opportunities)

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
| VISUALIZATION | 22 | 85% |
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
| `boost_confidence.py` | AI confidence assessment | `./boost_confidence.py TASK-002` |
| `task_registry.py` | Task CRUD operations | `./task_registry.py list` |
| `sprint.py` | Sprint management | `./sprint.py status` |

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
| Registry Version | 3.0.0 |
| Last Updated | 2026-01-23 |
| Consolidation | COMPLETE |
| Tasks Imported | 50 |
| Total Opportunities | 57 |
| Total Active Tasks | 6 |
