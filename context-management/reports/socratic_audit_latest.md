# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-23 02:49:07\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings

Based on the semantic definition of a **Stage**, I have audited the provided codebase. The analysis reveals a systemic architectural deviation from the specified concept. The pipeline is implemented using a procedural approach with standalone functions rather than an object-oriented one with classes inheriting from a common base.

---

- **Entity**: Stage Implementation Pattern (as Functions)
- **Status**: Non-Compliant
- **Evidence**: The main pipeline orchestrator, `run_full_analysis`, calls a series of regular Python functions to perform sequential processing tasks. These functions represent the "Stages" in the pipeline.

  Examples include:
  ```python
  # Stage 2: Standard Model enrichment
  print("\n🧬 Stage 2: Standard Model Enrichment...")
  with StageTimer(perf_manager, "Stage 2: Standard Model Enrichment") as timer:
      nodes = enrich_with_standard_model(nodes)
      ...

  # Stage 2.7: Octahedral Dimension Classification
  print("\n📐 Stage 2.7: Octahedral Dimension Classification...")
  with StageTimer(perf_manager, "Stage 2.7: Dimension Classification") as timer:
      try:
          from dimension_classifier import classify_all_dimensions
          dim_count = classify_all_dimensions(nodes)
          ...
  ```
  These functions, like `enrich_with_standard_model` and `classify_all_dimensions`, are the concrete implementations of the `Stage` concept.

- **Deviation**: This functional implementation pattern violates multiple invariants:
    - **Invariant 1 (Inherit from base class):** The stages are functions, not classes, so they cannot inherit from a `BaseStage` class.
    - **Invariant 2 (Implement 'execute'/'run'):** Stages are invoked by their unique function names (e.g., `enrich_with_standard_model`), not a standardized method like `execute` or `run`.
    - **Invariant 4 (Return standard format):** The functions do not return a standard `ProcessingResult` object. They take a specific data structure (like the `nodes` list), modify or replace it, and return it. The overall state is managed externally by the `run_full_analysis` function.

  The pattern is, however, compliant with the "stateless" invariant, as the functions operate on their inputs without maintaining an internal state between calls.

---

- **Entity**: `PatternMatcher`
- **Status**: Non-Compliant
- **Evidence**: In "Stage 2.10: Pattern-Based Atom Detection," a class instance is used to perform the processing, which is closer to the intended object-oriented design.

  ```python
  # Stage 2.10: Pattern-Based Atom Detection
  print("\n🧬 Stage 2.10: Pattern-Based Atom Detection...")
  with StageTimer(perf_manager, "Stage 2.10: Pattern Detection") as timer:
      try:
          from pattern_matcher import PatternMatcher
          ...
          pattern_matcher = PatternMatcher()
          ...
          atoms = pattern_matcher.detect_atoms(tree, bytes(body, 'utf8'), lang)
  ```
- **Deviation**: Despite being a class-based component, `PatternMatcher` does not adhere to the `Stage` definition:
    - **Invariant 1 (Inherit from base class):** There is no evidence that `PatternMatcher` inherits from a `BaseStage` class.
    - **Invariant 2 (Implement 'execute'/'run'):** It uses a specific method name, `detect_atoms`, instead of the standard `execute` or `run`.
    - **Invariant 4 (Return standard format):** The `detect_atoms` method returns a list of `atoms`, not a standardized `ProcessingResult` object.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM004]**: The code imports `FileEnricher` from `src.core.file_enricher` at the top level but never uses it within the provided file scope. Furthermore, a large number of public functions (`build_file_index`, `build_file_boundaries`, `_calculate_theory_completeness`, `compute_markov_matrix`, `detect_knots`, `compute_data_flow`, and several CLI helpers like `_resolve_output_dir`) are defined but are never called, making them orphan code within this module's context. (Severity: HIGH)\n- 🔴 **[AM002]**: The code violates its 'Stage' role, which implies stateless transformation. Functions like `detect_js_imports`, `detect_class_instantiation`, and `compute_markov_matrix` modify the input `edges` list in-place. This introduces side effects, breaking the stateless data pipeline paradigm and making the system's behavior harder to reason about and test. A Stage should return new or transformed data, not mutate its inputs. (Severity: HIGH)\n- 🔴 **[AM001]**: The `detect_knots` function implements a 'simplified Tarjan-like' algorithm to find cycles. This represents context myopia by reimplementing a fundamental graph algorithm, which is a solved problem, instead of using a standard, robust library (e.g., networkx). This custom, performance-limited implementation (`[:10]`, `[:200]`) is likely to be less efficient and more error-prone than an established solution. (Severity: MEDIUM)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings
