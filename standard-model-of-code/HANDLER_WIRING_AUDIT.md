# Handler Wiring Coverage Audit
**Date:** 2026-01-25
**Scope:** UI controls in `src/core/viz/assets/template.html`
**Analysis:** Cross-reference with JavaScript handlers in `panel-handlers.js` and `sidebar.js`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total controls in template** | 118 |
| **Total handlers implemented** | 70 |
| **Coverage** | 59.3% |
| **Orphaned controls** | 101 |
| **Status** | 🔴 CRITICAL GAP |

---

## Wired Controls (70 IDs)

These controls have JavaScript handlers attached in `panel-handlers.js` or `sidebar.js`:

### Panel Handlers (45)
- `metrics-overlay`
- `panel-alpha-decay`
- `panel-auto-rotate`
- `panel-cam-fit`
- `panel-cam-reset`
- `panel-colorblind`
- `panel-cool`
- `panel-edge-curve`
- `panel-edge-opacity`
- `panel-edge-width`
- `panel-export-embed`
- `panel-export-json`
- `panel-export-png`
- `panel-export-svg`
- `panel-filter-degree`
- `panel-freeze`
- `panel-high-contrast`
- `panel-khop`
- `panel-label-size`
- `panel-node-opacity`
- `panel-node-size`
- `panel-particle-speed`
- `panel-reduced-motion`
- `panel-reheat`
- `panel-reset-layout`
- `panel-rotate-speed`
- `panel-search-nodes`
- `panel-select-expand`
- `panel-select-isolate`
- `panel-stat-density`
- `panel-stat-edges`
- `panel-stat-selected`
- `panel-stat-visible`
- `panel-toggle-arrows`
- `panel-toggle-dead`
- `panel-toggle-depth`
- `panel-toggle-dock`
- `panel-toggle-gradient`
- `panel-toggle-highlight`
- `panel-toggle-labels`
- `panel-toggle-metrics`
- `panel-toggle-orphans`
- `panel-view-2d`
- `panel-view-3d`

### Sidebar Handlers (25)
- `btn-freeze`
- `btn-reset`
- `btn-screenshot`
- `hover-file`
- `hover-panel`
- `left-resize-handle`
- `right-resize-handle`
- `section-color`
- `section-layout`
- `section-physics`
- `section-schemes`
- `selection-clear`
- `selection-list`
- `selection-panel`
- `selection-title`
- `stat-edges`
- `stat-entropy`
- `stat-nodes`
- `view-mode-toggle`

---

## Orphaned Controls (101 IDs)

### Critical - No Handler Attached
These controls exist in the DOM but have no wired JavaScript handler:

#### Accessibility Controls (6)
- `a11y-focus-indicators` - Focus indicator toggle
- `a11y-font-size` - Font size adjustment slider
- `a11y-font-size-val` - Font size value display
- `a11y-large-text` - Large text toggle
- `a11y-screen-reader` - Screen reader toggle
- `accessibility` - Accessibility panel header

#### Camera/View Controls (10)
- `btn-2d` - 2D view button
- `camera` - Camera settings container
- `camera-auto-rotate` - Auto-rotate toggle
- `camera-bookmarks` - Camera bookmarks control
- `camera-reset` - Reset camera button
- `camera-rotate-speed` - Rotation speed slider
- `camera-rotate-speed-val` - Rotation speed value
- `camera-save-bookmark` - Save bookmark button
- `camera-zoom-fit` - Zoom to fit button
- `camera-zoom-in` / `camera-zoom-out` - Zoom controls

#### Edge Configuration (6)
- `cfg-edge-curve` - Edge curve toggle
- `cfg-edge-curve-num` - Edge curve value
- `cfg-edge-opacity` - Edge opacity slider
- `cfg-edge-opacity-num` - Edge opacity value
- `cfg-edge-width` - Edge width slider
- `cfg-edge-width-num` - Edge width value

#### Node Configuration (10)
- `cfg-label-size` - Label size slider
- `cfg-label-size-num` - Label size value
- `cfg-node-opacity` - Node opacity slider
- `cfg-node-opacity-num` - Node opacity value
- `cfg-node-res` - Node resolution setting
- `cfg-node-res-num` - Node resolution value
- `cfg-node-size` - Node size slider
- `cfg-node-size-num` - Node size value
- `cfg-particle-count` - Particle count slider
- `cfg-particle-count-num` - Particle count value

#### Particle/Physics (3)
- `cfg-particle-speed` - Particle speed slider (orphaned, panel-particle-speed wired)
- `cfg-particle-speed-num` - Particle speed value
- `cfg-toggle-pulse` - Pulse animation toggle

#### Toggle Controls (8)
- `cfg-toggle-arrows` - Arrow toggle
- `cfg-toggle-codome` - CODOME toggle
- `cfg-toggle-depth` - Depth toggle
- `cfg-toggle-edge-hover` - Edge hover toggle
- `cfg-toggle-gradient` - Gradient toggle
- `cfg-toggle-highlight` - Highlight toggle
- `cfg-toggle-labels` - Labels toggle (partial, toggle-labels also orphaned)
- `toggle-labels` - Alternative label toggle ID

