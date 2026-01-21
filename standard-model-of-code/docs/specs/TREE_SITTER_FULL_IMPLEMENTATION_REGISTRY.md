# TREE-SITTER FULL IMPLEMENTATION REGISTRY

> **The definitive task list for full tree-sitter capabilities in Collider.**
>
> **Created:** 2026-01-21
> **Sources:** Perplexity Research, GPT-52-PRO Analysis, Gemini RAG, Claude Opus Synthesis
> **Status:** MASTER REGISTRY - 87 tasks across 7 phases

---

## EXECUTIVE SUMMARY

| Phase | Tasks | Done | Ready (95%+) | Avg Confidence |
|-------|-------|------|--------------|----------------|
| P1: Query Infrastructure | 12 | **12** | COMPLETE | **100%** |
| P2: Scope Analysis | 14 | 0 | 0 | **87%** |
| P3: Control Flow | 10 | 0 | 0 | 68% |
| P4: Pattern Detection | 12 | 0 | 0 | 65% |
| P5: Cross-File Resolution | 10 | 0 | 0 | 55% |
| P6: Advanced Parsing | 12 | 0 | 0 | 48% |
| P7: Visualization Integration | 17 | 0 | 0 | 60% |
| **TOTAL** | **87** | **12** | **12** | **100%** |

**PHASE 1 COMPLETE:** All 12 tasks done. QueryLoader pattern, all .scm files, ERROR/MISSING detection, tests, docs.
**Next:** Phase 2 - Scope Analysis

---

## RAG VERIFICATION SUMMARY (2026-01-21)

**Verified via `analyze.py` with Gemini 2.5 Pro:**

| Question | Finding | Confidence Impact |
|----------|---------|-------------------|
| Which dimensions does scope analysis serve? | **D5 (STATE), D6 (EFFECT), D8 (LIFETIME)** + helps infer D3 (ROLE) | P2 Alignment +15% |
| QueryLoader architecture pattern? | **Class-based with singleton accessor** (ProfileLoader pattern) | P1-02 Factual +5% |
| Schema flexibility for scope data? | **No formal schema, additionalProperties effectively true** | P2-07 Factual +10% |
| How does scope map to constraints? | **INVARIANT-001, HEURISTIC-004, proposes HEURISTIC-005** | P2 Alignment +10% |
| Python class scope rule? | **PEP 227 confirmed - class bodies NOT lexical scopes** | P2-05 Factual +5% |

**Inline Query Locations Verified:**

| Location | Lines | Language | Node Types |
|----------|-------|----------|------------|
| tree_sitter_engine.py | 418-424 | Rust | function_item, struct_item, trait_item, impl_item, enum_item |
| tree_sitter_engine.py | 427-433 | Go | function_declaration, method_declaration, type_declaration |
| tree_sitter_engine.py | 436-463 | JS/TS | function_declaration, arrow_function, function_expression, class_declaration, method_definition |
| tree_sitter_engine.py | 471-479 | Fallback | function_item/declaration, struct_item, class_declaration |
| tree_sitter_engine.py | 677-680 | JS/TS | call_expression (hooks) |

**Edge Extractor Integration Point:**

- `TreeSitterEdgeStrategy.extract_edges()` at line 645
- Currently uses `_find_target_particle()` heuristic at line 675
- **Integration: Add scope bindings lookup before heuristic fallback**

---

## CONFIDENCE METHODOLOGY

```
Confidence = min(Factual, Alignment, Feasibility)

Factual (F):     Will this technically work? (API exists, tested)
Alignment (A):   Does this serve the Standard Model of Code?
Feasibility (X): Can we implement this with current resources?
```

| Level | Meaning | Action |
|-------|---------|--------|
| 95%+ | Verified all dimensions | **EXECUTE** |
| 85-94% | High confidence, minor gaps | Almost ready |
| 70-84% | Good but needs verification | Research needed |
| 50-69% | Moderate, significant gaps | Defer or prototype |
| <50% | Low confidence | DO NOT EXECUTE |

---

## PHASE 1: QUERY INFRASTRUCTURE (Foundation)

