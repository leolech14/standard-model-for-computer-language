# BARE Implementation Roadmap

> Realistic path from current state to automated semantic refinement.

**Status:** ACTIVE | **Version:** 1.0.0 | **Date:** 2026-01-26

---

## Current State Audit

### Already Implemented (What Works)

| Component | Tool | Status | Notes |
|-----------|------|--------|-------|
| **L0 Inventory** | `tdj.py` | Working | Scans 5200 files in 11ms |
| **Trigger Engine** | `trigger_engine.py` | Working | Post-commit macro triggers |
| **Enrichment Pipeline** | `enrichment_orchestrator.py` | Working | Orchestrates triage→boost→promote |
| **Inbox Triage** | `triage_inbox.py` | Working | Scores opportunities |
| **Confidence Boost** | `confidence_validator.py` | Working | AI-powered validation |
| **Batch Promote** | `batch_promote.py` | Working | Auto-promotes high-confidence OPPs |
| **Autopilot** | `autopilot.py` | Working | Circuit breakers, 24h enrichment trigger |

### Not Implemented (The Gaps)

| Component | From Spec | Gap Analysis |
|-----------|-----------|--------------|
| **Delta Detector** | L0 | TDJ tracks files but not semantic changes |
| **Boundary Mapper** | L1 | analysis_sets.yaml exists but not processed |
| **Semantic Clusterer** | L1 | No clustering logic |
| **Distiller** | L2 | No LLM-based summarization of clusters |
| **Atomizer** | L2 | No ATOM-*.yaml generation |
| **Global Synthesizer** | L3 | No live.yaml generation |
| **Self-Audit** | L3 | No automated quality checks |
| **Context Compiler** | ACI | Exists partially in analyze.py |

---

## Realistic Roadmap

### Milestone 0: Foundation (DONE)
*What we have working today*

```
Post-Commit Hook → Trigger Engine → (macro execution)
                                  ↘
                                   → Enrichment (24h stale trigger)
                                     → Triage → Boost → Promote → Deck
```

**Deliverables:**
- Post-commit automation
- Inbox processing pipeline
- Circuit breaker resilience

### Milestone 1: Delta Awareness (2-3 days)
*Know what changed, not just what exists*

**Objective:** Extend TDJ to track semantic deltas

**Tasks:**
1. Add `--delta` flag to TDJ that compares current scan to previous
2. Store delta in `intelligence/deltas/DELTA-{sha}.yaml`
3. Add delta summary to autopilot logs

**Output Format:**
```yaml
# intelligence/deltas/DELTA-abc123.yaml
sha: abc123
compared_to: def456
timestamp: 2026-01-26T10:00:00Z

summary:
  new: 3
  modified: 7
  deleted: 1

files:
  new:
    - path: src/new_module.py
      lines: 45
  modified:
    - path: src/core/analyzer.py
      lines_changed: 12
      sections: ["function:analyze", "class:Analyzer"]
  deleted:
    - path: old/deprecated.py
```

**Why This First:** Enables all downstream processors to work on changes only.

### Milestone 2: Boundary Integration (1-2 days)
*Use existing analysis_sets.yaml*

**Objective:** Map files to boundaries using existing config

**Tasks:**
1. Create `boundary_mapper.py` that reads `analysis_sets.yaml`
2. For each file in TDJ, assign boundary (body/brain/agent/unclassified)
3. Store in `intelligence/boundaries/boundary_map.yaml`

**Output Format:**
```yaml
# intelligence/boundaries/boundary_map.yaml
version: 2026-01-26T10:00:00Z

regions:
  body:
    pattern: "standard-model-of-code/src/**"
    file_count: 127
    coverage: 1.0
  brain:
    pattern: "context-management/**"
    file_count: 89
    coverage: 1.0
  agent:
    pattern: ".agent/**"
    file_count: 45
    coverage: 1.0
  unclassified:
    file_count: 12
    paths:
      - scripts/misc.py
      - temp/experiment.py
```

**Why This Second:** Simple mapping using existing config. No AI needed.

### Milestone 3: Lightweight Clustering (3-5 days)
*Group files by co-change patterns*

**Objective:** Create clusters based on git history, not embeddings

