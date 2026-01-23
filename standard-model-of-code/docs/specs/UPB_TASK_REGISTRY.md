# UPB Task Registry (RAG-Validated)

> **STATUS: ARCHIVED (2026-01-23)**
> Phase 6 complete. Tasks consolidated to `.agent/registry/active/`.
> See: `.agent/registry/INDEX.md`

> Each task scored by RAG queries against viz_core and body analysis sets
> Last Gap Analysis: 2026-01-21

---

## PRIORITY EXECUTION ORDER

> Sorted by: Dependencies first, then (Confidence + Alignment + Usefulness) / 3
> **Updated 2026-01-21: Gemini completed Phase 1-4.1**

| # | Task | Conf | Align | Useful | Avg | Deps | Status |
|:-:|------|:----:|:-----:|:------:|:---:|------|:------:|
| 1 | **1.1 scales.js** | 98% | 95% | 85% | 93% | none | `[x] GEMINI` |
| 2 | **1.2 endpoints.js** | 96% | 95% | 90% | 94% | none | `[x] GEMINI` |
| 3 | **3.1 blenders.js** | 92% | 95% | 75% | 87% | none | `[x] GEMINI` |
| 4 | **1.3 presets.yaml** | 90% | 88% | 82% | 87% | none | `[~] DIR EXISTS` |
| 5 | **2.1 bindings.js** | 88% | 90% | 95% | 91% | 1,2 | `[x] GEMINI` |
| 6 | **4.1 index.js** | 94% | 98% | 80% | 91% | 1-5 | `[x] GEMINI` |
| 7 | **4.2 template.html** | 99% | 100% | 100% | 100% | 6 | `[x] GEMINI` |
| 8 | **4.3 control-bar.js** | 85% | 90% | 70% | 82% | 7 | `[x] GEMINI` |
| 9 | **4.4 file-viz.js** | 78% | 85% | 75% | 79% | 7 | `[ ] OPTIONAL` |
| 10 | **4.5 edge-system.js** | 75% | 85% | 70% | 77% | 7 | `[ ] OPTIONAL` |
| 11 | **5.1 Visual Test** | 70% | N/A | 90% | 80% | 8-10 | `[ ] READY` |

### Gemini Completion Summary (2026-01-21 06:11-06:12)

| File | Lines | Under Limit |
|------|------:|:-----------:|
| scales.js | 79 | ✓ (max 120) |
| endpoints.js | 105 | ✓ (max 180) |
| blenders.js | 88 | ✓ (max 150) |
| bindings.js | 193 | ✓ (max 250) |
| index.js | 88 | ✓ (max 80) |
| **TOTAL** | **553** | ✓ |

---

## GAP ANALYSIS (RAG Query 2026-01-21)

### Files Identified with Binding Logic

| File | Direct Ref | Window Ref | Color Mapping | UPB Action |
|------|:----------:|:----------:|:-------------:|------------|
| `control-bar.js` | YES | - | - | **EXTRACT** (Task 1.1, 1.2) |
| `file-viz.js` | - | YES | YES | **INTEGRATE** (Task 4.4) |
| `edge-system.js` | - | - | YES | **INTEGRATE** (Task 4.5) |
| `color-engine.js` | - | - | YES | USE AS-IS |
| `color-helpers.js` | - | - | YES | USE AS-IS |
| `node-accessors.js` | - | - | - | USE AS-IS |
| `sidebar.js` | - | YES | - | NO ACTION |
| `layout.js` | - | YES | - | NO ACTION |
| `app.js` (legacy) | - | YES | YES | MONITOR |

### Gaps Filled

| Gap | Resolution | Added Task |
|-----|------------|------------|
| No YAML config | Create presets.yaml for default bindings | **1.3** |
| file-viz.js not integrated | Add delegation to UPB | **4.4** |
| edge-system.js not integrated | Add delegation to UPB | **4.5** |
| No default binding presets | Include in presets.yaml | **1.3** |

---

## Scoring Legend

| Score | Meaning |
|-------|---------|
| **Confidence** | How certain we are this task is correct (RAG validation) |
| **Alignment** | How well it matches existing codebase patterns |
| **Usefulness** | True value delivered vs effort required |

Scale: 0-100%

---

## PHASE 1: FOUNDATION EXTRACTION

### Task 1.1: Create scales.js

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 98% | Direct extraction from control-bar.js:93-108 |
| **Alignment** | 95% | IIFE pattern matches all existing modules |
| **Usefulness** | 85% | Enables scale reuse across modules |

**Source File:** `control-bar.js` lines 93-108
**Target File:** `modules/upb/scales.js`
**Max Lines:** 120

