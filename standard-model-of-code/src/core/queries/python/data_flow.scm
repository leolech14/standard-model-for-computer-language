; =============================================================================
; PYTHON DATA FLOW QUERIES - Assignment and mutation detection for D6:EFFECT
; =============================================================================
; Used by data_flow_analyzer.py to detect value flow and state mutations.
; =============================================================================

; -----------------------------------------------------------------------------
; SIMPLE ASSIGNMENT - x = value
; -----------------------------------------------------------------------------

(assignment
  left: (identifier) @target.name
  right: (_) @source) @assignment

; Attribute assignment - obj.attr = value (mutation)
(assignment
  left: (attribute) @target.attribute
  right: (_) @source) @assignment.attribute

; Subscript assignment - arr[i] = value (mutation)
(assignment
  left: (subscript) @target.subscript
  right: (_) @source) @assignment.subscript

; Tuple unpacking - a, b = values
(assignment
  left: (pattern_list) @target.destructure
  right: (_) @source) @assignment.destructure

; -----------------------------------------------------------------------------
; AUGMENTED ASSIGNMENT - x += value (always mutation)
; -----------------------------------------------------------------------------

(augmented_assignment
  left: (identifier) @target.name) @mutation.augmented

(augmented_assignment
  left: (attribute) @target.attribute) @mutation.augmented_attribute

(augmented_assignment
  left: (subscript) @target.subscript) @mutation.augmented_subscript

; -----------------------------------------------------------------------------
; GLOBAL/NONLOCAL DECLARATIONS (side effect indicators)
; -----------------------------------------------------------------------------

(global_statement
  (identifier) @global.name) @global

(nonlocal_statement
  (identifier) @nonlocal.name) @nonlocal

; -----------------------------------------------------------------------------
; DELETE STATEMENT (mutation)
; -----------------------------------------------------------------------------

(delete_statement
  (identifier) @delete.target) @delete

(delete_statement
  (attribute) @delete.attribute) @delete.attribute

(delete_statement
  (subscript) @delete.subscript) @delete.subscript

; -----------------------------------------------------------------------------
; SIDE EFFECT CALLS - I/O and external interactions
; -----------------------------------------------------------------------------

; print() call
(call
  function: (identifier) @_func
  (#eq? @_func "print")) @sideeffect.io

; input() call
(call
  function: (identifier) @_func
  (#eq? @_func "input")) @sideeffect.io

; open() call
(call
  function: (identifier) @_func
  (#eq? @_func "open")) @sideeffect.io

; requests.* calls
(call
  function: (attribute
    object: (identifier) @_obj
    (#eq? @_obj "requests"))) @sideeffect.external

; os.* calls
(call
  function: (attribute
    object: (identifier) @_obj
    (#eq? @_obj "os"))) @sideeffect.external

; subprocess.* calls
(call
  function: (attribute
    object: (identifier) @_obj
    (#eq? @_obj "subprocess"))) @sideeffect.external

; -----------------------------------------------------------------------------
; METHOD CALLS ON SELF (potential mutation)
; -----------------------------------------------------------------------------

; self.attr = value (in method)
(assignment
  left: (attribute
    object: (identifier) @_self
    (#eq? @_self "self"))) @mutation.self_attribute

; self.method() - method call on self
(call
  function: (attribute
    object: (identifier) @_self
    (#eq? @_self "self")
    attribute: (identifier) @method.name)) @call.self_method

; -----------------------------------------------------------------------------
; LIST/DICT MUTATIONS
; -----------------------------------------------------------------------------

; list.append(), list.extend(), etc.
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(append|extend|insert|pop|remove|clear|reverse|sort)$"))) @mutation.list_method

; dict.update(), dict.pop(), etc.
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(update|pop|popitem|clear|setdefault)$"))) @mutation.dict_method

; -----------------------------------------------------------------------------
; FOR LOOP VARIABLE BINDING (not mutation, but assignment)
; -----------------------------------------------------------------------------

(for_statement
  left: (identifier) @loop.variable
  right: (_) @loop.iterable) @loop.for

; Comprehension variable
(list_comprehension
  (for_in_clause
    left: (identifier) @comprehension.variable))

(dictionary_comprehension
  (for_in_clause
    left: (identifier) @comprehension.variable))

(set_comprehension
  (for_in_clause
    left: (identifier) @comprehension.variable))

(generator_expression
  (for_in_clause
    left: (identifier) @comprehension.variable))

; -----------------------------------------------------------------------------
; WALRUS OPERATOR (assignment expression)
; -----------------------------------------------------------------------------

(named_expression
  name: (identifier) @walrus.name
  value: (_) @walrus.value) @walrus

; -----------------------------------------------------------------------------
; WITH STATEMENT BINDING
; -----------------------------------------------------------------------------

(with_statement
  (with_clause
    (with_item
      value: (as_pattern
        (as_pattern_target) @with.variable)))) @with.binding
