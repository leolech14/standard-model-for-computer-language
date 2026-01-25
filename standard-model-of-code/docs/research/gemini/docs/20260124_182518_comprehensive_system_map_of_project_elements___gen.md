# Research: COMPREHENSIVE SYSTEM MAP of PROJECT_elements.

Generate a complete inventory of ALL subsystems, modu...

> **Date:** 2026-01-24 18:25:18
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:cb298407f26a7ef639f128950a2b0be88d223fd44c329fd985f25dd7255da5d1`
> **Raw JSON:** `raw/20260124_182518_comprehensive_system_map_of_project_elements___gen.json`

---

## Query

COMPREHENSIVE SYSTEM MAP of PROJECT_elements.

Generate a complete inventory of ALL subsystems, modules, and their relationships.

For EACH subsystem:
1. NAME and LOCATION (path)
2. PURPOSE (one sentence)
3. INPUTS and OUTPUTS
4. DEPENDENCIES (what it imports/consumes)
5. STATUS (working, partial, planned, orphaned)

Include:
- All tools in context-management/
- All tools in standard-model-of-code/
- The .agent/ governance layer
- Background processes (BARE, AEP, HSL, etc.)
- Research infrastructure
- Visualization layer

Draw the COMPLETE system topology. Show data flow arrows.
Identify any ORPHANED or DISCONNECTED components.
Rate overall architectural coherence (0-100).

---

## Response

# Comprehensive System Map: PROJECT_elements

**Analysis Date:** 2026-01-24
**Kernel Version:** 1.5.0
**Context:** Post-Consolidation, Post-Cutting Plan

---

## 1. System Topology

The system operates on a "Particle/Wave" duality, governed by an "Observer" layer.

```mermaid
graph TD
    %% DO NOT RENDER GRAPH, ASCII VERSION BELOW
```

```
┌───────────────── GOVERNANCE (The Observer) ─────────────────┐
│                                                             │
│  [.agent/KERNEL.md] <──> [.agent/registry/] <──> [.agent/runs/]
│          │                        ▲                    ▲
│          │ (Rules)                │ (Tasks)            │ (Logs)
│          ▼                        ▼                    ▼
│  ┌───────────────────────────────────────────────────────┐  │
│  │                AGENTS (Human & AI)                    │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
└──────────────────────────────┼──────────────────────────────┘
                               │ (Action)
                               ▼
┌────────────────── IMPLEMENTATION (The Particle) ──────────────────┐
│                                                                   │
│ [standard-model-of-code/]                                         │
│        │                                                          │
│        ├─> [Collider Engine] ──> [unified_analysis.json] ──────┐  │
│        │        (Static Analysis)                              │  │
│        │                                                       │  │
│        └─> [Visualization] <───────────────────────────────────┘  │
│                 (HTML/JS)                                         │
│                                                                   │
└──────────────────────────────┬────────────────────────────────────┘
                               │ (Context)
                               ▼
┌────────────────── INTELLIGENCE (The Wave) ────────────────────────┐
│                                                                   │
│ [context-management/]                                             │
│        │                                                          │
│        ├─> [ACI / analyze.py] <──> [Gemini 2.5/3]                 │
│        │       │                                                  │
│        │       └─> [Perplexity MCP] ──> [External Web]            │
│        │                                                          │
│        └─> [BARE / Refinery] ──> [.agent/intelligence/atoms/]     │
│               (Background Refinement)                             │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 2. Subsystem Inventory

### A. The Observer (Governance & State)

**S0: Kernel & Protocol**
- **Location:** `.agent/KERNEL.md`, `.agent/manifest.yaml`
- **Purpose:** Boot protocol, non-negotiable rules, and system configuration.
- **Inputs:** None (Root of Trust).
- **Outputs:** Agent behavioral constraints.
- **Status:** **ACTIVE** (v1.5.0).

**S5: Task Registry (Unified)**
- **Location:** `.agent/registry/` (`active/`, `inbox/`, `archive/`)
- **Purpose:** Single Source of Truth (SSOT) for work items and state machine.
- **Inputs:** `promote_opportunity.py`, `triage_inbox.py`.
- **Outputs:** `TASK-*.yaml`, `OPP-*.yaml`.
- **Dependencies:** `task.schema.yaml`, `opportunity.schema.yaml`.
- **Status:** **ACTIVE** (Consolidated).

**S8: Commit Hygiene**
- **Location:** `.pre-commit-config.yaml`, `commitlint.config.js`
- **Purpose:** Enforces conventional commits and code quality before ingestion.
- **Inputs:** Git commit events.
- **Outputs:** Pass/Fail signal to Git.
- **Status:** **ACTIVE**.

### B. The Particle (Implementation & Analysis)

**S1: Collider (The Engine)**
- **Location:** `standard-model-of-code/src/`
- **Purpose:** "Collapses" code into structured data (Unified Analysis).
- **Inputs:** Raw Source Code (`.py`, `.js`, etc.).
- **Outputs:** `unified_analysis.json` (The Ground Truth).
- **Dependencies:** Tree-sitter, Python AST.
- **Status:** **ACTIVE** (Refactored into Pipeline architecture).

**S1.1: Survey Module (Adaptive Layer)**
- **Location:** `standard-model-of-code/src/core/survey.py`
- **Purpose:** Fast pre-scan to determine exclusion patterns and dataset size.
- **Inputs:** File system.
- **Outputs:** `SurveyResult` (CCI metrics).
- **Status:** **ACTIVE** (Integrated Phase 10).

