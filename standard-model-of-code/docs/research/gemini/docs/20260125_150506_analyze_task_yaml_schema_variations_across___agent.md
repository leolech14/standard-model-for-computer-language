# Research: Analyze task YAML schema variations across: .agent/schema/task.schema.yaml, .agent/schema/opportunit...

> **Date:** 2026-01-25 15:05:06
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:bf19d14312993058d2b85b31d815aefdf6e7ab8155100f759bcd3f1434045fc8`
> **Raw JSON:** `raw/20260125_150506_analyze_task_yaml_schema_variations_across___agent.json`

---

## Query

Analyze task YAML schema variations across: .agent/schema/task.schema.yaml, .agent/schema/opportunity.schema.yaml, .agent/registry/active/*.yaml, .agent/registry/inbox/*.yaml. What fields are inconsistent? Propose a unified schema.

---

## Response

Based on the provided codebase context, I have analyzed the schema variations across the active tasks (`TASK-*.yaml`) and inferred the structure of opportunities and sprints.

Here is the analysis of inconsistencies and a proposal for a Unified Task Schema (v2.0).

### 1. Inconsistency Analysis

There is significant drift between tasks created at different times (Pipeline Refactor vs. Infrastructure vs. Agent Foundation).

#### A. Temporal Fields (High Variance)
| Concept | Variation 1 | Variation 2 | Variation 3 | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Creation** | `created: '2026-01-23...'` | `created_at: '...'` | `tracking.created_at` | `created_at` (ISO 8601) |
| **Update** | `updated: '...'` | `updated_at: '...'` | (Missing) | `updated_at` (ISO 8601) |
| **Completion** | `closed_at` | `completed_at` | `deferred_at` | `completed_at` (generic) |

#### B. Provenance & Linking
| Concept | Variation 1 | Variation 2 | Recommendation |
| :--- | :--- | :--- | :--- |
| **Source** | `promoted_from: OPP-XXX` | `source_opp: OPP-XXX` | `source_id` |
| **Sprint** | `sprint_id: SPRINT-XXX` | `sprint: SPRINT-XXX` | `sprint_id` |
| **Dependency** | `blocks` / `blocked_by` | `unblocks` | `dependencies` (list) |

#### C. Categorization
| Concept | Variation 1 | Variation 2 | Variation 3 | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Grouping** | `category: PIPELINE` | `domain: infrastructure` | `tags: [...]` | `domain` + `tags` |
| **Urgency** | `priority: P0` | `risk: A+` | (Implied by ID) | `priority` (P0-P3) |

#### D. Execution Logic (Critical Divergence)
*   **Pattern A (Pipeline Tasks):** `steps` is a list of objects (`id`, `action`, `status`, `evidence`).
*   **Pattern B (Infrastructure):** `execution_plan` is a list of objects (`step`, `action`, `effort`).
*   **Pattern C (Triage):** `steps` is a list of objects, but `steps_completed` is a separate list of IDs.
*   **Pattern D (Decision Deck):** `deliverables` object with `completed` and `pending` lists.

---

### 2. Proposed Unified Schema (Version 2.0)

This schema consolidates the 4D confidence model from `INDEX.md` with the rigorous execution tracking of `TASK-007`.

```yaml
# .agent/schema/task_v2.schema.yaml

# CORE IDENTITY
id: "TASK-{NUMBER}"         # Required: Format TASK-\d+
title: String               # Required: Short summary
status: Enum                # Required: [DISCOVERY, READY, ACTIVE, BLOCKED, COMPLETE, DEFERRED, WONT_DO]
owner: String               # Optional: Agent or User ID (e.g., "claude-session-20260123")

# PROVENANCE & TIMING
created_at: ISO8601         # Required
updated_at: ISO8601         # Required
completed_at: ISO8601       # Optional (Required if status is COMPLETE/WONT_DO)
source_id: String           # Optional: Link to OPP-XXX or previous TASK-XXX
sprint_id: String           # Optional: Link to SPRINT-XXX

# CLASSIFICATION
domain: String              # Required: [pipeline, visualization, infrastructure, intelligence, observer]
priority: Enum              # Optional: [P0, P1, P2, P3]
tags: List[String]          # Optional: Flexible grouping

# CONTEXT
description: Markdown       # Required: Detailed description
closure_reason: String      # Optional: Required if WONT_DO or DEFERRED
output_artifacts:           # Optional: List of produced assets
  - path: String
    description: String

# 4D CONFIDENCE (Unified)
# Formula: Overall = min(Factual, Alignment, Current, Onwards)
confidence:
  factual: Float            # 0-100: Understanding of current state
  alignment: Float          # 0-100: Mission fit
  current: Float            # 0-100: Codebase fit
  onwards: Float            # 0-100: Future roadmap fit
  overall: Float            # Calculated
  verdict: String           # [ACCEPT, DEFER, REJECT]

# EXECUTION PLAN
# Consolidates 'steps', 'execution_plan', and 'deliverables'
steps:
  - id: String              # e.g., "S01"
    action: String          # What to do
    status: Enum            # [PENDING, IN_PROGRESS, DONE, SKIPPED]
    evidence:               # Optional: Proof of completion
      file: String
      line: Number
      note: String

# DEPENDENCIES
dependencies:
  blocked_by: List[String]  # Task IDs
  blocks: List[String]      # Task IDs
```

---

### 3. Migration Strategy (Field Mapping)

To normalize the repository, apply the following transformations:

1.  **Normalize Dates:**
    *   `created` → `created_at`
    *   `updated` → `updated_at`
    *   `closed_at` / `deferred_at` → `completed_at` (status determines semantic meaning).

2.  **Normalize Execution:**
    *   Move `execution_plan` items → `steps`.
    *   Move `deliverables.pending` → `steps` (status: PENDING).
    *   Move `deliverables.completed` → `steps` (status: DONE).

3.  **Normalize Classification:**
    *   `category` → `domain` (lowercase).
    *   `risk` → Convert to `priority` (A++ = P0, A = P1, etc.) or move to `tags`.

4.  **Normalize Confidence:**
    *   Ensure all tasks have the `confidence` object. Older tasks might just have a scalar value; these need to be expanded to the 4D structure (defaulting sub-scores to the scalar value).

### 4. Implementation Plan

**Step 1: Create Schema Validator**
Create `.agent/tools/validate_schema.py` using `pydantic` or `jsonschema` to enforce the v2 structure.

**Step 2: Batch Migration Script**
Write a script to load all `TASK-*.yaml` files, apply the mapping logic above, and rewrite them.

**Step 3: Update Tooling**
Update `promote_opportunity.py` and `task_store.py` to generate/read the new format.

**Example Migrated YAML (TASK-059):**

```yaml
id: TASK-059
title: Sprawl Consolidation Infrastructure
status: COMPLETE
created_at: '2026-01-23T17:28:08.260984'
updated_at: '2026-01-23T18:00:00.000000' # Inferred
completed_at: '2026-01-23T18:00:00.000000' # Inferred
source_id: OPP-059
domain: infrastructure
priority: P2
description: |
  Infrastructure improvements for managing repository sprawl...
confidence:
  factual: 100
  alignment: 95
  current: 100
  onwards: 90
  overall: 90
steps:
  - id: S01
    action: Created SPRAWL_CONSOLIDATION_PLAN.md
    status: DONE
  - id: S02
    action: Updated archive config with 4 large directories
    status: DONE
  # ... (remaining items from description)
```

---

## Citations

_No citations provided_
