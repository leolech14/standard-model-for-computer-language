# Tree-sitter Scope Analysis: Deep Knowledge for Phase 2 Implementation

> **Date:** January 21, 2026
> **Source:** Research compiled from Perplexity, official tree-sitter docs, nvim-treesitter
> **Purpose:** Enable Phase 2 implementation of scope analysis in Collider

---

## 1. The Three Core Capture Patterns (locals.scm)

The locals.scm system uses **exactly three** semantic capture names:

| Pattern | Purpose | Stack Operation |
|---------|---------|-----------------|
| `@local.scope` | Marks syntax node that introduces new scope | PUSH to scope stack |
| `@local.definition` | Marks name being defined in current scope | RECORD in current scope |
| `@local.reference` | Marks name that may refer to earlier definition | SEARCH up scope stack |

**Critical insight:** These are NOT arbitrary names like highlights.scm uses. They have **fixed meaning** in tree-sitter's scope resolution engine.

---

## 2. How Scope Tracking Works Internally

```
SCOPE STACK (maintained during tree traversal):
┌─────────────────────────────────┐
│ Inner Function Scope            │  ← TOP (current)
│   definitions: [param2, y]      │
├─────────────────────────────────┤
│ Outer Function Scope            │
│   definitions: [param1, x]      │
├─────────────────────────────────┤
│ Module/Global Scope             │
│   definitions: [globalVar]      │
└─────────────────────────────────┘  ← BOTTOM

REFERENCE RESOLUTION:
1. Encounter @local.reference for identifier "x"
2. Search TOP scope (Inner Function) → NOT FOUND
3. Search NEXT scope (Outer Function) → FOUND!
4. Pair reference with definition
5. Both get same highlight/semantic token
```

**Shadowing is automatic:** First match wins (inner definitions shadow outer ones).

---

## 3. Concrete Python locals.scm

```scheme
; ============================================================
; python_locals.scm - Scope analysis for Python
; ============================================================

; SCOPES
; ------
; Function definitions create new scopes
(function_definition) @local.scope

; Lambda creates scope
(lambda) @local.scope

; Comprehensions create implicit scopes
(list_comprehension) @local.scope
(dictionary_comprehension) @local.scope
(set_comprehension) @local.scope
(generator_expression) @local.scope

; NOTE: Class bodies do NOT create lexical scopes in Python!
; Methods cannot access class-level variables without self/cls
; This is per PEP 227

; DEFINITIONS
; -----------
; Function/method parameters
(parameters (identifier) @local.definition)
(default_parameter name: (identifier) @local.definition)
(typed_parameter (identifier) @local.definition)
(typed_default_parameter name: (identifier) @local.definition)

; Lambda parameters
(lambda_parameters (identifier) @local.definition)

; Assignment targets
(assignment left: (identifier) @local.definition)

; Augmented assignment
(augmented_assignment left: (identifier) @local.definition)

; For loop variables
(for_statement left: (identifier) @local.definition)

; Comprehension iterators
(for_in_clause left: (identifier) @local.definition)

; With statement binding
(with_item value: (identifier) @local.definition)

; Exception handlers
(except_clause (identifier) @local.definition)

; Import aliases
(aliased_import alias: (identifier) @local.definition)
(import_from_statement name: (identifier) @local.definition)

; Named expression (walrus operator)
(named_expression name: (identifier) @local.definition)

; REFERENCES
; ----------
; All other identifiers are potential references
(identifier) @local.reference

; NOTE: The engine automatically excludes identifiers already
; captured as @local.definition from being @local.reference
```

---

## 4. Concrete JavaScript locals.scm

```scheme
; ============================================================
; javascript_locals.scm - Scope analysis for JavaScript
; ============================================================

; SCOPES
; ------
; Functions (all types)
(function_declaration) @local.scope
(function_expression) @local.scope
(arrow_function) @local.scope
(method_definition) @local.scope
(generator_function_declaration) @local.scope

; Block statements (for let/const block scoping)
(statement_block) @local.scope

; For loops create scope for let/const
(for_statement) @local.scope
(for_in_statement) @local.scope

; Class bodies
(class_body) @local.scope

; DEFINITIONS
; -----------
; Function parameters
(formal_parameters (identifier) @local.definition)
(formal_parameters (rest_pattern (identifier) @local.definition))

; Destructuring in parameters
(formal_parameters
  (object_pattern (shorthand_property_identifier_pattern) @local.definition))
(formal_parameters
  (array_pattern (identifier) @local.definition))

; Variable declarations
(variable_declarator name: (identifier) @local.definition)

; Destructuring assignments
(object_pattern (shorthand_property_identifier_pattern) @local.definition)
(array_pattern (identifier) @local.definition)

; Function and class declarations
(function_declaration name: (identifier) @local.definition)
(class_declaration name: (identifier) @local.definition)

; Import specifiers
(import_specifier (identifier) @local.definition)
(namespace_import (identifier) @local.definition)

; Catch clause parameter
(catch_clause parameter: (identifier) @local.definition)

; REFERENCES
; ----------
(identifier) @local.reference

; Exclude property identifiers (obj.property - property is not a reference)
(member_expression property: (property_identifier)) @ignore
```

---

## 5. Mapping to Collider/SMC Goals

### What This Enables

| Capability | Current (without locals) | With locals.scm |
|------------|-------------------------|-----------------|
| **Orphan Detection** | Heuristic (name patterns) | Definitive (unreferenced definitions) |
| **Edge Resolution** | Ambiguous (same name = maybe same target) | Precise (scope-aware resolution) |
| **RPBL Purity (P)** | Inferred from I/O keywords | Computed from variable mutations |
| **Dead Code** | `in_degree=0` (buggy before fix) | `@local.definition` with no `@local.reference` |

