# Prior Art - Standard Model of Code

> **Purpose:** Bibliography of referenced works and what was incorporated.
> **Last Updated:** 2026-01-24

---

## Category 1: Foundational Theory

### Koestler, Arthur - "The Ghost in the Machine" (1967)
- **Concept:** Holons - entities that are simultaneously wholes and parts
- **What we took:** The holon concept for our 16-level scale
- **What we added:** Specific application to code, 16 concrete levels (Bit → Universe)
- **Citation:** Koestler, A. (1967). The Ghost in the Machine. Hutchinson.

### Popper, Karl - "Three Worlds" (1978)
- **Concept:** World 1 (physical), World 2 (mental), World 3 (abstract objects)
- **What we took:** Tripartite ontology framework
- **What we added:** Mapping to Physical/Virtual/Semantic planes for code
- **Citation:** Popper, K. (1978). Three Worlds. The Tanner Lecture on Human Values.

### Ranganathan, S.R. - "Colon Classification" (1933)
- **Concept:** Faceted classification with PMEST (Personality, Matter, Energy, Space, Time)
- **What we took:** Idea of orthogonal classification dimensions
- **What we added:** 8 code-specific dimensions, statistical orthogonality proof
- **Citation:** Ranganathan, S.R. (1933). Colon Classification. Madras Library Association.

---

## Category 2: Software Architecture

### Evans, Eric - "Domain-Driven Design" (2003)
- **Concept:** Entity, ValueObject, Repository, Service, Factory, Aggregate
- **What we took:** Vocabulary for role taxonomy
- **What we added:** Extended to 33 roles, formal taxonomy structure
- **Citation:** Evans, E. (2003). Domain-Driven Design. Addison-Wesley.

### Martin, Robert C. - "Clean Architecture" (2017)
- **Concept:** Dependency rule, layer separation, boundaries
- **What we took:** Layer dimension concept (Presentation, Application, Domain, Infrastructure)
- **What we added:** RPBL character, purpose field, Q-metrics
- **Citation:** Martin, R.C. (2017). Clean Architecture. Prentice Hall.

### Gamma et al. - "Design Patterns" (1994)
- **Concept:** 23 design patterns (Factory, Builder, etc.)
- **What we took:** Pattern vocabulary for role classification
- **What we added:** Integration into unified role taxonomy, purpose emergence
- **Citation:** Gamma, E., Helm, R., Johnson, R., Vlissides, J. (1994). Design Patterns. Addison-Wesley.

---

## Category 3: Software Metrics

### McCabe, Thomas - "Cyclomatic Complexity" (1976)
- **Concept:** Complexity measure based on control flow graph
- **What we took:** Cyclomatic complexity as input to elevation function
- **What we added:** Integration into landscape metaphor, gradient risk classification
- **Citation:** McCabe, T.J. (1976). A Complexity Measure. IEEE Transactions on Software Engineering.

### Halstead, Maurice - "Software Science" (1977)
- **Concept:** Metrics based on operators and operands
- **What we took:** Awareness of metrics landscape
- **What we added:** Different approach (structural vs. vocabulary-based)
- **Citation:** Halstead, M.H. (1977). Elements of Software Science. Elsevier.

### Chidamber & Kemerer - "OO Metrics" (1994)
- **Concept:** WMC, DIT, NOC, CBO, RFC, LCOM
- **What we took:** Awareness of OO-specific metrics
- **What we added:** Language-agnostic approach via atoms/roles
- **Citation:** Chidamber, S.R., Kemerer, C.F. (1994). A Metrics Suite for OOD. IEEE TSE.

---

## Category 4: Systems Theory

### Bejan, Adrian - "Constructal Law" (1996)
- **Concept:** "For a finite-size system to persist, it must evolve to provide easier access to currents flowing through it"
- **What we took:** Flow must branch to persist - applies to code topology
- **What we added:** Application to dependency graph evolution
- **Citation:** Bejan, A. (1996). Constructal-theory network of conducting paths. Int. J. Heat Mass Transfer.

### Beer, Stafford - "Viable System Model" (1972)
- **Concept:** System 1-5 hierarchy for organizational viability
- **What we took:** Hierarchical system organization concept
- **What we added:** Mapping to code layers and purpose emergence
- **Citation:** Beer, S. (1972). Brain of the Firm. Allen Lane.

### Haken, Hermann - "Synergetics" (1977)
- **Concept:** Order parameters, slaving principle in self-organizing systems
- **What we took:** Hubs as order parameters concept
- **What we added:** Application to code graph structure
- **Citation:** Haken, H. (1977). Synergetics: An Introduction. Springer.

---

## Category 5: Graph Theory & Topology

### Euler, Leonhard - "Graph Theory" (1736)
- **Concept:** Nodes, edges, degree, connectivity
- **What we took:** Basic graph concepts
- **What we added:** Topology roles, disconnection taxonomy
- **Citation:** Euler, L. (1736). Solutio problematis ad geometriam situs pertinentis.

### Betti, Enrico - "Betti Numbers" (1871)
- **Concept:** Topological invariants (b₀ = components, b₁ = cycles)
- **What we took:** Betti number computation
- **What we added:** Mapping to code health signals
- **Citation:** Betti, E. (1871). Sopra gli spazi di un numero qualunque di dimensioni.

---

## Category 6: Code Quality

### Fowler, Martin & Beck, Kent - "Code Smells" (1999)
- **Concept:** Heuristic indicators of problematic code
- **What we took:** Smell categories concept
- **What we added:** Formalized 7-category pathogen taxonomy with detection rules
- **Citation:** Fowler, M. (1999). Refactoring: Improving the Design of Existing Code. Addison-Wesley.

### Cunningham, Ward - "Technical Debt" (1992)
- **Concept:** Debt metaphor for deferred code quality
- **What we took:** Debt concept
- **What we added:** Quantification via elevation/gradient metrics
- **Citation:** Cunningham, W. (1992). The WyCash Portfolio Management System. OOPSLA.

---

## Category 7: Industry Practice

### McAfee, John - "VirusScan" (1987)
- **Concept:** Signature-based malware detection, heuristic analysis
- **What we took:** Detection paradigm (signatures + heuristics)
- **What we added:** Application to code health (not malware), pathogen taxonomy
- **Note:** Name "John McAfee" for our system is INTERNAL ONLY due to trademark concerns

### SonarQube - Code Quality Platform
- **Concept:** Multi-language static analysis, quality gates
- **What we took:** Awareness of industry practice
- **What we added:** Unified theory (they have rules, we have physics)

---

## What We Did NOT Take

| Concept | Source | Why Not Used |
|---------|--------|--------------|
| Machine learning classification | Various | Deterministic pivot - AI is optional enrichment |
| Language-specific patterns | Various | Language-agnostic via Tree-sitter |
| Runtime analysis | Profilers | Static analysis only (for now) |
| Manual pattern definition | Many tools | Discovered, not defined |

---

## Novelty Gap Summary

| Domain | Prior Art | Our Contribution |
|--------|-----------|------------------|
| **Classification** | Scattered taxonomies | Unified 94-atom, 33-role system |
| **Dimensions** | Ad-hoc metrics | 8 orthogonal, proven independent |
| **Purpose** | Not formalized | π-field with emergence levels |
| **Health** | Individual metrics | Unified H = T + E + Gd + A formula |
| **Pathogens** | Code smells (informal) | 7-category formal taxonomy |
| **Coverage** | Partial, AI-dependent | 100% deterministic coverage |

---

## Version

| Field | Value |
|-------|-------|
| Document Version | 1.0.0 |
| Last Updated | 2026-01-24 |
