#!/usr/bin/env python3
"""
Semantic ID System — Self-Describing Identifiers for LLM Understanding

The Problem:
  Traditional IDs: "func_123", "class_456" → meaningless to LLMs
  
The Solution:
  Semantic IDs encode ALL fundamental information IN the ID itself:
  
  OLD: "dddpy/domain/todo/entity.py:Todo"
  NEW: "ORG.AGG.ENT|dddpy.domain.todo|Todo|has_id:true|mutable:true|bases:1"
  
  An LLM can READ the ID and immediately understand:
  - Organization continent, Aggregates fundamental, Entity level
  - File path context
  - Name
  - Key properties

This creates a SELF-ORGANIZING MATRIX where:
- IDs cluster by continent/fundamental
- Properties are queryable from the ID itself
- Syntax and semantics are unified

"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import hashlib
import re


# =============================================================================
# SEMANTIC ID COMPONENTS
# =============================================================================

class Continent(Enum):
    """The 4 continents from the Standard Model."""
    DATA = "DAT"       # Data Foundations
    LOGIC = "LOG"      # Logic & Flow
    ORG = "ORG"        # Organization
    EXEC = "EXE"       # Execution


class Fundamental(Enum):
    """Fundamental particles (simplified set)."""
    # Data Foundations
    PRIM = "PRM"       # Primitives
    VAR = "VAR"        # Variables
    
    # Logic & Flow
    EXPR = "EXP"       # Expressions
    STMT = "STM"       # Statements
    CTRL = "CTL"       # Control Structures
    FUNC = "FNC"       # Functions
    
    # Organization
    AGG = "AGG"        # Aggregates (classes)
    MOD = "MOD"        # Modules
    TYPE = "TYP"       # Types
    
    # Execution
    ENTRY = "ENT"      # Entry points
    HANDLER = "HDL"    # Handlers


class Level(Enum):
    """Abstraction level."""
    ATOM = "A"         # Syntax primitive
    MOLECULE = "M"     # Compound structure
    ORGANELLE = "O"    # Architecture role


# =============================================================================
# SEMANTIC ID CLASS
# =============================================================================

@dataclass
class SemanticID:
    """
    A self-describing identifier that encodes all fundamental information.
    
    Format: CONTINENT.FUNDAMENTAL.LEVEL|path|name|prop1:val1|prop2:val2|hash
    
    Examples:
      LOG.FNC.M|dddpy.usecase.todo|CreateTodoUseCase.execute|async:true|io:true|abc123
      ORG.AGG.M|dddpy.domain.todo|Todo|has_id:true|mutable:true|bases:0|def456
      DAT.PRM.A|dddpy.domain|string_literal|value:hello|len:5|ghi789
    """
    
    # Classification (the "chromosome")
    continent: Continent
    fundamental: Fundamental
    level: Level
    
    # Location (the "address")
    module_path: str       # dot-separated path
    name: str              # entity name
    
    # Properties (the "genes")
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Hash (for deduplication/change detection)
    content_hash: str = ""
    
    def __post_init__(self):
        """Compute hash if not provided."""
        if not self.content_hash:
            self.content_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute a short hash from core properties."""
        data = f"{self.continent.value}{self.fundamental.value}{self.module_path}{self.name}"
        return hashlib.md5(data.encode()).hexdigest()[:6]
    
    def to_string(self) -> str:
        """
        Generate the full semantic ID string.
        
        This is the key format that LLMs can parse and understand.
        """
        # Classification prefix
        classification = f"{self.continent.value}.{self.fundamental.value}.{self.level.value}"
        
        # Path and name
        location = f"{self.module_path}|{self.name}"
        
        # Properties (sorted for consistency)
        props = "|".join(f"{k}:{v}" for k, v in sorted(self.properties.items()))
        
        # Combine all parts
        if props:
            return f"{classification}|{location}|{props}|{self.content_hash}"
        else:
            return f"{classification}|{location}|{self.content_hash}"
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"SemanticID({self.to_string()})"
    
    @classmethod
    def parse(cls, id_string: str) -> 'SemanticID':
        """Parse a semantic ID string back into an object."""
        parts = id_string.split("|")
        
        # Parse classification
        classification = parts[0].split(".")
        continent = Continent(classification[0])
        fundamental = Fundamental(classification[1])
        level = Level(classification[2])
        
        # Parse location
        module_path = parts[1]
        name = parts[2]
        
        # Parse properties
        properties = {}
        for part in parts[3:-1]:  # Skip last (hash)
            if ":" in part:
                k, v = part.split(":", 1)
                # Try to parse value types
                if v.lower() == "true":
                    properties[k] = True
                elif v.lower() == "false":
                    properties[k] = False
                elif v.isdigit():
                    properties[k] = int(v)
                else:
                    properties[k] = v
        
        content_hash = parts[-1]
        
        return cls(
            continent=continent,
            fundamental=fundamental,
            level=level,
            module_path=module_path,
            name=name,
            properties=properties,
            content_hash=content_hash,
        )
    
    def to_llm_context(self) -> str:
        """
        Generate a natural language description for LLM context.
        
        This is what an LLM reads to understand the entity.
        """
        continent_names = {
            Continent.DATA: "Data Foundations",
            Continent.LOGIC: "Logic & Flow",
            Continent.ORG: "Organization",
            Continent.EXEC: "Execution",
        }
        
        level_names = {
            Level.ATOM: "syntax primitive",
            Level.MOLECULE: "compound structure",
            Level.ORGANELLE: "architecture role",
        }
        
        props_desc = ", ".join(f"{k}={v}" for k, v in self.properties.items())
        
        return (
            f"{self.name} is a {level_names[self.level]} in the {continent_names[self.continent]} "
            f"continent, specifically a {self.fundamental.name}. "
            f"Located at {self.module_path}. "
            f"Properties: {props_desc or 'none'}."
        )
    
    def similarity_vector(self) -> Tuple[int, int, int, str]:
        """
        Return a tuple that can be used for similarity comparison.
        
        Entities with similar vectors are architecturally similar.
        """
        return (
            list(Continent).index(self.continent),
            list(Fundamental).index(self.fundamental),
            list(Level).index(self.level),
            self.module_path.split(".")[0] if self.module_path else "",
        )


