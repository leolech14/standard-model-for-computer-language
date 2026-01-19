[Home](../README.md) > [Docs](./README.md) > **Atoms Reference**

---

# 🔬 Standard Code Model
## Atom Reference (Open Schema)

> **Note:** This is a reference of the atom ontology organized by 4 phases and 16 families.
> The schema is OPEN and continuously evolving. See `schema/fixed/atoms.json` for definitions.

---

## DATA Phase
> Data foundations - the matter of software

### Bits

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 1 | **BitFlag** | `DAT.BIT.A` | Single boolean flag |
| 2 | **BitMask** | `DAT.BIT.A` | Binary mask for operations |
| 3 | **ParityBit** | `DAT.BIT.A` | Error detection bit |
| 4 | **SignBit** | `DAT.BIT.A` | Numeric sign indicator |

### Bytes

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 5 | **ByteArray** | `DAT.BYT.A` | Raw byte sequence |
| 6 | **MagicBytes** | `DAT.BYT.A` | File format identifier |
| 7 | **PaddingBytes** | `DAT.BYT.A` | Alignment padding |
| 8 | **Buffer** | `DAT.BYT.A` | In-memory byte buffer |

### Primitives

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 9 | **Boolean** | `DAT.PRM.A` | True/false value |
| 10 | **Integer** | `DAT.PRM.A` | Whole number |
| 11 | **Float** | `DAT.PRM.A` | Decimal number |
| 12 | **String** | `DAT.PRM.A` | Text value |
| 13 | **Null** | `DAT.PRM.A` | Absence of value |
| 14 | **Undefined** | `DAT.PRM.A` | Uninitialized value |
| 15 | **Symbol** | `DAT.PRM.A` | Unique identifier |
| 16 | **BigInt** | `DAT.PRM.A` | Arbitrary precision integer |
| 17 | **Enum** | `DAT.PRM.A` | Enumeration value |
| 18 | **Char** | `DAT.PRM.A` | Single character |

### Variables

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 19 | **LocalVar** | `DAT.VAR.A` | Function-scoped variable |
| 20 | **GlobalVar** | `DAT.VAR.A` | Module/global scope variable |
| 21 | **Parameter** | `DAT.VAR.A` | Function parameter |
| 22 | **InstanceField** | `DAT.VAR.A` | Object instance property |
| 23 | **StaticField** | `DAT.VAR.A` | Class-level property |
| 24 | **Constant** | `DAT.VAR.A` | Immutable binding |
| 25 | **EnvironmentVar** | `DAT.VAR.A` | Environment variable reference |
| 26 | **ConfigValue** | `DAT.VAR.A` | Configuration parameter |

## LOGIC Phase
> Logic & flow - the forces of software

### Expressions

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 27 | **LiteralExpr** | `LOG.EXP.A` | Literal value expression |
| 28 | **IdentifierExpr** | `LOG.EXP.A` | Variable reference |
| 29 | **BinaryExpr** | `LOG.EXP.A` | Two-operand operation |
| 30 | **UnaryExpr** | `LOG.EXP.A` | Single-operand operation |
| 31 | **TernaryExpr** | `LOG.EXP.A` | Conditional expression |
| 32 | **CallExpr** | `LOG.EXP.A` | Function invocation |
| 33 | **MemberExpr** | `LOG.EXP.A` | Property access |
| 34 | **IndexExpr** | `LOG.EXP.A` | Array/map access |
| 35 | **ArrowExpr** | `LOG.EXP.A` | Arrow function expression |
| 36 | **AwaitExpr** | `LOG.EXP.A` | Promise await |
| 37 | **YieldExpr** | `LOG.EXP.A` | Generator yield |
| 38 | **SpreadExpr** | `LOG.EXP.A` | Spread operator |
| 39 | **TemplateExpr** | `LOG.EXP.A` | Template literal |
| 40 | **NewExpr** | `LOG.EXP.A` | Constructor call |
| 41 | **TypeofExpr** | `LOG.EXP.A` | Type introspection |

### Statements

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 42 | **Assignment** | `LOG.STM.A` | Variable assignment |
| 43 | **Declaration** | `LOG.STM.A` | Variable declaration |
| 44 | **ReturnStmt** | `LOG.STM.A` | Function return |
| 45 | **ThrowStmt** | `LOG.STM.A` | Exception throw |
| 46 | **BreakStmt** | `LOG.STM.A` | Loop/switch break |
| 47 | **ContinueStmt** | `LOG.STM.A` | Loop continue |
| 48 | **ExpressionStmt** | `LOG.STM.A` | Expression as statement |
| 49 | **EmptyStmt** | `LOG.STM.A` | No-op statement |
| 50 | **DebuggerStmt** | `LOG.STM.A` | Debugger breakpoint |
| 51 | **LabeledStmt** | `LOG.STM.A` | Labeled statement |

