"""
Four Pillars Metrics Calculator
===============================

Calculates metrics for the 4 Mathematical Pillars:
1. Constructal Law (flow optimization)
2. Markov Chains (reachability)
3. Knot Theory (cycles/spaghetti)
4. Game Theory (Nash equilibrium)
"""

from typing import List, Dict
from collections import defaultdict

from .models import FourPillarsMetrics, DetectionResults
from .algorithms import gini_coefficient, tarjan_scc_iterative, bfs_components
from .detector import CodeDetector


# Layer order for Game Theory violations
LAYER_ORDER = {
    'Interface': 0,
    'Application': 1,
    'Core': 2,
    'Infrastructure': 1
}


class FourPillarsCalculator:
    """Calculates all 4 Pillars metrics from graph data."""

    def __init__(self):
        self.pillars = FourPillarsMetrics()
        self.detector = CodeDetector()

    def calculate(
        self,
        particles: List[Dict],
        connections: List[Dict]
    ) -> FourPillarsMetrics:
        """
        Calculate all metrics using resolved graph data.
        Single source of truth for 4 Pillars + detections.
        """
        n = len(particles)
        e = len(connections)

        if n == 0:
            return self.pillars

        particle_ids = {p.get("id") for p in particles}
        particle_by_id = {p.get("id"): p for p in particles}

        # Build degree maps
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        for conn in connections:
            out_degree[conn.get("from")] += 1
            in_degree[conn.get("to")] += 1

        # Collect degrees
        degrees = [
            in_degree.get(p.get("id"), 0) + out_degree.get(p.get("id"), 0)
            for p in particles
        ]
        avg_degree = sum(degrees) / n

        # === PILLAR 1: Constructal Law ===
        self._calculate_constructal(degrees, n, e)

        # === PILLAR 2: Markov Chains (Reachability) ===
        self._calculate_markov(connections, particle_ids, n)

        # === PILLAR 3: Knot Theory (Cycles) ===
        sccs = self._calculate_knot(connections, particle_ids, n, e)

        # === PILLAR 4: Game Theory (Nash) ===
        self._calculate_game_theory(connections, particle_by_id)

        # === Graph-based detections ===
        hotspot_threshold = max(avg_degree * 2, 5)
        hub_threshold = max(avg_degree * 1.5, 4)

        self.detector.detect_graph_issues(
            particles, in_degree, out_degree,
            hotspot_threshold, hub_threshold
        )
        self.detector.results.dependency_cycles = sccs

        return self.pillars

    def _calculate_constructal(
        self,
        degrees: List[int],
        n: int,
        e: int
    ) -> None:
        """Calculate Constructal Law metrics (Pillar 1)."""
        gini = gini_coefficient(degrees)
        density = (2 * e) / (n * (n - 1)) if n > 1 else 0
        avg_degree = sum(degrees) / n if n > 0 else 0

        self.pillars.omega = round(density * 5 + gini * 5, 2)
        self.pillars.coupling = round(avg_degree, 1)

    def _calculate_markov(
        self,
        connections: List[Dict],
        particle_ids: set,
        n: int
    ) -> None:
        """Calculate Markov Chains metrics (Pillar 2)."""
        adj_undirected = defaultdict(set)
        for conn in connections:
            src, tgt = conn.get("from"), conn.get("to")
            if src in particle_ids and tgt in particle_ids:
                adj_undirected[src].add(tgt)
                adj_undirected[tgt].add(src)

        components = bfs_components(adj_undirected, particle_ids)
        largest = max(len(c) for c in components) if components else 0
        self.pillars.reachability = round((largest / n) * 100, 1)

    def _calculate_knot(
        self,
        connections: List[Dict],
        particle_ids: set,
        n: int,
        e: int
    ) -> List[List[str]]:
        """Calculate Knot Theory metrics (Pillar 3). Returns SCCs."""
        # Only consider non-containment edges for cycles
        adj_directed = defaultdict(list)
        for conn in connections:
            if conn.get("type", "").upper() == "CONTAINS":
                continue  # Skip containment edges
            src, tgt = conn.get("from"), conn.get("to")
            if src in particle_ids and tgt in particle_ids:
                adj_directed[src].append(tgt)

        sccs = tarjan_scc_iterative(adj_directed, particle_ids)
        cycle_nodes = set(node for scc in sccs for node in scc)
        cycle_ratio = len(cycle_nodes) / n if n > 0 else 0
        edge_ratio = e / n if n > 0 else 0

        self.pillars.spaghetti_score = round(
            cycle_ratio * 5 + min(edge_ratio, 10) / 2, 2
        )
        self.pillars.cycles_count = len(sccs)

        return sccs

    def _calculate_game_theory(
        self,
        connections: List[Dict],
        particle_by_id: Dict[str, Dict]
    ) -> None:
        """Calculate Game Theory metrics (Pillar 4)."""
        violations = 0

        for conn in connections:
            src_p = particle_by_id.get(conn.get("from"))
            tgt_p = particle_by_id.get(conn.get("to"))

            if src_p and tgt_p:
                src_order = LAYER_ORDER.get(src_p.get("layer", ""), -1)
                tgt_order = LAYER_ORDER.get(tgt_p.get("layer", ""), -1)

                if src_order >= 0 and tgt_order >= 0:
                    if src_order > tgt_order and src_p.get("layer") != 'Infrastructure':
                        violations += 1

        self.pillars.conflicts = violations
        self.pillars.nash_equilibrium = violations == 0

    def get_detections(self) -> DetectionResults:
        """Get detection results after calculation."""
        return self.detector.results
