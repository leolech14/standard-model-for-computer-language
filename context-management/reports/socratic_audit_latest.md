# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-26 05:56:35\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings

- **Entity**: `BaseStage` (`src/core/pipeline/base_stage.py`)
- **Status**: **Compliant**
- **Evidence**:
  - Inherits from `ABC`, establishing the root of the inheritance hierarchy for the concept.
  - Defines `@abstractmethod def execute(self, state: "CodebaseState") -> "CodebaseState"`, satisfying the execution interface invariant.
  - Defines `@property @abstractmethod def name(self) -> str`, satisfying the identifier invariant.
  - Includes `validate_input` and `validate_output` methods for pre/post checks.
  - Is stateless by definition (defines interface/methods only).

- **Entity**: `run_full_analysis` (Procedural Stages) (`src/core/full_analysis.py`)
- **Status**: **Non-Compliant**
- **Evidence**: The function explicitly delineates processing units as "Stages" in logs and telemetry (e.g., `print("\n🔬 Stage 1: Base Analysis...")`, `StageTimer(..., "Stage 1: Base Analysis")`).
- **Deviation**: These "Stages" are implemented procedurally as inline code blocks rather than as classes inheriting from `BaseStage`.
  - **Inheritance**: Does not inherit from `BaseStage`.
  - **Encapsulation**: Logic is mixed with orchestration in a single script, modifying local variables rather than implementing an isolated `execute` method.
  - **Note**: This appears to be a legacy implementation co-existing with the compliant `run_pipeline_analysis` function which delegates to the `pipeline` module (not provided, but implied to use `BaseStage`).\n\n### Semantic Guardrails (Antimatter Check)\n**PASSED**: No liabilities detected.\n\n## Concept: PipelineManager\n> Orchestrator that executes stages in sequence with timing.\n\n### Findings
- **Entity**: `PipelineManager` (class)
- **Status**: **Compliant**
- **Evidence**:
  - **Accepts BaseStage List**: The `__init__` method signature is defined as `def __init__(self, stages: List[BaseStage], ...`.
  - **Executes in order via run(state)**: The `run` method iterates sequentially: `for stage in self.stages: ... state = stage.execute(state)`.
  - **Tracks timing**: The `run` method captures execution time: `start_time = time.perf_counter() ... elapsed_ms = (time.perf_counter() - start_time) * 1000`.
  - **Callbacks**: The class accepts and utilizes `on_stage_start` and `on_stage_complete` in the `__init__` method and triggers them within the `run` loop.
- **Deviation**: N/A\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift detected in the Core layer. The PipelineManager (a Core component) directly utilizes `print()` for warnings. Core logic should be agnostic of the interface and should utilize a Logger or return status codes rather than writing directly to stdout. (Severity: MEDIUM)\n- 🔴 **[AM001]**: Context Myopia regarding `perf_manager`. The class accepts and stores a `PerformanceManager` dependency in `__init__`, but strictly ignores it in `run()`, re-implementing manual timing logic (`time.perf_counter`) instead of delegating to the specialized component provided. (Severity: HIGH)\n- 🔴 **[AM002]**: Inconsistent execution logic (Drift). The `run_stage` method bypasses the critical `validate_input` and `validate_output` safeguards established in the main `run` loop, allowing unsafe execution of stages. (Severity: LOW)\n\n## Concept: CodebaseState\n> Central state container passed between pipeline stages.\n\n### Findings

