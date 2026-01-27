# Research: UNIVERSAL API SCHEMA & MODULE INVENTORY

We have built THE HUB:
- RegistryOfRegistries (service loca...

> **Date:** 2026-01-27 09:20:35
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:789edfd9606944e517703cfebc74c4e42976356ad11c854bc2c3e94867601a6c`
> **Raw JSON:** `raw/20260127_092035_universal_api_schema___module_inventory__we_have_b.json`

---

## Query

UNIVERSAL API SCHEMA & MODULE INVENTORY

We have built THE HUB:
- RegistryOfRegistries (service locator + DI container)
- EventBus (pub/sub communication)
- PipelineManager (plugin orchestration with 27 stages)

TASK 1: DEFINE UNIVERSAL API SCHEMA

What interface must ALL modules implement to connect to the Hub?

Analyze existing patterns:
1. BaseStage (standard-model-of-code/src/core/pipeline/base_stage.py) - What contract does it define?
2. Registry interfaces - Do all registries follow a pattern?
3. Event patterns - What event naming conventions exist?

Propose MINIMAL UNIVERSAL INTERFACE:
- Required methods (initialize? register? start? stop?)
- Required metadata (name? version? dependencies?)
- Event contracts (what events to emit? what to listen for?)
- Data contracts (what schemas to follow?)

TASK 2: MODULE INVENTORY & CONVERSION PRIORITY

Scan codebase and categorize modules by Hub-compatibility:

CATEGORY A: ALREADY COMPATIBLE (no changes needed)
- Which modules already work with the Hub?
- Evidence: File paths + line numbers showing compatible patterns

CATEGORY B: EASILY CONVERTIBLE (1-2 hour refactor)
- Modules with clear boundaries, minimal dependencies
- Evidence: What makes them easy? Show code structure

CATEGORY C: NEED REFACTORING (4+ hours)
- Tightly coupled modules, God classes, global state
- Evidence: What coupling exists? Dependencies?

CATEGORY D: NOT APPLICABLE (don't need Hub integration)
- Pure utilities, standalone scripts, one-off tools
- Evidence: Why they don't need Hub?

CRITICAL MODULES TO PRIORITIZE:
1. Which 5-10 modules provide MAXIMUM VALUE if Hub-connected?
2. Which modules are BLOCKING others from Hub integration?
3. Which modules would DEMONSTRATE the Hub's value best?

Provide FORENSIC EVIDENCE:
- File paths and line numbers
- Code snippets showing patterns
- Dependency graphs
- Integration complexity estimates


---

## Response

You are asking for the **architectural blueprint** to bind the loosely coupled components of Collider into a cohesive "Hub" system, and a forensic inventory of the current codebase to determine migration costs.

Here is the forensic analysis and proposal.

---

### TASK 1: UNIVERSAL API SCHEMA (Proposed)

Based on the existing patterns in `BaseStage` and the `Registry` architecture, the Universal Schema must standardize **Lifecycle**, **Dependency Injection**, and **Communication**.

#### 1. Analysis of Existing Patterns

*   **Pipeline Stages (`BaseStage`)**:
    *   **Contract**: Defined in `[src/core/pipeline/base_stage.py:17-53]`.
    *   **Key Methods**: `execute(state) -> state`, `validate_input(state) -> bool`.
    *   **Identity**: `name` property.
*   **Registries**:
    *   **Contract**: Implicit. Seen in `[src/core/registry/registry_of_registries.py:111-121]`.
    *   **Key Methods**: `register()`, `get()`, `list_all()`.
    *   **Identity**: Hardcoded string keys in `_initialize_defaults` `[src/core/registry/registry_of_registries.py:82]`.
*   **Events**:
    *   **Contract**: Defined in `[src/core/event_bus.py:50-105]`.
    *   **Pattern**: String-based keys (`noun:verb`) and `Callable` handlers.

#### 2. The `IHubModule` Protocol

To unify these, every module connected to the Hub must implement this interface (Python Protocol).

```python
from typing import Dict, Any, Protocol
from src.core.event_bus import EventBus
from src.core.registry.registry_of_registries import RegistryOfRegistries

class IHubModule(Protocol):
    """
    Universal interface for any component managed by the Hub.
    """
    
    @property
    def name(self) -> str:
        """Unique identifier (e.g., 'universal_classifier')."""
        ...

    @property
    def version(self) -> str:
        """Semantic version of the module."""
        ...

    @property
    def dependencies(self) -> list[str]:
        """List of registry keys this module needs (e.g., ['roles', 'patterns'])."""
        ...

    def initialize(self, hub: RegistryOfRegistries) -> None:
        """
        Lifecycle Hook: Boot up.
        1. Store hub reference.
        2. Resolve dependencies.
        3. Subscribe to EventBus events.
        """
        ...

    def shutdown(self) -> None:
        """
        Lifecycle Hook: Teardown.
        1. Unsubscribe from EventBus.
        2. Close resources.
        """
        ...
```

#### 3. Data & Event Contracts
*   **Event Naming**: `domain:entity:action` (e.g., `analysis:node:classified`).
*   **Payload Schema**: Must be JSON-serializable `Dict[str, Any]`.
*   **State Access**: Modules should **never** share global state. They must request `CodebaseState` or specific Registries via the Hub.

---

### TASK 2: MODULE INVENTORY & CONVERSION PRIORITY

I have scanned the codebase and categorized modules based on their distance from the `IHubModule` interface defined above.

#### CATEGORY A: ALREADY COMPATIBLE
*Modules that already use `BaseStage` or are already integrated into the `RegistryOfRegistries`.*

1.  **Pipeline Manager**
    *   **Location**: `[src/core/pipeline/manager.py:18]`
    *   **Evidence**: Already orchestrates `BaseStage` objects. Acts as a sub-hub.
2.  **All Pipeline Stages**
    *   **Location**: `[src/core/pipeline/stages/*.py]`
    *   **Evidence**: `src/core/pipeline/stages/standard_model.py:16` inherits `BaseStage`. They have `name` properties and `execute` methods.
3.  **Core Registries**
    *   **Location**: `[src/core/registry/role_registry.py:25]`, `[src/core/registry/pattern_registry.py:35]`.
    *   **Evidence**: Already instantiated and managed by `RegistryOfRegistries` `[src/core/registry/registry_of_registries.py:89-98]`.

#### CATEGORY B: EASILY CONVERTIBLE (1-2 Hours)
*Modules with clean classes, limited dependencies, and no global state usage. They just need an `initialize(hub)` wrapper.*

1.  **Universal Classifier**
    *   **Location**: `[src/core/classification/universal_classifier.py:54]`
    *   **Why**: It currently fetches registries via global functions (`get_pattern_registry`, `get_role_registry`) in `__init__` `[src/core/classification/universal_classifier.py:58-59]`.
    *   **Refactor**: Change `__init__` to accept these registries as arguments, injected via `initialize(hub)`.
2.  **Constraint Engine**
    *   **Location**: `[src/core/constraint_engine.py:84]`
    *   **Why**: It loads profiles in `__init__` `[src/core/constraint_engine.py:91]`. This configuration loading should move to an initialization phase provided by the Hub.
3.  **Symbol Indexer**
    *   **Location**: `[src/core/symbol_indexer.py:83]`
    *   **Why**: It manages internal state (`self.index`) and dependencies (`_queries`). Ideally, it should register its index with the Hub so other modules can query it.

#### CATEGORY C: NEED REFACTORING (4+ Hours)
*Modules with hardcoded imports, script-like execution flow, or tight coupling.*

1.  **Full Analysis Orchestrator**
    *   **Location**: `[src/core/full_analysis.py]`
    *   **Evidence**: It is a script masquerading as a module.
        *   `[src/core/full_analysis.py:1155-1165]`: Hardcoded imports inside the execution flow (`from unified_analysis import analyze`).
        *   `[src/core/full_analysis.py:1169]`: Manually manages `StageTimer` and execution order.
    *   **Refactor**: Needs to be completely replaced by `PipelineManager` configuration. It essentially *duplicates* the Hub's job poorly.
2.  **Unified Analysis**
    *   **Location**: `[src/core/unified_analysis.py]`
    *   **Evidence**: Contains a massive `analyze` function `[src/core/unified_analysis.py:343]` that manually instantiates engines and orchestrates them.
    *   **Refactor**: This function should be decomposed. The `TreeSitterUniversalEngine` instantiation `[src/core/unified_analysis.py:377]` should be a service request to the Hub.
3.  **Tree Sitter Universal Engine**
    *   **Location**: `[src/core/tree_sitter_engine.py:281]`
    *   **Evidence**: It initializes its own delegates (`UniversalClassifier`, `PythonASTExtractor`) in `__init__` `[src/core/tree_sitter_engine.py:319-320]`.
    *   **Refactor**: These delegates should be injected.

#### CATEGORY D: NOT APPLICABLE
*Data structures, IRs, and standalone scripts.*

1.  **Intermediate Representation (IR)**
    *   **Location**: `[src/core/ir.py]`
    *   **Why**: Pure data classes.
2.  **CLI Scripts**
    *   **Location**: `[src/scripts/*.py]`
    *   **Why**: These are consumers of the Hub, not modules within it.

---

### CRITICAL MODULES TO PRIORITIZE

To maximize value and demonstrate the architecture, prioritize these 3 tasks:

#### 1. The Blocker: `src/core/full_analysis.py`
This script currently drives the application. It prevents the `PipelineManager` (The Hub's orchestrator) from being the single source of truth.
*   **Action**: Deprecate `run_full_analysis`. Move its logic into `create_full_pipeline` in `[src/core/pipeline/__init__.py:77]`.

#### 2. The Value Add: `src/core/classification/universal_classifier.py`
This is the "Brain" of Collider. By converting this to `IHubModule`, we allow:
*   Dynamic reloading of patterns/roles (via EventBus `patterns:updated`).
*   Hot-swapping classifiers (e.g., swapping `UniversalClassifier` for an LLM-based one) via the Registry.

#### 3. The Demonstrator: `src/core/constraint_engine.py`
This module consumes data from the graph and rules from a registry.
*   **Scenario**: When `constraint_engine` is Hub-connected, it can listen for `graph:updated` events. As soon as a node is added to the graph (by the parser), the Constraint Engine can *immediately* emit `violation:detected` events without waiting for the whole analysis to finish. This demonstrates the power of the EventBus.

---

## Citations

_No citations provided_
