#!/usr/bin/env python3
"""
DIMENSION CLASSIFIER (Tree-sitter Native)
==========================================

Classifies the 3 missing octahedral dimensions from the Standard Model theory:
- D4 BOUNDARY: Internal/Input/I-O/Output
- D5 STATE: Stateful/Stateless
- D7 LIFECYCLE: Create/Use/Destroy

Primary: Tree-sitter AST queries (.scm files)
Fallback: Regex patterns (legacy, for languages without queries)

Usage:
    from dimension_classifier import DimensionClassifier

    classifier = DimensionClassifier()
    node['boundary'] = classifier.classify_boundary(node).value
    node['state'] = classifier.classify_state(node).value
    node['lifecycle'] = classifier.classify_lifecycle(node).value
"""

import re
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger(__name__)


class BoundaryType(Enum):
    """D4: Does this code cross I/O boundaries?"""
    INTERNAL = "internal"    # Pure computation, no I/O
    INPUT = "input"          # Reads from external (params, files, network, DB)
    OUTPUT = "output"        # Writes to external (returns, files, network, DB)
    IO = "io"                # Both reads and writes externally


class StateType(Enum):
    """D5: Does this code maintain state?"""
    STATELESS = "stateless"  # Pure function, no mutable state
    STATEFUL = "stateful"    # Has instance vars, globals, or closure state


class LifecyclePhase(Enum):
    """D7: What lifecycle phase is this code in?"""
    CREATE = "create"        # Initialization: __init__, factory, builder
    USE = "use"              # Normal operation: business logic
    DESTROY = "destroy"      # Cleanup: __del__, close, dispose, cleanup


class LayerType(Enum):
    """D2: Clean Architecture layer classification."""
    INTERFACE = "Interface"        # API endpoints, CLI, web handlers
    APPLICATION = "Application"    # Use cases, services, orchestration
    CORE = "Core"                  # Entities, value objects, domain logic
    INFRASTRUCTURE = "Infrastructure"  # Database, file I/O, external services
    TEST = "Test"                  # Test files, fixtures, mocks
    UNKNOWN = "Unknown"            # Cannot determine layer


# Role confidence thresholds for tree-sitter detection
ROLE_CONFIDENCE = {
    'repository': 90,
    'service': 85,
    'controller': 85,
    'factory': 80,
    'handler': 80,
    'validator': 85,
    'mapper': 75,
    'utility': 60,
    'asserter': 90,
    'guard': 80,
    'emitter': 75,
    'lifecycle': 85,
    'internal': 70,
    # New roles
    'query': 75,
    'processor': 80,
    'parser': 85,
    'accessor': 70,
    'adapter': 80,
    'builder': 80,
}


# =============================================================================
# TREE-SITTER DIMENSION CLASSIFIER
# =============================================================================

