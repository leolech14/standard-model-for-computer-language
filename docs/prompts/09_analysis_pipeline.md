# MEGAPROMPT 09: ANALYSIS PIPELINE ARCHITECTURE

## Context
To populate the 8D classification + edge graph, a multi-stage analysis pipeline is needed.

## Your Task
Design the dependency-ordered analysis pipeline.

## Instructions

1. **Pipeline Stages** (ordered by dependency):
   ```
   1. AST Parsing (source → tree)
   2. Symbol Resolution (tree → named entities)
   3. Call Graph Construction (entities → calls edges)
   4. Import Graph Construction (files → imports edges)
   5. Type Inference (entities → types)
   6. Containment Graph (all → structural edges)
   7. D1 Classification (entities → atoms)
   8. D2-D8 Classification (entities → dimensions)
   9. Role Assignment (entities → roles)
   10. Edge Enrichment (add semantic/temporal edges)
   11. Confidence Aggregation
   12. Graph Validation
   ```

2. **For Each Stage**:
   - **Inputs**: What data is required?
   - **Outputs**: What is produced?
   - **Tools/Algorithms**: Tree-sitter? Call graph algorithm? etc.
   - **Failure Modes**: What can go wrong? (e.g., unparseable file)
   - **Fallbacks**: What to do on failure? (skip? estimate? LLM fallback?)

3. **Parallelization**:
   - Which stages can run in parallel?
   - Dependency DAG visualization

4. **Incremental Updates**:
   - If a single file changes, what re-runs?
   - Cache invalidation strategy

## Expected Output
- Pipeline stage table
- Dependency DAG
- Failure/fallback matrix
- Incremental update protocol
