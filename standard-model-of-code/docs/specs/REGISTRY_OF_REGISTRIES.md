# Registry of Registries

> A master index of all "plural" concepts, collections, and registries in the Standard Model of Code.

---

## Philosophy

Every classification system in this project is a **Registry**. Registries are:
- **Enumerable**: You can list all members
- **Stable**: Changes are tracked and versioned
- **Documented**: Each item has metadata

This document is the **meta-registry** - the registry of all registries.

---

## 1. Core Ontological Registries

The fundamental building blocks of the Standard Model of Code.

| Registry | Count | Location | Description |
|----------|-------|----------|-------------|
| **Atoms** | **94 impl / 200 theory** | `schema/fixed/atoms.json` | The Periodic Table of Code. Fundamental syntactic elements. |
| **Roles** | **33 canonical / 29 impl** | `schema/fixed/roles.json` | Semantic purpose (WHY). What the code *does*. |
| **Dimensions** | **8** | `schema/fixed/dimensions.json` | The 8 dimensions every code element exists within. |
| **Phases** | **4** | (embedded in atoms) | DATA, LOGIC, ORGANIZATION, EXECUTION |
| **Layers** | **4** | (embedded in topology) | Domain, Application, Infrastructure, Presentation |
| **Tiers** | **3** | `src/patterns/ATOMS_TIER*.yaml` | T0 (Core), T1 (Stdlib), T2 (Ecosystem) |

### The 8 Dimensions

| Dimension | Question | Values |
|-----------|----------|--------|
| WHAT | What is it? | Atom type |
| LAYER | Where in architecture? | Domain, App, Infra, Presentation |
| ROLE | What purpose? | 33 roles |
| BOUNDARY | Inside or outside? | Internal, External, Hybrid |
| STATE | Does it mutate? | Stateless, Stateful |
| EFFECT | Side effects? | Pure, Effectful |
| LIFECYCLE | When created/destroyed? | Singleton, Transient, Scoped |
| TRUST | Trust level? | Trusted, Untrusted |

---

## 2. Universal Property Binder (UPB) Registries

The visualization intelligence layer has its own taxonomy.

| Registry | Count | Location | Description |
|----------|-------|----------|-------------|
| **Scales** | **7** | `modules/upb/scales.js` | Transfer functions for data normalization |
| **Sources** | **~15** | `modules/upb/endpoints.js` | Data sources (inputs) available for binding |
| **Targets** | **~20** | `modules/upb/endpoints.js` | Visual targets (outputs) to bind to |
| **Blenders** | **6** | `modules/upb/blenders.js` | How to combine multiple bindings |
| **Presets** | **12** | `modules/upb/presets/defaults.yaml` | Pre-built binding configurations |

### UPB Scales (7)

| Scale | Formula | Best For |
|-------|---------|----------|
| `linear` | `(v-min)/(max-min)` | Uniform distributions |
| `sqrt` | `√v normalized` | Size perception (area→radius) |
| `log` | `log₁₀(v) normalized` | Power-law data (LoC, file sizes) |
| `exp` | `linear²` | Highlighting extremes |
| `inverse` | `1 - linear` | Flipping direction (age→freshness) |
| `discrete` | `indexOf / len` | Categorical data |
| `percentile` | Rank-based | Relative positioning |

### UPB Blenders (6)

| Blender | Behavior | Use Case |
|---------|----------|----------|
| `replace` | Last wins | Default, exclusive mappings |
| `average` | Mean of all | Position blending |
| `add` | Sum (clamped) | Cumulative effects |
| `multiply` | Product | Stacked transparency |
| `max` | Largest wins | Size (most important source) |
| `min` | Smallest wins | Constraints |

### UPB Presets (12)

| Preset | Purpose |
|--------|---------|
| `complexity` | Size + color by complexity |
| `importance` | PageRank + degree highlighting |
| `age` | Temporal visualization |
| `hierarchy` | Structural tiers |
| `scale_demo_*` | Linear/sqrt/log/exp demonstrations |
| `hotspot_finder` | Performance hotspots |
| `freshness_map` | Code freshness |
| `debt_detector` | Technical debt |
| `power_law_viz` | Dependency distribution |

---

## 3. Pipeline & Analysis Registries

| Registry | Count | Location | Description |
|----------|-------|----------|-------------|
| **Pipeline Stages** | **18** | `src/core/full_analysis.py` | Collider analysis stages |
| **Edge Types** | **6** | `schema/edge-types.json` | CONTAINS, CALLS, IMPORTS, INHERITS, IMPLEMENTS, USES |
| **Topology Shapes** | **5** | `src/core/topology_reasoning.py` | Star, Hierarchical, Mesh, Islands, Layered |
| **Codome Boundaries** | **6** | `src/core/full_analysis.py` | Synthetic external callers |

### The 18 Pipeline Stages

