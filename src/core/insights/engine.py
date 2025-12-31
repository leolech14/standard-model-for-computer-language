"""
Insights Engine
===============

Main facade that coordinates insight detection and reporting.
"""

from typing import List, Tuple
from collections import Counter

from .models import Insight, Priority
from .schemas import SCHEMAS
from .detectors import InsightDetector
from .reporter import InsightsReporter


class InsightsEngine:
    """Generates actionable insights from Collider output."""

    def __init__(self):
        self.insights: List[Insight] = []
        self.schemas = SCHEMAS
        self._detector = InsightDetector()
        self._reporter = InsightsReporter(SCHEMAS)

    def analyze(self, nodes: list, edges: list = None) -> List[Insight]:
        """
        Analyze Collider output and generate insights.

        Args:
            nodes: List of classified nodes from Collider
            edges: List of edges (optional)

        Returns:
            List of actionable insights
        """
        edges = edges or []

        # Count roles
        role_counts = Counter()
        for node in nodes:
            role = node.get('role', getattr(node, 'role', 'Unknown'))
            role_counts[role] += 1

        # Run all detectors
        self.insights = self._detector.detect_all(nodes, edges, role_counts)

        # Sort by priority
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3
        }
        self.insights.sort(key=lambda x: priority_order[x.priority])

        return self.insights

    def get_report(self) -> str:
        """Generate human-readable report."""
        return self._reporter.generate_report(self.insights)

    def get_summary(self) -> str:
        """Generate brief summary."""
        return self._reporter.generate_summary(self.insights)


def generate_insights(nodes: list, edges: list = None) -> Tuple[List[Insight], str]:
    """
    Convenience function to generate insights.

    Usage:
        from insights_engine import generate_insights

        result = analyze(path)
        insights, report = generate_insights(result.nodes, result.edges)
        print(report)
    """
    engine = InsightsEngine()
    insights = engine.analyze(nodes, edges)
    report = engine.get_report()
    return insights, report
