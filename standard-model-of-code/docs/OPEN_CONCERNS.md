# Open Concerns & Development Tracker

**Last Updated:** 2026-01-25
**Status:** AUTHORITATIVE (Single concerns tracker)
**Scope:** All domains (Particle, Wave, Observer, UI)

---

## Executive Summary (2026-01-25)

| Domain | Critical | High | Medium | Low | Blocked |
|--------|:--------:|:----:|:------:|:---:|:-------:|
| **Collider (Particle)** | 1 | 2 | 4 | 2 | 1 |
| **Context (Wave)** | 0 | 2 | 1 | 1 | 0 |
| **Agent (Observer)** | 0 | 1 | 2 | 1 | 0 |
| **UI (Visualization)** | 0 | 2 | 3 | 2 | 1 |
| **Infrastructure** | **2** | **1** | 0 | 0 | 0 |
| **Documentation** | 0 | **2** | 1 | 0 | 0 |
| **TOTAL** | **3** | **10** | **11** | **6** | **2** |

### Validated Metrics (2026-01-25)

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Collider Self-Grade | B (8.0+) | **7.6 (C)** | YELLOW |
| Wave-Particle Symmetry | 90 (Gold) | **81 (Silver)** | YELLOW |
| Test Pass Rate | >95% | **100%** (354/354) | GREEN |
| Node Count (Full+Tests) | 2,353 | 2,509 | GREEN (+6.6%) |
| Reachability | >60% | 29.3% | RED (strategic blocker) |
| Tree-sitter | Pinned | `>=0.20.0,<0.22` | GREEN |
| Documentation Files | - | 1,550 | HIGH VOLUME |
| Stale Docs (>30d) | <20% | **44%** (678) | YELLOW |
| TODOs/FIXMEs | <100 | **915** | RED |
| Glossary Files | 1 | **5** | RED (fragmented) |

---

## Session Summary (2026-01-23)

### Completed Tasks

| Task | Description | Files Modified |
|------|-------------|----------------|
| Pipeline Navigator Integration | P key now shows 27-stage pipeline with timing data | `full_analysis.py`, `pipeline-navigator.js` |
| Node Count Ground Truth | Established canonical counts: Core=1,179, Full=1,961 | `NODE_COUNT_GROUND_TRUTH.md` |
| File View Camera Fix | Camera state preserved when switching Atom/File views | `sidebar.js` |

### Key Changes

1. **`src/core/full_analysis.py`**
   - Added `build_pipeline_snapshot()` function (lines 950-1022)
   - Generates snapshot before output generation (lines 2194-2201)
   - Fixed survey import bug (`from src.core.survey import`)

2. **`src/core/viz/assets/modules/sidebar.js`**
   - Added camera state preservation in `setViewMode()` (lines 558-625)
   - Saves/restores camera position when switching between Atom/File views

3. **`src/core/survey.py`**
   - Added `.repos_cache/` to exclusion patterns

---

## Open Concerns

### HIGH PRIORITY

| ID | Concern | Impact | Status | Action |
|----|---------|--------|--------|--------|
| OC-009 | ~~Scope Leakage~~ | ~~Core count 2,809 >> Expected 1,179~~ | **RESOLVED** (2026-01-25) | Survey IS working (2,509 nodes, 51 paths excluded) |
| OC-001 | ~~Test failures in pattern_matcher.py~~ | ~~11 tests fail due to missing `tree_sitter`~~ | **FIXED** (2026-01-25) | Pinned `tree-sitter>=0.20,<0.22` |
| OC-010 | ~~88 skipped tests unexplained~~ | ~~40% of test suite skipped~~ | **INVALIDATED** (2026-01-25) | Only 2 skips, 354 passed (100% pass rate) |
| OC-002 | **Pipeline snapshot lacks per-stage node counts** | Navigator shows timing but not deltas | ENHANCEMENT | Instrument `snapshot.py` per-stage |
| OC-003 | **Pyright type errors in full_analysis.py** | ~10 type issues | TECH_DEBT | Policy: `# type: ignore` if fix >30 min |

