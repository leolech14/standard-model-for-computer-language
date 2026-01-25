# UI Refactor Vision

> Captured: 2026-01-20
> Updated: 2026-01-25 (DTE Research Complete)
> Status: Planning Phase

## Design Philosophy

**Core Principle:** The UI should be invisible. Its function is to convey information, not to be noticed. No glowy, futuristic, neon aesthetics. Just boring, functional, discreet interfaces that get out of the way.

---

## FOUNDATIONAL: Canvas Viewport Specifications

> Source: Voice capture session 2026-01-25

### Canvas Behavior

| Property | Specification | Status |
|----------|---------------|--------|
| **Size** | 100% of dedicated section (fills all available pixels) | CONFIRMED |
| **Bounds** | Infinite canvas (pannable in all directions) | CONFIRMED |
| **Background** | Canvas IS the background of the visualization area | CONFIRMED |

### Origin Point (0, 0, 0)

The origin is where the graph centers by default on load.

| Axis | Position | Status |
|------|----------|--------|
| **X (Horizontal)** | Center of canvas | CONFIRMED |
| **Y (Vertical)** | TBD - Options: Center (50%), Upper third (33%), Two-thirds up (66%) | NEEDS DECISION |
| **Z (Depth)** | Center (3D midpoint) | ASSUMED |

**Open Question:** What vertical position for origin feels most natural?
- **50% (center):** Symmetric, traditional
- **33% (upper third):** More "ground" below, sky above - feels grounded
- **66% (two-thirds up):** Graph hangs from top, more room to explore downward

### Camera Defaults

| Property | Value | Notes |
|----------|-------|-------|
| Initial zoom | TBD | Fit all nodes? Fixed distance? |
| Initial rotation | TBD | Front view? Slight angle? |
| Pan constraints | None (infinite) | User can pan anywhere |

### Technical Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser Viewport                        │
│  ┌──────────┬─────────────────────────────┬─────────────┐   │
│  │          │                             │             │   │
│  │  Left    │      CANVAS (100%)          │   Right     │   │
│  │  Sidebar │      ┌───────────────────┐  │   Sidebar   │   │
│  │          │      │                   │  │             │   │
│  │          │      │   Origin (0,0,0)  │  │             │   │
│  │          │      │        ●          │  │             │   │
│  │          │      │                   │  │             │   │
│  │          │      └───────────────────┘  │             │   │
│  │          │      (infinite, pannable)   │             │   │
│  └──────────┴─────────────────────────────┴─────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Voice Capture Notes (Raw)

> "The canvas takes every pixel of the dedicated section. It is infinite. We can pan. Origin 0,0,0 should be at center horizontally. Vertical position TBD - middle, upper third, or two-thirds?"

---

## FOUNDATIONAL: Semantic Pixel Sovereignty

> Source: Voice capture session 2026-01-25
> Audit: analyze.py forensic mode against viz_core

### The Principle

**Every single pixel displayed must be a controllable variable in our semantic system.**

This applies to:
- The diagram (nodes, edges, background)
- **AND** all frontend components (sidebars, buttons, sliders, text, borders)

Nothing hardcoded. Everything mappable. Full semantic control.

### The Architecture Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    USER PERCEPTION                          │
│                       (pixels)                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              OKLCH COLOR ENGINE                      │   │
│   │   Perceptually uniform: equal Δ = equal perception   │   │
│   │   L (Lightness) · C (Chroma) · H (Hue)              │   │
│   └─────────────────────────────────────────────────────┘   │
│                          ↑                                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │         UNIVERSAL PROPERTY BINDER (UPB)              │   │
│   │   Many-to-many: ANY attribute ↔ ANY visual channel   │   │
│   │   Sources: file_size, complexity, tier, role, etc.  │   │
│   │   Targets: L, C, H, size, opacity, position, etc.   │   │
│   └─────────────────────────────────────────────────────┘   │
│                          ↑                                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              DATA ENDPOINTS                          │   │
│   │   Every node attribute exposed as bindable source    │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Why OKLCH (Not Arbitrary)

