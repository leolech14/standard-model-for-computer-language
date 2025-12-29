# Comprehensive Refactoring Guide
## Standard Model of Code - Coupling Hotspot Resolution

**Generated**: 2025-12-28
**Analysis Basis**: 934 nodes, 5,931 edges
**Threshold**: 19.6 out-degree (avg * 2)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Hotspots | 69 |
| Expected (OK) | 19 |
| Needs Review | 50 |
| Priority 1 (Critical) | 5 |
| Priority 2 (High) | 5 |
| Priority 3 (Medium) | 6 |
| Estimated Total Effort | 40-60 hours |

---

## Priority 1: Critical Refactoring (Confidence: 85-95%)

### Task 1.1: Split LensInterrogator
**File**: `src/core/lens_interrogator.py`
**Metrics**: 701 lines, 2 classes, 24 methods, out-degree=119

**Confidence Score**: 92%

**Problem**: Single class handling multiple interrogation concerns - AST analysis, pattern matching, semantic extraction, and reporting.

**Refactoring Strategy**: Extract by Responsibility

**Step-by-Step**:
1. [ ] **Analyze current structure** (30 min)
   ```bash
   grep "def " src/core/lens_interrogator.py | head -30
   ```
   - Identify method groupings by prefix/purpose
   - Map dependencies between methods

2. [ ] **Create responsibility groups** (15 min)
   - AST Operations → `ASTLens`
   - Pattern Matching → `PatternLens`
   - Semantic Analysis → `SemanticLens`
   - Reporting → `LensReporter`

3. [ ] **Extract ASTLens class** (45 min)
   - Move AST traversal methods
   - Create `src/core/lenses/ast_lens.py`
   - Keep shared utilities in base class

4. [ ] **Extract PatternLens class** (45 min)
   - Move pattern matching methods
   - Create `src/core/lenses/pattern_lens.py`

5. [ ] **Extract SemanticLens class** (45 min)
   - Move semantic extraction methods
   - Create `src/core/lenses/semantic_lens.py`

6. [ ] **Create LensInterrogator facade** (30 min)
   - Compose the three lens classes
   - Maintain backward-compatible API

7. [ ] **Update imports across codebase** (20 min)
   ```bash
   grep -r "LensInterrogator" src/ --include="*.py"
   ```

8. [ ] **Run tests and verify** (20 min)
   ```bash
   python -m pytest tests/ -v -k "lens"
   ```

**Verification Checklist**:
- [ ] Each new class has < 40 out-degree
- [ ] No circular imports introduced
- [ ] All existing tests pass
- [ ] Public API unchanged

**Risk**: Medium - Central component, needs careful extraction
**Dependencies**: None (leaf component)

---

### Task 1.2: Split LayerRevealer
**File**: `src/analytics/layer_revealer.py`
**Metrics**: 596 lines, 2 classes, 19 methods, out-degree=96

**Confidence Score**: 90%

**Problem**: Combines layer detection, boundary analysis, and violation reporting in one class.

**Refactoring Strategy**: Extract by Domain Concept

**Step-by-Step**:
1. [ ] **Map current responsibilities** (20 min)
   - Layer Detection (which layer is code in?)
   - Boundary Analysis (what crosses layers?)
   - Violation Detection (what breaks rules?)
   - Metrics Calculation

2. [ ] **Extract LayerDetector** (40 min)
   - File: `src/analytics/layers/layer_detector.py`
   - Methods: `detect_layer()`, `classify_file()`, `get_layer_config()`
   - Target: < 25 dependencies

3. [ ] **Extract BoundaryAnalyzer** (40 min)
   - File: `src/analytics/layers/boundary_analyzer.py`
   - Methods: `find_crossings()`, `analyze_imports()`, `map_dependencies()`
   - Target: < 25 dependencies

4. [ ] **Extract ViolationReporter** (30 min)
   - File: `src/analytics/layers/violation_reporter.py`
   - Methods: `check_violations()`, `format_report()`, `severity_score()`
   - Target: < 20 dependencies

5. [ ] **Refactor LayerRevealer as coordinator** (30 min)
   - Inject the three components
   - Orchestrate analysis flow
   - Target: < 15 dependencies

6. [ ] **Create __init__.py for layers package** (10 min)
   ```python
   from .layer_detector import LayerDetector
   from .boundary_analyzer import BoundaryAnalyzer
   from .violation_reporter import ViolationReporter
   from .layer_revealer import LayerRevealer
   ```

7. [ ] **Update all imports** (15 min)

8. [ ] **Verify with tests** (20 min)

**Verification Checklist**:
- [ ] LayerRevealer out-degree < 30
- [ ] Each extracted class is single-responsibility
- [ ] Layer detection accuracy unchanged
- [ ] No performance regression

