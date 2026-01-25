# Research: DESIGN TASK: Generate a complete UI controls schema for a 3D code graph visualization tool.

CONTEXT...

> **Date:** 2026-01-25 01:50:21
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:b21de863823da675f17c547d9096ea050674a35930a626254043ec57ee09c7b0`
> **Raw JSON:** `raw/20260125_015021_design_task__generate_a_complete_ui_controls_schem.json`

---

## Query

DESIGN TASK: Generate a complete UI controls schema for a 3D code graph visualization tool.

CONTEXT:
- Tool: Collider (Standard Model of Code)
- Stack: Three.js + 3d-force-graph
- Current: 60 controls identified (9 working, 20 untested, 13 broken, 18 missing)
- Purpose: Visualize code structure as interactive 3D graph

REQUIREMENTS:
1. Analyze current controls in src/core/viz/assets/modules/*.js
2. Identify gaps compared to professional tools (Gephi, Neo4j Bloom)
3. Propose complete schema with:
   - Control categories (nodes, edges, layout, camera, filter, selection, export)
   - For each control: id, type, range/options, default, state_path, handler_module
   - Priority tier: P0 (essential), P1 (important), P2 (nice-to-have)

OUTPUT FORMAT: JSON schema with all controls organized by category.

Focus on what a code analysis visualization SPECIFICALLY needs (not generic graph viz).

---

## Response

As Chief Architect of the **Standard Model of Code** project, I have analyzed the current visualization implementation against our theoretical framework. The current UI suffers from fragmentation between the legacy monolithic `app.js` and the new modular architecture (`modules/*.js`).

The following schema unifies the UI around the **Holarchic** nature of the codebase (Atoms → Molecules → Cells → Organisms) and the **RPBL** (Responsibility, Purity, Boundary, Lifecycle) dimensions.

### Architectural Analysis

1.  **Topological Structure**: The controls must allow traversal of the **16-Level Scale**. We currently lack explicit controls for `L4 CONTAINER` (Classes) vs `L3 NODE` (Functions) filtering.
2.  **Knot Detection**: We need visualization modes specifically for **Cyclic Dependencies** (Knots), which are currently hidden in the general `force` layout.
3.  **Purpose Field**: The `color-engine.js` supports coloring by `roleCategory` and `subsystem`, but the UI lacks a dedicated "Purpose Gradient" mode to visualize the flow from Infrastructure → Domain → Presentation.

---

### Complete UI Controls Schema

```json
{
  "schema_version": "2.0",
  "meta": {
    "project": "Collider",
    "architecture": "Standard Model of Code",
    "renderer": "3d-force-graph"
  },
  "categories": [
    {
      "id": "VIEW_MODES",
      "label": "Holarchic View",
      "controls": [
        {
          "id": "view-mode-toggle",
          "label": "Granularity",
          "type": "toggle_group",
          "options": [
            { "value": "atoms", "label": "ATOMS (L3)", "desc": "Functions & Methods" },
            { "value": "files", "label": "FILES (L5)", "desc": "File Modules" },
            { "value": "containers", "label": "CLASSES (L4)", "desc": "Classes & Structs (Proposed)" }
          ],
          "default": "atoms",
          "state_path": "GRAPH_MODE",
          "handler_module": "SIDEBAR",
          "priority": "P0"
        },
        {
          "id": "btn-2d",
          "label": "Dimension",
          "type": "button_toggle",
          "options": ["2D", "3D"],
          "default": "3D",
          "state_path": "IS_3D",
          "handler_module": "DIMENSION",
          "priority": "P0"
        }
      ]
    },
    {
      "id": "LAYOUT_PHYSICS",
      "label": "Topology & Physics",
      "controls": [
        {
          "id": "layout-preset",
          "label": "Structure Strategy",
          "type": "select_grid",
          "options": [
            { "value": "force", "label": "Force" },
            { "value": "tree", "label": "Tree" },
            { "value": "radial", "label": "Radial" },
            { "value": "orbital", "label": "Orbital" },
            { "value": "codome", "label": "Codome" }
          ],
          "default": "force",
          "state_path": "ANIM.currentLayout",
          "handler_module": "ANIM",
          "priority": "P0"
        },
        {
          "id": "physics-charge",
          "label": "Repulsion (Charge)",
          "type": "slider",
          "range": { "min": -500, "max": 0, "step": 10 },
          "default": -120,
          "state_path": "PHYSICS_STATE.charge",
          "handler_module": "PHYSICS",
          "priority": "P1"
        },
        {
          "id": "physics-link",
          "label": "Edge Elasticity",
          "type": "slider",
          "range": { "min": 10, "max": 200, "step": 5 },
          "default": 50,
          "state_path": "PHYSICS_STATE.linkDistance",
          "handler_module": "PHYSICS",
          "priority": "P1"
        },
        {
          "id": "physics-gravity",
          "label": "Center Gravity",
          "type": "slider",
          "range": { "min": 0, "max": 0.5, "step": 0.01 },
          "default": 0.05,
          "state_path": "PHYSICS_STATE.centerStrength",
          "handler_module": "PHYSICS",
          "priority": "P2"
        },
        {
          "id": "btn-freeze",
          "label": "Freeze Simulation",
          "type": "button_toggle",
          "default": false,
          "state_path": "LAYOUT_FROZEN",
          "handler_module": "LAYOUT_HELPERS",
          "priority": "P1"
        }
      ]
    },
    {
      "id": "NODE_APPEARANCE",
      "label": "Node Semantics",
      "controls": [
        {
          "id": "node-color-mode",
          "label": "Color Dimension",
          "type": "select_dropdown",
          "options": [
            { "value": "tier", "label": "Architectural Tier" },
            { "value": "family", "label": "Atom Family" },
            { "value": "roleCategory", "label": "Role (Pattern)" },
            { "value": "layer", "label": "Layer (Clean Arch)" },
            { "value": "rpbl_responsibility", "label": "RPBL: Responsibility" },
            { "value": "rpbl_purity", "label": "RPBL: Purity" },
            { "value": "flow", "label": "Flow (Entrance/Exit)" }
          ],
          "default": "tier",
          "state_path": "VIS_STATE.colorBy",
          "handler_module": "SIDEBAR",
          "priority": "P0"
        },
        {
          "id": "cfg-node-size",
          "label": "Base Size",
          "type": "slider",
          "range": { "min": 0.2, "max": 4.0, "step": 0.1 },
          "default": 1.0,
          "state_path": "APPEARANCE_STATE.nodeScale",
          "handler_module": "SIDEBAR",
          "priority": "P1"
        },
        {
          "id": "node-size-mode",
          "label": "Size By",
          "type": "select_buttons",
          "options": [
            { "value": "uniform", "label": "Uniform" },
            { "value": "complexity", "label": "Complexity" },
            { "value": "fan_in", "label": "Fan-In" },
            { "value": "loc", "label": "LOC" }
          ],
          "default": "uniform",
          "state_path": "VIS_STATE.sizeBy",
          "handler_module": "NODE_HELPERS",
          "priority": "P1"
        },
        {
          "id": "cfg-toggle-labels",
          "label": "Show Labels",
          "type": "toggle",
          "default": true,
          "state_path": "VIS_FILTERS.metadata.showLabels",
          "handler_module": "SIDEBAR",
          "priority": "P1"
        }
      ]
    },
    {
      "id": "EDGE_APPEARANCE",
      "label": "Coupling & Flow",
      "controls": [
        {
          "id": "edge-mode",
          "label": "Connection Style",
          "type": "select_dropdown",
          "options": [
            { "value": "type", "label": "Semantic Type" },
            { "value": "gradient-tier", "label": "Tier Flow (Gradient)" },
            { "value": "gradient-flow", "label": "Markov Probability" },
            { "value": "gradient-depth", "label": "Call Depth" }
          ],
          "default": "type",
          "state_path": "EDGE_MODE",
          "handler_module": "EDGE",
          "priority": "P0"
        },
        {
          "id": "cfg-edge-opacity",
          "label": "Opacity",
          "type": "slider",
          "range": { "min": 0, "max": 1, "step": 0.05 },
          "default": 0.6,
          "state_path": "APPEARANCE_STATE.edgeOpacity",
          "handler_module": "SIDEBAR",
          "priority": "P1"
        },
        {
          "id": "cfg-particle-speed",
          "label": "Flow Rate",
          "type": "slider",
          "range": { "min": 0, "max": 0.05, "step": 0.001 },
          "default": 0.01,
          "state_path": "FLOW_CONFIG.particleSpeed",
          "handler_module": "FLOW",
          "priority": "P2"
        },
        {
          "id": "filter-edges",
          "label": "Filter Relationships",
          "type": "multi_select_chips",
          "options": ["calls", "contains", "inherits", "imports"],
          "default": [],
          "state_path": "VIS_FILTERS.edges",
          "handler_module": "SIDEBAR",
          "priority": "P1"
        }
      ]
    },
    {
      "id": "FILTERS",
      "label": "Data Filters",
      "controls": [
        {
          "id": "filter-tier",
          "label": "Filter Tiers",
          "type": "multi_select_chips",
          "options": ["T0", "T1", "T2"],
          "default": [],
          "state_path": "VIS_FILTERS.tiers",
          "handler_module": "SIDEBAR",
          "priority": "P0"
        },
        {
          "id": "filter-ring",
          "label": "Filter Rings",
          "type": "multi_select_chips",
          "options": ["DOMAIN", "APPLICATION", "INFRASTRUCTURE", "PRESENTATION"],
          "default": [],
          "state_path": "VIS_FILTERS.rings",
          "handler_module": "SIDEBAR",
          "priority": "P1"
        },
        {
          "id": "toggle-orphans",
          "label": "Hide Orphans",
          "type": "toggle",
          "default": false,
          "state_path": "VIS_FILTERS.hideOrphans",
          "handler_module": "DATA",
          "priority": "P2"
        }
      ]
    },
    {
      "id": "ANALYSIS",
      "label": "Intelligence & Insights",
      "controls": [
        {
          "id": "btn-insights",
          "label": "AI Insights",
          "type": "button",
          "action": "openPanel('insights')",
          "handler_module": "PANELS",
          "priority": "P1"
        },
        {
          "id": "btn-report",
          "label": "Brain Download",
          "type": "button",
          "action": "openPanel('report')",
          "handler_module": "PANELS",
          "priority": "P2"
        },
        {
          "id": "toggle-codome",
          "label": "Show CoDome Boundaries",
          "type": "toggle",
          "default": false,
          "state_path": "APPEARANCE_STATE.showCodome",
          "handler_module": "SIDEBAR",
          "priority": "P2"
        }
      ]
    }
  ]
}
```

### Implementation Gap Analysis

Current gaps identified between `src/core/viz/assets/modules/*.js` and the professional standard (Neo4j Bloom/Gephi):

1.  **Selection & Search**:
    *   *Missing:* A global search bar ("Command Palette") to find nodes by name, file path, or ID.
    *   *Action:* Implement a search module in `control-bar.js`.

2.  **Data-Driven Styling**:
    *   *Missing:* While `color-engine.js` is powerful, the UI (`control-bar.js`) only exposes rudimentary mapping. We need a "Data Mapper" UI to bind arbitrary metrics (e.g., `cyclomatic_complexity`) to visual properties (e.g., `nodeSize`).

3.  **Topological Filtering**:
    *   *Missing:* "K-Hop" filtering (show only neighbors of selected nodes within K steps). This is crucial for debugging spaghetti code.
    *   *Action:* Add `neighbor-depth` slider to `selection.js`.

4.  **Export/Snapshot**:
    *   *Missing:* High-res image export with transparent background, or data export of the current filtered subgraph (JSON/CSV).
    *   *Action:* Enhance `SIDEBAR` actions section.

### Topological Structures

To visualize the **Standard Model**, the following specific configurations should be applied via the `layout-preset` control:

*   **Atoms (L3)**: Best viewed with `force` layout, colored by `Role` or `Tier`.
*   **Rings**: Best viewed with `radial` layout (Domain center, Infra outer).
*   **Flow/Pipes**: Best viewed with `flow` edge mode + `gradient-flow` coloring to see the `Markov` probability chains.
*   **Layers**: Best viewed with `tree` layout (top-down) or `codome` (if spatial segregation is needed).

---

## Citations

_No citations provided_
