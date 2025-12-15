# 🌌 COMPREHENSIVE THEORY: Standard Model for Computer Language

> **The Complete Reference for Code Physics v14**

This document synthesizes all discoveries, suggestions, and key concepts for understanding "what is what" across all levels of computational systems.

---

## Part 1: The Core Insight

**The useful unit of software is NOT the file.**

It's the **things inside files** (functions, classes, data structures) and the **relationships between them** (calls, imports, inheritance). Files are just packaging.

This matters for AI because LLMs can't "see" structure—they need an **explicit map**.

---

## Part 2: The 4 Scale Levels

Every entity in code exists at one of four granularity levels:

| Level | Name | What It Is | Examples |
|-------|------|------------|----------|
| **L1** | Atom | Indivisible syntax unit | Variable, Operator, Literal, Expression |
| **L2** | Molecule | Composed of atoms | Function, Method, Handler, Validator |
| **L3** | Organism | Composed of molecules | Class, Module, Service, Component |
| **L4** | Ecosystem | The whole system | Package, Repository, Microservices |

### Containment Hierarchy

```
Ecosystem (L4)
  └── Organism (L3)
        └── Molecule (L2)
              └── Atom (L1)
```

**Key Principle:** Entities at each level can share the same **PURPOSE** but differ in **granularity**.

---

## Part 3: The 8 Dimensions of Code Physics

Every particle is measured across 8 orthogonal dimensions:

| # | Dimension | Values | Question |
|---|-----------|--------|----------|
| 1 | **WHAT** | 167 atoms | What is it made of? |
| 2 | **Layer** | Interface, App, Core, Infra, Tests | Where in the stack? |
| 3 | **Role** | Orchestrator, Data, Worker | What job does it do? |
| 4 | **Boundary** | Internal, Input, I/O, Output | How does it connect? |
| 5 | **State** | Stateful, Stateless | Does it hold memory? |
| 6 | **Effect** | Read, Write, ReadModify, Pure | What does it touch? |
| 7 | **Activation** | Event, Time, Direct | How is it triggered? |
| 8 | **Lifetime** | Transient, Session, Global | How long does it live? |

### The 9th Dimension: Scale (Proposed)

```json
{
  "scale": {
    "level": "molecule",
    "parent_id": "UserService",
    "children_ids": ["validate_email", "hash_password"],
    "depth": 2
  }
}
```

---

## Part 4: The 12 Fundamental Families (Quarks)

Atoms group into 12 families based on their nature:

| Family | Phase | Purpose | Count |
|--------|-------|---------|-------|
| Bits | Data | Binary flags/masks | 2 |
| Bytes | Data | Raw byte arrays | 3 |
| Primitives | Data | Basic values (int, string, bool) | 8 |
| Variables | Data | Named storage | 5 |
| Expressions | Logic | Value-producing combinations | 8 |
| Statements | Logic | Actions (return, assert) | 10 |
| Control | Logic | Flow (if, while, for) | 10 |
| Functions | Logic | Callable units | 10 |
| Aggregates | Organization | Composite structures (class, DTO) | 6 |
| Modules | Organization | Organizational units | 4 |
| Files | Organization | File-level entities | 1 |
| Executables | Execution | Runtime entry points | 9+ |

**Total Atoms:** 167 (v14)

---

## Part 5: The 4 Phases of Matter

Families belong to 4 phases (continents):

| Phase | Color | Families | Purpose |
|-------|-------|----------|---------|
| **Data** | Cyan | Bits, Bytes, Primitives, Variables | Store information |
| **Logic** | Magenta | Expressions, Statements, Control, Functions | Process information |
| **Organization** | Green | Aggregates, Modules, Files | Structure information |
| **Execution** | Amber | Executables | Run information |

---

## Part 6: Canonical Components by Layer

Components that appear universally across codebases, organized by architectural layer:

### Interface Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Rh | Route Handler | Orchestrator | Receives HTTP requests |
| Pr | Presenter | Data | Formats output for display |
| Iv | Input Validator | Worker | Validates incoming data |
| Uw | UI Wrapper | Data | Encapsulates UI components |

### App Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Uc | Use Case | Orchestrator | Coordinates business flow |
| Pm | Process Manager | Orchestrator | Manages multi-step processes |
| Ap | App Policy | Worker | Enforces application rules |
| Am | App Mapper | Data | Transforms between layers |

