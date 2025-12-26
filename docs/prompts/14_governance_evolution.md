# MEGAPROMPT 14: GOVERNANCE & EVOLUTION PROTOCOL

## Context
Standard Code is a living theory. Atoms, roles, and dimensions will evolve as we learn more.

## Your Task
Design a governance and evolution process.

## Instructions

1. **Versioning Scheme**:
   - Schema version: `2.0.0` (MAJOR.MINOR.PATCH)
   - MAJOR: Breaking changes (atom removed, role redefined)
   - MINOR: Additive changes (new atom, new dimension value)
   - PATCH: Bug fixes (typo in definition)

2. **Change Proposal Process**:
   - RFC (Request for Comments) template
   - Evidence required for change (data, annotation results, etc.)
   - Approval criteria (consensus? empirical threshold?)

3. **Migration Rules**:
   - If atom A is removed, all A classifications become Unknown? or mapped to B?
   - If role X is split into X1 and X2, how is historical data updated?
   - Provide migration scripts or rules

4. **Backward Compatibility**:
   - Analysis outputs must declare schema version
   - Tools must handle multiple versions gracefully
   - Deprecation warnings before removal

5. **Scientific Log**:
   - Document: "We hypothesized X. We tested by Y. Result was Z. Decision: ..."
   - Make uncertainty explicit: "ROLE=33 is our current best model, not proven truth"

6. **Communication**:
   - CHANGELOG.md for each version
   - Uncertainty disclosure in documentation
   - User-facing impact summary

## Expected Output
- Version scheme document
- RFC template
- Migration protocol
- Compatibility policy
- Scientific log template
