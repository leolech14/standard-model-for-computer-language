# UI Controls Schema for Collider Visualization

**Version:** 2.0
**Date:** 2026-01-25
**Sources:** Perplexity research (Gephi, Neo4j Bloom, Cytoscape, yFiles) + Gemini architect analysis

## Executive Summary

This schema defines **78 controls** across **9 categories** for the Collider 3D code visualization tool. Controls are prioritized as:
- **P0 (Essential):** 18 controls - Core functionality required for basic use
- **P1 (Important):** 32 controls - Expected by users of professional tools
- **P2 (Nice-to-have):** 28 controls - Advanced features for power users

## Design Principles

1. **Holarchic Navigation** - Support 16-level scale traversal (Bit → Universe)
2. **RPBL Dimensions** - Expose Responsibility, Purity, Boundary, Lifecycle
3. **Progressive Disclosure** - Basic controls visible, advanced in collapsible panels
4. **Keyboard-First** - Every control has a keyboard shortcut
5. **Accessibility** - WCAG AA compliance, colorblind modes, screen reader support

---

## Category 1: VIEW MODES (Holarchic Navigation)

Controls for navigating the 16-level scale hierarchy.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `view-granularity` | Granularity Level | toggle_group | `atoms` (L3), `files` (L5), `classes` (L4), `packages` (L6) | `atoms` | `GRAPH_MODE` | SIDEBAR | P0 |
| `btn-2d` | Dimension | button_toggle | `2D`, `3D` | `3D` | `IS_3D` | DIMENSION | P0 |
| `view-scope` | Scope Focus | dropdown | `full`, `selection`, `codome`, `neighborhood` | `full` | `VIEW_SCOPE` | SIDEBAR | P1 |
| `view-depth` | Depth Filter | slider | 1-10 hops | 10 | `VIS_FILTERS.maxDepth` | DATA | P2 |

**Keyboard Shortcuts:**
- `1` = Atoms view, `2` = Files view, `3` = Classes view
- `D` = Toggle 2D/3D
- `F` = Fit to view

---

## Category 2: LAYOUT & PHYSICS

Controls for graph layout algorithms and physics simulation.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `layout-preset` | Layout Algorithm | select_grid | `force`, `tree`, `radial`, `orbital`, `codome`, `hierarchical`, `grid` | `force` | `ANIM.currentLayout` | ANIM | P0 |
| `physics-charge` | Repulsion | slider | -500 to 0 | -120 | `PHYSICS_STATE.charge` | PHYSICS | P0 |
| `physics-link` | Link Distance | slider | 10-200 | 50 | `PHYSICS_STATE.linkDistance` | PHYSICS | P1 |
| `physics-gravity` | Center Gravity | slider | 0-0.5 | 0.05 | `PHYSICS_STATE.centerStrength` | PHYSICS | P2 |
| `physics-collision` | Collision Radius | slider | 0-50 | 10 | `PHYSICS_STATE.collisionRadius` | PHYSICS | P2 |
| `physics-iterations` | Iterations | slider | 50-500 | 100 | `PHYSICS_STATE.iterations` | PHYSICS | P2 |
| `btn-freeze` | Freeze Simulation | button_toggle | on/off | off | `LAYOUT_FROZEN` | LAYOUT_HELPERS | P1 |
| `physics-preset` | Physics Preset | button_group | `default`, `tight`, `loose`, `clustered` | `default` | `PHYSICS_PRESET` | PHYSICS | P1 |

**Layout Algorithms:**
| Algorithm | Best For | Standard Model Concept |
|-----------|----------|------------------------|
| `force` | General exploration | Atoms (L3) |
| `tree` | Hierarchical call graphs | Layers |
| `radial` | Clean Architecture rings | Domain → Infrastructure |
| `codome` | Boundary visualization | Codome boundaries |
| `hierarchical` | Package structure | L5-L7 scale |

**Keyboard Shortcuts:**
- `Space` = Freeze/unfreeze
- `L` = Cycle layouts
- `R` = Reset layout

---

## Category 3: NODE APPEARANCE

