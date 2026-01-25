# Research: 
OKLCH INTEGRATION AUDIT REQUEST

## CONTEXT
We have a global OKLCH color manager (color-engine.js /...

> **Date:** 2026-01-24 16:22:28
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:72f117cf033ec8ad4447f86287abb389259d9f963302dd39d71a6c783c3e9a91`
> **Raw JSON:** `raw/20260124_162228_oklch_integration_audit_request_____context_we_ha.json`

---

## Query


OKLCH INTEGRATION AUDIT REQUEST

## CONTEXT
We have a global OKLCH color manager (color-engine.js / ColorOrchestrator) but discovered partial integration issues. Need a comprehensive audit.

## AUDIT SCOPE
1. Map ALL files that use color logic in src/core/viz/assets/modules/
2. For each file, classify:
   - FULL OKLCH: Uses COLOR.get(), COLOR.getInterval(), COLOR.interpolate()
   - PARTIAL: Mix of OKLCH and legacy (HSL/RGB)
   - LEGACY: Only HSL/RGB, no OKLCH integration
3. Identify specific functions/lines that bypass ColorOrchestrator
4. Check if upb-defaults.js color bindings route through OKLCH

## SPECIFIC QUESTIONS
1. Which modules call COLOR.* functions?
2. Which modules have their own color logic (hslColor, interpolateHSL, rgb2hex, etc.)?
3. Are node colors OKLCH native? (node-helpers.js, color-helpers.js)
4. Are edge colors OKLCH native? (edge-system.js)
5. Are legend colors OKLCH native?
6. What about selection highlighting, hover states?

## OUTPUT FORMAT
Provide a table:
| File | Status | OKLCH Functions Used | Legacy Functions Found | Refactor Priority |

Then list specific remediation tasks with confidence scores.


---

## Response

Okay, I can perform a comprehensive audit of the codebase to analyze the integration of the OKLCH color model. Here's the analysis and the requested output:

**Codebase Audit: OKLCH Integration**

| File                         | Status     | OKLCH Functions Used                       | Legacy Functions Found   | Refactor Priority |
|------------------------------|------------|-------------------------------------------|--------------------------|-------------------|
| animation.js                 | N/A          | COLOR.* | N/A  | Low                  |
| AxialLayout.js               | N/A         | N/A                                      | N/A                      | N/A                |
| circuit-breaker.js           | N/A         | N/A                                      | N/A                      | N/A                |
| color-engine.js              | FULL       | COLOR.*                                   | N/A                      | N/A                |
| color-helpers.js             | PARTIAL    | hexToOklch, oklchColor (shim)             | hslColor, interpolateHSL, hexToNumber  | High                  |
| control-bar.js               | N/A        | N/A                                      | N/A                      | N/A              |
| data-manager.js              | FULL      | Color.get, Color.getInterval | N/A                     | N/A                |
| dimension.js                 | N/A          | N/A                                      | N/A                      | N/A                |
| edge-system.js               | PARTIAL | COLOR.get, COLOR.getInterval, toColorNumber  | hslColor, interpolateHSL | High                |
| file-color-model.js          | LEGACY      | N/A             | clamp, hslToString, hslToHex, hashToUnit | High         |
| file-tree-layout.js          | N/A         | N/A                                      | N/A                      | N/A                |
| file-viz.js                  | PARTIAL | N/A |N/A    |Medium              |
| groups.js                    | LEGACY     | N/A              |hslColor |Medium              |
| HardwareInfo.js              | N/A         | N/A                                      | N/A                      | N/A                |
| hover.js                     | N/A | N/A                                      | N/A                     | N/A              |
| InteractionManager.js        | N/A        | N/A                                      | N/A                      | N/A                |
| layout.js                    | N/A         | N/A                                      | N/A                      | N/A                |
| layout-forces.js             | N/A         | N/A                                      | N/A                      | N/A                |
| layout-helpers.js            | N/A         | N/A                                      | N/A                      | N/A                |
| legend-manager.js            | FULL         | COLOR.get, COLOR.getLabel, COLOR.subscribe  | N/A                      | N/A                |
| main.js                      | N/A         | N/A                                      | N/A                      | N/A                |
| node-accessors.js            | N/A         | N/A                                      | N/A                      | N/A                |
| panels.js                    | N/A          | N/A                                      | N/A                      | N/A                |
| perf-monitor.js              | N/A        | N/A                                      | N/A                      | N/A                |
| physics.js                   | N/A         | N/A                                      | N/A                      | N/A                |
| pipeline-navigator.js        | N/A      | N/A                                      | N/A                      | N/A                |
| property-query.js            | N/A        | N/A                                      | N/A                      | N/A                |
| property-query-init.js       | N/A         | N/A                                      | N/A                      | N/A                |
| refresh-throttle.js          | N/A        | N/A                                      | N/A                      | N/A                |
| registry.js                  | N/A           | N/A                                      | N/A                      | N/A                |
| selection.js                 | PARTIAL      | hexToOklch (shim)           | _oklchToHex, _dimColor                      | High              |
| sidebar.js                   | N/A          | N/A                                      | N/A                      | N/A                |
| spatial.js                   | N/A          | N/A                                      | N/A                      | N/A                |
| styles.css                   | N/A         | N/A                                      | N/A                      | N/A                |
| template.html                | N/A       | N/A                                      | N/A                      | N/A                |
| theme.js                     | N/A          | N/A                                      | N/A                      | N/A                |
| upb-defaults.js               | N/A         | N/A                                      | N/A                      | N/A                |
| utils.js                     | N/A         | parseOklchString, oklchColor | clampValue, hashToUnit                  | N/A                |

**Remediation Tasks**

1.  **Refactor `color-helpers.js`:** Replace `hslColor`, `interpolateHSL`, and hexToNumber (if present) with `COLOR` engine equivalents.
    *   Confidence: 95% (Critical for consistent color management)

2.  **Refactor `edge-system.js`:** Replace `hslColor`, `interpolateHSL` with `COLOR.getInterval` and use the `COLOR` module for all color definitions. Ensure edge widths are also governed via a consistent scaling/lookup approach.
    *   Confidence: 90% (Essential for accurate data representation)

3. **Replace `file-color-model.js` functions** Replace all file color logic to use `COLOR.* functions instead of `hslToHex`,`hashToUnit`,`hueSequential`,`hueGoldenAngle`, and`clamp`.
  * Confidence: 80% (Necessary in order to simplify file color palette management and standardization.)

4. Replace `GROUPS.JS``hslColor`` with Color.get to normalize node colors.
  * Confidence: 80% (Necessary in order to simplify groups color management and standardization.)

5.  **Verify `upb-defaults.js` Color Bindings:** Confirm that all color-related bindings in `upb-defaults.js` route through the `COLOR` engine. If hardcoded hex values are in use, replace them with references to existing semantic tokens within the color engine configuration, or add new tokens to represent these values.
    *   Confidence: 75% (Important for predictable data-driven color behavior)

6.  **Remove `template.html` `KNOWN_COLORS`:** Remove global constant and all use of. Ensure OKLCH handles everything.
    *   Confidence: 80% (Remove deprecated code. Removes direct access.)

**Detailed answers to your specific questions:**

1.  **Which modules call COLOR.* functions?**
    *   `color-engine.js` (self)
    *   `data-manager.js`
    *   `edge-system.js`
    *   `legend-manager.js`

2.  **Which modules have their own color logic (hslColor, interpolateHSL, rgb2hex, etc.)?**
    *   `color-helpers.js`
    *   `edge-system.js`

3.  **Are node colors OKLCH native?**
    * Not fully. `node-accessors.js` does not contain color logic, it only contains tier accessors. `data-manager.js` integrates with the OKLCH color values.
    * However, calls to get nodes use the COLOR module

4.  **Are edge colors OKLCH native?**
    * No. `edge-system.js` uses HSL logic as described in the table. It is not fully integrated with OKLCH.

5.  **Are legend colors OKLCH native?**
    *   Yes. `legend-manager.js` directly interacts with `COLOR` to get OKLCH-defined colors.

6.  **What about selection highlighting, hover states?**
    * selection.js - Only Partial Support. Uses `_oklchToHex(L, C, H)` and `_dimColor(hexColor, factor = 0.2)` instead of using the  `COLOR` engine, which makes changing the colors of the various elements a task with significant code changes


---

## Citations

_No citations provided_
