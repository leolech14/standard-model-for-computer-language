
from typing import List, Dict, Any, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field
import statistics
import math


@dataclass
class BettiNumbers:
    """Topological invariants for the code graph.

    Attributes:
        b0: Number of connected components (islands)
        b1: Number of independent cycles (circular dependencies)
        euler_characteristic: χ = b0 - b1 (topological signature)
    """
    b0: int  # Connected components
    b1: int  # Independent cycles

    @property
    def euler_characteristic(self) -> int:
        """χ = b0 - b1. Healthy code typically has χ ≈ 1."""
        return self.b0 - self.b1

    @property
    def health_signal(self) -> str:
        """Interpret Betti numbers for code health."""
        if self.b0 > 1 and self.b1 > 0:
            return "FRAGMENTED_CYCLIC"  # Islands + cycles = worst
        elif self.b0 > 1:
            return "FRAGMENTED"  # Disconnected but no cycles
        elif self.b1 > 5:
            return "HIGHLY_CYCLIC"  # Many circular dependencies
        elif self.b1 > 0:
            return "CYCLIC"  # Some circular dependencies
        else:
            return "ACYCLIC"  # Ideal: connected, no cycles


@dataclass
class ElevationResult:
    """Elevation analysis for a single node."""
    node_id: str
    elevation: float
    components: Dict[str, float] = field(default_factory=dict)


class ElevationModel:
    """Computes node elevation from code metrics.

    Elevation encodes structural complexity - how difficult a node is
    to understand or modify. Higher elevation = harder terrain.

    Components:
        - cyclomatic: Control flow complexity (30%)
        - coupling: Fan-out dependencies (30%)
        - size: Lines of code (20%)
        - maintainability: Composite quality metric (20%)
    """

    DEFAULT_WEIGHTS = {
        'cyclomatic': 0.3,
        'coupling': 0.3,
        'size': 0.2,
        'maintainability': 0.2
    }

    def __init__(self, weights: Dict[str, float] | None = None):
        self.weights = weights if weights is not None else self.DEFAULT_WEIGHTS

    def compute_elevation(self, metrics: Dict[str, Any]) -> float:
        """
        Compute elevation for a single node.

        Args:
            metrics: dict with keys:
                - cyclomatic_complexity (int): Control flow complexity
                - fan_out (int): Number of outgoing dependencies
                - loc (int): Lines of code
                - maintainability_index (float, 0-100): Quality score

        Returns:
            float: elevation value (typically 0-10 scale, can exceed)
        """
        cc = metrics.get('cyclomatic_complexity', 1)
        fo = metrics.get('fan_out', 0)
        loc = metrics.get('loc', 50)
        mi = metrics.get('maintainability_index', 80)

        # Component contributions (see LANDSCAPE_IMPLEMENTATION_GUIDE.md)
        cc_elev = math.log(max(1, cc / 5)) if cc > 0 else 0
        fo_elev = max(0, (fo - 8) ** 2) / 16 if fo > 8 else 0
        loc_elev = math.log(loc / 100) if loc > 100 else 0
        mi_elev = -(mi - 80) / 20

        # Weighted sum, normalized to [0, 10] with baseline at 5
        total = (
            self.weights['cyclomatic'] * cc_elev +
            self.weights['coupling'] * fo_elev +
            self.weights['size'] * loc_elev +
            self.weights['maintainability'] * mi_elev
        )

        return max(0, total + 5)

    def compute_elevation_map(
        self,
        nodes: List[Dict],
        edges: List[Dict]
    ) -> Dict[str, ElevationResult]:
        """
        Compute elevation for all nodes in a graph.

        Args:
            nodes: List of node dicts with 'id' and optional metrics
            edges: List of edge dicts with 'source' and 'target'

        Returns:
            Dict mapping node_id to ElevationResult
        """
        # Compute fan-out from edges
        fan_out = defaultdict(int)
        for edge in edges:
            fan_out[edge.get('source', '')] += 1

        result = {}
        for node in nodes:
            node_id = node.get('id', '')
            metrics = {
                'cyclomatic_complexity': node.get('cyclomatic_complexity', 1),
                'fan_out': fan_out[node_id],
                'loc': node.get('loc', node.get('line_count', 50)),
                'maintainability_index': node.get('maintainability_index', 80)
            }

            elevation = self.compute_elevation(metrics)
            result[node_id] = ElevationResult(
                node_id=node_id,
                elevation=elevation,
                components=metrics
            )

        return result


