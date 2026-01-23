# Agent Task Registry

> Dashboard for all active and archived tasks.
> Updated: 2026-01-22

---

## Active Tasks

| ID | Title | Status | Confidence | Blocker |
|----|-------|--------|------------|---------|
| TASK-000 | Bootstrap agent coordination system | EXECUTING | 90% | None |
| TASK-001 | Create Python MCP server template | SCOPED | 80% | None |

## Task Registries

| Registry | Domain | Tasks | Ready |
|----------|--------|-------|-------|
| [LEARNING_SYSTEM_TASK_REGISTRY.md](LEARNING_SYSTEM_TASK_REGISTRY.md) | Learning Repository Architecture | 10 | 5 |
| [MCP Factory Registry](../../context-management/tools/mcp/mcp_factory/TASK_CONFIDENCE_REGISTRY.md) | MCP Server Development | 10 | 4 |

---

## Quick Stats

```
Total Tasks:     2
  - Discovery:   0
  - Scoped:      1
  - Planned:     0
  - Executing:   1
  - Validating:  0
  - Complete:    0
  - Archived:    0

Active Runs:     0
Completed Runs:  1
```

---

## Recent Runs

| Run ID | Task | Agent | Status | Started |
|--------|------|-------|--------|---------|
| RUN-20260122-194058-claude | TASK-000 | claude | DONE | 2026-01-22T19:40 |

---

## Execution Order (Confidence-Ranked)

Tasks are prioritized by overall confidence (min of 4D scores):

```
READY NOW (>= 75%):
  1. TASK-000: Bootstrap agent coordination system  [90%] ← IN PROGRESS
  2. TASK-001: Create Python MCP server template    [80%]

NEXT SESSION (50-74%):
  (none)

BLOCKED (< 50% or dependencies):
  (none)
```

---

## How to Use This Registry

### Adding a Task

1. Create `registry/active/TASK-XXX.yaml` following `schema/task.schema.yaml`
2. Update this INDEX.md with task summary
3. Score 4D confidence (Factual, Alignment, Current, Onwards)
4. Set status to `DISCOVERY` or `SCOPED`

### Starting Work

1. Pick highest-confidence ready task
2. Create `runs/RUN-YYYYMMDD-HHMMSS-{agent}.yaml`
3. Update task status to `EXECUTING`
4. Log progress in RUN record

### Completing Work

1. Update RUN with handoff info
2. Update task with output artifacts
3. Move task to `COMPLETE` or `ARCHIVED`
4. Update this INDEX.md

---

## Archive

Completed and abandoned tasks move to `registry/archive/`.

| ID | Title | Final Status | Completed |
|----|-------|--------------|-----------|
| _No archived tasks yet_ | | | |

---

## Version

| Field | Value |
|-------|-------|
| Registry Version | 1.0.0 |
| Created | 2026-01-22 |
