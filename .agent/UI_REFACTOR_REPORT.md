# UI REFACTOR REPORT - Collider v4 Sidebar

> Comprehensive analysis of current UI issues, architecture understanding, and implementation path.
> Generated: 2026-01-18

---

## 1. EXECUTIVE SUMMARY

### 1.1 Current State
The Collider v4 sidebar UI has **critical usability issues** that make it nearly unusable for new users (rated 2/10 by product owner). The core problems are:

1. **Inverted mental model** - Clicking filters EXCLUDES items (strike-through) instead of ISOLATING them
2. **Visual chaos** - Multiple inconsistent component styles (neon sliders, emoji icons, boxed tiles)
3. **Information overload** - TOPOLOGY section dominates 50%+ of sidebar with jargon labels
4. **Performance issues** - Layout switching causes freezes/hangs

### 1.2 Goal
Transform the sidebar to match the clean, minimal style of the top panels (COLLIDER v4.0.0, NODES/EDGES/ENTROPY, System Metrics) using a "less than minimal" design philosophy:
- No borders → use empty space
- No boxes → use alignment and typography
- Soft gradients → not hard fills
- Information through positioning → not decoration

### 1.3 Session Progress
| Item | Status |
|------|--------|
| Preset buttons (Tier, Family, etc.) not working | ✅ FIXED |
| Edges missing on Spectrum/Infrared | ✅ FIXED |
| Panel overlap (top-left + sidebar) | ✅ FIXED |
| Sidebar styling partially unified | ✅ DONE |
| Emoji icons removed from layout buttons | ✅ FIXED |
| Emoji icons removed from preset buttons | ✅ FIXED |
| TOPOLOGY section collapsed by default | ✅ FIXED |
| CSS token audit | ✅ DONE |
| Filter logic inverted | ❌ PENDING (architecture understood) |
| Layout performance | ❌ PENDING |
| Neon sliders | ❌ PENDING |

---

## 2. ARCHITECTURE UNDERSTANDING

### 2.1 File Structure

```
src/core/viz/assets/
├── template.html      # HTML structure, component containers
├── styles.css         # All CSS (2400+ lines)
├── app.js             # All JS logic (8500+ lines)
└── vendor/
    └── 3d-force-graph.min.js

schema/viz/tokens/
├── theme.tokens.json   # Colors, typography, shadows
├── layout.tokens.json  # Spacing, radius, z-index, sizes
├── appearance.tokens.json  # Graph visuals (nodes, edges)
└── controls.tokens.json    # UI controls config
```

### 2.2 Token System

Tokens are defined in JSON, resolved by `token_resolver.py`, and injected as CSS custom properties.

**Naming convention:**
```
theme.tokens.json    → --color-bg-*, --color-text-*, --color-border-*, --shadow-*, --typography-*
layout.tokens.json   → --spacing-*, --radius-*, --z-index-*, --size-*, --blur-*, --offset-*
```

**Key tokens for sidebar:**
```css
--color-bg-elevated      /* Panel background */
--color-bg-panel-dark    /* Darker panel variant */
--color-border-strong    /* Visible borders */
--color-border-subtle    /* Faint dividers */
--color-text-primary     /* Bright text */
--color-text-secondary   /* Dimmer text */
--color-text-muted       /* Subtle text */
--spacing-1 to --spacing-12  /* 3px to 32px */
--radius-sm              /* 3px */
--radius-md              /* 6px */
--size-panel-width-md    /* 280px */
--size-row-height-md     /* 28px */
```

### 2.3 Sidebar Component Hierarchy

