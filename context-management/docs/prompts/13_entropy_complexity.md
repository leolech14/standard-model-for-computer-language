> **EPISTEMIC STANCE**: This prompt validates a MAP, not the territory. Canonical sets (200 atoms, 33 roles, 8 dimensions) are *working sets*, not claims of totality. Finding gaps is expected and valuable. Unknown is first-class. All claims are postulates with validation obligations.

---

# MEGAPROMPT 13: ENTROPY & COMPLEXITY MEASURES

## Context
Standard Code enables measuring complexity at multiple scales:
- L3 (function): How complex is this function?
- L4 (class): How complex is this class?
- L5 (file): How complex is this file?
- L7 (system): How complex is this system?

## Your Task
Define mathematically sound complexity measures.

## Instructions

1. **Entropy Definition**:
   - Shannon entropy over atom type distribution:
     $H(level) = -\sum P(atom_i) \log_2 P(atom_i)$
   - High entropy = diverse atoms = less predictable

2. **Complexity Measures**:
   - **Structural Complexity**: Edge count, depth, cyclomatic
   - **Semantic Complexity**: Role diversity, layer mixing
   - **Cognitive Complexity**: Estimated human effort to understand

3. **Aggregation Across Levels**:
   - L3 complexity → average → L4 complexity
   - L4 complexity → weighted sum → L5 complexity
   - ...and so on

4. **Correlation with Outcomes**:
   - Hypothesis: High entropy correlates with bugs
   - Hypothesis: High complexity correlates with slow pull request reviews
   - Test against historical data (if available)

5. **Actionable Thresholds**:
   - Propose "too complex" thresholds (e.g., "Function entropy > 4.0 = warning")

## Expected Output
- Entropy formula
- Complexity measures per level
- Aggregation rules
- Correlation hypotheses
- Threshold recommendations
