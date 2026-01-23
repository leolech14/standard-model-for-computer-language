# Learning System - Task Confidence Registry

> Confidence-scored task evaluation for the Learning Repository architecture.
> Generated: 2026-01-22 from research loop session.
> **Consolidated:** Merged AGENT-SYS tasks from multi-agent coordination session.

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

## Confidence Boosting Pipeline

```
1. TASK SEED → Initial 4D score from research/problem
       ↓
2. RISK CLASSIFICATION → Assign A/A+/A++ threshold
       ↓
3. CONFIDENCE BOOSTING (if below threshold):
   ├─ Gemini (analyze.py): Codebase-aware validation
   ├─ Perplexity (MCP): Technical/external verification
   ├─ File reads: Verify actual state vs assumptions
   └─ Synthesis: Revised 4D scores with rationale
       ↓
4. EXECUTION GATE
   ├─ Score >= threshold → EXECUTE
   └─ Score < threshold → BOOST again or DEFER
```

---

## Phase 0: Agent System Hardening (From Multi-Agent Coordination Research)

### TASK-100: Delete stale index.html (Pit of Success)

**Status:** ✅ **COMPLETE** (commit b6063fa)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 100% | File confirmed deleted, git status verified |
| Alignment | 100% | Eliminates agent confusion trap |
| Current | 100% | Done - single source of truth now |
| Onwards | 100% | Prevents future drift |

**Risk Level:** A++ (deletion) | **Threshold:** 99% | **Final:** 100%

---

### TASK-115: Implement atomic task reservation protocol

**Proposal:** Use filesystem `mv` for atomic task claiming to prevent race conditions.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 100% | Perplexity confirmed: `mv` is atomic on APFS, exactly one process wins |
| Alignment | 95% | Essential for multi-agent coordination |
| Current | 95% | Simple: add `claimed/` dir + mv operation |
| Onwards | 100% | Foundation for scaling to multiple agents |

**Risk Level:** A+ (new protocol) | **Threshold:** 95% | **Final:** 95% ✅ MEETS

**Implementation:**
```bash
# Atomic claim via filesystem move (POSIX-compliant)
mv .agent/registry/active/TASK-XXX.yaml .agent/registry/claimed/claude_TASK-XXX.yaml
```
1. Create `.agent/registry/claimed/` directory
2. Agent claims task by moving file (atomic on APFS)
3. Add timestamp to claimed filename for stale detection
4. Implement timeout-based expiry (30 min default)

**Source:** Perplexity research `20260122_220947_*.md`

---

### TASK-116: Reconcile task registries (SSOT)

**Proposal:** Migrate MCP Factory registry tasks to `.agent/` system, establish single source of truth.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Both registries visible, format understood |
| Alignment | 100% | SSOT is fundamental principle |
| Current | 90% | Clear migration path: MD → YAML |
| Onwards | 100% | Consolidates all task management |

**Risk Level:** A+ (migration) | **Threshold:** 95% | **Final:** 90% ❌ Needs +5%

**Implementation:**
1. Read `mcp_factory/TASK_CONFIDENCE_REGISTRY.md`
2. Create YAML per task in `.agent/registry/active/`
3. Prefix IDs with `MCP-` if collision
4. Archive original MD with deprecation header

---

### TASK-117: Enforce explicit task state machine

**Proposal:** Add RESERVED state, create validator for transitions.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Schema reviewed, current states clear |
| Alignment | 95% | Robustness aligned with mission |
| Current | 85% | Need to add RESERVED + validator script |
| Onwards | 95% | Essential for automation |

**Risk Level:** A+ (schema change) | **Threshold:** 95% | **Final:** 85% ❌ Needs +10%

**Proposed State Machine:**
```
DISCOVERY → SCOPED → PLANNED → RESERVED → EXECUTING → VALIDATING → COMPLETE
                        ↓                     ↓            ↓
                     ARCHIVED ←───────────────←────────────←
```

**Implementation:**
1. Add `RESERVED` to `task.schema.yaml` status enum
2. Create `.agent/tools/validate_transition.py`
3. Define valid transitions matrix
4. Hook into task update workflow

---

## Phase 1: Foundation (Immediate)

### TASK-101: Create SYSTEM_KERNEL.md

**Proposal:** Create universal instructional context module injected into all AI queries.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Pattern already exists implicitly in prompts.yaml modes and AGENT_BOOT.md |
| Alignment | 95% | Directly serves mission of robust AI-native development |
| Current | 85% | Fits current tooling, requires analyze.py modification |
| Onwards | 95% | Foundation for --research-loop and all future AI integrations |

**Verdict:** ✅ **ACCEPT** (85% confidence)

