# Architecture Anti-Pattern Investigation

> **Discovery Date:** 2026-01-19
> **Scope:** Collider Visualization Layer (`src/core/viz/assets/app.js`)
> **Method:** Deep code analysis + Collider self-analysis + AI forensic review
> **Status:** ACTIVE INVESTIGATION

---

## Executive Summary

During a sidebar UI refactor, a systematic investigation revealed **two critical findings:**

### Finding 1: Implicit Global State Machine (Architecture Anti-Pattern)

Collider's visualization layer (`app.js`, ~8000 lines) exhibits an **Implicit Global State Machine** pattern:
- **13+ mutable globals** (VIS_FILTERS, APPEARANCE_STATE, ACTIVE_DATAMAPS, etc.)
- **95+ scattered mutations** (55+ reads, 40+ writes to VIS_FILTERS alone)
- **No formal state management** - implicit contract: "remember to call `refreshGraph()`"
- **Missing DM layer** - The Data Management layer was intended to be the central aggregator but was never implemented

**This is not a bug—it's emergent architecture** that works but creates maintenance and extensibility risks.

### Finding 2: Collider Cannot Analyze JavaScript (Product Gap)

**Collider attempted to analyze itself and failed:**
- **220 nodes extracted** (functions, classes) ✓
- **0 edges extracted** (no call graph) ✗
- **100% Unknown roles** (no semantic classification) ✗

**Root Cause:** JavaScript `body_source` is not extracted. The edge extraction pipeline (`edge_extractor.py`) relies on `body_source` for regex-based call detection. Without it, no edges are created.

**Implication:** Collider's Python analysis is complete (nodes + edges + roles). JavaScript analysis is incomplete (nodes only).

---

## The Discovery

### Initial Observation

While planning a sidebar refactor, AI analysis (Gemini 2.0 Flash, architect mode) flagged:

> "The current Collider sidebar suffers from:
> - **High Complexity (D5: STATE):** Nested collapsible sections increase cognitive load
> - **Role Scattering (D3: ROLE):** Controls duplicated across UI elements violate Single Responsibility
> - **Layer Violation (D2: LAYER):** UI manipulation logic intertwined with core graph data"

### Deep Dive Results

Subsequent exploration revealed the problem is much deeper than the sidebar:

| Metric | Finding |
|--------|---------|
| Global mutable variables | 13+ |
| VIS_FILTERS read locations | 55+ |
| VIS_FILTERS write locations | 40+ |
| APPEARANCE_STATE properties | 14 |
| refreshGraph() callers | 21 |
| refreshGraph() globals read | 13 |
| Total app.js lines | ~8000 |
| Module separation | 0 (monolithic) |

---

## The Anti-Pattern: Implicit Global State Machine

### Pattern Description

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GLOBAL STATE SOUP                                │
│                                                                          │
│  VIS_FILTERS          APPEARANCE_STATE       ACTIVE_DATAMAPS            │
│  ├─ tiers (Set)       ├─ nodeScale          (Set of datamap IDs)        │
│  ├─ rings (Set)       ├─ edgeOpacity                                    │
│  ├─ roles (Set)       ├─ boundaryFill       CURRENT_DENSITY             │
│  ├─ edges (Set)       ├─ backgroundBase     (number 1-5)                │
│  ├─ families (Set)    ├─ colorMode                                      │
│  ├─ layers (Set)      ├─ sizeMode           GRAPH_MODE                  │
│  ├─ effects (Set)     ├─ edgeMode           ('atoms'|'files'|'hybrid')  │
│  ├─ edgeFamilies      ├─ amplifier                                      │
│  └─ metadata {}       └─ ...14 total        Graph, DM, FILE_GRAPH...    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                    ↑                    ↑                    ↑
                    │                    │                    │
          ┌─────────┴──────────┬─────────┴──────────┬────────┴─────────┐
          │                    │                    │                  │
     UI Event Handlers    Filter Functions     Layout Functions    Mode Switches
     (click, input)       (toggleTopo...)      (applyLayout...)   (file, flow)
          │                    │                    │                  │
          └─────────┬──────────┴─────────┬──────────┴────────┬─────────┘
                    │                    │                   │
                    ▼                    ▼                   ▼
              ┌──────────────────────────────────────────────────┐
              │              refreshGraph()                       │
              │  - Reads 13 globals                               │
              │  - Calls filterGraph(VIS_FILTERS, DATAMAPS, ...)  │
              │  - Updates Graph.graphData()                      │
              │  - Must be called after ANY state change          │
              └──────────────────────────────────────────────────┘
