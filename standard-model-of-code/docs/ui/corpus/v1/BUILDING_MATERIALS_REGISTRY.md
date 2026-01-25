# UI Building Materials Registry v1.1

**Date:** 2026-01-25
**Purpose:** Fine-grained inventory of all UI components, modules, tokens, and systems
**Status:** ACTIVE - Continuously Updated
**Validated By:** analyze.py + Gemini (gemini-3-pro-preview)

---

## VALIDATION SUMMARY (analyze.py)

| Metric | Value | Status |
|--------|-------|--------|
| **Total Controls** | 33 | VALIDATED |
| **Wired (functional)** | 22 (66.7%) | OK |
| **Orphaned (no binding)** | 8 (24.2%) | NEEDS FIX |
| **Dead Handler (empty)** | 3 (9.1%) | NEEDS FIX |
| **Pixel Sovereignty** | 75% | NEEDS WORK |
| **cfg-* IDs** | 17 | DOCUMENTED |
| **data-* Attributes** | 8 | DOCUMENTED |

**Research Sources:**
- Control Inventory: `research/gemini/docs/20260125_050508_ui_gap_fill__build_a_control_inventory_for_collid.md`
- Token Audit: `research/gemini/docs/20260125_050716_ui_gap_fill__token_sovereignty_audit__find____css.md`

---

## 1. Summary Metrics

| Category | Count | Location |
|----------|-------|----------|
| **JS Modules** | 58 | `modules/` |
| **UPB Modules** | 6 | `modules/upb/` |
| **Token Files** | 6 | `schema/viz/tokens/` |
| **CSS Lines** | 3,034 | `styles.css` |
| **app.js Lines** | 2,999 | `app.js` (legacy) |
| **HTML Template** | 1 | `template.html` |

---

## 2. Module Registry (58 Files)

### 2.1 Core Systems (Foundation)

| Module | Lines | Purpose | Dependencies |
|--------|-------|---------|--------------|
| `main.js` | 393 | Entry point, global bindings | All |
| `core.js` | 226 | Utilities, constants | None |
| `utils.js` | 636 | Helper functions | None |
| `registry.js` | 165 | Module registry pattern | None |

### 2.2 State Management

| Module | Lines | Purpose | State Object |
|--------|-------|---------|--------------|
| `vis-state.js` | ~400 | Unified state manager | `VIS_STATE` |
| `datamap.js` | 586 | Data→Visual mapping | `DATAMAP` |
| `data-manager.js` | 1,387 | Node/edge data store | `DataManager` |

### 2.3 Color System (OKLCH)

| Module | Lines | Purpose | Public API |
|--------|-------|---------|------------|
| `color-engine.js` | 1,399 | OKLCH color engine | `COLOR.get()`, `COLOR.getInterval()` |
| `color-helpers.js` | 442 | Color utilities | `hexToRgb()`, `interpolate()` |
| `color-telemetry.js` | 809 | Color debugging | `COLOR_TELEM.emit()` |
| `color-contract-test.js` | 658 | Color validation | `COLOR_TEST.runAll()` |
| `file-color-model.js` | 387 | File-based colors | `FileColorModel` |

### 2.4 Property Query (Provider Chain)

| Module | Lines | Purpose | Priority |
|--------|-------|---------|----------|
| `property-query.js` | 638 | Core query engine | - |
| `property-query-init.js` | 530 | Initialization | - |
| `upb-defaults.js` | 222 | Default bindings | 80 |

### 2.5 UPB (Universal Property Binder)

| Module | Lines | Purpose |
|--------|-------|---------|
| `upb/index.js` | 189 | UPB orchestrator |
| `upb/endpoints.js` | 673 | Source/target definitions |
| `upb/bindings.js` | 628 | Binding graph logic |
| `upb/scales.js` | 135 | Transform functions |
| `upb/blenders.js` | 133 | Value blending |

### 2.6 UI Chrome (Panels, Controls)

