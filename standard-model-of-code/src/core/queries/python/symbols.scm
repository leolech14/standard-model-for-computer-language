; Python Symbol Extraction Query
; Extracts functions, classes, methods, and other named symbols
;
; Captures:
;   @func.name / @func - Function definitions
;   @class.name / @class - Class definitions
;   @method.name / @method - Method definitions (inside classes)
;   @async.name / @async - Async function definitions
;   @decorator - Decorator usage
;   @lambda - Lambda expressions

; Regular function definitions
(function_definition
  name: (identifier) @func.name) @func

; Async function definitions
(function_definition
  "async"
  name: (identifier) @async.name) @async

; Class definitions
(class_definition
  name: (identifier) @class.name) @class

; Decorated functions (capture decorator separately)
(decorated_definition
  (decorator) @decorator
  definition: (function_definition
    name: (identifier) @func.name) @func)

; Decorated classes
(decorated_definition
  (decorator) @decorator
  definition: (class_definition
    name: (identifier) @class.name) @class)

; Lambda expressions (when assigned to variables)
(assignment
  left: (identifier) @lambda.name
  right: (lambda) @lambda)

; Global variable assignments at module level
(module
  (expression_statement
    (assignment
      left: (identifier) @global.name) @global))

; Type alias assignments (Python 3.12+)
(type_alias_statement
  name: (type) @type_alias.name) @type_alias
