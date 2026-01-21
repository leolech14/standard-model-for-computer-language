# COLLIDER.md - The Tool

> Everything about using Collider. Commands, output, architecture, troubleshooting.

---

## 1. COMMANDS

### Primary

| Command | Purpose |
|---------|---------|
| `./collider full <path>` | Complete 12-stage analysis |
| `./collider full <path> --output <dir>` | Custom output directory |
| `./collider full <path> --ai-insights` | With LLM enrichment |

### Graph Analysis

| Command | Purpose |
|---------|---------|
| `./collider graph <json>` | Analyze existing graph |
| `./collider graph <json> --bottlenecks` | Find bottlenecks |
| `./collider graph <json> --shortest-path a:b` | Path between nodes |

### Other

| Command | Purpose |
|---------|---------|
| `./collider viz <json>` | Generate HTML visualization |
| `./collider doctor <path>` | Validate pipeline + output |

### Flags

| Flag | Description |
|------|-------------|
| `--output`, `-o` | Output directory |
| `--ai-insights` | Enable LLM layer |
| `--verbose`, `-v` | Detailed logging |
| `--timing` | Pipeline timing |
| `--verbose-timing` | Per-stage timing |
| `--3d` | 3D visualization |

---

## 2. OUTPUT

### Files Generated

| File | Contents |
|------|----------|
| `unified_analysis.json` | Nodes, edges, metrics |
| `output.md` | Brain Download report |
| `collider_report.html` | Interactive 3D visualization |

### Brain Download Sections

| Section | Contents |
|---------|----------|
| IDENTITY | Node count, edge count, dead code % |
| CHARACTER (RPBL) | Responsibility, Purity, Boundary, Lifecycle |
| ARCHITECTURE | Type distribution, layer breakdown |
| HEALTH STATUS | Traffic-light indicators |
| IMPROVEMENTS | Prescriptive recipes |
| VISUAL REASONING | Topology shape |
| DOMAIN CONTEXT | Inferred business domain |
| AI INSIGHTS | LLM analysis (if enabled) |

### Topology Shapes

| Shape | Description |
|-------|-------------|
| Star | Central hub with spokes |
| Hierarchical | Tree-like structure |
| Mesh | Highly interconnected |
| Islands | Disconnected clusters |
| Layered | Clear architectural layers |

---

## 3. PIPELINE (18 Stages)

| Stage | Name | Produces |
|-------|------|----------|
| 1 | Base Analysis | AST, initial nodes |
| 2 | Standard Model | atom classification |
| 2.5 | Ecosystem Discovery | framework detection |
| 2.7 | Octahedral Dimensions | 8D vectors |
| 3 | Purpose Field | layers |
| 4 | Execution Flow | reachable_set, orphans |
| 5 | Markov Transitions | state matrix |
| 6 | Knot/Cycle Detection | cycles, knots |
| 6.5 | Graph Analytics | centrality, clustering |
| 6.6 | Statistical Metrics | distributions |
| 7 | Data Flow | data movement graph |
| 8 | Performance Prediction | hotspots |
| 8.5 | Constraint Validation | profile checks |
| 9 | Roadmap Evaluation | maturity score |
| 10 | Visual Reasoning | topology shape |
| 11 | Semantic Cortex | high-level patterns |
| 11b | AI Insights (optional) | LLM analysis |
| 12 | Consolidated Output | JSON, HTML, MD |

---

## 4. ARCHITECTURE

### Two-Layer System

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: DETERMINISTIC CORE (The Intelligence)         │
│  • 94 atoms, 4 phases, 16 families                      │
│  • 29 canonical roles                                   │
│  • Layer detection (Domain, Application, Infra, UI)     │
│  • Antimatter detection, RPBL scoring                   │
│  • Dead code detection, topology classification         │
│  STATUS: FULLY IMPLEMENTED                              │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: LLM ENRICHMENT (Optional)                     │
│  • Pattern narratives                                   │
│  • Refactoring suggestions                              │
│  • Risk explanations                                    │
│  PROVIDERS: Vertex AI Gemini, Ollama                    │
│  STATUS: IMPLEMENTED (--ai-insights)                    │
└─────────────────────────────────────────────────────────┘
```

**Key Insight:** Layer 1 IS the intelligence. Layer 2 is amplification.

### Bidirectionality Vision

**Current (Analysis):**
```
Codebase  ══════▶  Collider  ══════▶  Codespace (graph)
```

**Target (Synthesis):**
```
Codebase  ◀══════▶  Collider  ◀══════▶  Codespace (graph)
                                              │
                                         MANIPULATE