```
.side-dock                          # Outer container (position, width)
├── .side-handle-row                # Toggle + Lock buttons
│   ├── .side-handle                # "TOPOLOGY" toggle button
│   └── .side-lock                  # Lock icon button
└── .side-content                   # Collapsible panel content
    └── .side-section               # Repeating section container
        ├── .side-title             # Section header (collapsible)
        └── .collapsible-content    # Section body
            ├── .preset-grid        # Tier/Family/Layer/Ring/File/Flow buttons
            ├── .color-scheme-grid  # OKLCH skin buttons
            ├── .layout-grid        # Layout preset buttons
            ├── .topo-legend        # Filter legend items
            ├── .filter-row         # Chip-based filters
            └── [sliders]           # Appearance controls
```

### 2.4 Filter System Architecture

**State:**
```javascript
let VIS_FILTERS = {
    tiers: new Set(),       // T0, T1, T2
    rings: new Set(),       // DOMAIN, APPLICATION, etc.
    roles: new Set(),       // Not used?
    edges: new Set(),       // Edge types
    families: new Set(),    // LOG, DAT, ORG, EXE, EXT
    files: new Set(),       // File paths
    layers: new Set(),      // D2_LAYER values
    effects: new Set(),     // D6_EFFECT values
    edgeFamilies: new Set(), // Structural, Dependency, etc.
    metadata: { ... }       // Boolean toggles
};
```

**Current mental model (INVERTED - NOW FULLY UNDERSTOOD):**
- Empty Set = Show ALL items of that dimension
- Item in Set = INCLUDE that item (visible)
- Click legend item → Removes from Set → Hide it (strike-through)

**The actual logic (app.js lines 3030-3038):**
```javascript
visibleNodes = visibleNodes.filter(n => {
    if (tierFilterActive && !tierFilter.has(getNodeTier(n))) return false;
    if (ringFilterActive && !ringFilter.has(getNodeRing(n))) return false;
    // ... etc
    return true;
});
```
**Key insight:** Items IN the set are KEPT. So it's an INCLUSION filter. The click handler REMOVES items from the set when clicked.

**toggleTopoFilter() logic (app.js lines 5248-5254):**
```javascript
if (filterSet.has(value)) {
    filterSet.delete(value);       // Remove from set
    element.classList.add('filtered');  // Show strike-through (hidden)
} else {
    filterSet.add(value);          // Add to set
    element.classList.remove('filtered'); // Remove strike-through (visible)
}
```

**Desired mental model:**
- Empty Set = Show ALL items (same)
- Click legend item → Show ONLY that item (isolate)
- Shift+Click → Add to selection
- Click again → Back to ALL

**To fix:** Change click to CLEAR set, then ADD clicked item (isolate mode)

**Key functions:**
```javascript
filterGraph()           // Main filter application (lines 2960-3074)
toggleTopoFilter()      // Toggle click handler (lines 5234-5261)
toggleEdgeFilter()      // Edge toggle (lines 5263-5272)
clearAllFilters()       // Reset all Sets (lines 5278-5304)
createTopoLegendItem()  // Creates legend items (lines 5194-5232)
```

**Legend item click handler:** `toggleTopoFilter()` at line 5234 (called via `item.onclick` at line 5210)

### 2.5 Layout System Architecture

**State:**
```javascript
const LAYOUT_PRESETS = {
    force: { ... },
    orbital: { ... },
    radial: { ... },
    spiral: { ... },
    sphere: { ... },
    torus: { ... },
    grid: { ... },
    cylinder: { ... },
    tree: { ... },
    flock: { ... },
    galaxy: { ... }
};
let CURRENT_LAYOUT = 'force';
let LAYOUT_FROZEN = false;
```

**Key functions:**
```javascript
applyLayoutPreset(key, animate)  // Apply layout
freezeLayout()                    // Stop simulation
unfreezeLayout()                  // Resume simulation
saveNodePositions()               // Cache positions
```

**Performance issue:** Some layouts trigger expensive recalculations or don't properly stop the previous simulation.

### 2.6 Slider System

**Builder function:** `buildAppearanceSliders()` at ~line 6200

