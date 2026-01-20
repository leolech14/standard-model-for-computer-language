# COLLIDER - THE IMPLEMENTATION
## Standard Model of Code Applied

> **[THEORY.md](./theory/THEORY.md)** describes the map. **This document** describes the tool that uses the map.

---

## THE DICHOTOMY

| | Theory | Implementation |
|---|--------|----------------|
| **Name** | Standard Model of Code | Collider |
| **Purpose** | The map of software territory | The tool that navigates the territory |
| **Question** | *What are the atoms of software?* | *How do we detect them?* |
| **Location** | `docs/theory/THEORY.md` | `src/core/`, `cli.py` |
| **Output** | Conceptual framework | `output_llm-oriented_<project>_<timestamp>.json`, `output_human-readable_<project>_<timestamp>.html` |

---

# PART I: QUICK START

## Installation

```bash
cd standard-model-of-code
pip install -e .
```

## Basic Usage

```bash
# Full analysis of a codebase
./collider full /path/to/repo

# With 3D visualization
./collider viz --3d /path/to/repo
cd collider_output && ./start.sh
```

## Output

The output bundle is two files in `<output_dir>`:

- `output_llm-oriented_<project>_<timestamp>.json` (LLM-oriented knowledge)
- `output_human-readable_<project>_<timestamp>.html` (human-readable report + graph)

---

# PART II: THE OUTPUT STRUCTURE

## What The Brain Download Contains

The Brain Download is embedded in the LLM JSON output and rendered inside the HTML report.

| Section | What It Tells You |
|---------|-------------------|
| **IDENTITY** | Node count, edge count, dead code % |
| **CHARACTER (RPBL)** | 4-dimensional profile (Responsibility, Purity, Boundary, Lifecycle) |
| **ARCHITECTURE** | Type distribution, layer breakdown |
| **HEALTH STATUS** | Traffic-light indicators |
| **ACTIONABLE IMPROVEMENTS** | Prescriptive recipes with steps |
| **VISUAL REASONING** | Topology shape (Star, Mesh, Islands) |
| **DOMAIN CONTEXT** | Inferred business domain |

---

# PART III: STORAGE ARCHITECTURE

The Collider's output operates across **three distinct but interconnected layers**:

1. **Physical Layer** - Files on disk (JSON, CSV, databases)
2. **Virtual Layer** - In-memory data structures (graphs, indices, caches)
3. **Semantic Layer** - Meaning and relationships (8D + 8L queryable space)

## Physical Layer: JSON Output

**Primary Location**: `collider_output/output_llm-oriented_<project>_<timestamp>.json`

**Schema**: LLM-oriented bundle (graph + insights)

```json
{
  "meta": {
    "target": "src/core",
    "timestamp": "2025-12-27T...",
    "analysis_time_ms": 1234,
    "version": "4.0.0"
  },
  "counts": {...},
  "ecosystem_discovery": {
    "total_unknowns": 12,
    "ecosystems": {
      "react": {"unknown_count": 4},
      "go": {"unknown_count": 8}
    }
  },
  "kpis": {
    "edge_resolution_percent": 98.4,
    "call_ratio_percent": 42.1,
    "reachability_percent": 96.2,
    "dead_code_percent": 3.8,
    "knot_score": 2.5,
    "topology_shape": "STAR"
  },
  "nodes": [...],
  "edges": [...],
  "topology": {...},
  "semantics": {...},
  "brain_download": "..."
}
```

## Physical Layer: HTML Output

**Primary Location**: `collider_output/output_human-readable_<project>_<timestamp>.html`

This file renders the interactive graph, a live metrics panel (from `kpis`), and the embedded report (`brain_download`) in a single page.

### Visualization Controls (HTML)

See **Part XI: Visualization Architecture** for full control documentation.

Quick reference:
- **Datamaps**: Checkbox filters for node subsets (disabled in File Map view)
- **FILES**: File visualization modes (COLOR/HULLS/CLUSTER/MAP)
- **Expand**: INLINE/DETACH for file-node expansion (in MAP view)

### Node Structure

Each node contains ~100+ fields across 8 dimensions + 8 lenses:

