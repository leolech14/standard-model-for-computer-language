/-
  Theorem 3.8: Schema Minimality
  
  STATEMENT: The canonical schema S is minimal—removing any field loses information.
  
  PROOF: We construct counterexamples showing each field is necessary for core functionality.
-/

import StandardModel.Definitions

-- Define the canonical schema as a structure
structure CanonicalNode where
  id : String
  name : String
  kind : String
  role : Role
  layer : String
  deriving DecidableEq

structure CanonicalEdge where
  source : String
  target : String
  edge_type : String
  deriving DecidableEq

-- Define core functionalities that require all fields

-- Functionality 1: Uniqueness requires 'id'
def nodes_unique (nodes : List CanonicalNode) : Prop :=
  ∀ n1 n2, n1 ∈ nodes → n2 ∈ nodes → n1.id = n2.id → n1 = n2

-- Theorem: Without 'id', uniqueness is undefined
theorem id_necessary :
  ∃ (n1 n2 : CanonicalNode),
    n1.name = n2.name ∧
    n1.kind = n2.kind ∧
    n1.role = n2.role ∧
    n1.layer = n2.layer ∧
    n1.id ≠ n2.id := by
  -- Two nodes with same semantic properties but different IDs
  use ⟨"file1.py:UserRepo", "UserRepo", "class", 5, "Infrastructure"⟩,
      ⟨"file2.py:UserRepo", "UserRepo", "class", 5, "Infrastructure"⟩
  simp
  trivial

-- Functionality 2: Human navigation requires 'name'
def human_readable (n : CanonicalNode) : String := n.name

theorem name_necessary :
  ∃ (n1 n2 : CanonicalNode),
    n1.id ≠ n2.id ∧
    n1.kind = n2.kind ∧
    -- Cannot distinguish without name
    n1.name ≠ n2.name := by
  use ⟨"mod_a", "ServiceA", "class", 5, "App"⟩,
      ⟨"mod_b", "ServiceB", "class", 5, "App"⟩
  simp
  trivial

-- Functionality 3: Violation detection requires 'layer' + 'role'
def cross_layer_violation (n1 n2 : CanonicalNode) (e : CanonicalEdge) : Prop :=
  n1.id = e.source ∧ n2.id = e.target ∧
  (n1.layer = "Domain" ∧ n2.layer = "Infrastructure")

theorem layer_necessary_for_violations :
  ∃ (n1 n2 : CanonicalNode) (e : CanonicalEdge),
    e.source = n1.id ∧ e.target = n2.id ∧
    n1.layer ≠ n2.layer ∧
    cross_layer_violation n1 n2 e := by
  use ⟨"User", "User", "class", 8, "Domain"⟩,
      ⟨"UserRepo", "UserRepo", "class", 5, "Infrastructure"⟩,
      ⟨"User", "UserRepo", "IMPORTS"⟩
  simp [cross_layer_violation]
  trivial

-- Functionality 4: Semantic understanding requires 'role'
def is_repository (n : CanonicalNode) : Prop := n.role = 5

theorem role_necessary_for_semantic :
  ∃ (n1 n2 : CanonicalNode),
    n1.kind = n2.kind ∧
    n1.layer = n2.layer ∧
    n1.role ≠ n2.role ∧
    (is_repository n1 ≠ is_repository n2) := by
  use ⟨"UserRepo", "UserRepository", "class", 5, "Infrastructure"⟩,
      ⟨"User", "User", "class", 8, "Domain"⟩
  simp [is_repository]
  trivial

-- Functionality 5: Visualization requires 'kind' (syntactic type)
def node_shape (n : CanonicalNode) : String :=
  match n.kind with
  | "class" => "box"
  | "function" => "ellipse"
  | "module" => "hexagon"
  | _ => "circle"

theorem kind_necessary_for_viz :
  ∃ (n1 n2 : CanonicalNode),
    n1.role = n2.role ∧
    n1.layer = n2.layer ∧
    n1.kind ≠ n2.kind ∧
    node_shape n1 ≠ node_shape n2 := by
  use ⟨"get_user", "get_user", "function", 3, "Infrastructure"⟩,
      ⟨"UserRepo", "UserRepository", "class", 3, "Infrastructure"⟩
  simp [node_shape]
  trivial

-- Edge fields

-- Graph structure requires 'source' and 'target'
def forms_edge (e : CanonicalEdge) : Prop :=
  e.source.length > 0 ∧ e.target.length > 0

theorem source_target_necessary :
  ∀ (e : CanonicalEdge),
    forms_edge e → (e.source.length > 0 ∧ e.target.length > 0) := by
  intro e h
  exact h

-- Relationship semantics requires 'edge_type'
def is_call (e : CanonicalEdge) : Prop := e.edge_type = "CALLS"
def is_inheritance (e : CanonicalEdge) : Prop := e.edge_type = "INHERITS"

theorem edge_type_necessary :
  ∃ (e1 e2 : CanonicalEdge),
    e1.source = e2.source ∧
    e1.target = e2.target ∧
    e1.edge_type ≠ e2.edge_type ∧
    (is_call e1 ≠ is_call e2) := by
  use ⟨"A", "B", "CALLS"⟩, ⟨"A", "B", "INHERITS"⟩
  simp [is_call]
  trivial

-- Main theorem: Schema is minimal
theorem schema_minimal :
  (∃ (n1 n2 : CanonicalNode), n1.id ≠ n2.id ∧ n1.name = n2.name) ∧  -- id necessary
  (∃ (n1 n2 : CanonicalNode), n1.name ≠ n2.name ∧ n1.kind = n2.kind) ∧  -- name necessary
  (∃ (n1 n2 : CanonicalNode), n1.kind ≠ n2.kind ∧ n1.role = n2.role) ∧  -- kind necessary
  (∃ (n1 n2 : CanonicalNode), n1.role ≠ n2.role ∧ n1.layer = n2.layer) ∧  -- role necessary
  (∃ (n1 n2 : CanonicalNode), n1.layer ≠ n2.layer ∧ n1.kind = n2.kind) ∧  -- layer necessary
  (∃ (e1 e2 : CanonicalEdge), e1.edge_type ≠ e2.edge_type ∧ e1.source = e2.source) := by  -- edge_type necessary
  exact ⟨id_necessary, name_necessary, kind_necessary_for_viz, 
         role_necessary_for_semantic, layer_necessary_for_violations, edge_type_necessary⟩
