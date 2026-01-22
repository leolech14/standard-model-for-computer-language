; =============================================================================
; PYTHON ROLES QUERY (D3_ROLE)
; Tree-sitter-based role detection via structural patterns
; =============================================================================

; =============================================================================
; REPOSITORY PATTERN
; CRUD-like classes with data access methods
; =============================================================================

; Class with repository-like methods (find_*, get_*, save_*, delete_*)
(class_definition
  name: (identifier) @role.repository.class
  body: (block
    (function_definition
      name: (identifier) @_method
      (#match? @_method "^(find|get|save|delete|create|update|list|fetch)_"))))

; Class inheriting from base repository
(class_definition
  name: (identifier) @role.repository.inherits
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "(Repository|Store|DAO|DataAccess)")))

; =============================================================================
; SERVICE PATTERN
; Business logic coordinators
; =============================================================================

; Class with service naming
(class_definition
  name: (identifier) @role.service.naming
  (#match? @role.service.naming "Service$"))

; Class with @injectable/@service decorator
(decorated_definition
  (decorator
    (identifier) @_decorator
    (#match? @_decorator "^(injectable|service|Injectable|Service)$"))
  definition: (class_definition
    name: (identifier) @role.service.decorated))

; =============================================================================
; CONTROLLER PATTERN
; HTTP/API request handlers
; =============================================================================

; FastAPI/Flask route decorators
(decorated_definition
  (decorator
    (call
      function: (attribute
        object: (identifier) @_app
        attribute: (identifier) @_route
        (#match? @_route "^(get|post|put|delete|patch|route)$"))))
  definition: (function_definition
    name: (identifier) @role.controller.route))

; Class with controller naming
(class_definition
  name: (identifier) @role.controller.naming
  (#match? @role.controller.naming "(Controller|View|Resource|Endpoint)$"))

; Django view class
(class_definition
  name: (identifier) @role.controller.django
  superclasses: (argument_list
    (attribute
      attribute: (identifier) @_view
      (#match? @_view "(View|ViewSet|APIView)"))))

; =============================================================================
; FACTORY PATTERN
; Object creation methods that return new instances
; =============================================================================

; Function that creates and returns objects
(function_definition
  name: (identifier) @role.factory.function
  (#match? @role.factory.function "^(create|make|build|new)_")
  body: (block
    (return_statement
      (call))))

; Class with factory methods
(class_definition
  name: (identifier) @role.factory.class
  (#match? @role.factory.class "Factory$"))

; @staticmethod factory pattern
(decorated_definition
  (decorator
    (identifier) @_static
    (#eq? @_static "staticmethod"))
  definition: (function_definition
    name: (identifier) @role.factory.static
    (#match? @role.factory.static "^(create|from_|build)")))

; =============================================================================
; HANDLER PATTERN
; Event/message processors
; =============================================================================

; Event handler functions
(function_definition
  name: (identifier) @role.handler.function
  (#match? @role.handler.function "(handler|Handler|on_|handle_)"))

; Handler class with handle method
(class_definition
  name: (identifier) @role.handler.class
  (#match? @role.handler.class "Handler$")
  body: (block
    (function_definition
      name: (identifier) @_handle
      (#match? @_handle "^handle"))))

; =============================================================================
; VALIDATOR PATTERN
; Input validation
; =============================================================================

; Validator class
(class_definition
  name: (identifier) @role.validator.class
  (#match? @role.validator.class "(Validator|Schema|Form)$"))

; Validation function
(function_definition
  name: (identifier) @role.validator.function
  (#match? @role.validator.function "^(validate|check|verify|ensure)_"))

; Pydantic model (validator)
(class_definition
  name: (identifier) @role.validator.pydantic
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(BaseModel|BaseSettings)$")))

; =============================================================================
; TRANSFORMER/MAPPER PATTERN
; Data transformation
; =============================================================================

; Mapper class
(class_definition
  name: (identifier) @role.mapper.class
  (#match? @role.mapper.class "(Mapper|Converter|Transformer|Serializer)$"))

; Transform function
(function_definition
  name: (identifier) @role.mapper.function
  (#match? @role.mapper.function "^(map|convert|transform|serialize|deserialize|to_|from_)"))

; =============================================================================
; UTILITY PATTERN
; General-purpose helpers
; =============================================================================

; Utility class
(class_definition
  name: (identifier) @role.utility.class
  (#match? @role.utility.class "(Utils?|Helper|Tools?)$"))

; Utility function (no self, no class)
(module
  (function_definition
    name: (identifier) @role.utility.module_func
    parameters: (parameters)
    (#not-match? @role.utility.module_func "^(test_|_)")))

; =============================================================================
; TEST/ASSERTER PATTERN
; =============================================================================

; Test function
(function_definition
  name: (identifier) @role.asserter.function
  (#match? @role.asserter.function "^test_"))

; Test class
(class_definition
  name: (identifier) @role.asserter.class
  (#match? @role.asserter.class "^Test"))

; Pytest fixture
(decorated_definition
  (decorator
    (attribute
      object: (identifier) @_pytest
      (#eq? @_pytest "pytest")
      attribute: (identifier) @_fixture
      (#eq? @_fixture "fixture")))
  definition: (function_definition
    name: (identifier) @role.asserter.fixture))

; =============================================================================
; LIFECYCLE PATTERN
; Initialization, cleanup, context managers
; =============================================================================

; Dunder lifecycle methods
(function_definition
  name: (identifier) @role.lifecycle.dunder
  (#match? @role.lifecycle.dunder "^__(init|del|enter|exit|call)__$"))

; Setup/teardown
(function_definition
  name: (identifier) @role.lifecycle.setup
  (#match? @role.lifecycle.setup "^(setup|teardown|configure|initialize|dispose)"))

; =============================================================================
; INTERNAL/DTO PATTERN
; Data containers with minimal logic
; =============================================================================

; Dataclass
(decorated_definition
  (decorator
    (identifier) @_dataclass
    (#eq? @_dataclass "dataclass"))
  definition: (class_definition
    name: (identifier) @role.internal.dataclass))

; NamedTuple
(class_definition
  name: (identifier) @role.internal.namedtuple
  superclasses: (argument_list
    (identifier) @_base
    (#eq? @_base "NamedTuple")))

; TypedDict
(class_definition
  name: (identifier) @role.internal.typeddict
  superclasses: (argument_list
    (identifier) @_base
    (#eq? @_base "TypedDict")))

; Plain entity class (no suffix, CamelCase, has __init__)
(class_definition
  name: (identifier) @role.internal.entity
  (#match? @role.internal.entity "^[A-Z][a-z]+([A-Z][a-z]+)*$")
  body: (block
    (function_definition
      name: (identifier) @_init
      (#eq? @_init "__init__"))))

; =============================================================================
; GUARD PATTERN
; Access control, permissions
; =============================================================================

; Guard/permission class
(class_definition
  name: (identifier) @role.guard.class
  (#match? @role.guard.class "(Guard|Permission|Policy|Auth)"))

; Permission check function
(function_definition
  name: (identifier) @role.guard.function
  (#match? @role.guard.function "^(check_|has_|can_|is_allowed|require_)"))

; =============================================================================
; EMITTER PATTERN
; Event emission
; =============================================================================

; Event emitter class
(class_definition
  name: (identifier) @role.emitter.class
  (#match? @role.emitter.class "(Emitter|Publisher|Producer|Broadcaster)$"))

; Emit function
(function_definition
  name: (identifier) @role.emitter.function
  (#match? @role.emitter.function "^(emit|publish|broadcast|notify|dispatch)_"))
