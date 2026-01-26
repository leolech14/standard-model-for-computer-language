; PYTHON ROLES (D3_ROLE)

; -- REPOSITORY --
;    CRUD-like classes with data access methods

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

; -- SERVICE --
;    Business logic coordinators

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

; -- CONTROLLER --
;    HTTP/API request handlers

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

; -- FACTORY --
;    Object creation methods that return new instances

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

; -- HANDLER --
;    Event/message processors

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

; -- VALIDATOR --
;    Input validation

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

; -- TRANSFORMER/MAPPER --
;    Data transformation

; Mapper class
(class_definition
  name: (identifier) @role.mapper.class
  (#match? @role.mapper.class "(Mapper|Converter|Transformer|Serializer)$"))

; Transform function
(function_definition
  name: (identifier) @role.mapper.function
  (#match? @role.mapper.function "^(map|convert|transform|serialize|deserialize|to_|from_)"))

; -- UTILITY --
;    General-purpose helpers

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

; -- TEST/ASSERTER --

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

; -- LIFECYCLE --
;    Initialization, cleanup, context managers

; Dunder lifecycle methods
(function_definition
  name: (identifier) @role.lifecycle.dunder
  (#match? @role.lifecycle.dunder "^__(init|del|enter|exit|call)__$"))

; Setup/teardown
(function_definition
  name: (identifier) @role.lifecycle.setup
  (#match? @role.lifecycle.setup "^(setup|teardown|configure|initialize|dispose)"))

; -- INTERNAL/DTO --
;    Data containers with minimal logic

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

; -- GUARD --
;    Access control, permissions

; Guard/permission class
(class_definition
  name: (identifier) @role.guard.class
  (#match? @role.guard.class "(Guard|Permission|Policy|Auth)"))

; Permission check function
(function_definition
  name: (identifier) @role.guard.function
  (#match? @role.guard.function "^(check_|has_|can_|is_allowed|require_)"))

; -- EMITTER --
;    Event emission

; Event emitter class
(class_definition
  name: (identifier) @role.emitter.class
  (#match? @role.emitter.class "(Emitter|Publisher|Producer|Broadcaster)$"))

; Emit function
(function_definition
  name: (identifier) @role.emitter.function
  (#match? @role.emitter.function "^(emit|publish|broadcast|notify|dispatch)_"))

; -- QUERY --
;    Read-only computation, data retrieval

; Compute/calculate functions
(function_definition
  name: (identifier) @role.query.compute
  (#match? @role.query.compute "^(compute|calculate|evaluate|measure|determine)_"))

; Methods with compute/calculate prefix
(function_definition
  name: (identifier) @role.query.compute_method
  (#match? @role.query.compute_method "^(compute|calculate|evaluate)"))

; Getter-style functions (not in a class context)
(module
  (function_definition
    name: (identifier) @role.query.getter
    (#match? @role.query.getter "^get_")
    body: (block
      (return_statement))))

; Classification functions
(function_definition
  name: (identifier) @role.query.classifier
  (#match? @role.query.classifier "^(classify|categorize|identify|detect|recognize)"))

; Analysis functions
(function_definition
  name: (identifier) @role.query.analysis
  (#match? @role.query.analysis "^(analyze|analyse|inspect|examine|audit)"))

; Count/sum aggregation functions
(function_definition
  name: (identifier) @role.query.aggregate
  (#match? @role.query.aggregate "^(count|sum|average|total|aggregate)_"))

; -- PROCESSOR --
;    Data transformation pipelines, batch operations

; Process functions
(function_definition
  name: (identifier) @role.processor.function
  (#match? @role.processor.function "^(process|run|execute|perform|apply)_"))

; Batch processing functions
(function_definition
  name: (identifier) @role.processor.batch
  (#match? @role.processor.batch "^(batch|bulk|parallel)_"))

; Pipeline functions
(function_definition
  name: (identifier) @role.processor.pipeline
  (#match? @role.processor.pipeline "^(pipe|chain|stream|flow)_"))

; Processor class
(class_definition
  name: (identifier) @role.processor.class
  (#match? @role.processor.class "(Processor|Pipeline|Worker|Job)$"))

; -- PARSER --
;    Parsing and lexing

; Parser class
(class_definition
  name: (identifier) @role.parser.class
  (#match? @role.parser.class "(Parser|Lexer|Tokenizer|Reader)$"))

; Parse function
(function_definition
  name: (identifier) @role.parser.function
  (#match? @role.parser.function "^(parse|lex|tokenize|read)_"))

; -- ACCESSOR --
;    Property accessors

; Property decorated method
(decorated_definition
  (decorator
    (identifier) @_prop
    (#eq? @_prop "property"))
  definition: (function_definition
    name: (identifier) @role.accessor.property))

; Cached property
(decorated_definition
  (decorator
    (call
      function: (identifier) @_cached
      (#match? @_cached "^(cached_property|lru_cache)$")))
  definition: (function_definition
    name: (identifier) @role.accessor.cached))

; -- INTERNAL (Extended) --
;    Domain entities without standard suffixes

; Result class (computation results)
(class_definition
  name: (identifier) @role.internal.result
  (#match? @role.internal.result "(Result|Output|Response)$"))

; Config/Settings class
(class_definition
  name: (identifier) @role.internal.config
  (#match? @role.internal.config "(Config|Settings|Options|Parameters)$"))

; Metrics/Stats class
(class_definition
  name: (identifier) @role.internal.metrics
  (#match? @role.internal.metrics "(Metrics|Stats|Statistics|Report)$"))

; Index/Profile class
(class_definition
  name: (identifier) @role.internal.profile
  (#match? @role.internal.profile "(Index|Profile|Summary|Snapshot)$"))

; Model class (domain models)
(class_definition
  name: (identifier) @role.internal.model
  (#match? @role.internal.model "(Model|Entity|Record|Entry)$"))

; Classifier class
(class_definition
  name: (identifier) @role.internal.classifier
  (#match? @role.internal.classifier "Classifier$"))

; Enum-like class (constants)
(class_definition
  name: (identifier) @role.internal.enum
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(Enum|IntEnum|StrEnum|Flag)$")))

; ABC/Protocol (abstract base)
(class_definition
  name: (identifier) @role.internal.abstract
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(ABC|Protocol)$")))

; -- ADAPTER --
;    External system wrappers

; Adapter class
(class_definition
  name: (identifier) @role.adapter.class
  (#match? @role.adapter.class "(Adapter|Wrapper|Client|Connector|Gateway)$"))

; -- BUILDER --
;    Complex object construction (distinct from Factory)

; Builder class
(class_definition
  name: (identifier) @role.builder.class
  (#match? @role.builder.class "Builder$"))

; Build chain method (returns self)
(function_definition
  name: (identifier) @role.builder.method
  (#match? @role.builder.method "^(with|set|add)_")
  body: (block
    (return_statement
      (identifier) @_self
      (#eq? @_self "self"))))