- **Entity**: `CodebaseState` (in `src/core/data_management.py`)
- **Status**: **Compliant**
- **Evidence**:
  - **Collections**: The class initializes storage for the graph structure in `__init__`: `self.nodes: Dict[str, Dict[str, Any]] = {}` and `self.edges: List[Dict[str, Any]] = []`.
  - **Indexed Lookups**: The class maintains hash map indexes (`_by_file`, `_by_ring`, `_by_kind`, `_by_role`) initialized in `__init__` and populated in `load_initial_graph`. It exposes specific accessor methods (`get_by_file`, `get_by_ring`, `get_by_kind`, `get_by_role`) that perform O(1) key lookups.
  - **Metadata**: The `metadata` dictionary explicitly initializes `"layers_activated": []` in the constructor.
  - **Enrichment**: The method `enrich_node(self, node_id: str, layer_name: str, **attributes)` is implemented to merge attributes into existing nodes and update the `layers_activated` list.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift detected: The 'CodebaseState' class, acting as the Core Data Layer, executes a 'print()' statement in 'load_initial_graph'. Core domain logic must be free of side-effects like writing to stdout; such actions belong strictly to the CLI or Presentation layer. (Severity: HIGH)\n- 🔴 **[AM004]**: Orphan Code/Import detected: 'asdict' is imported from 'dataclasses' but never used. The method 'load_initial_graph' manually attempts to convert objects to dictionaries using 'vars()' or 'to_dict()', ignoring the robust standard library utility explicitly imported for this purpose. (Severity: MEDIUM)\n- 🔴 **[AM001]**: Context Myopia detected: The 'try-except' import block for 'normalize_output' attempts to handle import paths dynamically (script vs package context). This implies the module is ignoring the project's established package structure and execution context conventions. (Severity: LOW)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings

- **Entity**: `SmartExtractor` (`src/core/smart_extractor.py`)
- **Status**: **Compliant**
- **Evidence**:
  - Uses `ast.parse` and file reading (`path.read_text`) to gather data.
  - Explicitly delegates complex reasoning to an LLM via `format_card_for_llm`.
  - Logic like `_infer_layer` uses simple string pattern matching (`LAYER_PATTERNS`), not semantic inference.
- **Reasoning**: The component strictly adheres to gathering structural context (decorators, signatures, imports) and raw code to facilitate downstream classification, avoiding logic that interprets the code's purpose itself.

- **Entity**: `IntentExtractor` (`src/core/intent_extractor.py`)
- **Status**: **Compliant**
- **Evidence**:
  - Ingests raw data from `git log` subprocess calls, `README` file reads, and docstring regex extraction.
  - `classify_commit_intent` uses deterministic keyword matching (e.g., `if 'fix' in message`) rather than semantic understanding.
- **Reasoning**: While it derives "intent", it does so through mechanical extraction of explicit signals (Commit Conventional Commits, docstring placement) rather than complex reasoning.

- **Entity**: `EdgeExtractor` / Strategies (`src/core/edge_extractor.py`)
- **Status**: **Compliant**
- **Evidence**:
  - `JSModuleResolver` and `TreeSitterEdgeStrategy` operate directly on ASTs (Tree-sitter) or raw source strings (Regex).
  - Scope analysis (`QueryBasedScopeAnalyzer`) is mentioned but represents rigorous static analysis (variable visibility) rather than semantic reasoning about business logic.
- **Reasoning**: The component focuses entirely on syntactic relationships (calls, imports, inheritance) derived from raw code structure.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM004]**: The file 'edge_extractor.py' contains a critical syntax error and incomplete implementation. The method 'resolve_member_call' is defined in the signature but lacks a body, and the file terminates abruptly with a comment, rendering the class and module unusable (Orphan/Broken Code). (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia in 'smart_extractor.py'. The 'SmartExtractor' implements its own Python parsing logic using the 'ast' library (methods '_enrich_from_ast', '_extract_imports') to extract imports and class structures. This duplicates the parsing intent found in 'edge_extractor.py', which integrates 'tree_sitter' for similar structural analysis. The system should converge on a single parsing strategy (preferably the more robust 'tree_sitter') to avoid divergent behavior. (Severity: MEDIUM)\n- 🔴 **[AM002]**: Architectural Drift in 'src/core'. The modules 'intent_extractor.py' and 'smart_extractor.py' are placed in the 'core' layer but contain direct infrastructure implementations, specifically direct File I/O and 'subprocess' calls to 'git'. In a standard architectural model, 'Core' should remain pure or use interfaces, delegating volatile external IO (Git, Filesystem) to an Infrastructure/Adapter layer. (Severity: MEDIUM)\n\n
