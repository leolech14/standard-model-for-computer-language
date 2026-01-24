"""Tests for output_generator.py - stable output filename generation."""
import json
import pytest
from pathlib import Path
from src.core.output_generator import generate_outputs, write_llm_output


class TestStableOutputFilenames:
    """Tests for stable unified_analysis.json and collider_report.html creation."""

    def test_stable_json_created(self, tmp_path):
        """Verify unified_analysis.json is created alongside timestamped file."""
        data = {
            "nodes": [{"id": "test"}],
            "edges": [],
            "meta": {"target": "test_project"}
        }

        outputs = generate_outputs(data, tmp_path, target_name="test")

        # Both timestamped and stable files should exist
        assert outputs["llm"].exists()
        assert outputs["stable_json"].exists()
        assert outputs["stable_json"].name == "unified_analysis.json"

        # Content should be identical
        timestamped_content = outputs["llm"].read_text()
        stable_content = outputs["stable_json"].read_text()
        assert timestamped_content == stable_content

    def test_stable_html_created(self, tmp_path):
        """Verify collider_report.html is created alongside timestamped file."""
        data = {
            "nodes": [{"id": "test", "kind": "function"}],
            "edges": [],
            "meta": {"target": "test_project"}
        }

        outputs = generate_outputs(data, tmp_path, target_name="test")

        assert outputs["html"].exists()
        assert outputs["stable_html"].exists()
        assert outputs["stable_html"].name == "collider_report.html"

    def test_stable_json_content_valid(self, tmp_path):
        """Verify unified_analysis.json contains valid JSON with expected structure."""
        data = {
            "nodes": [{"id": "func1", "semantic_role": "utility"}],
            "edges": [{"source": "a", "target": "b"}],
            "semantic_analysis": {
                "entry_points": ["main"],
                "role_distribution": {"utility": 1}
            }
        }

        outputs = generate_outputs(data, tmp_path, target_name="test")

        # Load and verify structure
        loaded = json.loads(outputs["stable_json"].read_text())
        assert "nodes" in loaded
        assert "edges" in loaded
        # Note: semantic_analysis may be normalized/moved

    def test_multiple_runs_overwrite_stable(self, tmp_path):
        """Verify stable files are overwritten on subsequent runs."""
        data1 = {"nodes": [{"id": "v1"}], "edges": [], "meta": {"target": "t"}}
        data2 = {"nodes": [{"id": "v2"}], "edges": [], "meta": {"target": "t"}}

        # First run
        outputs1 = generate_outputs(data1, tmp_path, target_name="test", timestamp="20260101_000001")
        stable_content1 = outputs1["stable_json"].read_text()

        # Second run
        outputs2 = generate_outputs(data2, tmp_path, target_name="test", timestamp="20260101_000002")
        stable_content2 = outputs2["stable_json"].read_text()

        # Stable file should have new content
        assert "v2" in stable_content2
        assert "v1" not in stable_content2

        # Both timestamped files should exist
        assert outputs1["llm"].exists()
        assert outputs2["llm"].exists()


class TestWriteLlmOutput:
    """Tests for write_llm_output function."""

    def test_creates_directory(self, tmp_path):
        """Verify output directory is created if it doesn't exist."""
        nested_dir = tmp_path / "nested" / "output"
        data = {"test": "data"}

        path = write_llm_output(data, nested_dir, filename="test.json")

        assert path.exists()
        assert nested_dir.exists()

    def test_json_formatting(self, tmp_path):
        """Verify JSON is properly formatted with indentation."""
        data = {"nodes": [{"id": "test"}]}

        path = write_llm_output(data, tmp_path, filename="test.json")
        content = path.read_text()

        # Should be indented (pretty-printed)
        assert "\n" in content
        assert "  " in content  # 2-space indent
