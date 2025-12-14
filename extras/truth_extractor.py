#!/usr/bin/env python3
"""
🔍 TRUTH EXTRACTOR — Discovers Golden Truth FROM Repositories

The golden truth must come from the devs, not from us. This module finds:
1. ARCHITECTURE.md, DESIGN.md, docs/architecture/* files
2. Type annotations that declare intent (Entity, ValueObject, etc)
3. Decorators (@aggregate, @entity, @use_case)
4. Base class inheritance (ABC, BaseModel, etc)
5. Directory structure conventions (domain/, usecase/, infra/)
6. Docstrings with architectural markers

The extracted truth becomes the golden spec that we score against.
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
import json


@dataclass
class DiscoveredTruth:
    """Truth discovered from a repository."""
    repo_path: str
    repo_name: str
    
    # Sources found
    architecture_files: List[str] = field(default_factory=list)
    design_docs: List[str] = field(default_factory=list)
    
    # Inferred structure
    layers: List[str] = field(default_factory=list)
    
    # Developer-declared components
    declared_entities: List[Dict] = field(default_factory=list)
    declared_value_objects: List[Dict] = field(default_factory=list)
    declared_repositories: List[Dict] = field(default_factory=list)
    declared_use_cases: List[Dict] = field(default_factory=list)
    declared_services: List[Dict] = field(default_factory=list)
    
    # From type hints
    typed_components: List[Dict] = field(default_factory=list)
    
    # From inheritance
    base_class_map: Dict[str, List[str]] = field(default_factory=dict)
    
    # From decorators
    decorated_classes: List[Dict] = field(default_factory=list)
    
    # Confidence
    truth_confidence: float = 0.0
    truth_sources: List[str] = field(default_factory=list)


class TruthExtractor:
    """
    Extracts golden truth from repositories based on developer declarations.
    """
    
    # Files that might contain architecture truth
    TRUTH_FILES = [
        "ARCHITECTURE.md",
        "DESIGN.md",
        "architecture.md",
        "design.md",
        "docs/architecture.md",
        "docs/design.md",
        "docs/ARCHITECTURE.md",
        "docs/adr/*.md",  # Architecture Decision Records
        ".architecture",
        "CLAUDE.md",  # Some repos use this for AI context
        "README.md",  # Often has structure docs
    ]
    
    # DDD type hints we look for
    DDD_TYPE_PATTERNS = [
        r"class\s+(\w+)\s*\([^)]*Entity[^)]*\)",
        r"class\s+(\w+)\s*\([^)]*ValueObject[^)]*\)",
        r"class\s+(\w+)\s*\([^)]*AggregateRoot[^)]*\)",
        r"class\s+(\w+)\s*\([^)]*Repository[^)]*\)",
        r"class\s+(\w+)\s*\([^)]*UseCase[^)]*\)",
        r"class\s+(\w+)\s*\([^)]*Service[^)]*\)",
        r"class\s+(\w+)\s*\([^)]*Command[^)]*\)",
        r"class\s+(\w+)\s*\([^)]*Query[^)]*\)",
        r"class\s+(\w+)\s*\([^)]*Event[^)]*\)",
    ]
    
    # Decorators that declare component types
    DDD_DECORATORS = [
        r"@entity",
        r"@aggregate",
        r"@value_object",
        r"@repository",
        r"@use_case",
        r"@service",
        r"@domain_event",
        r"@command",
        r"@query",
    ]
    
    # Layer directory patterns
    LAYER_PATTERNS = {
        "domain": ["domain", "entities", "model", "core"],
        "application": ["application", "usecase", "usecases", "use_cases", "services"],
        "infrastructure": ["infrastructure", "infra", "adapters", "persistence", "repositories"],
        "presentation": ["presentation", "api", "web", "cli", "handlers", "controllers"],
        "interfaces": ["interfaces", "ports"],
    }
    
    def __init__(self):
        self.parsers = {}
        self._init_parsers()
    
    def _init_parsers(self):
        """Initialize tree-sitter parsers."""
        try:
            from tree_sitter import Language, Parser
            import tree_sitter_python as tspython
            self.parsers["python"] = Parser(Language(tspython.language()))
        except ImportError:
            pass
    
    def extract(self, repo_path: str) -> DiscoveredTruth:
        """
        Extract all discoverable truth from a repository.
        """
        path = Path(repo_path)
        truth = DiscoveredTruth(
            repo_path=str(path),
            repo_name=path.name,
        )
        
        # 1. Find architecture documentation
        self._find_architecture_docs(path, truth)
        
        # 2. Detect layer structure
        self._detect_layers(path, truth)
        
        # 3. Find type-hinted components
        self._find_typed_components(path, truth)
        
        # 4. Find decorated classes
        self._find_decorated_classes(path, truth)
        
        # 5. Find inheritance patterns
        self._find_inheritance_patterns(path, truth)
        
        # 5.b Find components by directory convention
        self._find_components_by_convention(path, truth)
        
        # 6. Parse architecture docs for explicit declarations
        self._parse_architecture_docs(truth)
        
        # Calculate confidence
        self._calculate_confidence(truth)
        
        return truth
    
    def _find_architecture_docs(self, path: Path, truth: DiscoveredTruth):
        """Find architecture documentation files."""
        for pattern in self.TRUTH_FILES:
            if "*" in pattern:
                for f in path.glob(pattern):
                    if f.is_file():
                        truth.architecture_files.append(str(f.relative_to(path)))
                        truth.truth_sources.append(f"doc:{f.name}")
            else:
                f = path / pattern
                if f.exists() and f.is_file():
                    truth.architecture_files.append(pattern)
                    truth.truth_sources.append(f"doc:{f.name}")
    
    def _detect_layers(self, path: Path, truth: DiscoveredTruth):
        """Detect architectural layers from directory structure."""
        for layer_name, patterns in self.LAYER_PATTERNS.items():
            for pattern in patterns:
                # Check top-level
                if (path / pattern).is_dir():
                    truth.layers.append(layer_name)
                    truth.truth_sources.append(f"dir:{pattern}")
                    break
                # Check one level deep
                for subdir in path.iterdir():
                    if subdir.is_dir() and (subdir / pattern).is_dir():
                        truth.layers.append(layer_name)
                        truth.truth_sources.append(f"dir:{subdir.name}/{pattern}")
                        break
    
    def _find_typed_components(self, path: Path, truth: DiscoveredTruth):
        """Find classes with DDD type hints."""
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(errors='replace')
                rel_path = str(py_file.relative_to(path))
                
                for pattern in self.DDD_TYPE_PATTERNS:
                    matches = re.findall(pattern, content)
                    for class_name in matches:
                        component_type = self._infer_type_from_pattern(pattern)
                        truth.typed_components.append({
                            "name": class_name,
                            "type": component_type,
                            "file": rel_path,
                            "source": "type_hint",
                        })
                        truth.truth_sources.append(f"type:{component_type}")
            except Exception:
                pass
    
    def _infer_type_from_pattern(self, pattern: str) -> str:
        """Infer component type from regex pattern."""
        if "Entity" in pattern:
            return "Entity"
        elif "ValueObject" in pattern:
            return "ValueObject"
        elif "AggregateRoot" in pattern:
            return "AggregateRoot"
        elif "Repository" in pattern:
            return "Repository"
        elif "UseCase" in pattern:
            return "UseCase"
        elif "Service" in pattern:
            return "Service"
        elif "Command" in pattern:
            return "Command"
        elif "Query" in pattern:
            return "Query"
        elif "Event" in pattern:
            return "Event"
        return "Unknown"
    
    def _find_decorated_classes(self, path: Path, truth: DiscoveredTruth):
        """Find classes with DDD decorators."""
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(errors='replace')
                rel_path = str(py_file.relative_to(path))
                
                for decorator in self.DDD_DECORATORS:
                    if re.search(decorator, content, re.IGNORECASE):
                        # Find the class after the decorator
                        pattern = rf"{decorator}\s*(?:\([^)]*\))?\s*\n\s*class\s+(\w+)"
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for class_name in matches:
                            truth.decorated_classes.append({
                                "name": class_name,
                                "decorator": decorator,
                                "file": rel_path,
                                "source": "decorator",
                            })
                            truth.truth_sources.append(f"decorator:{decorator}")
            except Exception:
                pass
    
    def _find_inheritance_patterns(self, path: Path, truth: DiscoveredTruth):
        """Find classes inheriting from known base classes."""
        known_bases = {
            "ABC": "Abstract",
            "BaseModel": "DTO",
            "Entity": "Entity",
            "ValueObject": "ValueObject",
            "AggregateRoot": "AggregateRoot",
            "Repository": "Repository",
            "UseCase": "UseCase",
            "Enum": "Enum",
            "Exception": "Error",
        }
        
        parser = self.parsers.get("python")
        if not parser:
            return
        
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(errors='replace')
                rel_path = str(py_file.relative_to(path))
                tree = parser.parse(content.encode())
                
                for node in self._walk(tree.root_node):
                    if node.type == "class_definition":
                        class_name = ""
                        bases = []
                        
                        for child in node.children:
                            if child.type == "identifier":
                                class_name = child.text.decode()
                            elif child.type == "argument_list":
                                for arg in child.children:
                                    if arg.type in ("identifier", "attribute"):
                                        base = arg.text.decode()
                                        bases.append(base)
                        
                        for base in bases:
                            base_simple = base.split(".")[-1]
                            if base_simple in known_bases:
                                if base_simple not in truth.base_class_map:
                                    truth.base_class_map[base_simple] = []
                                truth.base_class_map[base_simple].append({
                                    "name": class_name,
                                    "file": rel_path,
                                    "type": known_bases[base_simple],
                                })
                                truth.truth_sources.append(f"inheritance:{base_simple}")
            except Exception:
                pass
            except Exception:
                pass

        # Fallback to regex if no parser or to supplement
        self._find_inheritance_patterns_regex(path, truth, known_bases)

    def _find_inheritance_patterns_regex(self, path: Path, truth: DiscoveredTruth, known_bases: Dict[str, str]):
        """Regex fallback for inheritance patterns."""
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file): continue
            
            try:
                content = py_file.read_text(errors='replace')
                rel_path = str(py_file.relative_to(path))
                
                # Regex for class definitions: class Name(Base1, Base2):
                matches = re.findall(r"class\s+(\w+)\s*\(([^)]+)\)", content)
                for class_name, bases_str in matches:
                    bases = [b.strip() for b in bases_str.split(",")]
                    for base in bases:
                        base_simple = base.split(".")[-1]
                        if base_simple in known_bases:
                            if base_simple not in truth.base_class_map:
                                truth.base_class_map[base_simple] = []
                            
                            # Deduplicate
                            exists = any(item['name'] == class_name for item in truth.base_class_map[base_simple])
                            if not exists:
                                truth.base_class_map[base_simple].append({
                                    "name": class_name,
                                    "file": rel_path,
                                    "type": known_bases[base_simple],
                                })
                                truth.truth_sources.append(f"inheritance(regex):{base_simple}")
            except Exception:
                pass

    def _find_components_by_convention(self, path: Path, truth: DiscoveredTruth):
        """Find components based on directory structure conventions."""
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file): continue
            
            rel_path = str(py_file.relative_to(path))
            normalized = rel_path.lower()
            
            # convention -> type
            guessed_type = None
            if "/entities/" in normalized or "/domain/model/" in normalized:
                guessed_type = "Entity"
            elif "/value_objects/" in normalized:
                guessed_type = "ValueObject"
            elif "/repositories/" in normalized or "/infra/repos/" in normalized:
                guessed_type = "Repository"
            elif "/usecases/" in normalized or "/use_cases/" in normalized:
                guessed_type = "UseCase"
            elif "/services/" in normalized:
                guessed_type = "Service"
            elif "/controllers/" in normalized or "/handlers/" in normalized:
                guessed_type = "Controller"
            
            if guessed_type:
                 # Extract class names from file to verify
                 try:
                     content = py_file.read_text(errors='replace')
                     class_names = re.findall(r"class\s+(\w+)", content)
                     for cn in class_names:
                         # Append to declared lists if not present
                         target_list = None
                         if guessed_type == "Entity": target_list = truth.declared_entities
                         elif guessed_type == "ValueObject": target_list = truth.declared_value_objects
                         elif guessed_type == "Repository": target_list = truth.declared_repositories
                         elif guessed_type == "UseCase": target_list = truth.declared_use_cases
                         elif guessed_type == "Service": target_list = truth.declared_services
                         
                         if target_list is not None:
                             # Check existence
                             if not any(x['name'] == cn for x in target_list):
                                 target_list.append({
                                     "name": cn,
                                     "type": guessed_type,
                                     "file": rel_path,
                                     "source": "convention",
                                 })
                                 truth.truth_sources.append(f"convention:{guessed_type}")
                 except: pass

    def _walk(self, node):
        """Walk all nodes in tree."""
        yield node
        for child in node.children:
            yield from self._walk(child)
    
    def _parse_architecture_docs(self, truth: DiscoveredTruth):
        """Parse architecture docs for explicit component declarations."""
        path = Path(truth.repo_path)
        
        for doc_path in truth.architecture_files:
            try:
                content = (path / doc_path).read_text(errors='replace')
                
                # Look for component lists in markdown
                # Pattern: ## Entities / - Entity1 / - Entity2
                sections = re.split(r"^##\s+", content, flags=re.MULTILINE)
                
                for section in sections:
                    lines = section.split("\n")
                    if not lines:
                        continue
                    
                    header = lines[0].lower().strip()
                    
                    if "entit" in header:
                        self._extract_list_items(lines[1:], truth.declared_entities, "Entity", doc_path)
                    elif "value object" in header or "valueobject" in header:
                        self._extract_list_items(lines[1:], truth.declared_value_objects, "ValueObject", doc_path)
                    elif "repositor" in header:
                        self._extract_list_items(lines[1:], truth.declared_repositories, "Repository", doc_path)
                    elif "use case" in header or "usecase" in header:
                        self._extract_list_items(lines[1:], truth.declared_use_cases, "UseCase", doc_path)
                    elif "service" in header:
                        self._extract_list_items(lines[1:], truth.declared_services, "Service", doc_path)
                        
            except Exception:
                pass
    
    def _extract_list_items(self, lines: List[str], target: List[Dict], 
                            component_type: str, source: str):
        """Extract list items from markdown."""
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                name = line.lstrip("-*").strip()
                # Clean up markdown formatting
                name = re.sub(r"`([^`]+)`", r"\1", name)
                name = re.sub(r"\*\*([^*]+)\*\*", r"\1", name)
                name = name.split(" - ")[0].strip()  # Remove descriptions
                
                if name and not name.startswith("#"):
                    target.append({
                        "name": name,
                        "type": component_type,
                        "source": f"doc:{source}",
                    })
    
    def _calculate_confidence(self, truth: DiscoveredTruth):
        """Calculate confidence in extracted truth."""
        score = 0.0
        
        # Architecture docs are high confidence
        if truth.architecture_files:
            score += 0.3
        
        # Declared components are gold
        declared_count = (
            len(truth.declared_entities) +
            len(truth.declared_value_objects) +
            len(truth.declared_repositories) +
            len(truth.declared_use_cases) +
            len(truth.declared_services)
        )
        if declared_count > 0:
            score += 0.3
        
        # Typed components are silver
        if truth.typed_components:
            score += 0.2
        
        # Layer structure is bronze
        if len(truth.layers) >= 3:
            score += 0.1
        
        # Inheritance patterns
        if truth.base_class_map:
            score += 0.1
        
        truth.truth_confidence = min(score, 1.0)
    
    def to_golden_spec(self, truth: DiscoveredTruth) -> Dict:
        """Convert discovered truth to golden spec format."""
        components = []
        
        # Add declared components
        for comp in truth.declared_entities:
            components.append({"name": comp["name"], "type": "Entity", "source": comp.get("source", "declared")})
        for comp in truth.declared_value_objects:
            components.append({"name": comp["name"], "type": "ValueObject", "source": comp.get("source", "declared")})
        for comp in truth.declared_repositories:
            components.append({"name": comp["name"], "type": "Repository", "source": comp.get("source", "declared")})
        for comp in truth.declared_use_cases:
            components.append({"name": comp["name"], "type": "UseCase", "source": comp.get("source", "declared")})
        for comp in truth.declared_services:
            components.append({"name": comp["name"], "type": "Service", "source": comp.get("source", "declared")})
        
        # Add typed components
        for comp in truth.typed_components:
            components.append({"name": comp["name"], "type": comp["type"], "source": "type_hint"})
        
        # Add decorated components
        for comp in truth.decorated_classes:
            components.append({"name": comp["name"], "type": comp["decorator"].strip("@"), "source": "decorator"})
        
        # Add from inheritance
        for base, classes in truth.base_class_map.items():
            for cls in classes:
                components.append({"name": cls["name"], "type": cls["type"], "source": "inheritance"})
        
        return {
            "repo": truth.repo_name,
            "repo_path": truth.repo_path,
            "confidence": truth.truth_confidence,
            "truth_sources": list(set(truth.truth_sources)),
            "layers": truth.layers,
            "expected_components": components,
            "architecture_docs": truth.architecture_files,
        }


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🔍 Truth Extractor — Discover golden truth FROM repositories"
    )
    parser.add_argument("repo_path", help="Path to repo")
    parser.add_argument("--output", help="Output path for extracted spec")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔍 TRUTH EXTRACTOR — Developer-Declared Truth Discovery")
    print("=" * 70)
    
    extractor = TruthExtractor()
    truth = extractor.extract(args.repo_path)
    
    print(f"\n📁 Repo: {truth.repo_name}")
    print(f"📊 Confidence: {truth.truth_confidence:.0%}")
    
    print(f"\n📄 Architecture docs found: {len(truth.architecture_files)}")
    for doc in truth.architecture_files:
        print(f"   - {doc}")
    
    print(f"\n🏛️ Layers detected: {truth.layers}")
    
    print(f"\n📝 Components from type hints: {len(truth.typed_components)}")
    for comp in truth.typed_components[:10]:
        print(f"   - {comp['name']} ({comp['type']})")
    
    print(f"\n🏷️ Components from decorators: {len(truth.decorated_classes)}")
    for comp in truth.decorated_classes[:10]:
        print(f"   - {comp['name']} ({comp['decorator']})")
    
    print(f"\n🔗 Inheritance patterns:")
    for base, classes in truth.base_class_map.items():
        print(f"   {base}: {len(classes)} classes")
    
    if args.output:
        spec = extractor.to_golden_spec(truth)
        Path(args.output).write_text(json.dumps(spec, indent=2))
        print(f"\n💾 Golden spec: {args.output}")
