# Standard Model for Computer Language (Spectrometer v12)

Spectrometer is an architecture-aware codebase analyzer that extracts "particles" (components) and builds dependency graphs. It features a **Hybrid Static+LLM Pipeline** that combines deterministic static analysis with semantic role inference using LLMs.

## 🚀 Quick Start (Plug & Play)

No complex setup required. Works out of the box with standard Python 3.11+.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Analysis
Scan a repository (or folder) to generate a report, JSON results, and a dependency graph.

```bash
# Basic (Static Analysis Only)
python3 cli.py analyze /path/to/repo --mode minimal

# Hybrid (Static + LLM Semantic Inference)
# Requires Ollama running locally (default model: qwen2.5:7b-instruct)
python3 cli.py analyze /path/to/repo --mode minimal --llm
```

The output will be saved in `output/` by default.


## 🩺 System Health & Auditing

### Health Check
Verify that all pipelines (Regex, God Class Detector, Graph Logic, LLM connectivity) are operational.

```bash
python3 cli.py health
```

### Full Audit
Run a comprehensive validation that combines the health check with a live analysis of a target repo (or the current directory). This proves the toolchain works end-to-end.

```bash
# Audit the current directory
python3 cli.py audit .

# Audit a specific repo
python3 cli.py audit /path/to/repo --mode minimal
```

## 🧠 Architecture: The Hybrid Pipeline

1.  **Structural Truth (Static)**:
    *   Files are parsed using Regex (Minimal Mode) or Tree-Sitter (Full Mode if configured).
    *   **Nodes** (Classes, Functions) and **Edges** (Imports, Calls) are extracted deterministically.
    *   *Rule: If we can't prove it statically, it's not in the graph.*

2.  **Semantic Overlay (Heuristic)**:
    *   Components are assigned roles (e.g., `Controller`, `Repository`) based on naming conventions and patterns.
    *   Confidence scores are assigned.

3.  **LLM Escalation (Optional)**:
    *   Low-confidence components (< 55%) are sent to a local LLM (Ollama).
    *   The LLM analyzes code excerpts to infer the role.
    *   **Evidence Validator**: The system rejects any "hallucinated" evidence not found verbatim in the code.

4.  **Risk & Reporting**:
    *   **God Class Detector**: Identifies risk based on method counts and cohesion.
    *   **Architecture Compliance**: Checks for layer violations (e.g., Domain depending on Infrastructure).

## 📂 Project Structure

*   `cli.py`: **Main Entry Point**.
*   `learning_engine.py`: Orchestrator for the analysis pipeline.
*   `core/`: Core logic (Detectors, Graph Extractor, LLM Classifier).
*   `patterns/`: Regex patterns and definitions.
*   `extras/`: Legacy scripts and experimental tools (removed from root to reduce noise).
