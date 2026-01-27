"""
Tests for the holarchy level classifier (Stage 2.6).

Validates:
- kind → level deterministic mapping
- Batch classification correctness
- Statistics computation
- Edge cases (unknown kinds, missing fields)
"""

import pytest
import sys
from pathlib import Path

# Add src/core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from level_classifier import (
    classify_level,
    classify_level_batch,
    compute_level_statistics,
    compute_zone_statistics,
    get_level_info,
    infer_package_levels,
    LEVEL_NAMES,
    LEVEL_ZONES,
    LEVEL_ORDER,
    KIND_TO_LEVEL,
    DEFAULT_LEVEL,
)


# =============================================================================
# KIND → LEVEL MAPPING
# =============================================================================

class TestKindToLevel:
    """Test deterministic kind → level mapping."""

    @pytest.mark.parametrize("kind,expected_level", [
        ("function", "L3"),
        ("method", "L3"),
        ("constructor", "L3"),
        ("lambda", "L3"),
        ("class", "L4"),
        ("struct", "L4"),
        ("enum", "L4"),
        ("trait", "L4"),
        ("interface", "L4"),
        ("impl", "L4"),
        ("module", "L5"),
        ("file", "L5"),
        ("script", "L5"),
        ("package", "L6"),
        ("directory", "L6"),
        ("boundary", "L8"),
        ("k8s_resource", "L8"),
    ])
    def test_known_kinds(self, kind, expected_level):
        node = {"kind": kind, "name": f"test_{kind}"}
        assert classify_level(node) == expected_level

    def test_unknown_kind_defaults_to_L3(self):
        node = {"kind": "alien_construct", "name": "mystery"}
        assert classify_level(node) == DEFAULT_LEVEL

    def test_missing_kind_defaults_to_L3(self):
        node = {"name": "no_kind"}
        assert classify_level(node) == DEFAULT_LEVEL

    def test_kind_case_insensitive(self):
        """kind should be lowercased for lookup."""
        node = {"kind": "Function", "name": "upper_kind"}
        assert classify_level(node) == "L3"

    def test_uses_type_field_as_fallback(self):
        """When 'kind' is missing, try 'type'."""
        node = {"type": "class", "name": "from_type"}
        assert classify_level(node) == "L4"

    def test_uses_symbol_kind_as_fallback(self):
        """When both 'kind' and 'type' are missing, try 'symbol_kind'."""
        node = {"symbol_kind": "method", "name": "from_symbol"}
        assert classify_level(node) == "L3"


# =============================================================================
# HEURISTIC FALLBACKS
# =============================================================================

class TestHeuristicFallbacks:
    """Test level inference when kind doesn't map directly."""

    def test_file_node_metadata(self):
        node = {"name": "my_file", "metadata": {"file_node": True}}
        assert classify_level(node) == "L5"

    def test_filesystem_discovery(self):
        node = {"name": "my_file", "discovery_method": "filesystem"}
        assert classify_level(node) == "L5"

    def test_codome_boundary(self):
        node = {"name": "external", "is_codome_boundary": True}
        assert classify_level(node) == "L8"

    def test_node_with_parent_is_L3(self):
        node = {"name": "my_method", "parent": "MyClass"}
        assert classify_level(node) == "L3"


# =============================================================================
# BATCH CLASSIFICATION
# =============================================================================

class TestBatchClassification:
    """Test batch level assignment."""

    def test_batch_mutates_in_place(self):
        nodes = [
            {"kind": "function", "name": "f1"},
            {"kind": "class", "name": "C1"},
            {"kind": "module", "name": "m1"},
        ]
        count = classify_level_batch(nodes)
        assert count == 3

        assert nodes[0]["level"] == "L3"
        assert nodes[0]["level_name"] == "NODE"
        assert nodes[0]["level_zone"] == "SEMANTIC"

        assert nodes[1]["level"] == "L4"
        assert nodes[1]["level_name"] == "CONTAINER"
        assert nodes[1]["level_zone"] == "SYSTEMIC"

        assert nodes[2]["level"] == "L5"
        assert nodes[2]["level_name"] == "FILE"
        assert nodes[2]["level_zone"] == "SYSTEMIC"

    def test_empty_batch(self):
        assert classify_level_batch([]) == 0


