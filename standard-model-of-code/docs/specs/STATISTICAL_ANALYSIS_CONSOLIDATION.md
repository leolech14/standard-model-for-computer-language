# Statistical Analysis Consolidation

**Status:** CHECKPOINT - Consolidating before refactor
**Date:** 2026-01-25
**Trigger:** Perplexity research recommends centralized `src/core/stats/` subsystem

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Statistical modules found | 7 |
| Scattered locations | 3 directories |
| Unified subsystem | NO (gap) |
| Batch evidence | 590 repos graded |
| Key finding | CYCLES explains 90% of grade variance |

**Decision:** Consolidate into `src/core/stats/` per industry best practices (SCALe, Cycode patterns).

---

## 1. Current State Inventory

### Module Map

| Module | Location | Scope | Purpose |
|--------|----------|-------|---------|
| `stats_generator.py` | `src/core/` | Single codebase | Per-file particle statistics, summary generation |
| `scientific_charts.py` | `src/core/` | Single codebase | Matplotlib charts from unified_analysis.json |
| `statistical_metrics.py` | `src/core/pipeline/stages/` | Single codebase | Stage 6.6: Entropy, Halstead, maintainability |
| `analytics_engine.py` | `src/core/` | Single codebase | compute_all_metrics(), Halstead primitives |
| `graph_analyzer.py` | `src/core/` | Single codebase | Centrality, PageRank, community detection |
| `topology_reasoning.py` | `src/core/` | Single codebase | Betti numbers, elevation, LandscapeHealthIndex |
| `analyze_results.py` | `tools/batch_grade/` | **Batch/Aggregate** | Grade distribution, component variance, golden repos |

### Relationships

```
                    SINGLE CODEBASE                          BATCH
                    ───────────────                          ─────

┌─────────────────┐     ┌──────────────────┐
│ stats_generator │     │ analytics_engine │
│   (particles)   │     │   (Halstead)     │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         │    ┌──────────────────┤
         │    │                  │
         ▼    ▼                  ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│statistical_metrics│   │  graph_analyzer  │     │  analyze_results  │
│  (Stage 6.6)    │     │  (centrality)    │     │  (batch stats)    │
└─────────────────┘     └────────┬─────────┘     └───────────────────┘
                                 │                        ▲
                                 ▼                        │
                        ┌──────────────────┐              │
                        │topology_reasoning│──────────────┘
                        │ (Betti, Health)  │   feeds into
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │scientific_charts │
                        │  (visualization) │
                        └──────────────────┘
```

### Gap Analysis

| Concern | Current | Should Be |
|---------|---------|-----------|
| Entry point | None (scattered imports) | `from src.core.stats import ...` |
| Batch analysis | Isolated in tools/ | Part of core stats |
| Shared primitives | Duplicated | metrics.py with variance, mean, etc. |
| Normalization | Per-module | Centralized baselines |

---

## 2. Term Definitions (Glossary)

### Scope Terms

| Term | Definition | Example |
|------|------------|---------|
| **Single-codebase analysis** | Statistics computed for ONE repository | "flask has 7.56 health index" |
| **Batch/Aggregate analysis** | Statistics computed ACROSS multiple repositories | "67.5% of 590 repos scored C" |
| **Per-node metrics** | Statistics for individual code elements | "function foo has cyclomatic complexity 12" |
| **Codebase-level metrics** | Aggregated statistics for entire repo | "repo has 29.3% reachability" |

### Metric Terms

| Term | Definition | Module |
|------|------------|--------|
| **Entropy** | Information density of code structure | `analytics_engine.py` |
| **Halstead metrics** | Volume, difficulty, effort from operator/operand counts | `analytics_engine.py` |
| **Betti numbers** | Topological invariants (b0=components, b1=cycles) | `topology_reasoning.py` |
| **Elevation** | Layered depth in call hierarchy | `topology_reasoning.py` |
| **Gradients** | Rate of change across boundaries | `topology_reasoning.py` |
| **Health Index** | Composite score H = 10 × (wT + wE + wGd + wA) | `topology_reasoning.py` |