### The Key Insight for Collider

```
CURRENT COLLIDER FLOW:
  Source → Tree-sitter → Particles → Edges (heuristic resolution)
                                          ↓
                              AMBIGUITY: foo() in file A
                              Could call foo in file A, B, or C

WITH SCOPE ANALYSIS:
  Source → Tree-sitter → Particles → Scope Graph → Edges (deterministic)
                                          ↓
                              CERTAIN: foo() in scope X
                              References foo defined in scope Y
```

---

## 6. Implementation Architecture for Collider

### Directory Structure
```
src/core/queries/
├── python/
│   ├── symbols.scm      # Extract particles (current inline queries)
│   ├── locals.scm       # Scope analysis (NEW)
│   └── calls.scm        # Edge extraction (current inline)
├── javascript/
│   ├── symbols.scm
│   ├── locals.scm       # Scope analysis (NEW)
│   └── calls.scm
└── go/
    ├── symbols.scm
    └── calls.scm
```

### QueryLoader API
```python
class QueryLoader:
    """Load and cache .scm query files"""

    def get_query(self, language: str, query_type: str) -> Query:
        """
        Get compiled query.

        Args:
            language: 'python', 'javascript', 'go', etc.
            query_type: 'symbols', 'locals', 'calls'

        Returns:
            Compiled tree-sitter Query object (cached)
        """
        cache_key = f"{language}:{query_type}"
        if cache_key not in self._cache:
            path = self._base / language / f"{query_type}.scm"
            scm = path.read_text()
            lang_obj = self._get_language(language)
            self._cache[cache_key] = lang_obj.query(scm)
        return self._cache[cache_key]
```

### ScopeAnalyzer API
```python
class ScopeAnalyzer:
    """Extract scope information using locals.scm"""

    def analyze(self, tree: Tree, source: bytes) -> ScopeGraph:
        """
        Build scope graph from parse tree.

        Returns:
            ScopeGraph with:
              - scopes: List[Scope] (nested structure)
              - definitions: Dict[str, Definition]
              - references: List[Reference]
              - pairs: List[(Reference, Definition)]
        """

    def resolve_reference(self, ref: Reference) -> Optional[Definition]:
        """Find definition that a reference points to"""

    def find_unreferenced(self) -> List[Definition]:
        """Find definitions with no references (dead code candidates)"""
```

---

## 7. Critical Python Gotcha: Class Scope

**PEP 227 Rule:** Class bodies do NOT create lexical scopes for methods.

```python
class MyClass:
    x = 10  # Class attribute

    def method(self):
        print(x)  # ERROR! x is NOT in lexical scope
        print(self.x)  # CORRECT - must use self
```

**For locals.scm:** Do NOT add `(class_definition) @local.scope` for Python. Only add scope for the method bodies inside.

---

## 8. Integration with Existing Collider Components

### tree_sitter_engine.py Changes

```python
# Current: Inline hardcoded queries
query_str = """(function_definition name: (identifier) @name) @def"""

# New: Load from .scm files
query = self.query_loader.get_query('python', 'symbols')
```

### edge_extractor.py Changes

```python
# Current: Heuristic target resolution
def _find_target_particle(self, name: str) -> Optional[str]:
    # Prefers same-file matches (heuristic)

# New: Scope-aware resolution
def _find_target_particle(self, ref: Reference, scope_graph: ScopeGraph) -> Optional[str]:
    definition = scope_graph.resolve_reference(ref)
    if definition:
        return definition.particle_id
```

### full_analysis.py Changes

```python
# New Stage 2.5: Scope Analysis
print("\n🔬 Stage 2.5: Scope Analysis...")
scope_graphs = {}
for file_path, particles in by_file.items():
    tree = parser.parse(source)
    scope_graphs[file_path] = scope_analyzer.analyze(tree, source)

# Use in Stage 5 (Edge Extraction)
for edge in extract_edges(particles, scope_graphs):
    ...
```

---

## 9. Testing Strategy

### Golden File Tests
```python
def test_python_scope_resolution():
    source = '''
def outer(x):
    def inner(y):
        return x + y  # x references outer's x
    return inner
'''
    scope_graph = analyze(source)

    # Find reference to 'x' in inner function
    x_ref = find_reference(scope_graph, name='x', line=4)
    x_def = scope_graph.resolve_reference(x_ref)

    assert x_def.line == 1  # x is defined in outer's parameters
    assert x_def.scope.name == 'outer'
```

### Regression Tests
```bash
# Save current output as golden
python cli.py full tests/fixtures/scope_test/ --output /tmp/golden

# After changes, compare
python cli.py full tests/fixtures/scope_test/ --output /tmp/new
diff /tmp/golden/output.json /tmp/new/output.json
```

---

## 10. Phase 2 Sprint Tasks

| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Create `src/core/queries/` directory structure | S |
| 2.2 | Implement QueryLoader class | M |
| 2.3 | Write `python/locals.scm` | M |
| 2.4 | Write `javascript/locals.scm` | M |
| 2.5 | Implement ScopeAnalyzer class | L |
| 2.6 | Integrate with edge_extractor.py | M |
| 2.7 | Add Stage 2.5 to full_analysis.py | S |
| 2.8 | Write tests and validate | M |

**Estimated total:** 2-3 sprints

---

## References

- [Tree-sitter Syntax Highlighting Docs](https://tree-sitter.github.io/tree-sitter/3-syntax-highlighting.html)
- [nvim-treesitter Refactor Plugin](https://github.com/nvim-treesitter/nvim-treesitter-refactor)
- [PEP 227 - Statically Nested Scopes](https://peps.python.org/pep-0227/)
- [tree-sitter-javascript locals.scm](https://github.com/tree-sitter/tree-sitter-javascript/blob/master/queries/locals.scm)

