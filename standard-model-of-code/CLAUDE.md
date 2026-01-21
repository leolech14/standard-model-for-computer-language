# Collider (Standard Model of Code)

## Identity

| Fact | Value |
|------|-------|
| Theory | Standard Model of Code |
| Tool | Collider |
| Purpose | Find basic constituents of computer programs |
| Atoms | 200 documented, 94 implemented, 600+ ecosystem potential |
| Roles | 33 canonical, 29 implemented |
| Pipeline | 12 stages |
| Body Coverage | ~36% nodes have `body_source` |

## Canonical Sources

| Document | Path | Contents |
|----------|------|----------|
| Model | `docs/MODEL.md` | Theory, atoms, roles, proofs, history |
| Collider | `docs/COLLIDER.md` | Commands, pipeline, visualization controls |
| Viz UI Spec | `docs/specs/VISUALIZATION_UI_SPEC.md` | Technical spec for interactive UI |
| Tree-sitter Spec | `docs/specs/TREE_SITTER_INTEGRATION_SPEC.md` | Full TS integration guide |
| Tree-sitter Inventory | `docs/specs/TREE_SITTER_POWER_INVENTORY.md` | Capability checklist |
| **Tree-sitter Validation** | `docs/specs/TREE_SITTER_VALIDATION_REPORT.md` | Evidence-based validation (authoritative) |

## Commands

| Task | Command |
|------|---------|
| Analyze codebase | `./collider full <path> --output <dir>` |
| With AI insights | `./collider full <path> --ai-insights` |
| Self-check | `./collider full . --output .collider` |
| **Validate UI** | `python tools/validate_ui.py <html_path> --verbose` |
| Install | `pip install -e .` |
| Run tests | `pytest tests/` |

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
| **Edge Extractor** | `src/core/edge_extractor.py` |
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
  "body_source": "def validate(self, data):\n    ..."
}
```
