# Documentation Improvement Task Registry

> **ARCHIVED:** Low priority documentation polish tasks.
> 1/10 tasks complete (T-DOC-010). Remaining tasks deferred.
> Archived: 2026-01-23

---

**Date:** 2026-01-19
**Author:** Claude + Leonardo
**Status:** ARCHIVED (was ACTIVE)
**Validation Source:** Gemini 2.5 Pro Forensic Analysis

---

## 1. EXECUTIVE SUMMARY

This registry tracks documentation improvements optimized for **AI consumption**, not human browsing. All assumptions have been validated against Gemini 2.5 Pro analysis of CLAUDE.md and README.md.

**Core Principle:** Documentation is an AI interface. Design for machine cognition.

---

## 2. ASSUMPTION REGISTRY

### A1: Structure Over Prose
| Attribute | Value |
|-----------|-------|
| **Assumption** | Tables, code blocks, and lists are better than prose for AI |
| **Confidence** | 95% |
| **Validation** | ✓ VALIDATED by Gemini |
| **Evidence** | "Structure is King. Use tables, code blocks, lists, and Mermaid. These formats reduce ambiguity and are easily parsed into structured data, which is how an AI thinks." |
| **Source** | Gemini 2.5 Pro forensic analysis |

### A2: Dual-File Strategy Works
| Attribute | Value |
|-----------|-------|
| **Assumption** | Separate "execution manual" from "conceptual scaffolding" |
| **Confidence** | 90% |
| **Validation** | ✓ VALIDATED by Gemini |
| **Evidence** | "It correctly separates instructions for action from knowledge for understanding... This documentation suite succeeds by not trying to make one file do everything." |
| **Source** | Gemini 2.5 Pro forensic analysis |

### A3: Marketing Language is Noise
| Attribute | Value |
|-----------|-------|
| **Assumption** | Metaphorical/marketing language wastes tokens for AI |
| **Confidence** | 85% |
| **Validation** | ✓ VALIDATED by Gemini |
| **Evidence** | "Phrases like 'The periodic table of code' are powerful for humans but are effectively high-entropy noise for a purely execution-oriented AI." |
| **Source** | Gemini 2.5 Pro forensic analysis |

### A4: Redundancy Wastes Context Window
| Attribute | Value |
|-----------|-------|
| **Assumption** | Restating same concept multiple times hurts AI |
| **Confidence** | 80% |
| **Validation** | ✓ VALIDATED by Gemini |
| **Evidence** | "The core ideas are restated in multiple sections... For an AI, it can be redundant data that consumes context window space." |
| **Source** | Gemini 2.5 Pro forensic analysis |

### A5: Explicit AI Guidance is Gold
| Attribute | Value |
|-----------|-------|
| **Assumption** | Directly telling AI how to think about the project helps |
| **Confidence** | 95% |
| **Validation** | ✓ VALIDATED by Gemini |
| **Evidence** | "This is the single most valuable pattern. The section 'FOR AI: The Missing Semantic Layer' directly instructs the AI on how to frame its thinking." |
| **Source** | Gemini 2.5 Pro forensic analysis |

### A6: Concept-to-Code Bridging Required
| Attribute | Value |
|-----------|-------|
| **Assumption** | Every abstract concept must map to concrete file paths |
| **Confidence** | 90% |
| **Validation** | ✓ VALIDATED by Gemini |
| **Evidence** | "Always link abstract ideas to concrete file paths, as seen in the Dichotomy table. This is the most critical step for making theory actionable." |
| **Source** | Gemini 2.5 Pro forensic analysis |

### A7: GLOSSARY Defines Obvious Terms
| Attribute | Value |
|-----------|-------|
| **Assumption** | Current GLOSSARY defines generic terms AI already knows |
| **Confidence** | 90% |
| **Validation** | ✓ VALIDATED by Gemini 2.5 Pro |
| **Evidence** | `[docs/GLOSSARY.md:L12-L16]` defines "Atom", "Codespace", "Collider". `[docs/UNIFIED_THEORY.md:PART XIV]` contains "Essential Glossary" defining terms like "Abstraction", "Graph", "Hierarchy", "Node", "Recursion" which are foundational to AI training data. |
| **Source** | Gemini 2.5 Pro forensic analysis (2026-01-19) |