```

### Why It's Problematic

#### 1. No Single Source of Truth

Multiple globals affect the same behavior:
- `VIS_FILTERS.tiers` filters by tier
- `ACTIVE_DATAMAPS` also filters by tier (within datamap config)
- Both are independent—no coordination layer

#### 2. Implicit Contract: "Remember to Call refreshGraph()"

Every state mutation requires manually calling `refreshGraph()`:

```javascript
// Pattern repeated 40+ times in codebase
VIS_FILTERS.tiers.add('T0');
refreshGraph();  // MUST call this or UI desyncs
```

If you forget `refreshGraph()`, the visualization silently desyncs from state.

#### 3. Emergency Recovery as Architecture

The code detects "zero node" results and auto-clears filters:

```javascript
// Lines 3977-3994: Zero-node protection
if (subset.nodes.length === 0 && hasActiveFilters) {
    showToast('No nodes match current filters. Clearing filters.');
    clearAllFilters();  // EMERGENCY: Reset everything
    // Retry...
}
```

This is a **symptom** of missing input validation, not a feature.

#### 4. 8000 Lines, Zero Modules

All visualization code in one file:
- UI binding
- Graph rendering
- Physics simulation
- Color calculation
- Filter logic
- Layout algorithms
- File mode handling
- Selection management
- Animation systems

No separation. No interfaces. No testability.

#### 5. Mutation Without Coordination

Any function can write to any global at any time:

| Global | Writers | Readers |
|--------|---------|---------|
| VIS_FILTERS | 40+ locations | 55+ locations |
| APPEARANCE_STATE | 15+ locations | 30+ locations |
| ACTIVE_DATAMAPS | 5+ locations | 10+ locations |

---

## Evidence: Collider Self-Analysis

### Running Collider on Itself

```bash
./collider full src/core/viz/assets --output .collider/self-analysis
```

### Actual Findings (2026-01-19)

| Metric | Value | Implication |
|--------|-------|-------------|
| Nodes extracted | 220 | Functions and classes found |
| Edges extracted | **0** | **JavaScript call graph not implemented** |
| Classes | 3 | RuntimeRegistry, etc. |
| Functions | 217 | All standalone (no edge connections) |
| Roles assigned | 0% | 100% "Unknown" |
| Total lines | 11,865 | Confirms ~8000 line monolith |

### Meta-Finding: Collider Cannot Fully Analyze Itself

**JavaScript edge extraction is not implemented.**

This means:
- Collider extracts JS nodes (functions, classes) successfully
- But it cannot detect **calls between functions**
- Without edges, topology analysis is impossible
- The "Implicit Global State Machine" anti-pattern is **invisible to Collider**

```json
// From unified_analysis.json
{
  "edges": [],           // EMPTY - no call graph
  "stats": {
    "total_nodes": 220,
    "total_edges": 0,    // Critical limitation
    "unknown_percentage": 100.0
  }
}
```

**This is a product gap.** Collider's Python analysis extracts full call graphs; JavaScript analysis does not.

### Root Cause: Empty `body_source` for JavaScript

**The edge extraction pipeline (`edge_extractor.py:223-252`) relies on `body_source`:**

```python
# From edge_extractor.py
for p in particles:
    body = p.get('body_source', '')
    if body:
        # Look for function calls in body
        calls = re.findall(r'(?:self\.)?(\w+)\s*\(', body)
        # ... create edges ...
