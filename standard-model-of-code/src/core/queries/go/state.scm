; =============================================================================
; GO STATE QUERY (D5_STATE)
; Detects stateful vs stateless patterns
; =============================================================================

; =============================================================================
; STATEFUL PATTERNS
; =============================================================================

; Struct fields
(field_declaration) @state.stateful.struct_field

; Pointer receivers (can modify state)
(method_declaration
  receiver: (parameter_list
    (parameter_declaration
      type: (pointer_type)))
  @state.stateful.pointer_receiver)

; Global variables
(var_declaration
  (var_spec)) @state.stateful.global_var

; Package-level state
(short_var_declaration) @state.stateful.short_var

; Mutex/sync patterns
(call_expression
  function: (selector_expression
    field: (field_identifier) @_method
    (#match? @_method "^(Lock|Unlock|RLock|RUnlock)$"))
  @state.stateful.mutex)

; Channel operations (stateful communication)
(send_statement) @state.stateful.channel_send
(receive_statement) @state.stateful.channel_receive

; Map/slice mutations
(index_expression) @state.stateful.index_access

; Increment/decrement
(inc_statement) @state.stateful.increment
(dec_statement) @state.stateful.decrement

; Assignment
(assignment_statement) @state.stateful.assignment

; =============================================================================
; STATELESS PATTERNS
; =============================================================================

; Value receivers (cannot modify original)
(method_declaration
  receiver: (parameter_list
    (parameter_declaration
      type: (type_identifier)))
  @state.stateless.value_receiver)

; Const declarations
(const_declaration) @state.stateless.const

; Type declarations
(type_declaration) @state.stateless.type

; Pure function declarations (no receiver)
(function_declaration) @state.stateless.function
