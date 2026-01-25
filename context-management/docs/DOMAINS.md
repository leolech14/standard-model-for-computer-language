# DOMAINS - Vertical Slices Through the Projectome

> Cross-cuts through CODOME and CONTEXTOME that define functional areas.

## Definition

**Domain** (n.) — A vertical slice through both universes. Every domain has code (Codome) AND context (Contextome). A domain is defined by the relationship between its code and its documentation.

## The Cross-Cut Model

```
            │ CODOME              │ CONTEXTOME
            │ (executable)        │ (non-executable)
────────────┼─────────────────────┼──────────────────────────
Pipeline    │ full_analysis.py    │ PIPELINE_STAGES.md
            │ survey.py           │ specs/*.md
────────────┼─────────────────────┼──────────────────────────
Viz         │ modules/*.js        │ UI_SPEC.md
            │ styles.css          │ presets.yaml
────────────┼─────────────────────┼──────────────────────────
Governance  │ task_store.py       │ registry/*.yaml
            │ confidence.py       │ ROADMAP.yaml
────────────┼─────────────────────┼──────────────────────────
AI Tools    │ analyze.py          │ analysis_sets.yaml
            │ aci/*.py            │ prompts.yaml
────────────┼─────────────────────┼──────────────────────────
Theory      │ (N/A)               │ MODEL.md
            │                     │ docs/specs/*.md
```

## Domain Registry

| Domain | Codome Path | Contextome Path | Owner |
|--------|-------------|-----------------|-------|
| **Pipeline** | `standard-model-of-code/src/core/` | `standard-model-of-code/docs/specs/` | Collider |
| **Visualization** | `standard-model-of-code/src/core/viz/` | `standard-model-of-code/docs/specs/UI*.md` | Collider |
| **Governance** | `.agent/tools/` | `.agent/registry/`, `.agent/specs/` | Observer |
| **AI Tools** | `context-management/tools/ai/` | `context-management/config/` | Wave |
| **Theory** | — | `standard-model-of-code/docs/MODEL.md` | Human |
| **Archive** | `context-management/tools/archive/` | `context-management/tools/archive/config.yaml` | Wave |
| **Research** | `context-management/tools/mcp/` | `docs/research/` | Wave |

## Domain Symmetry

For any domain D:
- `D.code` ⊂ Codome (the executable implementation)
- `D.context` ⊂ Contextome (the specs, configs, docs)
- `D.symmetry` = how well D.code matches D.context

```
Domain Health = f(code_exists, context_exists, they_match)

SYMMETRIC   Code ←→ Context    Both exist, they match
ORPHAN      Code ←→ ∅          Code without docs
PHANTOM     ∅    ←→ Context    Spec without implementation
DRIFT       Code ←/→ Context   Both exist, they disagree
```

**Domain Health Score = Symmetric / (Symmetric + Orphan + Phantom + Drift)**

## Domain Operations

| Operation | Tool | Purpose |
|-----------|------|---------|
| Measure symmetry | HSL --verify | Detect drift |
| List domains | Registry of Registries | Discovery |
| Navigate domain | CLAUDE.md entry points | Jump to code/docs |
| Validate domain | Collider + ACI | Cross-check |

## Why Domains Matter

1. **Navigation** — Know where to look for code vs docs
2. **Completeness** — Detect orphan code or phantom specs
3. **Ownership** — Clear responsibility boundaries
4. **Health** — Measure documentation drift

## The Topology

```
┌─────────────────────────────────────────────────────────────┐
│                      PROJECTOME                              │
│                                                              │
│   ┌───────────────────┐     ┌───────────────────┐           │
│   │      CODOME       │     │    CONTEXTOME     │           │
│   │   (executable)    │     │  (non-executable) │           │
│   │                   │     │                   │           │
│   │ ┌───┐ ┌───┐ ┌───┐│     │┌───┐ ┌───┐ ┌───┐ │           │
│   │ │ P │ │ V │ │ G ││     ││ P │ │ V │ │ G │ │           │
│   │ │ i │ │ i │ │ o ││     ││ i │ │ i │ │ o │ │           │
│   │ │ p │ │ z │ │ v ││ ←─→ ││ p │ │ z │ │ v │ │           │
│   │ │ e │ │   │ │   ││     ││ e │ │   │ │   │ │           │
│   │ └───┘ └───┘ └───┘│     │└───┘ └───┘ └───┘ │           │
│   │                   │     │                   │           │
│   └───────────────────┘     └───────────────────┘           │
│                                                              │
│   Domains are VERTICAL slices through BOTH universes         │
└─────────────────────────────────────────────────────────────┘
```

## See Also

- `CODOME.md` — Executable universe
- `CONTEXTOME.md` — Non-executable universe
- `PROJECTOME.md` — Complete contents
- `TOPOLOGY_MAP.md` — Master navigation guide
- `.agent/SUBSYSTEM_INTEGRATION.md` — System connections

---

*Created: 2026-01-25*
*Domains are cross-cuts, not containers*
