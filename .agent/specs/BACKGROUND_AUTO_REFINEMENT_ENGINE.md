# Background Auto-Refinement Engine (BARE)

> A self-improving intelligence layer that continuously refines repository knowledge,
> validates truths, discovers opportunities, and optimizes its own workflows.

**Status:** DESIGN PHASE | **Version:** 0.1.0 | **Date:** 2026-01-23

---

## Vision

The Background Auto-Refinement Engine (BARE) is an always-on daemon that transforms
the repository from a static codebase into a **living, self-documenting, self-improving
knowledge system**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKGROUND AUTO-REFINEMENT ENGINE (BARE)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INPUTS                          PROCESSORS                    OUTPUTS     │
│   ───────                         ──────────                    ───────     │
│                                                                              │
│   ┌──────────┐                   ┌─────────────┐              ┌──────────┐  │
│   │ Codebase │──────────────────►│ Truth       │─────────────►│ TRUTHS   │  │
│   │ (git)    │                   │ Validator   │              │ .yaml    │  │
│   └──────────┘                   └─────────────┘              └──────────┘  │
│                                                                              │
│   ┌──────────┐                   ┌─────────────┐              ┌──────────┐  │
│   │ Docs     │──────────────────►│ Cross       │─────────────►│ DRIFT    │  │
│   │ (*.md)   │                   │ Validator   │              │ REPORT   │  │
│   └──────────┘                   └─────────────┘              └──────────┘  │
│                                                                              │
│   ┌──────────┐                   ┌─────────────┐              ┌──────────┐  │
│   │ Research │──────────────────►│ Concept     │─────────────►│ CONCEPT  │  │
│   │ outputs  │                   │ Mapper      │              │ GRAPH    │  │
│   └──────────┘                   └─────────────┘              └──────────┘  │
│                                                                              │
│   ┌──────────┐                   ┌─────────────┐              ┌──────────┐  │
│   │ Task     │──────────────────►│ Confidence  │─────────────►│ BOOSTED  │  │
│   │ Registry │                   │ Booster     │              │ TASKS    │  │
│   └──────────┘                   └─────────────┘              └──────────┘  │
│                                                                              │
│   ┌──────────┐                   ┌─────────────┐              ┌──────────┐  │
│   │ Commits  │──────────────────►│ Opportunity │─────────────►│ DISCOVERY│  │
│   │ Convos   │                   │ Explorer    │              │ INBOX    │  │
│   └──────────┘                   └─────────────┘              └──────────┘  │
│                                                                              │
│   ┌──────────┐                   ┌─────────────┐              ┌──────────┐  │
│   │ Own      │──────────────────►│ Self        │─────────────►│ WORKFLOW │  │
│   │ Metrics  │                   │ Optimizer   │              │ PATCHES  │  │
│   └──────────┘                   └─────────────┘              └──────────┘  │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│                          INTELLIGENCE STORE                                  │
│                    .agent/intelligence/                                      │
│                    gs://elements-archive-2026/intelligence/                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Processors

### 1. Truth Validator

**Purpose:** Generate and maintain validated facts about the repository.

**Outputs:**
```yaml
# .agent/intelligence/truths/repo_truths.yaml
version: "2026-01-23T05:00:00Z"
validated_by: "BARE/TruthValidator"
confidence: 0.95

counts:
  files:
    python: 127
    javascript: 48
    yaml: 34
    markdown: 89
  lines_of_code: 45678
  functions: 1234
  classes: 456

atoms:
  total: 3616
  tier0_core: 42
  tier1_stdlib: 21
  tier2_ecosystem: 3531
  coverage: 0.85

roles:
  canonical: 33
  implemented: 29
  gap: 4

pipeline:
  stages: 18
  avg_duration_ms: 4500
```

**Triggers:**
- Post-commit hook
- Daily at 06:00
- Manual via `./bare truth-validate`

---

### 2. Code-Docs Cross-Validator

**Purpose:** Detect drift between documentation claims and code reality.

