> **EPISTEMIC STANCE**: This prompt validates a MAP, not the territory. Canonical sets (167 atoms, 33 roles, 8 dimensions) are *working sets*, not claims of totality. Finding gaps is expected and valuable. Unknown is first-class. All claims are postulates with validation obligations.

---

# MEGAPROMPT 10: CORRECTNESS DEFINITIONS

## Context
What does it mean for the Standard Code knowledge graph to be "correct"?

## Your Task
Define correctness across multiple dimensions.

## Instructions

1. **Structural Correctness**:
   - All `calls` edges are real call relationships (no false positives)
   - All `imports` edges are real import relationships
   - All `contains` edges are valid containment
   - **Metric**: Precision/Recall vs. ground truth call graph

2. **Semantic Correctness**:
   - Role assignments are accurate (match human judgment)
   - Layer assignments are accurate
   - **Metric**: Accuracy vs. human-labeled gold set

3. **Epistemic Correctness**:
   - Confidence scores are calibrated
   - Provenance is traceable
   - **Metric**: ECE (Expected Calibration Error), audit pass rate

4. **Completeness**:
   - All entities in source code are represented
   - All relationships are captured
   - **Metric**: Coverage %

5. **Consistency**:
   - No logical contradictions (e.g., X is_a Repository AND is_a Controller)
   - All constraints satisfied
   - **Metric**: Constraint violation count

6. **Minimum Thresholds** (propose for each):
   - Structural: Precision ≥ X%, Recall ≥ Y%
   - Semantic: Accuracy ≥ Z%
   - Epistemic: ECE ≤ W%

## Expected Output
- Correctness taxonomy
- Metric definitions
- Minimum acceptable thresholds
- Test protocols for each
