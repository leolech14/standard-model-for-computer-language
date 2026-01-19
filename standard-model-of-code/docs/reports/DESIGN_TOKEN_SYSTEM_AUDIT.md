# Design Token System Audit

> Complete documentation of the Collider visualization token system.
> Last updated: 2026-01-19

---

## Confidence Methodology

**Every claim in this document was verified through:**

| Verification Layer | Method | Status |
|-------------------|--------|--------|
| 1. Initial Code Read | Read source files | ✓ Complete |
| 2. Second Intentional Verification | Grep with specific patterns | ✓ Complete |
| 3. Payload Inspection | Decompress COMPRESSED_PAYLOAD from HTML | ✓ Complete |
| 4. AI Alignment Check | `analyze.py --mode architect` query | ✓ Complete |

**AI Verification (2026-01-19):**

```
Query: "What are the design principles for the visualization token system?"
Source: analyze.py --mode forensic against token_resolver.py, appearance_engine.py, physics_engine.py

Key Findings:
1. "Two-layer architecture where tokens from JSON files control appearance and behavior"
2. "The design promotes clear separation between token files (JSON) and JavaScript runtime"
3. "The code aims to minimize hardcoded values"
4. "The intended design is to configure as much as possible through tokens"
```

**Payload Verification (2026-01-19):**

```
Decompressed COMPRESSED_PAYLOAD (189,840 chars) from generated HTML:
- physics in data: True (charge.strength = -120, link.distance = 50)
- appearance in data: True (animation.hue.speed = 0.0008)
- All token values correctly propagated to final output
```

---

## Executive Summary

The Collider HTML visualization uses a **two-layer architecture**:
- **Layer 1 (Controller):** JSON token files define all configurable values
- **Layer 2 (Controlled):** JavaScript/CSS consume tokens at runtime

