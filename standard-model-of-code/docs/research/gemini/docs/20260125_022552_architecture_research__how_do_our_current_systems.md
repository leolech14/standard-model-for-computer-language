# Research: ARCHITECTURE RESEARCH: How do our current systems handle semantic matching and value mapping?

QUEST...

> **Date:** 2026-01-25 02:25:52
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:4de84794bb1644574eb54c627e4ed05e49b904e14473b57c9e03aaf08e800f8b`
> **Raw JSON:** `raw/20260125_022552_architecture_research__how_do_our_current_systems.json`

---

## Query

ARCHITECTURE RESEARCH: How do our current systems handle semantic matching and value mapping?

QUESTIONS:
1. In property-query.js, how does the provider chain resolve values? What's the priority system?
2. In color-engine.js, how are categorical values (tier, family) mapped to continuous values (hue, chroma)?
3. In control-bar.js, how does the SCALES object transform values? What patterns exist?
4. Is there a central registry of all possible mappings, or are they scattered?
5. How does vis-state.js coordinate between different value domains?

Looking for: Existing patterns we can consolidate into the Data Trade Exchange (DTE).

OUTPUT: Pattern inventory with file:line references.

---

## Response

As Chief Architect, I have analyzed the codebase to map the current semantic matching and value transformation topologies.

The system currently exhibits a **Fragmented Translation Topology**. While individual modules (`color-engine.js`, `property-query.js`) demonstrate high coherence, the logic for mapping *Data Atoms* (Semantics) to *Visual Atoms* (Graphics) is distributed across three distinct layers, creating a "Logic Knot" in `node-helpers.js`.

Here is the architectural breakdown.

### 1. Property Query Resolution (The Arbiter)
**File:** `src/core/viz/assets/modules/property-query.js`

The `property-query.js` module implements a **Chain of Responsibility** pattern to resolve values. It does not know *what* the value means, only *where* to get it.

*   **Mechanism:** `resolve()` (Lines 218-278) iterates through a sorted array of providers.
*   **Priority System (Lines 203-207):**
    1.  **`OVERRIDE` (Priority 100):** Explicit UI overrides (e.g., global slider for "Node Size").
    2.  **`UPB` (Priority 80):** Unified Property Binder. Context-aware bindings (e.g., "Map Token Count to Size").
    3.  **`RAW` (Priority 20):** Intrinsic data fields on the UnifiedNode.
    4.  **`DEFAULT` (Fallback):** Schema defaults.

**Architectural Note:** This is the ideal insertion point for the DTE. Currently, the `UPB` provider (Lines 163-200) is the only "smart" layer, but it relies on an external config (`window.UPB_CONFIG`) rather than a negotiated exchange.

### 2. Color Engine Mapping (The Palette)
**File:** `src/core/viz/assets/modules/color-engine.js`

The Color Engine uses two distinct mapping topologies:

*   **Discrete Mapping (Categorical):**
    *   **Mechanism:** `palette` object (Lines 20-130).
    *   **Pattern:** Dictionary Lookup.
    *   **Mapping:** Semantic Keys (`T0`, `LOG`, `Service`) $\rightarrow$ Fixed OKLCH Constants.
    *   **Observation:** This is a static "Trade Agreement." The hue for "Service" is hardcoded to `h: 270` (Line 104). The DTE should make this negotiable.

*   **Continuous Mapping (Intervals):**
    *   **Mechanism:** `intervals` object (Lines 145-218) and `getInterval` (Lines 603-647).
    *   **Pattern:** Linear Interpolation (Lerp).
    *   **Mapping:** Normalized Scalar $[0, 1]$ $\rightarrow$ Gradient Path.
    *   **Topology:** The `schemePaths` (Lines 225-500) define 3D paths through color space (e.g., 'helix', 'viridis').

### 3. Control Bar Transformations (The Interface)
**File:** `src/core/viz/assets/modules/control-bar.js`

The Control Bar is a **UI Controller** that delegates the actual mathematics.

*   **Mechanism:** It creates a config object (`_config`) and passes it to `window.UPB.bind` (Line 431).
*   **Transformations:** `SCALES` (Lines 40-42) acts as a facade. It currently defaults to linear normalization: `(v - min) / (max - min)`.
*   **Ad-Hoc Range Calculation:** Lines 445-452 show `control-bar.js` attempting to calculate min/max ranges itself if `DATA.getRange` is unavailable. This is a **Leaky Abstraction**; the DTE should provide normalized data streams, relieving the UI of statistical analysis.

### 4. Registry Centralization (The Scatter)
**Status:** **Highly Scattered.**

There is no central registry. Mappings exist in isolated islands:

1.  **Semantic $\rightarrow$ Color:** `color-engine.js` (Lines 20-130).
2.  **Node State $\rightarrow$ Visual Mode:** `node-helpers.js` (Lines 22-55). This is the "Logic Knot." `MODE_ACCESSORS` manually maps `tier`, `layer`, `complexity`, etc., to specific calls in the Color Engine.
3.  **Data Source Options:** `control-bar.js` (Lines 77-113) hardcodes the list of available metrics (`token_estimate`, `complexity_density`, etc.).
4.  **UI $\rightarrow$ Command:** `registry.js` (Lines 14-68) handles command dispatch but not data mapping.

### 5. Vis-State Coordination (The State Container)
**File:** `src/core/viz/assets/modules/property-query-init.js` (Proxy for `vis-state.js`)

The `vis-state.js` (inferred from usage) acts as a **State Container**, not a coordinator.

*   It holds the "Current Selection" (e.g., `colorBy = 'tier'`).
*   It uses an **Epoch System** (`bumpRender`, Line 139 in `property-query-init.js`) to invalidate caches.
*   **Coordination Gap:** It does not enforce consistency. You can set `colorBy = 'flow'` while the edge mode is incompatible. The DTE needs to enforce topological consistency between dimensions.

---

## Pattern Inventory for DTE Consolidation

We can refactor these scattered patterns into the **Data Trade Exchange (DTE)**.

| Pattern Name | Source File:Lines | Description | DTE Opportunity |
| :--- | :--- | :--- | :--- |
| **Provider Chain** | `property-query.js`:203 | Priority-based value resolution | The DTE becomes the primary Provider (Priority 90), replacing ad-hoc UPB bindings. |
| **Semantic Dictionary** | `color-engine.js`:20 | Hardcoded mapping of `Key -> OKLCH` | Convert to **Semantic Ledger**. Allow themes to swap "Service" from Purple to Blue dynamically. |
| **Mode Accessor Switch** | `node-helpers.js`:22 | Maps state strings to color functions | **Critical Refactor.** Replace this hardcoded map with DTE "Trade Routes" (Data $\rightarrow$ Visualizer). |
| **Interval Interpolation** | `color-engine.js`:639 | Maps `0..1` to Color Gradient | Generalize into **Transfer Functions**. Allow mapping `0..1` to Size, Opacity, or Position, not just Color. |
| **Range Normalization** | `control-bar.js`:448 | Calculates min/max for scaling | Centralize in DTE **Normalization Layer**. Ensure all metrics are $0..1$ before reaching the renderer. |
| **Fallback Inference** | `node-accessors.js`:37 | Infers Tier (`T0`) from string prefix | Formalize as **Ingest Rules**. Raw data should be normalized into Atoms before visualization. |

### Architectural Recommendation

The **Logic Knot** in `node-helpers.js` (Lines 22-55) is the primary target. It tightly couples specific node fields (`rpbl.purity`) to specific color engine methods (`getInterval`).

**Strategy:**
1.  Extract `MODE_ACCESSORS` into the DTE.
2.  Abstract the inputs as **Signals** (e.g., `Signal('purity')`).
3.  Abstract the outputs as **Channels** (e.g., `Channel('color')`).
4.  The DTE manages the subscription: `Signal('purity')` $\rightarrow$ `TransferFunction` $\rightarrow$ `Channel('color')`.

---

## Citations

_No citations provided_
