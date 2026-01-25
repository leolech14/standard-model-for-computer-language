# Research: Python AST techniques for determining public vs private visibility of functions, classes, and module...

> **Date:** 2026-01-23 21:22:15
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:c24793068f289da8775c5b2683e07839723e5778e75e5ac5d791cdd6bbf3b18b`
> **Raw JSON:** `raw/20260123_212215_python_ast_techniques_for_determining_public_vs_pr.json`

---

## Query

Python AST techniques for determining public vs private visibility of functions, classes, and modules. Looking for: 1) Conventions (_underscore, __dunder, __all__), 2) How to detect exported symbols from __all__, 3) How tools like pdoc, sphinx-autodoc, or interrogate determine what's 'public', 4) Tree-sitter approaches for multi-language visibility detection. Include code examples.

---

## Response

# Python AST Techniques for Determining Public vs Private Visibility of Functions, Classes, and Modules

Public application programming interfaces and private implementation details represent fundamental concepts in software architecture, and Python provides multiple mechanisms for distinguishing between them through conventions, metadata attributes, and syntactic analysis. This comprehensive report explores the techniques for determining public versus private visibility in Python codebases, examining naming conventions, the `__all__` attribute, Abstract Syntax Tree analysis, tool-based approaches, and cross-language parsing strategies with Tree-Sitter. By understanding these visibility detection methods, developers can create more sophisticated code analysis tools, documentation generators, and static analyzers that respect Python's explicit-is-better-than-implicit philosophy while maintaining accuracy across diverse codebases and programming paradigms.

## Understanding Python Visibility Conventions

Python does not enforce strict privacy through language-level access control mechanisms like those found in Java or C++[1]. Instead, Python relies on well-established naming conventions that communicate developer intent to other programmers and tools[1]. These conventions serve as a social contract within the Python community, indicating whether a particular element should be considered part of the public API or reserved for internal use[6]. Understanding these conventions forms the foundation for programmatic visibility detection, as they determine how modules, classes, functions, and variables are categorized by analysis tools.

The most fundamental visibility convention in Python is the **underscore prefix**, which signals non-public scope to developers and tools[1][5][6]. When a name starts with a single leading underscore, it is considered protected or non-public, indicating that the name should not be accessed outside the class or module in which it is defined, except by subclasses[1][3]. This convention does not prevent access through direct attribute manipulation, but it communicates clear intent to library consumers that modifying or using such elements may break their code when the library is updated[5]. In practice, for library authors, this means they can modify or remove any object prefixed with a single underscore without worrying about compatibility concerns, while for library users, attempting to use anything starting with an underscore carries the risk of encountering breaking changes at any time[5].

The **double underscore prefix** invokes a different mechanism called **name mangling**, which provides a degree of pseudo-privacy through automatic name transformation by the Python interpreter[1][3]. When an attribute or method name begins with double underscores (but does not end with double underscores), Python internally renames it to `_ClassName__attributename`[3][51]. This transformation occurs at the bytecode compilation stage and is meant primarily to prevent accidental name conflicts in inheritance hierarchies rather than to enforce true privacy[3][51]. For example, if a parent class defines `__private` and a child class also defines `__private`, name mangling ensures they become `_Parent__private` and `_Child__private` respectively, preventing the child's attribute from accidentally shadowing the parent's[51]. While name mangling makes attributes less accessible from outside the class, it remains a convention-based protection mechanism rather than enforcement-based, as the mangled name can still be accessed if one knows the class name[3].

Module-level dunder names (names with double leading and trailing underscores) such as `__all__`, `__author__`, and `__version__` occupy a special place in Python's visibility system[46]. These names are used for module metadata and special configuration, with `__all__` being the most significant for visibility determination[46]. According to PEP 8, module-level dunder names should be placed after the module docstring but before any import statements[46], establishing a consistent location where visibility declarations appear in source files.

Beyond simple prefixing, Python's name resolution and scoping rules create natural visibility boundaries. Names that are imported from other modules are not considered public parts of the current module's API, even if they lack underscore prefixes[2]. This distinction is crucial because a module importing something as `from other_module import something` creates a reference to that object, but the object itself was defined elsewhere[2]. Documentation generation tools and visibility analyzers must account for this distinction when determining what constitutes a module's actual public API versus what happens to be accessible within it[2].

## The __all__ Attribute: Explicit Public API Declaration

The `__all__` attribute represents Python's primary mechanism for explicitly declaring the public interface of a module or package[2][27]. By defining `__all__` as a list of strings, module authors establish a precise, machine-readable declaration of which names should be considered part of the module's public API[2][27]. This attribute serves multiple critical functions: it controls what gets imported during wildcard imports (`from module import *`), it provides a human-readable list of public objects without examining the entire codebase, it informs static analysis tools about the public API including re-exports of imported objects, and it can influence tab completion and directory listing behavior in interactive environments[2][5].

When `__all__` is defined in a module, the names listed in it are considered public regardless of naming conventions, while names not in the list are considered non-public even if they lack underscore prefixes[2][27]. This creates a powerful override mechanism for cases where module authors want to export something that might otherwise be considered private by convention, or conversely, to hide something that might otherwise appear public[27]. For instance, a module might import a utility function from another package and include it in `__all__` to intentionally re-export it as part of its public API[2][27].

Consider a practical example where a module defines multiple functions but only exports specific ones through `__all__`:

```python
# math_operations.py