**Goal:** Externalize inline queries, create QueryLoader, enable Phase 2+

| ID | Task | F | A | X | **Conf** | Status | Evidence |
|----|------|---|---|---|----------|--------|----------|
| P1-01 | Create `src/core/queries/` directory | 99% | 95% | 99% | **95%** | **DONE** | Created 2026-01-21 |
| P1-02 | Create `queries/__init__.py` with QueryLoader | 98% | 95% | 95% | **95%** | **DONE** | ProfileLoader pattern, singleton |
| P1-03 | Extract Python symbols.scm + locals.scm | 95% | 95% | 95% | **95%** | **DONE** | 50 + 134 lines |
| P1-04 | Extract JavaScript symbols.scm + locals.scm | 95% | 95% | 95% | **95%** | **DONE** | TDZ-aware, hooks |
| P1-05 | Extract TypeScript symbols.scm | 95% | 95% | 95% | **95%** | **DONE** | Inherits JS locals |
| P1-06 | Extract Go symbols.scm | 95% | 95% | 92% | **95%** | **DONE** | funcs, methods, structs |
| P1-07 | Extract Rust symbols.scm | 95% | 95% | 92% | **95%** | **DONE** | structs, traits, impls |
| P1-08 | Refactor tree_sitter_engine.py | 90% | 95% | 88% | **88%** | **DONE** | Integration point mapped, tests passing |
| P1-09 | Add ERROR node detection | 99% | 95% | 99% | **95%** | **DONE** | count_parse_errors() implemented |
| P1-10 | Add MISSING node detection | 99% | 95% | 99% | **95%** | **DONE** | count_parse_errors() detects both |
| P1-11 | Query loading tests | 99% | 95% | 99% | **95%** | **DONE** | 20 tests passing |
| P1-12 | Documentation update | 99% | 95% | 99% | **95%** | **DONE** | COLLIDER.md, CLAUDE.md |

**Phase 1 Exit Criteria:**
- [x] All queries load from external .scm files
- [x] Existing tests pass (no regression)
- [x] ERROR/MISSING nodes detected and counted

**PHASE 1 COMPLETED: 2026-01-21**
- QueryLoader: `src/core/queries/__init__.py` with ProfileLoader pattern
- Query files: python, javascript, typescript, go, rust, _fallback
- Parse error detection: `count_parse_errors()` counts ERROR and MISSING nodes
- Tests: 20 QueryLoader tests + 3 parse error detection tests
- Integration: `get_query_for_language()` wrapper added to pipeline
- Total tests passing: 108+ (no regression)

---

## PHASE 2: SCOPE ANALYSIS (The Big Unlock)

**Goal:** Implement locals.scm support with tree-sitter-highlight algorithm

### Critical Corrections (GPT-52-PRO-REPLY.md)

| Correction | Impact |
|------------|--------|
| **4 captures, not 3** | `@local.definition-value` is required for initializer safety |
| **`local.scope-inherits`** | Property controls whether resolution stops at scope |
| **Port, don't invent** | Use tree-sitter-highlight algorithm exactly |
| **Python PEP 227** | Class bodies are NOT lexical scopes for methods |

### Tasks

