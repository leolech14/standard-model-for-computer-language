; =============================================================================
; RUST BOUNDARY QUERY (D4_BOUNDARY)
; Detects I/O patterns: Internal | Input | Output | I-O
; =============================================================================

; =============================================================================
; INPUT PATTERNS
; =============================================================================

; Function parameters
(parameter) @boundary.input.param

; File reading
(call_expression
  function: (scoped_identifier
    path: (identifier) @_mod
    (#match? @_mod "^(std::fs|tokio::fs|async_std::fs)$")
    name: (identifier) @_func
    (#match? @_func "^(read|read_to_string|read_dir|metadata)$"))
  @boundary.input.file)

; Environment variables
(macro_invocation
  macro: (identifier) @_macro
  (#match? @_macro "^(env|option_env)$")
  @boundary.input.env)

; stdin
(call_expression
  function: (scoped_identifier
    path: (identifier) @_mod
    (#eq? @_mod "std::io")
    name: (identifier) @_func
    (#eq? @_func "stdin"))
  @boundary.input.stdin)

; HTTP request (reqwest, hyper)
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(get|body|json|text|bytes)$"))
  @boundary.input.http)

; Database reads
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(query|fetch|get|find|select|load)$"))
  @boundary.input.database)

; Channel receive
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(recv|try_recv|recv_timeout)$"))
  @boundary.input.channel)

; =============================================================================
; OUTPUT PATTERNS
; =============================================================================

; Return expressions (explicit)
(return_expression) @boundary.output.return

; Last expression in block (implicit return)
(block
  (expression_statement)
  .
  (_) @boundary.output.implicit_return)

; println!/print! macros
(macro_invocation
  macro: (identifier) @_macro
  (#match? @_macro "^(print|println|eprint|eprintln|dbg)$")
  @boundary.output.print)

; File writing
(call_expression
  function: (scoped_identifier
    path: (identifier) @_mod
    (#match? @_mod "^(std::fs|tokio::fs)$")
    name: (identifier) @_func
    (#match? @_func "^(write|write_all|create)$"))
  @boundary.output.file)

; Write trait methods
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(write|write_all|write_fmt|flush)$"))
  @boundary.output.write)

; HTTP response
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(send|json|body|status)$"))
  @boundary.output.http)

; Database writes
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(execute|insert|update|delete|save)$"))
  @boundary.output.database)

; Channel send
(call_expression
  function: (field_expression
    field: (field_identifier) @_method
    (#match? @_method "^(send|try_send)$"))
  @boundary.output.channel)

; panic! macro
(macro_invocation
  macro: (identifier) @_macro
  (#eq? @_macro "panic")
  @boundary.output.panic)