### A8: Theory Files Have >30% Overlap
| Attribute | Value |
|-----------|-------|
| **Assumption** | THEORY_MAP, FORMAL_PROOF, MECHANIZED_PROOFS duplicate content |
| **Confidence** | 95% |
| **Validation** | ✓ VALIDATED by Gemini 2.5 Pro |
| **Evidence** | `[docs/THEORY_MAP.md:L30-L80]` describes "4-Tier Stack". `[docs/FORMAL_PROOF.md:Theorem 3.7]` proves same concept formally. `[docs/MECHANIZED_PROOFS.md:Verified Theorems]` and `[docs/FORMAL_PROOF.md:Theorems]` list exact same theorem set (3.3, 3.4, 3.5). Role count inconsistency: 33 in `[docs/UNIFIED_THEORY.md:L250]` vs 27 in `[docs/FORMAL_PROOF.md:Def 1.3]`. |
| **Source** | Gemini 2.5 Pro forensic analysis (2026-01-19) | |

### A9: No Single Command Reference
| Attribute | Value |
|-----------|-------|
| **Assumption** | CLI commands are scattered, no single reference |
| **Confidence** | 85% |
| **Validation** | ⚠️ PARTIALLY VALIDATED |
| **Evidence** | CLAUDE.md has "The One Command" section (good) but other commands scattered |
| **Source** | Local file analysis |

### A10: Error Documentation is Missing
| Attribute | Value |
|-----------|-------|
| **Assumption** | No troubleshooting guide exists |
| **Confidence** | 90% |
| **Validation** | ✓ VALIDATED (by absence) |
| **Evidence** | grep for "error", "troubleshoot", "debug" in docs/ shows no dedicated guide |
| **Source** | Local file analysis |

---

## 3. TASK REGISTRY

### T-DOC-001: Convert GLOSSARY to Structured Reference
| Attribute | Value |
|-----------|-------|
| **Priority** | P1 |
| **Confidence** | 90% |
| **Based On** | A1 (Structure over prose), A7 (Obvious terms) |
| **Status** | TODO |
| **File** | `docs/GLOSSARY.md` |
| **Action** | Replace prose definitions with table: Term \| JSON Path \| Valid Values \| Where Computed |
| **Success Criteria** | Every term maps to concrete code location |
| **Estimated Tokens Saved** | ~200 (30% reduction) |

### T-DOC-002: Add "FOR AI" Section to Key Docs
| Attribute | Value |
|-----------|-------|
| **Priority** | P1 |
| **Confidence** | 95% |
| **Based On** | A5 (Explicit AI guidance) |
| **Status** | TODO |
| **Files** | `docs/ARCHITECTURE.md`, `docs/THEORY_MAP.md`, `docs/ATOMS_REFERENCE.md` |
| **Action** | Add section explaining how AI should use this document |
| **Success Criteria** | Each doc starts with "Read this when you need to [specific task]" |
| **Estimated Token Cost** | +50 per doc (justified by utility) |

### T-DOC-003: Remove Marketing Language from PURPOSE_FIELD.md
| Attribute | Value |
|-----------|-------|
| **Priority** | P2 |
| **Confidence** | 85% |
| **Based On** | A3 (Marketing is noise) |
| **Status** | TODO |
| **File** | `docs/PURPOSE_FIELD.md` |
| **Action** | Remove metaphors, keep math/structure only |
| **Success Criteria** | No sentences that could be in a brochure |
| **Estimated Tokens Saved** | ~150 |

### T-DOC-004: Deduplicate Theory Files
| Attribute | Value |
|-----------|-------|
| **Priority** | P2 |
| **Confidence** | 95% |
| **Based On** | A4 (Redundancy wastes context), A8 (Overlap) - VALIDATED |
| **Status** | TODO (unblocked) |
| **Files** | `docs/THEORY_MAP.md`, `docs/FORMAL_PROOF.md`, `docs/MECHANIZED_PROOFS.md` |
| **Action** | Either merge or add clear differentiation at top of each |
| **Validated Finding** | Gemini confirmed: same theorems (3.3, 3.4, 3.5) in multiple files, 4-Tier Stack repeated, role count inconsistent (33 vs 27) |
| **Success Criteria** | No content appears in more than one file |
| **Estimated Tokens Saved** | ~500-1000 |