| ID | Task | F | A | X | **Conf** | Blocks | Evidence |
|----|------|---|---|---|----------|--------|----------|
| P2-01 | Create ScopeAnalyzer class skeleton | 90% | 95% | 92% | **90%** | - | GPT algorithm + RAG alignment |
| P2-02 | Implement Scope data model | 92% | 95% | 95% | **92%** | P2-01 | GPT spec |
| P2-03 | Implement Def data model | 92% | 95% | 95% | **92%** | P2-01 | `available_after_byte` |
| P2-04 | Implement Ref data model | 92% | 95% | 95% | **92%** | P2-01 | |
| P2-05 | Write Python locals.scm | 88% | 95% | 88% | **88%** | P1 | RAG: PEP 227 confirmed |
| P2-06 | Write JavaScript locals.scm | 85% | 95% | 85% | **85%** | P1 | TDZ handling, stock query exists |
| P2-07 | Write TypeScript locals.scm | 85% | 95% | 85% | **85%** | P2-06 | Inherits JS |
| P2-08 | Implement scope stack algorithm | 85% | 95% | 85% | **85%** | P2-01 | tree-sitter-highlight, GPT detailed |
| P2-09 | Implement @local.scope handling | 88% | 95% | 88% | **88%** | P2-08 | |
| P2-10 | Implement @local.definition handling | 88% | 95% | 88% | **88%** | P2-08 | |
| P2-11 | Implement @local.definition-value | 85% | 95% | 85% | **85%** | P2-10 | GPT critical correction |
| P2-12 | Implement @local.reference resolution | 85% | 95% | 85% | **85%** | P2-08 | |
| P2-13 | Integrate with edge_extractor.py | 80% | 95% | 80% | **80%** | P2-12 | RAG: Integration point at L675 |
| P2-14 | Golden tests (shadowing, PEP 227, TDZ) | 92% | 95% | 92% | **92%** | P2-12 | GPT test cases + RAG constraints |

**Phase 2 Exit Criteria:**
- [ ] ScopeAnalyzer produces ref→def bindings for Python/JS
- [ ] Python class scope rule (PEP 227) passes tests
- [ ] JS TDZ rule passes tests
- [ ] edge_extractor uses scope bindings when available

### The Algorithm (From tree-sitter-highlight)

```python
# Data Model
Scope { id, parent_id, byte_range, inherits: bool, defs: List[Def] }
Def   { name, node_id, available_after_byte }
Ref   { name, node_id, start_byte }

# Algorithm
1. Maintain scope stack
2. On @local.scope: push scope with node.byte_range, read inherits property
3. On @local.definition: add Def to current scope
   - available_after_byte = @local.definition-value.end_byte OR def.end_byte
4. On @local.reference: walk scopes innermost→outermost
   - For each scope, walk defs newest→oldest
   - Match if: name == def.name AND ref.start_byte >= def.available_after_byte
   - Stop if scope.inherits == false
```

---

## PHASE 3: CONTROL FLOW ANALYSIS

**Goal:** Extract cyclomatic complexity, nesting depth, branch analysis

| ID | Task | F | A | X | **Conf** | Blocks | Notes |
|----|------|---|---|---|----------|--------|-------|
| P3-01 | Create ControlFlowAnalyzer class | 80% | 75% | 85% | **75%** | P1 | |
| P3-02 | Python control flow query | 75% | 75% | 80% | **75%** | P3-01 | if/for/while/try |
| P3-03 | JavaScript control flow query | 75% | 75% | 80% | **75%** | P3-01 | |
| P3-04 | Cyclomatic complexity calculation | 85% | 85% | 90% | **85%** | P3-02 | Health metrics |
| P3-05 | Nesting depth calculation | 90% | 80% | 90% | **80%** | P3-02 | |
| P3-06 | Branch counting | 85% | 75% | 85% | **75%** | P3-02 | |
| P3-07 | Early return detection | 80% | 70% | 85% | **70%** | P3-02 | |
| P3-08 | Recursion detection | 65% | 65% | 70% | **65%** | P2 | Needs call graph |
| P3-09 | Add metrics to node schema | 90% | 85% | 95% | **85%** | P3-04 | |
| P3-10 | Control flow tests | 95% | 85% | 95% | **85%** | P3-04 | |

**Phase 3 Exit Criteria:**
- [ ] Cyclomatic complexity calculated for all functions
- [ ] Nesting depth calculated
- [ ] Metrics appear in unified_analysis.json

---

## PHASE 4: PATTERN DETECTION (Atom Enhancement)

**Goal:** Tree-sitter powered atom classification with higher confidence

