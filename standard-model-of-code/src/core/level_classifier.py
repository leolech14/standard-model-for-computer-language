"""
Holarchy Level Classifier - Assigns scale levels (L-3..L12) to nodes.

Bridges the gap between the 16-level scale defined in MODEL.md and
the actual nodes produced by the pipeline. Each node's `kind` field
(from tree-sitter) maps deterministically to a holarchy level.

The 16-Level Scale (Koestler's Holons):
    L12 UNIVERSE    | COSMOLOGICAL | All software
    L11 DOMAIN      | COSMOLOGICAL | Business domain
    L10 ORGANIZATION| COSMOLOGICAL | Org/repo collection
    L9  PLATFORM    | COSMOLOGICAL | Monorepo/platform
    L8  ECOSYSTEM   | COSMOLOGICAL | External boundaries
    L7  SYSTEM      | SYSTEMIC     | Major subsystem
    L6  PACKAGE     | SYSTEMIC     | Directory/package
    L5  FILE        | SYSTEMIC     | Source file (module)
    L4  CONTAINER   | SYSTEMIC     | Class/struct/enum
    L3  NODE        | SEMANTIC     | Function/method (THE atom)
    L2  BLOCK       | SEMANTIC     | if/for/try block
    L1  STATEMENT   | SEMANTIC     | Single statement
    L0  TOKEN       | SYNTACTIC    | Keyword/identifier
    L-1 CHARACTER   | PHYSICAL     | UTF-8 character
    L-2 BYTE        | PHYSICAL     | Raw byte
    L-3 BIT/QUBIT   | PHYSICAL     | Binary digit
"""

from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict


# =============================================================================
# LEVEL DEFINITIONS
# =============================================================================

# Canonical level names from MODEL.md
LEVEL_NAMES = {
    "L-3": "BIT",
    "L-2": "BYTE",
    "L-1": "CHARACTER",
    "L0":  "TOKEN",
    "L1":  "STATEMENT",
    "L2":  "BLOCK",
    "L3":  "NODE",
    "L4":  "CONTAINER",
    "L5":  "FILE",
    "L6":  "PACKAGE",
    "L7":  "SYSTEM",
    "L8":  "ECOSYSTEM",
    "L9":  "PLATFORM",
    "L10": "ORGANIZATION",
    "L11": "DOMAIN",
    "L12": "UNIVERSE",
}

# Zone groupings
LEVEL_ZONES = {
    "L-3": "PHYSICAL", "L-2": "PHYSICAL", "L-1": "PHYSICAL",
    "L0":  "SYNTACTIC",
    "L1":  "SEMANTIC", "L2": "SEMANTIC", "L3": "SEMANTIC",
    "L4":  "SYSTEMIC", "L5": "SYSTEMIC", "L6": "SYSTEMIC", "L7": "SYSTEMIC",
    "L8":  "COSMOLOGICAL", "L9": "COSMOLOGICAL", "L10": "COSMOLOGICAL",
    "L11": "COSMOLOGICAL", "L12": "COSMOLOGICAL",
}

# Numeric ordering for comparison
LEVEL_ORDER = {
    "L-3": -3, "L-2": -2, "L-1": -1,
    "L0": 0, "L1": 1, "L2": 2, "L3": 3,
    "L4": 4, "L5": 5, "L6": 6, "L7": 7,
    "L8": 8, "L9": 9, "L10": 10, "L11": 11, "L12": 12,
}


# =============================================================================
# KIND -> LEVEL MAPPING
# =============================================================================

