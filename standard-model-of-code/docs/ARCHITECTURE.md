# Collider Architecture

> The definitive guide to Collider's two-layer architecture and the bidirectionality vision.

---

## Core Principle

**The deterministic layer IS the intelligence. The LLM layer is optional enrichment.**

Collider is valuable and complete without any AI integration. The Standard Model of Code provides algorithmic, reproducible analysis that doesn't depend on language models.

---

## Two-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   LAYER 1: DETERMINISTIC CORE (The Intelligence)                    │
│   ════════════════════════════════════════════════                  │
│                                                                     │
│   THE THEORETICAL FOUNDATION (The Standard Model):                  │
│   ────────────────────────────────────────────────                  │
│   • Atomic Theory: OPEN SCHEMA organized into 4 phases,             │
│     16 families (DATA → LOGIC → ORGANIZATION → EXECUTION)           │
│   • Role Theory: Canonical roles (Repository, Entity, Service...)   │
│   • Layer Theory: Architectural placement (Domain, Infra, App, UI)  │
│   • Antimatter Laws: Cross-layer violation detection                │
│   • Purpose Field: System intent emergence                          │
│   • Execution Flow: Reachability and orphan detection               │
│                                                                     │
│   DERIVED ANALYSIS (built on the theory):                           │
│   ────────────────────────────────────────                          │
│   • RPBL Scoring       • Topology Classification                    │
│   • Coupling Analysis  • Dead Code Detection                        │
│   • Shortest Paths     • Markov Chain Analysis                      │
│   • Knot Detection     • Component Analysis                         │
│                                                                     │
│   STATUS: ✅ FULLY IMPLEMENTED                                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   LAYER 2: LLM ENRICHMENT (Optional Enhancement)                    │
│   ════════════════════════════════════════════════                  │
│                                                                     │
│   • Natural language summaries                                      │
│   • Pattern recognition narratives                                  │
│   • Refactoring suggestions in prose                                │
│   • Risk assessment explanations                                    │
│                                                                     │
│   PROVIDERS: Vertex AI Gemini, Ollama (local)                       │
│   STATUS: ✅ IMPLEMENTED (via --ai-insights flag)                   │
│                                                                     │
│   ⚠️  NOTE: This layer reasons about Collider's OUTPUT,             │
│       not the source code itself. It's meta-analysis.               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Bidirectionality Vision

### Current State: Unidirectional Analysis

```
     SOURCE CODE                              CODESPACE
┌──────────────────┐                    ┌──────────────────┐
│                  │                    │                  │
│  src/            │                    │    ┌───┐        │
│  ├── main.py     │  ══════════════▶   │    │ A │────┐   │
│  ├── utils.py    │     Collider       │    └───┘    │   │
│  └── models/     │     ANALYSIS       │      │      ▼   │
│      └── user.py │                    │      ▼    ┌───┐ │
│                  │                    │    ┌───┐  │ C │ │
│                  │                    │    │ B │──┴───┘ │
│                  │                    │    └───┘        │
└──────────────────┘                    └──────────────────┘
        │                                       │
        ▼                                       ▼
   You can READ                           You can SEE
   and EDIT manually                      the structure
```

### Target State: Bidirectional Transformation

```
     SOURCE CODE                              CODESPACE
┌──────────────────┐                    ┌──────────────────┐
│                  │                    │                  │
│  src/            │  ══════════════▶   │    ┌───┐        │
│  ├── main.py     │     Collider       │    │ A │────┐   │
│  ├── utils.py    │     ANALYSIS       │    └───┘    │   │
│  └── models/     │                    │      │      ▼   │
│      └── user.py │  ◀══════════════   │      ▼    ┌───┐ │
│                  │     Collider       │    ┌───┐  │ C │ │
│                  │     SYNTHESIS      │    │ B │──┴───┘ │
│                  │                    │    └───┘        │
└──────────────────┘                    └──────────────────┘
        │                                       │
        ▼                                       ▼
   REFACTORED                             MANIPULATE:
   OUTPUT                                 • Move nodes
                                          • Rewire edges
                                          • Extract modules
                                          • Merge components
```

### The Workflow

