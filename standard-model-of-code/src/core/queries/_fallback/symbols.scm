; Fallback Symbol Extraction Query
; Generic patterns that work across many languages
; Used when no language-specific query exists
;
; This is intentionally minimal to avoid false positives

; Generic function patterns
(function_definition) @func
(function_declaration) @func
(function_item) @func

; Generic class patterns
(class_definition) @class
(class_declaration) @class

; Generic struct patterns
(struct_item) @struct
(struct_definition) @struct

; Generic method patterns
(method_definition) @method
(method_declaration) @method
