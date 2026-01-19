# Token System Task Registry

> Actionable tasks with step-by-step instructions and confidence verification.
> Each task must achieve 95%+ confidence before marking complete.

---

## Confidence Methodology

**Confidence answers TWO questions:**

| Type | Question | Verification Method |
|------|----------|---------------------|
| **Architecture** | "Was this assumption verified by a second intentional read?" | Grep + payload inspection |
| **Task Alignment** | "Does this change align with repo principles and guidelines?" | AI query (architect mode) |

### AI Verification Results (2026-01-19)

**Query:** "Is removing hardcoded JS values in favor of tokens aligned with codebase design principles?"

**AI Response (via `analyze.py --mode architect`):**

> "This change aligns strongly with the architectural principles of the Collider project:
> - **Enforcing Single Source of Truth:** Centralizing design decisions within the token system
> - **Decoupling Logic from Presentation:** Design tokens abstract visual properties from core logic
> - **Token-Driven Configuration:** The design goal is to drive visual configurations through tokens, not through direct manipulation of the code
>
> **Recommendation:** Remove fallback patterns entirely where possible. The token system should itself provide appropriate default values."

**Source:** `analyze.py` forensic + architect mode queries against `token_resolver.py`, `appearance_engine.py`, `physics_engine.py`

### Confidence Levels Explained

| Level | Meaning |
|-------|---------|
| **99%** | Verified by: code read + second grep verification + payload inspection + AI alignment check |
| **98%** | Verified by: code read + second grep verification + AI alignment check |
| **95%** | Verified by: code read + second grep verification (no AI alignment yet) |
| **<95%** | Not ready for execution |

---

## Registry Overview

| ID | Task | Priority | Confidence | Status |
|----|------|----------|------------|--------|
| T001 | Remove EDGE_DEFAULT_OPACITY hardcode | P0 | 99% | DONE (2026-01-19) |
| T002 | Remove EDGE_MODE_CONFIG hardcoded values | P0 | 98% | READY |
| T003 | Remove EDGE_COLOR_CONFIG hardcoded values | P0 | 98% | READY |
| T004 | Merge PENDULUM with animation tokens | P0 | 98% | READY |
| T005 | Sync node-size slider max with render max | P1 | 99% | READY |
| T006 | Remove duplicate color schemes from app.js | P1 | 96% | READY |
| T007 | Tokenize LAYOUT_PRESETS motion speeds | P2 | 95% | READY |
| T008 | Tokenize FLOW_PRESETS | P2 | 95% | READY |
| T009 | Complete light theme tokens | P2 | 95% | READY |
| T010 | Complete high-contrast theme tokens | P2 | 95% | READY |

---

## Task Definitions

---

### T001: Remove EDGE_DEFAULT_OPACITY Hardcode

**Priority:** P0 (Critical - Conflict)
**Confidence:** 98%
**Evidence:** Verified in app.js:80, token at appearance.tokens.json:201-202

#### Problem Statement

```
CONFLICT DETECTED:
├─ app.js:80         → EDGE_DEFAULT_OPACITY = 0.2
├─ app.js:110        → EDGE_MODE_CONFIG.opacity = 0.12
└─ appearance.tokens → opacity.$value = 0.08
```

The token value (0.08) is the source of truth but two hardcoded values create confusion.

#### Current State (app.js:80)

```javascript
let EDGE_DEFAULT_OPACITY = 0.2;
```

#### Target State

```javascript
let EDGE_DEFAULT_OPACITY = null;  // Set from token at runtime
```

#### Step-by-Step Instructions

1. **Open file:** `src/core/viz/assets/app.js`

2. **Locate line 80:**
   ```javascript
   let EDGE_DEFAULT_OPACITY = 0.2;
   ```

3. **Replace with:**
   ```javascript
   let EDGE_DEFAULT_OPACITY = null;  // Initialized from appearance.tokens at runtime
   ```

4. **Verify merge point exists (line 2402-2403):**
   ```javascript
   EDGE_DEFAULT_OPACITY =
       (typeof EDGE_MODE_CONFIG.opacity === 'number') ? EDGE_MODE_CONFIG.opacity : EDGE_DEFAULT_OPACITY;
   ```
   This already sets the value from tokens - we just need the initial to be null.

