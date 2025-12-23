# 🌌 The Semantic Dimensions (8D Model with 4D Projection)

## The Insight
A single particle of code exists in **8 semantic dimensions** (see §2.4 of the Standard Model paper).
For practical visualization and simplified reasoning, these project into a **4D model**:

| 4D Projection | Source 8D Dimensions |
|---------------|----------------------|
| **WHAT** | WHAT (167 atom types) |
| **WHERE** | Layer + Boundary |
| **HOW** | State + Effect + Activation + Lifetime |
| **WHY** | Role |

The 4D model is a lossy compression: it combines correlated dimensions for usability.
The 16 Families (Periodic Table) correspond to the **WHAT** dimension.

---

## DIMENSION 1: WHAT (Material Composition)
**Question:** What is this made of?
**Answer:** One of 12 Fundamental Families.

| Family | Examples | Count |
|--------|----------|-------|
| Primitives | `String`, `Integer`, `Boolean` | 8 |
| Expressions | `BinaryOp`, `Call`, `Await` | 8 |
| Statements | `Return`, `Assert`, `Assign` | 10 |
| Control Structures | `If`, `While`, `Match` | 10 |
| Functions | `Def`, `Lambda`, `Async` | 10 |
| Variables | `LocalVar`, `Field`, `Pattern` | 5 |
| Aggregates | `Class`, `Module`, `Struct` | 6 |
| Modules | `Import`, `From`, `Alias` | 4 |
| Types | `Generic`, `Union`, `Annotation` | 4 |
| Executables | `Main`, `Async`, `Thread` | 9 |
| Bits | `BitFlag`, `BitMask` | 2 |
| Files | `Comment` | 1 |

**Status:** ✅ **COMPLETE** (167 atoms cataloged in v14).

---

## DIMENSION 2: HOW (Behavior)
**Question:** What does this DO?
**Answer:** Its computational behavior.

### Axes:
1.  **Purity:** Pure (no side effects) vs Impure (I/O, mutation).
2.  **Timing:** Sync vs Async.
3.  **Effect:** Read-only vs Mutating.
4.  **Return:** Void vs Value-returning.

**Examples:**
*   `PureFunction` → Pure, Sync, Read-only, Value-returning.
*   `Repository.save()` → Impure, Async, Mutating, Void.

**Status:** ⚠️ **PARTIAL** (Tracked in Hadron "Purity" dimension, but needs formalization).

---

## DIMENSION 3: WHERE (Boundary Context)
**Question:** Where does this live in the system?
**Answer:** Its architectural layer and boundary status.

### Axes:
1.  **Layer:** Domain / Application / Infrastructure / Presentation.
2.  **Boundary:** Internal (in-process) vs External (crosses boundary).
3.  **Ownership:** Core (our code) vs Dependency (3rd party).

**Examples:**
*   `Entity::validate()` → Domain, Internal, Core.
*   `APIHandler::handle()` → Presentation, External, Core.

**Status:** ⚠️ **PARTIAL** (Inferred from file paths, but not canonical).

---

## DIMENSION 4: WHY (Semantic Intent)
**Question:** What did the developer MEAN to build?
**Answer:** The pattern, role, or smell it embodies.

### Axes:
1.  **Pattern:** Factory, Strategy, Observer, Singleton, etc.
2.  **Role:** DTO, Service, Repository, Controller, etc. (DDD/Clean).
3.  **Smell:** God Class, Feature Envy, Shotgun Surgery, etc.

**Examples:**
*   A `Class` with 50 methods → **Smell: God Class**.
*   A `Function` returning a new instance → **Pattern: Factory**.

**Status:** ❌ **MISSING** (Requires LLM + heuristics, not AST-detectable).

---

## The Coordinate System
Every particle in your code has a **4D address**:

```
Particle(
  WHAT = "Function",
  HOW = (Pure=True, Async=False, Effect=ReadOnly, Return=Value),
  WHERE = (Layer=Domain, Boundary=Internal, Ownership=Core),
  WHY = (Pattern=None, Role="Repository", Smell=None)
)
```

---

## Roadmap to Completion

| Dimension | Status | Next Step |
|-----------|--------|-----------|
| WHAT | ✅ Complete | Maintain v14 registry |
| HOW | ✅ Integrated | Improve heuristics |
| WHERE | ✅ Integrated | Add more layer rules |
| WHY | ✅ Integrated | Expand pattern library |

**Goal:** ~~Move from a **1D model** (just material) to a **4D model** (full physics).~~
**Status:** ✅ **4D COMPLETE**
