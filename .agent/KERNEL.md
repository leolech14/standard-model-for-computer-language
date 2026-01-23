# Agent Kernel

> Bootstrap context for ALL AI agents. Read this FIRST before any work.

---

## Boot Protocol

```
1. READ this file (KERNEL.md)
2. READ manifest.yaml for discovery pointers
3. CHECK registry/INDEX.md for active tasks
4. FIND or CREATE a RUN record in runs/
5. BEGIN work, logging steps to your RUN record
```

---

## Project Identity

| Fact | Value |
|------|-------|
| **Project** | PROJECT_elements |
| **Core Product** | Standard Model of Code + Collider |
| **Mission** | Find the basic constituents of computer programs |
| **Owner** | Leonardo Lech (leonardo.lech@gmail.com) |

---

## Architecture: Concepts / Objects Duality

This project uses a fractal duality pattern:

| World | Contains | Example |
|-------|----------|---------|
| **Concepts** | Types, Schemas, Specs, Definitions | `task.schema.yaml` |
| **Objects** | Instances, Records, Data, Implementations | `TASK-001.yaml` |

The pattern applies at every level:

```
PROJECT_elements/
├── standard-model-of-code/   # Body (Collider engine)
│   ├── docs/specs/           # Concepts (MODEL.md, schemas)
│   └── src/                  # Objects (implementation)
│
├── context-management/       # Brain (AI tools)
│   ├── docs/                 # Concepts (guides, specs)
│   └── tools/                # Objects (scripts, servers)
│
└── .agent/                   # Agent Coordination
    ├── schema/               # Concepts (task.schema, run.schema)
    └── registry/, runs/      # Objects (TASK-XXX, RUN-*)
```

---

## Task / Run Separation

**TASK** = What should be true in the repository (strategic, persistent)
- Lives in `registry/active/TASK-XXX.yaml`
- Survives across sessions and agents
- Has 4D confidence score

**RUN** = One agent's attempt to advance a task (tactical, per-session)
- Lives in `runs/RUN-{timestamp}-{agent}.yaml`
- Documents what happened in one session
- Enables handoff between agents

---

## Task State Machine

Tasks follow a defined lifecycle. The tools enforce this (strict on claim, warn on release).

```
DISCOVERY → SCOPED → PLANNED → EXECUTING → VALIDATING → COMPLETE → ARCHIVED
                ↑                    ↓
                └──── RETRY ─────────┘
```

| State | Description | Can Claim? |
|-------|-------------|------------|
| DISCOVERY | Opportunity identified, not scoped | No |
| SCOPED | Requirements clear, ready to plan | **Yes** |
| PLANNED | Implementation approach defined | **Yes** |
| EXECUTING | Work in progress (has active RUN) | No |
| VALIDATING | Work done, awaiting verification | No |
| COMPLETE | Verified and merged | No |
| ARCHIVED | Closed (success or abandoned) | No |

### Using the Tools

```bash
# Claim a task (strict: only SCOPED/PLANNED)
.agent/tools/claim_task.sh TASK-001 my-agent

# Release when done (warn mode: logs unusual patterns)
.agent/tools/release_task.sh TASK-001 COMPLETE

# Check for stale claims (>30 min)
.agent/tools/check_stale.sh
```

---

## 4D Confidence Model

Every task is scored on four dimensions:

| Dimension | Question |
|-----------|----------|
| **Factual** | Is my understanding of current state correct? |
| **Alignment** | Does this serve the project's mission? |
| **Current** | Does this fit codebase as it exists? |
| **Onwards** | Does this fit where we're heading? |

**Overall** = `min(factual, alignment, current, onwards)` (bottleneck thinking)

| Verdict | Threshold |
|---------|-----------|
| ACCEPT | >= 75% |
| DEFER | 50-74% |
| REJECT | < 50% |

---

## Context Engineering

When assembling context for AI analysis, follow these research-backed principles:

### The Lost-in-the-Middle Effect

LLMs have U-shaped attention - they attend best to **beginning** and **end** of context.

