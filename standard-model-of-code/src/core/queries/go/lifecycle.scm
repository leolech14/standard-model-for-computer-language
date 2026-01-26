; =============================================================================
; GO LIFECYCLE QUERY (D7_LIFECYCLE)
; Detects lifecycle phases: Create | Use | Destroy
; =============================================================================

; =============================================================================
; CREATE PHASE
; =============================================================================

; Constructor functions (New* pattern)
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^New")
  @lifecycle.create.constructor)

; Factory functions
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^(Create|Build|Make|Init|Setup|Open|Connect)")
  @lifecycle.create.factory)

; init() function
(function_declaration
  name: (identifier) @_name
  (#eq? @_name "init")
  @lifecycle.create.init)

; Struct literal creation
(composite_literal) @lifecycle.create.composite_literal

; make() calls
(call_expression
  function: (identifier) @_func
  (#eq? @_func "make")
  @lifecycle.create.make)

; new() calls
(call_expression
  function: (identifier) @_func
  (#eq? @_func "new")
  @lifecycle.create.new)

; =============================================================================
; USE PHASE
; =============================================================================

; Regular methods (not create/destroy)
(method_declaration
  name: (field_identifier) @_name
  (#not-match? @_name "^(New|Create|Build|Init|Close|Destroy|Shutdown|Stop|Release|Dispose|Cleanup)")
  @lifecycle.use.method)

; Regular functions
(function_declaration
  name: (identifier) @_name
  (#not-match? @_name "^(New|Create|Build|Init|init|Close|Destroy|Shutdown|Stop|Release|Dispose|Cleanup)")
  @lifecycle.use.function)

; =============================================================================
; DESTROY PHASE
; =============================================================================

; Close methods/functions
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^(Close|Destroy|Shutdown|Stop|Release|Dispose|Cleanup|Teardown)")
  @lifecycle.destroy.destructor)

(method_declaration
  name: (field_identifier) @_name
  (#match? @_name "^(Close|Destroy|Shutdown|Stop|Release|Dispose|Cleanup)")
  @lifecycle.destroy.destructor)

; defer cleanup calls
(defer_statement
  (call_expression
    function: (selector_expression
      field: (field_identifier) @_method
      (#match? @_method "^(Close|Release|Unlock|Done|Cancel)$")))
  @lifecycle.destroy.defer_cleanup)

; Context cancellation
(call_expression
  function: (identifier) @_func
  (#eq? @_func "cancel")
  @lifecycle.destroy.context_cancel)

; Done channel patterns
(call_expression
  function: (selector_expression
    field: (field_identifier) @_method
    (#eq? @_method "Done"))
  @lifecycle.destroy.done)
