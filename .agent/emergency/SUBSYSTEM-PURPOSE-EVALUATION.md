# SUBSYSTEM PURPOSE EVALUATION

> **Goal:** Evaluate each real subsystem's purpose and how to accomplish it
> **Method:** For each subsystem, ask: What? Singular? Overlap? Accomplish?
> **Created:** 2026-01-26
> **Author:** Claude Opus 4.5

---

## EVALUATION FRAMEWORK

For each subsystem:

```
┌────────────────────────────────────────────────────────────────┐
│ 1. WHAT is its claimed purpose?                                │
│ 2. Is the purpose SINGULAR? (Can state in <10 words)           │
│ 3. Does it OVERLAP with other subsystems?                      │
│ 4. HOW can we accomplish that purpose with minimal entropy?    │
│ 5. VERDICT: Keep / Merge / Split / Clarify                     │
└────────────────────────────────────────────────────────────────┘
```

---

## PARTICLE REALM

### S1: Collider

```yaml
Location: standard-model-of-code/
Type: Engine
```

**1. WHAT:** Semantic code analysis - parse, classify, detect purpose, visualize

**2. SINGULAR?** NO - Collider does at least 4 things:
  - Parse code (tree-sitter)
  - Classify elements (atoms, roles)
  - Detect purpose (purpose field)
  - Generate outputs (reports, viz)

**3. OVERLAP?**
  - Visualization overlaps with no one (good)
  - Purpose detection is unique (good)
  - BUT: Collider is a GOD CLASS internally

**4. HOW TO ACCOMPLISH:**

```
Option A: Keep as monolith, clarify internal boundaries
  Collider
  ├── Stage 1-3: Parser (input: code, output: AST)
  ├── Stage 4-8: Analyzer (input: AST, output: graph)
  └── Stage 9-12: Presenter (input: graph, output: reports/viz)

Option B: Split into 3 subsystems
  P1: Parser (parse code → AST)
  P2: Analyzer (AST → semantic graph)
  P3: Presenter (graph → outputs)
```

**5. VERDICT:**
```
CLARIFY internal boundaries.
Keep as one subsystem but document the 3 internal phases.
The 28 stages are too granular; 3 phases is right level.
```

---

## WAVE REALM

### S2: HSL (Holographic Socratic Layer)

```yaml
Location: context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md
Type: Framework
```

**1. WHAT:** Validation framework for AI-assisted development

**2. SINGULAR?** UNCLEAR - "Validation framework" is vague. What does it validate?
  - Semantic correctness of code?
  - AI query quality?
  - Both?

**3. OVERLAP?**
  - S8 (Hygiene) also validates
  - S6 (BARE) also validates (continuous)
  - What's the boundary?

**4. HOW TO ACCOMPLISH:**

```
Define HSL as: "Semantic validation via AI"

HSL validates:
  ✓ Architecture alignment
  ✓ Purpose coherence
  ✓ Pattern compliance

HSL does NOT validate:
  ✗ Syntax (that's S8 Hygiene)
  ✗ Continuous monitoring (that's S6 BARE)
```

**5. VERDICT:**
```
CLARIFY boundaries.
HSL = "AI-powered semantic validation on demand"
Document: "Use HSL when you need AI to verify X"
```

---

### S3: analyze.py (ACI)

```yaml
Location: context-management/tools/ai/analyze.py
Type: Engine
```

**1. WHAT:** AI query interface - route questions to appropriate tier

**2. SINGULAR?** YES - "Route and execute AI queries"

**3. OVERLAP?**
  - S11 (ACI Refinery) prepares context for this
  - S12 (Centripetal) is a mode of this
  - S4 (Perplexity) is a tier within this

**4. HOW TO ACCOMPLISH:**

```
S3 is the FRONT DOOR to all AI capabilities.
It OWNS the query routing decision.
Other subsystems are COMPONENTS it uses:
  - S4 (Perplexity) = external tier
  - S11 (Refinery) = context preparation
  - S12 (Centripetal) = deep mode

This is CORRECT architecture.
S3 is the orchestrator; others are specialists.
```