**Risk**: Medium - Used by visualization
**Dependencies**: CanonicalVisualizer uses this

---

### Task 1.3: Decompose PurposeFieldDetector
**File**: `src/core/purpose_field.py`
**Metrics**: 368 lines, 4 classes, 9 methods, out-degree=74

**Confidence Score**: 88%

**Problem**: High "uses" count (47) indicates it references many enums/constants. Combines purpose detection with field classification.

**Refactoring Strategy**: Separate Detection from Classification

**Step-by-Step**:
1. [ ] **Audit enum/constant usage** (20 min)
   ```bash
   grep -E "[A-Z][A-Z_]+" src/core/purpose_field.py | sort | uniq -c
   ```

2. [ ] **Extract PurposeClassifier** (35 min)
   - Purpose: Map code elements to purpose categories
   - File: `src/core/purpose/purpose_classifier.py`
   - Move: Classification logic, enum mappings

3. [ ] **Extract FieldMapper** (35 min)
   - Purpose: Map purposes to architectural fields
   - File: `src/core/purpose/field_mapper.py`
   - Move: Field assignment logic

4. [ ] **Create purpose constants module** (20 min)
   - File: `src/core/purpose/constants.py`
   - Consolidate all enums and mappings
   - Single source of truth for purpose definitions

5. [ ] **Simplify PurposeFieldDetector** (25 min)
   - Compose classifier + mapper
   - Reduce to coordination logic only
   - Target: < 25 dependencies

6. [ ] **Update package structure** (15 min)
   ```
   src/core/purpose/
   ├── __init__.py
   ├── constants.py
   ├── purpose_classifier.py
   ├── field_mapper.py
   └── detector.py
   ```

7. [ ] **Verify** (15 min)

**Verification Checklist**:
- [ ] Constants centralized in one file
- [ ] Detector out-degree < 30
- [ ] Classification accuracy unchanged

**Risk**: Low-Medium - Well-defined boundaries
**Dependencies**: InsightsEngine, ExecutionFlowDetector

---

### Task 1.4: Refactor create_unified_output
**File**: `src/core/output_factory.py`
**Metrics**: 147 lines, 0 classes, 1 method, out-degree=63

**Confidence Score**: 95%

**Problem**: Single function with 63 calls - doing too much. Classic "God Function" anti-pattern.

**Refactoring Strategy**: Extract to Builder Pattern

**Step-by-Step**:
1. [ ] **Analyze function structure** (15 min)
   - Identify logical sections
   - Map data flow

2. [ ] **Create UnifiedOutputBuilder class** (30 min)
   ```python
   class UnifiedOutputBuilder:
       def __init__(self, config):
           self.config = config
           self._output = {}

       def with_metadata(self) -> 'UnifiedOutputBuilder': ...
       def with_nodes(self, nodes) -> 'UnifiedOutputBuilder': ...
       def with_edges(self, edges) -> 'UnifiedOutputBuilder': ...
       def with_stats(self, stats) -> 'UnifiedOutputBuilder': ...
       def with_classification(self, data) -> 'UnifiedOutputBuilder': ...
       def build(self) -> dict: ...
   ```

3. [ ] **Extract section builders** (45 min)
   - `_build_metadata()` - timestamps, versions
   - `_build_stats()` - aggregations
   - `_build_classification()` - type breakdowns
   - `_build_architecture()` - layer analysis

4. [ ] **Create factory function** (15 min)
   ```python
   def create_unified_output(data, config=None):
       return (UnifiedOutputBuilder(config)
           .with_metadata()
           .with_nodes(data['nodes'])
           .with_edges(data['edges'])
           .with_stats(data['stats'])
           .build())
   ```

5. [ ] **Update callers** (20 min)

6. [ ] **Verify output format unchanged** (15 min)
   ```bash
   diff <(python old_output.py) <(python new_output.py)
   ```

**Verification Checklist**:
- [ ] Builder methods each have < 10 dependencies
- [ ] Output JSON schema unchanged
- [ ] Backward compatible API

**Risk**: Low - Isolated function
**Dependencies**: run_proof, visualization

---

### Task 1.5: Modularize AntimatterEvaluator
**File**: `src/core/antimatter_evaluator.py`
**Metrics**: 356 lines, 3 classes, 14 methods, out-degree=59

**Confidence Score**: 87%

**Problem**: Evaluates multiple "antimatter" patterns (code smells) in one class.

**Refactoring Strategy**: Strategy Pattern for Evaluators

**Step-by-Step**:
1. [ ] **Identify evaluation types** (20 min)
   - Dead code detection
   - Unused imports
   - Unreachable branches
   - Shadow variables