1. **Analyze** - Run Collider to get the graph representation
2. **Visualize** - See the structure in the HTML report
3. **Identify** - Find issues (God classes, coupling, dead code)
4. **Manipulate** - Modify the graph (move, extract, merge)
5. **Synthesize** - Reconstruct the codebase from modified graph
6. **Verify** - Run tests on the refactored code

### Why Bidirectionality Matters

| Without Synthesis | With Synthesis |
|-------------------|----------------|
| "You have a God class" | "Here's your codebase with the God class split" |
| Manual refactoring | Automated refactoring |
| Analysis-only tool | Transformation tool |
| See problems | Fix problems |

---

## Node Body Storage

Nodes store their source code for reconstruction:

```json
{
  "id": "UserService.validate",
  "name": "validate",
  "kind": "method",
  "file_path": "src/services/user.py",
  "start_line": 45,
  "end_line": 67,
  "body_source": "def validate(self, data: dict) -> bool:\n    ...",
  "complexity": 8
}
```

**Current coverage:** ~36% of nodes have `body_source`
**Target coverage:** 90%+ for reconstructable node types

---

## Data Flow

### Analysis Pipeline (Implemented)

```
source files
     │
     ▼
┌─────────────┐
│   Parser    │  Tree-sitter extracts AST
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Extractor  │  Identify atoms (functions, classes, modules)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Classifier │  Assign types, roles, tiers (Standard Model)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Analyzer   │  Compute metrics, detect patterns
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Enricher   │  Add RPBL scores, topology classification
└──────┬──────┘
       │
       ▼
unified_analysis.json + collider_report.html
```

### Synthesis Pipeline (Not Yet Implemented)

```
modified graph (JSON)
     │
     ▼
┌─────────────┐
│  Validator  │  Check graph integrity (no orphans, valid refs)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Resolver   │  Resolve file paths, handle moves
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generator  │  Reconstruct file contents from node bodies
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Formatter  │  Apply consistent formatting (black, prettier)
└──────┬──────┘
       │
       ▼
reconstructed source files
```

---

## LLM Integration Details

### What the LLM Receives

The LLM layer receives **structured metrics**, not raw code:

```
Target: my_project
Nodes: 1356
Edges: 3288
Files: 59
Topology Shape: Hierarchical
RPBL: R=0.72, P=0.45, B=0.81, L=0.63

Top Hubs:
- ConfigManager (fan_out: 45)
- DatabaseService (fan_out: 38)
- EventDispatcher (fan_out: 31)

Sample Nodes:
- UserController (INTERFACE/class, T1)
- PaymentService.process (LOGIC/method, T0)
```

### What the LLM Produces

Structured insights in JSON format:

```json
{
  "executive_summary": "The codebase shows...",
  "patterns_detected": [
    {
      "pattern_name": "Facade",
      "pattern_type": "design_pattern",
      "confidence": 0.85,
      "affected_nodes": ["ConfigManager"],
      "evidence": "Central hub with high fan-out..."
    }
  ],
  "refactoring_opportunities": [...],
  "risk_areas": [...]
}
```

### When to Use LLM vs Deterministic

| Use Deterministic Layer | Use LLM Layer |
|-------------------------|---------------|
| "How many God classes?" | "Explain why this is a God class" |
| "Show coupling metrics" | "Suggest how to reduce coupling" |
| "List dead code" | "Prioritize which dead code to remove" |
| "Calculate shortest path" | "Explain the dependency chain" |

---

## File Reference

| File | Purpose |
|------|---------|
| `cli.py` | Entry point, command dispatch |
| `src/core/full_analysis.py` | 12-stage analysis pipeline |
| `src/core/unified_analysis.py` | Core graph generation |
| `src/core/brain_download.py` | Markdown report generation |
| `tools/visualize_graph_webgl.py` | HTML visualization |
| `context-management/tools/ai/analyze.py` | LLM integration |

---

## See Also

- [CLAUDE.md](../CLAUDE.md) - Agent quick reference
- [GAPS_ANALYSIS_2026-01-19.md](reports/GAPS_ANALYSIS_2026-01-19.md) - Current gaps and roadmap
- [Standard Model Theory](../schema/) - Theoretical foundations
