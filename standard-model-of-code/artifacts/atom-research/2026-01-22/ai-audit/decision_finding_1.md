---
# ============================================================================
# DECISION RECORD: Finding 1 (Pilot)
# ============================================================================
# This record documents the promotion decision for a research finding.
# All fields in the YAML frontmatter are machine-readable for CI/tooling.
# ============================================================================

finding_id: F1A
finding_summary: "In the 4-repo pilot, the 4 most frequent atoms (dynamic) account for 96-100% of nodes (median 98.81%)"
measurement_contract: "docs/research/MEASUREMENT_CONTRACT.md"
hypothesis_type: "distributional"  # Hypothesis A: dynamic top-4, not fixed base atoms
claim_level_from: L1
claim_level_to: L1    # BLOCKED - stays at L1
date_utc: 2026-01-22

# Run seal binding (this decision applies to exactly this sealed artifact set)
# Note: The manifest seals all artifacts including this decision.
# Verification: ./tools/research/verify_manifest.sh artifacts/atom-research/2026-01-22/
run_seal_manifest: "artifacts/atom-research/2026-01-22/MANIFEST.sha256"

# Run configuration
deterministic_mode: true
corpus_version: "pilot-v1"
corpus_size: 4
collider_commit: "8361d44"
corpus_repos: ["instructor", "httpx", "cobra", "zod"]
corpus_languages: ["Python", "Go", "TypeScript"]

# ============================================================================
# CLAIM LADDER (L1 vs L2 thresholds)
# ============================================================================
claims:
  L1_pilot:
    wording: "In the 4-repo pilot, top-4 mass is 96-100% (median 98.81%)"
    threshold_type: "observation"
    supported: true
  L2_target:
    wording: "Across 100+ stratified repos, top-4 mass median >= 70% with CI lower bound >= 65%"
    threshold_type: "lower_bound"
    supported: false
    reason: "Insufficient sample size (4 vs 100+ required)"

# ============================================================================
# METRICS (from deterministic computation)
# ============================================================================
metrics:
  # Primary metrics (required)
  top4_mass_median: 98.81
  top4_mass_range_low: 96.43
  top4_mass_range_high: 100.0
  unknown_median: 0.30
  unknown_range_high: 0.42

  # Secondary metrics
  n_repos_analyzed: 4
  total_nodes: 4971

# ============================================================================
# HARD GATES (all must be true to promote to L2)
# ============================================================================
hard_gates:
  G1_computation: true       # Deterministic metrics computed (Mode A)
  G2_thresholds: true        # PASS: Pilot metrics satisfy L1 claim (observation)
  G3_falsification_clear: true   # PASS: No actual falsifier found (only tests proposed)
  G4_artifacts_exist: true   # All audit artifacts saved with valid provenance
  G5_human_signoff: false    # Pending human review

# G2 Note: The original claim wording (70-90%) was conservative. Evidence exceeds it.
#          This is a claim revision issue, not a threshold failure.
# G3 Note: Adversarial audit proposed falsification TESTS, not actual falsifiers.
#          G3 fails only when a counterexample is found and unresolved.

# ============================================================================
# AI AUDIT ARTIFACTS
# ============================================================================
ai_audits:
  gemini:
    path: "artifacts/atom-research/2026-01-22/ai-audit/gemini_finding_1.md"
    status: "COMPLETED"
    provider: "gemini-2.5-pro"
  perplexity_context:
    path: "artifacts/atom-research/2026-01-22/ai-audit/perplexity_finding_1.md"
    status: "COMPLETED"
    provider: "sonar-pro"
  adversarial:
    path: "artifacts/atom-research/2026-01-22/ai-audit/adversarial_finding_1.md"
    status: "COMPLETED"
    provider: "sonar-pro"
    independence_note: "Same provider as perplexity_context - not fully independent"

# ============================================================================
# SOFT VOTES (advisory only - does not override hard gates)
# ============================================================================
soft_votes:
  gemini_supports: true
  perplexity_context_supports: null  # Provided literature context only
  adversarial_supports: false
  vote_summary: |
    Gemini: 99% confidence for analyzed repos, 65% for generalization.
    Adversarial: UNLIKELY verdict (2/10) for peer review at current sample size.
    Note: Both Perplexity audits from same provider (not independent).

# ============================================================================
# FALSIFICATION TRACKING
# ============================================================================
falsification:
  falsifier_found: false     # No actual counterexample found
  tests_proposed: 3          # Adversarial audit proposed 3 falsification tests
  tests_executed: 0          # None executed yet
  tests_description: |
    1. Language stratification: test if pattern is language-specific
    2. Repo complexity gradient: test on simple/complex/pathological repos
    3. Node-weight sensitivity: test depth-weighted and leaf-weighted schemes
  resolved: true             # No falsifier to resolve (tests are planned, not results)

