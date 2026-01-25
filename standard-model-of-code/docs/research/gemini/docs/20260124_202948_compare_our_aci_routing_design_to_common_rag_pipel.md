# Research: Compare our ACI routing design to common RAG pipeline patterns

> **Date:** 2026-01-24 20:29:48
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:95e1d7ff213869187aec31da71a5bb282b0eebbd3b50fb18f57064cff38cd671`
> **Raw JSON:** `raw/20260124_202948_compare_our_aci_routing_design_to_common_rag_pipel.json`

---

## Query

Compare our ACI routing design to common RAG pipeline patterns

---

## Response

Based on the `context-management/docs/ACI_DATASET_MANAGEMENT.md` and `WORKFLOW_FACTORY.md` files, here is a detailed comparison between the **ACI (Adaptive Context Intelligence)** routing design and **Common RAG (Retrieval-Augmented Generation)** patterns found in the industry.

### Executive Summary

**Common RAG** is typically **Probabilistic and Chunk-Based**. It relies on converting queries to vectors, finding similar text chunks, and feeding them to an LLM. It optimizes for *retrieval recall*.

**ACI Routing** is **Deterministic and Curriculum-Based**. It treats the context window as a finite resource to be engineered. It optimizes for *reasoning performance* by selecting entire architectural sets ("Curriculums") and positioning them strategically based on the LLM's attention span.

---

### 1. Comparative Architecture Matrix

| Feature | Common RAG Pattern | ACI Routing Design |
| :--- | :--- | :--- |
| **Unit of Retrieval** | **Text Chunks** (e.g., 500-1000 tokens). | **Whole Files / Defined Sets** (e.g., "pipeline" set = 120k tokens). |
| **Selection Logic** | **Vector Similarity** (Cosine distance). "Find text that looks like the query." | **Semantic Graph Traversal** + **Intent Classification**. "Find the architectural dependencies for this intent." |
| **Tiering** | Usually Single-Tier (Retrieval $\to$ Answer). | **4-Tier Router:** Instant (T0) $\to$ RAG (T1) $\to$ Long Context (T2) $\to$ Web (T3). |
| **Context Strategy** | **Stuffing**: Fills context until limit or Top-K. | **Sandwiching**: Places critical files at Start/End to combat U-Shaped attention loss. |
| **Latency/Cost** | Uniform (depends on retrieval speed). | **Variable**: T0 is instant/free; T2 is slow/expensive but deep. |
| **Data Source** | Vector Database (Embeddings). | **Live Codebase** + **Standard Model Graph** + **Cached Truths** (`repo_truths.yaml`). |

---

### 2. Key Differentiators of ACI

#### A. The "Curriculum Compiler" Approach
Common RAG asks: *"What data is similar to this query?"*
ACI asks: *"What is the optimal dataset required to solve this problem?"*

In `ACI_DATASET_MANAGEMENT.md`, ACI constructs a "Curriculum" using:
1.  **Set Resolution**: Expanding logical names (e.g., `architecture_review`) into specific file patterns.
2.  **Budgeting**: It calculates `max_tokens` based on the intent complexity (e.g., "Guru" tier = 50k tokens, "Archaeologist" tier = 200k tokens).
3.  **Integrity**: It prioritizes keeping whole files together rather than shredding them into chunks, preserving the "Global Topology" necessary for architectural reasoning.

#### B. Tier 0: The "Anti-AI" Optimization
Common RAG systems send almost every query to the LLM.
ACI implements a **Tier 0 (Instant)** layer:
*   **Mechanism:** Loads `repo_truths.yaml` (Cached Facts).
*   **Trigger:** Regex patterns like "how many files", "count of *".
*   **Result:** Returns an answer in <100ms with **0 tokens** consumed.
*   **Why it matters:** It prevents wasting expensive reasoning compute on static facts.

#### C. Graph-Based Semantic Matching
While "GraphRAG" is emerging in the industry, ACI uses a specific **Standard Model of Code** graph:
*   It traverses edges defined by code physics: `UPSTREAM` (inherits, implements) and `DOWNSTREAM` (calls, imports).
*   It calculates **Semantic Distance** in an 8-dimensional space (Dimensions D1-D8 in the Standard Model), rather than just embedding distance.
*   *Example:* If you ask about "Repositories," ACI identifies the `Retrieve` purpose ($\pi_2$) and the `Infrastructure` layer to select the correct files, even if the text doesn't strictly match the keywords.

#### D. The U-Shaped Attention Fix
Common RAG often dumps retrieval results into the middle of the prompt.
ACI explicitly manages **Context Positioning**:
*   **Critical Files:** Placed at the **START** and **END** of the context window.
*   **Supporting Files:** Placed in the "Lost-in-Middle" zone.
*   This creates a "Sandwich Strategy" ensuring the LLM retains the most vital architectural constraints while processing the details.

---

### 3. Workflow Decision Tree (ACI vs. Standard)

**User Query:** *"Why is the user login failing?"*

**Standard RAG Flow:**
1.  Embed query.
2.  Retrieve top 5 chunks containing "user", "login", "fail".
3.  Chunks might be from docs, old tests, or random comments.
4.  **Result:** LLM guesses based on fragments.

**ACI Routing Flow (from `WORKFLOW_FACTORY.md`):**
1.  **Query Analyzer:** Detects Intent=`DEBUG`, Complexity=`MODERATE`, Scope=`INTERNAL`.
2.  **Tier Router:** Maps (DEBUG, MODERATE, INTERNAL) $\to$ **Tier 2 (Long Context)**.
3.  **Semantic Matcher:** Identifies "User Login" relates to `AuthService` (Logic) and `UserRepository` (Data).
4.  **Graph Traversal:** Pulls `AuthService`, `UserRepository`, AND their immediate upstream interfaces.
5.  **Set Resolution:** Compiles these full files into a coherent dataset.
6.  **Result:** LLM has the full causal chain of the login logic and can trace the execution path.

### 4. Summary of Advantages

| Scenario | Winner | Reason |
| :--- | :--- | :--- |
| **"How many python files are there?"** | **ACI (Tier 0)** | Zero cost, instant, 100% accurate (via cache). |
| **"Where is the retry logic?"** | **Common RAG** | Needle-in-haystack search is faster via vector/keyword search. (ACI delegates this to its own Tier 1). |
| **"Review the auth architecture."** | **ACI (Tier 2)** | RAG fails at holistic review because it only sees chunks. ACI loads the full "Curriculum". |
| **"Write a new feature."** | **ACI (Tier 2)** | Requires understanding global constraints (Antimatter Laws) injected by ACI. |

### Conclusion

ACI is not just a retrieval system; it is a **Context Engineering Engine**. It acknowledges that LLMs are reasoning engines constrained by token limits and attention spans, and it optimizes the input "dataset" to maximize reasoning quality, whereas common RAG optimizes primarily for retrieval relevance.

---

## Citations

_No citations provided_