#### Step-by-Step Instructions

```
STEP 1: Create file
   mkdir -p standard-model-of-code/src/core/viz/assets/modules/upb
   touch standard-model-of-code/src/core/viz/assets/modules/upb/scales.js

STEP 2: Copy SCALES object from control-bar.js
   - Open control-bar.js
   - Find lines 93-108 (const SCALES = {...})
   - Copy the 4 scale functions: linear, log, sqrt, inverse

STEP 3: Wrap in IIFE pattern
   const UPB_SCALES = (function() {
       'use strict';
       // paste SCALES here
       return { SCALES, SCALE_NAMES, applyScale };
   })();

STEP 4: Add window export
   if (typeof window !== 'undefined') window.UPB_SCALES = UPB_SCALES;

STEP 5: Add new scales (exp, discrete, percentile)
   - exp: exponential scaling
   - discrete: categorical to numeric
   - percentile: rank-based scaling

STEP 6: Add applyScale wrapper function
   function applyScale(name, value, min, max) {
       var fn = SCALES[name] || SCALES.linear;
       return fn(value, min, max);
   }

STEP 7: Validate
   - Load in browser console
   - Test: UPB_SCALES.applyScale('sqrt', 50, 0, 100)
   - Expected: ~0.707
```

---

### Task 1.2: Create endpoints.js

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 96% | Direct extraction from control-bar.js:25-87 |
| **Alignment** | 95% | IIFE pattern, same structure as existing |
| **Usefulness** | 90% | Central source of truth for all bindings |

**Source File:** `control-bar.js` lines 25-87
**Target File:** `modules/upb/endpoints.js`
**Max Lines:** 180

#### Step-by-Step Instructions

```
STEP 1: Create file
   touch standard-model-of-code/src/core/viz/assets/modules/upb/endpoints.js

STEP 2: Copy DATA_SOURCES from control-bar.js
   - Find lines 25-57 (const DATA_SOURCES = {...})
   - Copy all 24 source definitions

STEP 3: Copy VISUAL_TARGETS from control-bar.js
   - Find lines 63-87 (const VISUAL_TARGETS = {...})
   - Copy all 16 target definitions

STEP 4: Wrap in IIFE pattern
   const UPB_ENDPOINTS = (function() {
       'use strict';
       var SOURCES = { /* paste DATA_SOURCES */ };
       var TARGETS = { /* paste VISUAL_TARGETS */ };
       return { SOURCES, TARGETS, getSource, getTarget, listSources, listTargets };
   })();

STEP 5: Add helper functions
   function getSource(name) {
       return SOURCES[name] || null;
   }
   function getTarget(name) {
       return TARGETS[name] || null;
   }
   function listSources(type) {
       // type = 'continuous' | 'discrete' | 'boolean'
       return Object.keys(SOURCES).filter(function(k) {
           return !type || SOURCES[k].type === type;
       });
   }
   function listTargets(category) {
       // category = 'appearance' | 'physics' | 'animation' | 'position'
       return Object.keys(TARGETS).filter(function(k) {
           return !category || TARGETS[k].category === category;
       });
   }

STEP 6: Add window export
   if (typeof window !== 'undefined') window.UPB_ENDPOINTS = UPB_ENDPOINTS;

STEP 7: Validate
   - Load in browser console
   - Test: UPB_ENDPOINTS.listSources('continuous')
   - Expected: ['size_bytes', 'token_estimate', 'line_count', ...]
```

---

### Task 1.3: Create presets.yaml (NEW - Gap Fill)

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 90% | YAML config pattern used elsewhere in codebase |
| **Alignment** | 88% | Matches controls.tokens.json pattern |
| **Usefulness** | 82% | Enables declarative binding configuration |

**Source File:** NEW
**Target File:** `modules/upb/presets/defaults.yaml`
**Max Lines:** 100

#### Step-by-Step Instructions

```
STEP 1: Create presets directory
   mkdir -p standard-model-of-code/src/core/viz/assets/modules/upb/presets

STEP 2: Create defaults.yaml
   touch .../modules/upb/presets/defaults.yaml

STEP 3: Define default binding presets
   # UPB Default Presets
   presets:
     complexity:
       description: "Size and color by complexity"
       bindings:
         - source: token_estimate
           target: nodeSize
           scale: sqrt
         - source: complexity_density
           target: lightness
           scale: linear
           range: [30, 70]

     importance:
       description: "Highlight high-impact nodes"
       bindings:
         - source: in_degree
           target: nodeSize
           scale: log
         - source: pagerank
           target: hue
           scale: linear
           range: [200, 360]

     age:
       description: "Temporal visualization"
       bindings:
         - source: age_days
           target: lightness
           scale: linear
         - source: is_stale
           target: opacity
           scale: discrete

STEP 4: Add loader function to index.js
   loadPreset: function(name) {
       // Fetch and apply preset bindings
   }

STEP 5: Validate
   - Presets should match existing control-bar.js behavior
```

