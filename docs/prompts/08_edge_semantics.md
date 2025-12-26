> **EPISTEMIC STANCE**: This prompt validates a MAP, not the territory. Canonical sets (167 atoms, 33 roles, 8 dimensions) are *working sets*, not claims of totality. Finding gaps is expected and valuable. Unknown is first-class. All claims are postulates with validation obligations.

---

# MEGAPROMPT 08: EDGE SEMANTICS & GRAPH SCHEMA

## Context
Standard Code defines 6 edge families:
1. Structural (contains, is_part_of)
2. Dependency (calls, imports, uses)
3. Inheritance (inherits, implements, mixes_in)
4. Semantic (is_a, has_role, serves, delegates_to)
5. Temporal (initializes, triggers, disposes, precedes)
6. (possibly more)

## Your Task
Define a rigorous graph schema with full semantics.

## Instructions

1. **For Each Edge Type**:
   - **Definition**: Precise meaning
   - **Source/Target Constraints**: What entity types can be connected?
   - **Properties**: weight, confidence, static/dynamic, etc.
   - **Inverse**: What's the reverse edge? (e.g., calls ↔ called_by)
   - **Transitivity**: Is it transitive? (e.g., contains is transitive)
   - **Composability**: Can edges combine? (e.g., inherits + implements = mixed_inheritance)

2. **Extraction Method**:
   - Static analysis: AST-based
   - Dynamic analysis: Runtime tracing
   - Inference: Graph-based propagation

3. **Validation Checks**:
   - Inverse consistency: If A→B exists, B→A exists (for symmetric edges)
   - Transitivity closure: If enabled, verify closure
   - Level constraints: Contains only goes higher→lower

4. **Schema Language**:
   - Propose a formal schema (JSON Schema, Cypher constraints, etc.)
   - Tool to validate graph against schema

## Expected Output
- Edge schema document (all edge types with full metadata)
- Extraction method per edge
- Validation query set
- Schema definition file