```json
{
  "id": "src/core/file.py::function_name",
  "name": "function_name",
  "kind": "function",
  "file_path": "src/core/file.py",
  "start_line": 42,
  "end_line": 58,

  "dimensions": {
    "D1_WHAT": "QueryFunction",
    "D2_LAYER": "Domain",
    "D3_ROLE": "Query",
    "D4_BOUNDARY": "Internal",
    "D5_STATE": "Stateless",
    "D6_EFFECT": "Pure",
    "D7_LIFECYCLE": "Use",
    "D8_TRUST": 82
  },

  "lenses": {
    "R1_IDENTITY": {...},
    "R2_ONTOLOGY": {...},
    "R3_CLASSIFICATION": {...},
    "R4_COMPOSITION": {...},
    "R5_RELATIONSHIPS": {...},
    "R6_TRANSFORMATION": {...},
    "R7_SEMANTICS": {...},
    "R8_EPISTEMOLOGY": {...}
  }
}
```

### Edge Structure

```json
{
  "id": "edge_12345",
  "source": "src/file1.py::ClassA",
  "target": "src/file1.py::ClassA.method_b",
  "type": "contains",
  "metadata": {
    "line_number": 42,
    "explicit": true
  }
}
```

**Edge Types**: `contains`, `calls`, `imports`, `inherits`, `implements`

### Scaling Characteristics

| Nodes | Edges | JSON Size | Parse Time |
|-------|-------|-----------|------------|
| 5 | 3 | ~10 KB | 416 ms |
| 571 | 3,218 | ~2.8 MB | 1,923 ms |
| ~10,000 | ~50,000 | ~50 MB | ~15 sec |
| ~100,000 | ~500,000 | ~500 MB | ~3 min |

## Virtual Layer: In-Memory Structures

### NetworkX Graph

```python
import networkx as nx

G = nx.DiGraph()
for node in data['nodes']:
    G.add_node(node['id'], **node)
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'], **edge)

# Query capabilities:
# - PageRank: nx.pagerank(G)
# - Betweenness: nx.betweenness_centrality(G)
# - Communities: nx.community.louvain_communities(G)
```

### Index Structures

```python
# Role index (O(1) lookup)
role_index = defaultdict(list)
for node in particles:
    role_index[node['role']].append(node['id'])

# Dimension index
state_effect_index = defaultdict(list)
for node in particles:
    key = (node['dimensions'].get('D5_STATE'),
           node['dimensions'].get('D6_EFFECT'))
    state_effect_index[key].append(node)
```

## Semantic Layer: Queryable Space

Every node exists at a point in 8D space:

```
Node "get_user_by_id" =
  (D1: QueryFunction,
   D2: Domain,
   D3: Query,
   D4: Internal,
   D5: Stateless,
   D6: Pure,
   D7: Use,
   D8: 82%)
```

### Pattern Queries

**Find Cacheable Functions**:
```bash
latest=$(ls -t collider_output/output_llm-oriented_*.json | head -1)
cat "$latest" | jq '
  .nodes | map(select(
    .dimensions.D5_STATE == "Stateless" and
    .dimensions.D6_EFFECT == "Pure"
  ))
'
```

**Security Audit (I/O Write Operations)**:
```bash
latest=$(ls -t collider_output/output_llm-oriented_*.json | head -1)
cat "$latest" | jq '
  .nodes | map(select(
    (.dimensions.D4_BOUNDARY == "Output" or
     .dimensions.D4_BOUNDARY == "I-O") and
    .dimensions.D6_EFFECT == "Write"
  ))
'
```

---

# PART IV: SCHEMA EXTENSIONS

## D9_INTENT (From Popper's World 2)

The programmer's mental intent — what the code is SUPPOSED to do.

```yaml
D9_INTENT:
  values:
    - "Documented"      # Clear docstring/comments explaining intent
    - "Implicit"        # Intent inferred from naming/patterns
    - "Ambiguous"       # Intent unclear
    - "Contradictory"   # Code behavior contradicts documentation
  detection:
    - Check for docstrings/comments
    - Compare docstring semantics to code behavior
    - Flag naming vs behavior mismatches
```

## D10_LANGUAGE (From Ranganathan's Matter Facet)

The programming language/platform — the "matter" of the code.

```yaml
D10_LANGUAGE:
  values:
    - "Python"
    - "TypeScript"
    - "JavaScript"
    - "Java"
    - "Go"
    - "Rust"
    - "C"
    - "C++"
    - "Other"
```

