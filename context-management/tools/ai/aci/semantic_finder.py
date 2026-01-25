"""
Semantic Finder
===============
SMoC Role: Finder | Domain: Semantic

Finds semantically related code using the Standard Model relationship graph:
- PURPOSE field (π₁-π₄) for semantic distance calculation
- 8 Dimensions for state-space proximity
- 19 Edge Types for upstream/downstream traversal
- 16 Scales for level-appropriate context selection

This is the "Curriculum Compiler" - it selects optimal context based on
semantic understanding of the query's relationship to the codebase graph.

Part of S3 (ACI subsystem).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple
import re


# =============================================================================
# PURPOSE FIELD HIERARCHY (π₁-π₄)
# =============================================================================
# From schema/particle.schema.json:614-655

class PurposeLevel(Enum):
    """Hierarchical emergence levels of PURPOSE field."""
    PI1_ATOMIC = "pi1"      # = Role (Query, Validator, Repository)
    PI2_MOLECULAR = "pi2"   # Emergent from effect + boundary + topology
    PI3_ORGANELLE = "pi3"   # Emergent from children's π₂ distribution
    PI4_SYSTEM = "pi4"      # Emergent from file-level π₃ distribution


# =============================================================================
# DIMENSION SEMANTICS
# =============================================================================
# From schema/fixed/dimensions.json

DIMENSION_WEIGHTS = {
    "D1_WHAT": 0.15,     # Atom type
    "D2_LAYER": 0.20,    # Architecture layer (high weight for context relevance)
    "D3_ROLE": 0.25,     # Purpose role (highest - directly semantic)
    "D4_BOUNDARY": 0.10, # IO boundary
    "D5_STATE": 0.05,    # Stateful/Stateless
    "D6_EFFECT": 0.15,   # Side effects (important for reasoning)
    "D7_LIFECYCLE": 0.05,
    "D8_TRUST": 0.05,    # Confidence
}

# Layer hierarchy for distance calculation
LAYER_ORDER = ["Interface", "Application", "Core", "Infrastructure", "Test"]

# Role similarity clusters (roles in same cluster are semantically close)
ROLE_CLUSTERS = {
    "data_access": ["Repository", "DAO", "Query", "Finder", "Reader", "Writer"],
    "business": ["Service", "Manager", "Orchestrator", "Coordinator", "UseCase"],
    "validation": ["Validator", "Guard", "Checker", "Constraint", "Sanitizer"],
    "transformation": ["Transformer", "Mapper", "Converter", "Adapter", "Translator"],
    "presentation": ["Controller", "Handler", "Presenter", "View", "Formatter"],
    "infrastructure": ["Gateway", "Client", "Provider", "Factory", "Builder"],
    "entity": ["Entity", "Aggregate", "ValueObject", "DTO", "Model"],
    "event": ["Event", "Command", "EventHandler", "CommandHandler", "Listener"],
}


# =============================================================================
# EDGE TYPE SEMANTICS
# =============================================================================
# From schema/particle.schema.json:330-400

class EdgeDirection(Enum):
    """Direction for graph traversal."""
    UPSTREAM = "upstream"     # Where it comes from (providers)
    DOWNSTREAM = "downstream" # Where it goes (consumers)
    BOTH = "both"


# Edge family classification
EDGE_FAMILIES = {
    "Structural": ["contains", "is_part_of"],
    "Dependency": ["calls", "imports", "uses", "references"],
    "Inheritance": ["inherits", "implements", "extends", "mixes_in"],
    "Semantic": ["returns", "receives", "delegates_to", "decorates", "wraps"],
    "Temporal": ["triggers", "disposes", "precedes", "follows"],
}

# Direction mapping for edges
UPSTREAM_EDGES = {"inherits", "implements", "extends", "receives", "decorates", "wraps", "precedes"}
DOWNSTREAM_EDGES = {"calls", "imports", "uses", "returns", "triggers", "delegates_to", "follows"}


# =============================================================================
# QUERY TO SEMANTIC SPACE MAPPING
# =============================================================================

# Keywords that map to specific PURPOSE levels
QUERY_PURPOSE_KEYWORDS = {
    # π₂ purposes
    "retrieve": "Retrieve",
    "fetch": "Retrieve",
    "get": "Retrieve",
    "load": "Retrieve",
    "save": "Persist",
    "persist": "Persist",
    "store": "Persist",
    "write": "Persist",
    "transform": "Transform",
    "convert": "Transform",
    "map": "Transform",
    "compute": "Compute",
    "calculate": "Compute",
    "process": "Compute",
    "validate": "Validate",
    "check": "Validate",
    "verify": "Validate",
    "coordinate": "Coordinate",
    "orchestrate": "Coordinate",
    "manage": "Coordinate",
    "transport": "Transport",
    "send": "Transport",
    "receive": "Transport",
    "present": "Present",
    "display": "Present",
    "render": "Present",
}

# Keywords that map to architecture layers
QUERY_LAYER_KEYWORDS = {
    "api": "Interface",
    "endpoint": "Interface",
    "controller": "Interface",
    "route": "Interface",
    "handler": "Interface",
    "service": "Application",
    "usecase": "Application",
    "workflow": "Application",
    "domain": "Core",
    "entity": "Core",
    "model": "Core",
    "repository": "Infrastructure",
    "database": "Infrastructure",
    "cache": "Infrastructure",
    "external": "Infrastructure",
    "test": "Test",
    "spec": "Test",
    "mock": "Test",
}

# Keywords that imply graph traversal direction
QUERY_DIRECTION_KEYWORDS = {
    "upstream": EdgeDirection.UPSTREAM,
    "provider": EdgeDirection.UPSTREAM,
    "dependency": EdgeDirection.UPSTREAM,
    "inherits": EdgeDirection.UPSTREAM,
    "extends": EdgeDirection.UPSTREAM,
    "downstream": EdgeDirection.DOWNSTREAM,
    "consumer": EdgeDirection.DOWNSTREAM,
    "caller": EdgeDirection.DOWNSTREAM,
    "uses": EdgeDirection.DOWNSTREAM,
    "implements": EdgeDirection.DOWNSTREAM,
    "both": EdgeDirection.BOTH,
    "related": EdgeDirection.BOTH,
    "connected": EdgeDirection.BOTH,
}


@dataclass
class SemanticTarget:
    """A semantically matched target for context loading."""
    purpose: Optional[str] = None           # π₂ purpose (Retrieve, Transform, etc.)
    layer: Optional[str] = None             # Architecture layer
    roles: List[str] = field(default_factory=list)  # DDD roles
    direction: EdgeDirection = EdgeDirection.BOTH   # Graph traversal direction
    scale_focus: Optional[str] = None       # L3 (NODE), L4 (CONTAINER), L5 (FILE)
    confidence: float = 0.0                 # Match confidence


@dataclass
class SemanticMatch:
    """Result of semantic query matching."""
    query: str
    targets: List[SemanticTarget]           # Matched semantic targets
    suggested_files: List[str]              # File patterns to include
    suggested_sets: List[str]               # Analysis sets to use
    traversal_strategy: str                 # "focused", "exploratory", "hierarchical"
    context_flow: str                       # "laminar" (coherent) or "turbulent" (mixed)
    reasoning: str                          # Explanation of match


def _extract_keywords(query: str) -> List[str]:
    """Extract significant keywords from query."""
    clean = re.sub(r'[^\w\s]', ' ', query.lower())
    words = clean.split()
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'to', 'of',
        'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
        'how', 'what', 'where', 'when', 'why', 'which', 'who',
        'this', 'that', 'these', 'those', 'it', 'its', 'i', 'me',
        'you', 'we', 'they', 'and', 'or', 'but', 'if', 'then',
    }
    return [w for w in words if w not in stop_words and len(w) > 2]


def _match_purpose(keywords: List[str]) -> Tuple[Optional[str], float]:
    """Match keywords to π₂ PURPOSE field."""
    for kw in keywords:
        if kw in QUERY_PURPOSE_KEYWORDS:
            return QUERY_PURPOSE_KEYWORDS[kw], 0.9

    # Partial matching
    for kw in keywords:
        for pattern, purpose in QUERY_PURPOSE_KEYWORDS.items():
            if pattern in kw or kw in pattern:
                return purpose, 0.6

    return None, 0.0


def _match_layer(keywords: List[str]) -> Tuple[Optional[str], float]:
    """Match keywords to architecture layer."""
    for kw in keywords:
        if kw in QUERY_LAYER_KEYWORDS:
            return QUERY_LAYER_KEYWORDS[kw], 0.9

    # Partial matching
    for kw in keywords:
        for pattern, layer in QUERY_LAYER_KEYWORDS.items():
            if pattern in kw or kw in pattern:
                return layer, 0.6

    return None, 0.0


def _match_direction(keywords: List[str]) -> EdgeDirection:
    """Match keywords to graph traversal direction."""
    for kw in keywords:
        if kw in QUERY_DIRECTION_KEYWORDS:
            return QUERY_DIRECTION_KEYWORDS[kw]
    return EdgeDirection.BOTH


def _match_roles(keywords: List[str]) -> List[str]:
    """Match keywords to DDD roles."""
    matched = []
    for kw in keywords:
        kw_lower = kw.lower()
        for roles in ROLE_CLUSTERS.values():
            for role in roles:
                if kw_lower in role.lower() or role.lower() in kw_lower:
                    if role not in matched:
                        matched.append(role)
    return matched


def _purpose_to_sets(purpose: str) -> List[str]:
    """Map PURPOSE to analysis sets."""
    mapping = {
        "Retrieve": ["pipeline", "data_access"],
        "Persist": ["infrastructure", "data_access"],
        "Transform": ["pipeline", "classifiers"],
        "Compute": ["pipeline", "algorithms"],
        "Validate": ["validators", "constraints"],
        "Coordinate": ["services", "orchestration"],
        "Transport": ["gateways", "infrastructure"],
        "Present": ["presentation", "viz_core"],
    }
    return mapping.get(purpose, ["pipeline"])


def _layer_to_sets(layer: str) -> List[str]:
    """Map architecture layer to analysis sets."""
    mapping = {
        "Interface": ["controllers", "api"],
        "Application": ["services", "pipeline"],
        "Core": ["domain", "entities", "theory"],
        "Infrastructure": ["infrastructure", "data_access"],
        "Test": ["tests"],
    }
    return mapping.get(layer, ["pipeline"])


def _determine_context_flow(targets: List[SemanticTarget]) -> str:
    """Determine if context flow is laminar (coherent) or turbulent (mixed)."""
    if not targets:
        return "turbulent"

    # Check purpose coherence
    purposes = [t.purpose for t in targets if t.purpose]
    if len(set(purposes)) <= 1:
        return "laminar"

    # Check layer coherence
    layers = [t.layer for t in targets if t.layer]
    if len(set(layers)) <= 2:
        # Adjacent layers are still laminar
        if len(layers) >= 2:
            layer_indices = [LAYER_ORDER.index(l) for l in layers if l in LAYER_ORDER]
            if layer_indices and max(layer_indices) - min(layer_indices) <= 1:
                return "laminar"

    return "turbulent"


def _determine_traversal_strategy(targets: List[SemanticTarget]) -> str:
    """Determine graph traversal strategy."""
    if not targets:
        return "exploratory"

    # If single focused target, use focused strategy
    if len(targets) == 1 and targets[0].confidence > 0.7:
        return "focused"

    # If multiple layers involved, use hierarchical
    layers = [t.layer for t in targets if t.layer]
    if len(set(layers)) > 1:
        return "hierarchical"

    return "exploratory"


def semantic_match(query: str) -> SemanticMatch:
    """
    Match query to semantic space of Standard Model of Code.

    This is the core "Curriculum Compiler" function that:
    1. Extracts semantic signals from the query
    2. Maps to PURPOSE field (π₁-π₄) hierarchy
    3. Identifies relevant architecture layers
    4. Determines graph traversal direction
    5. Suggests optimal context sets

    Args:
        query: The user's question or instruction

    Returns:
        SemanticMatch with targets, suggested files/sets, and reasoning
    """
    keywords = _extract_keywords(query)

    # Match semantic dimensions
    purpose, purpose_conf = _match_purpose(keywords)
    layer, layer_conf = _match_layer(keywords)
    direction = _match_direction(keywords)
    roles = _match_roles(keywords)

    # Build semantic targets
    targets = []

    if purpose or layer or roles:
        target = SemanticTarget(
            purpose=purpose,
            layer=layer,
            roles=roles,
            direction=direction,
            scale_focus="L3" if purpose else "L5",  # NODE for purpose, FILE for layer
            confidence=max(purpose_conf, layer_conf, 0.5 if roles else 0.0)
        )
        targets.append(target)

    # Determine suggested sets
    suggested_sets = []
    if purpose:
        suggested_sets.extend(_purpose_to_sets(purpose))
    if layer:
        suggested_sets.extend(_layer_to_sets(layer))
    if not suggested_sets:
        suggested_sets = ["pipeline", "theory"]  # Default

    # Deduplicate while preserving order
    seen = set()
    unique_sets = []
    for s in suggested_sets:
        if s not in seen:
            seen.add(s)
            unique_sets.append(s)

    # Build suggested file patterns
    suggested_files = []
    if layer:
        layer_patterns = {
            "Interface": ["**/controllers/**", "**/api/**", "**/routes/**"],
            "Application": ["**/services/**", "**/usecases/**"],
            "Core": ["**/domain/**", "**/entities/**", "**/models/**"],
            "Infrastructure": ["**/infrastructure/**", "**/repositories/**"],
            "Test": ["**/tests/**", "**/*_test.*"],
        }
        suggested_files.extend(layer_patterns.get(layer, []))

    # Determine flow characteristics
    context_flow = _determine_context_flow(targets)
    traversal_strategy = _determine_traversal_strategy(targets)

    # Build reasoning
    reasoning_parts = []
    if purpose:
        reasoning_parts.append(f"π₂ purpose: {purpose}")
    if layer:
        reasoning_parts.append(f"layer: {layer}")
    if roles:
        reasoning_parts.append(f"roles: {', '.join(roles)}")
    if direction != EdgeDirection.BOTH:
        reasoning_parts.append(f"traversal: {direction.value}")

    reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No strong semantic match - using exploratory strategy"

    return SemanticMatch(
        query=query,
        targets=targets,
        suggested_files=suggested_files,
        suggested_sets=unique_sets[:5],
        traversal_strategy=traversal_strategy,
        context_flow=context_flow,
        reasoning=reasoning,
    )


def get_upstream_context(particle_id: str, graph_data: Dict) -> List[str]:
    """
    Get upstream context (providers, dependencies) for a particle.

    Traverses UPSTREAM_EDGES to find what this particle depends on.
    """
    if "edges" not in graph_data:
        return []

    upstream = []
    for edge in graph_data["edges"]:
        if edge.get("source") == particle_id and edge.get("type") in UPSTREAM_EDGES:
            upstream.append(edge.get("target"))
        elif edge.get("target") == particle_id and edge.get("type") in DOWNSTREAM_EDGES:
            upstream.append(edge.get("source"))

    return upstream


def get_downstream_context(particle_id: str, graph_data: Dict) -> List[str]:
    """
    Get downstream context (consumers, callers) for a particle.

    Traverses DOWNSTREAM_EDGES to find what depends on this particle.
    """
    if "edges" not in graph_data:
        return []

    downstream = []
    for edge in graph_data["edges"]:
        if edge.get("source") == particle_id and edge.get("type") in DOWNSTREAM_EDGES:
            downstream.append(edge.get("target"))
        elif edge.get("target") == particle_id and edge.get("type") in UPSTREAM_EDGES:
            downstream.append(edge.get("source"))

    return downstream


def compute_semantic_distance(particle_a: Dict, particle_b: Dict) -> float:
    """
    Compute semantic distance between two particles in dimension space.

    Uses weighted dimension comparison from DIMENSION_WEIGHTS.
    Distance ranges from 0.0 (identical) to 1.0 (maximally different).
    """
    dims_a = particle_a.get("dimensions", {})
    dims_b = particle_b.get("dimensions", {})

    total_weight = 0.0
    weighted_diff = 0.0

    for dim, weight in DIMENSION_WEIGHTS.items():
        val_a = dims_a.get(dim)
        val_b = dims_b.get(dim)

        if val_a is None or val_b is None:
            continue

        total_weight += weight

        if dim == "D2_LAYER":
            # Layer distance is positional
            if val_a in LAYER_ORDER and val_b in LAYER_ORDER:
                idx_a = LAYER_ORDER.index(val_a)
                idx_b = LAYER_ORDER.index(val_b)
                diff = abs(idx_a - idx_b) / (len(LAYER_ORDER) - 1)
            else:
                diff = 1.0 if val_a != val_b else 0.0
        elif dim == "D3_ROLE":
            # Role distance uses clusters
            diff = 0.0 if val_a == val_b else 1.0
            for cluster_roles in ROLE_CLUSTERS.values():
                if val_a in cluster_roles and val_b in cluster_roles:
                    diff = 0.3  # Same cluster = close
                    break
        elif dim == "D8_TRUST":
            # Trust is numeric
            diff = abs(val_a - val_b) / 100.0
        else:
            # Categorical dimensions
            diff = 0.0 if val_a == val_b else 1.0

        weighted_diff += weight * diff

    if total_weight == 0:
        return 1.0

    return weighted_diff / total_weight


def format_semantic_match(match: SemanticMatch) -> str:
    """Format semantic match for display."""
    lines = [
        f"Query: {match.query[:80]}...",
        f"Strategy: {match.traversal_strategy} ({match.context_flow} flow)",
        f"Reasoning: {match.reasoning}",
    ]

    if match.targets:
        lines.append("Targets:")
        for t in match.targets:
            parts = []
            if t.purpose:
                parts.append(f"π₂={t.purpose}")
            if t.layer:
                parts.append(f"layer={t.layer}")
            if t.roles:
                parts.append(f"roles=[{','.join(t.roles[:3])}]")
            lines.append(f"  - {' '.join(parts)} (conf={t.confidence:.2f})")

    lines.append(f"Sets: {', '.join(match.suggested_sets)}")

    if match.suggested_files:
        lines.append(f"Files: {', '.join(match.suggested_files[:3])}")

    return "\n".join(lines)
