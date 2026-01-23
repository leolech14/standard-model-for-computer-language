# Documentation Reorganization Task Registry

> **ARCHIVED:** This registry is complete (7/10 tasks done, 3 deferred/rejected).
> No further action needed. Retained for historical reference.
> Archived: 2026-01-23

---

> Confidence-scored evaluation of proposed documentation changes.

**Date:** 2026-01-20
**Evaluator:** Claude (reviewing agent proposal)
**Context:** Agent proposed major docs restructure; this registry evaluates each task.

---

## Scoring Dimensions

| Dimension | Question | Scale |
|-----------|----------|-------|
| **Factual** | Is my understanding of current state correct? | 0-100% |
| **Vision** | Does this serve project mission? | 0-100% |
| **Current** | Does this fit codebase as it exists? | 0-100% |
| **Onwards** | Does this fit where codebase is heading? | 0-100% |

**Project Vision:** "Find the basic constituents of computer programs"
**Architecture:** Body (Collider engine) + Brain (AI tools, cloud)
**Principle:** Clean separation of concerns between hemispheres

---

## Registry

### TASK-001: Move THEORY.md to standard-model-of-code/docs/

**Source:** Agent proposal
**Action:** Relocate `context-management/docs/theory/THEORY.md` to `standard-model-of-code/docs/theory/`

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 90% | THEORY.md exists at stated path, 176KB, minimal overlap with MODEL.md |
| Vision | 40% | Theory consolidation sounds good but ignores hemisphere purpose |
| Current | 30% | Breaks Body/Brain separation - THEORY serves AI agents (Brain), MODEL serves tool (Body) |
| Onwards | 35% | Future AI agents need extended theory in Brain hemisphere for context |

**Verdict:** REJECT
**Why:** The split is architectural, not accidental. MODEL.md (8KB spec) is for Collider internals. THEORY.md (176KB narrative) is for AI agent context. Moving it conflates two different consumers.

---

### TASK-002: Create deep nesting (docs/ai/ops/prompts/)

**Source:** Agent proposal
**Action:** Restructure `context-management/docs/` into `ai/ops/`, `ai/prompts/`, `ai/agent_school/`

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 85% | Files exist, would fit in proposed structure |
| Vision | 45% | Organization sounds cleaner but adds navigation depth |
| Current | 40% | Current flat structure with good README is navigable |
| Onwards | 50% | Deep nesting may help at scale but unclear if needed |

**Verdict:** DEFER
**Why:** Premature optimization. Current structure works. Deep nesting adds cognitive load for marginal tidiness. Revisit if docs grow 3x.

---

### TASK-003: Move top-level PNGs to assets/

**Source:** My recommendation
**Action:** `git mv context-management/docs/*.png context-management/docs/assets/`

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 98% | 12 PNGs at root, 26 already in assets/, verified via ls |
| Vision | 75% | Cleaner docs root helps AI agents find text docs faster |
| Current | 95% | assets/ folder exists, same pattern already in use |
| Onwards | 85% | Consistent asset organization scales well |

**Verdict:** ACCEPT
**Why:** Low risk, high consistency. Assets belong in assets/. Pattern already established.

**Commands:**
```bash
git mv context-management/docs/*.png context-management/docs/assets/
grep -r "\.png" context-management/docs/*.md | grep -v assets/  # Check for broken refs
```

---

### TASK-004: Create reports/ folder and move report files

**Source:** Agent proposal (modified)
**Action:** Create `context-management/docs/reports/` and move 4 report-like files

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 85% | 4 files identified as reports, no reports/ folder exists |
| Vision | 55% | Marginal improvement to organization |
| Current | 60% | Only 4 files; creating folder for 4 files is borderline |
| Onwards | 65% | If more reports accumulate, pattern helps |

**Verdict:** OPTIONAL
**Why:** Not wrong, but not necessary. 4 files don't justify a new folder. Revisit if report count exceeds 8.

**Files in question:**
- DATA_LAYER_REFACTORING_MAP.md (18KB)
- EVAL_LOG.md (895B)
- REPOSITORY_AUDIT_2026-01-19.md (6KB)
- TIMELINE_ANALYSIS.md (12KB)

---

### TASK-005: Fix AI_OPERATING_MANUAL.md broken references

