# PROJECT_elements: Self-Portrait

**Generated:** 2026-01-24
**Purpose:** The Standard Model of Code analyzing itself
**Method:** Mapping discovered entities to the 16-level scale

---

## The Revelation

We have 10 subsystems documented (S1-S9b). But between them and the totality lies **connective tissue** - tools, utilities, state - that we called "dark matter."

These aren't orphans. They're **entities seeking their tribe**.

This document maps every discovered entity to its proper level in the scale.

---

## Level Mapping: PROJECT_elements

### L8: ECOSYSTEM - "PROJECT_elements"

The entire repository. Contains multiple systems working together toward a unified purpose: **finding the basic constituents of computer programs**.

```
PROJECT_elements/
├── standard-model-of-code/  (L7: System)
├── context-management/      (L7: System)
├── .agent/                  (L7: System)
├── archive/                 (L7: System - dormant)
├── related/                 (L7: System - external)
└── [root configs]           (L6: Package - governance)
```

**Terminology:** ECOSYSTEM = A cohesive collection of Systems with shared purpose

---

### L7: SYSTEM (formerly "Holon")

Self-contained units that can operate independently but integrate into the larger whole.

| System | Path | Purpose | Status |
|--------|------|---------|--------|
| **Collider** | `standard-model-of-code/` | Analysis engine (THE product) | ACTIVE |
| **Wave** | `context-management/` | AI/Intelligence layer | ACTIVE |
| **Observer** | `.agent/` | Governance/state | ACTIVE |
| **Archive** | `archive/` | Historical preservation | DORMANT |
| **External** | `related/` | Third-party tools | DEPENDENCY |

**Terminology:** SYSTEM = A Holon - autonomous unit with clear boundary and purpose

---

### L6: PACKAGE (Subsystems)

The 10 documented subsystems, plus newly discovered ones:

| ID | Subsystem | System | Path | Purpose |
|----|-----------|--------|------|---------|
| S1 | Collider Core | Collider | `standard-model-of-code/` | Semantic analysis |
| S2 | HSL | Wave | `docs/HOLOGRAPHIC_SOCRATIC_LAYER.md` | Validation rules |
| S3 | analyze.py | Wave | `tools/ai/analyze.py` | AI query interface |
| S4 | Perplexity MCP | Wave | `tools/mcp/` | External knowledge |
| S5 | Task Registry | Observer | `.agent/registry/` | Work tracking |
| S6 | BARE | Observer | `.agent/tools/bare` | Auto-refinement |
| S7 | Archive | Observer | `tools/archive/` | Cloud sync |
| S8 | Hygiene | Observer | `.pre-commit-config.yaml` | Commit guards |
| S9 | Laboratory | Collider | `tools/research/laboratory.py` | Experiment API |
| S9b | Lab Bridge | Wave | `tools/ai/laboratory_bridge.py` | Wave→Particle bridge |
| **S10** | Enrichment | Observer | `.agent/tools/enrichment_orchestrator.py` | Task enrichment |
| **S11** | Refinery | Wave | `tools/refinery/` | Context atomization |
| **S12** | Centripetal | Wave | `.agent/tools/centripetal_scan.py` | Deep analysis |

**Terminology:** PACKAGE = Subsystem - a functional unit within a System

---

### L5: FILE (Modules)

Individual source files. This is where the "orphan tools" live:

#### Observer System (.agent/) - Orphan Tools Seeking Tribes

| File | Proposed Tribe | Purpose |
|------|----------------|---------|
| `fact_loader.py` | S6 (BARE) | Loads validated facts |
| `confidence_validator.py` | S6 (BARE) | Validates confidence scores |
| `task_store.py` | S5 (Registry) | Task state management |
| `promote_opportunity.py` | S5 (Registry) | Opportunity → Task |
| `batch_promote.py` | S5 (Registry) | Bulk promotions |
| `triage_inbox.py` | S5 (Registry) | Inbox processing |
| `sprint.py` | S5 (Registry) | Sprint management |
| `priority_matrix.py` | NEW: S13? (Strategy) | Priority decisions |
| `wave_particle_balance.py` | NEW: S14? (Symmetry) | Doc↔Code balance |
| `symmetry_check.py` | NEW: S14? (Symmetry) | Symmetry validation |
| `deal_cards.py` | S5 (Registry) | Card-based UI |
| `oklch_color.py` | S1 (Collider) | Color utilities |
| `size_normalizer.py` | S1 (Collider) | Data normalization |

#### Wave System (context-management/) - Orphan Tools

| File | Proposed Tribe | Purpose |
|------|----------------|---------|
| `drift_guard.py` | S2 (HSL) | Drift Guard - detects semantic drift |
| `activity_watcher.py` | NEW: S15? (Telemetry) | Activity monitoring |
| `continuous_cartographer.py` | S11 (Refinery) | Continuous mapping |
| `loop.py` | S3 (analyze.py) | Interactive loop |
| `observe_session.py` | NEW: S15? (Telemetry) | Session observation |
| `insights_generator.py` | S3 (analyze.py) | AI insights |
| `perplexity_research.py` | S4 (Perplexity) | Research queries |