@dataclass
class LandscapeProfile:
    """Complete topological analysis of a codome."""

    # Topology (Betti numbers)
    b0: int  # Connected components
    b1: int  # Independent cycles

    # Elevation data
    elevations: Dict[str, float] = field(default_factory=dict)

    # Gradients
    gradients: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def euler_characteristic(self) -> int:
        """χ = b₀ - b₁."""
        return self.b0 - self.b1

    @property
    def has_cycles(self) -> bool:
        return self.b1 > 0

    @property
    def peaks(self) -> List[str]:
        """Nodes with elevation > 8 (complexity hotspots)."""
        return [nid for nid, elev in self.elevations.items() if elev > 8]

    @property
    def valleys(self) -> List[str]:
        """Nodes with elevation < 4 (well-designed areas)."""
        return [nid for nid, elev in self.elevations.items() if elev < 4]


class LandscapeHealthIndex:
    """Computes overall landscape health from topological metrics.

    Health Index (0-10 scale):
        - 9-10: A grade (excellent architecture)
        - 8-9:  B grade (good architecture)
        - 7-8:  C grade (acceptable)
        - 5-7:  D grade (needs improvement)
        - <5:   F grade (major issues)

    Components:
        - cycles (25%): Freedom from circular dependencies
        - elevation (25%): Low average complexity
        - gradients (25%): Dependencies flow downhill
        - coupling (15%): Low fan-out
        - isolation (10%): Appropriate modularity
    """

    DEFAULT_WEIGHTS = {
        'cycles': 0.25,
        'elevation': 0.25,
        'gradients': 0.25,
        'coupling': 0.15,
        'isolation': 0.10
    }

    def __init__(self, weights: Dict[str, float] | None = None):
        self.weights = weights if weights is not None else self.DEFAULT_WEIGHTS

    def compute(self, profile: LandscapeProfile) -> Dict[str, Any]:
        """
        Compute health index from landscape profile.

        Args:
            profile: LandscapeProfile with topology and elevation data

        Returns:
            dict with 'index', 'grade', 'component_scores'
        """
        node_count = len(profile.elevations) if profile.elevations else 1
        scores = {
            'cycles': self._cycle_health(profile.b1, node_count),
            'elevation': self._elevation_health(profile.elevations),
            'gradients': self._gradient_health(profile.gradients),
            'coupling': self._coupling_health(profile),
            'isolation': self._isolation_health(profile.b0, node_count)
        }

        index = sum(scores[k] * self.weights[k] for k in scores)

        return {
            'index': round(index, 2),
            'grade': self._to_grade(index),
            'component_scores': {k: round(v, 2) for k, v in scores.items()}
        }

    def _cycle_health(self, b1: int, node_count: int) -> float:
        """b₁ = 0 is perfect (10), degrades as cycle ratio increases.

        Normalized by codebase size: cycle_ratio = b1 / nodes
        - ratio < 0.5: excellent (score 8-10)
        - ratio 0.5-1.0: good (score 6-8)
        - ratio 1.0-2.0: moderate (score 4-6)
        - ratio > 2.0: concerning (score 2-4)

        Uses logarithmic scaling to avoid harsh penalties for large codebases.
        """
        if b1 == 0:
            return 10.0

        # Normalize by codebase size
        cycle_ratio = b1 / max(1, node_count)

        # Logarithmic scaling: log(1 + ratio) grows slowly for large ratios
        # Scale factor of 3 maps ratio=1.0 to ~2.1 penalty, ratio=2.0 to ~3.3 penalty
        penalty = math.log1p(cycle_ratio) * 3.0

        return max(1.0, min(10.0, 10.0 - penalty))

    def _elevation_health(self, elevations: Dict[str, float]) -> float:
        """Lower average elevation = healthier."""
        if not elevations:
            return 5.0
        avg = sum(elevations.values()) / len(elevations)
        return max(0, 10.0 - avg)

    def _gradient_health(self, gradients: List[Dict[str, Any]]) -> float:
        """Fewer problematic gradients = healthier."""
        if not gradients:
            return 5.0
        problematic = sum(1 for g in gradients if g.get('risk') == 'HIGH')
        ratio = problematic / len(gradients)
        return max(1.0, 10.0 - (ratio * 10))

    def _coupling_health(self, profile: LandscapeProfile) -> float:
        """Lower average fan-out = healthier."""
        if not profile.elevations:
            return 5.0
        # Use elevation as proxy for coupling (high elevation often means high coupling)
        avg_elev = sum(profile.elevations.values()) / len(profile.elevations)
        return max(3.0, 10.0 - (avg_elev * 0.5))

    def _isolation_health(self, b0: int, n: int) -> float:
        """Measure component cohesion.

        Uses nodes-per-component ratio:
        - ratio 10-50: excellent (well-organized modules)
        - ratio 5-10 or 50-100: good
        - ratio < 5: too fragmented (many tiny components)
        - ratio > 100: monolithic (too few components)

        Single component (b0=1) is acceptable for small codebases but
        concerning for large ones.
        """
        if n == 0:
            return 5.0
        if b0 == 0:
            return 5.0  # Edge case

        # Nodes per component
        nodes_per_component = n / b0

        # Ideal range: 10-50 nodes per component
        if 10 <= nodes_per_component <= 50:
            return 10.0
        elif 5 <= nodes_per_component < 10 or 50 < nodes_per_component <= 100:
            return 8.0
        elif nodes_per_component < 5:
            # Too fragmented - penalize logarithmically
            fragmentation = 5 / nodes_per_component  # How many times worse than ideal
            return max(3.0, 10.0 - math.log1p(fragmentation) * 2)
        else:
            # Too monolithic (> 100 nodes/component)
            monolith_ratio = nodes_per_component / 50  # How many times worse than ideal
            return max(3.0, 10.0 - math.log1p(monolith_ratio) * 2)

    def _to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 9.0:
            return 'A'
        elif score >= 8.0:
            return 'B'
        elif score >= 7.0:
            return 'C'
        elif score >= 5.0:
            return 'D'
        else:
            return 'F'


