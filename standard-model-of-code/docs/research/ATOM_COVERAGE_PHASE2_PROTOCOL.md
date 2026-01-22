# Atom Coverage Research: Phase 2 Protocol

> **Classification:** Research Protocol
> **Date:** 2026-01-22
> **Status:** DRAFT (pending execution)
> **Prerequisite:** Phase 1 hardened investigation (commit `ef487fb`)

---

## Overview

Phase 1 established causal findings with 93-97% confidence on a 7-repo corpus. Phase 2 generalizes these findings across a stratified corpus, measures T2 quality (precision), and closes the security-skew gap with functional enrichment.

### Goals

| ID | Goal | Success Metric |
|----|------|----------------|
| G1 | Generalization | Pareto claim holds across 100+ stratified repos |
| G2 | T2 Quality | Precision measured per ecosystem (target: >85%) |
| G3 | Functional Enrichment | Security/functional ratio improves from 77/23 to 55/45 |

---

## Claims Ladder

Claims upgrade only when evidence supports them:

| Level | Status | Evidence Required | Current Claims |
|-------|--------|-------------------|----------------|
| L0 | Observed in 1 repo | Single run | - |
| L1 | **CURRENT** | 7 repos, causal chains | Pareto distribution (93-97%) |
| L2 | Pending | 100+ stratified repos, CI | - |
| L3 | Future | Stable across versions, regression gates | - |

**Rule:** Never upgrade claims without meeting evidence requirements.

---

## Standard Run Configuration

> **All metrics in Phase 2 claims are computed from deterministic baseline runs.**

### Mode A: Deterministic Baseline (for all stats/claims)

```bash
./collider full <repo> --output <dir>
# NO additional flags
```

| Setting | Value | Rationale |
|---------|-------|-----------|
| LLM enrichment | OFF | Non-deterministic |
| AI insights | OFF | Non-deterministic |
| `--ai-insights` flag | NOT USED | Would add Gemini variation |
| Ignore patterns | Standard (vendor, node_modules, build) | Consistency |

### Mode B: Augmented (for product storytelling only)

```bash
./collider full <repo> --output <dir> --ai-insights
```

Used for marketing/demos but **never for research claims**.

### Metric Consistency Note

Phase 1 reported `Unknown: 8.3%` for self-repo (commit `ef487fb`).
Recent run showed `Unknown: 0%` due to:
1. Improved atom mappings between commits
2. Different analysis file version

**Rule:** All Phase 2 metrics must reference:
- Collider commit SHA
- Analysis file path
- Run timestamp

This prevents "tool changed mid-study" criticism.

---

## Study A: Structural Atom Generalization

### Hypotheses

| ID | Hypothesis | Falsification Condition |
|----|------------|-------------------------|
| H1 | Top-4 structural atoms account for 70-90% of nodes (median) | Median top-4 mass < 60% |
| H2 | Unknown rate is reducible without harming other metrics | Unknown rate cannot drop below 10% |
| H3 | Variance is driven by paradigm (OO vs functional, generated code) | No correlation found |

### Corpus Design

**Stratification Matrix:**

| Dimension | Strata | Minimum per Cell |
|-----------|--------|------------------|
| Language | Python, JS, TS, Go, Rust, Java | 5 repos |
| Domain | web-backend, web-frontend, CLI, library, ML, systems | 3 repos |
| Size | small (<2k LOC), medium (2k-50k), large (>50k) | 3 repos |

**Total minimum:** 6 languages × 6 domains × 3 sizes × 3-5 repos = 100-150 repos

**Hard cases (intentionally included):**
- Monorepos (multi-language)
- Generated code-heavy (protobuf, OpenAPI)
- Config-heavy (Terraform, Kubernetes YAML)
- DSL-heavy (SQL embedded, Jinja templates)

### Sampling Rules

1. **Random within stratum:** Use GitHub API to sample by language + stars
2. **Exclude forks:** Only original repos
3. **Minimum activity:** At least 1 commit in last 12 months
4. **Exclude duplicates:** No repos from same org that share code

### Metrics Schema

```yaml
# Per-repo metrics (stored in coverage.json)
repo_metrics:
  repo_url: string
  repo_commit_sha: string
  collider_commit_sha: string
  timestamp_utc: string

  # Structural metrics
  n_nodes: int
  top_1_mass: float  # % of nodes with most common atom
  top_2_mass: float
  top_4_mass: float
  unknown_rate: float  # % of nodes with Unknown atom

  # Base atom distribution
  atom_distribution:
    LOG.FNC.M: int
    ORG.AGG.M: int
    DAT.VAR.A: int
    ORG.MOD.O: int
    Unknown: int
    other: int

  # Optional advanced
  entropy: float  # Shannon entropy of distribution
  gini: float     # Gini coefficient (inequality)

  # T2 metrics
  t2_enrichment_rate: float
  ecosystems_detected: list[string]
```

