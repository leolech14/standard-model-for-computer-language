# Canonical Hierarchy of Code

**The complete, true, and verified hierarchy of code structure.**

---

## THE 3 REALMS (Modes of Existence)

Every level exists simultaneously in THREE realms. These are not levels — they are **dimensions** that cross-cut all levels.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           THE THREE REALMS                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────────────────────────────────────────────────────────────┐     ║
║   │                         SEMANTIC                                    │     ║
║   │                         (Meaning)                                   │     ║
║   │                                                                     │     ║
║   │   Purpose, Intent, Role, Relationships, Understanding              │     ║
║   │   "What does it MEAN?"                                              │     ║
║   │                                                                     │     ║
║   │   ┌───────────────────────────────────────────────────────────┐     │     ║
║   │   │                       VIRTUAL                             │     │     ║
║   │   │                       (Structure)                         │     │     ║
║   │   │                                                           │     │     ║
║   │   │   Symbols, AST, Files, Objects, Paths, References         │     │     ║
║   │   │   "What is its STRUCTURE?"                                │     │     ║
║   │   │                                                           │     │     ║
║   │   │   ┌─────────────────────────────────────────────────┐     │     │     ║
║   │   │   │                   PHYSICAL                      │     │     │     ║
║   │   │   │                   (Matter)                      │     │     │     ║
║   │   │   │                                                 │     │     │     ║
║   │   │   │   Bytes, Electrons, Disk, RAM, Network          │     │     │     ║
║   │   │   │   "Where is it STORED?"                         │     │     │     ║
║   │   │   │                                                 │     │     │     ║
║   │   │   └─────────────────────────────────────────────────┘     │     │     ║
║   │   └───────────────────────────────────────────────────────────┘     │     ║
║   └─────────────────────────────────────────────────────────────────────┘     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### REALM DEFINITIONS

| Realm | Substance | Question | Example (for a function) |
|-------|-----------|----------|--------------------------|
| **PHYSICAL** | Matter, Energy | Where is it stored? | Bytes at sector 4096 on SSD |
| **VIRTUAL** | Symbols, Structure | What is its form? | `def getUserById(id):` at line 42 |
| **SEMANTIC** | Meaning, Intent | What does it mean? | "Retrieves a user by ID from database" |

### HOW REALMS RELATE

```
PHYSICAL  ─encoding─►  VIRTUAL  ─interpretation─►  SEMANTIC
(bytes)                (symbols)                   (meaning)

← storage ─            ← parsing ─                 ← understanding
```

### THE STANDARD MODEL'S POSITION

```
PHYSICAL          VIRTUAL           SEMANTIC
                     │                  │
                     │    ┌─────────────┴─────────────┐
                     │    │   STANDARD MODEL          │
                     └───►│                           │
                          │   Reads VIRTUAL           │
                          │   Produces SEMANTIC       │
                          └───────────────────────────┘
```

**We READ from the Virtual realm (AST, names, paths) and PRODUCE Semantic understanding (roles, purposes, relationships).**

---

## 13 LEVELS OF CODE (L0 - L12)

The hierarchy from smallest to largest. Each level is REAL and DISTINCT.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           THE VERTICAL HIERARCHY                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  L12  UNIVERSE       🌐  All code everywhere (conceptual)                     ║
║        │                                                                      ║
║  L11  DOMAIN         🏛️   Industry vertical (banking, healthcare)             ║
║        │                                                                      ║
║  L10  ORGANIZATION   🏢  All code owned by one entity                         ║
║        │                                                                      ║
║  L9   PLATFORM       ☁️   Infrastructure hosting (K8s, AWS)                   ║
║        │                                                                      ║
║  L8   ECOSYSTEM      🔗  Interconnected systems (microservices)               ║
║        │                                                                      ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║        │             ↑ MACRO (above our ceiling)                              ║
║        │             ↓ OPERATIONAL (we analyze this)                          ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║        │                                                                      ║
║  L7   SYSTEM         ◇   A deployed codebase                                  ║
║        │                                                                      ║
║  L6   PACKAGE        📁  A module/folder                                      ║
║        │                                                                      ║
║  L5   FILE           📄  A source file                                        ║
║        │                                                                      ║
║  L4   CONTAINER      □   A class/struct                                       ║
║        │                                                                      ║
║  L3   NODE           ●   A function/method ★ FUNDAMENTAL UNIT                 ║
║        │                                                                      ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║        │             ↑ SEMANTIC (we classify this)                            ║
║        │             ↓ SYNTACTIC (inside the node)                            ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║        │                                                                      ║
║  L2   BLOCK          ▬   A control structure (if/for/while)                   ║
║        │                                                                      ║
║  L1   STATEMENT      ─   An instruction                                       ║
║        │                                                                      ║
║  L0   TOKEN          ·   A lexical unit (keyword, identifier)                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## LEVEL DEFINITIONS