Controls for node visual properties.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `node-color-mode` | Color By | dropdown | See options below | `tier` | `VIS_STATE.colorBy` | SIDEBAR | P0 |
| `node-color-scheme` | Color Scheme | button_group | `viridis`, `plasma`, `oklab`, `categorical` | `oklab` | `COLOR_SCHEME` | COLOR | P0 |
| `cfg-node-size` | Base Size | slider | 0.2-4.0 | 1.0 | `APPEARANCE_STATE.nodeScale` | SIDEBAR | P0 |
| `node-size-mode` | Size By | select_buttons | `uniform`, `complexity`, `fan_in`, `fan_out`, `loc`, `centrality` | `uniform` | `VIS_STATE.sizeBy` | NODE_HELPERS | P1 |
| `cfg-node-opacity` | Opacity | slider | 0-1 | 0.9 | `APPEARANCE_STATE.nodeOpacity` | SIDEBAR | P1 |
| `cfg-node-res` | Resolution | slider | 4-32 | 16 | `APPEARANCE_STATE.nodeResolution` | SIDEBAR | P2 |
| `cfg-toggle-labels` | Show Labels | toggle | on/off | on | `VIS_FILTERS.metadata.showLabels` | SIDEBAR | P0 |
| `cfg-label-size` | Label Size | slider | 0.5-3.0 | 1.0 | `APPEARANCE_STATE.labelScale` | SIDEBAR | P1 |
| `node-shape-mode` | Shape By | dropdown | `sphere`, `cube`, `role-icon`, `tier-shape` | `sphere` | `VIS_STATE.shapeBy` | NODE_HELPERS | P2 |
| `cfg-toggle-highlight` | Selection Glow | toggle | on/off | on | `APPEARANCE_STATE.highlightGlow` | SIDEBAR | P1 |
| `cfg-toggle-pulse` | Animate Entry Points | toggle | on/off | off | `ANIM.pulseEntryPoints` | ANIM | P2 |

**Color By Options (Standard Model Dimensions):**
| Value | Label | Description |
|-------|-------|-------------|
| `tier` | Architectural Tier | T0/T1/T2 |
| `family` | Atom Family | LOG/DAT/ORG/NET |
| `roleCategory` | Role Pattern | utility/orchestrator/hub/leaf |
| `layer` | Clean Arch Layer | Domain/Application/Infrastructure |
| `ring` | Ring | CORE/APPLICATION/EXTERNAL |
| `rpbl_responsibility` | RPBL: Responsibility | Worker/Coordinator/Manager |
| `rpbl_purity` | RPBL: Purity | Pure/Impure/Mixed |
| `flow` | Flow Position | Entrance/Middle/Exit |
| `depth` | Call Depth | Distance from entry |
| `health` | Health Score | Green/Yellow/Red |

**Keyboard Shortcuts:**
- `C` = Cycle color modes
- `S` = Cycle size modes
- `T` = Toggle labels

---

## Category 4: EDGE APPEARANCE

Controls for edge/relationship visual properties.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `edge-mode` | Edge Style | dropdown | `type`, `gradient-tier`, `gradient-flow`, `gradient-depth` | `type` | `EDGE_MODE` | EDGE | P0 |
| `edge-style` | Line Style | button_group | `solid`, `dashed`, `particles` | `solid` | `EDGE_STYLE` | EDGE | P1 |
| `cfg-edge-opacity` | Opacity | slider | 0-1 | 0.6 | `APPEARANCE_STATE.edgeOpacity` | SIDEBAR | P0 |
| `cfg-edge-width` | Width | slider | 0.1-5 | 1.0 | `APPEARANCE_STATE.edgeWidth` | SIDEBAR | P1 |
| `cfg-edge-curve` | Curvature | slider | 0-1 | 0.2 | `APPEARANCE_STATE.edgeCurvature` | SIDEBAR | P1 |
| `cfg-toggle-arrows` | Show Arrows | toggle | on/off | on | `APPEARANCE_STATE.showArrows` | SIDEBAR | P0 |
| `cfg-toggle-gradient` | Gradient Color | toggle | on/off | off | `APPEARANCE_STATE.edgeGradient` | SIDEBAR | P1 |
| `cfg-particle-speed` | Particle Speed | slider | 0-0.05 | 0.01 | `FLOW_CONFIG.particleSpeed` | FLOW | P2 |
| `cfg-particle-width` | Particle Size | slider | 1-10 | 4 | `FLOW_CONFIG.particleWidth` | FLOW | P2 |
| `cfg-toggle-edge-hover` | Hover Highlight | toggle | on/off | on | `APPEARANCE_STATE.edgeHoverHighlight` | SIDEBAR | P1 |

