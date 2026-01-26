# Research: SECOND ABSTRACTION DISCUSSION

We just created the FIRST abstraction: ./pe (unified CLI)
- Before: S...

> **Date:** 2026-01-26 00:56:33
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:e0e120455630647b2050b39f2df1d2f0adfcf59ef9c6ad32a7fcea01570b2b89`
> **Raw JSON:** `raw/20260126_005633_second_abstraction_discussion__we_just_created_the.json`

---

## Query

SECOND ABSTRACTION DISCUSSION

We just created the FIRST abstraction: ./pe (unified CLI)
- Before: Scattered tools, venv activation, long paths
- After: ./pe ask, ./pe status, ./pe collider, etc.

QUESTION: What is the SECOND abstraction?

The first abstraction unified ACCESS (how you invoke tools).
What would the second abstraction unify?

CANDIDATES:

A. INTENT ABSTRACTION
   - First: './pe ask "question"' (you specify the tool)
   - Second: './pe "fix the bug in auth.py"' (system figures out which tools)
   - The CLI becomes an AGENT that routes to the right tool

B. STATE ABSTRACTION  
   - First: Tools are stateless (each invocation is independent)
   - Second: Tools share context (what you asked before affects now)
   - Session memory, conversation continuity

C. WORKFLOW ABSTRACTION
   - First: Single commands (do one thing)
   - Second: Composed workflows (do a sequence)
   - './pe workflow review-pr' → runs: fetch, analyze, symmetry check, report

D. DECLARATIVE ABSTRACTION
   - First: Imperative (tell it what to DO)
   - Second: Declarative (tell it what you WANT)
   - './pe ensure "all tests pass"' vs './pe test'

E. REACTIVE ABSTRACTION
   - First: Pull (you invoke commands)
   - Second: Push (system notifies you)
   - './pe watch' → continuous monitoring, alerts when things drift

What is the most valuable second abstraction for PROJECT_elements?
Consider: What friction remains after ./pe?

---

## Response

Based on the `CODEBASE CONTEXT` provided—specifically the existence of **ACI (Adaptive Context Intelligence)**, the **Consumer Class Axioms** in `CODESPACE_ALGEBRA.md`, and the complexity of the **Tool Inventory** in `BACKGROUND_AI_LAYER_MAP.md`—the most valuable Second Abstraction is:

### **Candidate A: INTENT ABSTRACTION**

### The Logic
The First Abstraction (`./pe`) unified **ACCESS** (syntax, paths, environments).
The Second Abstraction must unify **CAPABILITY** (routing, selection, parameterization).

Currently, the friction is **Cognitive Load**. The user (human or agent) must know:
1.  Does "Audit" require `analyze.py --verify` or `collider full`?
2.  Does "Research" go to Gemini or Perplexity?
3.  Does "Fix" require `BARE` or manual intervention?

The **Intent Abstraction** moves this decision from the User to the System.

---

### The Evolution

| Feature | First Abstraction (Current) | Second Abstraction (Target) |
| :--- | :--- | :--- |
| **Input** | Explicit Command | Natural Language / Goal |
| **Logic** | User decides tool | ACI decides tool |
| **Role** | Launcher | Dispatcher |
| **Example** | `./pe analyze --aci "..."` | `./pe "Check for architectural drift"` |
| **Underlying Tech** | Bash Scripts | `aci_config.yaml` + `tier_orchestrator.py` |

### Why This Fits Your Codebase

1.  **You already built the Brain:** `context-management/config/aci_config.yaml` defines `intent_keywords`, `complexity_indicators`, and `routing_overrides`. You have a logic engine waiting to be the CLI controller.
2.  **The "Universal Consumer" Axiom:** `CODESPACE_ALGEBRA.md` (Axiom H5) states that programming is "Contextome curation at L1 (Natural Language)." An Intent Abstraction aligns the CLI with this theoretical axiom.
3.  **Tool Sprawl:** `BACKGROUND_AI_LAYER_MAP.md` lists 23 separate tools (`fact_loader`, `drift_guard`, `enrichment_orchestrator`, etc.). Expecting a user to memorize these is an anti-pattern.

### How It Works (The Implementation)

The `./pe` entry point changes from a switch-case of hardcoded commands to a pass-through for the **ACI Tier Orchestrator**.

**Scenario: User types `./pe "Is the pipeline module cohesive?"`**

1.  **Intent Analysis (ACI):**
    *   Detects keyword "cohesive" → Intent: `ARCHITECTURE`.
    *   Detects scope "pipeline module" → Analysis Set: `pipeline`.
2.  **Routing:**
    *   Intent `ARCHITECTURE` + Scope `INTERNAL` → Route to **Tier 2 (Long Context)**.
3.  **Execution:**
    *   System constructs the command: `python context-management/tools/ai/analyze.py --set pipeline --mode architect "Is the pipeline module cohesive?"`
4.  **Output:**
    *   Returns the insight.

### Why Not B, C, or D?

*   **B (State):** State is necessary *support* for Intent, but purely abstracting state (session management) doesn't solve the "which tool?" problem.
*   **C (Workflow):** Workflows are rigid. Intent is fluid. ACI handles workflows dynamically (e.g., `research_schemas.yaml`).
*   **D (Declarative):** This implies the system can *enforce* state (like Terraform). Given the code is "Dynamic Purpose" (`CODESPACE_ALGEBRA.md`), rigid enforcement is harder than intelligent assistance.

### The Vision for Abstraction 2

**"The CLI that thinks."**

Instead of a Swiss Army Knife (where you pick the blade), it becomes a Concierge (where you state the need).

*   **User:** `./pe "Verify the truth of the last commit"`
*   **System:** *Routes to BARE TruthValidator*
*   **User:** `./pe "Why is the graph knotty?"`
*   **System:** *Routes to Collider + ACI Graph Analysis*

This completes the **Particle/Wave** duality in the CLI:
*   **Particle:** The specific underlying tools (deterministic execution).
*   **Wave:** The Intent Abstraction (probabilistic routing based on meaning).

---

## Citations

_No citations provided_
