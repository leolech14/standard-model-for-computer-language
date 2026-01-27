# Collider (Standard Model of Code)

## Identity

| Fact | Value |
|------|-------|
| Theory | Standard Model of Code |
| Tool | Collider |
| Purpose | Find basic constituents of computer programs |
| Atoms | 3,525 total (80 core + 3,445 T2 mined) |
| Roles | 33 canonical, 29 implemented |
| Pipeline | 29 stages (5 phases) |
| **Node Count** | 1,179 core / 1,961 full (see `docs/specs/NODE_COUNT_GROUND_TRUTH.md`) |
| Body Coverage | ~36% nodes have `body_source` |

## Atom Inventory (Statistical Analysis)

| Tier | Count | Coverage | Description |
|------|-------|----------|-------------|
| Base | 22 | ~90% structural | Core semantic roles (Function, Class, Variable) |
| T0 | 42 | 100% parseable | AST atoms (definitional) |
| T1 | 21 | ~20-40% | Standard library patterns |
| T2 | 3,445 | 0-60% variable | Ecosystem-specific (178 ecosystems) |

**Key insight:** 4 base atoms (LOG.FNC.M, ORG.AGG.M, DAT.VAR.A, ORG.MOD.O) cover ~80-90% of code structure. T2 atoms provide semantic enrichment, not structural coverage.

**Data quality:** 77% of T2 atoms are security-focused (from Semgrep). Functional patterns need expansion.

See `docs/reports/ATOM_STATISTICAL_ANALYSIS.md` for full analysis.

## Canonical Sources

| Document | Path | Contents |
|----------|------|----------|
| **Theory Stack** | `docs/theory/THEORY_INDEX.md` | **CANONICAL** - Unified theory in 4 layers (L0-L3) |
| Model | `docs/MODEL.md` | Original theory doc (now unified into Stack) |
| Collider | `docs/COLLIDER.md` | Commands, pipeline, visualization controls |
| Viz UI Spec | `docs/specs/VISUALIZATION_UI_SPEC.md` | Technical spec for interactive UI |
| Tree-sitter Spec | `docs/specs/TREE_SITTER_INTEGRATION_SPEC.md` | Full TS integration guide |
| Tree-sitter Inventory | `docs/specs/TREE_SITTER_POWER_INVENTORY.md` | Capability checklist |
| **Tree-sitter Validation** | `docs/specs/TREE_SITTER_VALIDATION_REPORT.md` | Evidence-based validation (authoritative) |
| **Tree-sitter Tasks** | `docs/specs/TREE_SITTER_TASK_REGISTRY.md` | 46 tasks with confidence scores |
| **Codome Research** | `docs/research/CODOME_EDGE_DISCOVERY.md` | Boundary nodes, inferred edges, known bugs |
| **Atom Statistics** | `docs/reports/ATOM_STATISTICAL_ANALYSIS.md` | Coverage model, quality issues, honest numbers |
| **Atom Investigation** | `docs/research/ATOM_COVERAGE_INVESTIGATION.md` | Causal analysis, confidence scores, implications |
| **Codome Landscape** | `docs/specs/CODOME_LANDSCAPE.md` | Topology, elevation, gradients, Betti numbers |
| **Landscape Implementation** | `docs/specs/LANDSCAPE_IMPLEMENTATION_GUIDE.md` | Algorithms, pipeline integration, health index |
| **Node Count Ground Truth** | `docs/specs/NODE_COUNT_GROUND_TRUTH.md` | Canonical scope definitions, expected counts |
| **Open Concerns** | `docs/OPEN_CONCERNS.md` | Active issues, tech debt, session logs |
| **Theory Amendment** | `../context-management/docs/deep/THEORY_AMENDMENT_2026-01.md` | A1:Tools, A2:Dark Matter, A3:Confidence |
| **Ontological Foundations** | `../context-management/docs/deep/ONTOLOGICAL_FOUNDATIONS.md` | Axioms, category theory, semiotics, fundamentality stances |

## Commands

| Task | Command |
|------|---------|
| Analyze codebase | `./collider full <path> --output <dir>` |
| With AI insights | `./collider full <path> --ai-insights` |
| Self-check | `./collider full . --output .collider` |
| **Symmetry check** | `./collider symmetry <path> --docs <docs_path>` |
| **Trace deviations** | `./collider deviations <path> --code-dir src --docs-dir docs` |
| **Validate UI** | `python tools/validate_ui.py <html_path> --verbose` |
| **Export to GraphRAG** | `python tools/export_graphrag.py <analysis.json> --output <dir>` |
| Install | `pip install -e .` |
| Run tests | `pytest tests/` |

