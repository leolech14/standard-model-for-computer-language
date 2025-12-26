# THE 200 ATOM HYPOTHESIS

---

## Abstract

The original Standard Model claimed **167 atoms** as the complete set of code structures. Empirical validation across Python, TypeScript, Java, Go, and Rust revealed:

- **172 atoms** are needed today (167 + 5 validated additions)
- **~28 more concepts** remain unmapped
- **~200 atoms** may be the true coverage threshold

This document develops the hypothesis and sets up testing protocols.

---

## 1. THE EVOLUTION

```
v1.0: 167 atoms (theoretical design)
         ↓
v2.0: 172 atoms (+ Comprehension, MacroCall, ImplBlock, Defer, ImportStmt)
         ↓
v3.0: ~200 atoms (hypothesis - to be tested)
```

---

## 2. THE EVIDENCE

### 2.1 Scanner Results (December 2025)

| Language | Total AST Nodes | Mapped | Missing | Coverage |
|----------|-----------------|--------|---------|----------|
| Python | 108 | 51 | 47 | 47% |
| TypeScript | 115 | 55 | 63 | 48% |
| Go | 52 | 36 | 16 | 69% |
| Rust | 84 | 45 | 39 | 54% |
| Java | 95 | 49 | 49 | 52% |
| **Total** | **454** | **236** | **214** | **52%** |

### 2.2 Missing Category Breakdown

| Category | Count | Status |
|----------|-------|--------|
| Operator tokens (not real nodes) | ~80 | **SKIP** |
| Compile-time type nodes | ~60 | **DEFER** |
| True semantic gaps | ~75 | **ACTION** |

Of the 75 actionable gaps:
- ~50 map to **existing atoms** (crosswalk gap only)
- ~25 need **new atoms** (truly new concepts)

---

## 3. THE 28 CANDIDATE ATOMS

These concepts have no current atom mapping:

### 3.1 Pattern Matching Family (+4)

| ID | Name | Languages | Reason |
|----|------|-----------|--------|
| #173 | `MatchPattern` | Python, Rust | Pattern in match arm |
| #174 | `PatternGuard` | Rust | Guard clause in pattern |
| #175 | `WildcardPattern` | Python, Rust | `_` catch-all |
| #176 | `OrPattern` | Python, Rust | `x | y` alternatives |

### 3.2 Destructuring Family (+3)

| ID | Name | Languages | Reason |
|----|------|-----------|--------|
| #177 | `SpreadElement` | TS/JS | `...rest` expansion |
| #178 | `RestPattern` | All | Collect remaining |
| #179 | `DestructuringAssign` | All | `const {a, b} = obj` |

### 3.3 Expression Variants (+5)

| ID | Name | Languages | Reason |
|----|------|-----------|--------|
| #180 | `WalrusExpr` | Python | `:=` named expression |
| #181 | `NullishCoalesce` | TS/JS | `??` operator |
| #182 | `OptionalChain` | TS/JS | `?.` safe navigation |
| #183 | `RangeExpr` | Rust, Go | `start..end` ranges |
| #184 | `PipelineExpr` | Future | `x |> f` pipe operator |

### 3.4 Concurrency Extended (+4)

| ID | Name | Languages | Reason |
|----|------|-----------|--------|
| #185 | `ChannelClose` | Go | Distinct from send |
| #186 | `AsyncIterator` | TS, Python | `async for` |
| #187 | `ParallelFor` | Many | Parallel iteration |
| #188 | `AtomicOp` | Rust, Go | Atomic operations |

### 3.5 Metaprogramming (+4)

| ID | Name | Languages | Reason |
|----|------|-----------|--------|
| #189 | `Annotation` | Java, TS | `@Decorator` metadata |
| #190 | `Pragma` | Many | Compiler directives |
| #191 | `MacroRule` | Rust | Macro definition body |
| #192 | `Quote` | Lisp, Elixir | Code-as-data |

### 3.6 Type System (Optional) (+5)