**Slider HTML structure:**
```html
<div class="slider-row">
    <label class="slider-label">NODE SCALE</label>
    <input type="range" class="slider" id="node-scale" min="0.1" max="3" step="0.1" value="1">
    <span class="slider-value">1.00</span>
</div>
```

**CSS locations discovered:**
| Selector | Line | Style Type |
|----------|------|------------|
| `.density-slider` | 169 | Old density slider |
| `.filter-slider` | 1423-1462 | Entropy, cluster, file count |
| `.oklch-sliders`, `.oklch-range*` | 2212-2248 | **NEON** - colorful gradients |
| `.slider-row` | 2649-2683 | Newer unified style |
| `.slider-row.meta-amplifier` | 2686-2731 | Special "power" control |

**The neon slider issue (lines 2243-2248):**
```css
.oklch-range-l { background: linear-gradient(90deg, #000, #fff); }
.oklch-range-c { background: linear-gradient(90deg, #888, oklch(70% 0.4 220)); }
.oklch-range-h { background: linear-gradient(90deg,
    oklch(70% 0.15 0), oklch(70% 0.15 60), oklch(70% 0.15 120),
    oklch(70% 0.15 180), oklch(70% 0.15 240), oklch(70% 0.15 300), oklch(70% 0.15 360)); }
```
These rainbow/colorful sliders are for OKLCH color controls - arguably they SHOULD be colorful since they represent color values. But they stand out from the clean panel style.

---

## 3. CURRENT ISSUES - DETAILED

### 3.1 Filter Logic Inverted

**Symptom:**
- All legend items appear with strike-through and gray color
- Looks like everything is disabled/broken
- Users think "nothing works"

**Root cause:**
The filter system was designed for "exclusion" mode where you click to HIDE things. But this is counter-intuitive.

**Code location:**
```javascript
// app.js ~line 5080 (approximate)
legendItem.addEventListener('click', () => {
    const value = legendItem.dataset.value;
    if (filterSet.has(value)) {
        filterSet.delete(value);
        legendItem.classList.remove('filtered');
    } else {
        filterSet.add(value);
        legendItem.classList.add('filtered');
    }
    filterGraph();
});
```

**CSS for filtered state:**
```css
/* styles.css ~line 1115 */
.topo-legend-item.filtered {
    opacity: var(--opacity-disabled);
    text-decoration: line-through;
}
```

**What needs to change:**
1. Invert the logic: click = isolate (show only this)
2. Change visual states: selected = bright, unselected = subtle (not struck-through)
3. Add shift+click for multi-select
4. Add "show all" reset behavior

**Risk:**
- Touches multiple components
- May break existing state/URL persistence
- Must update ALL filter dimensions consistently

### 3.2 Layout Performance

**Symptom:**
- Clicking some layouts causes UI to freeze
- Nodes don't move to new positions
- Console shows no errors

**Suspected causes:**
1. Previous simulation not properly stopped
2. Layout calculation running on main thread
3. `LAYOUT_FROZEN` state not handled correctly
4. Large node count (923 nodes) + expensive force calculations

**Code location:**
```javascript
// app.js ~line 4200-4400 (LAYOUT_PRESETS)
// app.js ~line 6500-6560 (layout button handlers)
function applyLayoutPreset(key, animate) { ... }
```

**What I don't know:**
- Exact interaction between `freezeLayout()` and layout application
- Whether 3d-force-graph has known issues with layout switching
- If warmup/cooldown ticks are configured correctly

### 3.3 Neon Sliders

**Symptom:**
- Sliders have bright cyan/teal glow
- Doesn't match the clean, muted top panels

**Code location:**
```css
/* styles.css - search for input[type="range"] */
/* Likely around lines 1400-1500 */
```

**What needs to change:**
- Remove glow/shadow effects
- Use muted colors from token system
- Match the subtle style of other controls

### 3.4 Emoji Icons in Layout Buttons

**Symptom:**
- Layout buttons show emoji (🌀, 🔮, etc.)
- Inconsistent with text-based presets

