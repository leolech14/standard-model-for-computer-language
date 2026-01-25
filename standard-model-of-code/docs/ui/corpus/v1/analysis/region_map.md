# UI Region Map (9-Region Semantic Topology)

**Generated:** 2026-01-25
**Source:** template.html + ui_layout_model.json + dom_controls.json
**Status:** COMPLETE

---

## 3x3 Semantic Grid

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER (48px)                                   │
│  [Logo] [Stats: Nodes|Edges|Entropy] [GPU] [FPS]           [Target Name]    │
├──────────────────┬───────────────────────────────┬──────────────────────────┤
│                  │                               │                          │
│  LEFT SIDEBAR    │      CANVAS (3D Graph)        │    RIGHT SIDEBAR         │
│  (300px)         │      (flex: 1)                │    (280px)               │
│                  │                               │                          │
│  ┌────────────┐  │  ┌─────────────────────────┐  │  ┌────────────────────┐  │
│  │ View Mode  │  │  │                         │  │  │ Selection Panel    │  │
│  │ ATOMS|FILES│  │  │                         │  │  │ - Node details     │  │
│  ├────────────┤  │  │    3d-force-graph       │  │  │ - Metrics          │  │
│  │ Node Config│  │  │                         │  │  ├────────────────────┤  │
│  │ - Size     │  │  │    WebGL Canvas         │  │  │ Color Schemes      │  │
│  │ - Opacity  │  │  │                         │  │  │ - Tier             │  │
│  │ - Labels   │  │  │    (ForceGraph3D)       │  │  │ - Family           │  │
│  ├────────────┤  │  │                         │  │  │ - Ring             │  │
│  │ Edge Config│  │  │                         │  │  │ - File             │  │
│  │ - Opacity  │  │  │                         │  │  ├────────────────────┤  │
│  │ - Width    │  │  │                         │  │  │ Control Bar (UPB)  │  │
│  │ - Curve    │  │  │                         │  │  │ - Scope            │  │
│  ├────────────┤  │  └─────────────────────────┘  │  │ - Source           │  │
│  │ Physics    │  │                               │  │ - Target           │  │
│  │ - Charge   │  │  ┌─────────────────────────┐  │  │ - Scale            │  │
│  │ - Link     │  │  │ Tooltip / Legend        │  │  └────────────────────┘  │
│  │ - Presets  │  │  └─────────────────────────┘  │                          │
│  ├────────────┤  │                               │                          │
│  │ Layout     │  │                               │                          │
│  │ Presets    │  │                               │                          │
│  └────────────┘  │                               │                          │
│                  │                               │                          │
├──────────────────┴───────────────────────────────┴──────────────────────────┤
│                              DOCK (Mode Bar)                                 │
│  [2D] [Files] [Freeze] [Screenshot] [Reset]              [Selection Count]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Region Definitions

### Row 0: Global HUD (Header)

| Region | Position | Purpose | Controls |
|--------|----------|---------|----------|
| `hud.left` | Top-left | Brand + Stats | `.logo`, `.stat-value` (nodes/edges/entropy) |
| `hud.center` | Top-center | Performance | `#fps-display`, GPU info |
| `hud.right` | Top-right | Target | `.target-name`, density indicator |

### Row 1: Work Surface (Main Area)

| Region | Position | Purpose | Controls |
|--------|----------|---------|----------|
| `rail.left` | Left sidebar | Configuration | All `#cfg-*` controls, `.btn[data-*]` |
| `canvas.main` | Center | Visualization | `#3d-graph`, tooltips, legends |
| `rail.right` | Right sidebar | Context | Selection panel, color schemes, UPB |

### Row 2: Dock (Bottom)

| Region | Position | Purpose | Controls |
|--------|----------|---------|----------|
| `dock.left` | Bottom-left | View modes | `#btn-2d`, `#btn-files` |
| `dock.center` | Bottom-center | Actions | `#btn-freeze`, `#btn-screenshot` |
| `dock.right` | Bottom-right | Selection | Count indicators, group actions |