def add(a, b):
    """Public: Add two numbers."""
    return a + b

def _internal_helper(x):
    """Private helper function."""
    return x * 2

def subtract(a, b):
    """Public: Subtract two numbers."""
    return a - b

__all__ = ["add", "subtract"]
```

In this example, even though `_internal_helper` lacks underscore prefixes within the list, a wildcard import (`from math_operations import *`) will only bring in `add` and `subtract`[27]. Conversely, if a module imported a function that lacked a leading underscore but the author did not intend it as part of the public API, they could exclude it from `__all__`[2].

When `__all__` is not defined, Python follows the convention that all names without leading underscores, excluding imported names, are considered public[2][10]. This default behavior means that `__all__` is optional but becomes increasingly important as modules grow in complexity and as the distinction between implementation details and public interface becomes more critical[43]. Some documentation generation tools and static analyzers treat the absence of `__all__` in significant modules as a code quality issue, recommending that module authors explicitly declare their public API[43].

For packages containing multiple submodules, `__all__` can be used in the package's `__init__.py` file to control what is exposed at the package level, allowing authors to hide internal module structure from users[5][43]. This practice enables sophisticated API design where multiple internal modules collaborate to provide a cohesive public interface through a single entry point[5].

## Abstract Syntax Tree Analysis for Visibility Detection

The Python `ast` module provides the foundational tools for programmatic analysis of Python source code's structure, including visibility information[15][28][44]. An Abstract Syntax Tree is a tree representation of the syntactic structure of source code, where each node represents a construct in the language (such as a function definition, class, assignment, or name reference)[15][25]. By parsing Python source code into an AST, developers can examine and analyze code properties without executing it, making AST analysis ideal for static visibility detection[15][25].

The basic approach to AST-based visibility analysis begins with parsing source code into a tree structure using `ast.parse()`[15][28][44]. This function takes a string of Python source code and returns an `ast.Module` object representing the entire module, which contains a `body` attribute that is a list of all top-level statements and definitions[15]. From this module node, analysis proceeds by traversing the tree and identifying nodes representing functions, classes, and other definitions that might be public or private[25].

Consider a foundational example demonstrating AST parsing and examination:

```python
import ast

def analyze_module_visibility(source_code):
    """Parse source code and identify public/private definitions."""
    tree = ast.parse(source_code)
    
    # Check if __all__ is explicitly defined
    all_defined = None
    public_via_all = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Check for __all__ assignment
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        all_defined = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                all_defined.append(elt.value)
                        public_via_all = set(all_defined)
    
    # Identify all top-level definitions
    definitions = {
        'functions': [],
        'classes': [],
        'variables': []
    }
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            name = node.name
            is_public = determine_visibility(name, public_via_all, all_defined)
            definitions['functions'].append({
                'name': name,
                'public': is_public,
                'lineno': node.lineno
            })
        elif isinstance(node, ast.ClassDef):
            name = node.name
            is_public = determine_visibility(name, public_via_all, all_defined)
            definitions['classes'].append({
                'name': name,
                'public': is_public,
                'lineno': node.lineno,
                'methods': extract_class_methods(node, public_via_all, all_defined)
            })
    
    return definitions, all_defined