```

**JavaScript nodes have empty `body_source`:**
```json
// From self-analysis: all JS nodes
{ "name": "refreshGraph", "body_source": "" }
{ "name": "filterGraph", "body_source": "" }
{ "name": "DataManager", "body_source": "" }
```

**The cascade of failures:**
1. **tree_sitter_engine.py** extracts JS function signatures but not bodies
2. **body_source** is empty for all 220 JavaScript nodes
3. **edge_extractor.py** skips nodes with empty body_source
4. **Result:** 0 edges, making topology analysis impossible
5. **heuristic_classifier.py** also uses `body_source` for pattern matching → 100% Unknown roles

**Fix Required:** Add body extraction for JavaScript in tree-sitter parsing, similar to Python.

### What We Expected to See (If Edges Worked)

| Dimension | Expected Violation |
|-----------|-------------------|
| D3: ROLE | Role scattering - UI, Logic, Data mixed |
| D2: LAYER | Layer violations - no clear boundaries |
| D5: STATE | High state complexity - 13+ mutable globals |
| D7: COUPLING | High coupling - everything depends on everything |

**Topology prediction (if edges existed):**
- **Shape:** Hairball/Mesh (not Star or Tree)
- **Hubs:** `refreshGraph`, `filterGraph`, `initGraph`
- **Orphans:** Minimal (tightly coupled)
- **Knot Score:** High (circular dependencies likely)

### The Missing DM Layer

**Key architectural context:** The Data Management (DM) layer was **supposed to be** the central aggregator/consolidator for all state.

**What was intended:**
```
┌──────────────────────────────────────────────────────────────┐
│  DM LAYER (Intended Architecture)                            │
│  ─────────────────────────────────                           │
│  • Single source of truth for VIS_FILTERS, APPEARANCE_STATE  │
│  • Coordinated mutations through defined interface           │
│  • Observer pattern for graph updates                        │
│  • Clear separation: UI → DM → Graph                         │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  ACTUAL ARCHITECTURE (What Exists)                           │
│  ─────────────────────────────────                           │
│  • 13+ mutable globals scattered across 8000 lines           │
│  • Any function can write to any global at any time          │
│  • No coordination layer - direct mutations everywhere       │
│  • Implicit contract: "Remember to call refreshGraph()"      │
└──────────────────────────────────────────────────────────────┘
```

The DM layer was never formalized. Instead, the prototype grew organically and global state became the de facto architecture.

---

## Root Cause Analysis

### How Did This Happen?

1. **Prototype Evolution** - Started as a quick D3 visualization, grew organically
2. **Performance Pressure** - Global state is fast; abstractions add overhead
3. **Single Developer** - Patterns optimized for "I know where everything is"
4. **Framework Choice** - ForceGraph3D encourages imperative mutation style
5. **Success Trap** - It works, so why refactor?

### Why It Matters Now

1. **Sidebar Refactor Blocked** - Can't safely change UI without understanding all dependencies
2. **Feature Velocity** - Adding features requires tracing entire call graph
3. **Bug Surface** - Any change can silently break something elsewhere
4. **Testing** - Impossible to unit test with global state
5. **Onboarding** - New developers face 8000-line cliff

---

## Architectural Remediation Options

### Option A: Live With It (Status Quo)

**Approach:** Accept the architecture, document it thoroughly, work within constraints.

**Pros:**
- No risk of breaking working code
- No development time investment
- Already understood by current maintainers

**Cons:**
- Technical debt compounds
- New features increasingly risky
- No path to testability

**Recommendation:** Acceptable for maintenance mode.

---

### Option B: Facade Pattern (Recommended Short-Term)

**Approach:** Add a coordination layer that wraps globals without replacing them.

```javascript
class UIManager {
    // Facade: Coordinates existing globals, doesn't replace them