```

**Status:** Synthesis NOT YET IMPLEMENTED

### What LLM Receives

| Receives | Does NOT Receive |
|----------|------------------|
| Node counts | Actual source code |
| Metrics | Function implementations |
| Topology shape | File contents |
| Hub names | Business logic |

This is **meta-analysis** — AI analyzing an analysis.

---

## 5. SOURCE FILES

### Core

| Task | File |
|------|------|
| CLI entry | `cli.py` |
| Pipeline orchestrator | `src/core/full_analysis.py` |
| Graph generation | `src/core/unified_analysis.py` |
| Report generator | `src/core/brain_download.py` |
| Atom loader | `src/core/atom_loader.py` |
| Atom classifier | `src/patterns/atom_classifier.py` |
| Role assignment | `src/core/heuristic_classifier.py` |
| Topology classifier | `src/core/topology_reasoning.py` |
| HTML generator | `tools/visualize_graph_webgl.py` |

### Configuration

| Task | File |
|------|------|
| Base atoms (14) | `src/patterns/atoms.json` |
| T0 atoms (42) | `src/patterns/ATOMS_TIER0_CORE.yaml` |
| T1 atoms (21) | `src/patterns/ATOMS_TIER1_STDLIB.yaml` |
| T2 atoms (17) | `src/patterns/ATOMS_TIER2_ECOSYSTEM.yaml` |
| Role definitions | `schema/fixed/roles.json` |

### Visualization

| Task | File |
|------|------|
| HTML template | `src/core/viz/assets/template.html` |
| Styles | `src/core/viz/assets/styles.css` |
| Main application | `src/core/viz/assets/app.js` |
| Control Bar | `src/core/viz/assets/modules/control-bar.js` |
| File Visualization | `src/core/viz/assets/modules/file-viz.js` |
| Edge System | `src/core/viz/assets/modules/edge-system.js` |
| Animation | `src/core/viz/assets/modules/animation.js` |

---

## 6. VISUALIZATION CONTROLS

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `M` or `` ` `` | Toggle Control Bar |
| `Escape` | Close panels, collapse Control Bar |
| `I` | Show info for selected nodes |
| `W` | Cycle wave pattern |
| `Click` | Select node |
| `Shift+Click` | Multi-select |
| `Ctrl/Cmd+Click` | Toggle selection |

### Control Bar (Visual Mapping)

The **Control Bar** is a persistent UI at the bottom of the screen for dynamic visual mapping.

