# Scale Terminology: The 16 Levels

**Version:** 1.0.0
**Purpose:** Define what we call entities at each level of the scale

---

## The Problem

We have a 16-level scale from BIT to UNIVERSE. But when analyzing a codebase, we need **consistent terminology** for the entities we encounter.

This document establishes the canonical terms.

---

## The Scale (Revised)

| Level | Term | Zone | Definition |
|-------|------|------|------------|
| **L12** | UNIVERSE | Cosmological | All code ever written |
| **L11** | DOMAIN | Cosmological | A field (e.g., "web development", "finance") |
| **L10** | ORGANIZATION | Cosmological | A company/team's entire output |
| **L9** | PLATFORM | Cosmological | A product family (e.g., AWS, Google Cloud) |
| **L8** | ECOSYSTEM | Cosmological | A repository - **PROJECT_elements** |
| **L7** | SYSTEM | Systemic | A Holon - autonomous bounded unit |
| **L6** | PACKAGE | Systemic | A Subsystem - functional grouping |
| **L5** | MODULE | Systemic | A File - single source file |
| **L4** | CONTAINER | Semantic | A Class or major structure |
| **L3** | NODE | Semantic | A Function or method |
| **L2** | BLOCK | Semantic | A control flow unit |
| **L1** | STATEMENT | Semantic | A single executable line |
| **L0** | TOKEN | Syntactic | A lexical unit |
| **L-1** | CHARACTER | Physical | A single character |
| **L-2** | BYTE | Physical | 8 bits |
| **L-3** | BIT | Physical | Binary digit |

---

## The Working Vocabulary

For everyday use, we focus on **L3-L8** (the analyzable range):

| When you say... | You mean... | Level |
|-----------------|-------------|-------|
| "the project" | Ecosystem | L8 |
| "Collider" | System | L7 |
| "the Registry subsystem" | Package | L6 |
| "analyze.py" | Module | L5 |
| "the AtomClassifier class" | Container | L4 |
| "the classify() function" | Node | L3 |

---

## Mapping to PROJECT_elements

### L8: ECOSYSTEM

```
PROJECT_elements
├── Identity: "Standard Model of Code + Collider"
├── Purpose: "Find the basic constituents of computer programs"
├── Boundary: The git repository
└── Contains: 5 Systems
```

### L7: SYSTEM (The Realms)

```
Collider (Particle Realm)
├── Identity: "The analysis engine"
├── Purpose: "Collapse wave function → concrete analysis"
├── Boundary: standard-model-of-code/
└── Contains: 2 Packages (S1, S9)

Wave (Intelligence Realm)
├── Identity: "The AI layer"
├── Purpose: "Potential, research, enrichment"
├── Boundary: context-management/
└── Contains: 6 Packages (S2, S3, S4, S9b, S11, S12)

Observer (Governance Realm)
├── Identity: "The decision layer"
├── Purpose: "State, tasks, coordination"
├── Boundary: .agent/
└── Contains: 4 Packages (S5, S6, S7, S10)

Archive (Dormant)
├── Identity: "Historical record"
├── Purpose: "Preservation"
├── Boundary: archive/
└── Contains: Legacy code

External (Dependencies)
├── Identity: "Third-party tools"
├── Purpose: "Supporting infrastructure"
├── Boundary: related/
└── Contains: chrome-mcp
```

### L6: PACKAGE (Subsystems)

Current inventory: **12 subsystems**

| ID | Name | System | Primary Module | Purpose |
|----|------|--------|----------------|---------|
| S1 | Collider Core | Particle | `full_analysis.py` | Semantic analysis |
| S2 | HSL | Wave | `HOLOGRAPHIC_SOCRATIC_LAYER.md` | Validation rules |
| S3 | Analyzer | Wave | `analyze.py` | AI queries |
| S4 | Perplexity | Wave | `perplexity_mcp_server.py` | External knowledge |
| S5 | Registry | Observer | `registry/` | Task tracking |
| S6 | BARE | Observer | `bare/` | Auto-refinement |
| S7 | Archive | Observer | `archive.py` | Cloud sync |
| S8 | Hygiene | Observer | `.pre-commit-config.yaml` | Commit guards |
| S9 | Laboratory | Particle | `laboratory.py` | Experiment API |
| S9b | Lab Bridge | Wave | `laboratory_bridge.py` | Cross-realm bridge |
| S10 | Enrichment | Observer | `enrichment_orchestrator.py` | Task enrichment |
| S11 | Refinery | Wave | `refinery/` | Context atomization |
| S12 | Centripetal | Wave | `centripetal_scan.py` | Deep analysis |

### L5: MODULE (Files)

Approximately 500 active source files across the three Systems.

### L4-L3: CONTAINER and NODE

These are what Collider analyzes:
- ~1,200 Containers (classes)
- ~12,000 Nodes (functions/methods)

---

## Terminology Rules

### Rule 1: Use the Level Term

| Instead of... | Say... |
|---------------|--------|
| "the codebase" | "the Ecosystem" |
| "a folder" | "a System or Package" (depending on level) |
| "a file" | "a Module" |
| "a class" | "a Container" |
| "a function" | "a Node" |

### Rule 2: Qualify When Ambiguous

When discussing multiple levels:
- "S1 (Package)" not just "S1"
- "analyze.py (Module)" not just "analyze.py"
- "Collider (System)" not just "Collider"

### Rule 3: The Holon Relationship

Every entity is both:
- A **whole** containing parts (top-down view)
- A **part** within a larger whole (bottom-up view)

Collider is a System (whole) containing Packages.
Collider is also a part of PROJECT_elements (Ecosystem).

This is Koestler's Holon concept made practical.

---

## Visual Summary

```
                    ┌─────────────────────────────────────┐
                    │  L8: ECOSYSTEM                       │
                    │  PROJECT_elements                    │
                    │  "Standard Model of Code"            │
                    └───────────────┬─────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │ L7: SYSTEM│           │ L7: SYSTEM│           │ L7: SYSTEM│
    │ Collider  │           │   Wave    │           │ Observer  │
    │ (Particle)│           │           │           │           │
    └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
          │                       │                       │
    ┌─────┴─────┐           ┌─────┴─────┐           ┌─────┴─────┐
    │L6: PACKAGE│           │L6: PACKAGE│           │L6: PACKAGE│
    │ S1, S9    │           │S2,S3,S4...│           │S5,S6,S7...│
    └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
          │                       │                       │
    ┌─────┴─────┐           ┌─────┴─────┐           ┌─────┴─────┐
    │L5: MODULE │           │L5: MODULE │           │L5: MODULE │
    │ .py files │           │ .py files │           │ .py files │
    └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │ L4: CONTAINER (classes)   │
                    │ L3: NODE (functions)      │
                    │ L2: BLOCK (control flow)  │
                    │ L1: STATEMENT (lines)     │
                    └───────────────────────────┘
```

---

## Application

When Collider runs, it primarily operates at **L3-L5** (Node, Container, Module).

When we discuss architecture, we operate at **L6-L8** (Package, System, Ecosystem).

The SoS map documents **L6** (Packages/Subsystems) and their integrations.

The SELF_PORTRAIT documents the full **L3-L8** range.

---

## Open Questions

1. Should "Realm" (Particle/Wave/Observer) be a named level between System and Ecosystem?
2. Are S13-S15 (Strategy, Symmetry, Telemetry) valid new Packages or should they merge?
3. How do we handle cross-level references (e.g., a Node calling into another System)?

---

*This terminology is canonical for PROJECT_elements and should be used consistently in all documentation.*