    setFilter(dimension, value, active) {
        const set = VIS_FILTERS[dimension];
        if (active) set.add(value); else set.delete(value);
        this.scheduleRefresh();  // Debounced refresh
    }

    setAppearance(property, value) {
        APPEARANCE_STATE[property] = value;
        this.triggerCallback(property);  // Property-specific callback
    }

    scheduleRefresh() {
        // Debounce multiple rapid changes
        clearTimeout(this._refreshTimer);
        this._refreshTimer = setTimeout(() => refreshGraph(), 16);
    }
}
```

**Pros:**
- Incremental migration possible
- No breaking changes
- Adds debouncing (performance win)
- Single point for debugging

**Cons:**
- Two ways to do things during transition
- Doesn't solve underlying structure

**Recommendation:** Best for near-term refactors like sidebar.

---

### Option C: State Machine Formalization (Medium-Term)

**Approach:** Replace implicit state with explicit state machine.

```javascript
const GraphStateMachine = {
    state: {
        filters: { tiers: [], rings: [], ... },
        appearance: { nodeScale: 1, ... },
        mode: 'atoms'
    },

    transitions: {
        SET_FILTER: (state, { dimension, value, active }) => ({
            ...state,
            filters: {
                ...state.filters,
                [dimension]: active
                    ? [...state.filters[dimension], value]
                    : state.filters[dimension].filter(v => v !== value)
            }
        }),
        // ... other transitions
    },

    dispatch(action, payload) {
        this.state = this.transitions[action](this.state, payload);
        this.notify();  // Single render trigger
    }
};
```

**Pros:**
- Predictable state transitions
- Time-travel debugging possible
- Testable
- Single source of truth

**Cons:**
- Significant refactor effort
- Learning curve for contributors
- May impact performance if not careful

**Recommendation:** Worth planning for v2.0.

---

### Option D: Module Decomposition (Long-Term)

**Approach:** Split app.js into focused modules.

```
src/core/viz/
├── state/
│   ├── filters.js      # VIS_FILTERS management
│   ├── appearance.js   # APPEARANCE_STATE management
│   └── mode.js         # GRAPH_MODE management
├── render/
│   ├── graph.js        # Graph initialization & update
│   ├── colors.js       # Color calculation
│   └── edges.js        # Edge rendering
├── ui/
│   ├── sidebar.js      # Sidebar controls
│   ├── panels.js       # Info panels
│   └── hover.js        # Hover interactions
├── layout/
│   ├── force.js        # Force simulation
│   ├── radial.js       # Radial layout
│   └── presets.js      # Layout presets
└── index.js            # Composition root
```

**Pros:**
- Clear separation of concerns
- Testable units
- Parallel development possible
- Matches Standard Model principles

**Cons:**
- Major refactor
- Build system changes needed
- Risk of breaking during migration

**Recommendation:** Target architecture for v3.0.

---

## Investigation Protocol

### Phase 1: Self-Analysis (Complete)

1. [x] Document anti-pattern discovery
2. [x] Run Collider on `src/core/viz/assets`
3. [x] Extract topology metrics → **BLOCKED: 0 edges extracted (JS limitation)**
4. [x] Identify hub functions → **Manual grep required (see manual analysis)**
5. [x] Map coupling graph → **Partially complete via grep (55+ VIS_FILTERS reads)**

**Phase 1 Outcome:** Discovered Collider product gap. JavaScript edge extraction not implemented. Manual analysis was required to identify the anti-pattern.

### Phase 2: AI-Assisted Mapping (In Progress)

1. [x] Feed Collider output to `analyze.py --mode forensic` → **Limited value without edges**
2. [~] Generate dependency graph → **Manual grep analysis substituted**
3. [ ] Identify refactor boundaries
4. [ ] Estimate effort per module

**Phase 2 Pivot:** Since Collider cannot extract JS edges, manual grep-based analysis is the primary evidence source.

### Phase 3: Remediation Planning (Pending)

1. [ ] Choose remediation option (B recommended)
2. [ ] Create phased migration plan
3. [ ] Define success metrics

---

## Appendix A: Key Code Locations

| Component | Lines | Purpose |
|-----------|-------|---------|
| VIS_FILTERS definition | 254-270 | Filter state container |
| APPEARANCE_STATE definition | 275-292 | Visual state container |
| refreshGraph() | 3918-4008 | Central render coordinator |
| filterGraph() | 3219-3334 | Core filtering engine |
| toggleTopoFilter() | 5618-5645 | Filter toggle handler |
| buildSliders() | 6400-6700 | Appearance slider builders |
| initGraph() | 2600-2800 | Graph initialization |

---

## Appendix B: Manual Grep Evidence

Since Collider cannot extract JS edges, these findings were gathered via manual grep analysis.

### VIS_FILTERS Dependency Map

```
VIS_FILTERS
├── READS (55+ locations)
│   ├── filterGraph()           # Main consumer
│   ├── refreshGraph()          # Checks before filtering
│   ├── toggleTopoFilter()      # Checks current state
│   ├── buildFilterUI()         # Populates UI from state
│   ├── exportState()           # Serialization
│   └── ... 50+ more locations
│
├── WRITES (40+ locations)
│   ├── toggleTopoFilter()      # Toggle individual filters
│   ├── clearAllFilters()       # Bulk clear
│   ├── applyPreset()           # Preset application
│   ├── loadState()             # Deserialization
│   └── ... 35+ more locations
│
└── STRUCTURE
    ├── tiers: Set<string>      # T0, T1, T2, UNKNOWN
    ├── rings: Set<string>      # CORE, APP, INFRA, TESTING
    ├── roles: Set<string>      # Repository, Entity, Service...
    ├── edges: Set<string>      # Edge type filters
    ├── families: Set<string>   # LOG, DAT, ORG, EXE, EXT
    ├── layers: Set<string>     # Domain, Infrastructure...
    ├── effects: Set<string>    # Pure, ReadOnly, WriteOnly...
    ├── edgeFamilies: Set<string>
    └── metadata: Object        # showLabels, showEdges, etc.
