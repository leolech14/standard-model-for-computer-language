; =============================================================================
; PYTHON D5_STATE QUERIES - Statefulness detection
; =============================================================================
; Detects state maintenance patterns for D5:STATE dimension classification
; Values: stateless, stateful
; =============================================================================

; -----------------------------------------------------------------------------
; STATEFUL INDICATORS - Instance/class state
; -----------------------------------------------------------------------------

; self.attr access (reading instance state)
(attribute
  object: (identifier) @_self
  (#eq? @_self "self")
  attribute: (identifier) @state.instance_read) @state.self_access

; self.attr = value (writing instance state)
(assignment
  left: (attribute
    object: (identifier) @_self
    (#eq? @_self "self")
    attribute: (identifier) @state.instance_write)) @state.self_mutation

; self.attr += value (mutating instance state)
(augmented_assignment
  left: (attribute
    object: (identifier) @_self
    (#eq? @_self "self"))) @state.self_augmented

; cls.attr access (class state)
(attribute
  object: (identifier) @_cls
  (#eq? @_cls "cls")
  attribute: (identifier) @state.class_read) @state.cls_access

; cls.attr = value (class state mutation)
(assignment
  left: (attribute
    object: (identifier) @_cls
    (#eq? @_cls "cls"))) @state.cls_mutation

; -----------------------------------------------------------------------------
; GLOBAL/NONLOCAL STATE - Scope-escaping state
; -----------------------------------------------------------------------------

; global declaration
(global_statement
  (identifier) @state.global_var) @state.global

; nonlocal declaration
(nonlocal_statement
  (identifier) @state.nonlocal_var) @state.nonlocal

; -----------------------------------------------------------------------------
; CLASS-LEVEL STATE - Class attributes
; -----------------------------------------------------------------------------

; Class body assignment (class attribute)
(class_definition
  body: (block
    (expression_statement
      (assignment
        left: (identifier) @state.class_attr)))) @state.class_level

; Type-annotated class attribute
(class_definition
  body: (block
    (expression_statement
      (assignment
        left: (identifier) @state.typed_class_attr
        type: (_))))) @state.typed_class_level

; -----------------------------------------------------------------------------
; MUTABLE DEFAULT ARGUMENTS - Hidden state
; -----------------------------------------------------------------------------

; Default argument that is a list
(default_parameter
  value: (list) @state.mutable_default) @state.mutable_default_list

; Default argument that is a dict
(default_parameter
  value: (dictionary) @state.mutable_default) @state.mutable_default_dict

; Default argument that is a set
(default_parameter
  value: (set) @state.mutable_default) @state.mutable_default_set

; -----------------------------------------------------------------------------
; CLOSURE STATE - Captured variables
; -----------------------------------------------------------------------------

; Function inside function (potential closure)
(function_definition
  body: (block
    (function_definition) @state.nested_function)) @state.closure_parent

; Lambda inside function
(function_definition
  body: (block
    (_
      (lambda) @state.nested_lambda))) @state.lambda_closure

; -----------------------------------------------------------------------------
; MODULE-LEVEL STATE - Module globals
; -----------------------------------------------------------------------------

; Module-level assignment (outside class/function)
(module
  (expression_statement
    (assignment
      left: (identifier) @state.module_var))) @state.module_level

; Module-level augmented assignment
(module
  (expression_statement
    (augmented_assignment
      left: (identifier) @state.module_var_mutated))) @state.module_mutation

; -----------------------------------------------------------------------------
; DATACLASS/ATTRS STATE - Declared instance state
; -----------------------------------------------------------------------------

; @dataclass decorator
(decorated_definition
  (decorator
    (identifier) @_dec
    (#eq? @_dec "dataclass"))
  definition: (class_definition) @state.dataclass) @state.dataclass_decorated

; @dataclass() decorator with call
(decorated_definition
  (decorator
    (call
      function: (identifier) @_dec
      (#eq? @_dec "dataclass")))
  definition: (class_definition) @state.dataclass) @state.dataclass_call

; @attr.s or @attrs decorator
(decorated_definition
  (decorator
    (attribute
      object: (identifier) @_mod
      (#match? @_mod "^(attr|attrs)$")))
  definition: (class_definition) @state.attrs_class) @state.attrs_decorated

; -----------------------------------------------------------------------------
; PROPERTY STATE - Managed attribute access
; -----------------------------------------------------------------------------

; @property decorator
(decorated_definition
  (decorator
    (identifier) @_dec
    (#eq? @_dec "property"))
  definition: (function_definition
    name: (identifier) @state.property_name)) @state.property

; @x.setter decorator
(decorated_definition
  (decorator
    (attribute
      attribute: (identifier) @_setter
      (#eq? @_setter "setter")))
  definition: (function_definition) @state.setter) @state.property_setter

; -----------------------------------------------------------------------------
; CACHING/MEMOIZATION STATE - Hidden persistent state
; -----------------------------------------------------------------------------

; @cache decorator
(decorated_definition
  (decorator
    (identifier) @_dec
    (#match? @_dec "^(cache|lru_cache|cached)$"))
  definition: (function_definition) @state.cached_function) @state.cache_decorator

; @functools.cache / @functools.lru_cache
(decorated_definition
  (decorator
    (attribute
      object: (identifier) @_mod
      (#eq? @_mod "functools")
      attribute: (identifier) @_dec
      (#match? @_dec "^(cache|lru_cache)$")))
  definition: (function_definition) @state.cached_function) @state.functools_cache

; @functools.lru_cache() with call
(decorated_definition
  (decorator
    (call
      function: (attribute
        object: (identifier) @_mod
        (#eq? @_mod "functools")
        attribute: (identifier) @_dec
        (#match? @_dec "^(cache|lru_cache)$"))))
  definition: (function_definition) @state.cached_function) @state.functools_cache_call

; -----------------------------------------------------------------------------
; SINGLETON STATE - Single instance pattern
; -----------------------------------------------------------------------------

; _instance class attribute pattern
(class_definition
  body: (block
    (expression_statement
      (assignment
        left: (identifier) @_attr
        (#match? @_attr "^_?instance$")
        right: (none))))) @state.singleton_pattern