**Edge Type Colors (Semantic):**
| Edge Type | Color | Meaning |
|-----------|-------|---------|
| `calls` | Blue | Function invocation |
| `contains` | Gray | Structural containment |
| `inherits` | Purple | Class inheritance |
| `imports` | Green | Module dependency |
| `implements` | Cyan | Interface implementation |

**Keyboard Shortcuts:**
- `E` = Cycle edge modes
- `A` = Toggle arrows
- `G` = Toggle gradient

---

## Category 5: FILTERING

Controls for data subset selection.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `filter-tier` | Filter Tiers | multi_select_chips | `T0`, `T1`, `T2` | [] | `VIS_FILTERS.tiers` | SIDEBAR | P0 |
| `filter-family` | Filter Families | multi_select_chips | `LOG`, `DAT`, `ORG`, `NET` | [] | `VIS_FILTERS.families` | SIDEBAR | P1 |
| `filter-ring` | Filter Rings | multi_select_chips | `DOMAIN`, `APPLICATION`, `INFRASTRUCTURE`, `PRESENTATION` | [] | `VIS_FILTERS.rings` | SIDEBAR | P1 |
| `filter-edges` | Filter Edge Types | multi_select_chips | `calls`, `contains`, `inherits`, `imports` | [] | `VIS_FILTERS.edges` | SIDEBAR | P1 |
| `filter-role` | Filter Roles | multi_select_chips | All 33 roles | [] | `VIS_FILTERS.roles` | SIDEBAR | P2 |
| `toggle-orphans` | Hide Orphans | toggle | on/off | off | `VIS_FILTERS.hideOrphans` | DATA | P1 |
| `toggle-dead-code` | Hide Dead Code | toggle | on/off | off | `VIS_FILTERS.hideDeadCode` | DATA | P1 |
| `filter-degree-min` | Min Connections | slider | 0-20 | 0 | `VIS_FILTERS.minDegree` | DATA | P2 |
| `filter-degree-max` | Max Connections | slider | 1-100 | 100 | `VIS_FILTERS.maxDegree` | DATA | P2 |
| `search-nodes` | Search | text_input | free text | "" | `SEARCH_QUERY` | SEARCH | P0 |
| `search-scope` | Search Scope | dropdown | `name`, `file`, `all` | `all` | `SEARCH_SCOPE` | SEARCH | P1 |

**Keyboard Shortcuts:**
- `/` = Focus search
- `O` = Toggle orphans
- `Ctrl+F` = Advanced filter panel

---

## Category 6: SELECTION

Controls for interactive element selection.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `selection-mode` | Selection Mode | button_group | `single`, `multi`, `lasso` | `single` | `SELECTION_MODE` | SELECTION | P0 |
| `selection-clear` | Clear Selection | button | - | - | `action:clearSelection` | SELECTION | P0 |
| `selection-invert` | Invert Selection | button | - | - | `action:invertSelection` | SELECTION | P2 |
| `selection-expand` | Expand to Neighbors | button | - | - | `action:expandSelection` | SELECTION | P1 |
| `selection-isolate` | Isolate Selection | button | - | - | `action:isolateSelection` | SELECTION | P1 |
| `selection-k-hop` | K-Hop Depth | slider | 1-5 | 1 | `SELECTION_K_HOP` | SELECTION | P1 |
| `selection-export` | Export Selection | button | - | - | `action:exportSelection` | EXPORT | P1 |
| `selection-fit` | Fit to Selection | button | - | - | `action:fitToSelection` | CAMERA | P1 |

**Keyboard Shortcuts:**
- `Escape` = Clear selection
- `Shift+Click` = Multi-select
- `N` = Expand to neighbors
- `I` = Isolate selection

---

## Category 7: CAMERA