```

### refreshGraph() Call Tree

```
refreshGraph() [21 callers]
├── Reads 13 globals:
│   ├── VIS_FILTERS
│   ├── APPEARANCE_STATE
│   ├── ACTIVE_DATAMAPS
│   ├── CURRENT_DENSITY
│   ├── GRAPH_MODE
│   ├── Graph (ForceGraph3D instance)
│   ├── DM, FILE_GRAPH, ...
│
├── Called by:
│   ├── UI Event Handlers (11)
│   │   ├── toggleTopoFilter()
│   │   ├── slider.oninput callbacks (5)
│   │   ├── button.onclick handlers (3)
│   │   └── keyboard shortcuts (2)
│   │
│   ├── Mode Switches (4)
│   │   ├── switchToFileMode()
│   │   ├── switchToAtomMode()
│   │   ├── switchToFlowMode()
│   │   └── switchToHybridMode()
│   │
│   ├── Filter Operations (3)
│   │   ├── clearAllFilters()
│   │   ├── applyPreset()
│   │   └── loadState()
│   │
│   └── Layout Functions (3)
│       ├── applyRadialLayout()
│       ├── applyForceLayout()
│       └── resetLayout()
│
└── Implicit Contract:
    "After modifying ANY global state, you MUST call refreshGraph()
     or the UI will silently desync from the data."
```

### APPEARANCE_STATE Flow

```
APPEARANCE_STATE [14 properties, single-direction flow]

User Input → Slider → APPEARANCE_STATE → Callback → Graph Update