**Terminology:** FILE = Module - a single source file with coherent purpose

---

### L4: CONTAINER (Classes/Major Structures)

Classes, large data structures, configuration objects within files.

Examples from Collider (S1):
- `class UnifiedAnalyzer` in `full_analysis.py`
- `class AtomClassifier` in `atom_classifier.py`
- `class TreeSitterEngine` in `tree_sitter_engine.py`

**Terminology:** CONTAINER = Class or major structural unit

---

### L3: NODE (Functions/Methods)

Individual callable units. This is Collider's primary analysis level.

**Terminology:** NODE = Function, method, or callable

---

### L2: BLOCK

Logical blocks within functions (if/else, try/catch, loops).

**Terminology:** BLOCK = Control flow unit

---

### L1: STATEMENT

Individual statements.

**Terminology:** STATEMENT = Single executable line

---

### L0 and below: SYNTACTIC/PHYSICAL

Tokens, characters, bytes, bits. Below our semantic concern.

---

## The Terminology Stack

| Level | Term | Definition | Example in PROJECT_elements |
|-------|------|------------|----------------------------|
| L8 | **ECOSYSTEM** | Collection of Systems with shared purpose | PROJECT_elements |
| L7 | **SYSTEM** | Autonomous Holon with clear boundary | Collider, Wave, Observer |
| L6 | **PACKAGE** | Subsystem - functional unit | S1-S12 (and growing) |
| L5 | **MODULE** | Single source file | `analyze.py`, `full_analysis.py` |
| L4 | **CONTAINER** | Class or major structure | `class UnifiedAnalyzer` |
| L3 | **NODE** | Function or method | `def classify_atom()` |
| L2 | **BLOCK** | Control flow unit | `if node.kind == 'class':` |
| L1 | **STATEMENT** | Single executable | `return result` |

---

## Entity Census

### By Level

| Level | Count | How Counted |
|-------|-------|-------------|
| L8 Ecosystem | 1 | PROJECT_elements |
| L7 System | 5 | Collider, Wave, Observer, Archive, External |
| L6 Package | 12+ | S1-S12 (more emerging) |
| L5 Module | ~500 | .py files in active systems |
| L4 Container | ~1,200 | Classes (from Collider analysis) |
| L3 Node | ~12,000 | Functions/methods |

### Orphan Resolution

**Before:** 27 tools in `.agent/tools/` labeled "dark matter"
**After:** Each assigned to a tribe (Package/Subsystem)

| Tribe | Members | Status |
|-------|---------|--------|
| S5 (Registry) | 7 tools | Merge pending |
| S6 (BARE) | 3 tools | Merge pending |
| S1 (Collider) | 2 tools | Merge pending |
| S2 (HSL) | 1 tool | Merge pending |
| S3 (analyze.py) | 2 tools | Merge pending |
| S11 (Refinery) | 1 tool | Merge pending |
| NEW S13 (Strategy) | 1 tool | Propose new |
| NEW S14 (Symmetry) | 2 tools | Propose new |
| NEW S15 (Telemetry) | 2 tools | Propose new |

---

## Emergent Insights

### 1. The Three-Realm Architecture is Real

```
PARTICLE (Collider)     WAVE (Intelligence)     OBSERVER (Governance)
       S1                   S2, S3, S4              S5, S6, S7, S8
       S9                   S9b, S11, S12           S10
                            S15?                    S13?, S14?
```

### 2. Subsystem Count is Growing

- Started: 10 (S1-S9b)
- Discovered: 3 (S10-S12)
- Emerging: 3 (S13-S15)
- **Total: 16 subsystems** (!)

### 3. The Connective Tissue Has Structure

What we called "dark matter" is actually:
- **State storage** (`.agent/intelligence/`) → Part of Observer
- **Utility functions** (color, size) → Part of respective Systems
- **Coordination tools** (task_registry, sprint) → Part of S5/S6

### 4. Self-Similarity Across Levels

The Ecosystem has Systems has Packages has Modules has Containers has Nodes.
Each level exhibits the same pattern: **purpose-driven units with clear boundaries**.

---

## Next Steps

1. **Formalize S13-S15** or merge their tools into existing subsystems
2. **Update SUBSYSTEM_INTEGRATION.md** to v1.3.0 with new subsystems
3. **Run Collider on PROJECT_elements** to validate node counts at L3-L5
4. **Compare** this self-portrait with external codebases

---

## The Meta-Insight

The Standard Model of Code's first test subject is itself.

We're not just building a tool. We're **growing a theory** by:
1. Defining levels (done: 16 levels)
2. Naming entities (this document)
3. Discovering relationships (SoS map)
4. Validating predictions (Collider output)

The project knowing itself is the first step toward knowing all projects.

---

*This document is a living portrait. Update as entities are discovered or reclassified.*