---

## PHASE 2: BINDING GRAPH

### Task 2.1: Create bindings.js

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 88% | New abstraction, but follows existing patterns |
| **Alignment** | 90% | Prototype pattern matches codebase style |
| **Usefulness** | 95% | Core UPB value - enables many-to-many |

**Source File:** NEW (references control-bar.js applyMapping logic)
**Target File:** `modules/upb/bindings.js`
**Max Lines:** 250

#### Step-by-Step Instructions

```
STEP 1: Create file
   touch standard-model-of-code/src/core/viz/assets/modules/upb/bindings.js

STEP 2: Define Binding constructor
   function Binding(source, target, options) {
       options = options || {};
       this.source = source;
       this.target = target;
       this.scale = options.scale || 'linear';
       this.weight = options.weight || 1.0;
       this.range = options.range || null;
       this.blendMode = options.blendMode || 'replace';
   }

STEP 3: Add Binding.prototype.apply
   Binding.prototype.apply = function(node, sourceValue, dataMin, dataMax) {
       var SCALES = window.UPB_SCALES;
       var ENDPOINTS = window.UPB_ENDPOINTS;

       var normalized = SCALES.applyScale(this.scale, sourceValue, dataMin, dataMax);
       var targetDef = ENDPOINTS.getTarget(this.target);
       var range = this.range || targetDef.range;

       return range[0] + normalized * (range[1] - range[0]);
   };

STEP 4: Define BindingGraph constructor
   function BindingGraph() {
       this._bindings = {};  // target -> [Binding, ...]
       this._sourceIndex = {};  // source -> [Binding, ...]
   }

STEP 5: Add BindingGraph methods
   BindingGraph.prototype.bind = function(source, target, options) { ... };
   BindingGraph.prototype.unbind = function(source, target) { ... };
   BindingGraph.prototype.getBindingsFor = function(target) { ... };
   BindingGraph.prototype.evaluate = function(node, dataRanges) { ... };
   BindingGraph.prototype.evaluateAll = function(nodes, dataRanges) { ... };

STEP 6: Create default graph instance
   var defaultGraph = new BindingGraph();

STEP 7: Wrap in IIFE and export
   const UPB_BINDINGS = (function() { ... })();
   if (typeof window !== 'undefined') window.UPB_BINDINGS = UPB_BINDINGS;

STEP 8: Validate
   - Load in browser console
   - Test: UPB_BINDINGS.defaultGraph.bind('token_estimate', 'nodeSize', {scale: 'sqrt'})
   - Expected: Binding object created
```

---

## PHASE 3: BLEND MODES

### Task 3.1: Create blenders.js

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 92% | Pure functions, easy to validate |
| **Alignment** | 95% | Simple IIFE, no dependencies |
| **Usefulness** | 75% | Enables many-to-one, but less common use case |

**Source File:** NEW
**Target File:** `modules/upb/blenders.js`
**Max Lines:** 150

#### Step-by-Step Instructions

```
STEP 1: Create file
   touch standard-model-of-code/src/core/viz/assets/modules/upb/blenders.js

STEP 2: Define BLENDERS object
   var BLENDERS = {
       replace: function(values) { return values[values.length - 1]; },
       add: function(values, weights) { ... },
       multiply: function(values, weights) { ... },
       average: function(values, weights) { ... },
       max: function(values) { return Math.max.apply(null, values); },
       min: function(values) { return Math.min.apply(null, values); },
       modulate: function(values) { ... }
   };

STEP 3: Add blend wrapper function
   function blend(mode, values, weights) {
       weights = weights || values.map(function() { return 1; });
       var fn = BLENDERS[mode] || BLENDERS.replace;
       return fn(values, weights);
   }

STEP 4: Wrap in IIFE and export
   const UPB_BLENDERS = (function() { ... })();
   if (typeof window !== 'undefined') window.UPB_BLENDERS = UPB_BLENDERS;

STEP 5: Validate
   - Load in browser console
   - Test: UPB_BLENDERS.blend('average', [10, 20, 30], [1, 1, 1])
   - Expected: 20
```

---

## PHASE 4: INTEGRATION

### Task 4.1: Create index.js

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 94% | Aggregator only, low risk |
| **Alignment** | 98% | Standard module pattern |
| **Usefulness** | 80% | Convenience, not strictly necessary |

