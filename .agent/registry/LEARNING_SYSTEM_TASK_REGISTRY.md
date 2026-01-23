# Learning System - Task Confidence Registry

> Confidence-scored task evaluation for the Learning Repository architecture.
> **Version:** 3.2.0 | **Reassessed:** 2026-01-23

## Status Legend

| Emoji | State | Meaning |
|-------|-------|---------|
| ☑️  | COMPLETE | Done |
| 🟢 | READY | Meets threshold, execute anytime |
| 🟡 | NEEDS BOOST | Below threshold, needs confidence |
| 🚧 | BLOCKED | Waiting on dependency |
| 💤 | DEFERRED | Postponed indefinitely |
| 🛠️  | IN PROGRESS | Currently being worked |
| ⛔ | REJECTED | Won't do |

---

## Scoring Matrix

| Dimension | Question | Weight |
|-----------|----------|--------|
| **Factual** | Is my understanding of current state correct? | High |
| **Alignment** | Does this serve the project's mission? | High |
| **Current** | Does this fit codebase as it exists? | Medium |
| **Onwards** | Does this fit where we're heading? | Medium |

**Verdicts:** ACCEPT (>75%) | DEFER (50-75%) | REJECT (<50%)

## Risk-Adjusted Execution Thresholds

| Grade | Threshold | Task Type | Example |
|-------|-----------|-----------|---------|
| **A** | 85% | Standard tasks | Documentation, config changes |
| **A+** | 95% | Multi-file changes, new systems | New protocols, migrations |
| **A++** | 99% | High-risk refactors, deletions | File deletions, schema changes |

---

## Quick View

```
☑️  TASK-100  Delete index.html                   [b6063fa]
☑️  TASK-115  Atomic task reservation             [8df0de9]
☑️  TASK-116  Reconcile registries                [54a198e]
☑️  TASK-117  State machine enforcement           [54a198e]
☑️  TASK-110  Document Socratic Research Loop     [pending commit]
☑️  TASK-101  SYSTEM_KERNEL.md                    [dc3ae00]
☑️  MCP-001   BEST_PRACTICES.md
☑️  MCP-003   Dual-format utility
☑️  MCP-004   SHA-256 checksums
☑️  TASK-111  Update analysis_sets.yaml           [93d4de9]
☑️  TASK-118  Make registry optional in mirror    [6090fce]
☑️  TASK-119  Reduce token budgets to ≤200k       [6090fce]
☑️  TASK-114  Add Context Engineering docs        [pending commit]
☑️  TASK-106  Dataset optimization guide          [pending commit]
☑️  TASK-113  Positional strategy                 [5c7b35b]
☑️  TASK-103  analyze.py auto-save                 [d16826d]
🟡 TASK-120  Autonomous Confidence Booster        [70%] ← NEW
🟡 TASK-121  Task Opportunity Explorer            [65%] ← NEW
💤 TASK-104  Pre-commit hook                      [nice-to-have]
💤 TASK-102  --research-loop                      [complex scope]
💤 TASK-105  Live-reload for viz
💤 TASK-108  Knowledge embodiment workflow
💤 TASK-109  Deploy HSL to Cloud Run
⛔ MCP-007   Node.js template
⛔ TASK-112  Re-evaluate token budgets            [subsumed by TASK-119]
```

---

## ☑️  COMPLETED TASKS

### ☑️  TASK-100: Delete stale index.html (Pit of Success)
**Commit:** b6063fa

---

### ☑️  TASK-115: Implement atomic task reservation protocol
**Commit:** 8df0de9

**Deliverables:**
- `.agent/registry/claimed/` directory + README.md
- `.agent/tools/claim_task.sh` (atomic `mv`)
- `.agent/tools/release_task.sh` (COMPLETE/FAILED/RETRY)
- `.agent/tools/check_stale.sh` (>30 min detection)

---

### ☑️  TASK-101: Create SYSTEM_KERNEL.md
**Commit:** dc3ae00 → Delivered as `.agent/KERNEL.md`

---

### ☑️  MCP-001: Write BEST_PRACTICES.md
**Source:** MCP Factory registry

---

### ☑️  MCP-003: Abstract dual-format save utility
**Deliverable:** `context-management/tools/utils/output_formatters.py`

---

### ☑️  MCP-004: Add SHA-256 checksums to auto-save
**Included in:** output_formatters.py

---

### ☑️  TASK-116: Reconcile MCP Factory registry with .agent/
**Commit:** 54a198e

**Deliverables:**
- MCP Factory registry marked as SECONDARY source
- SSOT pointer to `.agent/registry/LEARNING_SYSTEM_TASK_REGISTRY.md`
- TASK-006 marked as MIGRATED → .agent/TASK-001

---

### ☑️  TASK-117: Enforce explicit task state machine
**Commit:** 54a198e

