#!/usr/bin/env python3
"""
Coverage Scanner - Find missing atoms in crosswalks

Uses Python's built-in ast module to enumerate all AST node types,
then compares against our crosswalk files to find gaps.

No external dependencies required.
"""

import ast
import json
from pathlib import Path
from typing import Set, Dict, List

# All Python AST node types (from ast module)
PYTHON_AST_NODES: Set[str] = {
    # Modules
    "Module", "Interactive", "Expression", "FunctionType",
    
    # Statements
    "FunctionDef", "AsyncFunctionDef", "ClassDef", "Return", "Delete",
    "Assign", "AugAssign", "AnnAssign", "For", "AsyncFor", "While", "If",
    "With", "AsyncWith", "Match", "Raise", "Try", "TryStar", "Assert",
    "Import", "ImportFrom", "Global", "Nonlocal", "Expr", "Pass", "Break",
    "Continue",
    
    # Expressions
    "BoolOp", "NamedExpr", "BinOp", "UnaryOp", "Lambda", "IfExp", "Dict",
    "Set", "ListComp", "SetComp", "DictComp", "GeneratorExp", "Await",
    "Yield", "YieldFrom", "Compare", "Call", "FormattedValue", "JoinedStr",
    "Constant", "Attribute", "Subscript", "Starred", "Name", "List",
    "Tuple", "Slice",
    
    # Expression context
    "Load", "Store", "Del",
    
    # Boolean operators
    "And", "Or",
    
    # Binary operators
    "Add", "Sub", "Mult", "MatMult", "Div", "Mod", "Pow", "LShift",
    "RShift", "BitOr", "BitXor", "BitAnd", "FloorDiv",
    
    # Unary operators
    "Invert", "Not", "UAdd", "USub",
    
    # Comparison operators
    "Eq", "NotEq", "Lt", "LtE", "Gt", "GtE", "Is", "IsNot", "In", "NotIn",
    
    # Comprehensions
    "comprehension",
    
    # Exception handling
    "ExceptHandler",
    
    # Arguments
    "arguments", "arg", "keyword",
    
    # Match patterns (3.10+)
    "match_case", "MatchValue", "MatchSingleton", "MatchSequence",
    "MatchMapping", "MatchClass", "MatchStar", "MatchAs", "MatchOr",
    
    # Type parameters (3.12+)
    "TypeVar", "ParamSpec", "TypeVarTuple", "TypeAlias",
}

# TypeScript AST node types (from TypeScript compiler API)
TYPESCRIPT_AST_NODES: Set[str] = {
    "SourceFile", "Block", "ModuleBlock", "ClassBody",
    
    # Declarations
    "VariableDeclaration", "FunctionDeclaration", "ClassDeclaration",
    "InterfaceDeclaration", "TypeAliasDeclaration", "EnumDeclaration",
    "ModuleDeclaration", "ImportDeclaration", "ExportDeclaration",
    "ExportAssignment", "NamespaceExportDeclaration",
    
    # Statements
    "VariableStatement", "ExpressionStatement", "IfStatement",
    "DoStatement", "WhileStatement", "ForStatement", "ForInStatement",
    "ForOfStatement", "ContinueStatement", "BreakStatement",
    "ReturnStatement", "WithStatement", "SwitchStatement", "LabeledStatement",
    "ThrowStatement", "TryStatement", "DebuggerStatement", "EmptyStatement",
    
    # Expressions
    "BinaryExpression", "UnaryExpression", "ConditionalExpression",
    "CallExpression", "NewExpression", "TaggedTemplateExpression",
    "TypeAssertionExpression", "ParenthesizedExpression", "DeleteExpression",
    "TypeOfExpression", "VoidExpression", "AwaitExpression", "YieldExpression",
    "SpreadElement", "ClassExpression", "OmittedExpression", "AsExpression",
    "NonNullExpression", "MetaProperty", "SatisfiesExpression",
    
    # Literals
    "NumericLiteral", "BigIntLiteral", "StringLiteral", "RegularExpressionLiteral",
    "NoSubstitutionTemplateLiteral", "TemplateHead", "TemplateMiddle",
    "TemplateTail", "TemplateSpan", "TemplateLiteralType",
    "TrueKeyword", "FalseKeyword", "NullKeyword", "UndefinedKeyword",
    
    # Primary
    "Identifier", "ThisKeyword", "SuperKeyword", "ArrayLiteralExpression",
    "ObjectLiteralExpression", "PropertyAccessExpression",
    "ElementAccessExpression", "FunctionExpression", "ArrowFunction",
    
    # Members
    "PropertyDeclaration", "MethodDeclaration", "Constructor",
    "GetAccessor", "SetAccessor", "IndexSignature",
    
    # Clauses
    "CaseClause", "DefaultClause", "HeritageClause", "CatchClause",
    
    # Types
    "TypeReference", "FunctionType", "ConstructorType", "TypeQuery",
    "TypeLiteral", "ArrayType", "TupleType", "OptionalType", "RestType",
    "UnionType", "IntersectionType", "ConditionalType", "InferType",
    "ParenthesizedType", "MappedType", "IndexedAccessType", "LiteralType",
    
    # Decorators
    "Decorator",
    
    # Other
    "Parameter", "TypeParameter", "ComputedPropertyName", "PrivateIdentifier",
    "ImportClause", "ImportSpecifier", "ExportSpecifier", "NamespaceImport",
    "NamespaceExport", "NamedImports", "NamedExports",
}