OKLCH was chosen through deliberate research, not chance:

| Property | Benefit |
|----------|---------|
| **Perceptual uniformity** | Equal mathematical Δ = equal visual Δ to human eye |
| **Hue stability** | Changing lightness doesn't shift hue (unlike HSL) |
| **Gamut mapping** | Handles sRGB boundaries gracefully |
| **Semantic encoding** | Data differences accurately represented as color differences |

> "With HSL, if you define a palette by varying hue while keeping lightness constant, the resulting colors won't look uniformly prominent. OKLCH solves this."
> — Academic research 2026-01-23

### Current Compliance Audit (2026-01-25)

**Status: 75% COMPLIANT (25% violations)**
> *Corrected via multi-parallel validation - see `docs/research/MULTI_PARALLEL_VALIDATION_REPORT.md`*

| Component | Compliance | Issue |
|-----------|------------|-------|
| Main graph nodes | ✅ 95% | Minor fallbacks |
| Main graph edges | ✅ 90% | PALETTE_HEX hardcoded |
| app.js monolith | ❌ 0% | EDGE_COLOR_CONFIG, FLOW_PRESETS hardcoded |
| Token conflicts | ❌ 0% | theme.tokens.json vs appearance.tokens.json |
| CSS UI chrome | ❌ 30% | Many hardcoded rgba(), hex |
| Template inline | ❌ 20% | Hardcoded color values |

### Violations Requiring Fix (Validated)

#### Critical (100% bypass)
1. **app.js:L112** - `EDGE_COLOR_CONFIG` hardcoded values
2. **app.js:L515** - `FLOW_PRESETS` hardcoded color schemes
3. **Token Conflict** - theme.tokens.json vs appearance.tokens.json overlap

#### High (Partial bypass)
4. **edge-system.js:L91-113** - PALETTE_HEX instead of COLOR module
5. **styles.css:L1064** - Hardcoded linear-gradient rgba values
6. **template.html:L1026** - Hardcoded ::before background colors

### Target State

**100% semantic control** where:

1. Every color flows through OKLCH engine
2. Every size/position controllable via UPB
3. CSS uses only variables: `var(--color-tier-0)`, `var(--spacing-md)`
4. No hardcoded hex, rgb, rgba anywhere
5. UI chrome follows same rules as diagram

### Connection to UPB

The Universal Property Binder enables this by:

```
DATA → UPB → OKLCH → PIXEL

Example binding:
  source: node.complexity
  target: node.color.chroma
  scale: logarithmic
  range: [0.05, 0.35]
```

Any data attribute can drive any visual channel through the UPB projection matrix.

### Integration Documents

| Document | Purpose |
|----------|---------|
| `specs/UNIVERSAL_PROPERTY_BINDER.md` | UPB architecture |
| `specs/UPB_IMPLEMENTATION_PLAN.md` | Extraction roadmap |
| `specs/UPB_LEGACY_SPRAWL.md` | Where binding logic currently lives |
| `research/perplexity/20260123_160126_*.md` | OKLCH academic research |
| `modules/color-engine.js` | OKLCH implementation |
| `modules/property-query.js` | UPB provider chain |

### Voice Capture Notes (Raw)

> "100% of pixels must be variables. Full control on every value displayed. Mapped to semantic understanding. UPB plays a role. OKLCH plays a role. All related, correlated. We didn't choose OKLCH by chance - it's robust and powerful. Everything interconnects."

---

## FOUNDATIONAL: Data Trade Exchange (DTE)

> Source: Voice capture session 2026-01-25
> Status: RESEARCH COMPLETE - Ready for Implementation
> Research: `docs/research/DTE_SEMANTIC_MATCHING_RESEARCH.md`

### The Concept

**"The place our systems go to match and calculate the interchangeable equivalency of the objects they handle."**

A central clearinghouse where:
- Different data representations meet
- Values are converted between domains
- Equivalencies are calculated and cached
- All modules trade through a common protocol

