# Project History: The Evolution of the Standard Model of Code

> **Layer:** 3 (Registry) | **Parent:** [MODEL.md](../MODEL.md) | **Index:** [README.md](../README.md)
> **Purpose:** Chronicle how the theory and tool evolved
> **Sources:** Git history, Gemini 2.5 Pro forensic extraction, documentation

---

## Timeline

### Phase 0: Pre-History (Before Dec 2025)

**The Learning Problem Hypothesis**

The project began with the assumption that classifying code was an AI learning problem.

| Assumption | Reality (discovered later) |
|------------|---------------------------|
| Naming reveals intent | Naming is ambiguous |
| AI must "learn" patterns | Structure is deterministic |
| Classification requires ML | Topology + Frameworks sufficient |

**Early Architecture:**
- `LearningEngine` - AI-based pattern learning
- `AutoPatternDiscovery` - ML pattern detection
- `LLMClassifier` - GPT-based role inference

**Early Research:**
- Mapped 152 unique AST node types across Python, JS, TypeScript

---

### Phase 1: Initial Commit (Dec 14, 2025)

**Tool Name:** Spectrometer v12

```
git: 89a4986 | 2025-12-14 | Initial commit: Spectrometer v12 (Minimal + Hybrid Pipeline)
```

The tool was called **Spectrometer** - analyzing code like light through a prism.

---

### Phase 2: The Pivot (Dec 23, 2025)

**THE CRITICAL DISCOVERY**

An experiment on **91 repositories** and **270,000 code nodes** revealed:

> Code structure can be deterministically classified with **>99% accuracy WITHOUT AI**.

**The Insight:** Information is encoded in:
1. **Topology** (file paths) - `/services/UserService.py` reveals role
2. **Frameworks** (decorators) - `@Controller` reveals role
3. **Genealogy** (inheritance) - `extends Repository` reveals role

**NOT in:**
- Naming alone (`processData` is ambiguous)
- Syntax alone (same AST, different purposes)

**Architectural Shift:**

| Archived (AI-centric) | Promoted (Deterministic) |
|-----------------------|--------------------------|
| LearningEngine | HeuristicClassifier |
| AutoPatternDiscovery | UniversalDetector |
| LLMClassifier | PatternMatcher |

**Philosophy Change:** From "Artificial Intelligence" to **"Code Physics"**

---

### Phase 3: Formalization - V1 (Dec 2025)

**FORMAL_PROOF.md authored**

The first complete formal definition of the Standard Model:

| Constant | V1 Value | Source |
|----------|----------|--------|
| Atoms | **167** | FORMAL_PROOF.md Def 1.2 |
| Roles | **27** | FORMAL_PROOF.md Def 1.3 |
| Families | **16** | FORMAL_PROOF.md |
| Phases | **4** | FORMAL_PROOF.md |
| Pipeline stages | **10** | FORMAL_PROOF.md Thm 3.7 |
| Semantic space | **45,090,000** | FORMAL_PROOF.md Thm 3.4 |

**Theoretical Foundations Documented:**

| Theory | Inspired |
|--------|----------|
| Koestler's Holons | 16 Levels of Abstraction |
| Popper's Three Worlds | 3 Planes (Physical, Virtual, Semantic) |
| Ranganathan's Facets | 8 Dimensions |
| Shannon's Information | IPO Cycle (Input-Process-Output) |
| Clean Architecture (Martin) | Layer dimension |
| DDD (Evans) | 33 Roles |
| Dijkstra's Layers | Abstraction concept |

---

### Phase 4: Rebrand (Jan 11, 2026)

**Spectrometer → Collider**

```
git: 8686330 | 2026-01-11 | chore: rebrand Spectrometer → Collider
```

**Why "Collider"?**
- Like a particle collider reveals fundamental particles
- The tool reveals the **atoms** of code
- Aligns with physics metaphor (atoms, antimatter, etc.)

---

### Phase 5: Evolution to V2 (Jan 2026)

**Model Expansion**

Scanner results from Dec 2025 showed coverage gaps in Rust, Go, and other languages.

| Constant | V1 | V2 | Change |
|----------|----|----|--------|
| Atoms | 167 | **200** | +33 |
| Roles | 27 | **33** | +6 |
| Families | 16 | **22** | +6 |
| Pipeline stages | 10 | **12** | +2 |
| Semantic space | 45M | **66M** | +21M |

**New Schema Files:**
- `schema/fixed/200_ATOMS.md` - 200 atoms enumerated
- `schema/fixed/roles.json` - 33 roles
- `src/patterns/ATOMS_TIER*.yaml` - T0/T1/T2 tiers

---

### Phase 6: Current State (Jan 19, 2026)

**Two-Layer Architecture Clarified:**

```
┌─────────────────────────────────────┐
│ Layer 2: LLM Enrichment (Optional)  │  ← AI explains, doesn't classify
├─────────────────────────────────────┤
│ Layer 1: Deterministic Core         │  ← THE INTELLIGENCE
└─────────────────────────────────────┘
```

**Bidirectionality Gap Identified:**
- Analysis: Code → Graph (DONE)
- Synthesis: Graph → Code (NOT YET)

**Implementation vs Documentation Gap Discovered:**
- V2 docs: 200 atoms, 33 roles
- Actual implementation: ~15 atom IDs, 29 roles

---

## Version Summary

| Version | Date | Atoms | Roles | Families | Tool Name |
|---------|------|-------|-------|----------|-----------|
| v0 | Pre-Dec 2025 | ~152 AST types | - | - | (research) |
| v1 | Dec 2025 | 167 | 27 | 16 | Spectrometer |
| v2 | Jan 2026 | 200 | 33 | 22 | Collider |

---

## Theoretical Lineage

```
                    FOUNDATIONAL THEORIES
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
Koestler            Popper               Ranganathan
(Holons)         (Three Worlds)      (Faceted Classification)
    │                      │                      │
    ▼                      ▼                      ▼
16 LEVELS            3 PLANES              8 DIMENSIONS
(L-3 to L12)    (Physical/Virtual/       (WHAT, LAYER,
                   Semantic)             ROLE, etc.)
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
Clean Arch              DDD                  Shannon
(Martin)              (Evans)          (Information Theory)
    │                      │                      │
    ▼                      ▼                      ▼
LAYER DIM            33 ROLES              IPO CYCLE
                                      (Memory→Input→Process→Output)
```

---

## Key Dates

| Date | Event |
|------|-------|
| 2025-12-14 | Initial commit: Spectrometer v12 |
| 2025-12-23 | THE PIVOT: AI → Deterministic |
| 2025-12-xx | FORMAL_PROOF.md authored (V1) |
| 2026-01-07 | Research phase: Category Theory, Semiotics, Zachman |
| 2026-01-11 | Rebrand: Spectrometer → Collider |
| 2026-01-13 | T2 ecosystem atoms (React, Rust, K8s) |
| 2026-01-14 | Quality enforcement metrics added |
| 2026-01-19 | V2 schema files created (200 atoms, 33 roles) |
| 2026-01-19 | Implementation gap discovered |

---
