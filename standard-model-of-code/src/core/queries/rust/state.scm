; =============================================================================
; RUST STATE QUERY (D5_STATE)
; Detects stateful vs stateless patterns
; =============================================================================

; =============================================================================
; STATEFUL PATTERNS
; =============================================================================

; Mutable references (&mut)
(reference_type
  (mutable_specifier)
  @state.stateful.mut_ref)

; Mutable bindings (let mut)
(let_declaration
  (mutable_specifier)
  @state.stateful.mut_binding)

; Self with mutable reference (&mut self)
(self_parameter
  (mutable_specifier)
  @state.stateful.mut_self)

; Struct fields
(field_declaration) @state.stateful.struct_field

; Static mut
(static_item
  (mutable_specifier)
  @state.stateful.static_mut)

; Cell/RefCell patterns (interior mutability)
(call_expression
  function: (scoped_identifier
    name: (type_identifier) @_type
    (#match? @_type "^(Cell|RefCell|Mutex|RwLock|AtomicUsize|AtomicBool)$"))
  @state.stateful.interior_mut)

; Arc/Rc with interior mutability
(generic_type
  type: (type_identifier) @_type
  (#match? @_type "^(Arc|Rc)$")
  type_arguments: (type_arguments
    (generic_type
      type: (type_identifier) @_inner
      (#match? @_inner "^(Mutex|RwLock|RefCell)$")))
  @state.stateful.shared_mut)

; Assignment expressions
(assignment_expression) @state.stateful.assignment
(compound_assignment_expr) @state.stateful.compound_assignment

; =============================================================================
; STATELESS PATTERNS
; =============================================================================

; Immutable bindings
(let_declaration
  pattern: (identifier)
  @state.stateless.immutable_binding)

; Const items
(const_item) @state.stateless.const

; Immutable self (&self)
(self_parameter
  @state.stateless.immutable_self)

; Pure functions (no self)
(function_item
  parameters: (parameters)
  @state.stateless.pure_function)

; Type definitions
(type_item) @state.stateless.type_alias
(struct_item) @state.stateless.struct_def
(enum_item) @state.stateless.enum_def