| Module | Lines | Purpose | Region |
|--------|-------|---------|--------|
| `sidebar.js` | 2,739 | Main sidebar logic | rail.left, rail.right |
| `control-bar.js` | 1,536 | Mapping controls | rail.left.top |
| `panels.js` | 1,126 | Panel management | all |
| `ui-manager.js` | 617 | UI orchestration | all |
| `ui-builders.js` | 932 | DOM builders | all |
| `hud.js` | 257 | HUD overlay | hud.* |
| `CodomeHUD.js` | 220 | Codome display | hud.center |
| `SettingsPanel.js` | 378 | Settings modal | overlay |

### 2.7 Visualization Core

| Module | Lines | Purpose |
|--------|-------|---------|
| `node-helpers.js` | 815 | Node rendering |
| `node-accessors.js` | 273 | Node property access |
| `edge-system.js` | 1,128 | Edge rendering |
| `selection.js` | 1,738 | Selection system |
| `hover.js` | 385 | Hover interactions |
| `tooltips.js` | 363 | Tooltip rendering |
| `legend-manager.js` | 573 | Legend display |

### 2.8 Layout System

| Module | Lines | Purpose |
|--------|-------|---------|
| `layout.js` | 1,440 | Main layout engine |
| `layout-helpers.js` | 407 | Layout utilities |
| `layout-forces.js` | 487 | Force calculations |
| `spatial.js` | 511 | Spatial algorithms |
| `AxialLayout.js` | 177 | Axial positioning |
| `file-tree-layout.js` | 764 | File tree layout |

### 2.9 Physics & Animation

| Module | Lines | Purpose |
|--------|-------|---------|
| `physics.js` | 483 | Physics simulation |
| `animation.js` | 1,500 | Animation system |
| `flow.js` | 1,067 | Flow animations |

### 2.10 Specialized Renderers

| Module | Lines | Purpose |
|--------|-------|---------|
| `hull-visualizer.js` | 793 | Convex hulls |
| `TowerRenderer.js` | 266 | Tower viz |
| `unlit-nodes.js` | 489 | Unlit rendering |
| `groups.js` | 499 | Group rendering |
| `HolarchyMapper.js` | 166 | Hierarchy mapping |

### 2.11 Features & Tools

| Module | Lines | Purpose |
|--------|-------|---------|
| `file-viz.js` | 703 | File visualization |
| `pipeline-navigator.js` | 1,068 | Pipeline nav |
| `report.js` | 692 | Report generation |
| `theory.js` | 710 | Theory display |
| `dimension.js` | 468 | Dimension controls |
| `theme.js` | 309 | Theme switching |

### 2.12 Performance

| Module | Lines | Purpose |
|--------|-------|---------|
| `perf-monitor.js` | 435 | FPS monitoring |
| `hardware-info.js` | 149 | GPU detection |
| `refresh-throttle.js` | 274 | Render throttling |
| `circuit-breaker.js` | 1,204 | Validation system |
| `InteractionManager.js` | 130 | Input handling |

---

## 3. Token Registry (6 Files)

### 3.1 theme.tokens.json (22,220 bytes)

**Purpose:** UI chrome theming - colors, typography, shadows

| Category | Token Count | Examples |
|----------|-------------|----------|
| `color.bg.*` | 18 | `base`, `surface`, `elevated`, `hover` |
| `color.border.*` | 6 | `default`, `subtle`, `strong`, `focus` |
| `color.text.*` | 8 | `primary`, `secondary`, `muted`, `disabled` |
| `color.accent.*` | 12 | `primary`, `primary-dim`, `teal`, `purple` |
| `color.status.*` | 14 | `success`, `warning`, `error`, `info` |
| `color.viz.*` | 8 | `tooltip-bg`, `node-glow`, `selection` |
| `color.edge.*` | 10 | `calls`, `contains`, `uses`, `imports` |
| `typography.family.*` | 2 | `sans`, `mono` |
| `typography.size.*` | 8 | `2xs`→`2xl` |
| `typography.weight.*` | 4 | `normal`, `medium`, `semibold`, `bold` |
| `shadow.*` | 5 | `none`, `sm`, `md`, `lg`, `glow-accent` |
| `themes.light.*` | ~50 | Light theme overrides |
| `themes.high-contrast.*` | ~50 | Accessibility theme |

