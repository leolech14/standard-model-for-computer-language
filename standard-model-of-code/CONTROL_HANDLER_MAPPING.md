# Control-Handler ID Mapping Reference
**Purpose:** Quick lookup for template control IDs and their corresponding handler bindings
**Generated:** 2026-01-25

---

## Legend
- ✅ **Wired**: Handler exists and is active
- ⚠️ **Mismatch**: Control exists but handler uses different ID
- ❌ **Orphaned**: No handler found
- 📝 **Display**: Read-only field (may not need handler)

---

## Wired Controls (Direct ID Match)

### Export Controls
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-export-json | Button | Yes | panel-handlers.js |
| ✅ panel-export-png | Button | Yes | panel-handlers.js |
| ✅ panel-export-svg | Button | Yes | panel-handlers.js |
| ✅ panel-export-embed | Button | Yes | panel-handlers.js |

### View Mode
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-view-2d | Button | Yes | panel-handlers.js |
| ✅ panel-view-3d | Button | Yes | panel-handlers.js |
| ✅ view-mode-toggle | Toggle | Yes | sidebar.js |

### Filter Controls
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-search-nodes | Input | Yes | panel-handlers.js |
| ✅ panel-toggle-orphans | Toggle | Yes | panel-handlers.js |
| ✅ panel-toggle-dead | Toggle | Yes | panel-handlers.js |
| ✅ panel-filter-degree | Slider | Yes | panel-handlers.js |

### Selection Controls
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-khop | Slider | Yes | panel-handlers.js |
| ✅ panel-select-expand | Button | Yes | panel-handlers.js |
| ✅ panel-select-isolate | Button | Yes | panel-handlers.js |
| ✅ selection-clear | Button | Yes | sidebar.js |
| ✅ selection-panel | Container | Yes | sidebar.js |
| ✅ selection-list | List | Yes | sidebar.js |

### Camera Controls (Panel)
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-cam-fit | Button | Yes | panel-handlers.js |
| ✅ panel-cam-reset | Button | Yes | panel-handlers.js |
| ✅ panel-auto-rotate | Toggle | Yes | panel-handlers.js |
| ✅ panel-rotate-speed | Slider | Yes | panel-handlers.js |

### Color Theme
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-cool | Toggle | Yes | panel-handlers.js |
| ✅ panel-reheat | Toggle | Yes | panel-handlers.js |
| ✅ panel-colorblind | Toggle | Yes | panel-handlers.js |
| ✅ panel-high-contrast | Toggle | Yes | panel-handlers.js |

### Accessibility
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-reduced-motion | Toggle | Yes | panel-handlers.js |

### Layout
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-reset-layout | Button | Yes | panel-handlers.js |
| ✅ panel-toggle-dock | Button | Yes | panel-handlers.js |
| ✅ panel-freeze | Button | Yes | panel-handlers.js |

### Statistics Display
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-stat-visible | Display | Yes | panel-handlers.js |
| ✅ panel-stat-selected | Display | Yes | panel-handlers.js |
| ✅ panel-stat-edges | Display | Yes | panel-handlers.js |
| ✅ panel-stat-density | Display | Yes | panel-handlers.js |

### Action Buttons
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ btn-freeze | Button | Yes | sidebar.js |
| ✅ btn-reset | Button | Yes | sidebar.js |
| ✅ btn-screenshot | Button | Yes | sidebar.js |

### Sidebar
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ section-color | Header | Yes | sidebar.js |
| ✅ section-layout | Header | Yes | sidebar.js |
| ✅ section-physics | Header | Yes | sidebar.js |
| ✅ section-schemes | Header | Yes | sidebar.js |
| ✅ left-resize-handle | Control | Yes | sidebar.js |
| ✅ right-resize-handle | Control | Yes | sidebar.js |

### Physics
| ID | Type | Handler | Module |
|----|------|---------|--------|
| ✅ panel-alpha-decay | Slider | Yes | panel-handlers.js |

---

## Naming Mismatch (Template ID ≠ Handler ID)

These controls ARE wired but use different IDs in template vs. handlers.

### cfg-* → panel-* (Configuration Controls)

