# Legacy Sprawl Map
> Generated: 2026-01-23
> Purpose: Document all scattered systems for Context Refinery consumption

---

## Summary

| Category | Files Found | Consolidated? | Action |
|----------|-------------|---------------|--------|
| Roadmaps | 11 | NO | Need unified roadmap |
| Task Registries | 13 | PARTIAL | REGISTRY_OF_REGISTRIES updated |
| Task Markdown | 13 | PARTIAL | Migration to .agent/registry/ ongoing |

---

## 1. Roadmap Files (11 found)

**Problem:** No single source of truth for project direction.

| File | Location | Status | Notes |
|------|----------|--------|-------|
| ROADMAP.md | `standard-model-of-code/` | ACTIVE | SMOC Development Roadmap (Phase 0-9) |
| RESEARCH_TO_IMPLEMENTATION_ROADMAP.md | `standard-model-of-code/docs/` | ACTIVE | Research→Implementation flow |
| T2_EXPANSION_ROADMAP.md | `standard-model-of-code/docs/specs/` | ACTIVE | Ecosystem atoms expansion |
| ROADMAP.md | `context-management/tools/mcp/mcp_factory/` | ACTIVE | MCP factory development |
| ROADMAP_TO_PROOF.md | `standard-model-of-code/.archive/docs_archive/` | ARCHIVED | Historical |
| ROADMAP.md | `standard-model-of-code/.archive/docs_archive/` | ARCHIVED | Historical |
| ROADMAP_10_OF_10.md | `context-management/docs/archive/` | ARCHIVED | Historical |
| ROADMAP.md | `archive/context-management-agent-2026-01-23/orientation/` | ARCHIVED | Backup |
| IMPLEMENTATION_ROADMAP.md | `archive/misc_docs/` | ARCHIVED | Historical |
| DDDLINT_PIVOT_ROADMAP.md | `archive/misc_docs/` | ARCHIVED | Historical |
| smart-buffer ROADMAP.md | `related/chrome-mcp/node_modules/` | EXTERNAL | Ignore |

### Recommendation
Create unified roadmap at `.agent/sprints/UNIFIED_ROADMAP.md` that references:
- SPRINT-002 (current: Context Refinery)
- Future sprints from SMOC ROADMAP.md phases

---

## 2. Task Registry Files (13 found)

**Problem:** Multiple registry formats across codebase.

| File | Location | Status | Items | Migrated To |
|------|----------|--------|-------|-------------|
| **TREE_SITTER_TASK_REGISTRY.md** | `standard-model-of-code/docs/specs/` | KEPT | 46 tasks | Canonical source |
| **PIPELINE_REFACTOR_TASK_REGISTRY.md** | `standard-model-of-code/docs/specs/` | MIGRATED | 35 tasks | OPP-006 |
| **TOKEN_SYSTEM_TASK_REGISTRY.md** | `standard-model-of-code/docs/reports/` | MIGRATED | 10 tasks | OPP-005 |
| UPB_TASK_REGISTRY.md | `standard-model-of-code/docs/specs/` | ARCHIVED | Phase 6 complete | - |
| ARCHITECTURE_DEBT_REGISTRY.md | `standard-model-of-code/docs/reports/` | REFERENCE | Analysis only | - |
| DOCS_IMPROVEMENT_TASK_REGISTRY.md | `standard-model-of-code/docs/reports/` | ARCHIVED | 1/10 done | - |
| DOCS_REORG_TASK_REGISTRY.md | `context-management/docs/` | ARCHIVED | 7/10 done | - |
| SIDEBAR_REFACTOR_TASK_REGISTRY.md | `standard-model-of-code/docs/reports/` | ARCHIVED | 1/13 done | - |
| ROLE_REGISTRY_HARDENING_PLAN.md | `standard-model-of-code/docs/plans/` | ACTIVE | Roles work | - |
| TREE_SITTER_FULL_IMPLEMENTATION_REGISTRY.md | `standard-model-of-code/docs/specs/` | DUPLICATE | → GCS archive | - |
| TASK_CONFIDENCE_REGISTRY.md | `context-management/tools/mcp/mcp_factory/` | SUPERSEDED | → .agent/registry | - |
| REGISTRY_REPORT.md | `context-management/registry/` | ACTIVE | Stats/state | - |
| REGISTRY_OF_REGISTRIES.md | `standard-model-of-code/docs/specs/` | ACTIVE | Meta-index | Updated 2026-01-21 |

### Recommendation
- Update REGISTRY_OF_REGISTRIES.md with current date
- Add Context Refinery registries when created
- Mark archived files with headers pointing to GCS location

---

## 3. Current Active System

### Primary Registry: `.agent/registry/`

| Directory | Contents |
|-----------|----------|
| `active/` | 7 tasks (TASK-001 to TASK-007) |
| `inbox/` | 57 opportunities (OPP-001 to OPP-057) |
| `archive/` | Completed/deferred items |

### Active Tasks
| ID | Title | Status | Sprint |
|----|-------|--------|--------|
| TASK-001 | (from migration) | SCOPED | - |
| TASK-002 | LangGraph state research | READY (98%) | - |
| TASK-003 | (from migration) | SCOPED | - |
| TASK-004 | CUTTING_PLAN execution | NEEDS_WORK (92%) | - |
| TASK-005 | Consolidate research directories | SCOPED | - |
| TASK-006 | Unify registry locations | SCOPED | - |
| **TASK-007** | **Define RefineryNode schema** | **READY** | **SPRINT-002** |

### Sprint Status
| Sprint | Name | Status | Target |
|--------|------|--------|--------|
| SPRINT-001 | Agent Task System | COMPLETE | 0.2.0 |
| SPRINT-002 | Context Refinery Foundation | EXECUTING | 0.3.0, 2026-01-30 |

---

## 4. Inbox Explosion Analysis

57 opportunities suggests aggressive auto-discovery is running. Categories:

| Range | Likely Source |
|-------|---------------|
| OPP-001 to OPP-007 | Manual creation (current session) |
| OPP-008 to OPP-057 | Auto-discovered by BARE/OpportunityExplorer |

**Action:** Review and prune inbox. Many may be duplicates or low-value.

---

## 5. Context Refinery Integration Points

When Context Refinery is built, it should consume:

| Source | Path | For |
|--------|------|-----|
| All roadmaps | `**/*ROADMAP*.md` | Strategic direction |
| All registries | `**/*REGISTRY*.md` | Task/debt tracking |
| Analysis sets | `context-management/config/analysis_sets.yaml` | Boundary definitions |
| Semantic models | `context-management/config/semantic_models.yaml` | Node schema basis |
| Git history | `.git/` | Delta detection |

---

## 6. Recommended Consolidation Path

1. **Immediate (SPRINT-002):**
   - Build RefineryNode schema (TASK-007)
   - Create corpus inventory tool
   - Auto-map all legacy sprawl files

2. **Next Sprint:**
   - Generate unified roadmap from sprawl
   - Deprecate scattered registry files
   - Point all to `.agent/registry/`

3. **Future:**
   - Auto-archive completed tasks to GCS
   - Delta-first reprocessing via HSL triggers

---

*This map will be consumed by the Context Refinery for initial corpus inventory.*
