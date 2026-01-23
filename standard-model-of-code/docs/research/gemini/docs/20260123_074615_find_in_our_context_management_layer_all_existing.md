# Research: Find in our context-management layer ALL existing workflows, tools, and context infrastructure that ...

> **Date:** 2026-01-23 07:46:15
> **Source:** gemini
> **Model:** gemini-2.5-pro
> **Checksum:** `sha256:074dc80ea579c374595ec444e40a3673a30808218aabf0974f68ac07b14a0c6a`
> **Raw JSON:** `raw/20260123_074615_find_in_our_context_management_layer_all_existing.json`

---

## Query

Find in our context-management layer ALL existing workflows, tools, and context infrastructure that could support building a CONTEXT REFINERY (RAG + Long Context hybrid system).

THE VISION:
A 'Continuous Context Refinement' system that:
1. Maps the entire corpus (repo + history + archives) at LOW resolution
2. Progressively REFINES by semantic clusters
3. ATOMIZES into semantic nodes with IDs and provenance
4. RECOMPILES on-demand into optimal context packages for queries

KEY PRINCIPLES TO MATCH:
- Outside-In (coarse-to-fine, map before detail)
- Delta-First (only reprocess what changed)
- Everything becomes a Node (atomization)
- Provenance (all outputs trace to inputs)
- Autonomy with Governance (discover freely, execute with gates)

WHAT I NEED YOU TO FIND:
1. Existing tools that already do parts of this (inventory, clustering, summarization)
2. Existing schemas/formats that could hold atoms/nodes/clusters
3. Existing workflows (BARE processors, ACI, HSL) that could integrate
4. Config files that define boundaries/regions (analysis_sets.yaml etc)
5. Storage patterns already in place (intelligence/, registry/, etc)
6. Gaps - what's missing to make this work

OUTPUT FORMAT:
- Table of existing assets mapped to Refinery components
- Dependency graph of what builds on what
- Recommended implementation order
- Confidence scores for each mapping

---

## Response

Of course. As a senior software engineer, I've analyzed the provided context to map your vision for a "Context Refinery" onto the existing infrastructure. The project has a significant number of components that align perfectly with your vision. It seems you're not starting from scratch but rather formalizing and connecting a set of powerful, pre-existing ideas and tools.

Here is a detailed breakdown of the existing assets, a proposed dependency graph, and an implementation plan to bring your Context Refinery to life.

### 1. Existing Assets Mapped to Refinery Components

The codebase is rich with components that directly support the "Map, Refine, Atomize, Recompile" lifecycle. The core principles of Outside-In, Delta-First, Atomization, and Provenance are already deeply embedded in the project's philosophy.

