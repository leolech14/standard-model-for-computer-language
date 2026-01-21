# Universal Property Binder (UPB) - Legacy Sprawl Mapping

> Confidence-scored inventory of modules affected by UPB implementation

## Executive Summary

The UPB will consolidate and replace fragmented binding logic currently spread across 12+ files in both Python (server-side) and JavaScript (client-side). This document maps the legacy sprawl with confidence scores for impact assessment.

---

## Confidence Score Legend

| Score | Meaning | Action Required |
|-------|---------|-----------------|
| **95-100%** | Definite impact, core functionality overlap | REPLACE or MAJOR REFACTOR |
| **80-94%** | High impact, significant overlap | REFACTOR |
| **60-79%** | Medium impact, partial overlap | EXTEND or INTEGRATE |
| **40-59%** | Low impact, tangential relationship | MINOR UPDATES |
| **0-39%** | Minimal impact, independent | NO ACTION |

---

## JavaScript Modules (Client-Side)

### TIER 1: REPLACE (95-100% Confidence)

| File | Confidence | Current Responsibility | UPB Action |
|------|------------|------------------------|------------|
| `modules/control-bar.js` | **98%** | Defines `DATA_SOURCES` and `VISUAL_TARGETS` schema | **REPLACE** - UPB will own endpoint definitions |
| `modules/file-viz.js` | **95%** | Contains `VISUAL_MAPPINGS` with hardcoded bindings | **REPLACE** - UPB binding graph supersedes |

**Evidence from RAG:**
- `control-bar.js`: Defines complete schema for sources (size_bytes, pagerank, tier, etc.) and targets (hue, saturation, nodeSize, charge, etc.)
- `file-viz.js`: Contains `applyVisualMapping()` function with hardcoded scale functions

### TIER 2: REFACTOR (80-94% Confidence)

| File | Confidence | Current Responsibility | UPB Action |
|------|------------|------------------------|------------|
| `modules/color-engine.js` | **88%** | OKLCH color space implementation, gradients | **REFACTOR** - Expose L/C/H as separate bindable channels |
| `modules/edge-system.js` | **82%** | Edge color/width based on node properties | **REFACTOR** - Edge bindings via UPB |
| `app.js` | **80%** | Glue layer, coordinates engines | **REFACTOR** - Wire UPB as central binding authority |

**Evidence from RAG:**
- `color-engine.js`: Contains stop-based gradients and generator functions for OKLCH
- `edge-system.js`: Calculates edge color via interpolation, width via weight mapping

### TIER 3: EXTEND (60-79% Confidence)

| File | Confidence | Current Responsibility | UPB Action |
|------|------------|------------------------|------------|
| `modules/animation.js` | **72%** | Animation loop, pulse/rotation control | **EXTEND** - Add animation channel bindings |
| `modules/physics.js` | **68%** | Client-side physics simulation config | **EXTEND** - Add physics channel bindings |
| `modules/selection.js` | **65%** | Pendulum-driven selection colors | **EXTEND** - Integrate pendulum as binding source |

### TIER 4: INTEGRATE (40-59% Confidence)

| File | Confidence | Current Responsibility | UPB Action |
|------|------------|------------------------|------------|
| `modules/data-manager.js` | **55%** | Data loading and state management | **INTEGRATE** - UPB reads from DataManager |
| `modules/layouts.js` | **52%** | Layout algorithms (grid, radial, spiral) | **INTEGRATE** - Position bindings feed layout |
| `modules/core.js` | **48%** | Core utilities, initialization | **INTEGRATE** - UPB initialization hook |

---

## Python Modules (Server-Side)

### TIER 1: REFACTOR (80-94% Confidence)

| File | Confidence | Current Responsibility | UPB Action |
|------|------------|------------------------|------------|
| `viz/appearance_engine.py` | **92%** | Node/edge color and size calculation | **REFACTOR** - Move binding logic to UPB, keep rendering |
| `viz/controls_engine.py` | **85%** | UI control configuration generation | **REFACTOR** - UPB generates binding UI config |

**Evidence from RAG:**
- `appearance_engine.py`: Contains `apply_to_nodes()`, `apply_to_edges()` with coloring schemes
- `controls_engine.py`: Token-based UI configuration assembly

### TIER 2: EXTEND (60-79% Confidence)

| File | Confidence | Current Responsibility | UPB Action |
|------|------------|------------------------|------------|
| `viz/physics_engine.py` | **75%** | Physics simulation config generation | **EXTEND** - Physics params as binding targets |
| `viz/server.py` | **70%** | Orchestrates all engines, template rendering | **EXTEND** - Add UPB to orchestration |

### TIER 3: INTEGRATE (40-59% Confidence)

| File | Confidence | Current Responsibility | UPB Action |
|------|------------|------------------------|------------|
| `visualize_graph_webgl.py` | **58%** | HTML generation, asset concatenation | **INTEGRATE** - Include UPB module in build |
| `output_generator.py` | **45%** | Output file writing | **INTEGRATE** - UPB config in output |

---