### 3.2 layout.tokens.json (3,858 bytes)

**Purpose:** Spacing, sizing, z-index, transitions

| Category | Token Count | Examples |
|----------|-------------|----------|
| `spacing.*` | 16 | `0`→`12` (0px→32px) |
| `radius.*` | 7 | `none`, `sm`, `md`, `lg`, `full` |
| `z-index.*` | 8 | `base`→`toast` (0→10000) |
| `duration.*` | 6 | `instant`→`lazy` (0ms→600ms) |
| `easing.*` | 5 | `linear`, `ease`, cubic-beziers |
| `transition.*` | 8 | `default`, `fast`, `colors`, `transform` |
| `breakpoint.*` | 5 | `sm`→`2xl` (640px→1536px) |
| `size.panel-width.*` | 3 | `sm`, `md`, `lg` |
| `size.button-height.*` | 3 | `sm`, `md`, `lg` |
| `blur.*` | 5 | `none`→`xl` (0→24px) |
| `offset.*` | 3 | `sidebar-top`, `panel-margin` |

### 3.3 appearance.tokens.json (14,566 bytes)

**Purpose:** Visual appearance defaults

| Category | Purpose |
|----------|---------|
| `node.*` | Default node appearance |
| `edge.*` | Default edge appearance |
| `animation.*` | Animation defaults |

### 3.4 controls.tokens.json (22,037 bytes)

**Purpose:** Control configuration

| Category | Purpose |
|----------|---------|
| `sliders.*` | Slider ranges and defaults |
| `toggles.*` | Toggle states |
| `presets.*` | Preset configurations |

### 3.5 physics.tokens.json (3,449 bytes)

**Purpose:** Physics simulation parameters

| Category | Purpose |
|----------|---------|
| `charge.*` | Node repulsion |
| `link.*` | Link forces |
| `gravity.*` | Center gravity |

### 3.6 performance.tokens.json (2,603 bytes)

**Purpose:** Performance thresholds

| Category | Purpose |
|----------|---------|
| `fps.*` | Target frame rates |
| `limits.*` | Node/edge limits |

---

## 4. CSS Architecture (3,034 lines)

### 4.1 Structure

| Section | Lines | Purpose |
|---------|-------|---------|
| Body/Base | 1-50 | Base styles, CSS vars |
| Bridge Layer | 69-91 | Legacy → Token mapping |
| HUD Panels | 25-70 | Top overlay panels |
| Bottom Dock | 94-200 | Bottom control dock |
| Sidebars | 200-600 | Left/right sidebars |
| Controls | 600-1200 | Sliders, buttons, chips |
| Panels | 1200-1800 | Panel internals |
| Specialized | 1800-2400 | Tooltips, modals, etc. |
| Responsive | 2400-2800 | Media queries |
| Animations | 2800-3034 | Keyframes |

### 4.2 CSS Variable Usage

| Pattern | Count | Example |
|---------|-------|---------|
| `var(--color-*)` | ~200 | `var(--color-bg-surface)` |
| `var(--spacing-*)` | ~150 | `var(--spacing-6)` |
| `var(--radius-*)` | ~40 | `var(--radius-sm)` |
| `var(--typography-*)` | ~80 | `var(--typography-size-sm)` |
| Hardcoded values | ~50 | **VIOLATIONS** |

---

## 5. Control Inventory

### 5.1 Sliders (cfg-*)