| Refinery Component | Existing Asset(s) | File(s) | Confidence | Rationale & Analysis |
| :--- | :--- | :--- | :--- | :--- |
| **Mapping (Coarse-to-Fine)** | `analysis_sets.yaml` config, `find_relocation_candidates.py` tool, `set_mappings` | `analysis_sets.yaml`, `REPOSITORY_AUDIT_2026-01-19.md`, `aci_config.yaml` | **95%** | `analysis_sets.yaml` is a human-curated map of semantic clusters. It defines the initial coarse-grained regions. The `find_relocation_candidates.py` tool (mentioned in the audit) shows automated clustering is already a concept. `set_mappings` in `aci_config.yaml` provides a basic topic-to-cluster mapping. |
| **Refinement (Progressive)** | 12-Stage Full Analysis Pipeline, Holographic-Socratic Layer (HSL) | `COLLIDER_ARCHITECTURE.md`, `HOLOGRAPHIC_SOCRATIC_LAYER.md` | **90%** | The 12-stage pipeline described in `COLLIDER_ARCHITECTURE.md` is a direct implementation of progressive refinement, moving from raw "particles" to "enriched nodes". The HSL provides the "Delta-First" mechanism via file-change triggers. |
| **Atomization (Nodes & Provenance)** | `semantic_models.yaml`, `UnifiedNode` / `Enriched Node` schema, `documentation_map.yaml`, `R8_EPISTEMOLOGY` lens | `semantic_models.yaml`, `COLLIDER_ARCHITECTURE.md`, `documentation_map.yaml`, `STORAGE_ARCHITECTURE.md` | **90%** | The project is built on atomization. `semantic_models.yaml` defines the schema for what an "atom" is. The `Enriched Node` is the physical data structure for it. `documentation_map.yaml` and the `R8` lens explicitly track provenance and evidence, fulfilling that key principle. |
| **Recompilation (On-Demand Context)** | Adaptive Context Intelligence (ACI), Analysis Sets, Workflow Factory | `aci_config.yaml`, `analysis_sets.yaml`, `WORKFLOW_FACTORY.md` | **85%** | ACI is the brain for on-demand recompilation, using `routing_overrides` and `tiers` (RAG vs. Long Context). `analysis_sets.yaml`'s `critical_files` and `positional_strategy` are the instructions for the "compiler". The hybrid `RAG -> Long Context` workflow is explicitly documented in `WORKFLOW_FACTORY.md`. |
| **Governance & Autonomy** | Antimatter Laws, 4D Scoring, Token Budgets, Confidence Scores | `semantic_models.yaml`, `DOCS_REORG_TASK_REGISTRY.md`, `aci_config.yaml`, `STORAGE_ARCHITECTURE.md` | **95%** | The project has extensive governance mechanisms. Antimatter laws are hard rules. 4D scoring (`Factual`, `Alignment`, `Current`, `Onwards`) is a sophisticated framework for gating autonomous actions. Token budgets and confidence scores (`R8_EPISTEMOLOGY` lens) provide further control. |
| **Storage & Retrieval** | `intelligence/`, `registry/`, `archive/` folders, File Search Stores, `archive.py mirror` tool | `analysis_sets.yaml`, `feedback` config in `aci_config.yaml`, `ASSET_INVENTORY.md`, `WORKFLOW_FACTORY.md` | **80%** | The system uses a layered storage approach. `archive/` for history, `.agent/intelligence/` for derived truths (feedback, metrics), and `.agent/registry/` for tasks. The `archive.py mirror` tool syncs to the cloud. `WORKFLOW_FACTORY.md` confirms the existence of indexed File Search (RAG) stores. |

### 2. Dependency & Workflow Graph

This Mermaid diagram illustrates how the existing components can be composed into the Context Refinery workflow.

```mermaid
graph TD
    subgraph A [Phase 1: Ingestion & Mapping]
        direction LR
        SOURCE[Source Code, Archives, Git History] -->|analyzed by| CONFIG
        subgraph CONFIG_FILES [Configuration as Code]
            direction TB
            AS[analysis_sets.yaml]
            SM[semantic_models.yaml]
        end
        CONFIG -->|guides| COLLIDER
    end

    subgraph B [Phase 2: Refinement & Atomization]
        direction TB
        COLLIDER(Collider Pipeline) -->|produces| NODES
        subgraph NODES[Atomized Nodes]
            direction TB
            UN(UnifiedNode Schema)
            EN(EnrichedNode Schema)
            R8(R8 Epistemology Lens for Provenance)
        end
        HSL(Holographic-Socratic Layer) -->|triggers re-analysis| COLLIDER
        SOURCE --. on change .-> HSL
    end
    
    subgraph C [Phase 3: Storage & Indexing]
        direction TB
        NODES -->|stored in| PL[Physical Layer (.json, .yaml)]
        PL -->|indexed by| RAG[RAG Index (File Search Stores)]
    end

    subgraph D [Phase 4: Query & Recompilation]
        direction TB
        QUERY[User Query] --> ACI(ACI Query Router)
        ACI -->|long context path| AS_SELECTOR(Analysis Set Selector)
        AS_SELECTOR -->|compiles context using| AS
        ACI -->|RAG path| RAG_QUERY(RAG Querier)
        RAG_QUERY --> RAG
        subgraph COMPILED_CONTEXT [On-Demand Context Package]
            RAG_QUERY --> CTX_CHUNKS(Retrieved Chunks)
            AS_SELECTOR --> CTX_FILES(Selected Files)
        end
        COMPILED_CONTEXT -->|fed to| LLM
        PROMPTS(prompts.yaml) -->|instructs| LLM
    end

    A --> B --> C --> D
```

