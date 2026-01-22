# Decision Record Template

> **Usage:** Copy this template for each promotion decision.
> **Location:** Save as `artifacts/atom-research/<date>/ai-audit/decision_finding_N.md`

---

```yaml
---
# ============================================================================
# DECISION RECORD: Finding [N]
# ============================================================================
# This record documents the promotion decision for a research finding.
# All fields in the YAML frontmatter are machine-readable for CI/tooling.
# ============================================================================

finding_id: F[N]
finding_summary: "[One-line summary of the finding]"
claim_level_from: L1
claim_level_to: L2
date_utc: YYYY-MM-DD

# Run configuration
deterministic_mode: true
corpus_version: [version number]
corpus_size: [number of repos]
collider_commit: "[SHA]"

# ============================================================================
# METRICS (from deterministic computation)
# ============================================================================
metrics:
  # Primary metrics (required)
  top4_mass_median: 0.00
  top4_mass_ci95_low: 0.00
  unknown_median: 0.00
  unknown_ci95_high: 0.00

  # Secondary metrics (if applicable)
  t2_enrichment_rate: 0.00
  n_repos_analyzed: 0
  total_nodes: 0

# ============================================================================
# HARD GATES (all must be true to promote)
# ============================================================================
hard_gates:
  G1_computation: false      # Deterministic metrics computed (Mode A)
  G2_thresholds: false       # Metrics satisfy claim's numeric bounds
  G3_falsification_clear: false  # No unresolved credible counterexample
  G4_artifacts_exist: false  # All audit artifacts saved
  G5_human_signoff: false    # Human owner recorded decision

# ============================================================================
# AI AUDIT ARTIFACTS
# ============================================================================
ai_audits:
  gemini: "artifacts/ai-audit/gemini_finding_[N].md"
  perplexity: "artifacts/ai-audit/perplexity_finding_[N].md"
  chatgpt: "artifacts/ai-audit/chatgpt_finding_[N].md"

# ============================================================================
# SOFT VOTES (advisory only - does not override hard gates)
# ============================================================================
soft_votes:
  gemini_supports: false
  perplexity_supports: false
  chatgpt_supports: false
  vote_summary: "[Summary of AI advisory input]"

# ============================================================================
# FALSIFICATION TRACKING
# ============================================================================
falsification:
  falsifier_found: false
  falsifier_description: "[Description of any falsifier found, or 'None']"
  falsifier_resolved: true
  resolution: "[How the falsifier was refuted, or 'N/A']"

# ============================================================================
# DECISION
# ============================================================================
decision:
  promote: false
  reason: "[If not promoting, explain why]"
  caveats: "[Any scope limitations or qualifications]"

# ============================================================================
# HUMAN SIGNOFF (required for G5)
# ============================================================================
human_signoff:
  owner: "[Name]"
  reviewer: "[Name or 'TBD']"
  date: YYYY-MM-DD
---
```

# Decision Narrative

## Summary

[One paragraph summarizing the decision and key factors.]

## Hard Gate Results

| Gate | Status | Evidence |
|------|--------|----------|
| G1: Computation | PASS/FAIL | [coverage.json exists, metrics computed via Mode A] |
| G2: Thresholds | PASS/FAIL | [Top-4 median X% vs threshold Y%, CI lower bound Z%] |
| G3: Falsification | PASS/FAIL | [No falsifier found / Falsifier refuted with evidence] |
| G4: Artifacts | PASS/FAIL | [All three AI audit files exist] |
| G5: Signoff | PASS/FAIL | [Human owner recorded] |

## Soft Votes

| AI System | Vote | Notes |
|-----------|------|-------|
| Gemini | Supports/Uncertain/Opposes | [Brief summary] |
| Perplexity | Supports/Uncertain/Opposes | [Brief summary] |
| ChatGPT | Supports/Uncertain/Opposes | [Brief summary] |

## Falsification Analysis

[If a falsifier was found, document:]
1. What the falsifier claimed
2. How it was investigated
3. Evidence that refutes it (or why it couldn't be refuted)

## Conclusion

[Final decision: Promote / Do Not Promote]

[If promoting, list any caveats or scope limitations.]

[If not promoting, explain what would need to change.]

---

## Checklist

Before finalizing this decision record:

- [ ] All YAML fields filled in
- [ ] All hard gates verified
- [ ] AI audit artifacts linked and exist
- [ ] Falsification section complete
- [ ] Human signoff recorded
- [ ] Narrative explains reasoning