def determine_visibility(name, public_via_all, all_defined):
    """Determine if a name should be considered public."""
    # If __all__ is explicitly defined, only names in it are public
    if all_defined is not None:
        return name in public_via_all
    
    # Otherwise, follow naming convention (no leading underscore means public)
    return not name.startswith('_')

def extract_class_methods(class_node, public_via_all, all_defined):
    """Extract methods from a class definition."""
    methods = []
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef):
            name = node.name
            # Class members follow different rules than module-level
            # Names starting with _ are considered private by convention
            is_public = not name.startswith('_')
            methods.append({
                'name': name,
                'public': is_public,
                'is_dunder': name.startswith('__') and name.endswith('__')
            })
    return methods
```

This example demonstrates how AST analysis can identify definitions and assess their visibility status. The approach parses source code into an AST, searches for `__all__` definitions to determine if the module explicitly declares its public API, and then examines each function and class definition to classify them as public or private based on naming conventions and explicit declarations[25].

The `ast.NodeVisitor` class provides a more structured approach to tree traversal by implementing the visitor pattern[15][25]. Rather than manually iterating through all nodes, developers can subclass `NodeVisitor` and implement methods named `visit_<NodeType>` that get called automatically when those specific node types are encountered during traversal[15][25][37]. This approach is particularly useful for more complex analysis tasks:

```python
import ast

class VisibilityAnalyzer(ast.NodeVisitor):
    """Visitor that analyzes and collects visibility information."""
    
    def __init__(self):
        self.public_names = set()
        self.all_defined = False
        self.module_docstring = None
        self.functions = []
        self.classes = []
        self.current_class = None
    
    def visit_Module(self, node):
        """Visit the module node."""
        # Extract module docstring
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            self.module_docstring = node.body[0].value.value
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """Check for __all__ definition."""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                self.all_defined = True
                if isinstance(node.value, ast.List):
                    for elt in node.value.elts:
                        if isinstance(elt, ast.Constant):
                            self.public_names.add(elt.value)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        visibility = self._determine_visibility(node.name)
        
        func_info = {
            'name': node.name,
            'lineno': node.lineno,
            'public': visibility == 'public',
            'visibility': visibility,
            'docstring': ast.get_docstring(node),
            'parent_class': self.current_class
        }
        self.functions.append(func_info)
        
        # Don't traverse nested functions
        if self.current_class is None:
            self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        visibility = self._determine_visibility(node.name)
        
        class_info = {
            'name': node.name,
            'lineno': node.lineno,
            'public': visibility == 'public',
            'visibility': visibility,
            'docstring': ast.get_docstring(node),
            'methods': []
        }
        
        # Visit class methods
        old_class = self.current_class
        self.current_class = node.name
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_visibility = self._determine_visibility(item.name)
                class_info['methods'].append({
                    'name': item.name,
                    'visibility': method_visibility,
                    'public': method_visibility == 'public'
                })
        
        self.current_class = old_class
        self.classes.append(class_info)
    
    def _determine_visibility(self, name):
        """Determine visibility based on naming convention."""
        if name.startswith('__') and name.endswith('__'):
            return 'dunder'
        elif name.startswith('__'):
            return 'private'
        elif name.startswith('_'):
            return 'protected'
        elif self.all_defined and name not in self.public_names:
            return 'private'
        else:
            return 'public'
```

This visitor-based approach automatically handles tree traversal, making it easier to implement complex analysis logic. The visitor pattern also integrates well with `ast.generic_visit()`, which can be called to continue traversing child nodes when custom logic needs to be inserted at specific points[15][25].

Name mangling detection requires special attention in AST analysis. When a name begins with double underscores within a class definition, the analyzer must recognize that Python will mangle the name internally[3][51]. This mangling means that accessing `obj.__private_attribute` will fail with an `AttributeError`, but accessing `obj._ClassName__private_attribute` will succeed[3][51]. Advanced visibility analyzers that aim to provide accurate introspection information should account for this transformation:

```python
import ast

