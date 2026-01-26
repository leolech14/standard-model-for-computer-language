; =============================================================================
; GO BOUNDARY QUERY (D4_BOUNDARY)
; Detects I/O patterns: Internal | Input | Output | I-O
; =============================================================================

; =============================================================================
; INPUT PATTERNS
; =============================================================================

; Function parameters
(parameter_declaration) @boundary.input.param

; HTTP request reading
(call_expression
  function: (selector_expression
    operand: (identifier) @_req
    (#match? @_req "^(r|req|request)$")
    field: (field_identifier) @_method
    (#match? @_method "^(Body|FormValue|URL|Header|Cookie|Context)$"))
  @boundary.input.http_request)

; File reading
(call_expression
  function: (selector_expression
    operand: (identifier) @_pkg
    (#match? @_pkg "^(os|ioutil|io|bufio)$")
    field: (field_identifier) @_func
    (#match? @_func "^(Open|Read|ReadFile|ReadAll|ReadDir)$"))
  @boundary.input.file)

; Environment variables
(call_expression
  function: (selector_expression
    operand: (identifier) @_pkg
    (#eq? @_pkg "os")
    field: (field_identifier) @_func
    (#match? @_func "^(Getenv|LookupEnv|Environ)$"))
  @boundary.input.env)

; Database reads
(call_expression
  function: (selector_expression
    field: (field_identifier) @_method
    (#match? @_method "^(Query|QueryRow|QueryContext|Get|Find|First|Select)$"))
  @boundary.input.database)

; Channel receive
(receive_statement) @boundary.input.channel

; =============================================================================
; OUTPUT PATTERNS
; =============================================================================

; Return statements
(return_statement) @boundary.output.return

; HTTP response writing
(call_expression
  function: (selector_expression
    operand: (identifier) @_w
    (#match? @_w "^(w|writer|response|rw)$")
    field: (field_identifier) @_method
    (#match? @_method "^(Write|WriteHeader|WriteString)$"))
  @boundary.output.http_response)

; fmt printing
(call_expression
  function: (selector_expression
    operand: (identifier) @_pkg
    (#eq? @_pkg "fmt")
    field: (field_identifier) @_func
    (#match? @_func "^(Print|Printf|Println|Fprint|Fprintf|Fprintln)$"))
  @boundary.output.print)

; Logging
(call_expression
  function: (selector_expression
    operand: (identifier) @_pkg
    (#match? @_pkg "^(log|logger|slog)$"))
  @boundary.output.log)

; File writing
(call_expression
  function: (selector_expression
    operand: (identifier) @_pkg
    (#match? @_pkg "^(os|ioutil|io|bufio)$")
    field: (field_identifier) @_func
    (#match? @_func "^(Write|WriteFile|WriteString|Create)$"))
  @boundary.output.file)

; Database writes
(call_expression
  function: (selector_expression
    field: (field_identifier) @_method
    (#match? @_method "^(Exec|ExecContext|Create|Insert|Update|Delete|Save)$"))
  @boundary.output.database)

; Channel send
(send_statement) @boundary.output.channel

; Panic
(call_expression
  function: (identifier) @_func
  (#eq? @_func "panic")
  @boundary.output.panic)
