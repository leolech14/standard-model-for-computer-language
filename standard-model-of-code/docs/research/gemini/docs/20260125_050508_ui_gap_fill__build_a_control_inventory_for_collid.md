# Research: 
UI GAP FILL: Build a control inventory for Collider UI.
Output JSON schema:
- selector/id
- visible...

> **Date:** 2026-01-25 05:05:08
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:42370cdb19803f445e66f7de232e4ff6d2b418b4e489e91a647a61ac5022820c`
> **Raw JSON:** `raw/20260125_050508_ui_gap_fill__build_a_control_inventory_for_collid.json`

---

## Query


UI GAP FILL: Build a control inventory for Collider UI.
Output JSON schema:
- selector/id
- visible label text
- component type
- handler binding location (file+line)
- state mutated (VIS_STATE / APPEARANCE_STATE / Graph / COLOR)
- status: wired | orphaned | dead handler
Also list all cfg-* IDs and data-* attributes.


---

## Response

Based on the provided codebase context, here is the Control Inventory for the Collider UI.

### **Overview**
The UI contains a mix of **active `cfg-*` controls** (bound in `sidebar.js`) and **legacy/orphaned controls** (found in the "Appearance" section of `template.html` or referenced in `panels.js` but missing from HTML).

### **Control Inventory**

```json
[
  {
    "selector": "#view-mode-toggle .view-mode-btn[data-mode='atoms']",
    "label": "ATOMS",
    "type": "Button (Segmented)",
    "binding": "sidebar.js:initViewModeToggle",
    "mutates": "GRAPH_MODE",
    "status": "wired"
  },
  {
    "selector": "#view-mode-toggle .view-mode-btn[data-mode='files']",
    "label": "FILES",
    "type": "Button (Segmented)",
    "binding": "sidebar.js:initViewModeToggle",
    "mutates": "GRAPH_MODE",
    "status": "wired"
  },
  {
    "selector": ".btn[data-size-mode]",
    "label": "Uniform, Degree, Fanout, Complex",
    "type": "Button Group",
    "binding": "sidebar.js",
    "mutates": "Graph.nodeVal",
    "status": "orphaned",
    "notes": "HTML exists, but sidebar.js has no explicit binding for data-size-mode selectors, only sliders."
  },
  {
    "selector": "#cfg-node-size",
    "label": "Base Size",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.nodeScale, Graph.nodeVal",
    "status": "wired"
  },
  {
    "selector": "#cfg-node-opacity",
    "label": "Opacity",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.nodeOpacity",
    "status": "wired"
  },
  {
    "selector": "#cfg-node-res",
    "label": "Resolution",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.nodeResolution",
    "status": "wired"
  },
  {
    "selector": "#cfg-label-size",
    "label": "Label Size",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "None",
    "status": "dead handler",
    "notes": "Switch case exists in JS, but logic body is empty."
  },
  {
    "selector": "#cfg-toggle-labels",
    "label": "Show Labels",
    "type": "Toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "VIS_FILTERS.metadata.showLabels, Graph.nodeLabel",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-highlight",
    "label": "Highlight Selected",
    "type": "Toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "None",
    "status": "dead handler",
    "notes": "Binding exists but function body is empty comment."
  },
  {
    "selector": "#cfg-toggle-pulse",
    "label": "Pulse Animation",
    "type": "Toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "ANIM.togglePulse",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-depth",
    "label": "3D Depth Shading",
    "type": "Toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "None",
    "status": "dead handler",
    "notes": "Binding exists but function body is empty comment."
  },
  {
    "selector": ".btn[data-edge-style]",
    "label": "Solid, Dashed, Particle",
    "type": "Button Group",
    "binding": "sidebar.js",
    "mutates": "None",
    "status": "orphaned",
    "notes": "HTML exists but no JS listener targets data-edge-style."
  },
  {
    "selector": "#cfg-edge-opacity",
    "label": "Opacity (Edge)",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.edgeOpacity",
    "status": "wired"
  },
  {
    "selector": "#cfg-edge-width",
    "label": "Width",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.edgeWidth, Graph.linkWidth",
    "status": "wired"
  },
  {
    "selector": "#cfg-edge-curve",
    "label": "Curvature",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "APPEARANCE_STATE.edgeCurvature, Graph.linkCurvature",
    "status": "wired"
  },
  {
    "selector": "#cfg-particle-speed",
    "label": "Particle Speed",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.linkDirectionalParticleSpeed",
    "status": "wired"
  },
  {
    "selector": "#cfg-particle-count",
    "label": "Particle Density",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.linkDirectionalParticles",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-arrows",
    "label": "Show Arrows",
    "type": "Toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "APPEARANCE_STATE.showArrows, Graph.linkDirectionalArrowLength",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-gradient",
    "label": "Gradient Colors",
    "type": "Toggle",
    "binding": "sidebar.js:_bindAppearanceControls",
    "mutates": "APPEARANCE_STATE.gradientEdges",
    "status": "wired"
  },
  {
    "selector": "#cfg-toggle-edge-hover",
    "label": "Highlight on Hover",
    "type": "Toggle",
    "binding": "sidebar.js",
    "mutates": "None",
    "status": "orphaned",
    "notes": "HTML exists but no JS binding in sidebar.js."
  },
  {
    "selector": "#cfg-toggle-codome",
    "label": "Show Codome Boundaries",
    "type": "Toggle",
    "binding": "sidebar.js",
    "mutates": "None",
    "status": "orphaned",
    "notes": "HTML exists but no JS binding in sidebar.js."
  },
  {
    "selector": ".btn[data-layout]",
    "label": "Force, Radial, Orbital, Sphere...",
    "type": "Button Grid",
    "binding": "sidebar.js:_bindLayoutPresets",
    "mutates": "ANIM.applyLayout",
    "status": "wired"
  },
  {
    "selector": "#physics-charge",
    "label": "Repulsion",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.d3Force('charge')",
    "status": "wired"
  },
  {
    "selector": "#physics-link",
    "label": "Link Distance",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "Graph.d3Force('link')",
    "status": "wired"
  },
  {
    "selector": "#physics-center",
    "label": "Center Pull",
    "type": "Slider",
    "binding": "sidebar.js:_bindPhysicsControls",
    "mutates": "Graph.d3Force('center')",
    "status": "wired"
  },
  {
    "selector": ".btn[data-physics]",
    "label": "Def, Tight, Loose, Boom",
    "type": "Button Grid",
    "binding": "sidebar.js:_bindPhysicsControls",
    "mutates": "Graph.d3Force (multiple)",
    "status": "wired"
  },
  {
    "selector": "#node-size",
    "label": "Node Size (Legacy)",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "None",
    "status": "orphaned",
    "notes": "Legacy slider in 'Appearance' section. _handleSliderChange only checks cfg-node-size."
  },
  {
    "selector": "#edge-opacity",
    "label": "Edge Opacity (Legacy)",
    "type": "Slider",
    "binding": "sidebar.js:_handleSliderChange",
    "mutates": "None",
    "status": "orphaned",
    "notes": "Legacy slider in 'Appearance' section. _handleSliderChange only checks cfg-edge-opacity."
  },
  {
    "selector": "#toggle-labels",
    "label": "Show Labels (Legacy)",
    "type": "Toggle",
    "binding": "sidebar.js",
    "mutates": "None",
    "status": "orphaned",
    "notes": "Legacy toggle in 'Appearance' section. Only cfg-toggle-labels is bound."
  },
  {
    "selector": "#btn-reset",
    "label": "Reset View",
    "type": "Button",
    "binding": "sidebar.js:_bindActionButtons",
    "mutates": "Graph.cameraPosition",
    "status": "wired"
  },
  {
    "selector": "#btn-screenshot",
    "label": "Screenshot",
    "type": "Button",
    "binding": "sidebar.js:_bindActionButtons",
    "mutates": "Canvas export",
    "status": "wired"
  },
  {
    "selector": "#btn-2d",
    "label": "Toggle 2D",
    "type": "Button",
    "binding": "dimension.js:setup",
    "mutates": "IS_3D, Graph.numDimensions",
    "status": "wired"
  },
  {
    "selector": "#btn-freeze",
    "label": "Freeze",
    "type": "Button",
    "binding": "sidebar.js:_bindActionButtons",
    "mutates": "Graph.d3AlphaTarget",
    "status": "wired"
  },
  {
    "selector": ".color-btn[data-preset]",
    "label": "Tier, Family, Layer, Ring...",
    "type": "Button Grid",
    "binding": "sidebar.js:initSchemeNavigator",
    "mutates": "VIS_STATE.colorBy",
    "status": "wired"
  }
]
```

### **Identifier Lists**

#### **Configuration IDs (`cfg-*`)**
Active controls found in `template.html` and bound in `sidebar.js`:
*   `cfg-node-size`
*   `cfg-node-opacity`
*   `cfg-node-res`
*   `cfg-label-size`
*   `cfg-toggle-labels`
*   `cfg-toggle-highlight`
*   `cfg-toggle-pulse`
*   `cfg-toggle-depth`
*   `cfg-edge-opacity`
*   `cfg-edge-width`
*   `cfg-edge-curve`
*   `cfg-particle-speed`
*   `cfg-particle-count`
*   `cfg-toggle-arrows`
*   `cfg-toggle-gradient`
*   `cfg-toggle-edge-hover`
*   `cfg-toggle-codome`

#### **Data Attributes**
Attributes used for logic logic binding in `sidebar.js`:
*   `data-mode` (View mode toggle)
*   `data-section` (Accordion collapse)
*   `data-size-mode` (Node sizing logic - *Currently Orphaned*)
*   `data-edge-style` (Edge styling logic - *Currently Orphaned*)
*   `data-layout` (Layout preset selection)
*   `data-physics` (Physics preset selection)
*   `data-preset` (Color mode selection)
*   `data-target` (Panel collapse target)

---

## Citations

_No citations provided_
