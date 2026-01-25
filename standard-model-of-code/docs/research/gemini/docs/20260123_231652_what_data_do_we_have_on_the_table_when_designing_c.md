# Research: What data do we have on the table when designing Collider for the Standard Model of Code? List all c...

> **Date:** 2026-01-23 23:16:52
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:59be1a0015d768db7e32754fd989bfcdd46db3e1da4ceda5dac4a9bc1a14aecf`
> **Raw JSON:** `raw/20260123_231652_what_data_do_we_have_on_the_table_when_designing_c.json`

---

## Query

What data do we have on the table when designing Collider for the Standard Model of Code? List all concrete assets: schemas, algorithms, metrics, modules, specs, and capabilities that are IMPLEMENTED (not planned). Be direct and exhaustive.

---

## Response

Okay, I will analyze the provided files and provide a direct and exhaustive list of implemented schemas, algorithms, metrics, modules, specs, and capabilities when designing Collider for the Standard Model of Code.

Here's a breakdown of the known assets:

**SCHEMAS**

*   **Node Schema**: Defined in `context-management/docs/COLLIDER_ARCHITECTURE.md` and exemplified in `context-management/docs/COLLIDER_ARCHITECTURE.md`. Includes `id`, `name`, `kind`, `file_path`, `start_line`, `end_line`, `role`, `role_confidence`, `discovery_method`, `params`, `return_type`, `complexity`, `in_degree`, `out_degree`, `layer`, `rpbl`, `atom`, `dimensions`.
*   **Edge Schema**: Defined in `context-management/docs/COLLIDER_ARCHITECTURE.md`. Includes `source`, `target`, `edge_type`, `weight`, `confidence`, `resolution`, `file_path`, `line`, `markov_weight`.
*  **Design Tokens**: `context-management/docs/COLLIDER_ARCHITECTURE.md` indicates `appearance.tokens.json` and `controls.tokens.json` exist but does not describe schema.

**ALGORITHMS**

*   **AST Parsing:** Using `tree_sitter_engine.py` to create a Tree Sitter Engine. This utilizes `parser/*` and `classification/*`.
*   **RPBL Classification:** Assigning RPBL scores during analysis (details in `src/core/unified_analysis.py`).
*   **Edge Extraction:** Using `edge_extractor.py` based on particles to create edges with resolution.
*   **Markov Matrix Computation**: Calculates Markov weights for edges in `src/core/full_analysis.py`
*   **Knot Detection**: `src/core/full_analysis.py` has `Knot Detection`

**METRICS**

*   **RPBL scores**: Responsibility, Purity, Boundary, Lifecycle
*   **Node degree**: in\_degree, out\_degree in UnifiedNode
*   **Codebase Health**: Health assessment during topology shape interpretation
*   **Coupling Analysis**: Coupling assessment during topology shape interpretation

**MODULES**

*   `tree_sitter_engine.py`: Parses source code.
*   `unified_analysis.py`: Creates UnifiedAnalysisOutput.
*   `edge_extractor.py`: Extracts edges.
*   `data_management.py`: Manages CodebaseState.
*   `standard_model_enricher.py`: Adds RPBL, atoms, dimensions.
*   `purpose_field.py`: Assigns layer assignments.
*   `execution_flow.py`: Determines entry points, and orphans.
*   `full_analysis.py`: Orchestrates full analysis.
*   `token_resolver.py`: Resolves token values.
*   `appearance_engine.py`: Styles nodes/edges.
*   `controls_engine.py`: Configures the UI panel.
*   `output_generator.py`: Outputs JSON + HTML files.

**SPECS (Implemented)**

*   No explicit list of implemented specs but the following are mentioned:
    *   "ACI v1.0 (Adaptive Context Intelligence)": from ACI_DATASET_MANAGEMENT.md
    *   "schema/viz/tokens" referenced in COLLIDER_ARCHITECTURE.md
    *   "semantic_models.yaml (Antimatter Laws)" mentioned in HOLOGRAPHIC_SOCRATIC_LAYER.md
    *   "Token budgets (aci_config.yaml)": from ACI_DATASET_MANAGEMENT.md
    *   "Agent context triggers (aci_config.yaml)": from ACI_DATASET_MANAGEMENT.md

**CAPABILITIES**

*   **Codebase Analysis**: Creates a semantic graph of the codebase.
*   **Pattern Recognition**: Identifies design patterns and anti-patterns.
*   **Code Quality Assessment**: Assesses responsibility, purity, boundary, and lifecycle scores.
*   **Refactoring Suggestions**: Provides specific refactoring opportunities.
*   **Topology Analysis**: Interprets the shape of the architecture and assesses overall health.
*   **Risk Area Detection**: Identifies risk areas and technical debt.
*   **Visualization**: Generates an interactive 3D graph of the codebase.
* **Evidence protocol**: Requires citations in AI responses for code references


---

## Citations

_No citations provided_
