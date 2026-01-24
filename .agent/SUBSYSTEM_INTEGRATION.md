# Subsystem Integration Map

> Canonical reference for how PROJECT_elements subsystems connect.
> **Last validated:** 2026-01-23 via Gemini analysis

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROJECT_elements SUBSYSTEMS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   SOURCE CODE                                                                │
│        │                                                                     │
│        ▼                                                                     │
│   ┌─────────────┐                                                            │
│   │  COLLIDER   │  ← Collapses wave function → particle of knowledge         │
│   │ (Particle)  │                                                            │
│   └─────┬───────┘                                                            │
│         │                                                                    │
│         ▼  unified_analysis.json                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    INTELLIGENCE LAYER (Wave)                         │   │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│   │  │ analyze.py  │◄───│     HSL     │    │ Perplexity  │              │   │
│   │  │ (Engine)    │    │ (Framework) │    │    MCP      │              │   │
│   │  └──────┬──────┘    └─────────────┘    └─────────────┘              │   │
│   │         │                                     ▲                      │   │
│   │         │  --verify mode                      │ External queries     │   │
│   │         └─────────────────────────────────────┘                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                    │
│         ▼  Tasks generated                                                   │
│   ┌─────────────┐                                                            │
│   │    TASK     │  ← State machine for work items                            │
│   │  REGISTRY   │                                                            │
│   └─────┬───────┘                                                            │
│         │                                                                    │
│         ▼  Tasks claimed                                                     │
│   ┌─────────────┐                                                            │
│   │    BARE     │  ← Auto-refinement (the "hands")                           │
│   │  (Engine)   │                                                            │
│   └─────┬───────┘                                                            │
│         │                                                                    │
│         └───────────────► SOURCE CODE (loop closes)                          │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   PARALLEL: Archive/Mirror syncs to GCS on every commit                      │
│             Commit Hygiene (pre-commit) validates before commit              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Subsystem Registry

| ID | Subsystem | Type | Path | Purpose |
|----|-----------|------|------|---------|
| S1 | **Collider** | Engine | `standard-model-of-code/` | Semantic code analysis (ground truth) |
| S2 | **HSL** | Framework | `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md` | Automated validation rules |
| S3 | **analyze.py** | Engine | `context-management/tools/ai/analyze.py` | AI query interface (implements HSL) |
| S4 | **Perplexity MCP** | Utility | `context-management/tools/mcp/perplexity_mcp_server.py` | External knowledge queries |
| S5 | **Task Registry** | State | `.agent/registry/` | Work item tracking |
| S6 | **BARE** | Engine | `.agent/tools/bare` | Background auto-refinement |
| S7 | **Archive/Mirror** | Utility | `context-management/tools/archive/` | Cloud sync (GCS) |
| S8 | **Commit Hygiene** | Guard | `.pre-commit-config.yaml`, `commitlint.config.js` | Enforce Conventional Commits |

---

## Data Flow

```
1. CODE COMMIT
   └─► Collider generates unified_analysis.json
   └─► Archive/Mirror syncs to GCS
   └─► BARE TruthValidator updates repo_truths.yaml

2. SCHEDULED VALIDATION (HSL)
   └─► analyze.py --verify runs against semantic_models.yaml
   └─► Violations generate tasks in Registry

3. TASK EXECUTION
   └─► BARE claims task from Registry
   └─► BARE generates fix
   └─► Commits → loop restarts at (1)

4. HUMAN QUERY
   └─► analyze.py processes query
   └─► Optional: Perplexity for external context
   └─► May generate task for manual or BARE execution
```

---

## Integration Points

### Implemented

| From | To | Mechanism | Status |
|------|-----|-----------|--------|
| Collider → analyze.py | unified_analysis.json | File read | ACTIVE |
| HSL → analyze.py | --verify flag | CLI invocation | ACTIVE |
| Git commit → Archive | post-commit hook | Shell script | ACTIVE |
| Git commit → BARE | post-commit hook | Shell script | ACTIVE |
| analyze.py → Research | Auto-save to docs/research/ | File write | ACTIVE |
| **Git commit ← Commit Hygiene** | pre-commit + commit-msg hooks | Block invalid commits | **ACTIVE** |

### Proposed (from Gemini analysis)

| From | To | Mechanism | Priority |
|------|-----|-----------|----------|
| analyze.py → Task Registry | Structured YAML output | P1 - Critical |
| Task Registry → BARE | tasks.yaml polling | P1 - Critical |
| analyze.py → Perplexity | --enable-external-search | P2 - Enhancement |
| CI/CD → Archive | GitHub Action | P2 - Enhancement |

---

## Relationship Clarifications

### HSL vs analyze.py --verify

**Not a redundancy.** This is a **concept/implementation** pair:

- **HSL** = The conceptual framework (the "what" and "why")
- **analyze.py --verify** = The execution engine (the "how")

The HSL documentation should reference: "Implemented via `analyze.py --verify`"

### Task Registry Format

**Current:** Markdown files (human-readable, machine-fragile)
**Proposed:** Structured YAML (machine-readable, enables automation)

Migration path:
1. Keep markdown for human visibility
2. Add parallel `tasks.yaml` for machine consumption
3. BARE reads from YAML, humans read from markdown

---

## Cross-Reference Index

For each subsystem, these are the key files to understand:

### Collider (S1)
- Entry: `standard-model-of-code/CLAUDE.md`
- Theory: `standard-model-of-code/docs/MODEL.md`
- Pipeline: `standard-model-of-code/src/core/full_analysis.py`

### HSL (S2)
- Spec: `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md`
- Config: `context-management/config/semantic_models.yaml`
- Implementation: `context-management/tools/ai/analyze.py` (--verify)

### analyze.py (S3)
- Source: `context-management/tools/ai/analyze.py`
- Config: `context-management/config/analysis_sets.yaml`
- User guide: `context-management/docs/AI_USER_GUIDE.md`

### Perplexity MCP (S4)
- Server: `context-management/tools/mcp/perplexity_mcp_server.py`
- Output: `docs/research/perplexity/`

### Task Registry (S5)
- Index: `.agent/registry/INDEX.md`
- Learning tasks: `.agent/registry/LEARNING_SYSTEM_TASK_REGISTRY.md`
- Schema: `.agent/schema/task.schema.yaml`

### BARE (S6)
- Spec: `.agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md`
- CLI: `.agent/tools/bare`
- Output: `.agent/intelligence/`

### Archive/Mirror (S7)
- Tool: `context-management/tools/archive/archive.py`
- Config: `context-management/tools/archive/config.yaml`
- Bucket: `gs://elements-archive-2026/`

### Commit Hygiene (S8)
- Pre-commit config: `.pre-commit-config.yaml`
- Commitlint config: `commitlint.config.js`
- Install: `pre-commit install --hook-type commit-msg --hook-type pre-commit`
- Kernel reference: `.agent/KERNEL.md` (Non-Negotiables #2)

---

## Integration Checklist

When adding a new subsystem:

- [ ] Add entry to Subsystem Registry table above
- [ ] Document data flow (inputs/outputs)
- [ ] Add to Cross-Reference Index
- [ ] Update architecture diagram if needed
- [ ] Add integration tests if machine-to-machine

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-01-24 | Added Commit Hygiene (S8) - pre-commit + commitlint |
| 1.0.0 | 2026-01-23 | Initial integration map (validated by Gemini analysis) |