# =============================================================================
# SEMANTIC ID GENERATOR
# =============================================================================

class SemanticIDGenerator:
    """
    Generates semantic IDs from code analysis data.
    
    Takes atoms, functions, classes from the extractors and produces
    LLM-optimized semantic IDs.
    """
    
    def __init__(self):
        # Mapping from AST types to classification
        self.ast_to_classification = {
            # Data Foundations
            "integer": (Continent.DATA, Fundamental.PRIM, Level.ATOM),
            "float": (Continent.DATA, Fundamental.PRIM, Level.ATOM),
            "string": (Continent.DATA, Fundamental.PRIM, Level.ATOM),
            "identifier": (Continent.DATA, Fundamental.VAR, Level.ATOM),
            "attribute": (Continent.DATA, Fundamental.VAR, Level.ATOM),
            
            # Logic & Flow
            "call": (Continent.LOGIC, Fundamental.EXPR, Level.ATOM),
            "binary_operator": (Continent.LOGIC, Fundamental.EXPR, Level.ATOM),
            "assignment": (Continent.LOGIC, Fundamental.STMT, Level.ATOM),
            "return_statement": (Continent.LOGIC, Fundamental.STMT, Level.ATOM),
            "if_statement": (Continent.LOGIC, Fundamental.CTRL, Level.ATOM),
            "for_statement": (Continent.LOGIC, Fundamental.CTRL, Level.ATOM),
            "function_definition": (Continent.LOGIC, Fundamental.FUNC, Level.MOLECULE),
            
            # Organization
            "class_definition": (Continent.ORG, Fundamental.AGG, Level.MOLECULE),
            "import_statement": (Continent.ORG, Fundamental.MOD, Level.ATOM),
            "import_from_statement": (Continent.ORG, Fundamental.MOD, Level.ATOM),
        }
    
    def generate_ids(self, codebase) -> List[SemanticID]:
        """Generate semantic IDs for the entire codebase."""
        from dataclasses import asdict
        ids = []
        
        # Functions
        for func in codebase.functions.values():
            # Convert dataclass to dict for compatibility
            data = asdict(func)
            ids.append(self.from_function(data, func.file))
            
        # Classes
        for cls in codebase.classes.values():
            data = asdict(cls)
            ids.append(self.from_class(data, cls.file))
            
        return ids
    
    def from_function(self, func_data: Dict, file_path: str) -> SemanticID:
        """Generate semantic ID for a function."""
        
        # Determine classification based on function properties
        is_async = func_data.get("is_async", False)
        has_io = any(call in str(func_data.get("calls", [])).lower() 
                     for call in ["save", "insert", "fetch", "request", "open", "write"])
        
        # Is it a handler/organelle?
        name = func_data.get("name", "")
        is_handler = any(x in name.lower() for x in ["handle", "execute", "run", "process"])
        is_validator = name.lower().startswith("validate")
        
        if is_handler or is_validator:
            level = Level.ORGANELLE
            fundamental = Fundamental.HANDLER
            continent = Continent.EXEC
        else:
            level = Level.MOLECULE
            fundamental = Fundamental.FUNC
            continent = Continent.LOGIC
        
        # Build properties
        properties = {
            "async": is_async,
            "io": has_io,
            "params": len(func_data.get("parameters", [])),
            "calls": len(func_data.get("calls", [])),
            "lines": func_data.get("end_line", 0) - func_data.get("start_line", 0),
        }
        
        # Remove false booleans for cleaner IDs
        properties = {k: v for k, v in properties.items() if v}
        
        # Module path from file
        module_path = file_path.replace("/", ".").replace(".py", "")
        
        return SemanticID(
            continent=continent,
            fundamental=fundamental,
            level=level,
            module_path=module_path,
            name=name,
            properties=properties,
        )
    
    def from_class(self, class_data: Dict, file_path: str) -> SemanticID:
        """Generate semantic ID for a class."""
        
        name = class_data.get("name", "")
        bases = class_data.get("bases", [])
        methods = class_data.get("methods", [])
        instance_vars = class_data.get("instance_vars", [])
        
        # Determine if it's a DDD pattern
        is_entity = "id" in [v.lower() for v in instance_vars]
        is_repository = "Repository" in name or any("save" in m or "find" in m for m in methods)
        is_usecase = "UseCase" in name or "execute" in methods
        is_value_object = not is_entity and len(instance_vars) > 0
        
        if is_repository:
            level = Level.ORGANELLE
            fundamental = Fundamental.HANDLER
            continent = Continent.EXEC
        elif is_usecase:
            level = Level.ORGANELLE
            fundamental = Fundamental.HANDLER
            continent = Continent.EXEC
        elif is_entity:
            level = Level.MOLECULE
            fundamental = Fundamental.AGG
            continent = Continent.ORG
        else:
            level = Level.MOLECULE
            fundamental = Fundamental.AGG
            continent = Continent.ORG
        
        # Build properties
        properties = {
            "bases": len(bases),
            "methods": len(methods),
            "vars": len(instance_vars),
        }
        
        if is_entity:
            properties["has_id"] = True
        if is_repository:
            properties["repo"] = True
        if is_usecase:
            properties["use_case"] = True
        
        properties = {k: v for k, v in properties.items() if v}
        
        module_path = file_path.replace("/", ".").replace(".py", "")
        
        return SemanticID(
            continent=continent,
            fundamental=fundamental,
            level=level,
            module_path=module_path,
            name=name,
            properties=properties,
        )
    
    def from_atom(self, ast_type: str, file_path: str, line: int) -> SemanticID:
        """Generate semantic ID for an atom."""
        
        classification = self.ast_to_classification.get(
            ast_type, 
            (Continent.DATA, Fundamental.PRIM, Level.ATOM)
        )
        
        module_path = file_path.replace("/", ".").replace(".py", "")
        
        return SemanticID(
            continent=classification[0],
            fundamental=classification[1],
            level=classification[2],
            module_path=module_path,
            name=f"{ast_type}@L{line}",
            properties={"line": line},
        )

    def from_particle(self, particle: Dict) -> SemanticID:
        """Generate semantic ID from a Universal Detector particle."""
        ptype = particle.get("type", "Unknown")
        name = particle.get("name", "")
        file_path = particle.get("file_path", "")
        
        # Default classification
        continent = Continent.ORG
        fundamental = Fundamental.AGG
        level = Level.MOLECULE
        
        # Map known types
        if ptype in ["UseCase", "Controller", "EventHandler", "Observer", "Command", "Query"]:
            continent = Continent.EXEC
            fundamental = Fundamental.HANDLER
            level = Level.ORGANELLE
        elif ptype in ["Repository", "RepositoryImpl", "Service", "DomainService", "Factory", "Policy"]:
            continent = Continent.EXEC
            fundamental = Fundamental.HANDLER
            level = Level.ORGANELLE
        elif ptype in ["Entity", "ValueObject", "DTO", "Specification"]:
            continent = Continent.ORG
            fundamental = Fundamental.AGG
            level = Level.MOLECULE
        elif particle.get("symbol_kind") == "function":
            continent = Continent.LOGIC
            fundamental = Fundamental.FUNC
            level = Level.MOLECULE
            
        module_path = file_path.replace("/", ".").replace(".py", "")
        if "spectrometer_v12_minimal" in module_path:
             # Clean up path slightly for internal repos
             try:
                 idx = module_path.index("spectrometer_v12_minimal")
                 module_path = module_path[idx+len("spectrometer_v12_minimal")+1:]
             except: pass
        if module_path.startswith("."): module_path = module_path[1:]
        
        properties = {
            "type": ptype,
            "line": particle.get("line", 0),
            "confidence": particle.get("confidence", 0),
        }
        
        return SemanticID(
            continent=continent,
            fundamental=fundamental,
            level=level,
            module_path=module_path,
            name=name,
            properties=properties,
        )