### T-DOC-005: Create ERRORS.md Troubleshooting Guide
| Attribute | Value |
|-----------|-------|
| **Priority** | P1 |
| **Confidence** | 90% |
| **Based On** | A10 (Error docs missing) |
| **Status** | TODO |
| **File** | `docs/ERRORS.md` (new) |
| **Action** | Create error→cause→solution reference |
| **Content** | Common errors from Collider, role detection issues, dead code false positives |
| **Success Criteria** | AI can grep error message and find solution |
| **Format** | Table: Error Pattern \| Cause \| Solution \| Example |

### T-DOC-006: Add Concept→Code Bridges to All Docs
| Attribute | Value |
|-----------|-------|
| **Priority** | P2 |
| **Confidence** | 90% |
| **Based On** | A6 (Concept-to-code bridging) |
| **Status** | TODO |
| **Files** | All docs/*.md |
| **Action** | Every concept mentioned must have corresponding file path |
| **Success Criteria** | No abstract term without `src/` or `schema/` reference |
| **Pattern** | "RPBL scoring (`src/core/rpbl_calculator.py:45-89`)" |

### T-DOC-007: Compress QUICKSTART.md to Pure Commands
| Attribute | Value |
|-----------|-------|
| **Priority** | P3 |
| **Confidence** | 80% |
| **Based On** | A1 (Structure over prose) |
| **Status** | TODO |
| **File** | `docs/QUICKSTART.md` |
| **Action** | Remove explanatory prose, keep only commands and tables |
| **Success Criteria** | <100 lines, all actionable |
| **Estimated Tokens Saved** | ~100 |

### T-DOC-008: Create COMMANDS.md Reference
| Attribute | Value |
|-----------|-------|
| **Priority** | P2 |
| **Confidence** | 85% |
| **Based On** | A9 (Scattered commands) |
| **Status** | TODO |
| **File** | `docs/COMMANDS.md` (new) |
| **Action** | Single file with ALL CLI commands, copy-paste ready |
| **Format** | Table: Command \| Purpose \| Example \| Output |
| **Success Criteria** | AI can find any command by grepping this one file |

### T-DOC-009: Remove Redundant Theory Restatements
| Attribute | Value |
|-----------|-------|
| **Priority** | P3 |
| **Confidence** | 80% |
| **Based On** | A4 (Redundancy wastes context) |
| **Status** | TODO |
| **Files** | `docs/README.md` (parent), various |
| **Action** | Each core concept stated exactly ONCE, others reference it |
| **Success Criteria** | grep for "4 phases" returns ≤3 results |

### T-DOC-010: Validate Mirror Configuration
| Attribute | Value |
|-----------|-------|
| **Priority** | P1 |
| **Confidence** | 100% |
| **Based On** | Mirror sync failed, blocking Gemini analysis |
| **Status** | ✓ COMPLETE |
| **File** | `context-management/tools/archive/config.yaml` |
| **Action** | Exclude .tools_venv, fix file path encoding issues |
| **Success Criteria** | `archive.py mirror` completes without errors |
| **Resolution** | Mirror sync completed 2026-01-19: 775 local → 779 remote files, 26 theory files available for Gemini analysis |

---

## 4. DEPENDENCY GRAPH

```
T-DOC-010 (Fix Mirror) ✓ COMPLETE
    │
    └──▶ T-DOC-004 (Dedupe Theory) [UNBLOCKED - ready]

T-DOC-001 (GLOSSARY) ──▶ standalone
T-DOC-002 (FOR AI sections) ──▶ standalone
T-DOC-003 (Remove marketing) ──▶ standalone
T-DOC-005 (ERRORS.md) ──▶ standalone
T-DOC-006 (Concept→Code) ──▶ depends on T-DOC-001, T-DOC-002
T-DOC-007 (QUICKSTART) ──▶ standalone
T-DOC-008 (COMMANDS.md) ──▶ standalone
T-DOC-009 (Remove redundancy) ──▶ depends on T-DOC-004
```

---

## 5. EXECUTION ORDER

| Phase | Tasks | Rationale |
|-------|-------|-----------|
| **Phase 1** | T-DOC-010 | Unblock validation |
| **Phase 2** | T-DOC-001, T-DOC-002, T-DOC-005, T-DOC-008 | High confidence, no dependencies |
| **Phase 3** | T-DOC-004 (after validation) | Needs mirror working |
| **Phase 4** | T-DOC-003, T-DOC-006, T-DOC-007 | Medium priority refinements |
| **Phase 5** | T-DOC-009 | Final cleanup after dedup |

---

## 6. CONFIDENCE SUMMARY

| Confidence Level | Count | Tasks |
|------------------|-------|-------|
| **100%** | 1 | T-DOC-010 ✓ COMPLETE |
| **95%** | 2 | T-DOC-002, T-DOC-004 |
| **90%** | 3 | T-DOC-001, T-DOC-005, T-DOC-006 |
| **85%** | 2 | T-DOC-003, T-DOC-008 |
| **80%** | 2 | T-DOC-007, T-DOC-009 |

---

## 7. METRICS

### Before (Estimated)
- Total docs/ tokens: ~15,000
- Duplication: ~15%
- Structure ratio (tables:prose): 30:70
- Concept→Code bridges: ~40%

### Target After
- Total docs/ tokens: ~12,000 (-20%)
- Duplication: <5%
- Structure ratio: 60:40
- Concept→Code bridges: 100%

---

## 8. VALIDATION PROTOCOL

For each task:
1. **Before:** Count tokens, measure structure ratio
2. **After:** Re-count, verify improvement
3. **Test:** Query Gemini with modified doc, compare response quality

---

## 9. CONFIDENCE METHODOLOGY

### What Confidence Means

| Level | For Assumptions | For Tasks |
|-------|-----------------|-----------|
| **99-100%** | Verified by 2nd intentional read + AI forensic analysis with line citations | Aligns with all repo principles + code verified + AI alignment check |
| **90-98%** | AI validated with quotes but no line-level verification | Aligns with documented principles, grep-verified |
| **80-89%** | Local analysis only, awaiting external validation | Based on assumption, not yet code-verified |
| **70-79%** | Hypothesis based on pattern observation | Derived from unvalidated assumption |
| **<70%** | Speculation requiring validation | Should not be acted upon |

### Verification Layers

```
Layer 1: Code Read     → Did you read the actual file?
Layer 2: Grep Verify   → Did you search to confirm pattern exists?
Layer 3: AI Analysis   → Did external AI (Gemini) validate with citations?
Layer 4: Alignment     → Does this match repo principles (CLAUDE.md)?
```

### Validation Run: 2026-01-19

**Command Used:**
```bash
python context-management/tools/ai/analyze.py \
  --set theory --mode forensic --model gemini-2.5-pro --yes \
  "Validate assumptions A1-A8 with line citations"
```

**Results:**
| Assumption | Gemini Verdict | Confidence | Key Citation |
|------------|----------------|------------|--------------|
| A1 | VALIDATED | 95% | `[docs/THEORY_MAP.md:L15-L27]` Mermaid diagrams |
| A2 | VALIDATED | 95% | `[CLAUDE.md]` "The One Command" vs `[docs/UNIFIED_THEORY.md]` theory |
| A3 | VALIDATED | 90% | `[docs/UNIFIED_THEORY.md:L133]` "Mandelbrot of Code" flagged |
| A4 | VALIDATED | 95% | 4 Phases repeated in 3 files with citations |
| A5 | VALIDATED | 95% | `[docs/FOUNDATIONAL_THEORIES.md:L420-L450]` "FOR AI" section |
| A6 | VALIDATED | 95% | `[docs/ARCHITECTURE.md:L196-L203]` File Reference table |
| A7 | VALIDATED | 90% | `[docs/UNIFIED_THEORY.md:PART XIV]` defines "Graph", "Node" |
| A8 | VALIDATED | 95% | Same theorems (3.3-3.5) in FORMAL_PROOF and MECHANIZED_PROOFS |

**Token Cost:** 121,316 input, 2,000 output (~$0.15)

---

*This registry will be updated as tasks complete and assumptions are validated.*
