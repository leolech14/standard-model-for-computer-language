# Infallible Plan: Taxonomy Completion

> Haiku-deployable instructions for completing Atoms (Structure) and Roles (Purpose) taxonomies.

**Generated:** 2026-01-20
**Source:** Gemini 2.5 Pro analysis
**Status:** READY FOR DEPLOYMENT

---

## Executive Summary

| Task | Steps | Impact |
|------|-------|--------|
| Add 20 missing roles to classifier | 1 | Completes Purpose Layer (π₁) |
| Add 8 missing atom IDs to atoms.json | 1 | Completes Structure Layer |
| Reconcile 16 extra roles | 3 | Single source of truth |
| **Total** | **5** | **100% taxonomy coverage** |

---

## TASK 1: Add 20 Missing Canonical Roles

**File:** `standard-model-of-code/src/core/heuristic_classifier.py`

### Step 1 of 5: Add Keyword Mappings for Missing Roles

Insert after the class definition, before `PREFIX_ROLES`:

```python
# Mappings for the 20 missing canonical roles from TAXONOMY_GAP_REPORT.md
MISSING_CANONICAL_ROLES = {
    'Asserter': ['assert', 'ensure', 'must'],
    'Cache': ['cache', 'memoize'],
    'Creator': ['create', 'new_entity', 'make_record'],
    'Destroyer': ['destroy', 'delete_entity', 'remove_record'],
    'Emitter': ['emit', 'publish', 'broadcast'],
    'Finder': ['find', 'search'],
    'Formatter': ['format', 'pretty_print', 'display_as'],
    'Getter': ['get_property', 'accessor'],
    'Guard': ['guard', 'can_activate', 'protect', 'check_access'],
    'Helper': ['helper', 'assist'],
    'Listener': ['listen', 'observe'],
    'Loader': ['load_data', 'fetch_from_source'],
    'Manager': ['manage', 'resource_manager'],
    'Mutator': ['mutate', 'modify', 'update_state'],
    'Orchestrator': ['orchestrate', 'coordinate', 'workflow'],
    'Parser': ['parse', 'lex', 'tokenize'],
    'Serializer': ['serialize', 'dump_to_format'],
    'Store': ['store', 'state_store', 'app_state'],
    'Subscriber': ['subscribe', 'on_message'],
    'Transformer': ['transform', 'convert_data']
}
```

Add this detection logic after dunder method check:

```python
# 1.5 Check for missing canonical role keywords (High Priority)
for role, keywords in self.MISSING_CANONICAL_ROLES.items():
    if any(keyword in short_lower for keyword in keywords):
        self.discovered_patterns[f'canonical_keyword:{role}'] += 1
        return (role, 90.0)
```

**Verification:**
```bash
grep -oE "'[A-Z][a-z]+'" standard-model-of-code/src/core/heuristic_classifier.py | sed "s/'//g" | sort | uniq | wc -l
# Expected: 49+ (13 old + 20 new + 16 extra before remapping)
```

---

## TASK 2: Add 8 Missing Atom IDs

**File:** `standard-model-of-code/src/patterns/atoms.json`

### Step 2 of 5: Add Missing Atom Objects

Add these 8 atom definitions to the `"atoms"` object:

```json
"DAT.BIT.A": {
    "id": "DAT.BIT.A",
    "name": "Bit",
    "layer": "Data",
    "description": "Bit-level data operations. Examples: BitFlag, BitMask, ParityBit."
},
"DAT.COL.A": {
    "id": "DAT.COL.A",
    "name": "Collection",
    "layer": "Data",
    "description": "Collection literals. Examples: ArrayLiteral, ObjectLiteral, TupleLiteral."
},
"EXE.IO.O": {
    "id": "EXE.IO.O",
    "name": "IO Operation",
    "layer": "Execution",
    "description": "I/O operations. Examples: FileRead, FileWrite, NetworkRead, HttpRequest."
},
"EXE.MEM.O": {
    "id": "EXE.MEM.O",
    "name": "Memory Operation",
    "layer": "Execution",
    "description": "Memory management operations. Examples: Allocation, Deallocation, Reference, Clone."
},
"EXE.MET.O": {
    "id": "EXE.MET.O",
    "name": "Metaprogramming",
    "layer": "Execution",
    "description": "Metaprogramming operations. Examples: MacroDef, Reflection, CodeGen, FFI."
},
"EXE.WRK.O": {
    "id": "EXE.WRK.O",
    "name": "Worker",
    "layer": "Execution",
    "description": "Concurrency primitives. Examples: Thread, Process, Goroutine, Task, Future."
},
"ORG.FIL.O": {
    "id": "ORG.FIL.O",
    "name": "File",
    "layer": "Organization",
    "description": "Code organization at the file level. Examples: SourceFile, Header, ConfigFile."
},
"ORG.TYP.O": {
    "id": "ORG.TYP.O",
    "name": "Type",
    "layer": "Organization",
    "description": "Type system constructs. Examples: TypeRef, ArrayType, FunctionType."
}
```

**Verification:**
```bash
jq '.atoms | keys | length' standard-model-of-code/src/patterns/atoms.json
# Expected: 22 (14 existing + 8 new)
```

---

## TASK 3: Reconcile 16 Extra Roles

**Decision:** Remap extra roles to canonical equivalents (do NOT modify roles.json).

### Remapping Table