def detect_name_mangling(class_node):
    """Identify attributes that will be subject to name mangling."""
    mangled_attributes = []
    
    for node in ast.walk(class_node):
        if isinstance(node, ast.Attribute):
            # Check if this is a self.__ reference
            if (isinstance(node.value, ast.Name) and 
                node.value.id == 'self' and
                node.attr.startswith('__') and
                not node.attr.endswith('__')):
                mangled_attributes.append({
                    'name': node.attr,
                    'mangled_name': f'_{class_node.name}{node.attr}',
                    'lineno': node.lineno
                })
    
    return mangled_attributes
```

## Tool-Based Visibility Detection Approaches

Professional documentation and analysis tools have developed sophisticated methods for determining visibility that go beyond simple naming convention analysis. These tools often combine multiple signals including naming conventions, `__all__` declarations, explicit metadata annotations, docstring analysis, and configuration settings. Understanding how established tools implement visibility detection provides insights into best practices and handles edge cases that simple approaches might miss.

The **pdoc** documentation generator determines visibility through a multi-layered approach[7][10]. When analyzing a module, pdoc first checks if `__all__` is defined; if it is, then only identifiers contained in that list are considered public, regardless of naming conventions[7][10]. If `__all__` is not defined, pdoc considers all items public that do not start with an underscore and that are defined in the current module (not imported from elsewhere)[7][10]. This distinction between defined and imported objects is crucial, as it prevents accidentally exposing third-party dependencies as part of a module's public API[10].

Beyond this basic logic, pdoc provides mechanisms for fine-grained control over visibility through special docstring annotations. Objects can be marked as private using the `@private` docstring annotation, or conversely, objects starting with underscores can be marked as public using the `@public` annotation[7]. This flexibility allows library authors to override the default visibility determination when special cases arise.

For improved integration with interactive environments, pdoc can be configured with a custom `__dir__()` function that returns only the public API, causing tab completion to show exclusively public names[5]. This technique demonstrates how visibility information can be operationalized to improve the developer experience:

```python
__all__ = ["public_function", "PublicClass"]

def public_function():
    """This is part of the public API."""
    pass

def _private_function():
    """This is private."""
    pass

def __dir__():
    """Control what appears in dir() and tab completion."""
    return __all__
```

**Sphinx's autodoc extension** approaches visibility determination through a combination of naming conventions and explicit metadata in docstrings[8]. By default, autodoc only includes public members with a docstring or inline documentation comments (`#:`)[8]. If `__all__` exists, it will be used to define which members are public, unless the `:members:` option is explicitly set[8]. Autodoc also supports the `:meta private:` and `:meta public:` docstring directives to explicitly mark members' visibility status, allowing authors to override default behavior for specific cases[8].

The presence of `__all__` in a module significantly changes autodoc's behavior. When `__all__` is defined, autodoc restricts automatic documentation generation to only the members listed in it[8]. This design choice respects the module author's explicit visibility declaration and prevents accidentally documenting implementation details.

**interrogate** focuses on docstring coverage rather than direct visibility analysis, but it intersects with visibility concerns by checking whether documented functions and methods are considered public or private[9]. The tool can be configured to ignore specific categories of objects through command-line options and configuration files[9]. For instance, the `:ignore-private:` option tells interrogate to exclude private methods from coverage calculations, recognizing that private implementation details may not require documentation to the same degree as public APIs[9].

These tool-based approaches demonstrate that visibility determination in practice involves:

First, checking explicit declarations like `__all__`[2][7][8]

Second, applying naming convention analysis (underscores)[1][3]

Third, distinguishing between locally-defined and imported objects[2][10]

Fourth, allowing explicit override through docstring annotations[7][8]

Fifth, considering tool-specific configuration and policies[9]

This layered approach accommodates both explicit and implicit visibility information while allowing flexibility for edge cases and special scenarios.

## Tree-Sitter Approaches for Multi-Language Visibility Detection

While Python-specific AST analysis with the `ast` module works well for Python code, analyzing codebases that span multiple languages requires a more language-agnostic approach. **Tree-Sitter** is a parser generator and incremental parsing library that builds concrete syntax trees for source code and efficiently updates them as files change[16]. Tree-Sitter's key advantage is its support for numerous programming languages through a unified interface, making it valuable for tools that need to analyze visibility across heterogeneous codebases[16][29][50].

