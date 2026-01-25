# Data Trade Exchange (DTE) - Semantic Matching Research

**Date:** 2026-01-25
**Phase:** Architecture Design - Context Gathering
**Purpose:** Research how systems handle semantic matching and value mapping to inform DTE design

---

## Executive Summary

The Data Trade Exchange (DTE) is a **central clearinghouse** where our systems go to match and calculate the interchangeable equivalency of objects they handle. This research examines industry patterns and our current implementation to design a production-grade semantic matching layer.

**Key Finding:** Our current architecture (UPB + property-query) implements **the binding graph** (WHAT connects to WHAT). The DTE completes the picture by implementing **the exchange engine** (HOW values transform between domains).

---

## 1. Current Architecture Analysis

### 1.1 Property Resolution Chain (property-query.js)

Our current provider-based resolution already implements a priority chain:

| Priority | Provider | Purpose |
|----------|----------|---------|
| **100** | OVERRIDE | User-forced values (sliders, toggles) |
| **80** | UPB | Declarative bindings from schema |
| **20** | RAW | Entity's own fields |
| **0** | DEFAULT | Schema fallbacks |

**Insight:** This is a **read path**. DTE will add a complementary **exchange path** for value transformation.

### 1.2 Scale Functions (upb/scales.js)

Current scale implementations:

```javascript
SCALES = {
    linear:   (v, min, max) => (v - min) / (max - min || 1),
    log:      (v, min, max) => logarithmic normalization,
    sqrt:     (v, min, max) => square root mapping,
    inverse:  (v, min, max) => 1 - linear,
    exp:      (v, min, max) => exponential emphasis,
    discrete: (v, min, max, domain) => categorical index mapping
}
```

**Gap Identified:** These are one-way transforms to [0,1]. DTE needs:
- Bidirectional transforms (encode/decode)
- Composition of multiple transforms
- Domain-aware type conversion

### 1.3 Datamap Matching (datamap.js)

Pattern matching for node classification:

```javascript
match: {
    atom_families: ['LOG', 'ORG'],    // Semantic category
    atom_prefixes: ['LOG.FNC'],       // Pattern match
    tiers: ['T0', 'T1'],              // Hierarchy level
    rings: ['CORE', 'OUTER'],         // Topology position
    roles: ['UTILITY', 'ORCHESTRATOR'] // Semantic role
}
```

**Insight:** This is **semantic matching** - exactly what DTE needs to generalize.

---

## 2. Industry Patterns for Semantic Value Mapping

### 2.1 Broker/Mediator Pattern