# Go AST node types (from go/ast package)
GO_AST_NODES: Set[str] = {
    # Files
    "File", "Package",
    
    # Declarations
    "GenDecl", "FuncDecl", "ImportSpec", "ValueSpec", "TypeSpec",
    
    # Statements
    "AssignStmt", "BlockStmt", "BranchStmt", "CaseClause", "CommClause",
    "DeclStmt", "DeferStmt", "EmptyStmt", "ExprStmt", "ForStmt", "GoStmt",
    "IfStmt", "IncDecStmt", "LabeledStmt", "RangeStmt", "ReturnStmt",
    "SelectStmt", "SendStmt", "SwitchStmt", "TypeSwitchStmt",
    
    # Expressions
    "BadExpr", "Ident", "Ellipsis", "BasicLit", "FuncLit", "CompositeLit",
    "ParenExpr", "SelectorExpr", "IndexExpr", "IndexListExpr", "SliceExpr",
    "TypeAssertExpr", "CallExpr", "StarExpr", "UnaryExpr", "BinaryExpr",
    "KeyValueExpr",
    
    # Types
    "ArrayType", "StructType", "FuncType", "InterfaceType", "MapType",
    "ChanType",
    
    # Other
    "Field", "FieldList",
}

# Rust AST node types (from Tree-sitter Rust grammar)
RUST_AST_NODES: Set[str] = {
    # Source and modules
    "source_file", "mod_item", "foreign_mod_item",
    
    # Items
    "const_item", "static_item", "type_item", "impl_item", "trait_item",
    "struct_item", "enum_item", "union_item", "extern_crate_declaration",
    "use_declaration", "function_item", "associated_type", "macro_definition",
    "macro_invocation",
    
    # Statements
    "let_declaration", "expression_statement", "empty_statement",
    
    # Expressions
    "block", "if_expression", "if_let_expression", "match_expression",
    "while_expression", "while_let_expression", "loop_expression",
    "for_expression", "return_expression", "break_expression",
    "continue_expression", "await_expression", "yield_expression",
    "try_expression", "closure_expression", "async_block",
    "call_expression", "method_call_expression", "generic_function",
    "field_expression", "index_expression", "range_expression",
    "binary_expression", "unary_expression", "reference_expression",
    "dereference_expression", "try_expression", "type_cast_expression",
    "assignment_expression", "compound_assignment_expr",
    "struct_expression", "tuple_expression", "array_expression",
    "parenthesized_expression", "unit_expression",
    
    # Patterns
    "tuple_pattern", "slice_pattern", "struct_pattern", "ref_pattern",
    "captured_pattern", "reference_pattern", "remaining_field_pattern",
    "mut_pattern", "range_pattern", "or_pattern", "identifier_pattern",
    "_", "rest_pattern",
    
    # Literals
    "string_literal", "raw_string_literal", "char_literal", "boolean_literal",
    "integer_literal", "float_literal",
    
    # Other
    "identifier", "field_identifier", "type_identifier", "lifetime",
    "attribute_item", "inner_attribute_item", "match_arm", "match_pattern",
    "visibility_modifier", "macro_rule", "token_tree",
}

# Java AST node types (from Eclipse JDT)
JAVA_AST_NODES: Set[str] = {
    # Compilation
    "CompilationUnit", "PackageDeclaration", "ImportDeclaration",
    
    # Types
    "TypeDeclaration", "ClassDeclaration", "InterfaceDeclaration",
    "EnumDeclaration", "AnnotationTypeDeclaration", "RecordDeclaration",
    
    # Class members
    "FieldDeclaration", "MethodDeclaration", "ConstructorDeclaration",
    "Initializer", "EnumConstantDeclaration", "AnnotationTypeMemberDeclaration",
    
    # Statements
    "Block", "ExpressionStatement", "VariableDeclarationStatement",
    "EmptyStatement", "AssertStatement", "SwitchStatement", "SwitchCase",
    "IfStatement", "WhileStatement", "DoStatement", "ForStatement",
    "EnhancedForStatement", "BreakStatement", "ContinueStatement",
    "ReturnStatement", "ThrowStatement", "SynchronizedStatement",
    "TryStatement", "CatchClause", "TypeDeclarationStatement",
    "ConstructorInvocation", "SuperConstructorInvocation", "LabeledStatement",
    "YieldStatement",
    
    # Expressions
    "Assignment", "MethodInvocation", "SuperMethodInvocation",
    "ClassInstanceCreation", "ArrayCreation", "ArrayInitializer",
    "FieldAccess", "SuperFieldAccess", "ArrayAccess", "ThisExpression",
    "ParenthesizedExpression", "InfixExpression", "PrefixExpression",
    "PostfixExpression", "ConditionalExpression", "CastExpression",
    "InstanceofExpression", "LambdaExpression", "MethodReference",
    "CreationReference", "ExpressionMethodReference", "SuperMethodReference",
    "TypeMethodReference", "SwitchExpression",
    
    # Literals
    "NumberLiteral", "CharacterLiteral", "StringLiteral", "TextBlock",
    "NullLiteral", "BooleanLiteral", "TypeLiteral",
    
    # Variables
    "SimpleName", "QualifiedName", "SingleVariableDeclaration",
    "VariableDeclarationFragment",
    
    # Types
    "SimpleType", "ArrayType", "ParameterizedType", "WildcardType",
    "UnionType", "IntersectionType", "NameQualifiedType", "PrimitiveType",
    "QualifiedType",
    
    # Other
    "Modifier", "Annotation", "MarkerAnnotation", "NormalAnnotation",
    "SingleMemberAnnotation", "MemberValuePair", "Dimension",
    "TypeParameter", "LineComment", "BlockComment", "Javadoc", "TagElement",
}


