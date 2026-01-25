# Codome Health Index (CHI)

> **Status:** DRAFT
> **Date:** 2026-01-23
> **Purpose:** Measure the QUALITY of a codome, not just completeness

---

## Beyond Completeness

Finding all particles is necessary but not sufficient. A healthy codome also needs:

| Dimension | Question | Metric |
|-----------|----------|--------|
| **Completeness** | Did we find all particles? | CCI (F2 Score) |
| **Documentation** | Is the code explained? | Documentation Density |
| **Redundancy** | Is code duplicated? | Redundancy Index |
| **Fluff** | Is there unnecessary abstraction? | Fluff Ratio |
| **Legacy Sprawl** | Is there dead/deprecated code? | Sprawl Index |
| **Purpose Alignment** | Does code serve its stated purpose? | Alignment Score |
| **Cohesion** | Do related things stay together? | Cohesion Metric |
| **Coupling** | Are modules properly decoupled? | Coupling Score |

---

## The Signal-Noise-Fluff Model

Professional repos have THREE categories, not two:

```
┌─────────────────────────────────────────────────────────────┐
│                    TOTAL FILE CONTENT                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   SIGNAL          NOISE              FLUFF                   │
│   (Particles)     (Necessary)        (Unnecessary)           │
│                                                              │
│   ████████        ░░░░░░░░░░░░       ▓▓▓▓▓▓                  │
│                                                              │
│   Functions       Whitespace         Dead code               │
│   Classes         Comments           Unused imports          │
│   Variables       Keywords           Over-abstraction        │
│   Methods         Operators          Redundant wrappers      │
│   Types           Imports            Legacy compatibility    │
│                   Literals           Debug scaffolding       │
│                   Control flow       TODO/FIXME debt         │
│                                                              │
└─────────────────────────────────────────────────────────────┘

SIGNAL + NOISE + FLUFF = 100%

Health = High SIGNAL, Appropriate NOISE, Low FLUFF
```

---

## 1. Documentation Density (DD)

### Formula

```
DD = (Comment Bytes + Docstring Bytes) / Total Bytes

Professional Range:
  DD < 5%   → UNDERDOCUMENTED (code smell)
  DD 5-15%  → HEALTHY (well-documented)
  DD 15-25% → VERBOSE (acceptable for public APIs)
  DD > 25%  → OVERDOCUMENTED (comments may be stale)
```

### Sub-metrics

```python
@dataclass
class DocumentationMetrics:
    total_comment_bytes: int
    inline_comments: int      # // or # at end of line
    block_comments: int       # /* */ or """ """
    docstrings: int           # Function/class documentation
    todo_comments: int        # TODO, FIXME, HACK, XXX

    # Quality indicators
    stale_comments: int       # Comments that don't match code
    redundant_comments: int   # Comments that repeat the code
    useful_comments: int      # Comments that add context

    @property
    def documentation_quality(self) -> float:
        """Ratio of useful comments to total comments."""
        total = self.inline_comments + self.block_comments + self.docstrings
        return self.useful_comments / total if total > 0 else 0
```

---

## 2. Redundancy Index (RI)

### Formula

```
RI = Duplicated Particles / Total Particles

Where "Duplicated" means:
  - Exact duplicates (same code)
  - Near-duplicates (>80% similar)
  - Semantic duplicates (same behavior, different implementation)
```

### Detection Methods

```python
def calculate_redundancy_index(particles: List[Particle]) -> RedundancyMetrics:
    """
    Find duplicate and near-duplicate code.
    """
    duplicates = {
        'exact': [],       # Hash match
        'near': [],        # AST structure match >80%
        'semantic': [],    # Same inputs → same outputs
    }

    # Method 1: Hash-based exact duplicate detection
    hashes = {}
    for p in particles:
        h = hash_particle_body(p)
        if h in hashes:
            duplicates['exact'].append((p, hashes[h]))
        else:
            hashes[h] = p

    # Method 2: AST structure comparison
    for i, p1 in enumerate(particles):
        for p2 in particles[i+1:]:
            similarity = compare_ast_structure(p1, p2)
            if similarity > 0.8:
                duplicates['near'].append((p1, p2, similarity))

    # Method 3: Semantic equivalence (expensive)
    # Compare function signatures and behavior patterns

    total_duplicated = (
        len(duplicates['exact']) +
        len(duplicates['near']) +
        len(duplicates['semantic'])
    )

    return RedundancyMetrics(
        redundancy_index=total_duplicated / len(particles),
        exact_duplicates=duplicates['exact'],
        near_duplicates=duplicates['near'],
        semantic_duplicates=duplicates['semantic'],
        verdict=get_redundancy_verdict(total_duplicated / len(particles))
    )

def get_redundancy_verdict(ri: float) -> str:
    if ri < 0.02:
        return "EXCELLENT (minimal duplication)"
    elif ri < 0.05:
        return "GOOD (acceptable duplication)"
    elif ri < 0.10:
        return "FAIR (consider refactoring)"
    else:
        return "POOR (significant code duplication)"
```

