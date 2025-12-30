"""
Purpose Flow Analyzer
=====================

Analyzes dependencies between layers and detects architectural violations.
"""

from typing import Dict, List, Tuple, Any

from .constants import Layer, LAYER_ORDER


class PurposeFlowAnalyzer:
    """
    Analyzes purpose flow across layers and detects violations.

    A violation occurs when a lower layer (e.g., Infrastructure)
    depends on a higher layer (e.g., Presentation).
    """

    def analyze(
        self,
        edges: List[Any],
        node_layers: Dict[str, Layer]
    ) -> Tuple[List[Tuple[str, str, str]], List[str]]:
        """
        Analyze edges for purpose flow and violations.

        Args:
            edges: List of edges (dicts or tuples)
            node_layers: Mapping of node_id to Layer

        Returns:
            Tuple of (purpose_flows, violations)
        """
        purpose_flows: List[Tuple[str, str, str]] = []
        violations: List[str] = []

        for edge in edges:
            source, target = self._extract_edge_endpoints(edge)
            if not source or not target:
                continue

            source_layer = node_layers.get(source, Layer.UNKNOWN)
            target_layer = node_layers.get(target, Layer.UNKNOWN)

            # Record flow
            flow_desc = f"{source_layer.value} -> {target_layer.value}"
            purpose_flows.append((source, target, flow_desc))

            # Check for violation
            violation = self._check_violation(
                source, target, source_layer, target_layer
            )
            if violation:
                violations.append(violation)

        return purpose_flows, violations

    def _extract_edge_endpoints(self, edge: Any) -> Tuple[str, str]:
        """Extract source and target from various edge formats."""
        if isinstance(edge, dict):
            source = edge.get('source', edge.get('from', ''))
            target = edge.get('target', edge.get('to', ''))
        elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
            source, target = str(edge[0]), str(edge[1])
        else:
            return '', ''
        return source, target

    def _check_violation(
        self,
        source_id: str,
        target_id: str,
        source_layer: Layer,
        target_layer: Layer
    ) -> str:
        """
        Check if an edge represents a layer violation.

        Violation: lower layer calling higher layer
        (e.g., Infrastructure -> Presentation)
        """
        source_order = LAYER_ORDER.get(source_layer, 99)
        target_order = LAYER_ORDER.get(target_layer, 99)

        # Skip if either layer is unknown
        if source_layer == Layer.UNKNOWN or target_layer == Layer.UNKNOWN:
            return ''

        # Skip testing layer (tests can call anything)
        if source_layer == Layer.TESTING:
            return ''

        # Violation: target is higher (lower order) than source
        if target_order < source_order:
            return (
                f"Layer violation: {source_layer.value} -> {target_layer.value} "
                f"({source_id} -> {target_id})"
            )

        return ''

    def summarize_flows(
        self,
        flows: List[Tuple[str, str, str]]
    ) -> Dict[str, int]:
        """
        Summarize flows by layer transition type.

        Args:
            flows: List of (source_id, target_id, flow_description)

        Returns:
            Dict of flow_type -> count
        """
        from collections import Counter
        flow_types = [flow[2] for flow in flows]
        return dict(Counter(flow_types))
