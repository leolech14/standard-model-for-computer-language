# Research: 
UI GAP FILL: Token sovereignty audit.
Find:
- CSS :root variables and any theme token files
- hard-...

> **Date:** 2026-01-25 05:07:16
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:4e108ec740d145d8601f3140cfb3b6ab8097551faa4dc4a7406afe53cad343e1`
> **Raw JSON:** `raw/20260125_050716_ui_gap_fill__token_sovereignty_audit__find____css.json`

---

## Query


UI GAP FILL: Token sovereignty audit.
Find:
- CSS :root variables and any theme token files
- hard-coded rgba()/hex colors in UI chrome
- conflicts between token sources
Deliver: tokens list + conflicts + top bypasses.


---

## Response

Based on the provided codebase context—specifically `DESIGN_TOKEN_SYSTEM_AUDIT.md` and `TOKEN_SYSTEM_TASK_REGISTRY.md`—here is the **Token Sovereignty Audit**.

### 1. Token Sources (The Sovereignty)
The system uses a **Two-Layer Architecture**: JSON files define the values, Python engines generate CSS variables (`var(--token)`), and JS consumes them.

**Token Definition Files:**
*   `schema/viz/tokens/theme.tokens.json`: (Colors, themes, shadows)
*   `schema/viz/tokens/appearance.tokens.json`: (Nodes, edges, physics, animation)
*   `schema/viz/tokens/layout.tokens.json`: (Spacing, sizing, z-index)
*   `schema/viz/tokens/controls.tokens.json`: (UI controls, sliders)

**CSS Variable Generation:**
*   **Generator:** `src/core/viz/token_resolver.py`
*   **Output Target:** `styles.css` (via injection)

### 2. Conflicts (Source vs. Implementation)
Critical disagreements between the Token definitions (Controller) and `app.js` (Controlled).

| Conflict Item | Token Source Value | Hard-coded JS Value (`app.js`) | Status |
| :--- | :--- | :--- | :--- |
| **Edge Opacity** | `0.08` (`appearance.tokens`) | `0.2` (var `EDGE_DEFAULT_OPACITY`) | **Critical** (3 sources of truth) |
| **Edge Width** | `0.6` (`appearance.tokens`) | `1.2` (`EDGE_MODE_CONFIG`) | **High** (2x difference) |
| **Edge Colors** | `oklch(...)` (`appearance`) | `#4dd4ff` (Hex in `theme.tokens`) | **High** (File format mismatch) |
| **Node Size** | `Max: 8.0` (`appearance`) | `Max: 3.0` (`controls` slider) | **Medium** (UI caps capability) |
| **Animation** | `hue.speed: 0.0008` | `gravity: 0.0008` (Hardcoded const) | **High** (Tokens ignored) |

### 3. Top Bypasses (Hard-coded Violations)
These are areas in the UI Chrome (`app.js`) that completely bypass the token system using hardcoded values.

**A. Hardcoded Color Configs (app.js lines ~99-119)**
The code explicitly defines hex codes instead of reading from the loaded config object.
```javascript
// VIOLATION: app.js
let EDGE_COLOR_CONFIG = {
    default: '#333333',
    calls: '#4dd4ff',    // Bypass
    contains: '#00ff9d', // Bypass
    uses: '#ffb800',     // Bypass
    imports: '#9aa0a6',  // Bypass
    inherits: '#ff6b6b'  // Bypass
};
```

**B. Flow Visualization Presets (app.js lines ~7789)**
Entire color schemes are hardcoded in the JavaScript, duplicating or ignoring the theme tokens.
```javascript
// VIOLATION: app.js
const FLOW_PRESETS = [
    { name: 'EMBER', particleColor: '#ff8c00', ... }, // Bypass
    { name: 'OCEAN', particleColor: '#00d4ff', ... }, // Bypass
    // ...
];
```

**C. Animation Physics (app.js lines ~295)**
The `PENDULUM` object hardcodes physics values that exist in `appearance.tokens.json` but are not merged at runtime.
```javascript
// VIOLATION: app.js
const PENDULUM = {
    hue: {
        damping: 0.9995,   // Bypass (exists in tokens)
        gravity: 0.0008,   // Bypass (exists in tokens)
        rotationSpeed: 0.8 // Bypass (exists in tokens)
    }
};
```

**D. Layout Preset Speeds (app.js lines ~4275)**
Motion speeds for layouts are hardcoded rather than tokenized.
```javascript
// VIOLATION: app.js
orbitSpeed: 0.002, // Bypass
rotateSpeed: 0.003 // Bypass
```

### 4. Remediation Plan
Refer to **`TOKEN_SYSTEM_TASK_REGISTRY.md`** in the context, specifically:
1.  **T001 - T003:** Remove hardcoded `EDGE_*` configs in `app.js`.
2.  **T004:** Merge `PENDULUM` constants with incoming animation tokens in `initGraph`.
3.  **T006:** Refactor `FLOW_PRESETS` to load from `THEME_CONFIG`.

---

## Citations

_No citations provided_