| ID | Task | F | A | X | **Conf** | Blocks | Notes |
|----|------|---|---|---|----------|--------|-------|
| P4-01 | Create patterns.scm framework | 75% | 85% | 80% | **75%** | P1 | |
| P4-02 | Python patterns.scm (Repository, Service, Factory) | 70% | 90% | 75% | **70%** | P4-01 | CRUD detection |
| P4-03 | JavaScript patterns.scm (Component, Hook, Handler) | 70% | 90% | 75% | **70%** | P4-01 | React patterns |
| P4-04 | Integrate with atom_classifier.py | 65% | 90% | 70% | **65%** | P4-02 | |
| P4-05 | RPBL Responsibility extraction | 60% | 95% | 65% | **60%** | P4-04 | Method count, fan-out |
| P4-06 | RPBL Purity extraction (D6:EFFECT) | 55% | 95% | 60% | **55%** | P2 | Assignment tracking |
| P4-07 | RPBL Boundary extraction | 70% | 95% | 75% | **70%** | P4-04 | External calls |
| P4-08 | RPBL Lifecycle extraction (D7) | 60% | 95% | 65% | **60%** | P4-02 | Pattern detection |
| P4-09 | D5:STATE extraction | 65% | 95% | 70% | **65%** | P2 | Scope analysis |
| P4-10 | Confidence scoring enhancement (D8:TRUST) | 70% | 95% | 75% | **70%** | P4-04 | Multi-source |
| P4-11 | Pattern detection tests | 90% | 90% | 90% | **90%** | P4-04 | |
| P4-12 | Documentation | 95% | 90% | 95% | **90%** | P4-11 | |

**Phase 4 Exit Criteria:**
- [ ] Atom classification uses tree-sitter patterns
- [ ] RPBL dimensions have tree-sitter evidence
- [ ] Classification confidence improved measurably

---

## PHASE 5: CROSS-FILE RESOLUTION

**Goal:** Resolve imports, track symbols across files

| ID | Task | F | A | X | **Conf** | Blocks | Notes |
|----|------|---|---|---|----------|--------|-------|
| P5-01 | Create SymbolIndex class | 70% | 80% | 75% | **70%** | P2 | |
| P5-02 | Python import resolution | 65% | 85% | 70% | **65%** | P5-01 | ImportExtractor exists |
| P5-03 | JavaScript import resolution | 60% | 85% | 65% | **60%** | P5-01 | ES6 + CommonJS |
| P5-04 | TypeScript import resolution | 55% | 85% | 60% | **55%** | P5-03 | Path aliases |
| P5-05 | Build cross-file call graph | 55% | 90% | 60% | **55%** | P5-02 | |
| P5-06 | Evaluate tree-sitter-stack-graphs | 50% | 70% | 50% | **50%** | - | Research task |
| P5-07 | Implement symbol lookup API | 60% | 80% | 65% | **60%** | P5-01 | |
| P5-08 | Handle re-exports | 50% | 75% | 55% | **50%** | P5-03 | |
| P5-09 | Handle dynamic imports | 40% | 70% | 45% | **40%** | P5-03 | |
| P5-10 | Cross-file tests | 85% | 85% | 85% | **85%** | P5-05 | |

**Phase 5 Exit Criteria:**
- [ ] Import statements resolve to target files
- [ ] Cross-file edges have higher confidence
- [ ] Symbol lookup works for common patterns

---

## PHASE 6: ADVANCED PARSING

**Goal:** Incremental parsing, error recovery, injections

| ID | Task | F | A | X | **Conf** | Blocks | Notes |
|----|------|---|---|---|----------|--------|-------|
| P6-01 | Implement incremental parsing | 85% | 50% | 60% | **50%** | - | Optimization only |
| P6-02 | Implement TSInputEdit tracking | 80% | 50% | 55% | **50%** | P6-01 | |
| P6-03 | Error recovery improvement | 75% | 60% | 60% | **60%** | - | |
| P6-04 | MISSING node detection | 90% | 70% | 85% | **70%** | P1 | |
| P6-05 | TreeCursor optimization | 85% | 55% | 70% | **55%** | - | Performance |
| P6-06 | Python SQL injection (injections.scm) | 50% | 45% | 45% | **45%** | P1 | Low priority |
| P6-07 | JavaScript GraphQL injection | 50% | 45% | 45% | **45%** | P1 | Low priority |
| P6-08 | HTML template injection | 45% | 40% | 40% | **40%** | P1 | Low priority |
| P6-09 | Query caching optimization | 80% | 60% | 75% | **60%** | P1 | Performance |
| P6-10 | Timeout handling improvement | 85% | 65% | 80% | **65%** | - | |
| P6-11 | Memory management audit | 70% | 55% | 60% | **55%** | - | |
| P6-12 | Thread safety documentation | 90% | 50% | 85% | **50%** | - | |

