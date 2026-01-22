# TREE-SITTER VALIDATION REPORT

> Evidence-based validation of Tree-sitter capabilities in Collider.
>
> **Validation Date:** 2026-01-21
> **Validation Method:** Live Python tests against installed packages
> **Status:** VALIDATED

---

## 1. INSTALLED VERSIONS (FACT)

Verified via `pip show`:

| Package | Version | Status |
|---------|---------|--------|
| tree-sitter | 0.25.2 | INSTALLED |
| tree-sitter-python | 0.25.0 | INSTALLED |
| tree-sitter-javascript | 0.25.0 | INSTALLED |
| tree-sitter-typescript | 0.23.2 | INSTALLED |
| tree-sitter-go | (configured) | IN pyproject.toml |
| tree-sitter-rust | (configured) | IN pyproject.toml |
| tree-sitter-java | (configured) | IN pyproject.toml |

---

## 2. API AVAILABILITY (VALIDATED)

### 2.1 tree_sitter Module Contents

```python
# Verified via dir(tree_sitter)
['LANGUAGE_VERSION', 'Language', 'LogType', 'LookaheadIterator',
 'MIN_COMPATIBLE_LANGUAGE_VERSION', 'Node', 'Parser', 'Point',
 'Query', 'QueryCursor', 'QueryError', 'QueryPredicate', 'Range',
 'Tree', 'TreeCursor']
```

**All major classes exist:** Query, QueryCursor, TreeCursor, Node, Tree, Parser, Language

### 2.2 Query Class Methods

```python
# Verified via dir(tree_sitter.Query)
['capture_count', 'capture_name', 'capture_quantifier', 'disable_capture',
 'disable_pattern', 'end_byte_for_pattern', 'is_pattern_guaranteed_at_step',
 'is_pattern_non_local', 'is_pattern_rooted', 'pattern_assertions',
 'pattern_count', 'pattern_settings', 'start_byte_for_pattern',
 'string_count', 'string_value']
```

### 2.3 QueryCursor Class Methods

```python
# Verified via dir(tree_sitter.QueryCursor)
['captures', 'did_exceed_match_limit', 'match_limit', 'matches',
 'set_byte_range', 'set_max_start_depth', 'set_point_range', 'timeout_micros']
```

### 2.4 Node Class Methods

```python
# Verified via dir(node)
['byte_range', 'child', 'child_by_field_id', 'child_by_field_name',
 'child_count', 'child_with_descendant', 'children', 'children_by_field_id',
 'children_by_field_name', 'descendant_count', 'descendant_for_byte_range',
 'descendant_for_point_range', 'edit', 'end_byte', 'end_point',
 'field_name_for_child', 'field_name_for_named_child', 'first_child_for_byte',
 'first_named_child_for_byte', 'grammar_id', 'grammar_name', 'has_changes',
 'has_error', 'id', 'is_error', 'is_extra', 'is_missing', 'is_named',
 'kind_id', 'named_child', 'named_child_count', 'named_children',
 'named_descendant_for_byte_range', 'named_descendant_for_point_range',
 'next_named_sibling', 'next_parse_state', 'next_sibling', 'parent',
 'parse_state', 'prev_named_sibling', 'prev_sibling', 'range',
 'start_byte', 'start_point', 'text', 'type', 'walk']
```

### 2.5 Tree Class Methods

```python
# Verified via dir(tree)
['changed_ranges', 'copy', 'edit', 'included_ranges', 'language',
 'print_dot_graph', 'root_node', 'root_node_with_offset', 'walk']
```

### 2.6 TreeCursor Methods (via tree.walk())

```python
# Verified via dir(tree.walk())
['copy', 'depth', 'descendant_index', 'field_id', 'field_name',
 'goto_descendant', 'goto_first_child', 'goto_first_child_for_byte',
 'goto_first_child_for_point', 'goto_last_child', 'goto_next_sibling',
 'goto_parent', 'goto_previous_sibling', 'node', 'reset', 'reset_to']
```

---

## 3. QUERY PREDICATES (VALIDATED)

### 3.1 Working Predicates

| Predicate | Test Query | Result |
|-----------|------------|--------|
| `#eq?` | `((function_definition name: (identifier) @name) (#eq? @name "foo"))` | **WORKS** - captured ['foo'] |
| `#not-eq?` | `((function_definition name: (identifier) @name) (#not-eq? @name "foo"))` | **WORKS** - captured ['bar', 'Baz'] |
| `#match?` | `((function_definition name: (identifier) @name) (#match? @name "^[A-Z]"))` | **WORKS** - captured ['Baz'] |
| `#not-match?` | `((function_definition name: (identifier) @name) (#not-match? @name "^[A-Z]"))` | **WORKS** - captured ['foo', 'bar'] |
| `#any-of?` | `((function_definition name: (identifier) @name) (#any-of? @name "foo" "bar"))` | **WORKS** - captured ['foo', 'bar'] |
| `#any-eq?` | For quantified captures | **WORKS** |
| `#any-match?` | For quantified captures | **WORKS** |
| `#set!` | `(string) @str (#set! injection.language "sql")` | **WORKS** - directive stored |