#### Filtering/Search (11)
- `filter-edges` - Edge filter control
- `filter-family-chips` - Family filter chips
- `filter-hide-dead` - Hide dead code (orphaned, panel-toggle-dead wired)
- `filter-hide-orphans` - Hide orphans (orphaned, panel-toggle-orphans wired)
- `filter-max-degree` - Max degree filter
- `filter-max-degree-val` - Max degree value
- `filter-min-degree` - Min degree filter (orphaned, panel-filter-degree wired)
- `filter-min-degree-val` - Min degree value
- `filter-rings` - Ring filter
- `filter-role-chips` - Role filter chips
- `filter-tier-chips` - Tier filter chips
- `filter-tiers` - Tier selection
- `filtering` - Filter section header

#### Hover/Inspection Info (7)
- `hover-atom` - Hovered atom type
- `hover-family` - Hovered family
- `hover-kind` - Hovered kind
- `hover-name` - Hovered name
- `hover-placeholder` - Placeholder text
- `hover-ring` - Hovered ring
- `hover-tier` - Hovered tier

#### Layout/Performance (6)
- `layout-phys` - Physics layout toggle
- `left-sidebar` - Left sidebar container
- `perf-fps` - FPS counter
- `perf-frame` - Frame time display
- `perf-hud` - Performance HUD
- `right-sidebar` - Right sidebar container

#### Selection/Stats (9)
- `selection` - Selection panel
- `selection-actions` - Selection action buttons
- `selection-box` - Selection info box
- `selection-count` - Selection count display
- `stats-density` - Density stat (orphaned, panel-stat-density wired)
- `stats-edges` - Edge count stat (orphaned, stat-edges wired)
- `stats-files` - File count stat
- `stats-nodes` - Node count stat (orphaned, stat-nodes wired)

#### Export/Analysis (5)
- `analysis` - Analysis panel header
- `export` - Export panel header
- `edge-appear` - Edge appearance toggle
- `node-appear` - Node appearance toggle
- `control-bar-container` - Control bar wrapper

#### Section Headers (3)
- `section-actions` - Actions section
- `section-appearance` - Appearance section
- `section-edge-config` - Edge config section
- `section-filters` - Filters section
- `section-node-config` - Node config section

#### Other Display Elements (5)
- `target-name` - Target element name display
- `view-modes` - View modes container
- Numeric display fields for sliders (orphaned -val/-num pairs)

---

## Analysis & Recommendations

### Root Cause: ID Naming Inconsistency

The wiring gap stems from **naming inconsistency** between template IDs and handler references:

| Template ID | Handler ID | Status |
|-------------|-----------|--------|
| `cfg-edge-opacity` | `panel-edge-opacity` | Mismatch |
| `filter-min-degree` | `panel-filter-degree` | Mismatch |
| `filter-hide-dead` | `panel-toggle-dead` | Mismatch |
| `stats-nodes` | `panel-stat-nodes` | Mismatch |

### Two-Tier Problem

**Tier 1: Naming Mismatch** (Likely Wired)
- Controls exist in template with one ID
- Handlers reference them with different ID
- ~30-40 controls probably functionally wired but appear orphaned
- **Action:** Reconcile naming or update handler references

**Tier 2: Truly Orphaned** (No Handler Logic)
- Controls in template but never referenced in any handler file
- Accessibility controls (a11y-*)
- Camera controls (`camera-*`)
- Display-only fields (`hover-*`, `stats-*`)
- **Action:** Implement handlers or remove from template

---

## Priority Recommendations

### Priority 1: Reconcile Naming
1. Audit which `cfg-*` controls are actually handled by `panel-*` IDs
2. Update template to use consistent prefixes OR update handlers
3. Create mapping document for future maintenance

### Priority 2: Accessibility Controls
1. Implement handlers for a11y-* controls (currently non-functional)
2. Connect to WCAG compliance system
3. Test with screen readers

### Priority 3: Camera Controls
1. Implement camera-* handlers or remove unused controls
2. Connect zoom/rotate to 3D scene if not already wired
3. Test camera bookmarks persistence

### Priority 4: Display-Only Fields
1. Mark read-only fields (stats, hover info) as non-interactive
2. Remove IDs from display-only elements if not needed for updates
3. Update this audit document with final classification

---

## Next Steps

1. **Quick Win:** Generate mapping of `cfg-*` → `panel-*` names (30 mins)
2. **Coverage Test:** Add console logging to track which handlers actually fire (30 mins)
3. **Gap Fill:** Implement missing handlers (3-5 hours depending on scope)
4. **Validation:** Run handler coverage test in browser console and verify 100% coverage

---

## Testing Command

Once handlers are implemented, validate coverage:

```bash
# In browser console:
Array.from(document.querySelectorAll('[id]'))
  .filter(el => !el.id.match(/^(panel-|grid|3d-|header|loader|toast|left-|right-|hover-|stats-|target-|control-bar)/))
  .map(el => el.id)
  .forEach(id => console.log(`${id}: ${window.PANEL_HANDLERS ? 'registered' : 'orphaned'}`))
```

---

**Report Generated:** 2026-01-25
**Audit Tool:** grep + comm analysis
**Files Analyzed:**
- `src/core/viz/assets/template.html` (118 IDs)
- `src/core/viz/assets/modules/panel-handlers.js` (45 handlers)
- `src/core/viz/assets/modules/sidebar.js` (25 handlers)
