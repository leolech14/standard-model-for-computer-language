; =============================================================================
; JAVASCRIPT LAYER QUERY (D2_LAYER)
; Tree-sitter-based Clean Architecture layer detection
; =============================================================================
; Layers: Interface | Application | Core | Infrastructure | Test | Unknown

; =============================================================================
; INFRASTRUCTURE LAYER
; Database, file I/O, external services, HTTP clients
; =============================================================================

; Database/ORM patterns
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(prisma|sequelize|mongoose|knex|typeorm)$"))
  @layer.infrastructure.orm)

; Repository pattern
(class_declaration
  name: (identifier) @_name
  (#match? @_name "(Repository|Store|DAO|DataAccess)$")
  @layer.infrastructure.repository)

; HTTP clients (fetch, axios, etc.)
(call_expression
  function: (identifier) @_func
  (#match? @_func "^fetch$")
  @layer.infrastructure.http)

(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(axios|fetch|http|https|got|superagent)$"))
  @layer.infrastructure.http)

; File system operations
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(fs|path|fsp)$"))
  @layer.infrastructure.file_io)

; Cache/Redis
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(redis|cache|memcached)$"))
  @layer.infrastructure.cache)

; =============================================================================
; INTERFACE LAYER
; API endpoints, routes, controllers, React components
; =============================================================================

; Express routes
(call_expression
  function: (member_expression
    object: (identifier) @_app
    property: (property_identifier) @_method
    (#match? @_method "^(get|post|put|delete|patch|use)$"))
  @layer.interface.express)

; Next.js/Remix route handlers
(export_statement
  declaration: (function_declaration
    name: (identifier) @_name
    (#match? @_name "^(GET|POST|PUT|DELETE|PATCH|loader|action)$"))
  @layer.interface.route_handler)

; React components (function)
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^[A-Z]")
  body: (statement_block
    (return_statement
      (jsx_element)))
  @layer.interface.react)

; React components (arrow function)
(lexical_declaration
  (variable_declarator
    name: (identifier) @_name
    (#match? @_name "^[A-Z]")
    value: (arrow_function
      body: (jsx_element)))
  @layer.interface.react)

(lexical_declaration
  (variable_declarator
    name: (identifier) @_name
    (#match? @_name "^[A-Z]")
    value: (arrow_function
      body: (parenthesized_expression
        (jsx_element))))
  @layer.interface.react)

; Controller naming
(class_declaration
  name: (identifier) @_name
  (#match? @_name "(Controller|Handler|Router|Endpoint)$")
  @layer.interface.naming)

; GraphQL resolvers
(pair
  key: (property_identifier) @_key
  (#match? @_key "^(Query|Mutation|Subscription)$")
  @layer.interface.graphql)

; =============================================================================
; APPLICATION LAYER
; Services, use cases, business logic orchestration
; =============================================================================

; Service classes
(class_declaration
  name: (identifier) @_name
  (#match? @_name "(Service|UseCase|Interactor|Orchestrator)$")
  @layer.application.service)

; Use case pattern (execute method)
(class_declaration
  name: (identifier) @_name
  body: (class_body
    (method_definition
      name: (property_identifier) @_method
      (#match? @_method "^(execute|run|perform|handle)$")))
  @layer.application.usecase)

; =============================================================================
; CORE/DOMAIN LAYER
; Entities, value objects, domain logic, types
; =============================================================================

; TypeScript interfaces/types (domain models)
(interface_declaration
  name: (type_identifier) @_name
  (#match? @_name "(Entity|Model|DTO|Props|State)$")
  @layer.core.interface)

(type_alias_declaration
  name: (type_identifier) @_name
  (#match? @_name "(Entity|Model|DTO|Props|State)$")
  @layer.core.type)

; Domain classes
(class_declaration
  name: (identifier) @_name
  (#match? @_name "(Entity|Aggregate|ValueObject|DomainObject|Model)$")
  @layer.core.entity)

; Enums
(enum_declaration
  @layer.core.enum)

; =============================================================================
; TEST LAYER
; Test files, fixtures, mocks
; =============================================================================

; Test functions (describe/it/test)
(call_expression
  function: (identifier) @_func
  (#match? @_func "^(describe|it|test|expect)$")
  @layer.test.function)

; Jest/Vitest patterns
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(jest|vi)$"))
  @layer.test.mock)

; beforeEach/afterEach
(call_expression
  function: (identifier) @_func
  (#match? @_func "^(beforeEach|afterEach|beforeAll|afterAll)$")
  @layer.test.lifecycle)
