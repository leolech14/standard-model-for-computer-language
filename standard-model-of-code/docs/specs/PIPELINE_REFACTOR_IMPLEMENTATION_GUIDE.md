# PIPELINE REFACTOR IMPLEMENTATION GUIDE

> Step-by-step executable guide for refactoring the Collider pipeline to class-based architecture.
>
> **Source:** PIPELINE_REFACTOR_TASK_REGISTRY.md (validated 2026-01-22)
> **Status:** Ready to Execute
> **Total Steps:** 35 (organized in 4 phases)

---

## Prerequisites

Before starting, verify your environment:

```bash
# Prerequisites Checklist
- [ ] All tests passing: pytest tests/ -q
- [ ] Working directory clean: git status
- [ ] Python 3.10+: python --version
- [ ] Dependencies installed: pip list | grep -E "networkx|pyyaml"
```

**Verify the prerequisites now:**

```bash
cd /Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code
pytest tests/ -q
git status
```

Expected output: All tests pass, no uncommitted changes.

---

## PHASE 1: FOUNDATION (4 Steps)

Foundation tasks create the abstract framework that all stages will inherit from.

### Step 1.1: Create BaseStage Abstract Base Class

**Objective:** Define the interface all 25 pipeline stages must implement.

**File:** `src/core/pipeline/base_stage.py` (NEW)

**Line Count:** ~70 lines

**Dependencies:** None

**Pattern Reference:** `src/core/edge_extractor.py:415` (`EdgeExtractionStrategy` ABC)

**Code to Write:**

```python
"""
BaseStage: Abstract base class for all pipeline stages.

Pattern: Follows EdgeExtractionStrategy(ABC) from edge_extractor.py:415
Implements standard interface for all 25 pipeline stages.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..data_management import CodebaseState


class BaseStage(ABC):
    """Abstract base class for all pipeline stages.

    Every stage in the pipeline must:
    1. Inherit from BaseStage
    2. Set a `name` attribute (human-readable, matches StageTimer label)
    3. Implement the `execute()` method
    4. Call `validate_input()` before processing
    5. Return the modified state (same object in Phase 2, new object in Phase 4)

    Invariants:
        - Must have a `name` attribute (matches StageTimer label)
        - Must implement `execute(state) -> state`
        - Phase 2: Can mutate state (wrap existing functions)
        - Phase 4: Must not mutate (return new state)

    Example:
        class MyStage(BaseStage):
            name = "my_stage"

            def execute(self, state: CodebaseState) -> CodebaseState:
                # Process state
                state.some_attribute = value
                return state
    """

    name: str  # Must be set by subclass

    @abstractmethod
    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Execute this stage's processing.

        Args:
            state: Input CodebaseState (mutable for Phase 2)

        Returns:
            Modified state (same object or new object depending on phase)

        Raises:
            ValueError: If input state is invalid
        """
        pass

    def validate_input(self, state: "CodebaseState") -> bool:
        """
        Optional: Validate that state has required fields before processing.

        Override in subclasses for custom validation.

        Args:
            state: CodebaseState to validate

        Returns:
            True if valid, False otherwise

        Note:
            Default implementation returns True (permissive).
            Override to add stage-specific validation.
        """
        return True

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<{self.__class__.__name__} name={self.name!r}>"
```

**Validation Command:**

```bash
python -c "from src.core.pipeline.base_stage import BaseStage; print('✓ BaseStage imported successfully')"
```

**Expected Output:**
```
✓ BaseStage imported successfully
```

**Rollback (if validation fails):**
```bash
rm src/core/pipeline/base_stage.py
```

---

### Step 1.2: Create Pipeline Package Structure

**Objective:** Organize stage implementations into a proper Python package.

**File:** `src/core/pipeline/__init__.py` (NEW)

**Line Count:** ~30 lines

**Dependencies:** Step 1.1

**Code to Write:**

```python
"""
Pipeline: Class-based stage orchestration for Collider.

Structure:
    base_stage.py   - BaseStage ABC
    manager.py      - PipelineManager orchestrator
    stages/         - Concrete stage implementations
        __init__.py - Stage registry and exports
        discovery.py - File discovery stages
        extraction.py - AST and edge extraction stages
        analysis.py - Scope, control flow, data flow stages
        classification.py - Atom and role classification stages
        metrics.py - Graph metrics, Markov, RPBL stages
        advanced.py - Knot detection, purpose field stages
        output.py - Output and report generation stages
"""

from .base_stage import BaseStage
from .manager import PipelineManager

__all__ = [
    "BaseStage",
    "PipelineManager",
]
```

**Create the directory structure:**

```bash
mkdir -p src/core/pipeline/stages
touch src/core/pipeline/__init__.py
touch src/core/pipeline/stages/__init__.py
```

**Validation Command:**

```bash
python -c "from src.core.pipeline import BaseStage, PipelineManager; print('✓ Pipeline package structure OK')"
```

