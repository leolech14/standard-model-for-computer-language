# Measurement Contract v1.0

> **Purpose:** Define exactly what is being measured so claims are stable and reproducible.
> **Status:** DRAFT - Requires human approval before L2 corpus run.
> **Version:** 1.0.0
> **Date:** 2026-01-22

---

## Q1: What Hypothesis Are We Testing?

### Answer: DYNAMIC TOP-4 (Hypothesis A)

**The claim is distributional/Zipfian, not ontological.**

| Hypothesis | Description | What We're Testing |
|------------|-------------|-------------------|
| **A (Dynamic)** | "The 4 most frequent atoms (whatever they are) cover >= X%" | **YES** |
| B (Fixed) | "These specific 4 atoms (LOG.FNC.M, etc.) are universal" | No (separate study) |

**Implementation Evidence:**

```python
# atom_coverage.py:113-116
def topk_mass(k: int) -> float:
    top_k_count = sum(count for _, count in sorted_atoms[:k])  # sorted by frequency
    return round(top_k_count / n_nodes * 100, 2)
```

The `top_4_mass` metric is the sum of the 4 most frequent atoms **per repo**, regardless of which atoms they are.

**Implication:** Our claim is about concentration/Pareto distribution, not about specific atoms being universal primitives.

### Future Study (F1B)

A separate finding (F1B) could test whether the **same 4 atoms** dominate across repos:
- Track which atoms are in the top-4 per repo
- Measure overlap/consistency
- Claim: "The same 4 atoms appear in the top-4 in >= Y% of repos"

This is NOT part of F1A (current study).

---

## Q2: What Is a "Node"?

### Answer: Collider Structural Node

A "node" is a **Collider output entity**, not a raw AST node.

| Property | Definition |
|----------|------------|
| Source | Collider `unified_analysis.json` → `nodes[]` array |
| Granularity | One node per structural entity (function, class, variable, module) |
| NOT included | Raw AST tokens (identifiers, literals, operators) |
| NOT included | Whitespace, comments, formatting |

**Node Schema (relevant fields):**

```json
{
  "id": "UserService.validate",
  "atom": "LOG.FNC.M",
  "file_path": "src/services/user.py",
  "start_line": 45,
  "end_line": 67
}
```

**What counts as a node:**
- Functions/methods → `LOG.FNC.M`
- Classes/aggregates → `ORG.AGG.M`
- Variables/attributes → `DAT.VAR.A`
- Modules/files → `ORG.MOD.O`
- Other recognized patterns → their respective atoms
- Unrecognized patterns → `Unknown`

**What does NOT count:**
- Individual AST tokens (tree-sitter produces these, Collider aggregates them)
- Import statements (unless classified as a pattern)
- Type annotations (inline)
- Decorators (rolled into the decorated entity)

### Versioning

Node extraction rules are tied to Collider version. Changes to `full_analysis.py` or `atom_classifier.py` can change node counts.

**Invariant:** For any given Collider commit, the same input repo produces the same node count.

---

## Q3: Scope Rules - What Code Is Included?

### Answer: Default Collider Scope with Documented Exclusions

| Category | Included? | Notes |
|----------|-----------|-------|
| Source code (`.py`, `.ts`, `.go`, etc.) | YES | Primary measurement target |
| Test directories (`tests/`, `test/`, `*_test.py`) | YES | But can be stratified |
| Documentation (`docs/`, `*.md`) | NO | Not parsed |
| Generated code (`dist/`, `build/`, `.next/`) | **EXCLUDE** | Must be filtered |
| Vendored dependencies (`vendor/`, `node_modules/`) | **EXCLUDE** | Must be filtered |
| Configuration (`.json`, `.yaml`, `.toml`) | NO | Not parsed as code |
| Minified/transpiled | **EXCLUDE** | Not representative |

### Exclusion Patterns (Collider Default)

```
node_modules/
vendor/
dist/
build/
.next/
__pycache__/
*.min.js
*.bundle.js
```

### Scope Tags for Corpus Entries

Each repo in the corpus MUST be tagged:

```yaml
repos:
  - name: "httpx"
    url: "https://github.com/encode/httpx"
    scope_tags:
      - "library"
      - "no_generated_code"
      - "has_tests"
    exclusions_applied: ["__pycache__/", "dist/"]
```

### Generated Code Handling

**Policy:** Repos with >20% generated code are flagged and analyzed separately.

