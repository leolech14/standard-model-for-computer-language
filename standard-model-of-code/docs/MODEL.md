# MODEL.md - The Standard Model of Code

> Everything about the theory. What it is, why it works, how it's proven.

---

## 1. FOUNDATIONS

### The Three Planes

| Plane | What Exists | Example |
|-------|-------------|---------|
| **Physical** | Bits, bytes, files on disk | `0x48 0x65 0x6C 0x6C 0x6F` |
| **Virtual** | AST nodes, runtime objects | `FunctionDeclaration`, `ClassInstance` |
| **Semantic** | Meaning, intent, architecture | `Repository`, `Entity`, `Service` |

**Source:** Popper's Three Worlds

### The 16-Level Scale

| Level | Name | Zone |
|-------|------|------|
| L12 | UNIVERSE | COSMOLOGICAL |
| L11 | DOMAIN | COSMOLOGICAL |
| L10 | ORGANIZATION | COSMOLOGICAL |
| L9 | PLATFORM | COSMOLOGICAL |
| L8 | ECOSYSTEM | COSMOLOGICAL |
| L7 | SYSTEM | SYSTEMIC |
| L6 | PACKAGE | SYSTEMIC |
| L5 | FILE | SYSTEMIC |
| L4 | CONTAINER | SYSTEMIC |
| L3 | NODE | SEMANTIC |
| L2 | BLOCK | SEMANTIC |
| L1 | STATEMENT | SEMANTIC |
| L0 | TOKEN | SYNTACTIC |
| L-1 | CHARACTER | PHYSICAL |
| L-2 | BYTE | PHYSICAL |
| L-3 | BIT/QUBIT | PHYSICAL |

**Source:** Koestler's Holons

---

## 2. CLASSIFICATION

### The 4 Phases

| Phase | Question | Contains |
|-------|----------|----------|
| **DATA** | What is this made of? | Primitives, Variables, Constants |
| **LOGIC** | What does it do? | Expressions, Statements, Functions |
| **ORGANIZATION** | How is it structured? | Classes, Modules, Services |
| **EXECUTION** | How does it run? | Handlers, Workers, Initializers |

### The 8 Dimensions

| Dimension | Question | Values |
|-----------|----------|--------|
| WHAT | What type? | Atom taxonomy |
| LAYER | Where in architecture? | Domain, Application, Infrastructure, UI |
| ROLE | What purpose? | Role taxonomy |
| BOUNDARY | Crosses boundaries? | Internal, External |
| STATE | Maintains state? | Stateless, Stateful |
| EFFECT | Side effects? | Pure, Impure |
| LIFECYCLE | What phase? | Init, Active, Dispose |
| TRUST | How confident? | 0-100% |

### Atoms

| Version | Count | Source |
|---------|-------|--------|
| V1 (documented) | 167 | FORMAL_PROOF.md |
| V2 (documented) | 200 | 200_ATOMS.md |
| **Implemented** | **94** | atom_loader.py |

**Breakdown:**
- atoms.json (base): 14
- ATOMS_TIER0_CORE.yaml: 42
- ATOMS_TIER1_STDLIB.yaml: 21
- ATOMS_TIER2_ECOSYSTEM.yaml: 17

### Roles (33 Canonical)

| Category | Roles |
|----------|-------|
| Query | Query, Finder, Loader, Getter |
| Command | Command, Creator, Mutator, Destroyer |
| Factory | Factory, Builder |
| Storage | Repository, Store, Cache |
| Orchestration | Service, Controller, Manager |
| Validation | Validator, Guard, Asserter |
| Transform | Transformer, Mapper, Serializer |
| Event | Handler, Listener, Subscriber |
| Utility | Utility, Formatter, Helper |
| Internal | Internal, Lifecycle |
| Unknown | Unknown |

**Implemented:** 29 roles

### RPBL Dimensions

| Dim | Low (1) | High (9) |
|-----|---------|----------|
| **R** (Responsibility) | Single purpose | Omnibus |
| **P** (Purity) | No side effects | Heavy I/O |
| **B** (Boundary) | Internal only | External APIs |
| **L** (Lifecycle) | Ephemeral | Singleton |

**Space:** 9^4 = 6,561 states

---

## 3. SCHEMA

### Node (Minimal)

```json
{
  "id": "user.py:UserRepository",
  "name": "UserRepository",
  "kind": "class",
  "role": "Repository",
  "layer": "Infrastructure"
}
```

### Node (Full)

| Field | Type | Stage |
|-------|------|-------|
| `id` | string | 1 |
| `name` | string | 1 |
| `kind` | string | 1 |
| `file_path` | string | 1 |
| `start_line`, `end_line` | int | 1 |
| `complexity` | int | 1 |
| `role` | string | 2 |
| `role_confidence` | float | 2 |
| `layer` | string | 6 |
| `is_orphan` | bool | 7 |
| `is_hotspot` | bool | 8 |
| `body_source` | string | 1 |
| `in_degree` | int | 7 |
| `out_degree` | int | 7 |
| `topology_role` | string | 7 |

### Relational Properties

Unlike intrinsic properties (atoms, roles, dimensions) which can be determined from a single node, **relational properties** emerge from graph context. You cannot know a node's `topology_role` without analyzing the entire dependency graph.

| Property | Requires | Description |
|----------|----------|-------------|
| `in_degree` | edge list | Number of incoming dependencies |
| `out_degree` | edge list | Number of outgoing dependencies |
| `topology_role` | full graph | Structural position in dependency graph |

#### Topology Roles