### 3.2 Non-Working Predicates (Correction)

| Predicate | Issue |
|-----------|-------|
| `#is?` | **NOT** `(#is? @capture property)` format. Requires: `(#is? "property" "value")` with string literals |
| `#is-not?` | Same issue - designed for locals.scm property system, not general capture filtering |

**Note:** These predicates are designed for the locals.scm scope tracking system and don't work as general capture filters.

---

## 4. QUERY FEATURES (VALIDATED)

| Feature | Test | Result |
|---------|------|--------|
| Basic patterns | `(function_definition name: (identifier) @name)` | **WORKS** |
| Field access | `name: (identifier)` | **WORKS** |
| Negated fields | `(function_definition !return_type name: (identifier) @fn)` | **WORKS** |
| Wildcard | `(function_definition body: (_) @body)` | **WORKS** - returns block nodes |
| Alternation | `[(function_definition) (class_definition)] @def` | **WORKS** |
| Quantifiers | `(decorator)* @decs` | **WORKS** (returns empty if no matches) |
| set_byte_range | `cursor.set_byte_range(0, 30)` | **WORKS** - limits results |

---

## 5. TREE FEATURES (VALIDATED)

### 5.1 Incremental Parsing

```python
# VALIDATED WORKING:
tree.edit(
    start_byte=20,
    old_end_byte=20,
    new_end_byte=30,
    start_point=(2, 0),
    old_end_point=(2, 0),
    new_end_point=(3, 0)
)
new_tree = parser.parse(new_code, old_tree)
changes = old_tree.changed_ranges(new_tree)
# Returns list of Range objects with changed regions
```

### 5.2 Error Detection

```python
# VALIDATED WORKING:
tree = parser.parse(b"def foo(\n    pass")  # Broken code
tree.root_node.has_error  # True
# ERROR nodes appear in tree with type 'ERROR'
```

### 5.3 TreeCursor Navigation

```python
# VALIDATED WORKING:
cursor = tree.walk()
cursor.goto_first_child()  # Returns bool
cursor.goto_next_sibling()  # Returns bool
cursor.goto_parent()  # Returns bool
cursor.node  # Current Node object
```

---

## 6. NODE TYPES BY LANGUAGE (VALIDATED)

### 6.1 Python (66 named types found)

**Definitions:**
- `function_definition`
- `class_definition`
- `decorated_definition`

**Note:** No separate `async_function_definition` - async functions are `function_definition` with `async` keyword child.

**Statements (18):**
`assert_statement`, `break_statement`, `continue_statement`, `delete_statement`, `expression_statement`, `for_statement`, `global_statement`, `if_statement`, `import_from_statement`, `import_statement`, `match_statement`, `nonlocal_statement`, `pass_statement`, `raise_statement`, `return_statement`, `try_statement`, `with_statement`, `yield`

**Expressions (12):**
`assignment`, `attribute`, `await`, `binary_operator`, `call`, `comparison_operator`, `dictionary_comprehension`, `generator_expression`, `lambda`, `list_comprehension`, `set_comprehension`

**Control Flow (12):**
`case_clause`, `elif_clause`, `else_clause`, `except_clause`, `finally_clause`, `for_in_clause`, `if_clause`, `with_clause`, `with_item`

### 6.2 JavaScript (71 named types found)

**Definitions (9):**
`arrow_function`, `class_body`, `class_declaration`, `class_heritage`, `field_definition`, `function_declaration`, `generator_function_declaration`, `lexical_declaration`, `method_definition`

**JSX (4):**
`jsx_element`, `jsx_self_closing_element`, `jsx_opening_element`, `jsx_closing_element`, `jsx_attribute`, `jsx_expression`

**Statements (19):**
Includes `export_statement`, `import_statement`, `try_statement`, `switch_statement`, etc.

**Expressions (11):**
Includes `call_expression`, `member_expression`, `await_expression`, `optional_chain`, `spread_element`, etc.

---

## 7. CURRENT COLLIDER USAGE (VALIDATED)

### 7.1 tree_sitter_engine.py

| Feature | Usage | Evidence |
|---------|-------|----------|
| Parser.parse() | YES | Line 370 |
| Query API | YES | Lines 382-424, 427-441 |
| #match? predicate | YES | Lines 402, 408 (React detection) |
| QueryCursor.captures() | YES | Line 444 |
| child_by_field_name() | YES | Lines 469-507 |
| Byte range for hooks | YES | Lines 579-580 (_node_start_byte, _node_end_byte) |

**Query Blocks Found:** 6 (Rust, Go, JS/TS, fallback Rust, fallback JS)

### 7.2 edge_extractor.py

| Feature | Usage | Evidence |
|---------|-------|----------|
| Parser.parse() | YES | JSModuleResolver, TreeSitterEdgeStrategy |
| Query API | **NO** | Uses manual visit() recursion |
| Node type checks | YES | ~11 types checked |
| child_by_field_name() | YES | member_expression, call_expression parsing |