2. [ ] **Create Evaluator interface** (15 min)
   ```python
   class AntimatterEvaluator(Protocol):
       def evaluate(self, node: dict) -> List[AntimatterIssue]: ...
       def name(self) -> str: ...
   ```

3. [ ] **Extract DeadCodeEvaluator** (30 min)
   - File: `src/core/evaluators/dead_code.py`

4. [ ] **Extract UnusedImportEvaluator** (30 min)
   - File: `src/core/evaluators/unused_imports.py`

5. [ ] **Extract UnreachableCodeEvaluator** (30 min)
   - File: `src/core/evaluators/unreachable.py`

6. [ ] **Create EvaluatorRegistry** (25 min)
   ```python
   class EvaluatorRegistry:
       def __init__(self):
           self._evaluators = []

       def register(self, evaluator: AntimatterEvaluator): ...
       def evaluate_all(self, nodes) -> List[AntimatterIssue]: ...
   ```

7. [ ] **Wire up in main evaluator** (20 min)

8. [ ] **Verify all issues detected** (20 min)

**Verification Checklist**:
- [ ] Each evaluator < 20 dependencies
- [ ] Registry coordinates without coupling
- [ ] All antimatter types still detected
- [ ] Easy to add new evaluators

**Risk**: Medium - Core analysis component
**Dependencies**: InsightsEngine, ProofRunner

---

## Priority 2: High Priority Refactoring (Confidence: 80-90%)

### Task 2.1: Decompose run_proof
**File**: `src/tools/prove.py`
**Metrics**: 544 lines, 0 classes, 2 methods, out-degree=56

**Confidence Score**: 85%

**Problem**: Monolithic proof orchestration function.

**Step-by-Step**:
1. [ ] Create `ProofOrchestrator` class
2. [ ] Extract `ProofStage` classes for each stage
3. [ ] Implement pipeline pattern
4. [ ] Add stage-level error handling

**Estimated Effort**: 3-4 hours

---

### Task 2.2: Split BoundaryMapper
**File**: `src/tools/boundary_mapper.py`
**Metrics**: 650 lines, 6 classes, 14 methods, out-degree=55

**Confidence Score**: 83%

**Problem**: Multiple mapping concerns combined.

**Step-by-Step**:
1. [ ] Extract `ModuleBoundaryMapper`
2. [ ] Extract `ClassBoundaryMapper`
3. [ ] Extract `FunctionBoundaryMapper`
4. [ ] Create unified `BoundaryMapperFacade`

**Estimated Effort**: 3-4 hours

---

### Task 2.3: Simplify DimensionEnricher
**File**: `src/core/dimension_enricher.py`
**Metrics**: 553 lines, 2 classes, 17 methods, out-degree=54

**Confidence Score**: 82%

**Problem**: Enriches multiple dimensions in one pass.

**Step-by-Step**:
1. [ ] Create `DimensionEnricherPipeline`
2. [ ] Extract enrichers per dimension type
3. [ ] Allow selective enrichment

**Estimated Effort**: 2-3 hours

---

### Task 2.4: Modularize AtomExtractor
**File**: `src/core/atom_extractor.py`
**Metrics**: 626 lines, 5 classes, 21 methods, out-degree=53

**Confidence Score**: 80%

**Problem**: Extracts multiple atom types with shared logic.

**Step-by-Step**:
1. [ ] Create `AtomExtractor` base class
2. [ ] Extract `FunctionAtomExtractor`
3. [ ] Extract `ClassAtomExtractor`
4. [ ] Extract `ModuleAtomExtractor`
5. [ ] Create `CompositeAtomExtractor`

**Estimated Effort**: 4-5 hours

---

### Task 2.5: Restructure ConversationFlowAnalyzer
**File**: `src/tools/conversation_mapper.py`
**Metrics**: 526 lines, 4 classes, 12 methods, out-degree=43

**Confidence Score**: 80%

**Problem**: Conversation analysis mixed with flow detection.

**Step-by-Step**:
1. [ ] Extract `ConversationParser`
2. [ ] Extract `FlowDetector`
3. [ ] Extract `ConversationReporter`

**Estimated Effort**: 2-3 hours

---

## Priority 3: Medium Priority Refactoring (Confidence: 70-85%)

### Task 3.1: ChatExtractor Cleanup
**File**: `src/tools/extract_chat_insights.py`
**Metrics**: 559 lines, 3 classes, 12 methods, out-degree=40

**Confidence Score**: 78%

**Estimated Effort**: 2 hours

---

### Task 3.2: LLMDiscoveryPipeline Modularization
**File**: `src/core/llm_discovery.py`
**Metrics**: 507 lines, 5 classes, 17 methods, out-degree=44