| Template ID | Handler ID | Type | Status |
|-------------|-----------|------|--------|
| ⚠️ cfg-edge-curve | panel-edge-curve | Toggle | **MISMATCH** |
| ⚠️ cfg-edge-opacity | panel-edge-opacity | Slider | **MISMATCH** |
| ⚠️ cfg-edge-opacity-num | panel-edge-opacity-num | Input | **MISMATCH** |
| ⚠️ cfg-edge-width | panel-edge-width | Slider | **MISMATCH** |
| ⚠️ cfg-edge-width-num | panel-edge-width-num | Input | **MISMATCH** |
| ⚠️ cfg-label-size | panel-label-size | Slider | **MISMATCH** |
| ⚠️ cfg-label-size-num | panel-label-size-num | Input | **MISMATCH** |
| ⚠️ cfg-node-opacity | panel-node-opacity | Slider | **MISMATCH** |
| ⚠️ cfg-node-opacity-num | panel-node-opacity-num | Input | **MISMATCH** |
| ⚠️ cfg-node-size | panel-node-size | Slider | **MISMATCH** |
| ⚠️ cfg-node-size-num | panel-node-size-num | Input | **MISMATCH** |
| ⚠️ cfg-particle-speed | panel-particle-speed | Slider | **MISMATCH** |
| ⚠️ cfg-particle-speed-num | panel-particle-speed-num | Input | **MISMATCH** |
| ⚠️ cfg-toggle-arrows | panel-toggle-arrows | Toggle | **MISMATCH** |
| ⚠️ cfg-toggle-depth | panel-toggle-depth | Toggle | **MISMATCH** |
| ⚠️ cfg-toggle-gradient | panel-toggle-gradient | Toggle | **MISMATCH** |
| ⚠️ cfg-toggle-highlight | panel-toggle-highlight | Toggle | **MISMATCH** |
| ⚠️ cfg-toggle-labels | panel-toggle-labels | Toggle | **MISMATCH** |

### stats-* → panel-stat-* (Statistics)

| Template ID | Handler ID | Type | Status |
|-------------|-----------|------|--------|
| ⚠️ stats-density | panel-stat-density | Display | **MISMATCH** |
| ⚠️ stats-edges | panel-stat-edges | Display | **MISMATCH** |
| 📝 stats-nodes | panel-stat-nodes? | Display | **LIKELY MISMATCH** |

---

## Orphaned Controls (No Handler)

### Accessibility Features (6)
| ID | Type | Priority | Note |
|----|------|----------|------|
| ❌ a11y-focus-indicators | Toggle | HIGH | WCAG 2.1 requirement |
| ❌ a11y-font-size | Slider | HIGH | WCAG 2.1 requirement |
| ❌ a11y-font-size-val | Input | HIGH | WCAG 2.1 requirement |
| ❌ a11y-large-text | Toggle | HIGH | WCAG 2.1 requirement |
| ❌ a11y-screen-reader | Toggle | HIGH | WCAG 2.1 requirement |
| ❌ accessibility | Header | - | Section header |

### Camera Controls (10)
| ID | Type | Priority | Note |
|----|------|----------|------|
| ❌ btn-2d | Button | MEDIUM | 2D view button |
| ❌ camera | Header | - | Section header |
| ❌ camera-auto-rotate | Toggle | MEDIUM | Auto-rotate feature |
| ❌ camera-bookmarks | Control | MEDIUM | Save/load view states |
| ❌ camera-reset | Button | MEDIUM | Reset to default |
| ❌ camera-rotate-speed | Slider | MEDIUM | Rotation speed |
| ❌ camera-rotate-speed-val | Input | MEDIUM | Speed value display |
| ❌ camera-save-bookmark | Button | MEDIUM | Save current view |
| ❌ camera-zoom-fit | Button | MEDIUM | Fit to screen |
| ❌ camera-zoom-in | Button | MEDIUM | Zoom in |
| ❌ camera-zoom-out | Button | MEDIUM | Zoom out |

### Node Configuration (4)
| ID | Type | Priority | Note |
|----|------|----------|------|
| ❌ cfg-node-res | Slider | LOW | Node resolution/quality |
| ❌ cfg-node-res-num | Input | LOW | Resolution value |
| ❌ cfg-particle-count | Slider | LOW | Particle count |
| ❌ cfg-particle-count-num | Input | LOW | Count value |

### Toggle Controls (4)
| ID | Type | Priority | Note |
|----|------|----------|------|
| ❌ cfg-toggle-codome | Toggle | LOW | CODOME view |
| ❌ cfg-toggle-edge-hover | Toggle | LOW | Edge hover detection |
| ❌ cfg-toggle-pulse | Toggle | LOW | Pulse animation |
| ❌ toggle-labels | Toggle | MEDIUM | Label visibility (duplicate?) |