## Binding Logic Distribution (Current State)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CURRENT BINDING SPRAWL                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PYTHON (Server)                    JAVASCRIPT (Client)                     │
│   ══════════════                     ══════════════════                      │
│                                                                              │
│   appearance_engine.py               control-bar.js                          │
│   ├─ Node coloring logic             ├─ DATA_SOURCES schema                  │
│   ├─ Edge coloring logic             ├─ VISUAL_TARGETS schema                │
│   └─ Size calculation                └─ Mapping validation                   │
│                                                                              │
│   physics_engine.py                  file-viz.js                             │
│   └─ Physics config                  ├─ VISUAL_MAPPINGS                      │
│                                      ├─ applyVisualMapping()                 │
│   controls_engine.py                 └─ Scale functions                      │
│   └─ UI config tokens                                                        │
│                                      color-engine.js                         │
│                                      ├─ OKLCH implementation                 │
│                                      ├─ Gradient stops                       │
│                                      └─ Generator functions                  │
│                                                                              │
│                                      edge-system.js                          │
│                                      ├─ Edge color interpolation             │
│                                      └─ Edge width mapping                   │
│                                                                              │
│                                      animation.js                            │
│                                      └─ Pulse/rotation params                │
│                                                                              │
│                                      physics.js                              │
│                                      └─ Force simulation config              │
│                                                                              │
│   PROBLEMS:                                                                  │
│   ─────────                                                                  │
│   1. Binding logic duplicated across Python and JS                          │
│   2. No single source of truth for mappings                                 │
│   3. Hardcoded scale functions in multiple files                            │
│   4. No blend mode support                                                  │
│   5. No many-to-many binding capability                                     │
│   6. No binding experimentation/intelligence                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## UPB Consolidation Target

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     UPB CONSOLIDATED ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PYTHON (Server)                    JAVASCRIPT (Client)                     │
│   ══════════════                     ══════════════════                      │
│                                                                              │
│   viz/upb/                           modules/upb/                            │
│   ├─ endpoints.py ◄──────────────────► endpoints.js                         │
│   │  (source/target definitions)      (mirrored definitions)                │
│   │                                                                         │
│   ├─ bindings.py ◄───────────────────► bindings.js                          │
│   │  (binding graph)                   (runtime binding eval)               │
│   │                                                                         │
│   ├─ blenders.py ◄───────────────────► blenders.js                          │
│   │  (blend mode impls)                (client blend eval)                  │
│   │                                                                         │
│   └─ presets/ ◄──────────────────────► presets/                             │
│      (YAML configs)                    (loaded at runtime)                  │
│                                                                              │
│   EXISTING MODULES (Delegated):                                             │
│   ─────────────────────────────                                             │
│   appearance_engine.py  → Uses UPB for color/size                           │
│   physics_engine.py     → Uses UPB for physics params                       │
│   color-engine.js       → Provides OKLCH conversion for UPB                 │
│   animation.js          → Reads animation params from UPB                   │
│                                                                              │
│   DEPRECATED:                                                                │
│   ───────────                                                               │
│   control-bar.js DATA_SOURCES    → Moved to upb/endpoints.js                │
│   control-bar.js VISUAL_TARGETS  → Moved to upb/endpoints.js                │
│   file-viz.js VISUAL_MAPPINGS    → Moved to upb/bindings.js                 │
│   file-viz.js applyVisualMapping → Replaced by upb/bindings.js              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Migration Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing visualizations | Medium | High | Maintain backward-compatible `VISUAL_MAPPINGS` parser |
| Performance regression | Low | Medium | Benchmark binding evaluation (<1ms per node) |
| UI confusion | Medium | Low | Gradual UI rollout, keep legacy controls as fallback |
| Python/JS sync issues | Medium | Medium | Single source YAML, generate both sides |

---

## Files Summary (Sorted by Confidence)

| Rank | File | Confidence | Action |
|------|------|------------|--------|
| 1 | `modules/control-bar.js` | 98% | REPLACE |
| 2 | `modules/file-viz.js` | 95% | REPLACE |
| 3 | `viz/appearance_engine.py` | 92% | REFACTOR |
| 4 | `modules/color-engine.js` | 88% | REFACTOR |
| 5 | `viz/controls_engine.py` | 85% | REFACTOR |
| 6 | `modules/edge-system.js` | 82% | REFACTOR |
| 7 | `app.js` | 80% | REFACTOR |
| 8 | `viz/physics_engine.py` | 75% | EXTEND |
| 9 | `modules/animation.js` | 72% | EXTEND |
| 10 | `viz/server.py` | 70% | EXTEND |
| 11 | `modules/physics.js` | 68% | EXTEND |
| 12 | `modules/selection.js` | 65% | EXTEND |
| 13 | `visualize_graph_webgl.py` | 58% | INTEGRATE |
| 14 | `modules/data-manager.js` | 55% | INTEGRATE |
| 15 | `modules/layouts.js` | 52% | INTEGRATE |
| 16 | `modules/core.js` | 48% | INTEGRATE |
| 17 | `output_generator.py` | 45% | INTEGRATE |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-21 | Claude + Leonardo | Initial legacy sprawl mapping |