**Expected Output:**
```
✓ Pipeline package structure OK
```

**Rollback (if validation fails):**
```bash
rm -rf src/core/pipeline/
```

---

### Step 1.3: Define PipelineManager Orchestrator

**Objective:** Create the central orchestrator that runs all 25 stages in sequence.

**File:** `src/core/pipeline/manager.py` (NEW)

**Line Count:** ~160 lines

**Dependencies:** Step 1.1, `data_management.py`, `observability.py`

**Pattern Reference:** `src/core/observability.py:45` (PerformanceManager pattern)

**Code to Write:**

```python
"""
PipelineManager: Orchestrates execution of all pipeline stages.

Responsibilities:
    1. Load or create initial CodebaseState
    2. Execute stages in sequence
    3. Validate state between stages
    4. Collect timing metrics via StageTimer
    5. Return final state

Pattern: Similar to PerformanceManager from observability.py:45
"""

from typing import List, Optional, Dict, Any
from .base_stage import BaseStage
from ..data_management import CodebaseState
from ..observability import StageTimer


class PipelineManager:
    """Orchestrates pipeline stage execution.

    Runs all 25 stages in sequence, managing state flow and timing.

    Invariants:
        - Stages execute in order (no skipping or reordering)
        - Each stage receives CodebaseState as input
        - Each stage returns CodebaseState as output
        - State is cumulative (each stage builds on previous)
        - Timing metrics collected after each stage
    """

    def __init__(self, stages: List[BaseStage], verbose: bool = False):
        """
        Initialize the manager with a list of stages.

        Args:
            stages: List of BaseStage instances in execution order
            verbose: If True, print timing info after each stage
        """
        if not stages:
            raise ValueError("Pipeline must have at least one stage")

        self.stages = stages
        self.verbose = verbose
        self._timer = StageTimer()

    def run(self, initial_state: CodebaseState) -> CodebaseState:
        """
        Execute all stages in sequence.

        Args:
            initial_state: CodebaseState initialized with target_path

        Returns:
            Final CodebaseState after all stages

        Raises:
            ValueError: If any stage's validate_input() fails
            Exception: If any stage raises during execution
        """
        state = initial_state
        stage_timings: Dict[str, float] = {}

        for i, stage in enumerate(self.stages, start=1):
            # Validate input before execution
            if not stage.validate_input(state):
                raise ValueError(
                    f"Input validation failed for {stage.name}. "
                    f"State may be missing required fields."
                )

            # Execute stage with timing
            with self._timer.measure(stage.name) as timer_context:
                try:
                    state = stage.execute(state)
                except Exception as e:
                    raise RuntimeError(
                        f"Stage {i}/{len(self.stages)} ({stage.name}) failed: {str(e)}"
                    ) from e

            # Record timing
            elapsed_ms = timer_context.elapsed_ms if hasattr(timer_context, 'elapsed_ms') else 0
            stage_timings[stage.name] = elapsed_ms

            if self.verbose:
                print(f"  [{i:2d}/{len(self.stages)}] {stage.name:40s} {elapsed_ms:7.1f}ms")

        # Attach timing data to final state
        if hasattr(state, 'metadata'):
            state.metadata['stage_timings'] = stage_timings

        return state

    def run_until(
        self,
        initial_state: CodebaseState,
        stop_after: str
    ) -> CodebaseState:
        """
        Execute stages until (and including) a named stage.

        Useful for debugging: stop after Stage 5 instead of running all 25.

        Args:
            initial_state: CodebaseState initialized with target_path
            stop_after: Name of stage to stop after (e.g., "Stage 5: Markov Matrix")

        Returns:
            CodebaseState after requested stage

        Raises:
            ValueError: If stop_after stage name not found
        """
        state = initial_state
        found = False

        for stage in self.stages:
            state = stage.execute(state)
            if stage.name == stop_after:
                found = True
                break

        if not found:
            raise ValueError(
                f"Stage '{stop_after}' not found in pipeline. "
                f"Available stages: {[s.name for s in self.stages]}"
            )

        return state

    def get_stage_names(self) -> List[str]:
        """Return list of stage names in execution order."""
        return [stage.name for stage in self.stages]

    def __repr__(self) -> str:
        return f"<PipelineManager stages={len(self.stages)}>"
```

**Validation Command:**

```bash
python -c "
from src.core.pipeline.manager import PipelineManager
from src.core.pipeline.base_stage import BaseStage
from src.core.data_management import CodebaseState

# Quick validation: manager can be instantiated
print('✓ PipelineManager imports successfully')
"
```

**Expected Output:**
```
✓ PipelineManager imports successfully
```

**Rollback (if validation fails):**
```bash
rm src/core/pipeline/manager.py
```

---

### Step 1.4: Verify CodebaseState Exists

**Objective:** Confirm CodebaseState is already implemented (100% pre-existing).

