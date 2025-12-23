# Theoretical Naming Schema: Standard Model of Code

**Version:** 2.0 (Theory Core)  
**Status:** Canonical Reference  
**Last Updated:** 2025-12-23

**Principle:** This document defines ONLY the core theoretical concepts of the Standard Model of Code. Implementation details (files, tools, scripts) are deliberately excluded as they may evolve.

---

## 1. Fundamental Theoretical Units

| Concept | Official Term | Definition |
|---------|---------------|------------|
| **Code element** | **Particle** | Any discrete unit of code (the fundamental quantum of code) |
| **Syntactic classification** | **Atom** | WHAT the particle is (1 of 167 types) |
| **Semantic classification** | **Role** | WHY the particle exists (1 of 27 purposes) |
| **Behavioral classification** | **Behavior** | HOW the particle operates (RPBL scores) |
| **Architectural classification** | **Layer** | WHERE the particle resides (Infrastructure/Domain/App/Interface) |

---

## 2. The Four Dimensions (WHAT-WHY-HOW-WHERE)

### 2.1 WHAT Dimension: Atoms
| Concept | Official Term | Cardinality | Definition |
|---------|---------------|-------------|------------|
| **Atom** | `atom` | 167 types | Syntactic classification from AST |
| **Atom Family** | `family` | 12 families | Grouping of related atoms |
| **Atom Phase** | `phase` | 4 phases | DATA, LOGIC, ORGANIZATION, EXECUTION |

**Core principle:** Atoms are objective, derivable from syntax.

### 2.2 WHY Dimension: Roles
| Concept | Official Term | Cardinality | Definition |
|---------|---------------|-------------|------------|
| **Role** | `role` | 27 types | Semantic purpose (Query, Command, Entity, etc.) |
| **Archetype** | `archetype` | ~5 groups | Grouping of related roles (CRUD, Structural, etc.) |

**Core principle:** Roles are subjective, inferred from patterns.

### 2.3 HOW Dimension: Behavior (RPBL)
| Concept | Official Term | Range | Definition |
|---------|---------------|-------|------------|
| **Responsibility** | `R` | 1-10 | Scope of duties (1=focused, 10=bloated) |
| **Purity** | `P` | 1-10 | Side-effect freedom (1=impure, 10=pure) |
| **Boundary** | `B` | 1-10 | External coupling (1=isolated, 10=entangled) |
| **Lifecycle** | `L` | 1-10 | Temporal scope (1=ephemeral, 10=persistent) |

**Core principle:** RPBL scores are measurable, objective properties.

### 2.4 WHERE Dimension: Layers
| Concept | Official Term | Position | Definition |
|---------|---------------|----------|------------|
| **Infrastructure** | `Infrastructure` | Bottom | Technical, framework, low-level |
| **Domain** | `Domain` | Core | Business logic, pure concepts |
| **Application** | `Application` | Orchestration | Use cases, workflows |
| **Interface** | `Interface` | Top | UI, API, external facing |

**Core principle:** Layers enforce separation of concerns.

---

## 3. Particle Relationships

| Concept | Official Term | Definition |
|---------|---------------|------------|
| **Dependency** | **Interaction** | One particle uses/calls another |
| **Interaction network** | **Interaction Network** | Graph of all interactions |
| **Interaction type** | `interaction_type` | CALLS, IMPORTS, INHERITS, INSTANTIATES |

**Core principle:** Interactions reveal structure.

---

## 4. Architectural Violations (Antimatter)

| Concept | Official Term | Detection Criteria | Definition |
|---------|---------------|-------------------|------------|
| **Violation** | **Antimatter** | Breaks architectural principles | Any code that violates theory |
| **God Class** | **Massive Particle** | R>8, B>8, >10 methods | Particle doing too much |
| **Layer violation** | **Layer Breach** | Lower layer → Higher layer | Infrastructure → Domain |
| **Circular dependency** | **Feedback Loop** | A → B → A | Cyclical interaction |
| **High coupling** | **Entanglement** | B>8, >20 interactions | Excessive dependencies |

**Core principle:** Antimatter = theoretical violations made manifest in code.

---

## 5. Semantic Space

| Concept | Official Term | Definition |
|---------|---------------|------------|
| **Semantic Space** | `Σ` (Sigma) | The 4D space: Atom × Role × RPBL × Layer |
| **Semantic ID** | `semantic_id` | Unique position in Σ (e.g., `LOG.FNC.M|Query|R7P9B3L5|Domain`) |
| **Space Cardinality** | `|Σ|` | 167 × 27 × 10,000 × 4 ≈ 180M possible states |

**Core principle:** Every particle maps to exactly one point in Σ.

---

## 6. Theoretical Properties

### 6.1 Completeness
| Property | Definition |
|----------|------------|
| **WHAT Completeness** | All syntactic structures map to an atom (167 atoms cover all AST nodes) |
| **WHY Completeness** | All semantic purposes map to a role (27 roles cover all intents) |
| **Boundedness** | Σ is finite (|Σ| < ∞) |

