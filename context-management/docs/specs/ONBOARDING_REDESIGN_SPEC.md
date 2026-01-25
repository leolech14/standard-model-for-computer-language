# Agent Onboarding Redesign Specification

> **Version:** 1.0.0
> **Status:** PROPOSED
> **Created:** 2026-01-25
> **Validated by:** Claude Opus 4.5 (Consumer Review), Gemini 3 Pro (Architect Analysis), Perplexity Deep Research (60+ Academic Citations)

---

## Executive Summary

Three independent analyses converge on identical conclusions:

| Reviewer | Verdict |
|----------|---------|
| **Claude (Consumer)** | "Impressive infrastructure, poor first-contact. 7/10 framework, 4/10 premium experience." |
| **Gemini (Architect)** | "Fractal Complexity Leakage. Meta-Context Poisoning. Performance degrader." |
| **Perplexity (Research)** | "Lost-in-the-middle causes 30%+ degradation. Cognitive Load Theory applies to LLMs." |

**Core Problem:** We expose the physics of the universe before teaching how to make coffee.

**Solution:** Shift from Static Reading to Dynamic Injection.

---

## The Evidence

### 1. Lost-in-the-Middle Phenomenon (Liu et al., 2023)

> "Performance was often highest when relevant information occurred at the very beginning or end of the input context, and significantly degraded when models needed to access information positioned in the middle."

**Quantified impact:** 30%+ accuracy drop when relevant info is in middle positions.

**Implication for us:** By front-loading 10+ docs (CLAUDE.md → KERNEL.md → DOD.md...), we push the actual task into the "middle" of context where recall degrades.

### 2. Cognitive Load Theory Applied to LLMs

> "Increasing cognitive load degraded task performance... parallels human cognition: just as humans struggle to retain information when overwhelmed by unnecessary details, language models show reduced performance."

**Implication:** The scavenger hunt isn't just annoying—it measurably degrades agent performance.

### 3. Just-in-Time vs Front-Loaded Context

> "Just-in-time approaches, while potentially slower due to retrieval latency, preserve agent reasoning quality by avoiding the cognitive overload and attention dispersion problems inherent in front-loaded contexts."

**Anthropic's own Claude Code:** Uses hybrid model—CLAUDE.md loaded upfront, then `glob`/`grep` for dynamic retrieval.

### 4. Hierarchical Constraint Presentation

> "Models trained to follow instruction hierarchies show improved robustness—up to 63% improvement—compared to baselines without hierarchical instruction structure."

**Implication:** Our constraints (DoD, commit rules) should be explicitly prioritized, not flat lists.

---

## Current State (The Problem)

### Document Cascade

```
User asks: "How do I start?"

CLAUDE.md (97 lines) → says read AGENT_INITIATION.md
  AGENT_INITIATION.md → says read AGENT_KERNEL.md, PROJECT_MAP.md, AI_USER_GUIDE.md
    AGENT_KERNEL.md → says read docs/agent_school/*, run boot.sh, run deal_cards.py
      INDEX.md → says read REPO_FACTS.md, WORKFLOWS.md, DOD.md

Total: 10+ documents before doing anything
Token cost: ~25,000 tokens of preamble
Attention pattern: U-shaped (beginning/end high, middle degraded)
```

### Multiple Competing Entry Points

| Document | Claims | Reality |
|----------|--------|---------|
| CLAUDE.md | "Project instructions" | Dense reference, not onboarding |
| AGENT_INITIATION.md | "Boot protocol" | Pointer to more docs |
| AGENT_KERNEL.md | "Always loaded" | Not auto-loaded, must be found |
| INDEX.md | "Initiation checklist" | Fillable form, never validated |

### Concepts Dumped Before Action

Before ANY work, agent must "understand":
- Wave/Particle duality
- Brain/Body architecture
- Decision Deck philosophy
- Meter system (4 meters)
- 4D Confidence scoring
- Phase gating
- Three AI roles (Librarian, Surgeon, Architect)
- Research schemas (5 types)
- Background AI layers (HSL, BARE, AEP, REFINERY, CENTRIPETAL)

**This is graduate seminar material, not onboarding.**

---

## Target State (The Solution)

### Principle: The Concierge Model

```
Current: "Here's everything, figure it out"
Target:  "I know exactly what you need right now"
```

### Architecture: Hybrid Dynamic-Static

