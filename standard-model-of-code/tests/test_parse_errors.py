"""Tests for ERROR/MISSING node detection."""
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from tree_sitter_engine import count_parse_errors

try:
    import tree_sitter
    import tree_sitter_python
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False


@pytest.mark.skipif(not HAS_TREE_SITTER, reason="tree-sitter not installed")
class TestParseErrors:
    """Test suite for parse error detection."""

    def _parse_python(self, code: str):
        """Helper to parse Python code using tree-sitter."""
        parser = tree_sitter.Parser()
        parser.language = tree_sitter.Language(tree_sitter_python.language())
        return parser.parse(bytes(code, 'utf8'))

    def test_valid_code_no_errors(self):
        """Valid Python code should have zero parse errors."""
        tree = self._parse_python("def foo(): pass")
        result = count_parse_errors(tree)
        assert result['error_count'] == 0, "Valid code should have no ERROR nodes"
        assert result['missing_count'] == 0, "Valid code should have no MISSING nodes"
        assert result['error_locations'] == []
        assert result['missing_locations'] == []

    def test_valid_class_no_errors(self):
        """Valid class definition should have zero parse errors."""
        code = '''
class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b
'''
        tree = self._parse_python(code)
        result = count_parse_errors(tree)
        assert result['error_count'] == 0
        assert result['missing_count'] == 0

    def test_missing_closing_paren_detected(self):
        """Missing closing parenthesis should trigger ERROR or MISSING."""
        tree = self._parse_python("def foo( pass")
        result = count_parse_errors(tree)
        # Should have some parse issue
        total = result['error_count'] + result['missing_count']
        assert total > 0, "Missing closing paren should create ERROR or MISSING nodes"

    def test_missing_colon_detected(self):
        """Missing colon in function definition should be detected."""
        tree = self._parse_python("def foo() pass")
        result = count_parse_errors(tree)
        total = result['error_count'] + result['missing_count']
        assert total > 0, "Missing colon should create ERROR or MISSING nodes"

    def test_syntax_error_line_tracking(self):
        """ERROR nodes should have correct line information."""
        code = "def foo(\n    x\n    y\n): pass"
        tree = self._parse_python(code)
        result = count_parse_errors(tree)

        # If errors were found, verify location structure
        if result['error_locations']:
            error = result['error_locations'][0]
            assert 'start_line' in error
            assert 'end_line' in error
            assert 'start_col' in error
            assert 'end_col' in error
            assert error['start_line'] >= 1
            assert error['end_line'] >= error['start_line']

    def test_missing_node_tracking(self):
        """MISSING nodes should be tracked with expected type and position."""
        tree = self._parse_python("def foo(")
        result = count_parse_errors(tree)

        # If missing nodes were found, verify structure
        if result['missing_locations']:
            missing = result['missing_locations'][0]
            assert 'expected' in missing
            assert 'line' in missing
            assert 'col' in missing
            assert missing['line'] >= 1
            assert missing['col'] >= 0

    def test_multiple_errors_counted(self):
        """Multiple syntax errors should all be counted."""
        code = """
def foo(
def bar(
def baz(
"""
        tree = self._parse_python(code)
        result = count_parse_errors(tree)
        # Should detect multiple issues
        assert result['error_count'] + result['missing_count'] > 0

    def test_result_dict_structure(self):
        """Result should always have required keys."""
        tree = self._parse_python("x = 1")
        result = count_parse_errors(tree)

        assert isinstance(result, dict)
        assert 'error_count' in result
        assert 'missing_count' in result
        assert 'error_locations' in result
        assert 'missing_locations' in result

        assert isinstance(result['error_count'], int)
        assert isinstance(result['missing_count'], int)
        assert isinstance(result['error_locations'], list)
        assert isinstance(result['missing_locations'], list)

    def test_unmatched_brackets(self):
        """Unmatched brackets should trigger ERROR or MISSING."""
        tree = self._parse_python("x = [1, 2, 3")
        result = count_parse_errors(tree)
        total = result['error_count'] + result['missing_count']
        assert total > 0, "Unmatched bracket should create ERROR or MISSING nodes"

    def test_indentation_error_pattern(self):
        """Indentation issues may trigger ERROR nodes."""
        code = """
def foo():
    x = 1
  y = 2
"""
        tree = self._parse_python(code)
        result = count_parse_errors(tree)
        # Indentation errors in Python may or may not create ERROR nodes
        # Just verify the function handles it without crashing
        assert 'error_count' in result
        assert isinstance(result['error_count'], int)

    def test_empty_code_no_errors(self):
        """Empty or whitespace-only code should have no errors."""
        tree = self._parse_python("")
        result = count_parse_errors(tree)
        assert result['error_count'] == 0
        assert result['missing_count'] == 0

    def test_comments_no_errors(self):
        """Comments should not trigger parse errors."""
        code = """
# This is a comment
def foo():
    # Comment in function
    return 42  # Inline comment
"""
        tree = self._parse_python(code)
        result = count_parse_errors(tree)
        assert result['error_count'] == 0
        assert result['missing_count'] == 0
