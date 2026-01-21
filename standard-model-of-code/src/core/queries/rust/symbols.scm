; Rust Symbol Extraction Query
; Extracts functions, structs, traits, impls, enums
;
; Captures:
;   @func.name / @func - Function items
;   @struct.name / @struct - Struct items
;   @trait.name / @trait - Trait items
;   @impl - Impl blocks
;   @enum.name / @enum - Enum items
;   @mod.name / @mod - Module declarations
;   @const.name / @const - Const items
;   @static.name / @static - Static items
;   @type.name / @type - Type alias items

; Function items
(function_item
  name: (identifier) @func.name) @func

; Struct items
(struct_item
  name: (type_identifier) @struct.name) @struct

; Trait items
(trait_item
  name: (type_identifier) @trait.name) @trait

; Impl blocks
(impl_item) @impl

; Impl blocks for traits
(impl_item
  trait: (type_identifier) @impl_trait.name
  type: (type_identifier) @impl_type.name) @impl

; Enum items
(enum_item
  name: (type_identifier) @enum.name) @enum

; Module declarations
(mod_item
  name: (identifier) @mod.name) @mod

; Const items
(const_item
  name: (identifier) @const.name) @const

; Static items
(static_item
  name: (identifier) @static.name) @static

; Type alias items
(type_item
  name: (type_identifier) @type.name) @type

; Macro definitions
(macro_definition
  name: (identifier) @macro.name) @macro

; Attribute macros (decorators)
(attribute_item) @attribute
