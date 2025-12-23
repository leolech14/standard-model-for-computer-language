/-
  Standard Model of Code - Definitions
  
  Core type definitions for the formal proof system.
-/

-- Define the Atom type representing the 167 atoms
inductive Atom : Type where
  | data : Fin 26 → Atom   -- DATA phase atoms
  | logic : Fin 61 → Atom  -- LOGIC phase atoms
  | org : Fin 45 → Atom    -- ORGANIZATION phase atoms
  | exec : Fin 35 → Atom   -- EXECUTION phase atoms
  deriving DecidableEq, Repr

-- Define the Role type (27 canonical roles)
def Role : Type := Fin 27
  deriving DecidableEq, Repr

-- Define RPBL as a 4-dimensional discrete space [1,10]^4
structure RPBL where
  responsibility : Fin 10
  purity : Fin 10
  boundary : Fin 10
  lifecycle : Fin 10
  deriving DecidableEq, Repr

-- Define the complete semantic space
def SemanticSpace : Type := Atom × Role × RPBL
  deriving DecidableEq, Repr

-- Helper: Count atoms in each phase
def atom_count_data : Nat := 26
def atom_count_logic : Nat := 61
def atom_count_org : Nat := 45
def atom_count_exec : Nat := 35
def atom_count_total : Nat := atom_count_data + atom_count_logic + atom_count_org + atom_count_exec

-- Prove total atom count
theorem atom_total_is_167 : atom_count_total = 167 := by
  rfl
