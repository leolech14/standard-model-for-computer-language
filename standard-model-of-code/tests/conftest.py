"""Pytest configuration and fixtures."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Optional


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
def hello_world():
    """Say hello."""
    print("Hello, World!")

class Calculator:
    """Simple calculator."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b
'''


@pytest.fixture
def sample_file(tmp_path, sample_python_code):
    """Create a sample Python file for testing."""
    file_path = tmp_path / "sample.py"
    file_path.write_text(sample_python_code)
    return file_path


# =============================================================================
# TREE-SITTER MOCKS
# =============================================================================

@pytest.fixture
def mock_tree_sitter_node():
    """Mock a tree-sitter Node object."""
    node = Mock()
    node.type = 'function_definition'
    node.start_point = (10, 0)
    node.end_point = (15, 1)
    node.start_byte = 150
    node.end_byte = 250
    node.text = b'def my_func(): pass'
    node.children = []
    node.parent = None
    node.is_named = True

    def child_by_field_name(field_name: str) -> Optional[Mock]:
        if field_name == 'name':
            name_node = Mock()
            name_node.text = b'my_func'
            name_node.type = 'identifier'
            return name_node
        elif field_name == 'parameters':
            params_node = Mock()
            params_node.children = []
            return params_node
        return None

    node.child_by_field_name = child_by_field_name
    return node


@pytest.fixture
def mock_tree_sitter_tree(mock_tree_sitter_node):
    """Mock a tree-sitter Tree object."""
    tree = Mock()
    tree.root_node = mock_tree_sitter_node
    return tree


@pytest.fixture
def mock_tree_sitter_parser(mock_tree_sitter_tree):
    """Mock tree-sitter Parser object."""
    parser = Mock()
    parser.language = None

    def parse(source_bytes: bytes):
        mock_tree_sitter_tree.root_node.text = source_bytes
        return mock_tree_sitter_tree

    parser.parse = parse
    return parser


@pytest.fixture
def mock_tree_sitter_query(mock_tree_sitter_node):
    """Mock tree-sitter Query object with captures."""
    query = Mock()

    def captures(node):
        return [
            (mock_tree_sitter_node, 'function.definition'),
        ]

    query.captures = captures
    return query


@pytest.fixture
def mock_tree_sitter_module(mock_tree_sitter_parser, mock_tree_sitter_query):
    """Patch entire tree_sitter module for isolated testing."""
    with patch.dict('sys.modules', {'tree_sitter': Mock()}):
        import sys
        ts_mock = sys.modules['tree_sitter']
        ts_mock.Parser = Mock(return_value=mock_tree_sitter_parser)
        ts_mock.Language = Mock()
        ts_mock.Query = Mock(return_value=mock_tree_sitter_query)
        yield ts_mock


# =============================================================================
# OLLAMA MOCKS
# =============================================================================

@pytest.fixture
def mock_ollama_response():
    """Mock successful ollama classification response."""
    return {
        "role": "Repository",
        "confidence": 0.95,
        "reasoning": "Mock classification for testing"
    }


@pytest.fixture
def mock_ollama_subprocess(mock_ollama_response):
    """Mock ollama subprocess calls."""
    result = Mock()
    result.returncode = 0
    result.stdout = json.dumps(mock_ollama_response)
    result.stderr = ""
    return result


@pytest.fixture
def mock_ollama_module(mock_ollama_subprocess):
    """Patch ollama-related subprocess calls."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = mock_ollama_subprocess
        yield mock_run


# =============================================================================
# NETWORK MOCKS
# =============================================================================

@pytest.fixture
def mock_http_response():
    """Mock HTTP response for URL checks."""
    response = Mock()
    response.status = 200
    response.read.return_value = b'{"status": "ok"}'
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=None)
    return response


@pytest.fixture
def mock_urlopen(mock_http_response):
    """Mock urllib.request.urlopen."""
    with patch('urllib.request.urlopen') as mock:
        mock.return_value = mock_http_response
        yield mock


# =============================================================================
# FILESYSTEM MOCKS
# =============================================================================

@pytest.fixture
def mock_large_codebase(tmp_path):
    """Create a mock codebase structure for testing."""
    # Create directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    # Create sample files
    (src_dir / "main.py").write_text("def main(): pass")
    (src_dir / "utils.py").write_text("def helper(): return 42")
    (tests_dir / "test_main.py").write_text("def test_main(): assert True")

    # Create README
    (tmp_path / "README.md").write_text("# Test Project")

    return tmp_path


# =============================================================================
# COMBINED FIXTURES
# =============================================================================

@pytest.fixture
def mock_all_external_deps(mock_tree_sitter_module, mock_ollama_module, mock_urlopen):
    """Mock all external dependencies for isolated unit testing."""
    return {
        'tree_sitter': mock_tree_sitter_module,
        'ollama': mock_ollama_module,
        'network': mock_urlopen,
    }
