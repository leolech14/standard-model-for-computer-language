# AI Orchestration Protocol for Phase 2 Research

> **Classification:** Research Methodology
> **Date:** 2026-01-22
> **Status:** ACTIVE
> **Prerequisite:** Phase 2 Protocol (ATOM_COVERAGE_PHASE2_PROTOCOL.md)

---

## Overview

This protocol defines how to coordinate three AI systems for maximum research rigor:

| System | Model | Strength | Research Role |
|--------|-------|----------|---------------|
| **Gemini** | gemini-2.5-pro | Long context (1M+), code understanding | Structural analysis, pattern detection |
| **Perplexity** | sonar-pro | Real-time web research, citations | Literature validation, external context |
| **ChatGPT** | o3 Extended Thinking | Deep reasoning, falsification | Hypothesis critique, audit review |

---

## Core Principle: Artifacts Are Authority

**AI systems advise; artifacts + metrics decide.**

Claims are promoted based on:
1. Deterministic metrics meeting thresholds
2. Evidence artifacts existing and being valid
3. No unresolved falsification

AI "agreement" is advisory input, not the decision authority.

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMOTION AUTHORITY                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   HARD GATES (must pass)         SOFT VOTES (advisory)      │
│   ─────────────────────          ────────────────────       │
│   ✓ Metrics meet thresholds      • AI interpretation        │
│   ✓ Artifacts exist              • Risk assessment          │
│   ✓ No unresolved falsifier      • Wording suggestions      │
│   ✓ Human signoff recorded       • Confidence estimates     │
│                                                             │
│   Metrics + Artifacts = Truth    AI = Advisor               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Hard Gates (Must Pass)

A claim CANNOT advance to L2 unless ALL hard gates pass:

| Gate | Requirement | Verification |
|------|-------------|--------------|
| **G1: Computation** | Deterministic metrics computed (Mode A) | `coverage.json` exists |
| **G2: Thresholds** | Metrics satisfy claim's numeric bounds | CI lower bound meets threshold |
| **G3: Falsification** | No unresolved credible counterexample | Falsifier either not found OR conclusively refuted |
| **G4: Artifacts** | All audit artifacts saved | `gemini_*.md`, `perplexity_*.md`, `chatgpt_*.md` exist |
| **G5: Signoff** | Human owner recorded decision | `decision_*.md` has `human_signoff` field |

### Veto Condition

**If ChatGPT (or any system) produces a credible falsification:**

1. The falsifier must be investigated
2. Evidence must conclusively refute it, OR
3. The claim stays at L1

**"Credible falsification"** means: a specific, testable counterexample that would disprove the claim if true.

```
Falsification found? ──► Can you refute with evidence? ──► Yes ──► Document refutation ──► Proceed
                                                      └─► No  ──► BLOCKED (stay at L1)
```

---

## Soft Votes (Advisory)

AI systems provide advisory input on:

| Input Type | AI Role | Authority |
|------------|---------|-----------|
| Interpretation of metrics | Gemini | Advisory |
| External literature context | Perplexity | Advisory |
| Risk assessment | ChatGPT | Advisory |
| Wording refinements | All | Advisory |
| Confidence estimates | All | Advisory |

**2/3 AI agreement** applies to:
- Whether the wording accurately reflects the data
- Whether the scope is appropriate
- Whether additional caveats are needed

**2/3 AI agreement does NOT**:
- Override failing hard gates
- Dismiss unresolved falsifications
- Substitute for missing artifacts

---

## System Roles and Scope Boundaries

### Gemini: Internal Structural Analysis

**Scope:** Code, metrics, pipeline behavior (internal to this repo)

**Use for:**
- Analyzing coverage metrics
- Validating evidence chains
- Spot-checking deterministic outputs
- Finding patterns in unified_analysis.json

**NOT for:** External validation, literature search

### Perplexity: External Context Only

**Scope:** Web research, literature, external benchmarks

**Use for:**
- Finding academic papers on Pareto distributions in code
- Industry reports on static analysis bias
- Standard methodologies for this type of research
- Analogies and framing support

