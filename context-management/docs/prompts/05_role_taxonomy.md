> **EPISTEMIC STANCE**: This prompt validates a MAP, not the territory. Canonical sets (200 atoms, 33 roles, 8 dimensions) are *working sets*, not claims of totality. Finding gaps is expected and valuable. Unknown is first-class. All claims are postulates with validation obligations.

---

# MEGAPROMPT 05: ROLE TAXONOMY VALIDATION

## Context
Standard Code defines 33 canonical roles (Query, Command, Repository, etc.).
Roles are assigned based on name patterns, decorators, call graph position, and LLM inference.

## Your Task
Design a human annotation study to validate role taxonomy.

## Instructions

1. **Study Design**:
   - **Sample**: 200 functions from 10 diverse repos (20 each)
   - **Annotators**: 3 independent human experts
   - **Task**: Assign one role to each function (or "Unknown")

2. **Annotation Guidelines** (create outline):
   - Role definitions with examples
   - Decision tree for ambiguous cases
   - "Unknown" criteria

3. **Metrics**:
   - **Inter-Annotator Agreement**: Fleiss' kappa
   - **Confusion Matrix**: Which role pairs are confused most?
   - **Classifier Agreement**: Human vs. Standard Code classifier

4. **Post-Study Actions**:
   - Merge confused role pairs OR add distinguishing features
   - Revise role definitions based on annotator feedback
   - Update classifier training data

5. **Backward Compatibility**:
   - If we merge roles A and B into AB, how do old analyses migrate?
   - Version scheme for role taxonomy

## Expected Output
- Annotation guideline outline
- Study protocol document
- Analysis plan with metrics
- Migration protocol