### MEDIUM PRIORITY

| ID | Concern | Impact | Status | Action |
|----|---------|--------|--------|--------|
| OC-004 | Physics behavior differs between Atom/File views | File view has `forceCenter(0,0,0)`, Atom doesn't | INVESTIGATE | Reproduce: toggle views, compare forces |
| OC-005 | Node count variance (2787→2807→2809) | ~0.7% drift between runs | MONITORING | Track in CI, establish baseline |
| OC-006 | Pipeline Navigator stage names mismatch | `stage_2_5` vs `stage_2.5` format | COSMETIC | Update `build_pipeline_snapshot()` |

### LOW PRIORITY

| ID | Concern | Impact | Status | Action |
|----|---------|--------|--------|--------|
| OC-007 | Unused variable warnings in sidebar.js (line 818, 828) | TypeScript lint | COSMETIC | Remove unused `active` vars |
| OC-008 | `snapshot.py` has unused FieldDelta/sample functions | Dead code | TECH_DEBT | Wire up or remove |

### RESOLVED (Fixed)

> ACI correctness audit (2026-01-24). Discovered by Codex, fixed by Claude.

| ID | Concern | Priority | Status |
|----|---------|----------|--------|
| OC-011 | ACI: HYBRID tier returned by routing but had no execution path in `analyze.py` (silent fall-through to internal-only) | HIGH | FIXED (`522d9e2`) |
| OC-012 | ACI: invalid set names emitted by semantic matching could crowd out valid sets, causing silent context loss | HIGH | FIXED (`522d9e2`) |
| OC-013 | Perplexity membrane missing: local repo context was injected into external search query, polluting retrieval | HIGH | FIXED (`522d9e2`) |
| OC-014 | Agent context triggers too generic ("run", "task", "confidence") → false positives | MEDIUM | FIXED (`522d9e2`) |
| OC-015 | ACI set cap applied before sanitization + FLASH_DEEP missing sanitization → valid sets dropped | MEDIUM | FIXED (`10e4001`) |

**Commits:**
- `522d9e2`: Phase 1 ACI correctness (set sanitization, HYBRID execution, Perplexity membrane, trigger refinement)
- `10e4001`: Pre-cap removal + FLASH_DEEP sanitization (bundled with elevation fix)

**Validation:** `--tier hybrid` smoke run + set sanitization debug + pytest (354 passed)

---

## CRITICAL: Infrastructure Failures (2026-01-25)

> Systems that exist, run, but fail to deliver their intended value due to wiring/configuration gaps.

### FAIL-001: Batch Grading Captured Grades Only, Not Full Scans

**Severity:** CRITICAL
**DoD Violation:** Yes - DoD required 999 full `collider full` scans, got 590 `collider grade` summaries
**Discovered:** 2026-01-25 by session investigation

#### What Happened

| Aspect | Expected | Actual |
|--------|----------|--------|
| Command | `collider full <repo> --output <dir>` | `collider grade <repo> --json` |
| Output | `unified_analysis.json` per repo (5-50MB each) | 500-byte JSON summary per repo |
| Data captured | topology_shape, dead_code_pct, layer/role distribution, full graph | grade, health_index, component_scores, node/edge counts only |
| Total data | ~30-50 GB of analysis artifacts | ~300 KB of summaries |

#### Root Cause

**File:** `standard-model-of-code/tools/batch_grade/run_batch_local.py:89`
```python
# WRONG: Uses lightweight grade command
[sys.executable, str(COLLIDER_ROOT / "cli.py"), "grade", str(repo_dir), "--json"]

# SHOULD BE: Full analysis with output capture
[sys.executable, str(COLLIDER_ROOT / "cli.py"), "full", str(repo_dir), "--output", str(output_dir)]
```

#### What We Have (Partially Useful)