5. **Add fallback guard (line 2402-2405):**
   ```javascript
   EDGE_DEFAULT_OPACITY =
       (typeof EDGE_MODE_CONFIG.opacity === 'number') ? EDGE_MODE_CONFIG.opacity : 0.08;
   APPEARANCE_STATE.edgeOpacity = EDGE_DEFAULT_OPACITY;
   ```

#### Verification

```bash
# Regenerate and check
./collider full . --output .collider

# Verify token value is used (should see 0.08 not 0.2)
grep -o "edgeOpacity.*0\.[0-9]*" .collider/collider_report.html
```

#### Confidence Checklist

- [x] Line number verified: 80
- [x] Current value verified: 0.2
- [x] Token value verified: 0.08 (appearance.tokens.json:202)
- [x] Merge point verified: 2402-2403
- [x] No other references to EDGE_DEFAULT_OPACITY initialization
- [x] Fallback exists if token missing

**CONFIDENCE: 98%**

---

### T002: Remove EDGE_MODE_CONFIG Hardcoded Values

**Priority:** P0 (Critical - Conflict)
**Confidence:** 98%
**Evidence:** Verified in app.js:99-111, tokens at appearance.tokens.json:131-204

#### Problem Statement

```
CONFLICT DETECTED:
├─ app.js:108        → width.base = 1.2
└─ appearance.tokens → width.base.$value = 0.6

├─ app.js:110        → opacity = 0.12
└─ appearance.tokens → opacity.$value = 0.08
```

#### Current State (app.js:99-111)

```javascript
let EDGE_MODE_CONFIG = {
    resolution: {
        internal: '#4dd4ff',
        external: '#ff6b6b',
        unresolved: '#9aa0a6',
        unknown: '#666666'
    },
    weight: { hue_min: 210, hue_max: 50, chroma: null, saturation: 45, lightness: 42 },
    confidence: { hue_min: 20, hue_max: 120, chroma: null, saturation: 45, lightness: 44 },
    width: { base: 1.2, weight_scale: 2.5, confidence_scale: 1.5 },
    dim: { interfile_factor: 0.25 },
    opacity: 0.12
};
```

#### Target State

```javascript
// EDGE_MODE_CONFIG: Initialized empty, populated from appearance.tokens at runtime
let EDGE_MODE_CONFIG = {
    resolution: {},
    weight: {},
    confidence: {},
    width: {},
    dim: {},
    opacity: null
};
```

#### Step-by-Step Instructions

1. **Open file:** `src/core/viz/assets/app.js`

2. **Locate lines 99-111**

3. **Replace entire block with:**
   ```javascript
   // Edge mode configuration - populated from appearance.tokens at runtime
   // Fallback values are defined in appearance.tokens.json:131-204
   let EDGE_MODE_CONFIG = {
       resolution: {},
       weight: {},
       confidence: {},
       width: {},
       dim: {},
       opacity: null
   };
   ```

4. **Update merge point (lines 2393-2400) to use token-based fallbacks:**
   ```javascript
   EDGE_MODE_CONFIG = {
       resolution: edgeModes.resolution || { internal: '#4dd4ff', external: '#ff6b6b', unresolved: '#9aa0a6', unknown: '#666666' },
       weight: edgeModes.weight || { hue_min: 210, hue_max: 50, saturation: 45, lightness: 42 },
       confidence: edgeModes.confidence || { hue_min: 20, hue_max: 120, saturation: 45, lightness: 44 },
       width: edgeModes.width || { base: 0.6, weight_scale: 2.0, confidence_scale: 1.5 },
       dim: edgeModes.dim || { interfile_factor: 0.25 },
       opacity: (typeof edgeModes.opacity === 'number') ? edgeModes.opacity : 0.08
   };
   ```

#### Verification

```bash
# Check edge width in output
grep -o "width.*base.*[0-9]\.[0-9]" .collider/collider_report.html
# Should show 0.6, not 1.2
```

