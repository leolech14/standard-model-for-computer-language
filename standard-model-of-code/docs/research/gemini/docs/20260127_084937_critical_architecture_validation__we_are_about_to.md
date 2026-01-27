# Research: CRITICAL ARCHITECTURE VALIDATION

We are about to build:
1. MINIMAL HUB - Module registry + DI + eve...

> **Date:** 2026-01-27 08:49:37
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:31bc89cc808c946db4f193a4a646c7e8c62774c8bebee84273e87b42bbabc450`
> **Raw JSON:** `raw/20260127_084937_critical_architecture_validation__we_are_about_to.json`

---

## Query

CRITICAL ARCHITECTURE VALIDATION

We are about to build:
1. MINIMAL HUB - Module registry + DI + event bus (~300 lines)
2. PLUGIN SYSTEM - plugin.json manifests + lifecycle hooks
3. MCP INTEGRATION - Model Context Protocol servers for AI agents
4. SCHEMA VALIDATION - JSON Schema for all module contracts
5. MULTI-CHANNEL DISTRIBUTION - Copy/paste, npm, git, CDN

BEFORE we build, search the codebase and validate:

QUESTION 1: Do we ALREADY HAVE a hub-like system?
- Look for: registry patterns, service locators, dependency injection
- Check: .agent/tools/, src/core/, context-management/
- Files to examine: Any containing 'registry', 'hub', 'container', 'inject'

QUESTION 2: Do we ALREADY HAVE module/plugin infrastructure?
- Look for: plugin loaders, module discovery, dynamic imports
- Check: trigger_engine.py, macro_executor.py, enrichment_orchestrator.py
- These already load YAML configs and execute dynamically - is that our plugin system?

QUESTION 3: Do we ALREADY HAVE schema validation?
- Look for: JSON Schema validation, contract testing, type checking
- Check: schema/ directory, validation tools
- Files: particle.schema.json, any validators

QUESTION 4: Do we ALREADY HAVE event bus / pub-sub?
- Look for: event emission, listeners, observers, callbacks
- Check: viz/assets/modules/event-bus.js (we have this!)
- Is it used? Is it the pattern to expand?

QUESTION 5: What SHOULD we integrate with vs rebuild?
- If we have 70% of a plugin system already (macros, triggers, registries)
- Should we REFACTOR existing → plugin pattern?
- Or build new hub and MIGRATE existing tools to it?

PROVIDE FORENSIC CITATIONS:
- File paths and line numbers for all evidence
- Exact code showing existing patterns
- Gaps where functionality is missing
- Integration points where new hub would connect

VERDICT REQUIRED:
- BUILD NEW (nothing exists that serves this purpose)
- REFACTOR EXISTING (we have pieces, unify them)
- EXTEND EXISTING (build on what works, add missing pieces)
- INTEGRATE (connect existing systems that don't talk)


---

## Response

Based on the forensic analysis of the provided codebase context, here is the validation report regarding the proposed "Minimal Hub" architecture.

### EXECUTIVE SUMMARY

**VERDICT: REFACTOR & EXTEND EXISTING**

The codebase **already contains** a functional Hub (`RegistryOfRegistries`), a Plugin System (`PipelineManager`/`BaseStage`), and partial Schema Validation (`validate_contract`). Building a *new* "Minimal Hub" from scratch would create architectural redundancy and technical debt. The correct path is to promote `RegistryOfRegistries` to the top-level Hub and generalize the `PipelineManager` pattern to handle non-analysis plugins.

---

### FORENSIC EVIDENCE

#### QUESTION 1: Do we ALREADY HAVE a hub-like system?
**YES. It is explicitly defined as `RegistryOfRegistries`.**

*   **Evidence:** `src/core/registry/registry_of_registries.py` implements a singleton Meta-Registry that manages other registries.
    *   **L50-L51:** `class RegistryOfRegistries:`
    *   **L63-L84:** Registers Atoms, Roles, Patterns, Schemas, Workflows, and Types.
    *   **L93:** `def register(self, name: str, registry: Any) -> None:`
    *   **L97:** `def get(self, name: str) -> Optional[Any]:`

*   **Service Locator Pattern:** The codebase relies heavily on Singleton accessors acting as service locators.
    *   `[src/core/registry/registry_of_registries.py:L127-L129]`: `get_meta_registry()`
    *   `[src/core/type_registry.py:L137-L139]`: `get_registry()`
    *   `[src/core/profile_loader.py:L162-L167]`: `get_profile_loader()`

**Conclusion:** You have a Hub. It just needs to be exposed as the central entry point for the new features (MCP, Multi-channel).

#### QUESTION 2: Do we ALREADY HAVE module/plugin infrastructure?
**YES. The `pipeline` package is a sophisticated plugin system.**

*   **Plugin Interface:** `src/core/pipeline/base_stage.py` defines the contract.
    *   **L17:** `class BaseStage(ABC):`
    *   **L42:** `def execute(self, state: "CodebaseState") -> "CodebaseState":`
    *   **L54:** `def validate_input(self, state: "CodebaseState") -> bool:`

*   **Plugin Orchestrator:** `src/core/pipeline/manager.py` handles execution.
    *   **L18:** `class PipelineManager:`
    *   **L50:** `def run(self, state: "CodebaseState") -> "CodebaseState":`

*   **Plugin Registration:** `src/core/pipeline/stages/__init__.py` registers 27 distinct stages.
    *   **L135:** `all_stages = { ... }` mapping string IDs to Stage instances.

**Conclusion:** You do not need to build a new plugin system. You need to generalize `BaseStage` to allow for non-analysis plugins (e.g., "DistributionStage" or "MCPServerStage") or reuse the pattern.

#### QUESTION 3: Do we ALREADY HAVE schema validation?
**PARTIALLY. Contract validation exists but is scattered.**

*   **Output Contract:** `src/core/normalize_output.py` enforces the output schema.
    *   **L323:** `def validate_contract(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:` checks required fields like `meta`, `nodes`, `edges`.

*   **Configuration Validation:** `src/core/profile_loader.py` validates YAML structure.
    *   **L106-L114:** Validates architecture profile structure manually during load.

*   **Role Validation:** `src/core/registry/role_registry.py` enforces canonical roles.
    *   **L37-L48:** Defines `_CANONICAL_ROLES`.
    *   **L156:** `def is_canonical(self, role: str) -> bool:`

**Conclusion:** You lack a centralized JSON Schema validator for *all* module contracts, but the logic for validation exists in `normalize_output.py`. This should be centralized into the Hub.

#### QUESTION 4: Do we ALREADY HAVE event bus / pub-sub?
**WEAK. It exists as linear hooks, not a true event bus.**

*   **Hooks:** `src/core/pipeline/manager.py` supports callbacks.
    *   **L33-L34:** `on_stage_start`, `on_stage_complete` callbacks.
    *   **L62:** `self._on_stage_start(stage)`
    *   **L80:** `self._on_stage_complete(stage, elapsed_ms)`

*   **Implicit Events:** `src/core/registry/role_registry.py` mentions `EventBus` and `EventHandler` as roles in the analyzed code (`L172-L173` in `standard_model_enricher.py`), but the *core infrastructure* itself uses a linear pipeline, not an event loop.

**Conclusion:** This is the only missing core component. The existing hooks are synchronous and coupled. A true Event Bus would decouple the stages further.

#### QUESTION 5: What SHOULD we integrate with vs rebuild?

**1. The Hub (Registry)**
*   **Action:** **REFACTOR** `src/core/registry/registry_of_registries.py`.
*   **Plan:** Rename to `CoreHub`. Add `get_service()` and `register_service()` methods to formalize DI. Use this to bootstrap MCP.

**2. Plugin System**
*   **Action:** **EXTEND** `src/core/pipeline/`.
*   **Plan:** The `PipelineManager` is robust. Don't rebuild it. Just create a `DistributionPipeline` using the same `PipelineManager` class but with different stages (e.g., `NpmPublishStage`, `GitPushStage`).

**3. Schema Validation**
*   **Action:** **EXTEND** `src/core/normalize_output.py`.
*   **Plan:** Extract `validate_contract` into a generic `SchemaValidator` service registered in the Hub.

**4. MCP Integration**
*   **Action:** **BUILD NEW**.
*   **Plan:** Build `src/interface/mcp_server.py`. It should import `get_meta_registry()` (the Hub) to access tools and data.

---

### ARCHITECTURE DEBT WARNING
You have a distinct "God Class" risk forming in `src/core/unified_analysis.py` (L190 `create_unified_output`) and `src/core/full_analysis.py`. These files manually orchestrate the flow that `PipelineManager` was designed to handle.

*   **Evidence:** `src/core/full_analysis.py` L167-L208 manually manages stages like `Survey`, `Base Analysis`, etc., despite `PipelineManager` existing.
*   **Recommendation:** Move the logic from `full_analysis.py` into a concrete `StandardAnalysisPipeline` configuration using `PipelineManager`.

### FINAL VERDICT

**DO NOT BUILD FROM SCRATCH.**

1.  **Hub:** Use `src/core/registry/registry_of_registries.py`.
2.  **Plugins:** Use `src/core/pipeline/manager.py`.
3.  **Validation:** Refactor `src/core/normalize_output.py` into a service.
4.  **Events:** Build `src/core/event_bus.py` (New) and register it in the Hub.

---

## Citations

_No citations provided_
