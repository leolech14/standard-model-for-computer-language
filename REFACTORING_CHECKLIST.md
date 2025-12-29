# Refactoring Checklist
## Quick Reference Task List

---

## Priority 1: Critical (Confidence 85-95%)

### [ ] 1.1 LensInterrogator → Split into 3 Lenses
**Confidence: 92%** | **Effort: 4h** | **Risk: Medium**
```
src/core/lens_interrogator.py (701 lines, out=119)
  ↓ Split into:
  src/core/lenses/ast_lens.py
  src/core/lenses/pattern_lens.py
  src/core/lenses/semantic_lens.py
```
- [ ] Analyze method groupings
- [ ] Extract ASTLens class
- [ ] Extract PatternLens class
- [ ] Extract SemanticLens class
- [ ] Create facade coordinator
- [ ] Update imports
- [ ] Run tests

---

### [ ] 1.2 LayerRevealer → Extract 3 Components
**Confidence: 90%** | **Effort: 4h** | **Risk: Medium**
```
src/analytics/layer_revealer.py (596 lines, out=96)
  ↓ Split into:
  src/analytics/layers/layer_detector.py
  src/analytics/layers/boundary_analyzer.py
  src/analytics/layers/violation_reporter.py
```
- [ ] Map responsibilities
- [ ] Extract LayerDetector
- [ ] Extract BoundaryAnalyzer
- [ ] Extract ViolationReporter
- [ ] Refactor as coordinator
- [ ] Create package __init__.py
- [ ] Update imports
- [ ] Verify with tests

---

### [ ] 1.3 PurposeFieldDetector → Separate Detection/Classification
**Confidence: 88%** | **Effort: 3h** | **Risk: Low-Medium**
```
src/core/purpose_field.py (368 lines, out=74)
  ↓ Split into:
  src/core/purpose/constants.py
  src/core/purpose/purpose_classifier.py
  src/core/purpose/field_mapper.py
  src/core/purpose/detector.py
```
- [ ] Audit enum usage
- [ ] Extract constants module
- [ ] Extract PurposeClassifier
- [ ] Extract FieldMapper
- [ ] Simplify detector
- [ ] Update package structure
- [ ] Verify

---

### [ ] 1.4 create_unified_output → Builder Pattern
**Confidence: 95%** | **Effort: 2h** | **Risk: Low**
```
src/core/output_factory.py (147 lines, out=63)
  ↓ Refactor to:
  UnifiedOutputBuilder class with fluent API
```
- [ ] Analyze function structure
- [ ] Create UnifiedOutputBuilder class
- [ ] Extract section builders
- [ ] Create factory function
- [ ] Update callers
- [ ] Verify output unchanged

---

### [ ] 1.5 AntimatterEvaluator → Strategy Pattern
**Confidence: 87%** | **Effort: 3h** | **Risk: Medium**
```
src/core/antimatter_evaluator.py (356 lines, out=59)
  ↓ Split into:
  src/core/evaluators/dead_code.py
  src/core/evaluators/unused_imports.py
  src/core/evaluators/unreachable.py
  src/core/evaluators/registry.py
```
- [ ] Identify evaluation types
- [ ] Create Evaluator interface
- [ ] Extract DeadCodeEvaluator
- [ ] Extract UnusedImportEvaluator
- [ ] Extract UnreachableCodeEvaluator
- [ ] Create EvaluatorRegistry
- [ ] Wire up in main
- [ ] Verify all issues detected

---

## Priority 2: High (Confidence 80-90%)

### [ ] 2.1 run_proof → Pipeline Pattern
**Confidence: 85%** | **Effort: 4h** | **Risk: Medium**
```
src/tools/prove.py (544 lines, out=56)
```
- [ ] Create ProofOrchestrator class
- [ ] Extract ProofStage classes
- [ ] Implement pipeline pattern
- [ ] Add stage-level error handling

---