```
Attention
    ^
    |  *                           *
    |   *                         *
    |    *                       *
    |     *       Lost         *
    |      *    in the       *
    |       *   Middle     *
    |        * * * * * * *
    +---------------------------------> Position
       Start              End
```

**Mitigation: Sandwich Method**
```
[Critical instructions]     ← Beginning (high attention)
[Supporting context]        ← Middle (lower attention)
[Key facts + instructions]  ← End (high attention)
```

### Token Budget Tiers

| Tier | Budget | Use Case | Risk |
|------|--------|----------|------|
| Guru | <50k | Focused analysis | Low |
| Architect | 50k-150k | Multi-file reasoning | Medium |
| Archeologist | 150k-200k | Deep exploration | High |
| Perilous | >200k | Avoid | Very High |

**Hard cap: 200k tokens.** Beyond this, lost-in-middle effects dominate.

### Token Quality > Quantity

**High-value tokens:**
- Directly relevant facts
- Canonical excerpts (not paraphrases)
- Disambiguating identifiers
- Clean structure (headings, bullets)

**Negative-value tokens (remove these):**
- Irrelevant background
- Redundant paraphrases
- Contradictory instructions
- Confusable near-misses
- Unfiltered logs

### Practical Rules

1. **Treat tokens as budget with ROI** - If it doesn't change the decision, remove it
2. **Position critical content at edges** - Start and end of context
3. **Use `critical_files` + `positional_strategy`** - In `analysis_sets.yaml`
4. **Prefer RAG for search, focused sets for reasoning**

**Reference:** `docs/research/perplexity/docs/20260123_context_window_tradeoffs_chatgpt.md`

---

## Agent Responsibilities

### Starting a Session

1. Check `registry/INDEX.md` for highest-priority incomplete task
2. Create a RUN record: `runs/RUN-YYYYMMDD-HHMMSS-{agent}.yaml`
3. Mark RUN status: `STARTED`
4. Read task context and any previous RUNs for that task

### During Work

1. Update RUN status: `IN_PROGRESS`
2. Log each step in `progress.step_log`
3. Create/modify files as needed
4. Commit atomically when reaching stable states

### Ending a Session

1. Update RUN with:
   - `handoff.summary`: What was accomplished
   - `handoff.next_steps`: What the next agent should do
   - `handoff.artifacts`: Files created/modified
2. Set RUN status: `DONE`, `HANDOFF_READY`, or `ABANDONED`
3. Update task confidence if changed
4. Commit all changes

---

## Non-Negotiables

1. **Git is truth** - All state lives in files, commits are transactions
2. **Never skip the RUN record** - Even quick fixes get documented
3. **Log before doing** - Announce intent, then act
4. **Handoff explicitly** - Next agent should understand state without reading code
5. **Conservative confidence** - When unsure, score lower

---

## Key Paths

| Need | Path |
|------|------|
| Task schemas | `.agent/schema/task.schema.yaml` |
| Run schemas | `.agent/schema/run.schema.yaml` |
| Active tasks | `.agent/registry/active/` |
| Task dashboard | `.agent/registry/INDEX.md` |
| Run history | `.agent/runs/` |
| Project config | `CLAUDE.md`, `context-management/docs/` |
| Collider code | `standard-model-of-code/src/` |
| AI tools | `context-management/tools/` |

---

## Quick Commands

```bash
# Analyze codebase with Collider
./collider full <path> --output <dir>

# Query with Gemini
python context-management/tools/ai/analyze.py "<query>"

# Run tests
cd standard-model-of-code && pytest tests/ -q

# Mirror to GCS
python context-management/tools/archive/archive.py mirror
```

---

## Version

| Field | Value |
|-------|-------|
| Kernel Version | 1.2.0 |
| Created | 2026-01-22 |
| Last Updated | 2026-01-23 |

### Changelog

- **1.2.0** (2026-01-23): Added Context Engineering section (lost-in-middle, token tiers, quality rules)
- **1.1.0** (2026-01-23): Added Task State Machine section, tool usage docs
- **1.0.0** (2026-01-22): Initial kernel with boot protocol, 4D model, TASK/RUN separation
