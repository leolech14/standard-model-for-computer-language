; =============================================================================
; RUST LIFECYCLE QUERY (D7_LIFECYCLE)
; Detects lifecycle phases: Create | Use | Destroy
; =============================================================================

; =============================================================================
; CREATE PHASE
; =============================================================================

; new() constructor pattern
(function_item
  name: (identifier) @_name
  (#eq? @_name "new")
  @lifecycle.create.new)

; Builder pattern
(function_item
  name: (identifier) @_name
  (#match? @_name "^(build|builder|create|make|init|setup|open|connect)")
  @lifecycle.create.builder)

; Default trait implementation
(impl_item
  trait: (type_identifier) @_trait
  (#eq? @_trait "Default")
  @lifecycle.create.default)

; From/Into implementations
(impl_item
  trait: (type_identifier) @_trait
  (#match? @_trait "^(From|Into|TryFrom|TryInto)$")
  @lifecycle.create.conversion)

; Struct expressions (instantiation)
(struct_expression) @lifecycle.create.struct_init

; =============================================================================
; USE PHASE
; =============================================================================

; Regular methods (not new/drop/create/close)
(function_item
  name: (identifier) @_name
  (#not-match? @_name "^(new|build|builder|create|make|init|drop|close|shutdown|dispose|cleanup)")
  @lifecycle.use.function)

; Impl methods
(function_signature_item
  name: (identifier) @_name
  (#not-match? @_name "^(new|drop|close)")
  @lifecycle.use.method)

; =============================================================================
; DESTROY PHASE
; =============================================================================

; Drop trait implementation
(impl_item
  trait: (type_identifier) @_trait
  (#eq? @_trait "Drop")
  @lifecycle.destroy.drop)

; drop() function call
(call_expression
  function: (identifier) @_func
  (#eq? @_func "drop")
  @lifecycle.destroy.drop_call)

; Close/shutdown methods
(function_item
  name: (identifier) @_name
  (#match? @_name "^(close|shutdown|dispose|cleanup|release|finish|terminate)")
  @lifecycle.destroy.close)

; Destructor patterns
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(close|shutdown|dispose|abort|cancel)$"))
  @lifecycle.destroy.cleanup_call)

; Take/replace patterns (ownership transfer for cleanup)
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(take|replace)$"))
  @lifecycle.destroy.take)
