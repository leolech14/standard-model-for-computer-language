# The Standard Model for Computer Language

## A Graph-Theoretic Framework for Semantic Code Analysis and Architectural Pattern Detection

**Leonardo Brockstedt Lech**  
Independent Research  
December 2025

---

## Abstract

We present the **Standard Model for Computer Language**, a comprehensive framework for representing, classifying, and analyzing software systems as multi-dimensional graph structures. Drawing inspiration from particle physics taxonomy, we propose a hierarchical ontology comprising **167 atomic code constructs** organized into **12 families** across **4 phases**, measured along **8 orthogonal semantic dimensions**. We map these atoms to **152 Tree-Sitter AST node types** across JavaScript, TypeScript, and Python.

We implement this model in the **Spectrometer** tool and validate it against **35,263 code entities** across 3 production codebases, achieving **100% classification coverage** with zero unmapped constructs. The framework successfully identifies architectural violations, God Functions, semantic duplicates, and refactoring opportunities with high precision.

**Keywords:** software architecture, static analysis, graph theory, semantic classification, code quality

---

## 1. Introduction

The fundamental challenge of modern software engineering is not writing code—it is **understanding code**. As systems grow in complexity, the ability to navigate, reason about, and modify existing codebases becomes the limiting factor in development velocity.

Traditional approaches rely on two extremes:

1. **Textual analysis** — treating code as natural language (fast but shallow)
2. **Full semantic analysis** — building complete type systems and execution traces (deep but intractable)

We propose a **middle path**: a graph-theoretic semantic model that captures the essential structure of software without requiring full program execution.

### Key Insight

> The useful unit of software is not the file—it is the **entities inside files** (functions, classes, types) and the **relationships between them** (calls, imports, inheritance).

### Contributions

1. A **167-atom ontology** for classifying code constructs
2. An **8-dimensional coordinate system** for semantic properties
3. A **4-level scale hierarchy** (Atom, Molecule, Organism, Ecosystem)
4. **152 Tree-Sitter AST node mappings** for language-agnostic extraction
5. **Empirical validation** on 35,263 code entities with 100% coverage
6. The **Spectrometer** implementation demonstrating practical application

---

## 2. The Standard Model

### 2.1 Scale Levels

Particles exist at four levels of granularity:

| Level | Name | Description | Examples |
|-------|------|-------------|----------|
| L1 | **Atom** | Indivisible unit | Variable, Literal, Expression |
| L2 | **Molecule** | Composed of atoms | Function, Method, Handler |
| L3 | **Organism** | Composed of molecules | Class, Module, Service |
| L4 | **Ecosystem** | The whole system | Package, Repository |

### 2.2 The 12 Families (167 Atoms)

Atoms group into 12 families across 4 phases:

![Taxonomy Chart](paper_charts/fig1_taxonomy.png)

**Figure 1.** The 167-atom taxonomy organized by phase and family. LOGIC phase dominates with 61 atoms, reflecting the primacy of behavioral constructs in software.

| Phase | Families | Atoms | Description |
|-------|----------|------:|-------------|
| **DATA** | Bits, Bytes, Primitives, Variables | 26 | The matter of software |
| **LOGIC** | Expressions, Statements, Control, Functions | 61 | The forces of software |
| **ORGANIZATION** | Aggregates, Services, Modules, Files | 45 | The structure of software |
| **EXECUTION** | Handlers, Workers, Initializers, Probes | 35 | The dynamics of software |
| **TOTAL** | 12 families | **167** | |

#### Definition 1 (Atom)

An **atom** is a language-agnostic semantic construct that:
- Maps to one or more Tree-Sitter AST node types
- Has a unique ID of form `PHASE.FAMILY.LEVEL` (e.g., `LOG.FNC.M`)
- Cannot be decomposed without losing semantic information essential to the 8-dimensional model

### 2.3 The 8 Dimensions

Every particle is measured across 8 orthogonal semantic dimensions:

![Dimensions Radar](paper_charts/fig5_dimensions.png)

