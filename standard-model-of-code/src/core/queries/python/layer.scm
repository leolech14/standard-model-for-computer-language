; =============================================================================
; PYTHON LAYER QUERY (D2_LAYER)
; Tree-sitter-based Clean Architecture layer detection
; =============================================================================
; Layers: Interface | Application | Core | Infrastructure | Test | Unknown

; =============================================================================
; INFRASTRUCTURE LAYER
; Database, file I/O, external services, repositories
; =============================================================================

; SQLAlchemy / Database patterns
(class_definition
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(Base|Model|DeclarativeBase|Session)$"))
  @layer.infrastructure.orm)

(class_definition
  superclasses: (argument_list
    (attribute
      attribute: (identifier) @_base
      (#match? @_base "^(Model|Base)$")))
  @layer.infrastructure.orm)

; Repository pattern
(class_definition
  name: (identifier) @_name
  (#match? @_name "(Repository|Store|DAO|DataAccess|Persistence)$")
  @layer.infrastructure.repository)

(class_definition
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "(Repository|Store|DAO|BaseRepository)"))
  @layer.infrastructure.repository)

; File I/O operations
(call
  function: (identifier) @_func
  (#match? @_func "^(open|read|write)$")
  @layer.infrastructure.file_io)

(call
  function: (attribute
    object: (identifier) @_obj
    (#match? @_obj "^(os|pathlib|shutil|glob)$"))
  @layer.infrastructure.file_io)

; HTTP clients
(call
  function: (attribute
    object: (identifier) @_obj
    (#match? @_obj "^(requests|httpx|aiohttp|urllib)$"))
  @layer.infrastructure.http)

; Database connections
(call
  function: (attribute
    object: (identifier) @_obj
    (#match? @_obj "^(psycopg2|pymysql|sqlite3|asyncpg|sqlalchemy)$"))
  @layer.infrastructure.database)

; Cache/Redis
(call
  function: (attribute
    object: (identifier) @_obj
    (#match? @_obj "^(redis|memcache|cache)$"))
  @layer.infrastructure.cache)

; =============================================================================
; INTERFACE LAYER
; API endpoints, CLI, web handlers, presentation
; =============================================================================

; FastAPI routes
(decorated_definition
  (decorator
    (call
      function: (attribute
        object: (identifier) @_app
        attribute: (identifier) @_method
        (#match? @_method "^(get|post|put|delete|patch|options|head)$"))))
  @layer.interface.fastapi)

(decorated_definition
  (decorator
    (attribute
      object: (identifier) @_router
      attribute: (identifier) @_method
      (#match? @_method "^(get|post|put|delete|patch)$")))
  @layer.interface.fastapi)

; Flask routes
(decorated_definition
  (decorator
    (call
      function: (attribute
        object: (identifier) @_app
        (#match? @_app "^(app|blueprint|bp)$")
        attribute: (identifier) @_route
        (#match? @_route "^route$"))))
  @layer.interface.flask)

; Django views
(class_definition
  superclasses: (argument_list
    (attribute
      attribute: (identifier) @_view
      (#match? @_view "^(View|APIView|ViewSet|GenericView|ModelViewSet)$")))
  @layer.interface.django)

; CLI with click/typer
(decorated_definition
  (decorator
    (call
      function: (attribute
        object: (identifier) @_cli
        (#match? @_cli "^(click|typer|app|cli)$")
        attribute: (identifier) @_cmd
        (#match? @_cmd "^(command|option|argument)$"))))
  @layer.interface.cli)

(decorated_definition
  (decorator
    (attribute
      object: (identifier) @_cli
      (#match? @_cli "^(click|typer)$")))
  @layer.interface.cli)

; Controller/Handler naming
(class_definition
  name: (identifier) @_name
  (#match? @_name "(Controller|Handler|View|Endpoint|Resource|Router)$")
  @layer.interface.naming)

; GraphQL resolvers
(decorated_definition
  (decorator
    (call
      function: (attribute
        attribute: (identifier) @_resolver
        (#match? @_resolver "^(resolver|mutation|query|field)$"))))
  @layer.interface.graphql)

; =============================================================================
; APPLICATION LAYER
; Use cases, services, orchestration
; =============================================================================

; Service classes
(class_definition
  name: (identifier) @_name
  (#match? @_name "(Service|UseCase|Interactor|Application|Orchestrator)$")
  @layer.application.service)

; Service with dependency injection
(decorated_definition
  (decorator
    (identifier) @_deco
    (#match? @_deco "^(injectable|service|inject|Inject)$"))
  definition: (class_definition)
  @layer.application.di)

; Use case pattern (execute/run method)
(class_definition
  name: (identifier) @_name
  body: (block
    (function_definition
      name: (identifier) @_method
      (#match? @_method "^(execute|run|perform|handle)$")))
  @layer.application.usecase)

; =============================================================================
; CORE/DOMAIN LAYER
; Entities, value objects, domain logic
; =============================================================================

; Domain entities
(class_definition
  name: (identifier) @_name
  (#match? @_name "(Entity|Aggregate|ValueObject|DomainObject)$")
  @layer.core.entity)

; Pydantic models (often domain)
(class_definition
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(BaseModel|BaseSettings)$"))
  @layer.core.pydantic)

; Dataclasses (domain entities)
(decorated_definition
  (decorator
    (identifier) @_deco
    (#eq? @_deco "dataclass"))
  definition: (class_definition)
  @layer.core.dataclass)

; Domain events
(class_definition
  name: (identifier) @_name
  (#match? @_name "(Event|DomainEvent|Message)$")
  @layer.core.event)

; Enums (domain values)
(class_definition
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(Enum|IntEnum|StrEnum|Flag)$"))
  @layer.core.enum)

; Abstract base classes (domain interfaces)
(class_definition
  superclasses: (argument_list
    (identifier) @_base
    (#match? @_base "^(ABC|Protocol)$"))
  @layer.core.abstract)

; =============================================================================
; TEST LAYER
; Test files, fixtures, mocks
; =============================================================================

; Test functions
(function_definition
  name: (identifier) @_name
  (#match? @_name "^test_")
  @layer.test.function)

; Test classes
(class_definition
  name: (identifier) @_name
  (#match? @_name "^Test")
  @layer.test.class)

; Pytest fixtures
(decorated_definition
  (decorator
    (attribute
      object: (identifier) @_pytest
      (#eq? @_pytest "pytest")
      attribute: (identifier) @_fixture
      (#eq? @_fixture "fixture")))
  @layer.test.fixture)

(decorated_definition
  (decorator
    (call
      function: (attribute
        object: (identifier) @_pytest
        (#eq? @_pytest "pytest")
        attribute: (identifier) @_fixture
        (#eq? @_fixture "fixture"))))
  @layer.test.fixture)

; unittest
(class_definition
  superclasses: (argument_list
    (attribute
      object: (identifier) @_unittest
      (#eq? @_unittest "unittest")
      attribute: (identifier) @_testcase
      (#eq? @_testcase "TestCase")))
  @layer.test.unittest)

; Mock imports
(import_from_statement
  module_name: (dotted_name) @_module
  (#match? @_module "^(unittest\\.mock|mock|pytest_mock)$")
  @layer.test.mock)
