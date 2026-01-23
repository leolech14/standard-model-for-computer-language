# Research: Audit the current state of .agent/ directory. What files are essential vs redundant? What consolidat...

> **Date:** 2026-01-23 08:26:39
> **Source:** gemini
> **Model:** gemini-2.5-pro
> **Checksum:** `sha256:7d3e7a7f7aede0873a68b385e220e0d7600c562ddcc5cbe2f43bbd6fd65815dc`
> **Raw JSON:** `raw/20260123_082639_audit_the_current_state_of__agent__directory__what.json`

---

## Query

Audit the current state of .agent/ directory. What files are essential vs redundant? What consolidation is still needed?

---

## Response

Of course. As a senior software engineer, here is a detailed audit of the `.agent/` directory based on the provided codebase context.

### Executive Summary

The `.agent/` directory serves as the "brain" for the Adaptive Context Intelligence (ACI) system, containing its boot protocols, task registries, and operational knowledge. The directory structure is well-defined through `analysis_sets.yaml` into logical components: `kernel`, `tasks`, `intelligence`, and `specs`.

The most critical finding is strong evidence of a **redundant `.agent/` directory**. The `REPOSITORY_AUDIT_2026-01-19.md` document explicitly decided to centralize all agent configuration into `context-management/`. This implies that any `.agent/` directory found under `standard-model-of-code/` is now obsolete and should be removed.

Consolidation is still needed, primarily in removing this redundant directory and streamlining the agent onboarding documentation within `agent_school/`.

---

### Current State Analysis: The "Brain Hemisphere"

The `.agent/` directory is designed to be the central nervous system for AI agents operating on this repository. Its structure is defined by the `analysis_sets.yaml` file, which groups the contents into four primary, composable sets for context injection:

1.  **`agent_kernel`**: The bootloader. Contains the absolute minimum context for an agent to understand its core directives and manifest. (`.agent/KERNEL.md`, `manifest.yaml`).
2.  **`agent_tasks`**: The to-do list. Contains active tasks, sprint plans, and the task registry, giving the agent awareness of its current work. (`.agent/registry/`, `.agent/sprints/`).
3.  **`agent_intelligence`**: The memory. Stores learned "truths," metrics, and concepts that inform the agent's reasoning. (`.agent/intelligence/`).
4.  **`agent_specs`**: The operating manual. Contains detailed specifications for the agent's own internal machinery, such as the "Background Auto-Refinement Engine (BARE)". (`.agent/specs/`, `.agent/workflows/`).

This modular structure is leveraged by the ACI system (configured in `aci_config.yaml`), which can inject `minimal`, `standard`, or `full` context levels by combining these sets.

---

### Essential vs. Redundant Files

#### Essential Files & Directories (Located in `context-management/.agent/`)

Based on the centralization decision, the single source of truth for agent context should be within `context-management/`. The following files are essential to the agent's operation:

| File/Directory | Purpose | Why It's Essential |
| :--- | :--- | :--- |
| **`.agent/KERNEL.md`** | Agent Boot Protocol | The first file an agent reads. `agent_kernel` set's critical file. Referenced in `AGENT_INITIATION.md`. |
| **`.agent/manifest.yaml`** | Agent Configuration | Defines the agent's core identity and capabilities. Part of `agent_kernel`. |
| **`.agent/registry/`** | Task & Learning System | The agent's "working memory" of tasks and knowledge. `agent_tasks` set's critical component. |
| **`.agent/intelligence/`** | Learned Truths & Metrics | The agent's long-term memory and self-evaluation data. Core of the `agent_intelligence` set. |
| **`.agent/specs/`** | System Specifications | Contains the design docs for the agent's own systems. Core of the `agent_specs` set. |
| **`.agent/docs/agent_school/`** | Onboarding & Workflows | Contains the rules of engagement for agents (`AGENT_BOOT.md`, `DOD.md`, `WORKFLOWS.md`). |

#### Redundant Files & Directories

The **`REPOSITORY_AUDIT_2026-01-19.md`** provides the most critical piece of evidence here under "Q2: Agent Config Distribution Model ✓ RESOLVED":

> **Decision**: **CENTRALIZED**
>
> | Option | ✓ | Justification |
> |---|---|---|
> | Distributed | ✗ | Fragments "Intelligence" |
> | **Centralized** | ✓ | Aligns with Brain concept. All meta-management in one place. |
>
> **Action**: Move `standard-model-of-code/.agent/` → `context-management/.agent/`

This makes it clear:

*   **Any directory at `standard-model-of-code/.agent/` is redundant and should be considered deprecated.** Its existence directly contradicts a key architectural decision made to improve coherence. This is the primary target for cleanup.
*   The `ORIENTATION_FILES.md` document mentions a mirror at `standard-model-of-code/.agent/orientation/`. The audit report recommends using symlinks for this to maintain a single source of truth. If this is a direct copy, it is redundant.

---

### Consolidation Still Needed: Actionable Recommendations

1.  **Execute the Centralization Decision:**
    *   **Action:** Verify the existence of a `.agent/` directory at `standard-model-of-code/.agent/`.
    *   **Action:** If it exists, perform a final diff against `context-management/.agent/` to ensure no unique, valuable information is present.
    *   **Action:** Once confirmed, **delete the entire `standard-model-of-code/.agent/` directory**. This is the single most important consolidation action required.

2.  **Streamline Agent Onboarding Documentation:**
    *   **Observation:** The `context-management/docs/agent_school/` directory contains multiple, slightly overlapping files for agent initiation (`AGENT_BOOT.md`, `AGENT_KERNEL.md`, `INDEX.md`, `REPO_FACTS.md`). `AGENT_KERNEL.md` appears to be a subset of `AGENT_BOOT.md`.
    *   **Recommendation:** Consolidate these into a single, canonical `AGENT_ONBOARDING_MANUAL.md`. This manual should contain:
        *   The non-negotiable rules (from `AGENT_KERNEL.md`).
        *   The boot sequence and report format (from `AGENT_BOOT.md` and `INDEX.md`).
        *   The command/fact reference (from `REPO_FACTS.md`).
        *   The full git workflow and DoD (from `WORKFLOWS.md` and `DOD.md`).
    *   **Benefit:** This creates a single, unambiguous entry point for new agents, reducing context size and eliminating potential contradictions.

3.  **Verify Orientation File Strategy:**
    *   **Observation:** `REPOSITORY_AUDIT_2026-01-19.md` recommends using symlinks for duplicated documentation like the `orientation` files.
    *   **Action:** Check if `context-management/.agent/orientation/` (if it exists post-cleanup) is a symlink or a copy.
    *   **Recommendation:** If it's a copy, replace it with a symlink pointing to the canonical source documentation to prevent drift, as per the audit's decision.

By executing these three steps, you will finalize the centralization of the agent's context, eliminate redundancy, and simplify its operational protocols.

---

## Citations

_No citations provided_
