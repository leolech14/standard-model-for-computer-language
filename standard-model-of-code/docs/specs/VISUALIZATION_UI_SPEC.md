# Visualization UI Specification

> Technical specification for the Collider interactive visualization system.

---

## Overview

The visualization UI consists of modular JavaScript components that provide interactive exploration of the code graph. All modules follow the IIFE (Immediately Invoked Function Expression) pattern for encapsulation.

---

## Module Architecture

### Loading Order

Modules are loaded in dependency order by `visualize_graph_webgl.py`:

```
1.  performance.js       - Performance monitoring
2.  core.js              - Constants & utilities
3.  node-accessors.js    - Node property functions
4.  color-engine.js      - OKLCH color system
5.  refresh-throttle.js  - Throttled graph updates
6.  legend-manager.js    - Legend system
7.  data-manager.js      - Data access layer
8.  animation.js         - Layout & animation controller
9.  selection.js         - Selection system
10. panels.js            - Panel management
11. sidebar.js           - Sidebar controls
12. edge-system.js       - Edge coloring & modes
13. file-viz.js          - File visualization modes
14. control-bar.js       - Visual mapping command bar
15. main.js              - Entry point + wiring
16. app.js               - Legacy monolith (shrinking)
```

### Module Pattern

```javascript
const MODULE_NAME = (function() {
    'use strict';

    // Private state
    let _state = {};

    // Private functions
    function _privateHelper() { ... }

    // Public API
    return {
        init,
        publicMethod,
        get state() { return _state; }
    };
})();
```

### State Unification Pattern

When extracting code from `app.js` into modules, **state must be unified** to prevent dual-state bugs.

**Problem:** Incomplete extraction creates two state variables (one in module, one in app.js) that diverge at runtime.

**Solution:** Module becomes single source of truth. Global access via getters and shims.

```javascript
// IN MODULE (file-viz.js)
const FILE_VIZ = (function() {
    let _enabled = false;  // Single source of truth
    let _mode = 'color';

    return {
        get enabled() { return _enabled; },
        get mode() { return _mode; },
        setEnabled(v) { _enabled = v; /* ...UI updates... */ },
        setMode(m) { _mode = m; /* ...apply mode... */ }
    };
})();

// OUTSIDE MODULE - Global getters (backward compatibility)
Object.defineProperty(window, 'fileMode', {
    get: () => FILE_VIZ.enabled,
    set: (v) => FILE_VIZ.setEnabled(v),
    configurable: true
});

// OUTSIDE MODULE - Shim functions (for onclick handlers)
function setFileModeState(enabled) {
    FILE_VIZ.setEnabled(enabled);
}
```

**Checklist for extraction:**
1. Move state declaration to module (`let _state`)
2. Expose via getter in module API (`get state()`)
3. Add global getter outside IIFE (`Object.defineProperty`)
4. Add shim function if needed for HTML onclick
5. Remove original declaration from app.js
6. Verify single source of truth with grep

---

## Control Bar Module

**File:** `src/core/viz/assets/modules/control-bar.js`

### Purpose

Provides a persistent command bar for dynamic visual mapping of any data dimension to any visual property.

### Public API

```javascript
CONTROL_BAR.init()              // Initialize UI
CONTROL_BAR.toggle()            // Show/hide
CONTROL_BAR.show()              // Show
CONTROL_BAR.hide()              // Hide
CONTROL_BAR.applyMapping()      // Apply current mapping
CONTROL_BAR.resetMapping()      // Reset to defaults
CONTROL_BAR.createGroupFromSelection()  // Create group
CONTROL_BAR.removeGroup(id)     // Remove group
```

### UPB Data Sources (Universal Property Binder)

The `UPB` module (`modules/upb/endpoints.js`) defines the canonical registry of data sources. 
**New in v3:** All sources now include **Semantic Tags** for logic blending.

| Key | Label | Type | Domain | Semantic Tags |
|-----|-------|------|--------|---------------|
| `token_estimate` | Token Count | continuous | file | `[structural, quantitative, size]` |
| `line_count` | Line Count | continuous | file | `[structural, quantitative, verticality]` |
| `complexity_density`| Complexity | continuous | file | `[structural, qualitative, entropy]` |
| `age_days` | Age (days) | continuous | file | `[temporal, quantitative, decay]` |
| `in_degree` | In-Degree | continuous | node | `[topological, quantitative, popularity]` |
| `tier` | Tier (Layer) | discrete | node | `[architectural, categorical, hierarchy]` |
| `role` | Role | discrete | node | `[semantic, categorical, purpose]` |
| `is_stale` | Is Stale? | boolean | file | `[temporal, boolean, risk]` |

