# Agent Task Registry

> Single source of truth for task management in PROJECT_elements.
> **Version:** 2.0.0 | **Updated:** 2026-01-23

---

## Architecture

```
.agent/registry/
├── inbox/           # Discovery Inbox (OPP-XXX.yaml)
├── active/          # Active tasks (TASK-XXX.yaml)
├── archive/         # Completed/rejected tasks
├── claimed/         # Task locks (atomic reservation)
└── README.md        # This file
```

---

## Workflows

### 1. Discovery → Task

```
Opportunity discovered → OPP-XXX in inbox/
                              ↓
                    ./promote_opportunity.py OPP-XXX
                              ↓
                    TASK-XXX in active/
```

### 2. Task Lifecycle

```
DISCOVERY → SCOPED → PLANNED → EXECUTING → VALIDATING → COMPLETE
                                    ↓
                              ./claim_task.sh TASK-XXX
                                    ↓
                              ./release_task.sh TASK-XXX COMPLETE
```

### 3. Sprint Integration

```
Tasks selected for sprint → .agent/sprints/SPRINT-XXX.yaml
                                    ↓
                            ./sprint.py status
```

---

## Directory Details

### inbox/ - Discovery Inbox

**Purpose:** Capture opportunities without immediate commitment.

**File format:** `OPP-XXX.yaml`

**Sources:**
- `BARE` - Background Auto-Refinement Engine
- `RESEARCH` - Perplexity/Gemini research findings
- `HUMAN` - Manual creation
- `WATCHER` - File system watchers
- `EXTERNAL` - External feedback

**Required fields:**
- `id`: OPP-XXX format
- `title`: Brief description
- `source`: One of the above
- `discovered_at`: ISO timestamp
- `description`: Full context

**Optional fields:**
- `urgency`: LOW, MEDIUM, HIGH, CRITICAL
- `suggested_action`: What to do
- `confidence`: 4D scores
- `related_to`: File paths or task IDs

### active/ - Active Tasks

**Purpose:** Tasks being actively worked on.

**File format:** `TASK-XXX.yaml`

**Required fields:**
- `id`: TASK-XXX format
- `title`: Brief description
- `status`: DISCOVERY, SCOPED, PLANNED, EXECUTING, VALIDATING, COMPLETE
- `description`: Full context

**4D Confidence Scoring:**
- `factual`: Is understanding of current state correct?
- `alignment`: Does this serve project mission?
- `current`: Does this fit codebase as it exists?
- `onwards`: Does this fit where we're heading?

**Verdict:** min(factual, alignment, current, onwards)

### archive/ - Completed Tasks

**Purpose:** Historical record of completed or rejected tasks.

Tasks move here when:
- Status becomes COMPLETE
- Status becomes REJECTED
- Superseded by another task

### claimed/ - Task Locks

**Purpose:** Atomic task reservation to prevent conflicts.

**Tools:**
- `./claim_task.sh TASK-XXX` - Claim a task
- `./release_task.sh TASK-XXX [STATUS]` - Release with status

---

## Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `promote_opportunity.py` | Inbox → Active | `./promote_opportunity.py OPP-001` |
| `sprint.py` | Sprint management | `./sprint.py status` |
| `boost_confidence.py` | AI confidence assessment | `./boost_confidence.py TASK-126` |
| `claim_task.sh` | Atomic task lock | `./claim_task.sh TASK-001` |
| `release_task.sh` | Release task lock | `./release_task.sh TASK-001 COMPLETE` |
| `check_stale.sh` | Find stale claims | `./check_stale.sh` |

---

## Numbering

| Range | System | Status |
|-------|--------|--------|
| TASK-000 to TASK-099 | Primary Agent Registry | ACTIVE |
| TASK-100 to TASK-127 | Legacy Learning System | ARCHIVED (GCS) |
| OPP-001 to OPP-999 | Discovery Inbox | ACTIVE |
| SPRINT-001+ | Sprint System | ACTIVE |

---

## Legacy System

The Learning System Task Registry (TASK-100 to TASK-127) was archived on 2026-01-23.

**Location:** `gs://elements-archive-2026/archive/legacy_learning_system/`

**Reason:** Consolidated into this unified system.

**Manifest:** See `ARCHIVE_MANIFEST.md` in GCS archive.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-22 | Initial INDEX.md |
| 2.0.0 | 2026-01-23 | Consolidated from Learning System, full README |
