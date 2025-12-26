#!/usr/bin/env python3
"""
Atom Registry — Canonical list of all known atoms in the taxonomy.

This is the SINGLE SOURCE OF TRUTH for:
- All known atoms (currently categorized)
- Their classification (continent, fundamental, level)
- Discovery history (when added, from which repo)

The registry grows as we discover new patterns!
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class AtomDefinition:
    """A canonical atom in the taxonomy."""
    id: int                          # Unique ID (1-96 from original, 97+ are discoveries)
    name: str                        # PascalCase name (e.g., "PureFunction")
    ast_types: List[str]             # Tree-sitter node types that map to this
    continent: str                   # Data Foundations, Logic & Flow, Organization, Execution
    fundamental: str                 # Bits, Variables, Functions, etc.
    level: str                       # atom, molecule, organelle
    description: str                 # What this atom represents
    detection_rule: str              # How to detect it
    
    # Discovery metadata
    source: str = "original"         # "original" or repo name where discovered
    discovered_at: str = ""          # ISO timestamp
    occurrence_count: int = 0        # Total times seen across all repos


class AtomRegistry:
    """
    The canonical registry of all known atoms.
    
    This grows over time as we discover new patterns.
    """
    
    def __init__(self):
        self.atoms: Dict[int, AtomDefinition] = {}
        self.ast_type_map: Dict[str, int] = {}  # node_type -> atom_id
        self.next_id: int = 97  # Original 96 + new discoveries
        self._init_canonical_atoms()
    
    def _init_canonical_atoms(self):
        """Initialize with the original 96 + refined atoms."""
        
        # ═══════════════════════════════════════════════════════════════════
        # DATA FOUNDATIONS (Cyan) — IDs 1-20
        # ═══════════════════════════════════════════════════════════════════
        
        # Bits (1-4)
        self._add(1, "BitFlag", ["binary_expression"], "Data Foundations", "Bits", "atom",
                  "Bit operation with mask", "bit operation + constant mask")
        self._add(2, "BitMask", ["binary_literal"], "Data Foundations", "Bits", "atom",
                  "Binary literal value", "binary literal 0b...")
        
        # Primitives (5-12)
        self._add(5, "Boolean", ["true", "false"], "Data Foundations", "Primitives", "atom",
                  "Boolean true/false value", "type bool")
        self._add(6, "Integer", ["integer"], "Data Foundations", "Primitives", "atom",
                  "Integer numeric value", "integer type")
        self._add(7, "Float", ["float"], "Data Foundations", "Primitives", "atom",
                  "Floating point value", "float type")
        self._add(8, "StringLiteral", ["string", "concatenated_string"], "Data Foundations", "Primitives", "atom",
                  "String literal value", "string literal")
        self._add(9, "NoneLiteral", ["none"], "Data Foundations", "Primitives", "atom",
                  "None/null value", "None/null literal")
        self._add(10, "ListLiteral", ["list"], "Data Foundations", "Primitives", "atom",
                   "List literal []", "list brackets")
        self._add(11, "DictLiteral", ["dictionary"], "Data Foundations", "Primitives", "atom",
                   "Dictionary literal {}", "dict braces")
        self._add(12, "TupleLiteral", ["tuple"], "Data Foundations", "Primitives", "atom",
                   "Tuple literal ()", "tuple parens")
        
        # Variables (13-17)
        self._add(13, "LocalVar", ["identifier"], "Data Foundations", "Variables", "atom",
                  "Local variable reference", "local declaration")
        self._add(14, "Parameter", ["typed_parameter", "default_parameter"], "Data Foundations", "Variables", "atom",
                  "Function parameter", "function parameter")
        self._add(15, "InstanceField", ["attribute"], "Data Foundations", "Variables", "atom",
                  "Instance field access", "this/self field access")
        self._add(16, "IndexAccess", ["subscript"], "Data Foundations", "Variables", "atom",
                  "Array/dict index access", "bracket access")
        self._add(17, "SliceAccess", ["slice"], "Data Foundations", "Variables", "atom",
                  "Slice access [a:b]", "slice notation")
        
        # ═══════════════════════════════════════════════════════════════════
        # LOGIC & FLOW (Magenta) — IDs 18-50
        # ═══════════════════════════════════════════════════════════════════
        
        # Expressions (18-25)
        self._add(18, "BinaryExpr", ["binary_operator"], "Logic & Flow", "Expressions", "atom",
                  "Binary operation a + b", "arithmetic/bitwise ops")
        self._add(19, "UnaryExpr", ["unary_operator", "not_operator"], "Logic & Flow", "Expressions", "atom",
                  "Unary operation -x, !x", "unary prefix")
        self._add(20, "ComparisonExpr", ["comparison_operator"], "Logic & Flow", "Expressions", "atom",
                  "Comparison a == b", "comparison ops")
        self._add(21, "LogicalExpr", ["boolean_operator"], "Logic & Flow", "Expressions", "atom",
                  "Logical and/or", "boolean ops")
        self._add(22, "CallExpr", ["call"], "Logic & Flow", "Expressions", "atom",
                  "Function call f(x)", "function call")
        self._add(23, "TernaryExpr", ["conditional_expression"], "Logic & Flow", "Expressions", "atom",
                  "Ternary a ? b : c", "conditional expression")
        self._add(24, "Closure", ["lambda"], "Logic & Flow", "Expressions", "atom",
                  "Lambda/closure", "lambda keyword")
        self._add(25, "AwaitExpr", ["await"], "Logic & Flow", "Expressions", "atom",
                  "Await expression", "await keyword")
        
        # Statements (26-35)
        self._add(26, "Assignment", ["assignment"], "Logic & Flow", "Statements", "atom",
                  "Variable assignment", "= operator")
        self._add(27, "AugmentedAssignment", ["augmented_assignment"], "Logic & Flow", "Statements", "atom",
                  "Augmented assignment +=", "+= operator")
        self._add(28, "ExpressionStmt", ["expression_statement"], "Logic & Flow", "Statements", "atom",
                  "Standalone expression", "expression as statement")
        self._add(29, "ReturnStmt", ["return_statement"], "Logic & Flow", "Statements", "atom",
                  "Return statement", "return keyword")
        self._add(30, "RaiseStmt", ["raise_statement"], "Logic & Flow", "Statements", "atom",
                  "Raise/throw exception", "raise keyword")
        self._add(31, "AssertStmt", ["assert_statement"], "Logic & Flow", "Statements", "atom",
                  "Assert statement", "assert keyword")
        self._add(32, "PassStmt", ["pass_statement"], "Logic & Flow", "Statements", "atom",
                  "Pass/no-op statement", "pass keyword")
        self._add(33, "BreakStmt", ["break_statement"], "Logic & Flow", "Statements", "atom",
                  "Break loop", "break keyword")
        self._add(34, "ContinueStmt", ["continue_statement"], "Logic & Flow", "Statements", "atom",
                  "Continue loop", "continue keyword")
        self._add(35, "DeleteStmt", ["delete_statement"], "Logic & Flow", "Statements", "atom",
                  "Delete statement", "del keyword")
        
        # Control Structures (36-45)
        self._add(36, "IfBranch", ["if_statement"], "Logic & Flow", "Control Structures", "atom",
                  "If conditional", "if/else")
        self._add(37, "ElifBranch", ["elif_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Elif branch", "elif keyword")
        self._add(38, "ElseBranch", ["else_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Else branch", "else keyword")
        self._add(39, "LoopFor", ["for_statement"], "Logic & Flow", "Control Structures", "atom",
                  "For loop", "for loop")
        self._add(40, "LoopWhile", ["while_statement"], "Logic & Flow", "Control Structures", "atom",
                  "While loop", "while loop")
        self._add(41, "TryCatch", ["try_statement"], "Logic & Flow", "Control Structures", "atom",
                  "Try/catch block", "try/except")
        self._add(42, "ExceptHandler", ["except_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Exception handler", "except clause")
        self._add(43, "FinallyBlock", ["finally_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Finally block", "finally clause")
        self._add(44, "ContextManager", ["with_statement"], "Logic & Flow", "Control Structures", "atom",
                  "With context manager", "with statement")
        self._add(45, "PatternMatch", ["match_statement", "case_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Pattern matching", "match/case")
        
        # Functions (46-55)
        self._add(46, "Function", ["function_definition"], "Logic & Flow", "Functions", "molecule",
                  "Function definition", "def keyword")
        self._add(47, "AsyncFunction", ["async_function_definition"], "Logic & Flow", "Functions", "molecule",
                  "Async function", "async def")
        self._add(48, "DecoratedFunction", ["decorated_definition"], "Logic & Flow", "Functions", "molecule",
                  "Decorated function", "@decorator")
        self._add(49, "Generator", ["generator_expression"], "Logic & Flow", "Functions", "molecule",
                  "Generator expression", "yield keyword")
        self._add(50, "ListComprehension", ["list_comprehension"], "Logic & Flow", "Functions", "atom",
                  "List comprehension", "[x for x in]")
        self._add(51, "DictComprehension", ["dictionary_comprehension"], "Logic & Flow", "Functions", "atom",
                  "Dict comprehension", "{k:v for}")
        self._add(52, "SetComprehension", ["set_comprehension"], "Logic & Flow", "Functions", "atom",
                  "Set comprehension", "{x for x}")
        self._add(53, "Decorator", ["decorator"], "Logic & Flow", "Functions", "atom",
                  "Decorator", "@symbol")
        self._add(54, "ParameterList", ["parameters"], "Logic & Flow", "Functions", "atom",
                  "Parameter list", "(params)")
        self._add(55, "ArgumentList", ["argument_list"], "Logic & Flow", "Functions", "atom",
                  "Argument list", "(args)")
        
        # ═══════════════════════════════════════════════════════════════════
        # ORGANIZATION (Green) — IDs 56-75
        # ═══════════════════════════════════════════════════════════════════
        
        # Aggregates (56-65)
        self._add(56, "Class", ["class_definition"], "Organization", "Aggregates", "molecule",
                  "Class definition", "class keyword")
        self._add(57, "ValueObject", [], "Organization", "Aggregates", "molecule",
                  "Immutable value type", "class immutable + no id")
        self._add(58, "Entity", [], "Organization", "Aggregates", "molecule",
                  "Entity with identity", "class with id field")
        self._add(59, "AggregateRoot", [], "Organization", "Aggregates", "organelle",
                  "Aggregate root", "raises domain events")
        self._add(60, "DTO", [], "Organization", "Aggregates", "molecule",
                  "Data transfer object", "data-only class")
        self._add(61, "Factory", [], "Organization", "Aggregates", "molecule",
                  "Factory class/method", "static create method")
        
        # Modules (66-75)
        self._add(66, "Import", ["import_statement"], "Organization", "Modules", "atom",
                  "Import statement", "import keyword")
        self._add(67, "ImportFrom", ["import_from_statement"], "Organization", "Modules", "atom",
                  "From import", "from x import y")
        self._add(68, "ImportAlias", ["aliased_import"], "Organization", "Modules", "atom",
                  "Import alias", "import as")
        self._add(69, "DottedName", ["dotted_name"], "Organization", "Modules", "atom",
                  "Dotted module path", "a.b.c")
        self._add(70, "Comment", ["comment"], "Organization", "Files", "atom",
                  "Code comment", "# or //")
        
        # Types (71-75)
        self._add(71, "TypeAnnotation", ["type"], "Organization", "Types", "atom",
                  "Type annotation", ": Type")
        self._add(72, "GenericType", ["generic_type"], "Organization", "Types", "atom",
                  "Generic type", "List[T]")
        self._add(73, "UnionType", ["union_type"], "Organization", "Types", "atom",
                  "Union type", "A | B")
        self._add(74, "KeywordArg", ["keyword_argument"], "Organization", "Types", "atom",
                  "Keyword argument", "key=value")
        
        # ═══════════════════════════════════════════════════════════════════
        # EXECUTION (Amber) — IDs 76-96
        # ═══════════════════════════════════════════════════════════════════
        
        # (These are typically organelles - inferred from patterns)
        self._add(76, "MainEntry", [], "Execution", "Executables", "organelle",
                  "Main entry point", "if __name__")
        self._add(77, "APIHandler", [], "Execution", "Executables", "organelle",
                  "API route handler", "@app.get/post")
        self._add(78, "CommandHandler", [], "Execution", "Executables", "organelle",
                  "Command handler (CQRS)", "handles *Command")
        self._add(79, "QueryHandler", [], "Execution", "Executables", "organelle",
                  "Query handler (CQRS)", "handles *Query")
        self._add(80, "EventHandler", [], "Execution", "Executables", "organelle",
                  "Event handler", "@Subscribe")
        self._add(81, "Middleware", [], "Execution", "Executables", "organelle",
                  "Middleware function", "calls next()")
        self._add(82, "Validator", [], "Execution", "Executables", "organelle",
                  "Validation function", "validate* + throws")
        self._add(83, "Repository", [], "Execution", "Executables", "organelle",
                  "Repository pattern", "save/find methods")
        self._add(84, "UseCase", [], "Execution", "Executables", "organelle",
                  "Use case handler", "single execute method")
    
    def _add(self, id: int, name: str, ast_types: List[str], continent: str, 
             fundamental: str, level: str, description: str, detection_rule: str):
        """Add an atom to the registry."""
        atom = AtomDefinition(
            id=id, name=name, ast_types=ast_types, continent=continent,
            fundamental=fundamental, level=level, description=description,
            detection_rule=detection_rule, source="original"
        )
        self.atoms[id] = atom
        
        # Map AST types to this atom
        for ast_type in ast_types:
            self.ast_type_map[ast_type] = id
    
    def add_discovery(self, name: str, ast_types: List[str], continent: str,
                      fundamental: str, level: str, description: str,
                      detection_rule: str, source_repo: str) -> int:
        """Add a newly discovered atom to the registry."""
        atom = AtomDefinition(
            id=self.next_id,
            name=name,
            ast_types=ast_types,
            continent=continent,
            fundamental=fundamental,
            level=level,
            description=description,
            detection_rule=detection_rule,
            source=source_repo,
            discovered_at=datetime.now().isoformat()
        )
        self.atoms[self.next_id] = atom
        
        for ast_type in ast_types:
            self.ast_type_map[ast_type] = self.next_id
        
        self.next_id += 1
        return atom.id
    
    def get_by_ast_type(self, ast_type: str) -> Optional[AtomDefinition]:
        """Get atom definition by AST node type."""
        if ast_type in self.ast_type_map:
            return self.atoms[self.ast_type_map[ast_type]]
        return None
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        by_continent = {}
        by_fundamental = {}
        by_level = {}
        by_source = {"original": 0, "discovered": 0}
        
        for atom in self.atoms.values():
            by_continent[atom.continent] = by_continent.get(atom.continent, 0) + 1
            by_fundamental[atom.fundamental] = by_fundamental.get(atom.fundamental, 0) + 1
            by_level[atom.level] = by_level.get(atom.level, 0) + 1
            if atom.source == "original":
                by_source["original"] += 1
            else:
                by_source["discovered"] += 1
        
        return {
            "total_atoms": len(self.atoms),
            "ast_types_mapped": len(self.ast_type_map),
            "by_continent": by_continent,
            "by_fundamental": by_fundamental,
            "by_level": by_level,
            "by_source": by_source,
            "next_id": self.next_id,
        }
    
    def export_canon(self, path: str):
        """Export the canonical registry to JSON."""
        data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "atoms": {
                str(id): {
                    "id": atom.id,
                    "name": atom.name,
                    "ast_types": atom.ast_types,
                    "continent": atom.continent,
                    "fundamental": atom.fundamental,
                    "level": atom.level,
                    "description": atom.description,
                    "detection_rule": atom.detection_rule,
                    "source": atom.source,
                    "discovered_at": atom.discovered_at,
                } for id, atom in self.atoms.items()
            }
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_summary(self):
        """Print a summary of the registry."""
        stats = self.get_stats()
        
        print("=" * 70)
        print("🧬 ATOM REGISTRY — Canonical Taxonomy")
        print("=" * 70)
        print()
        print(f"📊 Total Atoms: {stats['total_atoms']}")
        print(f"📊 AST Types Mapped: {stats['ast_types_mapped']}")
        print(f"📊 Original (96 base): {stats['by_source']['original']}")
        print(f"📊 Discovered: {stats['by_source']['discovered']}")
        print()
        
        print("By Continent:")
        for continent, count in sorted(stats['by_continent'].items(), key=lambda x: -x[1]):
            bar = "█" * min(count // 2, 30)
            print(f"  {continent:20} {count:3} {bar}")
        print()
        
        print("By Fundamental:")
        for fund, count in sorted(stats['by_fundamental'].items(), key=lambda x: -x[1]):
            bar = "█" * min(count, 30)
            print(f"  {fund:20} {count:3} {bar}")
        print()
        
        print("By Level:")
        for level, count in sorted(stats['by_level'].items(), key=lambda x: -x[1]):
            bar = "█" * min(count, 30)
            print(f"  {level:12} {count:3} {bar}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    registry = AtomRegistry()
    registry.print_summary()
    
    # Export canonical registry
    output_path = Path(__file__).parent.parent / "output" / "atom_registry_canon.json"
    output_path.parent.mkdir(exist_ok=True)
    registry.export_canon(str(output_path))
    print()
    print(f"💾 Exported to: {output_path}")