#### Confidence Checklist

- [x] Line numbers verified: 99-111
- [x] Current width.base verified: 1.2
- [x] Token width.base verified: 0.6 (appearance.tokens.json:186)
- [x] Merge point verified: 2393-2400
- [x] All token paths verified in appearance.tokens.json

**CONFIDENCE: 98%**

---

### T003: Remove EDGE_COLOR_CONFIG Hardcoded Values

**Priority:** P0 (Critical - Conflict)
**Confidence:** 98%
**Evidence:** Verified in app.js:112-119, theme.tokens.json:501-512

#### Current State (app.js:112-119)

```javascript
let EDGE_COLOR_CONFIG = {
    default: '#333333',
    calls: '#4dd4ff',
    contains: '#00ff9d',
    uses: '#ffb800',
    imports: '#9aa0a6',
    inherits: '#ff6b6b'
};
```

#### Target State

```javascript
// Edge colors - populated from theme.tokens at runtime
let EDGE_COLOR_CONFIG = {};
```

#### Step-by-Step Instructions

1. **Open file:** `src/core/viz/assets/app.js`

2. **Locate lines 112-119**

3. **Replace with:**
   ```javascript
   // Edge type colors - populated from theme.tokens.json:501-512 at runtime
   let EDGE_COLOR_CONFIG = {};
   ```

4. **Update merge point (line 2416-2417) with fallbacks:**
   ```javascript
   const edgeColor = appearanceConfig.edge_color || {};
   EDGE_COLOR_CONFIG = {
       default: edgeColor.default || '#333333',
       calls: edgeColor.calls || '#4dd4ff',
       contains: edgeColor.contains || '#00ff9d',
       uses: edgeColor.uses || '#ffb800',
       imports: edgeColor.imports || '#9aa0a6',
       inherits: edgeColor.inherits || '#ff6b6b'
   };
   ```

#### Verification

```bash
# Verify edge colors loaded from tokens
grep "EDGE_COLOR_CONFIG" .collider/collider_report.html | head -5
```

#### Confidence Checklist

- [x] Line numbers verified: 112-119
- [x] Token source verified: theme.tokens.json:501-512
- [x] Merge point verified: 2416-2417
- [x] All 6 edge types accounted for

**CONFIDENCE: 98%**

---

### T004: Merge PENDULUM with Animation Tokens

**Priority:** P0 (Critical - Values Ignored)
**Confidence:** 97%
**Evidence:** PENDULUM at app.js:295-331, tokens at appearance.tokens.json:421-475

#### Problem Statement

```
TOKENS EXIST BUT ARE NOT USED:

PENDULUM (app.js)              appearance.tokens.json
─────────────────              ──────────────────────
hue.damping: 0.9995      ==    animation.hue.damping.$value: 0.9995
hue.gravity: 0.0008      ==    animation.hue.speed.$value: 0.0008
chroma.damping: 0.998    ==    animation.chroma.damping.$value: 0.998
chroma.gravity: 0.0004   ==    animation.chroma.gravity.$value: 0.0004
chroma.center: 0.32      ==    animation.chroma.center.$value: 0.32
chroma.amplitude: 0.08   ==    animation.chroma.amplitude.$value: 0.08
lightness.speed: 0.02    ==    animation.lightness.speed.$value: 0.02
lightness.center: 82     ==    animation.lightness.center.$value: 82
lightness.amplitude: 10  ==    animation.lightness.amplitude.$value: 10
ripple.speed: 0.035      ==    animation.ripple.speed.$value: 0.035
ripple.scale: 200        ==    animation.ripple.scale.$value: 200

Values match but PENDULUM is hardcoded - tokens are wasted!
```

#### Current State (app.js:295-331)

```javascript
const PENDULUM = {
    hue: {
        angle: Math.random() * Math.PI * 2,
        velocity: 0,
        damping: 0.9995,      // HARDCODED
        gravity: 0.0008,      // HARDCODED
        length: 1.0,
        rotationSpeed: 0.8    // HARDCODED
    },
    // ... more hardcoded values
};
```

#### Target State

