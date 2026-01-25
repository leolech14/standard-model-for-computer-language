# GLOSSARY - PROJECT_elements

> The definitive terminology reference for humans and AI agents.

**Version:** 2.0.0
**Date:** 2026-01-25
**RFC 2119:** Terms MUST, SHOULD, MAY have normative meaning.

---

## NAVIGATION MAP

```
PROJECT_elements/
│
├── .agent/ ─────────────────────► OBSERVER (decides what to measure)
│   ├── registry/                   Tasks, schemas, state
│   ├── specs/                      Governance definitions
│   └── intelligence/               AI outputs
│
├── standard-model-of-code/ ─────► PARTICLE (collapsed reality)
│   ├── src/core/                   Collider pipeline
│   ├── docs/                       Theory (MODEL.md)
│   └── tools/                      Laboratory, utilities
│
└── context-management/ ──────────► WAVE (field of potential)
    ├── docs/                       This glossary, topology
    ├── tools/ai/                   analyze.py, ACI
    └── config/                     Semantic models
```

---

## THE ALGEBRA

```
UNIVERSES (Partition)
──────────────────────────────────────────────────────────
P = C ⊔ X           PROJECTOME = CODOME ⊔ CONTEXTOME
C ∩ X = ∅           Disjoint (no overlap)
X = P \ C           CONTEXTOME = PROJECTOME minus CODOME

REALMS (Partition)
──────────────────────────────────────────────────────────
P = Particle ⊔ Wave ⊔ Observer
    (directories are mutually exclusive)

DOMAINS (Cover)
──────────────────────────────────────────────────────────
⋃ Dᵢ = P            Domains cover everything
Dᵢ ∩ Dⱼ ≠ ∅         Overlap allowed (a file can be in multiple domains)

CLASSIFICATION (Function)
──────────────────────────────────────────────────────────
σ: Nodes → Atoms    Every node MUST map to exactly one atom

SYMMETRY (Relation)
──────────────────────────────────────────────────────────
R ⊆ C × X × S       Code × Docs × State
S = {SYMMETRIC, ORPHAN, PHANTOM, DRIFT}
```

---

## THE LOOP OF TRUTH

```
[CODEBASE]
    │
    │ (1. Scan)
    ▼
[COLLIDER] ───────► unified_analysis.json (Ground Truth)
                              │
                              ▼
[HSL / analyze.py] ◄──────────┘
    │
    │ (2. Validate)
    ▼
[TASK REGISTRY] ◄─── (3. Claim) ─── [BARE / AGENT]
                                          │
[CODEBASE] ◄──────── (4. Commit) ─────────┘
```

---

## CORE TERMS

### Universes

| Term | Definition |
|------|------------|
| **PROJECTOME** | The complete set of all files in the project. P = C ⊔ X. The universe. |
| **CODOME** | All executable code (.py, .js, .ts, .go, .rs, .css, .html). What runs. |
| **CONTEXTOME** | All non-executable content (.md, .yaml, .json configs). What informs. |

### Realms

| Term | Path | Definition |
|------|------|------------|
| **PARTICLE** | `standard-model-of-code/` | The collapsed reality. Measurement. Implementation. The Collider lives here. |
| **WAVE** | `context-management/` | The field of potential. Context. AI tools. Planning happens here. |
| **OBSERVER** | `.agent/` | The decision layer. Chooses what to measure. Tasks and governance live here. |

### Domains

| Term | Definition |
|------|------------|
| **DOMAIN** | A vertical slice through CODOME and CONTEXTOME. Every domain has code AND docs. |
| **Pipeline** | Domain: Collider stages, analysis logic. Code in `src/core/`, docs in `docs/specs/`. |
| **Visualization** | Domain: 3D graph rendering. Code in `viz/assets/`, docs in UI specs. |
| **Governance** | Domain: Task registry, confidence scoring. Code in `.agent/tools/`, docs in `.agent/specs/`. |
| **AI Tools** | Domain: analyze.py, ACI, research. Code in `tools/ai/`, docs in `config/`. |

---

## SUBSYSTEMS

| ID | Name | Type | Definition |
|----|------|------|------------|
| S1 | **Collider** | Engine | Static analysis pipeline. Parses code → extracts nodes → classifies atoms → builds graph. Outputs `unified_analysis.json`. |
| S2 | **HSL** | Framework | Holographic Socratic Layer. The conceptual validation rules. Detects drift between docs and code. |
| S3 | **analyze.py** | Tool | The implementation of HSL. Runs queries against the codebase with AI. `--verify` mode enforces rules. |
| S4 | **ACI** | System | Adaptive Context Intelligence. 5-tier query routing based on complexity. |
| S5 | **BARE** | Engine | Background Auto-Refinement Engine. Claims tasks, generates fixes, commits changes. The "hands" of the system. |
| S6 | **Laboratory** | Bridge | Research API connecting Wave (AI) to Particle (Collider). Runs experiments programmatically. |
| S7 | **Registry** | State | Task tracking system. Tasks are persistent, Runs are ephemeral. |