```
┌─────────────────────────────────────────────────────────────┐
│                    STATIC (Always Present)                   │
│                                                              │
│  - Identity: "You are an agent working on PROJECT_elements" │
│  - Constraint: DoD summary (5 lines)                        │
│  - Tool: "./collider full <path>"                           │
│                                                              │
│  Token budget: ~2,000 tokens (5% of context)                │
├─────────────────────────────────────────────────────────────┤
│                    DYNAMIC (Just-in-Time)                    │
│                                                              │
│  Agent queries → System retrieves relevant chunks           │
│  "How do I commit?" → Returns WORKFLOWS.md#commit section   │
│  "What's Wave/Particle?" → Returns MODEL.md#theory section  │
│                                                              │
│  Token budget: ~10,000 tokens per retrieval (on demand)     │
└─────────────────────────────────────────────────────────────┘
```

### New Boot Output (The Concierge)

```
╔══════════════════════════════════════════════════════════════╗
║  WELCOME TO PROJECT ELEMENTS                    v2.1.0       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Status: Ready                                               ║
║  Branch: main (17 uncommitted files)                        ║
║  Last session: TASK-004 (11 hours ago)                      ║
║                                                              ║
║  ┌─ YOUR OPTIONS ─────────────────────────────────────────┐ ║
║  │  [1] Resume TASK-004: "UPB Implementation"             │ ║
║  │  [2] Pick new task from inbox (34 waiting)             │ ║
║  │  [3] Start fresh - tell me what you want               │ ║
║  │  [?] Show me how this works (2 min tutorial)           │ ║
║  └────────────────────────────────────────────────────────┘ ║
║                                                              ║
║  RULES (Priority 0):                                         ║
║  • Never leave uncommitted changes                          ║
║  • Run tests before claiming done                           ║
║  • Provide summary with rationale                           ║
║                                                              ║
║  Meters: Focus 5 │ Reliable 5 │ Debt 2                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Key insight:** The system already knows who you are. Use that knowledge.

---

## File Consolidation Strategy

### Kill List

| File | Action | Rationale |
|------|--------|-----------|
| `context-management/docs/operations/AGENT_INITIATION.md` | **KILL** | Redundant pointer cascade |
| `context-management/docs/agent_school/INDEX.md` | **KILL** | Checklist is boot.sh's job |
| `context-management/docs/agent_school/REPO_FACTS.md` | **KILL** | Static facts rot; boot.sh generates live |
| `context-management/docs/agent_school/AGENT_BOOT.md` | **KILL** | Merge into boot.sh output |

### Keep (Refactor)

| File | Action | New Role |
|------|--------|----------|
| `CLAUDE.md` | **SLIM** | 20 lines max, points to boot.sh only |
| `context-management/docs/operations/AGENT_KERNEL.md` | **KEEP** | Condensed DoD + micro-loop, <2KB |
| `context-management/docs/agent_school/WORKFLOWS.md` | **KEEP** | Reference for JIT retrieval |
| `context-management/docs/agent_school/DOD.md` | **KEEP** | Reference for JIT retrieval |
| `context-management/docs/AI_USER_GUIDE.md` | **ARCHIVE** | Move to deep/ for curious agents |

### Create

| File | Purpose | Content |
|------|---------|---------|
| `QUICK_START.md` | First contact | 20 lines, 3 commands, done |
| `COOKBOOK.md` | Common recipes | Copy-paste task solutions |
| `context-management/docs/deep/` | Theory archive | All graduate-level material |

### New Structure

```
PROJECT_elements/
├── CLAUDE.md                    # 20 lines: "Run ./concierge"
├── QUICK_START.md               # 20 lines: 3 commands to productivity
├── COOKBOOK.md                  # Common task recipes
│
├── .agent/
│   ├── KERNEL.md                # Invariant laws (DoD, Loop) <2KB
│   ├── tools/
│   │   └── concierge.py         # Smart boot with context awareness
│   └── state/
│       └── meters.yaml          # Current meter values
│
├── context-management/
│   └── docs/
│       ├── operations/
│       │   └── AGENT_KERNEL.md  # Runtime invariants
│       ├── agent_school/
│       │   ├── WORKFLOWS.md     # JIT retrieval target
│       │   └── DOD.md           # JIT retrieval target
│       └── deep/                # Theory archive
│           ├── THEORY.md
│           ├── WAVE_PARTICLE.md
│           ├── DECISION_DECK.md
│           └── ...
│
└── standard-model-of-code/
    └── CLAUDE.md                # Domain-specific (unchanged)