**5. VERDICT:**
```
KEEP as-is.
S3 is correctly the central AI query handler.
S4, S11, S12 are correctly sub-components.
```

---

### S4: Perplexity MCP

```yaml
Location: context-management/tools/mcp/
Type: Utility
```

**1. WHAT:** External knowledge via Perplexity API

**2. SINGULAR?** YES - "Fetch external knowledge"

**3. OVERLAP?** NO - Only S4 talks to Perplexity

**4. HOW TO ACCOMPLISH:**
```
S4 is a DATA SOURCE, not a decision maker.
S3 decides WHEN to use S4.
S4 just fetches.

This is correct.
```

**5. VERDICT:**
```
KEEP as-is.
Could be renamed: "ExternalKnowledge" or "WebResearch"
But structure is correct.
```

---

### S9: Laboratory

```yaml
Location: standard-model-of-code/tools/research/laboratory.py
Type: Bridge
```

**1. WHAT:** Research experiments - hypothesis testing on code

**2. SINGULAR?** YES - "Run experiments on codebase"

**3. OVERLAP?**
  - S9b (Lab Bridge) is its client
  - Confusing: S9 is in PARTICLE realm (standard-model-of-code)
              but is a WAVE function (AI research)

**4. HOW TO ACCOMPLISH:**

```
PROBLEM: S9 is in wrong location.
  - Lives in Particle (standard-model-of-code/)
  - But serves Wave (AI research)

OPTIONS:
  A) Move S9 to context-management/tools/ai/
  B) Keep S9 in Particle, accept it's a bridge
  C) Merge S9 + S9b into single "Researcher" in Wave

Option C is cleanest:
  Researcher (new)
  ├── hypothesis testing
  ├── experiment execution
  └── result analysis
```

**5. VERDICT:**
```
MERGE S9 + S9b → "Researcher"
Location: context-management/tools/ai/researcher.py
Purpose: "Run and analyze codebase experiments"
```

---

### S9b: Lab Bridge

```yaml
Location: context-management/tools/ai/laboratory_bridge.py
Type: Client
```

**1. WHAT:** Wave→Particle bridge for Laboratory

**2. SINGULAR?** YES - "Call Laboratory from Wave"

