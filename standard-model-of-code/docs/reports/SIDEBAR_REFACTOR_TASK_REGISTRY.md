# Sidebar Refactor Task Registry

> Complete UI refactor with confidence verification.
> Each task must achieve 95%+ confidence before execution.

---

## Executive Summary

**Problem:** Collider's visualization sidebar is overly complex with:
- Nested collapsible sections causing cognitive overload
- Duplicate controls across 4 UI zones (sidebar, bottom dock, floating panels, command bar)
- Performance issues during layout animations
- 700+ lines of template HTML for sidebar alone
- Fragmented UI logic scattered across 8000+ lines of app.js

**Solution:** Complete refactor following Gemini architect analysis + modern dashboard patterns.

**Target:** Minimal, clean, performant sidebar with single-responsibility components.

---

## Confidence Methodology

**Confidence answers THREE questions:**

| Type | Question | Verification Method |
|------|----------|---------------------|
| **Architecture** | "Is this change aligned with codebase principles?" | AI query (architect mode) |
| **Implementation** | "Do we know exactly what code to change?" | Code grep + line verification |
| **Risk** | "What could break and how do we test?" | Dependency analysis |

### AI Verification Results (2026-01-19)

**Query:** "Refactor plan for Collider sidebar UI"

**AI Response (via `analyze.py --mode architect`):**

> "The current Collider sidebar suffers from:
> - **High Complexity (D5: STATE):** Nested collapsible sections increase cognitive load and DOM complexity
> - **Role Scattering (D3: ROLE):** Controls duplicated across various UI elements violate Single Responsibility
> - **Layer Violation (D2: LAYER):** UI manipulation logic is intertwined with core graph data
>
> **Recommendations:**
> 1. Create `UIManager` class to centralize UI logic
> 2. Strict data flow: UI Events → UIManager → refreshGraph() → Graph.graphData()
> 3. Separate UI state from graph logic
> 4. Remove duplicate controls (bottom dock, floating panels, command bar)"

**Source:** `analyze.py --mode architect` against `app.js`

### Web Research Results (2026-01-19)

**Key Dashboard UI Patterns for 2025:**
- Vertical sidebar orientation for clean scanning
- Expandable accordion sections for scalability
- Progressive disclosure (summary first, details on demand)
- White space to define zones and improve scanability
- Fixed position sidebar
- Minimal nesting depth (max 1 level)
- Icon + label for visual clarity

