# Research: Validate the implementation order for Decision Deck onboarding integration:

CURRENT STATE:
- Decisi...

> **Date:** 2026-01-23 15:50:11
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:71e1c304b187cbffe95a1263a711e51c3a8fe7eecf19c4dbfb0ca47894a041cc`
> **Raw JSON:** `raw/20260123_155011_validate_the_implementation_order_for_decision_dec.json`

---

## Query

Validate the implementation order for Decision Deck onboarding integration:

CURRENT STATE:
- Decision Deck MVP complete (.agent/deck/, deal_cards.py, deal_cards_ui.py)
- UI working with rainbow colors, context section, meters
- 7 cards defined (REG-001, RES-001, RES-002, GIT-001, ANA-001, DOC-001, WLD-000)
- Gemini + Perplexity validated the 'primacy effect' approach

PROPOSED ORDER:
1. Integrate into KERNEL.md boot sequence
2. Create CARD-SES-001 (Session Start card)
3. Wire deal_cards_ui.py to read real state from registry

QUESTION: Is this the right order? Or should we:
- Create the Session Start card FIRST (so boot has something to show)?
- Wire real state FIRST (so context section isn't hardcoded)?
- Something else?

Consider dependencies and the principle that agents should see the deck IMMEDIATELY on boot.

Rate each ordering option with confidence scores.

---

## Response

Analyze the implementation order using the provided context and the "Primacy Effect" principle (agents trust what they see first; early failures permanently degrade trust).

### Verdict: REJECT PROPOSED ORDER
The proposed order (`Kernel -> Card -> State`) creates a **High Risk** of adoption failure.

**Reasoning:**
1. **Broken Primacy:** If you update `KERNEL.md` first, the next agent will run the deck immediately. If the deck shows hardcoded data (e.g., "Phase: DESIGNING" when we are in `SPRINT-002 EXECUTING`) or lacks a valid "Start" card, the agent will perceive the tool as "hallucinating" or "broken."
2. **Missing Action:** If the Kernel instructs the agent to "Boot via Deck" but `CARD-SES-001` doesn't exist yet, the agent has no valid move and must use a Wildcard immediately. This trains the agent to bypass the deck.
3. **Dependency Violation:** Decision cards often use preconditions based on state (e.g., "Is Sprint Active?"). You cannot reliably define `CARD-SES-001` without the State wiring to support its preconditions.

---

### Recommended Order: "State First" Strategy

**Confidence:** 95% (vs 40% for proposed)

#### 1. Wire Real State (The "Truth" Layer)
**Goal:** Ensure the "Context" and "Meters" sections of the UI reflect reality.
- **Action:** Update `deal_cards.py` / `deal_cards_ui.py` to read:
  - Phase: From `.agent/sprints/SPRINT-002.yaml` (Status: EXECUTING)
  - Active Tasks: From `.agent/registry/active/` count
  - Meters: From `.agent/state/meters.yaml`
- **Why:** When the agent first sees the UI, it must match their internal context analysis. "It knows what I know."

#### 2. Create CARD-SES-001 (The "Action" Layer)
**Goal:** Provide a legal move for the specific moment of booting.
- **File:** `.agent/deck/CARD-SES-001.yaml`
- **Definition:**
  - **Title:** "Start Agent Session"
  - **Preconditions:** None (always available at boot)
  - **Steps:**
    1. Check `registry/INDEX.md` for priority.
    2. Create `runs/RUN-{timestamp}.yaml`.
    3. Log `STARTED` status.
  - **Outcomes:** Meters + Focus, + Reliability.
- **Why:** Eliminates the need for a Wildcard at the very first step.

#### 3. Integrate into KERNEL.md (The "Traffic" Layer)
**Goal:** Direct flow to the now-trustworthy system.
- **Action:** Update `Boot Protocol` in `.agent/KERNEL.md`.
- **Change:**
  ```markdown
  # OLD
  8. BEGIN work, logging steps to your RUN record

  # NEW
  8. RUN .agent/tools/deal_cards_ui.py --mode boot
  9. SELECT "CARD-SES-001" (Start Session) or appropriate card
  ```
- **Why:** The system is live, truthful, and has a valid path forward.

---

### Implementation Plan Summary

| Order | Step | Risk if Skipped/Reordered |
|:-----:|------|---------------------------|
| **1** | **Wire State** | Agent sees "Phase: DESIGNING" (fake) vs "EXECUTING" (real) → **LOSS OF TRUST** |
| **2** | **Create Card** | Agent boots but has no button to click → **FORCED WILDCARD** |
| **3** | **Update Kernel** | Agent ignores deck entirely because spec doesn't mandate it → **LOW ADOPTION** |

**Guidance:** Do not update `KERNEL.md` until running `python .agent/tools/deal_cards_ui.py` returns a UI that accurately describes `SPRINT-002` and offers a "Start Session" option.

---

## Citations

_No citations provided_