| ID | Name | Languages | Reason |
|----|------|-----------|--------|
| #193 | `GenericParam` | All typed | `<T>` type parameters |
| #194 | `UnionType` | TS, Python | `X | Y` type union |
| #195 | `IntersectionType` | TS | `X & Y` type merge |
| #196 | `TypeConstraint` | All typed | `where T: Clone` |
| #197 | `TypeAlias` | All typed | `type X = Y` |

### 3.7 Edge Cases (+3)

| ID | Name | Languages | Reason |
|----|------|-----------|--------|
| #198 | `DebuggerStmt` | TS/JS | `debugger;` breakpoint |
| #199 | `LabeledBlock` | Go, Java | Named break target |
| #200 | `EmptyStmt` | All | `;` no-op |

---

## 4. THE TESTING PROTOCOL

### 4.1 Phase 1: Crosswalk Completion

**Goal:** Map all 75 actionable gaps to existing or new atoms.

**Method:**
```bash
# Run the scanner
python3 src/tools/coverage_scanner.py

# For each missing node, decide:
# 1. Map to existing atom (update crosswalk)
# 2. Create new atom (update schema + crosswalk)
```

**Success Criteria:**
- Coverage > 90% for each language
- No "UNKNOWN" mappings remaining

### 4.2 Phase 2: Real Code Validation

**Goal:** Parse real codebases, count unmapped nodes.

**Method:**
```bash
# Parse a real project
python3 src/tools/parse_project.py /path/to/project

# Count:
# - Total nodes parsed
# - Nodes mapped to atoms
# - Nodes with "Unknown" atom
```

**Success Criteria:**
- < 5% "Unknown" atoms in real code
- All unknowns are obscure edge cases

### 4.3 Phase 3: Atom Count Convergence

**Goal:** Find the minimum atom set for 95% coverage.

**Method:**
1. Start with 172 atoms
2. Add atoms one-by-one for each new concept
3. Re-run validation after each addition
4. Stop when coverage plateaus

**Hypothesis:**
- Around **~200 atoms**, coverage will reach 95%+
- Diminishing returns after 200

---

## 5. THE DECISION MATRIX

For each "missing" AST node, use this decision tree:

```
Is it a real AST node (not operator token)?
├─ NO → SKIP (not a node)
└─ YES → Does it have runtime semantics?
          ├─ NO → DEFER (compile-time only, maybe future atom)
          └─ YES → Does an existing atom cover it?
                    ├─ YES → UPDATE CROSSWALK ONLY
                    └─ NO → CREATE NEW ATOM
```

---

## 6. THE VERSIONING PLAN

| Version | Atom Count | Status |
|---------|------------|--------|
| v2.0 | 172 | Current |
| v2.1 | ~185 | After crosswalk completion |
| v3.0 | ~200 | After real-code validation |
| LTS | 200 | Long-term stable |

---

## 7. ACTION ITEMS

### Immediate (This Week)

- [ ] Complete crosswalks for all 5 languages
- [ ] Add Pattern Matching atoms (#173-176)
- [ ] Add Destructuring atoms (#177-179)
- [ ] Re-run scanner to verify improvement

### Short-term (This Month)

- [ ] Parse real projects (Django, Express, Spring)
- [ ] Measure actual coverage on production code
- [ ] Finalize v2.1 with refined atom count

### Long-term (Q1 2026)

- [ ] Reach 200-atom stable version
- [ ] Document rationale for each atom
- [ ] Publish as canonical reference

---

## 8. APPENDIX: RUNNING THE TESTS

```bash
# 1. Check current coverage
python3 src/tools/coverage_scanner.py

# 2. View missing by language
python3 src/tools/coverage_scanner.py --lang python

# 3. Generate full report
python3 src/tools/coverage_scanner.py > docs/coverage_report.md

# 4. After updating crosswalks, verify improvement
python3 src/tools/coverage_scanner.py | grep "Total"
```

---

> *"The map grows to match the territory. 167 was the sketch. 200 is the survey."*