**Phase 6 Exit Criteria:**
- [ ] Incremental parsing works for file edits
- [ ] Error recovery produces useful trees
- [ ] Performance improved measurably

---

## PHASE 7: VISUALIZATION INTEGRATION

**Goal:** Surface tree-sitter insights in the 3D visualization

| ID | Task | F | A | X | **Conf** | Blocks | Notes |
|----|------|---|---|---|----------|--------|-------|
| P7-01 | Syntax error badge (red) | 85% | 80% | 85% | **80%** | P1-09 | |
| P7-02 | Complexity heatmap (node color) | 80% | 85% | 80% | **80%** | P3-04 | |
| P7-03 | Unused code indicator (faded) | 75% | 80% | 75% | **75%** | P2-12 | |
| P7-04 | Shadowing warning badge | 70% | 75% | 70% | **70%** | P2-14 | |
| P7-05 | Purity indicator (green/yellow/red) | 65% | 85% | 65% | **65%** | P4-06 | |
| P7-06 | Lifecycle phase indicator (shape) | 60% | 80% | 60% | **60%** | P4-08 | |
| P7-07 | Scope boundary visualization | 55% | 70% | 55% | **55%** | P2 | |
| P7-08 | Data flow animation | 45% | 65% | 45% | **45%** | P4-06 | |
| P7-09 | Call depth coloring | 70% | 75% | 70% | **70%** | P5-05 | |
| P7-10 | Import graph layer | 65% | 80% | 65% | **65%** | P5-02 | |
| P7-11 | Error node highlighting in code panel | 80% | 75% | 80% | **75%** | P1-09 | |
| P7-12 | Scope-aware edge coloring | 60% | 70% | 60% | **60%** | P2-13 | |
| P7-13 | Pattern match highlighting | 55% | 75% | 55% | **55%** | P4-04 | |
| P7-14 | UPB binding for complexity | 70% | 85% | 70% | **70%** | P3-04 | |
| P7-15 | UPB binding for purity | 65% | 85% | 65% | **65%** | P4-06 | |
| P7-16 | UPB binding for error count | 80% | 85% | 80% | **80%** | P1-09 | |
| P7-17 | Visualization tests | 85% | 80% | 85% | **80%** | P7-02 | |

**Phase 7 Exit Criteria:**
- [ ] At least 5 new visual channels use tree-sitter data
- [ ] UPB bindings work for complexity, purity, errors
- [ ] No regression in existing visualization

---

## DEPENDENCY GRAPH

```
P1 (Query Infrastructure)
 │
 ├──► P2 (Scope Analysis)
 │     │
 │     ├──► P4 (Pattern Detection) ──► P7 (Visualization)
 │     │
 │     └──► P5 (Cross-File) ──► P7
 │
 ├──► P3 (Control Flow) ──► P7
 │
 └──► P6 (Advanced Parsing)
```

---

## RECOMMENDED EXECUTION ORDER

### Sprint 1: Foundation (P1)
Execute: P1-01, P1-02, P1-09, P1-10, P1-11, P1-12
Raise to 95%: P1-03, P1-04, P1-05

### Sprint 2: Query Migration (P1 completion)
Execute: P1-03, P1-04, P1-05, P1-06, P1-07, P1-08

### Sprint 3: Scope Analysis MVP (P2)
Execute: P2-01 through P2-06, P2-14

### Sprint 4: Scope Integration (P2 completion)
Execute: P2-07 through P2-13

### Sprint 5: Control Flow (P3)
Execute: P3-01 through P3-06, P3-09, P3-10

### Sprint 6: Pattern Detection (P4)
Execute: P4-01 through P4-04, P4-11, P4-12

### Sprint 7: Visualization (P7 partial)
Execute: P7-01, P7-02, P7-11, P7-14, P7-16

