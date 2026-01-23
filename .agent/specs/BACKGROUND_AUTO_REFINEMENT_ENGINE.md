# Background Auto-Refinement Engine (BARE)

> A self-improving intelligence layer for continuous repository refinement.

**Status:** PARTIAL IMPLEMENTATION | **Version:** 0.2.0 | **Date:** 2026-01-23

---

## What's Implemented

### 1. Confidence Booster

**Tool:** `.agent/tools/boost_confidence.py`

Automatically boosts task confidence through Gemini-powered Socratic queries.

```bash
# Usage
python .agent/tools/boost_confidence.py TASK-002

# What it does
1. Loads task from registry
2. Identifies lowest-scoring 4D dimension
3. Generates targeted query using Gemini
4. Parses response, extracts evidence
5. Updates 4D scores with citations
```

**Status:** WORKING

### 2. Discovery Inbox

**Location:** `.agent/registry/inbox/`

Opportunities captured from research, audits, and manual discovery.

```yaml
# OPP-XXX.yaml format
id: OPP-007
title: "Opportunity title"
source: RESEARCH|BARE|HUMAN|WATCHER
discovered_at: "2026-01-23T..."
description: |
  Full context
```

**Status:** WORKING (57 opportunities captured)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                BARE (Partial Implementation)            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   IMPLEMENTED                        NOT YET            │
│   ───────────                        ───────            │
│                                                          │
│   ┌──────────────┐                  ┌──────────────┐    │
│   │ Confidence   │                  │ Truth        │    │
│   │ Booster      │ ✓                │ Validator    │    │
│   └──────────────┘                  └──────────────┘    │
│                                                          │
│   ┌──────────────┐                  ┌──────────────┐    │
│   │ Discovery    │                  │ Cross        │    │
│   │ Inbox        │ ✓                │ Validator    │    │
│   └──────────────┘                  └──────────────┘    │
│                                                          │
│                                      ┌──────────────┐    │
│                                      │ Concept      │    │
│                                      │ Mapper       │    │
│                                      └──────────────┘    │
│                                                          │
│   INTELLIGENCE STORE                                     │
│   .agent/intelligence/truths/current_truths.yaml ✓      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Directory Structure (Actual)

```
.agent/
├── intelligence/
│   └── truths/
│       └── current_truths.yaml     # Validated counts (manual)
│
├── registry/
│   ├── active/                     # Current tasks
│   ├── inbox/                      # Discovery Inbox (OPP-XXX) ✓
│   ├── claimed/                    # Task locks
│   └── archive/                    # Completed
│
└── tools/
    ├── boost_confidence.py         # ✓ IMPLEMENTED
    ├── task_registry.py            # ✓ IMPLEMENTED
    ├── sprint.py                   # ✓ IMPLEMENTED
    └── claim_task.sh               # ✓ IMPLEMENTED
```

---

## Roadmap (Not Yet Implemented)

### Phase 1: Foundation
- [ ] TruthValidator - Auto-generate repo_truths.yaml from Collider
- [ ] Post-commit hook integration
- [ ] CLI: `./bare truth`

### Phase 2: Validation
- [ ] CrossValidator - Detect code/docs drift
- [ ] Integrate with Holographic-Socratic Layer
- [ ] Drift reporting

### Phase 3: Intelligence
- [ ] ConceptMapper - Build semantic graph
- [ ] Concept index for fast lookup

### Phase 4: Full Daemon
- [ ] OpportunityExplorer processor
- [ ] Trigger scheduling
- [ ] SelfOptimizer

---

## Integration Points

| System | Status | Integration |
|--------|--------|-------------|
| **Collider** | Planned | TruthValidator uses Collider output |
| **analyze.py** | Working | ConfidenceBooster uses Gemini queries |
| **GCS** | Working | Intelligence mirrors to cloud |
| **Git hooks** | Planned | Post-commit triggers |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial design document |
| 0.2.0 | 2026-01-23 | Trimmed to reflect implementation (CUTTING_PLAN Phase 5) |
