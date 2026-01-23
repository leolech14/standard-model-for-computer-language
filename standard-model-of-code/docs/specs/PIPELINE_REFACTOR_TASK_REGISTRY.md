# PIPELINE REFACTOR TASK REGISTRY

> **DEPRECATED:** This registry has been migrated to `.agent/registry/inbox/OPP-006.yaml`
> The task definitions below remain valid but should be promoted via the new system.
> Last updated: 2026-01-23

---

> Master registry tracking pipeline class-based refactoring implementation.
>
> **Created:** 2026-01-22
> **Last Updated:** 2026-01-22 (Confidence Audit Complete)
> **Status:** VALIDATED - HIGH CONFIDENCE
> **Decision Source:** Holographic Socratic Layer + Architect Analysis + Codebase Audit

---

## EXECUTIVE SUMMARY

### The Problem

The Holographic Socratic Layer detected **systemic non-compliance** in the pipeline:

| Invariant | Expected | Actual | Status |
|-----------|----------|--------|--------|
| BaseStage inheritance | Class hierarchy | Standalone functions | FAIL |
| `execute`/`run` method | Standardized interface | Function names vary | FAIL |
| Statelessness | No side effects | Mutates input args | PARTIAL |
| Standard result format | `ProcessingResult` | `dict` | FAIL |

### The Decision

**Option B: Refactor to Classes** (Architect verdict)

Rationale grounded in Standard Model theory:
- Functions are L2/L3 holons; Stages should be L4 CONTAINERs
- Class-based stages have higher Q-Score (coherence, simplicity)
- Enables composite pattern over brittle linear chain
- Aligns implementation with theoretical framework

### Confidence Audit Results (2026-01-22)

**CRITICAL FINDING: Key infrastructure ALREADY EXISTS**

| Component | Status | Location | Confidence |
|-----------|--------|----------|------------|
| `CodebaseState` | **EXISTS** | `data_management.py:106` | 100% |
| `StageTimer` | **EXISTS** | `observability.py:191` | 100% |
| `PipelineStageResult` | **EXISTS** | `observability.py:22` | 100% |
| `PerformanceManager` | **EXISTS** | `observability.py:45` | 100% |
| `EdgeExtractionStrategy(ABC)` | **EXISTS** | `edge_extractor.py:415` | 100% |

**Actual Stage Count:** 25 (not 18 as initially estimated)

### Success Criteria

- [ ] All 25 pipeline stages wrapped in Stage classes
- [ ] `PipelineManager` orchestrates execution
- [x] `CodebaseState` defined (ALREADY EXISTS at `data_management.py:106`)
- [ ] State flows between stages (no mutation in P4)
- [ ] Holographic Socratic audit shows COMPLIANT
- [ ] All 216 tests passing
- [ ] No performance regression (< 20s for self-analysis)

---

## CURRENT PIPELINE INVENTORY

### Stages in `full_analysis.py` (25 total, validated)

