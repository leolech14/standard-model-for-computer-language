# Research: I have completed the PURPOSE_ONTOLOGY framework which establishes that PURPOSE = f(edges), not f(nod...

> **Date:** 2026-01-23 21:21:30
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:b5b1e371b406ab5c477e5b8baa46cd36894808e54b7fc67b9b6587c0463c0527`
> **Raw JSON:** `raw/20260123_212130_i_have_completed_the_purpose_ontology_framework_wh.json`

---

## Query

I have completed the PURPOSE_ONTOLOGY framework which establishes that PURPOSE = f(edges), not f(node_content). The ACTION vs WORD principle is validated.

Now I need to implement ALL of the following:

1. **Graph-based semantic indexer with NetworkX** - Build call graph, dependency graph, containment graph. Purpose determined by relationships.

2. **Top-down context propagation** - Parent purpose informs child analysis. Inject context when analyzing functions.

3. **Graph metrics calculator** - In-degree (utility), out-degree (orchestrator), clustering (modules), betweenness centrality (critical nodes).

4. **Multi-modal intent sources** - Extract purpose from README, commits, issues, not just code.

CONTEXT: I already have:
- Collider pipeline (full_analysis.py) that extracts nodes and edges
- Tree-sitter engine for AST parsing
- analyze.py for LLM queries
- unified_analysis.json output with nodes/edges

QUESTIONS:
1. What is the optimal implementation order?
2. Should these be separate tools or integrated into Collider pipeline?
3. What's the minimal viable implementation for each?
4. How do I avoid over-engineering while still being state-of-the-art?

Provide a concrete implementation roadmap with file paths and function signatures.

---

## Response

Okay, you've laid out a great vision for a more sophisticated, graph-aware purpose analysis. You're right, shifting the emphasis from node *content* to *connections* is key.

Here's a phased implementation roadmap, considering your existing codebase and the need for a balance between sophistication and practicality:

**Overall Approach:** Integrate these improvements as stages within your existing `full_analysis.py` pipeline. This leverages your existing infrastructure and maintains a single entry point.  The goal is to gradually enrich the information available to the system at each stage, rather than trying to do everything at once.

**Phase 1: Core Graph-Based Semantic Indexing (Focus on Structural Foundation)**

*   **Goal:** Establish basic graph infrastructure for purpose inference.
*   **Implementation Order:** 1. Edges, 2. Nodes, 3.Graph Metrics

    1.  **Create Basic NetworkX Graph (in a new `graph_framework.py`):**
        ```python
        # src/core/graph_framework.py
        import networkx as nx

        def build_nx_graph(nodes: List[Dict], edges: List[Dict]) -> nx.DiGraph:
            """Build NetworkX DiGraph from analysis output."""
            G = nx.DiGraph()
            for node in nodes:
                G.add_node(node['id'], **node) # Copy all node attributes
            for edge in edges:
                G.add_edge(edge['source'], edge['target'], **edge)  # Copy edge attributes
            return G
        ```
        *   Test: Create a simple test case. Ensure a basic graph is created from example nodes/edges.
        *   Minimal: Focus on basic connectivity.  Don't worry about edge weights or attributes yet.
        *   Integrate into existing pipeline: `full_analysis.py`

        ```python
        # src/core/full_analysis.py
        from graph_framework import build_nx_graph
        # Stage 3.1: Graph Generation
        print("\n\U0001F4D6 Stage 3.1: Build NetworkX Graph...")
        G = build_nx_graph(nodes, edges)
        print("✅ Stage 3.1: Success")
        ```

    2.  **Compute In-Degree and Out-Degree:** Modify existing `Node` object or enrich existing dict.
        ```python
        # Add to existing function or a new helper
        def compute_node_degrees(G: nx.Digraph) -> Dict[str, Dict[str, int]]:
            """Computes in-degree and out-degree for each node."""
            return {node: {'in_degree': G.in_degree(node), 'out_degree': G.out_degree(node)} for node in G.nodes}
        ```
        *   Test: Run on simple graph. Confirm accurate in/out-degrees.
        *   Integration: Full analysis pipeline

        ```python
        # src/core/full_analysis.py
        degrees = compute_node_degrees(G)
        for node in nodes:
            if node['id'] in degrees:
                node.update(degrees[node['id']])  # update the existing node object
        ```

**Phase 2: Top-Down Context Propagation (Information Passing)**

*   **Goal:** Implement basic dependency graph analytics AND top-down context passing to low-confidence components.
*   **Implementation Order:** 1. Code-Level, 2. Graph-Level

    1.  **Implement Propagate with Breadth-First Search (BFS):**
        ```python
        # src/core/graph_framework.py
        def propagate_context(
            G: nx.DiGraph,
            root_nodes: List[str],
            context: Dict,
            max_depth: int = 10  # Prevent infinite loops
        ) -> Dict:
          """Propagate context via BFS from root nodes downstream."""
          node_info = {}
          queue = deque([(node, 0) for node in root_nodes]) # (node_id, depth)
          visited = set() # For loop detection
          while queue:
              curr, depth = queue.popleft() # Pop from left = queue
              # Loop detection and depth limiter
              if curr in visited or depth > max_depth: continue

              # Check seen
              visited.add(curr)
              
              # Access the .nodes() metadata store using string as intended
              node_data = G.nodes[curr]

              # Create metadata
              if curr not in node_info:
                node_info[curr] = { **node_data, **context }
              else:
                node_info[curr] = { **node_data, **node_info[curr], **context }
              
              # Add adjacent nodes for further enrichment
              neighbors = G.successors(curr)
              for neighbor in neighbors:
                  queue.append((neighbor, depth+1))
                  # Propagate context
                  node_info[neighbor] = {
                      **G.nodes[neighbor],
                      **node_info[curr]
                  }
          return node_info # { id: all combined information }
        ```

        *   Test: Create a small test graph and confirm that context is propagated correctly. Add a cycle into your test to make sure that algorithm does not stall!
        *   Integration: in `full_analysis.py`

        ```python
        # src/core/full_analysis.py
        if not G:
          return
        from graph_framework import propagate_context
        # Get the important root notes to spread from
        important_node_ids = {node['id'] for node in analysis_results["nodes"] if node["role"] != "Unknown"}
        # Merge that information on the graph:
        enhanced_graph = propagate_context(G, important_node_ids, {}, 2)

        # Then add the enhanced information back
        for node in analysis_results["nodes"]:
            key = node.get('id')
            node_details = enhanced_graph.get(key)
            if node_details:
              node["enriched"] = "graph" # Prove that algo did work
        ```

    2.  **Create and Utilize a Graph-level Store:** Build on previous step.

        ```python
        # src/core/full_analysis.py

        ## Build quick role maps to extract to graph information
        all_classes   = { id for (id, node) in enhanced_graph.items() if node.symbol_kind == "class" }

        for k, node in enhanced_graph.items():
            if 'all_classes' in node:
              continue

            if node.symbol_kind == "function":
              related = []
              # Search if calling a known class
              for _target in graph.successors(k): # Access to data only here, otherwise, readOnly!
                  if _target in all_classes: # O(1) verification
                    related.append(_target.id)
              # Add graph information
              node['related_classes'] = related
        ```

        *   Test: Check to verify that all the proper links are present in your new nodes.
        *   Then: Verify that the output to the prompt/call has added information.
        *   This will take time to validate - suggest small batches
        *   At this step - verify your prompt is actually using this information!

**Phase 3: Advanced Metric Analysis (Quantifying Purpose)**

*   **Goal:** Measure code behavior
*   **Implementation Order:** Start with centralization/degree and then betweenness/page rank, then others.

    1.  **Implement Base Graph Metrics.** Start in a new `graph_metrics.py` (focus here on low-hanging fruit).
        ```python
        # src/core/graph_metrics.py
        import networkx as nx

        def get_degree_centrality(G: nx.DiGraph, node_id: str):
          return G.degree(node_id) # Can be split in and out if needed
        ```

        *Test and confirm this data!*
        *  Write simple unit test cases for each metric.
        *  Confirm results via debugging (e.g., `print` statements) on known graphs

    2.  **Integrate New Information into graph framework:**
        *   Pull existing calculations to new place.
        ```python
        # src/core/graph_framework.py
        from graph_metrics import get_degree_centrality

        def build_graph():
          degrees = { node:get_degree_centrality(G, node)}
        ```
        *   Add these metrics into the graph build process.

    3.  **Apply the above information to Prompts or Decisions.** This is more of a project decision, as it changes what we call an "Action" and "Value."

**Phase 4: Multimodal Intent Sources (Beyond the Code)**

*   **Goal:** Enrich purpose with data from READMEs, commit messages, and issue trackers (if accessible).

    1.  **Create Data Extractors:** Create simple functions to extract relevant text from these sources:
        *   `extract_readme_text(repo_path)`
        *   `extract_commit_messages(repo_path, num_commits=100)`
        *   `extract_issue_titles(repo_path, num_issues=50)`
    2.  **Create a method to merge the code model with natural language text**

**General Notes:**

*   **Focus on Concrete Steps:** Each phase should have clear, achievable goals.
*   **Iterate:** Test frequently, get feedback.

By breaking the work into phases, you can demonstrate value more quickly and refine the solution as you learn more about the specific challenges of your codebase.

---

## Citations

_No citations provided_