| Extra Role | Canonical Equivalent | Rationale |
|------------|---------------------|-----------|
| EventHandler | Handler | Direct mapping |
| Adapter | Mapper | Transforms interfaces |
| Benchmark | Asserter | Asserts performance truth |
| Client | Service | Consumes services |
| Configuration | Store | State management |
| Example | Asserter | Demonstrates/asserts behavior |
| Exception | Handler | Handles exceptional events |
| Fixture | Asserter | Test setup for assertions |
| Impl | Internal | Implementation detail |
| Iterator | Query | Sequential data access |
| Job | Command | Executable task |
| Middleware | Guard | Intercepts/protects access |
| Policy | Guard | Enforces rules |
| Provider | Factory | Provides instances |
| Specification | Asserter | Specifies truth conditions |
| Test | Asserter | Asserts truth of conditions |

### Step 3 of 5: Remap EventHandler to Handler

Replace all `'EventHandler'` with `'Handler'` in heuristic_classifier.py.

**Verification:**
```bash
! grep -q "'EventHandler'" standard-model-of-code/src/core/heuristic_classifier.py
# Expected: Exit code 0 (no matches)
```

### Step 4 of 5: Remap All Other Extra Roles

Apply the remapping table above throughout heuristic_classifier.py.

Key changes:
- `'Test'` → `'Asserter'`
- `'Specification'` → `'Asserter'`
- `'Fixture'` → `'Asserter'`
- `'Configuration'` → `'Store'`
- `'Policy'` → `'Guard'`
- `'Iterator'` → `'Query'`
- `'Job'` → `'Command'`
- `'Exception'` → `'Handler'`
- `'Adapter'` → `'Mapper'`
- `'Client'` → `'Service'`
- `'Provider'` → `'Factory'`
- `'Impl'` → `'Internal'`
- `'Middleware'` → `'Guard'`
- `'Benchmark'` → `'Asserter'`
- `'Example'` → `'Asserter'`

**Verification:**
```bash
EXTRA_ROLES="Adapter|Benchmark|Client|Configuration|Example|Exception|Fixture|Impl|Iterator|Job|Middleware|Policy|Provider|Specification|Test|EventHandler"
! grep -oE "'($EXTRA_ROLES)'" standard-model-of-code/src/core/heuristic_classifier.py
# Expected: Exit code 0 (no matches)
```

### Step 5 of 5: Verify roles.json Unchanged

**Verification:**
```bash
jq '.roles | keys | length' standard-model-of-code/schema/fixed/roles.json
# Expected: 33 (unchanged)
```

---

## Post-Execution Verification

### Full Verification Script

```bash
#!/bin/bash
set -e

echo "=== TAXONOMY COMPLETION VERIFICATION ==="

# 1. Check atom count
ATOMS=$(jq '.atoms | keys | length' standard-model-of-code/src/patterns/atoms.json)
echo "Atoms in atoms.json: $ATOMS (expected: 22)"
[ "$ATOMS" -eq 22 ] || exit 1

# 2. Check canonical roles unchanged
ROLES=$(jq '.roles | keys | length' standard-model-of-code/schema/fixed/roles.json)
echo "Roles in roles.json: $ROLES (expected: 33)"
[ "$ROLES" -eq 33 ] || exit 1

# 3. Check no extra roles in classifier
EXTRA="Adapter|Benchmark|Client|Configuration|Example|Exception|Fixture|Impl|Iterator|Job|Middleware|Policy|Provider|Specification|Test|EventHandler"
if grep -qE "'($EXTRA)'" standard-model-of-code/src/core/heuristic_classifier.py; then
    echo "ERROR: Extra roles still present in classifier"
    exit 1
fi
echo "No extra roles in classifier: PASS"

# 4. Check missing roles added
for role in Asserter Cache Creator Destroyer Emitter Finder Formatter Getter Guard Helper Listener Loader Manager Mutator Orchestrator Parser Serializer Store Subscriber Transformer; do
    if ! grep -q "'$role'" standard-model-of-code/src/core/heuristic_classifier.py; then
        echo "ERROR: Missing role $role not added"
        exit 1
    fi
done
echo "All 20 missing roles added: PASS"

echo ""
echo "=== ALL VERIFICATIONS PASSED ==="
```

---

## Commit Template

```bash
git add standard-model-of-code/src/patterns/atoms.json \
        standard-model-of-code/src/core/heuristic_classifier.py

git commit -m "$(cat <<'EOF'
feat: complete taxonomy - add 20 roles + 8 atoms + reconcile extras

## CHANGES
| File | Description |
|------|-------------|
| src/patterns/atoms.json | Add 8 missing atom IDs (DAT.BIT.A, DAT.COL.A, EXE.IO/MEM/MET/WRK.O, ORG.FIL/TYP.O) |
| src/core/heuristic_classifier.py | Add 20 missing canonical roles, remap 16 extras |

## TAXONOMY STATUS
- Atoms: 22 IDs (was 14) - 100% coverage
- Roles: 33 canonical (classifier now uses only canonical roles)

## VERIFICATION
jq '.atoms | keys | length' src/patterns/atoms.json  # 22
jq '.roles | keys | length' schema/fixed/roles.json  # 33 (unchanged)

## THEORY REFERENCE
- π₁(node) = role(node) - Purpose equation now fully implemented
- 200_ATOMS.md structural categories now complete

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
Co-Authored-By: Gemini 2.5 Pro <noreply@google.com>
EOF
)"
```

---

## Haiku Agent Deployment Notes

1. **Provide this file as context**
2. **Execute steps 1-5 in order**
3. **Run verification after each step**
4. **Run full verification script at end**
5. **Commit with provided template**

---

*Plan generated by Gemini 2.5 Pro | Validated by Claude Opus 4.5*
