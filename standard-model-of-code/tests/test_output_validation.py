"""Tests for output_validation module."""

import pytest
from core.output_validation import validate_node, validate_edge


class TestValidateNode:
    """Tests for validate_node function."""

    def test_valid_node(self):
        """Valid node should return no warnings."""
        node = {
            "id": "node_001",
            "name": "my_function",
            "role": "Function",
            "file": "src/main.py",
            "line": 10
        }
        warnings = validate_node(node)
        assert warnings == []

    def test_missing_required_field(self):
        """Missing field should return warning."""
        node = {
            "id": "node_001",
            "name": "my_function",
            # Missing: role, file, line
        }
        warnings = validate_node(node)
        assert len(warnings) == 3
        assert any("role" in w for w in warnings)

    def test_null_field_value(self):
        """Null field value should return warning."""
        node = {
            "id": "node_001",
            "name": None,  # Null
            "role": "Function",
            "file": "src/main.py",
            "line": 10
        }
        warnings = validate_node(node)
        assert len(warnings) == 1
        assert "name" in warnings[0]


class TestValidateEdge:
    """Tests for validate_edge function."""

    def test_valid_edge(self):
        """Valid edge should return no warnings."""
        edge = {
            "source": "node_001",
            "target": "node_002",
            "type": "calls"
        }
        warnings = validate_edge(edge)
        assert warnings == []

    def test_missing_target(self):
        """Missing target should return warning."""
        edge = {
            "source": "node_001",
            "type": "calls"
        }
        warnings = validate_edge(edge)
        assert len(warnings) == 1
        assert "target" in warnings[0]

    def test_missing_all_fields(self):
        """Missing all fields should return 3 warnings."""
        edge = {}
        warnings = validate_edge(edge)
        assert len(warnings) == 3
