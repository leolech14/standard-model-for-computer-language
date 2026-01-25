# Research: UI GAP FILL REQUEST (Collider UI)

Goal:
Produce an evidence-backed UI knowledge base that will allo...

> **Date:** 2026-01-25 01:32:12
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:49e373a5abd7522510830d4420204230954ac0c72a6f8c712f9262da0cead17d`
> **Raw JSON:** `raw/20260125_013212_ui_gap_fill_request__collider_ui___goal__produce_a.json`

---

## Query

UI GAP FILL REQUEST (Collider UI)

Goal:
Produce an evidence-backed UI knowledge base that will allow automatic task generation with high confidence.

Scope:
- All modules in src/core/viz/assets/modules/
- Focus on: ui-manager.js, layout.js, registry.js, ui-builders.js, sidebar.js, circuit-breaker.js
- CSS tokens in template.html (:root variables)
- Any module that binds event listeners to cfg-* ids or data-* attributes

Deliverables (MUST return as structured JSON blocks):

1) ui_control_inventory - For each interactive control:
   - element_id or selector
   - label_text
   - component_type (toggle/slider/button/select/chip/segmented)
   - region (left-sidebar/canvas/right-sidebar/header/dock)
   - handler_location (file:line)
   - state_path (e.g. APPEARANCE_STATE.nodeScale)
   - registry_command (if registered in REGISTRY)
   - status: wired | orphaned | dead_handler | missing_element

2) ui_tokens - Extract all :root CSS variables:
   - variable_name
   - value (hex/rgba/oklch)
   - semantic_category (bg/panel/border/text/accent/status)

3) ui_layout_model:
   - required_containers (DOM elements that must exist)
   - fixed_panels vs dynamic_panels
   - constraints (min widths, margins, docking rules)

4) findings:
   - top gaps blocking full-confidence task generation
   - controls with empty handlers
   - controls with no binding
   - duplicate/conflicting bindings

Return ONLY valid JSON for each deliverable, clearly labeled.

---

## Response

```json
{
  "ui_control_inventory": [
    {
      "element_id": "view-mode-toggle",
      "selector": ".view-mode-btn[data-mode='atoms']",
      "label_text": "ATOMS",
      "component_type": "segmented_button",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L486",
      "state_path": "GRAPH_MODE",
      "status": "wired"
    },
    {
      "element_id": "view-mode-toggle",
      "selector": ".view-mode-btn[data-mode='files']",
      "label_text": "FILES",
      "component_type": "segmented_button",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:486",
      "state_path": "GRAPH_MODE",
      "status": "wired"
    },
    {
      "element_id": "cfg-node-size",
      "label_text": "Base Size",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L821",
      "state_path": "APPEARANCE_STATE.nodeScale",
      "status": "wired"
    },
    {
      "element_id": "cfg-node-opacity",
      "label_text": "Opacity",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L825",
      "state_path": "APPEARANCE_STATE.nodeOpacity",
      "status": "wired"
    },
    {
      "element_id": "cfg-node-res",
      "label_text": "Resolution",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L829",
      "state_path": "Graph.nodeResolution",
      "status": "wired"
    },
    {
      "element_id": "cfg-label-size",
      "label_text": "Label Size",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L831",
      "state_path": "undefined",
      "status": "dead_handler"
    },
    {
      "element_id": "cfg-toggle-labels",
      "label_text": "Show Labels",
      "component_type": "toggle",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L777",
      "state_path": "VIS_FILTERS.metadata.showLabels",
      "status": "wired"
    },
    {
      "element_id": "cfg-toggle-highlight",
      "label_text": "Highlight Selected",
      "component_type": "toggle",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L786",
      "state_path": "undefined",
      "status": "empty_handler"
    },
    {
      "element_id": "cfg-toggle-pulse",
      "label_text": "Pulse Animation",
      "component_type": "toggle",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L790",
      "state_path": "ANIM.togglePulse",
      "status": "wired"
    },
    {
      "element_id": "cfg-toggle-depth",
      "label_text": "3D Depth Shading",
      "component_type": "toggle",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L796",
      "state_path": "undefined",
      "status": "empty_handler"
    },
    {
      "element_id": "cfg-edge-opacity",
      "label_text": "Opacity",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L838",
      "state_path": "APPEARANCE_STATE.edgeOpacity",
      "status": "wired"
    },
    {
      "element_id": "cfg-edge-width",
      "label_text": "Width",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L842",
      "state_path": "APPEARANCE_STATE.edgeWidth",
      "status": "wired"
    },
    {
      "element_id": "cfg-edge-curve",
      "label_text": "Curvature",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L846",
      "state_path": "APPEARANCE_STATE.edgeCurvature",
      "status": "wired"
    },
    {
      "element_id": "cfg-particle-speed",
      "label_text": "Particle Speed",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L850",
      "state_path": "Graph.linkDirectionalParticleSpeed",
      "status": "wired"
    },
    {
      "element_id": "cfg-particle-count",
      "label_text": "Particle Density",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L853",
      "state_path": "Graph.linkDirectionalParticles",
      "status": "wired"
    },
    {
      "element_id": "cfg-toggle-arrows",
      "label_text": "Show Arrows",
      "component_type": "toggle",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L800",
      "state_path": "APPEARANCE_STATE.showArrows",
      "status": "wired"
    },
    {
      "element_id": "cfg-toggle-gradient",
      "label_text": "Gradient Colors",
      "component_type": "toggle",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L808",
      "state_path": "APPEARANCE_STATE.gradientEdges",
      "status": "wired"
    },
    {
      "element_id": "cfg-toggle-edge-hover",
      "label_text": "Highlight on Hover",
      "component_type": "toggle",
      "region": "left-sidebar",
      "handler_location": "missing",
      "state_path": "undefined",
      "status": "orphaned"
    },
    {
      "element_id": "cfg-toggle-codome",
      "label_text": "Show Codome Boundaries",
      "component_type": "toggle",
      "region": "left-sidebar",
      "handler_location": "missing",
      "state_path": "undefined",
      "status": "orphaned"
    },
    {
      "element_id": "physics-charge",
      "label_text": "Repulsion",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L858",
      "state_path": "Graph.d3Force('charge').strength",
      "status": "wired"
    },
    {
      "element_id": "physics-link",
      "label_text": "Link Distance",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L864",
      "state_path": "Graph.d3Force('link').distance",
      "status": "wired"
    },
    {
      "element_id": "physics-center",
      "label_text": "Center Pull",
      "component_type": "slider",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L707",
      "state_path": "Graph.d3Force('center').strength",
      "status": "wired"
    },
    {
      "element_id": "btn-reset",
      "label_text": "Reset View",
      "component_type": "button",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L881",
      "state_path": "Graph.cameraPosition",
      "status": "wired"
    },
    {
      "element_id": "btn-screenshot",
      "label_text": "Screenshot",
      "component_type": "button",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L891",
      "state_path": "undefined",
      "status": "wired"
    },
    {
      "element_id": "btn-2d",
      "label_text": "Toggle 2D",
      "component_type": "button",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/dimension.js:L56",
      "state_path": "IS_3D",
      "status": "wired"
    },
    {
      "element_id": "btn-freeze",
      "label_text": "Freeze",
      "component_type": "button",
      "region": "left-sidebar",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L907",
      "state_path": "Graph.d3AlphaTarget",
      "status": "wired"
    },
    {
      "element_id": "cmd-files2",
      "label_text": "Toggle File Boundaries",
      "component_type": "command_button",
      "region": "dock",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L235",
      "state_path": "fileMode",
      "registry_command": "cmd-files2",
      "status": "wired"
    },
    {
      "element_id": "cmd-flow2",
      "label_text": "Toggle Flow Mode",
      "component_type": "command_button",
      "region": "dock",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L245",
      "state_path": "flowMode",
      "registry_command": "cmd-flow2",
      "status": "wired"
    },
    {
      "element_id": "cmd-3d",
      "label_text": "Toggle 2D/3D View",
      "component_type": "command_button",
      "region": "dock",
      "handler_location": "src/core/viz/assets/modules/sidebar.js:L254",
      "state_path": "IS_3D",
      "registry_command": "cmd-3d",
      "status": "wired"
    }
  ],
  "ui_tokens": [
    {
      "variable_name": "--bg",
      "value": "#0a0a0f",
      "semantic_category": "bg"
    },
    {
      "variable_name": "--surface",
      "value": "rgba(15, 15, 22, 0.85)",
      "semantic_category": "surface"
    },
    {
      "variable_name": "--surface-hover",
      "value": "rgba(25, 25, 35, 0.9)",
      "semantic_category": "surface"
    },
    {
      "variable_name": "--border",
      "value": "rgba(255, 255, 255, 0.08)",
      "semantic_category": "border"
    },
    {
      "variable_name": "--border-accent",
      "value": "rgba(74, 158, 255, 0.3)",
      "semantic_category": "border"
    },
    {
      "variable_name": "--text",
      "value": "rgba(255, 255, 255, 0.9)",
      "semantic_category": "text"
    },
    {
      "variable_name": "--text-dim",
      "value": "rgba(255, 255, 255, 0.5)",
      "semantic_category": "text"
    },
    {
      "variable_name": "--text-muted",
      "value": "rgba(255, 255, 255, 0.3)",
      "semantic_category": "text"
    },
    {
      "variable_name": "--accent",
      "value": "#4a9eff",
      "semantic_category": "accent"
    },
    {
      "variable_name": "--accent-dim",
      "value": "rgba(74, 158, 255, 0.15)",
      "semantic_category": "accent"
    },
    {
      "variable_name": "--accent-glow",
      "value": "rgba(74, 158, 255, 0.25)",
      "semantic_category": "accent"
    },
    {
      "variable_name": "--green",
      "value": "#5a9a70",
      "semantic_category": "status"
    },
    {
      "variable_name": "--yellow",
      "value": "#a09060",
      "semantic_category": "status"
    },
    {
      "variable_name": "--red",
      "value": "#b07070",
      "semantic_category": "status"
    },
    {
      "variable_name": "--cyan",
      "value": "#7090a0",
      "semantic_category": "status"
    },
    {
      "variable_name": "--glass",
      "value": "blur(12px)",
      "semantic_category": "effect"
    }
  ],
  "ui_layout_model": {
    "required_containers": [
      "#header",
      "#left-sidebar",
      "#right-sidebar",
      "#3d-graph",
      "#loader",
      "#perf-hud",
      "#toast",
      "#control-bar-container"
    ],
    "fixed_panels": [
      "top-left-header",
      "stats-panel",
      "metrics-panel",
      "bottom-dock",
      "report-panel",
      "side-dock"
    ],
    "dynamic_panels": [
      "hover-panel",
      "file-panel",
      "selection-panel"
    ],
    "constraints": {
      "sidebar_width": {
        "variable": "--sidebar-width",
        "default": "300px",
        "min": "240px",
        "max": "500px"
      },
      "right_panel_width": {
        "variable": "--right-panel-width",
        "default": "280px"
      },
      "header_height": {
        "variable": "--header-height",
        "default": "48px"
      },
      "min_graph_width": 320,
      "reflow_throttle_ms": 50,
      "panel_margin": 16
    }
  },
  "findings": {
    "top_gaps": [
      "Control 'cfg-label-size' (Label Size) has no logic in sidebar.js slider dispatch (L831).",
      "Control 'cfg-toggle-highlight' (Highlight Selected) toggle binding is empty (sidebar.js:L786).",
      "Control 'cfg-toggle-depth' (3D Depth Shading) toggle binding is empty (sidebar.js:L796).",
      "Control 'cfg-toggle-edge-hover' is in HTML but has no binding in sidebar.js.",
      "Control 'cfg-toggle-codome' is in HTML but has no binding in sidebar.js.",
      "Dual definition of 'btn-2d' binding: both in sidebar.js (commented out/reference) and dimension.js (authoritative).",
      "Old 'btn-edge-mode' referenced in comments but likely removed from HTML template."
    ],
    "empty_handlers": [
      "cfg-toggle-highlight",
      "cfg-toggle-depth"
    ],
    "missing_bindings": [
      "cfg-toggle-edge-hover",
      "cfg-toggle-codome",
      "cfg-label-size"
    ],
    "duplicates": [
      "btn-2d"
    ]
  }
}
```

---

## Citations

_No citations provided_
