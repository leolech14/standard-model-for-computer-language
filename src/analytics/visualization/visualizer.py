"""
Canonical Visualizer
====================

Main facade that coordinates all visualization components.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import DetectionResults, ArchitectureInsights, FourPillarsMetrics
from .detector import CodeDetector
from .metrics import FourPillarsCalculator
from .insights import InsightsGenerator
from .data_prep import DataPreparator


class CanonicalVisualizer:
    """
    Generates the canonical visualization for the Standard Model of Code.

    Integrates all analysis layers, detections, and metrics into
    a single interactive HTML visualization.
    """

    def __init__(self):
        self.atoms: List[Dict] = []
        self.edges: List[Dict] = []
        self._atom_by_id: Dict[str, Dict] = {}

        # Components
        self._detector = CodeDetector()
        self._calculator = FourPillarsCalculator()
        self._insights_gen = InsightsGenerator()
        self._data_prep = DataPreparator()

        # Results
        self.detections = DetectionResults()
        self.insights = ArchitectureInsights()
        self.pillars = FourPillarsMetrics()

        # Template path
        self.template_path = Path(__file__).parent.parent / "canonical_viz.html"

    def load(self, path: str) -> "CanonicalVisualizer":
        """Load analysis data from JSON file."""
        with open(path) as f:
            data = json.load(f)

        # Extract atoms
        self.atoms = (
            data.get("nodes", []) or
            data.get("atoms", []) or
            data.get("particles", []) or
            []
        )

        # Build fast lookup cache
        self._atom_by_id = {a.get("id", ""): a for a in self.atoms}

        # Extract edges
        self.edges = data.get("edges", [])

        # Extract pre-calculated math coverage
        math = data.get("math_coverage", {})
        if math:
            self._extract_pillars(math)

        # Run initial detections
        self.detections = self._detector.run_detections(self.atoms)

        # Generate initial insights
        self.insights = self._insights_gen.generate(self.atoms, self.detections)

        print(f"Loaded {len(self.atoms)} atoms, {len(self.edges)} edges")
        return self

    def _extract_pillars(self, math: Dict) -> None:
        """Extract 4 Pillars metrics from pre-calculated math_coverage."""
        constructal = math.get("constructal", {})
        self.pillars.omega = constructal.get("omega", 0.0)
        self.pillars.coupling = constructal.get("coupling", 0.0)
        self.pillars.cohesion = constructal.get("cohesion", 0.0)

        markov = math.get("markov", {})
        self.pillars.coderank_max = markov.get("max_coderank", 0.0)
        self.pillars.reachability = markov.get("reachability", 0.0)

        knot = math.get("knot", {})
        self.pillars.spaghetti_score = knot.get("spaghetti_score", 0.0)
        self.pillars.crossing_number = knot.get("crossing_number", 0)
        self.pillars.cycles_count = knot.get("cycles", 0)

        game = math.get("game", {})
        self.pillars.nash_equilibrium = game.get("nash_equilibrium", True)
        self.pillars.conflicts = game.get("conflicts", 0)

    def generate(self, input_path: str, output_path: Optional[str] = None) -> Path:
        """
        Generate the canonical visualization.

        Args:
            input_path: Path to unified_analysis.json
            output_path: Optional output path (defaults to same dir as input)

        Returns:
            Path to generated HTML file
        """
        self.load(input_path)

        # Determine output path
        input_p = Path(input_path)
        if output_path:
            out_path = Path(output_path)
        else:
            out_path = input_p.parent / "canonical_viz.html"

        # Load template
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        template = self.template_path.read_text()

        # Prepare data for injection
        particles_data = self._data_prep.prepare_particles(self.atoms)
        valid_ids = {p["id"] for p in particles_data}
        connections_data = self._data_prep.prepare_connections(self.edges, valid_ids)

        # Calculate all metrics with resolved graph
        self.pillars = self._calculator.calculate(particles_data, connections_data)
        self.detections = self._calculator.get_detections()

        # Merge initial detections (antimatter, god classes)
        initial = self._detector.results
        self.detections.antimatter_violations = initial.antimatter_violations
        self.detections.god_classes = initial.god_classes

        # Regenerate insights with final detections
        self._insights_gen.regenerate(self.detections)
        self.insights = self._insights_gen.insights

        analysis_data = self._data_prep.prepare_analysis(
            self.detections, self.insights, self.pillars
        )

        # Inject data into template
        html = self._inject_data(template, particles_data, connections_data, analysis_data)

        # Write output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html)

        print(f"Generated: {out_path}")
        print(f"  Atoms: {len(self.atoms)}")
        print(f"  Edges: {len(self.edges)}")
        print(f"  Health: {self.insights.health_score:.0f}%")
        print(f"  Coverage: {self.insights.coverage:.1f}%")

        return out_path

    def _inject_data(
        self,
        template: str,
        particles: List[Dict],
        connections: List[Dict],
        analysis: Dict
    ) -> str:
        """Inject data into HTML template."""
        injection = f"""
        /* <!-- DATA_INJECTION_START --> */
        const particles = {json.dumps(particles)};
        const connections = {json.dumps(connections)};
        const analysisData = {json.dumps(analysis)};
        /* <!-- DATA_INJECTION_END --> */
        """

        start_marker = "/* <!-- DATA_INJECTION_START --> */"
        end_marker = "/* <!-- DATA_INJECTION_END --> */"

        start_idx = template.find(start_marker)
        end_idx = template.find(end_marker)

        if start_idx != -1 and end_idx != -1:
            return template[:start_idx] + injection + template[end_idx + len(end_marker):]
        else:
            # Fallback: simple replacement
            return template.replace(
                "const particles = [];",
                f"const particles = {json.dumps(particles)};"
            ).replace(
                "const connections = [];",
                f"const connections = {json.dumps(connections)};"
            ).replace(
                "const analysisData = {};",
                f"const analysisData = {json.dumps(analysis)};"
            )

    def print_report(self) -> None:
        """Print a text report of detections and insights."""
        print("\n" + "=" * 70)
        print("CANONICAL ANALYSIS REPORT")
        print("=" * 70)

        print(f"\n{'─' * 40}")
        print("OVERVIEW")
        print(f"{'─' * 40}")
        print(f"  Atoms:     {len(self.atoms)}")
        print(f"  Edges:     {len(self.edges)}")
        print(f"  Coverage:  {self.insights.coverage:.1f}%")
        print(f"  Health:    {self.insights.health_score:.0f}%")

        print(f"\n{'─' * 40}")
        print("DETECTIONS")
        print(f"{'─' * 40}")
        print(f"  Antimatter violations: {len(self.detections.antimatter_violations)}")
        print(f"  God classes:           {len(self.detections.god_classes)}")
        print(f"  Orphan nodes:          {len(self.detections.orphan_nodes)}")
        print(f"  Coupling hotspots:     {len(self.detections.coupling_hotspots)}")
        print(f"  Hub nodes:             {len(self.detections.hub_nodes)}")

        print(f"\n{'─' * 40}")
        print("4 PILLARS")
        print(f"{'─' * 40}")
        print(f"  Constructal Law:")
        print(f"    Ω (Flow):            {self.pillars.omega:.2f}")
        print(f"    Coupling:            {self.pillars.coupling:.1f}")
        print(f"  Markov Chains:")
        print(f"    Reachability:        {self.pillars.reachability:.1f}%")
        print(f"  Knot Theory:")
        print(f"    Spaghetti Score:     {self.pillars.spaghetti_score:.2f}")
        print(f"    Cycles:              {self.pillars.cycles_count}")
        print(f"  Game Theory:")
        print(f"    Nash Equilibrium:    {'OK' if self.pillars.nash_equilibrium else 'FAIL'}")
        print(f"    Violations:          {self.pillars.conflicts}")

        if self.insights.recommendations:
            print(f"\n{'─' * 40}")
            print("RECOMMENDATIONS")
            print(f"{'─' * 40}")
            for rec in self.insights.recommendations:
                print(f"  • {rec}")

        print()


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python canonical_visualizer.py <analysis.json> [output.html]")
        print("\nGenerates an interactive visualization of the Standard Model analysis.")
        return

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 70)
    print("CANONICAL VISUALIZER - Standard Model of Code")
    print("=" * 70)

    viz = CanonicalVisualizer()
    out = viz.generate(input_path, output_path)
    viz.print_report()

    print(f"\nVisualization: {out}")
    print("Open in browser to explore.")


if __name__ == "__main__":
    main()
