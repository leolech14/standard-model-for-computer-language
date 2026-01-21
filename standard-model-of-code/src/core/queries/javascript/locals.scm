; JavaScript Locals Query (Scope Analysis)
; Based on tree-sitter-highlight algorithm
;
; IMPORTANT: JavaScript has different scoping rules:
;   - var: function-scoped, hoisted
;   - let/const: block-scoped, TDZ (Temporal Dead Zone)
;   - function declarations: hoisted with value
;
; Captures:
;   @local.scope - Introduces a new scope
;   @local.definition - Defines a name in current scope
;   @local.definition-value - The value/initializer of a definition
;   @local.reference - References a name

; Program (module) is the root scope
(program) @local.scope

; Function scopes
(function_declaration) @local.scope
(function_expression) @local.scope
(arrow_function) @local.scope
(generator_function_declaration) @local.scope
(method_definition) @local.scope

; Class scope
(class_declaration) @local.scope
(class_expression) @local.scope

; Block scopes (for let/const)
; NOTE: Only affects let/const, not var
(statement_block) @local.scope

; For loop scopes
(for_statement) @local.scope
(for_in_statement) @local.scope

; Catch clause scope
(catch_clause) @local.scope

; Switch case scope (for let/const)
(switch_case) @local.scope

; === DEFINITIONS ===

; Function parameters
(function_declaration
  parameters: (formal_parameters
    (identifier) @local.definition))
(function_expression
  parameters: (formal_parameters
    (identifier) @local.definition))
(arrow_function
  parameters: (formal_parameters
    (identifier) @local.definition))
(arrow_function
  parameter: (identifier) @local.definition)

; Rest parameters
(rest_pattern
  (identifier) @local.definition)

; Destructuring parameters
(object_pattern
  (shorthand_property_identifier_pattern) @local.definition)
(object_pattern
  (pair_pattern
    value: (identifier) @local.definition))
(array_pattern
  (identifier) @local.definition)

; var declarations (function-scoped, hoisted)
; NOTE: available_after_byte = 0 for var (hoisted)
(variable_declaration
  "var"
  (variable_declarator
    name: (identifier) @local.definition
    value: (_)? @local.definition-value))

; let declarations (block-scoped, TDZ)
; NOTE: available_after_byte = declaration end for TDZ
(lexical_declaration
  "let"
  (variable_declarator
    name: (identifier) @local.definition
    value: (_)? @local.definition-value))

; const declarations (block-scoped, TDZ)
(lexical_declaration
  "const"
  (variable_declarator
    name: (identifier) @local.definition
    value: (_)? @local.definition-value))

; Function declarations (hoisted with value)
; NOTE: available_after_byte = 0 (hoisted)
(function_declaration
  name: (identifier) @local.definition)

; Class declarations
(class_declaration
  name: (identifier) @local.definition)

; For loop variable (let/var)
(for_statement
  (variable_declaration
    (variable_declarator
      name: (identifier) @local.definition)))
(for_statement
  (lexical_declaration
    (variable_declarator
      name: (identifier) @local.definition)))

; For-in/for-of loop variable
(for_in_statement
  left: (identifier) @local.definition)
(for_in_statement
  left: (variable_declaration
    (variable_declarator
      name: (identifier) @local.definition)))

; Catch clause parameter
(catch_clause
  parameter: (identifier) @local.definition)

; Import definitions
(import_specifier
  name: (identifier) @local.definition)
(import_specifier
  alias: (identifier) @local.definition)
(namespace_import
  (identifier) @local.definition)
(import_clause
  (identifier) @local.definition)

; === REFERENCES ===

; Any identifier in expression context
(identifier) @local.reference
