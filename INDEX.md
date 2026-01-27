# PROJECT_elements - Master Index

> **Status:** CANONICAL
> **Purpose:** Single front door to the entire project
> **Rule:** If it's not linked from INDEX (or a registry), it's not part of the canonical narrative.

---

## Quick Navigation

| Action | Document |
|--------|----------|
| **What is this?** | [README.md](README.md) |
| **Run something** | [QUICK_START.md](QUICK_START.md) |
| **Understand structure** | [ARCHITECTURE_MAP.md](ARCHITECTURE_MAP.md) |
| **Find files** | [PROJECT_MAP.md](PROJECT_MAP.md) |

---

## The Canonical Reading Path

### 1. FOUNDATIONS (Tier 0 - Axioms)

These rarely change. If they change, everything must be reconsidered.

| Document | Purpose |
|----------|---------|
| [THEORY_AXIOMS.md](standard-model-of-code/docs/theory/THEORY_AXIOMS.md) | Formal mathematical axioms (A1-H5) |
| [PROJECTOME.md](context-management/docs/PROJECTOME.md) | Universe algebra: P = C ⊔ X |
| [CODOME.md](context-management/docs/CODOME.md) | Executable code definition |
| [CONTEXTOME.md](context-management/docs/CONTEXTOME.md) | Non-executable content definition |
| [GLOSSARY.md](context-management/docs/GLOSSARY.md) | 400+ terms, canonical vocabulary |

### 2. CORE THEORY (Tier 1 - Canonical Specs)

The Standard Model and its tool.

| Document | Purpose |
|----------|---------|
| [MODEL.md](standard-model-of-code/docs/MODEL.md) | **THE** Standard Model of Code |
| [COLLIDER.md](standard-model-of-code/docs/COLLIDER.md) | The analysis tool reference |
| [TOPOLOGY_MAP.md](context-management/docs/TOPOLOGY_MAP.md) | Spatial model of the repository |

### 3. ARCHITECTURE & NAVIGATION

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE_MAP.md](ARCHITECTURE_MAP.md) | System architecture overview |
| [PROJECT_MAP.md](PROJECT_MAP.md) | Directory topology |
| [THEORY_MAP.md](THEORY_MAP.md) | Complete theory documentation inventory |

### 4. OPERATIONS

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | Project instructions for AI |
| [AI_USER_GUIDE.md](context-management/docs/deep/AI_USER_GUIDE.md) | The three AI roles |
| [CLI_GRAMMAR.md](context-management/docs/agent_school/CLI_GRAMMAR.md) | ./pe command reference |

### 5. REGISTRIES (Tier 3 - Indices)

| Registry | Purpose |
|----------|---------|
| [REGISTRY_OF_REGISTRIES.md](standard-model-of-code/docs/specs/REGISTRY_OF_REGISTRIES.md) | Master index of all registries |
| [META_REGISTRY.yaml](.agent/META_REGISTRY.yaml) | Agent state registries |
| [CODOME_MANIFEST.yaml](.agent/CODOME_MANIFEST.yaml) | Declared code boundaries |

### 6. AUDIT & QUALITY

| Document | Purpose |
|----------|---------|
| [AUDIT_MANIFEST.md](AUDIT_MANIFEST.md) | Curated audit package spec |
| [DEEP_GHOSTS_REPORT.md](DEEP_GHOSTS_REPORT.md) | Broken references & duplicates |
| [OPEN_CONCERNS.md](standard-model-of-code/docs/OPEN_CONCERNS.md) | Active issues & tech debt |

---

## Truth Hierarchy

| Tier | Status | Description | Changes |
|------|--------|-------------|---------|
| **0** | AXIOM | Foundational definitions | Requires full reconsidering |
| **1** | CANONICAL | Specs, manuals, theory | Requires validation |
| **2** | DERIVED | Reports, audits, roadmaps | Changes frequently |
| **3** | GENERATED | Collider outputs, artifacts | Auto-generated |
| **4** | RESEARCH | AI research conversations | Useful context only |
| **∅** | ARCHIVE | Historical only | Never changes |

---

## Realm Entry Points

| Realm | Path | Entry Point | Purpose |
|-------|------|-------------|---------|
| **PARTICLE** | `standard-model-of-code/` | [CLAUDE.md](standard-model-of-code/CLAUDE.md) | Collider engine |
| **WAVE** | `context-management/` | [AI_USER_GUIDE.md](context-management/docs/deep/AI_USER_GUIDE.md) | AI tools |
| **OBSERVER** | `.agent/` | [KERNEL.md](.agent/KERNEL.md) | Governance |

---

## Artifact Registries

| Artifact Type | Registry | Latest |
|---------------|----------|--------|
| Collider outputs | [collider_outputs/REGISTRY.md](collider_outputs/REGISTRY.md) | TBD |
| Calibration data | [artifacts/INDEX.md](standard-model-of-code/artifacts/INDEX.md) | TBD |
| Schemas | [schema/REGISTRY.md](standard-model-of-code/schema/REGISTRY.md) | TBD |

---

## Packaging Tiers

| Pack | Size | Purpose | Contents |
|------|------|---------|----------|
| **Orientation** | ~100KB | Fast onboarding | Tier 0-1 docs only |
| **Audit** | ~500KB | External audit | + checksums + evidence |
| **Evidence** | ~50MB | Full validation | + collider outputs |
| **Full** | ~1GB | Everything | + artifacts + research |

See [AUDIT_MANIFEST.md](AUDIT_MANIFEST.md) for pack specifications.

---

## Commands

```bash
./pe boot              # Initialize session
./pe status            # Health check
./pe deck deal         # Available certified moves
./pe collider full .   # Run analysis
./pe ask "query"       # AI query
```

---

*Last validated: 2026-01-27*
*Status: CANONICAL*
