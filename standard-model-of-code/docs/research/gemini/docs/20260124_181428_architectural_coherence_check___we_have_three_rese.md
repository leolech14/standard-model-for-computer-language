# Research: ARCHITECTURAL COHERENCE CHECK.

We have three research/processing systems:
- System A: context-manag...

> **Date:** 2026-01-24 18:14:28
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:48439400aa0a7a9b35ec1b0f7df9229263baff88ee67fe732a637ad93e16dee1`
> **Raw JSON:** `raw/20260124_181428_architectural_coherence_check___we_have_three_rese.json`

---

## Query

ARCHITECTURAL COHERENCE CHECK.

We have three research/processing systems:
- System A: context-management/tools/ai/ (The Agent)
- System B: standard-model-of-code/tools/research/ (The Scientist)  
- System C: context-management/tools/refinery/ (The Librarian)

QUESTIONS:
1. Is there a SINGLE document that explains how all three connect?
2. Is there an UMBRELLA concept that unifies them?
3. Are they ORPHANED systems or properly integrated?
4. What is the IMPORT GRAPH - do they actually import each other?
5. Where is the SINGLE SOURCE OF TRUTH for this architecture?

Be brutally honest. If it's fragmented, say so.

---

## Response

Here is the brutally honest architectural coherence check based on the provided context.

### EXECUTIVE SUMMARY: PARTIALLY FRAGMENTED
**Coherence Score: 65/100 (Silver)**

The systems are **conceptually** unified but **implementationally** split. System A (Agent) and System C (Librarian) are tightly coupled via code imports. System B (Scientist) is legally separated—it operates as an independent "Particle" engine that produces data the others consume, but it does not share a runtime or import graph with them.

---

### 1. Is there a SINGLE document that explains how all three connect?
**NO.** There is no single document that explicitly diagrams the `Agent <-> Scientist <-> Librarian` relationship in one view.

*   **Closest Match:** `context-management/docs/BACKGROUND_AI_LAYER_MAP.md`.
    *   It maps the "Background AI Layer" (AEP, HSL, BARE) and mentions "Collider" (The Scientist's engine) and "Refinery" (The Librarian).
    *   *Failure:* It treats them as abstract boxes in a pipeline, not as a software architecture diagram explaining how the Python modules interact.
*   **The Gap:** You have to infer the connection by reading `AI_ORCHESTRATION_PROTOCOL.md` (which explains the process handoff between Scientist and Agent) and `aci/__init__.py` (which explains the code import between Agent and Librarian).

### 2. Is there an UMBRELLA concept that unifies them?
**YES, but it's abstract.**

The umbrella concept is **Wave-Particle Duality** (defined in `CLAUDE.md`).
*   **Particle (System B - The Scientist):** Deterministic, static analysis, hard metrics (`standard-model-of-code`).
*   **Wave (System A - The Agent):** Probabilistic, reasoning, context management (`context-management`).
*   **The Binder (System C - The Librarian/Refinery):** The mechanism that breaks "Particles" (code) into "Wave packets" (context atoms) for the AI to digest.

While the *philosophy* is consistent, the *tooling* enforces a hard separation (different virtual environments, different root directories).

### 3. Are they ORPHANED systems or properly integrated?
**System A & C are INTEGRATED. System B is ORPHANED (by design).**

*   **A + C (Agent + Librarian):** Tight Integration. The Agent's brain (`aci` module) directly imports the Librarian (`refinery`). They share the `.tools_venv` environment.
*   **B (Scientist):** Isolationist. It runs in the `standard-model-of-code` environment. It does **not** know System A or C exist. It dumps JSON files to disk, which System A later reads.
    *   *Why this matters:* You cannot import `Collider` classes inside the `Agent`. You can only read `collider` outputs. This prevents "live" collaboration between the static analyzer and the AI agent.

### 4. What is the IMPORT GRAPH?
The import graph confirms the "Process Gap":

```
[System A: Agent] <----(import)---- [System C: Librarian]
       |                                     |
       |                                     |
(Process Handoff / File I/O Only)            |
       |                                     |
       v                                     X (No Connection)
[System B: Scientist]
```

*   **Evidence:** `context-management/tools/ai/aci/__init__.py` lines 105-115 explicitly import `Refinery`, `PythonChunker`, etc.
*   **Evidence:** `AI_ORCHESTRATION_PROTOCOL.md` defines the link between B and A as a **manual command sequence** (Step 1: Run Collider -> Step 2: Run Analyze.py).

### 5. Where is the SINGLE SOURCE OF TRUTH for this architecture?
**It is fragmented across two realms:**

1.  **For the Automation/Process:** `context-management/docs/BACKGROUND_AI_LAYER_MAP.md`
    *   This defines how data flows between engines (BARE, AEP, HSL).
2.  **For the Research Methodology:** `standard-model-of-code/docs/research/AI_ORCHESTRATION_PROTOCOL.md`
    *   This defines the strict protocol of how the Scientist (B) and Agent (A) interact to validate claims.

**There is no single "System Architecture" document that covers both the Python class hierarchy and the process flow.**

---

### RECOMMENDATION

To reach **Gold** status (referenced in `CLAUDE.md`), you need a **Bridge Module**.

Currently, the Agent reads files generated by the Scientist. A true integration would allow the Agent to *invoke* the Scientist programmatically.

**Proposed Fix:**
Create `context-management/tools/ai/bridges/collider_bridge.py`.
This module would wrap the `standard-model-of-code` CLI commands, allowing the Agent to dynamically request "Particle" analysis without relying on a human to run the script first. This closes the loop and creates a unified graph.

---

## Citations

_No citations provided_