## Complexity Metrics (From Shannon's Entropy)

```yaml
metrics:
  complexity:
    cyclomatic: 5           # McCabe cyclomatic complexity
    cognitive: 8            # Cognitive complexity
    halstead_volume: 245.3  # Halstead metrics
    entropy: 3.2            # Shannon entropy of token distribution

  coupling:
    afferent: 5             # Incoming dependencies (Ca)
    efferent: 3             # Outgoing dependencies (Ce)
    instability: 0.375      # Ce / (Ca + Ce)
    tension: 0.6            # Balance between self-assertive and integrative
```

## DDD Properties

```yaml
ddd:
  is_aggregate_root: boolean
  aggregate_id: string
  bounded_context: string
  invariants:
    - "user_id must be positive"
    - "email must be valid format"
  domain_events:
    - "UserCreated"
    - "UserUpdated"
```

---

# PART V: ANTIMATTER LAWS

Architectural violations that the Collider can detect.

| ID | Name | Description | Severity |
|----|------|-------------|----------|
| AM001 | Layer Skip Violation | Direct dependency from higher to non-adjacent lower layer | ERROR |
| AM002 | Reverse Layer Dependency | Lower layer depending on higher layer | ERROR |
| AM003 | God Class | Class with too many responsibilities (>20 methods or >10 coupling) | WARNING |
| AM004 | Anemic Model | Entity with only getters/setters, no behavior | WARNING |
| AM005 | Bounded Context Violation | Cross-boundary dependency without explicit interface | ERROR |

### Detection Rules

```yaml
AM001:
  detection: "If L(source) - L(target) > 1 for same subsystem"
  examples:
    - "Controller calling Repository directly (skipping Service)"
    - "Interface layer calling Infrastructure directly"

AM002:
  detection: "If L(source) < L(target) for 'imports' edge"
  examples:
    - "Core domain importing Controller"
    - "Repository importing Service"

AM003:
  detection: "methods > 20 OR afferent_coupling > 10 OR files_referring > 15"

AM004:
  detection: "All methods are getters/setters AND no business logic"

AM005:
  detection: "Import across L6 boundary without using defined contract"
```

---

# PART VI: TAU NOTATION

Canonical particle ID format:

```
τ(Type:Role:Layer:Boundary:State:Effect:Lifecycle:Trust)
```

**Examples**:
- `τ(Method:Query:App:IO:SL:R:U:92)` = Method, Query role, Application layer, I-O boundary, Stateless, Read effect, Use phase, 92% confidence
- `τ(Class:Repository:Infra:IO:SF:RW:C:85)` = Class, Repository role, Infrastructure layer, I-O boundary, Stateful, ReadWrite, Create phase, 85%

**Abbreviations**:
| Dimension | Abbreviations |
|-----------|---------------|
| Boundary | Int=Internal, In=Input, Out=Output, IO=I-O |
| State | SF=Stateful, SL=Stateless |
| Effect | P=Pure, R=Read, W=Write, RW=ReadWrite |
| Lifecycle | C=Create, U=Use, D=Destroy |

---

# PART VII: KEY FILES

| File | Purpose |
|------|---------|
| `cli.py` | CLI entry point |
| `src/core/full_analysis.py` | Main pipeline orchestrator |
| `src/core/output_generator.py` | Emits the LLM/HTML output bundle |
| `src/core/brain_download.py` | Generates the embedded brain_download report |
| `src/core/unified_analysis.py` | Base graph analysis (writes unified_analysis.json if run directly) |
| `src/core/graph_analyzer.py` | Graph operations and metrics |
| `src/core/topology_reasoning.py` | Shape classification |
| `src/core/semantic_cortex.py` | Domain inference |
| `src/core/atom_registry.py` | The 94 implemented atoms |
| `schema/atoms.schema.json` | The 200 documented atoms |

---

# PART VIII: DATA PIPELINE

## Pipeline Stages

```
SOURCE CODE ──► EXTRACTION ──► CLASSIFICATION ──► ANALYSIS ──► OUTPUT
    │              │                │                │           │
  Files         AST Parse       Atom Match      Graph Ops    JSON/HTML
                Tree-sitter     LLM Classify    Metrics
```

