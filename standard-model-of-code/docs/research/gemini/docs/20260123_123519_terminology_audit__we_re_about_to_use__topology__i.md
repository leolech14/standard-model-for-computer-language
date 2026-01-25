# Research: TERMINOLOGY AUDIT: We're about to use 'TOPOLOGY' in the Survey/Codome Definition module to describe ...

> **Date:** 2026-01-23 12:35:19
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:73a848c9df7cb454e2530ca6ce7800901199a3cd5a92d45964e9ce6d27729ea7`
> **Raw JSON:** `raw/20260123_123519_terminology_audit__we_re_about_to_use__topology__i.json`

---

## Query

TERMINOLOGY AUDIT: We're about to use 'TOPOLOGY' in the Survey/Codome Definition module to describe project structure (Monolith vs Monorepo vs Microservices).

PROBLEM: We already use 'topology' elsewhere in the codebase:
- topology_reasoning.py uses it for GRAPH topology (Star, Mesh, Islands, Layers)
- The visualization shows topological patterns of code relationships

QUESTION: Is using 'TOPOLOGY' for project structure (Monolith/Monorepo/Microservices) the RIGHT term, or will it create AMBIGUITY?

If ambiguous, what's the CORRECT term for:
1. Graph shape analysis (currently 'topology') - nodes and edges forming patterns
2. Project structure type (proposed 'topology') - how the repo is organized

We need ZERO ambiguity. One term, one meaning.

Suggest precise terminology with clear definitions.

---

## Response

**VERDICT: YES, it creates dangerous ambiguity.**

You should **NOT** use `TOPOLOGY` for project structure (Monolith/Monorepo).

Based on your codebase (`full_analysis.py`, Stage 10), `TOPOLOGY` is already strictly defined as a **Graph Theory** term describing the shape of connectivity (Star, Mesh, Islands). Overloading this term will cause confusion between "How the repo is organized on disk" (Monorepo) and "How the atoms connect in the graph" (Mesh).

Here is the precise terminology strategy to eliminate ambiguity:

---

### 1. The Conflict (Evidence)
In `src/core/full_analysis.py` (lines 1182-1188), you currently have:
```python
# Stage 10: Visual Topology Analysis
topo = TopologyClassifier()
topology_result = topo.classify(nodes, edges)
full_output['kpis']['topology_shape'] = topology_result.get('shape', 'UNKNOWN')
```
And in lines 640-650, nodes are assigned a `topology_role` (hub, root, leaf).

If you introduce "Topology" to mean "Monorepo", a developer querying the system might ask: *"What is the topology?"*
*   **Answer A:** "It's a Monorepo." (Project Level)
*   **Answer B:** "It's a Mesh with high clustering." (Graph Level)
*   **Result:** Cognitive failure.

---

### 2. The Solution: Terminology Split

Keep **TOPOLOGY** for the graph. Use **ARCHETYPE** for the project structure.

#### A. Graph Shape Analysis → Keep "TOPOLOGY"
This is the correct mathematical term for the arrangement of nodes and edges.
*   **Definition:** The layout of connections and flow between code atoms.
*   **Values:** `Star`, `Mesh`, `Bus`, `Islands`, `Layered_DAG`.
*   **Context:** Used in `topology_reasoning.py` and visualization layers.
*   **Code Reference:** `full_analysis.py` lines 1180+.

#### B. Project Structure → Adopt "ARCHETYPE"
An archetype implies the fundamental model or pattern from which the project is derived. It describes the physical/deployment organization.
*   **Definition:** The high-level deployment and organizational strategy of the repository.
*   **Values:** `Monolith`, `Monorepo`, `Microservice`, `Library`, `Polyglot_Container`.
*   **Context:** Survey/Codome Definition module.

---

### 3. Implementation Guide

Here is how to structure your data models to reflect this separation cleanly.

#### In `Survey/Codome Definition`:
Do not use `project_topology`. Use `project_archetype`.

```python
@dataclass
class ProjectIdentity:
    """The high-level identity of the codebase."""
    root_path: str
    
    # TERMINOLOGY FIX: Use Archetype, not Topology
    archetype: str  # 'monolith', 'monorepo', 'microservices'
    
    languages: List[str]
    frameworks: List[str]
```

#### In `UnifiedAnalysisOutput` (src/core/unified_analysis.py):
Update the output schema to distinguish the three layers of structure:

1.  **Archetype** (Physical/Repo structure)
2.  **Architecture** (Logical Design Patterns)
3.  **Topology** (Graph Connectivity Shape)

```python
@dataclass
class UnifiedAnalysisOutput:
    # ... existing fields ...

    # 1. PHYSICAL / ORG STRUCTURE
    archetype: Dict[str, Any] = field(default_factory=lambda: {
        "type": "monolith",  # or monorepo, etc.
        "confidence": 0.0,
        "components": []     # e.g., list of packages in monorepo
    })

    # 2. LOGICAL DESIGN PATTERNS (Already exists in your code)
    architecture: Dict[str, Any] = field(default_factory=lambda: {
        "detected_patterns": [], # ["DDD", "MVC"]
        "layer_violations": []
    })
    
    # 3. GRAPH CONNECTIVITY SHAPE (Computed in Stage 10)
    topology: Dict[str, Any] = field(default_factory=lambda: {
        "shape": "mesh",     # or star, islands
        "connectivity_score": 0.0,
        "bottlenecks": []
    })
```

### Summary
*   **TOPOLOGY** = The **Shape** of the Graph (The "How it connects").
*   **ARCHETYPE** = The **Form** of the Project (The "What it is").

Use **ARCHETYPE** for Monolith/Monorepo.

---

## Citations

_No citations provided_