**Implementation:**
1. Create `context-management/.agent/SYSTEM_KERNEL.md` (~500 tokens)
2. Distill from: AGENT_BOOT.md, THEORY.md, prompts.yaml
3. Add Core Identity, Operational Rules, Architectural Principles, Response Formatting
4. Wire into analyze.py to prepend to all prompts

**Blocks:** TASK-102, TASK-103

---

### TASK-102: Implement --research-loop in analyze.py

**Proposal:** Add closed-loop Perplexity integration that returns scored Task Candidates.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 90% | Clear architecture from Gemini analysis, Perplexity MCP already working |
| Alignment | 95% | Core to knowledge accumulation and autonomous research |
| Current | 75% | Requires new mode in analyze.py, Perplexity API integration |
| Onwards | 95% | Enables self-improving research capability |

**Verdict:** ✅ **ACCEPT** (75% confidence)

**Implementation:**
1. Add `--research-loop` flag to analyze.py
2. Implement `_execute_research_loop(prompt, set)`:
   - Gemini-1: Reformulate query for web search
   - Perplexity: Execute search (use existing MCP or direct API)
   - Gemini-2: Synthesize with dataset context
3. Output: Task Candidate JSON array with 4D scoring
4. Auto-save to `docs/research/discoveries/`

**Blocked By:** TASK-101

---

### TASK-103: Validate analyze.py response storage

**Proposal:** Ensure all analyze.py responses are stored like Perplexity responses.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 70% | Perplexity auto-save confirmed working, analyze.py unclear |
| Alignment | 90% | Critical for knowledge accumulation ("we're paying for it") |
| Current | 80% | Can reuse DualFormatSaver from output_formatters.py |
| Onwards | 90% | Foundation for learning repository |

**Verdict:** ✅ **ACCEPT** (70% confidence)

**Implementation:**
1. Audit current analyze.py output behavior
2. Add DualFormatSaver integration (if missing)
3. Create `docs/research/gemini/` parallel to `docs/research/perplexity/`
4. Store: query, response, set used, token count, cost estimate

**Blocked By:** TASK-101

---

## Phase 2: Visualization Guardrails

### TASK-104: Add pre-commit hook for validate_ui.py

**Proposal:** Automate CIRCUIT validation before commits touching viz files.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | validate_ui.py exists and works, CIRCUIT module tested |
| Alignment | 80% | Prevents UI drift, but not core mission |
| Current | 90% | Simple hook, no new dependencies |
| Onwards | 85% | Enables confident UI changes |

**Verdict:** ✅ **ACCEPT** (80% confidence)

**Implementation:**
1. Create `.git/hooks/pre-commit` (or use husky/pre-commit framework)
2. Detect changes to `src/core/viz/assets/`
3. Run `python tools/validate_ui.py` on staged files
4. Block commit on failure

---

### TASK-105: Implement live-reload for viz development

**Proposal:** Add `./collider dev` mode with file watching and auto-regeneration.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 85% | Clear need from Gemini analysis, architecture understood |
| Alignment | 70% | Developer experience, not core mission |
| Current | 65% | Requires watchdog dependency, CLI changes |
| Onwards | 80% | Speeds up viz iteration significantly |

**Verdict:** ⏸️ **DEFER** (65% confidence) - Nice-to-have after core tasks

**Implementation:**
1. Add `watchdog` to dependencies
2. Create `cli.py dev` subcommand
3. Watch `src/core/viz/assets/` for changes
4. Auto-run visualize_graph_webgl.py on change
5. Optional: WebSocket for browser auto-refresh

---

## Phase 3: Knowledge Crystallization

### TASK-106: Document analysis_sets optimization strategy

**Proposal:** Create guide for RAG vs long-context dataset design.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 90% | WORKFLOW_FACTORY.md has tiered approach, but needs formalization |
| Alignment | 85% | Enables better AI utilization |
| Current | 90% | Pure documentation, no code changes |
| Onwards | 90% | Foundation for dataset purity principles |

**Verdict:** ✅ **ACCEPT** (85% confidence)

**Implementation:**
1. Add section to WORKFLOW_FACTORY.md or create DATASET_DESIGN_GUIDE.md
2. Document: RAG (Tier 2) for search, Long-context (Tier 1) for reasoning
3. Define purity principles: separation of concerns, minimal overlap
4. Include token budget guidance per set type

---

### TASK-107: Implement structured reassessment triggers

**Proposal:** Formalize when knowledge crystallization occurs.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 85% | HSL already has triggers (6hr, file-change, on-demand) |
| Alignment | 90% | Core to learning repository vision |
| Current | 70% | HSL exists but needs extension for knowledge crystallization |
| Onwards | 95% | Enables autonomous knowledge refinement |

**Verdict:** ✅ **ACCEPT** (70% confidence)

