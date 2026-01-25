# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-24 22:41:55\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings

- **Entity**: `run_full_analysis` (Function)
  - **Status**: Non-Compliant
  - **Evidence**: `def run_full_analysis(...)` implements steps explicitly labeled as "Stage 0", "Stage 1", "Stage 2" via `StageTimer` and procedural calls.
  - **Deviation**: This entity acts as a monolithic orchestrator but violates the **Stage** concept architecture.
    - **Invariant Breach**: Does not inherit from `BaseStage`.
    - **Invariant Breach**: Does not implement `execute(state: CodebaseState) -> CodebaseState`.
    - **Invariant Breach**: Manages state via loose variables (`nodes`, `edges`) instead of the `CodebaseState` container.
    - **Invariant Breach**: Defined as a procedural function rather than an encapsulated class.

- **Entity**: `create_codome_boundaries` (Function)
  - **Status**: Non-Compliant
  - **Evidence**: `def create_codome_boundaries(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:`
  - **Deviation**: Represents a distinct processing unit ("Codome Analysis") but is implemented as a functional helper rather than a `Stage`.
    - **Invariant Breach**: Does not inherit from `BaseStage`.
    - **Invariant Breach**: Signature is `(nodes, edges) -> Dict` instead of `execute(state) -> state`.
    - **Invariant Breach**: Lacks `name` property.

- **Entity**: `detect_knots` (Function)
  - **Status**: Non-Compliant
  - **Evidence**: `def detect_knots(nodes: List[Dict], edges: List[Dict]) -> Dict:`
  - **Deviation**: Represents a topology analysis unit but is implemented as a standalone function.
    - **Invariant Breach**: Does not inherit from `BaseStage`.
    - **Invariant Breach**: Incorrect method signature for a pipeline stage.

- **Entity**: `compute_markov_matrix` (Function)
  - **Status**: Non-Compliant
  - **Evidence**: `def compute_markov_matrix(nodes: List[Dict], edges: List[Dict]) -> Dict:`
  - **Deviation**: Represents a flow analysis unit but is implemented as a standalone function.
    - **Invariant Breach**: Does not inherit from `BaseStage`.
    - **Invariant Breach**: Incorrect method signature for a pipeline stage.

- **Entity**: `run_pipeline_analysis` (Function)
  - **Status**: Architecturally Aligned (Not a Stage)
  - **Evidence**: `state = pipeline.run(state)`
  - **Deviation**: This function acts as an entry point that correctly utilizes the `Pipeline` and `BaseStage` architecture (imported from `.pipeline`), contrasting with `run_full_analysis`. It is not a `Stage` itself but orchestrates the compliant pipeline.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM001]**: Context Myopia: The function 'detect_knots' manually re-implements a simplified, inefficient, and recursion-prone graph cycle detection algorithm. The import of 'src.core.graph_framework' implies access to 'networkx' (via 'build_nx_graph'), which provides robust, optimized standard algorithms (e.g., 'nx.simple_cycles') that should be used instead of custom implementations. (Severity: HIGH)\n- 🔴 **[AM002]**: Architectural Drift: The module is located in 'src.core' (Core Business Logic) but contains OS-specific presentation/UI logic in '_open_file' and '_manual_open_command' (invoking 'xdg-open', 'start', etc.). Opening reports in a browser is a CLI/Interface concern, not a Core Analysis concern. (Severity: MEDIUM)\n- 🔴 **[AM001]**: Context Myopia: 'detect_js_imports' and 'detect_class_instantiation' perform ad-hoc regex-based file parsing and I/O within the analysis orchestration layer. This duplicates parsing logic that belongs in the existing 'FileEnricher' or dedicated language parsers, fragmenting the 'Source of Truth' for dependency extraction. (Severity: MEDIUM)\n\n## Concept: PipelineManager\n> Orchestrator that executes stages in sequence with timing.\n\n### Findings

- **Entity**: `PipelineManager` (class in `src/core/pipeline/manager.py`)
- **Status**: Compliant
- **Evidence**:
    - **Accepts list of BaseStage**: The constructor explicitly defines the signature `def __init__(self, stages: List[BaseStage], ...)` and stores them in `self.stages`.
    - **Executes in order via run(state)**: The `run(state)` method iterates sequentially (`for stage in self.stages:`) and updates the state via `state = stage.execute(state)`.
    - **Tracks timing**: Inside the loop, the code captures `start_time = time.perf_counter()` and calculates `elapsed_ms` immediately after execution.
    - **Callbacks**: The class accepts `on_stage_start` and `on_stage_complete` in `__init__` and invokes them correctly within the execution loop (e.g., `self._on_stage_complete(stage, elapsed_ms)`).