From [Enterprise Architecture research](https://www.linkedin.com/pulse/architecture-learnings-part-16-broker-pattern-software-hitesh-das):

> "The Broker Pattern promotes decoupling between objects or services by introducing a central entity that handles communication and coordination."

**Applicability to DTE:**
- DTE acts as the **mediator** between different value domains
- Components don't need to know about each other's internal representations
- All transformations go through the central exchange

### 2.2 Event-Driven Architecture (Mediator Topology)

From [O'Reilly Software Architecture Patterns](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch02.html):

> "The mediator coordinates the data flow between sources and applications. The mediator stores a virtual and global view of real data (global schema) and the mappings between global and local views."

**DTE Components (mapped from this pattern):**

| EDA Component | DTE Equivalent |
|---------------|----------------|
| Queue | Request buffer |
| Mediator | Exchange engine |
| Channels | Domain pipes |
| Processors | Transform functions |

### 2.3 Semantic Data Integration

From [PMC Semantic Integration Research](https://pmc.ncbi.nlm.nih.gov/articles/PMC7924686/):

> "Wrappers convert data to a common data model (OEM - Object Exchange Model) and mediators combine and integrate them."

**Key Insight:** DTE needs a **canonical intermediate representation** that all domains can convert to/from.

### 2.4 Design Tokens Architecture (W3C 2025)

From [W3C Design Tokens Specification](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/):

The stable Design Tokens Specification (2025.10) provides a model for layered abstraction:

```
Layer 1: Global Primitives
    --color-blue-600: #0052CC

Layer 2: Semantic Mappings
    --color-interactive: var(--color-blue-600)

Layer 3: Component Tokens
    --button-background: var(--color-interactive)
```

**Application to DTE:**

| Token Layer | DTE Equivalent |
|-------------|----------------|
| Primitives | Raw data values |
| Semantic | Domain-specific meanings |
| Component | Channel-specific outputs |

### 2.5 Semantic Layer Architecture (2025 Trends)

From [Enterprise Knowledge Research](https://enterprise-knowledge.com/data-management-and-architecture-trends-for-2025/):

> "Semantic layers connect data to context through metadata, taxonomies, ontologies, and knowledge graphs. This supports reasoning, inference, and richer queries."

**Implication:** DTE should support:
- Metadata about transformations (not just the transforms)
- Queryable transformation history (AUDIT operation)
- Inference of missing mappings

---

## 3. D3.js Scale Patterns (Reference Implementation)

D3.js scales are the gold standard for data-to-visual mapping:

### 3.1 Scale Types

```javascript
// Continuous → Continuous
d3.scaleLinear()    // Linear interpolation
d3.scaleLog()       // Logarithmic
d3.scalePow()       // Power (including sqrt)
d3.scaleTime()      // Temporal values
d3.scaleSequential() // Sequential color

// Discrete → Discrete
d3.scaleOrdinal()   // Category → Color

// Continuous → Discrete
d3.scaleQuantize()  // Bins continuous to discrete
d3.scaleQuantile()  // Quantile-based bins
d3.scaleThreshold() // Explicit breakpoints

// Discrete → Continuous
d3.scaleBand()      // Categories with spacing
d3.scalePoint()     // Categories at points
```

### 3.2 Key D3 Scale Properties

| Property | Purpose | DTE Equivalent |
|----------|---------|----------------|
| `.domain()` | Input value range | Source domain |
| `.range()` | Output value range | Target domain |
| `.invert()` | Reverse mapping | Decode operation |
| `.clamp()` | Boundary handling | Coercion rules |
| `.nice()` | Round to nice values | Presentation formatting |

---

## 4. DTE Architecture Proposal

### 4.1 Core Operations

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA TRADE EXCHANGE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   QUOTE(from, to, value)   → { rate, formula, confidence }  │
│   │                                                          │
│   │  "What would this value become in the target domain?"    │
│   │                                                          │
│   TRADE(from, to, value)   → transformed_value              │
│   │                                                          │
│   │  "Execute the conversion, return the result."            │
│   │                                                          │
│   BATCH([{from, to, value}...]) → [transformed_values...]   │
│   │                                                          │
│   │  "Perform multiple conversions atomically."              │
│   │                                                          │
│   REGISTER(from, to, fn)   → exchange_id                    │
│   │                                                          │
│   │  "Add a new exchange rate/transformation."               │
│   │                                                          │
│   AUDIT(entity_id)         → [transaction_history...]       │
│   │                                                          │
│   │  "Show all conversions for this entity."                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Domain Registry

```javascript
const DOMAINS = {
    // Data Domains (Source)
    'data.loc':        { type: 'number', unit: 'lines', range: [0, Infinity] },
    'data.complexity': { type: 'number', unit: 'cyclomatic', range: [1, Infinity] },
    'data.depth':      { type: 'number', unit: 'levels', range: [0, 20] },
    'data.atom':       { type: 'categorical', cardinality: 3616 },
    'data.role':       { type: 'categorical', cardinality: 33 },
    'data.tier':       { type: 'ordinal', levels: ['T0', 'T1', 'T2'] },

    // Visual Domains (Target)
    'visual.size':     { type: 'number', unit: 'pixels', range: [1, 50] },
    'visual.color':    { type: 'color', space: 'oklch' },
    'visual.opacity':  { type: 'number', unit: 'alpha', range: [0, 1] },
    'visual.position': { type: 'vector3', unit: 'world_units' },
    'visual.label':    { type: 'string', maxLength: 64 },

    // Intermediate Domains (Canonical)
    'canonical.normalized': { type: 'number', range: [0, 1] },
    'canonical.rank':       { type: 'number', range: [0, 1] },
    'canonical.category':   { type: 'index', range: [0, N] }
};
```

### 4.3 Exchange Rate Registry

```javascript
const EXCHANGES = [
    // Continuous → Normalized
    { from: 'data.loc', to: 'canonical.normalized', fn: 'log', params: { base: 10 } },
    { from: 'data.complexity', to: 'canonical.normalized', fn: 'sqrt' },
    { from: 'data.depth', to: 'canonical.normalized', fn: 'linear' },

    // Normalized → Visual
    { from: 'canonical.normalized', to: 'visual.size', fn: 'lerp', params: { min: 2, max: 30 } },
    { from: 'canonical.normalized', to: 'visual.opacity', fn: 'lerp', params: { min: 0.3, max: 1.0 } },

    // Categorical → Color
    { from: 'data.atom', to: 'visual.color', fn: 'oklch_map', params: { hue_offset: 0 } },
    { from: 'data.role', to: 'visual.color', fn: 'palette_index' },
    { from: 'data.tier', to: 'visual.color', fn: 'ordinal_lightness' },

    // Composites (chainable)
    { from: 'data.loc', to: 'visual.size', via: ['canonical.normalized'] }
];
```

### 4.4 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                           UPB (Binding Layer)                         │
│              "WHAT visual channel shows WHAT data field"              │
├──────────────────────────────────────────────────────────────────────┤
│                                  │                                    │
│   binding: {                     │                                    │
│     node.color = data.role       │  ← Declarative intent              │
│     node.size  = data.loc        │                                    │
│   }                              │                                    │
│                                  ▼                                    │
├──────────────────────────────────────────────────────────────────────┤
│                           DTE (Exchange Layer)                        │
│               "HOW to transform values between domains"               │
├──────────────────────────────────────────────────────────────────────┤
│                                  │                                    │
│   ┌─────────────┐   ┌──────────────────┐   ┌─────────────┐          │
│   │   DOMAIN    │   │    EXCHANGE      │   │   DOMAIN    │          │
│   │   REGISTRY  │◀──│    REGISTRY      │──▶│   SCHEMA    │          │
│   │ (what exists)│   │ (how to convert) │   │ (constraints)│          │
│   └─────────────┘   └──────────────────┘   └─────────────┘          │
│                              │                                        │
│                              ▼                                        │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                     TRANSFORM ENGINE                          │   │
│   │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      │   │
│   │  │ QUOTE   │   │ TRADE   │   │ BATCH   │   │ AUDIT   │      │   │
│   │  └─────────┘   └─────────┘   └─────────┘   └─────────┘      │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                              │                                        │
│                              ▼                                        │
├──────────────────────────────────────────────────────────────────────┤
│                      PROPERTY-QUERY (Resolution Layer)                │
│                 "Which provider wins for this channel?"               │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.5 Value Flow Example

```
User changes slider: "Color by LoC"

1. UPB BINDING (declarative)
   node.color ← data.loc

2. DTE TRADE (transformation)
   TRADE('data.loc', 'visual.color', 450)

   Step 1: data.loc → canonical.normalized
           log10(450) / log10(maxLoc) = 0.72

   Step 2: canonical.normalized → visual.color
           oklch(65%, 0.15, 0.72 * 360°)
           = oklch(65%, 0.15, 259°)

   Result: "oklch(65% 0.15 259)"

3. PROPERTY-QUERY (resolution)
   Q.node(node, 'color') → "oklch(65% 0.15 259)"
```

---

## 5. Implementation Recommendations

### 5.1 Phase 1: Core Exchange Engine

```javascript
// dte.js - Data Trade Exchange
const DTE = (function() {
    const domains = new Map();
    const exchanges = new Map();
    const auditLog = [];

    return {
        // Register a domain
        registerDomain(id, schema) { ... },

        // Register an exchange rate
        registerExchange(from, to, fn, params = {}) { ... },

        // Get exchange rate without executing
        quote(from, to, value) {
            const path = findPath(from, to);
            const formula = describeTransform(path);
            const confidence = calculateConfidence(path);
            return { path, formula, confidence };
        },

        // Execute conversion
        trade(from, to, value, { audit = true } = {}) {
            const path = findPath(from, to);
            let current = value;
            for (const step of path) {
                current = step.fn(current, step.params);
            }
            if (audit) {
                auditLog.push({ from, to, input: value, output: current, timestamp: Date.now() });
            }
            return current;
        },

        // Batch conversions
        batch(trades) {
            return trades.map(t => this.trade(t.from, t.to, t.value));
        },

        // Query audit history
        audit(entityId) {
            return auditLog.filter(e => e.entityId === entityId);
        }
    };
})();
```

### 5.2 Phase 2: Integration with UPB

```javascript
// When UPB binding changes:
function onBindingChange(channel, dataField) {
    const from = `data.${dataField}`;
    const to = `visual.${channel}`;

    // Check if exchange exists
    const quote = DTE.quote(from, to, sampleValue);

    if (!quote.path) {
        console.warn(`No exchange path from ${from} to ${to}`);
        return false;
    }

    // Register with property-query
    propertyQuery.setTransform(channel, (value) => DTE.trade(from, to, value));
    return true;
}
```

### 5.3 Phase 3: OKLCH Color Exchange

```javascript
// Register OKLCH exchanges
DTE.registerExchange('canonical.normalized', 'visual.color.hue',
    (n) => n * 360, { space: 'oklch' });

DTE.registerExchange('canonical.normalized', 'visual.color.chroma',
    (n) => 0.05 + n * 0.25, { space: 'oklch' });

DTE.registerExchange('canonical.normalized', 'visual.color.lightness',
    (n) => 0.30 + n * 0.50, { space: 'oklch' });

// Composite color exchange
DTE.registerExchange('canonical.normalized', 'visual.color',
    (n, params) => {
        const h = DTE.trade('canonical.normalized', 'visual.color.hue', n);
        const c = DTE.trade('canonical.normalized', 'visual.color.chroma', n);
        const l = DTE.trade('canonical.normalized', 'visual.color.lightness', n);
        return `oklch(${l}% ${c} ${h})`;
    });
```

---

## 6. Key Decisions Needed

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Path finding** | BFS, weighted, manual | BFS for simplicity, weighted for optimization |
| **Caching** | Per-frame, persistent, LRU | LRU with epoch-based invalidation |
| **Audit storage** | Memory, IndexedDB, none | Memory with size cap (1000 entries) |
| **Missing exchanges** | Fail, interpolate, warn | Warn + reasonable default |
| **Composition** | Implicit via path, explicit pipes | Implicit with `via` field for control |

---

## 7. Sources

### Internal Codebase
- `src/core/viz/assets/modules/property-query.js` - Provider chain implementation
- `src/core/viz/assets/modules/upb/scales.js` - Scale functions
- `src/core/viz/assets/modules/datamap.js` - Semantic matching

### External Research
- [W3C Design Tokens Specification 2025.10](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/)
- [PMC - Semantic Integration of Heterogeneous Data Sources](https://pmc.ncbi.nlm.nih.gov/articles/PMC7924686/)
- [O'Reilly - Event-Driven Architecture Patterns](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch02.html)
- [Enterprise Knowledge - Semantic Layers 2025](https://enterprise-knowledge.com/data-management-and-architecture-trends-for-2025/)
- [LinkedIn - Broker Pattern in Software Architecture](https://www.linkedin.com/pulse/architecture-learnings-part-16-broker-pattern-software-hitesh-das)
- [Airbyte - Data Integration Patterns](https://airbyte.com/data-engineering-resources/data-integration-patterns)
- [dbt Labs - Data Integration 2025](https://www.getdbt.com/blog/data-integration)
- [Penpot - Design Tokens and CSS Variables](https://penpot.app/blog/the-developers-guide-to-design-tokens-and-css-variables/)

---

## 8. Next Steps

1. **Validate architecture** with Gemini long-context analysis
2. **Prototype DTE.js** (~150 lines) with core operations
3. **Integrate with existing scales.js** (extend, don't replace)
4. **Add to UI_REFACTOR_VISION.md** as confirmed architectural component
5. **Create task registry entries** for implementation phases