### 6.2 Minimality
| Property | Definition |
|----------|------------|
| **Dimension Independence** | WHAT ⊥ WHY ⊥ HOW (orthogonal, MI < 0.2) |
| **Non-Redundancy** | No atom/role can be derived from others |
| **Necessity** | Removing any dimension loses information |

### 6.3 Correctness
| Property | Definition |
|----------|------------|
| **Determinism** | Same input → Same output (algorithm is pure) |
| **Totality** | Algorithm always terminates with valid output |
| **Consistency** | No particle can have contradictory classifications |

---

## 7. The Pipeline (Theory)

| Concept | Official Term | Input | Output |
|---------|---------------|-------|--------|
| **Processing Stage** | `stage` | Data from previous stage | Enriched data |
| **DAG Property** | `acyclic` | Stages have topological order | No stage depends on future |
| **Information Flow** | `monotonic` | Data only accumulates | Never discarded |

**Stages (theoretical):**
1. **Classification** — Assign atoms
2. **Role Assignment** — Assign roles  
3. **Antimatter Detection** — Find violations
4. **Prediction** — Infer missing components
5. **Insight Generation** — Derive recommendations
6. **Layer Analysis** — Assign architectural layers
7. **Flow Tracing** — Map execution paths
8. **Cost Analysis** — Predict performance
9. **Proof Generation** — Validate correctness
10. **Synthesis** — Combine all dimensions

**Core principle:** Pipeline is a dependency-ordered transformation sequence.

---

## 8. Validation Concepts (Theory)

| Concept | Official Term | Definition |
|---------|---------------|------------|
| **Ground Truth** | `ground_truth` | Human-verified classifications |
| **Accuracy** | `accuracy` | Agreement with ground truth (%) |
| **Confidence** | `confidence` | Classifier certainty (0-100%) |
| **Coverage** | `coverage` | % of particles successfully classified |
| **Inter-rater Reliability** | `κ` (kappa) | Agreement between human annotators |

**Core principle:** Validation measures correctness against reality.

---

## 9. Mathematical Concepts

| Concept | Official Term | Definition |
|---------|---------------|------------|
| **Theorem** | `theorem` | Proven mathematical statement |
| **Axiom** | `axiom` | Unproven assumption (empirically validated) |
| **Proof** | `proof` | Logical derivation |
| **Mechanized Proof** | `mechanized_proof` | Machine-verified proof (Lean 4) |
| **Mutual Information** | `MI` | Statistical independence measure (bits) |
| **Orthogonality** | `⊥` | Dimensions are independent (MI < threshold) |

**Core principle:** Mathematics grounds the theory in rigor.

---

## 10. Quality Metrics (Theory)

| Metric | Official Term | Range | Interpretation |
|--------|---------------|-------|----------------|
| **Atomic Compliance** | `atomic_compliance` | 0-100 | How well code follows SM principles |
| **Antimatter Density** | `antimatter_density` | 0-1 | Fraction of particles that are violations |
| **Classification Confidence** | `avg_confidence` | 0-100% | Average certainty across all particles |
| **Dimension Orthogonality** | `MI(D₁, D₂)` | 0-∞ bits | Independence of dimensions |

---

## 11. Core Abbreviations (Theory)

| Symbol | Full Name | Meaning |
|--------|-----------|---------|
| **Σ** | Sigma (Semantic Space) | The 4D classification space |
| **RPBL** | Responsibility-Purity-Boundary-Lifecycle | Behavioral dimensions |
| **MI** | Mutual Information | Statistical independence |
| **⊥** | Orthogonal | Independent dimensions |
| **DAG** | Directed Acyclic Graph | Pipeline structure |

---

## 12. Particle States (Theory)

| State | Official Term | Definition |
|-------|---------------|------------|
| **Classified** | `classified` | Has complete classification (atom + role + behavior + layer) |
| **Partial** | `partial` | Missing one or more dimensions |
| **Confident** | `confident` | Classification confidence >75% |
| **Uncertain** | `uncertain` | Classification confidence <50% |
| **Violated** | `antimatter` | Fails architectural constraints |

---

## 13. Glossary (Theoretical Core)

| Term | One-Sentence Definition |
|------|------------------------|
| **Particle** | A discrete quantum of code |
| **Atom** | WHAT the particle is (syntactic type) |
| **Role** | WHY the particle exists (semantic purpose) |
| **Behavior** | HOW the particle operates (RPBL) |
| **Layer** | WHERE the particle resides (architectural tier) |
| **Interaction** | Dependency between particles |
| **Antimatter** | Code violating architectural principles |
| **Massive Particle** | Particle doing too much (God Class) |
| **Semantic Space (Σ)** | 4D classification space |
| **Semantic ID** | Unique coordinates in Σ |
| **Layer Breach** | Violation of layering (upward dependency) |
| **Entanglement** | Excessive coupling between particles |
| **Feedback Loop** | Circular dependency |
| **Orthogonality** | Dimensions are independent |
| **Completeness** | All code can be classified |
| **Minimality** | No redundant dimensions |

---

**This is the eternal theoretical core. Implementation may change, theory endures.**