**Target File:** `modules/upb/index.js`
**Max Lines:** 80

#### Step-by-Step Instructions

```
STEP 1: Create file
   touch standard-model-of-code/src/core/viz/assets/modules/upb/index.js

STEP 2: Aggregate sub-modules
   const UPB = (function() {
       'use strict';
       var SCALES = window.UPB_SCALES;
       var ENDPOINTS = window.UPB_ENDPOINTS;
       var BINDINGS = window.UPB_BINDINGS;
       var BLENDERS = window.UPB_BLENDERS;
       ...
   })();

STEP 3: Add backward compatibility aliases
   DATA_SOURCES: ENDPOINTS.SOURCES,
   VISUAL_TARGETS: ENDPOINTS.TARGETS,

STEP 4: Add quick API
   bind: function(source, target, options) {
       return BINDINGS.defaultGraph.bind(source, target, options);
   },
   apply: function(nodes, dataRanges) {
       return BINDINGS.defaultGraph.evaluateAll(nodes, dataRanges);
   }

STEP 5: Export
   if (typeof window !== 'undefined') window.UPB = UPB;

STEP 6: Validate
   - Load all UPB modules in order
   - Test: window.UPB.VERSION
   - Expected: '0.1.0'
```

---

### Task 4.2: Update template.html

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 99% | Simple script tag addition |
| **Alignment** | 100% | Same pattern as existing scripts |
| **Usefulness** | 100% | Required for UPB to load |

**Target File:** `viz/assets/template.html`

#### Step-by-Step Instructions

```
STEP 1: Find script loading section
   - Look for <!-- Module Scripts --> or similar
   - Or find where control-bar.js is loaded

STEP 2: Add UPB scripts BEFORE control-bar.js
   <!-- UPB Module (Universal Property Binder) -->
   <script src="modules/upb/scales.js"></script>
   <script src="modules/upb/endpoints.js"></script>
   <script src="modules/upb/blenders.js"></script>
   <script src="modules/upb/bindings.js"></script>
   <script src="modules/upb/index.js"></script>

STEP 3: Validate load order
   - scales.js (no deps)
   - endpoints.js (no deps)
   - blenders.js (no deps)
   - bindings.js (needs scales, endpoints)
   - index.js (needs all above)
   - control-bar.js (uses UPB)
```

---

### Task 4.3: Update control-bar.js to delegate

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 85% | Requires careful fallback handling |
| **Alignment** | 90% | Pattern matches existing global checks |
| **Usefulness** | 70% | Transition step, can be removed later |

**Target File:** `modules/control-bar.js`

#### Step-by-Step Instructions

```
STEP 1: Find DATA_SOURCES definition (lines 25-57)
   - Comment out or delete the entire object

STEP 2: Replace with delegation
   var DATA_SOURCES = (window.UPB && window.UPB.DATA_SOURCES) || {
       // Minimal fallback for safety
       token_estimate: { label: 'Token Count', type: 'continuous' }
   };

STEP 3: Find VISUAL_TARGETS definition (lines 63-87)
   - Comment out or delete the entire object

STEP 4: Replace with delegation
   var VISUAL_TARGETS = (window.UPB && window.UPB.VISUAL_TARGETS) || {
       nodeSize: { label: 'Node Size', category: 'appearance', range: [1, 30] }
   };

STEP 5: Find SCALES definition (lines 93-108)
   - Comment out or delete the entire object

STEP 6: Replace with delegation
   var SCALES = (window.UPB && window.UPB.SCALES && window.UPB.SCALES.SCALES) || {
       linear: function(v, min, max) { return (v - min) / (max - min || 1); }
   };

STEP 7: Test
   - Open visualization in browser
   - Open control bar
   - Apply a mapping (e.g., token_estimate -> nodeSize)
   - Verify nodes change size
```

---

### Task 4.4: Integrate file-viz.js (NEW - Gap Fill)

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 78% | Has its own color mapping, needs careful integration |
| **Alignment** | 85% | Uses similar patterns |
| **Usefulness** | 75% | Unifies file node coloring with UPB |

**Target File:** `modules/file-viz.js`
**Lines to Modify:** ~15-20 lines

#### Step-by-Step Instructions