## Visualization Development Workflow

**CRITICAL:** The final HTML report is a **build artifact**, not a source file.

### Source Files (EDIT THESE)

| File | Purpose |
|------|---------|
| `src/core/viz/assets/template.html` | HTML structure with `{{VERSION}}`, `{{STYLES}}`, `{{APP_JS}}` placeholders |
| `src/core/viz/assets/styles.css` | All CSS styles |
| `src/core/viz/assets/modules/*.js` | Modular JavaScript (48 files) |
| `src/core/viz/assets/app.js` | Legacy JS (being replaced by modules) |

### The Correct Workflow

1. **Edit source files** in `src/core/viz/assets/`
2. **Regenerate**: `./collider full <path> --output <dir>`
3. **View result**: Open the generated `collider_report.html`

### What NOT to Do

- **DO NOT** edit any `collider_report.html` or `output_*.html` directly (they are build artifacts)
- **DO NOT** look for `index.html` in viz/assets (it was deleted - it was a trap)
- **DO NOT** test changes by opening source files in browser (they have placeholders, not real code)

### Generation Pipeline

```
template.html + styles.css + 48 modules/*.js
        ↓
    visualize_graph_webgl.py
        ↓
    collider_report.html (standalone, all JS inlined)
```

See `tools/visualize_graph_webgl.py` for the generation logic.

## File Lookup

| Task | File |
|------|------|
| CLI entry | `cli.py` |
| Pipeline orchestrator | `src/core/full_analysis.py` |
| Report generator | `src/core/brain_download.py` |
| Topology classifier | `src/core/topology_reasoning.py` |
| HTML generator | `tools/visualize_graph_webgl.py` |
| Atom loader | `src/core/atom_loader.py` |
| Atom classifier | `src/patterns/atom_classifier.py` |
| Atom definitions | `src/patterns/ATOMS_TIER*.yaml` |
| Role definitions | `schema/fixed/roles.json` |
| HTML template | `src/core/viz/assets/template.html` |
| HTML styles | `src/core/viz/assets/styles.css` |
| HTML JS (legacy) | `src/core/viz/assets/app.js` |
| Control Bar | `src/core/viz/assets/modules/control-bar.js` |
| File Viz | `src/core/viz/assets/modules/file-viz.js` |
| **Circuit Breaker** | `src/core/viz/assets/modules/circuit-breaker.js` |
| **UI Validator** | `tools/validate_ui.py` |
| File Enricher | `src/core/file_enricher.py` |
| **Tree-sitter Engine** | `src/core/tree_sitter_engine.py` |
| **Query Loader** | `src/core/queries/__init__.py` |
| **Edge Extractor** | `src/core/edge_extractor.py` |
| **Codome Boundaries** | `src/core/full_analysis.py:165-298` |
| **Level Classifier** | `src/core/level_classifier.py` |
| **EventBus (Python)** | `src/core/event_bus.py` |
| **EventBus (JS)** | `src/core/viz/assets/modules/event-bus-v2.js` |
| **Hub (Registry of Registries)** | `src/core/registry/registry_of_registries.py` |
| **Plugin System (Pipeline)** | `src/core/pipeline/manager.py` |
| **OKLCH Integration Guide** | `docs/specs/OKLCH_INTEGRATION_GUIDE.md` |
| **Modularity Assessment** | `docs/specs/MODULARITY_ASSESSMENT.md` |
| **Architecture Synthesis** | `docs/specs/MODULAR_ARCHITECTURE_SYNTHESIS.md` |
| Module pattern | `docs/specs/VISUALIZATION_UI_SPEC.md#state-unification-pattern` |

## Output Files

| File | Contents |
|------|----------|
| `unified_analysis.json` | Nodes, edges, metrics (structured data) |
| `collider_report.html` | Interactive 3D visualization |
| `output.md` | Brain Download (markdown report) |

## Architecture

| Layer | Purpose | Status |
|-------|---------|--------|
| Layer 1 | Deterministic Core (THE intelligence) | Implemented |
| Layer 2 | LLM Enrichment (optional) | Implemented (`--ai-insights`) |

| Direction | Status |
|-----------|--------|
| Analysis (Code → Graph) | Implemented |
| Synthesis (Graph → Code) | NOT YET |

## Codome Boundaries (Stage 6.8)

**Status:** Pipeline implemented, UI pending

Synthetic nodes representing external callers we can't see in the code:

