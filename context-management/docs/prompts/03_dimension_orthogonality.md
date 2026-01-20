> **EPISTEMIC STANCE**: This prompt validates a MAP, not the territory. Canonical sets (200 atoms, 33 roles, 8 dimensions) are *working sets*, not claims of totality. Finding gaps is expected and valuable. Unknown is first-class. All claims are postulates with validation obligations.

---

# MEGAPROMPT 03: DIMENSION ORTHOGONALITY & BOUNDARY CASES

## Context
Standard Code classifies every code entity along 8 dimensions:
1. **WHAT** (200 atom types)
2. **LAYER** (Interface, Application, Core, Infrastructure, Test)
3. **ROLE** (33 canonical roles)
4. **BOUNDARY** (Internal, Input, I/O, Output)
5. **STATE** (Stateful, Stateless)
6. **EFFECT** (Pure, Read, Write, ReadModify)
7. **ACTIVATION** (Direct, Event, Time)
8. **LIFETIME** (Transient, Session, Global)

The claim is that these dimensions are **orthogonal** (independent) and **mutually exclusive** (each entity has exactly one value per dimension).

## Your Task
Rigorously test orthogonality and identify boundary cases.

## Instructions

1. **For Each Dimension**:
   - Define each value **precisely** (necessary and sufficient conditions)
   - List 3-5 **boundary cases** (entities that are hard to classify)
   - Specify **constraints** (e.g., "If EFFECT=Pure, then STATE must be Stateless")

2. **Orthogonality Test**:
   - For every pair of dimensions (28 pairs), ask:
     - Can every combination of values exist? (e.g., Pure + Stateful?)
     - If not, document the constraint.

3. **"Unknown" Policy**:
   - Define when "Unknown" is a valid value
   - Distinguish "Unknown" (not yet classified) from "N/A" (dimension doesn't apply)
   - Propose rules to prevent "Unknown" from becoming a catch-all

4. **Mutual Exclusivity Violations**:
   - Find cases where an entity could legitimately have 2 values (e.g., both "Direct" and "Event" activation)
   - Propose either: (a) new values, (b) primary/secondary scheme, or (c) redefine dimensions

## Expected Output
- Dimension definition table with precise boundaries
- Orthogonality matrix (28 pairs)
- Boundary case examples
- "Unknown" policy document
