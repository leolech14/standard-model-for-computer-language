; =============================================================================
; JAVASCRIPT/TYPESCRIPT IMPORTS QUERY
; Captures import/export statements for cross-file symbol resolution
; =============================================================================

; =============================================================================
; ES6 IMPORTS
; =============================================================================

; Default import: import React from 'react'
(import_statement
  (import_clause
    (identifier) @import.default)
  source: (string) @import.source)

; Named imports: import { useState, useEffect } from 'react'
(import_statement
  (import_clause
    (named_imports
      (import_specifier
        name: (identifier) @import.symbol)))
  source: (string) @import.source_named)

; Named import with alias: import { X as Y } from 'react'
(import_statement
  (import_clause
    (named_imports
      (import_specifier
        name: (identifier) @import.original
        alias: (identifier) @import.alias)))
  source: (string) @import.source_aliased)

; Namespace import: import * as React from 'react'
(import_statement
  (import_clause
    (namespace_import
      (identifier) @import.namespace))
  source: (string) @import.source_namespace)

; Side-effect import: import './styles.css'
(import_statement
  source: (string) @import.side_effect)

; =============================================================================
; COMMONJS IMPORTS
; =============================================================================

; const x = require('module')
(lexical_declaration
  (variable_declarator
    name: (identifier) @import.cjs_name
    value: (call_expression
      function: (identifier) @_require
      (#eq? @_require "require")
      arguments: (arguments
        (string) @import.cjs_source))))

; =============================================================================
; ES6 EXPORTS
; =============================================================================

; Named export: export function foo() {}
(export_statement
  declaration: (function_declaration
    name: (identifier) @export.function))

; Named export: export class Foo {}
(export_statement
  declaration: (class_declaration
    name: (identifier) @export.class))

; Named export: export const foo = ...
(export_statement
  declaration: (lexical_declaration
    (variable_declarator
      name: (identifier) @export.variable)))

; Default export function: export default function foo() {}
(export_statement
  "default"
  declaration: (function_declaration
    name: (identifier) @export.default_function))

; Default export class: export default class Foo {}
(export_statement
  "default"
  declaration: (class_declaration
    name: (identifier) @export.default_class))

; Default export expression: export default X
(export_statement
  "default"
  value: (identifier) @export.default_value)

; Re-export: export { foo } from './module'
(export_statement
  (export_clause
    (export_specifier
      name: (identifier) @export.reexport))
  source: (string) @export.reexport_source)

; =============================================================================
; COMMONJS EXPORTS
; =============================================================================

; module.exports = X
(expression_statement
  (assignment_expression
    left: (member_expression
      object: (identifier) @_module
      (#eq? @_module "module")
      property: (property_identifier) @_exports
      (#eq? @_exports "exports"))
    right: (identifier) @export.cjs_default))

; module.exports.foo = X
(expression_statement
  (assignment_expression
    left: (member_expression
      object: (member_expression
        object: (identifier) @_module2
        (#eq? @_module2 "module")
        property: (property_identifier) @_exports2
        (#eq? @_exports2 "exports"))
      property: (property_identifier) @export.cjs_named)))

; window.X = X (browser global export)
(expression_statement
  (assignment_expression
    left: (member_expression
      object: (identifier) @_window
      (#eq? @_window "window")
      property: (property_identifier) @export.window_global)))