| Boundary | ID | Description |
|----------|-----|-------------|
| TestFramework | `__codome__::test_entry` | pytest/jest invoke test functions |
| RuntimeEntry | `__codome__::entry_point` | __main__, CLI scripts |
| FrameworkDI | `__codome__::framework_managed` | decorators, DI containers |
| HTMLTemplate | `__codome__::cross_language` | JS called from HTML |
| ExternalAPI | `__codome__::external_boundary` | npm consumers, public API |
| DynamicDispatch | `__codome__::dynamic_target` | getattr, eval, reflection |

**Known Bug:** Degree calculation includes ALL edges (structural + calls). Should filter by family.
See `docs/research/CODOME_EDGE_DISCOVERY.md` for details.

## Rendering Stack

| Library | Version | Purpose |
|---------|---------|---------|
| Three.js | 0.149.0 | 3D rendering engine |
| 3d-force-graph | 1.73.3 | Force-directed graph layout |

**Note:** NOT raw WebGL. The stack is `3d-force-graph` → `Three.js` → `WebGL`.

## Theoretical Hierarchy

| Level | Concept |
|-------|---------|
| 0 | Three Layers (Physical, Virtual, Semantic) |
| 1 | 16-Level Scale (Bit → Universe) |
| 2 | Atoms, Dimensions, Roles |
| 3 | Patterns, Violations, Predictions |

## Output Sections

| Section | What It Contains |
|---------|------------------|
| IDENTITY | Node count, edge count, dead code % |
| CHARACTER (RPBL) | Responsibility, Purity, Boundary, Lifecycle |
| ARCHITECTURE | Type distribution, layer breakdown |
| HEALTH STATUS | Traffic-light indicators |
| IMPROVEMENTS | Prescriptive recipes |
| VISUAL REASONING | Topology shape (Star, Mesh, Islands) |
| DOMAIN CONTEXT | Inferred business domain |
| AI INSIGHTS | Pattern detection (if `--ai-insights`) |

## Visualization Shortcuts

| Key | Action |
|-----|--------|
| `M` or `` ` `` | Toggle Control Bar (visual mapping) |
| `I` | Show info for selected nodes |
| `Escape` | Close panels |

## UI Controls (Circuit Breaker Validated)

| Control | Type | Element ID | State Path | Purpose |
|---------|------|------------|------------|---------|
| Edge Opacity | slider | `cfg-edge-opacity` | `APPEARANCE_STATE.edgeOpacity` | Edge visibility |
| Edge Width | slider | `cfg-edge-width` | `APPEARANCE_STATE.edgeWidth` | Edge thickness |
| Edge Curvature | slider | `cfg-edge-curve` | `APPEARANCE_STATE.edgeCurvature` | Edge bend |
| Node Size | slider | `cfg-node-size` | `APPEARANCE_STATE.nodeScale` | Node radius |
| Node Opacity | slider | `cfg-node-opacity` | `APPEARANCE_STATE.nodeOpacity` | Node visibility |
| Show Arrows | toggle | `cfg-toggle-arrows` | `APPEARANCE_STATE.showArrows` | Directional arrows |
| Physics Charge | slider | `physics-charge` | `Graph.d3Force('charge')` | Node repulsion |
| Dimension Toggle | button | `btn-2d` | `IS_3D` | 2D/3D switch |
| View Mode | button | `btn-files` | `GRAPH_MODE` | Files/Atoms view |

**Validate controls:** `python tools/validate_ui.py <html> --verbose`

## Rules

| Rule | Why |
|------|-----|
| Regenerate before debugging HTML | Old outputs are stale |
| Run tests before commit | Catch regressions |
| LLM sees metrics, not code | Meta-analysis only |
| Theory + Tool live together | They inform each other |

## Node Schema

```json
{
  "id": "UserService.validate",
  "file_path": "src/services/user.py",
  "start_line": 45,
  "end_line": 67,
  "body_source": "def validate(self, data):\n    ...",

  "// Stage 6.7: Semantic Purpose Analysis (PURPOSE = f(edges))": "",
  "semantic_role": "utility",
  "closeness_centrality": 0.027,
  "reachable_from_entry": true,
  "depth_from_entry": 2,
  "is_bridge": false,
  "is_influential": true,
  "is_coordinator": false,
  "intent_profile": {
    "has_docstring": true,
    "docstring": "Validates user data against schema",
    "has_commits": true,
    "commit_intents": ["fix", "feature"]
  }
}
```

### Semantic Role Classification

| Role | Description | Degree Pattern |
|------|-------------|----------------|
| `utility` | Serves many callers | High in, low out |
| `orchestrator` | Coordinates many callees | Low in, high out |
| `hub` | Critical junction | High in, high out |
| `leaf` | Specialized/isolated | Low in, low out |
