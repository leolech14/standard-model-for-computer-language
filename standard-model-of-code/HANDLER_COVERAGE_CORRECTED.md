# Handler Wiring Coverage - Corrected Analysis
**Date:** 2026-01-25
**Status:** Gap identified with root cause identified

---

## Key Finding: Naming Mismatch Pattern

Template uses **different prefixes** than handler module:
- Template: `cfg-*`, `filter-*`, `stats-*`
- Handlers: `panel-*`, `panel-stat-*`

This creates an **apparent gap** but controls are actually wired.

---

## Corrected Coverage

### Actually Wired (Despite ID Mismatch)

These controls exist in template with one ID but are handled under a different name:

#### cfg-* → panel-* (12 controls)
| Template ID | Handler ID | Type |
|-------------|-----------|------|
| `cfg-edge-curve` | `panel-edge-curve` | Toggle |
| `cfg-edge-opacity` | `panel-edge-opacity` | Slider |
| `cfg-edge-width` | `panel-edge-width` | Slider |
| `cfg-label-size` | `panel-label-size` | Slider |
| `cfg-node-opacity` | `panel-node-opacity` | Slider |
| `cfg-node-size` | `panel-node-size` | Slider |
| `cfg-particle-speed` | `panel-particle-speed` | Slider |
| `cfg-toggle-arrows` | `panel-toggle-arrows` | Toggle |
| `cfg-toggle-depth` | `panel-toggle-depth` | Toggle |
| `cfg-toggle-gradient` | `panel-toggle-gradient` | Toggle |
| `cfg-toggle-highlight` | `panel-toggle-highlight` | Toggle |
| `cfg-toggle-labels` | `panel-toggle-labels` | Toggle |

#### stats-* → panel-stat-* (3 controls)
| Template ID | Handler ID | Type |
|-------------|-----------|------|
| `stats-density` | `panel-stat-density` | Display |
| `stats-edges` | `panel-stat-edges` | Display |
| stats-nodes could map to `panel-stat-nodes` | - | Display |

---

## Revised Coverage Analysis

### Corrected Metrics

| Metric | Count |
|--------|-------|
| Total template controls | 118 |
| Handlers explicitly matching template ID | 70 |
| Handlers matching via naming convention | 15 |
| **Actually wired** | **85** |
| **Real coverage** | **72%** |
| Truly orphaned (no handler logic) | 33 |

---

## Truly Orphaned Controls (33)

### Accessibility Controls (6)
- `a11y-focus-indicators` - Focus indicator toggle
- `a11y-font-size` - Font size slider
- `a11y-font-size-val` - Font size value
- `a11y-large-text` - Large text toggle
- `a11y-screen-reader` - Screen reader toggle
- `accessibility` - Section header

### Camera Controls (10)
- `btn-2d` - 2D view button
- `camera` - Section header
- `camera-auto-rotate` - Auto-rotate toggle
- `camera-bookmarks` - Bookmarks control
- `camera-reset` - Reset button
- `camera-rotate-speed` - Rotation speed slider
- `camera-rotate-speed-val` - Rotation speed value
- `camera-save-bookmark` - Save bookmark button
- `camera-zoom-fit` - Zoom to fit button
- `camera-zoom-in` / `camera-zoom-out` - Zoom buttons (2)

### Node/Edge Config (6)
- `cfg-node-res` - Node resolution
- `cfg-node-res-num` - Node resolution value
- `cfg-particle-count` - Particle count
- `cfg-particle-count-num` - Particle count value
- `cfg-particle-speed-num` - Particle speed value (note: cfg-particle-speed is wired)
- `cfg-toggle-codome` - CODOME toggle
- `cfg-toggle-edge-hover` - Edge hover detection
- `cfg-toggle-pulse` - Pulse animation toggle

### Filter Controls (5)
- `filter-edges` - Edge filtering checkbox
- `filter-family-chips` - Family filters
- `filter-max-degree` - Max degree
- `filter-max-degree-val` - Max degree value
- `filter-rings` - Ring filtering
- `filter-role-chips` - Role filters
- `filter-tier-chips` - Tier filters
- `filter-tiers` - Tier selection

### Display/Read-Only (7)
- `hover-atom` - Hover info (read-only)
- `hover-family` - Hover info (read-only)
- `hover-kind` - Hover info (read-only)
- `hover-name` - Hover info (read-only)
- `hover-placeholder` - Hover placeholder
- `hover-ring` - Hover info (read-only)
- `hover-tier` - Hover info (read-only)