Controls for 3D navigation and viewpoint.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `camera-zoom` | Zoom Level | slider | 0.01-200 | 1.0 | `CAMERA.zoom` | CAMERA | P1 |
| `btn-reset` | Reset Camera | button | - | - | `action:resetCamera` | SIDEBAR | P0 |
| `btn-fit-all` | Fit All | button | - | - | `action:fitAll` | CAMERA | P0 |
| `btn-fit-selection` | Fit Selection | button | - | - | `action:fitSelection` | CAMERA | P1 |
| `camera-auto-rotate` | Auto Rotate | toggle | on/off | off | `CAMERA.autoRotate` | CAMERA | P2 |
| `camera-rotate-speed` | Rotation Speed | slider | 0.1-5 | 1.0 | `CAMERA.rotateSpeed` | CAMERA | P2 |
| `camera-bookmark-save` | Save Bookmark | button | - | - | `action:saveBookmark` | CAMERA | P2 |
| `camera-bookmark-load` | Load Bookmark | dropdown | saved bookmarks | - | `action:loadBookmark` | CAMERA | P2 |

**Keyboard Shortcuts:**
- `Home` = Reset camera
- `F` = Fit all
- `Ctrl+1-9` = Load bookmark
- `Ctrl+Shift+1-9` = Save bookmark

---

## Category 8: EXPORT & CAPTURE

Controls for output generation.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `btn-screenshot` | Screenshot | button | - | - | `action:screenshot` | SIDEBAR | P0 |
| `export-format` | Image Format | dropdown | `png`, `jpeg`, `svg` | `png` | `EXPORT_FORMAT` | EXPORT | P1 |
| `export-resolution` | Resolution | dropdown | `1x`, `2x`, `4x` | `2x` | `EXPORT_RESOLUTION` | EXPORT | P1 |
| `export-background` | Background | dropdown | `dark`, `light`, `transparent` | `dark` | `EXPORT_BACKGROUND` | EXPORT | P1 |
| `export-data` | Export Data | button | - | - | `action:exportData` | EXPORT | P1 |
| `export-data-format` | Data Format | dropdown | `json`, `csv`, `graphml` | `json` | `EXPORT_DATA_FORMAT` | EXPORT | P2 |
| `export-video` | Record Video | button | - | - | `action:recordVideo` | EXPORT | P2 |

**Keyboard Shortcuts:**
- `P` = Screenshot
- `Ctrl+E` = Export data
- `Ctrl+Shift+P` = High-res screenshot

---

## Category 9: ACCESSIBILITY & HELP

Controls for inclusive design and user assistance.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `a11y-colorblind` | Colorblind Mode | dropdown | `none`, `deuteranopia`, `protanopia`, `tritanopia` | `none` | `A11Y.colorblindMode` | COLOR | P1 |
| `a11y-high-contrast` | High Contrast | toggle | on/off | off | `A11Y.highContrast` | COLOR | P1 |
| `a11y-reduced-motion` | Reduced Motion | toggle | on/off | auto | `A11Y.reducedMotion` | ANIM | P1 |
| `a11y-screen-reader` | Screen Reader Mode | toggle | on/off | off | `A11Y.screenReader` | A11Y | P2 |
| `btn-help` | Help Overlay | button | - | - | `action:showHelp` | PANELS | P0 |
| `btn-shortcuts` | Keyboard Shortcuts | button | - | - | `action:showShortcuts` | PANELS | P1 |
| `btn-tutorial` | Tutorial | button | - | - | `action:startTutorial` | PANELS | P2 |
| `loading-indicator` | Loading Status | indicator | progress | - | `LOADING_STATE` | UI | P0 |

**Keyboard Shortcuts:**
- `?` = Help overlay
- `Ctrl+/` = Keyboard shortcuts
- `Ctrl+.` = Command palette

---

## Category 10: ANALYSIS & INTELLIGENCE (Standard Model Specific)

Controls unique to code analysis visualization.