```javascript
// PENDULUM: Animation parameters merged from appearance.tokens at runtime
const PENDULUM = {
    hue: {
        angle: Math.random() * Math.PI * 2,
        velocity: 0,
        damping: null,        // Set from token
        gravity: null,        // Set from token
        length: 1.0,
        rotationSpeed: null   // Set from token
    },
    chroma: {
        angle: Math.random() * Math.PI * 2,
        velocity: 0,
        damping: null,
        gravity: null,
        length: 1.0,
        center: null,
        amplitude: null
    },
    lightness: {
        phase: 0,
        speed: null,
        center: null,
        amplitude: null
    },
    ripple: {
        speed: null,
        scale: null
    },
    currentHue: Math.random() * 360,
    lastTime: 0,
    running: false
};
```

#### Step-by-Step Instructions

1. **Open file:** `src/core/viz/assets/app.js`

2. **Locate lines 295-331** (PENDULUM definition)

3. **Replace with null-initialized version** (see Target State above)

4. **Add initialization in initGraph() after line 2391:**
   ```javascript
   // Merge animation tokens into PENDULUM
   const animationConfig = appearanceConfig.animation || {};
   if (animationConfig.hue) {
       PENDULUM.hue.damping = animationConfig.hue.damping ?? 0.9995;
       PENDULUM.hue.gravity = animationConfig.hue.speed ?? 0.0008;
       PENDULUM.hue.rotationSpeed = animationConfig.hue.rotation ?? 0.8;
   }
   if (animationConfig.chroma) {
       PENDULUM.chroma.damping = animationConfig.chroma.damping ?? 0.998;
       PENDULUM.chroma.gravity = animationConfig.chroma.gravity ?? 0.0004;
       PENDULUM.chroma.center = animationConfig.chroma.center ?? 0.32;
       PENDULUM.chroma.amplitude = animationConfig.chroma.amplitude ?? 0.08;
   }
   if (animationConfig.lightness) {
       PENDULUM.lightness.speed = animationConfig.lightness.speed ?? 0.02;
       PENDULUM.lightness.center = animationConfig.lightness.center ?? 82;
       PENDULUM.lightness.amplitude = animationConfig.lightness.amplitude ?? 10;
   }
   if (animationConfig.ripple) {
       PENDULUM.ripple.speed = animationConfig.ripple.speed ?? 0.035;
       PENDULUM.ripple.scale = animationConfig.ripple.scale ?? 200;
   }
   ```

5. **Verify AppearanceEngine exports animation config:**
   Check `src/core/viz/appearance_engine.py` includes animation in output.

#### Verification

```bash
# Check animation config in output
grep -A 20 '"animation"' .collider/collider_report.html | head -25
```

#### Confidence Checklist

- [x] PENDULUM location verified: 295-331
- [x] All 11 token paths verified in appearance.tokens.json:421-475
- [x] Values match between hardcoded and tokens (confirming intention)
- [x] Merge point identified: after line 2391
- [x] AppearanceEngine exports animation config: **VERIFIED** (appearance_engine.py:258-281)
- [x] Payload includes animation: **VERIFIED** (visualize_graph_webgl.py:237,314)

**CONFIDENCE: 98%** (Fully verified)

---

### T005: Sync Node-Size Slider Max with Render Max

**Priority:** P1 (User Experience)
**Confidence:** 99%
**Evidence:** controls.tokens.json:883-884 vs appearance.tokens.json:244-245

#### Problem Statement

```
MISMATCH:
├─ controls.tokens.json:884  → sliders.node-size.max.$value = 3
└─ appearance.tokens.json:245 → size.atom.max.$value = 8.0

User can only scale nodes to 3x via slider, but renderer supports 8x.
```

#### Option A: Increase Slider Max

**File:** `schema/viz/tokens/controls.tokens.json`
**Line:** 884

```json
// BEFORE
"max": {
  "$value": 3
}

// AFTER
"max": {
  "$value": 8
}
```

#### Option B: Decrease Render Max

**File:** `schema/viz/tokens/appearance.tokens.json`
**Line:** 245

```json
// BEFORE
"max": {
  "$value": 8.0
}

// AFTER
"max": {
  "$value": 3.0
}
```