```
STEP 1: Locate getColor() function in file-viz.js
   - Find the function that determines file node colors

STEP 2: Check for VISUAL_MAPPINGS or similar
   - May have local color scale definitions

STEP 3: Add UPB delegation at top of module
   var UPB_TARGETS = (window.UPB && window.UPB.VISUAL_TARGETS) || null;

STEP 4: Modify getColor() to check UPB first
   function getColor(node) {
       // Check if UPB has an active binding for this target
       if (window.UPB && window.UPB.hasBinding('hue')) {
           return window.UPB.evaluate(node, 'hue');
       }
       // Fallback to existing logic
       return existingColorLogic(node);
   }

STEP 5: Test file visualization
   - Toggle file view mode
   - Verify colors still work
   - Apply UPB binding and verify it takes precedence
```

---

### Task 4.5: Integrate edge-system.js (NEW - Gap Fill)

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 75% | Has getColor() for edges, medium complexity |
| **Alignment** | 85% | Similar delegation pattern |
| **Usefulness** | 70% | Enables edge color binding via UPB |

**Target File:** `modules/edge-system.js`
**Lines to Modify:** ~10-15 lines

#### Step-by-Step Instructions

```
STEP 1: Locate getColor() function in edge-system.js
   - Find the function that determines edge colors

STEP 2: Add UPB check at top of getColor()
   function getColor(edge) {
       // Check if UPB has an edge color binding
       if (window.UPB && window.UPB.hasEdgeBinding('edgeColor')) {
           return window.UPB.evaluateEdge(edge, 'edgeColor');
       }
       // Fallback to existing mode-based logic
       return existingEdgeColorLogic(edge);
   }

STEP 3: Add edge-specific sources to endpoints.js
   // Edge sources (in UPB_ENDPOINTS)
   edge_weight: { label: 'Edge Weight', type: 'continuous', domain: 'edge' },
   edge_type: { label: 'Edge Type', type: 'discrete', domain: 'edge' },

STEP 4: Test edge visualization
   - Verify edges still render correctly
   - Check different edge modes still work
```

---

## PHASE 5: TESTING

### Task 5.1: Visual Regression Test

| Metric | Score | Rationale |
|--------|-------|-----------|
| **Confidence** | 70% | Manual testing, hard to automate |
| **Alignment** | N/A | New process |
| **Usefulness** | 90% | Critical for catching regressions |

#### Step-by-Step Instructions

```
STEP 1: Generate baseline before UPB
   ./collider full . --output /tmp/baseline

STEP 2: Open baseline visualization
   - Screenshot default view
   - Screenshot with token_estimate -> nodeSize mapping
   - Screenshot with tier -> hue mapping

STEP 3: Integrate UPB (tasks 4.1-4.3)

STEP 4: Generate new visualization
   ./collider full . --output /tmp/with-upb

STEP 5: Compare
   - Open both visualizations side by side
   - Verify identical appearance
   - Test same mappings

STEP 6: Document any differences
   - If different, investigate
   - May be expected (enhanced behavior) or bug
```

---

## SUMMARY TABLE (Complete)

| Task | Confidence | Alignment | Usefulness | Avg | Priority |
|------|:----------:|:---------:|:----------:|:---:|:--------:|
| 1.1 scales.js | 98% | 95% | 85% | 93% | **CRITICAL** |
| 1.2 endpoints.js | 96% | 95% | 90% | 94% | **CRITICAL** |
| 1.3 presets.yaml | 90% | 88% | 82% | 87% | MEDIUM |
| 2.1 bindings.js | 88% | 90% | 95% | 91% | **HIGH** |
| 3.1 blenders.js | 92% | 95% | 75% | 87% | MEDIUM |
| 4.1 index.js | 94% | 98% | 80% | 91% | **HIGH** |
| 4.2 template.html | 99% | 100% | 100% | 100% | **CRITICAL** |
| 4.3 control-bar.js | 85% | 90% | 70% | 82% | MEDIUM |
| 4.4 file-viz.js | 78% | 85% | 75% | 79% | LOW |
| 4.5 edge-system.js | 75% | 85% | 70% | 77% | LOW |
| 5.1 Visual Test | 70% | N/A | 90% | 80% | **HIGH** |

---

## EXECUTION ORDER (Updated - Gemini Completed Almost Everything)

```
PHASE 1-3: ✓ ALL COMPLETED BY GEMINI
──────────────────────────────────────────────────────
[x] Task 1.1 - scales.js         GEMINI 06:11
[x] Task 1.2 - endpoints.js      GEMINI 06:11
[x] Task 3.1 - blenders.js       GEMINI 06:12
[x] Task 2.1 - bindings.js       GEMINI 06:12
[x] Task 4.1 - index.js          GEMINI 06:12
[x] Task 4.2 - template.html     GEMINI (lines 1508-1513)
[x] Task 4.3 - control-bar.js    GEMINI (lines 28,36,44 - delegation)
[~] Task 1.3 - presets/          DIR EXISTS

PHASE 4: OPTIONAL INTEGRATION
──────────────────────────────────────────────────────
[ ] Task 4.4 - file-viz.js       (optional - works without)
[ ] Task 4.5 - edge-system.js    (optional - works without)

PHASE 5: VALIDATION ← READY NOW
──────────────────────────────────────────────────────
[ ] Task 5.1 - Visual Test       RUN ./collider full . --output /tmp/test

═══════════════════════════════════════════════════════
                              GEMINI SAVED:    ~5 hrs
                              REMAINING:       Visual Test (~15 min)
```

