"""
Pattern Registry

Centralized storage for all role detection patterns.
Loads patterns from schema/learned/patterns.json - the ONLY place to edit patterns.
"""
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
import json
try:
    from core.registry.role_registry import get_role_registry
except ImportError:
    try:
        from registry.role_registry import get_role_registry
    except ImportError:
        def get_role_registry(): return None


@dataclass
class RolePattern:
    """A pattern that maps to a semantic role."""
    pattern: str
    role: str
    confidence: float
    pattern_type: str  # prefix, suffix, contains, exact
    language: str = "universal"  # universal, python, java, etc.
    description: str = ""


# Path to canonical patterns file
CANONICAL_PATTERNS_PATH = Path(__file__).parent.parent.parent / "canonical" / "learned" / "patterns.json"


class PatternRegistry:
    """
    Registry for all role detection patterns.

    LOADS FROM: schema/learned/patterns.json
    EDIT PATTERNS THERE, not in this code.
    """

    def __init__(self):
        self._prefix_patterns: Dict[str, Tuple[str, float]] = {}
        self._suffix_patterns: Dict[str, Tuple[str, float]] = {}
        self._path_patterns: Dict[str, Tuple[str, float]] = {}
        self._dunder_patterns: Dict[str, Tuple[str, float]] = {}
        self._decorator_patterns: Dict[str, str] = {}
        self._inheritance_patterns: Dict[str, str] = {}

        # Try to load from canonical file first
        if CANONICAL_PATTERNS_PATH.exists():
            self._load_from_canonical()
        else:
            self._load_default_patterns()

        self.role_registry = get_role_registry()

    def _canonicalize(self, role: str) -> str:
        """Ensure role is canonical."""
        if self.role_registry:
            return self.role_registry.get_canonical(role)
        return role

    def _load_from_canonical(self):
        """Load patterns from schema/learned/patterns.json."""
        with open(CANONICAL_PATTERNS_PATH) as f:
            data = json.load(f)

        # Load prefix patterns
        for pattern, info in data.get("prefix_patterns", {}).items():
            role = info.get("role", "Unknown")
            confidence = info.get("confidence", 75)
            self._prefix_patterns[pattern] = (role, confidence)

        # Load suffix patterns
        for pattern, info in data.get("suffix_patterns", {}).items():
            role = info.get("role", "Unknown")
            confidence = info.get("confidence", 75)
            self._suffix_patterns[pattern] = (role, confidence)

        # Load path patterns
        for pattern, info in data.get("path_patterns", {}).items():
            role = info.get("role", "Unknown")
            confidence = info.get("confidence", 75)
            self._path_patterns[pattern] = (role, confidence)

        # Load parameter type patterns (STRUCTURAL ANCHORS - Go framework types)
        self._param_type_patterns: Dict[str, Tuple[str, float]] = {}
        for pattern, info in data.get("parameter_type_patterns", {}).items():
            role = info.get("role", "Unknown")
            confidence = info.get("confidence", 90)
            self._param_type_patterns[pattern] = (role, confidence)

        # Load import patterns (STRUCTURAL ANCHORS - JS/TS imports)
        self._import_patterns: Dict[str, Tuple[str, float]] = {}
        for pattern, info in data.get("import_patterns", {}).items():
            role = info.get("role", "Unknown")
            confidence = info.get("confidence", 85)
            self._import_patterns[pattern] = (role, confidence)

        # Still need to load dunder/decorator/inheritance from defaults
        self._load_dunder_patterns()
        self._load_decorator_patterns()
        self._load_inheritance_patterns()

    def _load_dunder_patterns(self):
        """Load Python dunder method patterns."""
        self._dunder_patterns = {
            '__init__': ('Lifecycle', 95),
            '__new__': ('Factory', 95),
            '__del__': ('Lifecycle', 95),
            '__str__': ('Utility', 90),
            '__repr__': ('Utility', 90),
            '__eq__': ('Specification', 90),
            '__hash__': ('Utility', 90),
            '__len__': ('Query', 90),
            '__iter__': ('Iterator', 90),
            '__next__': ('Iterator', 90),
            '__getitem__': ('Query', 90),
            '__setitem__': ('Command', 90),
            '__call__': ('Command', 90),
            '__enter__': ('Lifecycle', 90),
            '__exit__': ('Lifecycle', 90),
        }

    def _load_decorator_patterns(self):
        """Load decorator patterns."""
        self._decorator_patterns = {
            'staticmethod': 'Utility',
            'classmethod': 'Factory',
            'property': 'Query',
            'abstractmethod': 'Specification',
            'pytest.fixture': 'Fixture',
            'fixture': 'Fixture',
            'get': 'Controller',
            'post': 'Controller',
            'put': 'Controller',
            'delete': 'Controller',
            'route': 'Controller',
            'test': 'Test',
        }

    def _load_inheritance_patterns(self):
        """Load DDD inheritance patterns."""
        self._inheritance_patterns = {
            'Entity': 'Entity',
            'BaseEntity': 'Entity',
            'ValueObject': 'ValueObject',
            'AggregateRoot': 'AggregateRoot',
            'Repository': 'Repository',
            'BaseRepository': 'Repository',
            'Command': 'Command',
            'Query': 'Query',
            'BaseSettings': 'Configuration',
        }

    def _load_default_patterns(self):
        """Load all default patterns (fallback if JSON not found)."""
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
            'get_': ('Query', 95), # LEARNED: Boosted from 85
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
            'login': ('Command', 85),  # LEARNED: Tier 1 adjudication
            'insert_': ('Command', 85),
            'create_': ('Factory', 95),  # LEARNED: Boosted from 85
            'do_': ('Command', 80),
            'run_': ('Command', 80),
            'execute_': ('Service', 60),
            'process_': ('Service', 60),

            # Factory patterns
            'build_': ('Factory', 85),
            'make_': ('Factory', 90),     # LEARNED
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
            'watch_': ('Observer', 80),  # INFERRED (Tier 2)
            '_should_': ('Specification', 85),  # INFERRED (Tier 3)

            # Mapper patterns
            'convert_': ('Transformer', 90), # LEARNED (was Mapper)
            'transform_': ('Transformer', 90), # LEARNED
            'to_': ('Transformer', 85),
            'as_': ('Transformer', 80),
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
            'Mixin': ('Adapter', 85),  # INFERRED (Tier 2)
            'Config': ('Configuration', 90),  # INFERRED (Tier 2)
            'Configuration': ('Configuration', 90),

            # Testing patterns (Tier 2)
            'Mock': ('TestDouble', 95),  # INFERRED
            'Mocker': ('TestDouble', 95),  # INFERRED
            'Stub': ('TestDouble', 90),  # INFERRED
            'Fake': ('TestDouble', 90),

            # DDD patterns (Tier 2)
            'Specifier': ('Specification', 80),  # INFERRED

            # Data patterns cont'd
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
        # Contains patterns (Legacy Heuristic capability)
        self._contains_patterns = {
            # Database/DB
            'database': ('Repository', 75),
            'db': ('Repository', 75),
            'sql': ('Repository', 75),
            'query': ('Repository', 75),
            'cursor': ('Repository', 75),
            'connection': ('Repository', 75),
            'pool': ('Repository', 75),

            # Auth
            'auth': ('Policy', 75),
            'permission': ('Policy', 75),
            'access': ('Policy', 75),

            # Rendering/UI
            'render': ('Utility', 75),
            'template': ('Factory', 75),
            'view': ('Controller', 75),
            'page': ('Controller', 75),
            'widget': ('Controller', 75),
            'ui': ('Controller', 75),

            # Lifecycle
            'session': ('Service', 70),
            'context': ('Service', 70),
            'state': ('Service', 70),

            # Operations
            'compute': ('Service', 70),
            'calculate': ('Service', 70),
            'process': ('Service', 70),
            'handle': ('EventHandler', 75),
            'callback': ('EventHandler', 75),

            # Utilities
            'parse': ('Utility', 75),
            'format': ('Utility', 75),
            'util': ('Utility', 75),
            'helper': ('Utility', 75),
            'log': ('Utility', 75),
            'trace': ('Utility', 75),
            'debug': ('Utility', 75),

            # Network
            'api': ('Controller', 75),
            'url': ('Query', 70),
            'http': ('Adapter', 75),
            'client': ('Client', 75),
            'request': ('DTO', 70),
            'response': ('DTO', 70),

            # Concurrency
            'mutex': ('Service', 75),
            'lock': ('Service', 75),
            'async': ('Service', 70),
            'worker': ('Job', 75),
            'task': ('Job', 75),
            'job': ('Job', 75),
            'queue': ('Service', 75),

            # Data Mapping
            'json': ('Mapper', 75),
            'xml': ('Mapper', 75),
            'csv': ('Mapper', 75),
            'map': ('Mapper', 70),
            'transform': ('Mapper', 75),
            'convert': ('Mapper', 75),
            'serialize': ('Mapper', 75),

            # Error Handling
            'error': ('Exception', 75),
            'fail': ('Exception', 75),
            'exception': ('Exception', 75),

            # File I/O
            'file': ('Adapter', 70),
            'io': ('Adapter', 70),
            'stream': ('Iterator', 75),

            # Go-specific patterns
            'goroutine': ('Service', 80),
            'channel': ('Service', 80),
            'chan': ('Service', 75),
            'defer': ('Lifecycle', 75),
            'context': ('Service', 80),
            'waitgroup': ('Service', 80),
            'wg': ('Service', 70),
            'grpc': ('Controller', 85),
            'proto': ('DTO', 80),
            'gin': ('Controller', 85),
            'echo': ('Controller', 85),
            'fiber': ('Controller', 85),
            'chi': ('Controller', 85),
            'mux': ('Controller', 80),
            'handler': ('EventHandler', 85),
            'middleware': ('Service', 85),
        }

        # Load contains patterns from JSON if available
        if CANONICAL_PATTERNS_PATH.exists():
            with open(CANONICAL_PATTERNS_PATH) as f:
                data = json.load(f)
                for pattern, info in data.get("contains_patterns", {}).items():
                    role = info.get("role", "Unknown")
                    confidence = info.get("confidence", 75)
                    self._contains_patterns[pattern] = (role, confidence)

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

    def get_contains_patterns(self) -> Dict[str, Tuple[str, float]]:
        """Get all contains patterns."""
        return self._contains_patterns.copy()

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
        for _, (role, _) in self._contains_patterns.items():
            roles.add(role)
        for _, (role, _) in self._dunder_patterns.items():
            roles.add(role)
        for _, role in self._decorator_patterns.items():
            roles.add(role)
        for _, role in self._inheritance_patterns.items():
            roles.add(role)
        return roles

    def classify_by_prefix(self, name: str) -> Tuple[str, float]:
        """Classify a name by prefix patterns.

        Uses camelCase/snake_case boundary detection to avoid false positives.
        E.g., 'use' should match 'useEffect' but NOT 'UserService'.
        """
        short_name = name.split('.')[-1] if '.' in name else name
        short_lower = short_name.lower()

        # Sort patterns by length (longest first) to match most specific
        sorted_patterns = sorted(self._prefix_patterns.items(),
                                  key=lambda x: len(x[0]), reverse=True)

        for prefix, (role, conf) in sorted_patterns:
            prefix_lower = prefix.lower()
            prefix_len = len(prefix)

            # Check if name starts with prefix (case-insensitive)
            if not short_lower.startswith(prefix_lower):
                continue

            # If exact match, it's valid
            if len(short_name) == prefix_len:
                return (self._canonicalize(role), conf)

            # Get the character after the prefix
            next_char = short_name[prefix_len]

            # Check for valid word boundary:
            # 1. snake_case: prefix ends with _ (e.g., 'get_' matches 'get_user')
            # 2. camelCase: next char is uppercase (e.g., 'use' matches 'useEffect')
            # 3. Underscore separator (e.g., 'test' matches 'test_user')

            if prefix.endswith('_'):
                # snake_case patterns like 'get_' - just need prefix match
                return (self._canonicalize(role), conf)
            elif next_char.isupper():
                # camelCase: 'useEffect' matches 'use' + 'E'
                # But 'UserService' should NOT match 'use' because 'u' != 'U'
                # Check case-sensitive prefix match for camelCase
                if short_name.startswith(prefix):
                    return (self._canonicalize(role), conf)
            elif next_char == '_':
                # 'test_user' matches 'test' + '_'
                if short_name[:prefix_len].lower() == prefix_lower:
                    return (self._canonicalize(role), conf - 5)  # Slightly lower confidence

        return ('Unknown', 0)

    def classify_by_suffix(self, name: str) -> Tuple[str, float]:
        """Classify a name by suffix patterns."""
        short_name = name.split('.')[-1] if '.' in name else name
        short_lower = short_name.lower()

        for suffix, (role, conf) in self._suffix_patterns.items():
            if short_name.endswith(suffix) or short_lower.endswith(suffix.lower()):
                return (self._canonicalize(role), conf)

        return ('Unknown', 0)

    def classify_by_contains(self, name: str) -> Tuple[str, float]:
        """Classify by substring patterns (Legacy Heuristic)."""
        short_name = name.split('.')[-1] if '.' in name else name
        short_lower = short_name.lower()

        best_match = ('Unknown', 0)

        for pattern, (role, conf) in self._contains_patterns.items():
            if pattern in short_lower:
                if conf > best_match[1]:
                    best_match = (self._canonicalize(role), conf)

        return best_match

    def classify_by_dunder(self, name: str) -> Tuple[str, float]:
        """Classify a dunder method."""
        short_name = name.split('.')[-1] if '.' in name else name

        if short_name in self._dunder_patterns:
            role, conf = self._dunder_patterns[short_name]
            return (self._canonicalize(role), conf)

        return ('Unknown', 0)

    # =========================================================================
    # STRUCTURAL ANCHOR METHODS (High Confidence)
    # These are "pseudo-decorators" - structural signals that strongly indicate role
    # =========================================================================

    def classify_by_param_type(self, param_types: List[str]) -> Tuple[str, float]:
        """Classify by function parameter types (Go framework anchors).

        Example: gin.Context → Controller (95% confidence)
        """
        if not hasattr(self, '_param_type_patterns'):
            return ('Unknown', 0)

        for param_type in param_types:
            # Normalize: remove leading * for pointers
            normalized = param_type.lstrip('*').strip()

            # Try exact match first
            if normalized in self._param_type_patterns:
                role, conf = self._param_type_patterns[normalized]
                return (self._canonicalize(role), conf)

            # Try partial match (e.g., "c *gin.Context" contains "gin.Context")
            for pattern, (role, conf) in self._param_type_patterns.items():
                if pattern in param_type:
                    return (self._canonicalize(role), conf)

        return ('Unknown', 0)

    def classify_by_import(self, imports: List[str]) -> Tuple[str, float]:
        """Classify by imports (JS/TS library anchors).

        Example: 'react' import → UIComponent (95% confidence)
        """
        if not hasattr(self, '_import_patterns'):
            return ('Unknown', 0)

        best_match = ('Unknown', 0)

        for imp in imports:
            # Extract package name from import path
            package = imp.split('/')[-1] if '/' in imp else imp
            package = package.split('/')[0]  # Handle scoped packages like @prisma/client

            # Check full import
            if imp in self._import_patterns:
                role, conf = self._import_patterns[imp]
                if conf > best_match[1]:
                    best_match = (role, conf)

            # Check package name
            elif package in self._import_patterns:
                role, conf = self._import_patterns[package]
                if conf > best_match[1]:
                    best_match = (role, conf)

        return best_match

    def classify_by_path(self, file_path: str) -> Tuple[str, float]:
        """Classify by file path patterns (universal directory anchors).

        Example: 'src/controllers/user.go' → Controller (90% confidence)
        """
        normalized = file_path.replace('\\', '/').lower()

        best_match = ('Unknown', 0)

        for pattern, (role, conf) in self._path_patterns.items():
            if pattern.lower() in normalized:
                if conf > best_match[1]:
                    best_match = (role, conf)

        return best_match


# Singleton instance
_pattern_registry = None

def get_pattern_registry() -> PatternRegistry:
    """Get the singleton pattern registry."""
    global _pattern_registry
    if _pattern_registry is None:
        _pattern_registry = PatternRegistry()
    return _pattern_registry


if __name__ == "__main__":
    repo = get_pattern_registry()

    print("Pattern Registry Summary")
    print("=" * 50)
    print(f"Prefix patterns: {len(repo.get_prefix_patterns())}")
    print(f"Suffix patterns: {len(repo.get_suffix_patterns())}")
    print(f"Contains patterns: {len(repo.get_contains_patterns())}")
    print(f"Dunder patterns: {len(repo.get_dunder_patterns())}")
    print(f"Decorator patterns: {len(repo.get_decorator_patterns())}")
    print(f"Inheritance patterns: {len(repo.get_inheritance_patterns())}")
    print(f"\nTotal unique roles: {len(repo.get_all_roles())}")
    print(f"Roles: {sorted(repo.get_all_roles())}")