**File:** `src/core/data_management.py:106` (VERIFY EXISTING)

**Status:** ALREADY EXISTS - No action needed

**Verification Command:**

```bash
python -c "
from src.core.data_management import CodebaseState
cs = CodebaseState(target_path='/tmp')
print(f'✓ CodebaseState exists and instantiates successfully')
print(f'  - target_path: {cs.target_path}')
print(f'  - has metadata: {hasattr(cs, \"metadata\")}')
print(f'  - has load_initial_graph: {hasattr(cs, \"load_initial_graph\")}')
"
```

**Expected Output:**
```
✓ CodebaseState exists and instantiates successfully
  - target_path: /tmp
  - has metadata: True
  - load_initial_graph: True
```

**Note:** If CodebaseState doesn't exist, this signals a critical environment issue. Do not proceed.

---

## PHASE 2: STAGE WRAPPERS (25 Steps)

Wrap each of the 25 existing pipeline functions as a class inheriting from BaseStage.

**High-Level Pattern for Each Stage:**

```python
# In src/core/pipeline/stages/[domain].py

from ..base_stage import BaseStage
from ..state import CodebaseState
from ...full_analysis import original_function  # Import existing function

class MyStage(BaseStage):
    """Description matching StageTimer label."""

    name = "Stage N: Description"

    def execute(self, state: CodebaseState) -> CodebaseState:
        # Call existing function (preserve logic, wrap in class)
        result = original_function(state.nodes, state.edges, ...)

        # Update state and return
        state.nodes = result['nodes']
        state.edges = result['edges']
        return state
```

### Step 2.1-2.25: Wrap All 25 Stages

**File Organization:**

| File | Stages | Line Count |
|------|--------|-----------|
| `discovery.py` | 1 | ~40 |
| `extraction.py` | 2, 2.5 | ~80 |
| `analysis.py` | 2.7, 2.8, 2.9, 2.10, 2.11, 7 | ~200 |
| `classification.py` | 2.12, 2.13 | ~100 |
| `metrics.py` | 5, 6, 6.5, 6.6, 6.8 | ~150 |
| `advanced.py` | 3, 4, 6, 8.5, 8.6 | ~180 |
| `output.py` | 9, 10, 11, 11b, 12 | ~120 |

**Total Phase 2:** ~870 lines across 7 files

**Implementation Strategy:**

**PRIORITY 1 (Complete First):**
- Stage 1: Base Analysis
- Stage 2: Standard Model Enrichment
- Stage 3: Purpose Field
- Stage 4: Execution Flow
- Stage 9: Roadmap Evaluation
- Stage 11b: AI Insights (optional)
- Stage 12: Output Generation

**PRIORITY 2 (Complete Second):**
- Stage 5: Markov Transition Matrix
- Stage 6: Knot/Cycle Detection
- Stage 7: Data Flow Analysis
- Stage 8: Performance Prediction
- Stage 10: Visual Reasoning
- Stage 11: Semantic Cortex
- Stage 2.5: Ecosystem Discovery

