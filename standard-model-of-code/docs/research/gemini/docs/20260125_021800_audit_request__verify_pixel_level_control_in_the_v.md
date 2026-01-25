# Research: AUDIT REQUEST: Verify pixel-level control in the visualization system.

QUESTIONS:
1. Is every visua...

> **Date:** 2026-01-25 02:18:00
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:a13745df5d6f55ab2f6bb0cda760fa34e8c0a810d8d1864fed56685c2c2032ce`
> **Raw JSON:** `raw/20260125_021800_audit_request__verify_pixel_level_control_in_the_v.json`

---

## Query

AUDIT REQUEST: Verify pixel-level control in the visualization system.

QUESTIONS:
1. Is every visual element (node color, edge color, background, UI chrome) mapped to a controllable variable?
2. Are there ANY hardcoded colors, sizes, or visual values that bypass our state system?
3. How does the Universal Property Binder (UPB) connect data attributes to visual channels?
4. How does the OKLCH color engine integrate - is it the ONLY color source or are there bypasses?
5. What percentage of visual output is under semantic control vs hardcoded?

Search for:
- Hardcoded hex colors (#fff, #000, rgb(), rgba())
- Magic numbers for sizes
- Direct style assignments that bypass state
- CSS that doesn't use variables

OUTPUT: Compliance report with specific violations if any.

---

## Response

**COMPLIANCE REPORT: PIXEL-LEVEL CONTROL AUDIT**

**DATE:** 2026-10-XX
**TARGET:** Visualization System Codebase
**STATUS:** PARTIALLY COMPLIANT (Estimated 85% coverage)

### 1. Executive Summary
The system utilizes a sophisticated **Universal Property Binder (UPB)** and **OKLCH Color Engine** to achieve high-granularity control over the primary graph visualization. However, specific subsystems (Tower Renderer, Groups, and CSS UI components) utilize "rogue" hardcoded values that bypass the central state machine, creating inconsistency in theming and configuration.

### 2. Violations of Central Control (Hardcoded Bypasses)

#### A. The Tower Renderer (Serious Violation)
The `TowerRenderer` module ignores the `COLOR` engine and `APPEARANCE_STATE`, using a localized, hardcoded theme object.
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/modules/TowerRenderer.js:L11-L25]`
```javascript
    const THEME = {
        background: 0x000000,
        gridColor: 0x0044aa,
        nodeColors: {
            L7: 0xffffff, // System (White)
            L6: 0xcccccc, // Package
            ...
            L0: 0x004400  // Token
        },
```
*   **Impact:** Changing the global theme or color presets will NOT affect the Tower layout view.

#### B. CODOME Boundary Colors
Node coloring logic contains a hardcoded fallback dictionary for "boundary" nodes, bypassing the palette system.
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/modules/node-helpers.js:L79-L86]`
```javascript
            const CODOME_COLORS = {
                'test_entry': '#4CAF50',      // Green
                'entry_point': '#2196F3',     // Blue
                'framework_managed': '#9C27B0', // Purple
                ...
            };
```

#### C. Group Colors
The Groups module maintains its own hardcoded color array instead of requesting colors from the `COLOR` engine's palette generator.
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/modules/groups.js:L525-L528]`
```javascript
    const GROUP_COLORS = [
        '#4a9eff', '#ff6b6b', '#51cf66', '#ffd43b',
        '#cc5de8', '#20c997', '#ff922b', '#748ffc'
    ];
```

#### D. Edge System Pre-computed Hexes
While `edge-system.js` uses `COLOR.interpolate`, it relies on a local `PALETTE_HEX` constant rather than fetching dynamic base colors from the `COLOR` module.
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/modules/edge-system.js:L91-L113]`
```javascript
    const PALETTE_HEX = {
        tier: {
            T0: '#4a90d9',      // Blue (h:210, s:70, l:55)
            ...
```

#### E. CSS UI Hardcoding
Specific UI elements contain hardcoded colors in CSS that do not use CSS variables, making them immune to theme switching.
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/assets/styles.css:L1064-L1065]`
```css
        .topo-layer-item.physical {
            background: linear-gradient(90deg, rgba(20, 60, 120, 0.3) 0%, rgba(15, 45, 90, 0.15) 100%);
```
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/template.html:L1026]`
```css
        .color-btn[data-preset="tier"]::before {
            background: #ff6b6b;
        }
```

---

### 3. Universal Property Binder (UPB) Integration
**Status:** **High Compliance.** The UPB is correctly architected to intercept and resolve properties before rendering.

The `PROPERTY_QUERY` module implements a priority resolution chain.
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/modules/property-query.js:L229-L233]`
```javascript
    const providers = [
        makeExplicitOverrideProvider({ getVisState }), // Priority 100
        makeUPBProvider({ getUPB, getVisState }),      // Priority 80
        makeRawDataProvider()                          // Priority 20
    ].sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0));
```

The UPB provider dynamically resolves paths or maps based on selector state:
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/modules/property-query.js:L158-L163]`
```javascript
            if (typeof binding === 'object' && binding !== null) {
                const state = getVisState?.() ?? {};
                const selectorKey = binding.by ? getPath(state, binding.by) : undefined;
                const picked = (binding.map && selectorKey != null)
                    ? binding.map[selectorKey]
                    : undefined;
```

### 4. OKLCH Color Engine Integration
**Status:** **Mixed.** The engine is robust, but not exclusive.

The `COLOR` module provides a comprehensive OKLCH transformation pipeline:
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/modules/color-engine.js:L990-L992]`
```javascript
    let h = (oklch.h + t.hueShift + 360) % 360;
    let c = Math.max(0, Math.min(0.4, oklch.c * t.chromaScale));
    let l = Math.max(0, Math.min(1, oklch.l + t.lightnessShift / 100));
```

However, fallback logic frequently reverts to hardcoded grays if the engine isn't ready or matching:
> **Evidence:** `[standard-model-of-code/src/core/viz/assets/modules/color-engine.js:L1024]`
```javascript
        const fallback = _toHex({ h: 0, c: 0.02, l: 0.40 });
        return fallback.hex; // Fallback gray
```

### 5. Control Statistics

*   **Semantic Control:** ~85% of the primary graph (Nodes, Edges in standard views) is controlled via `property-query.js` and `vis-state.js`.
*   **Hardcoded/Uncontrolled:** ~15%, primarily consisting of:
    1.  The `TowerRenderer` 3D view (100% hardcoded).
    2.  Secondary UI elements (Group chips, Topo map legends).
    3.  Specific edge gradient interpolations.

### Recommendations
1.  **Refactor `TowerRenderer.js`** to accept a `theme` object injected from `COLOR` rather than defining `const THEME`.
2.  **Replace `GROUP_COLORS`** in `groups.js` with `COLOR.generatePalette(n)`.
3.  **Refactor `node-helpers.js`** to move `CODOME_COLORS` into `color-engine.js`'s palette definition.
4.  **CSS Variables:** Replace hex codes in `styles.css` and `template.html` with CSS variables derived from the theme (e.g., `var(--color-tier-0)`).

---

## Citations

_No citations provided_
