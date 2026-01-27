# Knowledge Patchwork - 2026-01-26

> Safe documentation of what we know now, organized for gap analysis.

**Purpose:** Crystallize current state before planning next actions.
**Method:** Document → Analyze Gaps → Plan → Execute Slowly

---

## Section 1: What Works (Green Zone)

### 1.1 Core Pipeline (Collider)

| Component | Status | Evidence |
|-----------|--------|----------|
| Full Analysis Pipeline | **WORKING** | 28 stages execute, 354 tests pass |
| Atom Classification | **WORKING** | 167 atoms, T0-T2 tiers |
| Graph Generation | **WORKING** | Nodes + edges produced |
| HTML Visualization | **WORKING** | 3D force graph renders |
| Tree-sitter Integration | **WORKING** | Pinned `>=0.20,<0.22` |

**Proof:** `pytest tests/ -q` → 354 passed, 2 skipped

### 1.2 Automation Chain (Agent)

| Component | Status | Evidence |
|-----------|--------|----------|
| Post-Commit Hook | **WORKING** | Triggers on every commit |
| Trigger Engine | **WORKING** | Checks macro patterns |
| Circuit Breakers | **WORKING** | TDJ + trigger_engine healthy |
| Enrichment Pipeline | **WORKING** | Orchestrator ready |
| Batch Promote | **WORKING** | Tool exists, threshold logic ready |
| 24h Stale Trigger | **NEW** | Added 2026-01-26, will run on next commit |

**Proof:** `./autopilot.py status` → All systems green

### 1.3 Documentation Structure (Contextome)

| Layer | Status | Evidence |
|-------|--------|----------|
| CLAUDE.md (root) | **CURRENT** | Updated 2026-01-26 |
| Collider CLAUDE.md | **CURRENT** | Updated 2026-01-26 |
| GLOSSARY.md | **EXISTS** | But fragmented (5 files) |
| OPEN_CONCERNS.md | **AUTHORITATIVE** | Single tracker, updated |
| Agent Specs | **EXISTS** | Multiple specs in .agent/specs/ |

**Known Issue:** 44% of docs are stale (>30 days)

### 1.4 Research Infrastructure

| Component | Status | Evidence |
|-----------|--------|----------|
| Perplexity Integration | **WORKING** | `./pe research` queries work |
| Gemini Integration | **WORKING** | `./pe ask` queries work |
| Research Output Storage | **WORKING** | Stored in docs/research/ |

---

## Section 2: What Exists But Has Issues (Yellow Zone)

### 2.1 Metrics That Need Attention

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Collider Self-Grade | 7.6 (C) | 8.0+ (B) | -0.4 |
| Reachability | 29.3% | >60% | -30.7% |
| Wave-Particle Symmetry | 81 (Silver) | 90 (Gold) | -9 |
| TODO/FIXME Count | 915 | <100 | -815 |
| Stale Docs | 44% | <20% | -24% |

### 2.2 Partial Implementations

| System | What Works | What's Missing |
|--------|------------|----------------|
| Batch Grading | 590 grades collected | Full scans (unified_analysis.json) |
| Purpose Emergence | pi1-pi4 hierarchy coded | Not documented in Contextome |
| Graph Type Inference | 10 rules, working | Tests only added 2026-01-26 |
| BARE | Enrichment pipeline | L1-L3 layers (clusters, distill, synth) |
| Decision Deck | Card schema exists | Only 1 card (CARD-ANA-001) |

### 2.3 Known Bugs / Tech Debt

| ID | Issue | Impact | Status |
|----|-------|--------|--------|
| OC-002 | Pipeline lacks per-stage node counts | Navigator shows timing only | ENHANCEMENT |
| OC-003 | Pyright type errors in full_analysis.py | ~10 issues | TECH_DEBT |
| OC-004 | Physics differs Atom/File views | UX inconsistency | INVESTIGATE |

---

## Section 3: What's Missing (Red Zone / Gaps)

### 3.1 Documentation Gaps

| Gap | What's Needed | Why Important |
|-----|---------------|---------------|
| **PURPOSE_EMERGENCE.md** | Created 2026-01-26 but needs review | Core theoretical insight |
| **BARE roadmap** | Created 2026-01-26, needs validation | Automation future |
| **Unified Glossary** | 5 files → 1 authoritative | Terminology consistency |
| **Theory Amendment** | A1:Tools, A2:Dark Matter, A3:Confidence | Theory evolution |

### 3.2 Test Coverage Gaps

| Module | Test Status | Priority |
|--------|-------------|----------|
| `graph_type_inference.py` | **ADDED 2026-01-26** (29 tests) | Done |
| `purpose_emergence.py` | **MISSING** | HIGH |
| `topology_reasoning.py` | **MISSING** | HIGH |
| `edge_extractor.py` | **MISSING** | MEDIUM |

