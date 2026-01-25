# Research: List ALL enumerable collections in this codebase. For each collection, provide: 1) Name 2) Location ...

> **Date:** 2026-01-25 08:09:27
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:06a1908a3c5bf809ff13b0b031a879a03e23adacfdda3818bd2b40b8e2a76459`
> **Raw JSON:** `raw/20260125_080927_list_all_enumerable_collections_in_this_codebase.json`

---

## Query

List ALL enumerable collections in this codebase. For each collection, provide: 1) Name 2) Location (file path) 3) Item count if known 4) What kind of things it contains. Include: atoms, roles, dimensions, edge types, topology shapes, scales, any JSON/YAML that defines a fixed set of things.

---

## Response

Here is the comprehensive list of enumerable collections defined in the codebase, categorized by their domain.

### 1. Core Schema Definitions
These files define the fundamental ontology of the Standard Model of Code.

| Name | Location | Item Count | Contents / Description |
| :--- | :--- | :--- | :--- |
| **Fixed Atoms** | `schema/fixed/atoms.json` | 167 | The core 167 "Universal Atoms" organized into 4 Phases (Data, Logic, Organization, Execution) and 16 Families. |
| **Semantic Dimensions** | `schema/fixed/dimensions.json` | 8 | The 8 orthogonal axes of the model (WHAT, Layer, Role, Boundary, State, Effect, Activation, Lifetime). |
| **Canonical Roles** | `schema/fixed/roles.json` | 33 | The standardized "Why" definitions (Query, Command, Factory, Repository, etc.). |
| **Go Extensions** | `schema/atoms/extensions/go.json` | 20 | Go-specific atom definitions (Goroutine, Channel, Defer, etc.). |

### 2. Constraints & Validation
Rules and logic for validating the graph topology.

| Name | Location | Item Count | Contents / Description |
| :--- | :--- | :--- | :--- |
| **Tier A Rules** | `schema/constraints/rules.yaml` | 5 | "Axioms" (Antimatter sources). Universal impossibilities (e.g., Immutable + Mutation). |
| **Tier B Rules** | `schema/constraints/rules.yaml` | 3 | "Invariants". Profile-dependent architectural violations (e.g., Layer Dependency). |
| **Tier C Rules** | `schema/constraints/rules.yaml` | 4 | "Heuristics". Informative signals and code smells (e.g., God Class). |
| **Constraint Tiers** | `schema/constraints/taxonomy.yaml` | 3 | Taxonomy definitions for Tier A, B, and C constraints. |
| **Validity Functions** | `schema/constraints/taxonomy.yaml` | 4 | Formal mathematical definitions for graph validity. |
| **Constraint Scopes** | `schema/constraints/taxonomy.yaml` | 3 | Scopes of validation (node, edge, path). |

### 3. Language Mappings (Crosswalks)
Mapping rules between AST nodes and Standard Model Atoms.

| Name | Location | Item Count | Contents / Description |
| :--- | :--- | :--- | :--- |
| **Go Mappings** | `schema/crosswalks/go.json` | 52 | Maps Go AST nodes (e.g., `GoStmt`) to Atom IDs (e.g., `EXT.GO.001`). |
| **Java Mappings** | `schema/crosswalks/java.json` | 90 | Maps Java AST nodes (e.g., `RecordDeclaration`) to Atom IDs. |
| **Python Mappings** | `schema/crosswalks/python.json` | 95 | Maps Python AST nodes (e.g., `ListComp`) to Atom IDs. |
| **Rust Mappings** | `schema/crosswalks/rust.json` | 80 | Maps Rust AST nodes (e.g., `impl_item`) to Atom IDs. |
| **TS Mappings** | `schema/crosswalks/typescript.json` | 110 | Maps TypeScript AST nodes (e.g., `InterfaceDeclaration`) to Atom IDs. |

### 4. Pattern Recognition
Heuristics used to infer roles and attributes when AST analysis is insufficient.

| Name | Location | Item Count | Contents / Description |
| :--- | :--- | :--- | :--- |
| **Prefix Patterns** | `schema/learned/patterns.json` | ~70 | Naming prefixes (e.g., `get_` -> Query, `create_` -> Factory). |
| **Suffix Patterns** | `schema/learned/patterns.json` | ~70 | Naming suffixes (e.g., `Repository` -> Repository, `DTO` -> DTO). |
| **Path Patterns** | `schema/learned/patterns.json` | ~60 | Directory structure heuristics (e.g., `/controllers/` -> Controller). |
| **Import Patterns** | `schema/learned/patterns.json` | ~20 | Inference based on library imports (e.g., `mongoose` -> Repository). |
| **Inheritance Patterns** | `schema/learned/patterns.json` | ~15 | Inference based on class inheritance (e.g., `JpaRepository`). |
| **Exclusion Dirs** | `src/patterns/exclusions.yaml` | 22 | Directory patterns to ignore (vendor, node_modules, build artifacts). |
| **Exclusion Files** | `src/patterns/exclusions.yaml` | 25 | File patterns to ignore (minified code, lockfiles, generated code). |

### 5. Architectural Profiles
Configuration for specific architectural styles and paradigm constraints.

| Name | Location | Item Count | Contents / Description |
| :--- | :--- | :--- | :--- |
| **Classic Layered** | `schema/profiles/architecture/classic_layered.yaml` | 4 Layers | Defines `PRESENTATION` -> `INFRASTRUCTURE` hierarchy. |
| **Clean/Onion** | `schema/profiles/architecture/clean_onion.yaml` | 4 Layers | Defines `DOMAIN` (inner) to `INTERFACE` (outer) hierarchy. |
| **FP Strict** | `schema/profiles/dimensions/fp_strict.yaml` | 9 types | Defines Purity and Lifecycle semantics for Functional Programming. |
| **OOP Conventional** | `schema/profiles/dimensions/oop_conventional.yaml` | 9 types | Defines Purity and Lifecycle semantics for OOP. |

### 6. Visualization & Surface Tokens
Configuration for the UI, 3D rendering, and UX parity.

| Name | Location | Item Count | Contents / Description |
| :--- | :--- | :--- | :--- |
| **UI Zones** | `schema/surfaces/surface.manifest.json` | 1 | Definition of architectural surface zones (`viz`). |
| **UI Contracts** | `schema/surfaces/viz.surface.json` | 4 | Contracts for `command-bar`, `floating-panels`, `side-dock`, `bottom-dock`. |
| **Color Tokens** | `schema/viz/tokens/appearance.tokens.json` | ~50 | OKLCH color definitions for atoms, rings, edges, and UI modes. |
| **Animation Tokens** | `schema/viz/tokens/appearance.tokens.json` | 5 groups | Physics settings for hue, chroma, bloom, and layout presets. |
| **Data Maps** | `schema/viz/tokens/controls.tokens.json` | 16 | Visualization filters (e.g., "Show only T1", "Show only Logic"). |
| **Layout Presets** | `schema/viz/tokens/controls.tokens.json` | 11 | Algorithm presets (Force, Orbital, Radial, Sphere, Galaxy, etc.). |
| **Quality Tiers** | `schema/viz/tokens/performance.tokens.json` | 5 | Rendering tiers (Ultra to Minimal) based on node count. |
| **Physics Forces** | `schema/viz/tokens/physics.tokens.json` | 4 | D3 simulation forces (Charge, Link, Center, Collision). |
| **Theme Palettes** | `schema/viz/tokens/theme.tokens.json` | 3 | UI Chrome themes (Light, High-Contrast, Dark). |

### 7. Generated/Mined Atom Libraries (Tiers 0-2)
Specific patterns for detecting atoms in source code (Regex/Semgrep based).

| Name | Location | Item Count | Contents / Description |
| :--- | :--- | :--- | :--- |
| **Tier 0 Core** | `src/patterns/ATOMS_TIER0_CORE.yaml` | 43 | Universal language constructs (If, Loop, Function, Class). |
| **Tier 1 StdLib** | `src/patterns/ATOMS_TIER1_STDLIB.yaml` | 24 | Standard library capabilities (IO, Net, Math, Threads). |
| **Tier 2 Ecosystem** | `src/patterns/ATOMS_TIER2_ECOSYSTEM.yaml` | 17 | High-level patterns (React Component, Pandas DataFrame). |
| **T2 Cloud** | `src/patterns/t2_mined/ATOMS_T2_CLOUD.yaml` | 122 | Mined patterns for AWS, Kubernetes, Docker, Terraform. |
| **T2 Frontend** | `src/patterns/t2_mined/ATOMS_T2_FRONTEND.yaml` | 399 | Mined patterns for React, Vue, Angular, DOM manipulation. |
| **T2 Gaps** | `src/patterns/t2_mined/ATOMS_T2_GAPS.yaml` | 100 | Manual definitions for FastAPI, TensorFlow, PyTorch, Docker. |
| **T2 Java** | `src/patterns/t2_mined/ATOMS_T2_JAVA.yaml` | 265 | Mined patterns for Spring, Hibernate, JDBC, etc. |
| **T2 JS/Node** | `src/patterns/t2_mined/ATOMS_T2_JAVASCRIPT.yaml` | 327 | Mined patterns for Node, Express, Axios, Puppeteer. |
| **T2 Python** | `src/patterns/t2_mined/ATOMS_T2_PYTHON.yaml` | 566 | Mined patterns for Flask, Django, Requests, Pandas. |
| **T2 Other** | `src/patterns/t2_mined/ATOMS_T2_OTHER.yaml` | 1766 | Mined patterns for Ruby (Rails), Go, PHP, C#, .NET, Solidity. |

### 8. Ground Truth Data
Reference data for validating the system.

| Name | Location | Item Count | Contents / Description |
| :--- | :--- | :--- | :--- |
| **Gold Symbols** | `schema/ground_truth/standard_model_of_code.json` | ~30 | Validated roles for specific symbols in the codebase. |
| **Gold Files** | `schema/ground_truth/standard_model_of_code.json` | 51 | Hash and line counts for the core codebase files. |

---

## Citations

_No citations provided_
