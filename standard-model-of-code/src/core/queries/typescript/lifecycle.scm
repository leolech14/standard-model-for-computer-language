; =============================================================================
; TYPESCRIPT LIFECYCLE QUERY (D7_LIFECYCLE)
; Detects lifecycle phases: Create | Use | Destroy
; =============================================================================

; =============================================================================
; CREATE PHASE
; =============================================================================

; Constructor
(method_definition
  name: (property_identifier) @_name
  (#eq? @_name "constructor")
  @lifecycle.create.constructor)

; Factory functions
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^(create|build|make|init|setup|factory|construct)")
  @lifecycle.create.factory)

; Arrow factory functions
(lexical_declaration
  (variable_declarator
    name: (identifier) @_name
    (#match? @_name "^(create|build|make|init|setup|factory|construct)")
    value: (arrow_function))
  @lifecycle.create.factory)

; React useEffect with empty deps (mount)
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useEffect")
  arguments: (arguments
    (arrow_function)
    (array))
  @lifecycle.create.use_effect_mount)

; ngOnInit (Angular)
(method_definition
  name: (property_identifier) @_name
  (#eq? @_name "ngOnInit")
  @lifecycle.create.ng_init)

; componentDidMount (React class)
(method_definition
  name: (property_identifier) @_name
  (#eq? @_name "componentDidMount")
  @lifecycle.create.component_mount)

; =============================================================================
; USE PHASE
; =============================================================================

; Regular methods (default - use phase)
(method_definition
  name: (property_identifier) @_name
  (#not-match? @_name "^(constructor|ngOnInit|ngOnDestroy|componentDidMount|componentWillUnmount|destroy|dispose|cleanup|close)$")
  @lifecycle.use.method)

; Regular functions
(function_declaration
  name: (identifier) @_name
  (#not-match? @_name "^(create|build|make|init|setup|destroy|dispose|cleanup|close|teardown)")
  @lifecycle.use.function)

; =============================================================================
; DESTROY PHASE
; =============================================================================

; Destructor-like methods
(method_definition
  name: (property_identifier) @_name
  (#match? @_name "^(destroy|dispose|cleanup|close|teardown|shutdown|release)")
  @lifecycle.destroy.destructor)

; ngOnDestroy (Angular)
(method_definition
  name: (property_identifier) @_name
  (#eq? @_name "ngOnDestroy")
  @lifecycle.destroy.ng_destroy)

; componentWillUnmount (React class)
(method_definition
  name: (property_identifier) @_name
  (#eq? @_name "componentWillUnmount")
  @lifecycle.destroy.component_unmount)

; useEffect cleanup function
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useEffect")
  arguments: (arguments
    (arrow_function
      body: (statement_block
        (return_statement
          (arrow_function)))))
  @lifecycle.destroy.use_effect_cleanup)

; Disconnect/unsubscribe patterns
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(disconnect|unsubscribe|removeListener|off|close)$"))
  @lifecycle.destroy.cleanup_call)