| Location | Contents |
|----------|----------|
| `standard-model-of-code/tools/batch_grade/grades_DEGRADED_summary_only/` | 590 successful grades, 409 failed (RENAMED 2026-01-25) |
| `standard-model-of-code/tools/batch_grade/grades_DEGRADED_summary_only/DEGRADED.md` | Marker file explaining degradation |
| `standard-model-of-code/tools/batch_grade/full_scans/` | EMPTY - awaiting proper run |
| `standard-model-of-code/tools/batch_grade/repos_999.json` | List of 999 GitHub repos (top by stars) |

**Top 10 Healthiest (Grade B):**
- mingrammer/diagrams (8.29), jashkenas/backbone (8.17), VincentGarreau/particles.js (8.12)

**Key Learning:** CYCLES (b1) is the primary differentiator between grades (9.4 for B vs 1.0 for F).
See `grades_DEGRADED_summary_only/LEARNINGS.md` for full analysis.

#### What We Don't Have (The Actual DoD)

- [ ] `unified_analysis.json` for any of the 590 repos
- [ ] Topology shape distribution across real-world codebases
- [ ] Dead code % distribution
- [ ] Layer/role pattern analysis at scale
- [ ] Edge cases and crash reports from diverse repos

#### Path Forward

| Option | Effort | Cost | Outcome |
|--------|--------|------|---------|
| A. Re-run top 10 B-grade with `full` | 2 hrs | ~$0.05 | Proof of concept, golden repo candidates |
| B. Re-run all 590 successful with `full` | 8-12 hrs | ~$2-3 | Full dataset, ~30GB output |
| C. Fix script + re-run 1098 repos | 12-16 hrs | ~$3-5 | Complete experiment with expanded set |

#### Traceability Index

| Reference | Location |
|-----------|----------|
| Batch script (wrong command) | `standard-model-of-code/tools/batch_grade/run_batch_local.py:89` |
| Grade command definition | `standard-model-of-code/cli.py:679-793` |
| Full command definition | `standard-model-of-code/cli.py:799-850` |
| Degraded results | `standard-model-of-code/tools/batch_grade/grades_DEGRADED_summary_only/` |
| Degradation marker | `standard-model-of-code/tools/batch_grade/grades_DEGRADED_summary_only/DEGRADED.md` |
| **Learnings extracted** | `standard-model-of-code/tools/batch_grade/grades_DEGRADED_summary_only/LEARNINGS.md` |
| Full scans target | `standard-model-of-code/tools/batch_grade/full_scans/` |
| Repo list | `standard-model-of-code/tools/batch_grade/repos_999.json` |
| README | `standard-model-of-code/tools/batch_grade/README.md` |
| Subsystem registry | `.agent/SUBSYSTEM_INTEGRATION.md` (S11) |
| Task #37 | Session task list (REOPENED) |

---

### FAIL-002: Cloud Automation Never Deployed (By Design, But Undiscoverable)

**Severity:** CRITICAL
**Impact:** 34 opportunities stuck in local inbox, auto-boost pipeline non-functional
**Discovered:** 2026-01-25 by session investigation

#### What Happened

Cloud automation tools exist and are functional, but:
1. Never deployed to GCP (intentional per local-first strategy)
2. Not wired into post-commit hooks (fixed 2026-01-25)
3. Not documented in SUBSYSTEM_INTEGRATION.md (fixed 2026-01-25)
4. Not discoverable by agents or humans

#### Files Involved

| File | Purpose | Status |
|------|---------|--------|
| `.agent/tools/cloud/auto_boost_function.py` | Cloud Function for auto-promoting opportunities | EXISTS, NOT DEPLOYED |
| `.agent/tools/cloud/sync_registry.py` | Sync local registry ↔ GCS | EXISTS, NOW WIRED |
| `.agent/tools/cloud/deploy.sh` | Deployment script | EXISTS, NEVER RUN |
| `.agent/tools/cloud/check_status.sh` | Health check | CREATED 2026-01-25 |
| `.agent/hooks/post-commit` | Automation trigger | UPDATED 2026-01-25 to include sync |
| `.agent/SUBSYSTEM_INTEGRATION.md` | Integration map | UPDATED 2026-01-25 to add S10 |

