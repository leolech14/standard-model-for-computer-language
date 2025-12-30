"""
Hadron Taxonomy
===============

Mappings from tree-sitter nodes to the 96 Hadrons taxonomy.

Continents:
- Data Foundations (Cyan): Bits, Bytes, Primitives, Variables
- Logic & Flow (Magenta): Expressions, Statements, Control, Functions
- Organization (Yellow): Aggregates, Modules, Files
- Execution (Green): Executables, Runtime, Deployment
"""

from typing import Dict, Set

# =============================================================================
# ATOM DEFINITIONS - Direct mapping from tree-sitter node types
# =============================================================================

ATOM_MAP: Dict[str, Dict] = {
    # -------------------------------------------------------------------------
    # Data Foundations (Cyan) - Bits, Bytes, Primitives, Variables
    # -------------------------------------------------------------------------

    # Bits (1-4)
    "binary_expression": {"id": 1, "name": "BitFlag", "fundamental": "Bits", "continent": "Data Foundations"},
    "binary_literal": {"id": 2, "name": "BitMask", "fundamental": "Bits", "continent": "Data Foundations"},

    # Primitives (8-12)
    "true": {"id": 8, "name": "Boolean", "fundamental": "Primitives", "continent": "Data Foundations"},
    "false": {"id": 8, "name": "Boolean", "fundamental": "Primitives", "continent": "Data Foundations"},
    "integer": {"id": 9, "name": "Integer", "fundamental": "Primitives", "continent": "Data Foundations"},
    "float": {"id": 10, "name": "Float", "fundamental": "Primitives", "continent": "Data Foundations"},
    "string": {"id": 11, "name": "StringLiteral", "fundamental": "Primitives", "continent": "Data Foundations"},

    # Variables (13-17)
    "identifier": {"id": 13, "name": "LocalVar", "fundamental": "Variables", "continent": "Data Foundations"},
    "attribute": {"id": 15, "name": "InstanceField", "fundamental": "Variables", "continent": "Data Foundations"},

    # -------------------------------------------------------------------------
    # Logic & Flow (Magenta) - Expressions, Statements, Control, Functions
    # -------------------------------------------------------------------------

    # Expressions (18-20)
    "call": {"id": 19, "name": "CallExpr", "fundamental": "Expressions", "continent": "Logic & Flow"},

    # Statements (21-23)
    "assignment": {"id": 21, "name": "Assignment", "fundamental": "Statements", "continent": "Logic & Flow"},
    "expression_statement": {"id": 23, "name": "ExpressionStmt", "fundamental": "Statements", "continent": "Logic & Flow"},
    "return_statement": {"id": 22, "name": "ReturnStmt", "fundamental": "Statements", "continent": "Logic & Flow"},

    # Control Structures (24-29)
    "if_statement": {"id": 24, "name": "IfBranch", "fundamental": "Control Structures", "continent": "Logic & Flow"},
    "for_statement": {"id": 25, "name": "LoopFor", "fundamental": "Control Structures", "continent": "Logic & Flow"},
    "for_in_statement": {"id": 25, "name": "LoopFor", "fundamental": "Control Structures", "continent": "Logic & Flow"},
    "while_statement": {"id": 26, "name": "LoopWhile", "fundamental": "Control Structures", "continent": "Logic & Flow"},
    "match_statement": {"id": 27, "name": "SwitchCase", "fundamental": "Control Structures", "continent": "Logic & Flow"},
    "switch_statement": {"id": 27, "name": "SwitchCase", "fundamental": "Control Structures", "continent": "Logic & Flow"},
    "try_statement": {"id": 28, "name": "TryCatch", "fundamental": "Control Structures", "continent": "Logic & Flow"},

    # Functions (30-42) - These are MOLECULES, inferred from function_definition
    "function_definition": {"id": 30, "name": "Function", "fundamental": "Functions", "continent": "Logic & Flow"},
    "lambda": {"id": 34, "name": "Closure", "fundamental": "Functions", "continent": "Logic & Flow"},
    "async_function": {"id": 32, "name": "AsyncFunction", "fundamental": "Functions", "continent": "Logic & Flow"},
    "generator_function": {"id": 33, "name": "Generator", "fundamental": "Functions", "continent": "Logic & Flow"},
}


# =============================================================================
# MOLECULE DEFINITIONS - Compound patterns detected from atoms
# =============================================================================