*(See `modules/upb/endpoints.js` for full registry)*

### UPB Visual Targets

All visual properties are now managed by `UPB` and include semantic tags for auto-binding logic.

| Key | Label | Category | Range | Semantic Tags |
|-----|-------|----------|-------|---------------|
| `nodeSize` | Node Size | geometry | [1, 30] | `[visual, geometric, magnitude]` |
| `xPosition` | X Position | geometry | [-1000, 1000] | `[visual, geometric, spatial]` |
| `hue` | Color Hue | color | [0, 360] | `[visual, chromatic, identity]` |
| `saturation` | Saturation | color | [0, 100] | `[visual, chromatic, intensity]` |
| `charge` | Repulsion | physics | [-500, 0] | `[simulation, force, isolation]` |
| `collisionRadius` | Body Size | physics | [1, 50] | `[simulation, force, barrier]` |

### Universal Property Binder (UPB) Architecture
The `control-bar.js` no longer contains mapping logic. It delegates to the **UPB Graph**:
1. `UPB.bind(source, target)`: Creates a persistent link.
2. `UPB.apply(nodes)`: Evaluates all links and updates node visuals.
3. `UPB.index.js`: Main entry point.

### Scale Functions

```javascript
SCALES = {
    linear: (v, min, max) => (v - min) / (max - min),
    log:    (v, min, max) => log10(v) normalized,
    sqrt:   (v, min, max) => sqrt(v) normalized,
    inverse: (v, min, max) => 1 - linear(v)
}
```

### Configuration State

```javascript
_config = {
    source: 'token_estimate',  // Data field to map from
    target: 'nodeSize',        // Visual property to map to
    scale: 'sqrt',             // Scale function
    scope: 'selection',        // 'selection' | 'all' | 'group:X'
    invert: false              // Flip mapping direction
}
```

### CSS Classes

| Class | Purpose |
|-------|---------|
| `.control-bar` | Main container |
| `.control-bar.collapsed` | Hidden state |
| `.control-section` | Section wrapper |
| `.cb-select` | Dropdown styling |
| `.cb-btn` | Button styling |
| `.cb-btn-primary` | Primary action button |
| `.cb-badge` | Count badge |
| `.group-chip` | Group indicator |

---

## File Visualization Module

**File:** `src/core/viz/assets/modules/file-viz.js`

### Purpose

Manages file-level visualization including file coloring, file graph (files as nodes), and visual mappings from file metadata.

### Public API

```javascript
FILE_VIZ.setMode(mode)          // Set viz mode
FILE_VIZ.toggle()               // Toggle file mode
FILE_VIZ.getColor(idx, total)   // Get file color
FILE_VIZ.buildFileGraph()       // Build file-level graph
FILE_VIZ.applyVisualMapping(key, nodes)  // Apply mapping
```

### Modes

| Mode | Description |
|------|-------------|
| `color` | Files colored by golden-angle hue distribution |
| `hulls` | Convex hull boundaries around file clusters |
| `cluster` | Force-directed clustering by file |
| `map` | File graph mode - files become first-class nodes |
| `spheres` | Containment spheres with collision |

### Visual Mappings

The `VISUAL_MAPPINGS` object defines how file metadata maps to visual properties:

```javascript
VISUAL_MAPPINGS = {
    size_bytes: {
        property: 'nodeSize',
        scale: 'sqrt',
        min: 2, max: 20,
        label: 'File Size (bytes)'
    },
    format_category: {
        property: 'hue',
        discrete: true,
        values: {
            code: 210, config: 45, doc: 120,
            data: 280, test: 340, style: 180
        }
    },
    // ... more mappings
}
```

### File Node Schema

When in file graph mode, file nodes have this structure:

```javascript
{
    id: 'file:0',
    name: 'atom_classifier.py',
    fileIdx: 0,
    isFileNode: true,
    val: 5,                    // Node size
    color: 'hsl(210, 70%, 50%)',
    file_path: 'src/patterns/atom_classifier.py',
    atom_count: 15,
    // Enriched metadata
    size_bytes: 14298,
    token_estimate: 3572,
    line_count: 367,
    age_days: 5,
    format_category: 'code',
    complexity_density: 33.8,
    cohesion: 0.72
}
```

