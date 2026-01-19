"""Tests for guardrails module."""

import pytest
from core.guardrails import Guardrails, ResourceLimits, ResourceLimitExceeded


class TestResourceLimits:
    """Tests for ResourceLimits dataclass."""

    def test_default_values(self):
        """Default limits should have expected values."""
        limits = ResourceLimits()
        assert limits.max_file_size_mb == 10.0
        assert limits.max_files == 10000
        assert limits.max_total_size_mb == 500.0
        assert limits.max_nodes == 100000
        assert limits.max_edges == 500000

    def test_custom_values(self):
        """Custom values should be applied."""
        limits = ResourceLimits(max_files=100, max_file_size_mb=5.0)
        assert limits.max_files == 100
        assert limits.max_file_size_mb == 5.0


class TestGuardrails:
    """Tests for Guardrails class."""

    def test_default_limits(self):
        """Default limits should be reasonable."""
        g = Guardrails()
        assert g.limits.max_file_size_mb == 10.0
        assert g.limits.max_files == 10000

    def test_custom_limits(self):
        """Custom limits should be applied."""
        limits = ResourceLimits(max_files=100, max_file_size_mb=5.0)
        g = Guardrails(limits)
        assert g.limits.max_files == 100
        assert g.limits.max_file_size_mb == 5.0

    def test_check_file_nonexistent(self, tmp_path):
        """Nonexistent file should return False."""
        g = Guardrails()
        result = g.check_file(str(tmp_path / "nonexistent.py"))
        assert result is False

    def test_check_file_within_limits(self, tmp_path):
        """File within limits should return True."""
        g = Guardrails()
        test_file = tmp_path / "small.py"
        test_file.write_text("x = 1")
        result = g.check_file(str(test_file))
        assert result is True

    def test_file_count_limit(self, tmp_path):
        """Should raise when file count exceeded."""
        limits = ResourceLimits(max_files=2)
        g = Guardrails(limits)

        for i in range(3):
            f = tmp_path / f"file{i}.py"
            f.write_text(f"x = {i}")

            if i < 2:
                assert g.check_file(str(f)) is True
            else:
                with pytest.raises(ResourceLimitExceeded):
                    g.check_file(str(f))

    def test_node_limit(self):
        """Should raise when node limit exceeded."""
        limits = ResourceLimits(max_nodes=100)
        g = Guardrails(limits)

        g.check_nodes(50)  # OK
        g.check_nodes(50)  # OK (total 100)

        with pytest.raises(ResourceLimitExceeded):
            g.check_nodes(1)  # Exceeds

    def test_edge_limit(self):
        """Should raise when edge limit exceeded."""
        limits = ResourceLimits(max_edges=100)
        g = Guardrails(limits)

        g.check_edges(100)  # OK

        with pytest.raises(ResourceLimitExceeded):
            g.check_edges(1)  # Exceeds

    def test_get_stats(self, tmp_path):
        """Stats should reflect current usage."""
        g = Guardrails()
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        g.check_file(str(test_file))
        g.check_nodes(10)
        g.check_edges(5)

        stats = g.get_stats()
        assert stats["files_processed"] == 1
        assert stats["nodes"] == 10
        assert stats["edges"] == 5

    def test_reset(self):
        """Reset should clear all counters."""
        g = Guardrails()
        g.check_nodes(100)
        g.check_edges(50)

        g.reset()

        stats = g.get_stats()
        assert stats["nodes"] == 0
        assert stats["edges"] == 0
