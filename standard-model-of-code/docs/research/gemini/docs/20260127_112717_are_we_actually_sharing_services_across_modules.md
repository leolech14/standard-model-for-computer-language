# Research: ARE WE ACTUALLY SHARING SERVICES ACROSS MODULES?

We built this Hub architecture with:
- RegistryOfR...

> **Date:** 2026-01-27 11:27:17
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:b3f41ce87fd5c6fb12df0d4b5e9f09d6464667b1e4fd717ffa10ad36c75509f1`
> **Raw JSON:** `raw/20260127_112717_are_we_actually_sharing_services_across_modules.json`

---

## Query

ARE WE ACTUALLY SHARING SERVICES ACROSS MODULES?

We built this Hub architecture with:
- RegistryOfRegistries (service locator)
- EventBus (pub/sub)
- BasePlugin (interface)
- ClassifierPlugin (first service)
- MCP Server (AI interface)

CRITICAL QUESTION: Is any of this actually USED for cross-module service sharing?

VALIDATION NEEDED:

1. CURRENT SERVICE SHARING PATTERNS:
   - How do modules currently share functionality?
   - Do they import each other directly?
   - Do they use global singletons?
   - Do they pass instances around?
   - Evidence: Show actual code patterns from pipeline stages

2. PIPELINE STAGE COMMUNICATION:
   - How do 27 pipeline stages communicate?
   - Do they share services?
   - Do they pass data via CodebaseState only?
   - Evidence: Examine stage implementations

3. REGISTRY USAGE:
   - Are registries actually shared between modules?
   - Or does each module instantiate its own?
   - Evidence: Search for get_pattern_registry calls

4. REAL-WORLD NEED:
   - Do we ACTUALLY need service sharing?
   - Or is passing CodebaseState sufficient?
   - What use cases require shared services?

5. HUB VALUE PROPOSITION:
   - If modules don't share services, what's the Hub for?
   - Is it just organizing code?
   - Or enabling future service sharing?

PROVIDE EVIDENCE:
- Show actual import patterns in pipeline stages
- Show how data flows between stages
- Show if/where services are shared
- Identify if Hub solves a real problem or theoretical one

BE HONEST:
- If modules don't share services, say so
- If Hub is premature abstraction, say so
- If we built infrastructure before proving need, say so


---

## Response

Based on a forensic analysis of the provided core execution files (`full_analysis.py`, `unified_analysis.py`, `edge_extractor.py`), I have analyzed the service sharing and architectural patterns.

**VERDICT: The "Hub Architecture" (RegistryOfRegistries, EventBus, Plugins) is NOT used in the core analysis loop.**

The codebase operates as a **Procedural Monolith** with direct imports, not a service-oriented architecture. The components you listed (EventBus, BasePlugin, MCP Server) are absent from the execution flow provided.

Here is the evidence.

### 1. Current Service Sharing Patterns
**Modules do not share services via a Hub. They share logic via direct Python imports and pass data via function arguments.**

*   **Direct Imports (Tight Coupling):**
    The main orchestrator, `full_analysis.py`, explicitly imports every single "service" it needs. It does not ask a registry for them.
    ```python
    # full_analysis.py:1155-1164
    from unified_analysis import analyze
    from standard_model_enricher import enrich_with_standard_model
    from purpose_field import detect_purpose_field
    from purpose_emergence import compute_pi2, compute_pi3, compute_pi4
    from execution_flow import detect_execution_flow
    from performance_predictor import predict_performance
    ```

*   **Data Passing (No Shared State Service):**
    Data is passed as raw lists of dictionaries (`nodes`, `edges`) between functions. There is no shared service managing this state; it is local variable passing.
    ```python
    # full_analysis.py:1192
    nodes = enrich_with_standard_model(nodes)
    
    # full_analysis.py:1559 (Passing nodes/edges explicitly)
    purpose_field = detect_purpose_field(nodes, edges)
    
    # full_analysis.py:1652
    exec_flow = detect_execution_flow(nodes, edges, purpose_field)
    ```

### 2. Pipeline Stage Communication
**There is no EventBus. Communication is synchronous and sequential.**

*   **Sequential Execution:** The "stages" are simply print statements followed by function calls inside a massive `run_full_analysis` function.
    ```python
    # full_analysis.py:1169
    with StageTimer(perf_manager, "Stage 1: Base Analysis") as timer:
        # ... logic ...

    # full_analysis.py:1191
    print("\n🧬 Stage 2: Standard Model Enrichment...")
    with StageTimer(perf_manager, "Stage 2: Standard Model Enrichment") as timer:
        # ... logic ...
    ```

*   **The "New" Pipeline:** There is a refactored entry point `run_pipeline_analysis` that uses a `CodebaseState` object, but it still appears to run sequentially without an EventBus.
    ```python
    # full_analysis.py:1063
    state = pipeline.run(state)
    ```
    *Evidence of EventBus or asynchronous messaging is missing entirely from these files.*

### 3. Registry Usage
**Registries are used as Global Singletons via import, not via a Service Locator (Hub).**

The `RoleRegistry` is the only registry visible in the context. It is accessed by directly importing a getter function, which returns a module-level singleton. It does not go through a `RegistryOfRegistries`.

*   **Implementation:**
    ```python
    # unified_analysis.py:18-19
    from core.registry.role_registry import get_role_registry
    _role_registry = get_role_registry()
    ```
*   **Usage:**
    ```python
    # unified_analysis.py:223
    role_value = _role_registry.normalize(role_value)
    ```
*   **Conclusion:** This is standard Python module caching, not a dynamic service registry pattern.

### 4. Real-World Need vs. Architecture
**The analysis suggests the Hub is currently "Architecture Astronauting" (building complex structures for simple problems).**

*   **Current Reality:** The code functions perfectly well by passing `nodes` and `edges` lists between functions.
    *   **Evidence:** `full_analysis.py` successfully orchestrates ~15 distinct analysis steps (Survey, Base Analysis, Scope, Flow, Purpose, etc.) purely through procedural calls.
*   **The Problem with Hub:**
    *   The modules (e.g., `edge_extractor.py`, `graph_analyzer.py`) are stateless function libraries. They don't *need* to be instantiated as services or plugins.
    *   Example: `edge_extractor.py` defines a class `JSModuleResolver` (Line 69), but it implements a global singleton pattern (`_js_module_resolver`, Line 266) rather than being injected by a Hub.

### 5. Missing Components
The following components mentioned in your query are **completely absent** from the provided codebase context, indicating they are either unused, dead code, or exist in files not involved in the execution path:

1.  **RegistryOfRegistries:** No import or usage.
2.  **EventBus:** No import or usage.
3.  **BasePlugin / ClassifierPlugin:** No import or usage.
4.  **MCP Server:** No import or usage.

### Recommendation
**You are not sharing services.** You are sharing library functions via imports.

If the goal is to modularize:
1.  **Stick to `CodebaseState`:** The pattern in `run_pipeline_analysis` (`state = pipeline.run(state)`) [full_analysis.py:1063] is the correct direction. You don't need a Service Locator; you need a consistent Data Context passed down the chain.
2.  **Delete the Hub:** Unless you plan to dynamically load plugins at runtime (e.g., third-party extensions), the `RegistryOfRegistries` and `EventBus` are likely unnecessary overhead for a static analysis pipeline.

---

## Citations

_No citations provided_