---

## 3. Fluff Ratio (FR)

### Definition

**Fluff** = Code that exists but serves no purpose or adds unnecessary complexity.

### Categories

| Fluff Type | Detection | Example |
|------------|-----------|---------|
| **Dead Code** | Unreachable | `if (false) { ... }` |
| **Unused Imports** | Never referenced | `import { unused } from 'lib'` |
| **Unused Variables** | Declared but not used | `const x = 1; // never used` |
| **Unused Functions** | Defined but never called | `function helper() {}` |
| **Over-abstraction** | Single-use wrapper | `const add = (a, b) => a + b; add(1, 2);` |
| **Redundant Wrappers** | Pass-through functions | `function wrap(x) { return x; }` |
| **Legacy Shims** | Backwards-compat only | `if (oldAPI) { oldAPI() } else { newAPI() }` |
| **Debug Scaffolding** | `console.log`, `debugger` | Left-in debug code |
| **Commented Code** | `// old implementation` | Dead code as comments |

### Formula

```
FR = Fluff Particles / Total Particles

Professional Range:
  FR < 2%   → PRISTINE (very clean)
  FR 2-5%   → HEALTHY (normal maintenance debt)
  FR 5-10%  → NEEDS_CLEANUP (schedule refactoring)
  FR > 10%  → BLOATED (significant fluff)
```

### Detection

```python
def calculate_fluff_ratio(
    particles: List[Particle],
    edges: List[Edge]
) -> FluffMetrics:
    """
    Identify particles that are fluff.
    """
    # Build call graph
    callers = build_caller_map(edges)

    fluff = {
        'dead_code': [],
        'unused_imports': [],
        'unused_variables': [],
        'unused_functions': [],
        'over_abstraction': [],
        'redundant_wrappers': [],
        'debug_scaffolding': [],
        'commented_code': [],
    }

    for p in particles:
        # Unused: No incoming edges (except entry points)
        if not callers.get(p.id) and not is_entry_point(p):
            if p.type == 'Import':
                fluff['unused_imports'].append(p)
            elif p.type == 'Variable':
                fluff['unused_variables'].append(p)
            elif p.type == 'Function':
                fluff['unused_functions'].append(p)

        # Over-abstraction: Used exactly once, trivial body
        if len(callers.get(p.id, [])) == 1 and is_trivial(p):
            fluff['over_abstraction'].append(p)

        # Redundant wrapper: Just calls another function
        if is_passthrough(p):
            fluff['redundant_wrappers'].append(p)

        # Debug scaffolding
        if contains_debug_patterns(p):
            fluff['debug_scaffolding'].append(p)

    total_fluff = sum(len(v) for v in fluff.values())

    return FluffMetrics(
        fluff_ratio=total_fluff / len(particles),
        breakdown=fluff,
        total_fluff_particles=total_fluff,
        verdict=get_fluff_verdict(total_fluff / len(particles))
    )
```

---

## 4. Legacy Sprawl Index (LSI)

### Definition

**Legacy Sprawl** = Accumulation of outdated patterns, deprecated APIs, and migration debris.

### Indicators

