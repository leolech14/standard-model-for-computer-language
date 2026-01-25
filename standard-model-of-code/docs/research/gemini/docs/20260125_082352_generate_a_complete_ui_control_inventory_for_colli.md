# Research: Generate a complete UI control inventory for Collider visualization. For each control, provide:
1. S...

> **Date:** 2026-01-25 08:23:52
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:1f46564d0ba766e6718b846af745165cc06c24d382fc4eee8a3135693e4b3e3d`
> **Raw JSON:** `raw/20260125_082352_generate_a_complete_ui_control_inventory_for_colli.json`

---

## Query

Generate a complete UI control inventory for Collider visualization. For each control, provide:
1. Selector (CSS selector)
2. Type (slider, toggle, button, button-group)
3. Binding location (file:line)
4. State it mutates
5. Status (wired/orphaned/dead)

Focus on these source files:
- src/core/viz/assets/template.html (DOM elements)
- src/core/viz/assets/modules/sidebar.js (primary bindings)
- src/core/viz/assets/app.js (legacy bindings)

Output as JSON array with fields: selector, type, binding, mutates, status

---

## Response

```json
[
  {
    "selector": "#view-mode-toggle .view-mode-btn",
    "type": "button-group",
    "binding": "sidebar.js:initViewModeToggle",
    "mutates": "GRAPH_MODE, localStorage",
    "status": "wired"
  },
  {
    "selector": ".btn[data-size-mode]",
    "type": "button-group",
    "binding": "sidebar.js",
    "mutates": "VIS_STATE.sizeMode (via global delegation)",
    "status": "orphaned"
  },
  {
    "selector": "#cfg-node-size",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.nodeScale, Graph.nodeVal",
    "status": "wired"
  },
  {
    "selector": "#cfg-node-opacity",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.nodeOpacity",
    "status": "wired"
  },
  {
    "selector": "#cfg-node-res",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.nodeResolution",
    "status": "wired"
  },
  {
    "selector": "#cfg-label-size",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.labelSize, Graph.nodeLabel",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-labels",
    "type": "toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "VIS_FILTERS.metadata.showLabels, Graph.nodeLabel",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-highlight",
    "type": "toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "APPEARANCE_STATE.highlightSelected",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-pulse",
    "type": "toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "ANIM.togglePulse",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-depth",
    "type": "toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "APPEARANCE_STATE.depthShading",
    "status": "wired"
  },
  {
    "selector": ".btn[data-edge-style]",
    "type": "button-group",
    "binding": "sidebar.js",
    "mutates": "VIS_STATE.edgeStyle (via global delegation)",
    "status": "orphaned"
  },
  {
    "selector": "#cfg-edge-opacity",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.edgeOpacity",
    "status": "wired"
  },
  {
    "selector": "#cfg-edge-width",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.edgeWidth, Graph.linkWidth",
    "status": "wired"
  },
  {
    "selector": "#cfg-edge-curve",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.edgeCurvature, Graph.linkCurvature",
    "status": "wired"
  },
  {
    "selector": "#cfg-particle-speed",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.linkDirectionalParticleSpeed",
    "status": "wired"
  },
  {
    "selector": "#cfg-particle-count",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.linkDirectionalParticles",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-arrows",
    "type": "toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "APPEARANCE_STATE.showArrows, Graph.linkDirectionalArrowLength",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-gradient",
    "type": "toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "APPEARANCE_STATE.gradientEdges",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-edge-hover",
    "type": "toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "APPEARANCE_STATE.edgeHoverHighlight",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-codome",
    "type": "toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "window.SHOW_CODOME",
    "status": "wired"
  },
  {
    "selector": ".btn[data-layout]",
    "type": "button-group",
    "binding": "sidebar.js:_bindLayoutPresets",
    "mutates": "ANIM.applyLayout",
    "status": "wired"
  },
  {
    "selector": "#physics-charge",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.d3Force('charge')",
    "status": "wired"
  },
  {
    "selector": "#physics-link",
    "type": "slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.d3Force('link')",
    "status": "wired"
  },
  {
    "selector": "#physics-center",
    "type": "slider",
    "binding": "sidebar.js:_bindPhysicsControls",
    "mutates": "Graph.d3Force('center')",
    "status": "wired"
  },
  {
    "selector": "#physics-damping",
    "type": "slider",
    "binding": "sidebar.js:_bindPhysicsControls",
    "mutates": "Graph.d3VelocityDecay",
    "status": "wired"
  },
  {
    "selector": ".btn[data-physics]",
    "type": "button-group",
    "binding": "sidebar.js:_bindPhysicsControls",
    "mutates": "Physics Sliders, Graph Forces",
    "status": "wired"
  },
  {
    "selector": "#node-size",
    "type": "slider",
    "binding": "sidebar.js (implicit bind)",
    "mutates": "None (Legacy ID not in switch)",
    "status": "orphaned"
  },
  {
    "selector": "#edge-opacity",
    "type": "slider",
    "binding": "sidebar.js (implicit bind)",
    "mutates": "None (Legacy ID not in switch)",
    "status": "orphaned"
  },
  {
    "selector": "#toggle-labels",
    "type": "toggle",
    "binding": "None",
    "mutates": "None",
    "status": "dead"
  },
  {
    "selector": "#filter-tiers .chip",
    "type": "chip",
    "binding": "sidebar.js:populateFilterChips",
    "mutates": "VIS_FILTERS.tiers",
    "status": "wired"
  },
  {
    "selector": "#filter-rings .chip",
    "type": "chip",
    "binding": "sidebar.js:populateFilterChips",
    "mutates": "VIS_FILTERS.rings",
    "status": "wired"
  },
  {
    "selector": "#filter-edges .chip",
    "type": "chip",
    "binding": "sidebar.js:populateFilterChips",
    "mutates": "VIS_FILTERS.edges",
    "status": "wired"
  },
  {
    "selector": "#btn-reset",
    "type": "button",
    "binding": "sidebar.js:_bindActionButtons",
    "mutates": "Graph.cameraPosition",
    "status": "wired"
  },
  {
    "selector": "#btn-screenshot",
    "type": "button",
    "binding": "sidebar.js:_bindActionButtons",
    "mutates": "Canvas export",
    "status": "wired"
  },
  {
    "selector": "#btn-2d",
    "type": "button",
    "binding": "dimension.js:setup",
    "mutates": "window.IS_3D, Graph.numDimensions",
    "status": "wired"
  },
  {
    "selector": "#btn-freeze",
    "type": "button",
    "binding": "sidebar.js:_bindActionButtons",
    "mutates": "Graph.d3AlphaTarget",
    "status": "wired"
  },
  {
    "selector": "#selection-clear",
    "type": "button",
    "binding": "sidebar.js:updateSelectionPanel",
    "mutates": "SELECT.clear",
    "status": "wired"
  },
  {
    "selector": ".color-btn[data-preset]",
    "type": "button-group",
    "binding": "sidebar.js:initSchemeNavigator",
    "mutates": "VIS_STATE.colorBy",
    "status": "wired"
  },
  {
    "selector": ".scheme-btn",
    "type": "button-group",
    "binding": "sidebar.js:renderSchemeNavigator",
    "mutates": "VIS_STATE.palette (Color Scheme)",
    "status": "wired"
  }
]
```

---

## Citations

_No citations provided_