**S9: Visualization**
- **Location:** `standard-model-of-code/viz/`
- **Purpose:** Interactive frontend for the Standard Model of Code.
- **Inputs:** `unified_analysis.json`.
- **Outputs:** HTML/D3.js interactive graph.
- **Status:** **WORKING** (Recent fixes for data toggles).

### C. The Wave (Intelligence & Context)

**S3: ACI Engine (analyze.py)**
- **Location:** `context-management/tools/ai/analyze.py`
- **Purpose:** Adaptive Context Intelligence interface; gateway to LLMs.
- **Inputs:** User query, `analysis_sets.yaml`, `unified_analysis.json`.
- **Outputs:** Markdown reports, Code suggestions, Research docs.
- **Dependencies:** Gemini API, HSL Config.
- **Status:** **ACTIVE** (Rate limiting fixed in TASK-021).

**S2: Holographic Socratic Layer (HSL)**
- **Location:** `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md` (Rules) + `analyze.py --verify` (Engine).
- **Purpose:** Automated semantic validation and drift detection.
- **Inputs:** `semantic_models.yaml`, Codebase state.
- **Outputs:** Compliance verdicts (Pass/Fail).
- **Status:** **ACTIVE** (Daemonized via launchd).

**S4: Perplexity MCP**
- **Location:** `context-management/tools/mcp/perplexity_mcp_server.py`
- **Purpose:** External knowledge retrieval and fact-checking.
- **Inputs:** Research queries.
- **Outputs:** Cited research markdown.
- **Status:** **ACTIVE**.

**S6: BARE (Background Auto-Refinement Engine)**
- **Location:** `.agent/tools/bare` (CLI), `.agent/intelligence/` (Data).
- **Purpose:** Continuous background refinement of repository knowledge.
- **Inputs:** Git history, Registry state.
- **Outputs:** `repo_truths.yaml`, Confidence scores.
- **Components:**
    - `TruthValidator`: **ACTIVE**
    - `ConfidenceBooster`: **ACTIVE**
    - `Refinery (BARE-Live)`: **FOUNDATION LAID** (Sprint 003).
- **Status:** **PARTIAL** (Phase 1 operational, Phase 2 in scaffolding).

**S7: Archive & Mirror**
- **Location:** `context-management/tools/archive/`
- **Purpose:** Sprawl management and Cloud backup.
- **Inputs:** Repository state.
- **Outputs:** GCS Bucket (`gs://elements-archive-2026/`), Local Archive.
- **Status:** **ACTIVE**.

---

## 3. Data Flow Pathways

### The "Execution" Loop
1.  **Trigger:** Human or BARE creates `OPP-XXX` in Registry (S5).
2.  **Refinement:** `triage_inbox.py` / `boost_confidence.py` (S6/S3) scores the opportunity.
3.  **Promotion:** `promote_opportunity.py` converts to `TASK-XXX` (Ready state).
4.  **Claim:** Agent claims task, creates `RUN-XXX` (S0).
5.  **Action:** Agent modifies code in `standard-model-of-code/` (S1).
6.  **Verify:** `pre-commit` (S8) and `analyze.py --verify` (S2) validate changes.
7.  **Commit:** Changes persist to Git.

### The "Intelligence" Loop
1.  **Scan:** Collider (S1) runs on commit, generating `unified_analysis.json`.
2.  **Ingest:** BARE (S6) and HSL (S2) read analysis.
3.  **Detect:** HSL detects drift or violation.
4.  **Report:** HSL creates new `OPP-XXX` in Registry (S5).
5.  **Refine:** BARE-Live (Refinery) updates `.agent/intelligence/atoms/`.

---

## 4. Orphans & Disconnected Components

| Component | Location | Status | Diagnosis |
|-----------|----------|--------|-----------|
| **Decision Deck** | `.agent/deck/` | **ARCHIVED/WONT_DO** | (TASK-018) "Spec Theater". Code exists but marked unused/dead. |
| **Legacy Registries** | `standard-model-of-code/docs/*/REGISTRY.md` | **READ-ONLY** | Valid historical artifacts, but disconnected from active workflow. |
| **Testing Suite Doc** | `.agent/workflows/testing_suite.md` | **ARCHIVED** | Moved to `archive/agent_cuts/` via Cutting Plan. |
| **Old Truths** | `.agent/intelligence/truths/history/` | **ARCHIVED** | Historical snapshots removed to reduce noise. |

---

## 5. Architectural Coherence Rating

**Score: 88/100**

**Strengths:**
*   **High Symmetry:** The "Particle/Wave" split is well-respected in directory structure (`src` vs `context-management`).
*   **Unified Registry:** Consolidating multiple markdown files into the `.agent/registry` was a critical win.
*   **Strong Governance:** The Kernel and boot protocol provide clear "physics" for the agents.

**Weaknesses (The remaining 12%):**
*   **BARE-Live Maturity:** The "Refinery" (S6 Phase 2) is heavily specified but implementation is just starting (Sprint 003). It is the bridge between static analysis and dynamic context, currently a "construction zone".
*   **Visualization Lag:** The visual layer (S9) often lags behind the Collider's data structure changes (noted in OPP-058/059, though fixed).
*   **Decision Deck Confusion:** The artifacts exist but the system rejected the premise (TASK-018). These should be fully purged or explicitly marked as "Museum" to prevent Agent confusion.

**Conclusion:** The system is robust, self-documenting, and actively self-correcting. The architecture is stable enough to support high-velocity autonomous work.

---

## Citations

_No citations provided_