**Scope Boundary:** Perplexity provides external context and literature support; it does NOT validate internal measurements. Never cite Perplexity as evidence for:
- Your internal metrics
- Your code path claims
- Your corpus results

### ChatGPT: Falsification and Critique

**Scope:** Adversarial reasoning, methodology critique

**Use for:**
- Finding flaws in claims
- Identifying unstated assumptions
- Designing falsification tests
- Peer review preparation

**NOT for:** Generating metrics, validating internal data

---

## Data Handling: Privacy Boundary

**RULE: Internal code must not be sent to external tools.**

| Data Type | Gemini (internal) | Perplexity (external) | ChatGPT (external) |
|-----------|-------------------|----------------------|-------------------|
| Metrics (numbers) | OK | OK (summarized) | OK (summarized) |
| File paths | OK | Redact if private | Redact if private |
| Code snippets | OK | NO (unless public repo) | NO (unless public repo) |
| Architecture descriptions | OK | OK (summarized) | OK (summarized) |
| Proprietary logic | OK | NO | NO |

**Safe pattern for external tools:**
```
Instead of: "This function at src/core/classifier.py:45 does X"
Use:        "The classifier maps AST nodes to atoms via pattern matching"
```

**Public repo data:** If analyzing open-source repos (fastapi, httpx, etc.), snippets are acceptable.

---

## Reproducibility: Required Metadata

Every AI audit artifact MUST include this capture block:

```yaml
---
audit_metadata:
  model: "gemini-2.5-pro"           # Exact model name
  model_version: "2026-01"          # If available
  prompt_hash: "sha256:abc123..."   # Hash of exact prompt used
  analysis_set: "research_full"     # Context set used
  repo_commit: "e1d121c"            # Repo state at time of analysis
  date_utc: "2026-01-22T14:30:00Z"  # ISO 8601
  tool_version: "analyze.py v1.0"   # Tool version if applicable
---
```

**Checklist for every audit:**
- [ ] Model version recorded
- [ ] Prompt recorded verbatim (or hash)
- [ ] Context set recorded
- [ ] Repo commit(s) recorded
- [ ] Date UTC recorded
- [ ] Artifact path recorded

---

## System Roles by Study

### Study A: Structural Generalization

| Task | Primary AI | Verification AI | Method |
|------|------------|-----------------|--------|
| Corpus stratification | Gemini | Perplexity | Validate repo categories against GitHub data |
| Top-4 mass computation | Deterministic code | Gemini | Spot-check 10% of runs |
| Variance explanation | Gemini | ChatGPT | Propose/falsify paradigm correlations |
| L2 promotion decision | ChatGPT | Gemini | Extended thinking critique |

### Study B: T2 Precision

| Task | Primary AI | Verification AI | Method |
|------|------------|-----------------|--------|
| Sample selection | Deterministic code | Gemini | Verify stratified sampling |
| Initial labeling | Human | Gemini | AI suggests, human decides |
| Error classification | Gemini | ChatGPT | Cross-validate error types |
| Precision calculation | Deterministic code | ChatGPT | Audit methodology |

### Study C: Functional Enrichment

| Task | Primary AI | Verification AI | Method |
|------|------------|-----------------|--------|
| Pattern mining | Gemini | Perplexity | Find official framework docs |
| Atom generation | Gemini | ChatGPT | Critique pattern precision |
| Negative examples | ChatGPT | Gemini | Adversarial case generation |
| Quality gate | Human + ChatGPT | Gemini | Triple review |

---

## Workflow: Claim Promotion

### Step 1: Generate Finding (Deterministic)

1. Run Mode A analysis: `./collider full <repo> --output <dir>`
2. Compute metrics: `python tools/research/atom_coverage.py`
3. Check thresholds against claim requirements
4. Document in evidence ledger

**Hard Gate G1 + G2 checkpoint:** Metrics must meet thresholds before proceeding.

### Step 2: Gemini Analysis

```bash
.tools_venv/bin/python context-management/tools/ai/analyze.py \
  "Review Finding [N]: [summary]. Validate the evidence chain. Identify any gaps." \
  --set research_validation \
  --mode forensic
```

