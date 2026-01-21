# Scale Transforms - Warp Functions for Data Visualization

> Shape the distribution of ANY attribute before mapping to visuals.

---

## The Core Insight

Scales are **transfer functions** that reshape data distributions before visualization.

```
RAW DATA  ────►  SCALE TRANSFORM  ────►  NORMALIZED [0,1]  ────►  VISUAL PROPERTY
```

Without scales, all mappings are linear (boring, often wrong).
With scales, you can **warp the shape** to match human perception.

---

## Available Scales

| Scale | Formula | Visual Effect | Best For |
|-------|---------|---------------|----------|
| **linear** | `(v-min)/(max-min)` | Even spread | Uniform distributions |
| **sqrt** | `sqrt(v) normalized` | Compress large values | Size perception (area→radius) |
| **log** | `log10(v) normalized` | Heavy compression | Power-law data (LoC, file sizes) |
| **exp** | `norm²` | Emphasize extremes | Highlighting outliers |
| **inverse** | `1 - linear(v)` | Flip direction | Age→freshness, debt→health |
| **discrete** | `indexOf(v)/len` | Categorical→numeric | Tiers, layers, roles |

---

## Visual Comparison

Same data `[100, 200, 400, 800, 1600, 3200]` with different scales:

```
LINEAR:     ●  ●    ●      ●          ●                    ●
            ↑                                              ↑
           100                                           3200
           (even spacing between values)

SQRT:       ●  ●   ●    ●      ●          ●
            ↑                              ↑
           100                           3200
           (giants compressed, small differences preserved)

LOG:        ● ● ●  ●   ●    ●
            ↑              ↑
           100           3200
           (everything visible, extremes heavily compressed)

EXP:        .  .   ●     ●        ●                              ●
            ↑                                                    ↑
           100                                                 3200
           (small values nearly invisible, giants dominate)

INVERSE:                    ●                    ●          ●      ●    ●   ●  ●
                                                                           ↑
                                                                         100
           (3200 is now smallest, 100 is now largest)
```

---

## When to Use Each Scale

### Linear (Default)
- Data is uniformly distributed
- No natural outliers
- Example: `cohesion` scores (0-100 evenly spread)

### Sqrt (Recommended for Size)
- Mapping to **visual area** (node size, radius)
- Human perception: doubling area should double the value
- Example: `token_estimate` → `nodeSize`

### Log (Power-Law Data)
- Data spans multiple orders of magnitude
- Most values are small, few are huge
- Example: `line_count` (most files 50-500, some 5000+)

### Exp (Highlighting Extremes)
- You want to make outliers POP
- Small differences in large values matter
- Example: `complexity_density` → `pulseSpeed` (make complex nodes pulsate wildly)

### Inverse (Flip the Meaning)
- High raw value = low visual output
- Example: `age_days` → `lightness` (old = dark, new = bright)

---

## Composition Examples

### Example 1: Code Health Dashboard
```javascript
// Size = complexity (sqrt compresses monsters)
UPB.bind('complexity_density', 'nodeSize', { scale: 'sqrt' });

// Color = age (inverse: new=bright, old=dark)
UPB.bind('age_days', 'lightness', { scale: 'inverse' });

// Saturation = test coverage (linear)
UPB.bind('coverage_percent', 'saturation', { scale: 'linear' });
```

### Example 2: Dependency Hotspots
```javascript
// Size = in-degree (log: hubs visible but not overwhelming)
UPB.bind('in_degree', 'nodeSize', { scale: 'log' });

// Hue = tier (discrete: each tier gets unique hue)
UPB.bind('tier', 'hue', { scale: 'discrete' });

// Pulse = orphan status (binary)
UPB.bind('is_orphan', 'pulseSpeed', { scale: 'linear' });
```

### Example 3: Performance Analysis
```javascript
// Size = token count (sqrt for perceptual accuracy)
UPB.bind('token_estimate', 'nodeSize', { scale: 'sqrt' });

// Color = hotspot score (exp: make hotspots GLOW)
UPB.bind('hotspot_score', 'lightness', { scale: 'exp' });

// Charge = complexity (log: complex nodes push away)
UPB.bind('complexity_density', 'charge', { scale: 'log' });
```

---

## The Math

### Linear
```
f(v) = (v - min) / (max - min)
```
Input range → [0, 1] linearly.

### Sqrt
```
f(v) = (sqrt(v) - sqrt(min)) / (sqrt(max) - sqrt(min))
```
Compresses high values. Useful because human perception of area is sqrt-based.

### Log
```
f(v) = (log10(v) - log10(min)) / (log10(max) - log10(min))
```
Extreme compression. 10→100→1000 become evenly spaced.

### Exp
```
f(v) = ((v - min) / (max - min))²
```
Squares the linear result. Small values shrink, large values grow.

### Inverse
```
f(v) = 1 - linear(v)
```
Flips the output. Max input → 0, min input → 1.

### Discrete
```
f(v) = indexOf(v, domain) / (domain.length - 1)
```
Maps categorical values to evenly-spaced numeric positions.

---

## UI Access

In the visualization, press **M** (or backtick) to open the Control Bar:

```
┌─────────────────────────────────────────────────────────┐
│  SCOPE    SOURCE           →    TARGET       SCALING    │
│  ┌─────┐  ┌─────────────┐       ┌────────┐  ┌────────┐ │
│  │ All │  │token_estimate│  →   │nodeSize│  │ Sqrt ▼ │ │
│  └─────┘  └─────────────┘       └────────┘  └────────┘ │
│                                                         │
│  [ APPLY MAPPING ]  [ Reset ]                          │
└─────────────────────────────────────────────────────────┘
```

The **SCALING** dropdown lets you select any transform.

---

## Implementation

**Source:** `modules/upb/scales.js`

```javascript
const UPB_SCALES = {
    SCALES: {
        linear:   (v, min, max) => (v - min) / (max - min || 1),
        sqrt:     (v, min, max) => normalized_sqrt(v, min, max),
        log:      (v, min, max) => normalized_log10(v, min, max),
        exp:      (v, min, max) => Math.pow(linear(v, min, max), 2),
        inverse:  (v, min, max) => 1 - linear(v, min, max),
        discrete: (v, min, max, domain) => indexOf(v, domain) / (len - 1)
    },
    applyScale: function(name, value, min, max, domain) {
        const fn = SCALES[name] || SCALES.linear;
        return Math.max(0, Math.min(1, fn(value, min, max, domain)));
    }
};
```

All outputs are clamped to [0, 1] for safety.

---

## Key Insight

> **Scales are the secret weapon of data visualization.**
>
> The same data can tell completely different stories depending on the scale transform.
> A log scale reveals the long tail. An exp scale highlights outliers.
> A sqrt scale makes size perception accurate.
>
> Without scales, you're just doing linear interpolation.
> With scales, you're **shaping information**.

---

*Part of the Universal Property Binder (UPB) system.*
*See also: [UNIVERSAL_PROPERTY_BINDER.md](UNIVERSAL_PROPERTY_BINDER.md)*
