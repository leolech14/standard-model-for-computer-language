# Decision Deck Layer Specification

> **Version:** 1.0.0
> **Status:** IMPLEMENTING
> **Validated by:** Gemini 3 Pro (STRONG ACCEPT), Perplexity sonar-deep-research (60+ citations)
> **Created:** 2026-01-23

---

## Purpose

The Decision Deck Layer constrains AI agent actions to a curated library of **CERTIFIED MOVES**. Instead of free-form deciding, agents choose from validated cards with explicit preconditions, steps, and outcomes.

**Core Insight:** Unbounded action spaces cause hallucination, rabbit holes, and inconsistent quality. Constrained action spaces (research-validated: 40-60% improvement in task success rates) produce reliable, auditable behavior.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DECISION DECK LAYER                       │
│                    (Governance/Compass)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  DEALER  │───▶│  DISPLAY │───▶│  PLAYER  │              │
│  │          │    │          │    │          │              │
│  │ Reads    │    │ Renders  │    │ Executes │              │
│  │ state,   │    │ cards in │    │ selected │              │
│  │ filters  │    │ chat UI  │    │ card     │              │
│  │ cards    │    │          │    │          │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       │                                 │                    │
│       ▼                                 ▼                    │
│  ┌──────────┐                    ┌──────────┐              │
│  │   DECK   │                    │  METERS  │              │
│  │          │                    │          │              │
│  │ .agent/  │                    │ Focus    │              │
│  │ deck/    │                    │ Reliable │              │
│  │          │                    │ Debt     │              │
│  │ CARD-*   │                    │ Discover │              │
│  └──────────┘                    └──────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                         ACI LAYER                            │
│              (Adaptive Context Intelligence)                 │
│       tier_orchestrator.py, analyze.py, research tools      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        BARE LAYER                            │
│              (Background Auto-Refinement)                    │
│                Knowledge generation                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Display Protocol (MANDATORY)

**The user MUST see the deck dynamics in every decision point.**

### Card Presentation Format

When cards are dealt, render in chat:

```
╔══════════════════════════════════════════════════════════════╗
║  AVAILABLE ACTIONS                          Phase: DESIGNING ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  [1] CARD-REG-001: Promote Opportunity to Task               ║
║      ├─ Preconditions: ✓ OPP exists, ✓ confidence >= 75%     ║
║      ├─ Cost: ~500 tokens, LOW risk                          ║
║      └─ Unlocks: CARD-REG-002                                ║
║                                                              ║
║  [2] CARD-RES-001: Research with Perplexity                  ║
║      ├─ Preconditions: ✓ query defined                       ║
║      ├─ Cost: ~2000 tokens, LOW risk                         ║
║      └─ Unlocks: CARD-DOC-001                                ║
║                                                              ║
║  [3] CARD-GIT-001: Commit Checkpoint                         ║
║      ├─ Preconditions: ✓ changes staged                      ║
║      ├─ Cost: ~300 tokens, LOW risk                          ║
║      └─ Meters: +2 Reliability                               ║
║                                                              ║
║  [W] WILDCARD: Custom Action (requires justification)        ║
║      └─ Warning: Exits constrained mode, logged              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Playing: [2] CARD-RES-001

Rationale: Need external validation before promoting to task.
```

### Post-Action Report

After playing a card:

```
╔══════════════════════════════════════════════════════════════╗
║  CARD PLAYED: CARD-RES-001                         SUCCESS   ║
╠══════════════════════════════════════════════════════════════╣
║  State Changes:                                              ║
║    + Research saved to docs/research/perplexity/             ║
║    + CARD-DOC-001 now available                              ║
║                                                              ║
║  Meters:                                                     ║
║    Discovery: ████████░░ 8/10 (+2)                          ║
║    Focus:     ██████░░░░ 6/10 (unchanged)                   ║
║    Reliable:  ███████░░░ 7/10 (unchanged)                   ║
║    Debt:      ██░░░░░░░░ 2/10 (unchanged)                   ║
╚══════════════════════════════════════════════════════════════╝
```

### Minimal Format (For Speed)

When context is tight:

```
DECK [DESIGNING]: [1]Promote [2]Research [3]Commit [W]Wildcard
Playing [2] → Research needed first
```

---

## Card Schema

See `.agent/schema/card.schema.yaml` for full schema.

### Card ID Convention

```
CARD-{DOMAIN}-{NUMBER}

Domains:
  REG - Registry operations (tasks, opportunities, sprints)
  GIT - Git operations (commit, branch, PR)
  ANA - Analysis operations (Collider, pipeline)
  VIZ - Visualization operations
  RES - Research operations (Perplexity, Gemini, web)
  DOC - Documentation operations
  TST - Testing operations
  REF - Refactoring operations
  DEP - Deployment operations
```

### Essential Card Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | Yes | Unique identifier |
| `title` | Yes | Action verb phrase |
| `phase_gate` | Yes | When playable |
| `preconditions` | Yes | What must be true |
| `steps` | Yes | Ordered actions |
| `outcomes` | Yes | Success/failure effects |
| `context_injection` | No | Files to inject |
| `rollback` | No | Undo instructions |
| `cost` | No | Resource estimate |