class TreeSitterDimensionClassifier:
    """
    Tree-sitter based dimension classifier.
    Uses .scm query files for accurate AST-based pattern detection.
    """

    def __init__(self):
        self._parser = None
        self._language = None
        self._queries: Dict[str, Any] = {}
        self._query_text: Dict[str, str] = {}
        self._initialized = False

    def _ensure_initialized(self, language: str = 'python') -> bool:
        """Lazy initialization of tree-sitter parser and queries."""
        if self._initialized and self._current_language == language:
            return True

        try:
            import tree_sitter

            # Get language module
            if language == 'python':
                import tree_sitter_python
                lang_obj = tree_sitter_python.language()
            elif language == 'javascript':
                import tree_sitter_javascript
                lang_obj = tree_sitter_javascript.language()
            elif language == 'typescript':
                import tree_sitter_typescript
                lang_obj = tree_sitter_typescript.language_typescript()
            else:
                logger.debug(f"No tree-sitter support for {language}")
                return False

            # Create parser
            self._parser = tree_sitter.Parser()
            self._language = tree_sitter.Language(lang_obj)
            self._parser.language = self._language
            self._current_language = language

            # Load queries
            self._load_queries(language)

            self._initialized = True
            return True

        except ImportError as e:
            logger.debug(f"Tree-sitter not available: {e}")
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize tree-sitter: {e}")
            return False

    def _load_queries(self, language: str):
        """Load .scm query files for dimension classification."""
        import tree_sitter

        try:
            from src.core.queries import get_query_loader
        except ImportError:
            try:
                from core.queries import get_query_loader
            except ImportError:
                from queries import get_query_loader

        loader = get_query_loader()

        for query_type in ['boundary', 'state', 'lifecycle', 'roles', 'layer']:
            query_text = loader.load_query(language, query_type)
            if query_text:
                try:
                    self._queries[query_type] = tree_sitter.Query(self._language, query_text)
                    self._query_text[query_type] = query_text
                    logger.debug(f"Loaded {query_type}.scm for {language}")
                except Exception as e:
                    logger.warning(f"Failed to compile {query_type} query: {e}")

    def classify_boundary(self, source: str, language: str = 'python') -> BoundaryType:
        """Classify boundary type using tree-sitter queries."""
        if not self._ensure_initialized(language):
            return None

        if 'boundary' not in self._queries:
            return None

        tree = self._parser.parse(bytes(source, 'utf8'))
        captures = self._run_query('boundary', tree.root_node)

        has_input = any('input' in tag for tag in captures)
        has_output = any('output' in tag for tag in captures)

        if has_input and has_output:
            return BoundaryType.IO
        elif has_input:
            return BoundaryType.INPUT
        elif has_output:
            return BoundaryType.OUTPUT
        else:
            return BoundaryType.INTERNAL

    def classify_state(self, source: str, language: str = 'python') -> StateType:
        """Classify state type using tree-sitter queries."""
        if not self._ensure_initialized(language):
            return None

        if 'state' not in self._queries:
            return None

        tree = self._parser.parse(bytes(source, 'utf8'))
        captures = self._run_query('state', tree.root_node)

        # Any state-related capture indicates stateful
        if captures:
            return StateType.STATEFUL
        return StateType.STATELESS

    def classify_lifecycle(self, source: str, name: str, language: str = 'python') -> LifecyclePhase:
        """Classify lifecycle phase using tree-sitter queries."""
        if not self._ensure_initialized(language):
            return None

        if 'lifecycle' not in self._queries:
            return None

        tree = self._parser.parse(bytes(source, 'utf8'))
        captures = self._run_query('lifecycle', tree.root_node)

        # Check capture tags for lifecycle phase
        has_create = any('create' in tag for tag in captures)
        has_destroy = any('destroy' in tag for tag in captures)

        if has_create:
            return LifecyclePhase.CREATE
        elif has_destroy:
            return LifecyclePhase.DESTROY
        else:
            return LifecyclePhase.USE

    def classify_layer(self, source: str, language: str = 'python') -> Optional[LayerType]:
        """Classify Clean Architecture layer using tree-sitter queries."""
        if not self._ensure_initialized(language):
            return None

        if 'layer' not in self._queries:
            return None

        tree = self._parser.parse(bytes(source, 'utf8'))
        captures = self._run_query('layer', tree.root_node)

        # Check capture tags for layer classification
        # Priority: Test > Interface > Infrastructure > Application > Core
        # (Test is special case, Interface/Infrastructure are boundaries)
        layer_priority = [
            ('test', LayerType.TEST),
            ('interface', LayerType.INTERFACE),
            ('infrastructure', LayerType.INFRASTRUCTURE),
            ('application', LayerType.APPLICATION),
            ('core', LayerType.CORE),
        ]

        for layer_key, layer_type in layer_priority:
            if any(f'layer.{layer_key}' in tag for tag in captures):
                return layer_type

        return None  # Let fallback handle unknown

    def classify_role(self, source: str, name: str = '', language: str = 'python') -> Optional[Dict[str, Any]]:
        """
        Classify D3_ROLE using tree-sitter roles.scm queries.

        Returns dict with:
            - role: canonical role name (Repository, Service, Controller, etc.)
            - confidence: detection confidence (0-100)
            - evidence: list of matching patterns

        Returns None if tree-sitter unavailable or no role detected.
        """
        if not self._ensure_initialized(language):
            return None

        if 'roles' not in self._queries:
            return None

        tree = self._parser.parse(bytes(source, 'utf8'))
        captures = self._run_query_with_details('roles', tree.root_node, source)

        if not captures:
            return None

        # Prioritize roles by specificity (more specific patterns win)
        role_priority = [
            'repository', 'service', 'controller', 'factory',
            'validator', 'handler', 'mapper', 'guard', 'emitter',
            'asserter', 'lifecycle', 'parser', 'processor', 'adapter',
            'builder', 'query', 'accessor', 'internal', 'utility'
        ]

        detected_roles = {}
        for tag, details in captures.items():
            # Extract role from tag like 'role.repository.class'
            if tag.startswith('role.'):
                parts = tag.split('.')
                if len(parts) >= 2:
                    role_type = parts[1]
                    if role_type not in detected_roles:
                        detected_roles[role_type] = {
                            'patterns': [],
                            'confidence': ROLE_CONFIDENCE.get(role_type, 50)
                        }
                    detected_roles[role_type]['patterns'].extend(details)

        if not detected_roles:
            return None

        # Select best role by priority
        best_role = None
        for role in role_priority:
            if role in detected_roles:
                best_role = role
                break

        if not best_role:
            best_role = list(detected_roles.keys())[0]

        # Map to canonical role names
        canonical_map = {
            'repository': 'Repository',
            'service': 'Service',
            'controller': 'Controller',
            'factory': 'Factory',
            'handler': 'Handler',
            'validator': 'Validator',
            'mapper': 'Mapper',
            'utility': 'Utility',
            'asserter': 'Asserter',
            'guard': 'Guard',
            'emitter': 'Emitter',
            'lifecycle': 'Lifecycle',
            'internal': 'Internal',
            # New roles
            'query': 'Query',
            'processor': 'Processor',
            'parser': 'Parser',
            'accessor': 'Accessor',
            'adapter': 'Adapter',
            'builder': 'Builder',
        }

        return {
            'role': canonical_map.get(best_role, best_role.title()),
            'confidence': detected_roles[best_role]['confidence'],
            'evidence': detected_roles[best_role]['patterns'][:3],  # Top 3 patterns
            'all_detected': list(detected_roles.keys()),
        }

    def _run_query_with_details(self, query_type: str, root_node, source: str) -> Dict[str, List[str]]:
        """Run a query and return captures with matched text."""
        import tree_sitter

        query = self._queries.get(query_type)
        if not query:
            return {}

        cursor = tree_sitter.QueryCursor(query)
        captures = cursor.captures(root_node)

        result = {}
        for tag, nodes in captures.items():
            if tag.startswith('_'):  # Skip internal captures
                continue
            if nodes:
                matched_texts = []
                for node in nodes[:5]:  # Limit to 5 matches per tag
                    text = source[node.start_byte:node.end_byte]
                    if len(text) > 50:
                        text = text[:50] + '...'
                    matched_texts.append(text)
                result[tag] = matched_texts
        return result

    def _run_query(self, query_type: str, root_node) -> Set[str]:
        """Run a query and return set of capture tag names."""
        import tree_sitter

        query = self._queries.get(query_type)
        if not query:
            return set()

        cursor = tree_sitter.QueryCursor(query)
        captures = cursor.captures(root_node)

        # Extract all capture tag names
        tags = set()
        for tag, nodes in captures.items():
            if nodes:  # Only add if there are actual matches
                tags.add(tag)
        return tags


