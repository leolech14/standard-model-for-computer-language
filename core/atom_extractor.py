"""
Atom Extractor — Maps tree-sitter AST nodes to the 96 Hadrons taxonomy.

Hierarchy:
  ATOMS (syntax primitives) → MOLECULES (program structure) → ORGANELLES (architecture roles)

Tree-sitter provides the universal atomic layer. This module:
1. Extracts atoms from source code using tree-sitter
2. Composes atoms into molecules
3. Infers organelles (architecture roles) from patterns
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import json


class HadronLevel(Enum):
    """The three-level hierarchy from STANDARD_MODEL_STRUCTURE.md"""
    ATOM = "atom"           # Syntax primitives (tree-sitter leaf nodes)
    MOLECULE = "molecule"   # Program structure (tree-sitter compound nodes)
    ORGANELLE = "organelle" # Architecture roles (inferred from patterns)


@dataclass
class Hadron:
    """A detected code element mapped to the 96 Hadrons taxonomy."""
    id: int                          # 1-96 from HADRONS_96_FULL.md
    name: str                        # e.g., "PureFunction", "Entity"
    level: HadronLevel               # atom/molecule/organelle
    continent: str                   # Data Foundations, Logic & Flow, Organization, Execution
    fundamental: str                 # e.g., Bits, Functions, Aggregates
    
    # Source location
    file_path: str = ""
    start_line: int = 0
    end_line: int = 0
    text_snippet: str = ""
    
    # Detection evidence
    detection_rule: str = ""         # What matched
    confidence: float = 1.0          # 0.0-1.0
    
    # Composition (for molecules/organelles)
    composed_of: List[str] = field(default_factory=list)


# =============================================================================
# ATOM DEFINITIONS — Direct mapping from tree-sitter node types
# =============================================================================

ATOM_MAP: Dict[str, Dict] = {
    # ─────────────────────────────────────────────────────────────────────────
    # Data Foundations (Cyan) — Bits, Bytes, Primitives, Variables
    # ─────────────────────────────────────────────────────────────────────────
    
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
    
    # ─────────────────────────────────────────────────────────────────────────
    # Logic & Flow (Magenta) — Expressions, Statements, Control, Functions
    # ─────────────────────────────────────────────────────────────────────────
    
    # Expressions (18-20)
    "binary_expression": {"id": 18, "name": "ArithmeticExpr", "fundamental": "Expressions", "continent": "Logic & Flow"},
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
    
    # Functions (30-42) — These are MOLECULES, inferred from function_definition
    "function_definition": {"id": 30, "name": "Function", "fundamental": "Functions", "continent": "Logic & Flow"},
    "lambda": {"id": 34, "name": "Closure", "fundamental": "Functions", "continent": "Logic & Flow"},
    "async_function": {"id": 32, "name": "AsyncFunction", "fundamental": "Functions", "continent": "Logic & Flow"},
    "generator_function": {"id": 33, "name": "Generator", "fundamental": "Functions", "continent": "Logic & Flow"},
}


# =============================================================================
# MOLECULE DEFINITIONS — Compound patterns detected from atoms
# =============================================================================

MOLECULE_PATTERNS: Dict[str, Dict] = {
    # Organization (43-58) — Aggregates, Modules, Files
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
# ORGANELLE DEFINITIONS — Architecture roles inferred from molecule patterns
# =============================================================================

ORGANELLE_PATTERNS: Dict[str, Dict] = {
    # Function-based organelles (35-42)
    "command_handler": {"id": 35, "name": "CommandHandler", "fundamental": "Functions", "continent": "Logic & Flow",
                        "detection": "method handles *Command and returns void"},
    "query_handler": {"id": 36, "name": "QueryHandler", "fundamental": "Functions", "continent": "Logic & Flow",
                      "detection": "method handles *Query and returns data"},
    "event_handler": {"id": 37, "name": "EventHandler", "fundamental": "Functions", "continent": "Logic & Flow",
                      "detection": "@Subscribe/@On decorator or handles *Event"},
    "saga_step": {"id": 38, "name": "SagaStep", "fundamental": "Functions", "continent": "Logic & Flow",
                  "detection": "compensate* method in saga class"},
    "middleware": {"id": 39, "name": "Middleware", "fundamental": "Functions", "continent": "Logic & Flow",
                   "detection": "calls next() or await next"},
    "validator": {"id": 40, "name": "Validator", "fundamental": "Functions", "continent": "Logic & Flow",
                  "detection": "validate* method that throws"},
    "mapper": {"id": 41, "name": "Mapper", "fundamental": "Functions", "continent": "Logic & Flow",
               "detection": "*To*/*Map*/*Convert* method"},
    "reducer": {"id": 42, "name": "Reducer", "fundamental": "Functions", "continent": "Logic & Flow",
                "detection": "reduce/fold function signature"},
    
    # Class-based organelles
    "repository": {"id": 52, "name": "Repository", "fundamental": "Modules", "continent": "Organization",
                   "detection": "class with save/find/delete methods + I/O"},
    "use_case": {"id": 54, "name": "UseCase", "fundamental": "Modules", "continent": "Organization",
                 "detection": "class with single execute/handle method"},
    "controller": {"id": 63, "name": "Controller", "fundamental": "Executables", "continent": "Execution",
                   "detection": "class with route decorators (@app.get, etc.)"},
}


# =============================================================================
# I/O DETECTION — For purity analysis
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


# =============================================================================
# ATOM EXTRACTOR CLASS
# =============================================================================

class AtomExtractor:
    """
    Extracts atoms, molecules, and organelles from source code using tree-sitter.
    
    Usage:
        extractor = AtomExtractor()
        hadrons = extractor.extract(code, language="python", file_path="user.py")
    """
    
    def __init__(self):
        self.parsers: Dict[str, any] = {}
        self._init_parsers()
    
    def _init_parsers(self):
        """Initialize tree-sitter parsers for supported languages."""
        try:
            from tree_sitter import Language, Parser
            
            # Python
            try:
                import tree_sitter_python as tspython
                parser = Parser(Language(tspython.language()))
                self.parsers["python"] = parser
            except ImportError:
                pass
            
            # TypeScript
            try:
                import tree_sitter_typescript as tstypescript
                parser = Parser(Language(tstypescript.language_typescript()))
                self.parsers["typescript"] = parser
            except ImportError:
                pass
            
            # JavaScript
            try:
                import tree_sitter_javascript as tsjavascript
                parser = Parser(Language(tsjavascript.language()))
                self.parsers["javascript"] = parser
            except ImportError:
                pass
            
            # Go
            try:
                import tree_sitter_go as tsgo
                parser = Parser(Language(tsgo.language()))
                self.parsers["go"] = parser
            except ImportError:
                pass
                
            # Java
            try:
                import tree_sitter_java as tsjava
                parser = Parser(Language(tsjava.language()))
                self.parsers["java"] = parser
            except ImportError:
                pass
                
        except ImportError:
            print("Warning: tree-sitter not installed. Run: pip install tree-sitter")
    
    def extract(self, code: bytes, language: str = "python", file_path: str = "") -> List[Hadron]:
        """
        Extract all hadrons (atoms, molecules, organelles) from source code.
        
        Args:
            code: Source code as bytes
            language: Programming language (python, typescript, go, java)
            file_path: Path to source file (for reporting)
            
        Returns:
            List of detected Hadron objects
        """
        if language not in self.parsers:
            raise ValueError(f"Unsupported language: {language}. Available: {list(self.parsers.keys())}")
        
        parser = self.parsers[language]
        tree = parser.parse(code)
        
        hadrons: List[Hadron] = []
        
        # Phase 1: Extract ATOMS (leaf nodes)
        atoms = self._extract_atoms(tree.root_node, file_path)
        hadrons.extend(atoms)
        
        # Phase 2: Compose MOLECULES (compound patterns)
        molecules = self._extract_molecules(tree.root_node, file_path, atoms)
        hadrons.extend(molecules)
        
        # Phase 3: Infer ORGANELLES (architecture roles)
        organelles = self._infer_organelles(tree.root_node, file_path, atoms, molecules)
        hadrons.extend(organelles)
        
        return hadrons
    
    def _extract_atoms(self, root_node, file_path: str) -> List[Hadron]:
        """Extract atomic syntax elements from AST."""
        atoms = []
        
        def visit(node):
            if node.type in ATOM_MAP:
                mapping = ATOM_MAP[node.type]
                hadron = Hadron(
                    id=mapping["id"],
                    name=mapping["name"],
                    level=HadronLevel.ATOM,
                    continent=mapping["continent"],
                    fundamental=mapping["fundamental"],
                    file_path=file_path,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    text_snippet=node.text.decode()[:100] if node.text else "",
                    detection_rule=f"node_type={node.type}",
                )
                atoms.append(hadron)
            
            for child in node.children:
                visit(child)
        
        visit(root_node)
        return atoms
    
    def _extract_molecules(self, root_node, file_path: str, atoms: List[Hadron]) -> List[Hadron]:
        """Extract molecular patterns (classes, functions with context)."""
        molecules = []
        
        def visit(node):
            # Detect classes
            if node.type == "class_definition":
                molecule = self._classify_class(node, file_path)
                if molecule:
                    molecules.append(molecule)
            
            # Detect functions with semantic analysis
            if node.type == "function_definition":
                molecule = self._classify_function(node, file_path)
                if molecule:
                    molecules.append(molecule)
            
            for child in node.children:
                visit(child)
        
        visit(root_node)
        return molecules
    
    def _classify_class(self, node, file_path: str) -> Optional[Hadron]:
        """Classify a class node into the appropriate molecule/organelle."""
        class_name = ""
        has_id_field = False
        has_save_method = False
        has_find_method = False
        is_immutable = True  # Assume immutable until proven otherwise
        
        for child in node.children:
            if child.type == "identifier":
                class_name = child.text.decode() if child.text else ""
            elif child.type == "block":
                for stmt in child.children:
                    # Check for id field
                    if "id" in (stmt.text.decode() if stmt.text else "").lower():
                        if "self.id" in (stmt.text.decode() if stmt.text else "") or "this.id" in (stmt.text.decode() if stmt.text else ""):
                            has_id_field = True
                    # Check for mutation (setters)
                    if stmt.type == "function_definition":
                        func_name = ""
                        for c in stmt.children:
                            if c.type == "identifier":
                                func_name = c.text.decode() if c.text else ""
                                break
                        if func_name.startswith("set") or func_name.startswith("update"):
                            is_immutable = False
                        if func_name in ("save", "persist", "store"):
                            has_save_method = True
                        if func_name in ("find", "get", "load", "fetch"):
                            has_find_method = True
        
        # Classification logic
        if has_save_method and has_find_method:
            return Hadron(
                id=52, name="Repository", level=HadronLevel.ORGANELLE,
                continent="Organization", fundamental="Modules",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=class_name,
                detection_rule="class with save+find methods",
            )
        elif has_id_field and not is_immutable:
            return Hadron(
                id=44, name="Entity", level=HadronLevel.MOLECULE,
                continent="Organization", fundamental="Aggregates",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=class_name,
                detection_rule="class with id field + mutable",
            )
        elif is_immutable and not has_id_field:
            return Hadron(
                id=43, name="ValueObject", level=HadronLevel.MOLECULE,
                continent="Organization", fundamental="Aggregates",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=class_name,
                detection_rule="class immutable + no id",
            )
        
        return None
    
    def _classify_function(self, node, file_path: str) -> Optional[Hadron]:
        """Classify a function into pure/impure/async/handler."""
        func_name = ""
        is_async = False
        is_generator = False
        has_io = False
        return_type = None
        
        for child in node.children:
            if child.type == "identifier":
                func_name = child.text.decode() if child.text else ""
            elif child.type == "async":
                is_async = True
            elif child.type == "block":
                # Scan for I/O calls
                has_io = self._has_io_calls(child)
        
        # Classification
        if is_async:
            return Hadron(
                id=32, name="AsyncFunction", level=HadronLevel.MOLECULE,
                continent="Logic & Flow", fundamental="Functions",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=func_name,
                detection_rule="async keyword",
            )
        elif not has_io:
            return Hadron(
                id=30, name="PureFunction", level=HadronLevel.MOLECULE,
                continent="Logic & Flow", fundamental="Functions",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=func_name,
                detection_rule="no I/O calls detected",
                confidence=0.8,  # Not 100% sure without deeper analysis
            )
        else:
            return Hadron(
                id=31, name="ImpureFunction", level=HadronLevel.MOLECULE,
                continent="Logic & Flow", fundamental="Functions",
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                text_snippet=func_name,
                detection_rule="has I/O calls",
            )
    
    def _has_io_calls(self, node) -> bool:
        """Check if a node contains any I/O-related function calls."""
        if node.type == "call":
            call_text = node.text.decode() if node.text else ""
            for io_func in IO_INDICATORS:
                if io_func in call_text.lower():
                    return True
        
        for child in node.children:
            if self._has_io_calls(child):
                return True
        
        return False
    
    def _infer_organelles(self, root_node, file_path: str, 
                          atoms: List[Hadron], molecules: List[Hadron]) -> List[Hadron]:
        """Infer architecture-level organelles from patterns."""
        organelles = []
        
        # Look for handler patterns in function names
        def visit(node):
            if node.type == "function_definition":
                func_name = ""
                for child in node.children:
                    if child.type == "identifier":
                        func_name = child.text.decode() if child.text else ""
                        break
                
                # Command handler detection
                if "command" in func_name.lower() and "handle" in func_name.lower():
                    organelles.append(Hadron(
                        id=35, name="CommandHandler", level=HadronLevel.ORGANELLE,
                        continent="Logic & Flow", fundamental="Functions",
                        file_path=file_path,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        text_snippet=func_name,
                        detection_rule="name contains command+handle",
                    ))
                
                # Query handler detection
                elif "query" in func_name.lower() and "handle" in func_name.lower():
                    organelles.append(Hadron(
                        id=36, name="QueryHandler", level=HadronLevel.ORGANELLE,
                        continent="Logic & Flow", fundamental="Functions",
                        file_path=file_path,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        text_snippet=func_name,
                        detection_rule="name contains query+handle",
                    ))
                
                # Validator detection
                elif func_name.lower().startswith("validate"):
                    organelles.append(Hadron(
                        id=40, name="Validator", level=HadronLevel.ORGANELLE,
                        continent="Logic & Flow", fundamental="Functions",
                        file_path=file_path,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        text_snippet=func_name,
                        detection_rule="name starts with validate",
                    ))
            
            for child in node.children:
                visit(child)
        
        visit(root_node)
        return organelles
    
    def to_json(self, hadrons: List[Hadron]) -> str:
        """Convert hadrons to JSON for output."""
        return json.dumps([{
            "id": h.id,
            "name": h.name,
            "level": h.level.value,
            "continent": h.continent,
            "fundamental": h.fundamental,
            "file_path": h.file_path,
            "start_line": h.start_line,
            "end_line": h.end_line,
            "text_snippet": h.text_snippet,
            "detection_rule": h.detection_rule,
            "confidence": h.confidence,
        } for h in hadrons], indent=2)
    
    def summary(self, hadrons: List[Hadron]) -> Dict:
        """Generate summary statistics."""
        by_level = {"atom": 0, "molecule": 0, "organelle": 0}
        by_continent = {}
        by_fundamental = {}
        by_name = {}
        
        for h in hadrons:
            by_level[h.level.value] += 1
            by_continent[h.continent] = by_continent.get(h.continent, 0) + 1
            by_fundamental[h.fundamental] = by_fundamental.get(h.fundamental, 0) + 1
            by_name[h.name] = by_name.get(h.name, 0) + 1
        
        return {
            "total": len(hadrons),
            "by_level": by_level,
            "by_continent": by_continent,
            "by_fundamental": by_fundamental,
            "top_10_hadrons": sorted(by_name.items(), key=lambda x: -x[1])[:10],
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Demo usage
    demo_code = b'''
class UserRepository:
    def __init__(self, db):
        self.db = db
    
    def save(self, user):
        self.db.insert(user)
    
    def find(self, user_id):
        return self.db.query(user_id)

class Email:
    """Value object for email addresses."""
    def __init__(self, value: str):
        self._value = value
    
    @property
    def value(self) -> str:
        return self._value

def validate_email(email: str) -> bool:
    if "@" not in email:
        raise ValueError("Invalid email")
    return True

async def fetch_user(user_id: str):
    response = await request(f"/users/{user_id}")
    return response.json()

def calculate_total(items: list) -> float:
    return sum(item.price for item in items)
'''
    
    print("=" * 60)
    print("ATOM EXTRACTOR — Tree-sitter → 96 Hadrons Mapping")
    print("=" * 60)
    
    extractor = AtomExtractor()
    
    if "python" in extractor.parsers:
        hadrons = extractor.extract(demo_code, language="python", file_path="demo.py")
        
        print(f"\nExtracted {len(hadrons)} hadrons:\n")
        
        # Group by level
        for level in [HadronLevel.ORGANELLE, HadronLevel.MOLECULE, HadronLevel.ATOM]:
            level_hadrons = [h for h in hadrons if h.level == level]
            if level_hadrons:
                print(f"─── {level.value.upper()}S ({len(level_hadrons)}) ───")
                for h in level_hadrons[:10]:  # Show first 10
                    print(f"  [{h.id:2}] {h.name:20} | {h.fundamental:15} | L{h.start_line}")
                if len(level_hadrons) > 10:
                    print(f"  ... and {len(level_hadrons) - 10} more")
                print()
        
        print("\n─── SUMMARY ───")
        summary = extractor.summary(hadrons)
        print(f"Total: {summary['total']}")
        print(f"By level: {summary['by_level']}")
        print(f"Top hadrons: {summary['top_10_hadrons']}")
    else:
        print("\nError: tree-sitter-python not installed.")
        print("Run: pip install tree-sitter tree-sitter-python")