Properties:
├── nodeScale: number (1-5)
├── edgeOpacity: number (0-1)
├── boundaryFill: number (0-1)
├── backgroundBase: string (hex color)
├── backgroundBrightness: number (0-2)
├── colorMode: string (tier|family|role|layer|ring|effect)
├── sizeMode: string (uniform|degree|centrality)
├── edgeMode: string (curved|straight|particles)
├── amplifier: number (0.5-2)
├── labelScale: number (0.5-2)
├── labelVisibility: string (always|hover|selected)
├── physicsEnabled: boolean
├── currentPreset: string
└── selectedColorScheme: string

Data Flow (Controlled):
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  UI Slider  │───▶│  Callback   │───▶│  APPEARANCE │───▶│   Graph     │
│  (input)    │    │  Function   │    │   _STATE    │    │  .method()  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

This flow is BETTER than VIS_FILTERS because:
- Single-direction data flow
- Each slider has dedicated callback
- No "remember to refresh" pattern
```

### The Missing DM Layer (Conceptual)

```javascript
// WHAT SHOULD HAVE EXISTED:
class DataManager {
    #filters = { tiers: new Set(), ... };
    #appearance = { nodeScale: 1, ... };
    #subscribers = new Set();

    // Controlled mutations
    setFilter(dimension, value, active) {
        if (active) this.#filters[dimension].add(value);
        else this.#filters[dimension].delete(value);
        this.#notify('filters');
    }

    setAppearance(key, value) {
        this.#appearance[key] = value;
        this.#notify('appearance');
    }

    // Observer pattern
    subscribe(callback) { this.#subscribers.add(callback); }
    #notify(change) { this.#subscribers.forEach(cb => cb(change)); }

    // Single source of truth
    getState() { return { filters: this.#filters, appearance: this.#appearance }; }
}

// WHAT EXISTS INSTEAD:
let VIS_FILTERS = { ... };      // Anyone can write
let APPEARANCE_STATE = { ... }; // Anyone can write
// + 11 more globals
// + 95+ scattered mutations
// + Manual refreshGraph() calls everywhere
```

---

## Next Steps

1. [x] ~~Run Collider self-analysis~~ - **Complete** (revealed JS edge gap)
2. [x] ~~AI forensic review~~ - **Limited value** (no edges to analyze)
3. [x] ~~Quantify the problem~~ - **Complete via manual grep** (55+ reads, 40+ writes, 21 refresh callers)
4. [ ] **Product Decision: JS Edge Extraction** - Priority feature for Collider roadmap?
5. [ ] **Architecture Decision** - Choose remediation path (B: Facade recommended)
6. [ ] **Execute sidebar refactor** - Using facade pattern as pilot

---

## Discovered Product Gaps

| Gap | Root Cause | Impact | Fix |
|-----|------------|--------|-----|
| JS edge extraction | `body_source` empty for JS nodes | 0 edges → no topology | Extract JS function bodies in tree-sitter |
| JS role assignment | No body → no pattern matching | 100% Unknown | Depends on body extraction fix |
| `Manager` suffix missing | Not in `SUFFIX_ROLES` | `DataManager` not detected | Add `'Manager': 'Service'` to heuristics |
| No DM layer in viz | Architecture anti-pattern | Global state sprawl | Implement facade (Option B) |

### Technical Fix for JS Body Extraction

Location: `src/core/tree_sitter_engine.py` or `src/core/complete_extractor.py`

**Current behavior (Python):**
```python
# Python body extraction works
source = code[node.start_byte:node.end_byte]
# Returns: "def foo():\n    return bar()"
```

**Missing for JavaScript:**
```javascript
// JS function_declaration node has start_byte, end_byte
// But body extraction code path not implemented
// Should return: "function refreshGraph() { ... }"
```

**Required change:** In `_extract_function()`, add JavaScript body extraction using the same `start_byte:end_byte` slice that works for Python.

---

*Investigation initiated: 2026-01-19*
*Last updated: 2026-01-19*
*Lead: Claude Code (AI-assisted architecture analysis)*
*Tools: Collider (limited for JS), analyze.py (Gemini), grep, manual AST tracing*
*Key finding: Implicit Global State Machine anti-pattern + Collider JS edge extraction gap*
