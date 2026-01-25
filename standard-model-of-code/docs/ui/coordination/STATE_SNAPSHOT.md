# UI Overhaul State Snapshot

**Generated:** 2026-01-25 07:10:00
**For:** ChatGPT 5.2 Pro Extended Thinking (Orchestrator)
**Agents:** Claude Opus 4.5 x2 (CLI)
**State Version:** 3

---

## EXECUTIVE SUMMARY

The UI Overhaul is in **Late Phase 2** - Wave A (Fix Broken Controls) **COMPLETE**. Transitioning from monolithic architecture to modular, token-based system.

### Key Metrics

| Metric | Value | Target | Gap |
|--------|-------|--------|-----|
| Controls identified | 33 | 82 | 49 |
| Controls wired | **27 (81.8%)** | 100% | 18.2% |
| Pixel sovereignty | **~92%** | 95% | ~3% |
| JS modules | 54 | - | - |
| Total JS lines | 21,626 | - | - |

---

## PHASE STATUS

```
Phase 1: Corpus Bootstrap     [PARTIAL] - missing baseline HTML
Phase 2: Knowledge Gap Fill   [IN_PROGRESS] - 3/5 artifacts complete
Phase 3: 9-Region Map         [PENDING]
Phase 4: UI Scoring           [PENDING]
Phase 5: Task Registry        [PENDING]
Phase 6: Implementation       [BLOCKED] - needs style specs
```

---

## VALIDATED ARTIFACTS

### Complete (via analyze.py + Gemini)

| Artifact | Path | Key Findings |
|----------|------|--------------|
| `dom_controls.json` | `corpus/v1/extracted/` | 33 controls: **27 wired**, 5 orphaned, **0 dead** |
| `bindings.json` | `corpus/v1/extracted/` | 7 state objects, 4 binding locations |
| `bypass_report.md` | `corpus/v1/analysis/` | 4 bypass categories, 5 conflicts |
| `manifest.json` | `corpus/v1/` | v1.1, all metadata tracked |

### Pending

| Artifact | Purpose | Blocker |
|----------|---------|---------|
| `tokens.json` | Merged CSS variables | Need extraction script |
| `layout_containers.json` | Top-level layout | Need DOM analysis |
| `region_map.md` | 9-region topology | Need control→region mapping |
| `gaps_report.md` | Missing controls | Need diff against target 82 |

---

## CRITICAL INTEGRATION GAPS

### From Semantic Gap Analysis

1. **~~Token System is Architectural Fiction~~** **CORRECTED BY AGENT BETA**
   - **REALITY: Token system is FULLY IMPLEMENTED and WIRED**
   - `schema/viz/tokens/` contains 6 JSON files (2,726 lines)
   - `token_resolver.py` implements TokenResolver class
   - `visualize_graph_webgl.py` line 612: `resolver.generate_all_themes_css()`
   - `visualize_graph_webgl.py` line 617: `resolver.get_js_theme_config()`
   - **Remaining issue:** Some legacy code (app.js) bypasses tokens with hardcoded values

2. **DataManager Not Implemented**
   - Documented: Centralized data API
   - Reality: 24 `FULL_GRAPH` calls + 26 `Graph.graphData()` calls
   - Fix: Execute refactoring plan from `DATA_LAYER_REFACTORING_MAP.md`

3. **Hadrons Not Wired**
   - Data exists: `HADRONS_96.md` (96 composite structures)
   - Reality: Viz only processes Atoms, Roles, Tiers
   - Fix: Add Hadron dimension to UnifiedNode

4. **Legacy Monolith Still Active**
   - `app.js` (2,999 lines) loaded last by `main.js`
   - Owns Graph initialization loop
   - Blocks advanced physics isolation

---

## CONTROL STATUS DETAIL

### Orphaned (HTML exists, no JS binding)

| Selector | Purpose | Impact |
|----------|---------|--------|
| `.btn[data-size-mode]` | Node size mode | Buttons non-functional |
| `.btn[data-edge-style]` | Edge styling | Buttons non-functional |
| `#cfg-toggle-edge-hover` | Edge highlight | Toggle non-functional |
| `#cfg-toggle-codome` | Codome boundaries | Toggle non-functional |
| `#node-size` | Legacy duplicate | Confusing |
| `#edge-opacity` | Legacy duplicate | Confusing |
| `#toggle-labels` | Legacy duplicate | Confusing |