**Tasks:**
1. Create `cluster_detector.py` using git log analysis
2. Files that change together = cluster candidates
3. Store in `intelligence/clusters/CLUSTER-*.yaml`

**Algorithm:**
```python
def find_clusters():
    # Get last 100 commits
    for commit in git_log(limit=100):
        files = commit.changed_files
        if len(files) > 1 and len(files) < 10:
            # These files are related
            add_cochange_link(files)

    # Group by cochange frequency
    clusters = connected_components(cochange_graph)
    return clusters
```

**Why Co-Change:** Simpler than embeddings, reveals actual coupling.

### Milestone 4: Distillation (5-7 days)
*AI summarization of clusters*

**Objective:** Generate ATOM-*.yaml from clusters

**Tasks:**
1. Create `distiller.py` that takes a cluster
2. Use Gemini to summarize cluster purpose
3. Extract key concepts, interfaces, invariants
4. Store as `intelligence/atoms/ATOM-*.yaml`

**Output Format:**
```yaml
# intelligence/atoms/ATOM-0001.yaml
id: ATOM-0001
kind: module_group
title: "Atom Classification Pipeline"
created: 2026-01-26T10:00:00Z

summary:
  one_liner: "Classifies code into semantic atoms using pattern matching"

provenance:
  cluster_id: CLUSTER-007
  files:
    - src/core/atom_classifier.py
    - src/core/atom_loader.py

confidence:
  factual: 85
  current: 80
```

**Why After Clustering:** Distillation needs bounded scope.

### Milestone 5: Synthesis (3-4 days)
*Global view generation*

**Objective:** Create live.yaml from all atoms and clusters

**Tasks:**
1. Create `synthesizer.py` that aggregates all atoms
2. Detect gaps, conflicts, hotspots
3. Generate `intelligence/state/live.yaml`

**Why Last:** Depends on all previous layers.

---

## Implementation Order Rationale

```
M0 (DONE) → M1 (Delta) → M2 (Boundaries) → M3 (Clusters) → M4 (Distill) → M5 (Synth)
    ↓           ↓             ↓                ↓              ↓             ↓
 Working    Know what      Map to         Group by        AI            Global
 pipeline   changed        regions        coupling        summary       view
```

Each milestone:
1. Has clear deliverables
2. Can be tested independently
3. Builds on previous work
4. Provides value even if later milestones not done

---

## Deferred from Original Spec

These are NOT in the roadmap (too ambitious for now):

| Feature | Reason for Deferral |
|---------|---------------------|
| 5-minute cron | Post-commit trigger sufficient |
| Semantic embeddings | Co-change simpler, embeddings later |
| Full Decision Deck | ./pe deck exists, extend incrementally |
| Context Compiler | analyze.py --aci handles this |
| Continuous Self-Audit | Manual audits first |

---

## Success Metrics

| Milestone | Success Criteria |
|-----------|------------------|
| M1 | Delta files stored on each commit |
| M2 | 95% files classified to boundary |
| M3 | 10+ meaningful clusters identified |
| M4 | 50+ atoms generated |
| M5 | live.yaml exists and updates |

---

## Resource Estimates

| Milestone | Effort | Dependencies |
|-----------|--------|--------------|
| M1 | 2-3 days | git, TDJ |
| M2 | 1-2 days | analysis_sets.yaml |
| M3 | 3-5 days | git history |
| M4 | 5-7 days | Gemini API |
| M5 | 3-4 days | M1-M4 complete |

**Total: 14-21 days** (vs. months for full BARE-Live spec)

---

## Integration with Autopilot

Each milestone integrates with existing autopilot:

```python
# autopilot.py additions per milestone

# M1: Run delta detection
if should_run_delta():
    run_tool("delta_detector.py")

# M2: Run boundary mapping (weekly)
if should_run_boundaries():
    run_tool("boundary_mapper.py")

# M3: Run clustering (weekly)
if should_run_clustering():
    run_tool("cluster_detector.py")

# M4: Run distillation (on high-drift clusters)
if has_high_drift_clusters():
    run_tool("distiller.py", args=["--stale"])

# M5: Run synthesis (daily)
if should_run_synthesis():
    run_tool("synthesizer.py")
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-26 | Initial realistic roadmap based on current state audit |
