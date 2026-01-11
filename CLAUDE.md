# CLAUDE.md - Agent Instructions

> Quick reference for AI agents working on this codebase.

---

## 🏛️ Two Pillars

| Pillar | Location | Purpose |
|--------|----------|---------|
| **📚 THEORY** | `docs/`, `schema/` | The model (atoms, dimensions, layers) |
| **🔧 TOOL** | `src/core/`, `cli.py` | The implementation (Collider) |

---

## What Is This?

**Collider** is a code analysis tool that generates `output.md` - a structured report optimized for LLM consumption.

## The One Command

```bash
./collider full <path> [--output <dir>]
```

**Example:**
```bash
./collider full /path/to/repo --output /tmp/analysis
```

**Output:** `<output_dir>/output.md` - The "Brain Download"

---

## What The Output Contains

| Section | What It Tells You |
|---------|-------------------|
| **IDENTITY** | Node count, edge count, dead code % |
| **CHARACTER (RPBL)** | 4-dimensional profile (Responsibility, Purity, Boundary, Lifecycle) |
| **ARCHITECTURE** | Type distribution, layer breakdown |
| **HEALTH STATUS** | Traffic-light indicators (✅⚠️❌) |
| **ACTIONABLE IMPROVEMENTS** | Prescriptive recipes with steps |
| **VISUAL REASONING** | Topology shape (Star, Mesh, Islands) |
| **DOMAIN CONTEXT** | Inferred business domain |

---

## Key Files

| File | Purpose |
|------|---------|
| `cli.py` | CLI entry point |
| `src/core/full_analysis.py` | Main pipeline orchestrator |
| `src/core/brain_download.py` | Generates `output.md` |
| `src/core/metaphor_primer.md` | LLM persona instructions |
| `src/core/topology_reasoning.py` | Shape classification |
| `src/core/semantic_cortex.py` | Domain inference |

---

## Development

```bash
# Install
pip install -e .

# Run tests
pytest tests/

# Self-check
./collider full src/core --output /tmp/self_check
```

---

## The Philosophy

> "Collider is the architecture that allows us to see architecture."

The tool transforms invisible code structure into visible, actionable knowledge.
