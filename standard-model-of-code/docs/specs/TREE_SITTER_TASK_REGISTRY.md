# TREE-SITTER TASK REGISTRY

> Master registry tracking tree-sitter integration implementation status.
>
> **Created:** 2026-01-21
> **Last Updated:** 2026-01-22 (Full dimension coverage for JS including D6:EFFECT)
> **Status:** PHASES 1-4, 6-7 COMPLETE, PHASE 5 DEFERRED

---

## IMPLEMENTATION STATUS SUMMARY

| Phase | Status | Evidence |
|-------|--------|----------|
| **Phase 1: Foundation** | ✅ COMPLETE | `queries/`, loader, 25 .scm files |
| **Phase 2: Scope Analysis** | ✅ COMPLETE | `scope_analyzer.py` (824 lines) |
| **Phase 3: Control Flow** | ✅ COMPLETE | `control_flow_analyzer.py` (475 lines) |
| **Phase 4: Pattern Detection** | ✅ COMPLETE | `data_flow_analyzer.py` (872 lines), patterns.scm |
| **Phase 5: Advanced Features** | ⏸️ DEFERRED | Cross-file, injections - low alignment |
| **Phase 6: D3 ROLE Queries** | ✅ COMPLETE | roles.scm (Python, JavaScript, TypeScript, Go, Rust), imports.scm |
| **Phase 7: Visualization** | ✅ COMPLETE | UPB wiring, 15 SOURCES, 11 PRESETS |

**Tests:** 216 passing (100%)

---

## IMPLEMENTED FILES

### Core Analyzers (3,170 lines)

| File | Lines | Purpose |
|------|-------|---------|
| `src/core/tree_sitter_engine.py` | 999 | Main tree-sitter engine |
| `src/core/scope_analyzer.py` | 824 | Lexical scope analysis |
| `src/core/data_flow_analyzer.py` | 872 | D6:EFFECT purity detection |
| `src/core/control_flow_analyzer.py` | 475 | Cyclomatic complexity, nesting |

### Query Files (24 .scm files)

```
src/core/queries/
├── __init__.py              # Query loader (271 lines)
├── python/                  # 9 queries (full dimension coverage)
│   ├── symbols.scm          # Function/class extraction
│   ├── locals.scm           # Scope tracking
│   ├── patterns.scm         # Atom detection
│   ├── data_flow.scm        # Assignment tracking
│   ├── state.scm            # D5:STATE
│   ├── boundary.scm         # D4:BOUNDARY
│   ├── lifecycle.scm        # D7:LIFECYCLE
│   ├── imports.scm          # Import/export extraction
│   └── roles.scm            # D3:ROLE detection (278 lines)
├── javascript/              # 9 queries (full dimension coverage)
│   ├── symbols.scm
│   ├── locals.scm
│   ├── patterns.scm
│   ├── imports.scm          # ES6/CommonJS imports
│   ├── roles.scm            # D3:ROLE (358 lines)
│   ├── boundary.scm         # D4:BOUNDARY (219 lines)
│   ├── state.scm            # D5:STATE (249 lines)
│   ├── lifecycle.scm        # D7:LIFECYCLE (252 lines)
│   └── data_flow.scm        # D6:EFFECT (267 lines)
├── typescript/              # 2 queries
│   ├── symbols.scm
│   └── roles.scm            # D3:ROLE + interfaces/types (207 lines)
├── go/                      # 2 queries
│   ├── symbols.scm
│   └── roles.scm            # D3:ROLE (313 lines)
├── rust/                    # 2 queries
│   ├── symbols.scm
│   └── roles.scm            # D3:ROLE (247 lines)
└── _fallback/
    └── symbols.scm
```

### Pipeline Integration

| Stage | Name | Status |
|-------|------|--------|
| 2.8 | Scope Analysis | ✅ Integrated |
| 2.9 | Control Flow Metrics | ✅ Integrated |
| 2.10 | Pattern-Based Atom Detection | ✅ Integrated |
| 2.11 | Data Flow Analysis (D6:EFFECT) | ✅ Integrated |

### Visualization (UPB)

| Category | Items | Location |
|----------|-------|----------|
| SOURCES | 15 new | `upb/endpoints.js` |
| PRESETS | 11 new | `upb/bindings.js` |
| UI Optgroups | 3 new | `control-bar.js` |

**Dropdown Options Added:**
- Tree-sitter Analysis: D6_pure_score, D6_EFFECT, pagerank, betweenness_centrality, topology_role
- Control Flow (P3-09): cyclomatic_complexity, complexity_rating, max_nesting_depth, nesting_rating
- RPBL Character: rpbl_responsibility, rpbl_purity, rpbl_boundary, rpbl_lifecycle

---

## DEFERRED TASKS (Phase 5)

These tasks have low alignment with core mission and are deferred:

| Task | Confidence | Reason |
|------|------------|--------|
| Cross-file data flow | 50% | Significant architecture work |
| SQL injection parsing | 40% | Low priority, unclear value |
| GraphQL injection parsing | 40% | Low priority, unclear value |
| highlights.scm | 30% | Not core mission |

---

## CONFIDENCE METHODOLOGY (Reference)

**Confidence = min(Factual, Alignment)**

| Level | Meaning |
|-------|---------|
| **95%+** | Execute |
| **90-94%** | Almost ready |
| **85-89%** | Needs work |
| **<70%** | Do not execute |

---

## COMMITS (Implementation History)

| Hash | Description |
|------|-------------|
| `2102f8d` | JavaScript data_flow.scm for D6:EFFECT purity |
| `76103db` | JavaScript dimension queries (D4, D5, D7) |
| `19f2617` | Go and Rust roles.scm |
| `5bd8d53` | JavaScript and TypeScript roles.scm |
| `1212338` | Data flow analyzer (D6:EFFECT purity) |
| `288ee4b` | Wire tree-sitter data to visualization (P7) |
| `17f93cd` | Wire control flow metrics (P3-09) |
| `e20f966` | Wire RPBL character scores (P4-05/07/08) |
| `f063523` | Fix React atom pattern matching order |

---

## DOCUMENT STATUS

- [x] Phase 1 Foundation: COMPLETE
- [x] Phase 2 Scope Analysis: COMPLETE
- [x] Phase 3 Control Flow: COMPLETE
- [x] Phase 4 Pattern Detection: COMPLETE
- [ ] Phase 5 Advanced Features: DEFERRED
- [x] Phase 6 D3 ROLE Queries: COMPLETE (roles.scm for Python, JavaScript, TypeScript, Go, Rust)
- [x] Phase 7 Visualization: COMPLETE
- [x] All tests passing (216/216)