| # | Stage | Purpose |
|---|-------|---------|
| 1 | File Discovery | Find all source files |
| 2 | AST Parsing | Build syntax trees |
| 3 | Symbol Extraction | Extract functions, classes, etc. |
| 4 | Atom Classification | Map to Periodic Table |
| 5 | Role Detection | Assign semantic roles |
| 6 | Dependency Extraction | Build call graph |
| 6.5 | Edge Consolidation | Unify edge formats |
| 6.8 | Codome Boundaries | Add synthetic boundary nodes |
| 7 | Metrics Computation | Calculate complexity, cohesion |
| 8 | Topology Analysis | Detect architectural shape |
| 8.5 | Temporal Enrichment | Add git timestamps |
| 8.6 | Purpose Intelligence | Compute Q-scores |
| 9 | Graph Construction | Build unified graph |
| 10 | PageRank | Compute centrality |
| 11 | Community Detection | Find clusters |
| 12 | Antimatter Detection | Find violations |
| 13 | Report Generation | Create output.md |
| 14 | Visualization | Generate HTML |

---

## 4. Task Registries

> **Note:** As of 2026-01-23, task management is consolidated into `.agent/registry/`.
> Legacy markdown registries below are deprecated or archived. See `.agent/registry/INDEX.md`.

### Primary System (YAML-based)

| Registry | Status | Location | Description |
|----------|--------|----------|-------------|
| **Agent Registry** | **ACTIVE** | `.agent/registry/INDEX.md` | Central task management |
| **Discovery Inbox** | **ACTIVE** | `.agent/registry/inbox/*.yaml` | Opportunities pending promotion |

### Legacy Registries (Consolidated 2026-01-23)

| Registry | Status | Location | Description |
|----------|--------|----------|-------------|
| **Tree-sitter Tasks** | **KEPT** | `docs/specs/TREE_SITTER_TASK_REGISTRY.md` | 46 tasks, canonical source |
| **Pipeline Refactor** | **MIGRATED** | `docs/specs/PIPELINE_REFACTOR_TASK_REGISTRY.md` | 35 tasks → OPP-006 |
| **Token System** | **MIGRATED** | `docs/reports/TOKEN_SYSTEM_TASK_REGISTRY.md` | 10 tasks → OPP-005 |
| **UPB Tasks** | **ARCHIVED** | `docs/specs/UPB_TASK_REGISTRY.md` | Phase 6 complete |
| **Architecture Debt** | **REFERENCE** | `docs/reports/ARCHITECTURE_DEBT_REGISTRY.md` | Analysis, not tasks |
| **Docs Improvement** | **ARCHIVED** | `docs/reports/DOCS_IMPROVEMENT_TASK_REGISTRY.md` | 1/10 done, low priority |
| **Docs Reorg** | **ARCHIVED** | `context-management/docs/DOCS_REORG_TASK_REGISTRY.md` | 7/10 done |
| **Sidebar Refactor** | **ARCHIVED** | `docs/reports/SIDEBAR_REFACTOR_TASK_REGISTRY.md` | 1/13 done, deferred |

### Archived to GCS (Duplicates/Superseded)

Files archived to `gs://elements-archive-2026/archive/legacy_registries/`:

- `TREE_SITTER_FULL_IMPLEMENTATION_REGISTRY.md` - duplicate of TREE_SITTER_TASK_REGISTRY
- `TASK_CONFIDENCE_REGISTRY.md` - superseded by .agent/registry/

Local copies retained with ARCHIVED headers pointing to GCS location.

---

## 5. Schema & Definition Files

| File | Purpose | Location |
|------|---------|----------|
| `particle.schema.json` | Node validation schema | `schema/particle.schema.json` |
| `atoms.json` | Atom definitions | `schema/fixed/atoms.json` |
| `roles.json` | Role definitions | `schema/fixed/roles.json` |
| `dimensions.json` | Dimension definitions | `schema/fixed/dimensions.json` |
| `edge-types.json` | Edge type definitions | `schema/edge-types.json` |

---

## 6. Language & Ecosystem Registries

| Registry | Count | Location | Description |
|----------|-------|----------|-------------|
| **Tree-sitter Queries** | **7 languages** | `src/core/queries/*.scm` | Query files per language |
| **Ecosystem Atoms T2** | **17** | `src/patterns/ATOMS_TIER2_ECOSYSTEM.yaml` | Framework-specific atoms |

### Supported Languages

| Language | Query File | Status |
|----------|------------|--------|
| Python | `python.scm` | Full |
| JavaScript | `javascript.scm` | Full |
| TypeScript | `typescript.scm` | Full |
| Go | `go.scm` | Partial |
| Rust | `rust.scm` | Partial |
| Java | `java.scm` | Planned |
| C++ | `cpp.scm` | Planned |

---

## 7. Visualization Module Registry

