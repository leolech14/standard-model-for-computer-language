# Standard Model of Code: Theory Index

**Status:** ACTIVE | CANONICAL
**Version:** 2.0.0 (Unified Theory Stack)
**Created:** 2026-01-27
**Purpose:** Single entry point for ALL Standard Model theory

---

## What This Is

The **Standard Model of Code** is a formal framework for understanding software structure. It treats code like physics treats matter: atoms, dimensions, fields, emergence.

### The Core Insight

> Code is not ambiguous. 100% of code structure can be classified **deterministically, WITHOUT AI**. Information is encoded in topology, frameworks, and genealogy.

The Standard Model provides:
- **Atoms**: 3,525 classified types (80 core structural + 3,445 ecosystem-specific)
- **Dimensions**: 8-axis coordinate system (KIND, LAYER, ROLE, BOUNDARY, STATE, EFFECT, LIFECYCLE, TRUST)
- **Levels**: 16-level holarchy from L-3 (BIT) to L12 (UNIVERSE)
- **Purpose**: Graph-derived teleology (what code is FOR, not just WHAT it is)

---

## The Theory Stack (Read in Order)

The complete theory is organized as a **four-layer holarchy**, where each layer is a WHOLE when looking down and a PART when looking up:

| Layer | Document | Question Answered | Lines | Status |
|-------|----------|-------------------|-------|--------|
| **L0** | `L0_AXIOMS.md` | What MUST be true? | ~900 | VALIDATED |
| **L1** | `L1_DEFINITIONS.md` | What EXISTS in this theory? | ~700 | ACTIVE |
| **L2** | `L2_LAWS.md` | How do things BEHAVE? | ~800 | ACTIVE |
| **L3** | `L3_APPLICATIONS.md` | How do we MEASURE it? | ~600 | EVOLVING |

### Layer Dependencies

```
L3 (Applications)     <- Depends on: L2, L1, L0
   ↑
L2 (Laws)             <- Depends on: L1, L0
   ↑
L1 (Definitions)      <- Depends on: L0
   ↑
L0 (Axioms)           <- Depends on: Nothing (bedrock)
```

**No circular dependencies.** Each layer references only layers below it.

---

## Layer 0: AXIOMS (The Bedrock)

**File:** `L0_AXIOMS.md`

**What's inside:**
- Primitive notions (P, N, E, L, executable predicate)
- 8 axiom groups (A: Set Structure, B: Graph, C: Levels, D: Purpose, E: Constructal, F: Emergence, G: Observability, H: Consumer Classes)
- Mathematical foundations (category theory, semiotics, fundamentality)
- The Lawvere proof (why MECE partition is mathematically necessary)
- Validation results table

**Key axioms:**
- **A1**: P = C ⊔ X (PROJECTOME = CODOME ⊔ CONTEXTOME)
- **B1**: Code is a directed graph (N, E)
- **C1**: Levels form a total order (L-3 < ... < L12)
- **D1**: Purpose field exists (π: N → Purpose)
- **E1**: Code evolves to facilitate flow (Constructal)
- **F1**: Properties emerge at level transitions

**Status:** Most validated theory in the stack. Lawvere proof in A1.1 is peer-reviewed mathematics.

---

## Layer 1: DEFINITIONS (Complete Enumeration)

**File:** `L1_DEFINITIONS.md`

**What's inside:**
1. The Three Planes (Physical, Virtual, Semantic / Popper)
2. The 16-Level Scale (L-3 through L12, zones, holarchy)
3. The -ome Partition (Projectome, Codome, Contextome, Concordances)
4. Classification System (Atoms, Phases, Roles, Dimensions, RPBL)
5. Graph Elements (Nodes, Edges, Topology roles, Disconnection taxonomy)
6. Situation Formula (Role × Layer × Lifecycle × RPBL × Domain)
7. The 10 Universal Subsystems
8. Extensions (Toolome, Dark Matter, Confidence -- status-tagged)