Save to: `artifacts/ai-audit/gemini_finding_N.md`

Include metadata capture block at top.

### Step 3: Perplexity External Context

Query for external validation:
- Similar research methodologies
- Industry benchmarks
- Literature support (NOT internal validation)

Save to: `artifacts/ai-audit/perplexity_finding_N.md`

**Remember:** Perplexity provides context, not evidence for internal claims.

### Step 4: ChatGPT Falsification

Use Extended Thinking with adversarial prompt.

**CRITICAL:** If ChatGPT produces a credible falsifier:
1. Investigate immediately
2. Either refute with evidence OR stay at L1

Save to: `artifacts/ai-audit/chatgpt_finding_N.md`

**Hard Gate G3 checkpoint:** No unresolved falsification.

### Step 5: Decision Record

Create `artifacts/ai-audit/decision_finding_N.md` using the template.

**Hard Gate G4 + G5 checkpoint:** All artifacts exist, human signoff recorded.

---

## Decision Record Template

Use `docs/research/DECISION_TEMPLATE.md` for all promotion decisions.

```yaml
---
finding_id: F1
claim_level_from: L1
claim_level_to: L2
date_utc: 2026-01-22
deterministic_mode: true
corpus_version: 1
corpus_size: 100

metrics:
  top4_mass_median: 0.84
  top4_mass_ci95_low: 0.81
  unknown_median: 0.03
  unknown_ci95_high: 0.05

hard_gates:
  G1_computation: true
  G2_thresholds: true
  G3_falsification_clear: true
  G4_artifacts_exist: true
  G5_human_signoff: true

ai_audits:
  gemini: artifacts/ai-audit/gemini_finding_1.md
  perplexity: artifacts/ai-audit/perplexity_finding_1.md
  chatgpt: artifacts/ai-audit/chatgpt_finding_1.md

soft_votes:
  gemini_supports: true
  perplexity_supports: true
  chatgpt_supports: false
  vote_summary: "2/3 support, ChatGPT raised scope concern (addressed in caveats)"

falsification:
  falsifier_found: true
  falsifier_description: "Claim may not hold for generated code repos"
  falsifier_resolved: true
  resolution: "Added caveat: excludes repos >50% generated code"

decision:
  promote: true
  caveats: "Excludes generated-code-heavy repos"

human_signoff:
  owner: "Leonardo Lech"
  reviewer: "TBD"
  date: 2026-01-22
---

# Decision Narrative

## Summary
Finding 1 meets all hard gates for L2 promotion.

## Hard Gate Results
- G1: Metrics computed via Mode A on 100-repo corpus
- G2: Top-4 median (84%) exceeds threshold (70%), CI lower bound (81%) exceeds threshold (65%)
- G3: Falsification regarding generated code resolved by adding scope caveat
- G4: All three AI audit artifacts exist
- G5: Human signoff recorded

## Soft Votes
- Gemini: Supports, notes strong statistical foundation
- Perplexity: Supports, found similar Pareto findings in literature
- ChatGPT: Raised concern about generated code repos; resolved via caveat

## Conclusion
Promote Finding 1 to L2 with caveat: "Excludes repos with >50% generated code"
```

---

## Prompt Templates

### Gemini: Structural Analysis

**Use when:** Analyzing code patterns, coverage metrics, pipeline behavior

```
CONTEXT: Phase 2 Atom Coverage Research
SET: research_full
REPO_COMMIT: [current SHA]

TASK: [specific analysis task]

REQUIREMENTS:
1. Cite specific file paths and line numbers
2. Provide quantitative metrics where possible
3. Flag any data quality issues
4. Distinguish between observation and interpretation

OUTPUT FORMAT:
## Observation
[What the data shows]

## Interpretation
[What this means for the hypothesis]

## Confidence
[0-100% with justification]

## Limitations
[What this analysis cannot tell us]
```

**Command:**
```bash
.tools_venv/bin/python context-management/tools/ai/analyze.py \
  "[TASK]" \
  --set research_full \
  --mode forensic
```

### Perplexity: External Context

