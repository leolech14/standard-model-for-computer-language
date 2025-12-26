# THE 200 ATOMS - Complete Taxonomy

> *A useful working set, not a claim of totality.*

---

## Summary

| Phase | Families | Atoms |
|-------|----------|-------|
| **DATA** | 5 | 28 |
| **LOGIC** | 6 | 58 |
| **ORGANIZATION** | 5 | 52 |
| **EXECUTION** | 6 | 62 |
| **TOTAL** | 22 | **200** |

---

## PHASE 1: DATA (28 atoms)
*The matter of software - what code manipulates*

### Family 1.1: Bits (4)
| # | Name | ID | Description |
|---|------|----|-------------|
| 1 | BitFlag | DAT.BIT.A | Single boolean flag |
| 2 | BitMask | DAT.BIT.A | Binary mask for operations |
| 3 | ParityBit | DAT.BIT.A | Error detection bit |
| 4 | SignBit | DAT.BIT.A | Numeric sign indicator |

### Family 1.2: Bytes (4)
| # | Name | ID | Description |
|---|------|----|-------------|
| 5 | ByteArray | DAT.BYT.A | Raw byte sequence |
| 6 | MagicBytes | DAT.BYT.A | File format identifier |
| 7 | PaddingBytes | DAT.BYT.A | Alignment padding |
| 8 | Buffer | DAT.BYT.A | In-memory byte buffer |

### Family 1.3: Primitives (10)
| # | Name | ID | Description |
|---|------|----|-------------|
| 9 | Boolean | DAT.PRM.A | True/false value |
| 10 | Integer | DAT.PRM.A | Whole number |
| 11 | Float | DAT.PRM.A | Decimal number |
| 12 | String | DAT.PRM.A | Text value |
| 13 | Null | DAT.PRM.A | Absence of value |
| 14 | Undefined | DAT.PRM.A | Uninitialized value |
| 15 | Symbol | DAT.PRM.A | Unique identifier |
| 16 | BigInt | DAT.PRM.A | Arbitrary precision integer |
| 17 | Char | DAT.PRM.A | Single character |
| 18 | Regex | DAT.PRM.A | Regular expression literal |

### Family 1.4: Variables (6)
| # | Name | ID | Description |
|---|------|----|-------------|
| 19 | LocalVar | DAT.VAR.A | Local variable |
| 20 | GlobalVar | DAT.VAR.A | Global variable |
| 21 | Parameter | DAT.VAR.A | Function parameter |
| 22 | Constant | DAT.VAR.A | Immutable value |
| 23 | InstanceField | DAT.VAR.A | Object instance field |
| 24 | StaticField | DAT.VAR.A | Class-level field |

### Family 1.5: Collections (4)
| # | Name | ID | Description |
|---|------|----|-------------|
| 25 | ArrayLiteral | DAT.COL.A | Array/list literal |
| 26 | ObjectLiteral | DAT.COL.A | Object/dict literal |
| 27 | TupleLiteral | DAT.COL.A | Tuple literal |
| 28 | SetLiteral | DAT.COL.A | Set literal |

---

## PHASE 2: LOGIC (58 atoms)
*The behavior of software - what code does*

### Family 2.1: Functions (10)
| # | Name | ID | Description |
|---|------|----|-------------|
| 29 | Function | LOG.FNC.M | Function definition |
| 30 | Method | LOG.FNC.M | Class method |
| 31 | Lambda | LOG.FNC.M | Anonymous function |
| 32 | Constructor | LOG.FNC.M | Object constructor |
| 33 | Destructor | LOG.FNC.M | Object destructor |
| 34 | Getter | LOG.FNC.M | Property getter |
| 35 | Setter | LOG.FNC.M | Property setter |
| 36 | AsyncFunction | LOG.FNC.M | Async function |
| 37 | Generator | LOG.FNC.M | Generator function |
| 38 | Decorator | LOG.FNC.M | Function decorator |

