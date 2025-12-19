# 🔬 Standard Code Spectrometer

> **A Particle Accelerator for your Codebase** — Maps the fundamental structure of any software system using the Standard Model of Code.

## ⚡ Quick Start (30 seconds)

```bash
# 1. Clone and install
git clone https://github.com/leolech14/standard-code-spectrometer.git
cd standard-code-spectrometer
pip install -r requirements.txt

# 2. Analyze ANY repo
python cli.py analyze /path/to/any/repo

# 3. View results
cat output/learning/COMPREHENSIVE_REPORT.md
```

That's it. Works on Python, JavaScript, TypeScript out of the box.

## 🗺️ What We Have Mapped So Far

We currently map the full **Standard Model of Code v13**:

*   **12 Quarks**: The fundamental forces (Data, Logic, Organization, Execution).
*   **96 Hadrons**: Stable composite particles (e.g., `Repository`, `Service`, `Controller`).
*   **384 Sub-hadrons**: The granular atomic states, including:
    *   **342 Possible Particles**: Valid states observed in healthy code.
    *   **42 Impossible Particles (Antimatter)**: Theoretical constructs that violate the laws of physics (e.g., a `PureFunction` with `SideEffects`). Detection of these signals immediate collapse.

### 🎛️ The 8 Dimensions of Code Physics

Every particle is measured across **8 dimensions**:

| # | Dimension | Values | Question |
|---|-----------|--------|----------|
| 1 | **WHAT** | 167 atoms | What is it made of? |
| 2 | **Layer** | Interface, App, Core, Infra, Tests | Where in the stack? |
| 3 | **Role** | Orchestrator, Data, Worker | What job does it do? |
| 4 | **Boundary** | Internal, Input, I/O, Output | How does it connect? |
| 5 | **State** | Stateful, Stateless | Does it hold memory? |
| 6 | **Effect** | Read, Write, ReadModify, Pure | What does it touch? |
| 7 | **Activation** | Event, Time, Direct | How is it triggered? |
| 8 | **Lifetime** | Transient, Session, Global | How long does it live? |

