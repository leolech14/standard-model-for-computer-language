; =============================================================================
; PYTHON D4_BOUNDARY QUERIES - External boundary crossing detection
; =============================================================================
; Detects I/O operations for D4:BOUNDARY dimension classification
; Values: internal, input, output, io
; =============================================================================

; -----------------------------------------------------------------------------
; INPUT BOUNDARIES - Reading from external sources
; -----------------------------------------------------------------------------

; File operations - reading
(call
  function: (identifier) @_func
  (#eq? @_func "open")) @boundary.input.file

(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(read|readline|readlines)$"))) @boundary.input.file

; User input
(call
  function: (identifier) @_func
  (#eq? @_func "input")) @boundary.input.user

; HTTP requests - GET/read operations
(call
  function: (attribute
    object: (identifier) @_obj
    (#eq? @_obj "requests")
    attribute: (identifier) @_method
    (#match? @_method "^(get|head|options)$"))) @boundary.input.http

; Database queries - read operations
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(query|find|find_one|find_all|select|fetch|fetchone|fetchall|fetchmany|get|filter|all|first|one)$"))) @boundary.input.database

; Environment variables
(attribute
  object: (attribute
    object: (identifier) @_os
    (#eq? @_os "os")
    attribute: (identifier) @_env
    (#eq? @_env "environ"))) @boundary.input.env

(call
  function: (attribute
    object: (attribute
      object: (identifier) @_os
      (#eq? @_os "os")
      attribute: (identifier) @_env
      (#eq? @_env "environ"))
    attribute: (identifier) @_method
    (#eq? @_method "get"))) @boundary.input.env

; CLI arguments
(attribute
  object: (identifier) @_sys
  (#eq? @_sys "sys")
  attribute: (identifier) @_argv
  (#eq? @_argv "argv")) @boundary.input.cli

; JSON/YAML loading
(call
  function: (attribute
    object: (identifier) @_mod
    (#match? @_mod "^(json|yaml|toml|pickle)$")
    attribute: (identifier) @_method
    (#match? @_method "^(load|loads)$"))) @boundary.input.serialization

; Socket receive
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(recv|recvfrom|recvmsg|recv_into)$"))) @boundary.input.socket

; -----------------------------------------------------------------------------
; OUTPUT BOUNDARIES - Writing to external destinations
; -----------------------------------------------------------------------------

; Print/stdout
(call
  function: (identifier) @_func
  (#eq? @_func "print")) @boundary.output.stdout

; File write operations
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(write|writelines|writeto)$"))) @boundary.output.file

; HTTP requests - write operations
(call
  function: (attribute
    object: (identifier) @_obj
    (#eq? @_obj "requests")
    attribute: (identifier) @_method
    (#match? @_method "^(post|put|patch|delete)$"))) @boundary.output.http

; Database mutations
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(insert|insert_one|insert_many|update|update_one|update_many|delete|delete_one|delete_many|save|create|commit|execute|executemany)$"))) @boundary.output.database

; JSON/YAML dumping
(call
  function: (attribute
    object: (identifier) @_mod
    (#match? @_mod "^(json|yaml|toml|pickle)$")
    attribute: (identifier) @_method
    (#match? @_method "^(dump|dumps)$"))) @boundary.output.serialization

; Socket send
(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(send|sendto|sendmsg|sendall)$"))) @boundary.output.socket

; Logging
(call
  function: (attribute
    object: (identifier) @_obj
    (#match? @_obj "^(logging|logger|log)$"))) @boundary.output.logging

(call
  function: (attribute
    attribute: (identifier) @_method
    (#match? @_method "^(debug|info|warning|error|critical|exception|log)$"))) @boundary.output.logging

; Subprocess/shell commands
(call
  function: (attribute
    object: (identifier) @_mod
    (#eq? @_mod "subprocess")
    attribute: (identifier) @_method
    (#match? @_method "^(run|call|check_call|check_output|Popen)$"))) @boundary.output.subprocess

(call
  function: (attribute
    object: (attribute
      object: (identifier) @_os
      (#eq? @_os "os"))
    attribute: (identifier) @_method
    (#match? @_method "^(system|popen|spawn)$"))) @boundary.output.subprocess