**Outputs:**
```yaml
# .agent/intelligence/drift/drift_report.yaml
version: "2026-01-23T05:00:00Z"
validated_by: "BARE/CrossValidator"

violations:
  - type: "count_mismatch"
    doc: "docs/MODEL.md:45"
    claim: "167 atoms"
    reality: "3616 atoms"
    severity: "high"

  - type: "missing_implementation"
    doc: "docs/specs/TREE_SITTER_SPEC.md:123"
    claim: "Ruby support"
    reality: "not found in tree_sitter_engine.py"
    severity: "medium"

  - type: "outdated_example"
    doc: "docs/COLLIDER.md:89"
    claim: "./collider analyze"
    reality: "command is now ./collider full"
    severity: "low"

summary:
  total_violations: 3
  high: 1
  medium: 1
  low: 1
```

**Triggers:**
- On docs/*.md changes
- On src/**/*.py changes
- Daily at 06:00

---

### 3. Concept Mapper

**Purpose:** Build a semantic graph of concepts across code and docs.

**Outputs:**
```yaml
# .agent/intelligence/concepts/concept_graph.yaml
version: "2026-01-23T05:00:00Z"
validated_by: "BARE/ConceptMapper"

concepts:
  "Atom":
    definitions:
      - file: "docs/MODEL.md:34"
        text: "The basic structural unit..."
      - file: "src/core/atom_loader.py:12"
        text: "class Atom represents..."
    usages: 456
    related: ["Role", "Dimension", "Pattern"]

  "Role":
    definitions:
      - file: "docs/MODEL.md:89"
        text: "A role describes the function..."
      - file: "schema/fixed/roles.json:1"
        text: "canonical role definitions"
    usages: 234
    related: ["Atom", "Classifier"]

edges:
  - from: "Atom"
    to: "Role"
    type: "has_property"
    strength: 0.95
```

**Triggers:**
- Weekly full rebuild
- Incremental on file changes

---

### 4. Confidence Booster (TASK-120)

**Purpose:** Automatically boost task confidence through Socratic queries.

**Process:**
```
1. Scan registry for tasks < threshold
2. Identify lowest-scoring dimension per task
3. Generate targeted query (Gemini for internal, Perplexity for external)
4. Parse response, extract evidence
5. Update 4D scores with citations
6. If min(4D) >= threshold → mark READY
```

**Outputs:**
- Updated task files with boosted confidence
- Research outputs in `docs/research/`
- Boost audit log

---

### 5. Opportunity Explorer (TASK-121)

**Purpose:** Discover new task opportunities from signals.

**Process:**
```
1. Monitor: commits, research/, audits, conversations
2. Extract signals: TODOs, FIXMEs, unanswered questions, drift
3. Generate DRAFT-XXX.yaml with initial 4D scores
4. Place in Discovery Inbox
5. Terminal agent reviews and promotes/rejects
```

**Outputs:**
- DRAFT files in `.agent/registry/inbox/`
- Signal audit log

---

### 6. Self-Optimizer

**Purpose:** Analyze BARE's own performance and suggest improvements.

**Metrics Tracked:**
```yaml
# .agent/intelligence/metrics/bare_metrics.yaml
version: "2026-01-23T05:00:00Z"

performance:
  truth_validator:
    avg_runtime_ms: 2340
    last_run: "2026-01-23T06:00:00Z"
    success_rate: 0.98

  confidence_booster:
    tasks_boosted_this_week: 12
    avg_boost_per_task: 0.15
    queries_per_boost: 2.3
    cost_per_boost_usd: 0.04

  opportunity_explorer:
    drafts_created_this_week: 8
    acceptance_rate: 0.625
    false_positive_rate: 0.25

suggestions:
  - type: "efficiency"
    target: "confidence_booster"
    suggestion: "Batch similar tasks to reduce API calls"
    estimated_savings: "30% cost reduction"

  - type: "accuracy"
    target: "opportunity_explorer"
    suggestion: "Filter out test-file TODOs (high FP rate)"
    estimated_improvement: "15% better acceptance rate"
```

**Outputs:**
- Workflow patches (proposed config changes)
- Efficiency reports

---

## Directory Structure