| Indicator | Detection | Severity |
|-----------|-----------|----------|
| **Deprecated API usage** | `@deprecated`, console warnings | HIGH |
| **Old syntax patterns** | `var` instead of `const/let` | MEDIUM |
| **Mixed module systems** | `require()` + `import` in same file | MEDIUM |
| **Version-specific shims** | `if (nodeVersion < 14)` | HIGH |
| **Multiple implementations** | `getUserV1()`, `getUserV2()` | HIGH |
| **TODO/FIXME density** | Unresolved debt markers | MEDIUM |
| **Orphaned migrations** | Half-completed refactors | HIGH |
| **Compatibility layers** | Adapters for old interfaces | MEDIUM |

### Formula

```
LSI = (
    Deprecated_Usages * 3 +
    Old_Patterns * 1 +
    Mixed_Systems * 2 +
    Version_Shims * 3 +
    Multi_Implementations * 3 +
    TODO_Density * 1 +
    Orphaned_Migrations * 4
) / Total_Particles

Professional Range:
  LSI < 1%   → MODERN (actively maintained)
  LSI 1-3%   → HEALTHY (normal legacy)
  LSI 3-7%   → AGING (needs modernization)
  LSI > 7%   → SPRAWLING (significant tech debt)
```

---

## 5. Purpose Alignment Score (PAS)

### Definition

**Purpose Alignment** = Does the code do what its name/documentation says it does?

### Measurement

```python
def calculate_purpose_alignment(particle: Particle) -> AlignmentScore:
    """
    Compare declared purpose (name, docstring) with actual behavior.
    """
    # Extract declared purpose
    name_purpose = infer_purpose_from_name(particle.name)
    doc_purpose = extract_purpose_from_docstring(particle.docstring)

    # Extract actual behavior
    actual_behavior = analyze_particle_behavior(particle)

    # Compare
    name_alignment = compare_purpose_behavior(name_purpose, actual_behavior)
    doc_alignment = compare_purpose_behavior(doc_purpose, actual_behavior)

    # Flags
    flags = []
    if name_purpose and not name_alignment:
        flags.append("NAME_MISMATCH")  # e.g., `validateUser` that doesn't validate
    if doc_purpose and not doc_alignment:
        flags.append("DOC_MISMATCH")   # e.g., docstring says X, code does Y
    if not doc_purpose:
        flags.append("UNDOCUMENTED")   # No docstring to compare

    return AlignmentScore(
        name_alignment=name_alignment,
        doc_alignment=doc_alignment,
        overall=min(name_alignment, doc_alignment or 1.0),
        flags=flags
    )
```

### Common Misalignments

| Pattern | Issue | Example |
|---------|-------|---------|
| **Misleading Name** | Name doesn't match behavior | `saveUser()` that only validates |
| **Stale Docstring** | Docs describe old behavior | Docstring from v1, code is v3 |
| **Side Effects** | Undocumented mutations | `getUser()` that also logs analytics |
| **Partial Implementation** | Doesn't fully deliver | `validateEmail()` that only checks `@` |
| **Scope Creep** | Does too much | `initApp()` that also fetches data |

---

## 6. Professional SNR Calibration

### The SNR Paradox

```
Minified code:  SNR ~= 0.9  (90% signal, 10% noise)  → BAD
Professional:   SNR ~= 0.3  (30% signal, 70% noise)  → GOOD

Why? Because professional "noise" includes:
  - Documentation (valuable)
  - Whitespace (readability)
  - Error handling (robustness)
  - Validation (safety)
  - Tests (quality)
```

### Professional SNR Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│              PROFESSIONAL REPOSITORY SNR                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SIGNAL (30%)                                                │
│  ├── Function definitions     15%                            │
│  ├── Class definitions         5%                            │
│  ├── Variable declarations     8%                            │
│  └── Type definitions          2%                            │
│                                                              │
│  PRODUCTIVE NOISE (55%)                                      │
│  ├── Documentation/comments   12%   ← VALUABLE               │
│  ├── Whitespace/formatting    18%   ← READABILITY            │
│  ├── Error handling            8%   ← ROBUSTNESS             │
│  ├── Input validation          5%   ← SAFETY                 │
│  ├── Logging/monitoring        4%   ← OBSERVABILITY          │
│  ├── Import statements         3%   ← DEPENDENCIES           │
│  └── Control flow              5%   ← LOGIC                  │
│                                                              │
│  FLUFF (5%)                                                  │
│  ├── Dead code                 1%   ← SHOULD REMOVE          │
│  ├── Debug scaffolding         1%   ← SHOULD REMOVE          │
│  ├── Legacy shims              2%   ← TECH DEBT              │
│  └── Over-abstraction          1%   ← REFACTOR               │
│                                                              │
│  UNKNOWN (10%)                                               │
│  └── Unclassified bytes       10%   ← INVESTIGATE            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### SNR Quality Score