#### Root Cause

**Intentional but undocumented.** Per `context-management/docs/operations/CASE_AGAINST_PREMATURE_CLOUD.md`:
> "FIX LOCALLY FIRST → VALIDATE LOCALLY → THEN CLOUD"

But this decision was:
- Not visible in subsystem registry
- Not flagged as "pending deployment"
- Not linked from tool directories

#### Fixes Applied (2026-01-25)

1. Added S10 (Cloud Automation) to `.agent/SUBSYSTEM_INTEGRATION.md`
2. Wired `sync_registry.py` into `.agent/hooks/post-commit`
3. Created `.agent/tools/cloud/check_status.sh` for monitoring

#### Still Pending

- [ ] Deploy Cloud Function: `cd .agent/tools/cloud && ./deploy.sh scheduler`
- [ ] Create Cloud Scheduler job (hourly trigger)
- [ ] Initial sync: `python .agent/tools/cloud/sync_registry.py`
- [ ] Verify with: `.agent/tools/cloud/check_status.sh`

#### Traceability Index

| Reference | Location |
|-----------|----------|
| Cloud tools directory | `.agent/tools/cloud/` |
| Local-first decision doc | `context-management/docs/operations/CASE_AGAINST_PREMATURE_CLOUD.md` |
| Background AI Layer Map | `context-management/docs/BACKGROUND_AI_LAYER_MAP.md` (shows AEP Cloud: 0%) |
| Subsystem Integration | `.agent/SUBSYSTEM_INTEGRATION.md` (S10 added) |
| Post-commit hook | `.agent/hooks/post-commit` (sync added) |
| Health check | `.agent/tools/cloud/check_status.sh` |

---

### HIGH-001: Discoverability Pattern - Tools Exist But Aren't Wired

**Severity:** HIGH
**Pattern:** Recurring across batch_grade, cloud automation, potentially others

#### The Anti-Pattern

```
1. Tool is built ✓
2. Tool works when manually invoked ✓
3. Tool is NOT in subsystem registry ✗
4. Tool is NOT wired to triggers ✗
5. Tool outputs are NOT consumed ✗
6. Tool is invisible to agents/humans ✗
```

#### Known Instances

| Tool | Built | Works | In Registry | Wired | Outputs Consumed |
|------|:-----:|:-----:|:-----------:|:-----:|:----------------:|
| batch_grade | ✓ | ✓ | ✓ (S11) | ✗ | ✓ (`analyze_results.py`) |
| cloud/auto_boost | ✓ | ? | ✓ (S10) | ✗ | ✗ |
| cloud/sync_registry | ✓ | ✓ | ✓ (S10) | ✓ (now) | ✗ |

### HIGH-002: Batch Grade Has No Results Analyzer - **RESOLVED**

**Severity:** HIGH (was)
**Pattern:** Producer exists, consumer missing
**Status:** **RESOLVED** (2026-01-25)

#### Resolution

Created `standard-model-of-code/tools/batch_grade/analyze_results.py` that:
1. Loads `final_results_*.json` ✓
2. Computes statistics (grade distribution, component correlations) ✓
3. Identifies golden repo candidates ✓
4. Outputs markdown/JSON reports ✓
5. Works as CLI tool AND importable library ✓

#### Usage

```bash
# CLI: Generate markdown report
python tools/batch_grade/analyze_results.py <results.json>

# CLI: Generate JSON output
python tools/batch_grade/analyze_results.py <results.json> --format json

# Library: Programmatic access
from analyze_results import BatchAnalyzer
analyzer = BatchAnalyzer.from_file("final_results.json")
print(analyzer.grade_distribution)
print(analyzer.golden_repos(10, "B"))
```

#### Traceability

