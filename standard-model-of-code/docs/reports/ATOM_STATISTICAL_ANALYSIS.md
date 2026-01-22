# Atom Statistical Analysis

> Deep statistical analysis of the 3,616 atom inventory.
> Generated: 2026-01-22

## Executive Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total Atoms | 3,616 | Inventory size |
| Unique Atoms | 3,616 | 16 exact duplicates removed |
| Core Atoms (structure) | 22 | Cover ~90% of code nodes |
| T0 Atoms (AST) | 42 | 100% parseable code (definitional) |
| T1 Atoms (stdlib) | 21 | ~20-40% typical codebase |
| T2 Atoms (ecosystem) | 3,531 | Variable (0-60% by ecosystem) |
| Ecosystems | 178 | Languages + frameworks |

**Key Finding:** The claim "42 atoms cover 65% of code" is **misleading**. The truth:

- **4 atoms** cover ~80-90% of code **structure** (Function, Class, Variable, Module)
- **42 T0 atoms** cover 100% of **parseable code** (they ARE the syntax)
- **3,500+ T2 atoms** provide **semantic enrichment**, not structural coverage

## Tier Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 0: AST ATOMS (42)                                                  │
│ Coverage: 100% of parseable code (definitional)                         │
│ These ARE the syntax: C1_FunctionDef, C1_ForLoop, C1_Assignment         │
│ Utility: Low for analysis (too granular)                                │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ BASE ATOMS (22)                                                         │
│ Coverage: ~90% of code nodes → 4 atoms                                  │
│ Semantic roles: LOG.FNC.M, ORG.AGG.M, DAT.VAR.A, ORG.MOD.O              │
│ Utility: High for architecture analysis                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 1: STDLIB ATOMS (21)                                               │
│ Coverage: ~20-40% of code (uses standard library)                       │
│ IO, Networking, Async, Data: T1_IO_FILE, T1_NET_HTTP, T1_DATA_JSON      │
│ Utility: Medium (requires import analysis)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 2: ECOSYSTEM ATOMS (3,531)                                         │
│ Coverage: 0-60% (depends on ecosystem match)                            │
│ Framework patterns: EXT.DJANG.001, EXT.REACT.001, EXT.FASTAPI.001       │
│ Utility: High for framework-specific insights                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Distribution Analysis

### By Tier

| Tier | Count | % of Total |
|------|-------|------------|
| T0 (AST) | 42 | 1.2% |
| T1 (Stdlib) | 21 | 0.6% |
| T2 (Original) | 17 | 0.5% |
| T2 (Mined) | 3,530 | 97.2% |
| Base | 22 | 0.6% |

### By Source

| Source | Count | % |
|--------|-------|---|
| ATOMS_T2_OTHER.yaml | 1,766 | 48.6% |
| ATOMS_T2_PYTHON.yaml | 566 | 15.6% |
| ATOMS_T2_FRONTEND.yaml | 399 | 11.0% |
| ATOMS_T2_JAVASCRIPT.yaml | 327 | 9.0% |
| ATOMS_T2_JAVA.yaml | 265 | 7.3% |
| ATOMS_T2_CLOUD.yaml | 122 | 3.4% |
| ATOMS_T2_GAPS.yaml | 85 | 2.3% |
| Other | 102 | 2.8% |

### By Ecosystem (Top 20)

| Ecosystem | Count | % |
|-----------|-------|---|
| python | 282 | 7.8% |
| vue | 217 | 6.0% |
| java | 197 | 5.4% |
| django | 188 | 5.2% |
| go | 151 | 4.2% |
| aws-lambda | 122 | 3.4% |
| react | 119 | 3.3% |
| typescript | 118 | 3.2% |
| express | 107 | 2.9% |
| core | 102 | 2.8% |
| .net | 99 | 2.7% |
| flask | 94 | 2.6% |
| javascript | 76 | 2.1% |
| ruby | 71 | 2.0% |
| angular | 63 | 1.7% |
| scala | 57 | 1.6% |
| solidity | 55 | 1.5% |
| spring | 54 | 1.5% |
| rails | 54 | 1.5% |
| ocaml | 52 | 1.4% |

**Total Ecosystems: 178**

### By Category

| Category | Count | % | Issue |
|----------|-------|---|-------|
| security | 2,724 | 75.0% | **OVER-REPRESENTED** |
| general | 237 | 6.5% | - |
| best-practice | 158 | 4.4% | - |
| unknown | 80 | 2.2% | Needs classification |
| correctness | 73 | 2.0% | - |
| maintainability | 66 | 1.8% | - |
| Other | 294 | 8.1% | - |

## Quality Issues

### 1. Security Skew (Critical)

**77% of T2 atoms are security-focused** because they were mined from Semgrep rules.

This means:
- Excellent: Security vulnerability detection
- Poor: Functional pattern recognition

**Example for Django:**
- We detect: SQL injection, XSS, insecure cookies
- We miss: Models, Views, Templates, Forms, Signals, Middleware

**Recommendation:** Mine functional patterns from:
- Documentation (Django docs, React docs)
- Type stubs (typeshed, DefinitelyTyped)
- IDE plugins (PyCharm inspections, VSCode extensions)

### 2. Duplicate/Near-Duplicate Analysis

| Type | Count |
|------|-------|
| Exact ID duplicates | 16 |
| Similar names (semantic overlap) | 463 groups |

