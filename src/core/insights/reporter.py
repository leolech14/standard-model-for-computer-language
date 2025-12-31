"""
Insights Reporter
=================

Generates human-readable reports from insights.
"""

from typing import List, Dict

from .models import Insight
from .schemas import SCHEMAS


class InsightsReporter:
    """Generates reports from insights."""

    def __init__(self, schemas: Dict = None):
        self.schemas = schemas or SCHEMAS

    def generate_report(self, insights: List[Insight]) -> str:
        """Generate human-readable report."""
        if not insights:
            return "No significant issues detected."

        lines = ["# Actionable Insights Report\n"]

        # Group by type
        by_type = {}
        for insight in insights:
            key = insight.type.value
            if key not in by_type:
                by_type[key] = []
            by_type[key].append(insight)

        for type_name, type_insights in by_type.items():
            lines.append(f"\n## {type_name.upper()}\n")
            for i, insight in enumerate(type_insights, 1):
                lines.append(f"### {i}. {insight.title} [{insight.priority.value.upper()}]")
                lines.append(f"\n{insight.description}\n")
                lines.append(f"**Affected:** {', '.join(insight.affected_components[:3])}")
                lines.append(f"\n**Recommendation:** {insight.recommendation}")
                lines.append(f"\n**Effort:** {insight.effort_estimate}")

                if insight.schema:
                    schema = self.schemas.get(insight.schema)
                    if schema:
                        lines.append(f"\n\n**Optimization Schema: {schema.name}**")
                        lines.append(f"\n{schema.description}")
                        lines.append(f"\n\nSteps:")
                        for step in schema.steps:
                            lines.append(f"\n- {step}")

                lines.append("\n---\n")

        return "\n".join(lines)

    def generate_summary(self, insights: List[Insight]) -> str:
        """Generate a brief summary of insights."""
        if not insights:
            return "No issues found."

        by_priority = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for insight in insights:
            by_priority[insight.priority.value] += 1

        lines = [
            f"Found {len(insights)} insights:",
            f"  Critical: {by_priority['critical']}",
            f"  High: {by_priority['high']}",
            f"  Medium: {by_priority['medium']}",
            f"  Low: {by_priority['low']}",
        ]

        return "\n".join(lines)
