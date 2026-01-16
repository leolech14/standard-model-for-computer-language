#!/usr/bin/env python3
"""
Lightweight checks for visualization token alignment to canonical fields.
"""

import json
from pathlib import Path


def _load_tokens(path: Path):
    with open(path) as f:
        return json.load(f)


def test_controls_datamaps_alignment(project_root):
    controls_path = project_root / "schema" / "viz" / "tokens" / "controls.tokens.json"
    data = _load_tokens(controls_path)
    datamaps = data.get("datamaps", {}).get("$value", [])

    atom_family_ids = {dm.get("id") for dm in datamaps if isinstance(dm, dict)}
    for family in {"LOG", "DAT", "ORG", "EXE", "EXTERNAL"}:
        assert family in atom_family_ids, f"Missing datamap for atom_family: {family}"

    tier_values = set()
    for dm in datamaps:
        if not isinstance(dm, dict):
            continue
        match = dm.get("match", {})
        if "tiers" in match and isinstance(match["tiers"], list):
            tier_values.update(match["tiers"])

    for tier in {"T0", "T1", "T2", "UNKNOWN"}:
        assert tier in tier_values, f"Missing tier filter value: {tier}"


def test_appearance_ring_and_family_palettes(project_root):
    appearance_path = project_root / "schema" / "viz" / "tokens" / "appearance.tokens.json"
    data = _load_tokens(appearance_path)
    colors = data.get("color", {})

    ring = colors.get("ring", {})
    assert "PRESENTATION" in ring, "Missing ring palette for PRESENTATION"
    assert "UNKNOWN" in ring, "Missing ring palette for UNKNOWN"

    atom_family = colors.get("atom-family", {})
    for family in {"LOG", "DAT", "ORG", "EXE", "EXT", "UNKNOWN"}:
        assert family in atom_family, f"Missing atom_family palette: {family}"
