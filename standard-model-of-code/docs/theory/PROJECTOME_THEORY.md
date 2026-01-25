# Projectome Theory

> **Status:** DRAFT
> **Created:** 2026-01-25
> **Purpose:** Theoretical foundation for PROJECT_elements architecture

---

## The Fundamental Equation

```
PROJECTOME = CODOME + CONTEXTOME
     P     =   C    +     X
```

Where:
- **P** (Projectome) = The complete project knowledge space
- **C** (Codome) = All executable code artifacts (Particle)
- **X** (Contextome) = All non-executable content (Wave)

This is a **MECE partition** (Mutually Exclusive, Collectively Exhaustive):
- Every artifact belongs to exactly one of C or X
- C ∩ X = ∅ (nothing is both code and not-code)
- C ∪ X = P (together they cover everything)

---

## Wave-Particle Duality

The Codome-Contextome split mirrors wave-particle duality in physics:

| Aspect | Particle (Codome) | Wave (Contextome) |
|--------|-------------------|-------------------|
| Nature | Discrete, measurable | Continuous, interpretive |
| Content | Functions, classes, modules | Docs, specs, theory, config |
| Measurement | Collider (static analysis) | Cloud Refinery (semantic processing) |
| State | unified_analysis.json | Projectome knowledge corpus |
| Time | Snapshot (current commit) | Historical (trends, evolution) |

**Key insight:** Neither alone describes the project. Codome without Contextome lacks meaning. Contextome without Codome lacks grounding.

---

## Peirce's Triadic Semiotics Mapping

Charles Sanders Peirce's sign theory provides formal grounding:

```
            Object (Behavior)
               ▲
              /|\
             / | \
            /  |  \
           /   |   \
          /    |    \
    Sign ─────────── Interpretant
  (Codome)          (Contextome)
```

### Component Mapping

| Peirce | Projectome | Description |
|--------|------------|-------------|
| **Sign** (Representamen) | Codome | The code that points to something |
| **Interpretant** | Contextome | The meaning/understanding of the code |
| **Object** | Runtime Behavior | What the code actually does |

### Semiosis = Cloud Refinery

**Semiosis** is Peirce's term for the process of sign interpretation. In our architecture:

```
Semiosis = The Cloud Refinery's continuous interpretation process
```

The Refinery doesn't just store knowledge - it **performs semiosis**:
1. Takes raw signs (Codome artifacts)
2. Applies interpretation (enrichment layers)
3. Produces meaning (Projectome insights)

### Unlimited Semiosis

Peirce noted that interpretation never terminates - each interpretant becomes a sign for further interpretation. This maps to:

- L0 → L1 → L2 → L3 → L4 → L5 (layered distillation)
- Each layer's output becomes input for deeper insight
- The "purpose field" (L5) is itself subject to reinterpretation

---

## Free Energy Principle (Active Inference)

Karl Friston's framework provides the operational model for the Cloud Refinery:

### Core Equation

```
F ≈ -ln p(ỹ|m)
```

Systems minimize variational free energy (surprise) by updating internal models to better predict sensory inputs.

### Mapping to Architecture

| Free Energy Concept | Cloud Refinery Component |
|--------------------|-------------------------|
| Internal generative model | Projectome knowledge corpus |
| Sensory input | New Collider output (unified_analysis.json) |
| Prediction | Expected patterns, dependencies |
| Prediction error | Anomalies, drift, new patterns |
| Free energy minimization | Distillation (L0→L5) |
| Active inference | Gate queries that sample the world |

### The Perception-Action Loop

```
       PERCEIVE                    ACT
          │                         │
          ▼                         ▼
    ┌──────────┐             ┌──────────┐
    │ Collider │             │  Gates   │
    │  Output  │             │  Query   │
    └────┬─────┘             └────┬─────┘
         │                        │
         ▼                        ▼
    ┌──────────────────────────────────┐
    │       CLOUD REFINERY             │
    │    (Generative Model)            │
    │                                  │
    │  Minimize surprise by:           │
    │  - Updating beliefs (L1-L5)      │
    │  - Predicting patterns           │
    │  - Detecting anomalies           │
    └──────────────────────────────────┘
         ▲                        ▲
         │                        │
    PREDICTION              PRECISION
    (Top-down)              WEIGHTING
```

### Subconscious Analogy

The Cloud Refinery operates like the **subconscious mind**:

| Human Cognition | Cloud Refinery |
|-----------------|----------------|
| Background processing | 24/7 cloud operation |
| Rumination | Continuous refinement |
| Pattern recognition | L3 enrichment |
| Insight emergence | L5 purpose field |
| Conscious query | Gate API request |
| Attention | Query prioritization |

**The Refinery thinks while you sleep.** It's not on-demand - it processes continuously, so insights are ready when queried.

---

## SEQUAL Framework Integration