---

## Control → Region Mapping

### Left Sidebar (`rail.left`)

| Section | Controls | Status |
|---------|----------|--------|
| **View Mode** | `#view-mode-toggle .view-mode-btn` | ✅ Wired |
| **Node Config** | `#cfg-node-size`, `#cfg-node-opacity`, `#cfg-node-res` | ✅ Wired |
| **Node Labels** | `#cfg-toggle-labels`, `#cfg-label-size` | ✅ Wired |
| **Node Appearance** | `#cfg-toggle-highlight`, `#cfg-toggle-pulse`, `#cfg-toggle-depth` | ✅ Wired |
| **Size Mode** | `.btn[data-size-mode]` | ✅ Wired (app.js) |
| **Edge Config** | `#cfg-edge-opacity`, `#cfg-edge-width`, `#cfg-edge-curve` | ✅ Wired |
| **Edge Style** | `.btn[data-edge-style]` | ✅ Wired (app.js) |
| **Edge Particles** | `#cfg-particle-speed`, `#cfg-particle-count` | ✅ Wired |
| **Edge Toggles** | `#cfg-toggle-arrows`, `#cfg-toggle-gradient`, `#cfg-toggle-edge-hover` | ✅ Wired |
| **CODOME** | `#cfg-toggle-codome` | ✅ Wired |
| **Physics** | `#physics-charge`, `#physics-link`, `#physics-center` | ✅ Wired |
| **Physics Presets** | `.btn[data-physics]` | ✅ Wired |
| **Layout Presets** | `.btn[data-layout]` | ✅ Wired |

### Right Sidebar (`rail.right`)

| Section | Controls | Status |
|---------|----------|--------|
| **Color Schemes** | `.color-btn[data-preset]` | ✅ Wired |
| **Selection Panel** | `#hover-panel`, `#selection-panel` | ✅ Wired |
| **Control Bar (UPB)** | `#cb-scope`, `#cb-source`, `#cb-target`, `#cb-scale` | ✅ Wired |

### Dock (`dock.*`)

| Section | Controls | Status |
|---------|----------|--------|
| **Dimension** | `#btn-2d` | ✅ Wired |
| **View Mode** | `#btn-files` | ✅ Wired |
| **Actions** | `#btn-freeze`, `#btn-screenshot`, `#btn-reset` | ✅ Wired |

---

## CSS Layout Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `--sidebar-width` | 300px | Left sidebar default |
| `--right-panel-width` | 280px | Right sidebar default |
| `--min-sidebar-width` | 240px | Collapse threshold |
| `--max-sidebar-width` | 500px | Expand limit |
| `--header-height` | 48px | Top bar height |

---

## Accessibility Notes

- All sidebars collapsible (responsive design)
- Keyboard shortcuts: `M` or `` ` `` for Control Bar, `I` for info, `Esc` to close
- Touch targets: minimum 44px per constraint
- Focus management: panels trap focus when open

---

## Region Health

| Region | Controls | Wired | Coverage |
|--------|----------|-------|----------|
| `hud.*` | 8 | 8 | 100% |
| `rail.left` | 20 | 20 | 100% |
| `canvas.main` | 2 | 2 | 100% |
| `rail.right` | 8 | 8 | 100% |
| `dock.*` | 5 | 5 | 100% |
| **Total** | **43** | **43** | **100%** |

---

## Integration Points

- **SIDEBAR module**: `src/core/viz/assets/modules/sidebar.js` - Primary binding location
- **Control Bar**: `src/core/viz/assets/modules/control-bar.js` - UPB mappings
- **Circuit Breaker**: `src/core/viz/assets/modules/circuit-breaker.js` - Validation
- **Layout**: `src/core/viz/assets/modules/layout.js` - Spatial management

---

*Generated by Agent Alpha - UI Overhaul Wave C*
