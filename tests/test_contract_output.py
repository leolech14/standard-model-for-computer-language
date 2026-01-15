#!/usr/bin/env python3
"""
Contract tests for output normalization.
Ensures canonical meta/id/confidence after normalization.
"""

from src.core.normalize_output import normalize_output, validate_contract


def _sample_output(target_path: str):
    return {
        "target": target_path,
        "timestamp": "2026-01-01T00:00:00",
        "version": "0.0.1",
        "nodes": [
            {
                "id": f"{target_path}/app/main.py:Main.run",
                "name": "Main.run",
                "file_path": f"{target_path}/app/main.py",
                "atom": "LOG.FNC.M",
                "ring": "LOG",
                "confidence": 80,
                "role_confidence": 80,
            },
            {
                "id": f"{target_path}/app/utils.py:Helper",
                "name": "Helper",
                "file_path": f"{target_path}/app/utils.py",
                "atom": "ORG.AGG.M",
                "ring": "ORG",
                "confidence": 1.0,
            },
        ],
        "edges": [
            {
                "source": f"{target_path}/app/main.py:Main.run",
                "target": f"{target_path}/app/utils.py:Helper",
                "edge_type": "calls",
                "confidence": 50,
            }
        ],
    }


def test_normalize_output_contract():
    target_path = "/tmp/project"
    data = _sample_output(target_path)
    normalized = normalize_output(data)

    # Meta must be present
    meta = normalized.get("meta", {})
    assert meta.get("target") == target_path
    assert meta.get("timestamp")
    assert meta.get("version")

    # Confidence must be canonical 0..1 with raw preserved
    node_conf = normalized["nodes"][0]["confidence"]
    assert 0.0 <= node_conf <= 1.0
    assert normalized["nodes"][0]["confidence_raw"] == 80
    assert normalized["nodes"][0]["role_confidence"] == 0.8
    assert normalized["nodes"][0]["role_confidence_raw"] == 80
    assert normalized["nodes"][0]["atom_family"] == "LOG"

    edge_conf = normalized["edges"][0]["confidence"]
    assert 0.0 <= edge_conf <= 1.0
    assert normalized["edges"][0]["confidence_raw"] == 50

    # IDs must be canonical (double-colon) and file paths relative
    assert "::" in normalized["nodes"][0]["id"]
    assert normalized["nodes"][0]["file_path"] == "app/main.py"
    assert normalized["nodes"][1]["file_path"] == "app/utils.py"

    errors, warnings = validate_contract(normalized)
    assert errors == []
    assert warnings == []


def test_normalize_output_idempotent():
    target_path = "/tmp/project"
    data = _sample_output(target_path)
    once = normalize_output(data)
    twice = normalize_output(once)
    assert once == twice