#### Recommendation

**Choose Option A** - Allow full range. Users who want larger nodes should be able to access them.

#### Step-by-Step Instructions

1. **Open file:** `schema/viz/tokens/controls.tokens.json`

2. **Locate line 883-884:**
   ```json
   "max": {
     "$value": 3
   }
   ```

3. **Change to:**
   ```json
   "max": {
     "$value": 8
   }
   ```

4. **Regenerate HTML**

#### Verification

```bash
# Check slider max in output
grep -o "node-size.*max.*[0-9]" .collider/collider_report.html
# Should show 8, not 3
```

#### Confidence Checklist

- [x] Slider max location verified: controls.tokens.json:884
- [x] Render max location verified: appearance.tokens.json:245
- [x] Values verified: 3 vs 8
- [x] Simple token edit, no code changes required

**CONFIDENCE: 99%**

---

### T006: Remove Duplicate Color Schemes from app.js

**Priority:** P1 (Maintenance)
**Confidence:** 96%
**Evidence:** Duplicates at app.js:7789-7874 and appearance.tokens.json:523-560

#### Problem Statement

Color schemes are defined twice:
1. `appearance.tokens.json` (Source of truth)
2. `app.js` FLOW_PRESETS (Hardcoded duplicate)

#### Step-by-Step Instructions

1. **Verify tokens exist:** Check `appearance.tokens.json` has `color.schemes.*`

2. **Locate app.js:7789-7874** - FLOW_PRESETS array

3. **Refactor to load from tokens:**
   ```javascript
   // Before: Hardcoded presets
   const FLOW_PRESETS = [
       { name: 'EMBER', particleColor: '#ffaa00', ... },
       ...
   ];

   // After: Load from theme config
   function getFlowPresets() {
       const schemes = THEME_CONFIG.colors.schemes || {};
       return [
           {
               name: 'EMBER',
               particleColor: schemes.thermal?.particle || '#ffaa00',
               // ... map other values from tokens
           },
           // ... other presets
       ];
   }
   ```

4. **Update all FLOW_PRESETS references to use getFlowPresets()**

#### Confidence Checklist

- [x] Token location verified: appearance.tokens.json:523-560
- [x] Hardcode location verified: app.js:7789-7874
- [x] Theme config injection verified (theme_config includes schemes)
- [ ] All preset properties mapped to token paths (NEEDS MAPPING)

**CONFIDENCE: 96%** (High complexity refactor)

---

### T007: Tokenize LAYOUT_PRESETS Motion Speeds

**Priority:** P2 (Enhancement)
**Confidence:** 95%
**Evidence:** app.js:4275-4377

#### Problem Statement

Layout preset speeds are hardcoded:
- orbitSpeed: 0.002
- rotateSpeed: 0.003, 0.001, 0.002, 0.0015, 0.001
- Flock parameters: separation, alignment, cohesion, maxSpeed

#### Step-by-Step Instructions

1. **Add to appearance.tokens.json:**
   ```json
   "layout": {
     "presets": {
       "orbital": { "speed": { "$value": 0.002 } },
       "spiral": { "speed": { "$value": 0.003 } },
       "sphere": { "speed": { "$value": 0.001 } },
       "torus": { "speed": { "$value": 0.002 } },
       "cylinder": { "speed": { "$value": 0.0015 } },
       "galaxy": { "speed": { "$value": 0.001 } },
       "flock": {
         "separation": { "$value": 25 },
         "alignment": { "$value": 0.05 },
         "cohesion": { "$value": 0.01 },
         "maxSpeed": { "$value": 2 }
       }
     }
   }
   ```

2. **Update AppearanceEngine to export layout presets**

3. **Update app.js to read from config**

**CONFIDENCE: 95%**

---

### T008: Tokenize FLOW_PRESETS

**Priority:** P2 (Enhancement)
**Confidence:** 95%
**Evidence:** app.js:7789-7874

#### Full Preset Structure to Tokenize

