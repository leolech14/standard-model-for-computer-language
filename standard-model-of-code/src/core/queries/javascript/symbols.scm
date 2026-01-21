; JavaScript Symbol Extraction Query
; Extracts functions, classes, methods, and React-specific patterns
;
; Captures:
;   @func.name / @func - Function declarations and expressions
;   @class.name / @class - Class declarations
;   @method.name / @method - Method definitions
;   @arrow.name / @arrow - Arrow functions assigned to variables
;   @hook.name / @hook_call - React hook calls (useXxx pattern)

; Regular function declarations
(function_declaration
  name: (identifier) @func.name) @func

; Arrow functions assigned to variables
(variable_declarator
  name: (identifier) @arrow.name
  value: (arrow_function) @arrow)

; Arrow functions assigned to const (capture the whole statement)
(lexical_declaration
  (variable_declarator
    name: (identifier) @arrow.name
    value: (arrow_function) @arrow))

; Function expressions assigned to variables
(variable_declarator
  name: (identifier) @func.name
  value: (function_expression) @func)

; Class declarations
(class_declaration
  name: (identifier) @class.name) @class

; Class methods
(method_definition
  name: (property_identifier) @method.name) @method

; Object methods (shorthand)
(pair
  key: (property_identifier) @method.name
  value: (function_expression) @method)
(pair
  key: (property_identifier) @method.name
  value: (arrow_function) @method)

; Exported functions
(export_statement
  declaration: (function_declaration
    name: (identifier) @func.name) @func)

; Exported classes
(export_statement
  declaration: (class_declaration
    name: (identifier) @class.name) @class)

; Default export function
(export_statement
  (function_declaration
    name: (identifier) @func.name) @func)

; React hook calls (useXxx pattern)
(call_expression
  function: (identifier) @hook.name
  (#match? @hook.name "^use[A-Z]")) @hook_call

; Async functions
(function_declaration
  "async"
  name: (identifier) @async.name) @async

; Generator functions
(generator_function_declaration
  name: (identifier) @generator.name) @generator

; Object destructuring assignments (for component props pattern)
(variable_declarator
  name: (object_pattern) @destructure
  value: (_))
