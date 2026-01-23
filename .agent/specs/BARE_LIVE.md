# BARE-Live: Semantic Context Refinery

> Continuous background refinement of repository knowledge through
> outside-in semantic distillation, atomization, and governed execution.

**Status:** DESIGN PHASE | **Version:** 0.1.0 | **Date:** 2026-01-23

---

## Vision

BARE-Live evolves the Background Auto-Refinement Engine into a **Semantic Context Refinery** -
a 24/7 system that transforms raw repository content into distilled, addressable knowledge atoms.

**Core insight:** We apply the Collider's logic to context itself.
- Collider breaks code into structural atoms and reassembles patterns
- BARE-Live breaks the repo into **semantic atoms** and reassembles **context packs**

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                              BARE-LIVE ARCHITECTURE                            │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   CORPUS (everything processable)                                              │
│   ├── Repo HEAD (current state)                                               │
│   ├── Git history (deleteds, renames, lineages)                               │
│   ├── Archives (legacy, benchmarks, dumps)                                    │
│   └── Research outputs (perplexity/, gemini/)                                 │
│                                                                                │
│   ════════════════════════════════════════════════════════════════════════    │
│                                                                                │
│              OUTSIDE-IN REFINEMENT (Coarse → Fine → Coarse+)                   │
│                                                                                │
│   L0 ──► INVENTORY + DELTA DETECTOR                                           │
│          "what exists, what changed"                                           │
│                    │                                                           │
│                    ▼                                                           │
│   L1 ──► BOUNDARY MAPPER + SEMANTIC CLUSTERER                                 │
│          "where are the regions, how do files group"                           │
│                    │                                                           │
│                    ▼                                                           │
│   L2 ──► DISTILLER + ATOMIZER                                                 │
│          "extract meaning, create addressable atoms"                           │
│                    │                                                           │
│                    ▼                                                           │
│   L3 ──► GLOBAL SYNTHESIZER                                                   │
│          "recompile global view with more texture"                             │
│                    │                                                           │
│                    ▼                                                           │
│   ════════════════════════════════════════════════════════════════════════    │
│                                                                                │
│   INTELLIGENCE STORE                                                           │
│   ├── state/live.yaml         (global map)                                    │
│   ├── clusters/CLUSTER-*.yaml (semantic groups)                               │
│   ├── atoms/ATOM-*.yaml       (addressable knowledge)                         │
│   ├── coverage/ledger.yaml    (processing progress)                           │
│   └── drift/*.yaml            (staleness tracking)                            │
│                                                                                │
│   ════════════════════════════════════════════════════════════════════════    │
│                                                                                │
│   CONSUMERS                                                                    │
│   ├── ACI (Context Compiler) → builds query-specific packs                    │
│   ├── HSL (Socratic Layer)   → validates critical claims                      │
│   └── Sprints/Tasks          → governed execution                             │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Principles (Invariants)

### 1. Outside-In (Fora → Dentro)
Start with the whole at low resolution. Establish boundaries. Then zoom in.
The map comes before the detail. The first version can be ugly - but must exist.

### 2. Coarse-to-Fine in Layers
Operate in resolution levels:
- **L0:** Inventory + metrics + truths (fast, cheap)
- **L1:** Clusters + boundaries + coverage (moderate)
- **L2:** Distillation per cluster (expensive, targeted)
- **L3:** Global synthesis (periodic recompilation)

Always return to the whole with more texture.

### 3. Delta-First (Never Reprocess Everything)
The default is: reprocess only what changed.
Full reprocessing only on high drift or structural changes.

### 4. Atomization (Everything Becomes a Node)
- Cluster → Node
- Insight → Node
- Contradiction → Node
- Gap → Opportunity Node

This enables powerful recompilation.

### 5. Provenance (No Claim Without Source)
Every output traces back to inputs:
- path + sha + lines
- processor version + timestamp
- confidence score

### 6. Governance (Autonomy with Gates)
Autonomy is allowed for:
- Mapping, distilling, auditing, suggesting

Promotion to execution is gated:
- Threshold + review + workflow

---

## Glossary

### Structures
| Term | Definition |
|------|------------|
| **Corpus** | Everything processable (repo + history + archives + research) |
| **Inventory** | Index of corpus (files, hashes, timestamps, metadata) |
| **Boundary** | Semantic frontier at macro level (analysis_sets.yaml = boundary map) |
| **Cluster** | Dynamic semantic grouping (can cross paths/sets) |
| **Atom/Node** | Addressable unit with ID + provenance + relations |
| **Digest/State** | Low-resolution global view |

### Temporal
| Term | Definition |
|------|------------|
| **Delta** | What changed since last snapshot (new/modified/deleted/renamed) |
| **Coverage** | Percentage processed (by stage and boundary, not just global) |
| **Drift** | Semantic/structural change magnitude (reprocessing signal) |
| **Recency** | Temporal weight (recent changes get priority) |
| **Lineage** | Evolution history (renames, movements, origins) |

### Operations
| Term | Definition |
|------|------------|
| **Distillation** | Reduce noise, preserve operability |
| **Compilation** | Build query-specific context pack (atoms + deltas + evidence) |
| **Self-Audit** | System measures itself (coverage, contradictions, bias, gaps) |
| **Promotion** | Move Opportunity → Task (gated) |

---

## Processors (L0-L3)

### L0: Inventory + Delta Detector

**Runs:** On every commit, every 5 minutes (cron)

```yaml
# .agent/intelligence/inventory/inventory.yaml
version: "2026-01-23T09:00:00Z"
processor: "BARE-Live/Inventory"

files:
  total: 942
  by_type:
    python: 127
    javascript: 48
    yaml: 34
    markdown: 89
  largest:
    - path: "src/core/viz/assets/app.js"
      size_kb: 280

deltas:
  since_sha: "abc123"
  new: 3
  modified: 7
  deleted: 1
  renamed: 0
```

### L1: Boundary Mapper + Semantic Clusterer

**Runs:** On significant deltas, hourly

```yaml
# .agent/intelligence/boundaries/boundary_map.yaml
version: "2026-01-23T09:00:00Z"
processor: "BARE-Live/BoundaryMapper"

regions:
  body:
    set: "pipeline"
    files: 45
    coverage: 0.92
  brain:
    set: "brain"
    files: 78
    coverage: 0.85
  agent:
    set: "agent_full"
    files: 34
    coverage: 0.78
  unclassified:
    files: 12
    candidates_for_clustering: true
```

```yaml
# .agent/intelligence/clusters/CLUSTER-007.yaml
id: "CLUSTER-007"
name: "Atom Classification Pipeline"
version: "2026-01-23T09:00:00Z"
processor: "BARE-Live/SemanticClusterer"

members:
  - path: "src/core/atom_classifier.py"
    centrality: 0.95
  - path: "src/core/atom_loader.py"
    centrality: 0.82
  - path: "src/patterns/ATOMS_TIER0.yaml"
    centrality: 0.78

metrics:
  file_count: 8
  total_lines: 2340
  avg_centrality: 0.71
  drift_score: 0.12
  last_significant_change: "2026-01-21"

boundaries_crossed: ["body", "patterns"]
```

### L2: Distiller + Atomizer

**Runs:** When cluster reaches threshold (20 files or high drift)

```yaml
# .agent/intelligence/atoms/ATOM-0001.yaml
id: "ATOM-0001"
kind: "concept"  # concept | module | interface | invariant | decision | risk | gap | conflict
title: "Atom classification pipeline - high-level behavior"
status: "ACTIVE"  # ACTIVE | DEPRECATED | SUPERSEDED
created_at: "2026-01-23T09:15:00Z"
updated_at: "2026-01-23T09:15:00Z"

summary:
  one_liner: "Defines how raw inputs become classified atoms via staged transforms."
  details: |
    The atom classification pipeline operates in 4 stages:
    1. Loading (ATOMS_TIER*.yaml → memory)
    2. Matching (file patterns → candidate atoms)
    3. Scoring (confidence per dimension)
    4. Selection (highest confidence wins)

    Key invariant: Every file gets exactly one atom classification.

provenance:
  source_type: "repo"  # repo | git_history | external_archive | research
  head_sha: "abc123"
  inputs:
    - path: "src/core/atom_classifier.py"
      sha: "abc123"
      lines: "L10-L220"
    - path: "docs/MODEL.md"
      sha: "abc123"
      lines: "L45-L89"

boundaries:
  sets: ["pipeline", "classifiers"]
  cluster_id: "CLUSTER-007"

confidence_4d:
  factual: 0.85
  alignment: 0.95
  current: 0.80
  onwards: 0.90
  overall: 0.80  # min()

relations:
  depends_on: ["ATOM-0003", "ATOM-0012"]
  related_to: ["ATOM-0020"]
  conflicts_with: []

actions:
  opportunities: []
  tasks: []

tags: ["collider", "classification", "pipeline", "core"]
```

### L3: Global Synthesizer

**Runs:** Hourly, or on major drift

```yaml
# .agent/intelligence/state/live.yaml
version: "2026-01-23T10:00:00Z"
processor: "BARE-Live/GlobalSynthesizer"

state: "expanding"  # stable | expanding | contracting | refactoring

coverage:
  total_files: 942
  processed: 0.87
  by_region:
    body: 0.92
    brain: 0.85
    agent: 0.78

clusters:
  total: 14
  active: 12
  stale: 2

atoms:
  total: 156
  by_kind:
    concept: 45
    module: 67
    interface: 23
    invariant: 12
    gap: 9

hotspots:
  - cluster: "CLUSTER-007"
    reason: "High change frequency, core pipeline"
  - cluster: "CLUSTER-012"
    reason: "Documentation drift detected"

gaps:
  - id: "GAP-001"
    description: "No atoms for test infrastructure"
    severity: "medium"
  - id: "GAP-002"
    description: "Archive directory unprocessed"
    severity: "low"

contradictions: []

focus_recommendation: "Complete atom coverage for CLUSTER-007 before expanding"

confidence: 0.94
```

---

## Self-Audit + Drift Monitor

**Runs:** Continuously, emits Opportunities

```yaml
# .agent/intelligence/audit/self_audit.yaml
version: "2026-01-23T10:30:00Z"
processor: "BARE-Live/SelfAudit"

coverage_gaps:
  - region: "archive"
    processed: 0.0
    recommendation: "Schedule archaeological pass"

drift_alerts:
  - cluster: "CLUSTER-003"
    drift_score: 0.45
    threshold: 0.30
    action: "REPROCESS"

bias_detection:
  - finding: "70% of atoms are from Body hemisphere"
    expected: "50/50 Body/Brain"
    action: "Prioritize Brain distillation"

stale_atoms:
  - id: "ATOM-0023"
    last_verified: "2026-01-15"
    days_stale: 8
    action: "REVERIFY"

opportunities_generated:
  - ref: "OPP-005"
    source: "drift_alert"
    description: "Reprocess CLUSTER-003 due to high drift"
```

---

## Context Compiler (ACI Integration)

When a query arrives, the Context Compiler builds an optimal pack:

```python
# Pseudocode for context compilation
def compile_context(query: str, budget_tokens: int) -> ContextPack:
    profile = analyze_query(query)  # ACI

    # 1. Select relevant atoms
    atoms = select_atoms(
        intent=profile.intent,
        scope=profile.scope,
        clusters=get_relevant_clusters(query)
    )

    # 2. Add recent deltas for freshness
    deltas = get_recent_deltas(
        clusters=[a.cluster_id for a in atoms],
        since=days(3)
    )

    # 3. Include evidence snippets
    evidence = extract_evidence(
        atoms=atoms,
        max_tokens=budget_tokens * 0.3
    )

    # 4. Add global state summary
    state = load_live_state()

    # 5. Compile with positional strategy
    return ContextPack(
        state_summary=state.one_liner,  # front
        atoms=atoms,                     # middle
        evidence=evidence,               # middle
        deltas=deltas,                   # end (freshest last)
        total_tokens=sum_tokens()
    )
```

---

## Decision Deck Layer (Governance)

BARE-Live produces knowledge. The Decision Deck governs execution.

### Certified Moves (Cards)

Every action the system can take is a **Card** with:
- Preconditions (what must be true)
- Steps (tool invocations)
- Evidence (what proves success)
- Rollback (how to revert)

```yaml
# Example Card
card: "promote_opportunity"
intent: "task"
preconditions:
  - "OPP exists in inbox"
  - "Sprint not in EXECUTING (or override)"
steps:
  - validate_schema(opp)
  - run: ".agent/tools/promote_opportunity.py ${OPP_ID}"
  - add_to_sprint_backlog()
evidence:
  - "TASK-*.yaml created in registry/active/"
  - "OPP marked PROMOTED"
rollback:
  - delete_task()
  - restore_opp()
risk_level: "low"
```

### Meters (System Health)

| Meter | Description |
|-------|-------------|
| **Focus** | Alignment to current sprint DoD |
| **Reliability** | Evidence + checks pass rate |
| **Debt** | Skipped tests/docs/cleanup |
| **Discovery Pressure** | Exploration without venting to Inbox |
| **Coverage** | Distilled understanding percentage |

### Hard Rules (Never Break)
- No edits to critical files without explicit override
- No promotion OPP→TASK unless gate satisfied
- No large refactors during EXECUTING unless DoD demands
- No deletion without staged diff + rollback

### Soft Constraints (Meter Penalties)
- Skipping tests increases Debt
- Exploring during EXECUTING decreases Focus
- Repeated failures reduce autonomy level

---

## Directory Structure

```
.agent/intelligence/
├── state/
│   └── live.yaml                    # Global synthesis (L3)
├── inventory/
│   ├── inventory.yaml               # File index (L0)
│   └── deltas/
│       └── DELTA-{sha}.yaml         # Change tracking
├── boundaries/
│   └── boundary_map.yaml            # Region definitions (L1)
├── clusters/
│   ├── CLUSTER-001.yaml
│   ├── CLUSTER-002.yaml
│   └── ...
├── atoms/
│   ├── ATOM-0001.yaml
│   ├── ATOM-0002.yaml
│   └── ...
├── coverage/
│   └── ledger.yaml                  # Processing progress
├── drift/
│   ├── drift_report.yaml
│   └── history/
├── audit/
│   └── self_audit.yaml
├── truths/                          # From BARE Phase 1
│   └── repo_truths.yaml
├── concepts/                        # From BARE Phase 1
│   └── concept_graph.yaml
└── metrics/
    └── bare_metrics.yaml
```

---

## Cadence

| Processor | Trigger | Cost |
|-----------|---------|------|
| Inventory | Every commit, 5min cron | Low |
| Delta Detector | With Inventory | Low |
| Boundary Mapper | Hourly | Low |
| Semantic Clusterer | Hourly, on significant delta | Medium |
| Distiller | Per-cluster threshold | High (LLM) |
| Atomizer | With Distiller | Medium |
| Global Synthesizer | Hourly | Medium (LLM) |
| Self-Audit | Continuous | Low |

---

## Integration Points

| System | Integration |
|--------|-------------|
| **BARE Phase 1** | TruthValidator, CrossValidator feed L0 |
| **ACI** | Context Compiler consumes atoms/clusters |
| **HSL** | Validates critical atoms when needed |
| **Sprints** | Decision Deck governs execution |
| **Registry** | Opportunities flow to Inbox |
| **GCS** | Intelligence store mirrors to cloud |

---

## Implementation Phases

### Phase 1: Infrastructure
- [ ] Create intelligence directory structure
- [ ] Implement Inventory processor
- [ ] Implement Delta Detector
- [ ] CLI: `./bare-live inventory`, `./bare-live delta`

### Phase 2: Clustering
- [ ] Implement Boundary Mapper (use analysis_sets.yaml)
- [ ] Implement Semantic Clusterer (embeddings + k-means)
- [ ] CLI: `./bare-live cluster`

### Phase 3: Atomization
- [ ] Define ATOM schema (JSON Schema)
- [ ] Implement Distiller (Gemini-based)
- [ ] Implement Atomizer
- [ ] CLI: `./bare-live distill CLUSTER-007`

### Phase 4: Synthesis
- [ ] Implement Global Synthesizer
- [ ] Implement Self-Audit
- [ ] CLI: `./bare-live synth`, `./bare-live audit`

### Phase 5: ACI Integration
- [ ] Build Context Compiler
- [ ] Integrate with analyze.py --aci
- [ ] Test compilation quality

### Phase 6: Decision Deck
- [ ] Define Card schema
- [ ] Implement basic card deck (10 cards)
- [ ] Add phase-aware gating
- [ ] CLI/TUI: `./bare-live deck`

---

## Confidence Assessment

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 75% | Architecture clear, builds on existing BARE |
| Alignment | 98% | Core mission: self-understanding system |
| Current | 40% | Significant new infrastructure required |
| Onwards | 95% | Foundation for autonomous development |

**Overall: min(75, 98, 40, 95) = 40%**

**To Boost:**
1. Prototype Inventory + Delta (simplest, highest value)
2. Test Semantic Clusterer with existing embeddings
3. Define ATOM schema formally
4. Build one end-to-end flow: commit → cluster → atom → query

---

## References

- BARE Phase 1: `.agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md`
- ACI: `context-management/tools/ai/aci/`
- Analysis Sets: `context-management/config/analysis_sets.yaml`
- Grok Design Sessions: 2026-01-23 (Outside-In Refinery, Decision Deck Layer)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial design: Outside-In Refinery + Decision Deck |