| ID | Label | State Path | Range |
|----|-------|------------|-------|
| `cfg-edge-opacity` | Edge Opacity | `APPEARANCE_STATE.edgeOpacity` | 0-1 |
| `cfg-edge-width` | Edge Width | `APPEARANCE_STATE.edgeWidth` | 0.1-5 |
| `cfg-edge-curve` | Edge Curvature | `APPEARANCE_STATE.edgeCurvature` | 0-1 |
| `cfg-node-size` | Node Size | `APPEARANCE_STATE.nodeScale` | 0.1-3 |
| `cfg-node-opacity` | Node Opacity | `APPEARANCE_STATE.nodeOpacity` | 0-1 |
| `physics-charge` | Physics Charge | `Graph.d3Force('charge')` | -500 to 0 |
| `physics-link` | Link Distance | `Graph.d3Force('link')` | 10-200 |

### 5.2 Toggles

| ID | Label | State Path |
|----|-------|------------|
| `cfg-toggle-arrows` | Show Arrows | `APPEARANCE_STATE.showArrows` |
| `cfg-toggle-labels` | Show Labels | `APPEARANCE_STATE.showLabels` |
| `cfg-toggle-pulse` | Pulse Animation | `APPEARANCE_STATE.pulseEnabled` |
| `cfg-toggle-depth` | 3D Depth Shading | `APPEARANCE_STATE.depthShading` |

### 5.3 Buttons (btn-*)

| ID | Label | Action |
|----|-------|--------|
| `btn-2d` | 2D | Toggle dimension |
| `btn-3d` | 3D | Toggle dimension |
| `btn-files` | Files | Switch view mode |
| `btn-atoms` | Atoms | Switch view mode |
| `btn-reset` | Reset | Reset all settings |

### 5.4 Chips (Color Mode)

| ID | Label | Category |
|----|-------|----------|
| `tier` | TIER | Architecture |
| `family` | FAMILY | Taxonomy |
| `layer` | LAYER | Architecture |
| `ring` | RING | Topology |
| `role` | Role | Taxonomy |
| `complexity` | Complexity | Metrics |
| `loc` | LOC | Metrics |
| `fan_in` | Fan-In | Metrics |
| `fan_out` | Fan-Out | Metrics |
| `centrality` | Centrality | Topology |

### 5.5 Dropdowns (Mapping)

| ID | Purpose | Options Source |
|----|---------|----------------|
| `mapping-source` | Data source | `UPB.endpoints.sources` |
| `mapping-target` | Visual target | `UPB.endpoints.targets` |
| `mapping-scale` | Scale function | `UPB.scales` |

### 5.6 Color Schemes (33 Named)

**Sequential:** viridis, plasma, magma, inferno, cividis, turbo, mako, rocket

**Diverging:** coolwarm, spectral

**Thematic:** thermal, nightvision, ocean, terrain, electric

**Role-Semantic:** query, finder, command, creator, destroyer, factory, repository, cache, service, orchestrator, validator, guard, transformer, parser, handler, emitter, utility, lifecycle

---

## 6. Region Map (9-Square)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              COLLIDER UI REGIONS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┬─────────────────────────────────────┬─────────────┐       │
│   │ hud.left    │           hud.center                │ hud.right   │       │
│   │ Brand, stats│    Performance, Hardware cards      │ Counters    │       │
│   ├─────────────┼─────────────────────────────────────┼─────────────┤       │
│   │ rail.left   │                                     │ rail.right  │       │
│   │   .top      │                                     │   .top      │       │
│   │ SCOPE       │                                     │ SELECTION   │       │
│   │ MAPPING     │                                     │             │       │
│   ├─────────────┤         canvas.main                 ├─────────────┤       │
│   │ rail.left   │                                     │ rail.right  │       │
│   │   .body     │      (3D graph visualization)       │   .body     │       │
│   │ NODE CONFIG │                                     │ COLOR       │       │
│   │ EDGE CONFIG │                                     │ SCHEMES     │       │
│   │             │                                     │ COLOR MODE  │       │
│   ├─────────────┴─────────────────────────────────────┴─────────────┤       │
│   │                         dock.bottom                              │       │
│   │                   (Mode bar, view toggles)                       │       │
│   └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Data Flow Chains