**Figure 2.** The 8-dimensional semantic coordinate system. WHAT (167 types) provides the richest discrimination; State (2 types) provides the coarsest.

| # | Dimension | Domain | Values |
|---|-----------|--------|--------|
| 1 | **WHAT** | Atom types | 167 types (see §2.2) |
| 2 | **Layer** | Architectural position | Interface, Application, Core, Infrastructure, Test |
| 3 | **Role** | Functional purpose | Orchestrator, Data, Worker, Utility |
| 4 | **Boundary** | Connection type | Internal, Input, I/O, Output |
| 5 | **State** | Memory behavior | Stateful, Stateless |
| 6 | **Effect** | Side effects | Pure, Read, Write, ReadModify |
| 7 | **Activation** | Trigger mechanism | Direct, Event, Time |
| 8 | **Lifetime** | Temporal scope | Transient, Session, Global |

#### Definition 2 (Dimension)

Each dimension D is a partial function returning a value and confidence score:

```
D: Particle → Domain(D) × [0,1]
```

Dimensions are **conceptually orthogonal**: the value of one dimension cannot be deterministically derived from others.

---

## 3. Antimatter Detection

A key principle is **antimatter detection**: identifying impossible combinations of dimensional values.

### Definition 3 (Antimatter Law)

An antimatter law is a first-order constraint over particles, dimensions, and edges:

```
∀p ∈ Particles: Effect(p) = Pure ⇒ ¬∃q: (p, WRITES, q) ∈ Edges
```

### Canonical Antimatter Laws

| # | Law | Violation Type |
|---|-----|----------------|
| 1 | Pure function with WRITES edges | Effect contradiction |
| 2 | Stateless service with mutable fields | State contradiction |
| 3 | Core layer depending on Interface layer | Layer violation |
| 4 | Value Object with setter methods | Immutability violation |

### Detection Results

![Antimatter Chart](paper_charts/fig6_antimatter.png)

**Figure 3.** Antimatter detection in the ATMAN production codebase. 1,102 semantic duplicates indicate significant refactoring opportunity.

---

## 4. Graph Representation

Each particle is a **node** with properties:

```
Node: {
  id: string,
  name: string,
  kind: AtomType,
  file: string,
  in_degree: number,
  out_degree: number,
  dimensions: {
    layer: Layer,
    role: Role,
    effect: Effect,
    ...
  }
}
```

### Edge Types

| Edge | Description | Example |
|------|-------------|---------|
| CONTAINS | Parent holds child | Class → Method |
| CALLS | Function invokes function | handleApi → syncConnection |
| IMPORTS | Module depends on module | app.tsx → utils.ts |
| INHERITS | Class extends class | UserService → BaseService |
| IMPLEMENTS | Class realizes interface | Repository → IRepository |
| READS/WRITES | Data access | function → database |

---

## 5. Implementation: Spectrometer

The 5-layer pipeline:

1. **PARSING** (Tree-Sitter): Extract AST from source files
2. **GRAPH BUILDING**: Construct nodes and edges
3. **HEURISTIC CLASSIFICATION**: Pattern matching for 30+ semantic rules
4. **LLM ESCALATION**: AI inference for low-confidence cases (<55%)
5. **OUTPUT GENERATION**: JSON, Mermaid diagrams, Markdown reports

### Language Support

| Language | AST Nodes Mapped | Coverage |
|----------|-----------------|----------|
| JavaScript | 91 | ~95% |
| TypeScript | 107 | ~95% |
| Python | 62 | ~90% |
| **Total** | **152** | |

---

## 6. Empirical Evaluation

### 6.1 Validation Dataset

We validated the 167-atom taxonomy against 3 codebases:

![Validation Chart](paper_charts/fig2_validation.png)

**Figure 4.** Validation dataset: 35,263 code entities across 3 codebases. 100% mapped to the 167-atom taxonomy.

| Codebase | Language | Files | Entities | Coverage |
|----------|----------|------:|--------:|----------|
| Poetry | Python | 436 | 1,284 | 100% |
| Spectrometer | Python+JS | 8,411 | 24,654 | 100% |
| ATMAN | Node.js | 178 | 9,325 | 100% |
| **Total** | — | **9,025** | **35,263** | **100%** |

