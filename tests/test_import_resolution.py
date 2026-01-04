import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from unified_analysis import analyze


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _run_analysis(fixture_dir: Path, output_dir: Path) -> dict:
    analyze(str(fixture_dir), output_dir=str(output_dir))
    analysis_path = output_dir / "unified_analysis.json"
    return json.loads(analysis_path.read_text())


def test_import_internal_resolves(tmp_path: Path):
    fixture = FIXTURES_DIR / "toy_import_internal"
    output_dir = tmp_path / "internal_out"
    data = _run_analysis(fixture, output_dir)

    edges = [edge for edge in data.get("edges", []) if edge.get("edge_type") == "imports"]
    expected_path = str((fixture / "pkg" / "b.py").resolve())

    assert any(
        edge.get("resolution") == "resolved_internal"
        and str(edge.get("target", "")).startswith(f"{expected_path}:")
        for edge in edges
    )

    stats = data.get("stats", {}).get("import_resolution", {})
    assert stats.get("resolved_internal", 0) >= 1


def test_import_ambiguous_remains_unresolved(tmp_path: Path):
    fixture = FIXTURES_DIR / "toy_import_ambiguous"
    output_dir = tmp_path / "ambiguous_out"
    data = _run_analysis(fixture, output_dir)

    edges = [edge for edge in data.get("edges", []) if edge.get("edge_type") == "imports"]
    ambiguous = [
        edge for edge in edges
        if edge.get("resolution") == "unresolved"
        and edge.get("metadata", {}).get("import_resolution") == "ambiguous"
    ]

    assert ambiguous

    stats = data.get("stats", {}).get("import_resolution", {})
    assert stats.get("ambiguous", 0) >= 1


def test_import_resolves_to_file_node(tmp_path: Path):
    fixture = FIXTURES_DIR / "toy_import_file_node"
    output_dir = tmp_path / "file_node_out"
    data = _run_analysis(fixture, output_dir)

    edges = [edge for edge in data.get("edges", []) if edge.get("edge_type") == "imports"]
    expected_path = str((fixture / "pkg" / "c.py").resolve())

    assert any(
        edge.get("resolution") == "resolved_internal"
        and str(edge.get("target", "")).startswith(f"{expected_path}:")
        for edge in edges
    )

    stats = data.get("stats", {}).get("import_resolution", {})
    assert stats.get("resolved_to_file_no_node", 0) == 0
