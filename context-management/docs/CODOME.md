# CODOME - The Code Universe

> All executable code in a software project.

## Definition

**Codome** (n.) — The complete set of executable artifacts: source code files that can be parsed, compiled, or interpreted. The "doing layer" that implements functionality.

## The Two Universes

| Universe | Contains | File Types | Analyzed By |
|----------|----------|------------|-------------|
| **CODOME** | Executable code | .py, .js, .ts, .go, .rs, .java, .css, .html | Collider pipeline |
| **CONTEXTOME** | Non-executable content | .md, .yaml, .json (config) | AI reasoning (ACI) |

```
PROJECTOME (all project contents)
├── CODOME (executable)
│   └── All source code that runs
│
└── CONTEXTOME (non-executable)
    └── All content that informs
```

## Codome Boundary

**Includes:**

| Category | Pattern | Examples |
|----------|---------|----------|
| Source code | `**/*.py`, `**/*.js`, `**/*.ts` | Python, JavaScript, TypeScript |
| Compiled languages | `**/*.go`, `**/*.rs`, `**/*.java` | Go, Rust, Java |
| Markup (executable) | `**/*.html`, `**/*.css` | HTML templates, stylesheets |
| Query languages | `**/*.scm`, `**/*.sql` | Tree-sitter queries, SQL |
| Shell scripts | `**/*.sh`, `**/*.bash` | Automation scripts |

**Excludes:**

| Category | Reason |
|----------|--------|
| Documentation (.md) | That's Contextome |
| Configuration (.yaml, .json) | That's Contextome |
| Dependencies (node_modules, .venv) | External, not project code |
| Build artifacts (dist/, out/) | Generated, not source |
| Binaries (.exe, .so, .dll) | Not text, not parseable |

## Etymology

- **Code** — instructions for a computer
- **-ome** — complete set (Greek -ωμα)

## The Algebra

```
P = C ⊔ X        PROJECTOME = CODOME ⊔ CONTEXTOME (disjoint union)
C = P \ X        CODOME = PROJECTOME \ CONTEXTOME  (set difference)
C ∩ X = ∅        No overlap (mutually exclusive)
```

## The Terms

```
CODOME     = all executable code
CONTEXTOME = all non-executable content
PROJECTOME = CODOME ⊔ CONTEXTOME
```

## Codome Metrics

| Metric | Formula | Tool |
|--------|---------|------|
| **Node Count** | Total parseable symbols | Collider |
| **Coverage** | Analyzed / Total source files | CCI |
| **Health** | Topology + Edges + Gradients | Collider |
| **Completeness** | TP / (TP + FN) | CCI |

## Operations

| Operation | Tool | Purpose |
|-----------|------|---------|
| Parse | Tree-sitter | Extract AST |
| Classify | Collider | Assign atoms |
| Graph | Collider | Build edges |
| Visualize | Collider | 3D rendering |
| Measure | CCI | Completeness scoring |

## Derivative Specifications

| Doc | Purpose |
|-----|---------|
| `CODOME_COMPLETENESS_INDEX.md` | Measurement formulas |
| `CODOME_HEALTH_INDEX.md` | Health scoring |
| `CODOME_BOUNDARY_DEFINITION.md` | Inclusion/exclusion rules |
| `CODOME_LANDSCAPE.md` | Topology visualization |

## See Also

- `CONTEXTOME.md` — Non-executable content definition
- `PROJECTOME.md` — Complete project contents
- `DOMAINS.md` — Vertical slices through both universes
- `TOPOLOGY_MAP.md` — Master navigation guide
- `standard-model-of-code/docs/COLLIDER.md` — Analysis tool

---

*Created: 2026-01-25*
*The executable universe of PROJECT_elements*