### 7.1 Node Color Chain

```
User clicks TIER chip
    → sidebar.js:setColorMode('tier')
    → vis-state.js:VIS_STATE.colorBy = 'tier'
    → property-query.js:Q.node(n, 'color')
    → node-accessors.js:NODE.getTier(n)
    → color-engine.js:COLOR.get('tier', tierValue)
    → OKLCH → Hex conversion
    → Three.js material.color
    → GPU render
```

### 7.2 UI Chrome Chain

```
HTML element with class="hud-panel"
    → styles.css: background: var(--color-bg-elevated)
    → Bridge layer: --color-bg-elevated (CSS var)
    → Token injection: oklch(16% 0.02 250)
    → Browser CSS engine
    → Rendered pixel
```

### 7.3 Control Update Chain

```
User moves slider cfg-node-size
    → sidebar.js:_bindAppearanceControls()
    → APPEARANCE_STATE.nodeScale = value
    → VIS_STATE._epoch++
    → property-query cache invalidated
    → Graph.nodeVal() re-queries
    → Three.js geometry update
    → GPU render
```

---

## 8. Pixel Sovereignty Audit

### 8.1 Tokenized (75%)

| Area | Status | Source |
|------|--------|--------|
| Panel backgrounds | TOKEN | `var(--color-bg-*)` |
| Panel borders | TOKEN | `var(--color-border-*)` |
| Text colors | TOKEN | `var(--color-text-*)` |
| Spacing | TOKEN | `var(--spacing-*)` |
| Typography | TOKEN | `var(--typography-*)` |
| Shadows | TOKEN | `var(--shadow-*)` |
| Transitions | TOKEN | `var(--transition-*)` |

### 8.2 Violations (25%)

| Location | Issue | Fix |
|----------|-------|-----|
| `app.js:112` | `EDGE_COLOR_CONFIG` hardcoded | Move to tokens |
| `app.js:515` | `FLOW_PRESETS` hardcoded | Move to tokens |
| `styles.css` | ~50 hardcoded values | Replace with vars |
| `theme.tokens.json` vs `appearance.tokens.json` | Conflict | Merge |

---

## 9. External Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| Three.js | 0.149.0 | 3D rendering |
| 3d-force-graph | 1.73.3 | Force-directed layout |
| d3-force-3d | 3.0.5 | Physics simulation |

---

## 10. Build Artifacts

| File | Generated By | Contains |
|------|--------------|----------|
| `collider_report.html` | `visualize_graph_webgl.py` | Standalone HTML with inlined CSS/JS |

**Generation command:**
```bash
./collider full <path> --output <dir>
```

---

## 11. Quick Reference: What Goes Where

| Need to... | Edit |
|------------|------|
| Change UI colors | `schema/viz/tokens/theme.tokens.json` |
| Change spacing | `schema/viz/tokens/layout.tokens.json` |
| Change node colors | `modules/color-engine.js` palette |
| Add new control | `modules/sidebar.js` + `styles.css` |
| Add new color scheme | `modules/color-engine.js` schemePaths |
| Change physics | `schema/viz/tokens/physics.tokens.json` |
| Change layout rules | `styles.css` (CSS) or `modules/layout.js` (JS) |

---

## 12. Next: Phase 2 Artifacts Needed

| Artifact | Status | Path |
|----------|--------|------|
| `dom_controls.json` | PENDING | `corpus/v1/extracted/` |
| `bindings.json` | PENDING | `corpus/v1/extracted/` |
| `tokens.json` | PARTIAL | `corpus/v1/extracted/` |
| `bypass_report.md` | PENDING | `corpus/v1/analysis/` |
| `region_map.md` | PENDING | `corpus/v1/analysis/` |