### Family 2.2: Expressions (20)
| # | Name | ID | Description |
|---|------|----|-------------|
| 39 | BinaryExpr | LOG.EXP.A | Binary operation |
| 40 | UnaryExpr | LOG.EXP.A | Unary operation |
| 41 | TernaryExpr | LOG.EXP.A | Conditional expression |
| 42 | CallExpr | LOG.EXP.A | Function call |
| 43 | NewExpr | LOG.EXP.A | Object instantiation |
| 44 | MemberExpr | LOG.EXP.A | Property access |
| 45 | IndexExpr | LOG.EXP.A | Index access |
| 46 | SliceExpr | LOG.EXP.A | Slice operation |
| 47 | IdentifierExpr | LOG.EXP.A | Variable reference |
| 48 | TemplateExpr | LOG.EXP.A | Template string |
| 49 | SpreadExpr | LOG.EXP.A | Spread operator |
| 50 | AwaitExpr | LOG.EXP.A | Await expression |
| 51 | YieldExpr | LOG.EXP.A | Yield expression |
| 52 | TypeCast | LOG.EXP.A | Type conversion |
| 53 | ParenExpr | LOG.EXP.A | Parenthesized expression |
| 54 | **Comprehension** | LOG.EXP.A | List/set/dict comprehension *(NEW #168)* |
| 55 | **WalrusExpr** | LOG.EXP.A | := named expression *(NEW #180)* |
| 56 | **RangeExpr** | LOG.EXP.A | start..end range *(NEW #183)* |
| 57 | **MacroCall** | LOG.EXP.A | Macro invocation *(NEW #169)* |
| 58 | ThisExpr | LOG.EXP.A | Self/this reference |

### Family 2.3: Statements (12)
| # | Name | ID | Description |
|---|------|----|-------------|
| 59 | Assignment | LOG.STM.A | Variable assignment |
| 60 | ReturnStmt | LOG.STM.A | Return statement |
| 61 | BreakStmt | LOG.STM.A | Break statement |
| 62 | ContinueStmt | LOG.STM.A | Continue statement |
| 63 | ThrowStmt | LOG.STM.A | Throw/raise exception |
| 64 | Declaration | LOG.STM.A | Variable declaration |
| 65 | ExpressionStmt | LOG.STM.A | Expression as statement |
| 66 | **EmptyStmt** | LOG.STM.A | No-op statement *(NEW #200)* |
| 67 | **LabeledBlock** | LOG.STM.A | Labeled block *(NEW #199)* |
| 68 | **DebuggerStmt** | LOG.STM.A | Debugger breakpoint *(NEW #198)* |
| 69 | AssertStmt | LOG.STM.A | Assertion statement |
| 70 | DeleteStmt | LOG.STM.A | Delete operation |

### Family 2.4: Control Flow (10)
| # | Name | ID | Description |
|---|------|----|-------------|
| 71 | IfBranch | LOG.CTL.A | If condition |
| 72 | ForLoop | LOG.CTL.A | For loop |
| 73 | WhileLoop | LOG.CTL.A | While loop |
| 74 | DoWhileLoop | LOG.CTL.A | Do-while loop |
| 75 | ForOfLoop | LOG.CTL.A | For-of/for-in loop |
| 76 | SwitchCase | LOG.CTL.A | Switch statement |
| 77 | TryBlock | LOG.CTL.A | Try block |
| 78 | CatchClause | LOG.CTL.A | Catch clause |
| 79 | FinallyClause | LOG.CTL.A | Finally clause |
| 80 | Block | LOG.CTL.A | Code block |

### Family 2.5: Pattern Matching (6) *(NEW FAMILY)*
| # | Name | ID | Description |
|---|------|----|-------------|
| 81 | **MatchPattern** | LOG.CTL.A | Match arm pattern *(NEW #173)* |
| 82 | **WildcardPattern** | LOG.CTL.A | _ catch-all *(NEW #175)* |
| 83 | **OrPattern** | LOG.CTL.A | x \| y alternatives *(NEW #176)* |
| 84 | **RestPattern** | LOG.CTL.A | ...rest pattern *(NEW #178)* |
| 85 | DestructPattern | LOG.CTL.A | Destructuring pattern |
| 86 | GuardPattern | LOG.CTL.A | Pattern with guard |

---

## PHASE 3: ORGANIZATION (52 atoms)
*The structure of software - how code is arranged*

### Family 3.1: Aggregates (12)
| # | Name | ID | Description |
|---|------|----|-------------|
| 87 | Class | ORG.AGG.M | Class definition |
| 88 | Struct | ORG.AGG.M | Struct definition |
| 89 | Enum | ORG.AGG.M | Enumeration |
| 90 | Union | ORG.AGG.M | Union type (C/C++) |
| 91 | Record | ORG.AGG.M | Record type |
| 92 | Trait | ORG.AGG.M | Trait definition |
| 93 | **ImplBlock** | ORG.AGG.M | Impl block *(NEW #170)* |
| 94 | **TypeAlias** | ORG.AGG.M | Type alias *(NEW #197)* |
| 95 | Extension | ORG.AGG.M | Type extension |
| 96 | Mixin | ORG.AGG.M | Mixin class |
| 97 | Protocol | ORG.AGG.M | Protocol definition |
| 98 | Namespace | ORG.AGG.M | Namespace block |

### Family 3.2: Modules (8)
| # | Name | ID | Description |
|---|------|----|-------------|
| 99 | Module | ORG.MOD.O | Module definition |
| 100 | Package | ORG.MOD.O | Package/library |
| 101 | ImportStmt | ORG.MOD.O | Import statement |
| 102 | ExportStmt | ORG.MOD.O | Export statement |
| 103 | UseDecl | ORG.MOD.O | Use declaration |
| 104 | RequireStmt | ORG.MOD.O | Require statement |
| 105 | IncludeDir | ORG.MOD.O | Include directive |
| 106 | ExternCrate | ORG.MOD.O | External crate |

### Family 3.3: Files (6)
| # | Name | ID | Description |
|---|------|----|-------------|
| 107 | SourceFile | ORG.FIL.O | Source file |
| 108 | Header | ORG.FIL.O | Header file |
| 109 | ConfigFile | ORG.FIL.O | Configuration file |
| 110 | TestFile | ORG.FIL.O | Test file |
| 111 | SchemaFile | ORG.FIL.O | Schema file |
| 112 | ScriptFile | ORG.FIL.O | Script file |

### Family 3.4: Services/Interfaces (8)
| # | Name | ID | Description |
|---|------|----|-------------|
| 113 | Interface | ORG.SVC.M | Interface definition |
| 114 | AbstractClass | ORG.SVC.M | Abstract class |
| 115 | Contract | ORG.SVC.M | Contract/specification |
| 116 | Endpoint | ORG.SVC.M | API endpoint |
| 117 | EventDef | ORG.SVC.M | Event definition |
| 118 | SignalDef | ORG.SVC.M | Signal definition |
| 119 | SlotDef | ORG.SVC.M | Slot definition |
| 120 | Callback | ORG.SVC.M | Callback definition |

### Family 3.5: Type System (18) *(EXPANDED)*
| # | Name | ID | Description |
|---|------|----|-------------|
| 121 | TypeRef | ORG.TYP.O | Type reference |
| 122 | **GenericParam** | ORG.TYP.O | Generic type parameter *(NEW #193)* |
| 123 | **UnionType** | ORG.TYP.O | Union type X \| Y *(NEW #194)* |
| 124 | **IntersectionType** | ORG.TYP.O | Intersection type X & Y *(NEW #195)* |
| 125 | ArrayType | ORG.TYP.O | Array type |
| 126 | TupleType | ORG.TYP.O | Tuple type |
| 127 | FunctionType | ORG.TYP.O | Function type |
| 128 | OptionalType | ORG.TYP.O | Optional type |
| 129 | NullableType | ORG.TYP.O | Nullable type |
| 130 | MappedType | ORG.TYP.O | Mapped type |
| 131 | ConditionalType | ORG.TYP.O | Conditional type |
| 132 | IndexedType | ORG.TYP.O | Indexed access type |
| 133 | LiteralType | ORG.TYP.O | Literal type |
| 134 | PrimitiveType | ORG.TYP.O | Primitive type |
| 135 | WildcardType | ORG.TYP.O | Wildcard type |
| 136 | Lifetime | ORG.TYP.O | Rust lifetime |
| 137 | TypeConstraint | ORG.TYP.O | Type constraint |
| 138 | InferType | ORG.TYP.O | Inferred type |

---

## PHASE 4: EXECUTION (62 atoms)
*The runtime of software - how code runs*

### Family 4.1: Concurrency (12)
| # | Name | ID | Description |
|---|------|----|-------------|
| 139 | Thread | EXE.WRK.O | Thread |
| 140 | Process | EXE.WRK.O | Process |
| 141 | Goroutine | EXE.WRK.O | Go goroutine |
| 142 | Task | EXE.WRK.O | Async task |
| 143 | Future | EXE.WRK.O | Future/Promise |
| 144 | Channel | EXE.WRK.O | Channel communication |
| 145 | ChannelSend | EXE.WRK.O | Channel send |
| 146 | ChannelSelect | EXE.WRK.O | Channel select |
| 147 | Mutex | EXE.WRK.O | Mutex lock |
| 148 | Semaphore | EXE.WRK.O | Semaphore |
| 149 | AsyncBlock | EXE.WRK.O | Async block |
| 150 | SyncBlock | EXE.WRK.O | Synchronized block |

### Family 4.2: Error Handling (10)
| # | Name | ID | Description |
|---|------|----|-------------|
| 151 | Exception | EXE.HDL.O | Exception type |
| 152 | Error | EXE.HDL.O | Error type |
| 153 | Result | EXE.HDL.O | Result type |
| 154 | Option | EXE.HDL.O | Option/Maybe type |
| 155 | Panic | EXE.HDL.O | Panic/abort |
| 156 | **Defer** | EXE.HDL.O | Defer statement *(NEW #171)* |
| 157 | Finally | EXE.HDL.O | Finally cleanup |
| 158 | Recover | EXE.HDL.O | Panic recovery |
| 159 | Assertion | EXE.HDL.O | Runtime assertion |
| 160 | TryExpr | EXE.HDL.O | Try expression |

### Family 4.3: Memory Management (8)
| # | Name | ID | Description |
|---|------|----|-------------|
| 161 | Allocation | EXE.MEM.O | Memory allocation |
| 162 | Deallocation | EXE.MEM.O | Memory deallocation |
| 163 | Reference | EXE.MEM.O | Reference |
| 164 | Dereference | EXE.MEM.O | Dereference |
| 165 | Borrow | EXE.MEM.O | Rust borrow |
| 166 | Move | EXE.MEM.O | Move semantics |
| 167 | Clone | EXE.MEM.O | Deep copy |
| 168 | Drop | EXE.MEM.O | Destructor/drop |

### Family 4.4: I/O Operations (10)
| # | Name | ID | Description |
|---|------|----|-------------|
| 169 | FileRead | EXE.IO.O | File read |
| 170 | FileWrite | EXE.IO.O | File write |
| 171 | NetworkRead | EXE.IO.O | Network read |
| 172 | NetworkWrite | EXE.IO.O | Network write |
| 173 | StdinRead | EXE.IO.O | Standard input |
| 174 | StdoutWrite | EXE.IO.O | Standard output |
| 175 | StderrWrite | EXE.IO.O | Standard error |
| 176 | DatabaseQuery | EXE.IO.O | Database query |
| 177 | HttpRequest | EXE.IO.O | HTTP request |
| 178 | HttpResponse | EXE.IO.O | HTTP response |

### Family 4.5: Metaprogramming (12) *(EXPANDED)*
| # | Name | ID | Description |
|---|------|----|-------------|
| 179 | MacroDef | EXE.MET.O | Macro definition |
| 180 | **MacroRule** | EXE.MET.O | Macro rule *(NEW #191)* |
| 181 | **Annotation** | EXE.MET.O | Annotation/attribute *(NEW #189)* |
| 182 | Reflection | EXE.MET.O | Runtime reflection |
| 183 | CodeGen | EXE.MET.O | Code generation |
| 184 | Preprocessor | EXE.MET.O | Preprocessor directive |
| 185 | ConditionalCompile | EXE.MET.O | Conditional compilation |
| 186 | Pragma | EXE.MET.O | Compiler pragma |
| 187 | InlineASM | EXE.MET.O | Inline assembly |
| 188 | FFI | EXE.MET.O | Foreign function interface |
| 189 | Intrinsic | EXE.MET.O | Compiler intrinsic |
| 190 | BuiltinCall | EXE.MET.O | Built-in function call |

### Family 4.6: Initialization (10)
| # | Name | ID | Description |
|---|------|----|-------------|
| 191 | StaticInit | EXE.INI.O | Static initializer |
| 192 | LazyInit | EXE.INI.O | Lazy initialization |
| 193 | DefaultInit | EXE.INI.O | Default initialization |
| 194 | CopyInit | EXE.INI.O | Copy initialization |
| 195 | MoveInit | EXE.INI.O | Move initialization |
| 196 | AggregateInit | EXE.INI.O | Aggregate initialization |
| 197 | DesignatedInit | EXE.INI.O | Designated initializer |
| 198 | BraceInit | EXE.INI.O | Brace initialization |
| 199 | ZeroInit | EXE.INI.O | Zero initialization |
| 200 | UninitValue | EXE.INI.O | Uninitialized value |

---

## Summary by Status

| Category | Count |
|----------|-------|
| Original atoms (v1.0) | 167 |
| Cross-validated new (#168-#200) | 18 |
| Expansion atoms | 15 |
| **TOTAL** | **200** |

---

## Phase Distribution

```
DATA (28)        ████████████████░░░░░░░░░░░░░░░░░░░░░░░░ 14%
LOGIC (58)       ████████████████████████████░░░░░░░░░░░░ 29%
ORGANIZATION (52) █████████████████████████░░░░░░░░░░░░░░░ 26%
EXECUTION (62)   ███████████████████████████████░░░░░░░░░ 31%
```

---

> *"200 atoms is not a claim of completeness. It is the current useful working set."*

**Version:** 2.1.0  
**Validated:** 2025-12-26  
**Status:** Working Model (Open, Extensible)