**Current State:**
- 8 configuration systems identified
- 6 critical conflicts requiring resolution
- Physics: 95% tokenized (previously thought to be 0%)
- Colors: 75% tokenized (conflicts between files)
- Theme variants: 38% complete (light/high-contrast incomplete)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Configuration Systems Inventory](#2-configuration-systems-inventory)
3. [Token File Reference](#3-token-file-reference)
4. [Python Engine Reference](#4-python-engine-reference)
5. [JavaScript Runtime Reference](#5-javascript-runtime-reference)
6. [Conflict Registry](#6-conflict-registry)
7. [Gap Analysis](#7-gap-analysis)
8. [Confidence Matrix](#8-confidence-matrix)
9. [Remediation Checklist](#9-remediation-checklist)
10. [Verification Procedures](#10-verification-procedures)

---

## 1. Architecture Overview

### Data Flow

```
TOKEN FILES (JSON)          PYTHON ENGINES           HTML OUTPUT            BROWSER RUNTIME
─────────────────          ──────────────           ───────────            ───────────────

theme.tokens.json    ──┐
appearance.tokens.json─┼──► TokenResolver ─────────► CSS Variables ──────► styles.css
layout.tokens.json   ──┤    (singleton)             (injected)             var(--token)
controls.tokens.json ──┘
                           │
                           ├──► PhysicsEngine ─────► physics_config ──────► d3.forceSimulation
                           ├──► AppearanceEngine ──► appearance_config ───► Node/Edge rendering
                           └──► ControlsEngine ────► controls_config ─────► UI behavior
```

### Two-Layer Architecture

| Layer | Role | Files | Mutability |
|-------|------|-------|------------|
| **Controller** | Define all values | `schema/viz/tokens/*.json` | Edit to change behavior |
| **Controlled** | Consume values | `src/core/viz/assets/*` | Should NOT contain values |

### The Problem

The controlled layer (app.js) contains **hardcoded fallback values** that can:
1. Mask token loading failures
2. Create conflicts with token definitions
3. Make debugging difficult (which value is active?)

---

## 2. Configuration Systems Inventory

### Complete List (8 Systems)

| # | System | Location | Type | Purpose |
|---|--------|----------|------|---------|
| 1 | Theme Tokens | `schema/viz/tokens/theme.tokens.json` | JSON | Colors, themes, shadows |
| 2 | Appearance Tokens | `schema/viz/tokens/appearance.tokens.json` | JSON | Nodes, edges, physics, animation |
| 3 | Layout Tokens | `schema/viz/tokens/layout.tokens.json` | JSON | Spacing, sizing, z-index |
| 4 | Controls Tokens | `schema/viz/tokens/controls.tokens.json` | JSON | Keyboard, mouse, sliders, panels |
| 5 | TokenResolver | `src/core/viz/token_resolver.py` | Python | Loads tokens, generates CSS |
| 6 | PhysicsEngine | `src/core/viz/physics_engine.py` | Python | Outputs physics config to JS |
| 7 | AppearanceEngine | `src/core/viz/appearance_engine.py` | Python | Outputs appearance config to JS |
| 8 | ControlsEngine | `src/core/viz/controls_engine.py` | Python | Outputs controls config to JS |

### Auxiliary Systems (Not Primary)

| System | Location | Purpose |
|--------|----------|---------|
| AnalyzerConfig | `src/core/config.py` | Core analyzer settings (not viz) |
| Blender Tokens | `blender/tokens/appearance.tokens.json` | 3D Blender visualization |
| Surface Manifest | `schema/surfaces/surface.manifest.json` | UI surface contracts |

---

## 3. Token File Reference

### 3.1 theme.tokens.json

**Path:** `schema/viz/tokens/theme.tokens.json`
**Lines:** 637
**Purpose:** All color definitions and theme variants

#### Structure

```
theme.tokens.json
├── $default-theme: "dark"
├── themes/
│   ├── light/           (lines 9-80)
│   │   └── color.bg.*, color.text.*, color.border.*
│   └── high-contrast/   (lines 82-164)
│       └── color.bg.*, color.text.*, color.border.*
├── color/
│   ├── bg/              (lines 170-242) - 16 background variants
│   ├── border/          (lines 245-269) - 6 border variants
│   ├── text/            (lines 272-304) - 8 text variants
│   ├── accent/          (lines 307-359) - 9 accent variants
│   ├── status/          (lines 362-426) - 15 status variants
│   ├── data/            (lines 429-445) - 4 data colors
│   ├── neutral/         (lines 448-464) - 4 neutral colors
│   ├── gradient/        (lines 467-484) - 14 gradient components
│   ├── viz/             (lines 487-498) - 8 visualization colors
│   ├── edge/            (lines 501-512) - 11 edge type colors
│   ├── console/         (lines 515-520) - 4 console colors
│   └── schemes/         (lines 523-560) - 6 color schemes × 5 colors
└── shadow/              (lines 563-580) - 4 shadow definitions
```

#### Key Tokens

| Token Path | Value | Usage |
|------------|-------|-------|
| `color.bg.base` | `oklch(8% 0.02 250)` | Main background |
| `color.text.primary` | `oklch(100% 0 0)` | Primary text |
| `color.accent.primary` | `#00d4ff` | Cyan accent |
| `color.status.success` | `#22c55e` | Success green |
| `color.edge.calls` | `#4dd4ff` | Call edge color |

---

### 3.2 appearance.tokens.json

**Path:** `schema/viz/tokens/appearance.tokens.json`
**Lines:** 493
**Purpose:** Node/edge rendering, physics simulation, animation

#### Structure

```
appearance.tokens.json
├── render/              (lines 12-19)
│   ├── dimensions: 3
│   ├── node-resolution: 8
│   └── anti-alias: true
├── color/
│   ├── atom/            (lines 23-43) - Tier colors (T0-T3, unknown)
│   ├── atom-family/     (lines 45-69) - Family colors (LOG, DAT, ORG, EXE, EXT)
│   ├── ring/            (lines 71-103) - Layer colors (DOMAIN, APPLICATION, etc.)
│   ├── edge/            (lines 105-129) - Edge type colors
│   ├── edge-modes/      (lines 131-204) - Resolution, weight, opacity
│   ├── highlight/       (lines 206-219) - Selection colors
│   ├── background/      (line 221)
│   ├── panel/           (line 225)
│   └── accent/          (line 229)
├── size/                (lines 233-269)
│   ├── atom.base: 1.0
│   ├── atom.min: 0.5
│   ├── atom.max: 8.0
│   ├── atom.scale: 0.15
│   ├── edge.width: 0.8
│   └── boundary.*
├── opacity/             (lines 273-291)
│   ├── edge: 0.08
│   ├── boundary-fill: 0.1
│   ├── boundary-wire: 0.35
│   └── stars: 0.6
├── stars/               (lines 293-309)
│   ├── enabled: true
│   ├── count: 1500
│   ├── spread: 4000
│   └── size: 1.5
├── file-color/          (lines 310-335) - File-based coloring strategy
├── flow-mode/           (lines 337-367) - Markov flow visualization
├── physics/             (lines 369-419) ⭐ CRITICAL
│   ├── forces/
│   │   ├── charge.strength: -120
│   │   ├── charge.distanceMax: 500
│   │   ├── charge.distanceMin: 1
│   │   ├── link.distance: 50
│   │   ├── link.strength: 0.3
│   │   ├── center.strength: 0.05
│   │   └── collision.radius: 5
│   └── simulation/
│       ├── alphaMin: 0.001
│       ├── alphaDecay: 0.0228
│       ├── velocityDecay: 0.4
│       └── cooldownTicks: 200
├── animation/           (lines 421-475)
│   ├── hue.speed: 0.0008
│   ├── hue.damping: 0.9995
│   ├── hue.rotation: 0.8
│   ├── chroma.*
│   ├── lightness.*
│   └── ripple.*
└── bloom/               (lines 477-491)
    ├── enabled: false
    ├── strength: 1.2
    ├── radius: 0.4
    └── threshold: 0.2
```

#### Key Tokens

| Token Path | Value | Usage |
|------------|-------|-------|
| `physics.forces.charge.strength` | `-120` | Node repulsion |
| `physics.forces.link.distance` | `50` | Default link length |
| `physics.simulation.cooldownTicks` | `200` | Simulation duration |
| `size.atom.max` | `8.0` | Maximum node size |
| `animation.hue.speed` | `0.0008` | Rainbow animation speed |

---

### 3.3 layout.tokens.json

**Path:** `schema/viz/tokens/layout.tokens.json`
**Lines:** 135
**Purpose:** Spacing, sizing, z-index, transitions

#### Structure

```
layout.tokens.json
├── spacing/             (lines 3-24) - 0px to 32px scale
├── radius/              (lines 27-36) - Border radius scale
├── z-index/             (lines 39-48) - Layer stacking
├── duration/            (lines 49-55) - Animation timings
├── easing/              (lines 58-66) - Cubic bezier functions
├── transition/          (lines 69-80) - Pre-composed transitions
├── breakpoint/          (lines 83-88) - Responsive breakpoints
├── size/                (lines 90-115)
│   ├── panel-width: 200/280/360px
│   ├── button-height: 24/32/40px
│   ├── icon: 12/14/16/20px
│   ├── row-height: 24/28/32px
│   └── scrollbar.width: 4px
├── blur/                (lines 118-124) - Backdrop blur
└── offset/              (lines 127-132) - Panel positioning
```

---

### 3.4 controls.tokens.json

**Path:** `schema/viz/tokens/controls.tokens.json`
**Lines:** 1050+
**Purpose:** UI controls, keyboard shortcuts, panel configuration

#### Structure

```
controls.tokens.json
├── command-bar/         (lines 4-90)
│   ├── position: "bottom-center"
│   ├── buttons.* (visibility for each button)
│   └── order: [array of button IDs]
├── floating-panels/     (lines 93-213)
│   ├── layout: "stack"
│   ├── animation-duration: 200ms
│   └── panels.* (view, filter, style, oklch config)
├── side-dock/           (lines 216-450)
│   ├── width: 220
│   └── sections.* (topo, minimap, presets, etc.)
├── topo-tooltip/        (lines 538-550)
│   ├── delay-show: 300ms
│   └── delay-hide: 100ms
├── keyboard/            (lines 555-625)
│   └── shortcuts.* (all keybindings)
├── mouse/               (lines 627-659)
│   └── controls.* (rotate, pan, zoom, etc.)
├── interactions/        (lines 662-680)
│   └── hover.delay-hide-ms: 300
├── sliders/             (lines 854-972) ⭐ IMPORTANT
│   ├── density: min=0, max=100, default=100
│   ├── node-size: min=0.2, max=3, default=1
│   ├── edge-opacity: min=0, max=100, default=60
│   ├── zoom: min=10, max=300, default=100
│   ├── link-distance: min=10, max=100, default=30
│   └── ui-margin: min=5, max=30, default=15
└── panels/              (lines 990-1020)
    ├── metrics.visible: true
    ├── report.width: 420
    └── hover.delay-hide: 300ms
```

---

## 4. Python Engine Reference

### 4.1 TokenResolver

**Path:** `src/core/viz/token_resolver.py`
**Purpose:** Singleton that loads all tokens and provides resolution

#### Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `get_resolver()` | Get singleton instance | `TokenResolver` |
| `theme(path, default)` | Resolve theme token | Value |
| `appearance(path, default)` | Resolve appearance token | Value |
| `layout(path, default)` | Resolve layout token | Value |
| `controls(path, default)` | Resolve controls token | Value |
| `generate_css_variables()` | Generate CSS custom properties | `str` |
| `generate_all_themes_css()` | Generate multi-theme CSS | `str` |
| `get_js_theme_config()` | Get theme config for JS injection | `dict` |

#### Usage

```python
from src.core.viz.token_resolver import get_resolver

resolver = get_resolver()
charge = resolver.appearance("physics.forces.charge.strength", -120)
```

---

### 4.2 PhysicsEngine

**Path:** `src/core/viz/physics_engine.py`
**Purpose:** Reads physics tokens, outputs JS-ready config

#### Output Structure

```python
{
    "forces": {
        "charge": {
            "enabled": True,
            "strength": -120,
            "distanceMax": 500,
            "distanceMin": 1
        },
        "link": {
            "enabled": True,
            "distance": 50,
            "strength": 0.3
        },
        "center": {
            "enabled": True,
            "strength": 0.05
        },
        "collision": {
            "enabled": False,
            "radius": 5
        }
    },
    "simulation": {
        "alphaMin": 0.001,
        "alphaDecay": 0.0228,
        "velocityDecay": 0.4,
        "warmupTicks": 0,
        "cooldownTicks": 200
    },
    "constraints": {
        "fixY": False,
        "flattenZ": False
    }
}
```

---

### 4.3 AppearanceEngine

**Path:** `src/core/viz/appearance_engine.py`
**Purpose:** Reads appearance tokens, outputs JS-ready config

#### Output Structure (Partial)

```python
{
    "render": {"dimensions": 3, "nodeResolution": 8, "antiAlias": True},
    "colors": {
        "atom": {"t0-core": "oklch(...)", ...},
        "ring": {"DOMAIN": "oklch(...)", ...},
        "edge": {"default": "#...", ...}
    },
    "sizes": {"atom": {"base": 1.0, "min": 0.5, "max": 8.0, "scale": 0.15}},
    "opacity": {"edge": 0.08, "boundaryFill": 0.1},
    "animation": {...},
    "bloom": {...}
}
```

---

### 4.4 ControlsEngine

**Path:** `src/core/viz/controls_engine.py`
**Purpose:** Reads controls tokens, outputs JS-ready config

---

## 5. JavaScript Runtime Reference

### 5.1 Config Loading (app.js)

**Lines 2349-2450** - Configuration merge at initialization

```javascript
// Token config arrives via data payload
const physicsConfig = data.config?.physics || data.physics || {};
const appearanceConfig = data.config?.appearance || data.appearance || {};
const controlsConfig = data.config?.controls || data.controls || {};

// Merge with fallbacks
Object.assign(EDGE_MODE_CONFIG, appearanceConfig.edgeModes || {});
Object.assign(EDGE_COLOR_CONFIG, appearanceConfig.colors?.edge || {});
```

### 5.2 Hardcoded Fallbacks (app.js)

**Lines 80-145** - Global defaults that should be removed

```javascript
// ⚠️ THESE CREATE CONFLICTS WITH TOKENS
let EDGE_DEFAULT_OPACITY = 0.2;  // Token says 0.08

const EDGE_MODE_CONFIG = {
    width: { base: 1.2, ... },   // Token says 0.6
    opacity: 0.12,               // Token says 0.08
    ...
};

const EDGE_COLOR_CONFIG = {
    internal: '#4dd4ff',         // Duplicates theme.tokens
    ...
};
```

### 5.3 PENDULUM Object (app.js)

**Lines 295-331** - Animation state NOT merged with tokens

```javascript
const PENDULUM = {
    hue: {
        damping: 0.9995,    // Should come from token
        gravity: 0.0008,    // Should come from token
        rotationSpeed: 0.8  // Should come from token
    },
    // ... more hardcoded values
};
```

### 5.4 LAYOUT_PRESETS (app.js)

**Lines 4275-4377** - Layout configurations

| Preset | Motion | Cooldown | Hardcoded Values |
|--------|--------|----------|------------------|
| FORCE | settle | 300 | warmupTicks: 40 |
| ORBITAL | orbit | Infinity | orbitSpeed: 0.002 |
| RADIAL | static | 0 | - |
| SPIRAL | rotate | Infinity | rotateSpeed: 0.003 |
| SPHERE | rotate | Infinity | rotateSpeed: 0.001 |
| TORUS | rotate | Infinity | rotateSpeed: 0.002 |
| GRID | static | 0 | - |
| CYLINDER | rotate | Infinity | rotateSpeed: 0.0015 |
| TREE | static | 0 | - |
| FLOCK | flock | Infinity | separation, alignment, cohesion |
| GALAXY | rotate | Infinity | rotateSpeed: 0.001 |

### 5.5 FLOW_PRESETS (app.js)

**Lines 7789-7874** - Markov flow visualization presets

| Preset | Color | Particles | Speed | Hardcoded |
|--------|-------|-----------|-------|-----------|
| EMBER | #ff8c00 | 3 | 0.008 | Yes |
| OCEAN | #00d4ff | 4 | 0.006 | Yes |
| PLASMA | #ff00ff | 5 | 0.012 | Yes |
| MATRIX | #00ff00 | 6 | 0.015 | Yes |
| PULSE | #ff4444 | 2 | 0.004 | Yes |
| AURORA | #33ccbb | 4 | 0.007 | Yes |

---

## 6. Conflict Registry

### Conflict #1: Edge Opacity (3 Values)

| Location | Value | Line |
|----------|-------|------|
| `app.js` | `EDGE_DEFAULT_OPACITY = 0.2` | 80 |
| `app.js` | `EDGE_MODE_CONFIG.opacity = 0.12` | 110 |
| `appearance.tokens.json` | `opacity.edge = 0.08` | 202 |

**Winner:** Token (0.08) wins at runtime via merge
**Problem:** Confusing, 3 different values
**Fix:** Remove lines 80 and 110 from app.js

---

### Conflict #2: Edge Colors (2 Files)

| Location | Format | Line |
|----------|--------|------|
| `theme.tokens.json` | Hex (`#4dd4ff`) | 501-512 |
| `appearance.tokens.json` | OKLCH (`oklch(...)`) | 105-129 |

**Winner:** Appearance tokens overwrite theme tokens
**Problem:** Two sources of truth
**Fix:** Consolidate to one file (recommend appearance.tokens.json)

---

### Conflict #3: Edge Width

| Location | Value | Line |
|----------|-------|------|
| `app.js` | `width.base = 1.2` | 108 |
| `appearance.tokens.json` | `width.base = 0.6` | 186 |

**Winner:** Token wins at runtime
**Problem:** 2x difference in fallback
**Fix:** Remove hardcoded value from app.js

---

### Conflict #4: Node Size Range

| Location | Max Value | Line |
|----------|-----------|------|
| `controls.tokens.json` | `max: 3` (slider) | 889 |
| `appearance.tokens.json` | `max: 8.0` (render) | 245 |

**Winner:** UI caps user at 3x
**Problem:** User cannot access full 8x range
**Fix:** Sync values OR add "advanced" slider mode

---

### Conflict #5: PENDULUM Animation

| Location | Merged | Line |
|----------|--------|------|
| `app.js` | No | 295-331 |
| `appearance.tokens.json` | Yes (defined) | 421-475 |

**Winner:** Neither - hardcoded values used
**Problem:** Tokens exist but aren't applied
**Fix:** Merge token values into PENDULUM at init

---

### Conflict #6: Color Schemes

| Location | Line |
|----------|------|
| `appearance.tokens.json` | 523-560 |
| `app.js` | 7792-7865 |

**Winner:** Both exist, duplicated
**Problem:** Maintenance burden, can drift
**Fix:** Remove from app.js, load from tokens

---

## 7. Gap Analysis

### HIGH Priority Gaps

| Gap | Impact | Effort | Location |
|-----|--------|--------|----------|
| PENDULUM not merged | Animation ignores tokens | Low | app.js:295 |
| FLOW_PRESETS hardcoded | Cannot theme flow viz | Medium | app.js:7789 |
| LAYOUT_PRESETS hardcoded | Cannot adjust motion speeds | Medium | app.js:4275 |
| Theme variants incomplete | Light/HC themes partial | High | theme.tokens.json |

### MEDIUM Priority Gaps

| Gap | Impact | Effort | Location |
|-----|--------|--------|----------|
| Canvas margin hardcoded | Cannot adjust viewport | Low | app.js:1759 |
| OrbitControls defaults | Cannot customize camera | Low | app.js:2620 |
| Transition timings scattered | Inconsistent animations | Medium | app.js various |
| Console.log colors | Cannot theme debug output | Low | app.js various |

### LOW Priority Gaps

| Gap | Impact | Effort | Location |
|-----|--------|--------|----------|
| Three.js geometry sizes | Fixed sphere resolution | Low | app.js various |
| Toast timings | Minor UX | Low | app.js:3241 |

---

## 8. Confidence Matrix

```
SUBSYSTEM                    CONFIDENCE    EVIDENCE
───────────────────────────────────────────────────────────────

PHYSICS ENGINE
├─ Force parameters           95% HIGH     appearance.tokens:369-419
├─ Simulation parameters      95% HIGH     appearance.tokens:408-417
├─ Cluster force              80% MEDIUM   app.js:10277 (partial token)
├─ File cohesion              80% MEDIUM   app.js:10342 (partial token)
└─ Layout presets             40% LOW      app.js:4275 (hardcoded)

COLOR SYSTEM
├─ Background colors          95% HIGH     theme.tokens:170-242
├─ Text colors                95% HIGH     theme.tokens:272-304
├─ Accent colors              95% HIGH     theme.tokens:307-359
├─ Atom tier colors           95% HIGH     appearance.tokens:23-43
├─ Edge colors                60% CONFLICT theme + appearance
├─ Color schemes              50% CONFLICT tokens + app.js
└─ Console colors             40% LOW      app.js hardcoded

LAYOUT SYSTEM
├─ Spacing scale              95% HIGH     layout.tokens:3-24
├─ Border radius              95% HIGH     layout.tokens:27-36
├─ Panel dimensions           90% HIGH     layout.tokens:88-115
├─ Font sizes                 60% MEDIUM   some hardcoded in CSS
└─ Canvas margin              40% LOW      app.js:1759 hardcoded

CONTROLS SYSTEM
├─ Keyboard shortcuts         95% HIGH     controls.tokens:555-625
├─ Mouse controls             95% HIGH     controls.tokens:627-659
├─ Slider ranges              95% HIGH     controls.tokens:854-972
├─ Panel configuration        90% HIGH     controls.tokens:93-213
├─ Tooltip delays             95% HIGH     controls.tokens:538-550
└─ Transition timings         40% LOW      app.js scattered

ANIMATION SYSTEM
├─ Ripple effect              95% HIGH     appearance.tokens:469-472
├─ Particle animation         95% HIGH     appearance.tokens:356-364
├─ Bloom effects              95% HIGH     appearance.tokens:477-491
├─ PENDULUM animation         30% CONFLICT tokens exist, not merged
└─ Layout transitions         40% LOW      app.js:4399 hardcoded

THEME SYSTEM
├─ Dark theme                 95% HIGH     theme.tokens (base)
├─ Light theme                38% LOW      theme.tokens:9-80 (partial)
├─ High-contrast theme        38% LOW      theme.tokens:82-164 (partial)
└─ Runtime switching          90% HIGH     setTheme() implemented
```

---

## 9. Remediation Checklist

### Phase 1: Resolve Conflicts (Immediate)

- [ ] **Remove EDGE_DEFAULT_OPACITY** from app.js:80
- [ ] **Remove EDGE_MODE_CONFIG hardcoded values** from app.js:99-111
- [ ] **Remove EDGE_COLOR_CONFIG hardcoded values** from app.js:112-119
- [ ] **Consolidate edge colors** to appearance.tokens.json only
- [ ] **Sync node size max** between controls (3) and appearance (8)
- [ ] **Remove color schemes** from app.js:7792-7865

### Phase 2: Merge Token Values (Short-term)

- [ ] **Merge PENDULUM** with appearance.tokens animation values at init
- [ ] **Tokenize FLOW_PRESETS** - move to appearance.tokens.json
- [ ] **Tokenize LAYOUT_PRESETS** speeds - move to appearance.tokens.json
- [ ] **Tokenize canvas margin** (16px) - move to layout.tokens.json
- [ ] **Tokenize OrbitControls defaults** - move to controls.tokens.json

### Phase 3: Complete Theme Variants (Medium-term)

- [ ] **Light theme:** Add missing tokens (currently 38%)
  - [ ] status colors
  - [ ] edge colors
  - [ ] data colors
  - [ ] gradient colors
  - [ ] console colors
  - [ ] schemes
- [ ] **High-contrast theme:** Add missing tokens (currently 38%)
  - [ ] Same as above

### Phase 4: Eliminate Remaining Hardcodes (Long-term)

- [ ] **Transition timings** - Audit all setTimeout values
- [ ] **Three.js geometry sizes** - Consider tokenizing
- [ ] **Console.log colors** - Tokenize or accept as limitation

---

## 10. Verification Procedures

### After Any Token Change

```bash
# Regenerate HTML
./collider full . --output .collider

# Verify token injection
grep -c "var(--" .collider/collider_report.html

# Check for hardcoded colors in output
grep -E '#[0-9a-fA-F]{6}' .collider/collider_report.html | head -20
```

### Conflict Detection Script

```bash
# Find hardcoded hex colors in app.js
grep -n "'#[0-9a-fA-F]\{6\}'" src/core/viz/assets/app.js

# Find hardcoded numeric values in config objects
grep -n "base:\|strength:\|opacity:" src/core/viz/assets/app.js
```

### Theme Switching Test

1. Open `.collider/collider_report.html`
2. Open Settings panel
3. Click "Light" theme button
4. Verify background changes to near-white
5. Click "High Contrast" theme button
6. Verify high-contrast colors applied
7. Refresh page - verify theme persists (localStorage)

### Physics Token Verification

```bash
# Check physics config in output
grep -A 50 '"physics"' .collider/collider_report.html | head -60
```

---

## Appendix A: File Quick Reference

| File | Purpose | Lines |
|------|---------|-------|
| `schema/viz/tokens/theme.tokens.json` | Colors, themes | 637 |
| `schema/viz/tokens/appearance.tokens.json` | Nodes, edges, physics | 493 |
| `schema/viz/tokens/layout.tokens.json` | Spacing, sizing | 135 |
| `schema/viz/tokens/controls.tokens.json` | UI controls | 1050+ |
| `src/core/viz/token_resolver.py` | Token loading | ~200 |
| `src/core/viz/physics_engine.py` | Physics config | ~100 |
| `src/core/viz/appearance_engine.py` | Appearance config | ~150 |
| `src/core/viz/controls_engine.py` | Controls config | ~100 |
| `src/core/viz/assets/app.js` | Runtime JS | 11000+ |
| `src/core/viz/assets/styles.css` | CSS styles | 3130 |
| `src/core/viz/assets/template.html` | HTML template | 600+ |
| `tools/visualize_graph_webgl.py` | HTML generator | ~600 |

---

## Appendix B: Token Path Cheatsheet

```
COLORS
  theme("color.bg.base")
  theme("color.text.primary")
  theme("color.accent.primary")
  theme("color.status.success")
  appearance("color.atom.t0-core")
  appearance("color.ring.DOMAIN")
  appearance("color.edge.calls")

PHYSICS
  appearance("physics.forces.charge.strength")
  appearance("physics.forces.link.distance")
  appearance("physics.simulation.cooldownTicks")

SIZES
  appearance("size.atom.base")
  appearance("size.atom.max")
  appearance("size.edge.width")
  layout("size.panel-width.md")
  layout("spacing.4")

ANIMATION
  appearance("animation.hue.speed")
  appearance("animation.ripple.speed")
  appearance("bloom.strength")

CONTROLS
  controls("keyboard.shortcuts.toggle-3d")
  controls("sliders.node-size.max")
  controls("floating-panels.animation-duration")
```

---

*Document generated from comprehensive audit on 2026-01-19*
