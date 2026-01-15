#!/usr/bin/env python3
"""
Output normalization utilities for Collider.

Purpose: enforce canonical output contract at OUTPUT time while
preserving backward compatibility with legacy outputs.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import PurePath
from typing import Any, Dict, Iterable, List, Optional, Tuple


CONFIDENCE_SUFFIXES = ("_confidence", "_prob", "_probability")
ATOM_FAMILIES = {"LOG", "DAT", "ORG", "EXE", "EXT"}
TIER_VALUES = {"T0", "T1", "T2", "unknown"}
SCHEMA_CATEGORY_TO_FAMILY = {
    "LOGIC": "LOG",
    "DATA": "DAT",
    "ORGANIZATION": "ORG",
    "EXECUTION": "EXE",
    "ECOSYSTEM": "EXT",
}

_SCHEMA = None


def _get_schema():
    """Lazy-load unified atom schema if available."""
    global _SCHEMA
    if _SCHEMA is not None:
        return _SCHEMA
    try:
        from src.core.unified_atom_schema import get_unified_schema
    except ImportError:
        try:
            from unified_atom_schema import get_unified_schema
        except ImportError:
            _SCHEMA = None
            return _SCHEMA
    try:
        _SCHEMA = get_unified_schema()
    except Exception:
        _SCHEMA = None
    return _SCHEMA


def normalize_meta(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure meta.target/timestamp/version exist and are populated."""
    meta = data.get("meta")
    if not isinstance(meta, dict):
        meta = {}

    # Promote legacy root keys into meta (keep root for compatibility).
    for key in ("target", "timestamp", "version"):
        if key in data and key not in meta:
            meta[key] = data[key]

    if not meta.get("target"):
        meta["target"] = data.get("target_path") or data.get("target_name") or "unknown"
    if not meta.get("timestamp"):
        meta["timestamp"] = datetime.now().isoformat()
    if not meta.get("version"):
        meta["version"] = data.get("version") or data.get("collider_version") or "unknown"

    data["meta"] = meta
    return meta


def is_confidence_key(key: str) -> bool:
    lower = key.lower()
    if lower.endswith("_raw"):
        return False
    if lower == "confidence":
        return True
    return lower.endswith(CONFIDENCE_SUFFIXES)


def normalize_confidence_fields(obj: Dict[str, Any]) -> None:
    """Normalize confidence-like fields to 0..1, preserving raw values."""
    if not isinstance(obj, dict):
        return

    for key, value in list(obj.items()):
        if not is_confidence_key(key):
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue

        if 1.0 < numeric <= 100.0:
            raw_key = f"{key}_raw"
            obj.setdefault(raw_key, value)
            obj[key] = numeric / 100.0


def _derive_atom_family(atom_id: str) -> Optional[str]:
    if not atom_id:
        return None
    prefix = atom_id.split(".", 1)[0].upper()
    if prefix in ATOM_FAMILIES:
        return prefix
    schema = _get_schema()
    if schema:
        atom_def = schema.get(atom_id)
        if atom_def:
            category = str(atom_def.category).upper()
            return SCHEMA_CATEGORY_TO_FAMILY.get(category)
    return None


def _derive_tier(atom_id: str) -> str:
    if not atom_id:
        return "unknown"
    schema = _get_schema()
    if schema:
        atom_def = schema.get(atom_id)
        if atom_def and atom_def.tier:
            return atom_def.tier
    prefix = atom_id.split(".", 1)[0].upper()
    if prefix == "CORE":
        return "T0"
    if prefix == "ARCH":
        return "T1"
    if prefix == "EXT":
        return "T2"
    return "unknown"


def _normalize_taxonomy(node: Dict[str, Any]) -> None:
    atom_id = node.get("atom")
    derived_family = _derive_atom_family(atom_id) if atom_id else None
    if atom_id:
        if derived_family:
            node["atom_family"] = derived_family
        else:
            node.setdefault("atom_family", None)

    tier_value = node.get("tier")
    if isinstance(tier_value, str):
        tier_value = tier_value.upper()
        if tier_value in ("T0", "T1", "T2"):
            node["tier"] = tier_value
        elif tier_value.lower() == "unknown":
            node["tier"] = "unknown"
        else:
            tier_value = None
    if not tier_value or node.get("tier") not in TIER_VALUES:
        node["tier"] = _derive_tier(atom_id) if atom_id else "unknown"

    if "ring" not in node:
        node["ring"] = None