Tree-Sitter's query system provides a mechanism for searching and matching patterns in syntax trees using a Lisp-like query language[26][50]. Unlike regex-based approaches that operate on strings, Tree-Sitter queries understand code structure and can precisely target syntactic elements[26]. This capability extends visibility analysis to become language-agnostic, allowing the same conceptual analysis to be applied to Python, JavaScript, TypeScript, Go, and many other languages[26][29][50].

The fundamental Tree-Sitter workflow for visibility analysis involves three steps: first, parsing code into a syntax tree using a language-specific grammar; second, writing queries that match public or private patterns in that language; and third, executing queries against the tree to extract visibility information[50]. Consider how visibility analysis might be implemented using Tree-Sitter for multiple languages:

For **Python**, a Tree-Sitter query might identify public function definitions:

```
(module
  (function_definition
    name: (identifier) @function.name
    (#not-match? @function.name "^_")))
```

This query matches function definitions at the module level where the function name does not start with an underscore[26][50].

For **JavaScript**, an analogous query would target exported functions:

```
(export_statement
  (function_declaration
    name: (identifier) @function.name))
```

For **Go**, where visibility is determined by capitalization rather than underscores, the query would look for capitalized function declarations:

```
(function_declaration
  name: (identifier) @function.name
  (#match? @function.name "^[A-Z]"))
```

These examples demonstrate how Tree-Sitter enables visibility analysis by allowing language-specific query patterns to be written and applied to language-specific syntax trees[26][50].

Tree-Sitter's query predicates add powerful filtering capabilities to visibility detection[26]. Predicates like `#eq?`, `#match?`, `#not-match?`, and others enable precise matching of patterns[26]. For instance, to find all functions that are explicitly exported in Python (by appearing in `__all__`), a more complex query pattern could be constructed:

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query

# Setup parser
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

# Parse source code
source_code = b"""
__all__ = ["public_func", "PublicClass"]

def public_func():
    pass

def _private_func():
    pass

class PublicClass:
    pass

class _PrivateClass:
    pass
"""

tree = parser.parse(source_code)

# Query for module-level assignments to __all__
all_query = """
(assignment
  left: (identifier) @var_name
  (#eq? @var_name "__all__")
  right: (list
    (string (string_content) @export)))
"""

query = Query(PY_LANGUAGE, all_query)
matches = query.matches(tree.root_node)

exported_names = set()
for match in matches:
    for capture in match.captures:
        if capture.name == "export":
            # Extract string content, removing quotes
            exported_names.add(capture.node.text.decode('utf-8').strip('"\''))

print(f"Explicitly exported names: {exported_names}")
```

This Tree-Sitter-based approach can accurately extract what a module explicitly declares as public, similar to the AST-based approach but with the benefit of working across multiple languages[26][50].

Tree-Sitter's incremental parsing capability is particularly valuable for real-time analysis tools like integrated development environments and continuous analysis systems[50]. When source code changes, Tree-Sitter can update only the affected parts of the syntax tree rather than reparsing the entire file, making it efficient for tools that monitor code changes and provide immediate feedback[50]. This capability is less relevant for batch analysis but becomes essential for interactive tools that need to maintain current visibility information as developers type[50].

The trade-off with Tree-Sitter is that while it provides language-agnostic parsing and querying, each language's visibility rules are fundamentally different. Python uses underscore prefixes and `__all__` declarations; JavaScript uses explicit `export` keywords; Go uses capitalization; Rust uses explicit `pub` keywords; and so forth[26]. A comprehensive cross-language visibility system must implement language-specific logic for interpreting these different mechanisms, even if the parsing and query infrastructure is shared[29].

## Practical Implementation: Building a Unified Visibility Analyzer

Combining the various techniques discussed above, a practical visibility analyzer can be constructed that leverages AST analysis for Python and provides extensibility for other concerns. This implementation demonstrates how to integrate naming convention analysis, `__all__` detection, and visitor-based traversal into a cohesive tool:

```python
import ast
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field

