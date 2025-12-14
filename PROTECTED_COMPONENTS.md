# 🛡️ PROTECTED COMPONENTS

The following components constitute the **Core Spectrometer System**.
These files are protected from "Legacy Sprawl" and overengineering.

## 🧠 The Engine (Primary Pipeline)
*   **`learning_engine.py`**: The definitive Entry Point. Orchestrates Discovery, Graph, and Learning.
*   **`diagram_generator.py`**: Visualization Core. Generates Markdown + Mermaid reports.
*   **`llm_prompts.py`**: Intelligence Core. Generates context-rich prompts for AI.

## 🔧 Core Mechanics
*   **`core/discovery_engine.py`**: The "Eyes". Scans file system (rglob) and discovers Atoms.
*   **`core/graph_extractor.py`**: The "Synapses". Builds dependency graph (imports, calls, inheritance).
*   **`core/complete_extractor.py`**: The "Hands". Extracts code bodies and signatures.
*   **`core/atom_registry.py`**: The "Memory". Stores learned atomic patterns (130+ atoms).
*   **`core/semantic_ids.py`**: The "Identity". Generates universal IDs for components.

## 🧪 Validation & Truth
*   **`truth_extractor.py`**: Generates JSON spec from code (Golden Truth).
*   **`golden_scorer.py`**: Scores analysis against Golden Truth.
*   **`validation/` directory**: The Learning Data (100+ benchmark repos).

---

## 🏛️ Legacy / Specialized Modules
*(These are kept for specific use-cases but are NOT part of the primary Learning Engine pipeline)*
*   `legacy_main.py` (formerly `main.py`)
*   `core/god_class_detector.py` (Specialized Risk Analysis)
*   `core/universal_detector.py` (Legacy Orchestrator)
