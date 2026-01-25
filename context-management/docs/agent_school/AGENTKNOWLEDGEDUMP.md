# Agent Knowledge Dump

> Crystallized context for AI agents and humans. Everything you need to understand PROJECT_elements.
> **Generated:** 2026-01-23 | **By:** Claude Opus 4.5

---

## TL;DR - The 30-Second Version

**What:** A framework that treats source code like physics - with atoms, particles, waves, and observers.

**Why:** Current AI sees code as text. We want AI to see code as ARCHITECTURE.

**How:** The **Collider** tool analyzes any codebase and outputs a structured "particle" of knowledge.

**Current Phase:** Building the self-improving infrastructure (BARE) so the system refines itself.

---

## The Physics Metaphor (This is the Core Insight)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE QUANTUM CODE METAPHOR                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   SOURCE CODE exists as a WAVE FUNCTION:                             │
│   - All possible interpretations superposed                          │
│   - Meaning is probabilistic until observed                          │
│   - Structure is latent, not explicit                                │
│                                                                      │
│   The COLLIDER performs MEASUREMENT:                                 │
│   - Collapses the wave function                                      │
│   - Extracts concrete PARTICLES (atoms, roles, dimensions)           │
│   - Produces unified_analysis.json                                   │
│                                                                      │
│   The OBSERVER (AI agent) DECIDES WHAT TO MEASURE:                   │
│   - Tasks define what to collapse                                    │
│   - Context determines resolution                                    │
│   - Questions shape the particle extracted                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

This isn't just a metaphor. It's the architecture:

| Realm | Directory | Physics Role | Contains |
|-------|-----------|--------------|----------|
| **Particle** | `standard-model-of-code/` | Measurement, collapse, certainty | Collider engine, atoms, schemas |
| **Wave** | `context-management/` | Potential, field, possibility | AI tools, research, planning |
| **Observer** | `.agent/` | Decides what to measure | Tasks, intelligence, BARE |

---

## The Standard Model of Code

Just as physics has its Standard Model (quarks, leptons, bosons), code has structural atoms:

### Atom Hierarchy

```
TIER 0: CORE (80 atoms)
├── Entity, Repository, Service, Controller, Middleware
├── Factory, Builder, Singleton, Observer, Strategy
├── Config, Router, Handler, Validator, Transformer
└── ... (language-agnostic, universal patterns)

TIER 1: STDLIB (varies by language)
├── Python: dataclass, asyncio, typing constructs
├── JavaScript: Promise, EventEmitter, Module
└── ... (standard library patterns)

TIER 2: ECOSYSTEM (3,536 atoms across 250+ ecosystems)
├── React: Component, Hook, Context, Reducer
├── FastAPI: Endpoint, Dependency, Schema
├── Django: Model, View, Serializer
└── ... (framework-specific patterns)
```

### The 8 Dimensions

Every atom is classified across 8 dimensions:

| Dimension | Question | Values |
|-----------|----------|--------|
| **Layer** | Where in the stack? | UI, API, Domain, Data, Infra |
| **Behavior** | What does it do? | Creates, Reads, Transforms, Orchestrates |
| **Lifecycle** | When does it run? | Boot, Request, Background, Shutdown |
| **Scope** | How far does it reach? | Local, Module, Global, External |
| **Mutability** | Does it change? | Immutable, Controlled, Free |
| **Visibility** | Who can see it? | Private, Internal, Public |
| **Cardinality** | How many instances? | Singleton, Pooled, Transient |
| **Criticality** | How important? | Core, Support, Optional |

### 33 Canonical Roles

Beyond atoms, code has roles (what it DOES in the system):

```
STRUCTURAL:    Entity, ValueObject, Aggregate, Repository
BEHAVIORAL:    Service, Handler, Processor, Transformer
INTEGRATION:   Client, Adapter, Gateway, Facade
ORCHESTRATION: Controller, Coordinator, Saga, Workflow
INFRASTRUCTURE: Config, Logger, Monitor, Migrator
...
```

---

## The Collider Tool

The practical tool that implements the theory:

```bash
# Full analysis of any codebase
./collider full /path/to/repo --output /tmp/analysis

# Output structure:
/tmp/analysis/
├── unified_analysis.json    # The collapsed "particle"
├── atoms.json               # All detected atoms
├── edges.json               # Relationships between atoms
├── metrics.json             # Complexity, coverage stats
└── visualization.html       # Interactive 3D graph
```

### The 18-Stage Pipeline

```
1. Discovery      → Find all files
2. Parsing        → Build AST per file
3. Extraction     → Identify code elements
4. Classification → Assign atoms (heuristic + AI)
5. Role Detection → Assign canonical roles
6. Dimension      → Classify across 8 dimensions
7. Edge Building  → Map relationships
8. Graph Assembly → Build unified graph
9. Metrics        → Calculate statistics
10. Constraint    → Apply validation rules
11. Synthesis     → Generate unified_analysis.json
...
```

---

## Current Developmental Track

