; =============================================================================
; PYTHON ATOM PATTERNS - Tree-sitter queries for structural atom detection
; =============================================================================
; These patterns detect code atoms based on AST structure rather than regex.
; Captures use @atom.<type> naming for consistent extraction.
; =============================================================================

; -----------------------------------------------------------------------------
; ENTITY - Domain objects with identity
; -----------------------------------------------------------------------------

; Class inheriting from Entity/BaseModel with id field
(class_definition
  name: (identifier) @atom.entity.name
  superclasses: (argument_list
    (identifier) @_base)
  body: (block
    (expression_statement
      (assignment
        left: (identifier) @_field
        (#match? @_field "^id$|^_id$|^uuid$"))))
  (#match? @_base "^(Entity|BaseEntity|BaseModel|Model)$"))

; Dataclass with id field
(decorated_definition
  (decorator
    (identifier) @_dec
    (#eq? @_dec "dataclass"))
  definition: (class_definition
    name: (identifier) @atom.entity.name
    body: (block
      (expression_statement
        (assignment
          left: (identifier) @_field
          (#match? @_field "^id$|^_id$"))))))

; -----------------------------------------------------------------------------
; REPOSITORY - Data access patterns
; -----------------------------------------------------------------------------

; Class with CRUD methods (get/save/delete/find)
(class_definition
  name: (identifier) @atom.repository.name
  (#match? @atom.repository.name "Repository$|Repo$|Store$|DAO$")
  body: (block
    (function_definition
      name: (identifier) @_method
      (#match? @_method "^(get|find|save|delete|create|update|remove|fetch|store)"))))

; Abstract repository pattern
(class_definition
  name: (identifier) @atom.repository.name
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(ABC|Repository|AbstractRepository)$")))

; -----------------------------------------------------------------------------
; SERVICE - Business logic containers
; -----------------------------------------------------------------------------

; Class ending in Service with methods
(class_definition
  name: (identifier) @atom.service.name
  (#match? @atom.service.name "Service$|UseCase$|Interactor$")
  body: (block
    (function_definition)))

; Class with execute/run/process method
(class_definition
  name: (identifier) @atom.service.name
  body: (block
    (function_definition
      name: (identifier) @_method
      (#match? @_method "^(execute|run|process|handle|perform)$"))))

; -----------------------------------------------------------------------------
; CONTROLLER / HANDLER - Request handling
; -----------------------------------------------------------------------------

; FastAPI/Flask route decorators
(decorated_definition
  (decorator
    (call
      function: (attribute
        attribute: (identifier) @_route
        (#match? @_route "^(get|post|put|delete|patch|route)$"))))
  definition: (function_definition
    name: (identifier) @atom.controller.name))

; Class-based controller
(class_definition
  name: (identifier) @atom.controller.name
  (#match? @atom.controller.name "Controller$|Handler$|View$|Resource$"))

; Event handler functions
(function_definition
  name: (identifier) @atom.handler.name
  (#match? @atom.handler.name "^(handle_|on_|process_)"))

; -----------------------------------------------------------------------------
; FACTORY - Object creation
; -----------------------------------------------------------------------------

; Factory class pattern
(class_definition
  name: (identifier) @atom.factory.name
  (#match? @atom.factory.name "Factory$|Builder$|Creator$")
  body: (block
    (function_definition
      name: (identifier) @_method
      (#match? @_method "^(create|build|make|construct)"))))

; Factory function pattern
(function_definition
  name: (identifier) @atom.factory.name
  (#match? @atom.factory.name "^(create_|build_|make_|construct_|new_)")
  body: (block
    (return_statement)))

; -----------------------------------------------------------------------------
; DTO / VALUE OBJECT - Data containers
; -----------------------------------------------------------------------------

; Pydantic BaseModel
(class_definition
  name: (identifier) @atom.dto.name
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(BaseModel|Schema|DTO)$")))

; Named tuple
(assignment
  left: (identifier) @atom.valueobject.name
  right: (call
    function: (identifier) @_func
    (#eq? @_func "namedtuple")))

; TypedDict
(class_definition
  name: (identifier) @atom.dto.name
  superclasses: (argument_list
    (identifier) @_base
    (#eq? @_base "TypedDict")))

; Frozen dataclass (immutable value object)
(decorated_definition
  (decorator
    (call
      function: (identifier) @_dec
      (#eq? @_dec "dataclass")
      arguments: (argument_list
        (keyword_argument
          name: (identifier) @_kw
          value: (true)
          (#eq? @_kw "frozen")))))
  definition: (class_definition
    name: (identifier) @atom.valueobject.name))

; -----------------------------------------------------------------------------
; VALIDATOR - Validation logic
; -----------------------------------------------------------------------------

; Validator class
(class_definition
  name: (identifier) @atom.validator.name
  (#match? @atom.validator.name "Validator$|Checker$"))

; Validation function
(function_definition
  name: (identifier) @atom.validator.name
  (#match? @atom.validator.name "^(validate_|check_|verify_|ensure_|assert_)")
  body: (block
    (if_statement)))

; Pydantic validator decorator
(decorated_definition
  (decorator
    (identifier) @_dec
    (#match? @_dec "^(validator|field_validator|model_validator)$"))
  definition: (function_definition
    name: (identifier) @atom.validator.name))

; -----------------------------------------------------------------------------
; MAPPER / TRANSFORMER - Data conversion
; -----------------------------------------------------------------------------

; Mapper class
(class_definition
  name: (identifier) @atom.mapper.name
  (#match? @atom.mapper.name "Mapper$|Converter$|Transformer$|Adapter$"))

; Conversion function
(function_definition
  name: (identifier) @atom.mapper.name
  (#match? @atom.mapper.name "^(to_|from_|convert_|transform_|map_)"))

; -----------------------------------------------------------------------------
; QUERY - Read operations
; -----------------------------------------------------------------------------

; Query function pattern
(function_definition
  name: (identifier) @atom.query.name
  (#match? @atom.query.name "^(get_|find_|fetch_|search_|list_|query_)"))

; -----------------------------------------------------------------------------
; COMMAND - Write operations
; -----------------------------------------------------------------------------

; Command function pattern
(function_definition
  name: (identifier) @atom.command.name
  (#match? @atom.command.name "^(set_|add_|remove_|delete_|update_|save_|create_)"))

; -----------------------------------------------------------------------------
; TEST - Test functions and classes
; -----------------------------------------------------------------------------

; pytest test function
(function_definition
  name: (identifier) @atom.test.name
  (#match? @atom.test.name "^test_"))

; unittest TestCase
(class_definition
  name: (identifier) @atom.test.name
  superclasses: (argument_list
    (attribute
      attribute: (identifier) @_base
      (#eq? @_base "TestCase"))))

; pytest fixture
(decorated_definition
  (decorator
    (call
      function: (attribute
        attribute: (identifier) @_fix
        (#eq? @_fix "fixture"))))
  definition: (function_definition
    name: (identifier) @atom.fixture.name))

; -----------------------------------------------------------------------------
; EXCEPTION - Error types
; -----------------------------------------------------------------------------

; Custom exception class
(class_definition
  name: (identifier) @atom.exception.name
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "Exception$|Error$")))

; Exception with Error/Exception suffix
(class_definition
  name: (identifier) @atom.exception.name
  (#match? @atom.exception.name "(Error|Exception)$"))

; -----------------------------------------------------------------------------
; CONFIGURATION - Settings and config
; -----------------------------------------------------------------------------

; Settings class
(class_definition
  name: (identifier) @atom.configuration.name
  (#match? @atom.configuration.name "Settings$|Config$|Configuration$"))

; Pydantic settings
(class_definition
  name: (identifier) @atom.configuration.name
  superclasses: (argument_list
    (identifier) @_base
    (#eq? @_base "BaseSettings")))

; -----------------------------------------------------------------------------
; MIDDLEWARE - Request/response interceptors
; -----------------------------------------------------------------------------

; ASGI/WSGI middleware
(class_definition
  name: (identifier) @atom.middleware.name
  (#match? @atom.middleware.name "Middleware$")
  body: (block
    (function_definition
      name: (identifier) @_method
      (#match? @_method "^(__call__|dispatch)$"))))

; -----------------------------------------------------------------------------
; UTILITY - Helper functions
; -----------------------------------------------------------------------------

; Helper/utility function
(function_definition
  name: (identifier) @atom.utility.name
  (#match? @atom.utility.name "_helper$|_util$|^utils_|^helper_"))

; Private helper (single underscore prefix, not dunder)
(function_definition
  name: (identifier) @atom.internal.name
  (#match? @atom.internal.name "^_[^_]"))
