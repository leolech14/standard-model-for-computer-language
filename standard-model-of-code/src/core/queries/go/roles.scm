; =============================================================================
; GO ROLES QUERY (D3_ROLE)
; Tree-sitter-based role detection via structural patterns
; =============================================================================

; =============================================================================
; REPOSITORY PATTERN
; Data access structs with CRUD methods
; =============================================================================

; Struct with Repository/Store/DAO naming
(type_declaration
  (type_spec
    name: (type_identifier) @role.repository.struct
    type: (struct_type))
  (#match? @role.repository.struct "(Repository|Store|DAO|Repo)$"))

; Method on repository type with CRUD-like name
(method_declaration
  receiver: (parameter_list
    (parameter_declaration
      type: [(pointer_type (type_identifier) @_recv) (type_identifier) @_recv]
      (#match? @_recv "(Repository|Store|DAO|Repo)$")))
  name: (field_identifier) @role.repository.method
  (#match? @role.repository.method "^(Find|Get|Save|Delete|Create|Update|List|Fetch)"))

; =============================================================================
; SERVICE PATTERN
; Business logic coordinators
; =============================================================================

; Struct with Service naming
(type_declaration
  (type_spec
    name: (type_identifier) @role.service.struct
    type: (struct_type))
  (#match? @role.service.struct "Service$"))

; Service interface
(type_declaration
  (type_spec
    name: (type_identifier) @role.service.interface
    type: (interface_type))
  (#match? @role.service.interface "Service$"))

; =============================================================================
; HANDLER PATTERN
; HTTP/gRPC/event handlers
; =============================================================================

; Handler struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.handler.struct
    type: (struct_type))
  (#match? @role.handler.struct "Handler$"))

; Handler function (http.HandlerFunc signature pattern)
(function_declaration
  name: (identifier) @role.handler.function
  (#match? @role.handler.function "(Handler|Handle)"))

; Method with Handle prefix
(method_declaration
  name: (field_identifier) @role.handler.method
  (#match? @role.handler.method "^Handle"))

; =============================================================================
; CONTROLLER PATTERN
; Request controllers
; =============================================================================

; Controller struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.controller.struct
    type: (struct_type))
  (#match? @role.controller.struct "Controller$"))

; =============================================================================
; FACTORY PATTERN
; Constructor functions (New* pattern)
; =============================================================================

; Constructor function (Go convention: NewXxx)
(function_declaration
  name: (identifier) @role.factory.function
  (#match? @role.factory.function "^New[A-Z]")
  body: (block
    (statement_list
      (return_statement))))

; Make* factory function
(function_declaration
  name: (identifier) @role.factory.make
  (#match? @role.factory.make "^Make[A-Z]"))

; Create* factory function
(function_declaration
  name: (identifier) @role.factory.create
  (#match? @role.factory.create "^Create[A-Z]"))

; =============================================================================
; VALIDATOR PATTERN
; Input validation
; =============================================================================

; Validator struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.validator.struct
    type: (struct_type))
  (#match? @role.validator.struct "Validator$"))

; Validate function
(function_declaration
  name: (identifier) @role.validator.function
  (#match? @role.validator.function "^(Validate|Check|Verify|Is[A-Z])"))

; Validate method
(method_declaration
  name: (field_identifier) @role.validator.method
  (#match? @role.validator.method "^(Validate|Check|Verify)"))

; =============================================================================
; MAPPER/CONVERTER PATTERN
; Data transformation
; =============================================================================

; Mapper/Converter struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.mapper.struct
    type: (struct_type))
  (#match? @role.mapper.struct "(Mapper|Converter|Transformer)$"))

; ToXxx/FromXxx conversion functions
(function_declaration
  name: (identifier) @role.mapper.function
  (#match? @role.mapper.function "^(To[A-Z]|From[A-Z]|Convert|Map|Transform)"))

; Conversion methods
(method_declaration
  name: (field_identifier) @role.mapper.method
  (#match? @role.mapper.method "^(To[A-Z]|From[A-Z]|Convert|Map)"))

; =============================================================================
; MIDDLEWARE PATTERN
; Request middleware
; =============================================================================

; Middleware struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.middleware.struct
    type: (struct_type))
  (#match? @role.middleware.struct "Middleware$"))

; Middleware function
(function_declaration
  name: (identifier) @role.middleware.function
  (#match? @role.middleware.function "(Middleware|Interceptor)$"))

; =============================================================================
; UTILITY PATTERN
; Helper functions and utilities
; =============================================================================

; Utility package-level functions (common patterns)
(function_declaration
  name: (identifier) @role.utility.function
  (#match? @role.utility.function "^(Parse|Format|Encode|Decode|Hash|Generate|Build|Render)"))

; Helper struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.utility.struct
    type: (struct_type))
  (#match? @role.utility.struct "(Utils?|Helper|Tools?)$"))

; =============================================================================
; TEST PATTERN
; Test functions and benchmarks
; =============================================================================

; Test function (Go convention: Test*)
(function_declaration
  name: (identifier) @role.asserter.test
  (#match? @role.asserter.test "^Test[A-Z]"))

; Benchmark function
(function_declaration
  name: (identifier) @role.asserter.benchmark
  (#match? @role.asserter.benchmark "^Benchmark[A-Z]"))

; Example function
(function_declaration
  name: (identifier) @role.asserter.example
  (#match? @role.asserter.example "^Example[A-Z]"))

; =============================================================================
; INTERNAL/DTO PATTERN
; Data transfer objects and internal types
; =============================================================================

; Interface definition (behavioral contract)
(type_declaration
  (type_spec
    name: (type_identifier) @role.internal.interface
    type: (interface_type)))

; Plain struct (entity-like, no suffix pattern)
(type_declaration
  (type_spec
    name: (type_identifier) @role.internal.struct
    type: (struct_type))
  (#match? @role.internal.struct "^[A-Z][a-z]+([A-Z][a-z]+)*$")
  (#not-match? @role.internal.struct "(Service|Repository|Handler|Controller|Validator|Mapper|Middleware|Utils?|Helper|Store|DAO)$"))

; Request/Response structs
(type_declaration
  (type_spec
    name: (type_identifier) @role.internal.dto
    type: (struct_type))
  (#match? @role.internal.dto "(Request|Response|Req|Res|Input|Output|Params|Args|Options|Config)$"))

; =============================================================================
; GUARD PATTERN
; Authorization and access control
; =============================================================================

; Auth/Guard struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.guard.struct
    type: (struct_type))
  (#match? @role.guard.struct "(Auth|Guard|Permission|Policy|Authoriz)"))

; Auth check functions
(function_declaration
  name: (identifier) @role.guard.function
  (#match? @role.guard.function "^(Check|Has|Can|IsAllowed|Require|Authorize)"))

; =============================================================================
; EMITTER/PUBLISHER PATTERN
; Event emission
; =============================================================================

; Publisher/Emitter struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.emitter.struct
    type: (struct_type))
  (#match? @role.emitter.struct "(Publisher|Emitter|Producer|Broadcaster|Notifier)$"))

; Publish/Emit functions
(function_declaration
  name: (identifier) @role.emitter.function
  (#match? @role.emitter.function "^(Emit|Publish|Broadcast|Notify|Dispatch|Send)"))

; =============================================================================
; LIFECYCLE PATTERN
; Initialization and cleanup
; =============================================================================

; Init function (Go special)
(function_declaration
  name: (identifier) @role.lifecycle.init
  (#eq? @role.lifecycle.init "init"))

; Main function
(function_declaration
  name: (identifier) @role.lifecycle.main
  (#eq? @role.lifecycle.main "main"))

; Setup/Teardown methods
(method_declaration
  name: (field_identifier) @role.lifecycle.method
  (#match? @role.lifecycle.method "^(Setup|Teardown|Init|Close|Shutdown|Start|Stop)"))

; Close/Shutdown functions
(function_declaration
  name: (identifier) @role.lifecycle.function
  (#match? @role.lifecycle.function "^(Close|Shutdown|Cleanup|Dispose)"))

; =============================================================================
; ERROR PATTERN
; Custom error types
; =============================================================================

; Error type (implements error interface pattern)
(type_declaration
  (type_spec
    name: (type_identifier) @role.internal.error
    type: (struct_type))
  (#match? @role.internal.error "Error$"))

; =============================================================================
; CLIENT PATTERN
; External service clients
; =============================================================================

; Client struct
(type_declaration
  (type_spec
    name: (type_identifier) @role.utility.client
    type: (struct_type))
  (#match? @role.utility.client "Client$"))

; NewClient factory
(function_declaration
  name: (identifier) @role.factory.client
  (#match? @role.factory.client "^NewClient"))
