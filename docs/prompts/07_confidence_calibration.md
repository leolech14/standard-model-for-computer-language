> **EPISTEMIC STANCE**: This prompt validates a MAP, not the territory. Canonical sets (167 atoms, 33 roles, 8 dimensions) are *working sets*, not claims of totality. Finding gaps is expected and valuable. Unknown is first-class. All claims are postulates with validation obligations.

---

# MEGAPROMPT 07: CONFIDENCE & CALIBRATION SYSTEM

## Context
Standard Code assigns confidence scores to classifications (0-100%).
The claim is that these confidence scores are **calibrated** (when we say 90%, we are right 90% of the time).

## Your Task
Design a calibration and epistemics system.

## Instructions

1. **Define What Confidence Means**:
   - Probability of correctness? Agreement with gold standard? Model uncertainty?
   - Choose one interpretation and document it

2. **Confidence Computation Pipeline**:
   - Step 1: Rule-based confidence (pattern match strength)
   - Step 2: Model-based confidence (ML classifier probability)
   - Step 3: Cross-check adjustment (if call graph agrees, boost; if conflicts, reduce)
   - Step 4: Final aggregation

3. **Calibration Test**:
   - Take all classifications with confidence 85-90%
   - Measure actual accuracy against gold set
   - Plot: Expected vs. Actual (should be diagonal)
   - Compute ECE (Expected Calibration Error)

4. **Recalibration**:
   - If miscalibrated, apply Platt scaling or isotonic regression
   - Document recalibration procedure

5. **Human Review Escalation**:
   - Threshold for automatic human review (e.g., <60% confidence)
   - Priority queue by impact (high-connectivity nodes first)

6. **Confidence Evolution**:
   - As more code is analyzed, do confidence weights need re-tuning?
   - Online learning? Periodic batch retraining?

## Expected Output
- Confidence definition document
- Computation pipeline specification
- Calibration protocol
- Escalation policy
- Evolution/retraining schedule