def compute_gradient(source_elev: float, target_elev: float) -> Dict[str, Any]:
    """
    Compute gradient along a dependency edge.

    Positive gradient = depending on MORE complex code (uphill, bad)
    Negative gradient = depending on LESS complex code (downhill, good)

    Args:
        source_elev: Elevation of the source node
        target_elev: Elevation of the target node

    Returns:
        Dict with gradient value and classification
    """
    gradient = target_elev - source_elev

    if gradient > 2:
        direction = "STEEP_UPHILL"
        risk = "HIGH"
    elif gradient > 0:
        direction = "UPHILL"
        risk = "MEDIUM"
    elif gradient > -2:
        direction = "DOWNHILL"
        risk = "LOW"
    else:
        direction = "STEEP_DOWNHILL"
        risk = "MINIMAL"

    return {
        "gradient": round(gradient, 2),
        "direction": direction,
        "risk": risk
    }


class TopologyClassifier:
    """
    Analyzes the 'visual' shape of a software graph to help LLMs 'see' the architecture.
    Classifies into patterns like:
    - DISCONNECTED_ISLANDS: Many separate clusters
    - BIG_BALL_OF_MUD: High density, high tangles, no hierarchy
    - STAR_HUB: One massive central node (god object)
    - STRICT_LAYERS: Clear directional flow, low cycles
    - MESH: High connectivity but balanced
    """

    def classify(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """
        Classify the graph topology into architectural patterns.

        Args:
            nodes: List of node dictionaries with 'id' keys
            edges: List of edge dictionaries with 'source' and 'target' keys

        Returns:
            Dictionary with 'shape', 'description', and 'visual_metrics'
        """
        if not nodes:
            return {"shape": "EMPTY", "description": "No nodes found"}

        # 1. Betti Number Analysis (Topological Invariants)
        betti = self.compute_betti_numbers(nodes, edges)
        num_components = betti.b0
        num_cycles = betti.b1

        # Component size analysis
        components = self._find_components(nodes, edges)
        largest_component_size = max(len(c) for c in components) if components else 0
        percent_in_largest = (largest_component_size / len(nodes)) * 100

        # 2. Centrality Analysis (Hubs)
        in_degrees = defaultdict(int)
        out_degrees = defaultdict(int)
        for edge in edges:
            in_degrees[edge.get('target', '')] += 1
            out_degrees[edge.get('source', '')] += 1

        degrees = [in_degrees[n['id']] + out_degrees[n['id']] for n in nodes]
        max_degree = max(degrees) if degrees else 0
        avg_degree = statistics.mean(degrees) if degrees else 0
        # Centralization: How much is the graph dominated by one node?
        # (Simplified Freeman centralization)
        centralization = sum(max_degree - d for d in degrees) / ((len(nodes) - 1) * (len(nodes) - 2)) if len(nodes) > 2 else 0

        # 3. Hierarchy Analysis (Layers vs Cycles)
        # We can reuse Knot Score from existing analysis, but calculate a hierarchy score
        # Simple proxy: Ratio of feedback edges (cycles) to feedforward edges

        # 4. Classification Logic
        shape = "UNKNOWN"
        description = "Undefined structure"

        # Check STRICT_LAYERS first (ideal state: connected, no cycles)
        if num_cycles == 0 and num_components == 1:
            shape = "STRICT_LAYERS"
            description = "Acyclic layered architecture. Clean dependency flow."

        elif num_components > 5 and percent_in_largest < 50:
            shape = "DISCONNECTED_ISLANDS"
            description = f"Fragmented into {num_components} separate clusters."

        elif num_cycles > 10 and avg_degree > 5:
            shape = "BIG_BALL_OF_MUD"
            description = f"High coupling with {num_cycles} cycles. Tangled dependencies."

        elif centralization > 0.4 and len(nodes) > 10:
            # Only flag STAR_HUB for larger graphs to avoid false positives
            top_hub_id = max(nodes, key=lambda n: in_degrees[n['id']] + out_degrees[n['id']])['id']
            hub_name = top_hub_id.split(':')[-1]
            shape = "STAR_HUB"
            description = f"Dominated by central hub '{hub_name}' (Star Topology)."

        elif avg_degree > 10:
            shape = "DENSE_MESH"
            description = "Highly interconnected mesh."

        elif num_cycles > 0:
            shape = "CYCLIC_NETWORK"
            description = f"Connected with {num_cycles} dependency cycles."

        else:
            shape = "BALANCED_NETWORK"
            description = "Connected network with distributed responsibility."

        return {
            "shape": shape,
            "description": description,
            "betti_numbers": {
                "b0": betti.b0,
                "b1": betti.b1,
                "euler_characteristic": betti.euler_characteristic,
                "health_signal": betti.health_signal
            },
            "visual_metrics": {
                "components": num_components,
                "cycles": num_cycles,
                "largest_cluster_percent": round(percent_in_largest, 1),
                "centralization_score": round(centralization, 2),
                "density_score": round(avg_degree, 2)
            }
        }

    def _find_components(self, nodes: List[Dict], edges: List[Dict]) -> List[List[str]]:
        # Undirected component finding
        adj = defaultdict(set)
        for edge in edges:
            s, t = edge.get('source'), edge.get('target')
            if s and t:
                adj[s].add(t)
                adj[t].add(s)

        visited = set()
        components = []

        node_ids = set(n['id'] for n in nodes)

        for node in node_ids:
            if node not in visited:
                component = []
                queue = deque([node])
                visited.add(node)
                while queue:
                    curr = queue.popleft()
                    component.append(curr)
                    for neighbor in adj[curr]:
                        if neighbor in node_ids and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(component)

        return components

    def compute_betti_numbers(self, nodes: List[Dict], edges: List[Dict]) -> BettiNumbers:
        """
        Compute Betti numbers for the code graph.

        b₀ = Number of connected components
        b₁ = Number of independent cycles (using Euler characteristic: b₁ = |E| - |V| + b₀)

        For directed graphs, we treat edges as undirected for topological analysis.
        This gives us the "shape" of the dependency structure.

        Args:
            nodes: List of node dictionaries with 'id' keys
            edges: List of edge dictionaries with 'source' and 'target' keys

        Returns:
            BettiNumbers with b0 and b1
        """
        if not nodes:
            return BettiNumbers(b0=0, b1=0)

        # b₀: Count connected components
        components = self._find_components(nodes, edges)
        b0 = len(components)

        # b₁: Use Euler characteristic formula for graphs
        # For undirected graph: b₁ = |E| - |V| + b₀
        # We deduplicate edges (treat directed as undirected)
        unique_edges = set()
        for edge in edges:
            s, t = edge.get('source'), edge.get('target')
            if s and t:
                # Normalize edge direction for undirected comparison
                unique_edges.add((min(s, t), max(s, t)))

        num_edges = len(unique_edges)
        num_vertices = len(nodes)

        # b₁ = E - V + C (Euler formula for graphs)
        # This counts independent cycles
        b1 = max(0, num_edges - num_vertices + b0)

        return BettiNumbers(b0=b0, b1=b1)

    def _find_strongly_connected_components(self, nodes: List[Dict], edges: List[Dict]) -> List[List[str]]:
        """
        Find strongly connected components using Tarjan's algorithm.
        Used for detecting directed cycles in dependency graphs.

        Returns:
            List of SCCs (each SCC with >1 node indicates a cycle)
        """
        node_ids = [n['id'] for n in nodes]
        adj = defaultdict(list)
        for edge in edges:
            s, t = edge.get('source'), edge.get('target')
            if s and t:
                adj[s].append(t)

        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        sccs = []

        def strongconnect(v):
            index[v] = index_counter[0]
            lowlinks[v] = index_counter[0]
            index_counter[0] += 1
            stack.append(v)
            on_stack[v] = True

            for w in adj[v]:
                if w not in index:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif on_stack.get(w, False):
                    lowlinks[v] = min(lowlinks[v], index[w])

            if lowlinks[v] == index[v]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == v:
                        break
                sccs.append(scc)

        for v in node_ids:
            if v not in index:
                strongconnect(v)

        return sccs

    def count_directed_cycles(self, nodes: List[Dict], edges: List[Dict]) -> int:
        """
        Count the number of nodes involved in directed cycles.
        Nodes in SCCs of size > 1 are in cycles.

        Returns:
            Number of nodes participating in cycles
        """
        sccs = self._find_strongly_connected_components(nodes, edges)
        # SCCs with more than one node indicate cycles
        cyclic_nodes = sum(len(scc) for scc in sccs if len(scc) > 1)
        return cyclic_nodes