| # | Stage Name | Timer Label | Line | Side Effects |
|---|------------|-------------|------|--------------|
| 1 | Base Analysis | `Stage 1: Base Analysis` | 996 | I/O (file reads) |
| 2 | Standard Model Enrichment | `Stage 2: Standard Model Enrichment` | 1015 | Mutates nodes |
| 2.5 | Ecosystem Discovery | `Stage 2.5: Ecosystem Discovery` | 1046 | None |
| 2.7 | Dimension Classification | `Stage 2.7: Dimension Classification` | 1059 | Mutates nodes |
| 2.8 | Scope Analysis | `Stage 2.8: Scope Analysis` | 1071 | Mutates nodes |
| 2.9 | Control Flow Metrics | `Stage 2.9: Control Flow Metrics` | 1136 | Mutates nodes |
| 2.10 | Pattern Detection | `Stage 2.10: Pattern Detection` | 1213 | Mutates nodes |
| 2.11 | Data Flow Analysis | `Stage 2.11: Data Flow Analysis` | 1287 | Mutates nodes |
| 3 | Purpose Field | `Stage 3: Purpose Field` | 1364 | None |
| 3.5 | Organelle Purpose (π₃) | (no timer) | 1370 | Mutates nodes |
| 3.6 | System Purpose (π₄) | (no timer) | 1396 | Mutates nodes |
| 4 | Execution Flow | `Stage 4: Execution Flow` | 1425 | None |
| 5 | Markov Transition Matrix | `Stage 5: Markov Transition Matrix` | 1437 | Mutates edges |
| 6 | Knot/Cycle Detection | `Stage 6: Knot/Cycle Detection` | 1446 | None |
| 6.5 | Graph Analytics | `Stage 6.5: Graph Analytics` | 1455 | Mutates nodes |
| 6.6 | Statistical Metrics | `Stage 6.6: Statistical Metrics` | 1650 | Mutates nodes |
| 6.8 | Codome Boundaries | `Stage 6.8: Codome Boundaries` | 1670 | Mutates edges |
| 7 | Data Flow Analysis | `Stage 7: Data Flow Analysis` | 1697 | None |
| 8 | Performance Prediction | `Stage 8: Performance Prediction` | 1705 | None |
| 8.5 | Constraint Validation | `Stage 8.5: Constraint Validation` | 1717 | None |
| 8.6 | Purpose Intelligence | `Stage 8.6: Purpose Intelligence` | 1746 | Mutates nodes |
| 9 | Roadmap Evaluation | `Stage 9: Roadmap Evaluation` | 1937 | None |
| 10 | Visual Reasoning | `Stage 10: Visual Reasoning` | 1964 | None |
| 11 | Semantic Cortex | `Stage 11: Semantic Cortex` | 1979 | None |
| 11b | AI Insights (optional) | `Stage 11b: AI Insights` | 2009 | I/O (API call) |
| 12 | Output Generation | `Stage 12: Output Generation` | 2028 | I/O (file write) |

**File Index Building** also has StageTimer at line 1908.

### External Analyzers (Already Class-Based)

These are already compliant or near-compliant:

| Class | File | Status |
|-------|------|--------|
| `TreeSitterUniversalEngine` | `tree_sitter_engine.py` | Compliant |
| `EdgeExtractor` | `edge_extractor.py` | Compliant |
| `ScopeAnalyzer` | `scope_analyzer.py` | Compliant |
| `ControlFlowAnalyzer` | `control_flow_analyzer.py` | Compliant |
| `DataFlowAnalyzer` | `data_flow_analyzer.py` | Compliant |
| `AtomClassifier` | `atom_classifier.py` | Compliant |
| `TopologyReasoning` | `topology_reasoning.py` | Compliant |
| `BrainDownload` | `brain_download.py` | Compliant |

---

## PHASE 1: FOUNDATION

### P1-01: Define BaseStage Abstract Class

**Confidence:** 97% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `src/core/pipeline/base_stage.py` |
| **Lines** | ~50 |
| **Dependencies** | None |
| **Atom ID** | `ORG.SYS.A` (Organization, System, Abstract) |
| **Pattern** | Follow `EdgeExtractionStrategy(ABC)` at `edge_extractor.py:415` |

**Interface:**

```python
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..data_management import CodebaseState

class BaseStage(ABC):
    """Abstract base class for all pipeline stages.

    Pattern: Follows EdgeExtractionStrategy(ABC) from edge_extractor.py
    """

    name: str  # Human-readable stage name (matches StageTimer label)

    @abstractmethod
    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Execute this stage's processing.

        Args:
            state: Input state (mutable for now, immutable in P4)

        Returns:
            Same state object with enrichments added
        """
        pass

    def validate_input(self, state: "CodebaseState") -> bool:
        """Optional: Validate state has required fields."""
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
```

**Invariants:**
1. Must have a `name` attribute (matches StageTimer label)
2. Must implement `execute()`
3. Phase 2: Can mutate state (wrap existing functions)
4. Phase 4: Must not mutate (return new state)

---

### P1-02: Extend Existing CodebaseState

**Confidence:** 100% (Already Exists)

| Attribute | Value |
|-----------|-------|
| **File** | `src/core/data_management.py:106` |
| **Status** | **ALREADY EXISTS** |
| **Lines** | ~200 |
| **Dependencies** | None |

**Existing Implementation:**