**Code location:**
```html
<!-- template.html ~line 280-320 -->
<div class="layout-btn" data-layout="force">
    <span class="layout-icon">🌀</span>
    <span class="layout-name">FORCE</span>
</div>
```

**Fix:**
- Remove emoji or replace with simple text/symbols
- Or hide `.layout-icon` with CSS

### 3.5 TOPOLOGY Section Size

**Symptom:**
- TOPOLOGY section takes 50%+ of sidebar
- Contains: Tiers, Rings, Edges, Layers, Effects, Edge Families
- Too much information for first-time users

**What needs to change:**
1. Collapse TOPOLOGY by default
2. Or split into multiple smaller sections
3. Or hide advanced filters behind "Advanced..." expander

---

## 4. GAPS IN KNOWLEDGE

### 4.1 Must Investigate Before Fixing

| Gap | Why It Matters | How to Investigate |
|-----|----------------|-------------------|
| Filter click handler exact location | Need to modify logic | Grep for `legendItem.*click` or `filtered.*toggle` |
| How `filterGraph()` uses VIS_FILTERS | Understand exclusion vs inclusion | Read filterGraph() implementation |
| Whether filters persist to URL/storage | Don't break persistence | Search for `localStorage`, `URLSearchParams` |
| Layout preset application flow | Fix performance | Trace `applyLayoutPreset()` calls |
| Slider CSS location | Style consistently | Grep for `input\[type="range"\]` |
| Which components I touched today | Assess legacy risk | Git diff of styles.css |

### 4.2 Questions for Product Owner

1. Should filters persist across page refresh?
2. Is multi-select (shift+click) required or nice-to-have?
3. Should "show all" be explicit button or automatic on double-click?
4. Which TOPOLOGY subsections are essential vs. advanced?
5. Preferred visual for "selected" state: bright text, underline, or dot indicator?

---

## 5. CHANGES MADE THIS SESSION

### 5.1 Files Modified

| File | Changes |
|------|---------|
| `schema/viz/tokens/layout.tokens.json` | Added: `size.row-height`, `size.scrollbar`, `blur.*`, `offset.*` |
| `schema/viz/tokens/theme.tokens.json` | Added: `color.bg.scrollbar-*` |
| `src/core/viz/assets/styles.css` | Modified: `.side-dock` (tokenized), `.side-content`, `.side-handle*`, `.side-title`, `.preset-grid`, `.preset-btn` (simplified), `.layout-grid`, `.layout-btn` (simplified) |
| `src/core/viz/assets/template.html` | Removed emojis from layout buttons, removed emojis from preset buttons, made TOPOLOGY collapsible and collapsed by default |
| `src/core/viz/assets/app.js` | Added: preset button click handlers, `refreshGradientEdgeColors()` calls |

### 5.2 Specific Changes (Phase 2)

**Layout buttons (template.html lines 282-294):**
```html
<!-- BEFORE -->
<div class="layout-btn" data-layout="force">
    <span class="layout-icon">🌀</span>
    <span class="layout-name">Force</span>
</div>

<!-- AFTER -->
<div class="layout-btn active" data-layout="force" title="Physics-based clustering">Force</div>
```

**Preset buttons (template.html lines 215-222):**
```html
<!-- BEFORE -->
<div class="preset-btn" data-preset="tier">
    <span class="preset-icon">◐</span>
    <span class="preset-name">Tier</span>
</div>

<!-- AFTER -->
<div class="preset-btn active" data-preset="tier" title="Core → Architecture → External">Tier</div>
```

**TOPOLOGY section (template.html lines 143-147):**
```html
<!-- BEFORE -->
<div class="side-title">TOPOLOGY</div>
<div class="topo-map-container">

<!-- AFTER -->
<div class="side-title collapsible" data-target="topo-content">
    <span class="collapse-icon">▶</span> TOPOLOGY
</div>
<div class="collapsible-content collapsed" id="topo-content">
<div class="topo-map-container">
```

