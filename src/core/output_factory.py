#!/usr/bin/env python3
"""
COLLIDER OUTPUT FACTORY
=======================

Factory for creating UnifiedAnalysisOutput from raw analysis results.
Normalizes various data formats to the canonical schema.

Refactored to Builder pattern for better modularity and testability.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from schema import UnifiedAnalysisOutput


class UnifiedOutputBuilder:
    """
    Builder for constructing UnifiedAnalysisOutput with fluent API.

    Usage:
        output = (UnifiedOutputBuilder(target_path)
            .with_metadata(analysis_time_ms=1000)
            .with_nodes(raw_nodes)
            .with_edges(raw_edges)
            .with_stats(raw_stats)
            .with_classification()
            .with_auto_discovery(report)
            .build())
    """

    def __init__(self, target_path: str):
        """Initialize builder with target path."""
        self._target_path = target_path
        self._output = UnifiedAnalysisOutput(
            target_path=str(target_path),
            target_name=Path(target_path).name,
        )
        self._raw_stats: Dict = {}

    def with_metadata(self, analysis_time_ms: int = 0) -> 'UnifiedOutputBuilder':
        """Add metadata (timestamp, analysis time)."""
        self._output.generated_at = datetime.now().isoformat()
        self._output.analysis_time_ms = analysis_time_ms
        return self

    def with_nodes(self, nodes: List[Dict]) -> 'UnifiedOutputBuilder':
        """Add and normalize nodes."""
        for node in nodes:
            unified_node = self._normalize_node(node)
            self._output.nodes.append(unified_node)
        return self

    def with_edges(self, edges: List[Dict]) -> 'UnifiedOutputBuilder':
        """Add and normalize edges."""
        for edge in edges:
            unified_edge = self._normalize_edge(edge)
            self._output.edges.append(unified_edge)
        return self

    def with_stats(self, stats: Dict) -> 'UnifiedOutputBuilder':
        """Add statistics."""
        self._raw_stats = stats
        self._output.stats = {
            "total_files": stats.get("files_analyzed", stats.get("total_files", 0)),
            "total_lines": stats.get("total_lines_analyzed", stats.get("total_lines", 0)),
            "total_nodes": len(self._output.nodes),
            "total_edges": len(self._output.edges),
            "languages": list(stats.get("languages_detected", stats.get("languages", []))),
            "coverage_percentage": stats.get("recognized_percentage", stats.get("coverage_percentage", 0.0)),
            "unknown_percentage": 100.0 - stats.get("recognized_percentage", stats.get("coverage_percentage", 0.0)),
        }
        return self

    def with_classification(self) -> 'UnifiedOutputBuilder':
        """Calculate and add classification breakdown."""
        role_counts: Dict[str, int] = {}
        kind_counts: Dict[str, int] = {}
        confidence_dist = {"high": 0, "medium": 0, "low": 0}

        for node in self._output.nodes:
            role = node.get("role", "Unknown")
            kind = node.get("kind", "unknown")
            conf = node.get("role_confidence", 0)

            role_counts[role] = role_counts.get(role, 0) + 1
            kind_counts[kind] = kind_counts.get(kind, 0) + 1

            if conf >= 80:
                confidence_dist["high"] += 1
            elif conf >= 50:
                confidence_dist["medium"] += 1
            else:
                confidence_dist["low"] += 1

        self._output.classification = {
            "by_role": role_counts,
            "by_kind": kind_counts,
            "by_layer": {},
            "by_confidence": confidence_dist,
        }
        return self

    def with_auto_discovery(self, report: Optional[Dict]) -> 'UnifiedOutputBuilder':
        """Add auto-discovery report if available."""
        if report:
            self._output.auto_discovery = {
                "enabled": True,
                "patterns_applied": report.get("total_classified", 0),
                "particles_reclassified": report.get("particles_updated", 0),
                "top_patterns": report.get("top_patterns", []),
                "suggested_new_patterns": report.get("suggested_new_patterns", []),
            }
        return self

    def build(self) -> UnifiedAnalysisOutput:
        """Build and return the final output."""
        return self._output

    # ─────────────────────────────────────────────────────────────────
    # Private normalization methods
    # ─────────────────────────────────────────────────────────────────

    def _normalize_node(self, node: Dict) -> Dict:
        """Normalize a raw node to unified schema."""
        node_id = node.get("id")
        if not node_id:
            file = node.get("file_path", node.get("file", "unknown"))
            name = node.get("name", "unknown")
            node_id = f"{file}:{name}"

        return {
            "id": node_id,
            "name": node.get("name", ""),
            "kind": node.get("symbol_kind", node.get("kind", "unknown")),
            "file_path": node.get("file_path", node.get("file", "")),
            "start_line": node.get("line", node.get("start_line", 0)),
            "end_line": node.get("end_line", node.get("line", 0)),
            "role": node.get("type", node.get("role", "Unknown")),
            "role_confidence": node.get("confidence", node.get("role_confidence", 0.0)),
            "discovery_method": node.get("discovery_method", "pattern"),
            "params": node.get("params", []),
            "return_type": node.get("return_type", ""),
            "base_classes": node.get("base_classes", []),
            "decorators": node.get("decorators", []),
            "docstring": node.get("docstring", ""),
            "signature": node.get("evidence", node.get("signature", "")),
            "body_source": node.get("body_source", ""),
            "complexity": node.get("complexity", 0),
            "lines_of_code": (node.get("end_line", 0) - node.get("line", 0)) or 0,
            "in_degree": node.get("in_degree", 0),
            "out_degree": node.get("out_degree", 0),
            "layer": node.get("layer"),
            "dimensions": node.get("dimensions", {}),
            "lenses": node.get("lenses", {}),
            "metadata": node.get("metadata", {}),
        }

    def _normalize_edge(self, edge: Dict) -> Dict:
        """Normalize a raw edge to unified schema."""
        return {
            "source": edge.get("source", ""),
            "target": edge.get("target", ""),
            "edge_type": edge.get("edge_type", "unknown"),
            "weight": edge.get("weight", 1.0),
            "confidence": edge.get("confidence", 1.0),
            "file_path": edge.get("file", ""),
            "line": edge.get("line", 0),
            "metadata": edge.get("metadata", {}),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Backward-compatible factory function
# ─────────────────────────────────────────────────────────────────────────────

def create_unified_output(
    target_path: str,
    nodes: List[Dict],
    edges: List[Dict],
    stats: Dict,
    auto_discovery_report: Dict = None,
    analysis_time_ms: int = 0,
) -> UnifiedAnalysisOutput:
    """
    Create a unified output from analysis results.

    Backward-compatible wrapper around UnifiedOutputBuilder.

    Args:
        target_path: Path to the analyzed target
        nodes: List of node dicts (various formats accepted)
        edges: List of edge dicts
        stats: Statistics from the analysis
        auto_discovery_report: Report from pattern discovery
        analysis_time_ms: Total analysis time

    Returns:
        UnifiedAnalysisOutput with normalized data
    """
    return (UnifiedOutputBuilder(target_path)
        .with_metadata(analysis_time_ms)
        .with_nodes(nodes)
        .with_edges(edges)
        .with_stats(stats)
        .with_classification()
        .with_auto_discovery(auto_discovery_report)
        .build())