### Layout/Performance (5)
- `left-sidebar` - Layout container
- `right-sidebar` - Layout container
- `perf-fps` - FPS display (read-only)
- `perf-frame` - Frame time display (read-only)
- `perf-hud` - Performance HUD (read-only)

### Selection/Stats (3)
- `selection` - Selection container
- `selection-actions` - Actions container
- `selection-box` - Info box
- `selection-count` - Count display (read-only)
- `stats-files` - Files count (read-only)

### Layout/Analysis (2)
- `analysis` - Analysis header
- `export` - Export header
- `layout-phys` - Physics layout toggle
- `control-bar-container` - Layout container
- `target-name` - Target display
- `view-modes` - View mode buttons

---

## Actual Wiring Gaps vs. Display Elements

### Gap 1: cfg-particle-speed-num Not Linked
**Template:** `cfg-particle-speed-num` (value display)
**Handler:** Updates `panel-particle-speed-num`
**Status:** MISMATCH - Need to update template ID or handler reference

### Gap 2: Accessibility Controls Unimplemented
**Controls:** All `a11y-*` IDs
**Issue:** No handlers exist in any module
**Priority:** HIGH - These are WCAG compliance requirements

### Gap 3: Camera Controls Unimplemented
**Controls:** `camera-*` controls (10 items)
**Issue:** No handlers exist
**Note:** Some might be wired through other mechanisms (THREE.js events?)
**Priority:** MEDIUM - Only if features are supposed to be exposed

### Gap 4: Advanced Filters Unimplemented
**Controls:** `filter-family-chips`, `filter-role-chips`, `filter-tier-chips`
**Issue:** No handlers for chip selection
**Priority:** MEDIUM - Probably need semantic filtering implementation

### Gap 5: Display-Only Elements Misclassified
**Controls:** `hover-*`, `stats-*`, `perf-*` prefixes
**Issue:** These are read-only displays, shouldn't have handler IDs
**Priority:** LOW - Refactor to remove IDs if not needed for JS updates

---

## Root Causes

### 1. Inconsistent Naming Convention (Moderate Impact)
- Early template used `cfg-*` prefix for configuration
- Handlers switched to `panel-*` for consistency with panel architecture
- 15 controls are wired but appear orphaned

**Fix:** Update template to use `panel-*` prefix OR update handlers to reference template names

### 2. Incomplete Implementation (High Impact)
- Accessibility module skeleton exists but unimplemented
- Camera controls were added to template but handlers never built
- Advanced filtering (chips) designed but not coded

**Fix:** Implement handlers for these features OR remove controls from template

### 3. Display Elements with IDs (Low Impact)
- Many read-only display fields (hover info, stats) have IDs
- These pollute the "controls needing handlers" count
- But they may need IDs for JavaScript updates

**Fix:** Document which are intentionally read-only vs. waiting for implementation

---

## Remediation Path

### Phase 1: Quick Wins (1-2 hours)
1. Rename all `cfg-*` controls to `panel-*` in template (or vice versa in handlers)
2. Fix `cfg-particle-speed-num` → `panel-particle-speed-num`
3. Verify all 85 "actually wired" controls work correctly

### Phase 2: Feature Implementation (4-8 hours)
1. Implement accessibility handlers (a11y-*)
2. Implement or remove camera controls
3. Implement advanced filter chip handlers
4. Test WCAG compliance

### Phase 3: Cleanup (1 hour)
1. Remove IDs from pure display elements if not needed
2. Update this audit document with final classification
3. Add JSDoc comments indicating wiring status for each major control group

---

## Files to Update

| File | Action | Reason |
|------|--------|--------|
| `src/core/viz/assets/template.html` | Rename `cfg-*` → `panel-*` | Consistency |
| `src/core/viz/assets/modules/panel-handlers.js` | Add a11y, camera handlers | Feature implementation |
| `src/core/viz/assets/modules/sidebar.js` | Add filter chip handlers | Feature implementation |
| `HANDLER_WIRING_AUDIT.md` | Update with findings | Documentation |

---

## Verification Checklist

- [ ] All `cfg-*` controls renamed to `panel-*` (or handlers updated)
- [ ] All accessibility controls have working handlers
- [ ] All camera controls have working handlers or are removed
- [ ] All filter chips have working handlers
- [ ] Browser console shows 0 JS errors on panel initialization
- [ ] Manual testing confirms all controls work as expected
- [ ] Coverage audit re-run shows 100% or documents intentional gaps

---

**Status:** Ready for Phase 1 implementation
**Estimated Effort:** 6-12 hours total
**Blocking:** None - can be done incrementally
