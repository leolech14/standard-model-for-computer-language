# Research: VALIDATE AGENT APPROACH: Agent completed emergency triage (archived 695MB .repos_cache to GCS, updat...

> **Date:** 2026-01-23 16:07:59
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:1bd9bc8680b3c067111d96ff21e1830fea228ee56681d2333b61cc1de952f48e`
> **Raw JSON:** `raw/20260123_160759_validate_agent_approach__agent_completed_emergency.json`

---

## Query

VALIDATE AGENT APPROACH: Agent completed emergency triage (archived 695MB .repos_cache to GCS, updated .gitignore). Then presented raw confidence scores and offered to execute actions WITHOUT following the OPP->TASK promotion pipeline. User corrected: tasks require A(85%)/A+(95%)/A++(99%) promotion via cloud refinery before execution. What is the correct recentering protocol? What opportunities should be registered? What is the priority matrix?

---

## Response

You are right to correct the agent. Skipping the **Refinery** and jumping straight to **Execution** is a violation of the **Socratic Research Loop** defined in `context-management/docs/WORKFLOW_FACTORY.md`. It creates "Heisenbug Code" (Action without Intent) and violates the `AGENT_KERNEL.md` directive to "Never stop without path forward."

Here is the correct **Recentering Protocol**, the **Opportunities** to register, and the **Priority Matrix**.

---

### 1. The Recentering Protocol: The Refinery Pipeline

The agent must adhere to the **OPP → REFINERY → TASK** pipeline. Raw confidence is not enough; it must be **refined** through the "Cloud Refinery" (The Triad: Gemini/Perplexity/Docs) to reach execution thresholds.

**The Protocol:**

1.  **CAPTURE (OPP)**: Identify the raw need.
    *   *State:* Unverified.
    *   *Action:* Log to `.agent/registry/inbox/OPP-XXX.yaml`.
2.  **REFINE (The Cloud Refinery)**: Run the **Socratic Research Loop** (Recipe 6 in `WORKFLOW_FACTORY.md`).
    *   **Internal (Gemini)**: "Does codebase support this? Cite files." (Boosts *Current*)
    *   **External (Perplexity)**: "Is this industry best practice?" (Boosts *Factual/Onwards*)
    *   **Architecture (Docs)**: "Does this align with Standard Model?" (Boosts *Alignment*)
3.  **PROMOTE (TASK)**: Once the composite score meets the threshold, promote to `.agent/registry/active/TASK-XXX.yaml`.
4.  **EXECUTE**: Only now does the agent touch the code.

**The Thresholds (The Gates):**

| Grade | Score | Allowed Action |
|:---:|:---:|---|
| **A++** | **99%** | **Destructive/High-Risk.** Deletions, major refactors, schema locks. |
| **A+** | **95%** | **Standard Feature.** Multi-file changes, new systems (BARE, HSL). |
| **A** | **85%** | **Low Risk.** Docs, config, non-destructive tweaks. |
| **B** | **<85%** | **REJECT/DEFER.** Return to Refinery. Do not execute. |

---

### 2. Opportunities to Register (Immediate)

Based on your emergency triage and the current state of the repo (`DECISION_BRIEF_LOCAL_FIRST.md` and `AGENTKNOWLEDGEDUMP.md`), these are the Opportunities that must be registered:

#### OPP-001: HSL Local-First Reliability (The Critical Path)
*   **Source:** `context-management/docs/operations/DECISION_BRIEF_LOCAL_FIRST.md`
*   **Context:** HSL daemon fails with exit code 1. Cloud deployment is blocked until local fix.
*   **Goal:** Achieve "Local Reliability" (Phase 1).
*   **Refinery Needs:** Determine exact logging strategy for the daemon failure.

#### OPP-002: BARE Phase 2 Implementation (CrossValidator)
*   **Source:** `context-management/docs/agent_school/AGENTKNOWLEDGEDUMP.md`
*   **Context:** Phase 1 (TruthValidator) is done. Phase 2 detects code-docs drift.
*   **Goal:** Implement `CrossValidator` class.
*   **Refinery Needs:** Validate `semantic_models.yaml` schema against `CrossValidator` logic.

#### OPP-003: GCS Mirror Verification (Post-Triage)
*   **Source:** Recent Agent Action (Emergency Triage)
*   **Context:** `.repos_cache` (695MB) was archived.
*   **Goal:** Verify the artifact in GCS is retrievable and the local exclusion works.
*   **Refinery Needs:** Verify `gsutil` checksum commands.

---

### 3. The Priority Matrix

Use this matrix to guide the **Refinery Phase**. Do not execute until the "Current Score" meets the "Required Grade".

| ID | Subject | Priority | Required Grade | Current Score | Refinery Action Needed |
|:---|:---|:---:|:---:|:---:|---|
| **OPP-001** | **Fix HSL Daemon Locally** | **P0** | **A+ (95%)** | 60% | **Step 1:** Use Forensic Mode to find exact exit code 1 location in `hsl_daemon.py`. <br>**Step 2:** Validate "Chokidar" pattern via Perplexity for Python. |
| **OPP-003** | **Verify GCS Mirror** | **P1** | **A (85%)** | 70% | **Step 1:** Confirm `gsutil ls -L` syntax for size verification. <br>**Step 2:** Check `.gitignore` for correct exclusion syntax. |
| **OPP-002** | **BARE Phase 2** | **P2** | **A+ (95%)** | 40% | **Step 1:** Deep read `semantic_models.yaml` to understand "Antimatter" definitions. <br>**Step 2:** Map `CrossValidator` logic to `analyze.py`. |

### Agent Next Steps (Corrected)

1.  **Acknowledge** the violation of the promotion protocol.
2.  **Create** the YAML files for `OPP-001`, `OPP-002`, and `OPP-003` in `.agent/registry/inbox/`.
3.  **Enter the Refinery** for **OPP-001 (P0)** immediately.
    *   *Prompt:* "I will now perform forensic analysis on `hsl_daemon.py` to boost Factual confidence regarding the exit code 1 failure."

**System Status:** RECENTERED.
**Ready to Refine.**

---

## Citations

_No citations provided_
