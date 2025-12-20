#!/usr/bin/env python3
"""
Inheritance-Based Truth Extractor

Extracts high-confidence (99%) ground truth from DDD repositories by analyzing
class inheritance hierarchies. Classes that explicitly inherit from known DDD
base classes are identified with their roles.

This produces benchmark specs that can be trusted for validation.
"""

import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Known DDD base class patterns and their canonical type mappings
DDD_BASE_CLASSES = {
    # Entities
    "Entity": "Entity",
    "BaseEntity": "Entity",
    "EntityModel": "Entity",
    "DomainEntity": "Entity",
    
    # Value Objects
    "ValueObject": "ValueObject",
    "ValueObjectModel": "ValueObject",
    "BaseFrozenModel": "ValueObject",
    
    # Aggregates
    "AggregateRoot": "AggregateRoot",
    "Aggregate": "AggregateRoot",
    
    # Repositories
    "GenericRepository": "Repository",
    "AbstractRepository": "Repository",
    "BaseRepository": "Repository",
    
    # Commands/Queries (CQRS)
    "Command": "Command",
    "BaseCommand": "Command",
    "Query": "Query",
    "BaseQuery": "Query",
    
    # Events
    "DomainEvent": "DomainEvent",
    "Event": "DomainEvent",
    "IntegrationEvent": "DomainEvent",
    
    # Services
    "DomainService": "Service",
    "ApplicationService": "Service",
    
    # DTOs/Schemas (via Pydantic often)
    "BaseModel": "DTO",  # Pydantic - only in presentation/api layers
}

# Paths that indicate presentation layer (for BaseModel -> DTO mapping)
PRESENTATION_PATH_HINTS = {
    "presentation", "api", "schemas", "dto", "views", "endpoints",
    "controllers", "handlers", "routes", "rest", "graphql"
}

# Paths that indicate infrastructure layer (for Repository implementations)
INFRA_PATH_HINTS = {
    "infrastructure", "infra", "adapters", "persistence", "db", "database",
    "repositories", "repo", "sqlite", "postgres", "mysql", "mongo", "redis"
}


@dataclass
class ExtractedComponent:
    """A component extracted from source code with high confidence."""
    rel_file: str
    symbol: str
    symbol_kind: str  # 'class' or 'function'
    type: str  # The DDD role
    base_class: str  # What it inherits from
    confidence: float = 0.99
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "rel_file": self.rel_file,
            "symbol": self.symbol,
            "symbol_kind": self.symbol_kind,
            "type": self.type,
            "base_class": self.base_class,
            "confidence": self.confidence,
        }


@dataclass  
class ExtractionResult:
    """Result of extracting truth from a repository."""
    repo_name: str
    repo_path: str
    base_classes_found: dict[str, str] = field(default_factory=dict)  # name -> file
    components: list[ExtractedComponent] = field(default_factory=list)
    files_scanned: int = 0
    errors: list[str] = field(default_factory=list)


def _is_presentation_path(rel_path: str) -> bool:
    """Check if path is in presentation/API layer."""
    parts = set(Path(rel_path).parts)
    return bool(parts & PRESENTATION_PATH_HINTS)


def _is_infra_path(rel_path: str) -> bool:
    """Check if path is in infrastructure layer."""
    parts = set(Path(rel_path).parts)
    return bool(parts & INFRA_PATH_HINTS)


def _get_base_names(node: ast.ClassDef) -> list[str]:
    """Extract base class names from a class definition."""
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(base.attr)
        elif isinstance(base, ast.Subscript):
            # Generic types like Generic[T]
            if isinstance(base.value, ast.Name):
                bases.append(base.value.id)
            elif isinstance(base.value, ast.Attribute):
                bases.append(base.value.attr)
    return bases


def _find_ddd_base_definitions(repo_root: Path) -> dict[str, str]:
    """
    Find files that define DDD base classes (Entity, ValueObject, etc).
    Returns map of base_class_name -> relative_file_path
    """
    base_defs: dict[str, str] = {}
    
    for py_file in repo_root.rglob("*.py"):
        # Skip test files and hidden dirs
        rel = py_file.relative_to(repo_root)
        rel_str = str(rel)
        if any(part.startswith(".") or part in {"test", "tests", "__pycache__", ".git", "venv", ".venv"} 
               for part in rel.parts):
            continue
            
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue
            
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this class IS a DDD base class definition
                if node.name in DDD_BASE_CLASSES:
                    # Verify it's likely a base class (abstract or minimal)
                    bases = _get_base_names(node)
                    # Often inherits from ABC, Generic, or nothing (indicating base class)
                    if not bases or any(b in {"ABC", "Generic", "object", "type"} for b in bases):
                        base_defs[node.name] = rel_str
                        
    return base_defs


def _map_type_with_context(base_name: str, rel_path: str) -> tuple[str, float]:
    """
    Map a base class to a DDD type, with path context for refinement.
    Returns (type, confidence).
    """
    if base_name not in DDD_BASE_CLASSES:
        return ("Unknown", 0.5)
    
    base_type = DDD_BASE_CLASSES[base_name]
    confidence = 0.99
    
    # Special case: BaseModel is only DTO in presentation layer
    if base_name == "BaseModel":
        if _is_presentation_path(rel_path):
            return ("DTO", 0.95)
        else:
            # Could be domain model, lower confidence
            return ("Model", 0.70)
    
    # Repository implementations in infra layer
    if base_type == "Repository" and _is_infra_path(rel_path):
        return ("RepositoryImpl", 0.99)
    
    return (base_type, confidence)