### Run Metadata

Every run must produce `run_metadata.json`:

```json
{
  "repo_url": "https://github.com/org/repo",
  "repo_commit_sha": "abc123...",
  "collider_commit_sha": "ef487fb...",
  "cli_args": ["full", ".", "--output", ".collider"],
  "timestamp_utc": "2026-01-22T10:30:00Z",
  "language_mix": {"python": 0.8, "yaml": 0.15, "other": 0.05},
  "file_count": 234,
  "loc_estimate": 15000
}
```

### Promotion Criteria (L1 → L2)

| Criterion | Threshold |
|-----------|-----------|
| Corpus size | ≥ 100 repos |
| Stratification | All cells filled |
| Median top-4 mass | ≥ 70% with 95% CI lower bound ≥ 65% |
| Median Unknown rate | ≤ 10% (or explained by paradigm) |
| Reproducibility | Re-run on same corpus yields same results |

---

## Study B: T2 Quality (Precision)

### Hypotheses

| ID | Hypothesis | Falsification Condition |
|----|------------|-------------------------|
| H4 | T2 precision varies dramatically by ecosystem | Variance < 10% across ecosystems |
| H5 | Precision improves with pattern tightening | No improvement after refactoring |

### Sampling

For each major ecosystem (start with top 10 by atom count):

| Ecosystem | Sample Size | Stratification |
|-----------|-------------|----------------|
| Django | 200 nodes | models, views, routes, other |
| React | 200 nodes | components, hooks, effects, other |
| Flask | 150 nodes | routes, templates, config, other |
| Vue | 150 nodes | components, directives, other |
| Express | 150 nodes | routes, middleware, other |
| ... | ... | ... |

### Labeling Protocol

For each sampled node:

```yaml
sample_label:
  node_id: string
  repo: string
  t2_atom: string

  # Human judgment
  verdict: correct | incorrect | ambiguous

  # If incorrect, classify error type
  error_type:
    - broad_regex      # Pattern too permissive
    - wrong_ecosystem  # Triggered by wrong import
    - mis_parsed       # Node span incorrect
    - semantic_confusion  # Wrong atom chosen from similar options
    - other

  notes: string
  labeler: string
  timestamp: string
```

### Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Precision (per ecosystem) | correct / (correct + incorrect) | ≥ 85% |
| Weighted precision | Σ(precision_i × weight_i) | ≥ 85% |
| Ambiguity rate | ambiguous / total | ≤ 10% |
| Top offenders | Atoms with highest FP count | Prioritize for fix |

### Promotion Criteria

| Criterion | Threshold |
|-----------|-----------|
| Ecosystems measured | ≥ 10 |
| Samples per ecosystem | ≥ 100 |
| Overall precision | ≥ 85% |
| No ecosystem below | 70% precision |

---

## Study C: Functional Enrichment Program

### Problem Statement

Current T2 inventory: 77% security, 23% functional.
Target: 55% security, 45% functional (balanced).

### Architectural Primitives to Capture

| Ecosystem | Functional Patterns to Add |
|-----------|---------------------------|
| Django | models.Model, function views, class views, URL routing, serializers, middleware, admin, migrations, signals |
| Flask | @app.route, blueprints, request/response, templates, config, extensions |
| React | function components, class components, hooks (useState, useEffect, custom), routing, state management, context |
| Express | routes, middleware, request handlers, error handlers |
| FastAPI | path operations, dependencies, Pydantic models, background tasks |

### Mining Sources (Priority Order)

| Priority | Source | Method | Expected Yield |
|----------|--------|--------|----------------|
| P1 | Framework docs | Extract patterns from code samples | High precision |
| P2 | Type stubs | Parse typeshed/DefinitelyTyped | High recall |
| P3 | IDE inspections | Extract from PyCharm/VSCode | Medium |
| P4 | Non-security linters | Extract from pylint/eslint | Low-medium |

### Quality Gate for New Atoms

Every new functional atom MUST include:

```yaml
atom:
  id: EXT.DJANG.MODEL.001
  name: Django Model Definition
  tier: T2
  category: functional  # NOT security
  ecosystem: django

  # REQUIRED for quality gate
  positive_example: |
    class User(models.Model):
        name = models.CharField(max_length=100)

  negative_example: |
    class User:  # Not a Django model
        def __init__(self, name):
            self.name = name

  trigger:
    imports: ["django.db.models"]
    pattern: "class .*(models.Model)"

  # Test requirement
  test_file: tests/atoms/test_django_model.py
```

### Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Functional atom ratio | 23% | 45% |
| Django functional coverage | 0% | 30% of framework nodes |
| Flask functional coverage | 0% | 30% of framework nodes |
| React functional coverage | ~5% | 40% of framework nodes |
| New atom precision | N/A | ≥ 90% |

### Implementation Phases

| Phase | Deliverable | Timeline |
|-------|-------------|----------|
| C1 | Django functional atoms (10-15 patterns) | Week 1 |
| C2 | Flask functional atoms (8-10 patterns) | Week 2 |
| C3 | React functional atoms (12-15 patterns) | Week 3 |
| C4 | Validation study (precision measurement) | Week 4 |

---

## Artifact Layout

```
artifacts/atom-research/
├── 2026-01-22/                    # Date-stamped run
│   ├── corpus.yaml                # Repo list + stratification
│   ├── summary.csv                # Aggregated metrics
│   ├── summary.md                 # Human-readable report
│   ├── claims_ladder.md           # Current claim levels
│   └── repos/
│       ├── gatsby/
│       │   └── abc123/            # Commit SHA
│       │       ├── run_metadata.json
│       │       ├── unified_analysis.json
│       │       └── coverage.json
│       ├── meilisearch/
│       │   └── def456/
│       │       └── ...
│       └── ...
└── latest -> 2026-01-22/          # Symlink to latest
```

---

## CI/CD Integration

### Quality Gates (Immediate)

| Check | Condition | Action |
|-------|-----------|--------|
| No duplicate atom IDs | `atom_inventory.py --check-duplicates` | Fail PR |
| No category-less atoms | All atoms have category field | Fail PR |
| Unknown rate budget | Self-repo Unknown ≤ 10% | Warn (later: fail) |

### Regression Gates (Future)

| Check | Condition | Action |
|-------|-----------|--------|
| Top-4 mass stability | Δ < 5% from baseline | Warn |
| T2 precision stability | Δ < 3% from baseline | Warn |
| Unknown rate improvement | Never increases from baseline | Fail |

---

## Study D: D3_ROLE Tiered Classification

> **Status:** IMPLEMENTED (2026-01-22)
> **Commit:** (pending)

### Problem Statement

The `classify_role()` method in `dimension_classifier.py` used tree-sitter `roles.scm` queries but was **never called** in the pipeline. D3_ROLE was assigned purely via heuristics (path patterns, naming conventions).

### Solution: Tiered Classification

| Tier | Method | Confidence | Source |
|------|--------|------------|--------|
| 0 | Tree-sitter `roles.scm` queries | 70-95% | AST pattern matching |
| 1 | Heuristic fallback | 30-70% | Path, name, inheritance |

### Implementation

**File:** `src/core/classification/universal_classifier.py`

**Changes:**
1. Import `TreeSitterDimensionClassifier` (line 44-51)
2. Initialize `ts_role_classifier` in `__init__` (line 62-63)
3. Tiered classification in `_derive_dimensions()` (lines 610-640)

**Logic:**
```python
# Tier 0: Tree-sitter (if available and body_source exists)
ts_role_result = self.ts_role_classifier.classify_role(source=body, name=name, language=lang)

if ts_role_result and ts_role_result.get('confidence', 0) >= 70:
    dims["D3_ROLE"] = ts_role_result['role']
    dims["D3_ROLE_SOURCE"] = "tree-sitter"
    dims["D3_ROLE_CONFIDENCE"] = ts_role_result['confidence']
else:
    # Tier 1: Heuristic fallback
    dims["D3_ROLE"] = role  # from existing classification
    dims["D3_ROLE_SOURCE"] = "heuristic"
```

### New Schema Fields

| Field | Type | Description |
|-------|------|-------------|
| `D3_ROLE_SOURCE` | string | `"tree-sitter"` or `"heuristic"` |
| `D3_ROLE_CONFIDENCE` | int | 0-100, only present for tree-sitter |
| `D3_ROLE_EVIDENCE` | list | Matched patterns (tree-sitter only) |

### Validation Results (L0)

Tested on `src/core/classification/` (17 nodes):

| Metric | Value |
|--------|-------|
| Tree-sitter classified | 4 (24%) |
| Heuristic fallback | 12 (71%) |
| No source | 1 (5%) |
| Avg confidence (TS) | 81.2% |

