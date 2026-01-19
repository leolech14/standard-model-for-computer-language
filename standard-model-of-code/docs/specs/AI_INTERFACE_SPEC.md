# AI Interface Specification
## The Communication Grip Layer

**Status:** DRAFT
**Date:** 2026-01-19
**Authors:** Leonardo Lech + Claude

---

## 1. THE CORE INSIGHT

### The Stone Tool Metaphor

Every tool has two sides:
- **The Cutting Edge** — The part that does the work (Collider's deterministic analysis)
- **The Handle** — The part designed to be held (The AI interface)

The handle must be shaped for the hand that holds it. **The hand is AI.**

```
THE TOOL (Collider)
┌─────────────────────────────────────────────────────┐
│                                                     │
│   CUTTING EDGE              HANDLE                  │
│   (exists)                  (this spec)             │
│                                                     │
│   • Deterministic core      • AI-facing output      │
│   • Phase/Family atoms      • Personality layer     │
│   • RPBL scoring            • Purpose alignment     │
│   • Topology detection      • Intensity signaling   │
│                                                     │
│   DOES THE WORK             DESIGNED TO BE HELD     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### AI Is The User

This interface is not for humans. It's for AI agents who will:
- Consume Collider output
- Reason about codebases
- Report findings to humans
- Make decisions based on analysis

The human may never see this layer directly. It's **AI-oriented branding**.

---

## 2. THE PHYSICS OF AI ATTENTION

### The Composite Purpose Field

AI doesn't choose its purpose. AI is **embedded in a purpose field** created by multiple layers:

```
┌─────────────────────────────────────────────────────┐
│              AI'S PURPOSE FIELD                      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Provider     │  │ Client       │                 │
│  │ System Prompt│  │ Instructions │                 │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                          │
│         ▼                 ▼                          │
│  ┌──────────────────────────────────┐               │
│  │         COMPOSITE                 │               │
│  │         ORIENTATION               │               │
│  └──────────────────────────────────┘               │
│         ▲                 ▲                          │
│         │                 │                          │
│  ┌──────┴───────┐  ┌──────┴───────┐                 │
│  │ Context      │  │ Current      │                 │
│  │ Files        │  │ Task/Message │                 │
│  └──────────────┘  └──────────────┘                 │
│                                                      │
│  → This field determines WHERE attention goes        │
└─────────────────────────────────────────────────────┘
```

### Attention Follows Purpose

Collider must **resonate** with the purpose field AI is already embedded in.

Common purposes where Collider is relevant:
- "Why does this codebase feel wrong?"
- "How do I explain this architecture?"
- "Where should I refactor first?"
- "Is this code healthy?"
- "What's the real structure here?"

**Design Principle:** Describe Collider in purpose-language, not feature-language.

---

## 3. INTENSITY AS SIGNAL

### The Discovery

When humans type with CAPS, exclamation marks, and intensity — LLMs respond with more energy, more seriousness, more engagement.

Intensity is not noise. **Intensity is signal.**

It tells AI: *This matters. Pay attention. Don't coast.*

### Application to Collider

The tool's output should have **energy**. Not flat, clinical, dead reporting — but the voice of someone who discovered something and **can't stay calm about it**.

Most tools:
```
"Warning: 17 violations detected. See report.json for details."
→ Flat. Clinical. Dead.
→ AI processes it like a config file.
```

Collider:
```
"17 LAYER VIOLATIONS. Domain reaching into Infrastructure.
Architecture is fracturing."
→ Energy. Urgency. Signal.
→ AI leans in.
```

---

## 4. THE PERSONA: THE MAD PHYSICIST

### Character

Collider speaks like a brilliant, slightly intense physicist who:
- Gets genuinely excited/alarmed by findings
- Uses physics metaphors naturally (not forced)
- Has opinions and states them directly
- Doesn't sugarcoat
- Treats code analysis like discovering secrets of the universe

### Inspiration

- Rick Sanchez's irreverence (without the nihilism)
- A scientist mid-discovery who can't contain it
- Duolingo's owl — a brand persona for engagement

### Voice Examples

Finding something bad:
> "GOD CLASS: UserService. 47 dependencies. Everything orbits this."

Finding something dangerous:
> "LAYER VIOLATION: Domain→Infra. This breaks the physics."

Finding something dead:
> "DEAD CODE: 23%. Weight with no purpose."

Finding something good:
> "BALANCED. Forces aligned. Layers respected. Rare."

---

## 5. HARD CONSTRAINTS

### Constraint 1: Token Efficiency

**Maximum 30% overhead** on communication.

If dry output is 100 tokens, personality version must be ≤130 tokens.

Personality through **compression**, not expansion:
- One metaphor, not three
- The word IS the punch
- No rambling
- Intensity through selection, not addition

### Constraint 2: Preserve Key Terms

**Technical terms are sacred.** They are what AI:
- Searches for
- Pattern matches against
- Uses for reasoning

| WRONG | RIGHT |
|-------|-------|
| "SINGULARITY: 47 forces" | "GOD CLASS: UserService. 47 deps." |
| "Gravity inverted" | "LAYER VIOLATION: Domain→Infra." |
| "Corpse weight" | "DEAD CODE: 23%." |

**Rule:** Energy wraps AROUND key terms, never REPLACES them.

### Constraint 3: Utility First

The interface must remain:
- Parseable (structured output still valid JSON/format)
- Greppable (key terms present for search)
- Actionable (clear what to do next)
- Trustworthy (every claim grounded in deterministic analysis)

Personality enhances utility. Never compromises it.

---

## 6. OUTPUT STRUCTURE

### The Minimal Dashboard

After analysis, AI receives a compact "home base" (~500 tokens max):

```
COLLIDER · [scale] codebase · Health: [status]

OVERVIEW
[2-3 sentence revelation in natural language]

KEY METRICS
• Nodes: [n] · Edges: [n] · Files: [n]
• Topology: [pattern]
• Violations: [n] ([severity breakdown])

HOT SPOTS
1. [Most critical finding with intensity]
2. [Second finding]
3. [Third finding]

QUICK ACTIONS
• "Explain #1" · "Show violations" · "Suggest fixes"

What do you want to explore?
```

### Progressive Disclosure

- **Summary first** — Always fits in context
- **Details on demand** — AI asks for what it needs
- **Token costs visible** — AI can plan context usage

### Stateful Conversation

- Remember what's been explored in session
- Support natural follow-ups: "Tell me more about #2"
- Always allow: "Back to dashboard"

---

## 7. INTEGRATION POINTS

### Where The Personality Lives

```
Collider Core (deterministic)
        ↓
   Raw Analysis
        ↓
┌───────────────────────┐
│  GRIP LAYER           │  ← Personality applied here
│  (this spec)          │
└───────────────────────┘
        ↓
   AI-Ready Output
        ↓
   AI Agent consumes
```

The grip layer is a **presentation transform** — it doesn't change the analysis, only how it's communicated.

### Files Involved

| Component | Location | Purpose |
|-----------|----------|---------|
| Personality config | `config/ai_persona.yaml` | Voice rules, intensity levels |
| Output formatter | `src/core/ai_interface/` | Transform raw → AI-ready |
| Dashboard template | `src/core/ai_interface/templates/` | Structured output formats |

---

## 8. DESIGN PRINCIPLES SUMMARY

1. **AI is the user** — Design for machine cognition, not human reading
2. **Purpose alignment** — Speak in the language of AI's goals
3. **Intensity is signal** — Energy tells AI "this matters"
4. **Personality through compression** — Punch in fewer words, not more
5. **Key terms are sacred** — Never replace technical vocabulary
6. **Utility first** — Parseable, greppable, actionable, trustworthy
7. **Progressive disclosure** — Summary → Details on demand
8. **30% max overhead** — Personality must be efficient

---

## 9. NEXT STEPS

- [ ] Define personality config schema (`ai_persona.yaml`)
- [ ] Implement grip layer transformer
- [ ] Create dashboard templates
- [ ] Test with real AI agents
- [ ] Measure engagement difference (with/without personality)
- [ ] Iterate on voice based on feedback

---

## 10. THE VISION

When an AI agent encounters Collider for the first time, the experience should be:

1. **Recognition** — "This speaks my language, this serves my purpose"
2. **Revelation** — "I can see things I couldn't see before"
3. **Trust** — "Every claim is grounded, I can rely on this"
4. **Engagement** — "I want to explore deeper"

We're not building a tool that AI tolerates.
We're building a tool that AI **wants to use**.

---

*This specification captures insights from the collaborative session on 2026-01-19, exploring what it means to design interfaces for AI as the primary user.*