**3. OVERLAP?** Direct overlap with S9 (they're halves of same thing)

**4. HOW TO ACCOMPLISH:** See S9 above - merge them

**5. VERDICT:**
```
MERGE into S9 → "Researcher"
Delete Lab Bridge as separate subsystem.
```

---

### S11: ACI Refinery

```yaml
Location: context-management/tools/ai/aci/refinery.py
Type: Engine
```

**1. WHAT:** Context atomization - chunk, rank, prepare context for AI

**2. SINGULAR?** YES - "Prepare optimal context for AI queries"

**3. OVERLAP?**
  - Works FOR S3 (analyze.py)
  - Distinct from S3's routing function

**4. HOW TO ACCOMPLISH:**

```
S11 is correctly a SUB-COMPONENT of S3's ecosystem.
Not a peer subsystem.

Reclassify:
  S3: AI Query Engine
    └── S11: Context Preparation (internal module)
```

**5. VERDICT:**
```
DEMOTE from subsystem to component of S3.
S11 is not a top-level subsystem; it's internal to ACI.
```

---

### S12: Centripetal

```yaml
Location: .agent/tools/centripetal_scan.py
Type: Utility
```

**1. WHAT:** Deep 12-round analysis - intensive AI reasoning

**2. SINGULAR?** YES - "Deep multi-round AI analysis"

**3. OVERLAP?**
  - It's a MODE of S3 (analyze.py), not a separate system

**4. HOW TO ACCOMPLISH:**

```
S12 should be a flag/mode of S3:
  python analyze.py --mode centripetal "query"

Not a separate subsystem.
```

**5. VERDICT:**
```
DEMOTE from subsystem to mode of S3.
S12 is `analyze.py --mode deep`, not a separate system.
```

---

## OBSERVER REALM

### S5: Task Registry

```yaml
Location: .agent/registry/
Type: State
```

**1. WHAT:** Work tracking - store and query tasks

**2. SINGULAR?** YES - "Persist and query task state"

**3. OVERLAP?**
  - S10 (Enrichment) modifies tasks
  - S6 (BARE) reads tasks
  - S5 is the DATA, others are BEHAVIOR

**4. HOW TO ACCOMPLISH:**

```
S5 is correctly the STORE.
It should:
  ✓ Store tasks (YAML files)
  ✓ Provide query interface
  ✓ Emit events when tasks change

It should NOT:
  ✗ Decide which tasks to promote (that's S10)
  ✗ Execute tasks (that's S6)
```

**5. VERDICT:**
```
KEEP as-is.
S5 is correctly the data layer.
Add: Event emission interface for S6/S10 to subscribe.
```

---

### S6: BARE (Background Auto-Refinement Engine)

```yaml
Location: .agent/tools/bare
Type: Engine
```

**1. WHAT:** Autonomous refinement - continuously improve codebase

**2. SINGULAR?** VAGUE - "Auto-refinement" could mean:
  - Detecting issues (validation)
  - Fixing issues (execution)
  - Both?

**3. OVERLAP?**
  - S2 (HSL) validates semantics
  - S8 (Hygiene) validates syntax
  - S10 (Enrichment) improves tasks
  - What exactly does S6 do that others don't?

**4. HOW TO ACCOMPLISH:**

```
DEFINE S6 precisely:

BARE = "Autonomous EXECUTOR of refinements"

BARE does:
  ✓ Watch for triggers (commits, file changes)
  ✓ Match triggers to actionable tasks
  ✓ Execute refinement actions
  ✓ Report results

BARE does NOT:
  ✗ Validate (that's S2/S8)
  ✗ Decide priority (that's S10)
  ✗ Store tasks (that's S5)
```

**5. VERDICT:**
```
CLARIFY purpose.
BARE = "The executor" - it DOES things.
Validation, storage, prioritization are handled by others.
```

---

### S7: Archive

```yaml
Location: context-management/tools/archive/
Type: Utility
```

**1. WHAT:** Cloud mirroring - sync to GCS

**2. SINGULAR?** YES - "Mirror data to cloud"

**3. OVERLAP?** NO - Only S7 handles cloud sync

**4. HOW TO ACCOMPLISH:**
```
S7 is correctly isolated.
Single purpose, no overlap.
```

**5. VERDICT:**
```
KEEP as-is.
Clean, single-purpose utility.
```

---

### S8: Hygiene

```yaml
Location: .pre-commit-config.yaml
Type: Guard
```

**1. WHAT:** Pre-commit validation - syntax, format, rules

**2. SINGULAR?** YES - "Enforce commit quality rules"

**3. OVERLAP?**
  - S2 (HSL) also validates - but semantic, not syntactic
  - Boundary: S8 = fast, rule-based. S2 = slow, AI-based.

**4. HOW TO ACCOMPLISH:**

```
S8 = "Gate keeper for commits"

S8 checks:
  ✓ YAML/JSON/TOML syntax
  ✓ Whitespace, line endings
  ✓ Commit message format
  ✓ No secrets, no large files

S8 does NOT check:
  ✗ Semantic correctness (that's S2)
  ✗ Purpose coherence (that's Collider)
```

**5. VERDICT:**
```
KEEP as-is.
Boundary with S2 is clear: syntax vs semantics.
```

---

### S10: AEP (Enrichment)

```yaml
Location: .agent/tools/enrichment_orchestrator.py
Type: Engine
```

**1. WHAT:** Task promotion - move tasks from inbox to active

**2. SINGULAR?** YES - "Prioritize and promote tasks"

**3. OVERLAP?**
  - Works on S5's data
  - Distinct from S6's execution
  - Clean boundary

**4. HOW TO ACCOMPLISH:**

```
S10 = "The prioritizer"

S10 does:
  ✓ Score opportunities
  ✓ Decide what to promote
  ✓ Enrich task metadata

S10 does NOT:
  ✗ Execute tasks (that's S6)
  ✗ Store tasks (that's S5)
```

**5. VERDICT:**
```
KEEP as-is.
Consider rename: "Prioritizer" or "TaskPromoter"
```

---

### S13: Macro Registry

```yaml
Location: .agent/macros/
Type: State
```

**1. WHAT:** Recorded patterns - store and replay action sequences

**2. SINGULAR?** YES - "Store and replay action patterns"

**3. OVERLAP?**
  - Related to S6 (BARE executes, macros are WHAT to execute)
  - Clean boundary: S13 = patterns, S6 = execution

**4. HOW TO ACCOMPLISH:**

```
S13 = "Pattern library"

S13 stores:
  ✓ Recorded action sequences
  ✓ Trigger conditions
  ✓ Replay templates

S6 (BARE) uses S13 to know WHAT to do.
S13 doesn't execute; it just remembers.
```

**5. VERDICT:**
```
KEEP as-is.
Good separation: S13 = memory, S6 = muscle.
```

---

## SUMMARY: THE CONSOLIDATION PLAN

### Subsystems to KEEP (8)

| ID | Name | Purpose (Singular) |
|----|------|-------------------|
| S1 | Collider | Parse, classify, detect purpose in code |
| S3 | QueryEngine (analyze.py) | Route and execute AI queries |
| S4 | ExternalKnowledge (Perplexity) | Fetch external knowledge |
| S5 | TaskStore | Persist and query task state |
| S6 | Executor (BARE) | Execute refinement actions |
| S7 | Archive | Mirror data to cloud |
| S8 | Hygiene | Enforce commit quality rules |
| S10 | Prioritizer (AEP) | Score and promote tasks |

### Subsystems to MERGE (3 → 1)

| From | To | Reason |
|------|----|--------|
| S9 (Laboratory) | → Researcher | Same function, split location |
| S9b (Lab Bridge) | → Researcher | Same function, split location |
| S13 (Macros) | → Keep as S13 | Actually clean, keep |

### Subsystems to DEMOTE (2 → components)

| From | To | Reason |
|------|----|--------|
| S11 (ACI Refinery) | → Component of S3 | Sub-function of AI queries |
| S12 (Centripetal) | → Mode of S3 | Just a deep analysis flag |

### Subsystems to CLARIFY (2)

| ID | Clarification Needed |
|----|---------------------|
| S2 (HSL) | Define: "AI-powered semantic validation" vs S8's syntax validation |
| S6 (BARE) | Define: "Executor" - does things, doesn't decide what |

---

## FINAL SUBSYSTEM INVENTORY (Proposed)

```
PARTICLE (2)
├── P1: Collider (analyzer) - "Understand code structure and purpose"
└── (internal: Parser → Analyzer → Presenter phases)

WAVE (4)
├── W1: QueryEngine - "Route and execute AI queries"
│   └── (internal: Refinery, Centripetal mode)
├── W2: Validator (HSL) - "AI-powered semantic validation"
├── W3: Researcher - "Run codebase experiments"
└── W4: ExternalKnowledge - "Fetch from web/APIs"

OBSERVER (5)
├── O1: TaskStore - "Persist task state"
├── O2: Prioritizer - "Score and promote tasks"
├── O3: Executor (BARE) - "Run refinement actions"
├── O4: Hygiene - "Guard commit quality"
├── O5: Archive - "Mirror to cloud"
└── O6: MacroLibrary - "Store action patterns"
```

**Total: 11 subsystems (down from 13+)**
**Each has ONE clear purpose**
**Boundaries documented**

---

## IMPLEMENTATION STEPS

### Step 1: Document Boundaries (No Code Change)

Create `.agent/specs/SUBSYSTEM_BOUNDARIES.md`:
- For each subsystem pair, state the boundary
- "S2 validates semantics, S8 validates syntax"
- "S5 stores, S6 executes, S10 prioritizes"

### Step 2: Merge S9 + S9b

```bash
# Create new Researcher module
# Combine laboratory.py + laboratory_bridge.py
# Update LOL.yaml
```

### Step 3: Demote S11, S12

```bash
# Move refinery.py to be internal to analyze.py
# Make centripetal a --mode flag
# Update LOL.yaml
```

### Step 4: Rename for Clarity

```
analyze.py → query_engine.py (optional)
BARE → executor (in docs)
AEP → prioritizer (in docs)
```

---

*Each subsystem should pass the "10-word purpose test"*
