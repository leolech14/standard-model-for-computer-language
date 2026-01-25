# Research: List 3 key files in the pipeline

> **Date:** 2026-01-23 13:34:35
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:9d98cb78a51d5c85a9f0ef6c9f1c0243c22b0cec72b28bce86ea81c8e5843143`
> **Raw JSON:** `raw/20260123_133435_list_3_key_files_in_the_pipeline.json`

---

## Query

List 3 key files in the pipeline

---

## Response

Based on the **`analysis_sets.yaml`** configuration and **`COLLIDER_ARCHITECTURE.md`**, here are 3 key files in the analysis pipeline:

1.  **`standard-model-of-code/src/core/full_analysis.py`**
    *   **Role:** The main pipeline orchestrator and driver.
    *   **Why:** Listed as a **critical file** in the `pipeline` analysis set. It coordinates the 12-stage analysis process, managing the flow from parsing to output generation.

2.  **`standard-model-of-code/src/core/unified_analysis.py`**
    *   **Role:** The core analysis engine (Stages 1-6).
    *   **Why:** Handles the "Unified Analysis" phase, including AST parsing, RPBL classification, and auto-pattern discovery before passing data to the full analysis context.

3.  **`standard-model-of-code/src/core/edge_extractor.py`**
    *   **Role:** Relationship builder.
    *   **Why:** Explicitly included in the `pipeline` analysis set. It is responsible for determining connections (calls, imports, inheritance) between nodes, which is essential for constructing the semantic graph.

---

## Citations

_No citations provided_