**Use when:** Finding literature, external benchmarks, methodology standards

**Scope reminder:** External context only, not internal validation.

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a research context provider. Find external evidence, literature, and benchmarks. Always cite sources with URLs. You are providing CONTEXT, not validating internal measurements."
    },
    {
      "role": "user",
      "content": "CONTEXT NEEDED FOR: [claim summary]\n\nTasks:\n1. Find academic papers on this topic\n2. Find industry reports with similar findings\n3. Identify standard methodologies\n4. Note if the claim pattern is novel or established\n\nProvide URLs for all citations."
    }
  ]
}
```

**MCP Tool:**
```
mcp__perplexity__perplexity_research
```

### ChatGPT: Falsification Audit

**Use when:** Critiquing methodology, finding edge cases, preparing for peer review

```
ROLE: Adversarial Research Auditor

CONTEXT:
- Project: Standard Model of Code / Collider
- Phase: Phase 2 Atom Coverage Research
- Goal: Find flaws before L2 promotion

FINDING:
[paste finding with evidence - summarized, no proprietary code]

AUDIT TASKS:
1. ASSUMPTIONS: List all implicit assumptions. Which are testable?
2. METHODOLOGY: What could bias these results?
3. STATISTICS: Are the sample sizes adequate? Is the analysis appropriate?
4. REPRODUCIBILITY: What would prevent another team from replicating?
5. SCOPE: What does this finding NOT tell us?
6. FALSIFICATION: Design 3 specific tests that would disprove this claim
7. VERDICT: Would this survive peer review? (Yes/Probably/Unlikely/No)

Be direct. If you find a credible falsifier, describe it clearly.
```

---

## Artifact Layout

```
artifacts/
├── atom-research/
│   └── 2026-01-22/
│       ├── corpus.yaml
│       ├── summary.csv
│       ├── summary.md
│       ├── results.json
│       ├── repos/
│       │   └── ...
│       └── ai-audit/
│           ├── gemini_finding_1.md
│           ├── perplexity_finding_1.md
│           ├── chatgpt_finding_1.md
│           ├── decision_finding_1.md
│           ├── gemini_finding_2.md
│           ├── ...
│           └── ensemble_summary.md
```

---

## Anti-Patterns

### DO NOT:

1. **Promote on AI agreement alone** - Hard gates must pass first
2. **Ignore falsification** - Unresolved falsifier blocks promotion
3. **Send proprietary code externally** - Use summaries for Perplexity/ChatGPT
4. **Skip metadata capture** - Every audit needs the capture block
5. **Trust Perplexity for internal validation** - It provides context, not evidence
6. **Override hard gates with soft votes** - 3/3 AI agreement cannot fix failing metrics

### DO:

1. **Check hard gates first** - Before any AI review
2. **Document all AI outputs** - Full transcripts with metadata
3. **Investigate every falsifier** - Even if you think it's wrong
4. **Use forensic mode for Gemini** - Require line-level citations
5. **Record human signoff** - Every decision has an owner
6. **Separate observation from interpretation** - In all AI outputs

---

## Quick Reference

### Hard Gates Checklist
```
[ ] G1: Deterministic computation complete
[ ] G2: Metrics meet thresholds
[ ] G3: No unresolved falsification
[ ] G4: All audit artifacts saved
[ ] G5: Human signoff recorded
```

### Analyze Coverage (Gemini)
```bash
.tools_venv/bin/python context-management/tools/ai/analyze.py \
  "[query]" --set research_full --mode forensic
```

### External Context (Perplexity)
```
Use MCP: mcp__perplexity__perplexity_research
Scope: External literature and benchmarks ONLY
```

### Falsification Audit (ChatGPT)
```
Use Extended Thinking with adversarial prompt
If falsifier found: investigate before proceeding
```

### Decision Record
```
Use DECISION_TEMPLATE.md
All 5 hard gates must be true to promote
```

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial protocol | Claude Opus 4.5 |
| 2026-01-22 | Hardening: hard gates vs soft votes, veto condition, privacy boundary, reproducibility metadata, Perplexity scope | Claude Opus 4.5 |
