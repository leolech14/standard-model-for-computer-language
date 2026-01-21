; =============================================================================
; JAVASCRIPT/TYPESCRIPT ATOM PATTERNS - Tree-sitter queries for atom detection
; =============================================================================
; Detects React components, hooks, services, handlers, and other patterns.
; =============================================================================

; -----------------------------------------------------------------------------
; REACT COMPONENT - UI components
; -----------------------------------------------------------------------------

; Function component (capitalized name returning JSX)
(function_declaration
  name: (identifier) @atom.component.name
  (#match? @atom.component.name "^[A-Z]")
  body: (statement_block
    (return_statement
      (jsx_element))))

; Arrow function component
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.component.name
    (#match? @atom.component.name "^[A-Z]")
    value: (arrow_function
      body: (parenthesized_expression
        (jsx_element)))))

; Arrow function component with block body
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.component.name
    (#match? @atom.component.name "^[A-Z]")
    value: (arrow_function
      body: (statement_block
        (return_statement
          (jsx_element))))))

; Class component extending React.Component
(class_declaration
  name: (identifier) @atom.component.name
  (class_heritage
    (extends_clause
      value: (member_expression
        property: (property_identifier) @_base
        (#match? @_base "^(Component|PureComponent)$")))))

; -----------------------------------------------------------------------------
; REACT HOOK - State and effect hooks
; -----------------------------------------------------------------------------

; Custom hook (use* prefix)
(function_declaration
  name: (identifier) @atom.hook.name
  (#match? @atom.hook.name "^use[A-Z]"))

; Arrow function hook
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.hook.name
    (#match? @atom.hook.name "^use[A-Z]")
    value: (arrow_function)))

; -----------------------------------------------------------------------------
; SERVICE - Business logic
; -----------------------------------------------------------------------------

; Class ending in Service
(class_declaration
  name: (identifier) @atom.service.name
  (#match? @atom.service.name "Service$|UseCase$|Interactor$"))

; Service object literal
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.service.name
    (#match? @atom.service.name "Service$|service$")
    value: (object)))

; -----------------------------------------------------------------------------
; REPOSITORY / STORE - Data access
; -----------------------------------------------------------------------------

; Repository class
(class_declaration
  name: (identifier) @atom.repository.name
  (#match? @atom.repository.name "Repository$|Store$|DAO$"))

; Redux slice
(call_expression
  function: (identifier) @_func
  (#eq? @_func "createSlice")
  arguments: (arguments
    (object
      (pair
        key: (property_identifier) @_key
        (#eq? @_key "name")
        value: (string) @atom.store.name))))

; Zustand store
(call_expression
  function: (identifier) @_func
  (#eq? @_func "create")
  arguments: (arguments
    (arrow_function))) @atom.store

; -----------------------------------------------------------------------------
; CONTROLLER / HANDLER - Request handling
; -----------------------------------------------------------------------------

; Express route handler
(call_expression
  function: (member_expression
    object: (identifier) @_app
    property: (property_identifier) @_method
    (#match? @_method "^(get|post|put|delete|patch|use)$"))
  arguments: (arguments
    (string)
    (arrow_function))) @atom.controller

; Controller class
(class_declaration
  name: (identifier) @atom.controller.name
  (#match? @atom.controller.name "Controller$|Handler$"))

; Event handler function
(function_declaration
  name: (identifier) @atom.handler.name
  (#match? @atom.handler.name "^(handle|on)[A-Z]"))

; Event handler arrow function
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.handler.name
    (#match? @atom.handler.name "^(handle|on)[A-Z]")
    value: (arrow_function)))

; -----------------------------------------------------------------------------
; FACTORY - Object creation
; -----------------------------------------------------------------------------

; Factory function
(function_declaration
  name: (identifier) @atom.factory.name
  (#match? @atom.factory.name "^(create|build|make)[A-Z]"))

; Factory class
(class_declaration
  name: (identifier) @atom.factory.name
  (#match? @atom.factory.name "Factory$|Builder$"))

; -----------------------------------------------------------------------------
; MAPPER / TRANSFORMER - Data conversion
; -----------------------------------------------------------------------------

; Mapper function
(function_declaration
  name: (identifier) @atom.mapper.name
  (#match? @atom.mapper.name "^(map|convert|transform|to)[A-Z]"))

; Arrow function mapper
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.mapper.name
    (#match? @atom.mapper.name "Mapper$|Converter$|Transformer$")
    value: (arrow_function)))

; -----------------------------------------------------------------------------
; VALIDATOR - Validation logic
; -----------------------------------------------------------------------------

; Validator function
(function_declaration
  name: (identifier) @atom.validator.name
  (#match? @atom.validator.name "^(validate|check|verify|isValid)"))

; Zod/Yup schema
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.validator.name
    (#match? @atom.validator.name "Schema$|Validator$")
    value: (call_expression
      function: (member_expression))))

; -----------------------------------------------------------------------------
; DTO / TYPE - Data structures
; -----------------------------------------------------------------------------

; TypeScript interface
(interface_declaration
  name: (type_identifier) @atom.dto.name)

; TypeScript type alias
(type_alias_declaration
  name: (type_identifier) @atom.dto.name)

; -----------------------------------------------------------------------------
; TEST - Test functions
; -----------------------------------------------------------------------------

; Jest/Mocha describe block
(call_expression
  function: (identifier) @_func
  (#eq? @_func "describe")
  arguments: (arguments
    (string) @atom.test.name
    (arrow_function)))

; Jest/Mocha it/test block
(call_expression
  function: (identifier) @_func
  (#match? @_func "^(it|test)$")
  arguments: (arguments
    (string) @atom.test.name
    (arrow_function)))

; Test function with test_ prefix
(function_declaration
  name: (identifier) @atom.test.name
  (#match? @atom.test.name "^test[A-Z_]"))

; -----------------------------------------------------------------------------
; QUERY - Read operations
; -----------------------------------------------------------------------------

; Query function
(function_declaration
  name: (identifier) @atom.query.name
  (#match? @atom.query.name "^(get|find|fetch|search|list|query)[A-Z]"))

; React Query hook usage
(call_expression
  function: (identifier) @_func
  (#eq? @_func "useQuery")) @atom.query

; -----------------------------------------------------------------------------
; COMMAND / MUTATION - Write operations
; -----------------------------------------------------------------------------

; Command function
(function_declaration
  name: (identifier) @atom.command.name
  (#match? @atom.command.name "^(set|add|remove|delete|update|save|create)[A-Z]"))

; React Query mutation
(call_expression
  function: (identifier) @_func
  (#eq? @_func "useMutation")) @atom.command

; -----------------------------------------------------------------------------
; MIDDLEWARE - Request interceptors
; -----------------------------------------------------------------------------

; Express middleware
(function_declaration
  name: (identifier) @atom.middleware.name
  parameters: (formal_parameters
    (identifier) @_req
    (identifier) @_res
    (identifier) @_next
    (#eq? @_next "next")))

; Middleware class
(class_declaration
  name: (identifier) @atom.middleware.name
  (#match? @atom.middleware.name "Middleware$"))

; -----------------------------------------------------------------------------
; UTILITY - Helper functions
; -----------------------------------------------------------------------------

; Utility function
(function_declaration
  name: (identifier) @atom.utility.name
  (#match? @atom.utility.name "Helper$|Util$|Utils$|helper$|util$"))

; Utility module exports
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.utility.name
    (#match? @atom.utility.name "utils$|helpers$")
    value: (object)))

; -----------------------------------------------------------------------------
; CONFIGURATION - Config objects
; -----------------------------------------------------------------------------

; Config object
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.configuration.name
    (#match? @atom.configuration.name "^(config|Config|settings|Settings|options|Options)$")
    value: (object)))

; Environment config
(lexical_declaration
  (variable_declarator
    name: (identifier) @atom.configuration.name
    (#match? @atom.configuration.name "^(env|ENV|environment)$")))

; -----------------------------------------------------------------------------
; EXCEPTION / ERROR - Error types
; -----------------------------------------------------------------------------

; Custom error class
(class_declaration
  name: (identifier) @atom.exception.name
  (#match? @atom.exception.name "(Error|Exception)$")
  (class_heritage
    (extends_clause
      value: (identifier) @_base
      (#eq? @_base "Error"))))

; Error factory function
(function_declaration
  name: (identifier) @atom.exception.name
  (#match? @atom.exception.name "^(create|throw)[A-Z].*Error$"))

; -----------------------------------------------------------------------------
; CONTEXT / PROVIDER - React context
; -----------------------------------------------------------------------------

; React context creation
(call_expression
  function: (member_expression
    object: (identifier) @_react
    (#eq? @_react "React")
    property: (property_identifier) @_method
    (#eq? @_method "createContext"))) @atom.context

; Context provider component
(function_declaration
  name: (identifier) @atom.provider.name
  (#match? @atom.provider.name "Provider$"))

; -----------------------------------------------------------------------------
; REDUCER - State reducers
; -----------------------------------------------------------------------------

; Reducer function
(function_declaration
  name: (identifier) @atom.reducer.name
  (#match? @atom.reducer.name "Reducer$|reducer$")
  parameters: (formal_parameters
    (identifier) @_state
    (identifier) @_action))

; useReducer hook pattern
(call_expression
  function: (identifier) @_func
  (#eq? @_func "useReducer")) @atom.reducer