```python
class CodebaseState:
    """
    Singleton-like container for the entire state of a codebase analysis.

    Acts as the central bus for all 'Islands of Analysis' (Purpose, Flow, Perf, etc.)
    to write their results back into a shared, validated graph.
    """

    def __init__(self, target_path: str):
        self.target_path = target_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {...}

        # === INDEXED LOOKUPS (O(1) access) ===
        self._node_lookup: Dict[str, Dict[str, Any]] = {}
        self._by_file: Dict[str, Set[str]] = defaultdict(set)
        self._by_ring: Dict[str, Set[str]] = defaultdict(set)
        ...

    def load_initial_graph(self, nodes, edges): ...
    # ... more methods
```

**Task:** Add `with_updates()` method for functional update pattern (optional, P4).

---

### P1-03: Define PipelineManager

**Confidence:** 97% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `src/core/pipeline/manager.py` |
| **Lines** | ~150 |
| **Dependencies** | P1-01, P1-02 |

**Structure:**

```python
from typing import List, Optional
from .base_stage import BaseStage
from .state import CodebaseState
from ..observability import StageTimer

class PipelineManager:
    """Orchestrates pipeline stage execution."""

    def __init__(self, stages: List[BaseStage]):
        self.stages = stages
        self._timer = StageTimer()

    def run(self, initial_state: CodebaseState) -> CodebaseState:
        """Execute all stages in sequence."""
        state = initial_state

        for stage in self.stages:
            with self._timer.measure(stage.name):
                if not stage.validate_input(state):
                    raise ValueError(f"Invalid input for {stage.name}")
                state = stage.execute(state)

        # Add timing data to final state
        return state.with_updates(
            stage_timings=self._timer.get_timings()
        )

    def run_until(self, initial_state: CodebaseState,
                  stop_after: str) -> CodebaseState:
        """Execute stages until (and including) named stage."""
        state = initial_state
        for stage in self.stages:
            state = stage.execute(state)
            if stage.name == stop_after:
                break
        return state
```

---

### P1-04: Create Pipeline Package Structure

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **Files** | `src/core/pipeline/__init__.py` |
| **Lines** | ~20 |
| **Dependencies** | P1-01, P1-02, P1-03 |

**Directory Structure:**

```
src/core/pipeline/
├── __init__.py          # Public exports
├── base_stage.py        # BaseStage ABC
├── state.py             # CodebaseState dataclass
├── manager.py           # PipelineManager
└── stages/              # Stage implementations (Phase 2)
    ├── __init__.py
    ├── discovery.py     # FileDiscoveryStage
    ├── extraction.py    # ASTExtractionStage, EdgeExtractionStage
    ├── analysis.py      # ScopeStage, ControlFlowStage, DataFlowStage
    ├── classification.py # AtomClassificationStage, RoleAssignmentStage
    ├── metrics.py       # GraphMetricsStage, MarkovStage, RPBLStage
    ├── advanced.py      # KnotDetectionStage, PurposeFieldStage
    └── output.py        # OutputGenerationStage, ReportStage
```

---

## PHASE 2: STAGE WRAPPERS (Facade Pattern)

### P2-01 to P2-25: Wrap Each Stage

**Confidence:** 96% (Execute)

**Evidence:**
- `observe_stage` decorator exists at `observability.py:247` - ready to wrap functions
- `StageTimer` context manager at `observability.py:191` - already used by all 25 stages
- 8 external analyzers already class-based (see External Analyzers table above)
- Pattern follows existing `EdgeExtractionStrategy(ABC)` at `edge_extractor.py:415`

For each of the 25 stages, create a wrapper class that:
1. Inherits from `BaseStage`
2. Implements `execute(state) -> state`
3. Calls existing function internally
4. Returns new state (no mutation)

**Example: MarkovMatrixStage**

```python
# src/core/pipeline/stages/metrics.py

from ..base_stage import BaseStage
from ..state import CodebaseState

class MarkovMatrixStage(BaseStage):
    """Compute Markov transition matrix for code flow."""

    name = "markov_matrix"

    def execute(self, state: CodebaseState) -> CodebaseState:
        # Call existing function (imported from full_analysis)
        from ..full_analysis import compute_markov_matrix

        # Create copies to avoid mutation
        nodes = [n.copy() for n in state.nodes]
        edges = [e.copy() for e in state.edges]

        result = compute_markov_matrix(nodes, edges)

        return state.with_updates(
            edges=edges,  # Now includes markov_weight
            markov_matrix=result
        )
```