**Implementation:**
1. Extend semantic_models.yaml with "knowledge domains" beyond code
2. Add trigger: accumulated research threshold (e.g., 10 new Perplexity saves)
3. Add trigger: weekly synthesis job
4. Output: KNOWLEDGE_DIGEST.md summarizing new learnings

---

### TASK-108: Create knowledge embodiment workflow

**Proposal:** Define process for converting described knowledge into applied knowledge.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 75% | Dual-path concept validated, but process undefined |
| Alignment | 95% | Core to "materialized intelligence" vision |
| Current | 60% | Requires new workflow definition |
| Onwards | 95% | Differentiator for the project |

**Verdict:** ⏸️ **DEFER** (60% confidence) - Needs more research

**Implementation:**
1. Define embodiment criteria: when does a doc become code?
2. Create workflow: Discovery → Validation → Specification → Implementation → Verification
3. Add to WORKFLOW_FACTORY.md as "Recipe 7: Knowledge Embodiment"
4. Include examples from project history (SET_MAPPING as case study)

---

## Phase 4: Context Optimization (From Perplexity Research)

### TASK-111: Update analysis_sets.yaml schema

**Proposal:** Add `critical_files`, `positional_strategy`, and model-specific `max_tokens` fields.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Perplexity research validated with 60 citations, Gemini synthesized specific schema |
| Alignment | 90% | Directly improves AI tool effectiveness |
| Current | 85% | Extends existing YAML, backward compatible |
| Onwards | 95% | Foundation for intelligent context assembly |

**Verdict:** ✅ **ACCEPT** (85% confidence)

**Implementation:**
1. Add `critical_files: list[str]` field
2. Add `positional_strategy: enum[sandwich, front-load]` field
3. Change `max_tokens` to object with model-specific values
4. Update analyze.py to parse new fields

---

### TASK-112: Re-evaluate all set token budgets

**Proposal:** Audit and adjust all analysis sets to tiered system (Guru/Architect/Archeologist/Perilous).

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 90% | Research shows 50-60% effective context, current sets ignore this |
| Alignment | 85% | Prevents failed analyses from oversized context |
| Current | 90% | Pure config change, no code modification |
| Onwards | 90% | Enables predictable analysis quality |

**Verdict:** ✅ **ACCEPT** (85% confidence)

**Implementation:**
1. Tier 1 (Guru, 16k): viz_core, constraints, role_registry
2. Tier 2 (Architect, 64k): pipeline, classifiers, architecture_review
3. Tier 3 (Archeologist, 500k): research_full, revised body subsets
4. Tier 4 (Perilous, >500k): Flag with warnings (archeology, complete)

---

### TASK-113: Implement positional strategy in analyze.py

**Proposal:** Add "sandwich method" context assembly based on set configuration.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 85% | Clear algorithm from Gemini synthesis |
| Alignment | 90% | Directly addresses "lost-in-middle" problem |
| Current | 70% | Requires significant analyze.py modification |
| Onwards | 95% | Makes context engineering automatic |

**Verdict:** ✅ **ACCEPT** (70% confidence)

**Implementation:**
1. Read `critical_files` and `positional_strategy` from set config
2. Implement sandwich assembly: critical → supporting → critical → prompt
3. Add unit tests for context assembly order
4. Log position warnings when critical files missing

**Blocked By:** TASK-111

---

### TASK-114: Add Context Engineering to agent documentation

**Proposal:** Document "sandwich method" and lost-in-middle awareness in AGENT_BOOT.md.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Research validated, synthesis complete |
| Alignment | 85% | Educates agents on context engineering |
| Current | 95% | Pure documentation, no code |
| Onwards | 90% | Prevents future context myopia |

**Verdict:** ✅ **ACCEPT** (85% confidence)

**Implementation:**
1. Add "Context Engineering & Lost in Middle" section to AGENT_BOOT.md
2. Include sandwich method diagram
3. Add "Critical at start, critical at end" mantra
4. Reference Perplexity research document

---

## Phase 5: Infrastructure Hardening

### TASK-109: Deploy HSL to Cloud Run

**Proposal:** Move Holographic-Socratic Layer from local launchd to Cloud Run.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 80% | HOLOGRAPHIC_DEPLOYMENT_MANUAL.md exists with full guide |
| Alignment | 85% | Enables 24/7 monitoring regardless of laptop state |
| Current | 60% | Requires GCP setup, container build |
| Onwards | 90% | Foundation for always-on intelligence |

**Verdict:** ⏸️ **DEFER** (60% confidence) - After local system proven stable

---

### TASK-110: Create WORKFLOW_FACTORY Recipe 6: Socratic Research Loop

**Proposal:** Document the analyze.py → Perplexity → analyze.py closed loop.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 95% | Pattern defined in this session, clear architecture |
| Alignment | 90% | Documents core research workflow |
| Current | 95% | Pure documentation, references existing tools |
| Onwards | 90% | Enables reproducible research |