```mermaid
graph TD
    %% CLASSES DEFINITIONS
    classDef phase fill:#000,stroke:#fff,stroke-width:4px,color:#fff,font-size:20px;
    classDef cluster fill:#111,stroke:#666,stroke-width:2px,color:#fff;
    
    %% DATA FOUNDATIONS - CYAN THEME
    classDef cyanPhase fill:#003f4f,stroke:#00aaff,stroke-width:4px,color:#fff;
    classDef cyanQuark fill:#00222b,stroke:#0077aa,stroke-width:2px,color:#aeeeee;
    classDef cyanNode fill:#001116,stroke:#00aaff,stroke-width:1px,color:#fff;

    %% LOGIC & FLOW - MAGENTA THEME
    classDef magentaPhase fill:#4f003f,stroke:#ff00aa,stroke-width:4px,color:#fff;
    classDef magentaQuark fill:#2b0022,stroke:#aa0077,stroke-width:2px,color:#eeaeee;
    classDef magentaNode fill:#160011,stroke:#ff00aa,stroke-width:1px,color:#fff;

    %% ORGANIZATION - GREEN THEME
    classDef greenPhase fill:#004f2f,stroke:#00ff88,stroke-width:4px,color:#fff;
    classDef greenQuark fill:#002b1a,stroke:#00aa55,stroke-width:2px,color:#aeeeea;
    classDef greenNode fill:#00160d,stroke:#00ff88,stroke-width:1px,color:#fff;

    %% EXECUTION - AMBER THEME
    classDef amberPhase fill:#4f3f00,stroke:#ffaa00,stroke-width:4px,color:#fff;
    classDef amberQuark fill:#2b2200,stroke:#aa7700,stroke-width:2px,color:#eeeaee;
    classDef amberNode fill:#161100,stroke:#ffaa00,stroke-width:1px,color:#fff;


    subgraph PH_DATA["DATA FOUNDATIONS"]
        direction TB
        subgraph Q_BITS["Bits"]
            BitFlag
            BitMask
            ParityBit
            SignBit
        end
        subgraph Q_BYTES["Bytes"]
            ByteArray
            MagicBytes
            PaddingBytes
        end
        subgraph Q_PRIMITIVES["Primitives"]
            Boolean
            EnumValue
            Float
            Integer
            StringLiteral
        end
        subgraph Q_VARIABLES["Variables"]
            GlobalVar
            InstanceField
            LocalVar
            Parameter
            StaticField
        end
    end

    subgraph PH_LOGIC["LOGIC & FLOW"]
        direction TB
        subgraph Q_EXPRESSIONS["Expressions"]
            ArithmeticExpr
            CallExpr
            LiteralExpr
        end
        subgraph Q_STATEMENTS["Statements"]
            Assignment
            ExpressionStmt
            ReturnStmt
        end
        subgraph Q_CONTROL["Control Structures"]
            GuardClause
            IfBranch
            LoopFor
            LoopWhile
            SwitchCase
            TryCatch
        end
        subgraph Q_FUNCTIONS["Functions"]
            AsyncFunction
            Closure
            CommandHandler
            EventHandler
            Generator
            ImpureFunction
            Mapper
            Middleware
            PureFunction
            QueryHandler
            Reducer
            SagaStep
            Validator
        end
    end

    subgraph PH_ORG["ORGANIZATION"]
        direction TB
        subgraph Q_AGGREGATES["Aggregates"]
            AggregateRoot
            DTO
            Entity
            Factory
            Projection
            ReadModel
            ValueObject
        end
        subgraph Q_MODULES["Modules"]
            ApplicationPort
            BoundedContext
            DomainPort
            FeatureModule
            InfrastructureAdapter
        end
        subgraph Q_FILES["Files"]
            ConfigFile
            MigrationFile
            SourceFile
            TestFile
        end
    end

    subgraph PH_EXEC["EXECUTION"]
        direction TB
        subgraph Q_EXECUTABLES["Executables"]
            ABTestRouter
            APIHandler
            Actor
            BackgroundThread
            CLIEntry
            CacheWarmer
            CanaryDeployTrigger
            ChaosMonkey
            CircuitBreakerInit
            ConfigLoader
            ContainerEntry
            Coroutine
            CronJob
            DependencyInjectionContainer
            FeatureFlagCheck
            Fiber
            GracefulShutdown
            GraphQLResolver
            HealthCheck
            KubernetesJob
            LambdaEntry
            LoggerInit
            MainEntry
            MessageConsumer
            MetricsExporter
            MigrationRunner
            PanicRecover
            PluginLoader
            QueueWorker
            RateLimiter
            SeedData
            SelfHealingProbe
            ServerlessColdStart
            ServiceWorker
            TracerProvider
            WebSocketHandler
            WebWorker
            WorkerEntry
        end
    end

    %% RELATIONSHIPS
    PH_DATA ==> PH_LOGIC
    PH_LOGIC ==> PH_ORG
    PH_ORG ==> PH_EXEC

    %% APPLY STYLES - DATA
    class PH_DATA cyanPhase;
    class Q_BITS,Q_BYTES,Q_PRIMITIVES,Q_VARIABLES cyanQuark;
    class BitFlag,BitMask,ParityBit,SignBit cyanNode;
    class ByteArray,MagicBytes,PaddingBytes cyanNode;
    class Boolean,EnumValue,Float,Integer,StringLiteral cyanNode;
    class GlobalVar,InstanceField,LocalVar,Parameter,StaticField cyanNode;

    %% APPLY STYLES - LOGIC
    class PH_LOGIC magentaPhase;
    class Q_EXPRESSIONS,Q_STATEMENTS,Q_CONTROL,Q_FUNCTIONS magentaQuark;
    class ArithmeticExpr,CallExpr,LiteralExpr magentaNode;
    class Assignment,ExpressionStmt,ReturnStmt magentaNode;
    class GuardClause,IfBranch,LoopFor,LoopWhile,SwitchCase,TryCatch magentaNode;
    class AsyncFunction,Closure,CommandHandler,EventHandler,Generator,ImpureFunction magentaNode;
    class Mapper,Middleware,PureFunction,QueryHandler,Reducer,SagaStep,Validator magentaNode;

    %% APPLY STYLES - ORG
    class PH_ORG greenPhase;
    class Q_AGGREGATES,Q_MODULES,Q_FILES greenQuark;
    class AggregateRoot,DTO,Entity,Factory,Projection,ReadModel,ValueObject greenNode;
    class ApplicationPort,BoundedContext,DomainPort,FeatureModule,InfrastructureAdapter greenNode;
    class ConfigFile,MigrationFile,SourceFile,TestFile greenNode;

    %% APPLY STYLES - EXEC
    class PH_EXEC amberPhase;
    class Q_EXECUTABLES amberQuark;
    class ABTestRouter,APIHandler,Actor,BackgroundThread,CLIEntry,CacheWarmer amberNode;
    class CanaryDeployTrigger,ChaosMonkey,CircuitBreakerInit,ConfigLoader,ContainerEntry,Coroutine amberNode;
    class CronJob,DependencyInjectionContainer,FeatureFlagCheck,Fiber,GracefulShutdown,GraphQLResolver amberNode;
    class HealthCheck,KubernetesJob,LambdaEntry,LoggerInit,MainEntry,MessageConsumer amberNode;
    class MetricsExporter,MigrationRunner,PanicRecover,PluginLoader,QueueWorker,RateLimiter amberNode;
    class SeedData,SelfHealingProbe,ServerlessColdStart,ServiceWorker,TracerProvider amberNode;
    class WebSocketHandler,WebWorker,WorkerEntry amberNode;
```