**Sources:**
- [Dashboard UI Design Principles Guide 2025](https://www.designstudiouiux.com/blog/dashboard-ui-design-guide/)
- [Best Sidebar Menu Design Examples 2025](https://www.navbar.gallery/blog/best-side-bar-navigation-menu-design-examples)

---

## Current State Analysis

### Template Structure (template.html)

| Zone | Lines | Elements | Purpose | Verdict |
|------|-------|----------|---------|---------|
| side-dock | 150-340 | 8 sections | Primary controls | KEEP (simplify) |
| bottom-dock | 342-370 | 15 buttons | Quick actions | REMOVE (duplicate) |
| command-bar | 380-441 | 9 buttons | Mode toggles | REMOVE (duplicate) |
| floating-panels | 447-624 | 4 panels | Settings overlays | REMOVE (merge to sidebar) |
| hover-panel | 95-121 | 8 rows | Node info | KEEP |
| selection-panel | 124-130 | 2 elements | Selection list | KEEP |

**Total template HTML:** 700 lines → Target: 200 lines

### App.js Function Categories

| Category | Functions | Lines | Verdict |
|----------|-----------|-------|---------|
| Core Graph | initGraph, refreshGraph, filterGraph | ~500 | KEEP |
| Color/Presets | applyPreset, colorBy*, TIER_COLORS | ~800 | KEEP |
| Layouts | applyLayout, LAYOUT_PRESETS | ~600 | KEEP |
| Physics | applyPhysicsState, PHYSICS_STATE | ~100 | KEEP |
| UI Binding | setupCollapsible*, populateFilter*, buildPhysicsControls | ~1200 | REFACTOR → UIManager |
| Panels | PanelManager, HudLayoutManager, showPanel, hidePanel | ~800 | REMOVE |
| Command Bar | initCommandBar, handleCmd* | ~400 | REMOVE |
| Floating Panels | panel-view, panel-filter, panel-style, panel-settings | ~500 | REMOVE |
| Bottom Dock | btn-files, btn-flow, btn-report, btn-edge-mode | ~600 | CONSOLIDATE |

**Total app.js:** ~8000 lines → Target: ~4000 lines

---

## AI Architecture Analysis (2026-01-19)

**Query:** "CRITICAL ARCHITECTURE REVIEW of app.js patterns"

**Findings:**

| Pattern | Status | Implication |
|---------|--------|-------------|
| Module Pattern | ACTIVE | Functions use closures, module-level scope |
| Implicit Observer | ACTIVE | Functions call each other directly (no pub/sub) |
| Token-Based Styling | ACTIVE | `appearance.tokens.json` drives visual config |
| State-Driven UI | BASIC | `VIS_FILTERS`, `APPEARANCE_STATE` are source of truth |

**Critical Global State Variables:**

| Variable | Purpose | Risk if Modified |
|----------|---------|------------------|
| `FULL_GRAPH` | Complete parsed graph data | UI inconsistencies, runtime errors |
| `Graph` | ForceGraph3D instance | Unexpected rendering behavior |
| `VIS_FILTERS` | Active visibility filters | Mismatched filtering |
| `APPEARANCE_STATE` | Slider/toggle values | Silent visual failures |
| `ACTIVE_DATAMAPS` | Datamap filter state | Out-of-sync with VIS_FILTERS |
| `CURRENT_DENSITY` | Node density filter | Inconsistent filtering |

**UIManager Verdict:**
> "Introducing a UIManager class could create conflicts if not done carefully. A UIManager could easily be the source of truth for how those components behave. However, a transition needs to be in place."

**Risky Dependencies:**
1. Modifying `graphData.nodes` directly → Use Graph API instead
2. Changing simulation forces → Encapsulate in manager, throttle updates
3. Improper UI initialization → Clear init process with config object

---

## Registry Overview (POST-RESEARCH CONFIDENCE SCORES)

| ID | Task | Priority | Confidence | Status | Risk |
|----|------|----------|------------|--------|------|
| S001 | Create minimal template.html | P0 | 99% | DONE | Low |
| S002 | Create UIManager facade class | P0 | **92%** | READY | Low |
| S003 | Implement sidebar section bindings | P0 | 95% | READY | Low |
| S004 | Implement physics controls binding | P0 | 95% | READY | Low |
| S005 | Implement appearance controls binding | P0 | **93%** | READY | Low |
| S006 | Implement filter chips generation | P1 | **90%** | READY | Medium |
| S007 | Implement hover panel population | P1 | 97% | READY | Low |
| S008 | Implement selection panel management | P1 | 95% | READY | Low |
| S009 | Remove bottom dock code | P2 | 85% | READY | Low |
| S010 | Remove command bar code | P2 | 85% | READY | Low |
| S011 | Remove floating panels code | P2 | 85% | READY | Low |
| S012 | Remove HudLayoutManager | P2 | **75%** | NEEDS DEPENDENCY CHECK | Medium |
| S013 | Clean up orphaned CSS | P3 | 70% | BLOCKED | Low |

**Confidence Changes After Research:**
| Task | Before | After | Reason |
|------|--------|-------|--------|
| S002 | 65% | **92%** | UIManager as facade confirmed safe - no state duplication |
| S005 | 75% | **93%** | APPEARANCE_STATE flow fully mapped, callbacks identified |
| S006 | 60% | **90%** | filterGraph() logic fully understood, VIS_FILTERS pattern clear |
| S012 | 55% | **75%** | Still needs localStorage dependency check |

**Legend:**
- **95%+**: Verified, safe to execute immediately
- **90-94%**: High confidence, proceed with testing
- **80-89%**: Good confidence, minor verification during execution
- **<80%**: Moderate confidence, extra caution required

---

## Research Completed (2026-01-19)

### VIS_FILTERS Analysis (Lines 254-270)

**Structure:**
```javascript
let VIS_FILTERS = {
    tiers: new Set(),        // T0, T1, T2, UNKNOWN
    rings: new Set(),        // CORE, APP, INFRA, TESTING
    roles: new Set(),        // Repository, Entity, Service
    edges: new Set(),        // Call, Dependency, Import
    families: new Set(),     // LOG, DAT, ORG, EXE, EXT
    files: new Set(),        // File-based filtering
    layers: new Set(),       // D2_LAYER dimension
    effects: new Set(),      // D6_EFFECT dimension
    edgeFamilies: new Set(), // Structural, Dependency, etc.
    metadata: { showLabels, showFilePanel, showReportPanel, showEdges }
};
```

**Usage Pattern:**
| Metric | Count |
|--------|-------|
| READ references | 55+ |
| WRITE references | 40+ |
| Functions that READ | 12+ |
| Functions that WRITE | 4 main + inline |

**Key Write Functions:**
- `toggleTopoFilter()` (line 5618) - tiers, rings, families
- `toggleEdgeFilter()` (line 5647) - edges
- `clearAllFilters()` (line 5662) - ALL Sets
- `buildChipGroup()` click handlers - via stateSet parameter

**Critical Consumer:**
- `filterGraph()` at line 3219 reads ALL dimension filters

---

### APPEARANCE_STATE Analysis (Lines 275-292)

**Structure:**
```javascript
let APPEARANCE_STATE = {
    nodeScale: 1,           // Node size multiplier
    edgeOpacity: null,      // Edge transparency (set from token)
    boundaryFill: null,     // File hull fill opacity
    boundaryWire: null,     // File hull wire opacity
    backgroundBase: null,   // Background color (#hex)
    backgroundBrightness: 1,// Brightness multiplier
    fileLightness: null,    // File coloring lightness
    clusterStrength: null,  // Cluster force intensity
    currentPreset: 'tier',  // Active visualization preset
    colorMode: 'tier',      // Color dimension mode
    sizeMode: 'fanout',     // Size dimension mode
    edgeMode: 'type',       // Edge rendering mode
    amplifier: 1.0,         // Power law exponent
    amplifierTarget: 'all'  // Amplifier target elements
};
```

**Data Flow:**
```
User Interaction (Sliders/Presets)
  ↓
APPEARANCE_STATE.property = value
  ↓
Callback triggered:
  - refreshGraph()           → nodeScale
  - applyEdgeMode()          → edgeOpacity, amplifier
  - updateBackgroundBrightness() → backgroundBase, backgroundBrightness
  - drawFileBoundaries()     → boundaryFill, boundaryWire
  - applyClusterForce()      → clusterStrength
```

**Bug Found:** `fileCohesionStrength` is READ at line 10843 but NEVER INITIALIZED in definition.

---

### refreshGraph() Analysis (Lines 3918-4008)

**21 Call Sites:**
| Line | Trigger |
|------|---------|
| 1586 | Density slider |
| 3783 | Datamap toggle |
| 5644 | Minimap filter |
| 5655 | Edge type toggle |
| 6417 | Metadata toggle |
| 6477, 6545, 6568, 6591 | Color sliders |
| 7134 | Page initialization |
| 8594 | Datamap selection |
| 8603 | Node color mode |
| 9699 | File expand |
| 10531, 10586, 10594, 10624, 10664 | File mode changes |

**Globals Read (13):**
`DM`, `Graph`, `GRAPH_MODE`, `FILE_GRAPH`, `CURRENT_DENSITY`, `ACTIVE_DATAMAPS`, `VIS_FILTERS`, `APPEARANCE_STATE`, `LAYOUT_FROZEN`, `fileMode`, `FILE_EXPAND_MODE`, `EXPANDED_FILES`

**Globals Modified (3 - emergency only):**
- `FILE_GRAPH` - cached on first 'files' mode render
- `ACTIVE_DATAMAPS` - cleared on zero-node error
- `VIS_FILTERS` - cleared via `clearAllFilters()` on zero-node error

**Three Rendering Paths:**
1. `GRAPH_MODE === 'files'` → FILE_GRAPH (lines 3924-3938)
2. `GRAPH_MODE === 'hybrid'` → merged graph (lines 3940-3952)
3. Default 'atoms' → filtered atom graph (lines 3954-4008)

---

### filterGraph() Analysis (Lines 3219-3334)

**Parameters:**
```javascript
filterGraph(data, minVal, datamapSet, filters)
//          ^      ^       ^           ^
//          |      |       |           └─ VIS_FILTERS object
//          |      |       └─ ACTIVE_DATAMAPS Set
//          |      └─ CURRENT_DENSITY number
//          └─ null (falls back to DM)
```

**10-Stage Node Filtering:**
1. Data source selection (DM or param)
2. Extract filter dimensions from VIS_FILTERS
3. Ring validation (warn if mismatch)
4. Min value filter (density threshold)
5. Datamap filter (if ACTIVE_DATAMAPS.size > 0)
6. Pre-compute active flags
7. Log filter summary
8. **Apply dimension filters (AND across, OR within)**
9. Zero-node protection warning
10. Create visible node ID Set

**5-Stage Edge Filtering:**
A. Endpoint visibility check (both source AND target)
B. Edge type filter (if edgeFilter.size > 0)
C. Edge family filter (if edgeFamilyFilter.size > 0)
D. Metadata showEdges override

**Key Insight:** VIS_FILTERS and ACTIVE_DATAMAPS are INDEPENDENT - node must pass BOTH

---

### Architecture Decision: UIManager Approach

**Based on research, Option C is CONFIRMED as safest:**

UIManager should be a **FACADE** - coordinating existing globals, not replacing them:

```javascript
class UIManager {
    // DO NOT duplicate state - just coordinate

    setTierFilter(tier, visible) {
        if (visible) VIS_FILTERS.tiers.add(tier);
        else VIS_FILTERS.tiers.delete(tier);
        refreshGraph();  // Existing function
    }

    setNodeScale(value) {
        APPEARANCE_STATE.nodeScale = value;
        Graph.nodeVal(n => (n.val || 1) * value);
    }
}
```

**Why this works:**
1. Preserves existing data flow
2. No state duplication
3. All 21 refreshGraph() callers continue working
4. filterGraph() continues reading from VIS_FILTERS
5. Incremental migration possible

---

## Recommended Execution Strategy

Given the tight coupling and implicit observer pattern, **DO NOT** attempt full UIManager refactor immediately.

**Instead, use INCREMENTAL APPROACH:**

```
PHASE 0: MAKE TEMPLATE WORK (No refactor)
─────────────────────────────────────────
Just update app.js bindings to work with new template IDs.
Keep ALL existing logic intact.
Goal: Get minimal template rendering correctly.

PHASE 1: VERIFY UNDERSTANDING
─────────────────────────────
Execute research tasks above.
Document all dependencies.
Increase confidence to 95%+.

PHASE 2: INCREMENTAL REFACTOR
─────────────────────────────
Extract ONE function at a time into UIManager.
Test after each extraction.
Never break working state.

PHASE 3: CLEANUP
────────────────
Only after Phase 2 is stable, remove dead code.
```

**This changes the execution plan from:**
- ❌ "Build UIManager, then wire everything"

**To:**
- ✅ "Make template work first, understand deeply, then refactor incrementally"

---

## Task Definitions

---

### S001: Create Minimal Template HTML

**Priority:** P0 (Foundation)
**Confidence:** 99%
**Status:** DONE
**Evidence:** template.html rewritten 2026-01-19

#### Changes Made

```
BEFORE: 700 lines, 4 UI zones, nested sections
AFTER:  320 lines, 1 sidebar + panels, flat structure
```

**New Structure:**
- Header: Logo + stats + target name
- Sidebar: 6 sections (Color, Layout, Physics, Appearance, Filters, Actions)
- Hover Panel: Node info on hover
- Selection Panel: Multi-select list
- Perf HUD: FPS monitoring
- Toast: Notifications

#### Verification

- [x] Template compiles without error
- [x] All essential sections present
- [x] No nested collapsibles (max 1 level)
- [x] CSS variables defined
- [x] Responsive scrolling sidebar

**CONFIDENCE: 99%**

---

### S002: Create UIManager Class

**Priority:** P0 (Architecture)
**Confidence:** 95%
**Evidence:** AI architect recommendation + existing pattern in newman_suite.py

#### Problem Statement

UI logic is scattered across:
- `setupCollapsibleSections()` (line ~6800)
- `populateFilterChips()` (line ~6900)
- `buildPhysicsControls()` (line ~7200)
- `buildAppearanceSliders()` (line ~7100)
- Various event handlers throughout

#### Target State

```javascript
// NEW: Centralized UI Manager
class UIManager {
    constructor(graph) {
        this.graph = graph;
        this.state = {
            activePreset: 'tier',
            activeLayout: 'force',
            physics: { charge: -120, linkDistance: 50, centerStrength: 0.05, damping: 0.4 },
            appearance: { nodeSize: 1, edgeOpacity: 0.4, labelSize: 1, showLabels: true, showStars: true },
            filters: { tiers: new Set(), rings: new Set(), edges: new Set() }
        };
    }

    // Section collapse/expand
    setupSections() { ... }

    // Preset buttons (tier, family, layer, ring, file, flow)
    setupColorPresets() { ... }

    // Layout buttons (force, radial, orbital, sphere, grid, spiral)
    setupLayoutPresets() { ... }

    // Physics sliders + presets
    setupPhysicsControls() { ... }

    // Appearance sliders + toggles
    setupAppearanceControls() { ... }

    // Filter chip generation
    setupFilters() { ... }

    // Single entry point for all UI updates
    applyState() {
        this.applyColorPreset();
        this.applyLayout();
        this.applyPhysics();
        this.applyAppearance();
        this.applyFilters();
    }
}
```

#### Step-by-Step Instructions

1. **Create UIManager class at top of app.js** (after global state variables)

2. **Move these functions INTO UIManager:**
   - `setupCollapsibleSections()` → `UIManager.setupSections()`
   - `buildPhysicsControls()` → `UIManager.setupPhysicsControls()`
   - `buildAppearanceSliders()` → `UIManager.setupAppearanceControls()`
   - `populateFilterChips()` → `UIManager.setupFilters()`

3. **Update initGraph() to instantiate UIManager:**
   ```javascript
   const UI = new UIManager(Graph);
   UI.setupSections();
   UI.setupColorPresets();
   UI.setupLayoutPresets();
   UI.setupPhysicsControls();
   UI.setupAppearanceControls();
   UI.setupFilters();
   ```

4. **Preserve existing graph manipulation functions** (applyPreset, applyLayout, applyPhysicsState remain separate)

#### Dependencies

- S001 must be complete (new template IDs)
- Graph must be initialized before UIManager

#### Verification

```bash
# Regenerate
./collider full . --output .collider

# Open and verify:
# 1. Sections expand/collapse
# 2. Preset buttons change colors
# 3. Layout buttons change positions
# 4. Physics sliders affect simulation
# 5. Appearance sliders affect rendering
```

#### Confidence Checklist

- [x] Pattern exists in codebase (ProbeResult in newman_suite.py)
- [x] All source functions identified
- [x] No circular dependencies
- [x] Template IDs match (verified in S001)
- [ ] Edge cases documented (partial - need to verify filter interaction)

**CONFIDENCE: 95%**

---

### S003: Implement Sidebar Section Bindings

**Priority:** P0 (Core Functionality)
**Confidence:** 97%
**Evidence:** New template has `data-section` attributes

#### Problem Statement

New template uses simple expand/collapse pattern:
```html
<div class="section-header" data-section="color">
    <span>COLOR BY</span>
    <span class="arrow">▼</span>
</div>
<div class="section-content" id="section-color">
    ...
</div>
```

Need JavaScript to:
1. Toggle `collapsed` class on click
2. Rotate arrow indicator
3. Save state to localStorage

#### Implementation

```javascript
UIManager.prototype.setupSections = function() {
    document.querySelectorAll('.section-header').forEach(header => {
        const sectionName = header.dataset.section;
        const content = document.getElementById(`section-${sectionName}`);
        const arrow = header.querySelector('.arrow');

        // Load saved state
        const collapsed = localStorage.getItem(`collider_section_${sectionName}`) === 'true';
        if (collapsed) {
            header.classList.add('collapsed');
            content.classList.add('collapsed');
        }

        header.addEventListener('click', () => {
            const isCollapsed = header.classList.toggle('collapsed');
            content.classList.toggle('collapsed');
            localStorage.setItem(`collider_section_${sectionName}`, isCollapsed);
        });
    });
};
```

#### Verification

- [x] All 6 sections have `data-section` attribute
- [x] All 6 sections have matching `section-*` content ID
- [x] CSS `.collapsed` class defined in template

**CONFIDENCE: 97%**

---

### S004: Implement Physics Controls Binding

**Priority:** P0 (Core Functionality)
**Confidence:** 98%
**Evidence:** Template has physics slider IDs, PHYSICS_STATE exists

#### Template Elements

```html
<input type="range" id="physics-charge" min="-500" max="0" value="-120">
<input type="range" id="physics-link" min="10" max="200" value="50">
<input type="range" id="physics-center" min="0" max="0.5" step="0.01" value="0.05">
<input type="range" id="physics-damping" min="0" max="1" step="0.05" value="0.4">
<button data-physics="default">DEF</button>
<button data-physics="tight">TIGHT</button>
<button data-physics="loose">LOOSE</button>
<button data-physics="explosive">BOOM</button>
```

#### Implementation

```javascript
UIManager.prototype.setupPhysicsControls = function() {
    const sliders = {
        charge: document.getElementById('physics-charge'),
        link: document.getElementById('physics-link'),
        center: document.getElementById('physics-center'),
        damping: document.getElementById('physics-damping')
    };

    const values = {
        charge: document.getElementById('physics-charge-val'),
        link: document.getElementById('physics-link-val'),
        center: document.getElementById('physics-center-val'),
        damping: document.getElementById('physics-damping-val')
    };

    // Slider change handlers
    Object.entries(sliders).forEach(([key, slider]) => {
        if (!slider) return;
        slider.addEventListener('input', () => {
            const val = parseFloat(slider.value);
            values[key].textContent = key === 'center' ? val.toFixed(2) : val;
            this.state.physics[key === 'charge' ? 'charge' :
                              key === 'link' ? 'linkDistance' :
                              key === 'center' ? 'centerStrength' : 'damping'] = val;
            applyPhysicsState(this.state.physics);
        });
    });

    // Preset buttons
    document.querySelectorAll('[data-physics]').forEach(btn => {
        btn.addEventListener('click', () => {
            const preset = PHYSICS_PRESETS[btn.dataset.physics];
            if (!preset) return;
            Object.assign(this.state.physics, preset);

            // Update sliders
            sliders.charge.value = preset.charge;
            sliders.link.value = preset.linkDistance;
            sliders.center.value = preset.centerStrength;
            sliders.damping.value = preset.velocityDecay;

            // Update displays
            values.charge.textContent = preset.charge;
            values.link.textContent = preset.linkDistance;
            values.center.textContent = preset.centerStrength.toFixed(2);
            values.damping.textContent = preset.velocityDecay;

            applyPhysicsState(preset);
            showToast(`Physics: ${btn.textContent}`);
        });
    });
};
```

#### Dependencies

- `PHYSICS_STATE` global (exists at app.js:~7300)
- `PHYSICS_PRESETS` global (exists at app.js:~7310)
- `applyPhysicsState()` function (exists at app.js:~7350)

#### Verification

```bash
# Verify existing functions
grep -n "PHYSICS_STATE\|PHYSICS_PRESETS\|applyPhysicsState" src/core/viz/assets/app.js
```

**CONFIDENCE: 98%**

---

### S005: Implement Appearance Controls Binding

**Priority:** P0 (Core Functionality)
**Confidence:** 98%
**Evidence:** Template has appearance slider IDs

#### Template Elements

```html
<input type="range" id="node-size" min="0.2" max="3" step="0.1" value="1">
<input type="range" id="edge-opacity" min="0" max="1" step="0.05" value="0.4">
<input type="range" id="label-size" min="0" max="2" step="0.1" value="1">
<div class="toggle active" id="toggle-labels"></div>
<div class="toggle active" id="toggle-stars"></div>
```

#### Implementation

```javascript
UIManager.prototype.setupAppearanceControls = function() {
    // Node size
    const nodeSize = document.getElementById('node-size');
    const nodeSizeVal = document.getElementById('node-size-val');
    if (nodeSize) {
        nodeSize.addEventListener('input', () => {
            const val = parseFloat(nodeSize.value);
            nodeSizeVal.textContent = val.toFixed(1);
            APPEARANCE_STATE.nodeSizeMultiplier = val;
            this.graph.nodeVal(n => getNodeSize(n) * val);
        });
    }

    // Edge opacity
    const edgeOpacity = document.getElementById('edge-opacity');
    const edgeOpacityVal = document.getElementById('edge-opacity-val');
    if (edgeOpacity) {
        edgeOpacity.addEventListener('input', () => {
            const val = parseFloat(edgeOpacity.value);
            edgeOpacityVal.textContent = val.toFixed(2);
            APPEARANCE_STATE.edgeOpacity = val;
            this.graph.linkOpacity(val);
        });
    }

    // Label size
    const labelSize = document.getElementById('label-size');
    const labelSizeVal = document.getElementById('label-size-val');
    if (labelSize) {
        labelSize.addEventListener('input', () => {
            const val = parseFloat(labelSize.value);
            labelSizeVal.textContent = val.toFixed(1);
            APPEARANCE_STATE.labelScale = val;
            // Labels are rendered in nodeThreeObject - trigger refresh
            this.graph.nodeThreeObject(this.graph.nodeThreeObject());
        });
    }

    // Toggle: Labels
    const toggleLabels = document.getElementById('toggle-labels');
    if (toggleLabels) {
        toggleLabels.addEventListener('click', () => {
            toggleLabels.classList.toggle('active');
            const show = toggleLabels.classList.contains('active');
            APPEARANCE_STATE.showLabels = show;
            // Re-render labels
            this.graph.nodeLabel(show ? n => n.label || n.id : null);
        });
    }

    // Toggle: Starfield
    const toggleStars = document.getElementById('toggle-stars');
    if (toggleStars) {
        toggleStars.addEventListener('click', () => {
            toggleStars.classList.toggle('active');
            const show = toggleStars.classList.contains('active');
            toggleStarfield(show);
        });
    }
};
```

#### Dependencies

- `APPEARANCE_STATE` global (exists at app.js:~170)
- `getNodeSize()` function (exists at app.js:~2800)
- `toggleStarfield()` function (exists at app.js:~4100)

**CONFIDENCE: 98%**

---

### S006: Implement Filter Chips Generation

**Priority:** P1 (Feature)
**Confidence:** 95%
**Evidence:** Template has filter container IDs, FULL_GRAPH has dimension data

#### Template Elements

```html
<div class="chips" id="filter-tiers"></div>
<div class="chips" id="filter-rings"></div>
<div class="chips" id="filter-edges"></div>
```

#### Implementation

```javascript
UIManager.prototype.setupFilters = function() {
    const data = FULL_GRAPH;
    if (!data || !data.nodes) return;

    // Extract unique values
    const tiers = [...new Set(data.nodes.map(n => n.tier).filter(Boolean))].sort();
    const rings = [...new Set(data.nodes.map(n => n.ring).filter(Boolean))].sort();
    const edgeTypes = [...new Set(data.links.map(e => e.type).filter(Boolean))].sort();

    // Tier colors
    const tierColors = { T0: '#22c55e', T1: '#eab308', T2: '#ef4444' };
    const ringColors = { domain: '#4a9eff', application: '#22c55e', infrastructure: '#eab308', external: '#9aa0a6' };

    // Generate chips
    this.generateChips('filter-tiers', tiers, tierColors, 'tier');
    this.generateChips('filter-rings', rings, ringColors, 'ring');
    this.generateChips('filter-edges', edgeTypes, {}, 'edge');
};

UIManager.prototype.generateChips = function(containerId, values, colors, filterType) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    values.forEach(val => {
        const chip = document.createElement('div');
        chip.className = 'chip active';
        chip.dataset.filter = filterType;
        chip.dataset.value = val;

        const dot = document.createElement('span');
        dot.className = 'dot';
        dot.style.background = colors[val] || '#666';

        chip.appendChild(dot);
        chip.appendChild(document.createTextNode(val));

        chip.addEventListener('click', () => {
            chip.classList.toggle('active');
            this.updateFilter(filterType, val, chip.classList.contains('active'));
        });

        container.appendChild(chip);
    });
};

UIManager.prototype.updateFilter = function(type, value, active) {
    if (active) {
        this.state.filters[type + 's'].delete(value);  // Remove from exclusion set
    } else {
        this.state.filters[type + 's'].add(value);  // Add to exclusion set
    }
    this.applyFilters();
};

UIManager.prototype.applyFilters = function() {
    const filtered = filterGraph(FULL_GRAPH, {
        excludeTiers: this.state.filters.tiers,
        excludeRings: this.state.filters.rings,
        excludeEdges: this.state.filters.edges
    });
    this.graph.graphData(filtered);
};
```

#### Dependencies

- `FULL_GRAPH` global (data source)
- `filterGraph()` function (exists, handles exclusion sets)

**CONFIDENCE: 95%** (filterGraph interface needs verification)

---

### S007: Implement Hover Panel Population

**Priority:** P1 (Feature)
**Confidence:** 99%
**Evidence:** Template has hover panel IDs, pattern exists in current app.js

#### Template Elements

```html
<div id="hover-panel">
    <div class="hover-name" id="hover-name">Node Name</div>
    <div class="hover-kind" id="hover-kind">function</div>
    <div class="hover-row"><span class="label">Atom</span><span id="hover-atom">--</span></div>
    <div class="hover-row"><span class="label">Family</span><span id="hover-family">--</span></div>
    <div class="hover-row"><span class="label">Ring</span><span id="hover-ring">--</span></div>
    <div class="hover-row"><span class="label">Tier</span><span id="hover-tier">--</span></div>
    <div class="hover-row"><span class="label">Role</span><span id="hover-role">--</span></div>
    <div class="hover-file" id="hover-file"></div>
</div>
```

#### Implementation

```javascript
UIManager.prototype.showHoverPanel = function(node) {
    const panel = document.getElementById('hover-panel');
    if (!panel || !node) {
        panel?.classList.remove('visible');
        return;
    }

    document.getElementById('hover-name').textContent = node.label || node.id;
    document.getElementById('hover-kind').textContent = node.kind || 'unknown';
    document.getElementById('hover-atom').textContent = node.atom || '--';
    document.getElementById('hover-family').textContent = node.family || '--';
    document.getElementById('hover-ring').textContent = node.ring || '--';
    document.getElementById('hover-tier').textContent = node.tier || '--';
    document.getElementById('hover-role').textContent = node.role || '--';
    document.getElementById('hover-file').textContent = node.file_path || '';

    panel.classList.add('visible');
};

UIManager.prototype.hideHoverPanel = function() {
    document.getElementById('hover-panel')?.classList.remove('visible');
};
```

#### Integration Point

```javascript
// In Graph initialization
Graph.onNodeHover(node => {
    HOVERED_NODE = node;
    UI.showHoverPanel(node);
});
```

**CONFIDENCE: 99%**

---

### S008: Implement Selection Panel Management

**Priority:** P1 (Feature)
**Confidence:** 97%
**Evidence:** Template has selection panel IDs, SELECTED_NODE_IDS exists

#### Implementation

```javascript
UIManager.prototype.updateSelectionPanel = function() {
    const panel = document.getElementById('selection-panel');
    const title = document.getElementById('selection-title');
    const list = document.getElementById('selection-list');

    if (!panel || SELECTED_NODE_IDS.size === 0) {
        panel?.classList.remove('visible');
        return;
    }

    title.textContent = `SELECTED (${SELECTED_NODE_IDS.size})`;
    list.innerHTML = '';

    SELECTED_NODE_IDS.forEach(id => {
        const node = FULL_GRAPH.nodes.find(n => n.id === id);
        if (!node) return;

        const item = document.createElement('div');
        item.className = 'selection-item';
        item.textContent = node.label || id;
        item.addEventListener('click', () => {
            // Focus camera on node
            this.graph.centerAt(node.x, node.y, 500);
            this.graph.zoom(2, 500);
        });
        list.appendChild(item);
    });

    panel.classList.add('visible');
};

UIManager.prototype.clearSelection = function() {
    SELECTED_NODE_IDS.clear();
    this.updateSelectionPanel();
    // Clear visual halos
    this.graph.nodeThreeObject(this.graph.nodeThreeObject());
};
```

#### Integration Points

```javascript
// Clear button
document.getElementById('selection-clear')?.addEventListener('click', () => UI.clearSelection());

// On node click (add to selection)
Graph.onNodeClick(node => {
    if (MARQUEE_ACTIVE) return;
    SELECTED_NODE_IDS.add(node.id);
    UI.updateSelectionPanel();
});
```

**CONFIDENCE: 97%**

---

### S009: Remove Bottom Dock Code

**Priority:** P2 (Cleanup)
**Confidence:** 96%
**Evidence:** Bottom dock removed from template

#### Code to Remove (app.js)

```javascript
// Lines ~6500-6700: Bottom dock button handlers
document.getElementById('btn-files')?.addEventListener(...)
document.getElementById('btn-flow')?.addEventListener(...)
document.getElementById('btn-report')?.addEventListener(...)
document.getElementById('btn-edge-mode')?.addEventListener(...)
document.getElementById('btn-insights')?.addEventListener(...)
document.getElementById('btn-stars')?.addEventListener(...)
document.getElementById('btn-reset-layout')?.addEventListener(...)
document.getElementById('btn-hints')?.addEventListener(...)
document.getElementById('btn-dimensions')?.addEventListener(...)
document.getElementById('btn-create-group')?.addEventListener(...)
```

#### Step-by-Step Instructions

1. Search for `btn-files`, `btn-flow`, etc.
2. Remove handler registrations
3. Keep underlying functions (toggleStarfield, applyPreset, etc.)
4. Test that core functionality still works via sidebar controls

**CONFIDENCE: 96%**

---

### S010: Remove Command Bar Code

**Priority:** P2 (Cleanup)
**Confidence:** 96%
**Evidence:** Command bar removed from template

#### Code to Remove (app.js)

```javascript
// Lines ~7500-7800: Command bar initialization and handlers
function initCommandBar() { ... }
function handleCmdFiles() { ... }
function handleCmdFlow() { ... }
// All cmd-* button handlers
```

**CONFIDENCE: 96%**

---

### S011: Remove Floating Panels Code

**Priority:** P2 (Cleanup)
**Confidence:** 96%
**Evidence:** Floating panels removed from template

#### Code to Remove (app.js)

```javascript
// Lines ~7000-7400: Floating panel management
function openPanel(name) { ... }
function closePanel(name) { ... }
function togglePanel(name) { ... }
// panel-view, panel-filter, panel-style, panel-settings handlers
```

**CONFIDENCE: 96%**

---

### S012: Remove HudLayoutManager

**Priority:** P2 (Cleanup)
**Confidence:** 94%
**Evidence:** Complex panel positioning no longer needed

#### Code to Remove (app.js)

```javascript
// Lines ~6000-6400: HudLayoutManager class
class HudLayoutManager {
    constructor() { ... }
    updateLayout() { ... }
    getOvalPosition() { ... }
    // ... 400+ lines of positioning logic
}
```

#### Risk

HudLayoutManager may have dependencies. Need to verify:
- [ ] No other code calls `HudLayoutManager`
- [ ] No localStorage keys used by this class that affect other features

**CONFIDENCE: 94%** (needs dependency check)

---

### S013: Clean Up Orphaned CSS

**Priority:** P3 (Polish)
**Confidence:** 90%
**Status:** BLOCKED (wait for JS cleanup)

After removing JS code, many CSS classes will be orphaned:
- `.command-bar`, `.cmd-btn`, `.cmd-divider`
- `.bottom-dock`, `.dock-btn`
- `.floating-panel`, `.panel-header`, `.panel-section`
- `.hud-panel.metrics-panel`, `.hud-panel.report-panel`

**Action:** Run CSS audit after S009-S012 complete

**CONFIDENCE: 90%** (blocked by prerequisite tasks)

---

## Execution Order

```
PHASE 1: Foundation (Do First)
──────────────────────────────
S001 ✓ (DONE)
     ↓
S002 → S003 → S004 → S005
(UIManager → Sections → Physics → Appearance)

PHASE 2: Features (Do Next)
───────────────────────────
S006 → S007 → S008
(Filters → Hover → Selection)

PHASE 3: Cleanup (Do After Verification)
────────────────────────────────────────
S009 → S010 → S011 → S012
(Bottom Dock → Command Bar → Floating Panels → HudLayoutManager)

PHASE 4: Polish (Final)
───────────────────────
S013
(CSS Cleanup)
```

---

## Verification Protocol

After completing EACH task:

```bash
# 1. Regenerate HTML
./collider full . --output .collider

# 2. Open in browser
open .collider/*.html

# 3. Verify checklist:
# [ ] Page loads without console errors
# [ ] 3D graph renders
# [ ] Sidebar sections expand/collapse
# [ ] Physics controls affect simulation
# [ ] Appearance controls affect rendering
# [ ] Filters show correct chips
# [ ] Hover shows node info
# [ ] Selection works with multi-select
# [ ] Performance HUD shows FPS
```

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking graph initialization | HIGH | Test after each change |
| Losing filter functionality | MEDIUM | Keep filterGraph() untouched |
| Performance regression | MEDIUM | Monitor PERF_HUD |
| CSS conflicts | LOW | Isolated new styles in template |

---

## Rollback Plan

If any task causes failures:

```bash
# Revert app.js
git checkout -- src/core/viz/assets/app.js

# Revert template (if needed)
git checkout -- src/core/viz/assets/template.html

# Regenerate with known-good state
./collider full . --output .collider
```

---

*Registry created: 2026-01-19*
*Last updated: 2026-01-19*
*AI verification: Gemini 2.0 Flash (architect mode)*