### Filtering (8)
| ID | Type | Priority | Note |
|----|------|----------|------|
| ❌ filter-edges | Checkbox | MEDIUM | Edge filtering |
| ❌ filter-family-chips | Container | MEDIUM | Family tag selection |
| ❌ filter-max-degree | Slider | MEDIUM | Maximum degree |
| ❌ filter-max-degree-val | Input | MEDIUM | Max degree value |
| ❌ filter-rings | Checkbox | MEDIUM | Ring filtering |
| ❌ filter-role-chips | Container | MEDIUM | Role tag selection |
| ❌ filter-tier-chips | Container | MEDIUM | Tier tag selection |
| ❌ filter-tiers | Selector | MEDIUM | Tier selection |

### Display/Read-Only (7)
| ID | Type | Priority | Note |
|----|------|----------|------|
| 📝 hover-atom | Display | - | Info display only |
| 📝 hover-family | Display | - | Info display only |
| 📝 hover-kind | Display | - | Info display only |
| 📝 hover-name | Display | - | Info display only |
| 📝 hover-placeholder | Display | - | Placeholder text |
| 📝 hover-ring | Display | - | Info display only |
| 📝 hover-tier | Display | - | Info display only |

### Layout (5)
| ID | Type | Priority | Note |
|----|------|----------|------|
| 📝 left-sidebar | Container | - | Layout container |
| 📝 right-sidebar | Container | - | Layout container |
| 📝 perf-fps | Display | - | Read-only FPS counter |
| 📝 perf-frame | Display | - | Read-only frame time |
| 📝 perf-hud | Container | - | Performance HUD |

### Selection/Stats (5)
| ID | Type | Priority | Note |
|----|------|----------|------|
| 📝 selection | Container | - | Selection panel |
| 📝 selection-actions | Container | - | Action buttons |
| 📝 selection-box | Container | - | Info box |
| 📝 selection-count | Display | - | Read-only count |
| 📝 stats-files | Display | - | Read-only file count |

### Layout/Analysis (6)
| ID | Type | Priority | Note |
|----|------|----------|------|
| ❌ analysis | Header | LOW | Analysis section |
| ❌ export | Header | LOW | Export section |
| ❌ layout-phys | Toggle | LOW | Physics layout toggle |
| ❌ control-bar-container | Container | - | Layout container |
| 📝 target-name | Display | - | Current target display |
| 📝 view-modes | Container | - | View mode buttons |

---

## Summary by Status

| Status | Count | Action |
|--------|-------|--------|
| ✅ Wired (direct ID) | 45 | Monitor, test |
| ⚠️ Wired (name mismatch) | 15 | Standardize naming |
| ❌ Orphaned (needs implementation) | 24 | Implement or remove |
| 📝 Display only (likely ok) | 19 | Document, may not need handler |
| **TOTAL** | **118** | - |

---

## Recommended Actions

### 1. Fix Naming Mismatches (2-3 hours)
**Option A:** Rename template IDs to use `panel-*` prefix
- Pros: Matches handler expectations
- Cons: Requires template HTML edit

**Option B:** Update handlers to reference `cfg-*`, `stats-*` prefixes
- Pros: Template stays as-is
- Cons: More handler file changes

**Recommendation:** Go with Option A (template rename) for consistency

### 2. Implement Accessibility Handlers (4-6 hours)
**Blockers:** WCAG 2.1 compliance
**Deps:** a11y-* controls are currently non-functional
**Files to edit:** `panel-handlers.js` + new accessibility module if needed

### 3. Implement/Remove Camera Controls (2-4 hours)
**Decision needed:** Are these features wanted?
- If yes: Implement camera-* handlers
- If no: Remove from template

### 4. Implement Advanced Filters (4-6 hours)
**Controls:** filter-*-chips controls
**Note:** May require new filtering infrastructure

### 5. Audit Display-Only Fields (1 hour)
**Question:** Do we actually need IDs on read-only display elements?
**Action:** Document which are intentional, remove unnecessary IDs

---

**Last Updated:** 2026-01-25
**Audit Tool:** grep + comm-based analysis
**Next Review:** After implementing Phase 1 fixes