**Verdict:** ✅ **ACCEPT** (90% confidence)

**Implementation:**
1. Add to WORKFLOW_FACTORY.md
2. Document: Terminal → analyze.py (Gemini) → Perplexity → Gemini synthesis → Task Candidates
3. Include example prompts and expected outputs
4. Reference --research-loop once implemented (TASK-102)

**Blocked By:** None (can document before implementation)

---

## Execution Order (Confidence-Ranked by Risk Level)

```
COMPLETED:
✅ TASK-100: Delete index.html              [100%] A++ DONE (commit b6063fa)

READY NOW (meets threshold):
1. TASK-115: Atomic task reservation        [95%]  A+  ← EXECUTE NEXT
2. TASK-110: Document Socratic Research Loop [90%] A
3. TASK-111: Update analysis_sets.yaml      [85%]  A   CONTEXT OPT
4. TASK-112: Re-evaluate set token budgets  [85%]  A   CONTEXT OPT
5. TASK-114: Add Context Engineering docs   [85%]  A   CONTEXT OPT
6. TASK-101: Create SYSTEM_KERNEL.md        [85%]  A
7. TASK-106: Dataset optimization guide     [85%]  A
8. TASK-104: Pre-commit hook validate_ui    [80%]  A

NEEDS CONFIDENCE BOOST (below threshold):
9.  TASK-116: Reconcile registries          [90%]  A+ needs 95% (+5%)
10. TASK-117: State machine enforcement     [85%]  A+ needs 95% (+10%)
11. TASK-102: Implement --research-loop     [75%]  A  (blocked by 101)
12. TASK-113: Implement positional strategy [70%]  A  (blocked by 111)
13. TASK-103: Validate analyze.py storage   [70%]  A  (blocked by 101)
14. TASK-107: Reassessment triggers         [70%]  A

DEFERRED:
15. TASK-105: Live-reload for viz           [65%]  A  Phase 2
16. TASK-108: Knowledge embodiment workflow [60%]  A  Needs research
17. TASK-109: HSL to Cloud Run              [60%]  A  After stability

BLOCKED/DEPENDENCIES:
- TASK-102 blocked by TASK-101
- TASK-103 blocked by TASK-101
- TASK-113 blocked by TASK-111
```

---

## Registry Status

| Task | Status | Confidence | Risk | Threshold | Blocker |
|------|--------|------------|------|-----------|---------|
| TASK-100 | ✅ COMPLETE | 100% | A++ | 99% | None |
| TASK-101 | READY | 85% | A | 85% | None |
| TASK-102 | BLOCKED | 75% | A | 85% | TASK-101 |
| TASK-103 | BLOCKED | 70% | A | 85% | TASK-101 |
| TASK-104 | READY | 80% | A | 85% | None |
| TASK-105 | DEFERRED | 65% | A | 85% | Phase 2 |
| TASK-106 | READY | 85% | A | 85% | None |
| TASK-107 | READY | 70% | A | 85% | None |
| TASK-108 | DEFERRED | 60% | A | 85% | Needs research |
| TASK-109 | DEFERRED | 60% | A | 85% | HSL stability |
| TASK-110 | READY | 90% | A | 85% | None |
| TASK-111 | READY | 85% | A | 85% | None |
| TASK-112 | READY | 85% | A | 85% | None |
| TASK-113 | BLOCKED | 70% | A | 85% | TASK-111 |
| TASK-114 | READY | 85% | A | 85% | None |
| TASK-115 | **READY** | 95% | A+ | 95% | None |
| TASK-116 | BOOST | 90% | A+ | 95% | +5% needed |
| TASK-117 | BOOST | 85% | A+ | 95% | +10% needed |

---

## Source

This registry was generated from a research loop session on 2026-01-22 involving:
- Gemini analysis via `analyze.py --set brain`
- Perplexity deep research via `mcp__perplexity__perplexity_research`
- Human-agent collaborative refinement

**Key Research Artifacts:**
- `docs/research/perplexity/docs/20260122_225007_deep_research_on_llm_long_context_performance_trad.md`
- 60 citations on long-context performance trade-offs
- Validated: 50-60% effective context, lost-in-middle phenomenon, sandwich method

## Version

| Field | Value |
|-------|-------|
| Registry Version | 2.0.0 |
| Scoring Model | 4D Matrix (Atman) + Risk Thresholds |
| Created | 2026-01-22 |
| Last Updated | 2026-01-22 |
| Total Tasks | 18 |
| Complete | 1 (TASK-100) |
| Ready (meets threshold) | 9 |
| Needs Boost | 2 (TASK-116, 117) |
| Blocked | 4 |
| Deferred | 3 |