| Role | Condition | Meaning | Typical Atoms |
|------|-----------|---------|---------------|
| `orphan` | in=0, out=0 | Disconnected, possibly dead code | - |
| `root` | in=0, out>0 | Entry point, initiator | Main, Handler, CLI |
| `leaf` | in>0, out=0 | Terminal node, no dependencies | DTO, Query, Config |
| `hub` | high degree | Central coordinator, coupling risk | Service, Controller |
| `internal` | in>0, out>0 | Normal flow-through node | most nodes |

This classification follows graph theory conventions where "leaf" denotes a node with no outgoing edges (nothing depends on it downstream). The term was already used implicitly in `graph_type_inference.py` before being formalized here.

### Edge (Minimal)

```json
{
  "source": "user.py:UserService",
  "target": "user.py:UserRepository",
  "edge_type": "CALLS"
}
```

### Edge Types

| Type | Meaning |
|------|---------|
| CONTAINS | Parent-child |
| CALLS | Function invocation |
| IMPORTS | Module dependency |
| INHERITS | Class inheritance |
| IMPLEMENTS | Interface realization |
| USES | General dependency |

---

## 4. PURPOSE FIELD

### Hierarchy

```
Level 4: PURPOSE FIELD     - Global gradient across codebase
Level 3: LAYER PURPOSE     - Shared purpose in architectural layer
Level 2: COMPOSITE PURPOSE - Aggregated from grouped components
Level 1: ATOMIC PURPOSE    - Intrinsic purpose of function/class
```

### Layer Flow

```
PRESENTATION    → Purpose: Display (user sees data)
      ↓
APPLICATION     → Purpose: Orchestrate (use cases happen)
      ↓
DOMAIN          → Purpose: Express (business rules enforced)
      ↓
INFRASTRUCTURE  → Purpose: Implement (technical details handled)
```

### Purpose Equations

```
π₁(node)  = role(node)
π₂(class) = emergence(Σ π₁(method))
π₃(layer) = common_purpose({π₂(component)})
Π(codebase) = ∫ π₃(layer) d(layer)
```

### Antimatter (Violations)

| Violation | Example |
|-----------|---------|
| Domain → Infrastructure | Entity imports PostgresAdapter |
| UI → Domain | Component calls repository directly |
| Test → Production | Test code in main bundle |

---

## 5. PROOFS

### Key Theorems

| ID | Name | Claim |
|----|------|-------|
| 3.1 | WHAT Completeness | Atom taxonomy covers all syntactic structures |
| 3.2 | WHY Completeness | Role taxonomy achieves 100% coverage |
| 3.3 | RPBL Boundedness | RPBL space is finite (6,561 states) |
| 3.4 | Total Space | Semantic space < 50M states |
| 3.5 | Minimality | WHAT/WHY/HOW are minimal dimensions |
| 3.6 | Orthogonality | Dimensions are statistically independent |
| 3.7 | Pipeline DAG | 18-stage pipeline is valid topological order |
| 3.8 | Schema Minimality | Canonical schema is minimal |

### Lean 4 Verification

| Theorem | File | Status |
|---------|------|--------|
| 3.3 RPBL Boundedness | `Boundedness.lean` | Verified |
| 3.4 Total Space | `Boundedness.lean` | Verified |
| 3.5 Minimality | `Minimality.lean` | Verified |
| 3.7 Pipeline DAG | `Pipeline.lean` | Verified |
| 3.8 Schema Minimality | `Schema.lean` | Verified |

**Run:** `cd proofs/lean && lake build`

### Semantic Space Calculation

```
|Σ| = |Atom| × |Role| × |RPBL|
    = 94 × 29 × 6,561
    = 17,884,806 possible states
```

---

## 6. HISTORY

### The Discovery (Dec 2025)

**Hypothesis:** Code is ambiguous → need AI to classify

**Experiment:** 91 repositories, 270,000+ nodes

**Result:** 100% coverage with 0 unknowns — WITHOUT AI

**Discovery:** Information is encoded in:
1. **Topology** - `/services/UserService.py` reveals role
2. **Frameworks** - `@Controller` decorator reveals role
3. **Genealogy** - `extends Repository` reveals role

### The Pivot (Dec 23, 2025)

| Archived (AI-centric) | Promoted (Deterministic) |
|-----------------------|--------------------------|
| LearningEngine | HeuristicClassifier |
| AutoPatternDiscovery | UniversalDetector |
| LLMClassifier | PatternMatcher |

**Core Insight:**
> The deterministic layer IS the intelligence. The LLM layer is optional enrichment.

### Timeline

| Date | Event |
|------|-------|
| 2025-12-14 | Initial commit (Spectrometer v12) |
| 2025-12-23 | THE PIVOT: AI → Deterministic |
| 2026-01-11 | Rebrand: Spectrometer → Collider |
| 2026-01-19 | Atom integration (94 atoms unified) |

---

## 7. THEORETICAL LINEAGE

```
Koestler (Holons)     → 16 LEVELS
Popper (Three Worlds) → 3 PLANES
Ranganathan (Facets)  → 8 DIMENSIONS
Clean Architecture    → LAYER dimension
DDD (Evans)           → 33 ROLES
Shannon               → M-I-P-O CYCLE
```

---

## 8. THE 10 UNIVERSAL SUBSYSTEMS

Every codebase clusters into ~10 meta-components:

1. **Ingress** - Routers, controllers, middleware
2. **Egress** - External clients, webhooks
3. **Domain Core** - Entities, rules, use-cases
4. **Persistence** - ORM, repositories, migrations
5. **Async Processing** - Queues, workers, schedulers
6. **Presentation** - UI components, view models
7. **Security** - AuthN/AuthZ, policies
8. **Observability** - Logging, metrics, tracing
9. **Configuration** - Config loading, env vars
10. **Delivery** - CI/CD pipelines, IaC