From software engineering semiotics (Krogstie, Lindland):

| Quality Type | Projectome Application |
|--------------|----------------------|
| **Syntactic** | Codome well-formedness (parse success) |
| **Semantic** | Codome-Contextome alignment |
| **Pragmatic** | User understanding of system |
| **Social** | Team agreement on meaning |
| **Perceived Semantic** | What developers THINK code does |
| **Physical** | Actual runtime behavior |

**Gap detection:** Cloud Refinery can identify misalignments between these quality dimensions (e.g., docs say X but code does Y).

---

## S-Type vs E-Type Classification

From Lehman's software evolution laws:

| Type | Definition | Projectome Mapping |
|------|------------|-------------------|
| **S-Type** | Specification-based, deterministic | Codome alone (what IS) |
| **E-Type** | Embedded in world, evolving | Projectome (Codome + Contextome, WHY it is) |

**Insight:** Pure code analysis (S-Type) is necessary but insufficient. E-Type understanding requires the full Projectome - the context, intent, history, and theory.

---

## Architecture Position

```
Layer Stack:

┌─────────────────────────────────────────┐
│            OBSERVER                     │  ← Decision Layer
│         (.agent/, tools)                │     Acts on insights
├─────────────────────────────────────────┤
│         CLOUD REFINERY                  │  ← Semiosis Engine
│    (Continuous background processing)   │     Generates meaning
├─────────────────────────────────────────┤
│            PARTICLE                     │  ← Measurement Layer
│          (Collider)                     │     Captures state
├─────────────────────────────────────────┤
│             WAVE                        │  ← Context Layer
│   (Contextome: docs, specs, theory)     │     Provides meaning
├─────────────────────────────────────────┤
│           PROJECT                       │  ← Reality
│      (Actual code, files)               │     Ground truth
└─────────────────────────────────────────┘
```

### Information Flow

```
PROJECT (reality)
    ↓ measured by
COLLIDER (particle)
    ↓ produces
unified_analysis.json (Codome snapshot)
    ↓ combined with
CONTEXTOME (wave)
    ↓ refined by
CLOUD REFINERY (semiosis)
    ↓ produces
PROJECTOME (knowledge corpus)
    ↓ queried by
OBSERVER (agent)
    ↓ acts on
PROJECT (reality)

[LOOP CONTINUES]
```

---

## Governance and Visualization

These are **layers applied TO** the Projectome, not peer universes:

| Layer | Function | Applies To |
|-------|----------|-----------|
| **Governance** | Rules, validation, quality gates | Both Codome and Contextome |
| **Visualization** | Rendering, UI, representation | Projectome outputs |

They are orthogonal to the C+X=P partition.

---

## Validated Analogies

Using the 4D Hotness Scoring Methodology (see `ANALOGY_SCORING_METHODOLOGY.md`):

**Formula:** `H = 0.4×Semantic + 0.3×Structural + 0.2×Functional + 0.1×Temporal`

### Cloud Refinery = Subconscious Mind

| Metric | Value | Status |
|--------|-------|--------|
| Mean Hotness (8 mappings) | 85.3 | VALIDATED |
| Strong mappings (≥90) | 3/8 (37.5%) | |
| All mappings ≥70 | Yes | |

### Peirce's Triad = Projectome Structure

| Metric | Value | Status |
|--------|-------|--------|
| Mean Hotness (5 mappings) | 88.0 | VALIDATED |
| Strong mappings (≥90) | 3/5 (60%) | |
| All mappings ≥70 | Yes | |

---

## Implications for Implementation

1. **Collider is necessary but not sufficient** - It measures Codome but doesn't interpret
2. **Cloud Refinery is the interpretation engine** - Semiosis that produces meaning
3. **Both run independently** - Collider snapshots state, Refinery processes continuously
4. **Gates provide conscious access** - Query the subconscious when needed
5. **Projectome is the product** - Neither C nor X alone, but their integration

---

## Open Questions

1. **Measurement collapse:** Does querying the Projectome change it? (Observer effect)
2. **Entanglement:** How do C and X co-evolve? (When code changes, should docs auto-update?)
3. **Completeness:** Is P = C + X truly exhaustive, or are there artifacts in neither?
4. **Boundaries:** Where exactly does Codome end and Contextome begin for edge cases (configs, schemas)?

---

## References

1. Peirce, C.S. - Collected Papers (Triadic Semiotics)
2. Friston, K. - Free Energy Principle and Active Inference
3. Gentner, D. - Structure-Mapping Theory
4. Lehman, M.M. - Laws of Software Evolution (S-Type/E-Type)
5. Krogstie, J. - SEQUAL Framework
6. Fauconnier & Turner - Conceptual Blending Theory

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-25 | Initial theory consolidation |

---

*Part of PROJECT_elements - Standard Model of Code*