**Roles detected via tree-sitter:**
- `__init__` → Lifecycle (85%)
- `classify_function_pattern` → Handler (80%)
- `_get_function_type_by_name` → Handler (80%)

### Cross-Language Validation

| Language | Status | Test |
|----------|--------|------|
| Python | ✅ Working | Repository, Validator, Handler detected |
| JavaScript | ✅ Working | Repository (90%), boundary=io, state=stateful |
| TypeScript | ✅ Working | Shares JS queries |

### Promotion Path

| Level | Requirement | Status |
|-------|-------------|--------|
| L0 | Works on 1 repo | ✅ ACHIEVED |
| L1 | Works on 7 repos with >20% TS coverage | Pending |
| L2 | Works on 100+ repos | Pending |

### Connection to Other Studies

- **Study A (Structural):** D1_WHAT coverage is orthogonal to D3_ROLE
- **Study C (Functional):** roles.scm queries ARE functional pattern detection
- **Security skew:** Roles are NOT security-skewed (unlike T2 atoms)

---

## Research Tooling

### Required Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `atom_inventory.py` | Count atoms by tier/ecosystem/category | `tools/research/` |
| `atom_coverage.py` | Compute coverage metrics from analysis | `tools/research/` |
| `atom_quality.py` | Check duplicates, overlaps | `tools/research/` |
| `run_corpus.py` | Batch-run Collider on corpus | `tools/research/` |
| `summarize_corpus.py` | Aggregate metrics into report | `tools/research/` |

### Usage Examples

```bash
# Inventory analysis
python tools/research/atom_inventory.py --output artifacts/inventory.json

# Coverage from single analysis
python tools/research/atom_coverage.py .collider/unified_analysis.json --output coverage.json

# Quality checks
python tools/research/atom_quality.py --check-duplicates --check-overlaps

# Corpus run
python tools/research/run_corpus.py corpus.yaml --output artifacts/2026-01-22/

# Summarize
python tools/research/summarize_corpus.py artifacts/2026-01-22/ --output summary.md
```

---

## Timeline

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1 | Research tooling | Scripts, Makefile, CI checks |
| 2-3 | Study A: Corpus collection | 100 repos sampled, analyzed |
| 4 | Study A: Analysis | Summary stats, hypothesis tests |
| 5-6 | Study B: T2 labeling | 1000+ nodes labeled |
| 7 | Study B: Analysis | Precision report, top offenders |
| 8-10 | Study C: Functional enrichment | Django/Flask/React atoms |
| 11 | Study C: Validation | Precision measurement |
| 12 | Synthesis | Claims ladder update, final report |

---

## AI Orchestration

Phase 2 uses multi-AI validation with **hard gates** (must pass) and **soft votes** (advisory).

See **AI_ORCHESTRATION_PROTOCOL.md** for full details.

### Core Principle

**AI systems advise; artifacts + metrics decide.**

### Hard Gates (All Must Pass)

| Gate | Requirement |
|------|-------------|
| **G1** | Deterministic metrics computed (Mode A) |
| **G2** | Metrics satisfy claim's numeric bounds |
| **G3** | No unresolved credible falsification |
| **G4** | All audit artifacts saved |
| **G5** | Human signoff recorded |

### Veto Condition

If ChatGPT (or any system) produces a credible falsification:
1. Investigate immediately
2. Either refute with evidence, OR
3. **Claim stays at L1** (blocked)

### System Roles

| System | Model | Scope | Role |
|--------|-------|-------|------|
| Gemini | gemini-2.5-pro | Internal | Structural analysis, code validation |
| Perplexity | sonar-pro | External | Literature context (NOT internal validation) |
| ChatGPT | o3 Extended | External | Falsification, peer review prep |

### Soft Votes (Advisory)

2/3 AI agreement applies to wording, scope, and caveats. It does NOT override failing hard gates.

### Decision Records

Use **DECISION_TEMPLATE.md** for all promotion decisions. Machine-readable YAML frontmatter enables CI/tooling.

### Commands

```bash
# Gemini analysis
.tools_venv/bin/python context-management/tools/ai/analyze.py \
  "[query]" --set research_full --mode forensic

# Perplexity (via MCP) - external context only
mcp__perplexity__perplexity_research

# ChatGPT (manual with adversarial prompt)
# See AI_ORCHESTRATION_PROTOCOL.md for template
```

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial protocol draft | Claude Opus 4.5 |
| 2026-01-22 | Added AI orchestration section | Claude Opus 4.5 |
| 2026-01-22 | Hardening: hard gates vs soft votes, veto condition, decision template | Claude Opus 4.5 |
