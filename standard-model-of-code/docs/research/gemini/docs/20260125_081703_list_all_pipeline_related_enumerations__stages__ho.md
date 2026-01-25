# Research: List ALL pipeline-related enumerations: stages (how many?), edge types, topology shapes, codome boun...

> **Date:** 2026-01-25 08:17:03
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:7745593ed844b70d7afc4f7f7304e4581d8dcd416da2be72320449cbaf56b640`
> **Raw JSON:** `raw/20260125_081703_list_all_pipeline_related_enumerations__stages__ho.json`

---

## Query

List ALL pipeline-related enumerations: stages (how many?), edge types, topology shapes, codome boundaries, metrics computed. Be exhaustive.

---

## Response

Based on the provided codebase context, here is the exhaustive list of pipeline-related enumerations.

### 1. Pipeline Stages
There are **23 active stages** explicitly instrumented with `StageTimer` in `full_analysis.py` (excluding the skipped Stage 4.5).

*   **Stage 0:** Survey (Pre-Analysis Intelligence)
*   **Stage 1:** Base Analysis
*   **Stage 2:** Standard Model Enrichment
*   **Stage 2.5:** Ecosystem Discovery
*   **Stage 2.7:** Octahedral Dimension Classification
*   **Stage 2.8:** Scope Analysis
*   **Stage 2.9:** Control Flow Metrics
*   **Stage 2.10:** Pattern-Based Atom Detection
*   **Stage 2.11:** Data Flow Analysis (D6:EFFECT)
*   **Stage 3:** Purpose Field
*   **Stage 3.5:** Organelle Purpose (π₃)
*   **Stage 3.6:** System Purpose (π₄)
*   **Stage 4:** Execution Flow
*   **Stage 5:** Markov Transition Matrix
*   **Stage 6:** Knot/Cycle Detection
*   **Stage 6.5:** Graph Analytics
*   **Stage 6.6:** Statistical Metrics
*   **Stage 6.7:** Semantic Purpose Analysis
*   **Stage 6.8:** Codome Boundary Generation
*   **Stage 7:** Data Flow Analysis
*   **Stage 8:** Performance Prediction
*   **Stage 8.5:** Constraint Field Validation
*   **Stage 8.6:** Purpose Intelligence
*   **Stage 9:** Roadmap Evaluation
*   **Stage 10:** Visual Reasoning (Topology)
*   **Stage 11:** Semantic Cortex
*   *(Optional)* **Stage 11b:** AI Insights
*   **Stage 12:** Output Generation

---

### 2. Edge Types & Families
Defined across `edge_extractor.py`, `graph_analyzer.py`, and `full_analysis.py`.

**Primary Edge Types:**
*   `imports` (Module imports)
*   `contains` (Structural parent/child)
*   `calls` (Function/method calls)
*   `inherits` (Class inheritance)
*   `uses` (Attribute access/general usage)
*   `exposes` (Exports/Public API)
*   `decorates` (Decorator usage)
*   `instantiates` (Class instantiation - inferred)
*   `invokes` (Codome boundary inferred calls)

**Edge Families:**
*   `Dependency` (calls, uses, imports, instantiates, invokes)
*   `Structural` (contains)
*   `Inheritance` (inherits)
*   `Semantic` (decorates)
*   `Exposure` (exposes)
*   `Codome` (synthetic boundary edges)

**Edge Resolutions:**
*   `resolved_internal`
*   `external`
*   `unresolved`
*   `relative_import`
*   `ambiguous`
*   `resolved_to_file_no_node`

---

### 3. Codome Boundaries & Disconnection Taxonomy
Defined in `full_analysis.py` to classify why nodes appear disconnected.

**Codome Boundary Types (Synthetic Nodes):**
*   `test_entry` (TestFramework)
*   `entry_point` (RuntimeEntry)
*   `framework_managed` (FrameworkDI)
*   `cross_language` (HTMLTemplate)
*   `external_boundary` (ExternalAPI)
*   `dynamic_target` (DynamicDispatch)

**Disconnection Gap Types:**
*   `isolated` (No incoming or outgoing)
*   `no_incoming` (Has outgoing, no incoming)
*   `no_outgoing` (Has incoming, no outgoing)

**Suggested Actions:**
*   `OK` (Valid disconnection)
*   `CHECK` (Requires verification)
*   `DELETE` (Safe to remove)
*   `REVIEW` (Likely dead code)

---

### 4. Topology & Node Roles
Defined in `full_analysis.py` and `graph_analyzer.py`.

**Topology Roles (Structural):**
*   `orphan` (0 in, 0 out)
*   `root` (0 in, >0 out)
*   `leaf` (>0 in, 0 out)
*   `hub` (High degree connection)
*   `internal` (Standard node)

**Semantic Roles (Purpose-based):**
*   `utility`
*   `orchestrator`
*   `hub`
*   `leaf`

**Architectural Layers (Heuristic):**
*   `domain`
*   `application`
*   `infrastructure`
*   `presentation`
*   `cross_cutting`

---

### 5. Metrics Computed
Comprehensive list of metrics calculated across the pipeline stages.

**Graph & Network Metrics:**
*   `in_degree` / `out_degree`
*   `call_in_degree` / `call_out_degree` (Behavioral only)
*   `betweenness_centrality` (Bottleneck detection)
*   `pagerank` (Importance ranking)
*   `knot_score` (0-10 tangle rating)
*   `cycles_detected`
*   `bidirectional_edges`
*   `graph_density`
*   `avg_fanout`
*   `communities` (Leiden/Louvain counts)

**Code Quality & Complexity:**
*   `cyclomatic_complexity` (and `complexity_rating`)
*   `max_nesting_depth` (and `nesting_rating`)
*   `halstead_volume`
*   `estimated_bugs`
*   `dead_code_percent`
*   `lines_of_code`

**Standard Model (Theoretical):**
*   **RPBL Scores:** Responsibility, Purity, Boundary, Lifecycle
*   **Pi Scores:** π₂ (Molecular), π₃ (Organelle), π₄ (System)
*   **Q-Scores:** Codebase Intelligence quotient
*   **Data Flow:** Mutation count, Side-effect count, Purity score

**Constraints & Architecture:**
*   `antimatter_count` (Tier A violations)
*   `policy_violation_count` (Tier B violations)
*   `signal_count` (Tier C violations)
*   `rho_antimatter` / `rho_policy` (Density metrics)
*   `type_coverage`
*   `ring_coverage`

---

## Citations

_No citations provided_