**Stage Implementation Priority:**

| Priority | Stages | Rationale |
|----------|--------|-----------|
| **P1 (First)** | 1, 2, 3, 4, 9, 17, 18 | Core pipeline, I/O boundaries |
| **P2 (Second)** | 5, 6, 7, 8, 10, 11, 15 | Analysis stages |
| **P3 (Third)** | 12, 13, 14, 16 | Advanced/optional stages |

---

## PHASE 3: INTEGRATION

### P3-01: Refactor run_full_analysis()

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `src/core/full_analysis.py:950` |
| **Current Size** | 2087 lines |
| **Dependencies** | All P2 tasks |

**Evidence:**
- Entry point at line 950: `def run_full_analysis(target_path: str, output_dir: str = None, options: Dict[str, Any] = None)`
- Already uses `PerformanceManager` at line 972 and `StageTimer` throughout
- `CodebaseState` already exists at `data_management.py:106` - just need to wire it in
- Backward compatibility maintained via `state.to_dict()` (like `PipelineStageResult.to_dict()`)

**Before (current):**
```python
def run_full_analysis(target_path, output_dir, options):
    perf_manager = PerformanceManager(verbose=verbose_timing)
    perf_manager.start_pipeline()
    # ... 25 inline stages with StageTimer ...
    return {"nodes": nodes, "edges": edges, ...}
```

**After (refactored):**
```python
def run_full_analysis(target_path, output_dir, options):
    from .pipeline import PipelineManager, CodebaseState
    from .pipeline.stages import ALL_STAGES

    initial_state = CodebaseState(
        target_path=target_path,
        output_dir=output_dir,
        options=options or {}
    )

    manager = PipelineManager(stages=ALL_STAGES)
    final_state = manager.run(initial_state)

    return final_state.to_dict()  # Backward compatibility
```

---

### P3-02: Update semantic_models.yaml

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `context-management/config/semantic_models.yaml` |
| **Dependencies** | P3-01 |

**Update to reflect new architecture:**

```yaml
pipeline:
  scope: "standard-model-of-code/src/core/**"
  definitions:
    Stage:
      description: "A processing unit in the analysis pipeline."
      role: "Processing"
      invariants:
        - "Must inherit from BaseStage"
        - "Must implement execute(state) -> state method"
        - "Must not modify input state (return new state)"
        - "Must have a 'name' attribute"
      anchors:
        - file: "standard-model-of-code/src/core/pipeline/base_stage.py"
          pattern: "class BaseStage"
        - file: "standard-model-of-code/src/core/pipeline/stages/*.py"
          pattern: "class *Stage(BaseStage)"
```

---

### P3-03: Update Tests

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `tests/test_pipeline_stages.py` (new) |
| **Dependencies** | P2 tasks |
| **Existing Tests** | 216 tests across 17 test files |

**Evidence:**
- Existing test infrastructure: 216 tests collected
- Related tests already exist: `test_scope_analyzer.py`, `test_control_flow_analyzer.py`, `test_data_flow_analyzer.py`
- Test patterns established in `test_purpose_field.py`, `test_pattern_matcher.py`
- Observability testing: `PipelineStageResult.to_dict()` provides comparison interface

**Test Categories:**
1. Unit tests for each Stage class (follow `test_scope_analyzer.py` pattern)
2. Integration test for PipelineManager
3. Regression test comparing old vs new output using `to_dict()`
4. Performance benchmark (use existing `--timing` flag infrastructure)

---

## PHASE 4: CLEANUP

### P4-01: Remove Mutation Side Effects

**Confidence:** 95% (Execute)

**Evidence:**
Audit found 30+ mutation points with exact line numbers:

