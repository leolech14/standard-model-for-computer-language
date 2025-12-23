# The Standard Model of Code

> **Every code element has a PURPOSE. Purposes EMERGE hierarchically. This is the physics of software.**

## The Insight

Just as physics has the Standard Model (quarks, leptons, bosons), software has fundamental constituents:

| Physics           |  Code                                           |
|-------------------|-------------------------------------------------|
| 118 Elements.     | **167 Atoms** (structural types)                |
| Atomic properties | **RPBL Scores** (behavioral dimensions)         |
| Chemical bonds    | **Relationships** (calls, imports, inherits)    |
| Molecular purpose | **Roles** (27 semantic intents)                 |
| Conservation laws | **Antimatter Rules** (architectural constraints)|

## The Claim

```
Any code element in any codebase can be mapped to a semantic coordinate:

    σ(element) = (atom, role, RPBL)

Where:
    atom ∈ {167 structural types}
    role ∈ {27 semantic intents}  
    RPBL ∈ [1,10]⁴ (Responsibility, Purity, Boundary, Lifecycle)
```

**Empirically validated:**
- 212,052 nodes across 33 repositories
- 100% classification coverage
- 87.6% accuracy (94.7% on high-confidence)
- 1,860 nodes/second (no LLM required)

## Purpose Field Theory

Code has a **Purpose Field** - meaning that emerges hierarchically:

```
┌─────────────────────────────────────────────────────────────────┐
│  Level 4: PURPOSE FIELD (Application)                           │
│  The global semantic gradient across the entire codebase        │
├─────────────────────────────────────────────────────────────────┤
│  Level 3: LAYER PURPOSE (Architecture)                          │
│  Presentation → Application → Domain → Infrastructure           │
├─────────────────────────────────────────────────────────────────┤
│  Level 2: COMPOSITE PURPOSE (Emergence)                         │
│  UserRepository = {Query + Command} → "User persistence"        │
├─────────────────────────────────────────────────────────────────┤
│  Level 1: ATOMIC PURPOSE (Role)                                 │
│  get_user() → Query: "Retrieve data without modification"       │
└─────────────────────────────────────────────────────────────────┘
```

# 5. Actionable Insights (prioritized recommendations)
# 6. Summary (reproducible proof document)


**Installation:**
```bash
pip install .
```

**Run Analysis (Full Stream):**
```bash
collider analyze /path/to/code
```
This generates:
- `spectrometer_output/unified_analysis.json` (Data)
- `spectrometer_report.html` (Visualization)

**Other Commands:**
```bash
collider audit           # Run system health check
collider viz graph.json  # Regenerate visualization from JSON
```

## Visualization

The **Collider Visualization** provides an interactive 3D/2D visualization of your codebase's Purpose Field.

1. Generate analysis:
   ```bash
   collider analyze /path/to/code
   ```
2. Open `collider_report.html` (or `collider_viz.html`) in your browser.
   - Works fully offline (bundled assets).
   - Visualize relationships, layers, and hotpots.


### Example Output

```
🔬 COLLIDER - Standard Model of Code
======================================================================
Target: /path/to/code
Time:   2025-12-22T20:44:34

┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: ACTIONABLE INSIGHTS                                   │
└─────────────────────────────────────────────────────────────────┘
  Found 4 actionable insights:
    🟠 [HIGH] Low Test Coverage
       └─ Schema: TEST_COVERAGE
    🟠 [HIGH] God Class Detected
       └─ Schema: GOD_CLASS_DECOMPOSITION
    🟡 [MEDIUM] Missing Repository Pattern
       └─ Schema: REPOSITORY_PATTERN
    🟢 [LOW] Pure Function Optimization
       └─ Schema: PURE_FUNCTION_EXTRACTION

┌─────────────────────────────────────────────────────────────────┐
│ STAGE 6: SUMMARY                                               │
└─────────────────────────────────────────────────────────────────┘
  Total nodes:      535
  Coverage:         100.0%
  Avg confidence:   70.0%
  Speed:            1,609 nodes/sec

  ✓ Proof saved to: proof_output.json
```

## What The Collider Detects

### 1. Atomic Purpose (27 Roles)

| Role | Purpose |
|------|---------|
| `Query` | Retrieve data without modification |
| `Command` | Execute action that changes state |
| `Repository` | Abstract data persistence |
| `Service` | Coordinate business operations |
| `Factory` | Create and configure instances |
| `Validator` | Verify data meets constraints |
| `Test` | Verify behavior meets expectations |
| ... | [27 total - see docs/PURPOSE_FIELD.md] |

### 2. Structural Type (167 Atoms)