**CSS tokenization (styles.css lines 472-477):**
```css
/* BEFORE */
top: 20px;
left: 320px;
max-height: calc(100vh - 60px);

/* AFTER */
top: var(--offset-panel-margin);
left: calc(var(--size-panel-width-md) + var(--offset-panel-margin) * 2);
max-height: calc(100vh - var(--offset-panel-margin) * 3);
```

### 5.3 Legacy Issues Resolved

| Previous Issue | Status |
|----------------|--------|
| `left: 320px` hardcoded | ✅ Fixed - now uses calc with tokens |
| Mixed token/hardcoded values | ✅ Audited and fixed |
| Emoji icons inconsistent | ✅ Fixed - all buttons now text-only |
| TOPOLOGY section too prominent | ✅ Fixed - collapsed by default |

### 5.4 Git Diff Summary

```bash
# To see exact changes:
git diff src/core/viz/assets/styles.css
git diff src/core/viz/assets/template.html
git diff src/core/viz/assets/app.js
git diff schema/viz/tokens/
```

---

## 6. IMPLEMENTATION PLAN

### Phase 1: Safe Fixes ✅ COMPLETE

| Task | Status |
|------|--------|
| Remove emoji from layout buttons | ✅ Done |
| Remove emoji from preset buttons | ✅ Done |
| Collapse TOPOLOGY by default | ✅ Done |
| Audit and fix token consistency | ✅ Done |

### Phase 2: Investigation ✅ PARTIALLY COMPLETE

| Task | Status |
|------|--------|
| Map filter click handler flow | ✅ Done - `toggleTopoFilter()` at line 5234 |
| Understand filterGraph() | ✅ Done - lines 2960-3074 |
| Locate slider CSS | ✅ Done - 5 different slider styles found |
| Profile layout performance | ❌ Pending |

### Phase 3: Medium Fixes (Ready to implement)

| Task | Confidence | Notes |
|------|------------|-------|
| Fix slider styling | 70% | Now know all locations; OKLCH sliders may need special treatment |
| Human-readable labels | 65% | Need to trace label sources in app.js |

### Phase 4: Complex Fixes (Architecture now understood)

| Task | Confidence | Notes |
|------|------------|-------|
| Invert filter logic | 65% ↑ | Now understand exactly what to change in `toggleTopoFilter()` |
| Fix layout performance | 35% | Still need to profile |

---

## 7. CODE REFERENCES

### 7.1 Key Locations in app.js (VERIFIED)

| Function/Section | Line | Purpose |
|-----------------|------|---------|
| `VIS_FILTERS` | 133-149 | Filter state object |
| `filterGraph()` | 2960-3074 | Apply filters to graph (verified) |
| `refreshGraph()` | 3659-3749 | Refresh graph with filters |
| `LAYOUT_PRESETS` | 4211-4306 | Layout configurations (verified) |
| `createTopoLegendItem()` | 5194-5232 | Create legend items (verified) |
| `toggleTopoFilter()` | 5234-5261 | **FILTER CLICK HANDLER** (verified) |
| `toggleEdgeFilter()` | 5263-5272 | Edge toggle handler |
| `clearAllFilters()` | 5278-5304 | Reset filter state (verified) |
| Preset button handlers | 6390-6440 | Added this session |
| Color scheme handlers | 6440-6545 | OKLCH skin application |
| Layout button handlers | 6550-6568 | Layout switching (verified) |

### 7.2 Key Locations in styles.css (VERIFIED)

