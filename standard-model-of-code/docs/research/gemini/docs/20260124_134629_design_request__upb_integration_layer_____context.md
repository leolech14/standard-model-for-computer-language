# Research: DESIGN REQUEST: UPB Integration Layer

## CONTEXT

We have a visualization system with TWO parallel ...

> **Date:** 2026-01-24 13:46:29
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:49fc99ddef8722759929470057be7d4dd6640ed371e591031656c75d78d8bb2b`
> **Raw JSON:** `raw/20260124_134629_design_request__upb_integration_layer_____context.json`

---

## Query

DESIGN REQUEST: UPB Integration Layer

## CONTEXT

We have a visualization system with TWO parallel control paths:

### PATH A: Legacy (WORKING)
```
VIS_STATE.applyPreset('tier')
  → window.NODE_COLOR_MODE = 'tier'
  → node-helpers.js:getNodeColorByMode(node)
  → switch(NODE_COLOR_MODE) → Color.get('tier', node.tier)
  → node.color = '#hex'
  → Graph.nodeColor() renders
```

### PATH B: UPB Algebra (EXISTS BUT ORPHANED)
```
UPB.bind('complexity', 'hue', {scale: 'log'})
  → BINDINGS.defaultGraph stores binding
  → UPB.evaluate(node) returns {hue: 240, size: 12, ...}
  → ??? NOT CONNECTED TO RENDER ???