**Source:** My recommendation
**Action:** Update references from deleted filename to new `AI_USER_GUIDE.md`

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 95% | 6 files reference old name, verified via grep |
| Vision | 80% | Broken links hurt AI agent onboarding |
| Current | 100% | File was renamed, references are factually broken |
| Onwards | 90% | Clean references prevent future confusion |

**Verdict:** ACCEPT
**Why:** Factually broken. Must fix for correctness.

**Critical fix:**
```
context-management/docs/operations/AGENT_INITIATION.md:21
- Change: AI_OPERATING_MANUAL.md → AI_USER_GUIDE.md
```

**Secondary (auto-regenerates):**
- REGISTRY.json (lines 2222-2225)
- REGISTRY_REPORT.md (line 323)
- output/analysis_sets_report.md
- output/file_metadata_audit.csv

**Low priority (historical doc):**
- proposals/COLLIDER_AI_INSIGHTS_PROPOSAL.md (line 341)

---

### TASK-006: Move COLLIDER_ARCHITECTURE.md to standard-model-of-code/

**Source:** Agent proposal
**Action:** Relocate architecture doc from Brain to Body

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 90% | File exists at context-management/docs/COLLIDER_ARCHITECTURE.md |
| Vision | 60% | Architecture docs could live in either hemisphere |
| Current | 50% | Currently in Brain, referenced by AI tools for context injection |
| Onwards | 55% | Moving breaks existing tool configs (analysis_sets.yaml) |

**Verdict:** REJECT
**Why:** The file is actively used by `local_analyze.py` in architect mode. Moving it requires config updates and provides no functional benefit. Location is fine.

---

### TASK-007: Update README files to clarify doc roles

**Source:** My recommendation
**Action:** Add explicit role descriptions to both docs/README.md files

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 80% | Current README explains structure but roles could be clearer |
| Vision | 85% | Clear documentation serves AI agents and humans |
| Current | 90% | READMEs exist, just need enhancement |
| Onwards | 90% | Better onboarding scales with contributor growth |

**Verdict:** ACCEPT (LOW PRIORITY)
**Why:** Improves clarity without restructuring. Can be done incrementally.

**Suggested additions to context-management/docs/README.md:**
```markdown
## Document Roles

| Document | Consumer | Purpose |
|----------|----------|---------|
| MODEL.md (Body) | Collider tool | Canonical spec, definitions |
| THEORY.md (Brain) | AI agents | Extended narrative, context |
| COLLIDER_ARCHITECTURE.md | AI architect mode | System design reference |
```

---

## Summary Matrix

| Task | Factual | Vision | Current | Onwards | Verdict |
|------|---------|--------|---------|---------|---------|
| 001: Move THEORY.md | 90% | 40% | 30% | 35% | REJECT |
| 002: Deep nesting | 85% | 45% | 40% | 50% | DEFER |
| 003: Move PNGs | 98% | 75% | 95% | 85% | **ACCEPT** |
| 004: Create reports/ | 85% | 55% | 60% | 65% | OPTIONAL |
| 005: Fix broken refs | 95% | 80% | 100% | 90% | **ACCEPT** |
| 006: Move COLLIDER_ARCHITECTURE | 90% | 60% | 50% | 55% | REJECT |
| 007: Clarify README | 80% | 85% | 90% | 90% | ACCEPT (LOW) |

---

## Execution Order

1. **TASK-005** - Fix broken references (correctness)
2. **TASK-003** - Move PNGs to assets/ (consistency)
3. **TASK-007** - Update README (clarity) - optional

**Total effort:** ~10 minutes
**Risk:** Low
**Files changed:** 2-3 manual edits + 12 git mv operations

---

## What We're NOT Doing (and Why)

| Rejected Action | Why |
|-----------------|-----|
| Consolidating theory docs | Breaks hemisphere architecture |
| Deep folder nesting | Premature optimization |
| Moving COLLIDER_ARCHITECTURE.md | Breaks tool configs |
| Creating reports/ for 4 files | Insufficient volume |

---

## AI Validation Critique

**Source:** `local_analyze.py --mode architect` (2026-01-20)

### Scoring Adjustments Recommended

| Issue | Recommendation |
|-------|----------------|
| Factual scores too high | Reduce by 5-10% across board for conservatism |
| Vision underweighted | Strategic alignment should carry more weight |
| Current overweighted | Short-term fit emphasized over long-term |

