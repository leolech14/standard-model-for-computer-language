# CLAUDE.md - Agent Instructions

> Quick reference for AI agents working on this codebase.

---

## The Big Picture

**PROJECT_elements** is the effort to find the **basic constituents of computer programs**.

It relies on a **theoretical model** — a map — that aims to consolidate, in a **topological continuum**, all basic components of the software engineering space.

This is an **open model**: not in the sense of being freely available, but in the sense that it is **always growing and reframing its assumptions**.

### The Codespace

We call this hyper-complex, high-dimensional space the **codespace** — where all software artifacts exist and relate.

### Canonical Order (Most → Least Fundamental)

| Level | Concept | Status |
|-------|---------|--------|
| **0** | **Three Parallel Layers** (Physical, Virtual, Semantic) | Always Green |
| **1** | **16-Level Scale** (Bit → Universe) | Backbone |
| **2** | Atoms, Dimensions, Roles | Active |
| **3** | Patterns, Violations, Predictions | Active |

---

## The Dichotomy

| | Theory | Practice |
|---|--------|----------|
| **Name** | Standard Model of Code | Collider |
| **Purpose** | The map | The tool that uses the map |
| **Question** | *What are the atoms of software?* | *How do we detect them?* |
| **Location** | `docs/`, `schema/` | `src/core/`, `cli.py` |

This is the most distinctive aspect: **theory and application live together, informing each other**.

---

## Two-Layer Architecture

> **The deterministic layer IS the intelligence. The LLM layer is optional enrichment.**

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: DETERMINISTIC CORE (The Intelligence)            │
│  ───────────────────────────────────────────────            │
│                                                             │
│  THE THEORETICAL FOUNDATION (The Standard Model):          │
│  • Atomic Theory: OPEN SCHEMA organized into 4 phases,     │
│    16 families (DATA → LOGIC → ORGANIZATION → EXECUTION)   │
│  • Role Theory: Canonical roles (Repository, Entity, etc.) │
│  • Layer Theory: Architectural placement (Domain, Infra)   │
│  • Antimatter Laws: Cross-layer violation detection        │
│  • Purpose Field: System intent emergence                  │
│  • Execution Flow: Reachability and orphan detection       │
│                                                             │
│  DERIVED ANALYSIS (built on the theory):                   │
│  • RPBL Scoring         • Topology Classification          │
│  • Coupling Analysis    • Markov Chains                    │
│  • Dead Code Detection  • Knot Detection                   │
│                                                             │
│  STATUS: FULLY IMPLEMENTED - This is the core value        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: LLM ENRICHMENT (Optional)                        │
│  ───────────────────────────────────────────────            │
│  • Pattern narratives     • Risk explanations              │
│  • Refactoring prose      • Natural language summaries     │
│                                                             │
│  STATUS: IMPLEMENTED (--ai-insights flag)                  │
│  NOTE: Tool is fully functional WITHOUT this layer         │
└─────────────────────────────────────────────────────────────┘
```

---

## The Bidirectionality Vision

### Current: Analysis Only (Code → Graph)
```
Codebase  ══════▶  Collider  ══════▶  Codespace (graph)
```

### Target: Full Bidirectionality
```
Codebase  ◀══════▶  Collider  ◀══════▶  Codespace (graph)
                                              │
                                         MANIPULATE
                                         (move, merge,
                                          extract, rewire)
```

**The vision:** Manipulate the graph, then deterministically reconstruct the codebase.

**Status:** Synthesis layer NOT YET IMPLEMENTED. See `docs/ARCHITECTURE.md`.

---

## What Is Collider?

**Collider** is the implementation that applies this theory to real codebases. It generates:
- `unified_analysis.json` — Structured data (nodes, edges, metrics)
- `collider_report.html` — Interactive 3D visualization
- `output.md` — The "Brain Download" (markdown report)

## The One Command

```bash
./collider full <path> [--output <dir>]
```

**With AI Insights:**
```bash
./collider full <path> --ai-insights
```

**Example:**
```bash
./collider full /path/to/repo --output /tmp/analysis
```

---

## What The Output Contains

| Section | What It Tells You |
|---------|-------------------|
| **IDENTITY** | Node count, edge count, dead code % |
| **CHARACTER (RPBL)** | 4-dimensional profile (Responsibility, Purity, Boundary, Lifecycle) |
| **ARCHITECTURE** | Type distribution, layer breakdown |
| **HEALTH STATUS** | Traffic-light indicators |
| **ACTIONABLE IMPROVEMENTS** | Prescriptive recipes with steps |
| **VISUAL REASONING** | Topology shape (Star, Mesh, Islands) |
| **DOMAIN CONTEXT** | Inferred business domain |
| **AI INSIGHTS** | Pattern detection, refactoring suggestions (if --ai-insights) |

---

## Node Body Storage

Nodes store their source code for potential reconstruction:

```json
{
  "id": "UserService.validate",
  "file_path": "src/services/user.py",
  "start_line": 45,
  "end_line": 67,
  "body_source": "def validate(self, data):\n    ..."
}
```

**Current coverage:** ~36% of nodes have `body_source`

---

## Key Files

| File | Purpose |
|------|---------|
| `cli.py` | CLI entry point |
| `src/core/full_analysis.py` | Main pipeline orchestrator (12 stages) |
| `src/core/brain_download.py` | Generates `output.md` |
| `src/core/topology_reasoning.py` | Shape classification |
| `tools/visualize_graph_webgl.py` | HTML visualization generator |
| `docs/ARCHITECTURE.md` | Full architecture documentation |
| `docs/reports/GAPS_ANALYSIS_*.md` | Current gaps and roadmap |

---

## Critical Rules

### HTML Visualization Testing

**ALWAYS run the full pipeline when testing HTML output.**

```bash
./collider full . --output .collider
```

Old outputs are **stale** and will show phantom bugs. The HTML is generated from:
- `src/core/viz/assets/template.html`
- `src/core/viz/assets/styles.css`
- `src/core/viz/assets/app.js`

If you modify any of these, **regenerate** - never inspect old `.html` files.

### LLM Layer Understanding

The LLM (when enabled with `--ai-insights`) reasons about **Collider's output**, not the source code:
- It sees: node counts, metrics, topology shape, hub names
- It does NOT see: actual source code, function implementations

This is **meta-analysis** — AI analyzing an analysis.

---

## Development

```bash
# Install
pip install -e .

# Run tests
pytest tests/

# Self-check (ALWAYS use this when debugging HTML)
./collider full src/core --output /tmp/self_check

# With AI insights (requires gcloud auth)
./collider full src/core --output /tmp/self_check --ai-insights
```

---

## The Philosophy

> "Collider is the architecture that allows us to see architecture."

The tool transforms invisible code structure into visible, actionable knowledge.

> "The deterministic layer is the intelligence. AI is amplification, not the source."

The Standard Model provides algorithmic, reproducible analysis. LLMs help explain it in natural language.