MOLECULE_PATTERNS: Dict[str, Dict] = {
    # Organization (43-58) - Aggregates, Modules, Files
    "class_with_id": {"id": 44, "name": "Entity", "fundamental": "Aggregates", "continent": "Organization"},
    "class_immutable": {"id": 43, "name": "ValueObject", "fundamental": "Aggregates", "continent": "Organization"},
    "class_with_events": {"id": 45, "name": "AggregateRoot", "fundamental": "Aggregates", "continent": "Organization"},
    "class_readonly": {"id": 46, "name": "ReadModel", "fundamental": "Aggregates", "continent": "Organization"},
    "class_dto": {"id": 48, "name": "DTO", "fundamental": "Aggregates", "continent": "Organization"},
    "class_factory": {"id": 49, "name": "Factory", "fundamental": "Aggregates", "continent": "Organization"},

    # Modules (50-54)
    "folder_bounded_context": {"id": 50, "name": "BoundedContext", "fundamental": "Modules", "continent": "Organization"},
    "folder_feature": {"id": 51, "name": "FeatureModule", "fundamental": "Modules", "continent": "Organization"},
    "class_adapter": {"id": 52, "name": "InfrastructureAdapter", "fundamental": "Modules", "continent": "Organization"},
    "interface_port": {"id": 53, "name": "DomainPort", "fundamental": "Modules", "continent": "Organization"},
}


# =============================================================================
# ORGANELLE DEFINITIONS - Architecture roles inferred from molecule patterns
# =============================================================================

ORGANELLE_PATTERNS: Dict[str, Dict] = {
    # Function-based organelles (35-42)
    "command_handler": {
        "id": 35, "name": "CommandHandler", "fundamental": "Functions", "continent": "Logic & Flow",
        "detection": "method handles *Command and returns void"
    },
    "query_handler": {
        "id": 36, "name": "QueryHandler", "fundamental": "Functions", "continent": "Logic & Flow",
        "detection": "method handles *Query and returns data"
    },
    "event_handler": {
        "id": 37, "name": "EventHandler", "fundamental": "Functions", "continent": "Logic & Flow",
        "detection": "@Subscribe/@On decorator or handles *Event"
    },
    "saga_step": {
        "id": 38, "name": "SagaStep", "fundamental": "Functions", "continent": "Logic & Flow",
        "detection": "compensate* method in saga class"
    },
    "middleware": {
        "id": 39, "name": "Middleware", "fundamental": "Functions", "continent": "Logic & Flow",
        "detection": "calls next() or await next"
    },
    "validator": {
        "id": 40, "name": "Validator", "fundamental": "Functions", "continent": "Logic & Flow",
        "detection": "validate* method that throws"
    },
    "mapper": {
        "id": 41, "name": "Mapper", "fundamental": "Functions", "continent": "Logic & Flow",
        "detection": "*To*/*Map*/*Convert* method"
    },
    "reducer": {
        "id": 42, "name": "Reducer", "fundamental": "Functions", "continent": "Logic & Flow",
        "detection": "reduce/fold function signature"
    },

    # Class-based organelles
    "repository": {
        "id": 52, "name": "Repository", "fundamental": "Modules", "continent": "Organization",
        "detection": "class with save/find/delete methods + I/O"
    },
    "use_case": {
        "id": 54, "name": "UseCase", "fundamental": "Modules", "continent": "Organization",
        "detection": "class with single execute/handle method"
    },
    "controller": {
        "id": 63, "name": "Controller", "fundamental": "Executables", "continent": "Execution",
        "detection": "class with route decorators (@app.get, etc.)"
    },
}


# =============================================================================
# I/O DETECTION - For purity analysis
# =============================================================================

IO_INDICATORS: Set[str] = {
    # Database
    'save', 'insert', 'update', 'delete', 'find', 'query', 'execute', 'commit', 'rollback',
    # File
    'open', 'read', 'write', 'close', 'seek',
    # Network
    'request', 'fetch', 'send', 'recv', 'connect', 'get', 'post', 'put', 'patch',
    # Console
    'print', 'log', 'warn', 'error', 'info', 'debug',
    # System
    'sleep', 'exit', 'exec', 'spawn', 'fork',
}

PURE_INDICATORS: Set[str] = {
    # Math
    'abs', 'min', 'max', 'sum', 'len', 'round', 'floor', 'ceil', 'sqrt', 'pow',
    # String
    'upper', 'lower', 'strip', 'split', 'join', 'replace', 'format',
    # Collection
    'map', 'filter', 'reduce', 'sort', 'reverse', 'slice', 'concat',
}
