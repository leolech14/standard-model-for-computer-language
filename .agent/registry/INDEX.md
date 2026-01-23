# Agent Task Registry - Dashboard

> Quick view of all tasks and opportunities.
> **Updated:** 2026-01-23

---

## Active Tasks

| ID | Title | Status | Confidence | Sprint |
|----|-------|--------|------------|--------|
| TASK-001 | Bootstrap agent coordination system | COMPLETE | 100% | SPRINT-001 |
| TASK-002 | Deep comparison with LangGraph architecture | DISCOVERY | 70% | - |
| TASK-003 | Fix promote_opportunity.sh multiline bug | COMPLETE | 100% | SPRINT-001 |

---

## Discovery Inbox

| ID | Title | Source | Urgency |
|----|-------|--------|---------|
| OPP-001 | LangGraph architecture comparison | RESEARCH | MEDIUM |
| OPP-002 | Fix multiline YAML parsing in promote script | HUMAN | HIGH |
| OPP-003 | Consolidate research directories | MIGRATION | MEDIUM |
| OPP-004 | Document registry architecture | MIGRATION | LOW |
| OPP-005 | Token System Refactoring (10 tasks, 95%+) | MIGRATION | MEDIUM |
| OPP-006 | Pipeline Refactor (35 tasks, 95%+) | MIGRATION | HIGH |

---

## Quick Stats

```
Inbox:      6 opportunities (2 new from legacy migration)
Active:     3 tasks (2 complete, 1 discovery)
Archived:   1 task
Sprints:    1 active (SPRINT-001)
Legacy:     11 registries consolidated (2 deleted, 5 archived, 2 migrated, 2 kept)
```

---

## Current Sprint: SPRINT-001

**Name:** Agent System Foundation
**Status:** EXECUTING
**Progress:** 7/7 DOD items complete

See: `.agent/sprints/SPRINT-001.yaml`

---

## Execution Priority

```
READY NOW:
  (none - current sprint items complete)

DISCOVERY (needs scoping):
  1. TASK-002  LangGraph comparison       [70%]

INBOX (needs promotion):
  1. OPP-006   Pipeline Refactor          [95%+] ← 35 tasks READY
  2. OPP-005   Token System Refactoring   [95%+] ← 10 tasks READY
  3. OPP-003   Consolidate research dirs  [80%]
  4. OPP-004   Document registry arch     [87%]
  5. OPP-001   LangGraph comparison       [PROMOTED → TASK-002]
  6. OPP-002   Multiline bug fix          [PROMOTED → TASK-003]
```

---

## How to Use

### Promote an opportunity
```bash
.agent/tools/promote_opportunity.py OPP-003
```

### Check sprint status
```bash
.agent/tools/sprint.py status
```

### Boost task confidence
```bash
.agent/tools/boost_confidence.py TASK-002
```

### Run BARE processors
```bash
.agent/tools/bare status
.agent/tools/bare boost TASK-002
```

---

## Archive

| ID | Title | Final Status | Archived |
|----|-------|--------------|----------|
| TASK-000 | Bootstrap agent coordination | COMPLETE | 2026-01-23 |

### Legacy System (Offshore)

The Learning System Registry (TASK-100 to TASK-127) was consolidated and archived to GCS:
- `gs://elements-archive-2026/archive/legacy_learning_system/`

---

## Version

| Field | Value |
|-------|-------|
| Registry Version | 2.0.0 |
| Last Updated | 2026-01-23 |