---

## Meters

Four meters track agent behavior quality:

| Meter | Measures | Increases | Decreases |
|-------|----------|-----------|-----------|
| **Focus** | Staying on task | Completing cards, blocking distractions | Rabbit holes, scope creep |
| **Reliability** | Consistent output | Checkpoints, commits, tests | Failures, partial work |
| **Debt** | Accumulated shortcuts | (Always bad) | Refactoring, cleanup |
| **Discovery** | New knowledge found | Research, exploration | Repetition, stagnation |

### Meter Thresholds

```
0-2: CRITICAL - Immediate attention required
3-4: LOW - Consider corrective action
5-6: NORMAL - Operating range
7-8: HIGH - Strong performance
9-10: EXCELLENT - Peak performance
```

### Meter-Based Gating

Some cards require meter thresholds:

```yaml
# Example: Can't do big refactor if Debt is high
preconditions:
  - check: "meters.debt <= 5"
    description: "Must reduce debt before major changes"
```

---

## Phase Gating

Cards are filtered by current sprint phase:

| Phase | Available Card Types |
|-------|---------------------|
| `DESIGNING` | Research, Spec, Plan, Promote |
| `EXECUTING` | Implement, Test, Commit, Refactor |
| `VALIDATING` | Test, Review, Audit, Document |
| `COMPLETE` | Archive, Report, Retrospective |
| `ANY` | Always available (Git, Emergency) |

---

## The Wildcard

Every deal includes a Wildcard option for actions outside the deck.

**Rules:**
1. Requires explicit justification
2. Logged for pattern detection
3. High-frequency wildcard use triggers deck expansion
4. Carries `-1 Reliability` penalty

**When to use:**
- Emergency fixes
- Exploratory debugging
- User explicitly requests unconstrained action

---

## Integration Points

### With Task Registry

```
CARD-REG-001 ←→ promote_opportunity.py
CARD-REG-002 ←→ sprint.py start
CARD-REG-003 ←→ task_store.py update
```

### With 4D Confidence

Cards can require confidence thresholds:

```yaml
preconditions:
  - check: "task.confidence.factual >= 0.75"
    description: "High factual confidence required"
    confidence_min:
      factual: 0.75
```

### With ACI

Cards can specify research tier:

```yaml
steps:
  - action: "analyze.py --tier PERPLEXITY --query '...'"
    description: "Deep research via Perplexity"
```

### With BARE

BARE generates knowledge → Decision Deck governs action on that knowledge.

---

## MVP Implementation

### Phase 1: The Deck (Static)

1. Create `.agent/deck/` directory
2. Define 10-15 core cards covering:
   - Registry operations (3 cards)
   - Git operations (3 cards)
   - Research operations (3 cards)
   - Analysis operations (2 cards)
   - Documentation operations (2 cards)
3. Create `deal_cards.py` that reads state and filters

### Phase 2: The Dealer (Script)

```python
# .agent/tools/deal_cards.py

def deal(state: dict, phase: str, meters: dict) -> list[Card]:
    """Return playable cards given current state."""
    deck = load_deck()
    playable = []

    for card in deck:
        if phase not in card.phase_gate and 'ANY' not in card.phase_gate:
            continue
        if not all(check_precondition(p, state) for p in card.preconditions):
            continue
        playable.append(card)

    return playable[:5] + [WILDCARD]  # Max 5 + wildcard
```

### Phase 3: Gamification (Meters)

1. Add `.agent/state/meters.yaml`
2. Update meters after each card play
3. Display meter bar in chat
4. Gate cards on meter values

---

## Invariants

1. **Every action is a card** - No unconstrained moves (except Wildcard with justification)
2. **Visible to user** - Card deals and plays rendered in chat
3. **Stateless dealer** - Dealer reads state, doesn't own it (Git is truth)
4. **Rollback defined** - Every card documents undo path
5. **Meters auditable** - History of meter changes tracked

---

## Academic Foundations

| Pattern | Source | Application |
|---------|--------|-------------|
| GOAP | Game AI | Decoupling actions from sequences |
| Behavior Trees | Robotics | Hierarchical decision-making |
| Hoare Logic | Formal Methods | {P} C {Q} verification |
| Type State | PL Theory | State-dependent method availability |
| Constrained Decoding | NLP | Bounded output generation |

---

## Files

| File | Purpose |
|------|---------|
| `.agent/specs/DECISION_DECK_LAYER.md` | This spec |
| `.agent/schema/card.schema.yaml` | Card schema |
| `.agent/deck/*.yaml` | Card definitions |
| `.agent/state/meters.yaml` | Current meter values |
| `.agent/tools/deal_cards.py` | Dealer implementation |
| `.agent/tools/play_card.py` | Card execution helper |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-23 | Initial spec from Grok conversation, Gemini + Perplexity validation |