| Selector | Line | Purpose |
|----------|------|---------|
| `.hud-panel` | 36-46 | Clean panel style (TARGET) |
| `.side-dock` | 472-481 | Sidebar container (tokenized) |
| `.side-content` | 508-519 | Sidebar panel (tokenized) |
| `.side-title` | 580-618 | Section headers |
| `.preset-grid`, `.preset-btn` | 702-729 | Preset buttons (simplified) |
| `.layout-grid`, `.layout-btn` | 928-953 | Layout buttons (simplified) |
| `.topo-legend-item` | 1096-1140 | Legend items |
| `.topo-legend-item.filtered` | 1115-1121 | Filtered state |
| `.filter-slider` | 1423-1462 | Entropy/cluster sliders |
| `.oklch-sliders`, `.oklch-range*` | 2212-2248 | **NEON** sliders |
| `.slider-row` | 2649-2683 | Unified slider style |
| `.slider-row.meta-amplifier` | 2686-2731 | "Power" control |

### 7.3 Key Locations in template.html

| Element | Line (approx) | Purpose |
|---------|---------------|---------|
| `#dock-presets` | 209 | Presets section |
| `#preset-grid` | 211 | Preset buttons container |
| `#dock-schemes` | 239 | Color scheme buttons |
| `#layout-grid` | 280 | Layout buttons container |
| `#topo-tiers` | 150 | Tiers legend |
| `#topo-rings` | 155 | Rings legend |
| `#topo-edges` | 160 | Edges legend |
| `#topo-layers` | 173 | Layers legend (D2) |
| `#topo-effects` | 175 | Effects legend (D6) |
| `#topo-edge-families` | 177 | Edge families legend |

---

## 8. NEXT STEPS

### ✅ Completed
1. [x] Remove emoji from layout buttons
2. [x] Remove emoji from preset buttons
3. [x] Add `collapsed` class to TOPOLOGY section
4. [x] Audit today's CSS changes for token consistency
5. [x] Read `filterGraph()` implementation fully
6. [x] Trace legend item click handler
7. [x] Find slider CSS and understand structure

### Remaining Investigation
8. [ ] Profile layout switching performance

### Ready to Implement
9. [ ] Fix slider styling to match clean panels (know where all sliders are)
10. [ ] Implement filter logic inversion (know exactly what to change)
    - Modify `toggleTopoFilter()` at line 5234
    - Change: clear set, then add clicked item (isolate mode)
    - Add shift+click for multi-select

### Lower Priority
11. [ ] Fix layout performance (need investigation first)
12. [ ] Human-readable labels (T0→Core, etc.)

---

## 9. APPENDIX

### A. Token System Quick Reference

```css
/* Colors */
--color-bg-base          /* Near black */
--color-bg-surface       /* Panel bg */
--color-bg-elevated      /* Elevated panel */
--color-bg-hover         /* Hover state */
--color-bg-active        /* Active state */
--color-text-primary     /* White */
--color-text-secondary   /* 70% white */
--color-text-muted       /* 40% white */
--color-border-subtle    /* 4% white */
--color-border-strong    /* 15% white */

/* Spacing (px) */
--spacing-1: 3    --spacing-2: 5    --spacing-3: 8
--spacing-4: 10   --spacing-5: 12   --spacing-6: 14
--spacing-7: 16   --spacing-8: 20   --spacing-10: 24

/* Sizes */
--size-panel-width-sm: 200px
--size-panel-width-md: 280px
--size-row-height-sm: 24px
--size-row-height-md: 28px
--size-row-height-lg: 32px

/* Radius */
--radius-sm: 3px
--radius-md: 6px
--radius-lg: 8px
```

### B. Design Philosophy Reference

**"Less than minimal" principles:**
1. Remove borders → use alignment and empty space
2. Remove boxes → use typography hierarchy
3. Soft gradients → not hard fills
4. Information through positioning → not decoration
5. Single component style → consistency across all panels
6. Text-based controls → no icons unless essential

### C. Related Documentation

- `.agent/SET_MAPPING_IMPLEMENTATION.md` - Previous implementation guide
- `CLAUDE.md` - Project instructions
- `schema/viz/tokens/*.json` - Token definitions
