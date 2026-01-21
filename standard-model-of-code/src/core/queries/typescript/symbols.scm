; TypeScript Symbol Extraction Query
; Extends JavaScript with type-specific patterns
;
; INHERITANCE: TypeScript inherits from JavaScript
; This file only contains TypeScript-specific additions

; Type alias declarations
(type_alias_declaration
  name: (type_identifier) @type.name) @type

; Interface declarations
(interface_declaration
  name: (type_identifier) @interface.name) @interface

; Enum declarations
(enum_declaration
  name: (identifier) @enum.name) @enum

; Exported type aliases
(export_statement
  declaration: (type_alias_declaration
    name: (type_identifier) @type.name) @type)

; Exported interfaces
(export_statement
  declaration: (interface_declaration
    name: (type_identifier) @interface.name) @interface)

; Exported enums
(export_statement
  declaration: (enum_declaration
    name: (identifier) @enum.name) @enum)

; Namespace/module declarations
(module
  name: (identifier) @namespace.name) @namespace

; Abstract class declarations
(abstract_class_declaration
  name: (identifier) @abstract_class.name) @abstract_class

; Decorator usage (for classes and methods)
(decorator
  (call_expression
    function: (identifier) @decorator.name)) @decorator
(decorator
  (identifier) @decorator.name) @decorator
