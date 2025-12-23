"""
Pattern Repository

Centralized storage for all role detection patterns.
Single source of truth for pattern definitions across the codebase.
"""
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field


@dataclass 
class RolePattern:
    """A pattern that maps to a semantic role."""
    pattern: str
    role: str
    confidence: float
    pattern_type: str  # prefix, suffix, contains, exact
    language: str = "universal"  # universal, python, java, etc.
    description: str = ""


class PatternRepository:
    """
    Repository for all role detection patterns.
    
    Centralizes patterns that were previously scattered across:
    - auto_pattern_discovery.py
    - parser/symbol_classifier.py
    - tree_sitter_engine.py
    """
    
    def __init__(self):
        self._prefix_patterns: Dict[str, Tuple[str, float]] = {}
        self._suffix_patterns: Dict[str, Tuple[str, float]] = {}
        # New: Path patterns for context-aware classification
        self._path_patterns: Dict[str, Tuple[str, float]] = {
            '/test': ('Test', 95),
            '/tests': ('Test', 95),
            '/spec': ('Test', 90),
            '/scenarios': ('Test', 90),
            '/repository': ('Repository', 90),
            '/service': ('Service', 90),
            '/controller': ('Controller', 90),
            '/model': ('Entity', 85),
            '/entity': ('Entity', 85),
            '/util': ('Utility', 80),
            '/helper': ('Utility', 80),
        }
        self._dunder_patterns: Dict[str, Tuple[str, float]] = {}
        self._decorator_patterns: Dict[str, str] = {}
        self._inheritance_patterns: Dict[str, str] = {}
        
        self._load_default_patterns()
    
    def _load_default_patterns(self):
        """Load all default patterns."""
        
        # Prefix patterns (function names)
        self._prefix_patterns = {
            # Test patterns
            'test_': ('Test', 90),
            'test': ('Test', 85),  # Java: testUserLogin
            'should': ('Test', 85),  # BDD: shouldReturnUser
            'given': ('Test', 80),
            'when': ('Test', 80),
            'then': ('Test', 80),
            
            # Query patterns
            'get_': ('Query', 85),
            'fetch_': ('Query', 85),
            'find_': ('Query', 85),
            'load_': ('Query', 85),
            'read_': ('Query', 85),
            'search_': ('Query', 85),
            'query_': ('Query', 85),
            'list_': ('Query', 85),
            
            # Command patterns
            'set_': ('Command', 85),
            'update_': ('Command', 85),
            'delete_': ('Command', 85),
            'remove_': ('Command', 85),
            'add_': ('Command', 85),
            'save_': ('Command', 85),
            'insert_': ('Command', 85),
            'create_': ('Factory', 85),
            'do_': ('Command', 80),
            'run_': ('Command', 80),
            'execute_': ('Service', 60),  # Reduced from 85 (was UseCase/Service)
            'process_': ('Service', 60),  # Reduced from 80

            
            # Factory patterns
            'build_': ('Factory', 85),
            'make_': ('Factory', 85),
            'from_': ('Factory', 80),
            
            # Specification patterns
            'is_': ('Specification', 85),
            'has_': ('Specification', 85),
            'can_': ('Specification', 85),
            'should_': ('Specification', 85),
            'validate_': ('Validator', 85),
            'check_': ('Validator', 85),
            
            # Event patterns
            'handle_': ('EventHandler', 85),
            'on_': ('EventHandler', 85),
            
            # Mapper patterns
            'convert_': ('Mapper', 80),
            'transform_': ('Mapper', 80),
            'to_': ('Mapper', 80),
            'as_': ('Mapper', 75),
            'parse_': ('Utility', 80),
            'format_': ('Utility', 80),
            
            # Lifecycle patterns
            'init_': ('Lifecycle', 80),
            'setup_': ('Lifecycle', 80),
            'teardown_': ('Lifecycle', 80),
            'cleanup_': ('Lifecycle', 80),
            
            # Internal
            '_': ('Internal', 70),
            
            # Go/TypeScript specific
            'Test': ('Test', 85),  # Go: TestUserLogin
            'Benchmark': ('Test', 80),
            'Example': ('Test', 75),
            'describe': ('Test', 85),
            'it': ('Test', 85),
            'beforeEach': ('Fixture', 85),
            'afterEach': ('Fixture', 85),
        }
        
        # Suffix patterns (class names)
        self._suffix_patterns = {
            # Architecture roles
            'Service': ('Service', 90),
            'Repository': ('Repository', 90),
            'Controller': ('Controller', 90),
            'Handler': ('EventHandler', 85),
            'Listener': ('EventHandler', 85),
            
            # Creation patterns
            'Factory': ('Factory', 85),
            'Builder': ('Builder', 85),
            'Provider': ('Provider', 85),
            
            # Data patterns
            'Mapper': ('Mapper', 85),
            'Converter': ('Mapper', 80),
            'Transformer': ('Mapper', 80),
            'Serializer': ('Mapper', 80),
            'DTO': ('DTO', 85),
            'Entity': ('Entity', 85),
            
            # Validation patterns
            'Validator': ('Validator', 85),
            'Specification': ('Specification', 85),
            
            # Domain patterns
            'Command': ('Command', 85),
            'Query': ('Query', 85),
            'Event': ('DomainEvent', 85),
            'Policy': ('Policy', 85),
            
            # Infrastructure
            'Adapter': ('Adapter', 85),
            'Gateway': ('Gateway', 85),
            'Client': ('Client', 85),
            'Impl': ('RepositoryImpl', 80),
            
            # Configuration
            'Config': ('Configuration', 80),
            'Settings': ('Configuration', 80),
            'Options': ('Configuration', 75),
            
            # Testing
            'Test': ('Test', 85),
            'Mock': ('Fixture', 80),
            'Stub': ('Fixture', 80),
            'Fake': ('Fixture', 80),
            
            # Errors
            'Exception': ('Exception', 85),
            'Error': ('Exception', 80),
            
            # Utilities
            'Helper': ('Utility', 75),
            'Utils': ('Utility', 75),
            'Util': ('Utility', 75),
            'Manager': ('Service', 75),
            'Processor': ('Service', 75),
            'Middleware': ('Service', 80),
        }
        
        # Dunder methods (Python magic methods)
        self._dunder_patterns = {
            '__init__': ('Lifecycle', 95),
            '__new__': ('Factory', 95),
            '__del__': ('Lifecycle', 95),
            '__str__': ('Utility', 90),
            '__repr__': ('Utility', 90),
            '__eq__': ('Specification', 90),
            '__ne__': ('Specification', 90),
            '__lt__': ('Specification', 90),
            '__le__': ('Specification', 90),
            '__gt__': ('Specification', 90),
            '__ge__': ('Specification', 90),
            '__hash__': ('Utility', 90),
            '__bool__': ('Specification', 90),
            '__len__': ('Query', 90),
            '__iter__': ('Iterator', 90),
            '__next__': ('Iterator', 90),
            '__getitem__': ('Query', 90),
            '__setitem__': ('Command', 90),
            '__delitem__': ('Command', 90),
            '__contains__': ('Specification', 90),
            '__call__': ('Command', 90),
            '__enter__': ('Lifecycle', 90),
            '__exit__': ('Lifecycle', 90),
            '__getattr__': ('Query', 85),
            '__setattr__': ('Command', 85),
        }
        
        # Decorator patterns
        self._decorator_patterns = {
            # Python decorators
            'staticmethod': 'Utility',
            'classmethod': 'Factory',
            'property': 'Query',
            'abstractmethod': 'Specification',
            'pytest.fixture': 'Fixture',
            'fixture': 'Fixture',
            
            # Web framework decorators
            'get': 'Controller',
            'post': 'Controller',
            'put': 'Controller',
            'delete': 'Controller',
            'patch': 'Controller',
            'route': 'Controller',
            'api': 'Controller',
            'app.route': 'Controller',
            
            # Django
            'login_required': 'Controller',
            'permission_required': 'Policy',
            
            # Testing
            'test': 'Test',
            'pytest.mark': 'Test',
            'mock': 'Fixture',
            'patch': 'Fixture',
            
            # Java/Spring
            '@Service': 'Service',
            '@Repository': 'Repository',
            '@Controller': 'Controller',
            '@RestController': 'Controller',
            '@Component': 'Service',
            '@Test': 'Test',
            
            # NestJS/Angular
            '@Injectable': 'Service',
            '@Component': 'Controller',
            '@Pipe': 'Mapper',
            '@Directive': 'Service',
        }
        
        # DDD inheritance patterns (99% confidence)
        self._inheritance_patterns = {
            'BaseEntity': 'Entity',
            'Entity': 'Entity',
            'AbstractEntity': 'Entity',
            'ValueObject': 'ValueObject',
            'BaseValueObject': 'ValueObject',
            'AggregateRoot': 'AggregateRoot',
            'BaseAggregateRoot': 'AggregateRoot',
            'Repository': 'Repository',
            'BaseRepository': 'Repository',
            'AbstractRepository': 'Repository',
            'Command': 'Command',
            'BaseCommand': 'Command',
            'Query': 'Query',
            'BaseQuery': 'Query',
            'DomainService': 'DomainService',
            'ApplicationService': 'ApplicationService',
            'BaseSettings': 'Configuration',
            'Settings': 'Configuration',
        }
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    def get_path_patterns(self) -> Dict[str, Tuple[str, float]]:
        """Get all path patterns."""
        return self._path_patterns.copy()
    
    def get_prefix_patterns(self) -> Dict[str, Tuple[str, float]]:
        """Get all prefix patterns."""
        return self._prefix_patterns.copy()
    
    def get_suffix_patterns(self) -> Dict[str, Tuple[str, float]]:
        """Get all suffix patterns."""
        return self._suffix_patterns.copy()
    
    def get_dunder_patterns(self) -> Dict[str, Tuple[str, float]]:
        """Get all dunder method patterns."""
        return self._dunder_patterns.copy()
    
    def get_decorator_patterns(self) -> Dict[str, str]:
        """Get all decorator patterns."""
        return self._decorator_patterns.copy()
    
    def get_inheritance_patterns(self) -> Dict[str, str]:
        """Get all inheritance patterns."""
        return self._inheritance_patterns.copy()
    
    def get_all_roles(self) -> Set[str]:
        """Get all known role names."""
        roles = set()
        for _, (role, _) in self._prefix_patterns.items():
            roles.add(role)
        for _, (role, _) in self._suffix_patterns.items():
            roles.add(role)
        for _, (role, _) in self._dunder_patterns.items():
            roles.add(role)
        for _, role in self._decorator_patterns.items():
            roles.add(role)
        for _, role in self._inheritance_patterns.items():
            roles.add(role)
        return roles
    
    def classify_by_prefix(self, name: str) -> Tuple[str, float]:
        """Classify a name by prefix patterns."""
        name_lower = name.lower()
        short_name = name.split('.')[-1] if '.' in name else name
        short_lower = short_name.lower()
        
        for prefix, (role, conf) in self._prefix_patterns.items():
            # Check lowercase prefix match
            if short_lower.startswith(prefix.lower()):
                return (role, conf)
            # Check camelCase prefix (e.g., testUserLogin)
            if short_name.startswith(prefix) and len(short_name) > len(prefix):
                next_char = short_name[len(prefix)]
                if next_char.isupper() or next_char == '_':
                    return (role, conf - 5)  # Slightly lower confidence
        
        return ('Unknown', 0)
    
    def classify_by_suffix(self, name: str) -> Tuple[str, float]:
        """Classify a name by suffix patterns."""
        short_name = name.split('.')[-1] if '.' in name else name
        short_lower = short_name.lower()
        
        for suffix, (role, conf) in self._suffix_patterns.items():
            if short_name.endswith(suffix) or short_lower.endswith(suffix.lower()):
                return (role, conf)
        
        return ('Unknown', 0)
    
    def classify_by_dunder(self, name: str) -> Tuple[str, float]:
        """Classify a dunder method."""
        short_name = name.split('.')[-1] if '.' in name else name
        
        if short_name in self._dunder_patterns:
            return self._dunder_patterns[short_name]
        
        return ('Unknown', 0)


# Singleton instance
_pattern_repository = None

def get_pattern_repository() -> PatternRepository:
    """Get the singleton pattern repository."""
    global _pattern_repository
    if _pattern_repository is None:
        _pattern_repository = PatternRepository()
    return _pattern_repository


if __name__ == "__main__":
    repo = get_pattern_repository()
    
    print("Pattern Repository Summary")
    print("=" * 50)
    print(f"Prefix patterns: {len(repo.get_prefix_patterns())}")
    print(f"Suffix patterns: {len(repo.get_suffix_patterns())}")
    print(f"Dunder patterns: {len(repo.get_dunder_patterns())}")
    print(f"Decorator patterns: {len(repo.get_decorator_patterns())}")
    print(f"Inheritance patterns: {len(repo.get_inheritance_patterns())}")
    print(f"\nTotal unique roles: {len(repo.get_all_roles())}")
    print(f"Roles: {sorted(repo.get_all_roles())}")