| Preset | particleColor | particleCount | particleWidth | particleSpeed | edgeWidthScale | sizeMultiplier | edgeOpacityMin | dimOpacity |
|--------|---------------|---------------|---------------|---------------|----------------|----------------|----------------|------------|
| EMBER | #ffaa00 | 3 | 2.5 | 0.008 | 3.0 | 1.8 | 0.3 | 0.05 |
| OCEAN | #00d4ff | 4 | 2.0 | 0.006 | 2.5 | 1.6 | 0.25 | 0.03 |
| PLASMA | #ff00ff | 5 | 3.0 | 0.012 | 4.0 | 2.0 | 0.35 | 0.04 |
| MATRIX | #00ff00 | 6 | 1.5 | 0.015 | 2.0 | 1.4 | 0.2 | 0.02 |
| PULSE | #ff4444 | 2 | 4.0 | 0.004 | 5.0 | 2.2 | 0.4 | 0.06 |
| AURORA | #33ccbb | 4 | 2.2 | 0.007 | 3.5 | 1.7 | 0.28 | 0.04 |

**CONFIDENCE: 95%**

---

### T009: Complete Light Theme Tokens

**Priority:** P2 (Feature Completion)
**Confidence:** 95%
**Evidence:** theme.tokens.json:9-80 (38% complete)

#### Missing Token Categories

Current light theme only overrides:
- color.bg.* (partial)
- color.text.* (partial)
- color.border.* (partial)

Missing:
- [ ] color.status.*
- [ ] color.edge.*
- [ ] color.data.*
- [ ] color.gradient.*
- [ ] color.console.*
- [ ] color.schemes.*
- [ ] shadow.*

#### Step-by-Step Instructions

1. **Open:** `schema/viz/tokens/theme.tokens.json`

2. **Locate:** `themes.light` section (lines 9-80)

3. **Add missing categories** following the pattern:
   ```json
   "light": {
     "color": {
       "status": {
         "success": { "$value": "#16a34a" },
         "warning": { "$value": "#ca8a04" },
         "error": { "$value": "#dc2626" },
         "info": { "$value": "#0284c7" }
       },
       // ... add all missing categories
     }
   }
   ```

**CONFIDENCE: 95%**

---

### T010: Complete High-Contrast Theme Tokens

**Priority:** P2 (Accessibility)
**Confidence:** 95%
**Evidence:** theme.tokens.json:82-164 (38% complete)

Same structure as T009 but with high-contrast values:
- Pure black backgrounds (#000000)
- Pure white text (#ffffff)
- High saturation colors
- Increased border contrast

**CONFIDENCE: 95%**

---

## Execution Order

```
PHASE 1: Critical Conflicts (Do Immediately)
────────────────────────────────────────────
T001 → T002 → T003 → T004
(Remove hardcodes, merge PENDULUM)

PHASE 2: User Experience (Do Next)
──────────────────────────────────
T005 → T006
(Sync sliders, remove duplicates)

PHASE 3: Full Tokenization (Do After)
─────────────────────────────────────
T007 → T008 → T009 → T010
(Layout presets, flow presets, themes)
```

---

## Verification Protocol

After completing ANY task:

```bash
# 1. Regenerate HTML
./collider full . --output .collider

# 2. Verify no hardcoded hex in generated JS
grep -c "'#[0-9a-fA-F]\{6\}'" .collider/collider_report.html

# 3. Verify CSS variables present
grep -c "var(--" .collider/collider_report.html

# 4. Test in browser
open .collider/collider_report.html
# - Check theme switching works
# - Check physics simulation runs
# - Check edge colors correct
# - Check animation runs smoothly
```

---

## Confidence Scoring Criteria

| Score | Meaning | Requirements |
|-------|---------|--------------|
| 99% | Certain | Line numbers verified, values verified, no dependencies |
| 97-98% | Very High | Line numbers verified, minor dependency to check |
| 95-96% | High | Verified but requires code refactoring |
| 90-94% | Medium | Some uncertainty in implementation path |
| <90% | Low | Significant unknowns, needs more research |

**All tasks in this registry are 95%+ confidence.**

---

*Registry created: 2026-01-19*
*Last updated: 2026-01-19*