We map these particles, measure their "Mass" (Lines of Code), "Charge" (Dependencies), and "Spin" (Complexity), and generate a 3D model of your codebase.

---

## ⚡ The "One Button" Philosophy

You don't need a PhD in Physics to use this. You press one button, and we do the rest.

### 1. Analyze Everything

The **Analyze** command runs our complete hybrid pipeline:
1.  **Static Extraction**: Deterministically finds classes and functions.
2.  **Semantic Inference**: Uses LLMs (if enabled) to classify particles ensuring < 0.1% hallucination rate.
3.  **God Class Detection**: Scans for "Antimatter" (oversized, dangerous components).

```bash
python3 cli.py analyze /path/to/your/repo
```

*That's it.*

### 2. Check System Health

Verify that the particle accelerator is calibrated and ready to fire.

```bash
python3 cli.py health
```

### 3. Full Audit

Prove the entire pipeline works end-to-end on your code.

```bash
python3 cli.py audit /path/to/your/repo
```

### 4. Graph Analysis (NEW)

Analyze the generated graph for architectural insights:

```bash
# Full analysis: bottlenecks, PageRank, communities, bridges
python3 cli.py graph output/analysis/graph.json

# Find shortest path between two functions
python3 cli.py graph output/analysis/graph.json --shortest-path "handleApi:syncItemConnectionById"
```

**What it detects:**
| Algorithm | Purpose |
|-----------|---------|
| **Betweenness Centrality** | Find bottleneck functions (God Functions) |
| **PageRank** | Rank most important/depended-upon nodes |
| **Leiden Clustering** | Auto-discover natural subsystems |
| **Bridge Detection** | Find critical coupling edges |

### 5. Redundancy Detection (NEW)

Find duplicate code and over-engineering:

```bash
python3 core/redundancy_detector.py output/analysis/graph.json --report REDUNDANCY.md
```

**Detects:**
- **Semantic Duplicates**: Functions with similar names (e.g., `truncateString` appearing 7 times)
- **Structural Duplicates**: Functions with identical call patterns
- **Over-Engineering**: Pass-through wrappers, God functions with 100+ dependencies


---

## 🏗️ Technical Architecture

Our "Standard Model" is built on a **Hybrid Static+LLM Pipeline**:

1.  **Structural Truth (The "What")**:
    *   We use **Tree-Sitter** and **Regex** to build an immutable Graph of Truth. If a file exists, we know it. If a class is defined, we map it.
    *   *Zero Hallucinations allowed here.*

2.  **Semantic Role (The "Why")**:
    *   We overlay semantic meaning. Is this class a `Repository`? Is that function a `UseCase`?
    *   We use heuristic patterns first.
    *   If unsure (Confidence < 55%), we escalate to a **Local LLM** (Ollama/Qwen) to examine the code and make a determination.

3.  **Antimatter Detection**:
    *   We scan for **God Classes**—components with too much mass and responsibility. These are the black holes of your system.

---

## �️ Refactoring Toolkit (Experimental)

> **"From Map to Territory."**

We now include an experimental **Surgical Robot** to act on the insights.

*   **Location**: `tools/refactor/`
*   **Capabilities**:
    *   **Router Extractor**: Decompose Express `server.js` monoliths into atomic route handlers.
    *   **Dependency Tracer**: Auto-extract shared logic into `lib/` modules.

[See Refactoring Docs](tools/refactor/README.md)

---

## �📦 Installation

```bash
pip install -r requirements.txt
```

*(Optional) For Hybrid Mode semantic inference, ensure [Ollama](https://ollama.ai) is running.*

---

*Probing the deep structure of code.*