**Deliverables:**
- `claim_task.sh`: Strict gate - rejects non-SCOPED/PLANNED tasks
- `release_task.sh`: Warn mode - logs fast completions and state skips
- `KERNEL.md`: State machine diagram and tool usage docs

---

### ☑️  TASK-110: Document Socratic Research Loop
**Commit:** pending

**Deliverables:**
- Recipe 6 added to `context-management/docs/WORKFLOW_FACTORY.md`
- Documents: Gemini → Perplexity → File reads → Synthesis → Execute
- Includes execution thresholds (A/A+/A++) and example session

---

### ☑️  TASK-118: Make registry generation optional in mirror
**Commit:** pending

**Problem:** Cloud mirror auto-generates registry after every sync, causing
"always dirty" git status for registry files even when no real changes occurred.

**Deliverables:**
- Added `--no-registry` flag to `archive.py mirror` command
- Registry generation now conditional (skipped if flag present)
- File: `context-management/tools/archive/archive.py`

---

### ☑️  TASK-119: Reduce token budgets to ≤200k
**Commit:** pending

**Problem:** Perplexity research + ChatGPT Deep Research confirmed 200k is the
effective usable limit. Sets above this suffer lost-in-middle effects.

**Deliverables:**
- Reduced `archeology` from 300k → 200k
- Reduced `architecture_review` from 250k → 200k
- Reduced `implementation_review` from 350k → 200k
- Reduced `research_full` from 350k → 200k
- File: `context-management/config/analysis_sets.yaml`

**Note:** Subsumes TASK-112 (Re-evaluate token budgets)

---

### ☑️  TASK-114: Add Context Engineering docs to KERNEL.md
**Commit:** pending

**Deliverables:**
- Added "Context Engineering" section to `.agent/KERNEL.md`
- Documents: Lost-in-middle effect, U-shaped attention diagram
- Includes: Token budget tiers (Guru/Architect/Archeologist/Perilous)
- Practical rules: ROI thinking, edge positioning, critical_files usage

---

### ☑️  TASK-106: Dataset optimization guide
**Commit:** pending

**Deliverables:**
- Added "Dataset Optimization Strategy" section to WORKFLOW_FACTORY.md
- Documents: RAG vs Long Context decision matrix
- Includes: Purity principles, token budget decision tree
- Anti-patterns table with solutions

---

### ☑️  TASK-113: Implement positional strategy in analyze.py
**Status:** Already implemented (discovered during execution)

**Implementation found at:**
- `analyze.py:875-934` - `build_context_from_files()` function
- Supports both `sandwich` and `front-load` strategies
- Prints strategy info to stderr when active
- Called correctly from main() at lines 1905-1909

---

## 🟡 NEEDS CONFIDENCE BOOST

### 🟡 TASK-111: Update analysis_sets.yaml schema
**Risk:** A | **Threshold:** 85% | **Score:** 85%

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Perplexity research validated |
| Alignment | 90% | Improves AI tool effectiveness |
| Current | 85% | Extends existing YAML |
| Onwards | 95% | Foundation for context assembly |

**Implementation:**
1. Add `critical_files: list[str]` field
2. Add `positional_strategy: enum[sandwich, front-load]` field

**Unblocks:** TASK-113

---

### 🟢 TASK-112: Re-evaluate all set token budgets
**Risk:** A | **Threshold:** 85% | **Score:** 85%

**Implementation:**
- Tier 1 (Guru, 16k): viz_core, constraints, role_registry
- Tier 2 (Architect, 64k): pipeline, classifiers
- Tier 3 (Archeologist, 500k): research_full
- Tier 4 (Perilous, >500k): Flag with warnings

---

### 🟢 TASK-114: Add Context Engineering to agent docs
**Risk:** A | **Threshold:** 85% | **Score:** 85%

**Implementation:**
1. Add "Context Engineering" section to `.agent/KERNEL.md`
2. Include: lost-in-middle, sandwich method, U-shaped attention
3. Reference: `20260122_225007_*.md`

---

### 🟢 TASK-106: Document dataset optimization strategy
**Risk:** A | **Threshold:** 85% | **Score:** 85%

**Implementation:**
1. Add to WORKFLOW_FACTORY.md or create DATASET_DESIGN_GUIDE.md
2. Document: RAG for search, Long-context for reasoning

---

## 🟡 NEEDS CONFIDENCE BOOST

### 🟡 TASK-116: Reconcile task registries (SSOT)
**Risk:** A+ | **Threshold:** 95% | **Current:** 90% | **Gap:** +5%

**Registries Found:**
1. `.agent/registry/LEARNING_SYSTEM_TASK_REGISTRY.md`
2. `context-management/tools/mcp/mcp_factory/TASK_CONFIDENCE_REGISTRY.md`

**To Boost:** Verify migration plan won't lose data