**Examples of semantic overlap:**
- "format": 26 atoms across ecosystems
- "compile": 19 atoms
- "render": 18 atoms
- "template": 15 atoms

**Recommendation:** Create canonical mappings for common operations.

### 3. Pattern Quality

Sample patterns show **variable quality**:

**Good patterns (specific):**
```
EXT.FASTAPI.ROUTE.001: @app.get(...
EXT.REACT.BEST.001: this.state = {$NAME: <... this.props.$PROP ...>}
```

**Weak patterns (generic):**
```
EXT.LAMBDA.SEC.005: $CLIENT.escape(...)  # Too generic
EXT.REACT.GEN.005: $I18NEXT.t('$KEY', $OPTIONS)  # Library-specific
```

## Coverage Model (Honest Numbers)

### Structural Coverage (What we classify)

| Atom | Typical % | Node Type |
|------|-----------|-----------|
| LOG.FNC.M | 40-50% | Functions, Methods |
| ORG.AGG.M | 10-20% | Classes, Interfaces |
| DAT.VAR.A | 15-25% | Variables, Assignments |
| ORG.MOD.O | 5-10% | Modules, Imports |
| **Subtotal** | **80-90%** | **4 atoms** |
| Other base | 5-15% | Edge cases |
| Unknown | 0-10% | Unclassified |

### Semantic Enrichment (What T2 adds)

T2 atoms **augment** structural classification:

```
Node: "def get_user(request):"
├── Structural: LOG.FNC.M (Function) ← Always assigned
└── Semantic: EXT.DJANG.VIEW.001 (Django View) ← If pattern matches
```

**T2 coverage varies by ecosystem match:**

| Repo Type | Expected T2 % | Why |
|-----------|---------------|-----|
| Django app | 30-60% | Good Django patterns |
| React app | 40-70% | Good React patterns |
| Rust CLI | 5-20% | Fewer Rust patterns |
| Go microservice | 10-30% | Moderate Go patterns |
| Custom framework | 0-10% | No patterns exist |

### Observed Coverage (Test Results)

| Repo | T2 % | Ecosystems Detected |
|------|------|---------------------|
| gatsby | 60% | react |
| meilisearch | 36% | rust, ml |
| Made-With-ML | 20% | fastapi, ml |
| vuejs/core | 12% | react |
| Collider (self) | 1.3% | python |

## Pareto Analysis

**The 80/20 Rule applies:**

```
┌────────────────────────────────────────────────────────────────┐
│                    ATOM IMPACT DISTRIBUTION                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ████████████████████████████████████████  80% ← 4 atoms       │
│  ███████████████                           15% ← 18 atoms      │
│  ████                                       5% ← 3,594 atoms   │
│                                                                │
└────────────────────────────────────────────────────────────────┘

The long tail (3,594 atoms) provides:
- Semantic richness ("this is a Django view")
- Security detection ("SQL injection here")
- Framework intelligence ("React anti-pattern")

But NOT structural coverage improvement.
```

## Recommendations

### 1. Rename/Reframe Tiers

| Current | Proposed | Description |
|---------|----------|-------------|
| T0 | AST Atoms | Syntax elements (100% coverage) |
| Base | Structural Atoms | Architecture nodes (90% coverage) |
| T1 | Platform Atoms | Standard library (20-40%) |
| T2 | Domain Atoms | Framework-specific (variable) |

### 2. Fill Functional Gaps

Priority ecosystems needing **functional** atoms (not security):

| Ecosystem | Security Atoms | Functional Atoms | Gap |
|-----------|----------------|------------------|-----|
| Django | 188 | ~20 | HIGH |
| React | 119 | ~30 | MEDIUM |
| Flask | 94 | ~15 | HIGH |
| FastAPI | 15 | 15 | LOW |
| PyTorch | 20 | 20 | LOW |
| TensorFlow | 20 | 20 | LOW |

### 3. Quality Metrics

For each atom, track:
- **Specificity**: Does it match only what it claims?
- **Recall**: Does it find all instances?
- **Value**: Does detection provide actionable insight?

### 4. Deduplication Strategy

Create semantic equivalence classes:

```yaml
canonical_operations:
  rendering:
    - EXT.REACT.RENDER.*
    - EXT.VUE.RENDER.*
    - EXT.ANGULAR.RENDER.*
  serialization:
    - EXT.*.JSON.*
    - EXT.*.SERIALIZE.*
```

## Appendix: Corrected Claims

| Claim | Truth | Notes |
|-------|-------|-------|
| "42 atoms cover 65% of code" | 4 atoms cover 80-90% structurally | T0 atoms ARE code, not coverage |
| "3,616 atoms" | 3,616 unique IDs | 16 duplicates exist |
| "60% T2 coverage" | Variable by ecosystem | gatsby=60%, Collider=1.3% |
| "178 ecosystems" | 178 ecosystem tags | Quality varies greatly |

## Data Quality Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| Structural Atoms | A | 22 well-defined |
| T0 AST Atoms | A | 42 complete for Python |
| T1 Stdlib Atoms | B | 21 need detection implementation |
| T2 Security | A | 2,724 from Semgrep |
| T2 Functional | C | 806, needs expansion |
| Deduplication | B | 16 exact, 463 semantic |
| Documentation | C | Needs this report |

**Overall: B-** (Strong foundation, biased toward security)