# Deterministic mapping from tree-sitter `kind` to holarchy level.
# This is the core inference: kind tells us WHAT it is, level tells us WHERE
# it sits in the holarchy.
KIND_TO_LEVEL = {
    # L3: NODE (The Atom - function/method level entities)
    "function":     "L3",
    "method":       "L3",
    "constructor":  "L3",
    "destructor":   "L3",
    "getter":       "L3",
    "setter":       "L3",
    "property":     "L3",
    "lambda":       "L3",
    "closure":      "L3",
    "callback":     "L3",
    "hook":         "L3",
    "signal":       "L3",
    "slot":         "L3",
    "test":         "L3",

    # L4: CONTAINER (classes, structs, aggregates)
    "class":        "L4",
    "struct":       "L4",
    "enum":         "L4",
    "trait":        "L4",
    "interface":    "L4",
    "impl":         "L4",
    "protocol":     "L4",
    "mixin":        "L4",
    "namespace":    "L4",
    "union":        "L4",
    "typedef":      "L4",
    "type_alias":   "L4",

    # L5: FILE (source file level)
    "module":       "L5",
    "file":         "L5",
    "script":       "L5",
    "stylesheet":   "L5",
    "template":     "L5",
    "config":       "L5",
    "schema":       "L5",
    "migration":    "L5",

    # L6: PACKAGE (directory/package level)
    "package":      "L6",
    "directory":    "L6",
    "workspace":    "L6",
    "crate":        "L6",   # Rust crate

    # L7: SYSTEM (major subsystem)
    "subsystem":    "L7",
    "service":      "L7",   # microservice level
    "application":  "L7",

    # L8: ECOSYSTEM (external boundaries)
    "boundary":     "L8",
    "k8s_resource": "L8",
    "external":     "L8",
    "api":          "L8",

    # L2: BLOCK (sub-function structures)
    "block":        "L2",
    "if_block":     "L2",
    "for_block":    "L2",
    "try_block":    "L2",
    "case":         "L2",
    "match_arm":    "L2",

    # L1: STATEMENT
    "statement":    "L1",
    "expression":   "L1",
    "assignment":   "L1",
    "declaration":  "L1",

    # L0: TOKEN
    "token":        "L0",
    "identifier":   "L0",
    "keyword":      "L0",
    "literal":      "L0",
    "operator":     "L0",
    "variable":     "L0",
    "parameter":    "L0",
    "constant":     "L0",
}

# Default level when kind is unknown or missing
DEFAULT_LEVEL = "L3"  # Conservative: assume atom-level


# =============================================================================
# LEVEL CLASSIFIER
# =============================================================================

def classify_level(node: Dict[str, Any]) -> str:
    """
    Assign a holarchy level to a node based on its `kind` field.

    The mapping is deterministic: kind -> level.
    Falls back to heuristic inference when kind is missing.

    Args:
        node: A node dict with at least 'kind' or 'type' field

    Returns:
        Level string (e.g., "L3", "L5")
    """
    kind = node.get("kind", "").lower()
    if not kind:
        kind = node.get("type", "").lower()
    if not kind:
        kind = node.get("symbol_kind", "").lower()

    # Direct mapping
    if kind in KIND_TO_LEVEL:
        return KIND_TO_LEVEL[kind]

    # Heuristic fallbacks based on node properties
    return _infer_level_from_properties(node, kind)


def _infer_level_from_properties(node: Dict[str, Any], kind: str) -> str:
    """Infer level from node properties when kind doesn't map directly."""

    # File-level indicators
    if node.get("metadata", {}).get("file_node"):
        return "L5"
    if node.get("discovery_method") == "filesystem":
        return "L5"

    # Container indicators (has children that are methods/functions)
    if node.get("parent") is None and "." not in node.get("name", ""):
        # Top-level named entity without a dot -> could be class or module
        if kind in ("class", "struct", "enum"):
            return "L4"

    # Has a parent -> likely a method inside a class
    if node.get("parent"):
        return "L3"

    # Codome boundary nodes
    if node.get("is_codome_boundary"):
        return "L8"

    # Default to NODE level (the atom)
    return DEFAULT_LEVEL


def classify_level_batch(nodes: List[Dict[str, Any]]) -> int:
    """
    Assign holarchy levels to all nodes in a batch.

    Mutates each node dict in-place, adding:
        - 'level': The holarchy level string (e.g., "L3")
        - 'level_name': Human-readable name (e.g., "NODE")
        - 'level_zone': Zone grouping (e.g., "SEMANTIC")

    Args:
        nodes: List of node dicts

    Returns:
        Number of nodes classified
    """
    classified = 0
    for node in nodes:
        level = classify_level(node)
        node["level"] = level
        node["level_name"] = LEVEL_NAMES.get(level, "UNKNOWN")
        node["level_zone"] = LEVEL_ZONES.get(level, "UNKNOWN")
        classified += 1
    return classified


