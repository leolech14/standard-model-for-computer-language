# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-23 02:06:26\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings
The codebase uses a procedural approach for its analysis pipeline, where standalone functions act as processing units. This architectural choice is in direct conflict with the object-oriented `Stage` concept, which requires class-based implementation. Consequently, no entities in the provided file are compliant.

---
- **Entity**: `compute_markov_matrix`
- **Status**: Non-Compliant
- **Evidence**: The entity is defined as a standalone function:
  ```python
  def compute_markov_matrix(nodes: List[Dict], edges: List[Dict]) -> Dict:
      """
      Compute Markov transition matrix from call graph.
      ...
      """
  ```
- **Deviation**: The function fails to meet multiple invariants:
    - It is a standalone function and does not inherit from a `BaseStage` class.
    - It does not implement an `execute` or `run` method; its name is `compute_markov_matrix`.
    - It returns a standard Python `Dict`, not a `ProcessingResult` or `AnalysisResult` object.
    - It violates the spirit of statelessness by modifying its `edges` input list in-place (`edge['markov_weight'] = ...`).

---
- **Entity**: `detect_knots`
- **Status**: Non-Compliant
- **Evidence**: The entity is defined as a standalone function:
  ```python
  def detect_knots(nodes: List[Dict], edges: List[Dict]) -> Dict:
      """
      Detect dependency knots (cycles) and tangles in the graph.
      ...
      """
  ```
- **Deviation**: The function fails to meet multiple invariants:
    - It is a standalone function and does not inherit from a `BaseStage` class.
    - It does not implement an `execute` or `run` method; its name is `detect_knots`.
    - It returns a standard Python `Dict`, not a `ProcessingResult` or `AnalysisResult` object.

---
- **Entity**: `compute_data_flow`
- **Status**: Non-Compliant
- **Evidence**: The entity is defined as a standalone function:
  ```python
  def compute_data_flow(nodes: List[Dict], edges: List[Dict]) -> Dict:
      """
      Analyze data flow patterns across the codebase.
      """
  ```
- **Deviation**: The function fails to meet multiple invariants:
    - It is a standalone function and does not inherit from a `BaseStage` class.
    - It does not implement an `execute` or `run` method; its name is `compute_data_flow`.
    - It returns a standard Python `Dict`, not a `ProcessingResult` or `AnalysisResult` object.

---
- **Entity**: `create_codome_boundaries`
- **Status**: Non-Compliant
- **Evidence**: The entity is defined as a standalone function:
  ```python
  def create_codome_boundaries(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
      """
      Create synthetic codome boundary nodes and inferred edges.
      ...
      """
  ```
- **Deviation**: The function fails to meet multiple invariants:
    - It is a standalone function and does not inherit from a `BaseStage` class.
    - It does not implement an `execute` or `run` method.
    - It returns a standard Python `Dict`, not a `ProcessingResult` or `AnalysisResult` object.
    - It violates the spirit of statelessness by modifying its `edges` input list via calls to `detect_js_imports` and `detect_class_instantiation`.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM004]**: The function 'compute_data_flow' is defined as an incomplete stub with its signature trailing off (`-> Di`). This code is non-functional, cannot be called, and represents incomplete or abandoned work. It is classic orphan code that adds clutter and potential confusion without providing any functionality. (Severity: HIGH)\n- 🔴 **[AM004]**: The module imports 'FileEnricher' from 'src.core.file_enricher', but this import is never used anywhere in the provided file. This constitutes an unnecessary dependency and dead code at the module level. (Severity: LOW)\n- 🔴 **[AM004]**: Within the 'build_file_index' function, the variable 'node_to_file' is initialized and populated with data from the nodes list, but it is never read or used for any subsequent computation. This is a small but clear instance of orphan code within a function. (Severity: LOW)\n- 🔴 **[AM004]**: The 'detect_knots' function initializes and populates a 'reverse' graph dictionary. However, this variable is never subsequently read or used in the cycle detection logic, making its creation and population useless work. (Severity: LOW)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings
- **Entity**: `SmartExtractor`
- **Status**: Compliant
- **Evidence**: The class fulfills the definition of an Extractor by ingesting raw data from the codebase to prepare it for another component.
    - **Invariant 1 (Operates on raw file/AST):** The class directly reads source files (`file_path.read_text`) and parses them into an AST (`ast.parse(source)`) to extract information like code excerpts, docstrings, decorators, and base classes.
    - **Invariant 2 (No complex semantic reasoning):** The class's primary role is data aggregation. While `_infer_layer` performs a heuristic analysis, it is a simple, pattern-based check against file paths (`LAYER_PATTERNS`), not a complex analysis of the code's behavior or purpose. This is a form of pre-processing, not the architectural reasoning reserved for a Classifier.
- **Deviation**: None.

---
- **Entity**: `EdgeExtractionStrategy` (and its concrete implementations)
- **Status**: Compliant
- **Evidence**: The strategies are responsible for extracting structural relationships (edges) from source code, which is a form of raw data ingestion.
    - **Invariant 1 (Operates on raw file/AST):** The strategies operate on either raw source code snippets via regex (e.g., `PythonEdgeStrategy`: `re.findall(..., body)`) or on an AST generated by Tree-sitter (e.g., `TreeSitterEdgeStrategy`: `tree = self.parser.parse(source_bytes)`).
    - **Invariant 2 (No complex semantic reasoning):** The goal of these strategies is to identify factual, structural relationships like function calls or class inheritance. Even advanced implementations like `JavaScriptTreeSitterStrategy` that use a `JSModuleResolver` and scope analysis are performing language-level semantic resolution to accurately identify *what calls what*. This is distinct from the *architectural* reasoning a Classifier would perform (e.g., classifying a component's role). The reasoning is confined to correctly extracting the code's structure.
- **Deviation**: None.\n\n### Semantic Guardrails (Antimatter Check)\n**PASSED**: No liabilities detected.\n\n