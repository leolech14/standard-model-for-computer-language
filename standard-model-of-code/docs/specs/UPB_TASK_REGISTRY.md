# UPB Task Registry

> Implementation tasks for the Universal Property Binder

## Status Legend

| Status | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Complete |
| `[!]` | Blocked |

---

## Phase 1: Foundation (Core Data Structures)

### 1.1 Endpoint Definitions
- [ ] Define `SourceEndpoint` class with metadata (label, type, domain, range)
- [ ] Define `TargetEndpoint` class with metadata (label, category, range, unit)
- [ ] Create `endpoints.yaml` with all known sources and targets
- [ ] Implement endpoint discovery from `unified_analysis.json` schema

### 1.2 Binding Graph
- [ ] Define `Binding` class (source, target, scale, range, weight)
- [ ] Define `BindingGraph` class (collection of bindings with conflict detection)
- [ ] Implement binding serialization (YAML/JSON)
- [ ] Implement binding validation (type compatibility, range sanity)

### 1.3 Scale Functions
- [ ] Implement `linear` scale
- [ ] Implement `log` scale
- [ ] Implement `sqrt` scale
- [ ] Implement `exp` scale
- [ ] Implement `discrete` lookup
- [ ] Implement `percentile` normalization

---

## Phase 2: Blend Modes (Multi-Source → Single Target)

### 2.1 Blend Implementations
- [ ] Implement `add` blend
- [ ] Implement `multiply` blend
- [ ] Implement `average` blend
- [ ] Implement `max` blend
- [ ] Implement `min` blend
- [ ] Implement `weighted` blend with configurable weights
- [ ] Implement `modulate` blend

### 2.2 Blend Configuration
- [ ] Define blend mode schema
- [ ] Create blend mode UI selector
- [ ] Implement weight adjustment UI

---

## Phase 3: Broadcast (Single Source → Multi-Target)

### 3.1 Compound Signatures
- [ ] Define `Signature` class (one source, multiple target bindings)
- [ ] Implement signature presets (complexity, importance, activity)
- [ ] Create signature builder UI

### 3.2 Signature Presets
- [ ] `complexity-signature`: size + lightness + hue + pulse_rate
- [ ] `importance-signature`: size + mass + charge
- [ ] `activity-signature`: pulse_rate + perturbation + opacity
- [ ] `hierarchy-signature`: Y position + lightness + size
- [ ] `category-signature`: hue + X position + clustering

---

## Phase 4: OKLCH Integration

### 4.1 Geometric Color Space
- [ ] Refactor `color-engine.js` to expose L, C, H as separate bindable channels
- [ ] Implement OKLCH → sRGB conversion with gamut mapping
- [ ] Create OKLCH color picker UI component
- [ ] Implement perceptual uniformity validation

### 4.2 Color Bindings
- [ ] Bind any source → H (hue angle)
- [ ] Bind any source → C (chroma/saturation)
- [ ] Bind any source → L (lightness)
- [ ] Implement color blend modes (LAB interpolation)

---

## Phase 5: Projection Intelligence

### 5.1 Combination Tracking
- [ ] Create binding history log (timestamped experiments)
- [ ] Implement binding fingerprint (hash of configuration)
- [ ] Store user ratings for binding effectiveness

### 5.2 Pattern Detection
- [ ] Analyze which bindings reveal cluster structure
- [ ] Detect bindings that create visual collisions
- [ ] Identify bindings with high perceptual discrimination

### 5.3 Recommendation Engine
- [ ] Implement "suggest binding" based on data distribution
- [ ] Implement "auto-optimize" for maximum visual separation
- [ ] Create "semantic coherence" scorer

---

## Phase 6: UI Integration

### 6.1 UPB Control Panel
- [ ] Replace current `control-bar.js` with UPB UI
- [ ] Create drag-and-drop binding interface
- [ ] Implement real-time binding preview
- [ ] Create preset selector dropdown

### 6.2 Binding Visualizer
- [ ] Show current bindings as graph diagram
- [ ] Highlight conflicts (multiple exclusive bindings)
- [ ] Show blend weights visually

---

## Phase 7: Legacy Migration

### 7.1 Deprecate Legacy Systems
- [ ] Audit `control-bar.js` for UPB coverage
- [ ] Audit `file-viz.js` DATA_SOURCES/VISUAL_TARGETS
- [ ] Audit `appearance_engine.py` mapping logic
- [ ] Create migration path for existing configurations

### 7.2 Backward Compatibility
- [ ] Support legacy `VISUAL_MAPPINGS` format
- [ ] Auto-convert legacy configs to UPB format
- [ ] Maintain fallback rendering path

---

## Phase 8: Testing & Validation

### 8.1 Unit Tests
- [ ] Test all scale functions
- [ ] Test all blend modes
- [ ] Test binding validation
- [ ] Test OKLCH conversion

### 8.2 Visual Regression
- [ ] Capture baseline screenshots with current system
- [ ] Compare UPB output to baseline
- [ ] Document visual differences

### 8.3 Performance
- [ ] Benchmark binding evaluation (target: <1ms per node)
- [ ] Benchmark full graph re-render
- [ ] Optimize hot paths

---

## Dependencies

| Task | Depends On |
|------|------------|
| 2.x (Blends) | 1.x (Foundation) |
| 3.x (Broadcast) | 1.x (Foundation) |
| 4.x (OKLCH) | 1.x (Foundation) |
| 5.x (Intelligence) | 2.x, 3.x, 4.x |
| 6.x (UI) | 1.x, 4.x |
| 7.x (Migration) | 6.x |
| 8.x (Testing) | All |

---

## Legacy Sprawl (To Be Mapped)

Files that will be affected/replaced by UPB implementation:

| File | Confidence | Impact | Action |
|------|------------|--------|--------|
| `control-bar.js` | HIGH | REPLACE | Core mapping UI |
| `file-viz.js` | HIGH | REFACTOR | DATA_SOURCES/VISUAL_TARGETS |
| `color-engine.js` | MEDIUM | EXTEND | Add channel separation |
| `appearance_engine.py` | MEDIUM | REFACTOR | Server-side bindings |
| `app.js` | MEDIUM | INTEGRATE | Wire UPB to graph |
| `animation.js` | LOW | EXTEND | Animation channel bindings |
| `physics_engine.py` | LOW | EXTEND | Physics channel bindings |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-21 | Claude + Leonardo | Initial task registry |