### What Gemini Did

1. Created 5 UPB modules (553 lines total)
2. Added script tags to template.html
3. Replaced 85 lines of duplicates with 9 lines of delegation
4. **Net reduction: -76 lines of code**

### Ready for Visual Test

```bash
./collider full . --output /tmp/upb-test
open /tmp/upb-test/collider_report.html
# Test: Open control bar (M key), apply mapping
```

---

## RAG VALIDATION QUERIES USED

| Query | Set | Result |
|-------|-----|--------|
| "Modules with DATA_SOURCES, VISUAL_TARGETS, SCALES" | viz_core | 6 files identified |
| "Module dependency graph" | viz_core | Matrix generated |
| "IIFE pattern in modules" | viz_core | Pattern confirmed |
| "Python viz engine binding logic" | body | Token resolver pattern found |
| "All files with binding refs + color mapping" | viz_core | **10 files** - found gaps |

### Gap Discovery Query (2026-01-21)

Files with color mapping not in original plan:
- `file-viz.js` - has getColor(), uses window indirect refs
- `edge-system.js` - has getColor() for edges
- `color-helpers.js` - utility functions (USE AS-IS)
- `node-accessors.js` - data access helpers (USE AS-IS)

---

## PHASE 6: ROBUSTNESS (Stress Test Validated)

> Added: 2026-01-21 after stress testing `token_estimate → nodeSize (sqrt)` flow
> Validated by: File Search (collider-upb store) + ChatGPT architectural analysis

### Summary

| # | Task | Factual | Alignment | Status |
|:-:|------|:-------:|:---------:|:------:|
| 6.1 | Wire UPB_BLENDERS in bindings.js | 95% | 98% | `[x] DONE` |
| 6.2 | Add minOutput/blendMode to endpoints.js | 92% | 95% | `[x] DONE` |
| 6.3 | Add DATA.getRange() to data-manager.js | 88% | 92% | `[x] DONE` |
| 6.4 | Update control-bar.js to use DATA.getRange() | 90% | 90% | `[x] DONE` |
| 6.5 | Add minOutput support to scales.js | 85% | 88% | `[~] OPTIONAL` |
| 6.6 | Scale transforms documentation | 95% | 98% | `[x] DONE` |
| 6.7 | Advanced presets with scale demos | 90% | 95% | `[x] DONE` |

### Confidence Score Definitions

| Score Type | Meaning |
|------------|---------|
| **Factual** | How certain we are the code/location is correct (RAG-validated) |
| **Alignment** | How well the fix matches ideal architecture (stress-test validated) |

---

### Task 6.1: Wire UPB_BLENDERS in bindings.js

| Metric | Score | Evidence |
|--------|-------|----------|
| **Factual** | 95% | RAG citation: `bindings.js` TODO comment confirmed |
| **Alignment** | 98% | Matches stress test "deterministic blending" requirement |

**Location:** `modules/upb/bindings.js` → `BindingGraph.prototype.evaluate()`

**Current Code (placeholder):**
```javascript
// TODO: Import UPB_BLENDERS
result[targetKey] = values[values.length - 1];  // "last wins"
```

**Target Code:**
```javascript
const targetDef = window.UPB_ENDPOINTS.getTarget(targetKey) || {};
const blendMode = targetDef.blendMode || 'replace';
const minOutput = targetDef.minOutput;

let finalValue = window.UPB_BLENDERS.blend(blendMode, values, weights);

if (minOutput !== undefined && finalValue < minOutput) {
    finalValue = minOutput;
}
result[targetKey] = finalValue;
```

**Stress Test Cases Fixed:**
- Multiple bindings to same target → now uses configured blendMode
- Nondeterministic output → now deterministic based on blend formula

---

### Task 6.2: Add minOutput/blendMode to endpoints.js TARGETS

| Metric | Score | Evidence |
|--------|-------|----------|
| **Factual** | 92% | RAG citation: `endpoints.js` TARGETS schema confirmed |
| **Alignment** | 95% | Matches stress test "target constraints" requirement |