### Analysis Terms

| Term | Definition | Scope |
|------|------------|-------|
| **Stats** | Descriptive statistics (mean, median, variance) | Both |
| **Metrics** | Measured properties of code | Single |
| **Analytics** | Derived insights from metrics | Single |
| **Aggregation** | Combining metrics across repos | Batch |

---

## 3. Batch Grade Findings (Evidence)

**Source:** `tools/batch_grade/grades_DEGRADED_summary_only/LEARNINGS.md`
**Sample:** 590 successful grades from 999 attempted repos

### Grade Distribution

| Grade | Count | Percentage |
|-------|-------|------------|
| A | 0 | 0.0% |
| B | 10 | 1.7% |
| C | 398 | 67.5% |
| D | 178 | 30.2% |
| F | 4 | 0.7% |

### Component Discriminating Power

| Component | Grade B | Grade C | Grade D | Grade F | Variance |
|-----------|---------|---------|---------|---------|----------|
| **cycles** | **9.40** | 6.63 | 4.10 | **1.00** | **3.09** |
| isolation | 8.98 | 8.69 | 7.91 | 7.88 | 1.66 |
| gradients | 10.00 | 9.99 | 9.57 | 5.00 | 0.82 |
| elevation | 4.94 | 4.94 | 4.92 | 4.98 | **0.00** |
| coupling | 7.47 | 7.47 | 7.46 | 7.49 | **0.00** |

**KEY FINDING:** CYCLES (Betti b1) explains ~90% of grade variance. Elevation and Coupling are CONSTANT.

### Language Performance

| Language | Count | Avg Health | Interpretation |
|----------|-------|------------|----------------|
| Python | 140 | **7.48** | Healthiest |
| Go | 135 | 7.28 | Above average |
| JavaScript | 183 | 7.08 | Average |
| TypeScript | 132 | **6.65** | Lowest |

**Hypothesis:** TypeScript's complex dependency graphs (monorepos, barrel exports) create more cycles.

### Golden Repos (Grade B)

| Repo | Health | Nodes | Edges | Language |
|------|--------|-------|-------|----------|
| mingrammer/diagrams | 8.29 | 3141 | 3395 | Python |
| resume/resume.github.com | 8.17 | 14 | 16 | JavaScript |
| jashkenas/backbone | 8.17 | 73 | 76 | JavaScript |
| VincentGarreau/particles.js | 8.12 | 8 | 8 | JavaScript |
| vinta/awesome-python | 8.08 | 4 | 2 | Python |

---

## 4. Health Model Status

### Current Formula

```
H = 10 × (0.25×T + 0.25×E + 0.25×Gd + 0.25×A)

Where:
  T  = Topology score (from cycles/b1)
  E  = Elevation score (layer depth)
  Gd = Gradients score (boundary transitions)
  A  = Alignment score (NOT YET IMPLEMENTED)
```

**Location:** `src/core/topology_reasoning.py:LandscapeHealthIndex`

### Evidence-Based Reweighting Proposal

| Component | Current Weight | Proposed Weight | Justification |
|-----------|----------------|-----------------|---------------|
| Topology (T) | 0.25 | **0.40** | Highest variance (3.09), primary differentiator |
| Elevation (E) | 0.25 | **0.10** | Zero variance, constant ~5.0 |
| Gradients (Gd) | 0.25 | **0.30** | Moderate variance (0.82) |
| Alignment (A) | 0.25 | **0.20** | Not yet implemented |

**Proposed Formula:**
```
H = 10 × (0.40×T + 0.10×E + 0.30×Gd + 0.20×A)
```

### Open Questions

1. Why is Elevation constant at ~5.0?
2. Why is Coupling constant at ~7.5?
3. Should we add per-language normalization?
4. How to implement Alignment component?

---

## 5. Architecture Decision

### Perplexity Research (2026-01-25)

**Query:** Should aggregate batch analysis be standalone or centralized?

**Answer:** **Option B - Centralized `src/core/stats/` subsystem**

