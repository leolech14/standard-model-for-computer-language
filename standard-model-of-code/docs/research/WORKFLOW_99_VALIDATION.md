# Workflow: 99-Repo Validation Campaign

> **Goal:** Promote H1-H5 from L2 (calibration) → L3 (stable theory)
> **Gate:** All hypotheses pass falsification tests on 99 repos

---

## Phase 0: PLAN (You Are Here)

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 0: PLAN                                              │
├─────────────────────────────────────────────────────────────┤
│  0.1 Define 99-repo corpus                                  │
│      └── Stratify: 6 langs × 15-18 repos each              │
│                                                             │
│  0.2 Validate plan with Gemini (analyze.py)                │
│      └── Score: corpus balance, coverage, hard cases       │
│                                                             │
│  0.3 Validate plan with Perplexity                         │
│      └── Research: similar studies, methodology gaps       │
│                                                             │
│  0.4 Revise based on feedback                              │
│                                                             │
│  0.5 GATE: Plan approved (score ≥8/10 both validators)     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

---

## Phase 1: PREPARE

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: PREPARE                                           │
├─────────────────────────────────────────────────────────────┤
│  1.1 Create corpus_99_validation.yaml                       │
│      └── Include 33 calibration repos + 66 new            │
│                                                             │
│  1.2 Pin all repos to SHA commits                          │
│      └── Reproducibility requirement                       │
│                                                             │
│  1.3 Validate YAML syntax and repo accessibility           │
│      └── Dry-run: check all URLs resolve                   │
│                                                             │
│  1.4 Estimate runtime                                       │
│      └── ~3-4 hours based on calibration timing            │
│                                                             │
│  1.5 GATE: Corpus ready (all repos accessible)             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

---

## Phase 2: EXECUTE

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: EXECUTE                                           │
├─────────────────────────────────────────────────────────────┤
│  2.1 Run corpus                                             │
│      └── python3 tools/research/run_corpus.py              │
│          artifacts/atom-research/corpus_99_validation.yaml │
│          --output artifacts/atom-research/2026-01-XX       │
│                                                             │
│  2.2 Monitor progress                                       │
│      └── Track: success/fail ratio, timeouts              │
│                                                             │
│  2.3 Handle failures                                        │
│      └── Retry failed repos, document unfixable           │
│                                                             │
│  2.4 GATE: ≥90% success rate (≥89/99 repos)                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

---

## Phase 3: ANALYZE

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: ANALYZE                                           │
├─────────────────────────────────────────────────────────────┤
│  3.1 Aggregate results                                      │
│      └── Compute: top-4 mass, unknown rate by stratum     │
│                                                             │
│  3.2 Test each hypothesis against falsification criteria   │
│      ┌─────────────────────────────────────────────────┐   │
│      │ H1: >10% repos top-4 <80%? → FALSIFIED          │   │
│      │ H2: LOG.FNC.M <40% dominant? → FALSIFIED        │   │
│      │ H3: Language variance >15pp? → FALSIFIED        │   │
│      │ H4: Any repo >10% unknown? → FALSIFIED          │   │
│      │ H5: Domain variance >10pp? → FALSIFIED          │   │
│      └─────────────────────────────────────────────────┘   │
│                                                             │
│  3.3 Identify new outliers and patterns                    │
│                                                             │
│  3.4 GATE: All H1-H5 pass falsification tests              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

---

## Phase 4: VALIDATE

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: VALIDATE                                          │
├─────────────────────────────────────────────────────────────┤
│  4.1 Validate results with Gemini (analyze.py)             │
│      └── Questions:                                        │
│          - Are the statistics sound?                       │
│          - Any methodological flaws?                       │
│          - Confidence in hypothesis promotion?             │
│      └── Required score: ≥8/10                            │
│                                                             │
│  4.2 Validate results with Perplexity                      │
│      └── Questions:                                        │
│          - How do results compare to literature?           │
│          - Any contradicting studies?                      │
│          - Publication-ready methodology?                  │
│      └── Required: No major contradictions                │
│                                                             │
│  4.3 Cross-validate: Gemini + Perplexity agree             │
│                                                             │
│  4.4 GATE: Both validators approve (≥8/10, no conflicts)  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