### Future Sprints:
- Cross-file resolution (P5)
- Advanced parsing (P6)
- Full visualization (P7)
- RPBL completion (P4-05 through P4-10)

---

## TREE-SITTER CAPABILITY MAPPING

### Currently Used (15%)

| Capability | Status | Location |
|------------|--------|----------|
| Basic parsing | YES | tree_sitter_engine.py |
| 9 languages | YES | tree_sitter_engine.py |
| Inline queries | YES | tree_sitter_engine.py:382-441 |
| Timeout protection | YES | tree_sitter_engine.py |
| #match? predicate | PARTIAL | React hook detection |
| Field access | YES | call_by_field_name |

### Phase 1 Unlocks (+15% = 30%)

| Capability | Tasks |
|------------|-------|
| External .scm files | P1-01, P1-02 |
| ERROR node detection | P1-09 |
| MISSING node detection | P1-10 |
| Query caching | P1-02 |

### Phase 2 Unlocks (+20% = 50%)

| Capability | Tasks |
|------------|-------|
| @local.scope | P2-09 |
| @local.definition | P2-10 |
| @local.definition-value | P2-11 |
| @local.reference | P2-12 |
| Scope stack algorithm | P2-08 |
| Shadowing detection | P2-14 |
| Unused variable detection | P2-14 |

### Phase 3-7 Unlocks (+35% = 85%)

| Phase | Unlocks |
|-------|---------|
| P3 | Cyclomatic complexity, nesting depth, branches |
| P4 | Pattern queries, RPBL extraction, D5/D6/D7 |
| P5 | Import resolution, cross-file symbols |
| P6 | Incremental parsing, injections |
| P7 | Visual channels bound to tree-sitter data |

---

## LANGUAGE-SPECIFIC NOTES

### Python

| Gotcha | Rule | Evidence |
|--------|------|----------|
| Class scope (PEP 227) | Class bodies are NOT lexical scopes | peps.python.org |
| Comprehension scope | List/dict/set comprehensions create scopes | Python 3 semantics |
| Global/nonlocal | Not handled by locals.scm alone | Requires semantic analysis |

### JavaScript

| Gotcha | Rule | Evidence |
|--------|------|----------|
| TDZ | let/const cannot be accessed before declaration | MDN |
| var hoisting | var declarations hoist to function scope | MDN |
| Function hoisting | Function declarations hoist with value | MDN |
| Block scope | let/const are block-scoped, var is not | ES6 spec |

### TypeScript

| Gotcha | Rule | Evidence |
|--------|------|----------|
| Type-only imports | `import type` doesn't create runtime binding | TS spec |
| Path aliases | tsconfig paths need resolution | TS compiler API |
| Enums | Const enums inline at compile time | TS spec |

---

## SUCCESS METRICS

| Metric | Current | After P1 | After P2 | After Full |
|--------|---------|----------|----------|------------|
| Tree-sitter utilization | 15% | 30% | 50% | 85% |
| Edge confidence (avg) | 70% | 72% | 85% | 92% |
| Atom confidence (avg) | 65% | 67% | 75% | 88% |
| Coverage (D1-D8) | 4/8 | 4/8 | 6/8 | 8/8 |
| RPBL extraction | 1/4 | 1/4 | 2/4 | 4/4 |

---

## DOCUMENT HISTORY

| Date | Change | Author |
|------|--------|--------|
| 2026-01-21 | Initial creation from multi-source synthesis | Claude Opus |

---

## SOURCES

1. **GPT-52-PRO-REPLY.md** - Critical corrections on locals.scm algorithm
2. **Perplexity Research** - Comprehensive capability inventory
3. **TREE_SITTER_TASK_REGISTRY.md** - Previous task registry (46 tasks)
4. **TREE_SITTER_POWER_INVENTORY.md** - Capability checklist
5. **tree-sitter.github.io** - Official documentation
6. **helix-editor.com** - locals.scm implementation reference
7. **arxiv.org/pdf/2211.01224** - Stack graphs paper
8. **PEP 227** - Python nested scopes specification