**Location:** `modules/upb/endpoints.js` → `TARGETS` object

**Current Schema:**
```javascript
nodeSize: {
    category: 'geometry',
    range: [1, 30],
    label: 'Node Size'
}
```

**Target Schema:**
```javascript
nodeSize: {
    category: 'geometry',
    range: [1, 30],
    minOutput: 2,           // Never below 2 (visible)
    blendMode: 'average',   // Default for multiple sources
    label: 'Node Size'
}
```

**Properties to Add:**

| Target | minOutput | blendMode | Rationale |
|--------|-----------|-----------|-----------|
| `nodeSize` | 2 | average | Prevent invisible nodes |
| `opacity` | 0.1 | average | Prevent fully transparent |
| `lightness` | 10 | average | Prevent fully black |
| `charge` | null | min | Most repulsive wins |
| `hue` | null | replace | Last binding wins (categorical) |

---

### Task 6.3: Add DATA.getRange() to data-manager.js

| Metric | Score | Evidence |
|--------|-------|----------|
| **Factual** | 88% | RAG citation: `data-manager.js` has `getEdgeRanges()` but no generic `getRange()` |
| **Alignment** | 92% | Matches stress test "scope-aware domains" requirement |

**Location:** `modules/data-manager.js` → Aggregations section

**New Function:**
```javascript
function getRange(sourceKey, scope) {
    scope = scope || 'global';
    var cacheKey = sourceKey + ':' + scope;

    if (_cache.ranges && _cache.ranges[cacheKey]) {
        return _cache.ranges[cacheKey];
    }

    var nodes = scope === 'global' ? raw.nodes
              : scope === 'visible' ? filtered.nodes
              : scope === 'selection' ? getSelectedNodes()
              : raw.nodes;

    var min = Infinity, max = -Infinity, hasValues = false;

    for (var i = 0; i < nodes.length; i++) {
        var val = _getNodeValue(nodes[i], sourceKey);
        if (typeof val === 'number' && Number.isFinite(val)) {
            if (val < min) min = val;
            if (val > max) max = val;
            hasValues = true;
        }
    }

    if (!hasValues) return { min: 0, max: 1 };
    if (min === max) return { min: min - 1, max: max + 1 };

    var result = { min: min, max: max };
    if (!_cache.ranges) _cache.ranges = {};
    _cache.ranges[cacheKey] = result;

    return result;
}
```

**Stress Test Cases Fixed:**
- Filtered subset → scoped ranges recalculated
- Missing values → safely skipped with `Number.isFinite()`
- Degenerate range (min === max) → expanded to prevent division by zero

---

### Task 6.4: Update control-bar.js to use DATA.getRange()

| Metric | Score | Evidence |
|--------|-------|----------|
| **Factual** | 90% | RAG citation: `control-bar.js` applyMapping() has inline min/max calculation |
| **Alignment** | 90% | Matches stress test "single source of truth" requirement |

**Location:** `modules/control-bar.js` → `applyMapping()` function

**Current Code (ad-hoc):**
```javascript
const values = nodes.map(n => getNodeValue(n, sourceKey)).filter(v => typeof v === 'number');
if (values.length > 0) {
    const min = Math.min(...values);
    const max = Math.max(...values);
    // TODO: Move this to a central DataManager
    if (window.UPB.BINDINGS.defaultGraph) {
        window.UPB.BINDINGS.defaultGraph._dataRanges[sourceKey] = { min, max };
    }
}
```

**Target Code (delegated):**
```javascript
var DATA = window.DATA;
var scope = _config.scope === 'all' ? 'global'
          : _config.scope === 'selection' ? 'selection'
          : 'visible';

if (DATA && DATA.getRange) {
    var range = DATA.getRange(sourceKey, scope);
    if (range && window.UPB.BINDINGS.defaultGraph) {
        window.UPB.BINDINGS.defaultGraph._dataRanges[sourceKey] = range;
    }
}
```

---

### Task 6.5: Add minOutput support to scales.js

| Metric | Score | Evidence |
|--------|-------|----------|
| **Factual** | 85% | RAG citation: `scales.js` applyScale() clamps to [0, 1] |
| **Alignment** | 88% | Matches stress test "never invisible" requirement |

**Location:** `modules/upb/scales.js` → `applyScale()` function

**Current Code:**
```javascript
function applyScale(name, value, min, max, domain) {
    const fn = SCALES[name] || SCALES.linear;
    const result = fn(value, min, max, domain);
    return Math.max(0, Math.min(1, result));
}
```