# =============================================================================
# REGEX FALLBACK CLASSIFIER (Legacy)
# =============================================================================

class RegexDimensionClassifier:
    """
    Regex-based dimension classifier (fallback).
    Used when tree-sitter is not available or for unsupported languages.
    """

    # I/O detection patterns
    IO_PATTERNS = {
        'input': [
            r'\bopen\s*\(',           # file open
            r'\bread\s*\(',           # file read
            r'\.get\s*\(',            # dict/request get
            r'\brequests?\.',         # HTTP requests
            r'\.query\s*\(',          # DB query
            r'\.find\s*\(',           # DB find
            r'\.select\s*\(',         # SQL select
            r'\binput\s*\(',          # user input
            r'os\.environ',           # env vars
            r'\.recv\s*\(',           # socket recv
            r'json\.load\s*\(',       # JSON load
            r'yaml\.load\s*\(',       # YAML load
            r'\bsys\.argv',           # CLI args
        ],
        'output': [
            r'\.write\s*\(',          # file write
            r'\bprint\s*\(',          # stdout
            r'\.send\s*\(',           # socket/network send
            r'\.post\s*\(',           # HTTP post
            r'\.put\s*\(',            # HTTP put
            r'\.delete\s*\(',         # HTTP delete
            r'\.insert\s*\(',         # DB insert
            r'\.update\s*\(',         # DB update
            r'\.save\s*\(',           # persistence save
            r'\.commit\s*\(',         # transaction commit
            r'json\.dump\s*\(',       # JSON dump
            r'logging\.',             # logging calls
        ],
    }

    # State detection patterns
    STATE_PATTERNS = [
        r'self\.\w+\s*=',             # instance variable assignment
        r'cls\.\w+\s*=',              # class variable assignment
        r'\bglobal\s+\w+',            # global declaration
        r'nonlocal\s+\w+',            # nonlocal (closure)
    ]

    # Lifecycle phase detection
    LIFECYCLE_PATTERNS = {
        'create': [
            r'^__init__$',            # Python constructor
            r'^__new__$',             # Python allocator
            r'^create',               # create_x
            r'^build',                # build_x
            r'^make',                 # make_x
            r'^init',                 # init_x
            r'^setup',                # setup_x
            r'^construct',            # construct_x
            r'Factory$',              # xFactory class
            r'Builder$',              # xBuilder class
        ],
        'destroy': [
            r'^__del__$',             # Python destructor
            r'^__exit__$',            # Context manager exit
            r'^close$',               # close()
            r'^cleanup$',             # cleanup()
            r'^dispose$',             # dispose()
            r'^teardown',             # teardown_x
            r'^destroy',              # destroy_x
            r'^shutdown',             # shutdown_x
            r'^release',              # release_x
            r'^clear$',               # clear()
        ],
    }

    # Layer detection patterns (body-based)
    LAYER_PATTERNS = {
        'infrastructure': [
            r'\.execute\s*\(',        # DB execute
            r'\.cursor\s*\(',         # DB cursor
            r'sqlalchemy\.',          # SQLAlchemy ORM
            r'\.commit\s*\(',         # Transaction commit
            r'redis\.',               # Redis cache
            r'requests\.',            # HTTP requests
            r'httpx\.',               # HTTP client
            r'aiohttp\.',             # Async HTTP
            r'boto3\.',               # AWS SDK
            r's3\.put_object',        # S3 upload
            r'\.query\s*\(',          # DB query
            r'Repository',            # Repository pattern
        ],
        'interface': [
            r'@app\.(?:get|post|put|delete|patch)',   # Flask/FastAPI routes
            r'@router\.(?:get|post|put|delete|patch)', # FastAPI router
            r'@click\.',              # Click CLI
            r'@typer\.',              # Typer CLI
            r'APIView',               # Django REST
            r'ViewSet',               # Django ViewSet
            r'Controller',            # Controller pattern
        ],
        'application': [
            r'Service',               # Service pattern
            r'UseCase',               # Use case pattern
            r'Interactor',            # Interactor pattern
            r'\.execute\(',           # Use case execute
            r'Orchestrator',          # Orchestrator
        ],
        'core': [
            r'BaseModel',             # Pydantic
            r'@dataclass',            # Dataclass
            r'Enum\)',                # Enum inheritance
            r'Entity',                # Entity pattern
            r'ValueObject',           # Value object
            r'DomainEvent',           # Domain event
        ],
        'test': [
            r'^test_',                # Test functions
            r'^Test',                 # Test classes
            r'@pytest\.fixture',      # Pytest fixtures
            r'unittest\.TestCase',    # Unittest
            r'mock\.',                # Mocking
            r'assert\s+',             # Assertions
        ],
    }

    # Layer detection patterns (name-based)
    LAYER_NAME_PATTERNS = {
        'infrastructure': [
            r'Repository$',
            r'Store$',
            r'DAO$',
            r'Adapter$',
            r'Gateway$',
            r'Client$',
        ],
        'interface': [
            r'Controller$',
            r'Handler$',
            r'View$',
            r'Endpoint$',
            r'Resource$',
            r'Router$',
        ],
        'application': [
            r'Service$',
            r'UseCase$',
            r'Interactor$',
            r'Application$',
            r'Orchestrator$',
        ],
        'core': [
            r'Entity$',
            r'Aggregate$',
            r'ValueObject$',
            r'Domain',
            r'Model$',
        ],
        'test': [
            r'^test_',
            r'^Test',
            r'_test$',
            r'Test$',
        ],
    }

    def __init__(self):
        # Compile regex patterns for performance
        self.input_regexes = [re.compile(p, re.IGNORECASE) for p in self.IO_PATTERNS['input']]
        self.output_regexes = [re.compile(p, re.IGNORECASE) for p in self.IO_PATTERNS['output']]
        self.state_regexes = [re.compile(p) for p in self.STATE_PATTERNS]
        self.create_regexes = [re.compile(p, re.IGNORECASE) for p in self.LIFECYCLE_PATTERNS['create']]
        self.destroy_regexes = [re.compile(p, re.IGNORECASE) for p in self.LIFECYCLE_PATTERNS['destroy']]

        # Compile layer patterns
        self.layer_body_regexes = {
            layer: [re.compile(p, re.IGNORECASE) for p in patterns]
            for layer, patterns in self.LAYER_PATTERNS.items()
        }
        self.layer_name_regexes = {
            layer: [re.compile(p) for p in patterns]
            for layer, patterns in self.LAYER_NAME_PATTERNS.items()
        }

    def classify_boundary(self, body: str, signature: str = '') -> BoundaryType:
        """Classify the I/O boundary type."""
        combined = f"{signature}\n{body}"

        has_input = any(r.search(combined) for r in self.input_regexes)
        has_output = any(r.search(combined) for r in self.output_regexes)

        if has_input and has_output:
            return BoundaryType.IO
        elif has_input:
            return BoundaryType.INPUT
        elif has_output:
            return BoundaryType.OUTPUT
        else:
            return BoundaryType.INTERNAL

    def classify_state(self, body: str, kind: str = 'function') -> StateType:
        """Classify whether code maintains state."""
        # Classes are inherently stateful
        if kind == 'class':
            return StateType.STATEFUL

        # Check for state patterns in body
        for regex in self.state_regexes:
            if regex.search(body):
                return StateType.STATEFUL

        # Methods that modify self are stateful
        if 'self.' in body and '=' in body:
            if re.search(r'self\.\w+\s*[+\-*/%]?=', body):
                return StateType.STATEFUL

        return StateType.STATELESS

    def classify_lifecycle(self, name: str) -> LifecyclePhase:
        """Classify the lifecycle phase."""
        # Check create patterns
        for regex in self.create_regexes:
            if regex.search(name):
                return LifecyclePhase.CREATE

        # Check destroy patterns
        for regex in self.destroy_regexes:
            if regex.search(name):
                return LifecyclePhase.DESTROY

        return LifecyclePhase.USE

    def classify_layer(self, body: str, name: str, file_path: str = '') -> LayerType:
        """Classify Clean Architecture layer using regex patterns."""
        # Priority order: Test > Interface > Infrastructure > Application > Core
        layer_priority = ['test', 'interface', 'infrastructure', 'application', 'core']

        # Check name-based patterns first (more reliable)
        for layer in layer_priority:
            for regex in self.layer_name_regexes.get(layer, []):
                if regex.search(name):
                    return LayerType[layer.upper()]

        # Check body-based patterns
        for layer in layer_priority:
            for regex in self.layer_body_regexes.get(layer, []):
                if regex.search(body):
                    return LayerType[layer.upper()]

        # Path-based fallback (original logic)
        path = file_path.lower()
        if '/test' in path or 'test_' in path or '_test.py' in path:
            return LayerType.TEST
        elif '/api/' in path or '/routes/' in path or '/views/' in path or '/handlers/' in path:
            return LayerType.INTERFACE
        elif '/infrastructure/' in path or '/repositories/' in path or '/adapters/' in path:
            return LayerType.INFRASTRUCTURE
        elif '/services/' in path or '/application/' in path or '/usecases/' in path:
            return LayerType.APPLICATION
        elif '/domain/' in path or '/entities/' in path or '/core/' in path or '/models/' in path:
            return LayerType.CORE

        return LayerType.UNKNOWN