| Reference | Location |
|-----------|----------|
| **New module** | `standard-model-of-code/tools/batch_grade/analyze_results.py` |
| Manual analysis | `grades_DEGRADED_summary_only/LEARNINGS.md` |
| Stats generator (single scope) | `src/core/stats_generator.py` |
| Charts engine (single scope) | `src/core/scientific_charts.py` |

---

#### Required Checklist for New Tools

Before marking any tool "complete":
- [ ] Added to `.agent/SUBSYSTEM_INTEGRATION.md` with ID (S1, S2, ...)
- [ ] Wired to appropriate trigger (post-commit, cron, manual)
- [ ] Outputs documented with consumer identified
- [ ] Health check or validation method exists
- [ ] Linked from relevant CLAUDE.md files
- [ ] **Results have a consumer (not just producer)**

---

## Documentation Concerns (2026-01-25)

> Assessed via Collider self-analysis + manual audit. Full report: `docs/reports/DOCUMENTATION_HEALTH_ASSESSMENT_20260125.md`

### HIGH-003: Glossary Fragmentation (5 Files)

**Severity:** HIGH
**Impact:** No single source of truth for terminology
**Discovered:** 2026-01-25

| File | Location | Format | Status |
|------|----------|--------|:------:|
| GLOSSARY.md | `archive/docs_consolidated_2026-01-19/` | Markdown | ARCHIVED |
| GLOSSARY.yaml | `standard-model-of-code/docs/` | YAML | ACTIVE |
| GLOSSARY.md | `context-management/docs/archive/legacy_schema_2025/` | Markdown | LEGACY |
| GLOSSARY.md | `context-management/docs/` | Markdown | ACTIVE? |
| GLOSSARY_GAP_MAP.md | `context-management/docs/` | Markdown | META |

**Action:** Consolidate to single `standard-model-of-code/docs/GLOSSARY.yaml` with CI validation.

### HIGH-004: TODO Sprawl (915 Items)

**Severity:** HIGH
**Impact:** Untracked commitments, hidden technical debt
**Discovered:** 2026-01-25

**Count:** 915 TODOs/FIXMEs across codebase

**Problem:** TODOs represent promises to future developers. 915 untracked promises = 915 potential broken contracts.

**Action:** Triage into three buckets:
1. Convert to task registry entries
2. Delete if obsolete
3. Accept as permanent (add `# PERMANENT:` prefix)

### MEDIUM: Stale Documentation (44%)

**Severity:** MEDIUM
**Impact:** Outdated information may mislead

| Metric | Value |
|--------|-------|
| Total .md files | 1,550 |
| Stale (>30 days) | 678 (44%) |
| Recent (<7 days) | 803 (52%) |

**Action:** Archive audit - identify docs to delete, update, or mark as historical.

### Documentation Health Metrics

| Metric | Value | Target | Gap |
|--------|-------|--------|-----|
| Collider Self-Grade | 7.6/10 (C) | 8.0/10 (B) | 0.4 |
| Wave-Particle Symmetry | 81/100 | 90/100 | 9 |
| Max Cyclomatic Complexity | 217 | <50 | 167 |
| Dead Code | 2.09% | <5% | OK |
| Dependency Cycles | 0 | 0 | OK |

---

## Strategic Gaps (Phase Blockers)

> These block roadmap progress, not just code quality.

### CRITICAL (Blocks Phases)

| ID | Gap | Blocks | Status | Path Forward |
|----|-----|--------|--------|--------------|
| SG-001 | **Reachability bottleneck (29.3%)** | Phase 3-4 | BLOCKING | Expand entrypoint detection, improve call resolution |
| SG-002 | **Phase 2 (Resolution) not started** | Phase 3 | NOT_STARTED | Call resolver improvements, import strictness |
| SG-003 | **Health Model A-component** | Phase 5 | UNIMPLEMENTED | Formula exists (H=10×(0.25T+0.25E+0.25Gd+0.25A)), alignment scoring missing |
| SG-004 | **Task Registry → BARE loop** | Auto-refinement | PROPOSED | P1-Critical in SUBSYSTEM_INTEGRATION.md, needs tasks.yaml polling |

