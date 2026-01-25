# Research: Validate SPRINT-002 Context Refinery Foundation. Check: 1) Are all tasks properly defined? 2) What i...

> **Date:** 2026-01-23 12:29:01
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:d3c6ad5c0af584279c88e742ff40c8a0f81833f55c62c29b7686b9a7fb7d6c61`
> **Raw JSON:** `raw/20260123_122901_validate_sprint_002_context_refinery_foundation__c.json`

---

## Query

Validate SPRINT-002 Context Refinery Foundation. Check: 1) Are all tasks properly defined? 2) What is the execution order based on dependencies? 3) What is blocking progress? 4) Which task should be executed first?

---

## Response

Based on the provided codebase context, I have analyzed **SPRINT-002** and identified a **critical "Split Brain" condition** in the registry.

### 1. Are all tasks properly defined?
**NO. There is a severe data integrity collision.**

The system currently has two conflicting definitions for tasks `TASK-007` through `TASK-012`:

| Task ID | **SPRINT-002.yaml** Definition (Intended) | **TASK-XXX.yaml** File Definition (Actual on Disk) | Status |
|:---:|:---|:---|:---:|
| **007** | **Define RefineryNode schema** | *Refactor run_full_analysis()* | **CONFLICT** |
| **008** | **Build corpus inventory tool** | *Update semantic_models.yaml* | **CONFLICT** |
| **009** | **Build boundary mapper** | *Update Tests* | **CONFLICT** |
| **010** | **Build delta detector** | *Remove Mutation Side Effects* | **CONFLICT** |
| **011** | **Build basic distiller/atomizer** | *Remove I/O from Processing Stages* | **CONFLICT** |
| **012** | **Build global state synthesizer** | *Run Holographic Socratic Audit* | **CONFLICT** |

**Evidence of "Frankenstein" State:**
*   `TASK-007.yaml` has the **Title** "Refactor run_full_analysis" (Pipeline) but the **Steps** list "Define RefineryNode base schema fields" (Refinery).
*   The artifact `.agent/schema/refinery_node.schema.yaml` exists and cites `TASK-007`, yet the task file marks step 01 as `PENDING`.

### 2. Execution Order (Dependencies)
*Assuming the Registry is fixed to match the SPRINT-002 intent (Context Refinery/BARE-Live):*

The execution must follow the **Outside-In** and **Layered** architecture defined in `.agent/specs/BARE_LIVE.md`:

1.  **TASK-007 (Schema):** Define the `RefineryNode` atom structure. (Prerequisite for all).
2.  **TASK-008 (L0 Inventory):** Build the raw file inventory tool. (Input for Mapping).
3.  **TASK-010 (L0 Delta):** Build change detection. (Relies on Inventory).
4.  **TASK-009 (L1 Boundaries):** Build the boundary mapper using `analysis_sets.yaml`. (Relies on Inventory).
5.  **TASK-011 (L2 Distill):** Build the Atomizer/Distiller. (Relies on Boundaries + Schema).
6.  **TASK-012 (L3 Synth):** Build the Global Synthesizer. (Relies on Atoms).

### 3. What is blocking progress?
1.  **Registry Corruption:** An agent attempting `TASK-008` ("Build Inventory") will open the file and find instructions to "Update semantic_models.yaml". This will cause hallucination or failure.
2.  **Stale State:** `refinery_node.schema.yaml` exists, but `TASK-007` steps are marked `PENDING`.
3.  **Orphaned Work:** The Pipeline Refactor work (original titles for 007-012) is effectively overwritten in the Sprint plan but persists in the registry files.

### 4. Which task should be executed first?
**TASK-007 (Repair & Close)**

Before starting new work, you must resolve the identity crisis of `TASK-007`:
1.  Update `TASK-007.yaml` title and description to match the Schema work.
2.  Mark its steps as `DONE` (since `.agent/schema/refinery_node.schema.yaml` exists).
3.  Set status to `COMPLETE`.

**Immediate Next Action:**
Run a "Registry Repair" session to overwrite `TASK-007` through `TASK-012` with the definitions found in `SPRINT-002.yaml` (or move the old Pipeline tasks to new IDs if that work is still needed).

---

## Citations

_No citations provided_