### Core Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Be | Business Entity | Data | Core domain model |
| Vo | Value Object | Data | Immutable domain value |
| Bs | Core Service | Worker | Domain logic execution |
| Br | Business Rule | Worker | Domain constraint |
| De | Domain Event | Data | Domain state change signal |

### Infra Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Rp | Repository | Data | Persists/retrieves entities |
| Qo | Query Object | Data | Complex read queries |
| Ac | API Client | Worker | External API calls |
| Mp | Msg Producer | Worker | Sends messages |
| Mc | Msg Consumer | Worker | Receives messages |
| Bj | Background Job | Worker | Scheduled tasks |
| Cc | Cache | Data | Temporary storage |
| Cf | Config Loader | Data | Configuration access |
| Ff | Feature Flag | Data | Runtime toggles |
| Lg | Logger | Worker | Audit/debug output |
| Mt | Metrics | Worker | Telemetry collection |
| Sz | Serializer | Data | Data format conversion |

### Tests Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Tc | Test Case | Orchestrator | Executes assertions |
| Fx | Fixture | Data | Test data setup |
| Tr | Test Runner | Orchestrator | Executes test suites |

---

## Part 7: Cross-Level Integration (Meta-Components)

When components from different levels integrate, they form **meta-components** with shared purpose:

### Example: "User Authentication" Meta-Component

```
L4 (Ecosystem): AuthService
  └── L3 (Organism): UserAuthModule
        ├── L2 (Molecule): login_handler()
        │     ├── L1: validate_email (Expression)
        │     ├── L1: hash_password (Call)
        │     └── L1: token = jwt.encode() (Assignment)
        └── L2 (Molecule): verify_token()
              └── L1: decoded = jwt.decode() (Call)
```

**Principle:** The meta-component "Authentication" exists at ALL levels, just at different granularities.

---

## Part 8: Relationship Types (Edges)

| Edge Type | Meaning | Example |
|-----------|---------|---------|
| CONTAINS | Parent holds child | Class → Method |
| CALLS | Invokes | Function → Function |
| IMPORTS | Depends on | Module → Module |
| INHERITS | Extends | Class → BaseClass |
| IMPLEMENTS | Realizes | Class → Interface |
| READS | Accesses data | Function → Variable |
| WRITES | Mutates data | Function → Variable |
| PRODUCES | Creates output | Handler → Event |
| CONSUMES | Receives input | Handler → Event |

---

## Part 9: Complexity Metrics

| Metric | What It Measures | Threshold |
|--------|------------------|-----------|
| Cyclomatic | Branching paths | < 10 |
| Cognitive | Nesting depth | < 15 |
| Halstead Volume | Code vocabulary | < 500 |
| Depth of Inheritance | Class hierarchy | < 5 |
| Fan-In | Incoming dependencies | Context-dependent |
| Fan-Out | Outgoing dependencies | < 10 |

---

