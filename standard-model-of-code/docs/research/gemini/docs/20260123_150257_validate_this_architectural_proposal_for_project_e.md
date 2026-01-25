# Research: VALIDATE THIS ARCHITECTURAL PROPOSAL for PROJECT_elements:

## Decision Deck Layer (Gamification of ...

> **Date:** 2026-01-23 15:02:57
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:6d425dae761d3f9f63c764a89f63e747e2098f5e65d7be0efcac016c3ec61797`
> **Raw JSON:** `raw/20260123_150257_validate_this_architectural_proposal_for_project_e.json`

---

## Query

VALIDATE THIS ARCHITECTURAL PROPOSAL for PROJECT_elements:

## Decision Deck Layer (Gamification of Agent Governance)

CONCEPT: Instead of letting AI agents 'free-form decide anything', we constrain them to:
1. A curated library of CERTIFIED MOVES (cards/options)
2. Each move has preconditions, expected outcomes, and rollback
3. A secondary 'Game Master' layer generates available options based on current state
4. The agent SELECTS from valid moves rather than improvising

KEY COMPONENTS:
- CARD schema: id, intent, preconditions, steps, evidence, rollback
- METERS: Focus (alignment to DoD), Reliability, Debt, Discovery Pressure
- PHASE GATING: Different cards available in DESIGNING vs EXECUTING phase
- AUTONOMY LEVELS: Low-risk autopilot vs gated high-risk actions

INTEGRATION POINTS:
- Consumes: sprints/*.yaml, registry/tasks/*.yaml, intelligence/truths/repo_truths.yaml
- Produces: events.yaml (action log), state.yaml (meters)
- Routes gaps to: registry/inbox/opportunity-*.yaml

QUESTIONS TO VALIDATE:
1. Does this align with PROJECT_elements' existing architecture (BARE, ACI, sprints)?
2. Are there conflicts with current invariants in KERNEL.md?
3. What is missing from this design?
4. Is this approach academically sound (cite any relevant patterns)?
5. What's the MVP implementation order?

Be critical. Find flaws.

---

## Response

This is a **Senior Software Engineer analysis** of your "Decision Deck Layer" architectural proposal for `PROJECT_elements`.

### Executive Summary

**Verdict:** **STRONG ACCEPT (High Factual/Alignment Confidence)**
This proposal provides the missing "Governance Layer" referenced in `BARE_LIVE.md`. It solves the "rabbit hole" problem where agents hallucinate next steps during complex tasks. It aligns perfectly with the project's move toward atomization—treating *actions* as atoms (Cards) just as Collider treats code as atoms.

**Critical Risk:** Violating the "Worse is Better" philosophy (from `CUTTING_PLAN.md`) by over-engineering the "Game Master." This must be implemented as a static file generator, not a complex active server.

---

### 1. Alignment Analysis

The proposal integrates seamlessly with existing subsystems:

*   **With BARE (`.agent/specs/BARE_LIVE.md`):**
    *   BARE generates *Knowledge* (Atoms/Clusters).
    *   Decision Deck governs *Action* (Transitions).
    *   Your proposal explicitly matches the "Decision Deck Layer" placeholder in the BARE-Live spec.

*   **With Task Registry (`.agent/registry/`):**
    *   Current Task State Machine: `DISCOVERY → READY → EXECUTING → COMPLETE`.
    *   The "Deck" formalizes the transitions. Example: The `promote_opportunity` script becomes a "Card" only playable when `confidence >= threshold`.

*   **With 4D Confidence:**
    *   Cards can require specific 4D scores as preconditions (e.g., "Cannot play `MERGE_PR` card unless `Factual >= 95%`").

*   **With KERNEL.md:**
    *   Adheres to "Log before doing" (playing a card is a loggable event).
    *   Mitigates "Lost-in-the-Middle" effect: Instead of giving the agent a 50k token context and asking "What next?", you provide 5 valid Cards. The agent selects one. This drastically reduces cognitive load and hallucination.

### 2. Conflicts & Invariants

**Potential Conflict: "Git is Truth" vs. "Game Master" State**
*   **Risk:** If the "Game Master" keeps state in memory or a separate database, it violates `KERNEL.md`.
*   **Resolution:** The "Dealer" (Game Master) must be a script that reads the filesystem and outputs `available_moves.yaml`. It must be stateless and deterministic.

**Potential Conflict: Agent Autonomy**
*   **Risk:** Agents might get stuck if no cards are valid (Deadlock).
*   **Resolution:** You need a "Joker" or "Distress Signal" card that is *always* available, which escalates to Human review or creates a blockage entry in `runs/`.

**Invariant Check:**
*   Does it respect `PROJECT_elements` file duality? **Yes.**
    *   *Concept:* `cards/schema/move.schema.yaml`
    *   *Object:* `cards/deck/promote_opp.yaml`

### 3. Missing Components (Gap Analysis)

1.  **The "Dealer" Mechanism:**
    *   You defined the Cards and the Players, but not the Dealer. You need a script (`deal_cards.py`) that acts as a context-aware filter.
    *   *Input:* Repo State + Phase (Designing/Executing).
    *   *Output:* A concise list of valid Card IDs allowed *right now*.

2.  **The "Wildcard" (Emergency Exit):**
    *   If the agent hits an edge case not covered by a Card, they need a `REQUEST_NEW_CARD` or `ESCALATE_TO_HUMAN` move.

3.  **Cost/Resource Metrics:**
    *   Meters mentions "Debt" and "Focus," but `PROJECT_elements` cares deeply about **Tokens**. Cards should have estimated token costs.

4.  **Card Chaining (Combos):**
    *   Some complex actions are sequences. A Card should be able to trigger a "Sub-Deck" (a specific workflow like `run_tests` -> `fix_errors` -> `commit`).

### 4. Academic/Pattern Soundness

This approach is highly sound and maps to established patterns in AI and Game Development:

1.  **GOAP (Goal-Oriented Action Planning):**
    *   Used in F.E.A.R. and S.T.A.L.K.E.R. AI.
    *   Agents plan backwards from a Goal (World State) using Actions (Cards) that have Preconditions and Effects.
    *   *Your proposal is essentially GOAP for Coding Agents.*

2.  **Type State Pattern:**
    *   In Rust/Haskell: A file object cannot be `read()` until it is `open()`.
    *   In Decision Deck: The `submit_pr` Card is *typographically impossible* to play until the `run_tests` Card has returned `success`.

3.  **Constrained Decoding (LLM Specific):**
    *   By forcing the LLM to select from a set enum of Actions (Cards) rather than generating free text, you reduce the search space and collapse the wave function of potential errors.

### 5. MVP Implementation Order

Don't overbuild. Follow the "Cutting Plan" philosophy.

**Phase 1: The Deck (Static)**
1.  Define `.agent/schema/card.schema.yaml`.
2.  Create `.agent/deck/` directory.
3.  Port 5 existing scripts to Cards (YAML wrappers around the scripts):
    *   `claim_task`
    *   `create_run`
    *   `run_test`
    *   `log_step`
    *   `handoff`

**Phase 2: The Dealer (Script)**
1.  Create `.agent/tools/dealer.py`.
2.  Logic: Read `runs/latest.yaml` status.
3.  If `status == IN_PROGRESS`, deal [Log Step, Run Test, Create File].
4.  If `status == STARTED`, deal [Read Context, Claim Task].
5.  Output: Injects the "Hand" into the `system_prompt` or context window.

**Phase 3: The Gamification (Meters)**
1.  Add `state.yaml` to track "Focus" (Task drift) and "Debt" (Skipped tests).
2.  Update `dealer.py` to hide high-risk cards if Reliability Meter is low.

### Recommended Schema Adjustment

Add `context_injection` to your Card schema. Some cards need to inject specific context files (Concept/Object duality) to be useful.

```yaml
# .agent/deck/CARD-001.yaml
id: CARD-001
intent: "Run Socratic Audit"
phase: [VALIDATING, REVIEW]
cost: HIGH (Tokens)
context_injection:
  - ".agent/specs/BARE_LIVE.md"
preconditions:
  - "Run status is IN_PROGRESS"
  - "Files modified > 0"
tool_call:
  script: "python context-management/tools/ai/analyze.py --verify pipeline"
```

### Conclusion

This is the correct architectural evolution for `PROJECT_elements`. It moves the system from "Prompt Engineering" (fuzzy) to "System Engineering" (deterministic).

**Proceed with Phase 1 immediately.**

---

## Citations

_No citations provided_