### 3.3 Automation Gaps

| Gap | Current State | Needed |
|-----|---------------|--------|
| Inbox processing | 70 OPPs waiting | Enrichment run |
| Macro library | 0 macros in library | At least 1 production macro |
| Delta detection | Only TDJ file list | Semantic change tracking |

---

## Section 4: Active Work Streams

### 4.1 Just Completed (This Session)

| Item | Status | Commit |
|------|--------|--------|
| graph_type_inference tests | 29 tests, all pass | `13425bb` |
| PURPOSE_EMERGENCE.md | Created | `13425bb` |
| OPP-RESEARCH-001 (ConAff) | In inbox | `13425bb` |
| Autopilot 24h enrichment | Wired | `2bebee3` |
| BARE_IMPLEMENTATION_ROADMAP.md | Created | `2bebee3` |

### 4.2 Inbox (70 OPPs Waiting)

**Categories identified:**
- OPP-002 to OPP-092: Various improvements
- OPP-ARCH-*: Architecture opportunities (8)
- OPP-RESEARCH-001: ConAff research

**Next action:** Run enrichment to triage, score, and promote high-confidence items.

### 4.3 Active Tasks (in .agent/registry/active/)

33 tasks exist. Status unknown - need audit.

---

## Section 5: Confidence Assessment

### 5.1 What We Know With High Confidence (>90%)

1. The pipeline works end-to-end
2. Tests pass consistently
3. Automation infrastructure exists
4. Documentation structure is established

### 5.2 What We Know With Medium Confidence (60-90%)

1. Purpose emergence theory is sound
2. Enrichment pipeline will work when triggered
3. BARE roadmap is achievable in 14-21 days

### 5.3 What We're Uncertain About (<60%)

1. ~~Why reachability is only 29.3%~~ **RESOLVED** - Was stale data, actual is 99.8%
2. Whether 915 TODOs are real or noise
3. Whether batch grading full runs will succeed
4. ~~True state of 33 active tasks~~ **RESOLVED** - Audited, now 6 active

---

## Section 6: Gap Analysis Summary

### Critical Gaps (Block Progress)

1. ~~**Reachability investigation**~~ **RESOLVED** - Was stale data (99.8% actual)
2. ~~**Active task audit**~~ **RESOLVED** - 33→6 tasks, 27 archived
3. ~~**Inbox processing**~~ **RESOLVED** - 15 Decision Deck cards generated

### Knowledge Gaps (Need Research)

1. **ConAff applicability** - OPP-RESEARCH-001 proposes enhancement
2. **Theory amendments** - A1/A2/A3 need integration
3. ~~**Glossary consolidation**~~ **RESOLVED** - Was mischaracterized (complementary files)

### Execution Gaps (Need Work)

1. **Test coverage** - purpose_emergence, topology_reasoning
2. **Full batch scans** - 590 repos need `collider full`
3. **BARE M1** - Delta detection not started
4. **TASK-074** - Split analyze.py (AI scored 99% ready)

---

## Section 7: Crystallized Plan (Slow Pace)

### Week 1: Stabilize Knowledge (COMPLETE)

| Day | Focus | Status | Finding |
|-----|-------|--------|---------|
| Mon | Audit 33 active tasks | **DONE** | 82% were noise (33→6) |
| Tue | Investigate reachability | **DONE** | Phantom blocker (29.3% was stale, actual 99.8%) |
| Wed | Run enrichment | **DONE** | 15 new Decision Deck cards, TASK-074 ready |
| Thu | Consolidate glossary | **DONE** | Was mischaracterized (complementary, not fragmented) |
| Fri | Review patchwork | **DONE** | This update |

**Week 1 Key Insight:** 3 of 4 "critical" issues were phantoms (stale data or mischaracterization). Validating assumptions before acting is essential.

### Week 2: Fill Critical Gaps

| Day | Focus | Deliverable |
|-----|-------|-------------|
| Mon | Add tests for purpose_emergence | Test coverage +50 |
| Tue | Add tests for topology_reasoning | Test coverage +30 |
| Wed | Fix batch_grade script | Full scan capability |
| Thu | Run 10 full scans | Proof of concept |
| Fri | Update OPEN_CONCERNS | Resolved items marked |

### Week 3: BARE Milestone 1

| Day | Focus | Deliverable |
|-----|-------|-------------|
| Mon-Wed | Delta detection implementation | delta_detector.py |
| Thu-Fri | Integration with autopilot | Runs on commit |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | Claude | Initial knowledge patchwork |
| 1.1.0 | 2026-01-27 | Claude | Week 1 complete: resolved 3 phantom issues, updated gaps |