### The Problem It Solves

Currently, conversions happen ad-hoc:
- `color-engine.js` converts data → OKLCH
- `node-helpers.js` converts tier → color
- `edge-system.js` converts weight → width
- `control-bar.js` converts slider → parameter

Each module does its own conversion. No central truth. No reusability.

### The Vision

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA TRADE EXCHANGE (DTE)                        │
│         "The Central Clearinghouse for Value Equivalencies"          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   SELLERS (Data Sources)              BUYERS (Visual Consumers)      │
│   ══════════════════════              ═════════════════════════      │
│                                                                      │
│   node.complexity ────┐                      ┌──── OKLCH.chroma      │
│   node.tier ──────────┤                      ├──── node.size         │
│   node.file_size ─────┼───► EXCHANGE ◄──────┼──── node.opacity      │
│   edge.weight ────────┤    (rates)           ├──── edge.width        │
│   edge.type ──────────┤                      ├──── edge.color        │
│   filter.state ───────┘                      └──── ui.button.state   │
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    EXCHANGE RATES                            │   │
│   │                                                              │   │
│   │   complexity[0-100] ═══ chroma[0.05-0.35]  (log scale)      │   │
│   │   tier[T0,T1,T2]    ═══ hue[142,220,330]   (discrete map)   │   │
│   │   file_size[bytes]  ═══ size[0.5-4.0]     (sqrt scale)      │   │
│   │   weight[0-1]       ═══ width[0.5-3.0]    (linear scale)    │   │
│   │                                                              │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    EXCHANGE LEDGER                           │   │
│   │                                                              │   │
│   │   Every transaction recorded:                                │   │
│   │   - Who requested (module)                                   │   │
│   │   - What was exchanged (source → target)                     │   │
│   │   - Rate applied (scale + range)                             │   │
│   │   - Timestamp                                                │   │
│   │                                                              │   │
│   │   Enables: Debugging, Optimization, Analytics                │   │
│   │                                                              │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| **QUOTE** | Get exchange rate without executing | "What would complexity=75 be in chroma?" |
| **TRADE** | Execute conversion, return value | `DTE.trade('complexity', 75, 'chroma')` → 0.28 |
| **BATCH** | Multiple trades in one call | Trade all node properties at once |
| **REGISTER** | Add new exchange rate | Define new source↔target mapping |
| **AUDIT** | Query transaction history | "Who's using tier→hue mapping?" |

### Relationship to UPB

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   UPB (Universal Property Binder)                           │
│   ════════════════════════════════                          │
│   WHAT to bind (declarative configuration)                  │
│   "complexity should drive chroma"                          │
│                                                             │
│                         ↓ calls                             │
│                                                             │
│   DTE (Data Trade Exchange)                                 │
│   ═════════════════════════                                 │
│   HOW to convert (execution engine)                         │
│   "complexity 75 → chroma 0.28 via log scale"               │
│                                                             │
│                         ↓ outputs to                        │
│                                                             │
│   OKLCH Engine                                              │
│   ════════════                                              │
│   Final rendering to perceptually uniform color             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**UPB** = The binding graph (what connects to what)
**DTE** = The conversion engine (how values transform)
**OKLCH** = The final colorspace (perceptual output)

### Why "Exchange" Metaphor

Like a currency exchange:
- **Currencies** = Different value domains (bytes, percentages, pixels, OKLCH channels)
- **Exchange rates** = Scale functions + ranges
- **Traders** = Modules requesting conversions
- **Ledger** = Transaction log for debugging/analytics
- **Market makers** = Registered conversion providers

### Benefits

1. **Single source of truth** for all conversions
2. **Debuggable** - trace any visual back to source data
3. **Optimizable** - cache frequently used conversions
4. **Extensible** - register new rates without touching existing code
5. **Auditable** - understand which modules use which mappings

### Research-Backed Architecture (2026-01-25)

