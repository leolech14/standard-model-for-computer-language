# Universal Property Binder (UPB)

> Universal Many-to-Many Binding Between Data Attributes and Visual Channels

---

## Design Principles (Lessons from app.js Refactoring)

The app.js refactoring (12K → 3K lines) taught us critical lessons. UPB MUST NOT become another God class.

### Anti-Patterns to AVOID

| Anti-Pattern | Example from app.js | UPB Prevention |
|--------------|---------------------|----------------|
| God Class | 12K lines in one file | Max 300 lines per module |
| Feature Creep | Everything in app.js | Single responsibility per file |
| Hidden Dependencies | Implicit globals | Explicit imports only |
| Wrapper Functions | 40+ duplicates found | No wrappers, direct calls |
| Mixed Concerns | UI + Logic + Data | Strict separation |

### UPB Module Constraints

```
┌─────────────────────────────────────────────────────────────────┐
│                    UPB MODULE RULES                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. MAX 300 LINES per module (hard limit)                       │
│                                                                  │
│  2. SINGLE RESPONSIBILITY per file:                             │
│     ├─ endpoints.js    → ONLY endpoint definitions              │
│     ├─ bindings.js     → ONLY binding graph logic               │
│     ├─ blenders.js     → ONLY blend mode implementations        │
│     ├─ scales.js       → ONLY scale functions                   │
│     └─ intelligence.js → ONLY tracking/recommendations          │
│                                                                  │
│  3. NO GLOBALS - Everything through explicit exports            │
│                                                                  │
│  4. AI-GRIPPABLE:                                               │
│     ├─ Clear function names (verb + noun)                       │
│     ├─ JSDoc comments on public functions                       │
│     ├─ No magic numbers (use named constants)                   │
│     └─ Max 3 levels of nesting                                  │
│                                                                  │
│  5. TESTABLE - Pure functions where possible                    │
│                                                                  │
│  6. YAML-DRIVEN - Config in YAML, not hardcoded JS              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Target File Structure

```
modules/upb/                    # Max 7 files, each <300 lines
├─ index.js          (~80 lines)   # Public API only
├─ endpoints.js      (~200 lines)  # Source/Target definitions
├─ bindings.js       (~280 lines)  # Binding graph + evaluation
├─ blenders.js       (~180 lines)  # Blend mode implementations
├─ scales.js         (~150 lines)  # Scale function implementations
├─ intelligence.js   (~250 lines)  # Tracking + recommendations
└─ presets/                        # YAML configs (not JS)
   ├─ default.yaml
   ├─ complexity.yaml
   └─ hierarchy.yaml