```
.agent/
├── intelligence/
│   ├── truths/
│   │   ├── repo_truths.yaml          # Validated counts/stats
│   │   └── history/                   # Historical snapshots
│   ├── drift/
│   │   ├── drift_report.yaml          # Code-docs violations
│   │   └── history/
│   ├── concepts/
│   │   ├── concept_graph.yaml         # Semantic concept map
│   │   └── concept_index.json         # Fast lookup
│   ├── metrics/
│   │   ├── bare_metrics.yaml          # Self-performance
│   │   └── optimization_log.yaml      # Suggested improvements
│   └── roadmap/
│       ├── auto_roadmap.yaml          # Generated from tasks + research
│       └── priority_matrix.yaml       # Task prioritization
│
├── registry/
│   ├── active/                        # Current tasks
│   ├── inbox/                         # Discovery Inbox (DRAFT-XXX)
│   ├── claimed/                       # Task locks
│   └── archive/                       # Completed/rejected
│
├── specs/
│   └── BACKGROUND_AUTO_REFINEMENT_ENGINE.md  # This file
│
└── tools/
    ├── bare_daemon.py                 # Main orchestrator
    ├── truth_validator.py
    ├── cross_validator.py
    ├── concept_mapper.py
    ├── confidence_booster.py
    ├── opportunity_explorer.py
    └── self_optimizer.py
```

---

## Daemon Architecture

```python
# .agent/tools/bare_daemon.py (conceptual)

class BAREDaemon:
    """Background Auto-Refinement Engine"""

    def __init__(self):
        self.processors = [
            TruthValidator(),
            CrossValidator(),
            ConceptMapper(),
            ConfidenceBooster(),
            OpportunityExplorer(),
            SelfOptimizer(),
        ]
        self.schedule = Schedule()
        self.intelligence_store = IntelligenceStore()

    def run(self):
        while True:
            for processor in self.processors:
                if self.schedule.should_run(processor):
                    try:
                        result = processor.run()
                        self.intelligence_store.save(result)
                        self.log_success(processor, result)
                    except Exception as e:
                        self.log_failure(processor, e)

            self.sleep_until_next_trigger()
```

---

## Triggers

| Processor | Schedule | File Watch | Manual |
|-----------|----------|------------|--------|
| TruthValidator | Daily 06:00 | Post-commit | `./bare truth` |
| CrossValidator | Daily 06:00 | `*.md`, `*.py` | `./bare drift` |
| ConceptMapper | Weekly | - | `./bare concepts` |
| ConfidenceBooster | Every 4h | Registry changes | `./bare boost` |
| OpportunityExplorer | Every 2h | Post-commit | `./bare discover` |
| SelfOptimizer | Weekly | - | `./bare optimize` |

---

## Integration Points

| System | Integration |
|--------|-------------|
| **Collider** | TruthValidator uses Collider output for counts |
| **HSL** | CrossValidator extends HSL audits |
| **analyze.py** | ConfidenceBooster uses Gemini queries |
| **Perplexity MCP** | ConfidenceBooster uses for external validation |
| **Git hooks** | Post-commit triggers TruthValidator, OpportunityExplorer |
| **GCS** | Intelligence store mirrors to cloud |

**See also:** `.agent/SUBSYSTEM_INTEGRATION.md` for full integration map.

---

## Confidence Assessment

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Factual | 70% | Architecture clear, components exist in parts |
| Alignment | 98% | Core mission: self-improving system |
| Current | 50% | Significant new infrastructure required |
| Onwards | 95% | Foundation for fully autonomous development |

**Overall: min(70, 98, 50, 95) = 50%**

**To Boost:**
1. Prototype TruthValidator (simplest processor)
2. Validate CrossValidator against existing HSL
3. Design intelligence store schema
4. Define trigger coordination (prevent conflicts)

---

## Implementation Phases

### Phase 1: Foundation (MVP)
- [ ] Create `.agent/intelligence/` directory structure
- [ ] Implement TruthValidator (counts, stats)
- [ ] Add post-commit hook for TruthValidator
- [ ] Manual CLI: `./bare truth`

### Phase 2: Validation
- [ ] Implement CrossValidator
- [ ] Integrate with existing HSL
- [ ] Add drift reporting

### Phase 3: Intelligence
- [ ] Implement ConceptMapper
- [ ] Build concept graph
- [ ] Add semantic search

### Phase 4: Automation
- [ ] Implement ConfidenceBooster (TASK-120)
- [ ] Implement OpportunityExplorer (TASK-121)
- [ ] Full daemon mode

### Phase 5: Self-Improvement
- [ ] Implement SelfOptimizer
- [ ] Workflow patching
- [ ] Autonomous optimization proposals

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial design document |