def extract_inheritance_truth(repo_root: Path) -> ExtractionResult:
    """
    Extract high-confidence ground truth from a repository by analyzing
    class inheritance hierarchies.
    """
    repo_name = repo_root.name
    result = ExtractionResult(repo_name=repo_name, repo_path=str(repo_root))
    
    # First pass: find where base classes are defined
    result.base_classes_found = _find_ddd_base_definitions(repo_root)
    
    # Build set of all relevant base classes (predefined + discovered)
    relevant_bases = set(DDD_BASE_CLASSES.keys()) | set(result.base_classes_found.keys())
    
    # Second pass: find all classes that inherit from these bases
    seen_components: set[tuple[str, str]] = set()  # (file, symbol) for dedup
    
    for py_file in repo_root.rglob("*.py"):
        rel = py_file.relative_to(repo_root)
        rel_str = str(rel)
        
        # Skip non-essential files
        if any(part.startswith(".") or part in {"__pycache__", ".git", "venv", ".venv"} 
               for part in rel.parts):
            continue
        
        # Skip test files for golden specs
        if any(part in {"test", "tests", "testing"} for part in rel.parts):
            continue
            
        result.files_scanned += 1
        
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError as e:
            result.errors.append(f"{rel_str}: SyntaxError: {e}")
            continue
        except Exception as e:
            result.errors.append(f"{rel_str}: {type(e).__name__}: {e}")
            continue
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = _get_base_names(node)
                
                for base in bases:
                    if base in relevant_bases:
                        # Found a class inheriting from a DDD base
                        ddd_type, confidence = _map_type_with_context(base, rel_str)
                        
                        # Skip if type couldn't be determined with high confidence
                        if confidence < 0.80:
                            continue
                        
                        # Skip if it's the base class definition itself
                        if node.name == base:
                            continue
                        
                        # Deduplicate
                        key = (rel_str, node.name)
                        if key in seen_components:
                            continue
                        seen_components.add(key)
                        
                        component = ExtractedComponent(
                            rel_file=rel_str,
                            symbol=node.name,
                            symbol_kind="class",
                            type=ddd_type,
                            base_class=base,
                            confidence=confidence,
                        )
                        result.components.append(component)
                        break  # Only count first relevant base
    
    return result


def generate_bench_spec(result: ExtractionResult, scored_types: list[str] | None = None) -> dict[str, Any]:
    """
    Generate a benchmark spec JSON from extraction results.
    """
    if scored_types is None:
        # Default scored types based on what we found
        found_types = set(c.type for c in result.components)
        scored_types = sorted(found_types - {"Model", "Unknown"})
    
    # Filter to high-confidence components only
    high_conf_components = [c for c in result.components if c.confidence >= 0.95]
    
    expected_components = []
    for c in high_conf_components:
        expected_components.append({
            "rel_file": c.rel_file,
            "symbol": c.symbol,
            "symbol_kind": c.symbol_kind,
            "type": c.type,
        })
    
    return {
        "version": 1,
        "name": result.repo_name,
        "repo_dir": result.repo_name,
        "scored_types": scored_types,
        "ignore_path_globs": [
            "**/tests/**",
            "**/test/**",
            "**/__init__.py",
            "**/.venv/**",
            "**/.git/**",
        ],
        "expected_components": expected_components,
        "extraction_metadata": {
            "method": "inheritance_analysis",
            "confidence_threshold": 0.95,
            "files_scanned": result.files_scanned,
            "base_classes_found": result.base_classes_found,
        },
        "notes": f"Auto-generated via inheritance analysis. {len(high_conf_components)} components with ≥95% confidence.",
    }


def main(argv: list[str]) -> int:
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract high-confidence ground truth from DDD repositories via inheritance analysis."
    )
    parser.add_argument(
        "repo_path",
        help="Path to the repository to analyze.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path. If not specified, prints to stdout.",
    )
    parser.add_argument(
        "--bench-spec",
        action="store_true",
        help="Output as benchmark spec format instead of raw extraction.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print progress information.",
    )
    
    args = parser.parse_args(argv)
    repo_path = Path(args.repo_path).resolve()
    
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        return 1
    
    if args.verbose:
        print(f"Analyzing: {repo_path}", file=sys.stderr)
    
    result = extract_inheritance_truth(repo_path)
    
    if args.verbose:
        print(f"Files scanned: {result.files_scanned}", file=sys.stderr)
        print(f"Base classes found: {list(result.base_classes_found.keys())}", file=sys.stderr)
        print(f"Components extracted: {len(result.components)}", file=sys.stderr)
        if result.errors:
            print(f"Errors: {len(result.errors)}", file=sys.stderr)
    
    if args.bench_spec:
        output = generate_bench_spec(result)
    else:
        output = {
            "repo": result.repo_name,
            "repo_path": result.repo_path,
            "files_scanned": result.files_scanned,
            "base_classes_found": result.base_classes_found,
            "components": [c.to_dict() for c in result.components],
            "errors": result.errors,
        }
    
    json_str = json.dumps(output, indent=2)
    
    if args.output:
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(json_str)
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
