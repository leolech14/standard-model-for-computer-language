[Home](../README.md) > [Docs](./README.md) > **Quick Start**

---

# Quick Start (5 Minutes)

## What Is This?

**Collider** is a code analysis tool that reveals the hidden structure of software.

**The Standard Model of Code** is the theoretical framework it uses — a periodic table for software.

## The One Command

```bash
./collider full /path/to/your/code --output /tmp/analysis
```

This generates:
- `unified_analysis.json` — Structured graph data
- `collider_report.html` — Interactive 3D visualization
- `output.md` — Human-readable report

## What You'll Learn

| About Your Codebase | Collider Tells You |
|---------------------|-------------------|
| Structure | Topology shape (`src/core/topology_reasoning.py`) - Star, Mesh, Hierarchical |
| Health | RPBL scores (`src/core/full_analysis.py`), dead code %, violations |
| Architecture | Layer distribution, type breakdown |
| Hotspots | God classes, circular dependencies |

## The Key Insight

> **The deterministic layer IS the intelligence. The LLM layer is optional.**

Collider works without AI. Add `--ai-insights` for natural language explanations.

## Next Steps

| Goal | Read |
|------|------|
| Understand the theory | [THEORY_MAP](./THEORY_MAP.md) |
| See the atom types | [ATOMS_REFERENCE](./ATOMS_REFERENCE.md) |
| Learn key terms | [GLOSSARY](./GLOSSARY.md) |
| Agent instructions | [CLAUDE.md](../CLAUDE.md) |
| Full architecture | [ARCHITECTURE](./ARCHITECTURE.md) |