| Level | Name | Shape | Definition | Contains | Example |
|-------|------|-------|------------|----------|---------|
| **L12** | Universe | 🌐 | All code in existence | Domains | GitHub + all private code |
| **L11** | Domain | 🏛️ | All code for an industry | Organizations | All banking software |
| **L10** | Organization | 🏢 | All code owned by one entity | Platforms | Google's monorepo |
| **L9** | Platform | ☁️ | Infrastructure hosting code | Ecosystems | AWS, Kubernetes |
| **L8** | Ecosystem | 🔗 | Multiple interconnected systems | Systems | Microservices cluster |
| **L7** | System | ◇ | A single deployable codebase | Packages | `standard-model-of-code` |
| **L6** | Package | 📁 | A module/folder grouping | Files | `core/` directory |
| **L5** | File | 📄 | A source code file | Containers + Nodes | `atom_classifier.py` |
| **L4** | Container | □ | A class or struct | Nodes + Properties | `class AtomClassifier` |
| **L3** | Node | ● | A function or method | Blocks | `def classify()` |
| **L2** | Block | ▬ | A control structure | Statements | `if x > 0:` |
| **L1** | Statement | ─ | A single instruction | Tokens | `return result` |
| **L0** | Token | · | A lexical unit | Characters | `def`, `if`, `(` |

---

## OPERATIONAL BOUNDARIES

| Boundary | Levels | What We Do |
|----------|--------|------------|
| **MACRO** | L8-L12 | Beyond our scope (future work) |
| **OPERATIONAL** | L3-L7 | We ANALYZE these (semantic classification) |
| **SYNTACTIC** | L0-L2 | Inside the node (not classified semantically) |

**The NODE (L3) is the FUNDAMENTAL UNIT of semantic analysis.**

---

## 8 ESSENTIAL REALMS (Lenses of Understanding)

Complete set of lenses needed to fully understand code.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           THE EIGHT REALMS                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  1. IDENTITY         What is it called?      (name, path, signature)          ║
║                                                                               ║
║  2. ONTOLOGY         What exists?            (entities, properties)           ║
║                                                                               ║
║  3. CLASSIFICATION   What kind is it?        (role, type, category)           ║
║                                                                               ║
║  4. COMPOSITION      How is it structured?   (parts, wholes, nesting)         ║
║                                                                               ║
║  5. RELATIONSHIPS    How is it connected?    (calls, imports, inherits)       ║
║                                                                               ║
║  6. TRANSFORMATION   What does it do?        (input → process → output)       ║
║                                                                               ║
║  7. SEMANTICS        What does it mean?      (purpose, intent, role)          ║
║                                                                               ║
║  8. EPISTEMOLOGY     How certain are we?     (confidence, evidence, proof)    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## REALM DEFINITIONS

| # | Realm | Question | Answers | Example |
|---|-------|----------|---------|---------|
| 1 | **Identity** | What is it called? | Name, Path, Signature | `getUserById` at `core/user.py:42` |
| 2 | **Ontology** | What exists? | Entity type, Properties | "A function with 3 params" |
| 3 | **Classification** | What kind is it? | Role, Category, Type | "This is a Query" |
| 4 | **Composition** | How is it structured? | Parts, Container, Hierarchy | "6 methods inside 1 class" |
| 5 | **Relationships** | How is it connected? | Callers, Callees, Imports | "Called by 5, calls 2" |
| 6 | **Transformation** | What does it do? | Input, Process, Output | "Takes ID, returns User" |
| 7 | **Semantics** | What does it mean? | Purpose, Intent, Responsibility | "Retrieves user from DB" |
| 8 | **Epistemology** | How certain are we? | Confidence, Evidence, Source | "92% confidence from name pattern" |

---

## COMPLETENESS PROOF

Every aspect of code understanding is covered:

| Question | Covered By |
|----------|------------|
| What is it called? | Identity |
| What exists? | Ontology |
| What kind is it? | Classification |
| What's it made of? | Composition |
| What does it connect to? | Relationships |
| What does it do? | Transformation |
| What does it mean? | Semantics |
| How sure are we? | Epistemology |

**No gaps. Complete coverage.**

---

## TRUTH PROOF

Every level exists in reality:

| Level | Exists? | Evidence |
|-------|---------|----------|
| L0 Token | ✅ | Lexers produce tokens |
| L1 Statement | ✅ | AST contains statements |
| L2 Block | ✅ | Control structures are real |
| L3 Node | ✅ | Functions/methods exist |
| L4 Container | ✅ | Classes/structs exist |
| L5 File | ✅ | Files are on disk |
| L6 Package | ✅ | Directories are real |
| L7 System | ✅ | Deployments are real |
| L8 Ecosystem | ✅ | Docker-compose, K8s exist |
| L9 Platform | ✅ | AWS, Vercel exist |
| L10 Organization | ✅ | Monorepos exist |
| L11 Domain | ⚠️ | Conceptual grouping |
| L12 Universe | ⚠️ | Conceptual totality |

**L0-L10 are REAL. L11-L12 are conceptual.**

---

## SUMMARY

```
13 LEVELS:    L0 (Token) → L12 (Universe)
8 REALMS:     Identity, Ontology, Classification, Composition,
              Relationships, Transformation, Semantics, Epistemology

FUNDAMENTAL:  L3 NODE is the atom of semantic analysis
OPERATIONAL:  L3-L7 is our classification scope
COMPLETE:     All aspects of code understanding covered
TRUE:         All levels correspond to real structures
```

---

> This is the canonical hierarchy. It is complete. It is true.