---

### ☑️ TASK-103: Add auto-save to analyze.py responses
**Commit:** d16826d

**Deliverables:**
- Import DualFormatSaver with graceful fallback (try/except)
- Auto-save to `standard-model-of-code/docs/research/gemini/`
- All modes covered: one-shot, trace, insights, role_validation, plan_validation
- Format: `{timestamp}_{query_slug}.{md,json}`

**Implementation:**
- `analyze.py:155-170` - DualFormatSaver import + config
- `analyze.py:171-205` - auto_save_gemini_response() helper
- Auto-save calls in all response modes

---

## 🟡 NEEDS CONFIDENCE BOOST (New Tasks)

### 🟡 TASK-120: Autonomous Task Confidence Booster
**Risk:** A+ | **Threshold:** 95% | **Score:** 70%

**Vision:** Background daemon that automatically boosts task confidence by generating
and executing Socratic Research Loop queries until tasks meet execution thresholds.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 75% | Pattern exists (Perplexity MCP, analyze.py), needs architecture |
| Alignment | 95% | Core mission: self-improving task system |
| Current | 60% | Requires new infrastructure (daemon, query generator) |
| Onwards | 90% | Enables autonomous agent improvement |

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│               AUTONOMOUS CONFIDENCE BOOSTER                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. SCANNER                    2. QUERY GENERATOR                │
│     Read registry              Generate Gemini/Perplexity        │
│     Find tasks <85%            queries for each dimension        │
│                                                                  │
│  3. BATCH OPTIMIZER            4. EXECUTOR                       │
│     Group by semantic          Run queries in parallel           │
│     similarity                 Respect token limits              │
│     Track token budgets                                          │
│                                                                  │
│  5. CONFIDENCE UPDATER         6. REPORTER                       │
│     Parse AI responses         Log progress                      │
│     Update 4D scores           Notify when tasks READY           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Components:**
1. `confidence_scanner.py` - Reads registry, identifies <threshold tasks
2. `query_generator.py` - Generates targeted confidence-boosting queries
3. `batch_optimizer.py` - Groups by semantic similarity, respects token limits
4. `confidence_updater.py` - Parses AI responses, updates 4D scores
5. `boost_daemon.py` - Background process orchestrator

**Dependencies:**
- analyze.py (Gemini queries)
- Perplexity MCP (external validation)
- DualFormatSaver (auto-save responses)
- claim_task.sh (prevent conflicts with manual work)

**To Boost:** Design document, API specification, daemon architecture

---

### 🟡 TASK-121: Task Opportunity Explorer
**Risk:** A+ | **Threshold:** 95% | **Score:** 65%

**Vision:** Background process that discovers new task opportunities by analyzing
codebase changes, research outputs, and conversation patterns. Tasks are auto-generated
and wait in a **Discovery Inbox** for human/terminal agent approval before promotion
to the main registry.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 60% | Concept clear, no existing implementation |
| Alignment | 95% | Core mission: self-discovering improvement opportunities |
| Current | 55% | Requires new infrastructure |
| Onwards | 95% | Foundation for fully autonomous agents |

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│               TASK OPPORTUNITY EXPLORER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SOURCES                       ANALYZERS                         │
│  ┌─────────────┐              ┌─────────────────────────┐        │
│  │ Git commits │───────────►  │ Commit Message Analyzer │        │
│  │ (new code)  │              │ - Detect TODOs, FIXMEs  │        │
│  └─────────────┘              │ - Find incomplete work  │        │
│                               └─────────────────────────┘        │
│  ┌─────────────┐              ┌─────────────────────────┐        │
│  │ Perplexity  │───────────►  │ Research Gap Detector   │        │
│  │ research/   │              │ - Unanswered questions  │        │
│  └─────────────┘              │ - New best practices    │        │
│                               └─────────────────────────┘        │
│  ┌─────────────┐              ┌─────────────────────────┐        │
│  │ Socratic    │───────────►  │ Drift Detector          │        │
│  │ audits      │              │ - Spec violations       │        │
│  └─────────────┘              │ - New debt discovered   │        │
│                               └─────────────────────────┘        │
│  ┌─────────────┐              ┌─────────────────────────┐        │
│  │ Conversation│───────────►  │ Idea Extractor          │        │
│  │ transcripts │              │ - User requests         │        │
│  └─────────────┘              │ - Unfinished threads    │        │
│                               └─────────────────────────┘        │
│                                          │                       │
│                                          ▼                       │
│                          ┌───────────────────────────┐           │
│                          │   DISCOVERY INBOX         │           │
│                          │   .agent/registry/inbox/  │           │
│                          │                           │           │
│                          │   DRAFT-001.yaml          │           │
│                          │   DRAFT-002.yaml          │           │
│                          │   ...                     │           │
│                          └───────────────────────────┘           │
│                                          │                       │
│                                          ▼                       │
│                          ┌───────────────────────────┐           │
│                          │   APPROVAL PIPELINE       │           │
│                          │                           │           │
│                          │   Terminal Agent reviews: │           │
│                          │   - Dedup vs existing     │           │
│                          │   - Validate 4D scores    │           │
│                          │   - Check alignment       │           │
│                          │                           │           │
│                          │   Actions:                │           │
│                          │   [ACCEPT] → main registry│           │
│                          │   [REJECT] → archive      │           │
│                          │   [MERGE]  → combine      │           │
│                          └───────────────────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Components:**
1. `opportunity_scanner.py` - Monitors sources for signals
2. `commit_analyzer.py` - Extracts TODOs, incomplete patterns from commits
3. `research_gap_detector.py` - Finds unanswered questions in research/
4. `drift_detector.py` - Parses Socratic audits for violations
5. `idea_extractor.py` - Mines conversation logs for user requests
6. `task_proposer.py` - Creates DRAFT entries in inbox with 4D scores
7. `approval_agent.py` - Terminal agent for review/accept/reject

