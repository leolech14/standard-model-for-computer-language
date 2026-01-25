# Research: Test connectivity

> **Date:** 2026-01-23 12:47:48
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:7a31af5c9cbee67c6d710a6fbdeeec6d01ed8cbbffb10930ca44eda671033d7f`
> **Raw JSON:** `raw/20260123_124748_test_connectivity.json`

---

## Query

Test connectivity

---

## Response

Based on the provided codebase, the system "tests connectivity" (analyzes relationships between code elements) primarily through the **Edge Extractor** and **Graph Analyzer** modules.

Here is an analysis of how connectivity is determined, tested, and classified in this codebase:

### 1. Edge Detection (Connectivity Source)
The core logic for establishing connectivity resides in `src/core/edge_extractor.py`. It uses a "Strategy Pattern" to handle polyglot analysis:

*   **Extraction Strategies**:
    *   **Python**: Uses both Regex (`PythonEdgeStrategy`) and Tree-sitter AST (`PythonTreeSitterStrategy`) to find function calls (`calls`), attribute usage (`uses`), and class inheritance (`inherits`).
    *   **JavaScript/TypeScript**: Handles complex module resolution (`JSModuleResolver`) to track imports, `window` exports, and method calls.
    *   **Go/Rust**: Regex-based heuristic extraction.
*   **Edge Types**:
    *   `imports`: Dependency management.
    *   `calls`: Control flow.
    *   `inherits`: Object-oriented hierarchy.
    *   `contains`: Structural hierarchy (File -> Class -> Method).
    *   `exposes`: Public API boundaries.

### 2. Disconnection Analysis (Connectivity Gaps)
In `src/core/full_analysis.py`, the system explicitly tests for *lack* of connectivity using `classify_disconnection`. It replaces a simple "orphan" label with a taxonomy:

*   **Test Entry**: Connectivity is missing because it's a test file (e.g., `test_*.py`).
*   **Entry Point**: It's a `main` function or CLI script.
*   **Framework Managed**: Connectivity is implicit via decorators (e.g., `@app.route`, `@dataclass`).
*   **Cross-Language**: Called from HTML/Frontend (e.g., `.vue`, `.svelte`).
*   **Dynamic Dispatch**: Used via `getattr` or reflection.

### 3. Graph Topology (Connectivity Health)
The `src/core/graph_analyzer.py` and `src/core/full_analysis.py` modules run analytics to "test" the quality of the connectivity:

*   **Knot Detection**: checks for cycles (`detect_knots`) and bidirectional coupling ("tangles").
*   **Bridge Detection**: Identifies edges that, if removed, would disconnect the graph (`find_bridges`).
*   **Bottlenecks**: Uses Betweenness Centrality to find nodes that act as connectivity chokepoints.

### 4. Codome Boundaries (Synthetic Connectivity)
To fix "false" disconnections, `create_codome_boundaries` in `full_analysis.py` generates synthetic edges:
*   Creates **Codome Boundary** nodes (e.g., `__codome__::pytest`).
*   Injects inferred edges to nodes that appear isolated but are actually reached via frameworks or external events.

### Summary
The codebase verifies connectivity by:
1.  **Extracting** explicit references (imports/calls).
2.  **Classifying** why nodes might be disconnected (Disconnection Taxonomy).
3.  **Inferring** implicit connections (Codome Boundaries).
4.  **Measuring** the topology (Knots/Bridges).

---

## Citations

_No citations provided_