@dataclass
class SymbolInfo:
    """Information about a module symbol (function, class, variable)."""
    name: str
    kind: str  # 'function', 'class', 'variable', 'method'
    lineno: int
    visibility: str  # 'public', 'protected', 'private', 'dunder'
    docstring: str = None
    parent: str = None  # For methods, the containing class
    members: List['SymbolInfo'] = field(default_factory=list)  # For classes
    is_imported: bool = False
    mangled_name: str = None  # For double-underscore attributes

class ModuleVisibilityAnalyzer(ast.NodeVisitor):
    """Comprehensive analyzer for Python module visibility."""
    
    def __init__(self, source_code: str, module_path: str = None):
        self.source_code = source_code
        self.module_path = module_path
        self.tree = ast.parse(source_code)
        self.symbols: List[SymbolInfo] = []
        self.all_exports: Set[str] = None
        self.has_all_declaration = False
        self.imported_names: Set[str] = set()
        self.current_class: str = None
    
    def analyze(self) -> Dict:
        """Perform complete visibility analysis."""
        # First pass: collect __all__ and imports
        self._collect_metadata()
        
        # Second pass: visit all definitions
        self.visit(self.tree)
        
        return {
            'symbols': self.symbols,
            'all_exports': self.all_exports,
            'has_all_declaration': self.has_all_declaration,
            'public_api': self._get_public_api(),
            'private_api': self._get_private_api(),
            'protected_api': self._get_protected_api()
        }
    
    def _collect_metadata(self):
        """Collect __all__ exports and import information."""
        for node in ast.walk(self.tree):
            # Collect __all__
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        self.has_all_declaration = True
                        if isinstance(node.value, ast.List):
                            self.all_exports = set()
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    self.all_exports.add(elt.value)
            
            # Collect imported names
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    self.imported_names.add(name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    self.imported_names.add(name)
    
    def _determine_visibility(self, name: str, is_imported: bool = False) -> str:
        """Determine visibility classification for a name."""
        # Dunder (magic) methods
        if name.startswith('__') and name.endswith('__'):
            return 'dunder'
        
        # Double-underscore private (subject to name mangling)
        if name.startswith('__'):
            return 'private'
        
        # Single-underscore protected
        if name.startswith('_'):
            return 'protected'
        
        # If __all__ is defined, check if explicitly exported
        if self.has_all_declaration and self.all_exports is not None:
            return 'public' if name in self.all_exports else 'private'
        
        # If imported, not part of this module's public API
        if is_imported:
            return 'private'
        
        # Default: public
        return 'public'
    
    def visit_Module(self, node: ast.Module):
        """Visit module and extract module-level items."""
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions."""
        is_imported = node.name in self.imported_names
        visibility = self._determine_visibility(node.name, is_imported)
        
        symbol = SymbolInfo(
            name=node.name,
            kind='function' if self.current_class is None else 'method',
            lineno=node.lineno,
            visibility=visibility,
            docstring=ast.get_docstring(node),
            parent=self.current_class,
            is_imported=is_imported
        )
        
        # Handle name mangling for double-underscore names
        if node.name.startswith('__') and not node.name.endswith('__'):
            if self.current_class:
                symbol.mangled_name = f'_{self.current_class}{node.name}'
        
        self.symbols.append(symbol)
        
        # Don't visit nested functions for now
        if self.current_class is None:
            return
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions."""
        is_imported = node.name in self.imported_names
        visibility = self._determine_visibility(node.name, is_imported)
        
        class_symbol = SymbolInfo(
            name=node.name,
            kind='class',
            lineno=node.lineno,
            visibility=visibility,
            docstring=ast.get_docstring(node),
            is_imported=is_imported
        )
        
        # Visit methods
        old_class = self.current_class
        self.current_class = node.name
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_visibility = self._determine_visibility(item.name, False)
                method_symbol = SymbolInfo(
                    name=item.name,
                    kind='method',
                    lineno=item.lineno,
                    visibility=method_visibility,
                    docstring=ast.get_docstring(item),
                    parent=node.name
                )
                
                # Handle name mangling
                if item.name.startswith('__') and not item.name.endswith('__'):
                    method_symbol.mangled_name = f'_{node.name}{item.name}'
                
                class_symbol.members.append(method_symbol)
        
        self.current_class = old_class
        self.symbols.append(class_symbol)
    
    def visit_Assign(self, node: ast.Assign):
        """Visit assignments to track variables."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                # Skip __all__ assignment (already processed)
                if name == '__all__':
                    continue
                
                is_imported = name in self.imported_names
                visibility = self._determine_visibility(name, is_imported)
                
                if self.current_class is None:
                    # Module-level variable
                    symbol = SymbolInfo(
                        name=name,
                        kind='variable',
                        lineno=node.lineno,
                        visibility=visibility,
                        is_imported=is_imported
                    )
                    self.symbols.append(symbol)
    
    def _get_public_api(self) -> List[str]:
        """Get list of public symbols."""
        return [s.name for s in self.symbols 
                if s.visibility == 'public' and s.parent is None]
    
    def _get_private_api(self) -> List[str]:
        """Get list of private symbols."""
        return [s.name for s in self.symbols 
                if s.visibility in ('private', 'dunder') and s.parent is None]
    
    def _get_protected_api(self) -> List[str]:
        """Get list of protected symbols."""
        return [s.name for s in self.symbols 
                if s.visibility == 'protected' and s.parent is None]

# Example usage
if __name__ == "__main__":
    sample_code = '''
"""Module demonstrating visibility analysis."""

__all__ = ["PublicClass", "public_function"]

import json
from typing import Optional

def public_function(x: int) -> int:
    """A public function."""
    return _private_helper(x)

def _private_helper(x: int) -> int:
    """Private helper function."""
    return x * 2

class PublicClass:
    """A public class."""
    
    def public_method(self):
        """Public method."""
        self.__private_method()
    
    def __private_method(self):
        """Private method using name mangling."""
        pass

class _PrivateClass:
    """A private class."""
    pass

CONSTANT = 42
_PRIVATE_CONSTANT = 100
'''
    
    analyzer = ModuleVisibilityAnalyzer(sample_code)
    results = analyzer.analyze()
    
    print("=== Visibility Analysis Results ===")
    print(f"Has __all__ declaration: {results['has_all_declaration']}")
    print(f"Exported via __all__: {results['all_exports']}")
    print(f"\nPublic API: {results['public_api']}")
    print(f"Protected API: {results['protected_api']}")
    print(f"Private API: {results['private_api']}")
    
    print("\n=== All Symbols ===")
    for symbol in results['symbols']:
        parent_info = f" (in {symbol.parent})" if symbol.parent else ""
        print(f"  {symbol.name}{parent_info}: {symbol.visibility}")
        if symbol.mangled_name:
            print(f"    Mangled as: {symbol.mangled_name}")
```

This implementation demonstrates how to combine multiple visibility detection techniques into a practical tool. It properly handles `__all__` declarations, naming conventions, imported objects, name mangling, and distinguishes between module-level and class-level definitions. The tool can be extended to generate documentation, perform linting checks, or feed visibility information to other analysis tools.

## Conclusion

Determining public versus private visibility in Python represents a multifaceted challenge that combines language conventions, explicit metadata, syntactic analysis, and tool-specific policies. Python's philosophy of explicit-is-better-than-implicit manifests in multiple mechanisms for declaring and detecting visibility: the underscore prefix conventions provide lightweight signaling of intent, the `__all__` attribute enables explicit public API declaration, Abstract Syntax Trees enable programmatic analysis of source structure, and specialized tools like pdoc and Sphinx implement sophisticated visibility detection algorithms[2][7][8]. For multi-language codebases, Tree-Sitter provides a language-agnostic foundation for parsing and querying syntax across numerous programming languages, though language-specific visibility rules must still be implemented separately[26][50].

A comprehensive understanding of these visibility detection techniques enables developers to build more sophisticated code analysis tools, documentation generators, and static analyzers that respect Python's design philosophy while maintaining accuracy and flexibility[1][15][25]. By combining AST-based analysis with knowledge of Python conventions and explicit metadata, tools can effectively determine what constitutes an API's public surface and what remains implementation detail, ultimately improving code organization, documentation quality, and maintainability across Python projects.[27][43][46]

---

## Citations

1. https://www.geeksforgeeks.org/python/access-modifiers-in-python-public-private-and-protected/
2. https://realpython.com/python-all-attribute/
3. https://www.datacamp.com/tutorial/python-private-methods-explained
4. https://docs.python.org/3.5/library/ast.html
5. https://learn.scientific-python.org/development/patterns/exports/
6. https://docs.python.org/3/tutorial/classes.html
7. https://pdoc.dev/docs/pdoc.html
8. https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
9. https://interrogate.readthedocs.io
10. https://pdoc3.github.io/pdoc/doc/pdoc/
11. https://github.com/readthedocs/sphinx_rtd_theme/issues/842
12. https://coverage.readthedocs.io
13. https://ast-grep.github.io/advanced/custom-language.html
14. https://blog.pulsar-edit.dev/posts/20230927-savetheclocktower-modern-tree-sitter-part-2/
15. https://docs.python.org/3/library/ast.html
16. https://tree-sitter.github.io
17. https://github.com/neovim/neovim/issues/33346
18. https://discuss.python.org/t/log-importer-modules-from-within-the-module-that-is-being-imported/20855
19. https://docs.python.org/3/library/ast.html
20. https://discuss.python.org/t/inspect-getmembers-seems-to-show-extra-members-on-python-3-7/7035
21. https://www.pythonmorsels.com/inspecting-python-objects/
22. https://github.com/xbeat/Machine-Learning/blob/main/Exploring%20Python's%20Abstract%20Syntax%20Tree%20Manipulation.md
23. https://docs.python.org/3/library/inspect.html
24. https://betterprogramming.pub/how-to-use-underscore-properly-in-python-37df5e05ba4c
25. https://www.mattlayman.com/blog/2018/decipher-python-ast/
26. https://dev.to/shrsv/unraveling-tree-sitter-queries-your-guide-to-code-analysis-magic-41il
27. https://realpython.com/python-all-attribute/
28. https://docs.python.org/3/library/ast.html
29. https://www.dropstone.io/blog/ast-parsing-tree-sitter-40-languages
30. https://docs.python.org/3/library/ast.html
31. https://metallapan.se/post/using-the-ast-to-hack-constants-into-python/
32. https://www.digitalocean.com/community/tutorials/python-static-method
33. https://gabrielelanaro.github.io/blog/2014/12/12/extract-docstrings.html
34. https://www.youtube.com/watch?v=l67JN5mQnKI
35. https://machinelearningplus.com/python/python-method-decorators-classmethod-vs-staticmethod-vs-property/
36. https://deepsource.com/blog/python-asts-by-building-your-own-linter
37. https://arumoy.me/blogs/python-ast-extract-module-method-names/
38. https://docs.python.org/3/library/importlib.metadata.html
39. https://libcst.readthedocs.io/en/latest/tutorial.html
40. https://discuss.python.org/t/controlled-walking-of-nested-ast-nodes/3513
41. https://docs.python.org/3.10/library/importlib.metadata.html
42. https://docs.python.org/3/library/pydoc.html
43. https://mkdocstrings.github.io/griffe/guide/users/recommendations/public-apis/
44. https://docs.python.org/3/library/ast.html
45. https://docs.readthedocs.com/platform/latest/tutorial/index.html
46. https://peps.python.org/pep-0008/
47. https://blog.yonatan.dev/ast-scout-code-structure-visualization-tool/
48. https://discuss.python.org/t/how-name-resolution-works-in-python/26452
49. https://www.digitalocean.com/community/tutorials/python-static-method
50. https://dev.to/shrsv/diving-into-tree-sitter-parsing-code-with-python-like-a-pro-17h8
51. https://www.geeksforgeeks.org/python/name-mangling-in-python/
52. https://docs.python.org/3/whatsnew/3.8.html
53. https://www.youtube.com/watch?v=bP0zl4K_LY8
54. https://discuss.python.org/t/implement-inspect-getmembers-static/2550
55. https://devmethodologies.blogspot.com/2013/07/best-practice-in-c-for-modules.html
56. https://github.com/python/typeshed
57. https://docs.python.org/3/library/inspect.html
58. https://dev.to/koffeinfrei/private-methods-are-a-code-smell-5d14
59. https://peps.python.org/pep-0800/

---

## Usage Stats

- Prompt tokens: 90
- Completion tokens: 7450
- Total tokens: 7540