**Sources:**
- SCALe (CMU) - Aggregates multi-tool outputs into unified framework
- Cycode - Consolidated scanners with correlated findings
- Data aggregation best practices - Centralized repositories avoid silos

### Target Architecture

```
src/core/stats/
├── __init__.py              # Unified entry point
├── primitives.py            # Shared: mean, variance, correlation, normalization
├── information_theory.py    # Entropy, Halstead (from analytics_engine.py)
├── topology.py              # Betti, elevation, gradients (from topology_reasoning.py)
├── health_index.py          # LandscapeHealthIndex, grading
├── single_codebase.py       # Per-repo analysis (from stats_generator.py)
├── batch_aggregate.py       # Cross-repo analysis (from analyze_results.py)
└── charts.py                # Visualization (from scientific_charts.py)
```

### Benefits

1. **Single import:** `from src.core.stats import BatchAnalyzer, HealthIndex`
2. **Shared primitives:** No duplication of variance/mean calculations
3. **Consistent API:** Same patterns for single and batch analysis
4. **Testability:** One location to test all stats logic

---

## 6. Migration Plan (DO NOT EXECUTE YET)

### Phase 1: Create Subsystem Structure

| Action | From | To |
|--------|------|-----|
| Create directory | - | `src/core/stats/` |
| Create __init__.py | - | `src/core/stats/__init__.py` |
| Extract primitives | Various | `src/core/stats/primitives.py` |

### Phase 2: Move Single-Codebase Modules

| Action | From | To |
|--------|------|-----|
| Move stats_generator | `src/core/stats_generator.py` | `src/core/stats/single_codebase.py` |
| Move analytics_engine | `src/core/analytics_engine.py` | `src/core/stats/information_theory.py` |
| Move scientific_charts | `src/core/scientific_charts.py` | `src/core/stats/charts.py` |
| Extract from topology_reasoning | `src/core/topology_reasoning.py` | `src/core/stats/topology.py` |

### Phase 3: Integrate Batch Analysis

| Action | From | To |
|--------|------|-----|
| Move analyze_results | `tools/batch_grade/analyze_results.py` | `src/core/stats/batch_aggregate.py` |
| Update imports | `tools/batch_grade/` | Import from `src.core.stats` |

### Phase 4: Update Consumers

| Consumer | Current Import | New Import |
|----------|----------------|------------|
| `full_analysis.py` | `from core.stats_generator import...` | `from core.stats import...` |
| `cli.py` | Various | `from core.stats import...` |
| `pipeline/stages/statistical_metrics.py` | `from analytics_engine import...` | `from ..stats import...` |

### Risks

| Risk | Mitigation |
|------|------------|
| Import breakage | Run full test suite after each move |
| Circular imports | Careful dependency ordering |
| Lost functionality | Audit each module before moving |

---

## 7. Traceability Index

| Reference | Location |
|-----------|----------|
| This spec | `docs/specs/STATISTICAL_ANALYSIS_CONSOLIDATION.md` |
| Health Model spec | `docs/specs/HEALTH_MODEL_CONSOLIDATED.md` |
| Batch learnings | `tools/batch_grade/grades_DEGRADED_summary_only/LEARNINGS.md` |
| Open concerns | `docs/OPEN_CONCERNS.md` (FAIL-001, HIGH-002) |
| Perplexity research | `docs/research/perplexity/docs/20260125_193155_*.md` |
| Topology reasoning | `src/core/topology_reasoning.py` |
| Analytics engine | `src/core/analytics_engine.py` |
| Stats generator | `src/core/stats_generator.py` |
| Batch analyzer | `tools/batch_grade/analyze_results.py` |

---

## 8. Next Actions (Pending Approval)

| Priority | Action | Blocked By |
|----------|--------|------------|
| P0 | Approve this consolidation document | User review |
| P1 | Execute migration Phase 1 (structure) | P0 |
| P1 | Update Health Model weights based on evidence | P0 |
| P2 | Execute migration Phases 2-4 | P1 |
| P3 | Add per-language normalization | P2 |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-25 | Initial consolidation checkpoint |