**Cross-references:**
- Atoms: canonical data in `../../schema/fixed/atoms.json`
- Roles: canonical data in `../../schema/fixed/roles.json`
- Dimensions: canonical data in `../../schema/fixed/dimensions.json`

**Principle:** Every concept defined **exactly once**. Other documents reference, never redefine.

---

## Layer 2: LAWS (Dynamic Behavior)

**File:** `L2_LAWS.md`

**What's inside:**
1. **Purpose Laws**: pi1-pi4 equations (THE canonical definition of purpose emergence)
2. **Emergence Laws**: Systems of Systems, epsilon > 1, fractal composition
3. **Flow Laws**: Constructal principle, flow substances, resistance = debt
4. **Concordance Laws**: Drift as distance, symmetry formula, purpose preservation
5. **Antimatter Laws**: Violations (reference `../../schema/antimatter_laws.yaml`)
6. **Communication Theory**: Shannon M-I-P-O cycle, semiosis, Free Energy Principle
7. **Evolution Laws**: Drift integral, interface surface, evolvability
8. **Theorem Candidates**: Unproven but empirically supported

**Status:** Contains both validated laws (Constructal, Emergence) and developing theory (Communication, FEP mapping).

---

## Layer 3: APPLICATIONS (Measurement & Implementation)

**File:** `L3_APPLICATIONS.md`

**What's inside:**
1. **Purpose Intelligence**: Q-scores formula, 5 intrinsic metrics, propagation
2. **Health Model**: H = T + E + Gd + A formula, Betti numbers, gradients
3. **Detection & Measurement**: Graph inference rules, dark matter signatures, confidence aggregation
4. **Pipeline Integration**: Stage mapping (29 stages), output schema
5. **Proofs & Verification**: Theorems 3.1-3.8, Lean 4 status, empirical results
6. **History**: The pivot (Dec 2025), timeline, key discoveries

**Status:** Most empirically grounded layer. Tied directly to Collider implementation.

---

## Cross-Cutting Resources

### Terminology Spine
**File:** `../../docs/GLOSSARY.yaml`
- 122 terms with categories
- Every term traces to one definition in L0-L3
- Machine-readable for validation

### Machine-Readable Schemas
**Directory:** `../../schema/fixed/`
- `atoms.json` -- 3,525 atoms across 4 phases
- `dimensions.json` -- 8 dimensions with domains
- `roles.json` -- 33 canonical roles
- `antimatter_laws.yaml` -- Violation rules

### Attribution & Provenance
**File:** `KNOWLEDGE_TREE.md`
- Intellectual lineage (Koestler, Popper, Evans, Shannon, etc.)
- Referenced vs Original theory attribution

---

## Quick Reference: Concept → Location Map

| Concept | Layer | Section | Line Ref |
|---------|-------|---------|----------|
| **P = C ⊔ X** | L0 | Axiom A1 | L0:24-36 |
| **16-Level Scale** | L1 | sec 2 | L1:~40-80 |
| **Holarchy** | L1 | sec 2.3 | L1:~70-75 |
| **Three Planes** | L1 | sec 1 | L1:~20-35 |
| **Atoms** | L1 | sec 4.1 | L1:~150-200 |
| **Phases (4)** | L1 | sec 4.2 | L1:~160-170 |
| **Roles (33)** | L1 | sec 4.3 | L1:~200-230 |
| **Dimensions (8)** | L1 | sec 4.4 | L1:~240-290 |
| **RPBL** | L1 | sec 4.5 | L1:~300-320 |
| **Codome** | L1 | sec 3.2 | L1:~85-110 |
| **Contextome** | L1 | sec 3.3 | L1:~115-140 |
| **Concordances** | L1 | sec 3.4 | L1:~145-170 |
| **Purpose Field** | L2 | sec 1 | L2:~20-90 |
| **pi1-pi4** | L2 | sec 1.1-1.4 | L2:~30-75 |
| **Emergence** | L2 | sec 2 | L2:~95-140 |
| **Constructal** | L2 | sec 3 | L2:~145-180 |
| **Drift** | L2 | sec 4.1 | L2:~210-240 |
| **Q-Scores** | L3 | sec 1 | L3:~20-90 |
| **Health Model** | L3 | sec 2 | L3:~95-150 |
| **Toolome** | L1 | sec 8.1 | L1:~430-460 |
| **Dark Matter** | L1 | sec 8.2 | L1:~465-490 |
| **Confidence** | L1 | sec 8.3 | L1:~495-520 |
| **Lawvere Proof** | L0 | sec 2.A1.1 | L0:~50-90 |
| **Category Theory** | L0 | sec 10.1 | L0:~700-800 |
| **Semiotics** | L0 | sec 10.2 | L0:~810-870 |
| **Fundamentality Stances** | L0 | sec 10.3 | L0:~875-920 |

