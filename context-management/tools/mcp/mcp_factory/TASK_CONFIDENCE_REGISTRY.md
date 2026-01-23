# MCP Factory - Task Confidence Registry

> **ARCHIVED:** Superseded by `.agent/registry/` system.
> TASK-006 migrated to `.agent/registry/active/TASK-001.yaml`
> Archived to GCS: `gs://elements-archive-2026/archive/legacy_registries/`
> Date: 2026-01-23

---

> **STATUS: ARCHIVED** - Primary task tracking moved to `.agent/registry/`
> See: `.agent/registry/INDEX.md` for consolidated view.

---

> Confidence-scored task evaluation using 4D matrix (adopted from PROJECT_atman).

## Scoring Matrix

| Dimension | Question | Weight |
|-----------|----------|--------|
| **Factual** | Is my understanding of current state correct? | High |
| **Vision** | Does this serve MCP Factory's mission? | High |
| **Current** | Does this fit codebase as it exists? | Medium |
| **Onwards** | Does this fit where we're heading? | Medium |

**Verdicts:** ACCEPT (>75%) | DEFER (50-75%) | REJECT (<50%) | OPTIONAL (context-dependent)

---

## Phase 1 Tasks

### TASK-001: Write BEST_PRACTICES.md

**Proposal:** Create best practices document from Perplexity research.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Have 849-line research + Gemini analysis |
| Vision | 90% | Core to MCP Factory mission |
| Current | 85% | Clear inputs, no blockers |
| Onwards | 90% | Foundation for templates/validation |

**Verdict:** ✓ **ACCEPT** (90% confidence)

---

### TASK-002: Integrate into HSL (semantic_models.yaml)

**Proposal:** Add MCP Factory to Holographic-Socratic Layer validation.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 70% | Know the pattern, haven't tested |
| Vision | 95% | Directly solves drift problem |
| Current | 60% | Need to verify HSL still works |
| Onwards | 90% | Critical for long-term maintenance |

**Verdict:** ⏸️ **DEFER** (79% confidence) - Test HSL first with small example

---

### TASK-003: Abstract dual-format save utility

**Proposal:** Extract to `tools/utils/output_formatters.py`.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Working code exists in perplexity_mcp_server.py |
| Vision | 80% | Enables reuse across tools |
| Current | 90% | Simple extraction |
| Onwards | 85% | Gemini recommended this |

**Verdict:** ✓ **ACCEPT** (88% confidence)

---

### TASK-004: Add SHA-256 checksums to auto-save

**Proposal:** Add fixity verification per Perplexity evaluation.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 90% | Clear requirement from research |
| Vision | 75% | Nice-to-have, not core mission |
| Current | 95% | Low complexity, hashlib exists |
| Onwards | 80% | Supports archival integrity |

**Verdict:** ✓ **ACCEPT** (85% confidence)

---

### TASK-005: Document CONFIG_PANEL pattern in agent school

**Proposal:** Add to agent_school/WORKFLOWS.md as best practice.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 85% | Pattern proven, just needs docs |
| Vision | 70% | Valuable but not core to MCP Factory |
| Current | 60% | Need to locate agent school files |
| Onwards | 75% | Helps future Brain hemisphere tools |

**Verdict:** ⏸️ **OPTIONAL** (73% confidence) - Do after Phase 1 core tasks

---

## Phase 2 Tasks

### TASK-006: Create Python stdio server template

> **⚠️ MIGRATED** → `.agent/registry/active/TASK-001.yaml`

**Proposal:** Create `templates/python_stdio_server/` scaffold.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 90% | Have reference implementation |
| Vision | 95% | Core mission - make MCP creation trivial |
| Current | 80% | Need BEST_PRACTICES.md first |
| Onwards | 95% | Foundation for scaffold.py |

**Verdict:** ✓ **MIGRATED** - Now tracked as TASK-001 in .agent/

---

### TASK-007: Create Node.js stdio server template

**Proposal:** Create `templates/node_stdio_server/` scaffold.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 30% | No reference implementation |
| Vision | 60% | Expands reach but Python-first project |
| Current | 20% | Would need research |
| Onwards | 50% | Not critical path |

**Verdict:** ✗ **REJECT** (40% confidence) - Defer indefinitely, Python-first

---

### TASK-008: Build tools/scaffold.py

**Proposal:** Interactive generator for new MCP servers.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 60% | Clear concept, UX undefined |
| Vision | 90% | Key to "MCP in <5 min" goal |
| Current | 50% | Need template first |
| Onwards | 85% | Critical for adoption |

**Verdict:** ⏸️ **DEFER** (71% confidence) - After TASK-006 (template)

---

## Phase 3 Tasks

### TASK-009: Build tools/validate.py

**Proposal:** Compliance tester for MCP servers.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 50% | Need BEST_PRACTICES.md to know what to validate |
| Vision | 85% | Critical for quality |
| Current | 40% | Blocked by TASK-001 |
| Onwards | 90% | Automates enforcement |

**Verdict:** ⏸️ **DEFER** (66% confidence) - After TASK-001

---

### TASK-010: Build tools/registry.py

**Proposal:** Track deployed MCP servers.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 40% | Scope unclear - what to track? where? |
| Vision | 70% | Useful for multi-server management |
| Current | 30% | No immediate need (only 1 server) |
| Onwards | 60% | Value increases with scale |

**Verdict:** ⏸️ **DEFER** (50% confidence) - Revisit when we have 3+ servers

---

## Execution Order (Confidence-Ranked)

```
COMPLETED (Phase 1 Core):
1. TASK-001: BEST_PRACTICES.md        [90%] ✓ DONE
2. TASK-003: Dual-format utility      [88%] ✓ DONE (tools/utils/output_formatters.py)
3. TASK-004: SHA-256 checksums        [85%] ✓ DONE (included in utility)

MIGRATED TO .agent/:
4. TASK-006: Python template          → .agent/TASK-001

REMAINING MCP-SPECIFIC:
5. TASK-002: HSL integration          [79%] (test first)
6. TASK-005: Document CONFIG_PANEL    [73%]
7. TASK-008: scaffold.py              [71%] (blocked by TASK-006/migrated)
8. TASK-009: validate.py              [66%]
9. TASK-010: registry.py              [50%] (needs scale)

REJECTED:
- TASK-007: Node.js template          [40%] (not Python-first)
```

---

## Registry Status

| Task | Status | Confidence | Blocker |
|------|--------|------------|---------|
| TASK-001 | **DONE** | 90% | None |
| TASK-002 | DEFERRED | 79% | Need HSL test |
| TASK-003 | **DONE** | 88% | None |
| TASK-004 | **DONE** | 85% | None |
| TASK-005 | OPTIONAL | 73% | Phase 1 first |
| TASK-006 | **MIGRATED** | - | → .agent/TASK-001 |
| TASK-007 | REJECTED | 40% | Not Python-first |
| TASK-008 | BLOCKED | 71% | TASK-006 |
| TASK-009 | READY | 66% | ~~TASK-001~~ |
| TASK-010 | DEFERRED | 50% | Need scale |

---

## Version

| Field | Value |
|-------|-------|
| Registry Version | 1.2.0 |
| Scoring Model | 4D Matrix (Atman) |
| Created | 2026-01-22 |
| Last Updated | 2026-01-23 |
| Completed | TASK-001, TASK-003, TASK-004 |
| Migrated | TASK-006 → .agent/TASK-001 |
| SSOT | `.agent/registry/LEARNING_SYSTEM_TASK_REGISTRY.md` |
