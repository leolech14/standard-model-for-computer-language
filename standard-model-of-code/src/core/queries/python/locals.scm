; Python Locals Query (Scope Analysis)
; Based on tree-sitter-highlight algorithm and PEP 227
;
; IMPORTANT: Python class bodies are NOT lexical scopes for methods (PEP 227)
; Class scope is only visible within the class body, not in nested functions/methods.
;
; Captures:
;   @local.scope - Introduces a new scope
;   @local.definition - Defines a name in current scope
;   @local.definition-value - The value/initializer of a definition
;   @local.reference - References a name

; Module is the root scope
(module) @local.scope

; Function definitions create scopes
; NOTE: Parameters and body share the function scope
(function_definition) @local.scope

; Class definitions create scopes
; BUT: inherits=false because class scope doesn't propagate to methods
(class_definition) @local.scope
; set! local.scope-inherits false  ; This would be set via property

; Comprehensions create their own scopes (Python 3+)
(list_comprehension) @local.scope
(dictionary_comprehension) @local.scope
(set_comprehension) @local.scope
(generator_expression) @local.scope

; Lambda creates a scope
(lambda) @local.scope

; === DEFINITIONS ===

; Function parameter definitions
(function_definition
  parameters: (parameters
    (identifier) @local.definition))

; Parameters with default values
(function_definition
  parameters: (parameters
    (default_parameter
      name: (identifier) @local.definition
      value: (_) @local.definition-value)))

; *args and **kwargs
(function_definition
  parameters: (parameters
    (list_splat_pattern
      (identifier) @local.definition)))
(function_definition
  parameters: (parameters
    (dictionary_splat_pattern
      (identifier) @local.definition)))

; Typed parameters
(function_definition
  parameters: (parameters
    (typed_parameter
      (identifier) @local.definition)))

; Variable assignments
(assignment
  left: (identifier) @local.definition
  right: (_) @local.definition-value)

; Pattern assignment (tuple unpacking)
(assignment
  left: (pattern_list
    (identifier) @local.definition))
(assignment
  left: (tuple_pattern
    (identifier) @local.definition))

; For loop variables
(for_statement
  left: (identifier) @local.definition)
(for_statement
  left: (pattern_list
    (identifier) @local.definition))
(for_statement
  left: (tuple_pattern
    (identifier) @local.definition))

; Comprehension variables
(list_comprehension
  (for_in_clause
    left: (identifier) @local.definition))
(generator_expression
  (for_in_clause
    left: (identifier) @local.definition))

; With statement bindings
(with_statement
  (with_clause
    (with_item
      value: (as_pattern
        alias: (as_pattern_target
          (identifier) @local.definition)))))

; Exception handlers
(except_clause
  (as_pattern
    alias: (as_pattern_target
      (identifier) @local.definition)))

; Import statements (creates definitions)
(import_statement
  name: (dotted_name
    (identifier) @local.definition))
(import_from_statement
  name: (dotted_name
    (identifier) @local.definition))
(aliased_import
  alias: (identifier) @local.definition)

; Named expression (walrus operator :=)
(named_expression
  name: (identifier) @local.definition
  value: (_) @local.definition-value)

; Class attribute assignment (inside class body)
(class_definition
  body: (block
    (expression_statement
      (assignment
        left: (identifier) @local.definition))))

; === REFERENCES ===

; Any identifier used in an expression context is a reference
(identifier) @local.reference
