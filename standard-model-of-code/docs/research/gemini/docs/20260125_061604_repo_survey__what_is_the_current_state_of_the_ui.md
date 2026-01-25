# Research: 
REPO SURVEY: What is the current state of the UI Overhaul?

List:
1. All corpus artifacts created (...

> **Date:** 2026-01-25 06:16:04
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:8eeb5747de942616cc9203a6bd7fdac4cbbe62dd5e06a65db19c20bf23314b73`
> **Raw JSON:** `raw/20260125_061604_repo_survey__what_is_the_current_state_of_the_ui.json`

---

## Query


REPO SURVEY: What is the current state of the UI Overhaul?

List:
1. All corpus artifacts created (with validation status)
2. All pending Phase 2 items
3. Key blockers for Phase 3-6
4. Critical integration points between systems
5. What data exists but hasn't been connected semantically


---

## Response

Based on a comprehensive review of the provided codebase context, the UI Overhaul is in a **mature transitional state (Late Phase 2)**. The system has successfully moved from a monolithic architecture (`app.js`) to a modular, component-based architecture, though the "legacy monolith" still exists as the final loading step.

Here is the detailed survey of the current state:

### 1. Corpus Artifacts Created & Validation Status

The core infrastructure ("The Corpus") is established. Validation is handled primarily by the **Circuit Breaker** module.

| Artifact | File | Status | Validation Method |
| :--- | :--- | :--- | :--- |
| **Module Registry** | `modules/main.js` | **Active** | Validates presence of 15 core modules at runtime (`REQUIRED_MODULES`). |
| **Control Validator** | `modules/circuit-breaker.js` | **Active** | **High Confidence.** Automated runtime testing of UI controls against internal state (`runAll()`). Currently tests sliders, toggles, and buttons. |
| **Color Contract** | `modules/color-contract-test.js` | **Active** | **High Confidence.** Ensures OKLCH engine outputs valid Hex codes and handles edge cases/gamut clipping. |
| **Data Gatekeeper** | `modules/data-manager.js` | **Active** | Self-tests node/edge integrity on init. Replaces direct access to `FULL_GRAPH`. |
| **Layout Engine** | `modules/layout.js` | **Active** | Replaces `HudLayoutManager`. Includes debug overlay (`Ctrl+Shift+L`) to validate panel bounding boxes. |
| **UI Skeleton** | `template.html` | **Stable** | Defines the dual-sidebar layout, command bar, and HUD containers used by modules. |

### 2. Pending Phase 2 Items (Data Binding & Property Resolution)

Phase 2 focuses on "Universal Property Binding" (UPB)—decoupling UI controls from specific graph mutations.

*   **Full UPB Integration:** While `modules/property-query.js` (The "Q" engine) is implemented to resolve properties via `Overrides > UPB > Raw > Default`, the **`sidebar.js`** module still contains legacy direct bindings.
    *   *Current:* Sliders directly call `Graph.d3Force(...)`.
    *   *Required:* Sliders should update `VIS_STATE`, and the Renderer should read from `Q.node()` or `Q.edge()`.
*   **Control Bar Connection:** `modules/control-bar.js` implements the UI for mapping data sources to visual targets, but the actual execution relies on `window.UPB` which needs to be fully wired into the renderer loop in `main.js` / `app.js`.
*   **State Serialization:** The `VIS_STATE` object needs a formal serialization method to save/load the entire visualization configuration (layout + colors + physics) as a single "Preset".

### 3. Key Blockers for Phase 3-6 (Interactivity, Intelligence, & Polish)

*   **Legacy Monolith (`app.js`):** `modules/main.js` loads `app.js` last. This legacy file likely still owns the `Graph` (3d-force-graph) initialization loop. Until initialization is moved to a dedicated module, advanced physics and rendering features (Phase 3) cannot be fully isolated.
*   **Global Graph Dependency:** Almost all modules (`sidebar.js`, `edge-system.js`, `physics.js`) rely on `window.Graph` being globally available. This makes unit testing logic difficult and prevents multi-graph scenarios.
*   **Renderer Abstraction:** There is no "Renderer Module." The `3d-force-graph` instance is manipulated directly by multiple modules. A facade is needed to mediate between the Logic modules (Physics, Layout) and the Render library.

### 4. Critical Integration Points

These are the semantic bridges that hold the system together:

*   **The "Q" Object (`property-query.js`):** The single bottleneck for rendering decisions.
    *   *Integration:* `Graph.nodeColor(n => Q.node(n, 'color'))`
*   **The Data Manager (`data-manager.js`):** The single source of truth for graph data.
    *   *Integration:* Replaces `graphData` calls. Provides O(1) lookups (`index.nodeById`, `index.nodesByTier`) used by `legend-manager.js` and `sidebar.js`.
*   **The Color Engine (`color-engine.js`):** The translation layer for data-to-pixel.
    *   *Integration:* Used by `node-helpers.js`, `edge-system.js`, and `legend-manager.js` to ensure consistent palette application via OKLCH.
*   **The Event Bus (Implicit):** Currently relying on `window` level functions (e.g., `refreshGraph`, `applyEdgeMode`) defined in `main.js` shims. This needs to move to a formal `Events` module.

### 5. Disconnected Data (Exists but not Semantically Connected)

The following data is present in `DATA` or the DOM but not fully utilized in the 3D visualization:

*   **AI Insights -> Graph Selection:** `modules/report.js` renders "Risk Areas" and "Refactoring Opportunities," but clicking them does not select/zoom the relevant nodes in the 3D graph.
*   **Pipeline Snapshot -> Visual State:** `modules/pipeline-navigator.js` visualizes the build pipeline, but it doesn't affect the graph. (e.g., You cannot "rewind" the graph to see what it looked like at the "edge_extraction" stage).
*   **Codome Boundaries:** `data-manager.js` merges `codome_boundaries`, but they are currently just rendered as standard nodes/edges. The *concept* of the boundary (a membrane or distinct zone) is visually indistinct from standard clusters.
*   **RPBL Metrics:** The "Responsibility, Purity, Boundary, Lifecycle" scores exist in `node-helpers.js`, but there is no specific "RPBL Dashboard" or specialized visualization mode to view these 4 dimensions simultaneously.

---

## Citations

_No citations provided_
