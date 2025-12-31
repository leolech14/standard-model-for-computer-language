"""
Architecture Insights Generator
===============================

Generates high-level architecture insights from analysis data.
"""

from typing import List, Dict

from .models import ArchitectureInsights, DetectionResults


class InsightsGenerator:
    """Generates architecture insights from atoms and detections."""

    def __init__(self):
        self.insights = ArchitectureInsights()

    def generate(
        self,
        atoms: List[Dict],
        detections: DetectionResults
    ) -> ArchitectureInsights:
        """Generate insights from atoms and detection results."""
        self.insights = ArchitectureInsights()

        self._calculate_distributions(atoms)
        self._calculate_coverage(atoms)
        self._calculate_health_score(detections)
        self._generate_recommendations(detections)

        return self.insights

    def _calculate_distributions(self, atoms: List[Dict]) -> None:
        """Calculate layer and role distributions."""
        for atom in atoms:
            # Layer distribution
            layer = atom.get("layer") or atom.get("arch_layer") or "Unknown"
            self.insights.layer_distribution[layer] = \
                self.insights.layer_distribution.get(layer, 0) + 1

            # Role distribution
            role = atom.get("role", "Unknown")
            self.insights.role_distribution[role] = \
                self.insights.role_distribution.get(role, 0) + 1

    def _calculate_coverage(self, atoms: List[Dict]) -> None:
        """Calculate classification coverage."""
        total = len(atoms)
        classified = sum(1 for a in atoms if a.get("role") != "Unknown")
        self.insights.coverage = (classified / total * 100) if total > 0 else 0

    def _calculate_health_score(self, detections: DetectionResults) -> None:
        """Calculate overall health score based on issues."""
        issues = (
            len(detections.antimatter_violations) * 10 +
            len(detections.god_classes) * 5 +
            len(detections.coupling_hotspots) * 3 +
            len(detections.orphan_nodes) * 1
        )
        self.insights.health_score = max(0, 100 - issues)

    def _generate_recommendations(self, detections: DetectionResults) -> None:
        """Generate actionable recommendations."""
        self.insights.recommendations = []

        if detections.antimatter_violations:
            self.insights.recommendations.append(
                f"Fix {len(detections.antimatter_violations)} antimatter violations"
            )

        if detections.god_classes:
            self.insights.recommendations.append(
                f"Refactor {len(detections.god_classes)} god classes"
            )

        if detections.coupling_hotspots:
            self.insights.recommendations.append(
                f"Reduce coupling in {len(detections.coupling_hotspots)} hotspots"
            )

        if self.insights.coverage < 80:
            self.insights.recommendations.append(
                f"Improve classification coverage (currently {self.insights.coverage:.1f}%)"
            )

    def regenerate(self, detections: DetectionResults) -> None:
        """Regenerate recommendations after metrics recalculation."""
        self._calculate_health_score(detections)
        self._generate_recommendations(detections)