### Control

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 52 | **IfBranch** | `LOG.CTL.A` | Conditional branch |
| 53 | **ElseBranch** | `LOG.CTL.A` | Alternative branch |
| 54 | **SwitchCase** | `LOG.CTL.A` | Switch case clause |
| 55 | **DefaultCase** | `LOG.CTL.A` | Switch default |
| 56 | **ForLoop** | `LOG.CTL.A` | For iteration |
| 57 | **ForInLoop** | `LOG.CTL.A` | For-in iteration |
| 58 | **ForOfLoop** | `LOG.CTL.A` | For-of iteration |
| 59 | **WhileLoop** | `LOG.CTL.A` | While iteration |
| 60 | **DoWhileLoop** | `LOG.CTL.A` | Do-while iteration |
| 61 | **TryBlock** | `LOG.CTL.A` | Exception handling try |
| 62 | **CatchClause** | `LOG.CTL.A` | Exception handler |
| 63 | **FinallyClause** | `LOG.CTL.A` | Cleanup block |
| 64 | **GuardClause** | `LOG.CTL.A` | Early return guard |
| 65 | **WithBlock** | `LOG.CTL.A` | With statement (deprecated) |

### Functions

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 66 | **PureFunction** | `LOG.FNC.M` | No side effects, deterministic |
| 67 | **ImpureFunction** | `LOG.FNC.M` | Has side effects |
| 68 | **AsyncFunction** | `LOG.FNC.M` | Returns promise |
| 69 | **Generator** | `LOG.FNC.M` | Yields values |
| 70 | **AsyncGenerator** | `LOG.FNC.M` | Async iteration |
| 71 | **Constructor** | `LOG.FNC.M` | Object initializer |
| 72 | **Method** | `LOG.FNC.M` | Class method |
| 73 | **Getter** | `LOG.FNC.M` | Property getter |
| 74 | **Setter** | `LOG.FNC.M` | Property setter |
| 75 | **Lambda** | `LOG.FNC.M` | Anonymous function |
| 76 | **Closure** | `LOG.FNC.M` | Captures outer scope |
| 77 | **Callback** | `LOG.FNC.M` | Passed as argument |
| 78 | **Middleware** | `LOG.FNC.M` | Request/response interceptor |
| 79 | **Decorator** | `LOG.FNC.M` | Function wrapper |
| 80 | **Hook** | `LOG.FNC.M` | Lifecycle hook |
| 81 | **Validator** | `LOG.FNC.M` | Input validation |
| 82 | **Mapper** | `LOG.FNC.M` | Data transformation |
| 83 | **Reducer** | `LOG.FNC.M` | Aggregation function |
| 84 | **Predicate** | `LOG.FNC.M` | Boolean test function |
| 85 | **Comparator** | `LOG.FNC.M` | Ordering function |
| 86 | **Factory** | `LOG.FNC.M` | Object creation |
| 87 | **Builder** | `LOG.FNC.M` | Fluent construction |

## ORGANIZATION Phase
> Organization - the structure of software

### Aggregates

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 88 | **Entity** | `ORG.AGG.M` | Identity-based domain object |
| 89 | **ValueObject** | `ORG.AGG.M` | Immutable value container |
| 90 | **AggregateRoot** | `ORG.AGG.M` | Consistency boundary |
| 91 | **DTO** | `ORG.AGG.M` | Data transfer object |
| 92 | **ViewModel** | `ORG.AGG.M` | UI-specific model |
| 93 | **ReadModel** | `ORG.AGG.M` | Query-optimized projection |
| 94 | **Command** | `ORG.AGG.M` | Intent to change state |
| 95 | **Query** | `ORG.AGG.M` | Request for data |
| 96 | **Event** | `ORG.AGG.M` | Something that happened |
| 97 | **Projection** | `ORG.AGG.M` | Event-sourced view |
| 98 | **Specification** | `ORG.AGG.M` | Business rule |
| 99 | **Policy** | `ORG.AGG.M` | Decision logic |
| 100 | **Enum** | `ORG.AGG.M` | Finite value set |
| 101 | **Record** | `ORG.AGG.M` | Immutable data record |
| 102 | **Tuple** | `ORG.AGG.M` | Fixed-size collection |
| 103 | **Union** | `ORG.AGG.M` | Type union/variant |

### Services

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 104 | **DomainService** | `ORG.SVC.M` | Domain logic without state |
| 105 | **ApplicationService** | `ORG.SVC.M` | Use case orchestration |
| 106 | **InfrastructureService** | `ORG.SVC.M` | External system adapter |
| 107 | **Repository** | `ORG.SVC.M` | Aggregate persistence |
| 108 | **Gateway** | `ORG.SVC.M` | External API client |
| 109 | **Adapter** | `ORG.SVC.M` | Port implementation |
| 110 | **Facade** | `ORG.SVC.M` | Simplified interface |
| 111 | **Proxy** | `ORG.SVC.M` | Access control wrapper |
| 112 | **Mediator** | `ORG.SVC.M` | Component coordination |
| 113 | **Observer** | `ORG.SVC.M` | Event subscription |
| 114 | **Strategy** | `ORG.SVC.M` | Interchangeable algorithm |
| 115 | **State** | `ORG.SVC.M` | State machine behavior |

