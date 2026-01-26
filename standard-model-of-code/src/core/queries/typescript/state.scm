; =============================================================================
; TYPESCRIPT STATE QUERY (D5_STATE)
; Detects stateful vs stateless patterns
; =============================================================================

; =============================================================================
; STATEFUL PATTERNS
; =============================================================================

; Class properties (instance state)
(public_field_definition) @state.stateful.property
(private_field_definition) @state.stateful.private_property

; Property assignment in constructor
(assignment_expression
  left: (member_expression
    object: (this) @_this)
  @state.stateful.this_assignment)

; useState hook (React)
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useState")
  @state.stateful.use_state)

; useReducer hook (React)
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useReducer")
  @state.stateful.use_reducer)

; useRef hook (React - mutable ref)
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useRef")
  @state.stateful.use_ref)

; Class with constructor
(class_declaration
  body: (class_body
    (method_definition
      name: (property_identifier) @_name
      (#eq? @_name "constructor")))
  @state.stateful.class_with_constructor)

; Let/var declarations (mutable)
(lexical_declaration
  kind: "let"
  @state.stateful.let)

(variable_declaration
  @state.stateful.var)

; Mutation operators
(update_expression) @state.stateful.update
(augmented_assignment_expression) @state.stateful.augmented_assignment

; =============================================================================
; STATELESS PATTERNS
; =============================================================================

; Const declarations (immutable)
(lexical_declaration
  kind: "const"
  @state.stateless.const)

; Arrow functions without this
(arrow_function
  @state.stateless.arrow)

; Pure function declarations
(function_declaration
  @state.stateless.function)

; Type/interface declarations (no runtime state)
(type_alias_declaration) @state.stateless.type
(interface_declaration) @state.stateless.interface
