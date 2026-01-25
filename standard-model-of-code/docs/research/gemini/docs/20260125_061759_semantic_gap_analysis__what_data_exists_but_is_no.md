# Research: 
SEMANTIC GAP ANALYSIS: What data exists but is NOT connected?

Cross-reference these sources:
1. do...

> **Date:** 2026-01-25 06:17:59
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:7ffc2ca7d2ac8731b4d1d319184de24d3e93839d6dd2745fb203314c6eb2adc5`
> **Raw JSON:** `raw/20260125_061759_semantic_gap_analysis__what_data_exists_but_is_no.json`

---

## Query


SEMANTIC GAP ANALYSIS: What data exists but is NOT connected?

Cross-reference these sources:
1. docs/ui/corpus/v1/manifest.json
2. docs/ui/corpus/v1/extracted/*.json
3. docs/ui/overhaul/*.md
4. schema/viz/tokens/*.json
5. src/core/viz/assets/modules/*.js

Find:
- Data that exists in multiple places but isn't linked
- Concepts mentioned in docs but not implemented
- Implementation details not documented
- Orphaned systems (code exists, no docs)
- Missing integration points

Output as structured inventory.


---

## Response

Based on the cross-reference of the provided context files, specifically `COLLIDER_ARCHITECTURE.md`, `DATA_LAYER_REFACTORING_MAP.md`, `ASSET_INVENTORY.md`, and the configuration files, here is the structured Semantic Gap Analysis.

### ⚠️ CRITICAL FINDING: THE "GHOST CORPUS"
The most significant gap is the reference to `docs/ui/corpus/v1/manifest.json`. **This file does not exist in the provided repository inventory.**
*   **Evidence:** `ASSET_INVENTORY.md` lists reference datasets (`HADRONS_96.md`, `RPBL_1440.csv`), but no "UI Corpus".
*   **Implication:** The prompt implies a data structure for UI hydration (`manifest.json` + `extracted/*.json`) that is likely planned or local-only, but the codebase (specifically `visualize_graph_webgl.py`) is currently using a monolithic `unified_analysis.json` output pattern.

---

### 1. DATA DISCONNECTS (Exists but not Linked)

| Data Source | Current State | Missing Link |
| :--- | :--- | :--- |
| **Hadrons (96)** | Exists in `context-management/reference_datasets/HADRONS_96.md` | **Not wired to Viz:** The visualization engine (`visualize_graph_webgl.py`) processes Atoms, Roles, and Tiers, but has no logic to ingest or visualize the "Hadron" composite structures defined in the reference dataset. |
| **Continents (12)** | Mentioned in `ASSET_INVENTORY.md` as "Partial/Missing" | **No Schema Definition:** Unlike Atoms and Roles, there is no `schema/fixed/continents.json`. The concept exists in theory docs but has no data structure for the tool to consume. |
| **Design Tokens** | `schema/viz/tokens/*.json` defined in `COLLIDER_ARCHITECTURE.md` | **Hardcoded Implementation:** `DATA_LAYER_REFACTORING_MAP.md` reveals that `visualize_graph_webgl.py` still relies on internal `NODE_COLOR_MODE` logic (lines ~1333) rather than dynamically loading the JSON token definitions. |

### 2. CONCEPTUAL GAPS (Docs vs. Implementation)

**A. The Token Resolver Mirage**
*   **Documented:** `COLLIDER_ARCHITECTURE.md` describes a `TokenResolver` Singleton that loads `appearance.tokens.json` and `controls.tokens.json`.
*   **Implemented:** `DATA_LAYER_REFACTORING_MAP.md` shows the actual code uses global state variables (`VIS_FILTERS`, `ACTIVE_DATAMAPS`) and manual color mode switches (`setNodeColorMode`).
*   **Gap:** The "Token System" is currently architectural fiction; the code is still imperative.

**B. The "Worker" Discrepancy**
*   **Documented:** Architecture docs describe a pipeline flow.
*   **Implemented:** `visualize_graph_webgl.py` (Line 1721) relies on a `Worker.postMessage` mechanism to handle `FULL_GRAPH`.
*   **Gap:** The threading/worker model—critical for performance—is absent from `COLLIDER_ARCHITECTURE.md`, which focuses on logical data flow rather than runtime execution flow.

### 3. ORPHANED SYSTEMS (Code without Connection)

**A. The JS Modules (`src/core/viz/assets/modules/*.js`)**
*   **Status:** Referenced in `analysis_sets.yaml` under `viz_core`.
*   **Disconnect:** The main analysis script (`visualize_graph_webgl.py`) generates a massive HTML file (5559 lines). It is unclear how or if these modular JS files are bundled into that output.
*   **Risk:** The codebase appears to be split between a "Legacy Monolith" generator (Python) and a "Modern Modular" frontend (JS) without a clear build pipeline connecting them.

**B. The `markov` Data Key**
*   **Status:** `DATA_LAYER_REFACTORING_MAP.md` identifies `data.get("markov", {})` at line 264.
*   **Disconnect:** While the Python backend computes it, the visualization logic for "Flow Mode" (`applyFlowVisualization`) accesses it directly from globals, bypassing the proposed `DataManager` structure. It is a "floating" dataset not indexed for O(1) access.

### 4. MISSING INTEGRATION POINTS

**A. The DataManager Gap**
*   `DATA_LAYER_REFACTORING_MAP.md` explicitly calls for a `DataManager` class to solve "Scattered Lookups" and "No Reactive Updates".
*   **Current State:** Data is accessed via 24 disparate `FULL_GRAPH` calls and 26 `Graph.graphData()` calls.
*   **Missing:** The centralized API to mediate between the Raw Data (JSON) and the Visualizer (WebGL).

**B. The "Brain Download" Bridge**
*   **Documented:** `TOOL.md` claims the `brain_download` report is embedded in the HTML.
*   **Implemented:** `DATA_LAYER_REFACTORING_MAP.md` lists `BD["brain_download"]` in the Output flow.
*   **Gap:** There is no "toggle" or interaction logic documented that explains *how* the 3D graph interacts with the text report (e.g., clicking a node highlighting the relevant section in the Brain Download).

### 5. RECOMMENDATION: REMEDIATION TASKS

Based on this inventory, the following immediate actions are required to close the semantic gaps:

1.  **Locate/Create UI Corpus:** Clarify if `docs/ui/corpus/v1/` is a missing file or a future spec. If future, create a placeholder schema.
2.  **Implement TokenResolver:** Refactor `visualize_graph_webgl.py` to actually load and use `schema/viz/tokens/*.json` instead of hardcoded color switches.
3.  **Wire Hadrons:** Add a processor in the Python backend to read `HADRONS_96.md` and inject "Hadron ID" into the `UnifiedNode` dimensions.
4.  **Formalize DataManager:** Execute the refactoring plan to create the `DataManager` class in JS, serving as the single source of truth for the frontend.

---

## Citations

_No citations provided_