## Part 10: The Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT: Source Code                    │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 1: PARSING (Tree-Sitter)                         │
│  • AST Extraction                                        │
│  • Syntax Nodes                                          │
│  Output: Raw Atoms                                       │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: GRAPH BUILDING (NetworkX/Neo4j)               │
│  • Nodes = Components                                    │
│  • Edges = Relationships                                 │
│  Output: Dependency Graph                                │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: HEURISTIC CLASSIFICATION                      │
│  • Pattern Matching (regex, path, decorator)            │
│  • Dimensional Tagging (8D coordinates)                 │
│  Output: Classified Particles                            │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 4: LLM ESCALATION (Ollama/GPT)                   │
│  • Low-confidence (<55%) particles                      │
│  • Purpose inference                                     │
│  • Evidence validation                                   │
│  Output: Validated Classifications                       │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 5: OUTPUT GENERATION                             │
│  • 8D Particle Registry (JSON)                          │
│  • Graph Export (Mermaid, Neo4j)                        │
│  • Violation Report                                      │
│  Output: Canonical Architecture Map                      │
└─────────────────────────────────────────────────────────┘
```

---

## Part 11: Open-Source Tools Integration

| Tool | Purpose | Layer |
|------|---------|-------|
| Tree-Sitter | AST Parsing | 1 |
| Bandit | Side-effect detection (HOW) | 3 |
| import-linter | Boundary enforcement (WHERE) | 3 |
| NetworkX | In-memory graphs | 2 |
| Neo4j | Scalable graph DB | 2 |
| Ollama | Local LLM inference | 4 |

---

## Part 12: Key Principles

1. **Truth First, Meaning Second** — Parse structure before inferring roles.
2. **Evidence-Anchored Classification** — Every role claim must cite code evidence.
3. **Graceful Degradation** — If tools fail, fall back to heuristics.
4. **Universal Meta-Components** — Group by purpose, not by syntax.
5. **Scale Awareness** — Track containment and granularity explicitly.
6. **8D Coordinates** — Every particle has a complete dimensional profile.
7. **Antimatter Detection** — Flag impossible combinations (e.g., Pure + SideEffects).

---

## Part 13: Current Coverage

| Dimension | Implementation Status | Coverage |
|-----------|----------------------|----------|
| WHAT | ✅ Complete | 167 atoms |
| Layer | ✅ Complete | 5 values |
| Role | ✅ Complete | 3 values |
| Boundary | ✅ Complete | 4 values |
| State | ✅ Complete | 2 values |
| Effect | ✅ Complete | 4 values |
| Activation | ✅ Complete | 3 values |
| Lifetime | ✅ Complete | 3 values |
| Scale | ⚠️ Proposed | 4 levels |

---

## Part 14: Next Steps

1. **Implement Scale Dimension** — Add containment tracking to particle registry
2. **Build Cross-Level Aggregator** — Group particles by shared purpose
3. **Create Meta-Component Detector** — Identify universal patterns
4. **Extend Open-Source Integration** — Add more HOW/WHERE tools
5. **Build Visualization Layer** — Interactive graph navigation

---

## Part 15: The 7 Semantic Layers (GPT Model)

Entities exist across 7 orthogonal semantic layers:

| Layer | Where It Exists | Example Kinds |
|-------|-----------------|---------------|
| **Physical** | Filesystem | repo, folder, file, span |
| **Code** | Language symbols | package, module, class, function, type |
| **Runtime** | Execution | process, thread, container, invocation |
| **Deploy** | Infrastructure | image, workload, pod, service, ingress |
| **Contract** | APIs | endpoint, event topic, message schema |
| **Data** | Storage | datastore, schema, table, column, index |
| **Concept** | Domain | bounded context, aggregate, entity, value object |

### Critical Rule

> **CONTAINS is layer-local and forms a tree. Everything else is a different relation.**

This single constraint prevents 80% of "what lives inside what" confusion.

---

## Part 16: Entity Coordinates

Every entity is uniquely identified by three coordinates:

```
Entity = (Layer, Kind, Locator) + Metadata
```

| Coordinate | What It Is | Examples |
|------------|------------|----------|
| **Layer** | Where it exists | code, data, deploy, concept |
| **Kind** | What it is | code.symbol.class, data.table, contract.http_route |
| **Locator** | How to find it | fully qualified name, path + line, resourceName |

### Example Locators by Layer

| Layer | Locator Format |
|-------|----------------|
| Physical | `path + byte/line span` |
| Code | `language + FQN + signature` |
| Data | `connection-id + schema.table.column` |
| Contract | `METHOD + path` or `topic name` |
| Deploy | `cluster/ns + resourceName` |
| Runtime | `workloadRef + pid` |

---

## Part 17: Cross-Layer Correspondence (Edges)

When the "same concept" exists across layers, use correspondence edges (not CONTAINS):

| Edge Type | Meaning | Example |
|-----------|---------|---------|
| **REALIZES** | Implementation realizes concept | code.symbol REALIZES concept.use_case |
| **REPRESENTS** | Schema represents concept | contract.schema REPRESENTS concept.entity |
| **PERSISTS_AS** | Concept stored as data | concept.entity PERSISTS_AS data.table |
| **EXPOSED_AS** | Capability exposed via contract | concept.use_case EXPOSED_AS contract.http_route |
| **HANDLED_BY** | Contract handled by runtime | contract.route HANDLED_BY runtime.service |
| **OWNS** | Component owns concept/data | runtime.service OWNS concept.aggregate |

### Example: "User" Across Layers

```
concept.domain_entity: User
  │
  ├── PERSISTS_AS → data.table: users
  ├── REPRESENTS ← contract.schema: UserDTO
  └── EXPOSED_AS → contract.route: GET /users/{id}
                      │
                      └── HANDLED_BY → runtime.service: identity-api
