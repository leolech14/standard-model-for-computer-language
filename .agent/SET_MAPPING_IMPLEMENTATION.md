# SET MAPPING IMPLEMENTATION GUIDE

> Comprehensive technical reference for extending VIS_FILTERS with theoretical dimensions.
> Generated: 2026-01-18 | Status: PLANNING COMPLETE

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Unmapped Opportunities](#3-unmapped-opportunities)
4. [Data Flow Architecture](#4-data-flow-architecture)
5. [Confidence Matrix](#5-confidence-matrix)
6. [Implementation Specifications](#6-implementation-specifications)
7. [Code References](#7-code-references)
8. [Testing Strategy](#8-testing-strategy)
9. [Appendices](#9-appendices)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Objective

Extend the visualization filter system (`VIS_FILTERS`) to expose theoretical dimensions from the Standard Model of Code that are currently computed but not filterable in the UI.

### 1.2 Current vs Target State

| Metric | Current | Target (Phase 1) | Target (Full) |
|--------|---------|------------------|---------------|
| Filter Sets | 6 | 9 | 19 |
| Dimensions Exposed | 3 | 6 | 10 |
| Edge Filters | 1 (type) | 2 (type + family) | 2 |
| Filter Combinations | ~10K | ~100K | ~1M+ |

### 1.3 Phase 1 Scope

| Set | Dimension | Values | Confidence | Effort |
|-----|-----------|--------|------------|--------|
| `layers` | D2_LAYER | 6 values | 90% | LOW |
| `effects` | D6_EFFECT | 4 values | 90% | LOW |
| `edgeFamilies` | edge.family | 5 values | 60% | MEDIUM |

### 1.4 Key Finding

**Data exists but is nested.** The Python extraction populates `node.dimensions.D2_LAYER` and `node.dimensions.D6_EFFECT`, but `app.js` expects flat properties like `node.tier` and `node.role`. Solution: Flatten during JSON serialization.

---

## 2. CURRENT STATE ANALYSIS

### 2.1 VIS_FILTERS Structure

**File**: `src/core/viz/assets/app.js` (lines 133-146)

```javascript
let VIS_FILTERS = {
    tiers: new Set(),      // D1_TIER: Holarchy levels (L-3 to L12)
    rings: new Set(),      // Ring classification
    roles: new Set(),      // D3_ROLE: 33 semantic roles
    edges: new Set(),      // Edge types (19 values)
    families: new Set(),   // Atom families: LOG, DAT, ORG, EXE, EXT
    files: new Set(),      // File-based filtering
    metadata: {
        showLabels: true,
        showFilePanel: true,
        showReportPanel: true,
        showEdges: true
    }
};
```

### 2.2 Filter Application Flow

**File**: `src/core/viz/assets/app.js` - `filterGraph()` function (lines 2875+)

```
Input Graph
    │
    ├── 1. Density Filter (node count limit)
    │
    ├── 2. Datamap Filter (zoom-based visibility)
    │
    ├── 3. Dimension Filters ← NEW FILTERS GO HERE
    │   ├── Tier Filter (tierFilter.has(getNodeTier(n)))
    │   ├── Ring Filter (ringFilter.has(getNodeRing(n)))
    │   ├── Role Filter (roleFilter.has(node.role))
    │   ├── Family Filter (familyFilter.has(getNodeAtomFamily(n)))
    │   ├── [NEW] Layer Filter (layerFilter.has(node.layer))
    │   └── [NEW] Effect Filter (effectFilter.has(node.effect))
    │
    ├── 4. Edge Filters
    │   ├── Edge Type Filter (edgeFilter.has(edge.edge_type))
    │   └── [NEW] Edge Family Filter (edgeFamilyFilter.has(edge.family))
    │
    └── Output: Filtered {nodes, edges}
```

### 2.3 Accessor Function Pattern

Existing accessor functions in `app.js`:

```javascript
function getNodeTier(n) {
    return n.tier ?? n.dimensions?.D1_TIER ?? 'Unknown';
}

function getNodeRing(n) {
    return n.ring ?? n.layer ?? 'Unknown';
}

function getNodeAtomFamily(n) {
    return n.atom_family || n.family ||
           (n.atom ? n.atom.split('.')[0] : 'Unknown');
}
```

**Pattern to follow** for new accessors:
```javascript
function getNodeLayer(n) {
    return n.layer ?? n.dimensions?.D2_LAYER ?? 'Unknown';
}

function getNodeEffect(n) {
    return n.effect ?? n.dimensions?.D6_EFFECT ?? 'Unknown';
}

function getEdgeFamily(e) {
    return e.family ?? EDGE_TYPE_TO_FAMILY[e.edge_type] ?? 'Unknown';
}
```

---

## 3. UNMAPPED OPPORTUNITIES

### 3.1 Priority Tier 1: Phase 1 Implementation

#### 3.1.1 D2_LAYER (Architectural Layer)

| Property | Value |
|----------|-------|
| **Dimension ID** | D2 |
| **Semantic** | WHERE - Clean Architecture layer |
| **Schema Source** | `schema/particle.schema.json` lines 115-124 |
| **Particle Path** | `particle.dimensions.D2_LAYER` |
| **Domain Values** | `Interface`, `Application`, `Core`, `Infrastructure`, `Test`, `Unknown` |
| **Theory Reference** | Robert Martin's Clean Architecture |
| **Use Cases** | Filter by architectural layer; validate layer dependencies |
| **Color Suggestion** | Interface: cyan, Application: blue, Core: purple, Infrastructure: orange, Test: green |

**Value Descriptions**:
- `Interface` - Controllers, presenters, UI adapters
- `Application` - Use cases, orchestrators, services
- `Core` - Domain entities, business logic, value objects
- `Infrastructure` - Database, external APIs, frameworks
- `Test` - Test code, fixtures, mocks
- `Unknown` - Unclassified

#### 3.1.2 D6_EFFECT (Side Effect Classification)

| Property | Value |
|----------|-------|
| **Dimension ID** | D6 |
| **Semantic** | HOW - Side effect behavior |
| **Schema Source** | `schema/particle.schema.json` lines 146-152 |
| **Particle Path** | `particle.dimensions.D6_EFFECT` |
| **Domain Values** | `Pure`, `Read`, `Write`, `ReadWrite` |
| **Theory Reference** | Functional programming purity |
| **Use Cases** | Identify pure functions; find state mutations; track data flow |
| **Color Suggestion** | Pure: green, Read: blue, Write: red, ReadWrite: orange |

**Value Descriptions**:
- `Pure` - No side effects, deterministic output
- `Read` - Reads external state but doesn't modify
- `Write` - Modifies external state
- `ReadWrite` - Both reads and writes external state

#### 3.1.3 EDGE_FAMILY (Edge Family Classification)

| Property | Value |
|----------|-------|
| **Schema Source** | `schema/particle.schema.json` lines 354-361 |
| **Edge Path** | `edge.family` |
| **Domain Values** | `Structural`, `Dependency`, `Inheritance`, `Semantic`, `Temporal` |
| **Current Status** | **NOT IMPLEMENTED** - Schema exists but edges not classified |
| **Use Cases** | Filter by relationship type; simplify graph view |
| **Color Suggestion** | Structural: gray, Dependency: blue, Inheritance: purple, Semantic: cyan, Temporal: orange |

**Edge Type to Family Mapping**:
```javascript
const EDGE_TYPE_TO_FAMILY = {
    // Structural - containment relationships
    'contains': 'Structural',
    'defines': 'Structural',
    'declares': 'Structural',

    // Dependency - usage relationships
    'imports': 'Dependency',
    'calls': 'Dependency',
    'uses': 'Dependency',
    'references': 'Dependency',
    'requires': 'Dependency',

    // Inheritance - type relationships
    'inherits': 'Inheritance',
    'extends': 'Inheritance',
    'implements': 'Inheritance',
    'mixes': 'Inheritance',

    // Semantic - meaning relationships
    'related_to': 'Semantic',
    'similar_to': 'Semantic',

    // Temporal - lifecycle relationships
    'creates': 'Temporal',
    'destroys': 'Temporal',
    'initializes': 'Temporal'
};
```

### 3.2 Priority Tier 2: Future Implementation

| Set | Dimension | Values | Status | Notes |
|-----|-----------|--------|--------|-------|
| `boundaries` | D4_BOUNDARY | Internal, Input, Output, I-O | Data exists | Flow direction |
| `states` | D5_STATE | Stateful, Stateless | Data exists | Binary toggle |
| `lifecycles` | D7_LIFECYCLE | Create, Use, Destroy | Data exists | Temporal phase |
| `confidence` | D8_TRUST | Low/Medium/High | Data exists | Needs bucketing |
| `intents` | D9_INTENT | Documented, Implicit, Ambiguous, Contradictory | Data exists | Popper World 2 |
| `languages` | D10_LANGUAGE | Python, JS, Go, etc. | Data exists | Multi-lang support |

### 3.3 Priority Tier 3: Domain-Specific

| Set | Domain | Values | Status | Notes |
|-----|--------|--------|--------|-------|
| `violations` | Antimatter laws | AM001-AM005 | Partial | In particle.violations |
| `severity` | Violation level | ERROR, WARNING, INFO | Partial | In particle.violations |
| `contexts` | DDD bounded context | Domain-specific | Partial | In particle.ddd |
| `phases` | Atom phase | DATA, LOGIC, ORGANIZATION, EXECUTION | Mapped as families | Higher-level grouping |

---

## 4. DATA FLOW ARCHITECTURE

### 4.1 End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     PYTHON EXTRACTION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  src/core/universal_classifier.py                               │
│  ├── Analyzes source files                                      │
│  ├── Assigns all 8 dimensions:                                  │
│  │   └── D1_WHAT, D2_LAYER, D3_ROLE, D4_BOUNDARY,              │
│  │       D5_STATE, D6_EFFECT, D7_LIFECYCLE, D8_TRUST           │
│  └── Returns particle dict with nested dimensions               │
│                                                                 │
│  src/core/edge_extractor.py                                     │
│  ├── Extracts relationships                                     │
│  ├── Creates edges with: source, target, edge_type             │
│  └── ❌ DOES NOT assign edge.family                            │
│                                                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     JSON SERIALIZATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  src/core/unified_analysis.py (lines 240-260)                   │
│  ├── Converts particles to JSON nodes                           │
│  ├── Current: Preserves nested structure                        │
│  │   └── node.dimensions.D2_LAYER (nested)                     │
│  ├── [NEEDED]: Flatten key dimensions                           │
│  │   └── node.layer = node.dimensions.D2_LAYER                 │
│  │   └── node.effect = node.dimensions.D6_EFFECT               │
│  └── Outputs graph.json                                         │
│                                                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VISUALIZATION                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  src/core/viz/assets/app.js                                     │
│  ├── Loads graph.json                                           │
│  ├── VIS_FILTERS controls visibility                            │
│  ├── filterGraph() applies all filters                          │
│  ├── Accessor functions read node properties                    │
│  │   └── Current: getNodeTier(n), getNodeRole(n)               │
│  │   └── [NEEDED]: getNodeLayer(n), getNodeEffect(n)           │
│  └── 3d-force-graph renders filtered data                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Current Node Structure (from graph.json)

```json
{
  "id": "topology_reasoning.py::TopologyClassifier",
  "name": "TopologyClassifier",
  "type": "class",
  "file": "src/core/topology_reasoning.py",
  "line": 45,

  "tier": 4,
  "role": "DTO",
  "atom": "ORG.AGG.M",
  "atom_family": "ORG",

  "dimensions": {
    "D1_WHAT": "ORG.AGG.M",
    "D2_LAYER": "Application",
    "D3_ROLE": "Utility",
    "D4_BOUNDARY": "Internal",
    "D5_STATE": "Stateful",
    "D6_EFFECT": "ReadWrite",
    "D7_LIFECYCLE": "Use",
    "D8_TRUST": 30.0
  }
}
```

### 4.3 Target Node Structure (after flattening)

```json
{
  "id": "topology_reasoning.py::TopologyClassifier",
  "name": "TopologyClassifier",
  "type": "class",
  "file": "src/core/topology_reasoning.py",
  "line": 45,

  "tier": 4,
  "role": "DTO",
  "atom": "ORG.AGG.M",
  "atom_family": "ORG",

  "layer": "Application",
  "effect": "ReadWrite",

  "dimensions": {
    "D1_WHAT": "ORG.AGG.M",
    "D2_LAYER": "Application",
    "D3_ROLE": "Utility",
    "D4_BOUNDARY": "Internal",
    "D5_STATE": "Stateful",
    "D6_EFFECT": "ReadWrite",
    "D7_LIFECYCLE": "Use",
    "D8_TRUST": 30.0
  }
}
```

### 4.4 Current Edge Structure

```json
{
  "source": "topology_reasoning.py::topology_reasoning",
  "target": "statistics",
  "edge_type": "imports",
  "resolution": "external",
  "weight": 1.0,
  "confidence": 1.0
}
```

### 4.5 Target Edge Structure

```json
{
  "source": "topology_reasoning.py::topology_reasoning",
  "target": "statistics",
  "edge_type": "imports",
  "family": "Dependency",
  "resolution": "external",
  "weight": 1.0,
  "confidence": 1.0
}
```

---

## 5. CONFIDENCE MATRIX

### 5.1 Phase 1 Confidence Assessment

| Question | layers (D2_LAYER) | effects (D6_EFFECT) | edgeFamilies |
|----------|-------------------|---------------------|--------------|
| **Data computed in Python?** | ✅ YES (95%) | ✅ YES (95%) | ❌ NO (100%) |
| **Data in graph.json?** | ✅ YES nested (95%) | ✅ YES nested (95%) | ❌ NO (100%) |
| **Property path known?** | ✅ `dimensions.D2_LAYER` | ✅ `dimensions.D6_EFFECT` | ⚠️ Need to add |
| **Values populated?** | ✅ 6 values | ✅ 4 values | N/A |
| **app.js can access?** | ⚠️ Needs accessor | ⚠️ Needs accessor | ⚠️ Needs accessor |
| **UI pattern exists?** | ✅ Copy from tier | ✅ Copy from tier | ✅ Copy from edges |
| **Overall Confidence** | **90%** | **90%** | **60%** |

### 5.2 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Dimensions not populated for some nodes | Medium | Low | Default to "Unknown" |
| Performance degradation with more filters | Low | Medium | Lazy evaluation, caching |
| UI cluttered with too many options | Medium | Medium | Collapsible sections, presets |
| Edge family classification incorrect | Medium | Low | Review mapping, allow override |

### 5.3 Evidence Trail

**D2_LAYER is populated** - Verified in:
- `src/core/classification/universal_classifier.py` - Assignment logic
- `.collider/output_llm-oriented_core_20260118_191534.json` - Sample output shows values

**D6_EFFECT is populated** - Verified in:
- `src/core/classification/universal_classifier.py` - Assignment logic
- Sample output shows "Pure", "Read", "Write", "ReadWrite" values

**edge.family is NOT populated** - Verified in:
- `src/core/edge_extractor.py` - No family assignment
- Sample output shows no family field on edges

---

## 6. IMPLEMENTATION SPECIFICATIONS

### 6.1 Implementation Option A: Flatten in Python (RECOMMENDED)

#### 6.1.1 Modify unified_analysis.py

**File**: `src/core/unified_analysis.py`
**Location**: Node serialization (around line 240-260)

```python
# Add after existing node property assignments
def serialize_node(particle):
    node = {
        "id": particle["id"],
        "name": particle["name"],
        # ... existing fields ...

        # Flatten key dimensions for visualization
        "layer": particle.get("dimensions", {}).get("D2_LAYER", "Unknown"),
        "effect": particle.get("dimensions", {}).get("D6_EFFECT", "Unknown"),

        # Keep full dimensions for reference
        "dimensions": particle.get("dimensions", {})
    }
    return node
```

#### 6.1.2 Add edge family classification

**File**: `src/core/edge_extractor.py`
**Location**: Edge creation

```python
EDGE_TYPE_TO_FAMILY = {
    'contains': 'Structural',
    'defines': 'Structural',
    'imports': 'Dependency',
    'calls': 'Dependency',
    'uses': 'Dependency',
    'inherits': 'Inheritance',
    'extends': 'Inheritance',
    'implements': 'Inheritance',
}

def create_edge(source, target, edge_type, **kwargs):
    return {
        "source": source,
        "target": target,
        "edge_type": edge_type,
        "family": EDGE_TYPE_TO_FAMILY.get(edge_type, "Dependency"),
        **kwargs
    }
```

### 6.2 Implementation Option B: Read Nested in app.js

#### 6.2.1 Add accessor functions

**File**: `src/core/viz/assets/app.js`
**Location**: After existing accessor functions (around line 500)

```javascript
/**
 * Get architectural layer (D2_LAYER) from node
 * Values: Interface, Application, Core, Infrastructure, Test, Unknown
 */
function getNodeLayer(n) {
    return n.layer ?? n.dimensions?.D2_LAYER ?? 'Unknown';
}

/**
 * Get side effect classification (D6_EFFECT) from node
 * Values: Pure, Read, Write, ReadWrite
 */
function getNodeEffect(n) {
    return n.effect ?? n.dimensions?.D6_EFFECT ?? 'Unknown';
}

/**
 * Get edge family from edge
 * Values: Structural, Dependency, Inheritance, Semantic, Temporal
 */
function getEdgeFamily(e) {
    if (e.family) return e.family;

    const EDGE_TYPE_TO_FAMILY = {
        'contains': 'Structural',
        'defines': 'Structural',
        'imports': 'Dependency',
        'calls': 'Dependency',
        'uses': 'Dependency',
        'inherits': 'Inheritance',
        'extends': 'Inheritance',
        'implements': 'Inheritance',
        'references': 'Semantic',
        'creates': 'Temporal',
        'destroys': 'Temporal'
    };

    return EDGE_TYPE_TO_FAMILY[e.edge_type] ?? 'Dependency';
}
```

### 6.3 VIS_FILTERS Extension

**File**: `src/core/viz/assets/app.js`
**Location**: VIS_FILTERS declaration (lines 133-146)

```javascript
let VIS_FILTERS = {
    // Existing
    tiers: new Set(),
    rings: new Set(),
    roles: new Set(),
    edges: new Set(),
    families: new Set(),
    files: new Set(),

    // NEW - Phase 1
    layers: new Set(),        // D2_LAYER: Interface, Application, Core, Infrastructure, Test
    effects: new Set(),       // D6_EFFECT: Pure, Read, Write, ReadWrite
    edgeFamilies: new Set(),  // Structural, Dependency, Inheritance, Semantic, Temporal

    metadata: {
        showLabels: true,
        showFilePanel: true,
        showReportPanel: true,
        showEdges: true
    }
};
```

### 6.4 Filter Application

**File**: `src/core/viz/assets/app.js`
**Location**: filterGraph() function (around line 2900)

```javascript
function filterGraph(graph, density, datamaps, filters) {
    // ... existing code ...

    // Get new filters
    const layerFilter = filters.layers;
    const effectFilter = filters.effects;
    const edgeFamilyFilter = filters.edgeFamilies;

    const layerFilterActive = layerFilter.size > 0;
    const effectFilterActive = effectFilter.size > 0;
    const edgeFamilyFilterActive = edgeFamilyFilter.size > 0;

    // Apply node filters
    visibleNodes = visibleNodes.filter(n => {
        // ... existing filters ...

        // NEW: Layer filter
        if (layerFilterActive && !layerFilter.has(getNodeLayer(n))) return false;

        // NEW: Effect filter
        if (effectFilterActive && !effectFilter.has(getNodeEffect(n))) return false;

        return true;
    });

    // Apply edge filters
    visibleEdges = visibleEdges.filter(e => {
        // ... existing edge type filter ...

        // NEW: Edge family filter
        if (edgeFamilyFilterActive && !edgeFamilyFilter.has(getEdgeFamily(e))) return false;

        return true;
    });

    // ... rest of function ...
}
```

### 6.5 clearAllFilters() Update

**File**: `src/core/viz/assets/app.js`
**Location**: clearAllFilters() function (around line 5175)

```javascript
function clearAllFilters() {
    // Existing
    VIS_FILTERS.tiers.clear();
    VIS_FILTERS.rings.clear();
    VIS_FILTERS.families.clear();
    VIS_FILTERS.roles.clear();
    VIS_FILTERS.files.clear();
    VIS_FILTERS.edges.clear();

    // NEW - Phase 1
    VIS_FILTERS.layers.clear();
    VIS_FILTERS.effects.clear();
    VIS_FILTERS.edgeFamilies.clear();

    // ... rest of function ...
}
```

### 6.6 Color Definitions

**File**: `src/core/viz/assets/app.js`
**Location**: Color configuration section

```javascript
const LAYER_COLORS = {
    'Interface': '#00d4ff',      // Cyan
    'Application': '#4d94ff',    // Blue
    'Core': '#9966ff',           // Purple
    'Infrastructure': '#ff9933', // Orange
    'Test': '#33cc66',           // Green
    'Unknown': '#888888'         // Gray
};

const EFFECT_COLORS = {
    'Pure': '#22c55e',           // Green
    'Read': '#3b82f6',           // Blue
    'Write': '#ef4444',          // Red
    'ReadWrite': '#f59e0b'       // Orange/Amber
};

const EDGE_FAMILY_COLORS = {
    'Structural': '#888888',     // Gray
    'Dependency': '#4d94ff',     // Blue
    'Inheritance': '#9966ff',    // Purple
    'Semantic': '#00d4ff',       // Cyan
    'Temporal': '#ff9933'        // Orange
};
```

---

## 7. CODE REFERENCES

### 7.1 Key Files

| File | Purpose | Lines of Interest |
|------|---------|-------------------|
| `src/core/viz/assets/app.js` | Main visualization | 133-146 (VIS_FILTERS), 2875+ (filterGraph), 5175+ (clearAllFilters) |
| `src/core/unified_analysis.py` | JSON serialization | 240-260 (node conversion) |
| `src/core/edge_extractor.py` | Edge extraction | Edge creation logic |
| `src/core/classification/universal_classifier.py` | Dimension assignment | D2_LAYER, D6_EFFECT logic |
| `schema/particle.schema.json` | Schema definitions | 115-124 (D2_LAYER), 146-152 (D6_EFFECT), 354-361 (edge.family) |
| `schema/types.py` | Python types | Layer, Effect, EdgeFamily enums |

### 7.2 Existing Patterns to Follow

**Tier Filter Pattern** (lines 2905-2910):
```javascript
const tierFilter = filters.tiers;
const tierFilterActive = tierFilter.size > 0;
// ...
if (tierFilterActive && !tierFilter.has(getNodeTier(n))) return false;
```

**Edge Type Filter Pattern** (lines 2950-2955):
```javascript
const edgeFilter = filters.edges;
const edgeFilterActive = edgeFilter.size > 0;
// ...
if (edgeFilterActive && !edgeFilter.has(e.edge_type || e.type)) return false;
```

### 7.3 Schema References

**D2_LAYER Schema** (`particle.schema.json` lines 115-124):
```json
"D2_LAYER": {
  "type": "string",
  "enum": ["Interface", "Application", "Core", "Infrastructure", "Test", "Unknown"],
  "description": "Clean Architecture layer"
}
```

**D6_EFFECT Schema** (`particle.schema.json` lines 146-152):
```json
"D6_EFFECT": {
  "type": "string",
  "enum": ["Pure", "Read", "Write", "ReadWrite"],
  "description": "Side effect classification"
}
```

**EdgeFamily Schema** (`particle.schema.json` lines 354-361):
```json
"family": {
  "type": "string",
  "enum": ["Structural", "Dependency", "Inheritance", "Semantic", "Temporal"],
  "description": "Edge family classification"
}
```

---

## 8. TESTING STRATEGY

### 8.1 Verification Steps

#### Step 1: Verify Data Availability
```bash
# Generate fresh output
./collider full . --output .collider

# Check for D2_LAYER values
grep -o '"D2_LAYER": "[^"]*"' .collider/*.json | sort | uniq -c

# Check for D6_EFFECT values
grep -o '"D6_EFFECT": "[^"]*"' .collider/*.json | sort | uniq -c

# Check for edge.family values (should be none before implementation)
grep -o '"family": "[^"]*"' .collider/*.json | sort | uniq -c
```

#### Step 2: Test Filter Logic
```javascript
// In browser console after loading visualization
console.log('Layers:', [...new Set(window.GRAPH_DATA.nodes.map(n => n.dimensions?.D2_LAYER))]);
console.log('Effects:', [...new Set(window.GRAPH_DATA.nodes.map(n => n.dimensions?.D6_EFFECT))]);
```

#### Step 3: Test Filter Application
```javascript
// Add layer filter
VIS_FILTERS.layers.add('Core');
refreshGraph();
// Should show only Core layer nodes

// Clear and test effect
clearAllFilters();
VIS_FILTERS.effects.add('Pure');
refreshGraph();
// Should show only pure functions
```

### 8.2 Expected Outcomes

| Test | Expected Result |
|------|-----------------|
| Layer filter "Core" | Only domain logic nodes visible |
| Layer filter "Infrastructure" | Only persistence/external nodes visible |
| Effect filter "Pure" | Only side-effect-free nodes visible |
| Effect filter "Write" | Only state-mutating nodes visible |
| Edge family "Structural" | Only containment edges visible |
| Edge family "Inheritance" | Only extends/implements edges visible |
| Combined filters | Intersection of all active filters |
| Clear all filters | All nodes/edges visible |

### 8.3 Regression Checks

- [ ] Existing tier filter still works
- [ ] Existing role filter still works
- [ ] Existing family filter still works
- [ ] Existing edge type filter still works
- [ ] Zero-node protection triggers correctly
- [ ] Preset switching clears new filters
- [ ] Legend UI updates for new filters

---

## 9. APPENDICES

### Appendix A: Complete Dimension Reference

| ID | Name | Facet | Values | Description |
|----|------|-------|--------|-------------|
| D1 | WHAT | P (Personality) | Atom taxonomy | What type of code element |
| D2 | LAYER | E (Energy) | Interface, Application, Core, Infrastructure, Test | Clean Architecture layer |
| D3 | ROLE | M (Matter) | 33 semantic roles | Semantic purpose |
| D4 | BOUNDARY | S (Space) | Internal, Input, Output, I-O | Information flow direction |
| D5 | STATE | T (Time) | Stateful, Stateless | State management |
| D6 | EFFECT | - | Pure, Read, Write, ReadWrite | Side effect behavior |
| D7 | LIFECYCLE | T (Time) | Create, Use, Destroy | Object lifecycle phase |
| D8 | TRUST | - | 0-100 | Classification confidence |
| D9 | INTENT | - | Documented, Implicit, Ambiguous, Contradictory | Programmer intent clarity |
| D10 | LANGUAGE | M (Matter) | Python, JS, Go, etc. | Programming language |

### Appendix B: Edge Type to Family Mapping

| Edge Type | Family | Rationale |
|-----------|--------|-----------|
| contains | Structural | Containment relationship |
| defines | Structural | Definition relationship |
| declares | Structural | Declaration relationship |
| imports | Dependency | Module dependency |
| calls | Dependency | Function/method call |
| uses | Dependency | Usage relationship |
| requires | Dependency | Requirement relationship |
| references | Dependency | Reference relationship |
| inherits | Inheritance | Class inheritance |
| extends | Inheritance | Class extension |
| implements | Inheritance | Interface implementation |
| mixes | Inheritance | Mixin inclusion |
| related_to | Semantic | Semantic relationship |
| similar_to | Semantic | Similarity relationship |
| creates | Temporal | Object creation |
| destroys | Temporal | Object destruction |
| initializes | Temporal | Initialization |

### Appendix C: Implementation Checklist

#### Phase 1A: Layer Filter
- [ ] Add `layers: new Set()` to VIS_FILTERS
- [ ] Add `getNodeLayer()` accessor function
- [ ] Add LAYER_COLORS configuration
- [ ] Update filterGraph() with layer filter
- [ ] Update clearAllFilters() to clear layers
- [ ] Add layer filter UI (copy tier pattern)
- [ ] Test with generated data

#### Phase 1B: Effect Filter
- [ ] Add `effects: new Set()` to VIS_FILTERS
- [ ] Add `getNodeEffect()` accessor function
- [ ] Add EFFECT_COLORS configuration
- [ ] Update filterGraph() with effect filter
- [ ] Update clearAllFilters() to clear effects
- [ ] Add effect filter UI (copy tier pattern)
- [ ] Test with generated data

#### Phase 1C: Edge Family Filter
- [ ] Add `edgeFamilies: new Set()` to VIS_FILTERS
- [ ] Add `getEdgeFamily()` accessor function
- [ ] Add EDGE_FAMILY_COLORS configuration
- [ ] Add EDGE_TYPE_TO_FAMILY mapping
- [ ] Update filterGraph() with edge family filter
- [ ] Update clearAllFilters() to clear edgeFamilies
- [ ] Add edge family filter UI (copy edge type pattern)
- [ ] (Optional) Update edge_extractor.py to assign family
- [ ] Test with generated data

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-18 | Claude | Initial comprehensive document |

---

## Related Documents

- `.agent/FILTER_SYSTEM_AUDIT.md` - Filter system architecture audit
- `schema/particle.schema.json` - Particle schema definition
- `docs/theory/FOUNDATIONAL_THEORIES.md` - Theoretical foundations
- `CLAUDE.md` - Agent instructions and project overview