### Dead Handlers (binding exists, empty body)

| Selector | Binding | Fix |
|----------|---------|-----|
| `#cfg-label-size` | `sidebar.js:_handleSliderChange` | Implement size logic |
| `#cfg-toggle-highlight` | `sidebar.js:_bindAppearanceControls` | Implement highlight |
| `#cfg-toggle-depth` | `sidebar.js:_bindAppearanceControls` | Implement depth shading |

---

## PIXEL SOVEREIGNTY VIOLATIONS

### Top Bypasses in app.js

| Location | Issue | Priority |
|----------|-------|----------|
| Lines 99-119 | `EDGE_COLOR_CONFIG` hardcoded hex | P0 |
| Lines ~7789 | `FLOW_PRESETS` hardcoded colors | P1 |
| Lines ~295 | `PENDULUM` physics hardcoded | P1 |
| Lines ~4275 | Layout speeds hardcoded | P2 |

### Token Conflicts

| Item | Token Value | Hardcoded Value | Severity |
|------|-------------|-----------------|----------|
| Edge Opacity | 0.08 | 0.2 | CRITICAL |
| Edge Width | 0.6 | 1.2 | HIGH |
| Edge Colors | oklch(...) | #4dd4ff | HIGH |
| Node Size Max | 8.0 | 3.0 | MEDIUM |

---

## SYSTEMS ARCHITECTURE

### State Objects

| Object | Purpose | Mutated By |
|--------|---------|------------|
| `VIS_STATE` | Unified visualization state | sidebar.js |
| `APPEARANCE_STATE` | Visual properties | sidebar.js |
| `VIS_FILTERS` | Filtering metadata | sidebar.js |
| `GRAPH_MODE` | atoms/files mode | sidebar.js |
| `DATAMAP` | Data mappings | control-bar.js |

### Key Modules (by size)

| Module | Lines | Purpose |
|--------|-------|---------|
| sidebar.js | 1,408 | Main UI logic |
| color-engine.js | 1,398 | OKLCH color system |
| selection.js | 912 | Selection management |
| control-bar.js | 893 | UPB mapping UI |
| data-manager.js | 839 | Data access layer |

---

## RECOMMENDED TASK DECOMPOSITION

### For Orchestrator

**Wave A: Fix Broken Controls**
1. Wire orphaned `data-size-mode` buttons
2. Wire orphaned `data-edge-style` buttons
3. Implement `cfg-label-size` slider logic
4. Implement `cfg-toggle-highlight` toggle
5. Implement `cfg-toggle-depth` toggle

**Wave B: Pixel Sovereignty**
1. Refactor `EDGE_COLOR_CONFIG` to use tokens
2. Refactor `FLOW_PRESETS` to use tokens
3. Merge `PENDULUM` with animation tokens
4. Tokenize layout speeds

**Wave C: Integration**
1. Implement actual TokenResolver
2. Create DataManager facade
3. Wire Hadrons to visualization

---

## COORDINATION NOTES

### For Agent 1 (Alpha)
- Primary: Code implementation
- Focus: sidebar.js, control-bar.js bindings
- Tools: Edit, Write, Bash

### For Agent 2 (Beta)
- Primary: Validation and research
- Focus: Token extraction, documentation
- Tools: analyze.py, Grep, Read

### Sync Points
- After each Wave completion
- On any blocking issue
- Before any architectural change

---

## FILES TO READ

```
# Corpus
docs/ui/corpus/v1/manifest.json
docs/ui/corpus/v1/extracted/dom_controls.json
docs/ui/corpus/v1/extracted/bindings.json
docs/ui/corpus/v1/analysis/bypass_report.md

# Planning
docs/ui/overhaul/RUNBOOK_v1.md
docs/ui/overhaul/ROR_v1.md

# Source
src/core/viz/assets/modules/sidebar.js
src/core/viz/assets/modules/control-bar.js
src/core/viz/assets/app.js

# Tokens
schema/viz/tokens/theme.tokens.json
schema/viz/tokens/appearance.tokens.json
```

---

## CHECKSUM

```
State Version: 1
Generated: 2026-01-25T06:20:00Z
SHA-256: [compute on paste]
```