---

## CLASSIFICATION

### Atoms

| Term | Definition |
|------|------------|
| **Atom** | A semantic category assigned to a code node. 3,616 total across tiers. |
| **Tier 0** | Core AST atoms (42). Definitional. 100% coverage. |
| **Tier 1** | Standard library patterns (21). 20-40% coverage. |
| **Tier 2** | Ecosystem-specific (3,531). Variable coverage. |

### Roles (33 Canonical)

| Category | Roles |
|----------|-------|
| Query | Query, Finder, Loader, Getter |
| Command | Command, Creator, Mutator, Destroyer |
| Factory | Factory, Builder |
| Storage | Repository, Store, Cache |
| Orchestration | Service, Controller, Manager |
| Validation | Validator, Guard, Asserter |
| Transform | Transformer, Mapper, Serializer |
| Event | Handler, Listener, Subscriber |
| Utility | Utility, Formatter, Helper |
| Internal | Internal, Lifecycle |
| Unknown | Unknown (fallback) |

---

## SYMMETRY STATES

| State | Code | Docs | Definition |
|-------|------|------|------------|
| **SYMMETRIC** | ✓ | ✓ | Code and docs exist and match. Healthy. |
| **ORPHAN** | ✓ | ✗ | Code exists without documentation. Tech debt. |
| **PHANTOM** | ✗ | ✓ | Documentation exists without implementation. Spec not built. |
| **DRIFT** | ✓ | ✓ | Both exist but disagree. Dangerous. |

---

## OPERATIONAL PROTOCOL

### Work Units

| Term | Persistence | Definition |
|------|-------------|------------|
| **Task** | Persistent | Strategic unit. Survives sessions. What SHOULD be true. Stored in registry. |
| **Run** | Ephemeral | Tactical unit. Dies with session. What IS happening now. |

### Confidence

| Term | Definition |
|------|------------|
| **4D Confidence** | `min(Factual, Alignment, Current, Onwards)`. All four dimensions MUST score. |
| **Factual** | Does this match reality? Evidence-based. |
| **Alignment** | Does this serve the project mission? |
| **Current** | Is this up to date? |
| **Onwards** | Does this enable future work? |

### Artifacts

| Term | Definition |
|------|------------|
| **unified_analysis.json** | The canonical output of Collider. Single source of truth for code state. |
| **Ground Truth** | Data verified by Collider. Confidence 100%. |
| **Inference** | Data derived by AI. Confidence < 100%. |

---

## FOUNDATIONAL STRUCTURES

### Three Planes

| Plane | Substance | Question |
|-------|-----------|----------|
| **Physical** | Bits, bytes, files | Where is it stored? |
| **Virtual** | AST, runtime objects | What is its form? |
| **Semantic** | Meaning, intent | What does it mean? |

### 16-Level Scale

| Zone | Levels | Description |
|------|--------|-------------|
| Cosmological | L8-L12 | Universe → Domain → Org → Platform → Ecosystem |
| Systemic | L4-L7 | System → Package → File → Container |
| Semantic | L1-L3 | Node → Block → Statement |
| Syntactic/Physical | L-3-L0 | Token → Character → Byte → Bit |

**Operational Zone:** L3-L7 (Node to System). This is where Collider classifies.

### 8 Dimensions

| Dimension | Question |
|-----------|----------|
| WHAT | What type? (Atom) |
| LAYER | Where in architecture? |
| ROLE | What purpose? |
| BOUNDARY | Crosses boundaries? |
| STATE | Maintains state? |
| EFFECT | Side effects? |
| LIFECYCLE | What phase? |
| TRUST | How confident? |

---

## CONCEPT/OBJECT DUALITY

```
LEVEL           CONCEPT (Definition)        OBJECT (Instance)
─────────────   ────────────────────────    ─────────────────────
Work Mgmt       task.schema.yaml        ──► TASK-001.yaml
Execution       run.schema.yaml         ──► RUN-20260125-CLAUDE
Validation      semantic_models.yaml    ──► repo_truths.yaml
Classification  roles.json              ──► unified_analysis.json
```

**Rule:** Concepts define structure. Objects are instances. ALWAYS schema-first.

---

