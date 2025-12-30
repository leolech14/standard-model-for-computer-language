"""
Purpose Field Detector
======================

Orchestrates purpose detection across all levels.
Uses PurposeClassifier for classification and FlowAnalyzer for violations.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import Counter

from .constants import Layer, LAYER_PURPOSES
from .purpose_classifier import PurposeClassifier
from .flow_analyzer import PurposeFlowAnalyzer


@dataclass
class PurposeNode:
    """A node with its purpose at all levels"""
    id: str
    name: str
    kind: str  # function, class, module

    # Level 1: Atomic Purpose
    atomic_purpose: str = "Unknown"
    atomic_confidence: float = 0.0

    # Level 2: Composite Purpose (for classes/modules)
    composite_purpose: Optional[str] = None
    child_purposes: List[str] = field(default_factory=list)

    # Level 3: Layer
    layer: Layer = Layer.UNKNOWN

    # Parent/children for hierarchy
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)


@dataclass
class PurposeField:
    """The complete purpose field of a codebase"""
    nodes: Dict[str, PurposeNode]
    layer_purposes: Dict[Layer, str]
    purpose_flow: List[Tuple[str, str, str]]
    violations: List[str]

    def summary(self) -> dict:
        """Summarize the purpose field"""
        layer_counts = Counter(n.layer for n in self.nodes.values())
        purpose_counts = Counter(n.atomic_purpose for n in self.nodes.values())

        return {
            "total_nodes": len(self.nodes),
            "layers": {l.value: c for l, c in layer_counts.items()},
            "purposes": dict(purpose_counts.most_common(10)),
            "violations": len(self.violations),
            "layer_purposes": {l.value: p for l, p in self.layer_purposes.items()}
        }


class PurposeFieldDetector:
    """
    Detects the Purpose Field of a codebase.

    Coordinates:
    - PurposeClassifier for role/layer classification
    - PurposeFlowAnalyzer for violation detection
    """

    def __init__(self):
        self.nodes: Dict[str, PurposeNode] = {}
        self.classifier = PurposeClassifier()
        self.flow_analyzer = PurposeFlowAnalyzer()

    def detect_field(
        self,
        analysis_nodes: list,
        edges: list = None
    ) -> PurposeField:
        """
        Detect the complete Purpose Field from analysis output.

        Args:
            analysis_nodes: List of nodes from unified_analysis
            edges: List of edges (optional, for flow analysis)

        Returns:
            PurposeField with all levels computed
        """
        edges = edges or []

        # Stage 1: Create PurposeNodes with atomic purpose
        self._create_nodes(analysis_nodes)

        # Stage 2: Build hierarchy (parent-child relationships)
        self._build_hierarchy()

        # Stage 3: Compute composite purpose (emergence)
        self._compute_composite_purposes()

        # Stage 4: Assign layers using classifier
        self._assign_layers()

        # Stage 5: Analyze flow and detect violations
        node_layers = {nid: n.layer for nid, n in self.nodes.items()}
        purpose_flow, violations = self.flow_analyzer.analyze(edges, node_layers)

        return PurposeField(
            nodes=self.nodes,
            layer_purposes=LAYER_PURPOSES,
            purpose_flow=purpose_flow,
            violations=violations
        )

    def _create_nodes(self, analysis_nodes: list):
        """Create PurposeNodes from analysis output"""
        for i, node in enumerate(analysis_nodes):
            # Handle both dict and object
            if hasattr(node, 'id'):
                node_id = node.id
                name = node.name
                kind = node.kind
                role = node.role
                conf = node.role_confidence
            else:
                node_id = node.get('id', '')
                name = node.get('name', 'unknown')
                kind = node.get('kind', 'function')
                role = node.get('role', 'Unknown')
                conf = node.get('role_confidence', 0.0)

            if not node_id:
                node_id = name or f"node_{i}"

            self.nodes[node_id] = PurposeNode(
                id=node_id,
                name=name,
                kind=kind,
                atomic_purpose=role,
                atomic_confidence=conf
            )

    def _build_hierarchy(self):
        """Build parent-child relationships from name patterns"""
        for node_id, node in self.nodes.items():
            if '.' in node.name:
                parent_name = node.name.rsplit('.', 1)[0]
                for pid, pnode in self.nodes.items():
                    if pnode.name == parent_name:
                        node.parent_id = pid
                        pnode.children_ids.append(node_id)
                        break

    def _compute_composite_purposes(self):
        """Compute emergent composite purpose for parent nodes"""
        for node in self.nodes.values():
            if node.children_ids:
                child_roles = [
                    self.nodes[cid].atomic_purpose
                    for cid in node.children_ids
                    if cid in self.nodes
                ]
                node.child_purposes = child_roles
                node.composite_purpose = self.classifier.classify_composite(child_roles)

    def _assign_layers(self):
        """Assign architectural layers using classifier"""
        for node in self.nodes.values():
            node.layer = self.classifier.get_effective_layer(
                role=node.atomic_purpose,
                name=node.name,
                composite_purpose=node.composite_purpose
            )


# Convenience function (backward compatible)
def detect_purpose_field(nodes: list, edges: list = None) -> PurposeField:
    """
    Convenience function to detect purpose field.

    Usage:
        from purpose.detector import detect_purpose_field

        result = analyze(path)
        field = detect_purpose_field(result.nodes, result.edges)
        print(field.summary())
    """
    detector = PurposeFieldDetector()
    return detector.detect_field(nodes, edges)