| Stage | Line | Current Mutation | Fix |
|-------|------|-----------------|-----|
| Markov | 731, 734 | `edge['markov_weight'] = ...` | Copy then modify |
| RPBL | 1022-1025 | `node['rpbl_*'] = ...` | Copy then modify |
| Scope | 1117 | `node['scope_analysis'] = ...` | Copy then modify |
| Control Flow | 1174, 1186-1189 | `node['control_flow'] = ...` | Copy then modify |
| Atoms | 1251, 1264-1265 | `node['detected_atoms'] = ...` | Copy then modify |
| Data Flow | 1328 | `node['data_flow'] = ...` | Copy then modify |
| Graph Metrics | 1489-1519 | `node['in_degree'] = ...` etc. | Copy then modify |

**Pattern:** Use `dict.copy()` before modification, return new collection from stage.

### P4-02: Remove I/O from Processing Stages

**Confidence:** 90% (Almost Ready)

| Issue | Location | Fix |
|-------|----------|-----|
| `print()` statements | lines 975-980, etc. | Replace with `logging.info()` |
| PerformanceManager init | line 972 | Move to PipelineManager constructor |
| File I/O | OutputStage | Already isolated in Stage 12 |

### P4-03: Run Holographic Socratic Audit

**Confidence:** 95% (Execute)

```bash
python context-management/tools/ai/analyze.py --verify pipeline
```

**Expected Result:** COMPLIANT for Stage concept

---

## CONFIDENCE METHODOLOGY

**Confidence = min(Factual, Alignment)**

| Level | Meaning | Action |
|-------|---------|--------|
| **95%+** | Execute immediately | Green light |
| **90-94%** | Almost ready | Minor clarification needed |
| **85-89%** | Needs work | Design review required |
| **80-84%** | Uncertain | Prototype first |
| **<80%** | Do not execute | More research needed |

---

## TASK SUMMARY

| Phase | Tasks | Confidence | Status |
|-------|-------|------------|--------|
| **P1: Foundation** | 4 | 97-100% | **READY** |
| **P2: Wrappers** | 25 | 96% | **READY** |
| **P3: Integration** | 3 | 95% | **READY** |
| **P4: Cleanup** | 3 | 90-95% | **READY** |

**Total Tasks:** 35 (updated from 28 due to 25 stages vs 18)
**Ready to Execute:** 35 (all phases have 95%+ confidence)
**Critical Finding:** P1-02 (CodebaseState) is **ALREADY IMPLEMENTED**

### Confidence Summary by Task

| Task | Confidence | Evidence |
|------|------------|----------|
| P1-01 (BaseStage) | 97% | Follow `EdgeExtractionStrategy(ABC)` pattern |
| P1-02 (CodebaseState) | **100%** | Already exists at `data_management.py:106` |
| P1-03 (PipelineManager) | 97% | `PerformanceManager` pattern exists |
| P1-04 (Package Structure) | 95% | Standard Python package |
| P2-* (Stage Wrappers) | 96% | `observe_stage` decorator + `StageTimer` exist |
| P3-01 (Integration) | 95% | Entry point identified, backward compat via `to_dict()` |
| P3-02 (Semantic Models) | 95% | YAML update only |
| P3-03 (Tests) | 95% | 216 tests exist, patterns established |
| P4-01 (Mutation Removal) | 95% | 30+ mutation points identified with line numbers |
| P4-02 (I/O Removal) | 90% | Locations identified |
| P4-03 (Socratic Audit) | 95% | Command ready: `--verify pipeline` |

---

## RISKS & MITIGATIONS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Performance regression | Medium | High | Benchmark before/after |
| Breaking existing tests | Low | Medium | Run tests after each stage |
| Scope creep | Medium | Medium | Strict phase boundaries |
| Immutability overhead | Low | Low | Profile memory usage |

---

## DOCUMENT HISTORY

| Date | Change |
|------|--------|
| 2026-01-22 | Initial creation from Holographic Socratic audit findings |
| 2026-01-22 | **CONFIDENCE AUDIT COMPLETE** - All phases now 95%+ |
|            | - P1-02: Changed from "Define" to "Extend Existing" (CodebaseState exists) |
|            | - P2: Updated to 25 stages (was 18), added evidence |
|            | - P3-01: Added exact line numbers, increased to 95% |
|            | - P3-03: Added test count (216 tests), increased to 95% |
|            | - P4-01: Added 30+ mutation point line numbers, increased to 95% |
|            | - Total tasks updated from 28 to 35 |