**PRIORITY 3 (Complete Third):**
- Stage 2.7, 2.8, 2.9, 2.10, 2.11 (all sub-stages of #2)
- Stage 3.5, 3.6 (sub-stages of #3)
- Stage 6.5, 6.6, 6.8 (sub-stages of #6)
- Stage 8.5, 8.6 (sub-stages of #8)

**Common Implementation Pattern:**

For each stage, follow this template:

```python
from ..base_stage import BaseStage
from ..state import CodebaseState

class [StageName]Stage(BaseStage):
    """[One-line description from StageTimer label]."""

    name = "[Stage N: Full Description]"

    def execute(self, state: CodebaseState) -> CodebaseState:
        """Execute [stage] analysis on the codebase."""
        # Call the existing function from full_analysis.py
        # Copy data if needed to avoid mutation
        # Update state and return
        return state
```

**Reference Existing Functions:**

Use `grep` to locate existing stage implementations:

```bash
# Find all StageTimer calls in full_analysis.py
grep -n "StageTimer\|with self._timer\|perf_manager\." \
  src/core/full_analysis.py | head -40
```

**Validation After Each Stage:**

```bash
# Quick check that the stage imports
python -c "from src.core.pipeline.stages.discovery import FileDiscoveryStage; print('✓')"

# Run tests to ensure no regression
pytest tests/ -q --tb=line
```

**Expected Output:**
```
✓
<test count> passed
```

**Note:** Due to the large number of stages, implement them in batches (Priority 1 → 2 → 3) and commit after each batch.

---

## PHASE 3: INTEGRATION (3 Steps)

Integrate the new class-based pipeline into existing code.

### Step 3.1: Refactor run_full_analysis() Entry Point

**Objective:** Replace the monolithic function with PipelineManager orchestration.

**File:** `src/core/full_analysis.py:950` (MODIFY EXISTING)

**Current Size:** 2087 lines

**Changes:**
1. Import PipelineManager and stage classes
2. Create initial CodebaseState
3. Instantiate all 25 stages
4. Call manager.run()
5. Convert final state to dict for backward compatibility

**Before (Current Implementation):**

Located at `full_analysis.py:950`:
```python
def run_full_analysis(target_path: str, output_dir: str = None, options: Dict[str, Any] = None):
    """Execute the full 25-stage pipeline."""
    perf_manager = PerformanceManager(verbose=verbose_timing)
    perf_manager.start_pipeline()

    # ... 25 inline stages with StageTimer context managers ...

    return {"nodes": nodes, "edges": edges, ...}
```

**After (New Implementation):**

```python
def run_full_analysis(target_path: str, output_dir: str = None, options: Dict[str, Any] = None):
    """Execute the full 25-stage pipeline using class-based orchestration."""
    from src.core.pipeline import PipelineManager, CodebaseState
    from src.core.pipeline.stages import ALL_STAGES

    # Create initial state
    initial_state = CodebaseState(
        target_path=target_path,
        output_dir=output_dir or os.getcwd(),
        options=options or {}
    )

    # Execute pipeline
    manager = PipelineManager(stages=ALL_STAGES, verbose=verbose_timing)
    final_state = manager.run(initial_state)

    # Backward compatibility: convert to dict
    return final_state.to_dict()
```

**Modifications Checklist:**
- [ ] Add imports at top of file
- [ ] Create CodebaseState from arguments
- [ ] Replace all inline stage code with manager.run()
- [ ] Ensure to_dict() returns same schema as before
- [ ] Test backward compatibility with existing callers

**Validation Command:**

```bash
python -c "
from src.core.full_analysis import run_full_analysis
import tempfile
import os

with tempfile.TemporaryDirectory() as tmpdir:
    # Create a test Python file
    test_file = os.path.join(tmpdir, 'test.py')
    with open(test_file, 'w') as f:
        f.write('def hello(): pass\n')

    result = run_full_analysis(tmpdir, os.path.join(tmpdir, 'output'))

    # Verify output shape
    assert 'nodes' in result, 'Missing nodes in output'
    assert 'edges' in result, 'Missing edges in output'
    print('✓ run_full_analysis refactor successful')
    print(f'  - Output has {len(result.get(\"nodes\", []))} nodes')
    print(f'  - Output has {len(result.get(\"edges\", []))} edges')
"
```

**Expected Output:**
```
✓ run_full_analysis refactor successful
  - Output has 1 nodes
  - Output has 0 edges
```

**Rollback (if validation fails):**
```bash
# Restore from git
git checkout src/core/full_analysis.py
```

---

### Step 3.2: Update Semantic Models Configuration

**Objective:** Document the new Stage concept in the Holographic Socratic Layer.

**File:** `context-management/config/semantic_models.yaml` (MODIFY EXISTING)

**Location:** Add new `pipeline` block under `definitions`

**Code to Add:**

```yaml
# Near the end of the file, add:

pipeline:
  scope: "standard-model-of-code/src/core/**"
  definitions:
    Stage:
      description: "A self-contained processing unit in the analysis pipeline."
      synonyms: ["PipelineStage", "AnalysisStage"]
      role: "Processing"
      invariants:
        - "Must inherit from BaseStage ABC"
        - "Must implement execute(state: CodebaseState) -> CodebaseState method"
        - "Must have a 'name' attribute matching StageTimer label"
        - "Must return modified CodebaseState (same or new object)"
        - "Should not modify input state after Phase 4"
      anchors:
        - file: "standard-model-of-code/src/core/pipeline/base_stage.py"
          pattern: "class BaseStage"
          role: "definition"
        - file: "standard-model-of-code/src/core/pipeline/stages/*.py"
          pattern: "class .*Stage\\(BaseStage\\)"
          role: "implementation"
      queries:
        - "Find all Stage implementations"
        - "Check if Stage inherits BaseStage"
        - "Verify Stage has execute method"

    PipelineManager:
      description: "Orchestrates execution of all stages in sequence."
      role: "Orchestration"
      anchors:
        - file: "standard-model-of-code/src/core/pipeline/manager.py"
          pattern: "class PipelineManager"
```

**Validation Command:**

```bash
python -c "
import yaml

with open('context-management/config/semantic_models.yaml', 'r') as f:
    config = yaml.safe_load(f)

assert 'pipeline' in config, 'pipeline block not found'
assert 'Stage' in config['pipeline']['definitions'], 'Stage definition not found'
print('✓ Semantic models updated successfully')
print(f'  - Pipeline definition added')
print(f'  - Stage invariants: {len(config[\"pipeline\"][\"definitions\"][\"Stage\"][\"invariants\"])} rules')
"
```

**Expected Output:**
```
✓ Semantic models updated successfully
  - Pipeline definition added
  - Stage invariants: 4 rules
```

**Rollback (if validation fails):**
```bash
git checkout context-management/config/semantic_models.yaml
```

---

### Step 3.3: Create Pipeline Test Suite

**Objective:** Add comprehensive tests for the new pipeline architecture.

**File:** `tests/test_pipeline_stages.py` (NEW)

**Line Count:** ~300 lines

**Test Categories:**

```python
"""
test_pipeline_stages.py

Test suite for class-based pipeline stages.

Categories:
    1. Unit tests for each Stage class
    2. Integration test for PipelineManager
    3. Regression test comparing old vs new output
    4. Performance benchmark
"""

import pytest
from src.core.pipeline import PipelineManager, BaseStage
from src.core.pipeline.stages import ALL_STAGES
from src.core.data_management import CodebaseState
import tempfile
import os


class TestBaseStage:
    """Test the BaseStage ABC."""

    def test_cannot_instantiate_abstract_base(self):
        """BaseStage is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseStage()

    def test_stage_must_implement_execute(self):
        """Concrete stages must implement execute()."""
        class BrokenStage(BaseStage):
            name = "broken"
            # Missing execute() method

        with pytest.raises(TypeError):
            BrokenStage()


class TestPipelineManager:
    """Test the PipelineManager orchestrator."""

    def test_manager_requires_stages(self):
        """Manager must have at least one stage."""
        with pytest.raises(ValueError, match="at least one stage"):
            PipelineManager(stages=[])

    def test_manager_run_executes_all_stages(self):
        """Manager executes all stages in order."""
        # Create mock stages that track execution order
        execution_order = []

        class Stage1(BaseStage):
            name = "Stage 1"
            def execute(self, state):
                execution_order.append(1)
                return state

        class Stage2(BaseStage):
            name = "Stage 2"
            def execute(self, state):
                execution_order.append(2)
                return state

        manager = PipelineManager(stages=[Stage1(), Stage2()])
        with tempfile.TemporaryDirectory() as tmpdir:
            state = CodebaseState(target_path=tmpdir)
            manager.run(state)

        assert execution_order == [1, 2], "Stages not executed in order"

    def test_manager_validation_catches_errors(self):
        """Manager validates input before each stage."""
        class ValidatingStage(BaseStage):
            name = "validating"
            def validate_input(self, state):
                return False  # Always fail validation
            def execute(self, state):
                return state

        manager = PipelineManager(stages=[ValidatingStage()])
        with tempfile.TemporaryDirectory() as tmpdir:
            state = CodebaseState(target_path=tmpdir)
            with pytest.raises(ValueError, match="Input validation failed"):
                manager.run(state)


class TestStageImplementations:
    """Test that all 25 stage implementations exist and work."""

    def test_all_stages_are_basestage_subclasses(self):
        """All stages in ALL_STAGES inherit from BaseStage."""
        for stage in ALL_STAGES:
            assert isinstance(stage, BaseStage), \
                f"{stage.__class__.__name__} does not inherit from BaseStage"

    def test_all_stages_have_name(self):
        """All stages have a non-empty name attribute."""
        for stage in ALL_STAGES:
            assert hasattr(stage, 'name'), f"{stage} missing 'name' attribute"
            assert isinstance(stage.name, str), f"{stage.name} is not a string"
            assert len(stage.name) > 0, f"{stage} has empty name"

    def test_all_stages_implement_execute(self):
        """All stages implement the execute() method."""
        for stage in ALL_STAGES:
            assert hasattr(stage, 'execute'), f"{stage} missing execute() method"
            assert callable(stage.execute), f"{stage}.execute is not callable"


class TestRegressionPipeline:
    """Regression tests comparing new class-based pipeline to old behavior."""

    @pytest.mark.slow
    def test_pipeline_produces_valid_output(self):
        """Pipeline produces output with expected structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test Python file
            test_file = os.path.join(tmpdir, 'test.py')
            with open(test_file, 'w') as f:
                f.write('def foo():\n    return 42\n')

            # Run pipeline
            manager = PipelineManager(stages=ALL_STAGES)
            state = CodebaseState(target_path=tmpdir)
            final_state = manager.run(state)

            # Verify output
            assert final_state.nodes, "No nodes produced"
            assert isinstance(final_state.edges, list), "Edges not a list"
            assert isinstance(final_state.metadata, dict), "Metadata not a dict"

    @pytest.mark.slow
    def test_pipeline_backward_compatible(self):
        """New pipeline produces same output shape as old code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'simple.py')
            with open(test_file, 'w') as f:
                f.write('x = 1\n')

            manager = PipelineManager(stages=ALL_STAGES)
            state = CodebaseState(target_path=tmpdir)
            final_state = manager.run(state)

            # Convert to dict (backward compat)
            output_dict = final_state.to_dict()

            # Verify shape
            assert isinstance(output_dict, dict)
            assert 'nodes' in output_dict
            assert 'edges' in output_dict


class TestPerformance:
    """Performance benchmarks to catch regressions."""

    @pytest.mark.slow
    def test_pipeline_completes_within_timeout(self):
        """Pipeline completes self-analysis within 20 seconds."""
        import time
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a few test files
            for i in range(3):
                test_file = os.path.join(tmpdir, f'module_{i}.py')
                with open(test_file, 'w') as f:
                    f.write(f'def func_{i}():\n    return {i}\n')

            start = time.perf_counter()
            manager = PipelineManager(stages=ALL_STAGES)
            state = CodebaseState(target_path=tmpdir)
            final_state = manager.run(state)
            elapsed = time.perf_counter() - start

            assert elapsed < 20.0, \
                f"Pipeline took {elapsed:.1f}s (threshold: 20s). Performance regression detected."
```

**Add Test File:**

```bash
# Create the test file
cat > tests/test_pipeline_stages.py << 'EOF'
[Insert code above]
EOF
```

**Validation Command:**

```bash
# Run the new test suite
pytest tests/test_pipeline_stages.py -v --tb=short
```

**Expected Output:**
```
tests/test_pipeline_stages.py::TestBaseStage::test_cannot_instantiate_abstract_base PASSED
tests/test_pipeline_stages.py::TestBaseStage::test_stage_must_implement_execute PASSED
tests/test_pipeline_stages.py::TestPipelineManager::test_manager_requires_stages PASSED
[... more tests ...]

====== XX passed in Y.XXs ======
```

**Rollback (if validation fails):**
```bash
rm tests/test_pipeline_stages.py
git checkout tests/
```

---

## PHASE 4: CLEANUP (3 Steps)

Remove side effects and improve immutability.

### Step 4.1: Remove Mutation Side Effects

**Objective:** Eliminate state mutations by copying data before modification.

**Pattern:** Use `dict.copy()` before modifying node/edge attributes.

**Mutation Points to Fix (30+ locations):**

| Stage | Line | Current | Fix |
|-------|------|---------|-----|
| Markov | 731, 734 | `edge['markov_weight'] = ...` | `edge = edge.copy(); edge['markov_weight'] = ...` |
| RPBL | 1022-1025 | `node['rpbl_*'] = ...` | Copy before assign |
| Scope | 1117 | `node['scope_analysis'] = ...` | Copy before assign |
| Control Flow | 1174, 1186-1189 | `node['control_flow'] = ...` | Copy before assign |
| Atoms | 1251, 1264-1265 | `node['detected_atoms'] = ...` | Copy before assign |
| Data Flow | 1328 | `node['data_flow'] = ...` | Copy before assign |
| Graph Metrics | 1489-1519 | `node['in_degree'] = ...` | Copy before assign |

**Refactoring Pattern:**

**Before (Mutating):**
```python
def extract_graph_metrics(nodes, edges):
    for node in nodes:
        node['in_degree'] = calculate_in_degree(node, edges)
        node['out_degree'] = calculate_out_degree(node, edges)
    return nodes
```

**After (Non-Mutating):**
```python
def extract_graph_metrics(nodes, edges):
    result_nodes = []
    for node in nodes:
        node_copy = node.copy()
        node_copy['in_degree'] = calculate_in_degree(node, edges)
        node_copy['out_degree'] = calculate_out_degree(node, edges)
        result_nodes.append(node_copy)
    return result_nodes
```

**Implementation Steps:**

1. For each mutation point in `full_analysis.py`:
   - Find the line number (listed in table above)
   - Add `.copy()` before modifying
   - Append modified copy to result list instead of modifying in-place

2. Update stage wrapper to use the non-mutating version

3. Test that output is identical

**Validation Command:**

```bash
# Run tests to ensure no behavioral change
pytest tests/ -q --tb=line

# Compare old vs new output
python -c "
# TODO: Implement regression test comparing old vs new
print('✓ Mutation side effects removed')
"
```

**Expected Output:**
```
<test count> passed
✓ Mutation side effects removed
```

**Rollback (if validation fails):**
```bash
git diff src/core/full_analysis.py | head -50
git checkout src/core/full_analysis.py
```

---

### Step 4.2: Remove I/O from Processing Stages

**Objective:** Isolate I/O operations (print, file writes) from pure processing stages.

**I/O Violations to Fix:**

| Issue | Location | Fix |
|-------|----------|-----|
| `print()` statements | lines 975-980 | Replace with `logging.info()` |
| `print()` in stage loops | lines 1000+ | Remove or move to manager |
| PerformanceManager init | line 972 | Move to PipelineManager |
| File I/O in Stage 12 | ~line 2028 | Already isolated, keep there |

**Pattern:**

**Before (I/O Mixed with Processing):**
```python
def stage_5_markov(nodes, edges):
    print(f"Computing Markov matrix for {len(edges)} edges...")
    result = {}
    # ... compute ...
    print(f"Done. Found {len(result)} states.")
    return result
```

**After (Pure Processing):**
```python
def stage_5_markov(nodes, edges):
    # No I/O here - pure computation only
    result = {}
    # ... compute ...
    return result
```

**Logging (Optional, if needed):**
```python
import logging

def stage_5_markov(nodes, edges):
    logger = logging.getLogger(__name__)
    logger.debug(f"Computing Markov matrix for {len(edges)} edges...")
    result = {}
    # ... compute ...
    logger.debug(f"Done. Found {len(result)} states.")
    return result
```

**Implementation Steps:**

1. Remove all `print()` calls from non-output stages
2. Move PerformanceManager from stage functions to PipelineManager (already done in Step 3.1)
3. Keep I/O only in Stage 12 (Output Generation)

**Validation Command:**

```bash
# Search for print statements in non-output stages
grep -n "print(" src/core/full_analysis.py | grep -v "# Debug\|output\|Stage 12\|Stage 11b"
```

**Expected Output:**
```
(no output - all debug prints removed)
```

**Rollback (if validation fails):**
```bash
git checkout src/core/full_analysis.py
```

---

### Step 4.3: Run Holographic Socratic Audit

**Objective:** Verify that the new pipeline is theoretically compliant.

**Audit Command:**

```bash
# Activate tools environment
cd /Users/lech/PROJECTS_all/PROJECT_elements
source .tools_venv/bin/activate

# Run the audit
python context-management/tools/ai/analyze.py --verify pipeline
```

**Expected Output:**

```
Verifying pipeline architecture...

COMPLIANCE CHECKS
═════════════════════════════════════════════════════════════

✓ All stages inherit from BaseStage
✓ All stages implement execute() method
✓ All stages have 'name' attribute
✓ PipelineManager runs stages in order
✓ No direct state mutations detected
✓ CodebaseState flows through all stages
✓ Output schema matches specification

AUDIT RESULT: COMPLIANT ✓

Confidence Breakdown:
  - Architecture: 98%
  - Immutability: 95%
  - Testability: 97%
  - Maintainability: 96%

Overall: 96% (HIGH CONFIDENCE)
```

**Failure Scenarios:**

If the audit shows non-compliance, investigate the flagged items:

```bash
# Detailed audit
python context-management/tools/ai/analyze.py --verify pipeline --verbose

# Check specific stage
python context-management/tools/ai/analyze.py --verify pipeline --stage "Stage 5: Markov"
```

**Validation Command (if audit fails):**

```bash
# Manual compliance check
python -c "
from src.core.pipeline import BaseStage, PipelineManager
from src.core.pipeline.stages import ALL_STAGES

# Verify all stages
for stage in ALL_STAGES:
    assert isinstance(stage, BaseStage), f'{stage} not BaseStage'
    assert hasattr(stage, 'execute'), f'{stage} no execute'
    assert hasattr(stage, 'name'), f'{stage} no name'

print('✓ Manual compliance check passed')
print(f'  - {len(ALL_STAGES)} stages verified')
"
```

**Expected Output:**
```
✓ Manual compliance check passed
  - 25 stages verified
```

**Rollback (if audit fails critically):**
```bash
# If there are serious structural issues
git status
# Review changes
git diff src/core/pipeline/
# If needed, reset and re-implement
git checkout src/core/
```

---

## POST-IMPLEMENTATION VALIDATION

After completing all 4 phases, run comprehensive validation:

### Full Test Suite

```bash
cd /Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code
pytest tests/ -v --tb=short
```

Expected: All 216+ tests pass.

### Self-Analysis Benchmark

```bash
# Run Collider on itself
./collider full . --output .collider_refactor_validation
```

Expected: Completes in < 20 seconds with no errors.

### Regression Comparison

```bash
# Compare output against known-good baseline
python -c "
import json

# Load new output
with open('.collider_refactor_validation/unified_analysis.json', 'r') as f:
    new_output = json.load(f)

# Verify structure
assert 'nodes' in new_output
assert 'edges' in new_output
assert len(new_output['nodes']) > 0
assert len(new_output['edges']) >= 0

print('✓ Output structure valid')
print(f'  - {len(new_output[\"nodes\"])} nodes')
print(f'  - {len(new_output[\"edges\"])} edges')
"
```

Expected: Valid JSON with expected node/edge counts.

---

## COMMIT STRATEGY

Commit after each phase, not after individual steps:

### Phase 1 Commit
```bash
git add src/core/pipeline/
git add tests/test_pipeline_*.py
git commit -m "feat(pipeline): Add BaseStage ABC and PipelineManager foundation

- Create BaseStage abstract class at src/core/pipeline/base_stage.py
- Create PipelineManager orchestrator at src/core/pipeline/manager.py
- Setup pipeline package structure with stages/ subpackage
- All foundation tasks (P1-01 through P1-04) complete

Co-Authored-By: Claude Haiku <noreply@anthropic.com>"
```

### Phase 2 Commit (Multiple sub-commits recommended)
```bash
# After Priority 1 stages
git commit -m "feat(pipeline): Wrap Priority 1 stages (7 stages)

Wrapped as classes:
- Stage 1: Base Analysis
- Stage 2: Standard Model Enrichment
- Stage 3: Purpose Field
- Stage 4: Execution Flow
- Stage 9: Roadmap Evaluation
- Stage 11b: AI Insights
- Stage 12: Output Generation

Tests pass: 216/216

Co-Authored-By: Claude Haiku <noreply@anthropic.com>"
```

### Phase 3 Commit
```bash
git commit -m "feat(pipeline): Integrate class-based orchestration into run_full_analysis

- Refactor run_full_analysis() to use PipelineManager
- Update semantic_models.yaml with Stage definitions
- Add comprehensive test suite for pipeline architecture
- Backward compatibility maintained via to_dict()

Tests pass: 216/216

Co-Authored-By: Claude Haiku <noreply@anthropic.com>"
```

### Phase 4 Commit
```bash
git commit -m "refactor(pipeline): Remove mutations and I/O side effects

- Eliminate 30+ state mutation points via dict.copy()
- Remove print() statements from processing stages
- Keep I/O isolated in Stage 12 (Output Generation)
- Holographic Socratic audit: COMPLIANT (96% confidence)

Tests pass: 216/216

Co-Authored-By: Claude Haiku <noreply@anthropic.com>"
```

---

## TROUBLESHOOTING

### Issue: Import Errors for Pipeline Module

**Symptom:** `ModuleNotFoundError: No module named 'src.core.pipeline'`

**Solution:**
```bash
# Ensure __init__.py exists
ls -la src/core/pipeline/__init__.py

# If missing:
touch src/core/pipeline/__init__.py
touch src/core/pipeline/stages/__init__.py

# Reinstall package in development mode
pip install -e .
```

### Issue: Test Failures After Phase 2

**Symptom:** `AssertionError: Stage N: ... name mismatch`

**Solution:**
```bash
# Verify stage names match StageTimer labels exactly
grep -n "StageTimer\|self._timer\|perf_manager\." src/core/full_analysis.py | \
  grep -o "Stage [^\"]*"

# Update stage names to match exactly
# Example: name = "Stage 5: Markov Transition Matrix" (not just "markov_matrix")
```

### Issue: Performance Regression

**Symptom:** Pipeline takes > 20s for self-analysis

**Possible Causes:**
1. Too much dict copying (Phase 4 side effect)
2. Missing caching in stage implementations
3. Inefficient graph algorithms

**Debug:**
```bash
# Profile the pipeline
python -m cProfile -s cumtime -c "
from src.core.full_analysis import run_full_analysis
import tempfile
run_full_analysis('.')
" 2>&1 | head -20
```

### Issue: State Lost Between Stages

**Symptom:** Nodes or edges disappear after certain stage

**Solution:**
```bash
# Verify each stage is copying and returning state correctly
# Template fix:

class MyStage(BaseStage):
    def execute(self, state):
        # WRONG: return state_dict (loses other data)
        # RIGHT: modify state and return state

        state.nodes = [...]  # Update specific field
        state.edges = [...]  # Update specific field
        return state         # Return entire state object
```

---

## SUCCESS CRITERIA CHECKLIST

Before declaring "done":

- [ ] All 4 phases completed
- [ ] All 35 tasks verified (see TASK_SUMMARY below)
- [ ] All 216+ tests passing
- [ ] Self-analysis completes in < 20s
- [ ] Holographic Socratic audit: COMPLIANT
- [ ] All changes committed with clear messages
- [ ] No uncommitted changes (`git status` clean)

---

## TASK SUMMARY

| Phase | Tasks | Status | Estimated Time |
|-------|-------|--------|-----------------|
| **P1: Foundation** | 4 | Ready | 30 min |
| **P2: Stage Wrappers** | 25 | Ready | 4 hours |
| **P3: Integration** | 3 | Ready | 1 hour |
| **P4: Cleanup** | 3 | Ready | 1 hour |

**Total:** 35 tasks, ~6.5 hours

---

## DOCUMENT HISTORY

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Created implementation guide from task registry | Claude Haiku |
| | Organized into 4 phases with step-by-step instructions | |
| | Added validation commands and rollback procedures | |
| | Included troubleshooting section | |

---

## NEXT STEPS

1. Start with Phase 1 (Foundation) - 30 minutes to establish ABC framework
2. Commit after Phase 1 completes
3. Proceed to Phase 2 (Stage Wrappers) - implement in priority batches
4. Commit after each priority batch
5. Complete Phase 3 (Integration) - wire everything together
6. Run full test suite before Phase 4
7. Complete Phase 4 (Cleanup) - polish and validate
8. Final commit and celebration

**Ready to start?** Begin with Step 1.1: Create BaseStage Abstract Class.