### Where We Are (Sprint-001 EXECUTING)

```
PHASE 1: FOUNDATION        [COMPLETE]
├── Theory documented (MODEL.md)
├── Collider MVP working
├── 3,616 atoms defined
└── Pipeline operational

PHASE 2: INTELLIGENCE      [IN PROGRESS] ← WE ARE HERE
├── ACI system implemented ✓
├── BARE Phase 1 (TruthValidator) ✓
├── Task Registry with 4D confidence ✓
├── Sprint system operational ✓
└── Repo-org cleanup tasks queued

PHASE 3: AUTOMATION        [PLANNED]
├── BARE Phase 2 (CrossValidator)
├── BARE Phase 3 (ConceptMapper)
├── Full daemon mode
└── Self-optimization loop

PHASE 4: EMERGENCE         [VISION]
├── Autonomous task generation
├── Self-improving pipelines
└── AI-native development at scale
```

### Recent Commits (Development Velocity)

```
21d320b refactor: Adopt Particle/Wave duality (replace Body/Brain)
03f8ef5 docs: Update ARCHITECTURE_MAP with Particle/Wave duality
8c17c50 feat(aci): Implement Adaptive Context Intelligence system
e4e9586 chore: Audit .gitignore for generated outputs
9b83026 docs: Create ARCHITECTURE_MAP.md
9d38049 feat(.agent): Add YAML-based task registry CLI
c3b7518 chore(.agent): Transition SPRINT-001 to EXECUTING
957a7b3 docs(registry): Add 6 REPO-ORG tasks for cleanup
6c5a90f feat(.agent): Implement Sprint System and Discovery Inbox
```

---

## Key Systems

### 1. ACI (Adaptive Context Intelligence)

Auto-selects the right context tier for every query:

```
USER QUERY
    │
    ▼
┌─────────────────┐
│ QUERY ANALYZER  │ → Detects intent, complexity, scope
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TIER ROUTER    │ → Selects execution tier
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
 TIER 0    TIER 1   TIER 2   TIER 3
 INSTANT    RAG     GEMINI  PERPLEXITY
 (truths)  (search) (sets)  (external)
```

**Usage:**
```bash
python analyze.py --aci "how does atom classification work"
python analyze.py --aci "what tasks are ready to execute"
python analyze.py --aci --tier perplexity "latest Python best practices 2026"
```

### 2. BARE (Background Auto-Refinement Engine)

A self-improving daemon that:
- Validates truths about the repo
- Detects code-docs drift
- Boosts task confidence scores
- Discovers new opportunities
- Optimizes its own workflows

```
INPUTS                    PROCESSORS                 OUTPUTS
───────                   ──────────                 ───────
Codebase (git)     ──►    Truth Validator      ──►   repo_truths.yaml
Docs (*.md)        ──►    Cross Validator      ──►   drift_report.yaml
Research outputs   ──►    Concept Mapper       ──►   concept_graph.yaml
Task Registry      ──►    Confidence Booster   ──►   boosted tasks
Commits/Convos     ──►    Opportunity Explorer ──►   discovery inbox
Own Metrics        ──►    Self Optimizer       ──►   workflow patches
```

**Current Status:** Phase 1 complete (TruthValidator operational)

### 3. Task Registry with 4D Confidence

Every task is scored on 4 dimensions:

| Dimension | Question |
|-----------|----------|
| **Factual** | Is my understanding of current state correct? |
| **Alignment** | Does this serve the project's mission? |
| **Current** | Does this fit codebase as it exists? |
| **Onwards** | Does this fit where we're heading? |

**Overall = min(F, A, C, O)** - Bottleneck thinking

| Verdict | Threshold |
|---------|-----------|
| ACCEPT | >= 75% |
| DEFER | 50-74% |
| REJECT | < 50% |

### 4. HSL (Holographic-Socratic Layer)

24/7 AI guardian that validates semantic invariants:

```yaml
# semantic_models.yaml defines laws like:
antimatter:
  - id: AM001
    name: "Zombie Module"
    description: "Module imported but never used"
    detection_prompt: "Find imports with zero references"
    severity: HIGH
```

---

## Repository Statistics (Live from BARE)

```yaml
version: '2026-01-23T08:24:23'
validated_by: BARE/TruthValidator
confidence: 0.7

counts:
  files:
    python: 186
    javascript: 98
    yaml: 25
    markdown: 212
    json: 168
    html: 42
    css: 14
  lines_of_code: 130787
  functions: 341
  classes: 183

pipeline:
  stages: 18

atoms:
  total: 3616
  tier0_core: 80
  tier2_ecosystem: 3536
  ecosystems: 250+
```

---

## Directory Map

