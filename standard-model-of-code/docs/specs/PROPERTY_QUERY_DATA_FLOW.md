# Property Query System - Data Flow Map

> Complete data flow from UI controls to rendered visuals
>
> **Status: CIRCUIT COHERENT** (Option A implemented 2026-01-24)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  PRESET BUTTONS │  │    SLIDERS      │  │   TOGGLES       │             │
│  │  ───────────────│  │  ──────────────│  │  ──────────────│             │
│  │  colorPreset    │  │  nodeOpacity    │  │  showArrows     │             │
│  │  sizeMode       │  │  edgeOpacity    │  │                 │             │
│  │  viewMode       │  │  edgeWidth      │  │                 │             │
│  │  edgeStyle      │  │  edgeCurvature  │  │                 │             │
│  │  edgeColorMode  │  │  nodeSizeScale  │  │                 │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│           │ SELECTOR           │ OVERRIDE           │                       │
│           │ (feeds UPB)        │ (wins everything)  │                       │
│           ▼                    ▼                    ▼                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             VIS_STATE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  window.VIS_STATE = {                                                       │
│      _epoch: 42,                    ← Cache invalidation counter            │
│                                                                             │
│      // SELECTOR STATE (parameterizes UPB)                                  │
│      colorPreset: 'tier',           ← Which color binding to use            │
│      sizeMode: 'uniform',           ← Which size binding to use             │
│      viewMode: 'atoms',             ← Which label binding to use            │
│      edgeStyle: 'solid',            ← Which edge width binding              │
│      edgeColorMode: 'type',         ← Which edge color binding              │
│                                                                             │
│      // SCALE MULTIPLIERS                                                   │
│      nodeSizeScale: 1.0,            ← Post-resolution multiplier            │
│      edgeWidthScale: 1.0,           ← Post-resolution multiplier            │
│                                                                             │
│      // OVERRIDE STATE (Priority 100 - wins everything)                     │
│      nodeOpacity: 0.9,              ← Direct slider value                   │
│      edgeOpacity: 0.6,              ← Direct slider value                   │
│      edgeCurvature: 0.2,            ← Direct slider value                   │
│      edgeWidth: null,               ← null = use UPB binding                │
│                                                                             │
│      overrides: {                   ← Explicit override bag                 │
│          node: {},                                                          │
│          edge: {}                                                           │
│      }                                                                      │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ bumpRender()
                                 │ _epoch++
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PROPERTY QUERY (Q)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Q.node(entity, channel) → value                                            │
│  Q.edge(entity, channel) → value                                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      PROVIDER CHAIN                                  │   │
│  │                   (sorted by priority)                               │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ PRIORITY 100: EXPLICIT OVERRIDE                              │   │   │
│  │  │ ────────────────────────────────────────────────────────────│   │   │
│  │  │ Source: VIS_STATE.overrides[kind][channel]                   │   │   │
│  │  │         VIS_STATE.nodeOpacity (for node.opacity)             │   │   │
│  │  │         VIS_STATE.edgeOpacity (for edge.opacity)             │   │   │
│  │  │         VIS_STATE.edgeCurvature (for edge.curvature)         │   │   │
│  │  │         VIS_STATE.edgeWidth (for edge.width)                 │   │   │
│  │  │                                                              │   │   │
│  │  │ Returns: Direct value if set, else undefined → fall through  │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │                              ▼ (if undefined)                        │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ PRIORITY 80: UPB BINDING                                     │   │   │
│  │  │ ────────────────────────────────────────────────────────────│   │   │
│  │  │ Source: UPB_CONFIG[kind][channel]                            │   │   │
│  │  │                                                              │   │   │
│  │  │ Binding types:                                               │   │   │
│  │  │   • Constant: 4, 0.8, true, '#ff00aa'                       │   │   │
│  │  │   • Path: 'tier_color' → entity.tier_color                   │   │   │
│  │  │   • Selected: { by: 'colorPreset', map: {...}, default }     │   │   │
│  │  │                                                              │   │   │
│  │  │ Example (node.color with colorPreset='tier'):                │   │   │
│  │  │   binding = { by: 'colorPreset', map: { tier: 'tier_color' }}│   │   │
│  │  │   selectorKey = VIS_STATE.colorPreset = 'tier'               │   │   │
│  │  │   resolved = 'tier_color'                                    │   │   │
│  │  │   value = entity.tier_color                                  │   │   │
│  │  │                                                              │   │   │
│  │  │ Returns: Resolved value if valid, else undefined → fall thru │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │                              ▼ (if undefined)                        │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ PRIORITY 20: RAW DATA                                        │   │   │
│  │  │ ────────────────────────────────────────────────────────────│   │   │
│  │  │ Source: entity[channel] or entity[kind + '_' + channel]      │   │   │
│  │  │                                                              │   │   │
│  │  │ Example: entity.color, entity.node_color                     │   │   │
│  │  │                                                              │   │   │
│  │  │ Returns: Direct field if exists, else undefined → fall thru  │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │                              ▼ (if undefined)                        │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ PRIORITY 0: SCHEMA DEFAULT                                   │   │   │
│  │  │ ────────────────────────────────────────────────────────────│   │   │
│  │  │ Source: DEFAULT_VIS_SCHEMA[kind][channel].default            │   │   │
│  │  │                                                              │   │   │
│  │  │ Examples:                                                    │   │   │
│  │  │   node.color   → '#9aa0a6'                                   │   │   │
│  │  │   node.size    → 4                                           │   │   │
│  │  │   node.opacity → 1.0                                         │   │   │
│  │  │   edge.color   → '#9aa0a6'                                   │   │   │
│  │  │   edge.width   → 1                                           │   │   │
│  │  │   edge.opacity → 0.6                                         │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      POST-RESOLUTION                                 │   │
│  │ ───────────────────────────────────────────────────────────────────│   │
│  │ 1. Apply scale multipliers:                                         │   │
│  │    • node.size *= VIS_STATE.nodeSizeScale                          │   │
│  │    • edge.width *= VIS_STATE.edgeWidthScale                        │   │
│  │                                                                      │   │
│  │ 2. Coerce to type (from schema):                                    │   │
│  │    • color: string or number, valid format                          │   │
│  │    • number: clamp to [min, max]                                    │   │
│  │    • boolean: truthy conversion                                     │   │
│  │    • string: toString()                                             │   │
│  │                                                                      │   │
│  │ 3. Cache result with epoch:                                         │   │
│  │    cache[entity][kind:channel] = { epoch, value }                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GRAPH ACCESSORS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Graph.nodeColor(node => Q.node(node, 'color') ?? node.color ?? '#888888')  │
│  Graph.nodeVal(node => Q.node(node, 'size') ?? node.size ?? 4)              │
│  Graph.nodeLabel(node => Q.node(node, 'label') ?? node.label ?? '')         │
│  Graph.linkColor(edge => Q.edge(edge, 'color') ?? edge.color ?? '#666666')  │
│  Graph.linkWidth(edge => Q.edge(edge, 'width') ?? edge.width ?? 1.0)        │
│  Graph.linkCurvature(edge => Q.edge(edge, 'curvature') ?? 0.0)              │
│  Graph.nodeOpacity(Q.node({}, 'opacity'))    ← Global value                 │
│  Graph.linkOpacity(Q.edge({}, 'opacity'))    ← Global value                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          3D FORCE GRAPH                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  For each node in scene:                                                    │
│      color  = nodeColor(node)                                               │
│      size   = nodeVal(node)                                                 │
│      label  = nodeLabel(node)                                               │
│      alpha  = nodeOpacity                                                   │
│                                                                             │
│  For each edge in scene:                                                    │
│      color     = linkColor(edge)                                            │
│      width     = linkWidth(edge)                                            │
│      curvature = linkCurvature(edge)                                        │
│      alpha     = linkOpacity                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            THREE.JS → WebGL                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌──────────┐                                   │
│                              │  RENDER  │                                   │
│                              │  FRAME   │                                   │
│                              └──────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Cache Invalidation Flow

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌─────────────┐
│ UI Control   │────▶│ bumpRender() │────▶│ _epoch++     │────▶│ Refresh     │
│ Changed      │     │               │     │              │     │ Hook        │
└──────────────┘     └───────────────┘     └──────────────┘     └──────┬──────┘
                                                                       │
                                                                       ▼
                     ┌───────────────────────────────────────────────────┐
                     │                                                   │
                     │  registerRenderRefresh(() => {                    │
                     │      Graph.nodeOpacity(Q.node({}, 'opacity'));    │
                     │      Graph.linkOpacity(Q.edge({}, 'opacity'));    │
                     │      Graph.refresh();                             │
                     │  });                                              │
                     │                                                   │
                     └───────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                     ┌───────────────────────────────────────────────────┐
                     │  Per-entity cache check:                          │
                     │                                                   │
                     │  if (cached.epoch !== currentEpoch) {             │
                     │      // Re-resolve through provider chain         │
                     │  }                                                │
                     └───────────────────────────────────────────────────┘
```

## UPB Binding Examples

### Node Color (Selected Mapping)

```javascript
// UPB_CONFIG.node.color
{
    by: 'colorBy',               // ← Reads VIS_STATE.colorBy (legacy key)
    map: {
        tier:       'tier_color',      // → entity.tier_color
        family:     'family_color',    // → entity.family_color
        layer:      'layer_color',     // → entity.layer_color
        complexity: 'complexity_color' // → entity.complexity_color
    },
    default: 'tier_color'
}

// Resolution with colorBy = 'family':
// 1. selectorKey = VIS_STATE.colorBy = 'family'
// 2. picked = map['family'] = 'family_color'
// 3. value = entity.family_color = '#3498db'
```

### Node Size (Constant or Path)

```javascript
// UPB_CONFIG.node.size
{
    by: 'sizeBy',                 // ← Legacy VIS_STATE key
    map: {
        uniform:    4,            // ← Constant value
        degree:     'degree',     // → entity.degree
        fanout:     'fanout',     // → entity.fanout
        complexity: 'elevation'   // → entity.elevation
    },
    default: 4
}

// Resolution with sizeBy = 'degree':
// 1. selectorKey = VIS_STATE.sizeBy = 'degree'
// 2. picked = map['degree'] = 'degree'
// 3. value = entity.degree = 7
// 4. scaled = 7 * VIS_STATE.nodeSizeScale
```

## File Locations

| File | Purpose |
|------|---------|
| `modules/vis-schema.js` | Schema defaults + type constraints |
| `modules/property-query.js` | Provider chain resolver |
| `modules/upb-defaults.js` | Default UPB binding configuration |
| `modules/property-query-init.js` | Init, wiring, debug helpers |
| `app.js` | Graph accessor wiring |

## Debug Commands

```javascript
// Console commands
Q.node(node, 'color')           // Direct query
Q.explainNode(node, 'color')    // Resolution trace with steps
debugNode(node)                 // Full channel dump

// Keyboard shortcuts
Ctrl+X                          // Debug selected node
Ctrl+Shift+X                    // Debug selected edge

// Manual override
setNodeOverride('color', '#ff0000')  // Force all nodes red
clearOverrides()                      // Remove all overrides
```

## Design Principles

1. **Render-time query**: Compute at render, not pre-compute
2. **Provider chain**: Priority-based fallback (Override > UPB > Raw > Default)
3. **Coercion per-provider**: Invalid values fall through to next provider
4. **Epoch-based cache**: WeakMap keyed by entity, invalidated by `_epoch++`
5. **Selector vs Override**: Selectors parameterize UPB, overrides bypass it

---

## Integration: Option A (Adapter Strategy)

**Implemented: 2026-01-24**

Instead of replacing VIS_STATE (high risk, ~500 lines changed), we adapted Property Query
to work with existing VIS_STATE keys. This is the "adapter" or "shim" strategy.

### Changes Made

| File | Change | Purpose |
|------|--------|---------|
| `upb-defaults.js` | `colorPreset` → `colorBy` | Match VIS_STATE key names |
| `upb-defaults.js` | `sizeMode` → `sizeBy` | Match VIS_STATE key names |
| `upb-defaults.js` | `edgeColorMode` → `edgeBy` | Match VIS_STATE key names |
| `vis-state.js` | Guard legacy path when `Q` active | Prevent accessor overwrite |
| `vis-state.js` | Call `bumpRender()` in `_refreshGraph()` | Connect UI → PQ refresh |
| `property-query-init.js` | Use legacy keys + compatibility aliases | Bulletproof migration |

### Coherent Data Flow

```
UI Click
    │
    ▼
VIS_STATE.setColorBy('tier')
    │
    ▼
applyState({ colorBy: 'tier' })
    │
    ▼
_refreshGraph()
    │
    ├─► if (Q) skip legacy ─────────────────────────┐
    │   else applyNodeColors() + Graph.nodeColor()  │
    │                                               │
    ▼                                               │
bumpRender() ◄──────────────────────────────────────┘
    │
    ▼
_epoch++
    │
    ▼
Graph.refresh()
    │
    ▼
Graph.nodeColor(n => Q.node(n, 'color'))
    │
    ▼
UPB Provider reads VIS_STATE.colorBy = 'tier'
    │
    ▼
Returns entity.tier_color
```

### Validation

- Circuit Breaker: 9/9 PASS
- Legacy field names removed from UPB
- `bumpRender()` called on every UI change

---

*Generated: 2026-01-24*
*System: Property Query v1.0.0 + Option A Integration*