---

## Edge System Module

**File:** `src/core/viz/assets/modules/edge-system.js`

### Public API

```javascript
EDGE.setMode(mode)    // Set edge coloring mode
EDGE.cycleMode()      // Cycle through modes
EDGE.getColor(link)   // Get color for edge
EDGE.getWidth(link)   // Get width for edge
EDGE.apply()          // Apply current mode
```

### Edge Modes

| Mode | Description |
|------|-------------|
| `gradient-tier` | Color by source/target tier |
| `gradient-file` | Color by source/target file |
| `gradient-flow` | Color by data flow direction |
| `gradient-depth` | Color by graph depth |
| `gradient-semantic` | Color by semantic similarity |
| `type` | Color by edge type |
| `weight` | Color by edge weight |
| `mono` | Single color |

---

## Data Flow

### File Metadata Enrichment

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Python Pipeline (full_analysis.py)                │
│  FileEnricher adds:                                         │
│  - size_bytes, token_estimate, line_count                   │
│  - age_days, modified_date                                  │
│  - format_category, purpose                                 │
│  - complexity_density, cohesion                             │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: JSON Payload (unified_analysis.json)              │
│  file_boundaries[] contains enriched data                   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: JS Visualization                                  │
│  - DATA module loads file_boundaries                        │
│  - FILE_VIZ.buildFileGraph() creates file nodes             │
│  - CONTROL_BAR.applyMapping() maps data to visuals          │
└─────────────────────────────────────────────────────────────┘
```

### Selection Flow

```
User Click → SELECT.toggle(node) → Update SELECTED_NODE_IDS
           → updateSelectionVisuals() → Graph.refresh()
           → CONTROL_BAR.updateNodeCount()
```

### Visual Mapping Flow

```
User Config → CONTROL_BAR._config
Apply Click → getTargetNodes() → Filter by scope
            → applyMapping() → For each node:
                → getNodeValue(node, source)
                → scaleFn(value, min, max)
                → applyToNode(node, target, value)
            → Graph.refresh()
```

---

## Keyboard Integration

Shortcuts are registered in `main.js` via `MODULE_SHORTCUTS`:

```javascript
window.MODULE_SHORTCUTS = {
    'KeyM': () => CONTROL_BAR.toggle(),
    'Backquote': () => CONTROL_BAR.toggle()
};
```

The keyboard handler in `app.js` checks `MODULE_SHORTCUTS` before other handlers.

---

## Styling Guidelines

### Color Palette (Dark Glassmorphic)

```css
--bg-primary: rgba(20, 25, 35, 0.95);
--bg-secondary: rgba(30, 40, 60, 0.8);
--border-subtle: rgba(100, 150, 255, 0.2);
--border-active: rgba(100, 180, 255, 0.5);
--text-primary: #e0e8ff;
--text-secondary: rgba(150, 180, 255, 0.7);
--accent-blue: #4a9eff;
```

### Backdrop Blur

```css
backdrop-filter: blur(20px);
```

### Transitions

```css
transition: all 0.2s ease;  /* UI interactions */
transition: transform 0.3s ease;  /* Panel animations */
```

---

## Extension Points

### Adding a New Data Source

1. Add to `DATA_SOURCES` in `control-bar.js`:
```javascript
DATA_SOURCES.my_metric = {
    label: 'My Metric',
    type: 'continuous',
    domain: 'node'
};
```

2. Add to source dropdown HTML in `createUI()`

3. Ensure data is available on nodes (via enrichment pipeline or graph analysis)

### Adding a New Visual Target

1. Add to `VISUAL_TARGETS` in `control-bar.js`:
```javascript
VISUAL_TARGETS.myProperty = {
    label: 'My Property',
    category: 'appearance',
    range: [0, 100]
};
```

2. Add to target dropdown HTML

3. Handle in `applyToNode()`:
```javascript
case 'myProperty':
    node.myProperty = value;
    break;
```

4. Ensure the graph renderer uses this property

---

## Performance Considerations

- Use `REFRESH.throttled()` for graph updates (max 60fps)
- File graph mode guards against >500 nodes for flock simulation
- Spatial hashing for O(n) neighbor lookup in animations
- Debounce node count updates (1000ms interval)