```
PROJECT_elements/
├── CLAUDE.md                    # Project entry point
├── AGENTKNOWLEDGEDUMP.md        # THIS FILE
│
├── standard-model-of-code/      # PARTICLE REALM
│   ├── docs/
│   │   ├── MODEL.md             # Theory spec
│   │   ├── COLLIDER.md          # Tool spec
│   │   └── specs/               # Detailed specs (UPB, etc.)
│   ├── src/
│   │   ├── core/                # Pipeline, classifiers
│   │   ├── patterns/            # Atom definitions (YAML)
│   │   └── viz/                 # Visualization (HTML/JS)
│   ├── schema/                  # JSON schemas
│   └── tests/                   # pytest suite
│
├── context-management/          # WAVE REALM
│   ├── config/
│   │   ├── analysis_sets.yaml   # Context sets for AI
│   │   ├── aci_config.yaml      # ACI configuration
│   │   └── semantic_models.yaml # HSL validation rules
│   ├── tools/
│   │   ├── ai/
│   │   │   ├── analyze.py       # Main AI interface
│   │   │   └── aci/             # ACI module
│   │   ├── mcp/                 # MCP servers (Perplexity)
│   │   └── archive/             # GCS sync tools
│   └── docs/
│       └── research/            # Perplexity/Gemini outputs
│
├── .agent/                      # OBSERVER REALM
│   ├── KERNEL.md                # Boot protocol
│   ├── manifest.yaml            # Discovery pointers
│   ├── SUBSYSTEM_INTEGRATION.md # How systems connect
│   ├── specs/
│   │   └── BACKGROUND_AUTO_REFINEMENT_ENGINE.md
│   ├── schema/                  # Task/Run schemas
│   ├── registry/                # Active tasks
│   ├── sprints/                 # Sprint definitions
│   ├── intelligence/
│   │   └── truths/              # BARE outputs
│   └── tools/                   # Claim/release scripts
│
└── archive/                     # Historical/staging
```

---

## How to Work Here

### For AI Agents

1. **Read KERNEL.md first** - Non-negotiable boot protocol
2. **Check registry/INDEX.md** - Find work to do
3. **Claim before working** - Atomic reservation prevents conflicts
4. **Use ACI for queries** - `--aci` flag auto-selects context
5. **Commit atomically** - Git is truth
6. **Log everything** - RUN records enable handoff

### For Humans

1. **Start at CLAUDE.md** - Project entry point
2. **Use Collider for analysis** - `./collider full <path>`
3. **Use analyze.py for AI queries** - `python analyze.py --aci "<query>"`
4. **Check .agent/registry for tasks** - What needs doing
5. **Read docs/research for context** - Perplexity/Gemini outputs

---

## Key Insights (Hard-Won Knowledge)

### Context Engineering

LLMs have U-shaped attention. They attend best to START and END of context.

```
Attention
    ^
    |  *                           *
    |   *                         *
    |    *       Lost in        *
    |     *     the Middle    *
    |        * * * * * * * *
    +---------------------------------> Position
```

**Mitigation:** Sandwich method - critical content at edges.

**Token Budgets:**
- Guru (<50k): Safe, focused
- Architect (50-150k): Multi-file reasoning
- Archeologist (150-200k): Deep exploration
- Perilous (>200k): Avoid - lost-in-middle dominates

### The Duality Pattern

Everything in this project has a dual nature:

| Concept World | Object World |
|---------------|--------------|
| Schema | Instance |
| Spec | Implementation |
| Type | Value |
| Theory | Data |
| Wave | Particle |

This pattern is FRACTAL - it applies at every level.

### Why "Standard Model of Code"?

Physics found ~17 fundamental particles that explain all matter.
We hypothesize code has ~80-100 fundamental structural patterns (atoms).

The analogy holds:
- **Atoms** = Quarks/Leptons (building blocks)
- **Roles** = Forces (how blocks interact)
- **Dimensions** = Properties (mass, charge, spin)
- **Collider** = Particle accelerator (reveals structure)

---

## What's Next

### Immediate (This Sprint)

1. Complete repo-org cleanup (TASK-122 through TASK-127)
2. BARE Phase 2 - CrossValidator for code-docs drift
3. Strengthen ACI feedback loop

### Near-Term

1. BARE Phase 3 - ConceptMapper for semantic graph
2. Full daemon mode for continuous refinement
3. Integration with Claude Code hooks

### Vision

A codebase that improves itself:
- Detects its own inconsistencies
- Proposes fixes with confidence scores
- Learns from human acceptance/rejection
- Evolves its own analysis patterns

---

## Quick Reference

| Need | Command/Path |
|------|--------------|
| Analyze repo | `./collider full . --output .collider` |
| AI query | `python analyze.py --aci "query"` |
| Check tasks | `.agent/registry/INDEX.md` |
| Claim task | `.agent/tools/claim_task.sh TASK-XXX agent-name` |
| Run tests | `cd standard-model-of-code && pytest tests/ -q` |
| Sync to GCS | `python context-management/tools/archive/archive.py mirror` |
| Boot protocol | `.agent/KERNEL.md` |
| Theory | `standard-model-of-code/docs/MODEL.md` |
| Subsystems | `.agent/SUBSYSTEM_INTEGRATION.md` |

---

*This document is a snapshot. The system evolves. When in doubt, check git log and .agent/registry.*
