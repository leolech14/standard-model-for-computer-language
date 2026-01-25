# ALL POSSIBILITIES

> **Purpose:** Single source of truth for everything that COULD be done.
> **Last Updated:** 2026-01-24
> **Principle:** The tool exists. These are possibilities, not claims.

---

## HOW TO USE THIS DOCUMENT

```
1. Scan for what resonates
2. Pick ONE thing
3. Do it
4. Update this document
```

---

## CATEGORY 1: IMMEDIATE (Tasks in Progress)

**Source:** Task list (#18-#36)

| ID | What | Status |
|----|------|--------|
| #22 | Fix MISALIGNMENT: UNKNOWN vs CLEAN | READY |
| #23 | Consolidate Pollution vs Pathogen terminology | READY |
| #30 | Normalization + bounds contract | READY |
| #33 | Define Q-metric mathematical formulas | READY |
| #19 | Decompose Q_purity into 3 components | READY |
| #20 | Weighted PurityAlignmentScore | READY |
| #25 | Document two-tier truth model | READY |
| #34 | Pathogen impact inventory | READY |
| #18 | Implement Health Model (H=T+E+Gd+A) | BLOCKED by above |
| #24 | Map pathogens to health components | BLOCKED by #34 |
| #21 | Pathogen override for scoring | BLOCKED by #18 |
| #32 | CLI debug flags | READY |
| #28 | ./collider mcafee command | BLOCKED by #21 |
| #36 | Goodhart's Law protection | READY |
| #35 | Select golden repos | READY |
| #31 | Health regression harness | BLOCKED by #35 |
| #26 | Refactor run_full_analysis (CC=217) | READY |
| #27 | Refactor cli.py main (CC=181) | READY |
| #29 | Refine orphan detection patterns | READY |

---

## CATEGORY 2: OPPORTUNITIES (Inbox)

**Source:** .agent/registry/inbox/OPP-*.yaml

### HIGH IMPACT

| ID | What | Confidence |
|----|------|------------|
| OPP-007 | Context Refinery: RAG + Long Context hybrid | 90% |
| OPP-005 | Perplexity research tool integration | 85% |
| OPP-006 | Socratic audit misalignment fixes | 90% |

### PIPELINE REFACTORING

| ID | What | Confidence |
|----|------|------------|
| OPP-023 | Define BaseStage abstract class | 97% |
| OPP-024 | Extend CodebaseState | 100% |
| OPP-025 | Define PipelineManager | 97% |
| OPP-026 | Create pipeline package structure | 95% |
| OPP-027 | Refactor run_full_analysis() | 95% |

### VISUALIZATION

| ID | What | Confidence |
|----|------|------------|
| OPP-013 | Create index.js | 94% |
| OPP-014 | Update template.html | 99% |
| OPP-008 | Create scales.js | 85% |
| OPP-009 | Create endpoints.js | 90% |
| OPP-010 | Create presets.yaml | 82% |
| OPP-011 | Create bindings.js | 88% |
| OPP-012 | Create blenders.js | 87% |

### AI INTEGRATION

| ID | What | Confidence |
|----|------|------------|
| OPP-058 | Gemini context caching for FLASH_DEEP | 90% |
| OPP-059 | Sprawl consolidation infrastructure | 90% |
| OPP-060 | Autonomous Enrichment Pipeline (AEP) | 80% |

---

## CATEGORY 3: THEORETICAL QUESTIONS

**Source:** THEORY_EXPANSION_2026.md, RESEARCH_DIRECTIONS.md

### OPEN QUESTIONS (Unanswered)

| Question | Domain |
|----------|--------|
| At what level does "meaning" emerge? | PURPOSE |
| Is there a ground level where systems become mere structure? | SCALE |
| Can we compute emergence? Detect when π(n+1) > Σ π(n)? | PURPOSE |
| What flows through the graph? Dependencies, control, data, understanding? | FLOW |
| Is evolvability computable from structure alone? | EVOLUTION |
| Are the 94 atoms complete? Will new paradigms need new atoms? | ATOMS |
| Is the health formula stable across domains? | HEALTH |
| Can we ever fully trace cross-language boundaries? | BOUNDARIES |
| Is anything TRULY dead without runtime evidence? | ORPHANS |
| Is there a universal "framework marker"? | DETECTION |

### RESEARCH DIRECTIONS (Explored but not implemented)

| Direction | Source | Status |
|-----------|--------|--------|
| Normalized Systems Theory | ScienceDirect | RESEARCHED |
| Category Theory for composition | ResearchGate | RESEARCHED |
| Network centrality metrics | arXiv 2501.13520 | PARTIAL (betweenness done) |
| Biological evolvability (Wagner) | Literature | RESEARCHED |
| Constructal Law application | Bejan | CONCEPTUAL |
| Viable System Model mapping | Beer | CONCEPTUAL |

---

## CATEGORY 4: TOOL CAPABILITIES

**Source:** What Collider COULD do but doesn't yet

### NOT IMPLEMENTED

| Capability | Difficulty | Value |
|------------|------------|-------|
| Runtime analysis (not just static) | HIGH | HIGH |
| Git history integration (evolution tracking) | MEDIUM | HIGH |
| Multi-repo analysis | MEDIUM | MEDIUM |
| Real-time watch mode | MEDIUM | MEDIUM |
| IDE plugin (VSCode, JetBrains) | HIGH | HIGH |
| CI/CD integration (GitHub Actions) | LOW | HIGH |
| API mode (not just CLI) | MEDIUM | HIGH |
| Web UI (not just local HTML) | HIGH | MEDIUM |

### PARTIALLY IMPLEMENTED

| Capability | Current State | Gap |
|------------|---------------|-----|
| Health scoring | Formula exists, not unified | #18 |
| Pathogen detection | Survey has PollutionAlert | #34 |
| Disconnection taxonomy | Research done, not in code | #29 |
| Tree-sitter scope analysis | 5-10% utilized | Large |
| Visualization controls | Working but scattered | UPB tasks |

---

## CATEGORY 5: BUSINESS POSSIBILITIES

**Source:** This session, IP strategy discussion

### DECISIONS NEEDED

| Decision | Options | Status |
|----------|---------|--------|
| Business model | SaaS / CLI / Enterprise / API | NOT DECIDED |
| Open source strategy | Open core / Proprietary / Source available | NOT DECIDED |
| Legal entity | LLC / Ltda / None | NOT DONE |
| Trademark | "Collider" / alternatives | NOT SEARCHED |
| Patent track | Yes / No | NOT DECIDED |
| Antivirus product name | Not "McAfee" - alternatives? | NOT DECIDED |

### IP ACTIONS

| Action | Status |
|--------|--------|
| Create legal entity | TODO |
| Assign IP to entity | TODO |
| CLA for contributors | TODO |
| Trademark search | TODO |
| Decide patent strategy | TODO |
| Timestamped milestones (signed tags) | TODO |

---

## CATEGORY 6: TECHNICAL DEBT

**Source:** OPEN_CONCERNS.md

### HIGH PRIORITY BUGS

| ID | Issue | Impact |
|----|-------|--------|
| OC-009 | Scope leakage: Core count 2,809 >> 1,179 | BUG |
| OC-001 | Test failures (tree_sitter missing) | ENVIRONMENT |
| OC-010 | 88 skipped tests unexplained | UNKNOWN RISK |

### MEDIUM PRIORITY

| ID | Issue | Impact |
|----|-------|--------|
| OC-002 | Pipeline snapshot lacks per-stage counts | ENHANCEMENT |
| OC-003 | Pyright type errors in full_analysis.py | TECH_DEBT |
| OC-004 | Physics differs between Atom/File views | INVESTIGATE |
| OC-005 | Node count variance 0.7% between runs | MONITORING |

### GOD FUNCTIONS

| Function | CC | Location |
|----------|-----|----------|
| run_full_analysis | 217 | full_analysis.py |
| main | 181 | cli.py |
| _analyze_single_file | 150+ | (estimated) |

---

## CATEGORY 7: DOCUMENTATION

**Source:** Sprawl analysis this session

### CONSOLIDATION NEEDED

| Topic | Currently | Should Be |
|-------|-----------|-----------|
| Atoms | 3 YAML + scattered docs | ATOMS.md |
| Roles | roles.json + MODEL.md | ROLES.md |
| Health | 4+ spec files | HEALTH.md |
| Pipeline | code + PIPELINE_STAGES.md | PIPELINE.md |
| Pathogens | Not written | PATHOGENS.md |
| Visualization | Multiple specs | VISUALIZATION.md |

### RESEARCH ARCHIVE

| Location | Count | Action |
|----------|-------|--------|
| docs/research/gemini/ | 80+ | Keep, don't consolidate |
| docs/research/perplexity/ | 40+ | Keep, don't consolidate |
| docs/research/*.md | 30+ | Review, archive stale |

---

## CATEGORY 8: SESSION IDEAS (From Today)

**Source:** This conversation

| Idea | What | Priority |
|------|------|----------|
| John McAfee | Code antivirus system | HIGH |
| Perplexity refutation | "Impossible" claim is dust | DONE (documented) |
| Knowledge Tree | IP provenance | DONE |
| Legal docs | ORIGINAL_CLAIMS, PRIOR_ART, DISCLOSURE | DONE |
| Task validation | Gemini audit, 4 new tasks | DONE |
| Theory liberation | Tool is truth, not claims | INSIGHT |
| Possibility consolidation | This document | DONE |

---

## THE TRUTH

```
The tool exists.
The tool works.
Everything else is possibility.

Pick one. Do it. Ship it.
```

---

## VERSION

| Field | Value |
|-------|-------|
| Created | 2026-01-24 |
| Total Possibilities | 100+ |
| Categories | 8 |
| Next Action | Pick one |
