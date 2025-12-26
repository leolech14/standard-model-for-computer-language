# Complete Glossary of the Standard Model

**The definitive list of all concepts, terms, and structures.**

---

## MASTER STRUCTURE

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     THE STANDARD MODEL OF CODE                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   3 PLANES      (modes of existence - ALWAYS ALL 3)                          ║
║   13 LEVELS     (containment hierarchy - EXACTLY ONE per entity)             ║
║   8 LENSES      (perspectives - ALWAYS ALL 8)                                ║
║   N ATOMS       (semantic categories - ONE assigned per Node)                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 1. THE 3 PLANES (Modes of Existence)

Every entity exists in all 3 planes simultaneously.

| # | Plane | Substance | Question | Example |
|---|-------|-----------|----------|---------|
| 1 | **PHYSICAL** | Matter, Energy | Where is it stored? | Bytes on SSD |
| 2 | **VIRTUAL** | Symbols, Structure | What is its form? | `def foo():` |
| 3 | **SEMANTIC** | Meaning, Intent | What does it mean? | "Creates users" |

---

## 2. THE 13 LEVELS (Containment Hierarchy)

Each entity IS exactly one level, CONTAINS lower levels, IS CONTAINED BY higher levels.

| Level | Name | Symbol | Definition | Contains | Example |
|-------|------|--------|------------|----------|---------|
| **L12** | Universe | 🌐 | All code everywhere | Domains | GitHub + all repos |
| **L11** | Domain | 🏛️ | Industry vertical | Organizations | All banking code |
| **L10** | Organization | 🏢 | Company codebase | Platforms | Google monorepo |
| **L9** | Platform | ☁️ | Infrastructure | Ecosystems | AWS, Kubernetes |
| **L8** | Ecosystem | 🔗 | Connected systems | Systems | Microservices cluster |
| **L7** | System | ◇ | Deployable codebase | Packages | `standard-model-of-code` |
| **L6** | Package | 📁 | Module/folder | Files | `core/` directory |
| **L5** | File | 📄 | Source file | Containers, Nodes | `atom_classifier.py` |
| **L4** | Container | □ | Class/struct | Nodes, Properties | `class AtomClassifier` |
| **L3** | **Node** ★ | ● | Function/method | Blocks | `def classify()` |
| **L2** | Block | ▬ | Control structure | Statements | `if x > 0:` |
| **L1** | Statement | ─ | Instruction | Tokens | `return result` |
| **L0** | Token | · | Lexical unit | Characters | `def`, `if`, `(` |

### Operational Boundaries

| Zone | Levels | What We Do |
|------|--------|------------|
| MACRO | L8-L12 | Beyond our scope |
| **OPERATIONAL** | L3-L7 | **We classify these** |
| SYNTACTIC | L0-L2 | Inside the node |

---

## 3. THE 8 LENSES (Perspectives for Understanding)

Every entity can be viewed through all 8 lenses.

| # | Lens | Question | What It Reveals |
|---|------|----------|-----------------|
| 1 | **Identity** | What is it called? | Name, path, signature |
| 2 | **Ontology** | What exists? | Entity type, properties |
| 3 | **Classification** | What kind is it? | Role, category, atom type |
| 4 | **Composition** | How is it structured? | Parts, container, nesting |
| 5 | **Relationships** | How is it connected? | Calls, imports, inherits |
| 6 | **Transformation** | What does it do? | Input → Process → Output |
| 7 | **Semantics** | What does it mean? | Purpose, intent, responsibility |
| 8 | **Epistemology** | How certain are we? | Confidence, evidence, source |

---

## 4. THE ATOM CATALOG (Semantic Categories)

Atoms are the role types that Nodes can be classified as.

### Query Atoms (Read Data)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Query** | Retrieves data | `get*`, `find*`, `fetch*` | `getUserById()` |
| **Finder** | Searches for entities | `find*`, `search*` | `findByEmail()` |
| **Loader** | Loads from storage | `load*`, `read*` | `loadConfig()` |

### Command Atoms (Write Data)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Command** | Modifies state | `set*`, `update*`, `delete*` | `updateUser()` |
| **Creator** | Creates new entities | `create*`, `make*`, `build*` | `createUser()` |
| **Mutator** | Changes existing | `update*`, `modify*` | `updateEmail()` |
| **Destroyer** | Removes entities | `delete*`, `remove*`, `destroy*` | `deleteUser()` |

### Factory Atoms (Create Instances)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Factory** | Creates instances | `*Factory`, `create*` | `UserFactory.create()` |
| **Builder** | Builds complex objects | `*Builder`, `build*` | `QueryBuilder.build()` |

### Storage Atoms (Persist Data)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Repository** | Stores/retrieves entities | `*Repository`, `*Repo` | `UserRepository.save()` |
| **Store** | State container | `*Store` | `UserStore.get()` |
| **Cache** | Temporary storage | `*Cache`, `cache*` | `CacheManager.get()` |

