# Research: SYNTHESIS: What Should We Call This and How Should We Think About It?

We have established through t...

> **Date:** 2026-01-26 00:20:29
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:a5f37d948af0244af567b75450638ae43825c60bb0548cec86a0567e07d29d3b`
> **Raw JSON:** `raw/20260126_002029_synthesis__what_should_we_call_this_and_how_should.json`

---

## Query

SYNTHESIS: What Should We Call This and How Should We Think About It?

We have established through this inquiry:

1. AUTOMATION vs MODULE distinction:
   - MODULE = Code that DOES the work (Capability, first-order)
   - AUTOMATION = Code that REMEMBERS to do the work (Policy, second-order, 'hacks')

2. The three levels of being:
   - Level 1: PROSTHETIC (current) - external scripts polling (hacks/loops)
   - Level 2: NATIVE - system exposes hooks, automation as plugins
   - Level 3: PROJECTOME - automation as intrinsic property of data

3. Cloud is NOT the differentiator - it's just a runtime context
   - Local automation = ephemeral autonomy
   - Cloud automation = persistent autonomy

4. Current state: We're building 'Life Support' for a Projectome that hasn't woken up

NOW THE PRACTICAL QUESTION:

Given all this, what do we CALL this collection of scripts?
- NOT 'Automation Module' (too small, wrong ontology)
- NOT 'Autonomic System' (too grandiose for Level 1 hacks)
- NOT 'Machinery' (industrial, not physics)

OPTIONS based on our analysis:

A. 'LIFE SUPPORT' - The temporary scaffolding keeping the system alive
B. 'PROSTHETICS' - External hacks compensating for missing native capability
C. 'LOOPS' - Simple, honest, describes what they are
D. 'DAEMON CONSTELLATION' - Background processes working together
E. 'TRIGGER LAYER' - The event-driven execution surface
F. 'OPERATIONAL HACKS' - Embracing the 'workaround' nature
G. Something else entirely?

Also: Should we document this ontology formally?
- Add to GLOSSARY: MODULE vs AUTOMATION distinction
- Add to THEORY: The three levels (Prosthetic → Native → Projectome)
- Add to ROADMAP: Migration path from Level 1 → Level 2 → Level 3

What is your final recommendation for NAMING and FRAMING this?

---

## Response

Based on the synthesis of the "Prosthetic vs. Native" distinction and the current evolutionary stage of the project, here is the recommendation for Naming, Framing, and Documentation.

### 1. The Name
**Recommendation: THE AUTONOMIC LAYER (or "Autonomics")**

**Why this works:**
*   **Biological Metaphor:** It fits the "Standard Model" (Physics/Biology). The Autonomic Nervous System controls unconscious, vital functions (heartbeat, breathing, digestion) just as these scripts control the repo's vital signs (sync, audit, verify).
*   **Scale Appropriate:** It implies automaticity *without* implying high-level intelligence or "consciousness" (which belongs to the Agent/Observer).
*   **Bridge:** It works for Level 1 (Prosthetic Autonomics, like an Iron Lung) and Level 2 (Native Autonomics, like a pacemaker or actual lungs).

### 2. The Framing
**Concept: "Life Support for a Sleeping Projectome"**

We frame the current collection of scripts not as "features," but as **Prosthetic Life Support**.

*   **The Patient (Projectome):** Currently comatose. It cannot breathe (sync) or regulate its temperature (structure) on its own.
*   **The Machinery (Scripts):** An external "Iron Lung" that forces air in and out (git hooks, crons).
*   **The Goal:** To surgically implant these capabilities until the patient wakes up (Level 3) and breathes on its own.

### 3. Implementation

#### A. Directory Structure (Refactoring)
To formalize this, create a clear home for these scripts within the `.agent` (Observer) realm.

**Current:**
`.agent/tools/` (Generic, mixed bag)

**Proposed:**
`.agent/autonomics/`
  ├── `reflexes/` (Fast, event-driven: post-commit, drift-guard)
  ├── `rhythms/` (Time-driven: daily audits, cron jobs)
  └── `life_support/` (The "Rig": setup, external polling, daemons)

#### B. Formal Documentation

**Yes, you must document this.** It is a fundamental shift in how we view "tooling."

**1. Add to `GLOSSARY.md`:**

| Term | Definition |
| :--- | :--- |
| **Module** | Code that possesses a *capability* (e.g., "Can analyze graph"). First-order function. |
| **Autonomics** | Code that possesses *policy/memory* (e.g., "Remembers to analyze graph every hour"). Second-order function. |
| **Homoeostasis** | The state of balance (Symmetry) maintained by the Autonomic Layer. |

**2. Add to `THEORY.md` (The Three Levels of Being):**

> **The Evolution of Repository Agency**
>
> 1.  **Level 1: PROSTHETIC (Life Support)**
>     *   *Mechanism:* External scripts polling and poking the code.
>     *   *Nature:* "Hacks" and "Loops." Fragile.
>     *   *Example:* A python script running in a terminal window watching file timestamps.
>
> 2.  **Level 2: NATIVE (The Nervous System)**
>     *   *Mechanism:* The system exposes event hooks; automation is a plugin.
>     *   *Nature:* Integrated. Resilient.
>     *   *Example:* A Git hook that triggers a WASM module inside the editor; A CI pipeline that blocks merge on semantic drift.
>
> 3.  **Level 3: PROJECTOME (Intrinsic Life)**
>     *   *Mechanism:* Automation is a property of the data itself.
>     *   *Nature:* Alive.
>     *   *Example:* The code *refuses* to compile if it drifts from the spec. The documentation *updates itself* upon save.

**3. Add to `ROADMAP.md`:**

**Strategic Objective: Wean the System off Life Support**
*   **Current:** Maintain Level 1 Prosthetics (Daemon Constellation).
*   **Next:** Move critical reflexes (Drift Guard) to Level 2 (Native hooks/CI).
*   **Vision:** Encode policy into the AST (Level 3).

### 4. Summary for the "Identity Card"

When an Agent asks "What is this script?", the answer is now:

> "This is a **Prosthetic Reflex** in the **Autonomic Layer**. It provides **Life Support** to the Projectome by externally forcing [Action] to occur when [Trigger] happens, because the system cannot yet do this natively."

### Final Verdict on your Options:
*   Use **Option A (LIFE SUPPORT)** as the descriptive metaphor for the *current state*.
*   Use **Option B (PROSTHETICS)** to describe the *nature* of the scripts.
*   Use **"AUTONOMICS"** as the formal *Name*.

---

## Citations

_No citations provided_