| Module | Purpose | Location |
|--------|---------|----------|
| `control-bar.js` | User controls UI | `modules/control-bar.js` |
| `file-viz.js` | File-level visualization | `modules/file-viz.js` |
| `edge-system.js` | Edge rendering | `modules/edge-system.js` |
| `circuit-breaker.js` | Fault tolerance | `modules/circuit-breaker.js` |
| `upb/index.js` | UPB orchestrator | `modules/upb/index.js` |
| `upb/scales.js` | Scale transforms | `modules/upb/scales.js` |
| `upb/endpoints.js` | Sources & targets | `modules/upb/endpoints.js` |
| `upb/blenders.js` | Blend modes | `modules/upb/blenders.js` |
| `upb/bindings.js` | Active bindings | `modules/upb/bindings.js` |

---

## Quick Reference

### Counts at a Glance

| What | Count |
|------|-------|
| Atoms (implemented) | 94 |
| Atoms (documented) | 200 |
| Roles | 33 |
| Dimensions | 8 |
| UPB Scales | 7 |
| UPB Targets | ~20 |
| UPB Blenders | 6 |
| UPB Presets | 12 |
| Pipeline Stages | 18 |
| Edge Types | 6 |
| Languages | 7 |
| Task Registries | 5 |

---

## Adding a New Registry

If you create a new "collection of things":

1. Add it to this document in the appropriate section
2. Include: Name, Count, Location, Description
3. If > 5 items, create a sub-table listing them
4. Update counts when the registry changes

Format:
```markdown
| **[Name](link)** | **Count** | `path` | Description |
```

---

## 8. Constraint & Validation Registries

| Registry | Count | Location | Description |
|----------|-------|----------|-------------|
| **Antimatter Laws** | **5** | `schema/antimatter_laws.yaml` | AM001-AM005: LayerSkip, ReverseLayer, GodClass, AnemicModel, BoundedContextViolation |
| **Constraint Tiers** | **3** | `schema/constraints/taxonomy.yaml` | A (Axioms), B (Invariants), C (Heuristics) |
| **Architecture Profiles** | **4** | `schema/profiles/architecture/` | classic_layered, clean_onion, fp_strict, oop_conventional |

---

## 9. Design Tokens (Visualization Config)

| Token File | Purpose | Location |
|------------|---------|----------|
| `appearance.tokens.json` | Colors, opacity, sizes | `schema/viz/tokens/` |
| `controls.tokens.json` | UI control styling | `schema/viz/tokens/` |
| `layout.tokens.json` | Spacing, positioning | `schema/viz/tokens/` |
| `physics.tokens.json` | Force-directed graph params | `schema/viz/tokens/` |
| `performance.tokens.json` | Perf tuning params | `schema/viz/tokens/` |
| `theme.tokens.json` | Theme/color schemes | `schema/viz/tokens/` |

---

## 10. Language Crosswalks

Map language-specific AST nodes to canonical atoms.

| Language | File | Status |
|----------|------|--------|
| Python | `schema/crosswalks/python.json` | Complete |
| TypeScript | `schema/crosswalks/typescript.json` | Complete |
| Go | `schema/crosswalks/go.json` | Complete |
| Rust | `schema/crosswalks/rust.json` | Partial |
| Java | `schema/crosswalks/java.json` | Planned |

---

## 11. Purpose & Quality Registries

| Registry | Count | Location | Description |
|----------|-------|----------|-------------|
| **Purpose Emergence** | **4 levels** | `schema/particle.schema.json` | π₁ (Atomic) → π₄ (System) |
| **Q-Scores** | **6 metrics** | `schema/particle.schema.json` | Q_alignment, Q_coherence, Q_density, Q_completeness, Q_simplicity, Q_intrinsic |

---

## 12. Analysis Configuration (Brain Hemisphere)

| Registry | Count | Location | Description |
|----------|-------|----------|-------------|
| **Analysis Sets** | **17+** | `context-management/config/analysis_sets.yaml` | brain, body, viz, complete, etc. |
| **Prompts** | **14+** | `context-management/config/prompts.yaml` | claims_ledger, lens_validation, dimension_orthogonality, etc. |
| **Semantic Models** | **varies** | `context-management/config/semantic_models.yaml` | AI model configs |

---

## Summary: All Registries at a Glance

| Category | Registries | Total Items |
|----------|------------|-------------|
| Core Ontological | 6 | ~350 |
| UPB | 5 | ~60 |
| Pipeline/Analysis | 4 | ~35 |
| Task Registries | 5 | ~60 tasks |
| Schemas | 5 | - |
| Languages | 7 | - |
| Viz Modules | 9 | - |
| Constraints | 3 | ~12 |
| Design Tokens | 6 | - |
| Crosswalks | 5 | - |
| Purpose/Quality | 2 | ~10 |
| Analysis Config | 3 | ~33 |
| **TOTAL** | **60 registries** | **~560 items** |

---

*Last updated: 2026-01-21*
*Part of the Standard Model of Code project*