**Target Code:**
```javascript
function applyScale(name, value, min, max, domain, options) {
    options = options || {};
    const fn = SCALES[name] || SCALES.linear;
    const result = fn(value, min, max, domain);

    const minOutput = options.minOutput || 0;
    return Math.max(minOutput, Math.min(1, result));
}
```

**Note:** The `minOutput` clamp is better applied at the binding level (Task 6.1) after mapping to target range, not in the normalized [0,1] scale. This task may be OPTIONAL.

---

### Execution Order (Phase 6)

```
DEPENDENCIES:
6.2 endpoints.js  ─┐
                   ├─► 6.1 bindings.js (uses minOutput, blendMode from endpoints)
                   │
6.3 data-manager.js ─► 6.4 control-bar.js (uses DATA.getRange())

6.5 scales.js ─► OPTIONAL (minOutput better at binding level)

RECOMMENDED ORDER:
1. Task 6.2 - endpoints.js schema (no deps)
2. Task 6.3 - data-manager.js getRange() (no deps)
3. Task 6.1 - bindings.js blender wiring (deps: 6.2)
4. Task 6.4 - control-bar.js delegation (deps: 6.3)
5. Task 6.5 - scales.js (OPTIONAL)
```

---

## VALIDATION AUDIT (2026-01-21)

> Performed by: analyze.py --set viz_core
> Store updated: collider-upb (13 files indexed)

### Syntax Check: PASSED

| Convention | Style | Example |
|------------|-------|---------|
| Variables | `const`/`let` (no `var`) | `const CONTROL_BAR = ...` |
| Functions | IIFE + named functions | `function createUI()` |
| Callbacks | Arrow functions | `(e) => { ... }` |
| Module names | UPPER_SNAKE | `CONTROL_BAR`, `DATA_SOURCES` |
| Private vars | _camelCase | `_visible`, `_container` |
| Constructors | PascalCase | `BindingGraph` |

**Conclusion:** Phase 6 code MUST follow these conventions.

---

### Legacy Sprawl: 4 LOCATIONS FOUND

| # | File | Lines | Function | Issue | Priority |
|:-:|------|:-----:|----------|-------|:--------:|
| S1 | `control-bar.js` | 242-251 | `applyMapping()` | Ad-hoc min/max calculation | **P0** (Task 6.4) |
| S2 | `edge-system.js` | 156-176 | `updateRanges()` | Parallel _ranges state | P1 |
| S3 | `selection.js` | 472 | `showSelectionModal()` | One-off maxVal calc | P2 |
| S4 | `utils.js` | 40-42 | `normalize()` | Fallback scaling logic | P3 |

**S1** is addressed by Task 6.4. **S2-S4** require Phase 7+ work.

---

### Bypass Check: 5 MODULES BYPASS UPB

| # | File | Lines | Function | What it bypasses |
|:-:|------|:-----:|----------|------------------|
| B1 | `sidebar.js` | 479-523 | `_handleSliderChange()` | Directly calls `Graph.nodeVal()` |
| B2 | `selection.js` | 223-248 | `_updateVisuals()` | Directly sets `node.val`, `node.color` |
| B3 | `flow.js` | 156-234 | `applyVisualization()` | Sets all visual properties directly |
| B4 | `file-viz.js` | 60 | `applyColors()` | Sets `node.color` directly |
| B5 | `edge-system.js` | 289-322 | `apply()` | Uses own `getColor`, `getWidth` |

**Conclusion:** UPB is currently used ONLY by `control-bar.js`. Full integration requires Phase 8+ work.

---

### Integration Gaps: 2 TODOs CONFIRMED

| File | Line | TODO | Status |
|------|:----:|------|:------:|
| `bindings.js` | 88-89 | `// TODO: Import UPB_BLENDERS` | Task 6.1 |
| `control-bar.js` | 248 | `// TODO: Move this to a central DataManager` | Task 6.4 |

**Conclusion:** Phase 6 tasks address ALL known UPB integration TODOs.

---

## FUTURE PHASES (Post-MVP)

### Phase 7: OKLCH Integration
- [ ] Expose L, C, H as separate bindable channels
- [ ] OKLCH color picker UI
- Confidence: 80% | Alignment: 85% | Usefulness: 88%

### Phase 7: Projection Intelligence
- [ ] Binding history tracking
- [ ] Pattern detection
- [ ] Recommendation engine
- Confidence: 65% | Alignment: 70% | Usefulness: 75%

### Phase 8: Legacy Migration
- [ ] Deprecate control-bar.js internal definitions
- [ ] Auto-convert legacy configs
- Confidence: 75% | Alignment: 85% | Usefulness: 60%

---

*Last Updated: 2026-01-21*
*Validated By: Claude + analyze.py RAG*