```

## THE GAP

File: `src/core/viz/assets/modules/node-helpers.js`
Function: `getNodeColorByMode(node)`

This function ONLY reads `window.NODE_COLOR_MODE` global.
It does NOT check if UPB has active bindings.

## REQUIREMENTS

1. **Backward Compatible**: Legacy presets (tier, family, layer) must keep working
2. **UPB Priority**: If UPB has bindings for a target, UPB wins
3. **Minimal Changes**: Modify node-helpers.js, not rewrite everything
4. **Clean Interface**: Single point of integration

## QUESTIONS

1. Where exactly should the UPB check be inserted?
2. What's the interface contract between UPB.evaluate() and node-helpers.js?
3. Should VIS_STATE presets eventually call UPB.bind() internally?
4. How do we handle partial bindings (UPB has hue but not size)?

## FILES INVOLVED

- `modules/node-helpers.js` - Main color computation (MODIFY)
- `modules/upb/index.js` - UPB public API (READ)
- `modules/vis-state.js` - Preset system (MAYBE MODIFY)
- `app.js` - Graph.nodeColor() callback (VERIFY)

Design the minimal integration that connects UPB to the render path.

---

## Response

Okay, let's design the integration of the Universal Property Binder (UPB) into the node color rendering pipeline, prioritizing backward compatibility and a clean interface.  Here's a breakdown of the design, addressing the key questions and requirements.

**1. Integration Point: `modules/node-helpers.js` - `getNodeColorByMode(node)`**

This is the correct place to insert the UPB check. We want UPB to take priority if it has a binding that defines a node's color. The check should occur *before* the existing `switch` statement or the direct lookup in MODE_ACCESSORS.

```javascript
function getNodeColorByMode(node) {
    const Color = window.Color;
    const NODE_COLOR_MODE = window.NODE_COLOR_MODE;

    // **[INSERT UPB CHECK HERE]**  <-----

    // Special case: CODOME boundary nodes (external callers)
    // Always use their explicit color_hint, regardless of color mode
    if (node.is_codome_boundary || node.kind === 'boundary') {
        if (node.color_hint) {
            return node.color_hint;
        }
    }

    // Use MODE_ACCESSORS map - O(1) lookup instead of if-chain
    const accessor = MODE_ACCESSORS[NODE_COLOR_MODE];
    if (accessor) return accessor(node, Color);

    // Default fallback
    return Color.get('tier', window.getNodeTier(node));
}
```

**2. Interface Contract: `UPB.evaluate(node)`**

The most direct interface is to have `getNodeColorByMode(node)` call `UPB.evaluate(node)` and use any color-related properties it returns.  We need to handle two cases:

*   **Full UPB Control:** UPB provides *the* color.
*   **Partial UPB Control:** UPB provides only the `hue`, and the rest of the color can come from defaults.

Revised `getNodeColorByMode` with direct UPB integration:

```javascript
function getNodeColorByMode(node) {
    const Color = window.Color;
    const NODE_COLOR_MODE = window.NODE_COLOR_MODE;
    const UPB = window.UPB;

    // *** INTEGRATION POINT: Check for UPB bindings ***
    if (UPB && typeof UPB.evaluate === 'function') {
        const upbValues = UPB.evaluate(node);

        if (upbValues && upbValues.color) {
            // Full UPB Color Control: use the provided color
            return upbValues.color; // UPB already hands off the final color
        } else if (upbValues && upbValues.hue) {
             // Partial UPB Color Control: Hue override
            let baseColor = Color.get('tier', window.getNodeTier(node));  // Default or other source
            let oklchColor;

            if(typeof baseColor == 'string'){
                oklchColor = Color.hexToOklch(baseColor);
            }
            else{
                oklchColor = baseColor;
            }

            oklchColor.h = upbValues.hue;

            return Color.toHex(oklchColor);

        }
    }

    // Special case: CODOME boundary nodes (external callers)
    // Always use their explicit color_hint, regardless of color mode
    if (node.is_codome_boundary || node.kind === 'boundary') {
        if (node.color_hint) {
            return node.color_hint;
        }
    }

    // Use MODE_ACCESSORS map - O(1) lookup instead of if-chain
    const accessor = MODE_ACCESSORS[NODE_COLOR_MODE];
    if (accessor) return accessor(node, Color);

    // Default fallback
    return Color.get('tier', window.getNodeTier(node));
}
```

**3. VIS_STATE and UPB: Eventual Alignment**

Yes, *eventually*, `VIS_STATE.applyPreset()` *should* call `UPB.bind()` internally. This will centralize all binding logic within UPB, making the system more maintainable.  This refactoring can be done in a separate phase after confirming the core integration works.

Here's a conceptual sketch of how that might look:

```javascript
// In modules/vis-state.js
function applyPreset(presetName) {
  // Existing preset logic...

  // New: delegate to UPB
  UPB.bindFromPreset(presetName);
}
```

and UPB could contain the definitions for every single preset. This is a larger architectural shift and can wait.

**4. Handling Partial Bindings**

The updated `getNodeColorByMode` already handles partial bindings. If UPB only provides `hue`, the code falls back to using existing color logic to determine the base color and then overrides the hue component.

**Additional Considerations:**

*   **Performance**: Measure the impact of the `UPB.evaluate()` call on performance. If necessary, consider caching the results of `UPB.evaluate()` on the node itself, invalidating the cache when bindings change.
*   **Error Handling:** Add robust error handling around the `UPB.evaluate()` call to prevent crashes if there are issues with the UPB configuration.  Log errors to the console for debugging.
*   **Edge Cases**: Consider all scenarios, particularly with boundary nodes, to ensure all paths are accounted for.
*   **Testing**: Implement unit and integration tests. Specifically add cases for
 *    - Having UPB manage colors, but no UPB properties exist (graceful failure)
 *    - All presets continue to work
 *    - Combinations of different rendering configurations

**Revised Code Snippets**

**`modules/node-helpers.js` (Revised):**

```javascript
function getNodeColorByMode(node) {
    const Color = window.Color;
    const NODE_COLOR_MODE = window.NODE_COLOR_MODE;
    const UPB = window.UPB;

    // *** INTEGRATION POINT: Check for UPB bindings ***
    if (UPB && typeof UPB.evaluate === 'function') {
        const upbValues = UPB.evaluate(node);

        if (upbValues && upbValues.color) {
            // Full UPB Color Control: use the provided color
            return upbValues.color; // UPB already hands off the final color
        } else if (upbValues && upbValues.hue) {
             // Partial UPB Color Control: Hue override
            let baseColor = Color.get('tier', window.getNodeTier(node));  // Default or other source
            let oklchColor;

            if(typeof baseColor == 'string'){
                oklchColor = Color.hexToOklch(baseColor);
            }
            else{
                oklchColor = baseColor;
            }

            oklchColor.h = upbValues.hue;

            return Color.toHex(oklchColor);

        }
    }

    // Special case: CODOME boundary nodes (external callers)
    // Always use their explicit color_hint, regardless of color mode
    if (node.is_codome_boundary || node.kind === 'boundary') {
        if (node.color_hint) {
            return node.color_hint;
        }
    }

    // Use MODE_ACCESSORS map - O(1) lookup instead of if-chain
    const accessor = MODE_ACCESSORS[NODE_COLOR_MODE];
    if (accessor) return accessor(node, Color);

    // Default fallback
    return Color.get('tier', window.getNodeTier(node));
}
```

This design provides a clear integration point, maintains backward compatibility, and lays the groundwork for future consolidation of the binding logic into UPB. Remember to test thoroughly!

---

## Citations

_No citations provided_