---

## Phase 5: PROMOTE

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: PROMOTE                                           │
├─────────────────────────────────────────────────────────────┤
│  5.1 Update HYPOTHESES_L2.md → HYPOTHESES_L3.md            │
│      └── Mark validated hypotheses as L3 (stable)         │
│                                                             │
│  5.2 Update MEASUREMENT_CONTRACT.md                        │
│      └── Add 99-repo evidence                             │
│                                                             │
│  5.3 Generate FINDINGS_REPORT.md                           │
│      └── Executive summary for documentation              │
│                                                             │
│  5.4 Seal audit pack                                       │
│      └── MANIFEST.sha256 for all artifacts                │
│                                                             │
│  5.5 GATE: All docs updated, manifest sealed               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
```

---

## Phase 6: COMMIT

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 6: COMMIT                                            │
├─────────────────────────────────────────────────────────────┤
│  6.1 Stage all artifacts                                    │
│      └── artifacts/atom-research/2026-01-XX/              │
│      └── docs/research/HYPOTHESES_L3.md                   │
│      └── docs/research/FINDINGS_REPORT.md                 │
│                                                             │
│  6.2 Commit with structured message                        │
│      └── feat(research): Promote H1-H5 to L3              │
│          - 99-repo validation complete                     │
│          - All falsification tests passed                  │
│          - Gemini: X/10, Perplexity: approved             │
│                                                             │
│  6.3 Push to remote                                        │
│                                                             │
│  6.4 GATE: CI passes, commit on main                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                         DONE
```

---

## Gate Summary

| Phase | Gate | Criteria |
|-------|------|----------|
| 0 | Plan approved | Gemini ≥8/10, Perplexity ≥8/10 |
| 1 | Corpus ready | All 99 repos accessible |
| 2 | Execution complete | ≥90% success rate |
| 3 | Analysis complete | All H1-H5 tested |
| 4 | Validation passed | Both validators ≥8/10 |
| 5 | Docs updated | Manifest sealed |
| 6 | Committed | CI green, on main |

---

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 0: Plan | 1 hr | 1 hr |
| Phase 1: Prepare | 30 min | 1.5 hr |
| Phase 2: Execute | 3-4 hr | 5 hr |
| Phase 3: Analyze | 30 min | 5.5 hr |
| Phase 4: Validate | 30 min | 6 hr |
| Phase 5: Promote | 30 min | 6.5 hr |
| Phase 6: Commit | 15 min | **~7 hr total** |

---

## Rollback Triggers

| Condition | Action |
|-----------|--------|
| Gemini score <6/10 | Revise plan, restart Phase 0 |
| >20% repo failures | Fix corpus, restart Phase 2 |
| Any hypothesis falsified | Document, do NOT promote to L3 |
| Validators disagree | Investigate, resolve before proceeding |

---

## Commands Quick Reference

```bash
# Phase 0: Validate plan
python3 context-management/tools/ai/analyze.py "Validate 99-repo corpus plan" --set research_validation

# Phase 2: Execute
python3 tools/research/run_corpus.py artifacts/atom-research/corpus_99_validation.yaml --output artifacts/atom-research/2026-01-XX

# Phase 3: Analyze
python3 tools/research/summarize_corpus.py artifacts/atom-research/2026-01-XX/results.json

# Phase 4: Validate
python3 context-management/tools/ai/analyze.py "Validate 99-repo results against hypotheses" --set research_validation

# Phase 5: Seal
python3 tools/research/validate_audit_pack.py artifacts/atom-research/2026-01-XX --seal

# Phase 6: Commit
git add artifacts/atom-research/ docs/research/
git commit -m "feat(research): Promote H1-H5 to L3 - 99-repo validation"
```