### IMPORTANT (Reduces Capability)

| ID | Gap | Impact | Status | Path Forward |
|----|-----|--------|--------|--------------|
| SG-005 | **UPB documented but unintegrated** | Visualization intelligence | 13:0 docs:code | Wire to HTML generation |
| SG-006 | **BARE 40% missing** | Inference pipeline | CrossValidator + ConceptMapper = 0% | Implement or descope |
| SG-007 | **Centripetal Scan blocked** | Strategic insights | API quota | Budget allocation or batch mode |
| SG-008 | **Cross-language (TS/JS) unscoped** | Phase 8 | ZERO implementation | Tree-sitter JS/TS grammars |

### MINOR (Tech Debt)

| ID | Gap | Impact | Status |
|----|-----|--------|--------|
| SG-009 | Wave-Particle asymmetry | 81/100 Silver | 19 docs without code, 8 code undocumented |
| SG-010 | Terminology (Attributes vs Lenses) | Phase 5 deliverable | Model.md uses both inconsistently |
| SG-011 | Perplexity not in HSL loop | External research | --enable-external-search proposed (P2) |

---

## Known Limitations

### Pipeline Navigator

- **No per-stage node/edge counts** - Only captures timing, not data flow deltas
- **Static stage layout** - Hardcoded PIPELINE_PHASES array, doesn't adapt to actual stages
- **No stage drill-down** - Clicking stages shows placeholder data only

### File View

- **Camera delay** - 100ms setTimeout for camera restore may cause brief flicker
- **Physics reset** - File graph applies different forces than atom graph

### Node Count Ground Truth

- **Tolerance:** ±10% from canonical counts
- **Scope ambiguity:** "Core" vs "Full" depends on what's included in analysis

---

## Technical Debt

### Type System

**Policy:** Add `# type: ignore` to legacy analysis code if fix takes >30 mins. Prioritize velocity over perfection.

```bash
# Verify type errors:
pyright src/core/full_analysis.py

# Known issues:
#   - Line 1025: CodebaseState not defined
#   - Lines 1171-1180: UnifiedAnalysisOutput.get() issues
#   - Lines 1182, 1187: nodes/edges possibly unbound
```

### Module Dependencies

```bash
# Check if tree_sitter is installed:
python -c "import tree_sitter; print('OK')"

# Fix: Add to requirements.txt OR implement graceful fallback
# pattern_matcher.py: 11 tests skip/fail without tree_sitter
```

---

## Monitoring Metrics

| Metric | Expected | Actual (2026-01-25) | Delta | Status |
|--------|----------|---------------------|-------|--------|
| Full+Tests node count | 2,353 | 2,509 | +6.6% | GREEN |
| Pipeline stages | 27 | 24 | -11% | CHECK |
| Test pass rate | >95% | **100%** (354/354) | +5% | GREEN |
| Reachability | >60% | 29.3% | -50% | RED (strategic blocker) |

---

## Next Session Priorities

1. **HIGH-003: Consolidate 5 glossaries → 1** - Single source of truth for terminology
2. **HIGH-004: Triage 915 TODOs** - Convert to tasks, delete obsolete, or mark permanent
3. **Task #26: Refactor run_full_analysis (CC=217)** - God Function must die
4. **Task #37: Fix batch grading** - Re-run with `collider full` not `grade`
5. **Create src/core/stats/ subsystem** - Per Perplexity research recommendation

---

## Reference: Ground Truth Node Counts

| Scope | Count | What It Includes |
|-------|-------|------------------|
| **Collider Core** | ~1,179 | Python analysis engine + pipeline stages |
| **Collider Full** | ~1,961 | Core + JavaScript visualization |
| **With Tests** | ~2,353 | Full + test suite |
| **Everything** | ~2,787 | All code in repo |

See: `docs/specs/NODE_COUNT_GROUND_TRUTH.md`

---

## Session Log

> **Retention Policy:** Logs older than 7 days are archived to `docs/archive/session_logs/`

### 2026-01-25