**TreeSitter Strategies:** PythonTreeSitterStrategy, JavaScriptTreeSitterStrategy, TypeScriptTreeSitterStrategy

---

## 8. CORRECTIONS TO INITIAL SPEC

| Item | Initial Assumption | Validated Reality |
|------|-------------------|-------------------|
| #is? predicate | Works like `(#is? @capture property)` | **WRONG** - requires `(#is? "key" "value")` format |
| async_function_definition | Separate Python node type | **WRONG** - uses `function_definition` with `async` child |
| QueryPredicate class | Usable for custom predicates | **LIMITED** - no public methods, internal use |
| Node types per language | ~100 assumed | Python: 66, JS: 71 (in test sample) |
| TreeCursor availability | Assumed available | **CONFIRMED** - tree_sitter.TreeCursor exists |
| Incremental parsing | Assumed API exists | **CONFIRMED** - Tree.edit() + changed_ranges() work |

---

## 9. VALIDATED RECOMMENDATIONS

### 9.1 High Confidence (Validated Working)

1. **Use Query API in edge_extractor.py** - Replace manual visit() with Query patterns
2. **Use QueryCursor.set_byte_range()** - For scoped queries within functions
3. **Use #any-of? predicate** - For multi-pattern matching (CRUD methods, etc.)
4. **Check node.has_error** - For syntax quality metrics
5. **Extract queries to .scm files** - For maintainability

### 9.2 Medium Confidence (API Exists, Needs Integration Work)

6. **Implement incremental parsing** - Tree.edit() works, needs file watcher
7. **Use TreeCursor for large files** - Memory-efficient traversal available
8. **Leverage pattern_settings()** - For injection metadata via #set!

### 9.3 Needs Further Validation

9. **locals.scm scope tracking** - #is?/#is-not? work differently than assumed
10. **Cross-file data flow** - Requires significant architecture work

---

## 10. TEST CODE REFERENCE

All validations were performed with live Python code. Key test patterns:

```python
import tree_sitter
import tree_sitter_python

lang = tree_sitter.Language(tree_sitter_python.language())
parser = tree_sitter.Parser()
parser.language = lang
tree = parser.parse(b"code here")

# Query execution
query = tree_sitter.Query(lang, "pattern here")
cursor = tree_sitter.QueryCursor(query)
captures = cursor.captures(tree.root_node)

# Incremental parsing
tree.edit(start_byte=X, old_end_byte=Y, new_end_byte=Z, ...)
new_tree = parser.parse(new_code, tree)
changes = tree.changed_ranges(new_tree)

# Error detection
tree.root_node.has_error  # bool
```

---

## 11. D3_ROLE CLASSIFICATION (VALIDATED 2026-01-22)

### 11.1 Implementation Status

The `classify_role()` method in `dimension_classifier.py` is now **wired into the pipeline** via `universal_classifier.py`.

| Component | Status | Evidence |
|-----------|--------|----------|
| `roles.scm` queries | ✅ Loaded | Python, JavaScript, TypeScript |
| `classify_role()` method | ✅ Called | `universal_classifier.py:625-629` |
| Tiered fallback | ✅ Working | Tree-sitter → Heuristic |

### 11.2 Coverage Metrics

Tested on `src/core/classification/` (17 nodes):

| Source | Count | Percentage |
|--------|-------|------------|
| tree-sitter | 4 | 24% |
| heuristic | 12 | 71% |
| none | 1 | 5% |

**Average confidence (tree-sitter):** 81.2%

### 11.3 Detected Role Patterns

| Role | Confidence | Pattern |
|------|------------|---------|
| Repository | 90% | `find_by_*`, `save`, `query` methods |
| Validator | 85% | `validate_*`, raises `ValidationError` |
| Handler | 80% | `*_pattern`, processing methods |
| Lifecycle | 85% | `__init__`, `__del__`, `close` |
| Service | 85% | Business logic orchestration |

### 11.4 Cross-Language Results

```python
# Python
UserRepository → Repository (90%, tree-sitter)
validate_email → Validator (85%, tree-sitter)

# JavaScript
UserService → Repository (90%, tree-sitter)
  boundary: io
  state: stateful
```

### 11.5 Schema Impact

New fields in `dimensions` object:

```json
{
  "D3_ROLE": "Repository",
  "D3_ROLE_SOURCE": "tree-sitter",
  "D3_ROLE_CONFIDENCE": 90,
  "D3_ROLE_EVIDENCE": ["find_by_id", "save"]
}
```

---

## DOCUMENT STATUS

- [x] API availability validated
- [x] Query predicates tested
- [x] Query features tested
- [x] Tree features tested
- [x] Node types enumerated
- [x] Current usage audited
- [x] Corrections documented
- [x] Recommendations prioritized
- [x] D3_ROLE classification validated (2026-01-22)

**This document supersedes assumptions in TREE_SITTER_INTEGRATION_SPEC.md for any conflicts.**
