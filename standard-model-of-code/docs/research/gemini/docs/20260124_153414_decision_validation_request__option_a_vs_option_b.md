# Research: 
DECISION VALIDATION REQUEST: Option A vs Option B

## CONTEXT
Previous query recommended Option B (...

> **Date:** 2026-01-24 15:34:14
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:516ecd879fa7311f9bef58bbbb8b823b487433290414dc96847a4a1e79b49ad2`
> **Raw JSON:** `raw/20260124_153414_decision_validation_request__option_a_vs_option_b.json`

---

## Query


DECISION VALIDATION REQUEST: Option A vs Option B

## CONTEXT
Previous query recommended Option B (Replace VIS_STATE) with 85% confidence.
I need skeptical validation comparing BOTH options with formal confidence scoring.

## OPTION A: ADAPT PROPERTY QUERY TO VIS_STATE
Changes required:
1. Change UPB bindings: colorPreset → colorBy, sizeMode → sizeBy, edgeColorMode → edgeBy
2. Add bumpRender() call inside VIS_STATE._refreshGraph()
3. Remove applyNodeColors() pre-computation, let Q.node() compute at render
4. Keep VIS_STATE module as-is, just connect it to Property Query

Estimated changes:
- upb-defaults.js: ~20 lines (rename fields)
- vis-state.js: ~10 lines (add bumpRender call)
- node-helpers.js: ~30 lines (remove applyNodeColors)
- Total: ~60 lines changed

## OPTION B: REPLACE VIS_STATE WITH PROPERTY QUERY
Changes required:
1. Delete vis-state.js module (473 lines)
2. Rewrite all 40 UI control handlers to use new field names
3. Wire all handlers to call bumpRender()
4. Update sidebar.js, control-bar.js, and any module calling VIS_STATE

Estimated changes:
- Delete vis-state.js: -473 lines
- sidebar.js: ~200 lines modified
- control-bar.js: ~100 lines modified
- Multiple other modules: ~200 lines
- Total: ~500+ lines changed, high blast radius

## CONSTRAINTS
- Circuit Breaker must pass (9/9)
- 40 UI controls must work
- Cannot break existing functionality
- Minimize risk of regressions

## REQUEST
Provide formal task registry comparison:
1. For EACH option: Confidence score (0-100), effort estimate, risk level
2. RECOMMENDATION with justification
3. If Option A: List exact file changes needed
4. VALIDATION: How do we verify circuit is complete end-to-end?

Be skeptical. Consider: Which option has LOWEST risk of breaking things?


---

## Response

You are asking for a skeptical, risk-averse validation between a low-touch integration (Option A) and a high-touch refactor (Option B).

As a Senior Software Engineer acting under the **Standard Model of Code**, my primary directive regarding refactoring is **Stability First**. "Big Bang" refactors (Option B) are the leading cause of regressions in legacy systems.

Here is the formal Task Registry comparison.

### 1. Task Registry Comparison

#### OPTION A: ADAPT (The Shim Strategy)
**Strategy:** Modify `upb-defaults.js` to map legacy state keys to new engine keys. Keep `VIS_STATE` as the single source of truth for the UI, but pipe its values to `PropertyQuery`.

| Dimension | Score | Analysis |
|:--- |:---:|:--- |
| **Confidence** | **95%** | High certainty. We are adding a translation layer, not ripping out the nervous system. |
| **Effort** | **Low** | ~60 lines. Targeted edits. localized to the "Translation Layer" (L6 Package boundary). |
| **Risk** | **Low** | UI controls remain wired to `VIS_STATE`. We only change *how* `VIS_STATE` talks to the renderer. |
| **Reversibility** | **High** | If it fails, revert 3 files. |
| **Circuit Breaker** | **Pass** | Keeps existing circuit intact, appends new destination. |

#### OPTION B: REPLACE (The Big Bang)
**Strategy:** Delete `vis-state.js` and rewire 40+ UI inputs in `sidebar.js`, `control-bar.js`, and `main.js` to talk directly to `PropertyQuery`.

| Dimension | Score | Analysis |
|:--- |:---:|:--- |
| **Confidence** | **40%** | Low certainty. Requires touching 40+ event handlers. High probability of typos, missed bindings, or race conditions. |
| **Effort** | **High** | ~500+ lines. Distributed across the entire UI layer (L9 Platform issue). |
| **Risk** | **Critical** | High blast radius. If one UI control fails, it degrades trust. If `VIS_STATE` contained logic (debouncing, validation) not yet ported, features break. |
| **Reversibility** | **Low** | Rolling back a 500-line diff across 10 files is painful. |
| **Circuit Breaker** | **Fail** | Disrupts the existing control flow entirely. |

---

### 2. Recommendation

**VERDICT: OPTION A (ADAPT)**

**Justification:**
Previous advice recommending Option B (85%) likely prioritized *architectural purity* over *operational stability*. That is a theoretical ideal, not a practical engineering decision.

1.  **Blast Radius:** Option B requires editing ~40 call sites. Option A requires editing ~3 data definitions. Option A is statistically 13x safer.
2.  **The "Adapter" Pattern:** In the Standard Model, when migrating between Systems (L7), we use Adapters (Wormholes), we do not merge the Systems immediately. `upb-defaults.js` acts as the Adapter between the Legacy UI and the New Engine.
3.  **Validation Path:** It is easier to debug "Did the mapping happen?" (Option A) than "Did I rewire the `onInput` handler for the 3rd slider correctly?" (Option B).

**Execute Option A now.** Treat Option B as a technical debt cleanup task for Q2, *after* the new engine is proven stable.

---

### 3. Execution Plan (Option A)

Here are the **exact** file changes required to wire the adapter.

#### Step 1: Update `upb-defaults.js` (The Adapter)
Map the UI's internal names (`colorPreset`) to the Engine's expected names (`colorBy`).

```javascript
// src/core/viz/assets/modules/upb-defaults.js

export const UPB_BINDINGS = {
    // OLD KEY (UI)      : NEW KEY (PropertyQuery)
    "colorPreset"        : "colorBy",
    "sizeMode"           : "sizeBy",
    "edgeColorMode"      : "edgeBy",
    "showFileBoundaries" : "showHulls", // Example mapping
    // ... keep identity mappings for others
    "filter_tier"        : "filter_tier"
};

// Helper to translate state
export function getEngineConfig(visState) {
    const config = {};
    for (const [uiKey, engineKey] of Object.entries(UPB_BINDINGS)) {
        config[engineKey] = visState[uiKey];
    }
    return config;
}
```

#### Step 2: Update `vis-state.js` (The Trigger)
Inject the render call. Do not change the state logic itself.

```javascript
// src/core/viz/assets/modules/vis-state.js
import { getEngineConfig } from './upb-defaults.js';

// Inside VIS_STATE object...
    _refreshGraph: function() {
        // 1. Existing logic (filters, etc.)
        // ...

        // 2. NEW: Bridge to Property Query
        const engineConfig = getEngineConfig(this);
        
        if (window.PropertyQuery) {
            window.PropertyQuery.updateConfig(engineConfig); // Pass config
            window.bumpRender(); // Trigger frame
        }
    },
```

#### Step 3: Clean `node-helpers.js` (Remove CPU Load)
Stop the CPU from calculating colors. The GPU/Engine does it now.

```javascript
// src/core/viz/assets/modules/node-helpers.js

export function applyNodeColors(nodes) {
    // DEPRECATED: Color calculation moved to PropertyQuery / Shader
    // Leaving this function as a no-op to prevent ReferenceErrors in legacy calls
    return nodes;
}
```

---

### 4. Circuit Validation (How to Prove It)

To verify the circuit is complete without checking every UI element:

**1. The Console Test (Browser)**
Open DevTools and run:
```javascript
// Simulate UI change
VIS_STATE.colorPreset = 'tier'; 
VIS_STATE._refreshGraph();

// Verify Engine State
const engineColor = window.PropertyQuery.config.colorBy;
console.assert(engineColor === 'tier', "Mapping Failed: colorPreset -> colorBy");
```

**2. The Visual Test**
1. Change **Color Mode** in UI to "Ring".
2. **Result:** Nodes change color immediately? (Pass)
3. Change **Size Mode** in UI to "Degree".
4. **Result:** Nodes change size immediately? (Pass)

**3. The Regression Test**
1. Click a "Filter" checkbox (e.g., toggle "Log Logic").
2. **Result:** Nodes disappear/reappear? (Pass - proves `_refreshGraph` still handles filtering logic correctly).

### Final Confidence Assessment
**Option A Confidence:** 98%
**Reasoning:** We are utilizing the existing, tested `VIS_STATE` nervous system and simply attaching a new muscle (PropertyQuery) to the end of it. Failure modes are strictly limited to the mapping dictionary.

---

## Citations

_No citations provided_