| ID | Label | Type | Options/Range | Default | State Path | Handler | Priority |
|----|-------|------|---------------|---------|------------|---------|----------|
| `toggle-codome` | Show Codome Boundaries | toggle | on/off | off | `APPEARANCE_STATE.showCodome` | SIDEBAR | P1 |
| `toggle-knots` | Highlight Cycles | toggle | on/off | off | `ANALYSIS.showKnots` | ANALYSIS | P1 |
| `toggle-bridges` | Highlight Bridges | toggle | on/off | off | `ANALYSIS.showBridges` | ANALYSIS | P2 |
| `btn-insights` | AI Insights Panel | button | - | - | `action:openInsights` | PANELS | P1 |
| `btn-report` | Brain Download | button | - | - | `action:openReport` | PANELS | P1 |
| `flow-animation` | Animate Flow | toggle | on/off | off | `FLOW.animate` | FLOW | P2 |
| `markov-threshold` | Flow Probability Threshold | slider | 0-1 | 0.1 | `FLOW.markovThreshold` | FLOW | P2 |
| `health-overlay` | Health Heatmap | toggle | on/off | off | `ANALYSIS.healthOverlay` | ANALYSIS | P2 |

---

## Implementation Roadmap

### Phase 1: Fix Broken (3 controls)
- `cfg-label-size` - Add handler logic
- `cfg-toggle-highlight` - Add handler logic
- `cfg-toggle-depth` - Add handler logic

### Phase 2: Wire Orphaned (6 controls)
- `cfg-toggle-edge-hover` - Add event listener
- `cfg-toggle-codome` - Add event listener
- `[data-edge-style]` - Add click handlers
- Wire 3 duplicate legacy IDs

### Phase 3: Add P0 Missing (8 controls)
- `search-nodes` - Command palette search
- `btn-help` - Help overlay with shortcuts
- `loading-indicator` - Progress feedback
- `btn-fit-all` - Fit to view button
- `a11y-colorblind` - Colorblind mode selector
- `selection-clear` (already exists, verify)
- `export-format` - Screenshot options
- `undo-action` - Undo last action

### Phase 4: Add P1 Features (24 controls)
- Filter chips (tier, family, ring)
- Selection expansion (neighbors, isolate)
- Camera bookmarks
- Export options
- Accessibility modes

### Phase 5: Add P2 Features (18 controls)
- Advanced physics tuning
- Video recording
- Flow animation
- Health heatmap

---

## State Architecture

```
GLOBAL_STATE
├── GRAPH_MODE: 'atoms' | 'files' | 'classes'
├── IS_3D: boolean
├── LAYOUT_FROZEN: boolean
├── APPEARANCE_STATE
│   ├── nodeScale: number
│   ├── nodeOpacity: number
│   ├── edgeOpacity: number
│   ├── edgeWidth: number
│   └── ...
├── VIS_STATE
│   ├── colorBy: string
│   ├── sizeBy: string
│   └── shapeBy: string
├── VIS_FILTERS
│   ├── tiers: string[]
│   ├── families: string[]
│   ├── rings: string[]
│   ├── edges: string[]
│   ├── roles: string[]
│   ├── hideOrphans: boolean
│   ├── hideDeadCode: boolean
│   └── maxDepth: number
├── PHYSICS_STATE
│   ├── charge: number
│   ├── linkDistance: number
│   ├── centerStrength: number
│   └── collisionRadius: number
├── SELECTION
│   ├── mode: 'single' | 'multi' | 'lasso'
│   ├── nodes: string[]
│   └── kHop: number
├── CAMERA
│   ├── zoom: number
│   ├── autoRotate: boolean
│   └── bookmarks: object[]
├── A11Y
│   ├── colorblindMode: string
│   ├── highContrast: boolean
│   └── reducedMotion: boolean
└── ANALYSIS
    ├── showKnots: boolean
    ├── showBridges: boolean
    └── healthOverlay: boolean
```

---

## Summary

| Category | P0 | P1 | P2 | Total |
|----------|----|----|----|----|
| View Modes | 2 | 1 | 1 | 4 |
| Layout & Physics | 2 | 4 | 2 | 8 |
| Node Appearance | 4 | 4 | 3 | 11 |
| Edge Appearance | 3 | 5 | 2 | 10 |
| Filtering | 2 | 6 | 3 | 11 |
| Selection | 2 | 5 | 1 | 8 |
| Camera | 2 | 2 | 4 | 8 |
| Export | 1 | 4 | 2 | 7 |
| Accessibility | 2 | 3 | 2 | 7 |
| Analysis | 0 | 4 | 4 | 8 |
| **Total** | **18** | **38** | **24** | **82** |

**Current State:** 29 working + 20 untested = 49 implemented
**Gap:** 33 controls to implement
**Target:** 82 total controls for professional-grade tool