- **Entity**: `extract_call_edges` (Main Orchestrator Function)
- **Status**: Compliant
- **Evidence**: The function orchestrates the extraction process by operating on `particles` (which contain raw `body_source`) and `results` (which contain `raw_imports` and `raw_content`). It builds structural edges like `imports`, `contains`, and `inherits` from pre-parsed metadata and delegates body analysis to language-specific strategies. For example, it passes raw file content to the `JSModuleResolver`: `resolver.analyze_file(file_path, content)`.
- **Deviation**: None. The function is a pure orchestrator for extraction tasks, transforming raw or semi-raw data into a structured graph of relationships without inferring high-level concepts.

---
- **Entity**: `EdgeExtractionStrategy` (and its Regex-based subclasses: `PythonEdgeStrategy`, `JavascriptEdgeStrategy`, etc.)
- **Status**: Compliant
- **Evidence**: These strategies operate directly on the raw source code of a function body. For instance, `PythonEdgeStrategy` uses `body = particle.get('body_source', '')` and then applies `re.findall(r'(?:self\.)?(\w+)\s*\(', body)` to find call patterns. This is a direct operation on raw file content. The logic is based on simple lexical patterns, not semantic understanding.
- **Deviation**: None. This is a classic example of extraction from raw content.

---
- **Entity**: `TreeSitterEdgeStrategy` (and its subclasses: `PythonTreeSitterStrategy`, `JavaScriptTreeSitterStrategy`, etc.)
- **Status**: Compliant
- **Evidence**: This family of strategies operates on an Abstract Syntax Tree (AST). The code explicitly parses the raw body source into an AST: `tree = self.parser.parse(source_bytes)`. It then traverses this tree to find specific node types, such as `call_expression`, to identify function calls. This perfectly matches the "Must operate on raw file content or AST" invariant. While it uses a `ScopeAnalyzer` for more accurate reference resolution, this is a structural analysis task (determining which declaration a name refers to) rather than complex semantic reasoning (determining what a function *does*).
- **Deviation**: None. The use of an AST and scope analysis is an advanced extraction technique, but it remains within the defined boundaries of an Extractor, as it reasons about code structure, not its conceptual purpose.

---
- **Entity**: `JSModuleResolver`
- **Status**: Compliant
- **Evidence**: The `JSModuleResolver` class is responsible for resolving module references in JavaScript. It does this by parsing JavaScript files (`analyze_file`) using Tree-sitter (an AST parser) to find `import`, `require`, and `window.export` patterns. This is an operation on an AST derived from raw file content. Its purpose is to resolve dependencies to build an accurate call graph, which is a core extraction task. It does not attempt to classify the *role* or *meaning* of the modules it resolves.
- **Deviation**: None. This component performs sophisticated reference resolution, but this is a form of structural analysis, not the "complex semantic reasoning" that a Classifier would perform. It determines *where* a symbol is defined, not *what* it represents conceptually.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: The component violates its 'Extractor' role by introducing a global stateful singleton ('_js_module_resolver'). An extractor should be a stateless transformer of inputs to outputs. The use of a global instance, managed by `get_js_module_resolver()` and `reset_js_module_resolver()`, introduces side effects and hidden dependencies, drifting from a pure architectural role towards a stateful service, which complicates testing and concurrency. (Severity: MEDIUM)\n- 🔴 **[AM001]**: The code exhibits context myopia regarding its own project structure. The repeated, cascading `try-except ImportError` blocks for `scope_analyzer` (from 'src.core', 'core', and root) indicate the module is unaware of its canonical location within the project and is attempting to guess the import path. This suggests a fragile coupling and a lack of established architectural context for internal dependencies. (Severity: MEDIUM)\n- 🔴 **[AM004]**: The method `get_callee_with_location` within the `TreeSitterEdgeStrategy` class is defined but is never called within the provided code. Its counterpart, `extract_callee_name`, is used instead. While potentially intended for future enhancements, in its current state, it constitutes orphan code that is not integrated into any execution path. (Severity: LOW)\n- 🔴 **[AM001]**: The regex-based strategies (e.g., `PythonEdgeStrategy`, `JavascriptEdgeStrategy`) use hardcoded, incomplete lists of common built-in functions to ignore. This is a myopic approach that fails to consider the full context of a language's standard library, leading to brittle heuristics and potential false positives. For example, a more robust method for Python would be to check against the `__builtins__` module directly. (Severity: LOW)\n\n