; =============================================================================
; TYPESCRIPT BOUNDARY QUERY (D4_BOUNDARY)
; Detects I/O patterns: Internal | Input | Output | I-O
; =============================================================================

; =============================================================================
; INPUT PATTERNS
; =============================================================================

; Function parameters
(formal_parameters
  (required_parameter) @boundary.input.param)

; HTTP request reading
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(body|query|params|headers|cookies)$"))
  @boundary.input.request)

; File reading
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(fs|fsp)$")
    property: (property_identifier) @_method
    (#match? @_method "^(read|readFile|readFileSync|readdir)$"))
  @boundary.input.file)

; Environment variables
(member_expression
  object: (member_expression
    object: (identifier) @_process
    (#eq? @_process "process")
    property: (property_identifier) @_env
    (#eq? @_env "env"))
  @boundary.input.env)

; Fetch/HTTP GET
(call_expression
  function: (identifier) @_func
  (#eq? @_func "fetch")
  @boundary.input.http)

; Database reads
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(find|findOne|findMany|select|query|get)$"))
  @boundary.input.database)

; =============================================================================
; OUTPUT PATTERNS
; =============================================================================

; Return statements
(return_statement) @boundary.output.return

; Console/logging
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#eq? @_obj "console"))
  @boundary.output.console)

; File writing
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(fs|fsp)$")
    property: (property_identifier) @_method
    (#match? @_method "^(write|writeFile|writeFileSync|appendFile)$"))
  @boundary.output.file)

; HTTP response
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(send|json|render|redirect|status)$"))
  @boundary.output.response)

; Database writes
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(create|insert|update|delete|save|upsert)$"))
  @boundary.output.database)

; Throw statements
(throw_statement) @boundary.output.throw