```

---

## Part 18: Facet-Based Component Model

A **Component** is a container that collects evidence across multiple layers via facets:

| Facet | What It Captures |
|-------|------------------|
| **Code** | Entrypoints, modules, symbols |
| **Deploy** | Image, workload, env vars, replicas |
| **Runtime** | Process type, concurrency model |
| **Contract** | Routes, topics, schemas |
| **Data** | Tables, caches, queues |
| **Ops** | CI jobs, alerts, dashboards |

### Example Component

```json
{
  "id": "identity-api",
  "facets": {
    "code": ["src/server.ts", "src/routes/*"],
    "deploy": "k8s/identity-api.yaml",
    "runtime": { "type": "nodejs_http_server", "replicas": 3 },
    "contract": ["GET /users/{id}", "POST /auth/login"],
    "data": ["users", "sessions"],
    "ops": ["ci/identity.yml", "alerts/auth-failure.yaml"]
  }
}
```

---

## Part 19: The 10 Universal Subsystems

Most repositories cluster into ~10 meta-components (subsystems):

| # | Subsystem | What It Contains | Purpose |
|---|-----------|------------------|---------|
| 1 | **Ingress** | Routers, controllers, middleware, auth entrypoints | Receive requests |
| 2 | **Egress** | External clients, outbound webhooks, payment calls | Call external systems |
| 3 | **Domain Core** | Entities, rules, workflows/use-cases | Business logic |
| 4 | **Persistence** | ORM/repositories, migrations, DB adapters | Store data |
| 5 | **Async Processing** | Queues, workers, schedulers, event handlers | Background work |
| 6 | **Presentation** | UI components, view models, templates | Display data |
| 7 | **Security** | AuthN/AuthZ, policies, secret access | Protect system |
| 8 | **Observability** | Logging, metrics, tracing, alerts | Monitor health |
| 9 | **Configuration** | Config loading, env vars, runtime wiring | Configure behavior |
| 10 | **Delivery** | Build/test pipelines, packaging, IaC | Ship code |

---

## Part 20: The Core Atomic Blocks (GPT Analysis)

~8-10 atoms cover 95%+ of everyday code:

| # | Atom | Purpose | Prevalence |
|---|------|---------|------------|
| 1 | Values/Types | Represent information | 98%+ |
| 2 | Bindings (Names) | Give values stable names | 98%+ |
| 3 | Expressions | Transform data | 95%+ |
| 4 | Statements/Effects | Change state | 95%+ |
| 5 | Sequencing | Define order of actions | 95%+ |
| 6 | Selection (Branching) | Choose behavior | 95%+ |
| 7 | Repetition (Iteration) | Process collections | 95%+ |
| 8 | Abstraction (Functions) | Package behavior | 90%+ |
| 9 | Composition (Calling) | Assemble from parts | 90%+ |
| 10 | Modularity (Modules) | Control scope | 85%+ |
| 11 | Error Handling | Make failure explicit | 80%+ |
| 12 | Concurrency | Handle parallelism | 45%+ |

---

## Part 21: The Capability Model (Purpose)

The most universal cross-language primitive is **Capability**:

```
Capability = (Verb, Object, Boundary, Contract)
```

| Component | What It Is | Examples |
|-----------|------------|----------|
| **Verb** | Action performed | ingest, transform, persist, retrieve, emit, coordinate |
| **Object** | Domain noun | Order, User, File, Event, Session |
| **Boundary** | Where it runs | process, container, function, browser |
| **Contract** | Inputs/outputs | request schema, latency constraints |

### Example

A "controller," "route handler," and "lambda handler" all become:

```
Capability: Ingest(HTTP Request) → Transform(Order) → Emit(Event)
```

Different mechanisms, **same purpose**.

---

## Part 22: The Critical Design Rule

> **CONTAINS is layer-local and forms a tree. Everything else is a different relation.**

### Layer-Local Containment Trees

```
Physical:  repo → dir → file → span
Code:      package → module → class → method
Deploy:    cluster → namespace → workload → pod
Contract:  api → route → request_schema
Data:      datastore → schema → table → column
Concept:   bounded_context → aggregate → entity → value_object
```

### Never Mix Layers in CONTAINS

❌ `concept.User CONTAINS code.UserClass` — WRONG
✅ `code.UserClass REALIZES concept.User` — CORRECT

---

## Part 23: Two-Graph Architecture

Maintain two separate graphs:

| Graph | Purpose | Answers |
|-------|---------|---------|
| **Containment Graph** | Layer-pure nesting | "Where is it defined?" "What's inside what?" |
| **Architecture Graph** | Cross-layer connections | "Who owns it?" "What implements it?" |

---

## Part 24: Output Format (Canonical IR)

The output is an Intermediate Representation with two layers:

### Layer 1: Facts (High Fidelity)

```json
{
  "facts": {
    "entrypoints": [...],
    "routes": [...],
    "datastores": [...],
    "events": [...],
    "config_keys": [...]
  }
}
```

### Layer 2: Interpretation (Purpose + Components)

```json
{
  "components": [
    {
      "id": "c_ingress_http",
      "kind": "interface.http_api",
      "purpose": [{ "capability": "Ingest(HTTP)", "confidence": 0.98 }],
      "evidence": ["route:r1", "entrypoint:ep1"]
    }
  ],
  "subsystems": [
    { "id": "ss_ingress", "kind": "Ingress", "members": [...] }
  ]
}
```

---

## Part 25: Roadmap — Next Evolution

### Phase 1: Immediate (Days)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | Layer-Local CONTAINS validation | 2h | Fixes 80% confusion |
| P0 | Two-Layer IR (Facts + Interpretation) | 4h | Trustworthy output |
| P1 | Scale Dimension (9th D) | 4h | Hierarchical navigation |
| P1 | Cross-Layer Edges (REALIZES, PERSISTS_AS) | 4h | Complete architecture graph |

### Phase 2: Strategic (Weeks)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P2 | **Leiden Clustering** for auto-subsystem discovery | 1 day | 🔥 Game changer |
| P2 | LanceDB integration for vector retrieval | 1 day | Fast code search |
| P2 | Facet-Based Components | 2 days | Clean multi-layer view |
| P2 | Community Summaries (LLM-generated) | 1 day | Readable architecture |

### Phase 3: Vision (Months)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P3 | **Full GraphRAG integration** | 3 days | Global + Local queries |
| P3 | 7 Semantic Layers (replace 5-layer model) | 1 week | Theoretical completeness |
| P3 | Interactive Graph Visualization | 1 week | Human navigation |
| P3 | coAST Universal AST | 2 weeks | True polyglot support |

---

## Part 26: Key Research Citations

### Hierarchies & Graph Databases

- [Modeling Categories in a Graph Database](https://neo4j.com) - Neo4j
- [GraphRAG: Hierarchical Approach to RAG](https://lancedb.com/blog/graphrag-hierarchical-approach-to-retrieval-augmented-generation/) - LanceDB
- [Understanding Graph Databases: A Comprehensive Tutorial](https://arxiv.org) - arXiv
- [Entity understanding with hierarchical graph learning](https://sciencedirect.com) - ScienceDirect

### Managing Model Complexity

- [The Architecture of Complexity](https://medium.com) - Medium
- [What is Software Complexity?](https://vfunction.com) - vFunction
- [Code Complexity: An In-Depth Explanation and Metrics](https://blog.codacy.com) - Codacy
- [Identifying Code Complexity's Effect on Dev Productivity](https://faros.ai) - Faros AI
- [Complexity Theory in Practice](https://agility-at-scale.com) - Agility at Scale

### Hierarchical Code Analysis

- [Hierarchical Graph-Based Code Summarization](https://arxiv.org) - arXiv
- [Hierarchical Reasoning in Graph-Based RAG](https://openreview.net) - OpenReview
- [Building a Graph-Based Code Analysis Engine](https://rustic-ai.github.io) - Rustic AI

### Graph Visualization

- [Best Graph Database Visualization Tools](https://puppygraph.com) - PuppyGraph
- [15 Best Graph Visualization Tools](https://neo4j.com) - Neo4j
- [Data Analysis and Visualization](https://tomsawyer.com) - Tom Sawyer Software

### LLM + Code Analysis

- [CodexGraph](https://reddit.com) - Reddit (discussion)
- [A Graph-Integrated Large Language Model](https://openreview.net) - OpenReview
- [coala/coAST: Universal AST](https://github.com) - GitHub
- [Large Language Models for Code Analysis](https://arxiv.org) - arXiv

---

*This document is the canonical reference for the Standard Model for Computer Language v14.*

