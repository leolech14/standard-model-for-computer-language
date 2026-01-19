[Home](../README.md) > [Docs](./README.md) > **Glossary**

---

# Glossary

Key terms used throughout the Standard Model documentation.

---

## Core Concepts

| Term | Definition |
|------|------------|
| **Atom** | The fundamental unit of code structure. Every code element (function, class, variable) is classified as an atom. |
| **Codespace** | The hyperdimensional semantic space where all software artifacts exist and relate. |
| **Collider** | The implementation tool that applies Standard Model theory to real codebases. |
| **Standard Model of Code** | The theoretical framework — a periodic table for software. |

## The 4 Phases

| Phase | Contains | Purpose |
|-------|----------|---------|
| **DATA** | Bits, Bytes, Primitives, Variables | The matter of software |
| **LOGIC** | Expressions, Statements, Control, Functions | The forces of software |
| **ORGANIZATION** | Aggregates, Services, Modules, Files | The structure of software |
| **EXECUTION** | Handlers, Workers, Initializers, Probes | The dynamics of software |

## Analysis Concepts

| Term | Definition |
|------|------------|
| **Antimatter** | Violations of architectural laws (e.g., Domain→Infrastructure dependency). |
| **Dead Code** | Nodes unreachable from any entry point. |
| **Edge** | A dependency relationship between two nodes. |
| **God Class** | A node with excessive dependencies (high hub score). |
| **Knot** | A circular dependency pattern. |
| **Layer** | Architectural placement: Domain, Infrastructure, Application, UI. |
| **Node** | A code element in the graph (function, class, module). |
| **Orphan** | A node with no incoming or outgoing edges. |
| **Role** | Canonical behavior pattern (Repository, Entity, Controller, etc.). |
| **Topology** | The shape of the dependency graph (Star, Mesh, Hierarchical, Islands). |

## RPBL Scoring

| Dimension | Measures |
|-----------|----------|
| **R** - Responsibility | How focused is this code? (Single vs. multiple concerns) |
| **P** - Purity | How side-effect-free? (Pure functions vs. I/O heavy) |
| **B** - Boundary | How well-encapsulated? (Clean interfaces vs. leaky abstractions) |
| **L** - Lifecycle | How stable? (Long-lived vs. frequently changing) |

## Architecture Terms

| Term | Definition |
|------|------------|
| **Analysis** | Code → Graph transformation (implemented). |
| **Bidirectionality** | The ability to transform in both directions (code ↔ graph). |
| **Deterministic Core** | The algorithmic analysis layer — reproducible, no AI. |
| **Grip Layer** | The AI-facing communication interface. |
| **LLM Enrichment** | Optional AI layer for natural language summaries. |
| **Synthesis** | Graph → Code transformation (not yet implemented). |

---

See also: [THEORY_MAP](./THEORY_MAP.md) for how these concepts relate.