---

## How to Navigate

### If you want to understand...

| Goal | Read This | Then This |
|------|-----------|-----------|
| **The complete theory** | THEORY_INDEX.md (this file), then L0→L1→L2→L3 in order | - |
| **Just the core structure** | L0_AXIOMS.md + L1_DEFINITIONS.md | Skip L2-L3 for now |
| **How to implement it** | L3_APPLICATIONS.md | Reference L2 for formulas |
| **Purpose emergence** | L2_LAWS.md sec 1 | Then L3 sec 1 (Q-scores) |
| **Health metrics** | L3_APPLICATIONS.md sec 2 | Reference L2 sec 3-4 |
| **Mathematical foundations** | L0_AXIOMS.md sec 2, 10 | CODESPACE_ALGEBRA.md for elaboration |
| **Semiotic connections** | L0_AXIOMS.md sec 10.2 | ONTOLOGICAL_FOUNDATIONS.md archive |
| **What a term means** | GLOSSARY.yaml | Traces to L0-L3 definition |
| **IP attribution** | KNOWLEDGE_TREE.md | External theory sources |

### If you want to find...

| Thing | Where |
|-------|-------|
| Atom taxonomy | L1 sec 4.1 + `schema/fixed/atoms.json` |
| Role list | L1 sec 4.3 + `schema/fixed/roles.json` |
| Dimension definitions | L1 sec 4.4 + `schema/fixed/dimensions.json` |
| Purpose equations | L2 sec 1.2 (CANONICAL) |
| Q-score formula | L3 sec 1.1 |
| Health formula | L3 sec 2.1 |
| Concordance score | L2 sec 4.1 |
| Antimatter violations | L2 sec 5 + `schema/antimatter_laws.yaml` |
| Pipeline stages | L3 sec 4.1 |
| Proofs | L3 sec 5 |
| History timeline | L3 sec 7.2 |

---

## Relation to Original Documents

The Theory Stack **unifies and supersedes** the following documents, which remain available as historical references:

| Original Document | Role | Relation to Stack |
|------------------|------|-------------------|
| `MODEL.md` | The original "theory of everything" | Content split across L1-L3 |
| `THEORY_AXIOMS.md` | Formal axioms | Merged into L0 |
| `ONTOLOGICAL_FOUNDATIONS.md` | Category theory + semiotics | Merged into L0 sec 10 |
| `CODESPACE_ALGEBRA.md` | Mathematical formalization | Split: algebra -> L0, dynamics -> L2 |
| `THEORY_EXPANSION_2026.md` | Theory extensions | Split across L1-L2 |
| `PURPOSE_EMERGENCE.md` | pi functions implementation | Split: equations -> L2, rules -> L3 |
| `PURPOSE_INTELLIGENCE.md` | Q-scores | Merged into L3 |
| `THEORY_AMENDMENT_2026-01.md` | 3 amendments | Integrated into L1 (defs) + L3 (impl) |
| `CODOME.md`, `CONTEXTOME.md`, `PROJECTOME.md` | Universe definitions | Merged into L1 sec 3 |
| `CONCORDANCES.md` | Concordance theory | Split: defs -> L1, algebra -> L2 |

