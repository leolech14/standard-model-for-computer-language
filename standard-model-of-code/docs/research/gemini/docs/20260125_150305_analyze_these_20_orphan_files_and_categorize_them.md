# Research: Analyze these 20 orphan files and categorize them by purpose. Which should be added to CODOME_MANIFE...

> **Date:** 2026-01-25 15:03:05
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:eabad9ef8eacfd3a24b9ee4aa49d1cfec67981d65de92b276b289ab13cbeb014`
> **Raw JSON:** `raw/20260125_150305_analyze_these_20_orphan_files_and_categorize_them.json`

---

## Query

Analyze these 20 orphan files and categorize them by purpose. Which should be added to CODOME_MANIFEST.yaml? Files: UI_REFACTOR_IMPLEMENTATION_LOGIC.md, UI_ARCHITECTURE_VALIDATION_CONSOLIDATED.md, UI_OVERHAUL_CONTEXT_INVENTORY.md, SCALE_INOUT_TOPOLOGY.md, HEALTH_MODEL_CONSOLIDATED.md, PROPERTY_QUERY_DATA_FLOW.md, UI_CONTROLS_SCHEMA.md, SEMANTIC_INDEXER_IMPLEMENTATION.md, graph_framework.py, scientific_charts.py, graph_metrics.py, wave_extractor.py, symmetry_reporter.py, visibility_analyzer.py, identity_matcher.py, intent_extractor.py, chart_viewer.py, laboratory_bridge.py, industrial_ui.py, research_schemas.yaml

---

## Response

Based on the codebase context provided (specifically `full_analysis.py` which references several of these files) and the file names, here is the categorization of the 20 orphan files and the recommendation for the `CODOME_MANIFEST.yaml`.

### 1. Categorization by Purpose

I have grouped the files into four distinct domains based on the "Standard Model of Code" architecture observed in the context.

#### Group A: Core Graph Engine (The Physics)
These files provide the fundamental logic for the analysis pipeline seen in `full_analysis.py`. They appear as orphans likely because they are **library definitions** or **helpers** imported by the main pipeline but not calling out to much else themselves, or they are utilities.
*   `graph_framework.py`: **Critical.** Defines how the graph is built (`build_nx_graph`, `find_entry_points`).
*   `graph_metrics.py`: **Critical.** Calculates centrality and critical nodes.
*   `intent_extractor.py`: **Critical.** Extracts docstrings and commit signals.
*   `identity_matcher.py`: Logic for resolving node identity (likely used during graph construction).
*   `visibility_analyzer.py`: logic for determining scope/visibility (public/private).

#### Group B: UI & Visualization (The Lens)
These files represent the presentation layer. UI entry points often appear as orphans because nothing calls *them*; they call the backend.
*   `industrial_ui.py`: Likely the main entry point or container for the UI.
*   `chart_viewer.py`: Component for rendering visualizations.
*   `scientific_charts.py`: Library for generating the specific chart types.
*   `UI_CONTROLS_SCHEMA.md`: **Schema.** Defines the contract for UI interactions.
*   `UI_REFACTOR_IMPLEMENTATION_LOGIC.md`: *Process Artifact (Temporary).*
*   `UI_ARCHITECTURE_VALIDATION_CONSOLIDATED.md`: *Process Artifact (Temporary).*
*   `UI_OVERHAUL_CONTEXT_INVENTORY.md`: *Process Artifact (Temporary).*

#### Group C: Theoretical Definitions (The Theory)
These define the "Codome" theory (Standard Model). These are crucial for the `CODOME_MANIFEST` as they define the mental model.
*   `SCALE_INOUT_TOPOLOGY.md`: Defines the topological structure (Scale-Free/In-Out).
*   `HEALTH_MODEL_CONSOLIDATED.md`: Defines what constitutes "healthy" code in this system.
*   `PROPERTY_QUERY_DATA_FLOW.md`: Documentation on how data flows through the system.
*   `research_schemas.yaml`: **Schema.** Data definitions for the research/analysis layer.
*   `SEMANTIC_INDEXER_IMPLEMENTATION.md`: Documentation on how the semantic engine works.

#### Group D: Specialized Analysis (The Tools)
Specific analysis tools that likely plug into the main pipeline.
*   `wave_extractor.py`: Likely a specialized extractor (perhaps for "waves" of execution or phased analysis).
*   `symmetry_reporter.py`: Reporting tool for structural symmetry.
*   `laboratory_bridge.py`: Integration layer (Bridge pattern) likely connecting the core analysis to an experimental "laboratory" environment.

---

### 2. CODOME_MANIFEST.yaml Recommendations

The `CODOME_MANIFEST.yaml` should define the **boundary**, **schema**, and **entry points** of the system. Process logs (like refactor plans) should be excluded.

**✅ MUST ADD (Structural Definitions & Core Logic)**
*   **`research_schemas.yaml`**: Essential. Defines the data structure.
*   **`graph_framework.py`**: Essential. Defines the graph topology rules.
*   **`graph_metrics.py`**: Essential. Defines the measurement rules.
*   **`intent_extractor.py`**: Essential. Defines how meaning is derived.
*   **`UI_CONTROLS_SCHEMA.md`**: Essential. Defines the UI interface contract.
*   **`SCALE_INOUT_TOPOLOGY.md`**: Essential. Theoretical basis for the graph structure.
*   **`HEALTH_MODEL_CONSOLIDATED.md`**: Essential. Theoretical basis for metrics.

**⚠️ CONSIDER ADDING (Entry Points & Bridges)**
*   **`industrial_ui.py`**: Add if this is the canonical UI entry point.
*   **`laboratory_bridge.py`**: Add if this defines the interface to external systems/experiments.

**❌ DO NOT ADD (Process Artifacts)**
*   `UI_REFACTOR_IMPLEMENTATION_LOGIC.md`
*   `UI_ARCHITECTURE_VALIDATION_CONSOLIDATED.md`
*   `UI_OVERHAUL_CONTEXT_INVENTORY.md`
*   *(These are temporal logs, not system definitions).*

### 3. YAML Snippet for Update

Here is how you should structure the addition to your `CODOME_MANIFEST.yaml`:

```yaml
manifest:
  definitions:
    schemas:
      - path: "research_schemas.yaml"
        type: "data_contract"
        description: "Core data structures for research analysis"
      - path: "UI_CONTROLS_SCHEMA.md"
        type: "interface_contract"
        description: "Schema definition for UI control surfaces"
    
    theory:
      - path: "SCALE_INOUT_TOPOLOGY.md"
        type: "architecture_definition"
      - path: "HEALTH_MODEL_CONSOLIDATED.md"
        type: "metrics_definition"

  components:
    core_engine:
      - path: "graph_framework.py"
        role: "topology_builder"
      - path: "graph_metrics.py"
        role: "analytics_engine"
      - path: "intent_extractor.py"
        role: "semantic_processor"
    
    presentation:
      - path: "industrial_ui.py"
        role: "ui_entry_point"
```

---

## Citations

_No citations provided_
