# Module Conversion Inventory - Hub Compatibility Assessment

> **Purpose:** Categorize all modules by Hub-compatibility and prioritize conversion
> **Analysis:** Gemini 3.0 Pro forensic analysis (2026-01-27)
> **Status:** Blueprint for migration

---

## Universal API Schema (IHubModule)

Every Hub-connected module must implement:

```python
class IHubModule(Protocol):
    @property
    def name(self) -> str: ...          # Unique identifier

    @property
    def version(self) -> str: ...       # Semantic version

    @property
    def dependencies(self) -> list[str]: ...  # Required registries

    def initialize(self, hub: RegistryOfRegistries) -> None:
        """Receive hub, resolve dependencies, subscribe to events"""

    def register(self) -> None:
        """Register capabilities and event subscriptions"""

    def start(self) -> None:
        """Begin normal operation"""

    def stop(self) -> None:
        """Graceful shutdown"""
```

**Event Contract:**
- Naming: `domain:entity:action` (e.g., `analysis:node:classified`)
- Payload: JSON-serializable `Dict[str, Any]`

**Implemented in:** `src/core/plugin/base_plugin.py`

---

## Category A: ALREADY COMPATIBLE (No Changes)

| Module | Location | Evidence |
|--------|----------|----------|
| **PipelineManager** | `src/core/pipeline/manager.py:18` | Already orchestrates BaseStage modules |
| **27 Pipeline Stages** | `src/core/pipeline/stages/*.py` | All inherit BaseStage, have `name` + `execute` |
| **Core Registries (6)** | `src/core/registry/*.py` | Already managed by RegistryOfRegistries |

**Total: 34 modules** (1 manager + 27 stages + 6 registries)

---

## Category B: EASILY CONVERTIBLE (1-2 hours each)

| Module | Location | Current Issue | Fix |
|--------|----------|---------------|-----|
| **UniversalClassifier** | `src/core/classification/universal_classifier.py:54` | Fetches registries in `__init__` (L58-59) | Accept registries via `initialize(hub)` |
| **ConstraintEngine** | `src/core/constraint_engine.py:84` | Loads config in `__init__` (L91) | Load config via `initialize(hub)` |
| **SymbolIndexer** | `src/core/symbol_indexer.py:83` | Internal state, no hub connection | Register index with hub as service |
| **TreeSitterEngine** | `src/core/tree_sitter_engine.py:281` | Instantiates delegates in `__init__` (L319-320) | Inject delegates via hub |
| **DimensionClassifier** | `src/core/dimension_classifier.py` | Uses hardcoded tree-sitter queries | Fetch queries from hub registry |

**Effort: 5-10 hours total** (5 modules × 1-2 hours)

---

## Category C: NEED REFACTORING (4+ hours each)

| Module | Location | Issue | Refactor |
|--------|----------|-------|----------|
| **full_analysis.py** | `src/core/full_analysis.py` | God script - duplicates PipelineManager | **DEPRECATE** - Move logic to PipelineManager config |
| **unified_analysis.py** | `src/core/unified_analysis.py:343` | Massive `analyze()` function orchestrates manually | **DECOMPOSE** - Extract engines as services |
| **brain_download.py** | `src/core/brain_download.py` | Generates reports, tightly coupled to output format | Extract report generators as plugins |

**Effort: 12-20 hours total**

**BLOCKER:** `full_analysis.py` prevents PipelineManager from being the orchestrator.

---

## Category D: NOT APPLICABLE (Don't Convert)

| Module | Location | Reason |
|--------|----------|--------|
| **IR (Intermediate Rep)** | `src/core/ir.py` | Pure data classes |
| **CLI Scripts** | `src/scripts/*.py` | Consumers of Hub, not modules |
| **Standalone Utilities** | Various | No state, no coordination needs |

---

## Priority Conversion Targets

### Priority 1: THE BLOCKER

**full_analysis.py** → Deprecate

| Current | Problem | Solution |
|---------|---------|----------|
| Script orchestrates analysis | Duplicates PipelineManager logic | Move to `create_full_pipeline()` config |
| Location: L1155-1165 | Hardcoded import order | Let PipelineManager resolve dependencies |

**Impact:** Unblocks PipelineManager as single orchestrator.

**Effort:** 4-6 hours

---

### Priority 2: THE VALUE MULTIPLIER

**UniversalClassifier** → Hub Plugin

| Current | Problem | Solution |
|---------|---------|----------|
| Fetches registries in `__init__` | Can't hot-reload | Inject via `initialize(hub)` |
| Location: L58-59 | Hardcoded globals | Listen for `patterns:updated` events |

**Impact:**
- Dynamic pattern reloading
- Hot-swappable classifiers
- Foundation for LLM-based classification

**Effort:** 1-2 hours

---

### Priority 3: THE DEMONSTRATOR

**ConstraintEngine** → Event-Driven Plugin

| Current | Problem | Solution |
|---------|---------|----------|
| Loads config in `__init__` | Runs post-analysis only | Listen for `graph:updated` events |
| Location: L91 | Batch-only | Emit `violation:detected` in real-time |

**Impact:**
- Real-time constraint checking
- Incremental violation detection
- Demonstrates EventBus value

**Effort:** 1-2 hours

---

## Conversion Roadmap

### Phase 1: Foundation (Complete)
- [x] EventBus built
- [x] Integrated into RegistryOfRegistries
- [x] BasePlugin interface defined

### Phase 2: Quick Wins (6 hours)
- [ ] Convert UniversalClassifier → BasePlugin
- [ ] Convert ConstraintEngine → EventDrivenPlugin
- [ ] Convert SymbolIndexer → ServicePlugin

### Phase 3: Architecture Fix (6 hours)
- [ ] Deprecate full_analysis.py
- [ ] Move orchestration to PipelineManager config
- [ ] Test entire pipeline via Hub

### Phase 4: MCP Integration (4 hours)
- [ ] Build MCP server wrapper
- [ ] Expose Hub capabilities via MCP
- [ ] Create plugin.json manifests

---

## Integration Complexity Matrix

| Module | Compatibility | Effort | Value | Priority |
|--------|--------------|--------|-------|----------|
| UniversalClassifier | B | 2h | HIGH | P1 |
| ConstraintEngine | B | 2h | HIGH | P1 |
| SymbolIndexer | B | 1h | MED | P2 |
| TreeSitterEngine | B | 2h | MED | P2 |
| DimensionClassifier | B | 1h | LOW | P3 |
| full_analysis.py | C | 6h | CRITICAL | P0 |
| unified_analysis.py | C | 8h | HIGH | P2 |
| brain_download.py | C | 4h | MED | P3 |

**Recommendation:** Start with P0 (full_analysis.py deprecation), then P1 modules.

---

## Success Criteria

Module is Hub-compatible when:
- [x] Inherits from BasePlugin
- [x] Implements initialize/register/start/stop
- [x] Uses hub.get() instead of global imports
- [x] Emits events for state changes
- [x] Has tests validating Hub integration
- [x] Documented in HUB_INTEGRATION_INDEX.md

---

## Sources

- Gemini Analysis: `docs/research/gemini/sessions/20260127_092035_*`
- Architecture Blueprint: `docs/specs/MODULAR_ARCHITECTURE_SYNTHESIS.md`
- BaseStage Pattern: `src/core/pipeline/base_stage.py`
