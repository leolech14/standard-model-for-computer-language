# Research: What are ALL the names, acronyms, and terms we have used to refer to the cloud-based AI automation l...

> **Date:** 2026-01-25 01:49:31
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:62e02f607341b0e9eb730ba9e56bfb9a44e00c3dd545f0b864eb5cb8c75ee29f`
> **Raw JSON:** `raw/20260125_014931_what_are_all_the_names__acronyms__and_terms_we_hav.json`

---

## Query

What are ALL the names, acronyms, and terms we have used to refer to the cloud-based AI automation layer that runs background audits, enrichment, and refinement? List every name found in docs, code comments, and config files. Include: HSL, BARE, AEP, and any other terms.

---

## Response

Based on the codebase analysis, here is the comprehensive list of all names, acronyms, and terms used to refer to the cloud-based AI automation layer, categorized by their architectural scope.

### 1. The Core Acronyms (The 5 Engines)
These are the specific processing units defined in `BACKGROUND_AI_LAYER_MAP.md`.

*   **BARE** - **Background Auto-Refinement Engine**
    *   *Also referred to as:* "The Hands," "Self-Refinement."
    *   *Function:* Handles post-commit truths, confidence boosting, and task claiming.
*   **HSL** - **Holographic-Socratic Layer**
    *   *Also referred to as:* "The Critic," "Socratic Audit."
    *   *Function:* Semantic validation against "Antimatter Laws" to detect architectural drift.
*   **AEP** - **Autonomous Enrichment Pipeline**
    *   *Function:* Transforms raw opportunities (Inbox) into validated tasks via research loops.
*   **ACI** - **Adaptive Context Intelligence**
    *   *Function:* The context curation system ("Curriculum Compiler") that selects optimal datasets for AI queries.
*   **REFINERY** - **Context Refinery**
    *   *Also referred to as:* "Meta-Solution," "RefineryNode."
    *   *Function:* Atomizes code into semantic units (chunks) for RAG and caching.

### 2. Overarching Architectural Terms
These terms refer to the entire system of background processing.

*   **Background AI Data Processing Layer** (Canonical name in `BACKGROUND_AI_LAYER_MAP.md`)
*   **The Brain** (Used in `manifest.yaml` and architecture docs to contrast with "The Body" / Collider).
*   **Intelligence Layer (Wave)** (Used in `KERNEL.md` to describe the potential/field vs the particle/implementation).
*   **Adaptive Intelligence Layer** (Used in `registry/INDEX.md` referring to Phase 10).
*   **Repository Context System** (Used in `REPOSITORY_CONTEXT_SYSTEM.md`).
*   **Context Management** (The directory name `context-management/` containing these tools).

### 3. Functional Personas (Role-Based Names)
The documentation frequently personifies these automation tools based on their behavior.

*   **The Critic** (HSL running semantic verification).
*   **The Cartographer** (The `continuous_cartographer.py` tool running mapping).
*   **The Guardian** (A specific mode of the cartographer that triggers on file changes).
*   **The Researcher** (Manual trigger mode for external Perplexity queries).
*   **The Surgeon** (Forensic analysis mode).
*   **The Architect** (Global reasoning mode).
*   **The Observer** (The agent kernel component that decides what to measure).
*   **Antigravity** (The name of the AI Agent listed as the "Auditor" in `REPOSITORY_AUDIT_2026-01-19.md`).

### 4. Infrastructure & Implementation Terms
Terms used in config files, scripts, and deployment manuals.

*   **HSL Daemon** (The continuous background process).
*   **Quartet Watchdog** (The 6-hour schedule defined in `HOLOGRAPHIC_DEPLOYMENT_MANUAL.md`).
*   **Socratic Audit Job** (The Cloud Run job name).
*   **Curriculum Compiler** (Used in `ACI_DATASET_MANAGEMENT.md` to describe data preparation).
*   **TruthValidator** (Component of BARE).
*   **ConfidenceBooster** (Component of BARE).
*   **Centripetal Scan** (Deep 12-round analysis tool).

### 5. Historical / Legacy Terms
Terms found in timeline analysis or older docs but still present.

*   **Spectrometer** (Original name for the analysis engine before "Collider").
*   **Alien Architecture** (Used in `AI_USER_GUIDE.md` to describe the non-standard topology).
*   **Decision Deck Layer** (A proposed governance layer in `TASK-018.yaml`).

### Summary Hierarchy

```text
The Brain / Intelligence Layer (The System)
├── BARE (The Hands - Fixes things)
├── HSL (The Critic - Validates things)
├── AEP (The Planner - Enriches tasks)
├── ACI (The Teacher - Compiles context)
└── Refinery (The Miller - Grinds code into atoms)
```

---

## Citations

_No citations provided_