```
SNR_Quality = (SIGNAL + PRODUCTIVE_NOISE) / (SIGNAL + PRODUCTIVE_NOISE + FLUFF)

Where:
  PRODUCTIVE_NOISE = Documentation + Whitespace + Error Handling + Validation + Logging

Professional Range:
  SNR_Quality > 95%  → EXCELLENT
  SNR_Quality 90-95% → GOOD
  SNR_Quality 80-90% → FAIR
  SNR_Quality < 80%  → NEEDS_WORK
```

---

## The Codome Health Index (CHI)

### Composite Formula

```
CHI = w1*CCI + w2*(1-RI) + w3*(1-FR) + w4*(1-LSI) + w5*PAS + w6*DD_norm + w7*SNR_Q

Where:
  CCI     = Completeness (F2 Score)
  RI      = Redundancy Index (lower is better)
  FR      = Fluff Ratio (lower is better)
  LSI     = Legacy Sprawl Index (lower is better)
  PAS     = Purpose Alignment Score
  DD_norm = Normalized Documentation Density (peak at 10-15%)
  SNR_Q   = SNR Quality Score

Default weights:
  w1 = 0.20  (Completeness)
  w2 = 0.15  (Redundancy)
  w3 = 0.15  (Fluff)
  w4 = 0.15  (Legacy Sprawl)
  w5 = 0.15  (Purpose Alignment)
  w6 = 0.10  (Documentation)
  w7 = 0.10  (SNR Quality)
```

### Interpretation

```
CHI >= 90%  → EXCELLENT HEALTH (exemplary codebase)
CHI 80-89%  → GOOD HEALTH (well-maintained)
CHI 70-79%  → FAIR HEALTH (some issues)
CHI 60-69%  → POOR HEALTH (needs attention)
CHI < 60%   → CRITICAL (major refactoring needed)
```

---

## Health Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                  CODOME HEALTH REPORT                        │
│                     my-project v2.1.0                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CODOME HEALTH INDEX (CHI): 84%  [████████░░] GOOD           │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Dimension            Score   Status                  │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ Completeness (CCI)    98%    ████████████ EXCELLENT  │    │
│  │ Redundancy (1-RI)     95%    ████████████ EXCELLENT  │    │
│  │ Fluff (1-FR)          92%    ███████████░ GOOD       │    │
│  │ Legacy (1-LSI)        78%    ████████░░░░ FAIR       │    │
│  │ Alignment (PAS)       85%    █████████░░░ GOOD       │    │
│  │ Documentation (DD)    72%    ███████░░░░░ FAIR       │    │
│  │ SNR Quality           88%    █████████░░░ GOOD       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  TOP ISSUES:                                                 │
│  1. Legacy Sprawl: 22% of code uses deprecated patterns      │
│     → src/legacy/*.js (recommend: migrate to v3 API)         │
│                                                              │
│  2. Documentation: 8% below target                           │
│     → src/core/*.js missing docstrings                       │
│                                                              │
│  3. Fluff: 8% unused code detected                           │
│     → 12 unused functions, 34 unused imports                 │
│                                                              │
│  RECOMMENDATIONS:                                            │
│  • Run `collider clean --unused` to remove dead code         │
│  • Run `collider migrate --deprecated` for API updates       │
│  • Add docstrings to 45 undocumented functions               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

| Phase | Task | Status | Priority |
|-------|------|--------|----------|
| 1 | Exhaustive Classification | TODO | HIGH |
| 2 | Documentation Density | TODO | MEDIUM |
| 3 | Redundancy Detection | TODO | MEDIUM |
| 4 | Fluff Detection | TODO | HIGH |
| 5 | Legacy Sprawl Analysis | TODO | MEDIUM |
| 6 | Purpose Alignment | TODO | LOW |
| 7 | CHI Composite Score | TODO | HIGH |
| 8 | Health Dashboard | TODO | MEDIUM |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial draft with 7 dimensions |
