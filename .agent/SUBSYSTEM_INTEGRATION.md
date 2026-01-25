# Subsystem Integration Map

> Canonical reference for how PROJECT_elements subsystems connect.
> **Last validated:** 2026-01-24 via Laboratory Bridge integration

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
│   ┌─────────────┐         ┌─────────────┐                                   │
│   │  COLLIDER   │────────►│ LABORATORY  │  ← Scientist research tools       │
│   │ (Particle)  │         │ (Particle)  │    atom_coverage, hypothesis_eval │
│   └─────┬───────┘         └──────┬──────┘                                   │
│         │                        │                                          │
│         ▼  unified_analysis.json │  ExperimentResult                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    INTELLIGENCE LAYER (Wave)                         │   │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│   │  │ analyze.py  │◄───│     HSL     │    │ Perplexity  │              │   │
│   │  │ (Engine)    │    │ (Framework) │    │    MCP      │              │   │
│   │  └──────┬──────┘    └─────────────┘    └─────────────┘              │   │
│   │         │                                     ▲                      │   │
│   │         │  --verify mode                      │ External queries     │   │
│   │         └─────────────────────────────────────┘                      │   │
│   │         │                                                            │   │
│   │         ▼                                                            │   │
│   │  ┌──────────────────┐                                                │   │
│   │  │ laboratory_bridge │◄──── Programmatic API to Scientist            │   │
│   │  │ (Wave↔Particle)   │      run_laboratory(), measure_coverage()     │   │
│   │  └──────────────────┘                                                │   │
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
| S9 | **Laboratory** | Bridge | `standard-model-of-code/tools/research/laboratory.py` | Scientist facade (Particle-side API) |
| S9b | **Laboratory Bridge** | Client | `context-management/tools/ai/laboratory_bridge.py` | Agent client (Wave-side caller) |
| S10 | **Cloud Automation** | Engine | `.agent/tools/cloud/` | Auto-boost opportunities via GCS + Cloud Function |
| S11 | **Batch Grade** | Experiment | `standard-model-of-code/tools/batch_grade/` | Mass Collider validation on 999+ repos (RunPod) |

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
| **analyze.py → Laboratory** | laboratory_bridge.py | Python import | **ACTIVE** |
| **Laboratory → Scientist Tools** | subprocess with templates | CLI execution | **ACTIVE** |
| **Git commit → Cloud Automation** | post-commit → sync_registry.py | Shell script | **ACTIVE** |
| **Cloud Scheduler → auto_boost** | Hourly HTTP trigger | Cloud Function | **PENDING DEPLOY** |

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

### Laboratory (S9)
- Facade: `standard-model-of-code/tools/research/laboratory.py`
- Client: `context-management/tools/ai/laboratory_bridge.py`
- API: `run_experiment(ExperimentRequest) -> ExperimentResult`
- Convenience: `measure_coverage()`, `evaluate_hypothesis()`
- Output: Experiment artifacts in temp directories

### Cloud Automation (S10)
- Directory: `.agent/tools/cloud/`
- Tools:
  - `sync_registry.py` - Sync local registry ↔ GCS
  - `auto_boost_function.py` - Cloud Function for auto-promotion
  - `deploy.sh` - Deploy to GCP
- Trigger: Post-commit hook + Cloud Scheduler (hourly)
- Bucket: `gs://elements-archive-2026/.agent/registry/`
- Health check: `.agent/tools/cloud/check_status.sh`

### Batch Grade (S11)
- Directory: `standard-model-of-code/tools/batch_grade/`
- Scripts:
  - `runpod_agent.py` - Full automation: create pod, run job, download results
  - `run_batch_local.py` - Parallel grading (runs on pod or locally)
  - `repos_999.json` - List of 999 GitHub repos to grade
- Outputs:
  - `grades_DEGRADED_summary_only/` - DEGRADED: 590 grade summaries only
  - `full_scans/` - EMPTY: Target for proper `collider full` run
- **STATUS: FAIL-001** - Ran with `grade` not `full`, missing unified_analysis.json
- Degradation marker: `grades_DEGRADED_summary_only/DEGRADED.md`
- Concern tracker: `standard-model-of-code/docs/OPEN_CONCERNS.md` (FAIL-001)

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
| 1.4.0 | 2026-01-25 | Added Batch Grade (S11) with FAIL-001 status |
| 1.3.0 | 2026-01-25 | Added Cloud Automation (S10), wired post-commit hook, health check |
| 1.2.0 | 2026-01-24 | Added Laboratory Bridge (S9) - Wave↔Particle integration |
| 1.1.0 | 2026-01-24 | Added Commit Hygiene (S8) - pre-commit + commitlint |
| 1.0.0 | 2026-01-23 | Initial integration map (validated by Gemini analysis) |