def _iter_nodes(data: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    nodes = data.get("nodes", [])
    return nodes if isinstance(nodes, list) else []


def _iter_edges(data: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    edges = data.get("edges", [])
    return edges if isinstance(edges, list) else []


def _candidate_roots(target: str) -> List[PurePath]:
    if not target:
        return []
    root = PurePath(str(target))
    roots = [root]
    # If target is a file, also try its parent.
    if root.suffix:
        roots.append(root.parent)
    else:
        roots.append(root.parent)
    # Deduplicate while preserving order.
    seen = set()
    deduped = []
    for item in roots:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def normalize_file_paths(nodes: Iterable[Dict[str, Any]], target: str) -> None:
    """Make node.file_path relative to meta.target when possible."""
    roots = _candidate_roots(target)
    if not roots:
        return

    for node in nodes:
        file_path = node.get("file_path")
        if not file_path:
            continue
        try:
            path = PurePath(str(file_path))
        except (TypeError, ValueError):
            continue

        for root in roots:
            try:
                rel = path.relative_to(root)
            except ValueError:
                continue
            node["file_path"] = str(rel)
            break


def canonicalize_ids(
    nodes: Iterable[Dict[str, Any]],
    edges: Iterable[Dict[str, Any]],
) -> Dict[str, str]:
    """
    Canonicalize node ids to file_path::qualified_name.
    Updates edge source/target references accordingly.
    """
    id_map: Dict[str, str] = {}

    for node in nodes:
        raw_id = node.get("id")
        if not raw_id or not isinstance(raw_id, str):
            continue

        if "::" in raw_id:
            file_part, name_part = raw_id.split("::", 1)
        elif ":" in raw_id:
            # Split on last colon to avoid Windows drive-letter issues.
            file_part, name_part = raw_id.rsplit(":", 1)
        else:
            continue

        file_part = node.get("file_path") or file_part
        new_id = f"{file_part}::{name_part}"
        if new_id != raw_id:
            id_map[raw_id] = new_id
            node["id"] = new_id

    if not id_map:
        return id_map

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source in id_map:
            edge["source"] = id_map[source]
        if target in id_map:
            edge["target"] = id_map[target]

    return id_map


def normalize_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply all output-normalization steps in-place."""
    if not isinstance(data, dict):
        return data

    meta = normalize_meta(data)
    nodes = list(_iter_nodes(data))
    edges = list(_iter_edges(data))

    normalize_file_paths(nodes, str(meta.get("target") or ""))

    for node in nodes:
        if isinstance(node, dict):
            normalize_confidence_fields(node)
            _normalize_taxonomy(node)
    for edge in edges:
        if isinstance(edge, dict):
            normalize_confidence_fields(edge)

    canonicalize_ids(nodes, edges)
    return data


def validate_contract(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Validate output contract; returns (errors, warnings)."""
    errors: List[str] = []
    warnings: List[str] = []

    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    for key in ("target", "timestamp", "version"):
        if not meta.get(key):
            errors.append(f"meta.{key} missing or empty")

    nodes = list(_iter_nodes(data))
    node_ids = {n.get("id") for n in nodes if isinstance(n, dict) and n.get("id")}

    def check_confidence_fields(obj: Dict[str, Any], label: str) -> None:
        for key, value in obj.items():
            if not is_confidence_key(key):
                continue
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                errors.append(f"{label} {key} not numeric: {value}")
                continue
            if not 0.0 <= numeric <= 1.0:
                errors.append(f"{label} {key} out of range: {value}")

    for idx, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"node[{idx}] is not a dict")
            continue
        node_id = node.get("id", "")
        if not node_id:
            errors.append(f"node[{idx}] missing id")
        elif "::" not in node_id:
            warnings.append(f"node[{idx}] legacy id format: {node_id}")

        atom_id = node.get("atom")
        atom_family = node.get("atom_family")
        if atom_id:
            if not atom_family:
                errors.append(f"node[{idx}] atom_family missing for atom {atom_id}")
            elif str(atom_family).upper() not in ATOM_FAMILIES:
                errors.append(f"node[{idx}] atom_family invalid: {atom_family}")

        tier = node.get("tier")
        if tier not in TIER_VALUES:
            errors.append(f"node[{idx}] tier invalid: {tier}")

        check_confidence_fields(node, f"node[{idx}]")

    edges = list(_iter_edges(data))
    for idx, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edge[{idx}] is not a dict")
            continue
        source = edge.get("source")
        if not source:
            errors.append(f"edge[{idx}] missing source")
        elif source not in node_ids:
            errors.append(f"edge[{idx}] source not in graph: {source}")

        check_confidence_fields(edge, f"edge[{idx}]")

    return errors, warnings
