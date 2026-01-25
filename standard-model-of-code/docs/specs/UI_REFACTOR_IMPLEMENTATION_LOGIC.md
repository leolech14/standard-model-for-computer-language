# UI Refactor Implementation Logic

**Date:** 2026-01-25
**Purpose:** Connect validated architecture to concrete UI refactoring tasks
**Status:** LOGIC ESTABLISHED

---

## 1. The Core Insight

**The UI refactoring is NOT just visual polish - it's the USER-FACING INTERFACE to our validated architecture.**

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                              │
│                                                                      │
│   "I want node SIZE to show FILE SIZE"                              │
│   "I want node COLOR to show COMPLEXITY"                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FLOATING MAPPER (CR#1)                            │
│                                                                      │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│   │ Visual Attr │ ←→ │    DTE      │ ←→ │ Data Param  │            │
│   │   (SIZE)    │    │  (EXCHANGE) │    │ (file_size) │            │
│   └─────────────┘    └─────────────┘    └─────────────┘            │
│                                                                      │
│   This IS the DTE's user interface!                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE STACK                                │
│                                                                      │
│   UPB ──────► DTE ──────► Property-Query ──────► OKLCH ──────► PIXEL│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Dependency Graph: Architecture → UI Tasks

```
                    ┌─────────────────────────┐
                    │   CANVAS FOUNDATION     │
                    │   (100%, infinite,      │
                    │    origin specs)        │
                    └───────────┬─────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
┌───────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│ PIXEL SOVEREIGNTY │ │       DTE       │ │  LAYOUT SYSTEM      │
│ (75% → 100%)      │ │ (Exchange Layer)│ │  (Resizable panels) │
└─────────┬─────────┘ └────────┬────────┘ └──────────┬──────────┘
          │                    │                     │
          │                    │                     │
          ▼                    ▼                     ▼
┌───────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│ CR#2: De-glamorize│ │ CR#1: Floating  │ │ CR#4: Section resize│
│ UI Colors         │ │ Mapper          │ │ CR#5: Sidebar resize│
│                   │ │                 │ │                     │
│ DEPENDS ON:       │ │ DEPENDS ON:     │ │ INDEPENDENT         │
│ Token system      │ │ DTE operational │ │ (Can do in parallel)│
└───────────────────┘ └─────────────────┘ └─────────────────────┘
          │                    │
          │                    │
          └────────┬───────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ CR#3: Remove    │
          │ Star Field      │
          │                 │
          │ PREREQUISITE    │
          │ (Clean canvas)  │
          └─────────────────┘
```

---

## 3. Logical Relationships Explained

### 3.1 Floating Mapper IS the DTE Interface

| What User Sees | What Architecture Does |
|----------------|----------------------|
| Dropdown: "Size" | UPB selects `visual.size` channel |
| Dropdown: "File Size" | UPB selects `data.loc` source |
| Dropdown: "Log" | DTE selects exchange rate function |
| Button: "Apply" | DTE.REGISTER() + Property-Query invalidate |

**The Floating Mapper (CR#1) cannot work properly without DTE.**

Current control-bar.js has this UI but it's wired to scattered functions. DTE centralizes the conversion logic.

```javascript
// CURRENT (scattered)
control-bar.js → window.UPB.bind() → upb/scales.js → refreshGraph()

// WITH DTE (centralized)
floating-mapper.js → DTE.REGISTER(from, to, scale) → Property-Query.invalidate()
```

### 3.2 De-glamorize Colors REQUIRES Pixel Sovereignty

| Why? | Explanation |
|------|-------------|
| Can't change what you don't control | Hardcoded colors in app.js bypass any theme changes |
| 25% violations | EDGE_COLOR_CONFIG, FLOW_PRESETS ignore CSS variables |
| Single source of truth | De-glamorizing means ONE place defines ALL colors |

**Implementation Order:**
1. Fix Pixel Sovereignty violations (app.js:L112, L515)
2. Move all colors to tokens.json
3. THEN de-glamorize by changing token values

```javascript
// WRONG ORDER
styles.css: --accent-color: gray;  // Changed!
app.js: EDGE_COLOR_CONFIG = { highlight: '#00ff00' };  // Still glowing!

// RIGHT ORDER
1. Remove EDGE_COLOR_CONFIG from app.js
2. Add to tokens.json: "edge.highlight": "var(--accent-color)"
3. Change --accent-color to muted gray
```

### 3.3 Star Field Removal is a PREREQUISITE

| Why First? | Explanation |
|------------|-------------|
| Cognitive noise | Stars confuse what's data vs decoration |
| Clean baseline | Canvas should show ONLY meaningful pixels |
| Bug exists | Stars appear even when "off" - broken state |

**Before implementing Canvas Foundation, we need a clean canvas.**

### 3.4 Resizable Panels are INDEPENDENT

| Why Parallel? | Explanation |
|---------------|-------------|
| Layout ≠ Data | Panel sizes don't affect data→visual mapping |
| CSS-focused | Mostly styles.css + sidebar.js changes |
| No DTE dependency | Works with current or new architecture |

**Can implement CR#4 and CR#5 in parallel with DTE work.**

---

## 4. Implementation Phases

### Phase 0: Clean Slate (PREREQUISITE)
**Goal:** Remove noise, fix broken state

| Task | Files | Effort |
|------|-------|--------|
| Remove star field (CR#3) | stars.js, main.js, app.js | LOW |
| Fix star toggle bug | template.html | LOW |

**Exit Criteria:** Canvas shows only nodes/edges, no decorative elements

---

### Phase 1: Pixel Sovereignty (FOUNDATION)
**Goal:** 100% semantic control over every displayed pixel

| Task | Files | Effort |
|------|-------|--------|
| Remove EDGE_COLOR_CONFIG | app.js:L112 | LOW |
| Remove FLOW_PRESETS hardcodes | app.js:L515 | LOW |
| Resolve token file conflict | theme.tokens.json, appearance.tokens.json | MEDIUM |
| Audit remaining hardcodes | grep for hex/rgb/rgba | LOW |

**Exit Criteria:** `grep -r "#[0-9a-f]{6}" modules/` returns 0 results

---

### Phase 2: DTE Core (ARCHITECTURE)
**Goal:** Central exchange engine operational

| Task | Files | Effort |
|------|-------|--------|
| Create dte.js core | NEW: modules/dte.js | MEDIUM |
| Define domain registry | dte.js | LOW |
| Define exchange registry | dte.js | LOW |
| Add DTE provider to property-query | property-query-init.js | LOW |
| Migrate UPB_SCALES to DTE | upb/scales.js → dte.js | MEDIUM |

**Exit Criteria:** `DTE.TRADE('data.loc', 'visual.size', 100)` returns correct value

---

### Phase 3A: Floating Mapper (USER INTERFACE)
**Goal:** User can bind any data to any visual

| Task | Files | Effort |
|------|-------|--------|
| Restyle control-bar as floating | styles.css | LOW |
| Wire dropdowns to DTE domains | control-bar.js | MEDIUM |
| Wire scale selector to DTE exchanges | control-bar.js | MEDIUM |
| Wire Apply to DTE.REGISTER | control-bar.js | LOW |

**Exit Criteria:** User selects "Size ← LoC (log)" and nodes resize accordingly

---

### Phase 3B: De-glamorize Colors (VISUAL STYLE)
**Goal:** Invisible, boring UI chrome

| Task | Files | Effort |
|------|-------|--------|
| Define muted token palette | tokens.json | LOW |
| Replace bright blues with grays | tokens.json | LOW |
| Remove glow effects | styles.css (box-shadow) | LOW |
| Reduce border contrast | styles.css | LOW |

**Exit Criteria:** UI chrome is visually secondary to canvas content

---

### Phase 4: Layout Polish (PARALLEL TRACK)
**Goal:** Professional resizable layout

| Task | Files | Effort |
|------|-------|--------|
| Add section resize handles (CR#4) | template.html, sidebar.js | MEDIUM |
| Add sidebar resize handles (CR#5) | template.html, sidebar.js | HIGH |
| Implement localStorage persistence | sidebar.js | LOW |
| Add react-resizable-panels (optional) | package.json, imports | HIGH |

**Exit Criteria:** User can drag to resize any panel, persists across sessions

---

## 5. Critical Path Analysis

```
Week 1                    Week 2                    Week 3
─────────────────────────────────────────────────────────────────────

Phase 0: Stars ──┐
                 │
Phase 1: Pixels ─┴──────────┐
                            │
Phase 2: DTE Core ──────────┴──────────┐
                                       │
                     Phase 3A: Mapper ─┴─────────── COMPLETE
                                       │
                     Phase 3B: Colors ─┘

─────────────────────────────────────────────────────────────────────
PARALLEL TRACK:

Phase 4: Layout ───────────────────────────────────── COMPLETE
```

**Critical Path:** Phase 0 → Phase 1 → Phase 2 → Phase 3A

**Parallel Track:** Phase 4 (can start immediately, no dependencies)

---

## 6. Risk Matrix

| Risk | Impact | Mitigation |
|------|--------|------------|
| DTE delays Floating Mapper | HIGH | Mapper can use current UPB.bind() initially |
| Token conflict breaks colors | MEDIUM | Backup current tokens before merge |
| Resize panels break layout | LOW | Use feature flag, test thoroughly |
| OKLCH browser support | LOW | Already in production, CSS fallbacks exist |

---

## 7. Success Metrics

### Phase 0 Complete
- [ ] `modules/stars.js` archived
- [ ] Star toggle removed from template.html
- [ ] Canvas shows only data elements

### Phase 1 Complete
- [ ] `grep -rE "(#[0-9a-fA-F]{6}|rgb\(|rgba\()" modules/ app.js` returns 0
- [ ] All colors flow through tokens.json
- [ ] Single token file (conflict resolved)

### Phase 2 Complete
- [ ] `DTE.TRADE()` works for all current bindings
- [ ] `DTE.QUOTE()` returns correct formulas
- [ ] Property-Query uses DTE provider

### Phase 3 Complete
- [ ] Floating Mapper visually centered on canvas
- [ ] User can create new bindings without code
- [ ] UI chrome is "invisible" (user doesn't notice it)

### Phase 4 Complete
- [ ] All sections vertically resizable
- [ ] Both sidebars horizontally resizable
- [ ] Sizes persist in localStorage

---

## 8. Why This Order Matters

### Wrong Order (Common Mistake)

```
❌ Start with Floating Mapper CSS
   → Looks nice but bindings don't work
   → DTE not ready, falls back to scattered code
   → User confusion: "Why doesn't Apply work?"

❌ Start with De-glamorize colors
   → Change CSS variables
   → Hardcoded colors still glow
   → Inconsistent UI: some gray, some bright

❌ Start with resizable panels
   → Works fine but...
   → Wastes time if we switch to React
   → Better to validate architecture first
```

### Right Order (What We're Doing)

```
✓ Phase 0: Clean canvas (remove noise)
   → Clear baseline for all future work

✓ Phase 1: Pixel Sovereignty (control)
   → PREREQUISITE for any visual changes
   → No more "why is this still blue?"

✓ Phase 2: DTE Core (infrastructure)
   → PREREQUISITE for Floating Mapper
   → Central truth for all conversions

✓ Phase 3: User-facing features
   → Now they WORK, not just LOOK good

✓ Phase 4: Layout polish (parallel)
   → Independent, can do anytime
```

---

## 9. Connection to Validated Architecture

| Validation Finding | UI Refactor Impact |
|-------------------|-------------------|
| DTE rated 9/10 coherence | Enables Floating Mapper (CR#1) |
| Property-Query ready for DTE | No core refactor needed |
| 75% Pixel Sovereignty (not 85%) | Phase 1 is larger than thought |
| OKLCH validated | Color de-glamorizing is safe |
| Provider Chain = industry standard | Our approach is proven |
| datamap.js needs refactor | Part of Phase 2 scope |

---

## 10. Summary: The Logic Chain

```
1. VALIDATED ARCHITECTURE
   │
   ├── DTE is the "Exchange"
   │   └── Floating Mapper is DTE's UI ──────► CR#1
   │
   ├── Pixel Sovereignty required
   │   └── De-glamorize needs control ───────► CR#2
   │
   ├── Clean canvas prerequisite
   │   └── Remove star field noise ──────────► CR#3
   │
   └── Layout independent of data
       └── Resize panels in parallel ────────► CR#4, CR#5
```

**The architecture validation wasn't academic - it directly determined implementation order.**