**Directory Structure:**
```
.agent/registry/
├── active/           # Tasks being worked on
├── inbox/            # Discovery Inbox (DRAFT-XXX.yaml)
├── claimed/          # Claimed tasks (locks)
└── archive/          # Rejected/completed drafts
```

**Dependencies:**
- Git hooks (post-commit trigger)
- HSL daemon (socratic audits)
- Perplexity research directory
- Claude conversation logs
- Terminal agent (human or automated reviewer)

**To Boost:** Define signals taxonomy, scoring heuristics, approval criteria

---

## 🚧 BLOCKED

(No blocked tasks - TASK-113 and TASK-117 were completed in earlier sessions)

---

## 💤 DEFERRED

### 💤 TASK-105: Live-reload for viz development
**Score:** 65% | **Reason:** Nice-to-have

### 💤 TASK-108: Knowledge embodiment workflow
**Score:** 60% | **Reason:** Needs research

### 💤 TASK-109: Deploy HSL to Cloud Run
**Score:** 60% | **Reason:** After local stability

---

## ⛔ REJECTED

### ⛔ MCP-007: Node.js template
**Reason:** Python-first project

---

## Execution Priority

```
NEEDS BOOST (research to reach 95% threshold):
1. 🟡 TASK-120  Autonomous Confidence Booster  [70%] +25% needed
2. 🟡 TASK-121  Task Opportunity Explorer      [65%] +30% needed

DEFERRED:
- 💤 TASK-104  Pre-commit hook     (nice-to-have, not core mission)
- 💤 TASK-102  --research-loop     (complex scope, needs design)
- 💤 TASK-105  Live-reload for viz
- 💤 TASK-108  Knowledge embodiment workflow
- 💤 TASK-109  Deploy HSL to Cloud Run

POTENTIAL NEW TASKS:
- Build subgraph retrieval API (GraphRAG runtime)
- Automate RAG → LC hybrid pipeline
- Community auto-summarization
```

---

## Registry Summary

| Status | Count | Tasks |
|--------|-------|-------|
| ☑️  COMPLETE | 16 | 100, 103, 115, 116, 117, 110, 101, 111, 118, 119, 114, 106, 113, MCP-001, MCP-003, MCP-004 |
| 🟡 NEEDS BOOST | 2 | 120 (Confidence Booster), 121 (Opportunity Explorer) |
| 🟢 READY | 0 | (none at threshold yet) |
| 💤 DEFERRED | 5 | 104, 102, 105, 108, 109 |
| ⛔ REJECTED | 2 | MCP-007, 112 (subsumed) |
| **TOTAL** | **25** | |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-22 | Initial creation |
| 2.0.0 | 2026-01-22 | Merged AGENT-SYS tasks, added risk thresholds |
| 3.0.0 | 2026-01-23 | Reassessed: 6 tasks complete, updated blockers |
| 3.1.0 | 2026-01-23 | Added emoji status legend, Quick View section |
| 3.2.0 | 2026-01-23 | Session complete: +3 tasks (116, 117, 110), Socratic Loop documented |
| 3.3.0 | 2026-01-23 | Context purity: +2 tasks (118, 119), token budgets reduced to ≤200k |
| 3.4.0 | 2026-01-23 | All ready tasks complete: +3 (114, 106, 113), RAG/LC thresholds documented |
| 3.5.0 | 2026-01-23 | Boost analysis: TASK-103 boosted to 85%, TASK-104/102 deferred |
| 3.6.0 | 2026-01-23 | TASK-103 complete: analyze.py auto-save with DualFormatSaver |
| 3.7.0 | 2026-01-23 | New tasks: TASK-120 (Autonomous Confidence Booster), TASK-121 (Task Opportunity Explorer) |
