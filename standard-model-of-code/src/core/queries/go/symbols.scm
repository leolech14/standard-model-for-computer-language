; Go Symbol Extraction Query
; Extracts functions, methods, structs, interfaces
;
; Captures:
;   @func.name / @func - Function declarations
;   @method.name / @method - Method declarations
;   @struct.name / @struct - Struct type declarations
;   @interface.name / @interface - Interface type declarations
;   @type.name / @type - Type alias declarations

; Function declarations
(function_declaration
  name: (identifier) @func.name) @func

; Method declarations (with receiver)
(method_declaration
  name: (field_identifier) @method.name) @method

; Struct type declarations
(type_declaration
  (type_spec
    name: (type_identifier) @struct.name
    type: (struct_type))) @struct

; Interface type declarations
(type_declaration
  (type_spec
    name: (type_identifier) @interface.name
    type: (interface_type))) @interface

; Type alias declarations
(type_declaration
  (type_spec
    name: (type_identifier) @type.name)) @type

; Anonymous functions (func literals)
(func_literal) @func

; Const declarations
(const_declaration
  (const_spec
    name: (identifier) @const.name)) @const

; Var declarations
(var_declaration
  (var_spec
    name: (identifier) @var.name)) @var

; Package declarations
(package_clause
  (package_identifier) @package.name) @package