**Result:** Zero unmapped constructs across all codebases.

### 6.2 Phase Distribution

![Distribution Chart](paper_charts/fig3_distribution.png)

**Figure 5.** Phase distribution of 35,263 code entities. LOGIC (75.1%) dominates, reflecting the behavioral nature of software.

| Phase | Entities | Percentage |
|-------|--------:|-----------:|
| LOGIC | 26,476 | 75.1% |
| ORGANIZATION | 8,173 | 23.2% |
| EXECUTION | 614 | 1.7% |

### 6.3 Graph Metrics

![Graph Metrics](paper_charts/fig4_graph_metrics.png)

**Figure 6.** Graph complexity by codebase. Edge-to-node ratio ranges from 1.6 (ATMAN) to 2.3 (Poetry), indicating varying coupling density.

| Codebase | Nodes | Edges | E/N Ratio |
|----------|------:|------:|----------:|
| Poetry | 3,441 | 7,860 | 2.28 |
| Spectrometer | 49,471 | 79,494 | 1.61 |
| ATMAN | 18,655 | 29,689 | 1.59 |

### 6.4 Key Findings (ATMAN Case Study)

| Finding | Metric | Implication |
|---------|--------|-------------|
| God Function | `handleApi` (489 calls) | Single point of failure |
| God Component | `App.tsx` (2,908 lines) | Decomposition needed |
| Semantic Duplicates | 1,102 groups | Consolidation opportunity |
| Structural Duplicates | 48 groups | Shared utility extraction |

---

## 7. Theoretical Properties

### Property 1 (Totality)

Every Tree-Sitter AST node of interest maps to at least one atom in A.

### Property 2 (Well-Formedness)

The CONTAINS edge relation forms a forest with unique roots:

```
(P, E_CONTAINS) is acyclic ∧ each component has unique root
```

### Property 3 (Monotonicity)

Adding files cannot invalidate existing dimension assignments:

```
S ⊆ S' ⇒ ∀p ∈ S: D(p)_S = D(p)_S'
```

### Property 4 (Compositionality)

Organism-level dimensions derive from constituent molecules:

```
State(organism) = Stateful ⟺ ∃m ∈ molecules(organism): State(m) = Stateful
```

---

## 8. Conclusion

The **Standard Model for Computer Language** provides a principled, graph-theoretic framework for understanding software structure. By treating code as **matter with measurable properties across 8 dimensions**, we enable systematic detection of architectural patterns and violations.

The physics metaphor provides a memorable vocabulary. The true value lies in the underlying graph model:
- **Nodes** represent entities
- **Edges** represent relationships  
- **Dimensions** capture semantic meaning
- **Antimatter laws** encode architectural constraints

### Future Work

1. **Extended language support** (Java, Go, Rust, C++)
2. **Automated refactoring** based on antimatter detection
3. **GraphRAG integration** for codebase Q&A
4. **IDE plugins** for real-time architectural feedback

---

## References

[1] Lehman, M. M. (1980). "Programs, Life Cycles, and Laws of Software Evolution." *Proc. IEEE*.

[2] Ferrante, J., Ottenstein, K. J., & Warren, J. D. (1987). "The program dependence graph and its use in optimization." *ACM TOPLAS*.

[3] Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.

[4] Traag, V. A., Waltman, L., & van Eck, N. J. (2019). "From Louvain to Leiden: guaranteeing well-connected communities." *Scientific Reports*.

[5] Edge et al. (2024). "From Local to Global: A Graph RAG Approach to Query-Focused Summarization." *arXiv preprint*.

---

## Appendix A: Atom Reference

The complete 167-atom taxonomy is available at:

`https://github.com/leolech14/standard-model-for-computer-language/blob/main/ATOMS_REFERENCE.md`

---

**Code & Data Availability**

Spectrometer is open source:  
`https://github.com/leolech14/standard-model-for-computer-language`

---

*Probing the deep structure of code.*