def infer_package_levels(nodes: List[Dict[str, Any]]) -> int:
    """
    Promote directory-grouping nodes to L6 (PACKAGE) based on
    file path analysis. If multiple L5 (FILE) nodes share a directory,
    that directory represents an L6 package.

    This is a second-pass enrichment that runs after initial classification.

    Args:
        nodes: List of already-classified node dicts

    Returns:
        Number of synthetic package groupings detected
    """
    # Group files by their parent directory
    dir_to_files: Dict[str, List[str]] = defaultdict(list)
    for node in nodes:
        if node.get("level") == "L5":
            file_path = node.get("file_path", "")
            if "/" in file_path:
                parent_dir = "/".join(file_path.split("/")[:-1])
                dir_to_files[parent_dir].append(node.get("id", ""))

    # Count directories that contain multiple files (true packages)
    packages = {d: files for d, files in dir_to_files.items() if len(files) >= 2}
    return len(packages)


def compute_level_statistics(nodes: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Compute the distribution of nodes across holarchy levels.

    Returns:
        Dict mapping level strings to counts, e.g., {"L3": 450, "L4": 80, "L5": 120}
    """
    counter = Counter()
    for node in nodes:
        level = node.get("level", DEFAULT_LEVEL)
        counter[level] += 1
    # Sort by level order
    return dict(sorted(counter.items(), key=lambda x: LEVEL_ORDER.get(x[0], 0)))


def compute_zone_statistics(nodes: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Compute the distribution of nodes across zones.

    Returns:
        Dict mapping zone names to counts, e.g., {"SEMANTIC": 500, "SYSTEMIC": 200}
    """
    counter = Counter()
    for node in nodes:
        zone = node.get("level_zone", LEVEL_ZONES.get(node.get("level", ""), "UNKNOWN"))
        counter[zone] += 1
    return dict(sorted(counter.items()))


def get_level_info(level: str) -> Dict[str, Any]:
    """
    Get full information about a holarchy level.

    Returns:
        Dict with name, zone, order, description
    """
    descriptions = {
        "L-3": "Binary digit - the physical foundation",
        "L-2": "Raw byte - 8-bit encoding unit",
        "L-1": "Character - UTF-8 encoded symbol",
        "L0":  "Token - smallest meaningful syntax unit (keyword, identifier, literal)",
        "L1":  "Statement - single executable instruction",
        "L2":  "Block - control flow structure (if/for/try)",
        "L3":  "Node - function or method (THE atom of the Standard Model)",
        "L4":  "Container - class, struct, enum, trait (aggregates nodes)",
        "L5":  "File - source file or module (compilation unit)",
        "L6":  "Package - directory or package (namespace boundary)",
        "L7":  "System - major subsystem (parser, classifier, visualizer)",
        "L8":  "Ecosystem - external boundaries and integrations",
        "L9":  "Platform - monorepo or platform (e.g., Collider)",
        "L10": "Organization - company or team repository collection",
        "L11": "Domain - business domain (e.g., code analysis)",
        "L12": "Universe - all software",
    }
    return {
        "level": level,
        "name": LEVEL_NAMES.get(level, "UNKNOWN"),
        "zone": LEVEL_ZONES.get(level, "UNKNOWN"),
        "order": LEVEL_ORDER.get(level, 0),
        "description": descriptions.get(level, "Unknown level"),
    }


def format_level_summary(nodes: List[Dict[str, Any]]) -> str:
    """Format a human-readable summary of level distribution."""
    stats = compute_level_statistics(nodes)
    zone_stats = compute_zone_statistics(nodes)
    total = sum(stats.values())

    lines = [f"Holarchy Level Distribution ({total} nodes):"]
    lines.append("")

    for zone in ["PHYSICAL", "SYNTACTIC", "SEMANTIC", "SYSTEMIC", "COSMOLOGICAL"]:
        zone_count = zone_stats.get(zone, 0)
        if zone_count == 0:
            continue
        pct = (zone_count / total * 100) if total else 0
        lines.append(f"  {zone} ({zone_count} nodes, {pct:.1f}%):")
        for level, count in stats.items():
            if LEVEL_ZONES.get(level) == zone and count > 0:
                name = LEVEL_NAMES.get(level, "?")
                lines.append(f"    {level} {name}: {count}")
        lines.append("")

    return "\n".join(lines)