**All original files remain unchanged.** The Stack is the NEW canonical reference.

---

## The Unification Principle

This structure follows the Standard Model's own design philosophy:

> **Each level is a WHOLE when looking down (contains parts) and a PART when looking up (contained by higher levels).**

Applied to theory itself:
- L0 is the whole when axioms look down at primitive notions
- L0 is a part when L1 looks up (definitions rest on axioms)
- L1 is the whole when definitions look down at individual concepts
- L1 is a part when L2 looks up (laws reference definitions)
- etc.

The stack **IS** a holarchy. It uses the theory to organize the theory.

---

## Validation Status

| Check | Result |
|-------|--------|
| Concept inventory | 461 concepts extracted, 391 unique |
| Duplication audit | CODOME/CONTEXTOME/PROJECTOME intentionally cross-defined; no problematic conflicts |
| Completeness | All 122 GLOSSARY.yaml terms trace to L0-L3 |
| Self-describing | Theory Stack uses 16-level structure to organize itself |
| External validation | Pending (AI reads only Stack, answers 10 questions) |

---

## For Developers: How to Use This

### When implementing a feature:
1. Read L1 section for the concepts you're using
2. Read L3 for the measurement formulas
3. Reference L2 only if you need dynamic behavior equations

### When debugging theory:
1. Check L0 -- is an axiom being violated?
2. Check L1 -- is a definition wrong?
3. Check L2 -- is a law not holding?
4. Check L3 -- is measurement failing?

### When proposing theory extensions:
1. Where does it belong? (L0 for new axioms, L1 for new entities, L2 for new laws, L3 for new metrics)
2. Add with explicit `[PROPOSED]` status tag
3. Once validated, promote to `[ACTIVE]`

---

## For AI Agents: Navigation Protocol

**First visit:**
1. Read this file (THEORY_INDEX.md)
2. Read L0_AXIOMS.md sections 1-3 (primitive notions + first 3 axiom groups)
3. Read L1_DEFINITIONS.md sections 1-4 (planes, levels, -omes, classification)

**For specific queries:**
- Use the Quick Reference table above to jump directly to the concept
- Follow cross-references to machine-readable schemas when present

**Validation:**
- Every claim you make about the Standard Model must trace to a specific section in L0-L3
- Cite as: `[L1 sec 3.2]` or `[L0 Axiom A1]`

---

## The Four Questions (Theory Orientation Test)

After reading the Stack, you should be able to answer:

1. **What MUST be true?** → P = C ⊔ X (Axiom A1), graph structure (Axiom B1), level ordering (Axiom C1)
2. **What EXISTS?** → 3,525 atoms, 33 roles, 8 dimensions, 16 levels, 2 universes, N concordances
3. **How does it BEHAVE?** → Purpose emerges (pi1→pi4), flow optimizes (Constructal), systems compose (epsilon > 1)
4. **How do we MEASURE it?** → Q-scores (5 metrics), Health (4 components), Drift (distance in embedding space)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **2.0.0** | 2026-01-27 | Theory Stack created. Unified 15+ documents into 4 layers. |
| 1.0.0 | 2025-12 | Original theory documented across MODEL.md, THEORY_AXIOMS.md, etc. |

---

## See Also

- `KNOWLEDGE_TREE.md` -- IP attribution and external theory sources
- `../../schema/` -- Machine-readable canonical data
- `../../CLAUDE.md` -- Canonical sources table for the entire project
- `../../../context-management/docs/GLOSSARY.yaml` -- All 122 terms

---

*This is the ONE document to read first. Everything else is detail.*