**Confidence Score**: 75%

**Estimated Effort**: 3 hours

---

### Task 3.3: SmartExtractor Simplification
**Metrics**: out-degree=37

**Confidence Score**: 75%

**Estimated Effort**: 2 hours

---

### Task 3.4: CompleteExtractor Decomposition
**Metrics**: out-degree=37

**Confidence Score**: 72%

**Estimated Effort**: 2 hours

---

### Task 3.5: PythonASTParser Modularization
**Metrics**: out-degree=47

**Confidence Score**: 70%

**Estimated Effort**: 3 hours

---

### Task 3.6: ExecutionFlowDetector Cleanup
**Metrics**: out-degree=47

**Confidence Score**: 70%

**Estimated Effort**: 2-3 hours

---

## Refactoring Patterns Reference

### Pattern 1: Extract Class
**When**: Single class doing multiple things
**How**: Identify responsibility groups → Create new classes → Compose in original

### Pattern 2: Strategy Pattern
**When**: Multiple algorithms/evaluators
**How**: Define interface → Extract implementations → Use registry/factory

### Pattern 3: Builder Pattern
**When**: Complex object construction
**How**: Create builder class → Chain methods → Build final object

### Pattern 4: Facade Pattern
**When**: Need backward compatibility
**How**: Keep original API → Delegate to new components → Gradual migration

### Pattern 5: Pipeline Pattern
**When**: Sequential processing stages
**How**: Define stage interface → Extract stages → Chain execution

---

## Verification Commands

```bash
# Re-run analysis after each refactoring
python3 cli.py analyze src/ --output output/post_refactor

# Check coupling reduction
python3 -c "
import json
data = json.loads(open('output/post_refactor/unified_analysis.json').read())
edges = [e for e in data['edges'] if e.get('edge_type','').upper() != 'CONTAINS']
from collections import Counter
out_deg = Counter(e['source'] for e in edges)
print('Top 10 by out-degree:')
for name, deg in out_deg.most_common(10):
    print(f'  {name}: {deg}')
"

# Run tests
python3 -m pytest tests/ -v

# Check for circular imports
python3 -c "
import sys
sys.setrecursionlimit(100)
try:
    from src.core import lens_interrogator
    print('No circular imports')
except RecursionError:
    print('CIRCULAR IMPORT DETECTED')
"
```

---

## Risk Matrix

| Task | Impact | Effort | Risk | Priority Score |
|------|--------|--------|------|----------------|
| 1.1 LensInterrogator | High | 4h | Medium | 9.2 |
| 1.2 LayerRevealer | High | 4h | Medium | 9.0 |
| 1.3 PurposeFieldDetector | Medium | 3h | Low | 8.8 |
| 1.4 create_unified_output | Medium | 2h | Low | 9.5 |
| 1.5 AntimatterEvaluator | Medium | 3h | Medium | 8.7 |
| 2.1 run_proof | High | 4h | Medium | 8.5 |
| 2.2 BoundaryMapper | Medium | 4h | Medium | 8.3 |
| 2.3 DimensionEnricher | Medium | 3h | Low | 8.2 |
| 2.4 AtomExtractor | High | 5h | Medium | 8.0 |
| 2.5 ConversationFlowAnalyzer | Low | 3h | Low | 8.0 |

---

## Execution Order Recommendation

**Phase 1 - Quick Wins (Day 1)**
1. Task 1.4: create_unified_output (2h, lowest risk)
2. Task 1.3: PurposeFieldDetector (3h, low risk)

**Phase 2 - Core Components (Day 2-3)**
3. Task 1.1: LensInterrogator (4h)
4. Task 1.2: LayerRevealer (4h)
5. Task 1.5: AntimatterEvaluator (3h)

**Phase 3 - Supporting Components (Day 4-5)**
6. Task 2.1: run_proof (4h)
7. Task 2.2: BoundaryMapper (4h)
8. Task 2.4: AtomExtractor (5h)

**Phase 4 - Cleanup (Day 6)**
9. Remaining Priority 2 & 3 tasks

---

## Success Metrics

After refactoring completion:

| Metric | Before | Target |
|--------|--------|--------|
| Max out-degree | 247 | < 50 |
| Avg out-degree | 9.82 | < 8.0 |
| Hotspots (>19.6) | 69 | < 25 |
| Components needing review | 50 | < 15 |
| Test coverage | Current | >= Current |

---

## Notes

- Always run tests after each task
- Commit after each successful refactoring
- Update imports incrementally
- Keep public APIs stable where possible
- Document breaking changes

**Last Updated**: 2025-12-28