- **Deviation**: None.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift: The class docstring explicitly lists 'Handle errors gracefully' as a responsibility, but the 'run' method contains no exception handling (try/except) blocks. Any exception raised by 'stage.execute(state)' will crash the entire pipeline, violating the stated design role. (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia: The class accepts a 'perf_manager' argument and stores it, but never utilizes it in the 'run' method. Instead, it re-implements basic timing logic using 'time.perf_counter()' and ignores the established observability component provided in the constructor. (Severity: MEDIUM)\n- 🔴 **[AM002]**: Architectural Drift (Layer Violation): The 'run' method uses 'print()' for warnings. In a 'Core' layer component of a complex system ('standard-model-of-code'), logging should be routed through a logger or the observability module, not written directly to stdout. (Severity: LOW)\n\n## Concept: CodebaseState\n> Central state container passed between pipeline stages.\n\n### Findings

- **Entity**: `CodebaseState` (in `src/core/data_management.py`)
- **Status**: **Compliant**
- **Evidence**:
    - **Nodes/Edges Collections**: The class initializes `self.nodes = {}` and `self.edges = []` in `__init__` and populates them in `load_initial_graph`.
    - **O(1) Lookups**: The class maintains hash map indexes (`_by_file`, `_by_ring`, `_by_kind`, `_by_role`) and provides corresponding accessor methods (`get_by_file`, `get_by_ring`, etc.) that perform dictionary lookups.
    - **Metadata Tracking**: `self.metadata` is initialized with `"layers_activated": []` in `__init__`.
    - **Enrichment**: The method `enrich_node(self, node_id, layer_name, **attributes)` is present. It updates node attributes and appends the `layer_name` to `self.metadata["layers_activated"]`.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM004]**: The classes 'UnifiedNode', 'UnifiedEdge', and 'UnifiedAnalysisOutput' are imported from 'unified_analysis' but never referenced in the code. The implementation relies on generic dictionary manipulation and 'Any' types instead of these domain models. (Severity: MEDIUM)\n- 🔴 **[AM002]**: Architectural Drift detected in 'load_initial_graph': The Core Data Layer contains a direct call to 'print()', coupling data management logic with the CLI/Presentation layer. This should be handled via a logger or returned as status metadata. (Severity: LOW)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\nBased on the provided codebase and the semantic definition of an **Extractor**, here is the audit report.

### Findings

- **Entity**: `intent_extractor.py` (Module)
  - **Status**: Compliant
  - **Evidence**: The module ingests raw data from multiple sources: file content (`extract_readme_intent`), git logs (`extract_commit_intents`), and source code strings (`extract_docstring_intent`).
  - **Reasoning**: While it contains a function named `classify_commit_intent`, the logic relies on simple keyword matching (e.g., checking if "fix" is in the message) rather than complex semantic reasoning or architectural inference. It aggregates raw signals into a profile.

- **Entity**: `SmartExtractor` (Class in `smart_extractor.py`)
  - **Status**: Compliant
  - **Evidence**: Its stated purpose is "Rich Context Extraction for LLM Classification". It reads raw source files and parses ASTs (`_enrich_from_ast`) to populate a `ComponentCard`.
  - **Reasoning**: It strictly gathers structural data (lines, decorators, imports) and heuristics (folder layer via path patterns). It explicitly delegates the "complex semantic reasoning" to an external LLM by formatting the extracted data into a prompt (`format_card_for_llm`).

- **Entity**: `EdgeExtractionStrategy` & Subclasses (in `edge_extractor.py`)
  - **Status**: Compliant
  - **Evidence**: These classes (e.g., `PythonEdgeStrategy`, `TreeSitterEdgeStrategy`) operate directly on `body_source` strings using regex or `tree-sitter` ASTs.
  - **Reasoning**: They identify syntactic relationships (calls, imports, inheritance) based on raw patterns and structure. They do not interpret the business logic or intent of the connections, satisfying the invariant of avoiding complex semantic reasoning.

- **Entity**: `JSModuleResolver` (Class in `edge_extractor.py`)
  - **Status**: Compliant
  - **Evidence**: Analyzes Javascript file content using AST traversals to track `window` exports and `require`/`import` statements.
  - **Reasoning**: It performs data ingestion to resolve scope and linking, operating strictly on the syntax tree of the raw files.

### Summary
All analyzed components adhere to the **Extractor** concept. They focus on ingesting raw data (files, git history, AST nodes) and structuring it (into profiles, cards, or edges) without crossing the boundary into complex semantic reasoning, which is reserved for the Classifier role.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM001]**: In 'intent_extractor.py', the function 'extract_docstring_intent' re-implements Python docstring extraction using brittle regex patterns. This violates Context Myopia by ignoring the Python standard library's 'ast' module (which is correctly utilized in the sibling file 'smart_extractor.py') and creating unnecessary, inferior duplication of logic. (Severity: HIGH)\n- 🔴 **[AM001]**: In 'edge_extractor.py', the import logic for 'ScopeAnalyzer' attempts three different import paths (src.core..., core..., and local). This 'guesswork' indicates the code is myopic to the project's actual package structure, suggesting it was copied from elsewhere without proper integration into the project's namespace context. (Severity: MEDIUM)\n- 🔴 **[AM002]**: In 'intent_extractor.py', the core logic tightly couples with the shell environment by directly executing 'git' subprocesses. This constitutes Architectural Drift for a 'core' module, which should ideally abstract infrastructure concerns (like VCS operations) behind an adapter interface to maintain testability and layer separation. (Severity: MEDIUM)\n\n
