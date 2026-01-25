# Research: COMPLETENESS AUDIT: The SoS map lists 10 subsystems (S1-S9b). But I found these additional tools tha...

> **Date:** 2026-01-24 21:40:24
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:14d372b5d2254d249352ee599f7f170b471dcd28dfe61ec5291f2f1f1f44d3cd`
> **Raw JSON:** `raw/20260124_214024_completeness_audit__the_sos_map_lists_10_subsystem.json`

---

## Query

COMPLETENESS AUDIT: The SoS map lists 10 subsystems (S1-S9b). But I found these additional tools that may be significant subsystems NOT in the map:

FOUND BUT UNLISTED:
- context-management/tools/refinery/ (5 modules: atom_generator, boundary_mapper, delta_detector, corpus_inventory, state_synthesizer)
- context-management/tools/hsl_daemon.py (HSL scheduler)
- .agent/tools/aep_orchestrator.py (Autonomous Enrichment Pipeline)
- .agent/tools/centripetal_scan.py (Deep analysis tool)
- context-management/tools/ai/aci/ (Adaptive Context Intelligence - 8 modules)

QUESTION: Should these be added to the SoS map as new subsystems (S10, S11, etc)? Rate each by significance (HIGH/MEDIUM/LOW) and recommend which to add.

---

## Response

Based on the `BACKGROUND_AI_LAYER_MAP.md` (which explicitly outlines "The Five Engines") and the current `SUBSYSTEM_INTEGRATION.md`, your assessment is correct. The System-of-Systems (SoS) map is missing critical autonomous engines that have been defined in the AI architecture.

Here is the completeness audit and integration recommendations.

### Executive Summary

The `SUBSYSTEM_INTEGRATION.md` is currently lagging behind the `BACKGROUND_AI_LAYER_MAP.md`. While the Integration Map lists 10 subsystems, the AI Map identifies **"Five Processing Engines"**, three of which (AEP, Refinery, Centripetal) are missing or conflated in the current integration view.

### Analysis of Found Tools

#### 1. Autonomous Enrichment Pipeline (`.agent/tools/aep_orchestrator.py`)
*   **Role:** Automates the lifecycle of tasks from "Opportunity" (OPP) to "Task" (TASK). It orchestrates research, scoring, and promotion.
*   **Current Status:** Missing. Distinct from BARE (S6) because BARE *executes* tasks, whereas AEP *plans and refines* them.
*   **Significance:** **HIGH**. This is the "Brain" of the autonomous workflow. Without it, the Task Registry (S5) is static.
*   **Recommendation:** **ADD as S10**.

#### 2. Refinery / ACI (`context-management/tools/refinery/` & `.../aci/`)
*   **Role:** listed as **Engine #4 (Refinery)** in the AI Map. It performs "Context Atomization" (chunking code into semantic units like `RefineryNode`). The `aci` folder likely contains the core logic (Adaptive Context Intelligence) while `refinery` contains the tools.
*   **Current Status:** Missing. Currently, `analyze.py` (S3) is doing heavy lifting, but Refinery is a distinct specialized engine for token optimization.
*   **Significance:** **HIGH**. It is the prerequisite data layer for all efficient AI operations (AEP and HSL).
*   **Recommendation:** **ADD as S11**. Consolidate `refinery` and `aci` into a single subsystem "ACI Refinery".

#### 3. Centripetal Scan (`.agent/tools/centripetal_scan.py`)
*   **Role:** **Engine #5** in the AI Map. Performs deep, 12-round progressive resolution analysis (Macro → Nano).
*   **Current Status:** Missing.
*   **Significance:** **MEDIUM**. While powerful, it acts more like a heavy-duty specialized tool triggered manually/on-demand rather than a continuous background loop like BARE or AEP.
*   **Recommendation:** **ADD as S12**. It represents "Deep Intelligence" vs. S3's "Operational Intelligence."

#### 4. HSL Daemon (`context-management/tools/hsl_daemon.py`)
*   **Role:** The scheduler/watcher that triggers Socratic Audits.
*   **Current Status:** **S2 (HSL)** is currently listed as a "Framework". The daemon is the runtime implementation.
*   **Significance:** **HIGH (Functional) / LOW (Architectural)**. It is vital, but it is not distinct enough from HSL to warrant a new top-level ID.
*   **Recommendation:** **MERGE into S2**. Update S2's definition in the map to be "HSL Service" (Framework + Daemon) rather than just "Framework".

---

### Recommended Updates to SoS Map

Add the following rows to the **Subsystem Registry** table in `SUBSYSTEM_INTEGRATION.md`:

| ID | Subsystem | Type | Path | Purpose |
|----|-----------|------|------|---------|
| **S10** | **AEP** | Engine | `.agent/tools/aep_orchestrator.py` | Task enrichment & promotion (Inbox → Registry) |
| **S11** | **ACI Refinery** | Engine | `context-management/tools/refinery/` | Context atomization & semantic chunking |
| **S12** | **Centripetal** | Engine | `.agent/tools/centripetal_scan.py` | Deep 12-round recursive analysis |

### Updated Integration Data Flow
*You should also propose adding these connections to the Integration Map:*

1.  **S11 (Refinery) → S10 (AEP):** AEP uses Refinery atoms to understand tasks cheaply (low token cost).
2.  **S11 (Refinery) → S2 (HSL):** HSL uses Refinery to validate "Antimatter Laws" on specific code chunks.
3.  **S10 (AEP) → S5 (Task Registry):** AEP writes validated `TASK-*.yaml` files.
4.  **S12 (Centripetal) → S4 (Perplexity):** Heavy user of external queries for "World Knowledge" calibration.

### Revised Architecture Diagram Draft

The "Intelligence Layer" section of your ASCII diagram needs to expand:

```text
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    INTELLIGENCE LAYER (Wave)                        │
   │                                                                     │
   │   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
   │   │ S3       │    │ S12      │    │ S10      │◄───│ S11      │      │
   │   │ Analyze  │    │ DeepScan │    │ AEP      │    │ Refinery │      │
   │   └──────────┘    └──────────┘    └────┬─────┘    └────▲─────┘      │
   │                                        │               │            │
   │                                        ▼               │            │
   │                                   Task Registry      Source         │
   └─────────────────────────────────────────────────────────────────────┘
```

---

## Citations

_No citations provided_