### Stage 1: Extraction
- **Input**: Source files (*.py, *.js, *.ts, etc.)
- **Tool**: `tree_sitter_extractor.py`, `edge_extractor.py`
- **Output**: Raw AST nodes with location info

### Stage 2: Classification
- **Input**: Raw nodes from extraction
- **Tool**: `atom_classifier.py`, `llm_classifier.py`
- **Output**: Classified entities with atoms/roles

### Stage 3: Unified Analysis
- **Input**: Classified entities + edges
- **Tool**: `unified_analysis.py`, `data_management.py`
- **Output**: Complete graph with metrics

### Stage 4: Output Generation
- **Input**: Analysis results
- **Tool**: `output_generator.py`, `visualize_graph_webgl.py`
- **Output**: JSON + HTML bundle

## Canonical Data Conventions

### ID Format
**Standard**: `file_path::qualified_name` (double-colon)
```python
# Correct
"src/foo.py::MyClass.my_method"

# Legacy (still supported but deprecated)
"src/foo.py:MyClass"
```

### Confidence Scale
**Standard**: Always 0.0 to 1.0 (never 0-100)

**Canonical Rule**: All confidence/probability-like fields (`confidence`, `role_confidence`, `cohesion`, `probability`, etc.) are normalized to 0.0–1.0 in stored data. UI may display as percentage; internal calculations use 0–1.

```python
# Correct
confidence = 0.85
cohesion = 0.72

# Wrong
confidence = 85  # ❌
```

**Legacy Handling**: Any 0–100 values encountered during import are normalized to 0–1 on export. Original values preserved as `*_raw` fields when needed for debugging.

### Validation Rules

| Field | Rule | Severity |
|-------|------|----------|
| `id` | Required, format `file::name` | ERROR |
| `confidence` | 0.0 ≤ x ≤ 1.0 | ERROR |
| `atom` | Format `RING.SUB.TIER` | WARNING |
| Edge `source` | Must exist in graph | ERROR |

---

# PART IX: DEVELOPMENT & TESTING

## Installation

```bash
pip install -e .
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Integration tests only
pytest tests/ -v -k 'integration'

# Skip slow tests
pytest tests/ -v -m 'not slow'

# List without running
pytest tests/ --collect-only
```

## Test Architecture

| Test Type | Location | Purpose |
|-----------|----------|---------|
| **Unit** | `tests/test_*.py` | Component isolation |
| **Integration** | `tests/test_integration.py` | Pipeline verification |
| **Browser** | HTML output → Console | WebGL self-test (23 tests) |

## Self-Analysis

```bash
./collider full src/core --output /tmp/self_check
```

## Test Markers

```python
@pytest.mark.slow           # Skip with -m "not slow"
@pytest.mark.integration    # Integration tests
@pytest.mark.requires_tree_sitter  # Needs tree-sitter
```

---

# PART X: ALTERNATIVE OUTPUT FORMATS

## CSV Export

```bash
latest=$(ls -t collider_output/output_llm-oriented_*.json | head -1)
cat "$latest" | jq -r '
  .nodes[] |
  [.name, .role, .dimensions.D5_STATE, .dimensions.D6_EFFECT] |
  @csv
' > nodes.csv
```

## SQLite Database

```sql
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  name TEXT,
  kind TEXT,
  role TEXT,
  d5_state TEXT,
  d6_effect TEXT,
  confidence REAL,
  lenses_json TEXT
);

CREATE TABLE edges (
  id TEXT PRIMARY KEY,
  source TEXT,
  target TEXT,
  type TEXT
);

CREATE INDEX idx_role ON nodes(role);
CREATE INDEX idx_state_effect ON nodes(d5_state, d6_effect);
```

## PostgreSQL (Production Scale)

```sql
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  name TEXT,
  kind TEXT,
  role TEXT,
  dimensions JSONB,
  lenses JSONB,
  search_vector tsvector
);

CREATE INDEX idx_dimensions_gin ON nodes USING gin(dimensions);
CREATE INDEX idx_search ON nodes USING gin(search_vector);
```

---

# PART XI: VISUALIZATION ARCHITECTURE

## Hierarchical Zoom Model

The 3D visualization implements a **three-level hierarchy**:

```
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 1: FILESYSTEM                                        │
│  Each node = a FILE or FOLDER                               │
│  Edges = imports, dependencies between files                │
├─────────────────────────────────────────────────────────────┤
│  LEVEL 2: FILE BOUNDARIES (Containers)                      │
│  Files as translucent "bubbles" containing atoms            │
│  Can see through to atoms inside                            │
│  COLOR / HULLS / CLUSTER modes                              │
├─────────────────────────────────────────────────────────────┤
│  LEVEL 3: ATOMS (1000+ individual nodes)                    │
│  Functions, classes, methods, variables                     │
│  Full graph with all relationships                          │
└─────────────────────────────────────────────────────────────┘
```

### The "Pop Bubble" Animation

When file boundaries are dissolved:

1. **Initial State**: Atoms clustered within file boundary containers
2. **Transition**: Boundary hulls fade/pop
3. **Physics Equilibrium**: Atoms freed from spatial constraints
4. **Final State**: New equilibrium based on actual relationships (calls, imports)

This reveals the **true topology** — relationships that transcend file organization.

### 2D ↔ 3D Dimension Toggle

The visualization supports smooth animated transitions:

- **3D Mode**: Full spatial exploration, starfield background, depth
- **2D Mode**: Flat disk projection, cleaner for screenshots/analysis

### Toggle Controls

| Button | Function |
|--------|----------|
| **FILES** | Toggle file visualization mode |
| **FLOW** | Markov chain view - edge thickness by transition probability |
| **EDGE** | Cycle edge coloring modes (TYPE/RESOLUTION/WEIGHT/CONFIDENCE) |
| **STARS** | Toggle background starfield (avoid confusion with nodes) |
| **2D/3D** | Animated dimension transition |
| **REPORT** | Show/hide embedded brain download |

#### File Visualization Sub-Controls

When **FILES** is active, additional controls appear:

| Sub-Button | Function |
|------------|----------|
| **COLOR** | Color atoms by their parent file |
| **HULLS** | Draw convex hull boundaries around file groups |
| **CLUSTER** | Force-cluster atoms by file (physics constraint) |
| **MAP** | Switch to file-node view (files become nodes) |

#### File Map Expand Controls

When **MAP** is active (file-node view):

| Sub-Button | Function |
|------------|----------|
| **INLINE** | Expand file node in place to show atoms |
| **DETACH** | Expand and detach file node for isolated view |

### Starfield Disambiguation

The cosmic starfield creates depth but can confuse visual parsing:

- **Stars**: Tiny, white, static, very distant (z-depth 5000)
- **Nodes**: Larger, colored, interactive, clustered in center

Use **STARS** toggle when you need clean screenshots or reduced visual noise.

### Smart Text Placement System (v1)

> **Status**: Implemented

The visualizer uses **HudLayoutManager** for intelligent collision-avoidance:

**Features:**
- Rect-based collision detection using `getBoundingClientRect()`
- Tracks occupied regions: sidebar (when locked/open/hover), header, stats, metrics, bottom dock
- File panel dynamically placed in best available position (4-corner candidates)
- Smooth "dance" animation: `transition: left/top 150ms ease-out`
- Throttled reflow (50ms + RAF) to avoid layout thrashing

**Priority System:**
1. Sidebar (when locked/open/hover) - highest priority, defines exclusion zone
2. Top-center stats - fixed position
3. Metrics panel (top-right) - fixed position
4. Bottom dock - fixed position
5. File panel - dynamic placement, yields to all fixed elements

**Reflow Triggers:**
- Window resize
- Sidebar lock/unlock toggle
- Sidebar hover enter/leave
- File panel visibility change (node hover, FILES mode toggle)

---

# APPENDIX: THE THREE-LAYER PRINCIPLE

The output storage mirrors the theoretical Three Layers:

| Layer | Physical | Virtual | Semantic |
|-------|----------|---------|----------|
| **What** | Files on disk | In-memory structures | Queryable meaning |
| **Format** | JSON, CSV, SQLite | Python dicts, NetworkX | 8D coordinate space |
| **Question** | "Where is it?" | "How do I access it?" | "What does it mean?" |
| **Persistence** | Durable | Ephemeral | Derived |

All three are necessary:
- Physical for persistence
- Virtual for performance
- Semantic for intelligence

---

**Last Updated**: 2026-01-15
**Schema Version**: 3.2.0