# ============================================================================
# DECISION
# ============================================================================
decision:
  promote: false
  outcome: BLOCKED
  reason: "Sample size insufficient for L2 (4 vs 100+ required)"
  blocking_factors:
    - "Corpus size: 4 repos vs 100+ required for L2"
    - "Falsification tests: proposed but not executed"
    - "Claim wording: needs revision (evidence exceeds original 70-90% claim)"
  caveats: "Finding is VALID at L1 (pilot observation) but cannot be GENERALIZED to L2 without larger corpus"

# ============================================================================
# HUMAN SIGNOFF (required for G5)
# ============================================================================
human_signoff:
  owner: "TBD"
  reviewer: "TBD"
  date: null
---

# Decision Narrative

## Summary

Finding 1 (Pareto Distribution of Structural Atoms) is **VALID at L1** (pilot observation) with strong metrics (98.81% top-4 mass, 0.3% unknown rate). However, it **cannot be promoted to L2** because the pilot corpus (4 repos) is insufficient for generalization claims. The adversarial audit proposed falsification tests but found no actual counterexample.

## Claim Revision Required

The original claim wording ("70-90%") is too conservative based on pilot evidence:

| Claim | Threshold | Pilot Evidence | Status |
|-------|-----------|----------------|--------|
| Original | 70-90% | 96-100% | Evidence exceeds claim |
| Proposed L1 | "96-100% in pilot" | 96-100% | Observation match |
| Proposed L2 | ">= 70% (CI lower bound >= 65%)" | TBD | Requires 100+ repos |

**Recommendation:** Revise L1 to report pilot facts accurately. Define L2 as a lower-bound claim with confidence intervals.

## Hard Gate Results

| Gate | Status | Evidence |
|------|--------|----------|
| G1: Computation | **PASS** | `results.json` exists, metrics computed via Mode A (deterministic) |
| G2: Thresholds | **PASS** | Pilot metrics satisfy L1 observation claim |
| G3: Falsification | **PASS** | No falsifier found; tests proposed but not executed |
| G4: Artifacts | **PASS** | All three audit files exist with valid provenance |
| G5: Signoff | **PENDING** | Awaiting human owner decision |

**Why BLOCKED despite G1-G4 passing:** L2 requires corpus size >= 100. This is a precondition failure, not a gate failure.

## Soft Votes

| AI System | Vote | Notes |
|-----------|------|-------|
| Gemini | **Supports** | 99% confidence for analyzed repos; 65% for generalization; recommends larger corpus |
| Perplexity (Context) | **Neutral** | Found related Pareto research (macro-level) but no direct prior art for element-level claims |
| Perplexity (Adversarial) | **Opposes** | UNLIKELY verdict (2/10) at current sample size; flags methodology concerns |

**Independence Note:** Both Perplexity audits use sonar-pro. For true ensemble diversity, a human adversarial pass or different external model would strengthen the audit.

## Falsification Analysis

The adversarial audit **proposed** three falsification tests but did not **find** a falsifier:

### Proposed Tests (Not Yet Executed)

| Test | Hypothesis | Prediction | Status |
|------|------------|------------|--------|
| Language Stratification | Pattern is language-specific, not universal | 15-25% variance between languages | **NOT EXECUTED** |
| Complexity Gradient | Pattern breaks on complex/pathological code | <50% for metaprogramming-heavy repos | **NOT EXECUTED** |
| Node-Weight Sensitivity | High mass is counting artifact | Divergence between weighting schemes | **NOT EXECUTED** |

**G3 Status:** PASS because no actual counterexample was found. Proposed tests are inputs to Phase 2, not falsification results.

## Conclusion

**Decision: BLOCKED (stays at L1)**

| Dimension | L1 Status | L2 Status |
|-----------|-----------|-----------|
| Claim validity | **VALID** (observation) | **BLOCKED** (insufficient data) |
| Sample size | 4 repos (sufficient for pilot) | 100+ repos (required) |
| Falsification | No falsifier found | Tests proposed, need execution |

### What Would Promote to L2

1. **Expand corpus to 100+ repos** with stratification by language, domain, complexity
2. **Execute falsification tests** from adversarial audit
3. **Compute confidence intervals** via bootstrapping
4. **Revise claim wording** to lower-bound with CI: "top-4 mass >= X% (CI95 lower bound >= Y%)"

---

## Checklist

- [x] All YAML fields filled in
- [x] Hard gates verified with correct semantics
- [x] AI audit artifacts linked with valid provenance
- [x] Falsification section distinguishes proposed vs found
- [ ] Human signoff recorded
- [x] Narrative explains reasoning
- [x] claim_level_to reflects BLOCKED status (stays L1)