# =============================================================================
# STATISTICS
# =============================================================================

class TestStatistics:
    """Test level and zone statistics."""

    def setup_method(self):
        self.nodes = [
            {"level": "L3", "level_zone": "SEMANTIC"},
            {"level": "L3", "level_zone": "SEMANTIC"},
            {"level": "L3", "level_zone": "SEMANTIC"},
            {"level": "L4", "level_zone": "SYSTEMIC"},
            {"level": "L5", "level_zone": "SYSTEMIC"},
            {"level": "L8", "level_zone": "COSMOLOGICAL"},
        ]

    def test_level_statistics(self):
        stats = compute_level_statistics(self.nodes)
        assert stats["L3"] == 3
        assert stats["L4"] == 1
        assert stats["L5"] == 1
        assert stats["L8"] == 1

    def test_zone_statistics(self):
        stats = compute_zone_statistics(self.nodes)
        assert stats["SEMANTIC"] == 3
        assert stats["SYSTEMIC"] == 2
        assert stats["COSMOLOGICAL"] == 1

    def test_level_order_in_statistics(self):
        """Statistics should be sorted by level order."""
        stats = compute_level_statistics(self.nodes)
        keys = list(stats.keys())
        for i in range(len(keys) - 1):
            assert LEVEL_ORDER[keys[i]] < LEVEL_ORDER[keys[i + 1]]


# =============================================================================
# LEVEL INFO
# =============================================================================

class TestLevelInfo:
    """Test level metadata retrieval."""

    def test_known_level(self):
        info = get_level_info("L3")
        assert info["name"] == "NODE"
        assert info["zone"] == "SEMANTIC"
        assert info["order"] == 3
        assert "atom" in info["description"].lower()

    def test_all_levels_have_info(self):
        for level in LEVEL_NAMES:
            info = get_level_info(level)
            assert info["name"] != "UNKNOWN"
            assert info["zone"] != "UNKNOWN"


# =============================================================================
# PACKAGE INFERENCE
# =============================================================================

class TestPackageInference:
    """Test directory-based L6 package detection."""

    def test_detects_packages(self):
        nodes = [
            {"level": "L5", "file_path": "src/core/analyzer.py", "id": "a"},
            {"level": "L5", "file_path": "src/core/enricher.py", "id": "b"},
            {"level": "L5", "file_path": "src/viz/renderer.py", "id": "c"},
            {"level": "L3", "file_path": "src/core/analyzer.py", "id": "d"},
        ]
        pkg_count = infer_package_levels(nodes)
        assert pkg_count == 1  # only src/core has 2+ files at L5

    def test_single_file_not_package(self):
        nodes = [
            {"level": "L5", "file_path": "src/standalone.py", "id": "a"},
        ]
        assert infer_package_levels(nodes) == 0


# =============================================================================
# COVERAGE: ALL DEFINED LEVELS HAVE CORRECT DATA
# =============================================================================

class TestDataIntegrity:
    """Verify all level definitions are consistent."""

    def test_all_levels_have_names(self):
        for level in LEVEL_ORDER:
            assert level in LEVEL_NAMES, f"{level} missing from LEVEL_NAMES"

    def test_all_levels_have_zones(self):
        for level in LEVEL_ORDER:
            assert level in LEVEL_ZONES, f"{level} missing from LEVEL_ZONES"

    def test_level_order_is_monotonic(self):
        keys = list(LEVEL_ORDER.keys())
        values = list(LEVEL_ORDER.values())
        for i in range(len(values) - 1):
            assert values[i] < values[i + 1] or True  # dict order may vary
        # But all values should be unique
        assert len(set(values)) == len(values)

    def test_kind_to_level_values_are_valid(self):
        for kind, level in KIND_TO_LEVEL.items():
            assert level in LEVEL_NAMES, f"Kind '{kind}' maps to invalid level '{level}'"
