# CONTEXTOME - The Context Universe

> The complete set of non-executable content in a software project.

## Definition

**Contextome** (n.) — All non-executable artifacts: documentation, configuration, AI outputs, research, and metadata. The "meaning layer" that explains, configures, and governs the executable Codome.

## The Two Universes

| Universe | Contains | File Types | Analyzed By |
|----------|----------|------------|-------------|
| **CODOME** | Executable code | .py, .js, .ts, .go, .rs | Collider pipeline |
| **CONTEXTOME** | Non-executable content | .md, .yaml, .json (config) | AI reasoning (ACI) |

```
PROJECTOME (all project contents)
├── CODOME (executable)
│   └── All source code that runs
│
└── CONTEXTOME (non-executable)
    └── All content that informs
```

## Domains: The Cross-Cut

**Domains** are vertical slices through both universes. Each domain has code (Codome) AND context (Contextome):

```
            │ CODOME          │ CONTEXTOME
            │ (code)          │ (docs/config)
────────────┼─────────────────┼──────────────────
Pipeline    │ full_analysis.py│ PIPELINE_STAGES.md
            │ survey.py       │ specs/*.md
────────────┼─────────────────┼──────────────────
Viz         │ modules/*.js    │ UI_SPEC.md
            │ styles.css      │ presets.yaml
────────────┼─────────────────┼──────────────────
Governance  │ task_store.py   │ registry/*.yaml
            │ confidence.py   │ ROADMAP.yaml
────────────┼─────────────────┼──────────────────
AI Tools    │ analyze.py      │ analysis_sets.yaml
            │ aci/*.py        │ prompts.yaml
```

**A Domain is defined by the relationship between its code and its context.**

### Domain Symmetry

For any domain D:
- `D.code` ⊂ Codome (the executable implementation)
- `D.context` ⊂ Contextome (the specs, configs, docs)
- `D.symmetry` = how well D.code matches D.context

```
Domain Health = f(code_exists, context_exists, they_match)

Perfect:    Code ←→ Context  (documented and implemented)
Orphan:     Code ←→ ∅        (undocumented code)
Phantom:    ∅    ←→ Context  (unimplemented spec)
```

## Contextome Boundary

**Includes:**

| Category | Pattern | Examples |
|----------|---------|----------|
| Documentation | `**/docs/**/*.md` | MODEL.md, specs |
| Configuration | `**/*.yaml`, `**/*.json` | analysis_sets.yaml |
| AI Outputs | `**/research/**` | Perplexity, Gemini |
| Agent State | `.agent/**/*.yaml` | Tasks, sprints |
| Schemas | `**/schema/**/*.json` | particle.schema.json |

**Excludes:**

| Category | Reason |
|----------|--------|
| Source code (.py, .js) | That's Codome |
| Test code | That's Codome |
| Build artifacts | Generated |
| Binaries | Not text |

## Etymology

- **Context** — surrounding information that gives meaning
- **-ome** — complete set (Greek -ωμα)

## The Algebra

```
P = C ⊔ X        PROJECTOME = CODOME ⊔ CONTEXTOME (disjoint union)
X = P \ C        CONTEXTOME = PROJECTOME \ CODOME  (set difference)
C ∩ X = ∅        No overlap (mutually exclusive)
```

## The Terms

```
CODOME     = all executable code
CONTEXTOME = all non-executable content
PROJECTOME = CODOME ⊔ CONTEXTOME
```

## Contextome Health Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Coverage** | Documented nodes / Codome nodes | > 80% |
| **Freshness** | Updated last 30 days / Total | > 50% |
| **Symmetry** | Matching code-doc pairs / Total | > 90% |
| **Discoverability** | In ROR / Total | 100% |

## Operations

| Operation | Tool | Purpose |
|-----------|------|---------|
| Query | `analyze.py --set <name>` | AI search |
| Validate | HSL | Drift detection |
| Index | Registry of Registries | Discovery |
| Archive | `archive.py mirror` | GCS backup |

## See Also

- `CODOME.md` — Executable code definition
- `PROJECTOME.md` — Complete project contents
- `DOMAINS.md` — Vertical slices through both universes
- `TOPOLOGY_MAP.md` — Master navigation guide
- `CODOME_COMPLETENESS_INDEX.md` — Codome measurement
- `REGISTRY_OF_REGISTRIES.md` — Full enumeration

---

*Updated: 2026-01-25*
*Corrected: Domains are cross-cuts, not separate universes*
