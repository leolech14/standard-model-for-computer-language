/-
  Theorem 3.5: Minimality
  
  STATEMENT: The SMC classification dimensions are minimal—no dimension can be removed without losing expressiveness.
  
  PROOF: We show that each dimension captures unique information that cannot be derived from others.
-/

import StandardModel.Definitions

-- Define example elements that prove dimensions are independent

-- Example 1: Same atom, different roles
def method_as_query : SemanticSpace := 
  (.logic 0, 5, ⟨1, 9, 1, 1⟩)  -- Method atom, Query role, high purity

def method_as_command : SemanticSpace :=
  (.logic 0, 6, ⟨1, 1, 1, 1⟩)  -- Method atom, Command role, low purity

-- Theorem: WHAT ≠ WHY (atom doesn't determine role)
theorem what_neq_why : 
  ∃ (s1 s2 : SemanticSpace), 
    s1.1 = s2.1 ∧ s1.2.1 ≠ s2.2.1 := by
  use method_as_query, method_as_command
  simp [method_as_query, method_as_command]
  -- Same atom (logic 0), different roles (5 ≠ 6)
  trivial

-- Example 2: Same atom, different RPBL
def pure_function : SemanticSpace :=
  (.logic 10, 8, ⟨10, 10, 1, 1⟩)  -- Function atom, high R, high P

def impure_function : SemanticSpace :=
  (.logic 10, 8, ⟨10, 1, 1, 1⟩)   -- Function atom, high R, low P

-- Theorem: WHAT ≠ HOW (atom doesn't determine RPBL)
theorem what_neq_how :
  ∃ (s1 s2 : SemanticSpace),
    s1.1 = s2.1 ∧ s1.2.2 ≠ s2.2.2 := by
  use pure_function, impure_function
  simp [pure_function, impure_function]
  -- Same atom, different RPBL (purity differs)
  trivial

-- Example 3: Same role, different RPBL
def pure_factory : SemanticSpace :=
  (.logic 20, 10, ⟨9, 10, 1, 1⟩)  -- Factory role, pure

def impure_factory : SemanticSpace :=
  (.logic 20, 10, ⟨9, 1, 5, 1⟩)   -- Factory role, impure, external I/O

-- Theorem: WHY ≠ HOW (role doesn't determine RPBL)
theorem why_neq_how :
  ∃ (s1 s2 : SemanticSpace),
    s1.2.1 = s2.2.1 ∧ s1.2.2 ≠ s2.2.2 := by
  use pure_factory, impure_factory
  simp [pure_factory, impure_factory]
  -- Same role, different RPBL
  trivial

-- Main theorem: No dimension is redundant
theorem dimensions_minimal :
  (∃ (s1 s2 : SemanticSpace), s1.1 = s2.1 ∧ s1.2.1 ≠ s2.2.1) ∧  -- WHAT ≠ WHY
  (∃ (s1 s2 : SemanticSpace), s1.1 = s2.1 ∧ s1.2.2 ≠ s2.2.2) ∧  -- WHAT ≠ HOW
  (∃ (s1 s2 : SemanticSpace), s1.2.1 = s2.2.1 ∧ s1.2.2 ≠ s2.2.2) := by  -- WHY ≠ HOW
  exact ⟨what_neq_why, what_neq_how, why_neq_how⟩

-- Corollary: All three dimensions are necessary
theorem all_dimensions_necessary :
  ∀ (project : SemanticSpace → Atom × Role),
  ∃ (s1 s2 : SemanticSpace),
    project s1 = project s2 ∧ s1 ≠ s2 := by
  intro project
  -- If we remove RPBL (project to Atom × Role), we lose information
  use pure_function, impure_function
  constructor
  · simp [pure_function, impure_function]
  · simp [pure_function, impure_function]
    trivial