# =============================================================================
# UNIFIED DIMENSION CLASSIFIER (Public API)
# =============================================================================

class DimensionClassifier:
    """
    Unified dimension classifier.
    Uses tree-sitter when available, falls back to regex.

    This maintains the original API while using tree-sitter under the hood.
    """

    def __init__(self):
        self._ts_classifier = TreeSitterDimensionClassifier()
        self._regex_classifier = RegexDimensionClassifier()
        self._use_tree_sitter = True  # Try tree-sitter first

    def _get_language(self, node: Dict[str, Any]) -> str:
        """Detect language from node or file path."""
        file_path = node.get('file_path', '')
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith(('.js', '.jsx')):
            return 'javascript'
        elif file_path.endswith(('.ts', '.tsx')):
            return 'typescript'
        return 'python'  # default

    def classify_boundary(self, node: Dict[str, Any]) -> BoundaryType:
        """
        Classify the I/O boundary type of a node.

        Args:
            node: Node dict with 'body_source', 'signature', 'file_path', etc.

        Returns:
            BoundaryType enum value
        """
        body = node.get('body_source', '') or node.get('body', '') or ''
        signature = node.get('signature', '') or ''

        # Try tree-sitter first
        if self._use_tree_sitter and body:
            language = self._get_language(node)
            result = self._ts_classifier.classify_boundary(body, language)
            if result is not None:
                return result

        # Fallback to regex
        return self._regex_classifier.classify_boundary(body, signature)

    def classify_state(self, node: Dict[str, Any]) -> StateType:
        """
        Classify whether a node maintains state.

        Args:
            node: Node dict with 'body_source', 'kind', 'file_path', etc.

        Returns:
            StateType enum value
        """
        body = node.get('body_source', '') or node.get('body', '') or ''
        kind = node.get('kind', 'function')

        # Try tree-sitter first
        if self._use_tree_sitter and body:
            language = self._get_language(node)
            result = self._ts_classifier.classify_state(body, language)
            if result is not None:
                return result

        # Fallback to regex
        return self._regex_classifier.classify_state(body, kind)

    def classify_lifecycle(self, node: Dict[str, Any]) -> LifecyclePhase:
        """
        Classify the lifecycle phase of a node.

        Args:
            node: Node dict with 'name', 'body_source', 'file_path', etc.

        Returns:
            LifecyclePhase enum value
        """
        name = node.get('name', '')
        body = node.get('body_source', '') or node.get('body', '') or ''

        # Try tree-sitter first (uses both name and body)
        if self._use_tree_sitter and body:
            language = self._get_language(node)
            result = self._ts_classifier.classify_lifecycle(body, name, language)
            if result is not None:
                return result

        # Fallback to regex (name-based only)
        return self._regex_classifier.classify_lifecycle(name)

    def classify_layer(self, node: Dict[str, Any]) -> LayerType:
        """
        Classify D2_LAYER using tree-sitter AST patterns.

        Args:
            node: Node dict with 'body_source', 'name', 'file_path', etc.

        Returns:
            LayerType enum value
        """
        body = node.get('body_source', '') or node.get('body', '') or ''
        name = node.get('name', '')
        file_path = node.get('file_path', '')

        # Try tree-sitter first
        if self._use_tree_sitter and body:
            language = self._get_language(node)
            result = self._ts_classifier.classify_layer(body, language)
            if result is not None:
                return result

        # Fallback to regex (uses body, name, and path)
        return self._regex_classifier.classify_layer(body, name, file_path)

    def classify_all(self, node: Dict[str, Any]) -> Dict[str, str]:
        """
        Classify D4_BOUNDARY, D5_STATE, D7_LIFECYCLE for a node.

        Returns:
            Dict with 'boundary', 'state', 'lifecycle' string values
        """
        return {
            'boundary': self.classify_boundary(node).value,
            'state': self.classify_state(node).value,
            'lifecycle': self.classify_lifecycle(node).value,
        }


