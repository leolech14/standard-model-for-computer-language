# Research: List ALL task-related collections: task registries, opportunity inboxes, sprint definitions, batch d...

> **Date:** 2026-01-25 08:10:40
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:baf472aeb31c1dafdd8b3108ed32a1fcc4442aaf52a792729baaabc865357f88`
> **Raw JSON:** `raw/20260125_081040_list_all_task_related_collections__task_registries.json`

---

## Query

List ALL task-related collections: task registries, opportunity inboxes, sprint definitions, batch definitions, card decks. For each: name, path, item count, status (active/archived).

---

## Response

Based on the provided codebase context, here is the comprehensive list of all task-related collections.

### 1. Task Registries
*Primary systems for tracking approved work.*

| Name | Path | Item Count | Status |
| :--- | :--- | :--- | :--- |
| **Unified Task Registry** | `.agent/registry/active/` | **~25** files visible (IDs range TASK-001 to TASK-066)* | **Active** |
| **Legacy UPB Registry** | `standard-model-of-code/docs/specs/UPB_TASK_REGISTRY.md` | 15 tasks | **Archived** (Read-only) |
| **Legacy Pipeline Registry** | `standard-model-of-code/docs/specs/PIPELINE_REFACTOR_TASK_REGISTRY.md` | 10 tasks | **Archived** (Read-only) |
| **Legacy Tree-sitter Registry** | `standard-model-of-code/docs/specs/TREE_SITTER_TASK_REGISTRY.md` | 1 task | **Archived** (Read-only) |
| **Legacy Token System** | `standard-model-of-code/docs/reports/TOKEN_SYSTEM_TASK_REGISTRY.md` | 8 tasks | **Archived** (Read-only) |
| **Legacy Sidebar Registry** | `standard-model-of-code/docs/reports/SIDEBAR_REFACTOR_TASK_REGISTRY.md` | 3 tasks | **Archived** (Read-only) |
| **Legacy Modularization** | `standard-model-of-code/docs/reports/MODULARIZATION_TASKS.md` | 13 tasks | **Archived** (Read-only) |

*\*Note: The INDEX.md summary lists 9 "Active" tasks, but the file directory contains numerous "COMPLETE" tasks (e.g., TASK-001, TASK-066) retained for history.*

### 2. Opportunity Inboxes
*Staging areas for potential work/ideas.*

| Name | Path | Item Count | Status |
| :--- | :--- | :--- | :--- |
| **Discovery Inbox** | `.agent/registry/inbox/` | **59** opportunities | **Active** |

### 3. Sprint Definitions
*Time-boxed execution containers.*

| Name | Path | Item Count | Status |
| :--- | :--- | :--- | :--- |
| **SPRINT-001** (Foundation) | `.agent/sprints/SPRINT-001.yaml` | 2 primary tasks | **COMPLETE** |
| **SPRINT-002** (Context Refinery) | `.agent/sprints/SPRINT-002.yaml` | 6 primary tasks | **EXECUTING** |
| **SPRINT-003** (Refinery Fdn) | `.agent/sprints/SPRINT-003.yaml` | 1 primary task | **COMPLETE** |

### 4. Batch Definitions
*Thematic groupings of tasks spanning potentially multiple sprints.*

| Name | Path | Item Count | Status |
| :--- | :--- | :--- | :--- |
| **BATCH-010** (Adaptive Intel) | Defined in `.agent/registry/INDEX.md` | 23 tasks (6 sub-batches) | **PLANNING** |

### 5. Card Decks
*Constrained action spaces for agent execution.*

| Name | Path | Item Count | Status |
| :--- | :--- | :--- | :--- |
| **Decision Deck Layer** | `.agent/deck/` | 9 cards (e.g., `CARD-REG-001`) | **Archived** (WONT_DO)* |

*\*Note: Per TASK-018, the Decision Deck system was built but deemed "Meta-Tooling Unused" and closed on 2026-01-23.*

---

## Citations

_No citations provided_