## EDGE TYPES

| Type | Direction | Meaning | Example |
|------|-----------|---------|---------|
| **calls** | A → B | A invokes B | `main() calls init()` |
| **imports** | A → B | A depends on B | `app.py imports utils` |
| **inherits** | A → B | A extends B | `Dog inherits Animal` |
| **implements** | A → B | A realizes B | `UserRepo implements IRepo` |
| **contains** | A → B | A holds B | `Class contains method` |
| **uses** | A → B | A references B | `handler uses logger` |

---

## ETYMOLOGY

| Term | Origin | Meaning |
|------|--------|---------|
| **-ome** | Greek -ωμα | Complete set (genome, proteome) |
| **Particle/Wave** | Quantum physics | Duality of measurement vs potential |
| **Collider** | Particle physics | Tool that smashes things to find constituents |
| **Holons** | Koestler | Parts that are also wholes |
| **Three Worlds** | Popper | Physical, mental, abstract knowledge |

---

## QUICK REFERENCE

```
PROJECTOME = CODOME ⊔ CONTEXTOME     (partition)
CODOME     = all executable code
CONTEXTOME = all non-executable content
DOMAINS    = vertical slices (cover, may overlap)
REALMS     = Particle | Wave | Observer (partition by directory)

σ: Nodes → Atoms                     (classification function)
R: Code × Docs → Symmetry State      (symmetry relation)

Confidence = min(Factual, Alignment, Current, Onwards)
```

---

---

## PURPOSE FIELD (Teleological Layer)

> Full formalization in `CODESPACE_ALGEBRA.md` §10

| Term | Definition |
|------|------------|
| **Purpose Field** | 𝒫: N → ℝᵏ — Vector field over nodes defining WHAT each entity is FOR |
| **Purpose = Identity** | IDENTITY(n) ≡ 𝒫(n) — You ARE what you're FOR |
| **Focusing Funnel** | Purpose is diffuse at L0, sharp at L12 (emergent from aggregation) |
| **Transcendence** | Entity gains purpose by participating in level L+1 |
| **Dynamic Purpose** | 𝒫_human(t) — Flows and adapts moment-to-moment |
| **Crystallized Purpose** | 𝒫_code(t) — Frozen at commit, static until next change |
| **Purpose Drift** | Δ𝒫 = 𝒫_human - 𝒫_code — Gap between human intent and frozen code |
| **Technical Debt** | ∫|d𝒫_human/dt|dt — Accumulated purpose change since commit |
| **Emergence Signal** | ‖𝒫(parent)‖ > Σ‖𝒫(children)‖ → New layer born |

### Physical Analogy

| Code Concept | Physics Analogy |
|--------------|-----------------|
| Purpose vector | Magnetic dipole moment |
| System purpose | External B-field |
| Misalignment | Stored potential energy |
| Refactoring | Torque realigning dipoles |
| Evolution | Gradient descent on energy |

---

## QUERY MANIFEST (AI Record Format)

> The canonical record of an AI query. Schema in `config/query_manifest_schema.yaml`

| Field | Purpose |
|-------|---------|
| **model** | name, provider, tier, temperature |
| **context** | type, sources, tokens_est, truncation |
| **metrics** | input_tokens, output_tokens, latency_ms, cost_usd |
| **quality** | confidence, completeness, specificity |
| **result** | takeaway, key_findings |
| **implications** | applies_to, documented_in, action_items |

**Compact Format:**
```
# QUERY MANIFEST
model: MODEL | temp=T | tier=TIER
context: TOKENSk from SOURCE
metrics: in=INk out=OUTk latency=Ts cost=$C
quality: conf=C complete=C specific=S
takeaway: "SUMMARY"
documented_in: PATH
```

**Principle:** If you can't show the manifest, the query didn't happen.

---

## SEE ALSO

| Doc | Purpose |
|-----|---------|
| `CODOME.md` | Executable universe definition |
| `CONTEXTOME.md` | Non-executable universe definition |
| `PROJECTOME.md` | Complete contents definition |
| `DOMAINS.md` | Vertical slice definitions |
| `TOPOLOGY_MAP.md` | Master navigation guide |
| `.agent/SUBSYSTEM_INTEGRATION.md` | System connections |
| `standard-model-of-code/docs/MODEL.md` | Full theory |
| `CODESPACE_ALGEBRA.md` | Mathematical formalization (Purpose Field, Emergence, Constructal Law) |

---

*Created: 2026-01-25*
*Sources: Gemini analysis, Perplexity validation, legacy glossary, MODEL.md*
*Structure: RFC 2119 compliant, AI-agent optimized*