def classify_all_dimensions(nodes: List[Dict[str, Any]]) -> int:
    """
    Classify all 3 missing dimensions for a list of nodes.
    Modifies nodes in-place.

    Args:
        nodes: List of node dicts

    Returns:
        Number of nodes classified
    """
    classifier = DimensionClassifier()
    count = 0

    for node in nodes:
        dims = classifier.classify_all(node)

        # Add to node
        node['boundary'] = dims['boundary']
        node['state'] = dims['state']
        node['lifecycle'] = dims['lifecycle']

        # Also add to dimensions sub-dict if it exists
        if 'dimensions' in node and isinstance(node['dimensions'], dict):
            node['dimensions']['boundary'] = dims['boundary']
            node['dimensions']['state'] = dims['state']
            node['dimensions']['lifecycle'] = dims['lifecycle']

        count += 1

    return count


if __name__ == "__main__":
    # Demo
    test_nodes = [
        {
            'name': '__init__',
            'kind': 'method',
            'body_source': 'self.data = []',
            'file_path': 'test.py'
        },
        {
            'name': 'process',
            'kind': 'function',
            'body_source': 'result = compute(x); print(result); return result',
            'file_path': 'test.py'
        },
        {
            'name': 'read_file',
            'kind': 'function',
            'body_source': 'with open(path) as f: return f.read()',
            'file_path': 'test.py'
        },
        {
            'name': 'cleanup',
            'kind': 'function',
            'body_source': 'self.conn.close()',
            'file_path': 'test.py'
        },
    ]

    classifier = DimensionClassifier()

    print("Dimension Classification Demo (Tree-sitter + Regex Fallback)")
    print("=" * 60)

    # Check if tree-sitter is available
    ts_available = classifier._ts_classifier._ensure_initialized('python')
    print(f"Tree-sitter available: {ts_available}")

    for node in test_nodes:
        dims = classifier.classify_all(node)
        print(f"\n{node['name']}:")
        print(f"  Boundary:  {dims['boundary']}")
        print(f"  State:     {dims['state']}")
        print(f"  Lifecycle: {dims['lifecycle']}")
