# PROJECTOME - The Complete Project Contents

> All contents of a software project: code + context.

## Definition

**Projectome** (n.) — The totality of all files in a software project. The union of Codome (executable) and Contextome (non-executable).

```
PROJECTOME = CODOME ∪ CONTEXTOME
```

## The Model

```
┌─────────────────────────────────────────────────────────────────┐
│                         PROJECTOME                               │
│                    (all project contents)                        │
│                                                                  │
│    ┌─────────────────────┐    ┌─────────────────────┐           │
│    │       CODOME        │    │     CONTEXTOME      │           │
│    │    (executable)     │    │  (non-executable)   │           │
│    │                     │    │                     │           │
│    │  • .py, .js, .ts    │    │  • .md, .yaml       │           │
│    │  • .go, .rs, .java  │    │  • .json (config)   │           │
│    │  • .css, .html      │    │  • research outputs │           │
│    │                     │    │                     │           │
│    │  "What runs"        │    │  "What informs"     │           │
│    └─────────────────────┘    └─────────────────────┘           │
│                                                                  │
│    ─────────────── DOMAINS (cross-cuts) ───────────────         │
│                                                                  │
│    Pipeline ──────┼── code ──────────┼── specs                  │
│    Visualization ─┼── modules/*.js ──┼── UI_SPEC.md             │
│    Governance ────┼── tools/*.py ────┼── registry/*.yaml        │
│    AI Tools ──────┼── aci/*.py ──────┼── config/*.yaml          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Terminology

| Term | Definition | Standard Alternative |
|------|------------|---------------------|
| **Projectome** | All project contents | "project files", "repo contents" |
| **Codome** | All executable code | "codebase", "source code" |
| **Contextome** | All non-executable content | "documentation", "metadata" |
| **Domain** | Vertical slice through Codome + Contextome | "module", "feature", "bounded context" |

## Why New Terms?

Standard terms are ambiguous:

| Standard Term | Problem |
|---------------|---------|
| "Codebase" | Sometimes includes docs, sometimes not |
| "Repository" | The container, not the contents |
| "Project" | The container, not the contents |
| "Source" | Usually just code |

The -ome terms provide:
1. **Completeness** — implies "the full set"
2. **Boundary** — clear inclusion/exclusion rules
3. **Measurability** — enables health metrics

## Current Counts (PROJECT_elements)

| Universe | Files | Description |
|----------|-------|-------------|
| **Codome** | ~250 | .py, .js, .css, .html, .scm |
| **Contextome** | ~600 | .md, .yaml, .json |
| **PROJECTOME** | ~850 | Total source files |

*Excludes: .venv, node_modules, __pycache__, .git*

## Domains

| Domain | Codome Files | Contextome Files |
|--------|--------------|------------------|
| Pipeline | src/core/*.py | docs/specs/PIPELINE*.md |
| Visualization | viz/assets/*.js | docs/specs/UI*.md |
| Governance | .agent/tools/*.py | .agent/registry/*.yaml |
| AI Tools | tools/ai/*.py | config/*.yaml |
| Theory | (N/A) | docs/MODEL.md |

## Domain Symmetry

A healthy domain has both code AND context that match:

```
Symmetry States:
────────────────
SYMMETRIC   Code ←→ Context    Both exist, they match
ORPHAN      Code ←→ ∅          Code without docs
PHANTOM     ∅    ←→ Context    Spec without implementation
DRIFT       Code ←/→ Context   Both exist, they disagree
```

**Domain Health = Symmetric / (Symmetric + Orphan + Phantom + Drift)**

## Operations

| Operation | Scope | Tool |
|-----------|-------|------|
| Measure Codome | Executable only | Collider |
| Query Contextome | Non-executable | ACI (analyze.py) |
| Index Projectome | Everything | Registry of Registries |
| Validate Symmetry | Code ↔ Context | HSL |

## Etymology

- **-ome** — complete set (Greek -ωμα)
- Biological parallels: genome, proteome, connectome

## The Algebra

```
P = C ⊔ X        PROJECTOME = CODOME ⊔ CONTEXTOME (disjoint union)
X = P \ C        CONTEXTOME = PROJECTOME \ CODOME  (set difference)
C ∩ X = ∅        No overlap (mutually exclusive)
```

**Partition:** CODOME and CONTEXTOME partition PROJECTOME — every file belongs to exactly one, together they cover everything (MECE: Mutually Exclusive, Collectively Exhaustive).

## The Terms

```
CODOME     = all executable code
CONTEXTOME = all non-executable content
PROJECTOME = CODOME ⊔ CONTEXTOME
```

That's it.

## See Also

- `CODOME.md` — Executable code definition
- `CONTEXTOME.md` — Non-executable content definition
- `DOMAINS.md` — Vertical slices through both universes
- `TOPOLOGY_MAP.md` — Master navigation guide
- `CODOME_COMPLETENESS_INDEX.md` — Code measurement spec
- `REGISTRY_OF_REGISTRIES.md` — Full enumeration

## Research Validation

Perplexity research confirming terminology value:
- `docs/research/perplexity/docs/20260125_152945_*.md` — Initial validation
- `docs/research/perplexity/docs/20260125_153041_*.md` — DSL value argument

---

*Created: 2026-01-25*
*Model: 2 universes (Codome + Contextome) + N domains (cross-cuts)*