- **AM** - Multi-agent UI overhaul session (ChatGPT 5.2 Pro orchestrating, Claude as Agent Beta)
- **PM** - Created `analyze_results.py` batch results analyzer (closes HIGH-002)
  - CLI tool and importable library
  - Generates markdown/JSON reports
  - Computes grade distribution, component variance, golden repos
  - Location: `standard-model-of-code/tools/batch_grade/analyze_results.py`
- **PM** - Investigated cloud automation discoverability failure (FAIL-002)
  - Found `.agent/tools/cloud/` tools existed but not wired
  - Fixed: Added S10 to SUBSYSTEM_INTEGRATION.md
  - Fixed: Wired sync_registry.py to post-commit hook
  - Created: check_status.sh health monitor
- **PM** - Investigated RunPod batch grading results (FAIL-001)
  - Found 590 grades captured, but NO full unified_analysis.json
  - Root cause: `run_batch_local.py:89` uses `grade` not `full`
  - DoD was 999 full scans, got 590 summaries only
  - Documented as CRITICAL infrastructure failure
- **PM** - Added Infrastructure domain to Executive Summary (2 CRITICAL, 1 HIGH)
- **PM** - Identified discoverability anti-pattern (HIGH-001)
- **Task #37** - REOPENED (was incorrectly marked complete - only got grades, not full scans)
- **PM** - Statistical Analysis Consolidation
  - Perplexity research: Centralized `src/core/stats/` recommended
  - Created `docs/specs/STATISTICAL_ANALYSIS_CONSOLIDATION.md`
  - Mapped 7 statistical modules, identified migration plan
- **PM** - Documentation Health Assessment
  - Collider self-grade: 7.6/10 (C)
  - Found 1,550 .md files, 5 fragmented glossaries, 915 TODOs
  - Created `docs/reports/DOCUMENTATION_HEALTH_ASSESSMENT_20260125.md`
  - Added HIGH-003 (glossary fragmentation), HIGH-004 (TODO sprawl)
  - Added Documentation domain to Executive Summary (2 HIGH, 1 MEDIUM)

### 2026-01-24

- **22:00** - Knowledge gaps audit via Explore agent (31 gaps identified)
- **22:10** - Added Strategic Gaps section (SG-001 through SG-011)
- **22:15** - Separated tactical bugs (OC-*) from phase blockers (SG-*)

### 2026-01-23

- **14:33** - Session started (continuation from context loss)
- **14:35** - Regenerated build, found pipeline_snapshot missing
- **14:38** - Located snapshot.py in pipeline/, integrated into full_analysis.py
- **14:39** - Added `build_pipeline_snapshot()` function
- **14:40** - Verified pipeline_snapshot in output (24 stages, 27055ms)
- **14:42** - Task #1 (Pipeline Navigator) completed
- **14:43** - Investigated File View controls issue
- **14:44** - Added camera state preservation to sidebar.js
- **14:45** - Task #3 (File View controls) completed
- **14:46** - Tests: 136 passed, 11 failed (tree_sitter), 88 skipped
- **14:48** - Created OPEN_CONCERNS.md tracker
- **15:02** - Gemini validation: 8.5/10 rating
- **15:05** - Upgraded based on Gemini feedback (added OC-009, % Delta, Action column)
- **15:08** - Re-validation: 9.5/10 rating
- **15:10** - Final upgrade: Added OC-010, tree-sitter version pin, type policy
- **15:15** - Regenerated timestamp CSV: 56,361 files tracked
- **15:18** - Created TIMESTAMP_WORKFLOW.md for agent onboarding

---

## Validation History

| Date | Validator | Score | Key Feedback |
|------|-----------|-------|--------------|
| 2026-01-23 15:02 | Gemini 3 Pro | 8.5/10 | Elevate scope bug, add retention policy, add % Delta |
| 2026-01-23 15:08 | Gemini 3 Pro | 9.5/10 | Tree-sitter version trap, scope hypothesis, 88 skipped tests |
