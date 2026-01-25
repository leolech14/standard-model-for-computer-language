# Research: How does ACI select datasets for queries? List all available analysis sets and explain the routing m...

> **Date:** 2026-01-24 22:08:39
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:8d885dd5ab2c0f2846a6d99eeadcaf13cffb7572c90b7d37e3f2649f32ad435a`
> **Raw JSON:** `raw/20260124_220839_how_does_aci_select_datasets_for_queries__list_all.json`

---

## Query

How does ACI select datasets for queries? List all available analysis sets and explain the routing matrix.

---

## Response

Based on the `context-management/docs/ACI_DATASET_MANAGEMENT.md` and related documentation, here is the breakdown of how the Adaptive Context Intelligence (ACI) system selects data, the available sets, and the routing logic.

### 1. How ACI Selects Datasets

ACI treats context selection as a data engineering problem rather than a simple retrieval task. It uses a 4-step pipeline to "compile" a curriculum for the AI:

1.  **Query Analysis (The Profiler)**
    The system first profiles the user query to determine three factors:
    *   **Intent:** (e.g., ARCHITECTURE, DEBUG, TASK, COUNT).
    *   **Complexity:** Simple (<3 keywords), Moderate, or Complex (>6 keywords).
    *   **Scope:** Internal (repo only), External (world knowledge), or Hybrid.

2.  **Semantic Graph Matching (The Locator)**
    It maps the query against the "Standard Model of Code" graph using 8 dimensions (Role, Layer, etc.).
    *   It calculates **Semantic Distance** to find relevant code atoms.
    *   It performs **Edge Traversal** (Upstream/Downstream) to find dependencies and dependents.
    *   It determines **Context Flow**: Is the context "Laminar" (coherent/local) or "Turbulent" (scattered)?

3.  **Set Resolution & Merging**
    If the routing decision points to Long Context (Tier 2), ACI resolves named sets defined in `analysis_sets.yaml`.
    *   **Composition:** It expands `includes` (e.g., `architecture_review` includes `pipeline` + `classifiers`).
    *   **Token Budgeting:** It applies a `max()` aggregation strategy on token limits (not a sum) to ensure headroom.
    *   **Positioning:** It applies a "Sandwich Strategy," placing critical files at the very beginning and very end of the context window to combat the LLM "Lost-in-Middle" effect.

4.  **Agent Context Injection**
    If the intent is `TASK`, the system automatically injects the `.agent/` context (kernel, protocols, memory) regardless of the specific code files selected.

---

### 2. Available Analysis Sets

Based on the configuration files and documentation references provided, the following sets are defined or referenced in the system:

| Set Name | Description / Contents | Token Budget |
| :--- | :--- | :--- |
| **`architecture_review`** | Full architectural overview. Includes `pipeline`, `classifiers`, and `constraints`. Uses "sandwich" positioning. | 200k (Hard Cap) |
| **`pipeline`** | Core analysis logic files (e.g., `full_analysis.py`). | 120k |
| **`classifiers`** | Logic for atom/role classification (`src/core/classification/*.py`). | 80k |
| **`constraints`** | System rules and invariants (`schema/constraints/*.yaml`). | 50k |
| **`brain`** | AI tools and configuration (Brain hemisphere). | N/A (Dynamic) |
| **`theory`** | Theoretical documentation (`THEORY.md`, etc.). | ~50-60k |
| **`schema`** | JSON schemas defining atoms, roles, and dimensions. | N/A |
| **`agent_tasks`** | Active tasks from `.agent/registry`. | N/A |
| **`agent_kernel`** | Core agent protocols (`AGENT_KERNEL.md`). | ~2k |
| **`agent_full`** | Complete agent context including memory and intelligence. | High |

*Note: Sets can be dynamically merged. For example, ACI may generate a temporary set containing [`agent_tasks`, `agent_kernel`, `pipeline`] for a specific request.*

---

### 3. The Routing Matrix

The **Tier Router** determines *how* the query is answered based on the `[Intent × Complexity × Scope]` profile. This prevents wasting tokens on simple queries or under-powering complex ones.

#### The Matrix Logic

| Intent | Complexity | Scope | **Tier Selected** | **Mechanism** |
| :--- | :--- | :--- | :--- | :--- |
| **COUNT** | SIMPLE | INTERNAL | **TIER 0 (Instant)** | Returns cached facts from `repo_truths.yaml`. Zero tokens used. |
| **LOCATE** | SIMPLE | INTERNAL | **TIER 1 (RAG)** | Performs vector/keyword search. Returns citations. (~1k tokens). |
| **DEBUG** | MODERATE | INTERNAL | **TIER 2 (Long Context)** | Loads specific file clusters for reasoning. (50k-150k tokens). |
| **ARCHITECTURE**| ANY | INTERNAL | **TIER 2 (Long Context)** | Loads broad structural context. (Up to 200k tokens). |
| **TASK** | ANY | ANY | **TIER 2 (Long Context)** | Injects Agent context + relevant code. |
| **RESEARCH** | ANY | EXTERNAL | **TIER 3 (Perplexity)** | Performs live web search via Perplexity API. |

#### Tier Performance Reference

*   **Tier 0 (Instant):** <100ms, $0 cost. (e.g., "How many python files are there?")
*   **Tier 1 (RAG):** ~5s, Low cost. (e.g., "Where is the `UnifiedNode` class defined?")
*   **Tier 2 (Long Context):** ~60s, High cost ($0.10-$0.40). (e.g., "Refactor the semantic matcher to support 12 dimensions.")
*   **Tier 3 (Perplexity):** ~30s, Medium cost. (e.g., "What are the latest best practices for tree-sitter in 2026?")

---

## Citations

_No citations provided_
