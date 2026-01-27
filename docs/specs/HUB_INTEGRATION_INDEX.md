# Hub Integration Index - Component Findability

> **Purpose:** Quick reference for finding Hub components and integration points
> **Updated:** 2026-01-27

---

## The Hub (RegistryOfRegistries)

| Component | Location | Purpose |
|-----------|----------|---------|
| **Hub Class** | `src/core/registry/registry_of_registries.py` | Central service locator + DI container |
| **Hub Accessor** | `get_meta_registry()` | Global singleton access |
| **EventBus (Python)** | `src/core/event_bus.py` | Pub/sub for modules |
| **EventBus (JS)** | `src/core/viz/assets/modules/event-bus-v2.js` | Browser pub/sub |

---

## Registries (Data Sources)

| Registry | File | Count | Access |
|----------|------|-------|--------|
| Atoms | `src/core/atom_registry.py` | 3,525 | `hub.get('atoms')` |
| Roles | `src/core/registry/role_registry.py` | 33 | `hub.get('roles')` |
| Types | `src/core/type_registry.py` | 36 | `hub.get('types')` |
| Patterns | `src/core/registry/pattern_registry.py` | 36 | `hub.get('patterns')` |
| Schemas | `src/core/registry/schema_registry.py` | 13 | `hub.get('schemas')` |
| Workflows | `src/core/registry/workflow_registry.py` | 4 | `hub.get('workflows')` |

---

## Plugin System (Pipeline)

| Component | Location | Purpose |
|-----------|----------|---------|
| **Plugin Interface** | `src/core/pipeline/base_stage.py` | BaseStage contract |
| **Plugin Manager** | `src/core/pipeline/manager.py` | Orchestrates execution |
| **Plugin Registry** | `src/core/pipeline/stages/__init__.py` | 27 stages registered |

---

## Integration Points

### Python Modules Using Hub

```python
from src.core.registry.registry_of_registries import get_meta_registry

hub = get_meta_registry()

# Access registries
roles = hub.get('roles')
atoms = hub.get('atoms')

# Use event bus
hub.event_bus.on('stage:complete', my_handler)
hub.event_bus.emit('analysis:started', {'timestamp': now()})
```

### JavaScript Modules Using EventBus

```javascript
// Global singleton
EVENT_BUS.on('graph:updated', (data) => {
    console.log('Graph has', data.nodeCount, 'nodes');
});

EVENT_BUS.emit('graph:updated', {nodeCount: 1234});
```

---

## Airdrop-Ready Modules (Copy-Paste Integration)

| Module | Files | Dependencies | Status |
|--------|-------|--------------|--------|
| color-engine.js | 1 | None | ✅ Ready |
| oklch_color.py | 2 | pyyaml | ✅ Ready |
| event-bus-v2.js | 1 | None | ✅ Ready |
| event_bus.py | 1 | None | ✅ Ready |
| atom_loader.py | 1 | pyyaml | ✅ Ready |
| graph_metrics.py | 1 | networkx | ✅ Ready |

---

## Documentation (Guides)

| Guide | Location | Purpose |
|-------|----------|---------|
| OKLCH Colors | `docs/specs/OKLCH_INTEGRATION_GUIDE.md` | Color system API |
| Modularity | `docs/specs/MODULARITY_ASSESSMENT.md` | Portability analysis |
| Architecture | `docs/specs/MODULAR_ARCHITECTURE_SYNTHESIS.md` | Plugin architecture blueprint |
| This Index | `docs/specs/HUB_INTEGRATION_INDEX.md` | Component findability |

---

## Research (Perplexity - 5 Query Series)

| Topic | Location |
|-------|----------|
| Plugin Architecture Patterns | `docs/research/perplexity/docs/20260127_070656_*` |
| AI-Agent Module Design | `docs/research/perplexity/docs/20260127_070953_*` |
| Central Hub Patterns | `docs/research/perplexity/docs/20260127_083816_*` |
| Distribution Strategies | `docs/research/perplexity/docs/20260127_084018_*` |
| Schema-Driven Integration | `docs/research/perplexity/docs/20260127_084223_*` |

---

## Quick Commands

```bash
# Test EventBus
pytest tests/test_event_bus.py -v

# Check Hub status
python3 -c "from standard_model_of_code.src.core.registry.registry_of_registries import get_meta_registry; print(get_meta_registry().status_report())"

# List all registries
python3 -c "from standard_model_of_code.src.core.registry.registry_of_registries import get_meta_registry; print(get_meta_registry().list_registries())"
```

---

## Next Steps (Ordered)

1. ✅ EventBus built (21 tests passing)
2. ✅ Integrated into RegistryOfRegistries
3. ✅ Documented in CLAUDE.md + this index
4. ⏭️ Wire PipelineManager to emit events
5. ⏭️ Build MCP server wrapper
6. ⏭️ Create plugin.json manifests
