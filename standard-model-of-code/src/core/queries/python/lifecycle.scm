; =============================================================================
; PYTHON D7_LIFECYCLE QUERIES - Lifecycle phase detection
; =============================================================================
; Detects object lifecycle patterns for D7:LIFECYCLE dimension classification
; Values: create, use, destroy, manage
; =============================================================================

; -----------------------------------------------------------------------------
; CREATE PHASE - Object instantiation and initialization
; -----------------------------------------------------------------------------

; __init__ method definition
(function_definition
  name: (identifier) @_name
  (#eq? @_name "__init__")) @lifecycle.create.init

; __new__ method definition
(function_definition
  name: (identifier) @_name
  (#eq? @_name "__new__")) @lifecycle.create.new

; Class instantiation call - ClassName()
(call
  function: (identifier) @lifecycle.class_instantiation
  (#match? @lifecycle.class_instantiation "^[A-Z]")) @lifecycle.create.instantiation

; Factory method pattern - create_*, make_*, build_*
(function_definition
  name: (identifier) @_name
  (#match? @_name "^(create|make|build|new|construct|initialize|init|setup|spawn|generate)_")) @lifecycle.create.factory

; @classmethod factory (cls.method())
(call
  function: (attribute
    object: (identifier) @_cls
    (#eq? @_cls "cls"))) @lifecycle.create.classmethod_factory

; copy/deepcopy calls
(call
  function: (identifier) @_func
  (#match? @_func "^(copy|deepcopy)$")) @lifecycle.create.copy

(call
  function: (attribute
    object: (identifier) @_mod
    (#eq? @_mod "copy")
    attribute: (identifier) @_func
    (#match? @_func "^(copy|deepcopy)$"))) @lifecycle.create.copy_module

; -----------------------------------------------------------------------------
; DESTROY PHASE - Object cleanup and teardown
; -----------------------------------------------------------------------------

; __del__ method definition
(function_definition
  name: (identifier) @_name
  (#eq? @_name "__del__")) @lifecycle.destroy.del

; __exit__ method definition (context manager cleanup)
(function_definition
  name: (identifier) @_name
  (#eq? @_name "__exit__")) @lifecycle.destroy.exit

; close() method call
(call
  function: (attribute
    attribute: (identifier) @_method
    (#eq? @_method "close"))) @lifecycle.destroy.close

; dispose() method call
(call
  function: (attribute
    attribute: (identifier) @_method
    (#eq? @_method "dispose"))) @lifecycle.destroy.dispose

; shutdown() method call
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(shutdown|terminate|stop|halt|kill)$"))) @lifecycle.destroy.shutdown

; cleanup/teardown function definitions
(function_definition
  name: (identifier) @_name
  (#match? @_name "^(destroy|cleanup|teardown|dispose|finalize|release|free|clear|reset|remove|delete)_?")) @lifecycle.destroy.cleanup_func

; del statement
(delete_statement) @lifecycle.destroy.del_statement

; gc.collect() call
(call
  function: (attribute
    object: (identifier) @_mod
    (#eq? @_mod "gc")
    attribute: (identifier) @_method
    (#eq? @_method "collect"))) @lifecycle.destroy.gc

; -----------------------------------------------------------------------------
; MANAGE PHASE - Lifecycle orchestration
; -----------------------------------------------------------------------------

; __enter__ method definition (context manager)
(function_definition
  name: (identifier) @_name
  (#eq? @_name "__enter__")) @lifecycle.manage.enter

; with statement (managed lifecycle)
(with_statement) @lifecycle.manage.with_block

; @contextmanager decorator
(decorated_definition
  (decorator
    (identifier) @_dec
    (#eq? @_dec "contextmanager"))
  definition: (function_definition) @lifecycle.manage.contextmanager_func) @lifecycle.manage.contextmanager

; @contextlib.contextmanager decorator
(decorated_definition
  (decorator
    (attribute
      object: (identifier) @_mod
      (#eq? @_mod "contextlib")
      attribute: (identifier) @_dec
      (#eq? @_dec "contextmanager")))
  definition: (function_definition) @lifecycle.manage.contextmanager_func) @lifecycle.manage.contextlib_contextmanager

; Pool patterns - connection pool, thread pool, etc.
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(get_connection|acquire|borrow|checkout)$"))) @lifecycle.manage.pool_acquire

(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(release|return_connection|checkin)$"))) @lifecycle.manage.pool_release

; atexit registration
(call
  function: (attribute
    object: (identifier) @_mod
    (#eq? @_mod "atexit")
    attribute: (identifier) @_method
    (#eq? @_method "register"))) @lifecycle.manage.atexit

; signal handlers
(call
  function: (attribute
    object: (identifier) @_mod
    (#eq? @_mod "signal")
    attribute: (identifier) @_method
    (#eq? @_method "signal"))) @lifecycle.manage.signal

; -----------------------------------------------------------------------------
; USE PHASE - Normal operation (default)
; -----------------------------------------------------------------------------

; Regular method call (use phase indicator when not create/destroy/manage)
(call
  function: (attribute
    attribute: (identifier) @lifecycle.use.method_call)) @lifecycle.use.method

; Property access (use phase)
(attribute
  attribute: (identifier) @lifecycle.use.property_access) @lifecycle.use.property

; -----------------------------------------------------------------------------
; ASYNC LIFECYCLE - Async resource management
; -----------------------------------------------------------------------------

; __aenter__ method definition
(function_definition
  name: (identifier) @_name
  (#eq? @_name "__aenter__")) @lifecycle.manage.async_enter

; __aexit__ method definition
(function_definition
  name: (identifier) @_name
  (#eq? @_name "__aexit__")) @lifecycle.destroy.async_exit

; async with statement
(with_statement
  "async") @lifecycle.manage.async_with

; asyncio.create_task
(call
  function: (attribute
    object: (identifier) @_mod
    (#eq? @_mod "asyncio")
    attribute: (identifier) @_method
    (#eq? @_method "create_task"))) @lifecycle.create.async_task

; task.cancel()
(call
  function: (attribute
    attribute: (identifier) @_method
    (#eq? @_method "cancel"))) @lifecycle.destroy.async_cancel

; -----------------------------------------------------------------------------
; TEST LIFECYCLE - Test setup/teardown
; -----------------------------------------------------------------------------

; setUp/tearDown methods
(function_definition
  name: (identifier) @_name
  (#match? @_name "^(setUp|setUpClass|setUpModule)$")) @lifecycle.create.test_setup

(function_definition
  name: (identifier) @_name
  (#match? @_name "^(tearDown|tearDownClass|tearDownModule)$")) @lifecycle.destroy.test_teardown

; pytest fixtures
(decorated_definition
  (decorator
    (call
      function: (attribute
        object: (identifier) @_mod
        (#eq? @_mod "pytest")
        attribute: (identifier) @_dec
        (#eq? @_dec "fixture"))))
  definition: (function_definition) @lifecycle.manage.pytest_fixture) @lifecycle.manage.fixture

(decorated_definition
  (decorator
    (attribute
      object: (identifier) @_mod
      (#eq? @_mod "pytest")
      attribute: (identifier) @_dec
      (#eq? @_dec "fixture")))
  definition: (function_definition) @lifecycle.manage.pytest_fixture) @lifecycle.manage.fixture_simple

; -----------------------------------------------------------------------------
; RESOURCE LIFECYCLE - File/DB/Network resources
; -----------------------------------------------------------------------------

; open() call (resource creation)
(call
  function: (identifier) @_func
  (#eq? @_func "open")) @lifecycle.create.file_open

; Database connection
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(connect|create_connection|get_connection)$"))) @lifecycle.create.db_connect

; Socket creation
(call
  function: (attribute
    object: (identifier) @_mod
    (#eq? @_mod "socket")
    attribute: (identifier) @_method
    (#eq? @_method "socket"))) @lifecycle.create.socket

