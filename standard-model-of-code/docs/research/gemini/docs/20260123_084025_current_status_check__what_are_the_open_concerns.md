# Research: Current status check: What are the open concerns, pending tasks, and immediate priorities in the .ag...

> **Date:** 2026-01-23 08:40:25
> **Source:** gemini
> **Model:** gemini-2.5-pro
> **Checksum:** `sha256:b58239a14bc0ef4bbc59a6e536ce96c52168733212dcf3bd2ad0c1bb45953eca`
> **Raw JSON:** `raw/20260123_084025_current_status_check__what_are_the_open_concerns.json`

---

## Query

Current status check: What are the open concerns, pending tasks, and immediate priorities in the .agent/ system? What needs attention?

---

## Response

Of course. As a senior software engineer, here is my analysis of the current status, open concerns, and immediate priorities for the `.agent/` system based on the provided codebase.

### Executive Summary

The agent system is at a critical inflection point. It has just completed a foundational sprint (`SPRINT-001`) which established core mechanics like the discovery inbox and sprint registry. However, this "bulk phase" has also created significant design complexity and cruft.

The immediate priorities are twofold and slightly in tension:
1.  **Simplification:** Execute `TASK-004` (the `CUTTING_PLAN`) to reduce complexity, archive dead weight, and create a leaner, more maintainable system.
2.  **Expansion:** Execute `SPRINT-002`, an ambitious project to build the "Context Refinery," which is the foundation for a much more advanced RAG system.

My primary recommendation is to **execute the `CUTTING_PLAN` first**. It is a high-priority, `READY` task that will simplify the codebase, making the `SPRINT-002` work easier and more robust.

---

### 1. Open Concerns

The file `.agent/OPEN_CONCERNS.md` provides a clear, self-aware assessment of the system's strategic weaknesses. While `SPRINT-001` has begun to address them, the underlying issues remain relevant:

*   **A. Discovery & Consolidation Gap:** Valuable insights from research get lost.
    *   **Status:** Partially addressed. The "Discovery Inbox" (`.agent/registry/inbox/`) and `promote_opportunity.py` now exist, but a "Research Refinery" pipeline to automate insight extraction is still just a proposal.

*   **B. Fragmented Context Loading:** Agents lack a holistic view of the codebase.
    *   **Status:** Partially addressed. The `KERNEL.md` boot protocol provides grounding, but the proposed "Regional RAG Clustering" to manage large contexts is not built.

*   **C. No Sprint Discipline:** Work can drift without clear targets.
    *   **Status:** Addressed. The `.agent/sprints/` system is now in place and `SPRINT-001` is `COMPLETE`. The discipline must now be maintained.

*   **D. Roadmap Not Institutionalized:** Strategic plans are scattered and not enforced.
    *   **Status:** Unaddressed. The proposal for a central `ROADMAP_REGISTRY.yaml` has not been implemented.

*   **E. Research History Untapped:** Over 50 Perplexity queries have been saved but not systematically mined for insights.
    *   **Status:** Unaddressed. The extraction pipeline is a key goal of the proposed "Research Refinery."

---

### 2. Pending Tasks & Immediate Priorities

Here is a breakdown of the current work landscape, from most to least urgent.

#### **Priority 1: Housekeeping & Simplification (The `CUTTING_PLAN`)**

This is the most pressing and actionable item. `TASK-004: Execute CUTTING_PLAN` is in `READY` status with `HIGH` priority. It aims to transition the system from its "bulk" design phase to a "lean" operational state.

**Key Actions in `TASK-004`:**
1.  **Archive Dead Weight:** Remove unused files like `.agent/intelligence/truths/history/*` and misplaced docs like `testing_suite.md` into a forensically-sound archive.
2.  **Create Meta-Registry:** Consolidate multiple scattered registry tables into a single, machine-readable `.agent/META_REGISTRY.yaml`.
3.  **Simplify Task State Machine:** Reduce the number of task states from 7 to 5 (`DISCOVERY → READY → EXECUTING → COMPLETE → ARCHIVED`) to lower procedural overhead.
4.  **Trim BARE Spec:** Refactor the `BACKGROUND_AUTO_REFINEMENT_ENGINE.md` spec to clearly separate what is *implemented* (TruthValidator) from what is *aspirational* (the other 5 processors).

#### **Priority 2: Active Sprint Work (`SPRINT-002`)**

The system is currently in `SPRINT-002: Context Refinery Foundation`, which is in the `EXECUTING` state. This is a major undertaking to build a sophisticated context management system.

**Sprint Status:**
*   **Goal:** Build a RAG/Long-Context hybrid that can atomize and recompile repository knowledge.
*   **Completed Work:**
    *   `TASK-007`: The `RefineryNode` schema has been defined in `.agent/schema/refinery_node.schema.yaml`. This is a comprehensive schema unifying multiple concepts.
*   **Pending Work (What needs attention):**
    *   `TASK-008`: Build corpus inventory tool.
    *   `TASK-009`: Build boundary mapper.
    *   `TASK-010`: Build delta detector for incremental processing.
    *   `TASK-011`: Build a basic distiller/atomizer.
    *   `TASK-012`: Build a global state synthesizer.

#### **Priority 3: Other Scoped Tasks (Backlog)**

These tasks are scoped and ready to be planned or claimed, likely after `SPRINT-002` is complete.
*   **`TASK-005` (SCOPED):** Perplexity research tool.
*   **`TASK-006` (SCOPED):** Socratic audit misalignment fixes.

#### **Priority 4: Triage Discovery Inbox**

The `.agent/registry/INDEX.md` shows **57 opportunities** in the inbox. There is a high-priority batch of `PIPELINE` related tasks (`OPP-023` to `OPP-027`) that are ready for promotion. This is the next wave of work once the current priorities are cleared.

---

### 3. What Needs Attention Now: A Prioritized Action Plan

1.  **Claim and Execute `TASK-004` (CUTTING_PLAN).**
    *   **Rationale:** This task is `READY`, `HIGH` priority, and directly addresses the system's growing complexity. Completing this will "sharpen the saw," making all subsequent work (especially `SPRINT-002`) simpler and faster. It's a classic case of paying down technical debt to increase future velocity.

2.  **Continue with `SPRINT-002` Execution.**
    *   **Rationale:** This is the declared focus of the current sprint. The next step is to create and begin work on `TASK-008` (Corpus Inventory Tool), which is the next `PENDING` item in the sprint's definition of done. The team needs to decide whether to pause this for `TASK-004` or run them in parallel. I strongly recommend doing `TASK-004` first.

3.  **Formalize the Roadmap.**
    *   **Rationale:** Concern 'D' (Roadmap Not Institutionalized) is a significant strategic risk. The ambitious BARE specs (`BACKGROUND_AUTO_REFINEMENT_ENGINE.md`, `BARE_LIVE.md`) are currently just large design documents. A concrete, versioned roadmap would help sequence these ambitions into achievable chunks and prevent work from drifting. This could be the focus of a future Design Sprint.

---

## Citations

_No citations provided_