def load_crosswalk(language: str) -> Dict:
    """Load crosswalk file for a language."""
    crosswalk_path = Path(__file__).parent.parent.parent / "schema" / "crosswalks" / f"{language}.json"
    if crosswalk_path.exists():
        with open(crosswalk_path) as f:
            return json.load(f)
    return {"mappings": []}


def get_mapped_nodes(crosswalk: Dict) -> Set[str]:
    """Extract all mapped AST nodes from a crosswalk."""
    return {m["ast_node"] for m in crosswalk.get("mappings", [])}


def find_missing(language: str, known_nodes: Set[str]) -> List[Dict]:
    """Find AST nodes not in our crosswalk."""
    crosswalk = load_crosswalk(language)
    mapped = get_mapped_nodes(crosswalk)
    
    missing = []
    for node in sorted(known_nodes - mapped):
        missing.append({
            "ast_node": node,
            "status": "MISSING",
            "suggested_atom": suggest_atom(node, language),
        })
    
    return missing


def suggest_atom(node_type: str, language: str) -> str:
    """Suggest an atom for an unmapped node type."""
    node_lower = node_type.lower()
    
    # Literals
    if "literal" in node_lower or node_lower in ("true", "false", "null"):
        return "DAT.PRM.A (Literal)"
    
    # Variables/Identifiers
    if "identifier" in node_lower or "name" in node_lower:
        return "LOG.EXP.A (IdentifierExpr)"
    
    # Statements
    if "statement" in node_lower or "stmt" in node_lower:
        return "LOG.STM.A (Statement)"
    
    # Expressions
    if "expression" in node_lower or "expr" in node_lower:
        return "LOG.EXP.A (Expression)"
    
    # Declarations
    if "declaration" in node_lower or "decl" in node_lower:
        return "ORG.AGG.M (Declaration)"
    
    # Types
    if "type" in node_lower and "spec" not in node_lower:
        return "ORG.AGG.M (TypeDef)"
    
    # Operators
    if node_type in ("Add", "Sub", "Mult", "Div", "And", "Or", "Not"):
        return "(skip - operator token, not node)"
    
    # Context (Load, Store, Del)
    if node_type in ("Load", "Store", "Del"):
        return "(skip - context marker, not node)"
    
    return "UNKNOWN - manual review needed"


def generate_report():
    """Generate coverage report for all languages."""
    languages = {
        "python": PYTHON_AST_NODES,
        "typescript": TYPESCRIPT_AST_NODES,
        "go": GO_AST_NODES,
        "rust": RUST_AST_NODES,
        "java": JAVA_AST_NODES,
    }
    
    print("=" * 70)
    print("ATOM COVERAGE SCANNER - Finding Missing AST Nodes")
    print("=" * 70)
    
    total_missing = 0
    all_missing = {}
    
    for lang, nodes in languages.items():
        crosswalk = load_crosswalk(lang)
        mapped = get_mapped_nodes(crosswalk)
        missing = find_missing(lang, nodes)
        
        # Filter out skips
        actionable_missing = [m for m in missing if "skip" not in m["suggested_atom"]]
        
        print(f"\n{'─' * 70}")
        print(f"{lang.upper()}")
        print(f"{'─' * 70}")
        print(f"Total AST nodes:   {len(nodes)}")
        print(f"Mapped in crosswalk: {len(mapped)}")
        print(f"Missing (actionable): {len(actionable_missing)}")
        
        if actionable_missing:
            print("\nMISSING NODES:")
            for m in actionable_missing[:15]:  # Show first 15
                print(f"  - {m['ast_node']:30} → {m['suggested_atom']}")
            if len(actionable_missing) > 15:
                print(f"  ... and {len(actionable_missing) - 15} more")
        
        total_missing += len(actionable_missing)
        all_missing[lang] = actionable_missing
    
    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {total_missing} total missing nodes across all languages")
    print(f"{'=' * 70}")
    
    return all_missing


if __name__ == "__main__":
    generate_report()
