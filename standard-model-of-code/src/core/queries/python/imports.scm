; =============================================================================
; PYTHON IMPORTS QUERY
; Captures import statements for cross-file symbol resolution
; =============================================================================

; Basic import: import os, sys
(import_statement
  name: (dotted_name) @import.module)

; Import with alias: import numpy as np
(import_statement
  name: (aliased_import
    name: (dotted_name) @import.module
    alias: (identifier) @import.alias))

; From import: from os import path
(import_from_statement
  module_name: (dotted_name)? @import.source_module
  module_name: (relative_import)? @import.relative
  name: (dotted_name) @import.symbol)

; From import with alias: from os import path as p
(import_from_statement
  module_name: (dotted_name)? @import.source_module
  module_name: (relative_import)? @import.relative
  name: (aliased_import
    name: (dotted_name) @import.symbol
    alias: (identifier) @import.alias))

; Wildcard import: from module import *
(import_from_statement
  module_name: (dotted_name)? @import.source_module
  (wildcard_import) @import.wildcard)

; =============================================================================
; EXPORTS (Module-level definitions that can be imported)
; =============================================================================

; Module-level function definitions
(module
  (function_definition
    name: (identifier) @export.function))

; Module-level class definitions
(module
  (class_definition
    name: (identifier) @export.class))

; Module-level assignments (constants, module variables)
(module
  (expression_statement
    (assignment
      left: (identifier) @export.variable)))

; Module-level annotated assignments
(module
  (expression_statement
    (assignment
      left: (identifier) @export.variable)))

; __all__ list (explicit exports)
(module
  (expression_statement
    (assignment
      left: (identifier) @export.all_marker
      (#eq? @export.all_marker "__all__")
      right: (list
        (string) @export.all_item))))