**Access:** Press `M` or backtick `` ` ``

#### Scope Options

| Scope | Description |
|-------|-------------|
| Selected Nodes | Apply to current selection |
| All Nodes | Apply to entire graph |
| Group X | Apply to saved node group |

#### Source Fields (MAP from)

| Category | Fields |
|----------|--------|
| Structural | `token_estimate`, `line_count`, `size_bytes`, `code_lines`, `complexity_density`, `cohesion` |
| Temporal | `age_days` |
| Graph | `in_degree`, `out_degree` |
| Categorical | `tier`, `ring`, `layer`, `role`, `format_category`, `effect` |
| Boolean | `is_test`, `is_config`, `is_stale` |

#### Target Properties (MAP to)

| Category | Properties |
|----------|------------|
| Appearance | `nodeSize`, `hue`, `saturation`, `lightness`, `opacity` |
| Position | `xPosition`, `yPosition`, `zPosition`, `radius` |
| Physics | `charge`, `mass` |
| Animation | `pulseSpeed` |

#### Scale Types

| Scale | Use Case |
|-------|----------|
| Linear | Even distribution |
| Sqrt | Compress large values |
| Log | Extreme ranges |
| Inverse | Flip mapping |

#### Groups

- Click `+G` to create group from selection
- Groups appear as colored chips with node counts
- Use for A/B visual comparison

### File Visualization Modes

| Mode | Description |
|------|-------------|
| Color | Each file gets unique hue |
| Hulls | Boundary polygons around file clusters |
| Cluster | Force-based file grouping |
| Map | File nodes view (files as first-class nodes) |
| Spheres | Containment spheres |

### Edge Modes

| Mode | Colors By |
|------|-----------|
| gradient-tier | Source/target tier |
| gradient-file | Source/target file |
| gradient-flow | Data flow direction |
| type | Edge type (calls, imports, etc.) |
| mono | Single color |

---

## 7. LOOKUP TABLES

### Term → JSON Path → Code Location

| Term | JSON Path | Computed In |
|------|-----------|-------------|
| Atom | `$.particles[*].atom` | `atom_classifier.py` |
| Role | `$.particles[*].metadata.role` | `heuristic_classifier.py` |
| Layer | `$.particles[*].ddd.layer` | `purpose_field.py` |
| Dead Code | `$.execution_flow.orphans[*]` | `execution_flow.py` |
| Knot | `$.knots.cycles[*]` | `topology_reasoning.py` |
| Topology | `$.statistics.topology` | `topology_reasoning.py` |
| Antimatter | `$.particles[*].violations[*]` | `antimatter_evaluator.py` |

### RPBL → JSON Path

| Dimension | JSON Path |
|-----------|-----------|
| Responsibility | `$.rpbl_profile.responsibility` |
| Purity | `$.rpbl_profile.purity` |
| Boundary | `$.rpbl_profile.boundary` |
| Lifecycle | `$.rpbl_profile.lifecycle` |

### Graph Metrics → JSON Path

| Metric | JSON Path |
|--------|-----------|
| In-Degree | `$.particles[*].metrics.in_degree` |
| Out-Degree | `$.particles[*].metrics.out_degree` |
| Entry Points | `$.execution_flow.entry_points[*]` |
| Dead Code % | `$.coverage.dead_code_percent` |

### Output Files

| File | Produces |
|------|----------|
| `unified_analysis.json` | `unified_analysis.py` |
| `output.md` | `brain_download.py` |
| `collider_report.html` | `viz/` |

---

## 7. DEVELOPMENT

### Setup

```bash
pip install -e .
```

### Test

```bash
pytest tests/ -q
```

### Self-Check

```bash
./collider full . --output .collider
```

### With AI

```bash
gcloud auth application-default login
./collider full . --ai-insights --output .collider
```

### Critical Rule

**ALWAYS regenerate after modifying visualization files:**
```bash
./collider full . --output .collider
```

Never trust old `.html` outputs — they are stale.

---

## 8. TROUBLESHOOTING

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `path argument is required` | No path provided | `./collider full /path/to/repo` |
| `No Python files found` | Wrong path | `ls -la /path && find /path -name '*.py'` |
| `Graph has no nodes` | Parser failed | Check encoding: `file -i /path/*.py` |
| `Dead code percentage 100%` | No entry points | Check for `__main__` blocks |
| `AI insights unavailable` | Not authenticated | `gcloud auth application-default login` |
| `JSONDecodeError` | Malformed output | `python -m json.tool graph.json` |
| `Ollama connection refused` | Not running | `ollama serve` |

### Debug Commands

| Situation | Command |
|-----------|---------|
| Verbose output | `./collider full /path 2>&1` |
| Validate schema | `python -m jsonschema schema/atom.schema.json` |
| Inspect graph | `python -m json.tool .collider/graph.json` |
| Test graph | `./collider graph .collider/graph.json --bottlenecks` |

### Common Scenarios

**No Python files:**
```bash
ls -la /path/to/repo
find /path/to/repo -name '*.py' -type f
```

**Graph has no nodes:**
```bash
./collider full /path --verbose-timing
file -i src/**/*.py
```

**Dead code 100%:**
- No reachable entry points
- Check for `__main__` or `if __name__ == '__main__':`

---

## 9. SCRIPTS

### Orientation Files Export

Export context for AI agents:

```bash
./scripts/sync-orientation-files.sh          # One-time sync
./scripts/sync-orientation-files.sh --watch  # Continuous sync
./scripts/sync-orientation-files.sh --zip    # Generate zip
```

**Destination:** `~/Downloads/orientation-files/`

### Exported Files

| Source | Destination |
|--------|-------------|
| README.md | REPO_README.md |
| CLAUDE.md | CLAUDE.md |
| docs/TOOL.md | TOOL.md |
| docs/MODEL.md | MODEL.md |

### Requirements

```bash
brew install fswatch  # For watch mode
```

---

## 10. VERSION HISTORY

| Date | Event |
|------|-------|
| 2025-12-14 | Initial commit (Spectrometer v12) |
| 2025-12-23 | THE PIVOT: AI → Deterministic |
| 2026-01-11 | Rebrand: Spectrometer → Collider |
| 2026-01-19 | Atom integration (94 atoms unified) |
