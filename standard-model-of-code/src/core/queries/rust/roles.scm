; =============================================================================
; RUST ROLES QUERY (D3_ROLE)
; Tree-sitter-based role detection via structural patterns
; =============================================================================

; =============================================================================
; REPOSITORY PATTERN
; Data access structs with CRUD methods
; =============================================================================

; Struct with Repository/Store/DAO naming
(struct_item
  (type_identifier) @role.repository.struct
  (#match? @role.repository.struct "(Repository|Store|Dao|Repo)$"))

; =============================================================================
; SERVICE PATTERN
; Business logic coordinators
; =============================================================================

; Struct with Service naming
(struct_item
  (type_identifier) @role.service.struct
  (#match? @role.service.struct "Service$"))

; Service trait
(trait_item
  (type_identifier) @role.service.trait
  (#match? @role.service.trait "Service$"))

; =============================================================================
; HANDLER PATTERN
; Request/event handlers
; =============================================================================

; Handler struct
(struct_item
  (type_identifier) @role.handler.struct
  (#match? @role.handler.struct "Handler$"))

; Handler trait
(trait_item
  (type_identifier) @role.handler.trait
  (#match? @role.handler.trait "Handler$"))

; Handler function
(function_item
  name: (identifier) @role.handler.function
  (#match? @role.handler.function "(handler|handle)"))

; Async handler (common in Rust web frameworks)
(function_item
  name: (identifier) @role.handler.async
  (#match? @role.handler.async "^(get|post|put|delete|patch)_"))

; =============================================================================
; CONTROLLER PATTERN
; Request controllers
; =============================================================================

; Controller struct
(struct_item
  (type_identifier) @role.controller.struct
  (#match? @role.controller.struct "Controller$"))

; =============================================================================
; FACTORY PATTERN
; Constructor functions
; =============================================================================

; new() constructor (Rust convention)
(function_item
  name: (identifier) @role.factory.new
  (#eq? @role.factory.new "new"))

; builder pattern
(function_item
  name: (identifier) @role.factory.builder
  (#eq? @role.factory.builder "builder"))

; from_* constructors
(function_item
  name: (identifier) @role.factory.from
  (#match? @role.factory.from "^from_"))

; create_* functions
(function_item
  name: (identifier) @role.factory.create
  (#match? @role.factory.create "^(create|make|build)_"))

; =============================================================================
; VALIDATOR PATTERN
; Input validation
; =============================================================================

; Validator struct
(struct_item
  (type_identifier) @role.validator.struct
  (#match? @role.validator.struct "Validator$"))

; Validate function
(function_item
  name: (identifier) @role.validator.function
  (#match? @role.validator.function "^(validate|check|verify|is_)"))

; =============================================================================
; MAPPER/CONVERTER PATTERN
; Data transformation
; =============================================================================

; Mapper/Converter struct
(struct_item
  (type_identifier) @role.mapper.struct
  (#match? @role.mapper.struct "(Mapper|Converter|Transformer)$"))

; Conversion functions (into_*, to_*, from_*)
(function_item
  name: (identifier) @role.mapper.function
  (#match? @role.mapper.function "^(into_|to_|convert|transform)"))

; =============================================================================
; MIDDLEWARE PATTERN
; Request middleware
; =============================================================================

; Middleware struct
(struct_item
  (type_identifier) @role.middleware.struct
  (#match? @role.middleware.struct "Middleware$"))

; Middleware trait
(trait_item
  (type_identifier) @role.middleware.trait
  (#match? @role.middleware.trait "Middleware$"))

; =============================================================================
; UTILITY PATTERN
; Helper functions and utilities
; =============================================================================

; Utility module functions (common patterns)
(function_item
  name: (identifier) @role.utility.function
  (#match? @role.utility.function "^(parse|format|encode|decode|hash|generate)_"))

; Helper struct
(struct_item
  (type_identifier) @role.utility.struct
  (#match? @role.utility.struct "(Utils?|Helper|Tools?)$"))

; =============================================================================
; TEST PATTERN
; Test functions
; =============================================================================

; Test function (test_ prefix convention)
(function_item
  name: (identifier) @role.asserter.test
  (#match? @role.asserter.test "^test_"))

; =============================================================================
; INTERNAL/DTO PATTERN
; Data transfer objects and internal types
; =============================================================================

; Trait definition (behavioral contract)
(trait_item
  (type_identifier) @role.internal.trait)

; Enum definition
(enum_item
  (type_identifier) @role.internal.enum)

; Request/Response/DTO structs
(struct_item
  (type_identifier) @role.internal.dto
  (#match? @role.internal.dto "(Request|Response|Dto|Input|Output|Params|Args|Options|Config)$"))

; =============================================================================
; ERROR PATTERN
; Custom error types
; =============================================================================

; Error struct
(struct_item
  (type_identifier) @role.internal.error
  (#match? @role.internal.error "Error$"))

; Error enum
(enum_item
  (type_identifier) @role.internal.error_enum
  (#match? @role.internal.error_enum "Error$"))

; =============================================================================
; GUARD PATTERN
; Authorization and access control
; =============================================================================

; Guard struct
(struct_item
  (type_identifier) @role.guard.struct
  (#match? @role.guard.struct "(Auth|Guard|Permission|Policy)"))

; Permission check functions
(function_item
  name: (identifier) @role.guard.function
  (#match? @role.guard.function "^(check_|has_|can_|is_allowed|require_|authorize)"))

; =============================================================================
; EMITTER/PUBLISHER PATTERN
; Event emission
; =============================================================================

; Publisher/Emitter struct
(struct_item
  (type_identifier) @role.emitter.struct
  (#match? @role.emitter.struct "(Publisher|Emitter|Producer|Broadcaster|Notifier|Sender)$"))

; Publish/Emit functions
(function_item
  name: (identifier) @role.emitter.function
  (#match? @role.emitter.function "^(emit|publish|broadcast|notify|dispatch|send)_"))

; =============================================================================
; LIFECYCLE PATTERN
; Initialization and cleanup
; =============================================================================

; main function
(function_item
  name: (identifier) @role.lifecycle.main
  (#eq? @role.lifecycle.main "main"))

; init/setup functions
(function_item
  name: (identifier) @role.lifecycle.function
  (#match? @role.lifecycle.function "^(init|setup|teardown|cleanup|dispose|close|shutdown)"))

; =============================================================================
; CLIENT PATTERN
; External service clients
; =============================================================================

; Client struct
(struct_item
  (type_identifier) @role.utility.client
  (#match? @role.utility.client "Client$"))