### Blind Spots Identified

The AI identified these gaps in the original registry:

---

### TASK-008: Reconcile Atom Documentation

**Source:** AI critique
**Action:** Reconcile FORMAL_PROOF.md (167 atoms) vs 200_ATOMS.md vs implemented (94 atoms)

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 85% | Multiple atom counts exist, discrepancy is real |
| Vision | 95% | Core to project mission ("find basic constituents") |
| Current | 70% | Docs exist but aren't reconciled |
| Onwards | 95% | Atom clarity is foundational for tool evolution |

**Verdict:** ACCEPT (HIGH PRIORITY)
**Why:** 73 documented atoms are not implemented. Where did they go? Deprecated? Planned? This is a truth gap.

**Questions to resolve:**
- Are the 73 missing atoms deprecated or deferred?
- Should 200_ATOMS.md be updated to mark implementation status?
- Should FORMAL_PROOF.md be archived as historical?

---

### TASK-009: Add Schema Validation for Token Files

**Source:** AI critique
**Action:** Add JSON Schema validation for `appearance.tokens.json` and `controls.tokens.json`

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 75% | Token files exist, no schema validation currently |
| Vision | 70% | Type safety improves tool reliability |
| Current | 60% | Stringly-typed dot notation is fragile |
| Onwards | 80% | Schema validation prevents silent failures |

**Verdict:** ACCEPT (MEDIUM PRIORITY)
**Why:** Token resolution uses string lookups; schema validation catches errors early.

---

### TASK-010: Expand README Scope

**Source:** AI critique
**Action:** Add tooling links and contribution guidelines to README files

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Factual | 80% | READMEs exist, don't include tooling/contribution info |
| Vision | 75% | Onboarding serves growth |
| Current | 85% | Low effort, high discoverability gain |
| Onwards | 80% | Contributors need clear entry points |

**Verdict:** ACCEPT (LOW PRIORITY)
**Why:** Enhances onboarding without restructuring.

**Content to add:**
- Links to CLI tools using the models
- How to propose changes to atoms
- How to add new patterns

---

## Revised Summary Matrix

| Task | Factual | Vision | Current | Onwards | Verdict |
|------|---------|--------|---------|---------|---------|
| 001: Move THEORY.md | 85% | 40% | 30% | 35% | REJECT |
| 002: Deep nesting | 80% | 45% | 40% | 50% | DEFER |
| 003: Move PNGs | 95% | 75% | 95% | 85% | **ACCEPT** |
| 004: Create reports/ | 80% | 55% | 55% | 65% | OPTIONAL |
| 005: Fix broken refs | 90% | 80% | 100% | 90% | **ACCEPT** |
| 006: Move COLLIDER_ARCHITECTURE | 85% | 60% | 50% | 55% | REJECT |
| 007: Clarify README | 75% | 85% | 90% | 90% | ACCEPT (LOW) |
| 008: Reconcile Atoms | 85% | 95% | 70% | 95% | **ACCEPT (HIGH)** |
| 009: Token Schema | 75% | 70% | 60% | 80% | ACCEPT (MEDIUM) |
| 010: Expand README | 80% | 75% | 85% | 80% | ACCEPT (LOW) |

*Scores adjusted -5% on Factual per AI recommendation for conservatism.*

---

## Revised Execution Order

1. **TASK-005** - Fix broken references (correctness)
2. **TASK-003** - Move PNGs to assets/ (consistency)
3. **TASK-008** - Reconcile atom documentation (foundational truth)
4. **TASK-009** - Token schema validation (reliability)
5. **TASK-007/010** - README improvements (onboarding)

---

## Appendix: Factual Verification Commands

```bash
# Verify PNG counts
ls context-management/docs/*.png | wc -l        # Should be 12
ls context-management/docs/assets/*.png | wc -l # Should be 26

# Verify broken references
grep -r "AI_OPERATING_MANUAL" context-management/

# Verify THEORY.md location and size
wc -c context-management/docs/theory/THEORY.md  # ~176KB
wc -c standard-model-of-code/docs/MODEL.md      # ~8KB

# Verify hemisphere structure
ls -la context-management/docs/README.md
ls -la standard-model-of-code/docs/README.md
```