Based on industry pattern research ([W3C Design Tokens](https://www.w3.org/community/design-tokens/2025/), [Semantic Layers](https://enterprise-knowledge.com/data-management-and-architecture-trends-for-2025/), [Broker/Mediator Pattern](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch02.html)):

```
┌──────────────────────────────────────────────────────────────────────┐
│                           UPB (Binding Layer)                         │
│              "WHAT visual channel shows WHAT data field"              │
├──────────────────────────────────────────────────────────────────────┤
│   binding: { node.color = data.role, node.size = data.loc }          │
│                                  ▼                                    │
├──────────────────────────────────────────────────────────────────────┤
│                           DTE (Exchange Layer)                        │
│               "HOW to transform values between domains"               │
├──────────────────────────────────────────────────────────────────────┤
│   ┌─────────────┐   ┌──────────────────┐   ┌─────────────┐          │
│   │   DOMAIN    │   │    EXCHANGE      │   │   DOMAIN    │          │
│   │   REGISTRY  │◀──│    REGISTRY      │──▶│   SCHEMA    │          │
│   │ (what exists)│   │ (how to convert) │   │ (constraints)│          │
│   └─────────────┘   └──────────────────┘   └─────────────┘          │
│                              ▼                                        │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │  QUOTE | TRADE | BATCH | REGISTER | AUDIT                     │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                              ▼                                        │
├──────────────────────────────────────────────────────────────────────┤
│                      PROPERTY-QUERY (Resolution Layer)                │
│                 "Which provider wins for this channel?"               │
└──────────────────────────────────────────────────────────────────────┘
```

### Domain Registry (Confirmed)

| Domain | Type | Range | Example |
|--------|------|-------|---------|
| `data.loc` | number | [0, ∞] | Lines of code |
| `data.complexity` | number | [1, ∞] | Cyclomatic |
| `data.tier` | ordinal | [T0, T1, T2] | Atom tier |
| `data.role` | categorical | 33 values | Semantic role |
| `canonical.normalized` | number | [0, 1] | Intermediate |
| `visual.size` | number | [1, 50] | Pixels |
| `visual.color` | color | OKLCH | L, C, H |

### Implementation Phases

| Phase | Deliverable | Scope |
|-------|-------------|-------|
| **1** | `dte.js` core (~150 lines) | QUOTE, TRADE, REGISTER |
| **2** | Integration with `scales.js` | Extend existing scales |
| **3** | OKLCH exchanges | Color-specific transforms |
| **4** | AUDIT + debugging tools | Transaction history |

### Open Questions (Resolved via Research)

| Question | Answer |
|----------|--------|
| Sync or async? | **Sync** - conversions are fast (microseconds) |
| Hot-reloadable? | **Yes** - use epoch-based cache invalidation |
| Persist ledger? | **No** - memory only with 1000-entry cap |
| Invalid inputs? | **Warn + reasonable default** - never crash |
| Performance tracking? | **Yes** - via AUDIT operation |

### Voice Capture Notes (Raw)

> "We need to design a Data Trade Exchange - THE PLACE our systems go to match and calculate the interchangeable equivalency of the objects they handle."

---

## Change Request #1: Bottom Component (Footer → Floating Mapper)

### Current State
- Fixed footer at bottom of page
- Full-width, glued to bottom edge
- Contains: Scope selector (Selected Nodes / All Nodes)
- Style: Part of the sidebar system, feels like a footer

### Desired State
- **Floating component** in bottom-center of canvas
- NOT full-width - compact, centered
- Like ChatGPT input bar / "Higgs Field" input bar style
- **Purpose:** Visual Mapping Interface
  - Simple UI to map: `[Visual Attribute]` ↔ `[Data Parameter]`
  - Example: "Size of nodes" ↔ "File size in bytes"
  - Make it obvious: "You matched these two values, now they correlate visually"
- Give users full data visualization power in an intuitive way

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `template.html` | Contains footer markup | Restructure to floating component |
| `styles.css` | Footer styles | New floating styles, centered positioning |
| `modules/control-bar.js` | Visual mapping logic | May need to integrate with new component |
| `modules/sidebar.js` | Currently manages this? | Remove footer responsibility |

### Legacy to Handle
- Current footer markup in template.html
- Footer-related CSS classes
- Any JS that expects footer to be part of sidebar

### Confidence: 85%
### Complexity: Medium

---

## Change Request #2: UI Color Palette - De-glamorize

### Current State
- Bright light blue accent colors
- Glowy, futuristic aesthetic
- Neon-replacement colors that still attract attention
- Interface "wants to be seen"

### Desired State
- Boring, muted colors
- Discreet, unnoticeable
- Functional over aesthetic
- "You don't even notice it's there"
- Interface that delivers information invisibly

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `styles.css` | All UI colors defined here | Mute all accent colors |
| `template.html` | Inline styles? | Remove any inline glowy styles |
| `modules/theme.js` | Theme configuration | Update color palette |

### Color Direction
- Replace bright blues with muted grays
- Remove glow effects (box-shadow with color)
- Reduce contrast between UI and background
- Make borders subtle, not prominent

### Legacy to Handle
- Current color variables in CSS
- Any hardcoded colors in JS

### Confidence: 90%
### Complexity: Low-Medium

---

## Change Request #3: Remove Star Field Feature

### Current State
- Star field exists in codebase
- Toggle in sidebar (shows "deactivated")
- **BUG:** Stars appear on canvas even when toggle is off
- Only disappears after toggle on→off cycle

### Desired State
- **Remove entirely** - not just hide
- Rationale: Nodes ARE the stars. Adding more dots creates confusion.
- Meaningless visual elements that look strikingly similar to actual data

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `modules/stars.js` | Star field implementation | DELETE or archive |
| `template.html` | Star toggle in sidebar | Remove toggle |
| `styles.css` | Star-related styles | Remove |
| `modules/main.js` | STARS module wiring | Remove references |
| `app.js` | Any star initialization | Remove |

### Legacy to Handle
- `modules/stars.js` - archive to `archive/` folder
- STARS_STORAGE_KEY in localStorage
- Any references in other modules

### Confidence: 95%
### Complexity: Low

---

## Change Request #4: Resizable Sidebar Sections (Vertical)

### Current State
- Fixed-height sections within sidebars
- No ability to resize individual sections
- Some sections have empty space (right sidebar bottom)
- Cannot compact or expand sections

### Desired State
- **Drag borders** between sections to resize vertically
- Each section independently resizable
- **Constraints:**
  - Minimum height: ~66-100px (keeps section visible but compact)
  - Maximum height: Slightly more than content needs
  - Scrollable when compacted below content height
- Smart behavior: respect element count in section

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `template.html` | Section structure | Add resize handles |
| `styles.css` | Section styles | resize cursor, min/max heights |
| `modules/sidebar.js` | Sidebar logic | Add resize drag handlers |

### Implementation Notes
- Use CSS `resize: vertical` or custom drag handlers
- Store user preferences in localStorage
- Sections: filters, schemes, controls, etc.

### Legacy to Handle
- Current fixed-height CSS
- Any hardcoded height values

### Confidence: 75%
### Complexity: Medium-High

---

## Change Request #5: Resizable Sidebars (Horizontal)

### Current State
- Fixed-width left and right sidebars
- Vertical divider line exists but not draggable
- Cannot adjust canvas vs sidebar ratio

### Desired State
- **Drag vertical divider** to resize sidebars
- Left and right sidebars resize **independently**
- Components inside **reflow** when width changes:
  - More width → elements spread horizontally, less vertical space
  - Less width → elements stack vertically, more scrolling
- Smart responsive behavior

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `template.html` | Layout structure | Add draggable dividers |
| `styles.css` | Sidebar widths | Flexbox/Grid adjustments |
| `modules/sidebar.js` | Sidebar management | Resize handlers, reflow logic |

### Implementation Notes
- CSS Grid or Flexbox with dynamic columns
- Store widths in localStorage
- Minimum sidebar width to prevent collapse
- Maximum to prevent canvas from disappearing

### Legacy to Handle
- Current fixed-width CSS
- Any layout assumptions in JS

### Confidence: 70%
### Complexity: High

---

## Summary Task List

| # | Task | Confidence | Complexity | Priority |
|---|------|------------|------------|----------|
| 1 | Remove star field feature | **98%** | Low | High |
| 2 | De-glamorize UI colors | **95%** | Low-Med | High |
| 3 | Convert footer to floating mapper | **92%** | Medium | High |
| 4 | Add vertical section resizing | **85%** | Med-High | Medium |
| 5 | Add horizontal sidebar resizing | **80%** | High | Medium |

### Confidence Justification (Updated after code review)

**#1 Stars (98%):** Code is isolated - `modules/stars.js` (89 lines), starfield creation in app.js (lines 1997-2019), MODULE_ORDER in visualize_graph_webgl.py. Clean removal.

**#2 Colors (95%):** All glowy colors are in `control-bar.js` inline styles and `styles.css`. Pattern: `rgba(100, 150, 255, ...)` everywhere. Search-and-replace friendly.

**#3 Floating Mapper (92%):** `control-bar.js` already has the EXACT UI needed (SCOPE, MAP, TO, SCALE, APPLY). Just needs CSS repositioning:
- Current: `position: fixed; bottom: 0; left: 0; right: 0;` (full-width)
- Needed: `left: 50%; transform: translateX(-50%); max-width: 900px; border-radius: 12px;`

**#4 Vertical Section Resize (85%):** Template already uses `.section` > `.section-header` + `.section-content` pattern. Add CSS `resize: vertical` or custom drag handlers. Store in localStorage.

**#5 Horizontal Sidebar Resize (80%):** Uses CSS variable `--sidebar-width: 280px`. Add draggable divider elements. More complex due to responsive reflow, but clear path.

---

## File Change Summary

### Files to DELETE/Archive
- `modules/stars.js` → `archive/stars.js`

### Files to MODIFY (Heavy)
- `styles.css` - colors, layout, resize styles
- `template.html` - structure changes
- `modules/sidebar.js` - resize logic

### Files to MODIFY (Light)
- `modules/main.js` - remove STARS wiring
- `modules/control-bar.js` - integrate with floating mapper
- `app.js` - remove star references

---

## Open Questions

1. Floating mapper: Should it have a collapse/expand state?
2. Section resizing: Should collapsed sections have a "header only" mode?
3. Color palette: Any specific reference for "boring" UI? (macOS? Windows? Material?)
4. Should sidebar widths be synced or fully independent?

---

## Architecture Coordination

### Concurrent Refactoring (Other Agent)
- Extracting UI functions (15) → `modules/ui-controls.js`
- MODULE_ORDER defined in `tools/visualize_graph_webgl.py`

### Module Assignment for UI Changes

| Change | Target Module | Notes |
|--------|---------------|-------|
| Star field removal | DELETE `stars.js` | Also remove from MODULE_ORDER |
| UI colors | `styles.css` + `theme.js` | No new module needed |
| Floating mapper | NEW `modules/visual-mapper.js` OR extend `control-bar.js` | TBD |
| Section resizing | `modules/sidebar.js` | Extend existing |
| Sidebar resizing | `modules/sidebar.js` + CSS | Extend existing |

### Functions Still in app.js (Relevant to UI)
- `buildChipGroup`, `buildMetadataControls`, `buildAppearanceSliders`
- These may move to `ui-controls.js` soon - coordinate!

---

## Next Steps

1. [ ] Review and approve this vision document
2. [ ] **Coordinate with refactoring agent** on ui-controls.js
3. [ ] Prioritize: Start with #1 (stars removal) - quick win
4. [ ] Then #2 (colors) - visual consistency
5. [ ] Then #3 (floating mapper) - UX improvement
6. [ ] Finally #4 & #5 (resizing) - polish features