**Detection heuristic:**
- Files matching `*.generated.*`, `*.g.*`, `*_pb2.py`
- Directories: `generated/`, `proto/`, `codegen/`

**Metric to track:** `generated_code_ratio` (even if estimated)

---

## Q4: Unit of Inference

### Answer: REPO-LEVEL Distribution

| Approach | Description | Our Choice |
|----------|-------------|------------|
| **Repo-level** | Each repo yields one `top_4_mass` → report median + CI over repos | **YES** |
| Corpus-level | Merge all nodes, compute one value (overweights large repos) | No |

**Why repo-level:**
- Each repo is an independent sample
- Avoids large repos dominating the distribution
- Enables meaningful confidence intervals
- Standard practice in empirical software engineering

**Metrics reported:**
- `top_4_mass_median`: Median across repos
- `top_4_mass_ci95_low`: 95% CI lower bound (bootstrap or percentile)
- `top_4_mass_ci95_high`: 95% CI upper bound
- `top_4_mass_min`: Minimum observed
- `top_4_mass_max`: Maximum observed

---

## Q5: Falsifier Definition

### Answer: Explicit Thresholds

A **falsifier** is an observed result that blocks L2 promotion.

| Falsifier Type | Threshold | Blocks L2? |
|----------------|-----------|------------|
| **Single repo collapse** | Any in-scope repo with `top_4_mass < 50%` | YES |
| **Stratum failure** | >10% of repos in any language stratum have `top_4_mass < 60%` | YES |
| **Language divergence** | Language means differ by >25 percentage points | YES (universality claim) |
| **Weighting sensitivity** | Weighted vs unweighted differ by >20 points | INVESTIGATE (not auto-block) |

### Proposed Tests (From Adversarial Audit)

| Test | Hypothesis to Disprove | Falsifier Criterion |
|------|------------------------|---------------------|
| Language Stratification | Pattern is universal across languages | Language means differ by >25pp |
| Complexity Gradient | Pattern holds for all complexity levels | Any "complex" repo <50% |
| Weighting Sensitivity | Metric is robust to counting method | Weighted vs unweighted >20pp divergence |

### Falsifier vs Proposed Test

| Term | Definition |
|------|------------|
| **Proposed test** | A test designed to stress the claim |
| **Executed test** | A test that has been run with recorded outcome |
| **Falsifier found** | An executed test produced a result meeting falsifier criteria |
| **Falsifier resolved** | The falsifier was explained (scope violation, bug, etc.) or the claim was revised |

**G3 (Falsification Clear) fails ONLY when:**
- A falsifier is found AND
- It is not resolved

Proposed tests do not fail G3. They are inputs to Phase 2.

---

## Q6: Independence Requirement

### Answer: Documented, Not Enforced

| Rule | Description |
|------|-------------|
| **Minimum** | At least 2 AI audits from different models |
| **Ideal** | Audits from different providers (Gemini + Perplexity + human) |
| **Required documentation** | Each audit must declare its provider and note independence status |

**Current state (F1 pilot):**
- Gemini (gemini-2.5-pro) - internal forensic
- Perplexity (sonar-pro) - external context
- Perplexity (sonar-pro) - adversarial

**Independence note:** Perplexity used for both context and adversarial. Documented but not ideal.

**Recommendation for L2:** Add human adversarial pass or different external model.

---

## Q7: Drift Control

### Answer: Frozen Corpus + Regression Budget

| Control | Definition |
|---------|------------|
| **Frozen corpus** | A fixed set of repos used for regression testing |
| **Metrics drift budget** | Maximum allowed change in key metrics after classifier changes |
| **Regression gate** | Block release if metrics drift exceeds budget |

### Drift Budget (Proposed)

| Metric | Max Drift | Action if Exceeded |
|--------|-----------|-------------------|
| `top_4_mass_median` | +/- 5pp | Investigate |
| `unknown_rate_median` | +3pp | Block release |
| `n_nodes` (per repo) | +/- 20% | Investigate extraction changes |

### Frozen Corpus

The pilot repos (instructor, httpx, cobra, zod) become the initial frozen corpus.

After L2 promotion, select 20 representative repos as the long-term regression set.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-22 | Initial draft |

---

## Approval

- [ ] Human owner reviewed
- [ ] Decision: APPROVED / NEEDS REVISION
- [ ] Date: ____

---

*This contract governs all F1 measurements. Changes require version bump and re-approval.*
