# 🧠 Collider Learning Ledger

> **System Memory:** Tracks permanent changes to the Pattern Repository.
> **Auto-Generated:** Updates by `scripts/train_serial.py`.

## 📊 Current Inventory (2025-12-23)

| Layer | Count |
|:---|---:|
| Prefix Patterns | 57 |
| Suffix Patterns | 43 |
| Path Patterns | 11 |
| ROLE_MAP Entries | 38 |
| Atom Aliases | 4 |
| **TOTAL** | **153** |

---

## 📜 Permanent Pattern Commits

| Date | Pattern | Type | Role | Confidence | Trigger |
|:---|:---|:---|:---|:---|:---|
| 2025-12-23 | `test_` | Prefix | **Test** | **95%** | Loop #1 (Test Blindness) |
| 2025-12-23 | `create_` | Prefix | **Factory** | **95%** | Loop #2 (Utility Confusion) |
| 2025-12-23 | `make_` | Prefix | **Factory** | **90%** | Loop #2 (Utility Confusion) |
| 2025-12-23 | `get_` | Prefix | **Query** | **95%** | Loop #3 (Auto-Discovery) |
| 2025-12-23 | `transfer_` | Prefix | **Mapper** | **85%** | Loop #3 (Auto-Discovery) |
| 2025-12-23 | `convert_` | Prefix | **Mapper** | **85%** | Loop #3 (Auto-Discovery) |
| 2025-12-23 | `/test` | Path | **Test** | **95%** | Loop #4 (Context Awareness) |
| 2025-12-23 | Path Context Fix | Code | **Test → TestDouble Alias** | **93.7%** | Pydantic Breakthrough |

### Session 2025-12-23 (Late) - Suffix Patterns (+14 items)

| Pattern | Type | Role | Confidence |
|:---|:---|:---|---:|
| `Mixin` | Suffix | Adapter | 85% |
| `Config` | Suffix | Configuration | 90% |
| `Configuration` | Suffix | Configuration | 90% |
| `Mock` | Suffix | TestDouble | 95% |
| `Mocker` | Suffix | TestDouble | 95% |
| `Stub` | Suffix | TestDouble | 90% |
| `Fake` | Suffix | TestDouble | 90% |
| `Specifier` | Suffix | Specification | 80% |
| `watch_` | Prefix | Observer | 80% |
| `_should_` | Prefix | Specification | 85% |

### Session 2025-12-23 (Late) - Atom Aliases (+4 items)

| Alias | Atom ID |
|:---|:---|
| `configuration` | DAT.VAR.A |
| `adapter` | ORG.SVC.M |
| `observer` | EXE.HDL.O |
| `specification` | ORG.AGG.M |

### Session 2025-12-23 (Late) - ROLE_MAP Additions (+5 items)

| Atom Subtype | Canonical Role |
|:---|:---|
| TestDouble | Test |
| Observer | EventHandler |
| Specification | Service |
| Configuration | Configuration |
| TestModule | Test |

---

## 📝 Learning Protocol
When adding new patterns, ALWAYS report:
1. **What** was added (exact pattern string)
2. **Where** (prefix/suffix/path/ROLE_MAP/alias)
3. **Target** (role or atom ID)
4. **Confidence** (percentage)
5. **Before/After** (count delta)



### Session 2025-12-23 (Late Night) - CRITICAL PREFIX FIX

**BREAKTHROUGH:** Prefix patterns were in repository but NEVER checked in classification!

| Fix | Type | Impact |
|:---|:---|---:|
| Added PREFIX pattern matching to `classify_by_name` | Code | **+26.7%** on Tier 1 |
| Added `login` → Command | Prefix | +1 pattern |
| Added `query` atom alias | Alias | +1 alias |

**Before/After on Tier 1 FastAPI Samples:**
- Before: 43.3% (13/30)
- After: **70.0% (21/30)**

**Inventory Update:**
- Prefix Patterns: 57 → 58 (+1: login)
- Atom Aliases: 4 → 5 (+1: query)
- **TOTAL: 154 items**

## 2025-12-23 11:36 - freeCodeCamp Investigation

**Source**: Platinum wave investigation of freeCodeCamp/freeCodeCamp (1728 nodes, 62.3% conf)

### New Prefixes
- `create*` → Factory (85%)
- `is*`, `has*`, `should*`, `can*` → Specification (80%)
- `build*` → Factory (85%)
- `on*` → EventHandler (85%)
- `Step*`, `Block*` → DTO (85%)
- `Module*` → Provider (85%)
- `Super*` → Service (80%)

### New Suffixes
- `*Route` → Controller (90%)
- `*Location` → DTO (85%)
- `*Order` → DTO (80%)


## 2025-12-23 12:11 - JS/TS Framework Patterns

**Source**: Benchmark analysis showing TypeScript/JavaScript repos at 62% avg confidence

### New Prefixes (19)
- React: `use*` → Hook, `with*` → Decorator, `render*` → View
- Vue: `setup*`, `onMounted*`, `onUpdated*`, `onUnmounted*` → Lifecycle
- General: `dispatch*` → Command, `emit*` → DomainEvent, `subscribe*` → Observer

### New Suffixes (15)
- React: `*Component` → View, `*Container` → Controller, `*Provider` → Provider
- Redux: `*Reducer`, `*Action`, `*Thunk`, `*Saga` → Command/EventHandler
- State: `*Selector` → Query, `*Store` → Repository, `*Slice` → Module
- Vue: `*Composable` → Utility, `*Directive` → Decorator


## 2025-12-23 15:51 - Go Language Patterns

**Source**: golang/go repo analysis (89,279 nodes, 61,325 low-conf)

### New Prefixes
- `tes*` → Test (11,204 occurrences)
- `new*` → Factory (Go's NewXxx pattern)
- `ini*` → Lifecycle (init functions)
- `run*` → Command
- `benchmark*`, `example*`, `fuzz*` → Test

### New Suffixes  
- `*Error`, `*rror` → Exception (573 occurrences)
- `*Type` → DTO (391 occurrences)
- `*Handler` → EventHandler
- `*Option(s)`, `*Opts`, `*Config` → Configuration (Go functional options)
- `*Writer`, `*Reader`, `*Scanner` → Repository/Query
- `*Builder` → Factory
- `*Walker`, `*Visitor` → Iterator/Observer


## 2025-12-23 - Go/JS Pattern Boost
- Added 9 prefix patterns
- Added 11 suffix patterns
- Target: Go (10.7% gap), JS/TS (10.4% gap)
- New Go patterns: Handle*, Serve*, With*, *Middleware, *Option, *Cmd
- New JS patterns: use* (hooks), *Page, *Layout, *Provider, *Context, on*, handle*
- Expected improvement: ~76,000 nodes gain 8%+ confidence

## 2025-12-23 - Structural Anchors Strategy
- Implemented "Pseudo-Decorators" approach based on external insight
- Added NEW pattern types: parameter_type_patterns, import_patterns
- Added 14 Go framework param patterns (gin.Context, http.ResponseWriter)
- Added 26 JS/TS import patterns (react, express, prisma)
- Added 18 Java Spring/JPA annotation patterns
- Added 40 directory path patterns (controllers/, models/, services/)
- Expected impact: 66% → 75% average confidence
- Key insight: Treat structural signals with TIER 1 (95%) confidence like decorators