### 3. Recommended Implementation Order & Gap Analysis

The foundation is incredibly strong. The primary task is one of integration and formalization rather than creation. Here is a phased plan to build the refinery.

#### Phase 1: Formalize the "Atom" and Ingestion Pipeline
This phase focuses on creating a single, canonical representation for a piece of context.

*   **Action:**
    1.  **Unify the Node Schema:** Define a single, canonical TypeScript/JSON schema for a `RefineryNode`. This will unify the concepts from `semantic_models.yaml` (Atom, Dimension), the `Enriched Node` from `COLLIDER_ARCHITECTURE.md`, and the `R8 Epistemology` lens from `STORAGE_ARCHITECTURE.md`. This schema is the heart of the "Atomization" principle.
    2.  **Formalize the "Collider" as the Refiner:** Officially designate the 12-stage analysis pipeline as the core refinement engine. Its primary output (`unified_analysis.json`) should be a serialized graph of `RefineryNode` objects.
*   **Gaps Filled:** The current schemas are scattered and conceptual. This creates a single, machine-readable source of truth for what a "node" is.

#### Phase 2: Build the Unified Storage & Retrieval Layer
This phase addresses the need for a central, queryable repository of all refined atoms.

*   **Action:**
    1.  **Implement the DataManager API:** The `DATA_LAYER_REFACTORING_MAP.md` provides a perfect blueprint. Create a server-side `DataManager` class that loads all refined nodes from the physical layer (JSON outputs).
    2.  **Provide Indexed Access:** This `DataManager` should provide O(1) lookups as proposed: `getNodeById`, `getNodesByFile`, `getEdgesFrom`, etc.
    3.  **Automate RAG Indexing:** Create a script that uses `analysis_sets.yaml` to automatically create/update the `File Search` stores mentioned in `WORKFLOW_FACTORY.md`. This makes the refined atoms searchable.
*   **Gaps Filled:** This bridges the gap between scattered storage (`.json` files, `intelligence/` folder) and a queryable system. It automates the manual RAG indexing process.

#### Phase 3: Implement the Smart Query Router (ACI)
This phase builds the "on-demand recompiler" front-end.

*   **Action:**
    1.  **Build the ACI Router:** Implement the logic defined in `aci_config.yaml`. This router will take a user query and, based on keywords and complexity indicators, decide which tier to use (`instant`, `rag`, `long_context`).
    2.  **Implement the Hybrid Workflow:** Code the `RAG -> Long Context` flow from `WORKFLOW_FACTORY.md`. A query can first hit the RAG layer (via the `DataManager`) to retrieve top-k nodes, which are then compiled into a long-context prompt using the `positional_strategy` from `analysis_sets.yaml`.
*   **Gaps Filled:** This moves the ACI and Workflow Factory from concepts and documentation into a single, functioning tool.

#### Phase 4: Integrate Continuous Refinement (HSL)
This phase implements the "Delta-First" principle.

*   **Action:**
    1.  **Connect HSL to the Pipeline:** The `HOLOGRAPHIC_SOCRATIC_LAYER.md` describes watch-based triggers. This needs to be connected to the Collider pipeline.
    2.  **Implement Incremental Updates:** The biggest technical challenge. The Collider pipeline must be adapted to support incremental "refinement" of a single file's nodes and updating their relationships in the `DataManager` without re-processing the entire repository. This is critical for efficiency.
    3.  **Add Git History Ingestion:** Create a new processor that can walk git history, run the refinery on past versions of key files (e.g., from `critical_files`), and add temporal context to the nodes (e.g., "this function was refactored on date X").
*   **Gaps Filled:** This addresses the "Delta-First" and "maps the entire corpus... including history" principles, which are currently more conceptual than implemented.

By following this roadmap, you can systematically connect the powerful, existing components into a cohesive and fully-realized Context Refinery. The project's existing documentation and configuration show that the architectural thinking is already 90% complete.

---

## Citations

_No citations provided_
