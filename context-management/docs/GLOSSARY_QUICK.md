# Quick Glossary - 10 Terms for Day 1

> Learn these first. Everything else can wait.

## The Essentials

| Term | Definition | When You'll See It |
|------|------------|-------------------|
| **Collider** | The analysis tool. Parses code, builds graph, outputs `unified_analysis.json`. | `./collider full <path>` |
| **CODOME** | All executable code (.py, .js, .ts, etc). What runs. | Collider analyzes this |
| **CONTEXTOME** | All non-executable content (.md, .yaml, configs). What informs. | ACI queries this |
| **Atom** | A semantic category for code (Function, Class, Service, etc). | Node classification |
| **Node** | A single code element in the graph (function, class, variable). | Graph building |
| **Edge** | A connection between nodes (calls, imports, inherits). | Dependency tracking |
| **Task** | A persistent work item. Survives sessions. | `.agent/registry/` |
| **Concierge** | The boot command. Shows status, options, rules. | `./concierge` |
| **DOD** | Definition of Done. Clean tree + tests pass + committed + summary. | End of every task |
| **Symmetry** | Code matches docs. ORPHAN = code without docs. PHANTOM = docs without code. | Health checks |

## Commands You Need

```bash
./concierge                     # Start here
./collider full <path>          # Analyze code
pytest tests/ -q                # Run tests
git status                      # Before claiming "done"
```

## What You Don't Need Yet

These are real concepts, but learn them later:

- Wave/Particle/Observer (physics metaphor for directories)
- 4D Confidence (Factual/Alignment/Current/Onwards)
- 16-Level Scale (Bit to Universe)
- Purpose Field (teleological layer)
- Betti Numbers (topological invariants)

**Rule:** If you don't encounter it in your first task, you don't need to know it yet.

---

*Full glossary: `GLOSSARY.md` (340 lines)*
*This file: 10 terms, 60 seconds to read*
