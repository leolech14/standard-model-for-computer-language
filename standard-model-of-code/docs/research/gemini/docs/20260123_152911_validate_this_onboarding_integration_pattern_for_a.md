# Research: Validate this onboarding integration pattern for AI agents:

PROPOSAL: Decision Deck as Onboarding P...

> **Date:** 2026-01-23 15:29:11
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:b5bc6a42420b64db7f4056fed5129d86e2c9c79258f25a07c07e2f90b30288ae`
> **Raw JSON:** `raw/20260123_152911_validate_this_onboarding_integration_pattern_for_a.json`

---

## Query

Validate this onboarding integration pattern for AI agents:

PROPOSAL: Decision Deck as Onboarding Primitive

The idea: When any AI agent (Claude, Gemini, etc.) starts a session in PROJECT_elements, the boot sequence IMMEDIATELY forces them to interact with the Decision Deck. Before doing any work, the agent must:

1. Run deal_cards.py to see available actions
2. Select a card from the deck
3. Execute that card's steps

WHY THIS MATTERS:
- The card selection experience becomes the FIRST thing the agent does
- This embeds the constrained action pattern into working memory
- It becomes part of the agent's mental model of how to work in this codebase
- Every session starts with the same ritual, creating consistency

INTEGRATION POINT:
- Current boot: context-management/tools/maintenance/boot.sh
- Current onboarding: context-management/docs/operations/AGENT_KERNEL.md
- The deck lives at: .agent/deck/
- The dealer: .agent/tools/deal_cards.py

PSYCHOLOGICAL PRINCIPLE:
- First impressions set expectations
- Repeated patterns become automatic
- Constrained choice at start prevents scope creep

QUESTION: Is this a sound approach? What are the risks? How should the boot sequence integrate with deal_cards.py?

Rate this proposal:
- Factual confidence (is this technically sound?)
- Alignment confidence (does this serve the project's mission?)
- Implementation confidence (can this be built cleanly?)

---

## Response

Based on the provided codebase context, particularly `.agent/KERNEL.md` (Boot Protocol) and `.agent/specs/DECISION_DECK_LAYER.md`, here is the analysis of your proposal.

### Verdict: STRONG ACCEPT
**This is a foundational architectural improvement.** Integrating the Decision Deck into the boot sequence transforms the deck from a passive "tool" into an active "operating environment." It solves the "blank canvas" paralysis common in LLM agents by immediately providing a constrained menu of certified moves.

---

### 1. Confidence Ratings

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Factual** | **95%** | Technically sound. `deal_cards.py` is a standard script execution. It leverages the existing `KERNEL.md` boot flow without breaking git/filesystem constraints. |
| **Alignment** | **100%** | Perfectly aligns with the project mission of "Reliable, Auditable Behavior" and the `DECISION_DECK_LAYER.md` goal of "constrained action spaces." |
| **Implementation** | **90%** | Requires `deal_cards.py` (TASK-018) to be completed and `KERNEL.md` to be updated. Low technical risk, high architectural leverage. |

---

### 2. Strategic Analysis

#### Why this works (The Psychological/Technical Bridge)
Your insight about "working memory" is technically accurate regarding LLM context windows.
1.  **Attention Anchoring:** LLMs attend heavily to the beginning and end of context. By forcing a structured decision event *immediately* after the context load, you anchor the model's behavior pattern in "constrained choice" rather than "free-form generation."
2.  **Context Injection:** The `deal_cards.py` output (the rendered deck) acts as an immediate RAG injection of *what is possible* in the system right now, preventing hallucinations about tools that don't exist.
3.  **State Synchronization:** It forces the agent to read the system state (Phase, Meters) before typing a single line of code.

#### The "Ritual" as Protocol
Current agents often skip from "I have read the context" to "I will now write code." The Deck forces an intermediate step: "I have read the context, I see my options, I choose Strategy X." This validates the **Governance Layer** defined in `.agent/specs/DECISION_DECK_LAYER.md`.

---

### 3. Implementation Plan

To implement this, you must modify the **Boot Protocol** in `.agent/KERNEL.md`.

#### Current Boot Protocol (KERNEL.md)
```markdown
6. CLAIM task BEFORE starting work
7. FIND or CREATE a RUN record in runs/
8. BEGIN work, logging steps to your RUN record
```

#### Proposed Boot Protocol (Revised)
The Deck becomes the mechanism for *claiming* and *executing*.

```markdown
6. CHECK registry/INDEX.md for active tasks
7. FIND or CREATE a RUN record in runs/
8. INITIATE DECK RITUAL:
   a. Run: .agent/tools/deal_cards.py
   b. Review available Certified Moves
   c. Select a Card (e.g., CARD-REG-004 "Claim Task" or CARD-RES-001 "Research")
   d. Execute Card steps
```

### 4. Required Adjustments

To make this seamless, you need specific "Opening Game" cards. The current deck (in `TASK-018`) focuses on *doing* work. You need cards for *starting* work.

**New Cards Required:**
1.  **`CARD-SESSION-START` (The "Boot" Card)**
    *   **Context:** Runs automatically or is the only option if no task is claimed.
    *   **Options:** Unlocks `CARD-REG-CLAIM` or `CARD-TRIAGE-INBOX`.
2.  **`CARD-REG-CLAIM`**
    *   **Action:** Wraps `.agent/tools/claim_task.sh`.
    *   **Outcome:** Sets environment variable `CURRENT_TASK`, unlocks `EXECUTING` phase cards.

---

### 5. Risk Assessment & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **The "Empty Hand"** | Agent boots, runs dealer, gets 0 cards because preconditions (like "Task Claimed") aren't met. | **Default State:** The dealer must always return at least "Setup/Claim" cards if no task is active. "Wildcard" must always be available. |
| **Token Cost** | Rendering the full deck every boot consumes tokens. | **Compact Mode:** Ensure `deal_cards.py` supports a `--compact` flag for the boot sequence (headers only, no full descriptions). |
| **Friction** | Simple fixes feel bureaucratic. | **Wildcard:** Allow the "Wildcard" option (already in spec) to be played immediately for "Quick Fix" sessions, logging the justification. |

### 6. Integration Code Snippet

**Update `deal_cards.py` (Logic)**
```python
def get_boot_cards(agent_context):
    """
    If no task is claimed in the RUN record, force 'Registry' phase cards.
    """
    if not agent_context.current_task:
        return [
            load_card("CARD-REG-004"), # Claim Task
            load_card("CARD-REG-005"), # Triage Inbox
            load_card("CARD-MNT-001")  # System Health Check
        ]
    else:
        # Standard dealing logic based on Task Phase
        return deal_standard_hand(agent_context)
```

### Summary
This proposal is **ACCEPTED**. It converts the "Decision Deck" from a feature into the **primary interface** for agent interaction, effectively creating a "Game Loop" architecture for the agent system.

**Next Step:** Update `.agent/KERNEL.md` to mandate the Deck Ritual at Step 8.

---

## Citations

_No citations provided_