Organized in 4 phases:
- **DATA** (26): Entity, ValueObject, DTO, Enum...
- **LOGIC** (61): Query, Command, Filter, Validate...
- **ORGANIZATION** (45): Repository, Service, Factory, Controller...
- **EXECUTION** (35): Constructor, Middleware, Event, Transaction...

### 3. Behavioral Dimensions (RPBL)

| Dimension | Question | Scale |
|-----------|----------|-------|
| **R**esponsibility | How focused is it? | 1 (god class) → 10 (single purpose) |
| **P**urity | Does it have side effects? | 1 (impure) → 10 (pure function) |
| **B**oundary | Does it cross system boundaries? | 1 (internal) → 10 (external I/O) |
| **L**ifecycle | How long does it live? | 1 (request) → 10 (application) |

### 4. Violations (Antimatter)

The Standard Model defines what code **CANNOT** do:

```
❌ Repository → Controller   (infrastructure calling presentation)
❌ Query with side effects   (role violation)
❌ Service with no tests     (coverage violation)
❌ Entity without Repository (persistence gap)
```

### 5. Predictions

Detect **MISSING** components:

```
Entities found:    User, Order, Product, Payment
Repositories:      UserRepository, OrderRepository

PREDICTION: ProductRepository and PaymentRepository are MISSING
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STANDARD MODEL (Theory)                     │
│              167 Atoms + 27 Roles + RPBL + Rules                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      COLLIDER (Implementation)                  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ PIPELINE: tools/prove.py                                │   │
│   │                                                         │   │
│   │ 1. AST Parse      → Extract code structure              │   │
│   │ 2. RPBL Score     → Classify behavior                   │   │
│   │ 3. Pattern Match  → Detect roles                        │   │
│   │ 4. Predictions    → Find missing components             │   │
│   │ 5. Insights       → Generate recommendations            │   │
│   │ 6. Fix Templates  → Produce solution code               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   CORE MODULES:                                                 │
│   core/unified_analysis.py      - Main analysis pipeline        │
│   core/auto_pattern_discovery.py - Role detection               │
│   core/purpose_field.py         - Hierarchical emergence        │
│   core/purpose_registry.py      - Purpose definitions           │
│   core/insights_engine.py       - Actionable recommendations    │
│   core/fix_generator.py         - Code template generator       │
│   core/antimatter_evaluator.py  - Violation detection           │
└─────────────────────────────────────────────────────────────────┘
```

## Optimization Schemas (13)

When the Collider detects issues, it recommends **optimization schemas** - proven patterns to fix them:

| Schema | When to Apply |
|--------|---------------|
| `REPOSITORY_PATTERN` | Entities without repositories |
| `SERVICE_EXTRACTION` | Controllers with embedded logic |
| `TEST_COVERAGE` | Low test-to-logic ratio |
| `CQRS_SEPARATION` | Mixed read/write operations |
| `LAYER_ENFORCEMENT` | Cross-layer violations |
| `GOD_CLASS_DECOMPOSITION` | Classes with 20+ methods |
| `PURE_FUNCTION_EXTRACTION` | Functions mixing pure/impure |
| `EVENT_SOURCING` | Audit requirements |
| `SAGA_PATTERN` | Distributed transactions |
| `FACTORY_METHOD` | Scattered object creation |
| `STRATEGY_PATTERN` | Switch/if-else chains |
| `DEPENDENCY_INJECTION` | Hard-coded dependencies |
| `ERROR_HANDLING` | Inconsistent exception handling |

Each schema includes step-by-step instructions and code templates.

## The Remarkable Claim

> **Software has LAWS, like physics.**
>
> The Standard Model defines those laws.
> Violations are not "code smells" - they are IMPOSSIBLE states.
> Purpose flows through architecture like energy through a system.
>
> **This makes software engineering a SCIENCE, not an ART.**

## Documentation

| Document | Description |
|----------|-------------|
| [FORMAL_PROOF.md](docs/FORMAL_PROOF.md) | Mathematical proof of completeness |
| [PURPOSE_FIELD.md](docs/PURPOSE_FIELD.md) | Purpose emergence theory |
| [ATOMS_REFERENCE.md](docs/ATOMS_REFERENCE.md) | Complete 167-atom taxonomy |
| [DIMENSIONS.md](docs/DIMENSIONS.md) | RPBL behavioral dimensions |

## Validation

| Metric | Value |
|--------|-------|
| Repositories tested | 33 |
| Nodes classified | 212,052 |
| Coverage | 100% |
| Overall accuracy | 87.6% |
| High-confidence accuracy | 94.7% |
| Speed | 1,860 nodes/sec |

## License

MIT

---

*"The periodic table of code. Every element has a purpose. Every purpose has a place."*
