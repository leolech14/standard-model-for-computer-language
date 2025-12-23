"""
Symbol Classifier

Classifies code symbols (functions, classes, methods) into semantic roles.
Part of the TreeSitterUniversalEngine decomposition (GOD_CLASS_DECOMPOSITION).
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class SymbolKind(Enum):
    """Kind of code symbol."""
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    PROPERTY = "property"
    VARIABLE = "variable"
    CONSTANT = "constant"
    MODULE = "module"


@dataclass
class ClassifiedSymbol:
    """A classified code symbol with its metadata."""
    name: str
    kind: SymbolKind
    role: str
    confidence: float
    file_path: str
    line: int
    end_line: int = 0
    parent: str = ""
    evidence: str = ""
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: str = ""
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "role": self.role,
            "confidence": self.confidence,
            "file_path": self.file_path,
            "line": self.line,
            "end_line": self.end_line,
            "parent": self.parent,
            "evidence": self.evidence,
            "decorators": self.decorators,
            "base_classes": self.base_classes,
            "docstring": self.docstring,
        }


# DDD base class mappings (99% confidence)
DDD_BASE_CLASS_MAPPINGS = {
    # Entities & Value Objects
    "BaseEntity": "Entity",
    "Entity": "Entity",
    "AbstractEntity": "Entity",
    "ValueObject": "ValueObject",
    "BaseValueObject": "ValueObject",
    
    # Aggregates
    "AggregateRoot": "AggregateRoot",
    "BaseAggregateRoot": "AggregateRoot",
    
    # Repositories
    "Repository": "Repository",
    "BaseRepository": "Repository",
    "AbstractRepository": "Repository",
    
    # Commands & Queries
    "Command": "Command",
    "BaseCommand": "Command",
    "Query": "Query",
    "BaseQuery": "Query",
    
    # Services
    "DomainService": "DomainService",
    "ApplicationService": "Service",
    
    # Configuration
    "BaseSettings": "Configuration",
    "Settings": "Configuration",
}

# Decorator mappings
DECORATOR_MAPPINGS = {
    # Python
    "staticmethod": "Utility",
    "classmethod": "Factory",
    "property": "Query",
    "abstractmethod": "Specification",
    "pytest.fixture": "Fixture",
    "fixture": "Fixture",
    
    # FastAPI/Flask
    "get": "Controller",
    "post": "Controller",
    "put": "Controller",
    "delete": "Controller",
    "patch": "Controller",
    "route": "Controller",
    "api": "Controller",
    
    # Django
    "login_required": "Controller",
    "permission_required": "Policy",
    
    # Testing
    "test": "Test",
    "pytest.mark": "Test",
    "mock": "Fixture",
    "patch": "Fixture",
}


class SymbolClassifier:
    """Classifies code symbols based on names, inheritance, and decorators."""
    
    # Prefix patterns for function classification
    PREFIX_PATTERNS = {
        'test_': ('Test', 90),
        'get_': ('Query', 85),
        'fetch_': ('Query', 85),
        'find_': ('Query', 85),
        'load_': ('Query', 85),
        'set_': ('Command', 85),
        'update_': ('Command', 85),
        'delete_': ('Command', 85),
        'remove_': ('Command', 85),
        'add_': ('Command', 85),
        'create_': ('Factory', 85),
        'build_': ('Factory', 85),
        'make_': ('Factory', 85),
        'validate_': ('Validator', 85),
        'check_': ('Validator', 85),
        'is_': ('Specification', 85),
        'has_': ('Specification', 85),
        'can_': ('Specification', 85),
        'handle_': ('EventHandler', 85),
        'on_': ('EventHandler', 85),
        'process_': ('Service', 80),
        'execute_': ('UseCase', 80),
        'convert_': ('Mapper', 80),
        'transform_': ('Mapper', 80),
        'to_': ('Mapper', 80),
        'from_': ('Factory', 80),
        '_': ('Internal', 70),
    }
    
    # Suffix patterns for class classification
    SUFFIX_PATTERNS = {
        'Service': ('Service', 90),
        'Repository': ('Repository', 90),
        'Controller': ('Controller', 90),
        'Handler': ('EventHandler', 85),
        'Factory': ('Factory', 85),
        'Builder': ('Builder', 85),
        'Mapper': ('Mapper', 85),
        'Validator': ('Validator', 85),
        'Entity': ('Entity', 85),
        'DTO': ('DTO', 85),
        'Command': ('Command', 85),
        'Query': ('Query', 85),
        'Event': ('DomainEvent', 85),
        'Policy': ('Policy', 85),
        'Specification': ('Specification', 85),
        'Exception': ('Exception', 85),
        'Error': ('Exception', 80),
        'Test': ('Test', 85),
        'Mock': ('Fixture', 80),
        'Stub': ('Fixture', 80),
        'Fake': ('Fixture', 80),
        'Config': ('Configuration', 80),
        'Settings': ('Configuration', 80),
    }
    
    # Dunder method mappings
    DUNDER_MAPPINGS = {
        '__init__': ('Lifecycle', 95),
        '__new__': ('Factory', 95),
        '__del__': ('Lifecycle', 95),
        '__str__': ('Utility', 90),
        '__repr__': ('Utility', 90),
        '__eq__': ('Specification', 90),
        '__hash__': ('Utility', 90),
        '__iter__': ('Iterator', 90),
        '__next__': ('Iterator', 90),
        '__getitem__': ('Query', 90),
        '__setitem__': ('Command', 90),
        '__call__': ('Command', 90),
        '__enter__': ('Lifecycle', 90),
        '__exit__': ('Lifecycle', 90),
    }
    
    def classify(
        self,
        name: str,
        kind: SymbolKind,
        file_path: str,
        line: int,
        decorators: List[str] = None,
        base_classes: List[str] = None,
        evidence: str = "",
    ) -> ClassifiedSymbol:
        """Classify a symbol based on all available evidence."""
        decorators = decorators or []
        base_classes = base_classes or []
        
        # Try classification in order of confidence
        role, confidence = self._classify_by_inheritance(base_classes)
        
        if confidence < 90:
            dec_role, dec_conf = self._classify_by_decorators(decorators)
            if dec_conf > confidence:
                role, confidence = dec_role, dec_conf
        
        if confidence < 85:
            name_role, name_conf = self._classify_by_name(name, kind)
            if name_conf > confidence:
                role, confidence = name_role, name_conf
        
        if confidence < 70:
            ev_role, ev_conf = self._classify_by_evidence(evidence)
            if ev_conf > confidence:
                role, confidence = ev_role, ev_conf
        
        return ClassifiedSymbol(
            name=name,
            kind=kind,
            role=role,
            confidence=confidence,
            file_path=file_path,
            line=line,
            decorators=decorators,
            base_classes=base_classes,
            evidence=evidence,
        )
    
    def _classify_by_inheritance(self, base_classes: List[str]) -> Tuple[str, float]:
        """Classify by DDD base class inheritance (highest confidence)."""
        for base in base_classes:
            # Handle full path like module.Entity -> Entity
            simple_name = base.split('.')[-1]
            if simple_name in DDD_BASE_CLASS_MAPPINGS:
                return (DDD_BASE_CLASS_MAPPINGS[simple_name], 99)
        return ("Unknown", 0)
    
    def _classify_by_decorators(self, decorators: List[str]) -> Tuple[str, float]:
        """Classify by decorator patterns."""
        for dec in decorators:
            # Handle full decorator path
            simple_name = dec.split('.')[-1].lower()
            if simple_name in DECORATOR_MAPPINGS:
                return (DECORATOR_MAPPINGS[simple_name], 90)
            
            # Check partial matches
            for pattern, role in DECORATOR_MAPPINGS.items():
                if pattern in dec.lower():
                    return (role, 85)
        
        return ("Unknown", 0)
    
    def _classify_by_name(self, name: str, kind: SymbolKind) -> Tuple[str, float]:
        """Classify by naming conventions."""
        name_lower = name.lower()
        short_name = name.split('.')[-1] if '.' in name else name
        short_lower = short_name.lower()
        
        # Check dunder methods
        if short_lower in self.DUNDER_MAPPINGS:
            return self.DUNDER_MAPPINGS[short_lower]
        
        # Check prefix patterns
        for prefix, (role, conf) in self.PREFIX_PATTERNS.items():
            if short_lower.startswith(prefix):
                return (role, conf)
        
        # Check suffix patterns (case-insensitive)
        for suffix, (role, conf) in self.SUFFIX_PATTERNS.items():
            if short_name.endswith(suffix) or short_lower.endswith(suffix.lower()):
                return (role, conf)
        
        # Default based on kind
        if kind == SymbolKind.CLASS:
            return ("DTO", 50)
        elif kind == SymbolKind.FUNCTION:
            return ("Utility", 50)
        
        return ("Unknown", 0)
    
    def _classify_by_evidence(self, evidence: str) -> Tuple[str, float]:
        """Classify by code evidence (body patterns)."""
        if not evidence:
            return ("Unknown", 0)
        
        evidence_lower = evidence.lower()
        
        # Database patterns
        if any(x in evidence_lower for x in ['select', 'insert', 'update ', 'delete from']):
            return ("Repository", 75)
        
        # HTTP patterns
        if any(x in evidence_lower for x in ['request', 'response', 'http', 'json']):
            return ("Controller", 70)
        
        # Validation patterns
        if any(x in evidence_lower for x in ['raise', 'assert', 'error', 'exception']):
            return ("Validator", 65)
        
        return ("Unknown", 0)


# Module-level convenience function
_classifier = SymbolClassifier()

def classify_symbol(
    name: str,
    kind: str,
    file_path: str,
    line: int,
    **kwargs
) -> ClassifiedSymbol:
    """Convenience function to classify a symbol."""
    kind_enum = SymbolKind(kind) if isinstance(kind, str) else kind
    return _classifier.classify(name, kind_enum, file_path, line, **kwargs)


if __name__ == "__main__":
    # Test the classifier
    classifier = SymbolClassifier()
    
    tests = [
        ("UserRepository", SymbolKind.CLASS, [], []),
        ("get_user_by_id", SymbolKind.FUNCTION, [], []),
        ("UserEntity", SymbolKind.CLASS, [], ["BaseEntity"]),
        ("test_user_login", SymbolKind.FUNCTION, ["pytest.fixture"], []),
        ("__init__", SymbolKind.METHOD, [], []),
    ]
    
    print("Symbol Classification Tests:")
    for name, kind, decorators, bases in tests:
        result = classifier.classify(name, kind, "test.py", 1, decorators=decorators, base_classes=bases)
        print(f"  {name:25} → {result.role:15} ({result.confidence}%)")