```

**Total: ~1,140 lines** (vs app.js 12K - still 10x smaller)

---

## Purpose

The Universal Property Binder (UPB) is the core visualization intelligence layer that enables:
- **Every data attribute** exposed as a bindable endpoint (source)
- **Every visual property** exposed as a target endpoint (channel)
- **Full combinatorial freedom** to couple any source to any target
- **Many-to-many bindings** where one attribute drives multiple channels
- **Blend modes** where multiple attributes drive one channel
- **Intelligence layer** to track, analyze, and recommend bindings

The ultimate destination is the **PIXEL** - rendered through OKLCH geometric color space.

---

## Core Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SEMANTIC PROJECTION MATRIX (UPB)                         │
│                     "Every Attribute ↔ Every Channel"                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   DATA ENDPOINTS (Sources)              VISUAL ENDPOINTS (Targets)           │
│   ════════════════════════              ════════════════════════             │
│                                                                              │
│   Structural:                           OKLCH Geometry:                      │
│   ├─ file_size                          ├─ L (Lightness)  ─────────┐        │
│   ├─ line_count                         ├─ C (Chroma)     ─────────┤        │
│   ├─ token_count                        ├─ H (Hue)        ─────────┤        │
│   ├─ complexity                                                    │        │
│                                         Spatial Geometry:          │        │
│   Semantic:                             ├─ X position     ─────────┤        │
│   ├─ tier                               ├─ Y position     ─────────┤        │
│   ├─ family                             ├─ Z position     ─────────┤        │
│   ├─ layer                              ├─ radius         ─────────┤        │
│   ├─ role                               ├─ angle          ─────────┤        │
│   ├─ phase                                                         │        │
│                                         Size Geometry:             │        │
│   Graph:                                ├─ node_size      ─────────┤        │
│   ├─ in_degree                          ├─ edge_width     ─────────┤        │
│   ├─ out_degree                                                    │        │
│   ├─ pagerank                           Physics:                   │        │
│   ├─ betweenness                        ├─ mass           ─────────┤        │
│   ├─ clustering                         ├─ charge         ─────────┤        │
│                                         ├─ damping        ─────────┤        │
│   Temporal:                             ├─ velocity       ─────────┤        │
│   ├─ age                                                           │        │
│   ├─ last_modified                      Animation:                 │        │
│   ├─ commit_frequency                   ├─ pulse_rate     ─────────┤        │
│                                         ├─ rotation_speed ─────────┤        │
│   State:                                ├─ oscillation    ─────────┤        │
│   ├─ is_orphan                          ├─ perturbation   ─────────┤        │
│   ├─ is_hotspot                                                    │        │
│   ├─ is_selected                        Opacity:                   │        │
│   └─ ...                                └─ alpha          ─────────┘        │
│                                                                              │
│         ▲                                         ▲                          │
│         │                                         │                          │
│         └──────────────────┬──────────────────────┘                          │
│                            │                                                 │
│                            ▼                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      BINDING MATRIX                                  │   │
│   │                                                                      │   │
│   │   ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐    │   │
│   │   │         │   H     │   C     │   L     │  Size   │ Physics │    │   │
│   │   ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤    │   │
│   │   │ tier    │  ●      │         │         │         │         │    │   │
│   │   │ family  │         │  ●      │         │         │         │    │   │
│   │   │ role    │  ●      │         │         │         │         │    │   │
│   │   │ size    │         │         │         │  ●      │         │    │   │
│   │   │ degree  │         │         │  ●      │         │  ●      │    │   │
│   │   │ ...     │ [ANY]   │ [ANY]   │ [ANY]   │ [ANY]   │ [ANY]   │    │   │
│   │   └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘    │   │
│   │                                                                      │   │
│   │   SCALE FUNCTIONS: linear | log | sqrt | exp | discrete             │   │
│   │   NORMALIZATION: min-max | z-score | percentile                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                            │                                                 │
│                            ▼                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      PROJECTION INTELLIGENCE                         │   │
│   │                                                                      │   │
│   │   1. Combination Tracking: Log all binding experiments              │   │
│   │   2. Pattern Detection: Which bindings reveal structure?            │   │
│   │   3. Perceptual Analysis: Which bindings are distinguishable?       │   │
│   │   4. Semantic Coherence: Which bindings make semantic sense?        │   │
│   │   5. Recommendation Engine: Suggest optimal bindings                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                            │                                                 │
│                            ▼                                                 │
│                     ┌──────────────┐                                         │
│                     │    PIXEL     │                                         │
│                     │   (Final     │                                         │
│                     │   Render)    │                                         │
│                     └──────────────┘                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Many-to-Many Binding Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SEMANTIC PROJECTION MATRIX (UPB)                         │
│                     Many-to-Many Binding Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   EXAMPLE: "complexity" drives 4 channels simultaneously                     │
│                                                                              │
│                        ┌──────► H (Hue)         [warm = complex]             │
│                        │                                                     │
│   complexity ──────────┼──────► Size            [bigger = complex]           │
│                        │                                                     │
│                        ├──────► L (Lightness)   [darker = complex]           │
│                        │                                                     │
│                        └──────► pulse_rate      [faster = complex]           │
│                                                                              │
│   RESULT: Complex nodes are LARGE, DARK, WARM, and PULSING FAST             │
│           → Compound visual signature, instantly recognizable                │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   BINDING GRAPH (not just matrix)                                            │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │    [tier]─────────┬──────────────────►[H]◄──────────┬────[role]     │   │
│   │                   │                                  │               │   │
│   │                   ├──────────────────►[Y]            │               │   │
│   │                   │                                  │               │   │
│   │    [family]───────┼──────────────────►[C]◄──────────┤               │   │
│   │                   │                    │             │               │   │
│   │                   │                    │             │               │   │
│   │    [complexity]───┼──────►[Size]◄──────┼─────────────┘               │   │
│   │                   │         │          │                             │   │
│   │                   │         │          │                             │   │
│   │    [degree]───────┴──────►[mass]◄──────┴────[pagerank]              │   │
│   │                             │                                        │   │
│   │                             ▼                                        │   │
│   │                        [damping]                                     │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   BINDING TYPES:                                                             │
│   ─────────────                                                              │
│   ● Exclusive (1:1)    - Only one source per target                         │
│   ● Additive (N:1)     - Multiple sources sum/blend into target             │
│   ● Broadcast (1:N)    - One source drives multiple targets                 │
│   ● Mesh (N:M)         - Full many-to-many coupling                         │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   BLEND MODES (when multiple sources → one target)                           │
│   ───────────────────────────────────────────────────────────────────────   │
│                                                                              │
│   │ Mode       │ Formula                    │ Use Case                  │   │
│   ├────────────┼────────────────────────────┼───────────────────────────┤   │
│   │ Add        │ A + B                      │ Cumulative effects        │   │
│   │ Multiply   │ A × B                      │ Reinforcing signals       │   │
│   │ Average    │ (A + B) / 2                │ Balanced blend            │   │
│   │ Max        │ max(A, B)                  │ Dominant signal wins      │   │
│   │ Min        │ min(A, B)                  │ Conservative blend        │   │
│   │ Weighted   │ w₁A + w₂B                  │ Prioritized blend         │   │
│   │ Modulate   │ A × (1 + B×k)              │ B modulates A             │   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   BINDING DEFINITION SCHEMA                                                  │
│   ───────────────────────────────────────────────────────────────────────   │
│                                                                              │
│   {                                                                          │
│     "id": "complexity-signature",                                            │
│     "name": "Complexity Visual Signature",                                   │
│     "sources": ["complexity"],                                               │
│     "targets": [                                                             │
│       { "channel": "H",          "scale": "linear", "range": [60, 0] },     │
│       { "channel": "size",       "scale": "sqrt",   "range": [4, 24] },     │
│       { "channel": "L",          "scale": "linear", "range": [0.7, 0.3] },  │
│       { "channel": "pulse_rate", "scale": "log",    "range": [0.5, 4] }     │
│     ],                                                                       │
│     "semantic": "Complex code appears large, dark, warm, and agitated"       │
│   }                                                                          │
│                                                                              │
│   // Multi-source example                                                    │
│   {                                                                          │
│     "id": "importance-blend",                                                │
│     "name": "Node Importance",                                               │
│     "sources": [                                                             │
│       { "attr": "pagerank",   "weight": 0.4 },                              │
│       { "attr": "degree",     "weight": 0.3 },                              │
│       { "attr": "complexity", "weight": 0.3 }                               │
│     ],                                                                       │
│     "blend": "weighted",                                                     │
│     "targets": [                                                             │
│       { "channel": "size", "scale": "sqrt", "range": [2, 30] }              │
│     ],                                                                       │
│     "semantic": "Important nodes are larger based on blended metrics"        │
│   }                                                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Combinatorial Space

With N sources and M targets, the binding possibilities are:

| Sources | Targets | 1:1 Bindings | N:M Bindings (with blends) |
|---------|---------|--------------|----------------------------|
| 20 | 15 | 20 × 15 = 300 | 2²⁰ × 2¹⁵ ≈ 34 billion |

This is why **Projection Intelligence** is essential - to navigate the space and find meaningful combinations.

---

## OKLCH Geometric Foundation

The OKLCH color space is **geometric**:
- **L** = vertical axis (lightness: 0 = black, 1 = white)
- **C** = radial distance (chroma: 0 = gray, 0.4 = vivid)
- **H** = angle (hue: 0-360° around the color wheel)

This means **color IS geometry**. When you bind:
- `tier → L` (hierarchy becomes brightness)
- `family → H` (category becomes hue angle)
- `complexity → C` (complexity becomes color intensity)

You're projecting semantic dimensions onto a 3D color cylinder. The pixel is the final coordinate in this semantic-geometric space.

---

## Module Location

```
standard-model-of-code/src/core/viz/
├── spm/                           # NEW: Universal Property Binder
│   ├── __init__.py
│   ├── endpoints.py               # Source & Target endpoint definitions
│   ├── bindings.py                # Binding graph implementation
│   ├── blenders.py                # Blend mode implementations
│   ├── intelligence.py            # Tracking, analysis, recommendations
│   └── presets/                   # Pre-configured binding sets
│       ├── default.yaml
│       ├── complexity.yaml
│       └── architecture.yaml
├── assets/modules/
│   ├── spm.js                     # Browser-side UPB implementation
│   └── spm-ui.js                  # UI for binding experimentation
```

---

## Related Documents

- `VISUALIZATION_UI_SPEC.md` - UI specification for visual controls
- `color-engine.js` - Current OKLCH implementation
- `control-bar.js` - Current mapping UI (to be replaced by UPB)
- `file-viz.js` - Current file visualization bindings

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-21 | Claude + Leonardo | Initial architecture specification |
