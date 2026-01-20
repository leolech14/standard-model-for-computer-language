# Taxonomy Gap Report

> Analysis of implementation gaps in Atoms (Structure) and Roles (Purpose)

**Generated:** 2026-01-20
**Status:** ACTION REQUIRED

---

## Executive Summary

| Taxonomy | Canonical | Implemented | Gap | Coverage |
|----------|-----------|-------------|-----|----------|
| **Atoms** (Structure) | 200 | ~94 | 106 | 47% |
| **Roles** (Purpose) | 33 | 13 | 20 | 39% |

**Critical Finding:** Role coverage is worse than atom coverage. The purpose layer (π₁) is only 39% complete.

---

## ATOMS GAP (Structure Layer)

### Summary

| Metric | Value |
|--------|-------|
| Documented in 200_ATOMS.md | 200 |
| Unique Atom IDs (categories) | 22 |
| Implemented Atom IDs | 14 |
| **Missing Atom IDs** | **8** |

### Missing Atom Categories

| Atom ID | Count | Examples | Domain |
|---------|-------|----------|--------|
| `DAT.BIT.A` | 4 | BitFlag, BitMask, ParityBit, SignBit | Bit-level data |
| `DAT.COL.A` | 4 | ArrayLiteral, ObjectLiteral, TupleLiteral, SetLiteral | Collections |
| `EXE.IO.O` | 10 | FileRead, FileWrite, NetworkRead, StdinRead, HttpRequest | I/O Operations |
| `EXE.MEM.O` | 8 | Allocation, Deallocation, Reference, Borrow, Clone | Memory Management |
| `EXE.MET.O` | 10 | MacroDef, Reflection, CodeGen, Preprocessor, FFI | Metaprogramming |
| `EXE.WRK.O` | 12 | Thread, Process, Goroutine, Task, Future, Channel | Concurrency |
| `ORG.FIL.O` | 6 | SourceFile, Header, ConfigFile, TestFile, SchemaFile | File Types |
| `ORG.TYP.O` | 15 | TypeRef, ArrayType, FunctionType, GenericParam | Type System |

### Atoms by Phase

| Phase | Count | Description |
|-------|-------|-------------|
| DATA | 28 | Primitives, variables, collections |
| LOGIC | 47 | Functions, expressions, control flow |
| ORGANIZATION | 47 | Classes, modules, types |
| EXECUTION | 59 | I/O, memory, concurrency, lifecycle |

### Implementation Status

**Implemented Atom IDs (14):**
```
DAT.BYT.A  DAT.PRM.A  DAT.VAR.A  LOG.EXP.A  LOG.STM.A
LOG.CTL.A  LOG.FNC.M  ORG.MOD.O  ORG.AGG.M  ORG.SVC.M
EXE.INI.O  EXE.HDL.O  SYS.CFG.O  SYS.DEP.O
```

---

## ROLES GAP (Purpose Layer)

### Summary

| Metric | Value |
|--------|-------|
| Canonical roles (roles.json) | 33 |
| Implemented (matching canonical) | 13 |
| **Missing from implementation** | **20** |
| Extra (not canonical) | 16 |

### Missing Canonical Roles (20)

| Role | Purpose | Priority |
|------|---------|----------|
| **Asserter** | Assert truth of conditions | HIGH |
| **Cache** | Temporarily store data for performance | HIGH |
| **Creator** | Create new entity/record | HIGH |
| **Destroyer** | Delete/remove entity | HIGH |
| **Emitter** | Emit/publish events | HIGH |
| **Finder** | Search for data based on criteria | HIGH |
| **Formatter** | Format output for display | MEDIUM |
| **Getter** | Access property/attribute | HIGH |
| **Guard** | Protect access or enforce conditions | HIGH |
| **Helper** | Specific assistive logic | LOW |
| **Listener** | Passive event observation | MEDIUM |
| **Loader** | Load data from storage/source | HIGH |
| **Manager** | Manage resources or components | HIGH |
| **Mutator** | Modify existing entity/state | HIGH |
| **Orchestrator** | Coordinate complex workflows | HIGH |
| **Parser** | Parse input format to data | HIGH |
| **Serializer** | Serialize properties to output format | HIGH |
| **Store** | Manage application state | HIGH |
| **Subscriber** | Subscribe to event stream | MEDIUM |
| **Transformer** | Convert data format | HIGH |

### Implemented Canonical Roles (13)

```
✓ Builder      ✓ Command     ✓ Controller  ✓ Factory
✓ Handler      ✓ Internal    ✓ Lifecycle   ✓ Mapper
✓ Query        ✓ Repository  ✓ Service     ✓ Utility
✓ Validator
```

### Extra Roles (Not in Canonical 33)

These exist in implementation but aren't in `roles.json`:

```
Adapter       Benchmark     Client        Configuration
Example       Exception     Fixture       Impl
Iterator      Job           Middleware    Policy
Provider      Specification Test          Unknown
```

**Decision needed:** Should these be added to canonical roles.json?

---

## Root Cause Analysis

### Why the Gap Exists

1. **Atoms:** The 200_ATOMS.md is a theoretical taxonomy. Implementation focused on most common patterns first (Tier 0/1), deferring specialized atoms (I/O, memory, metaprogramming) to later.

2. **Roles:** The `heuristic_classifier.py` was built pragmatically, adding roles as encountered in real codebases. It diverged from the canonical `roles.json` definition.

### The π₁ Equation Impact

```
π₁(node) = role(node)
```

If only 13 of 33 roles are implemented, then:
- 60% of code nodes may get incorrect/missing purpose classification
- The "Purpose Field" (Section 4 of MODEL.md) is incomplete

---

## Recommendations

### Priority 1: Complete Roles (Purpose Layer)

| Action | Effort | Impact |
|--------|--------|--------|
| Add 20 missing roles to classifier | Medium | HIGH - completes purpose layer |
| Reconcile 16 extra roles with canonical | Low | Clarity |

### Priority 2: Complete Atoms (Structure Layer)

| Action | Effort | Impact |
|--------|--------|--------|
| Add 8 missing Atom IDs to atoms.json | Low | Structural completeness |
| Add AST mappings for new IDs | Medium | Recognition capability |

### Priority 3: Reconciliation

| Action | Effort | Impact |
|--------|--------|--------|
| Update MODEL.md with accurate counts | Low | Documentation truth |
| Decide on extra roles (canonical or remove) | Low | Single source of truth |

---

## Verification Commands

```bash
# Count atoms in 200_ATOMS.md
grep -E "^\| [0-9]+ \|" standard-model-of-code/schema/fixed/200_ATOMS.md | wc -l

# Count canonical roles
jq '.roles | keys | length' standard-model-of-code/schema/fixed/roles.json

# List implemented roles in classifier
grep -oE "'[A-Z][a-z]+'" standard-model-of-code/src/core/heuristic_classifier.py | sort | uniq

# Count atoms in implementation
grep -c "id:" standard-model-of-code/src/patterns/ATOMS_TIER*.yaml
```

---

## Next Steps

1. [ ] Add 20 missing roles to `heuristic_classifier.py`
2. [ ] Add 8 missing Atom IDs to `atoms.json`
3. [ ] Update MODEL.md line 74 (correct implementation count)
4. [ ] Decide fate of 16 extra roles
5. [ ] Add recognition patterns for new atoms/roles

---

*Report generated by Claude Opus 4.5 | Validated against source files*