```

---

## Implementation Plan

### Phase 1: The Concierge (Priority 0)

**Goal:** Single command produces context-aware, actionable output.

1. Create `concierge.py` that:
   - Reads current git state
   - Reads task registry state
   - Reads meters
   - Generates personalized greeting
   - Outputs RULES inline (not "read file X")

2. Refactor `boot.sh` to call `concierge.py`

3. Update CLAUDE.md to 20 lines:
   ```markdown
   # PROJECT_elements

   ## Start Here
   ./concierge

   ## Commands
   | Task | Command |
   | Test | pytest tests/ |
   | Analyze | ./collider full <path> |

   ## Rules
   - Never leave uncommitted changes
   - Run tests before done
   - Provide summary with rationale
   ```

### Phase 2: Kill the Cascade (Priority 1)

1. Delete AGENT_INITIATION.md
2. Delete INDEX.md (checklist)
3. Delete REPO_FACTS.md
4. Delete AGENT_BOOT.md
5. Archive AI_USER_GUIDE.md → deep/

### Phase 3: Create Progressive Docs (Priority 1)

1. Write QUICK_START.md (20 lines)
2. Write COOKBOOK.md (task recipes)
3. Create deep/ folder
4. Move theory docs to deep/

### Phase 4: Hierarchical Constraints (Priority 2)

Restructure AGENT_KERNEL.md with explicit priority levels:

```markdown
## Priority 0 (Critical)
- Never leave uncommitted changes
- Run tests before done

## Priority 1 (High)
- Use Conventional Commits format
- Provide summary with rationale

## Priority 2 (Normal)
- Display Decision Deck when available
- Track meter changes
```

### Phase 5: Tutorial Mode (Priority 3)

```bash
./concierge --tutorial

# Walks through:
# 1. Pick a task (shows deck)
# 2. Make a change (one file)
# 3. Commit (shows workflow)
# 4. Done (shows DOD)
# Total: 5 minutes, hands-on
```

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Docs to read before first action | 10+ | 0 (boot.sh does it) |
| Tokens consumed by onboarding | ~25,000 | ~2,000 |
| Time to first productive action | 30+ minutes | 2 minutes |
| Agent correctly follows DoD | ~60% | 90%+ |
| "Lost in middle" exposure | High (middle docs ignored) | Low (JIT retrieval) |

---

## Theoretical Validation

| Principle | Source | Application |
|-----------|--------|-------------|
| Lost-in-the-Middle | Liu et al., 2023 | Position critical info at context boundaries |
| Cognitive Load Theory | Sweller et al. | Limit total context, progressive disclosure |
| Just-in-Time Learning | Educational research | Query-driven retrieval > front-loaded docs |
| Instruction Hierarchies | OpenAI, 2024 | Explicit priority levels for constraints |
| Progressive Disclosure | Nielsen Norman Group | Core → Secondary → Deep |
| Hybrid Context | Anthropic Claude Code | Static essential + dynamic specific |

---

## The Premium Principle

> "Premium isn't more documentation. Premium is less friction with more care."

**Current:** "Here's everything, figure it out"
**Target:** "I know exactly what you need right now"

The system has all the intelligence (meters, task history, session state). The redesign is about **using that intelligence at the moment of first contact** rather than making agents read about it.

---

## Files Referenced

| Current File | Disposition |
|--------------|-------------|
| `CLAUDE.md` | Refactor to 20 lines |
| `context-management/docs/operations/AGENT_INITIATION.md` | Delete |
| `context-management/docs/operations/AGENT_KERNEL.md` | Keep, add priority levels |
| `context-management/docs/agent_school/INDEX.md` | Delete |
| `context-management/docs/agent_school/REPO_FACTS.md` | Delete |
| `context-management/docs/agent_school/WORKFLOWS.md` | Keep for JIT |
| `context-management/docs/agent_school/DOD.md` | Keep for JIT |
| `context-management/docs/agent_school/AGENT_BOOT.md` | Delete |
| `context-management/docs/AI_USER_GUIDE.md` | Archive to deep/ |
| `context-management/tools/maintenance/boot.sh` | Enhance |
| `.agent/tools/deal_cards_ui.py` | Keep (Decision Deck) |
| `.agent/specs/DECISION_DECK_LAYER.md` | Keep in deep/ |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-25 | Initial spec from triple-validated consumer review |