### Orchestration Atoms (Coordinate Work)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Service** | Business logic | `*Service` | `UserService.register()` |
| **Controller** | Request handling | `*Controller`, `handle*` | `UserController.get()` |
| **Manager** | Coordinates resources | `*Manager` | `SessionManager.create()` |
| **Orchestrator** | Complex workflows | `*Orchestrator` | `PaymentOrchestrator.run()` |

### Validation Atoms (Check Correctness)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Validator** | Validates input | `validate*`, `*Validator` | `validateEmail()` |
| **Guard** | Protects access | `*Guard`, `check*` | `AuthGuard.check()` |
| **Asserter** | Enforces conditions | `assert*`, `ensure*` | `ensureValid()` |

### Transformation Atoms (Convert Data)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Transformer** | Converts formats | `*Transformer`, `to*`, `from*` | `toDTO()` |
| **Mapper** | Maps between types | `*Mapper`, `map*` | `UserMapper.toEntity()` |
| **Serializer** | Serializes data | `*Serializer`, `serialize*` | `JsonSerializer.write()` |
| **Parser** | Parses input | `*Parser`, `parse*` | `parseJSON()` |

### Event Atoms (React to Events)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Handler** | Handles events | `*Handler`, `handle*`, `on*` | `onUserCreated()` |
| **Listener** | Listens for events | `*Listener`, `listen*` | `EventListener.on()` |
| **Subscriber** | Subscribes to streams | `*Subscriber`, `subscribe*` | `subscribe()` |
| **Emitter** | Emits events | `*Emitter`, `emit*` | `emit()` |

### Utility Atoms (Helper Functions)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Utility** | General helper | `*Utils`, `*Helper` | `formatDate()` |
| **Formatter** | Formats output | `format*`, `*Formatter` | `formatCurrency()` |

### Internal Atoms (Implementation Details)

| Atom | Purpose | Name Pattern | Example |
|------|---------|--------------|---------|
| **Internal** | Private/impl | `_*`, `__*` (not dunder) | `_buildQuery()` |
| **Lifecycle** | Init/dispose | `__init__`, `dispose`, `setup` | `__init__()` |
| **Callback** | Callback function | `*Callback`, `cb*` | `onComplete()` |

### Unknown Atom

| Atom | Purpose | When Used |
|------|---------|-----------|
| **Unknown** | Unclassified | No pattern match, low confidence |

---

## 5. CORE ENTITY DEFINITIONS

| Term | Definition | Level |
|------|------------|-------|
| **Entity** | Any identifiable unit in the hierarchy | Any |
| **Node** | A function or method — the fundamental unit | L3 |
| **Container** | A class or struct that holds Nodes | L4 |
| **Particle** | A Node with classification attached (Node + Atom + Confidence) | L3 |
| **Edge** | A relationship between entities (call, import, inherit) | Cross-level |

---

## 6. RELATIONSHIP TYPES (Edges)

| Edge Type | Direction | Meaning | Example |
|-----------|-----------|---------|---------|
| **calls** | A → B | A invokes B | `main() calls init()` |
| **imports** | A → B | A depends on B | `app.py imports utils` |
| **inherits** | A → B | A extends B | `Dog inherits Animal` |
| **implements** | A → B | A realizes B | `UserRepo implements IRepo` |
| **contains** | A → B | A holds B | `Class contains method` |
| **uses** | A → B | A references B | `handler uses logger` |

---

## 7. CLASSIFICATION SOURCES

How confidence is derived:

| Source | Confidence | Example |
|--------|------------|---------|
| **Ground Truth** | 100% | Manually verified |
| **Name Pattern** | 60-90% | `get*` → Query |
| **Decorator** | 85-95% | `@app.route` → Controller |
| **Inheritance** | 80-95% | `extends Repository` |
| **Graph Inference** | 50-70% | Called by Controller → likely Service |
| **LLM Fallback** | 40-60% | AI classification |
| **Unknown** | 0-30% | No match |

---

## 8. CONFIDENCE LEVELS

| Range | Name | Meaning |
|-------|------|---------|
| 95-100% | **Certain** | Ground truth or very strong evidence |
| 80-94% | **High** | Strong pattern match |
| 60-79% | **Medium** | Pattern match with some ambiguity |
| 40-59% | **Low** | Weak evidence or inference |
| 0-39% | **Uncertain** | Needs human review |

---

## SUMMARY COUNT

| Category | Count |
|----------|-------|
| **Planes** | 3 |
| **Levels** | 13 |
| **Lenses** | 8 |
| **Atom Categories** | ~30+ |
| **Edge Types** | 6 |
| **Confidence Sources** | 6 |

---

> This is the complete glossary. All terms are defined. The model is closed.