### Modules

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 116 | **FeatureModule** | `ORG.MOD.O` | Self-contained feature |
| 117 | **SharedModule** | `ORG.MOD.O` | Cross-cutting utilities |
| 118 | **CoreModule** | `ORG.MOD.O` | Essential abstractions |
| 119 | **InfraModule** | `ORG.MOD.O` | External integrations |
| 120 | **TestModule** | `ORG.MOD.O` | Test utilities |
| 121 | **ConfigModule** | `ORG.MOD.O` | Configuration |
| 122 | **Package** | `ORG.MOD.O` | Published package |
| 123 | **Namespace** | `ORG.MOD.O` | Logical grouping |
| 124 | **Layer** | `ORG.MOD.O` | Architectural layer |

### Files

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 125 | **SourceFile** | `ORG.FIL.O` | Code file |
| 126 | **TestFile** | `ORG.FIL.O` | Test suite file |
| 127 | **ConfigFile** | `ORG.FIL.O` | Configuration file |
| 128 | **SchemaFile** | `ORG.FIL.O` | Data schema definition |
| 129 | **MigrationFile** | `ORG.FIL.O` | Database migration |
| 130 | **Script** | `ORG.FIL.O` | Standalone script |
| 131 | **EntryPoint** | `ORG.FIL.O` | Application entry |
| 132 | **TypeDef** | `ORG.FIL.O` | Type definitions |

## EXECUTION Phase
> Execution - the dynamics of software

### Handlers

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 133 | **APIHandler** | `EXE.HDL.O` | HTTP endpoint handler |
| 134 | **WebSocketHandler** | `EXE.HDL.O` | WebSocket connection |
| 135 | **GraphQLResolver** | `EXE.HDL.O` | GraphQL field resolver |
| 136 | **EventHandler** | `EXE.HDL.O` | Event subscriber |
| 137 | **CommandHandler** | `EXE.HDL.O` | CQRS command handler |
| 138 | **QueryHandler** | `EXE.HDL.O` | CQRS query handler |
| 139 | **MessageConsumer** | `EXE.HDL.O` | Queue message handler |
| 140 | **WebhookHandler** | `EXE.HDL.O` | Webhook receiver |
| 141 | **ErrorHandler** | `EXE.HDL.O` | Error boundary |

### Workers

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 142 | **CronJob** | `EXE.WRK.O` | Scheduled task |
| 143 | **QueueWorker** | `EXE.WRK.O` | Background job processor |
| 144 | **BatchProcessor** | `EXE.WRK.O` | Bulk data processing |
| 145 | **StreamProcessor** | `EXE.WRK.O` | Real-time data pipeline |
| 146 | **MigrationRunner** | `EXE.WRK.O` | Database migration executor |
| 147 | **SeedRunner** | `EXE.WRK.O` | Data seeding |
| 148 | **CacheWarmer** | `EXE.WRK.O` | Cache initialization |
| 149 | **Indexer** | `EXE.WRK.O` | Search indexing |

### Initializers

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 150 | **MainEntry** | `EXE.INI.O` | Application main() |
| 151 | **ServerBootstrap** | `EXE.INI.O` | Server startup |
| 152 | **DIContainer** | `EXE.INI.O` | Dependency injection setup |
| 153 | **ConfigLoader** | `EXE.INI.O` | Config initialization |
| 154 | **LoggerInit** | `EXE.INI.O` | Logging setup |
| 155 | **DatabaseInit** | `EXE.INI.O` | DB connection setup |
| 156 | **CacheInit** | `EXE.INI.O` | Cache connection |
| 157 | **PluginLoader** | `EXE.INI.O` | Plugin initialization |

### Probes

| # | Atom | ID | Description |
|--:|------|-------|-------------|
| 158 | **HealthCheck** | `EXE.PRB.O` | Liveness/readiness probe |
| 159 | **MetricsExporter** | `EXE.PRB.O` | Prometheus/metrics |
| 160 | **TracerProvider** | `EXE.PRB.O` | Distributed tracing |
| 161 | **CircuitBreaker** | `EXE.PRB.O` | Fault tolerance |
| 162 | **RateLimiter** | `EXE.PRB.O` | Request throttling |
| 163 | **FeatureFlag** | `EXE.PRB.O` | Feature toggle check |
| 164 | **AuditLogger** | `EXE.PRB.O` | Audit trail |
| 165 | **GracefulShutdown** | `EXE.PRB.O` | Clean termination |
| 166 | **TestDouble** | `EXE.PRB.O` | Mock/stub for testing |
| 167 | **Fixture** | `EXE.PRB.O` | Test data setup |

---
**Total: 167 atoms across 4 phases and 16 families**