### [ ] 2.2 BoundaryMapper → Facade Pattern
**Confidence: 83%** | **Effort: 4h** | **Risk: Medium**
```
src/tools/boundary_mapper.py (650 lines, out=55)
```
- [ ] Extract ModuleBoundaryMapper
- [ ] Extract ClassBoundaryMapper
- [ ] Extract FunctionBoundaryMapper
- [ ] Create BoundaryMapperFacade

---

### [ ] 2.3 DimensionEnricher → Pipeline Pattern
**Confidence: 82%** | **Effort: 3h** | **Risk: Low**
```
src/core/dimension_enricher.py (553 lines, out=54)
```
- [ ] Create DimensionEnricherPipeline
- [ ] Extract per-dimension enrichers
- [ ] Allow selective enrichment

---

### [ ] 2.4 AtomExtractor → Composite Pattern
**Confidence: 80%** | **Effort: 5h** | **Risk: Medium**
```
src/core/atom_extractor.py (626 lines, out=53)
```
- [ ] Create AtomExtractor base class
- [ ] Extract FunctionAtomExtractor
- [ ] Extract ClassAtomExtractor
- [ ] Extract ModuleAtomExtractor
- [ ] Create CompositeAtomExtractor

---

### [ ] 2.5 ConversationFlowAnalyzer → Extract Components
**Confidence: 80%** | **Effort: 3h** | **Risk: Low**
```
src/tools/conversation_mapper.py (526 lines, out=43)
```
- [ ] Extract ConversationParser
- [ ] Extract FlowDetector
- [ ] Extract ConversationReporter

---

## Priority 3: Medium (Confidence 70-85%)

### [ ] 3.1 ChatExtractor Cleanup
**Confidence: 78%** | **Effort: 2h**
```
src/tools/extract_chat_insights.py (559 lines, out=40)
```

### [ ] 3.2 LLMDiscoveryPipeline Modularization
**Confidence: 75%** | **Effort: 3h**
```
src/core/llm_discovery.py (507 lines, out=44)
```

### [ ] 3.3 SmartExtractor Simplification
**Confidence: 75%** | **Effort: 2h**

### [ ] 3.4 CompleteExtractor Decomposition
**Confidence: 72%** | **Effort: 2h**

### [ ] 3.5 PythonASTParser Modularization
**Confidence: 70%** | **Effort: 3h**

### [ ] 3.6 ExecutionFlowDetector Cleanup
**Confidence: 70%** | **Effort: 3h**

---

## Execution Schedule

| Phase | Tasks | Time | Days |
|-------|-------|------|------|
| 1. Quick Wins | 1.4, 1.3 | 5h | Day 1 |
| 2. Core | 1.1, 1.2, 1.5 | 11h | Days 2-3 |
| 3. Supporting | 2.1, 2.2, 2.4 | 13h | Days 4-5 |
| 4. Cleanup | Remaining | 11h | Day 6 |

**Total Estimated Effort: 40-50 hours**

---

## Verification After Each Task

```bash
# 1. Run analysis
python3 cli.py analyze src/ --output output/post_refactor

# 2. Check coupling reduction
python3 -c "
import json
from collections import Counter
data = json.loads(open('output/post_refactor/unified_analysis.json').read())
edges = [e for e in data['edges'] if e.get('edge_type','').upper() != 'CONTAINS']
out_deg = Counter(e['source'] for e in edges)
hotspots = sum(1 for d in out_deg.values() if d > 19.6)
print(f'Hotspots: {hotspots} (target: <25)')
print(f'Max out-degree: {max(out_deg.values())} (target: <50)')
"

# 3. Run tests
python3 -m pytest tests/ -v

# 4. Commit
git add -A && git commit -m "refactor: [component name] - reduce coupling"
```

---

## Target Metrics

| Metric | Before | After |
|--------|--------|-------|
| Max out-degree | 247 | < 50 |
| Hotspots | 69 | < 25 |
| Avg out-degree | 9.82 | < 8.0 |

---

*Generated: 2025-12-28*