# =============================================================================
# SEMANTIC MATRIX
# =============================================================================

class SemanticMatrix:
    """
    A self-organizing matrix of semantic IDs.
    
    This is the LLM-optimized view of the codebase:
    - Grouped by continent/fundamental
    - Sorted by similarity
    - Ready for embedding and retrieval
    """
    
    def __init__(self):
        self.ids: List[SemanticID] = []
        self.by_continent: Dict[Continent, List[SemanticID]] = {c: [] for c in Continent}
        self.by_fundamental: Dict[Fundamental, List[SemanticID]] = {f: [] for f in Fundamental}
        self.by_level: Dict[Level, List[SemanticID]] = {l: [] for l in Level}
        self.by_module: Dict[str, List[SemanticID]] = {}
    
    def add(self, semantic_id: SemanticID):
        """Add a semantic ID to the matrix."""
        self.ids.append(semantic_id)
        self.by_continent[semantic_id.continent].append(semantic_id)
        self.by_fundamental[semantic_id.fundamental].append(semantic_id)
        self.by_level[semantic_id.level].append(semantic_id)
        
        module = semantic_id.module_path.split(".")[0] if semantic_id.module_path else "root"
        if module not in self.by_module:
            self.by_module[module] = []
        self.by_module[module].append(semantic_id)
    
    def to_llm_context(self, max_items: int = 100) -> str:
        """
        Generate a complete LLM context from the matrix.
        
        This is what you feed to an LLM to understand the codebase.
        """
        lines = [
            "# Codebase Semantic Map",
            "",
            f"Total entities: {len(self.ids)}",
            "",
        ]
        
        # Group by continent
        for continent in Continent:
            items = self.by_continent[continent]
            if items:
                lines.append(f"## {continent.name} ({len(items)} items)")
                for item in items[:max_items // 4]:
                    lines.append(f"  - {item.to_string()}")
                lines.append("")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        """Get matrix statistics."""
        return {
            "total": len(self.ids),
            "by_continent": {c.name: len(self.by_continent[c]) for c in Continent},
            "by_level": {l.name: len(self.by_level[l]) for l in Level},
            "modules": len(self.by_module),
        }
    
    def export_for_embedding(self) -> List[Dict]:
        """
        Export IDs in a format suitable for vector embedding.
        
        Each entry can be embedded and used for semantic search.
        """
        return [
            {
                "id": sid.to_string(),
                "text": sid.to_llm_context(),
                "vector_key": sid.similarity_vector(),
            }
            for sid in self.ids
        ]


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import json
    from pathlib import Path
    
    print("=" * 70)
    print("🧬 SEMANTIC ID SYSTEM — LLM-Optimized Identifiers")
    print("=" * 70)
    print()
    
    # Demo: Generate semantic IDs from sample data
    generator = SemanticIDGenerator()
    matrix = SemanticMatrix()
    
    # Load complete codebase data
    codebase_path = Path(__file__).parent.parent / "output" / "complete_codebase.json"
    
    if codebase_path.exists():
        data = json.loads(codebase_path.read_text())
        
        print(f"Processing {len(data.get('functions', {}))} functions, {len(data.get('classes', {}))} classes...")
        print()
        
        # Generate semantic IDs for functions
        for fid, func in data.get("functions", {}).items():
            sid = generator.from_function(func, func.get("file", ""))
            matrix.add(sid)
        
        # Generate semantic IDs for classes
        for cid, cls in data.get("classes", {}).items():
            sid = generator.from_class(cls, cls.get("file", ""))
            matrix.add(sid)
        
        stats = matrix.get_stats()
        
        print("📊 SEMANTIC MATRIX STATS:")
        print(f"   Total IDs: {stats['total']}")
        print()
        print("   By Continent:")
        for c, count in stats['by_continent'].items():
            bar = "█" * min(count, 30)
            print(f"     {c:8} {count:4} {bar}")
        print()
        print("   By Level:")
        for l, count in stats['by_level'].items():
            bar = "█" * min(count, 30)
            print(f"     {l:10} {count:4} {bar}")
        print()
        
        # Show sample semantic IDs
        print("🆔 SAMPLE SEMANTIC IDs:")
        print("-" * 70)
        for sid in matrix.ids[:10]:
            print(f"  {sid.to_string()}")
        print()
        
        # Show LLM context for one
        print("🤖 LLM CONTEXT EXAMPLE:")
        print("-" * 70)
        if matrix.ids:
            print(f"  {matrix.ids[0].to_llm_context()}")
        print()
        
        # Export
        export_path = Path(__file__).parent.parent / "output" / "semantic_ids.json"
        export_data = {
            "stats": stats,
            "ids": [sid.to_string() for sid in matrix.ids],
            "llm_context": matrix.to_llm_context(),
        }
        export_path.write_text(json.dumps(export_data, indent=2))
        print(f"💾 Exported to: {export_path}")
        
    else:
        print(f"ERROR: Complete codebase not found at {codebase_path}")
        print("Run complete_extractor.py first.")
