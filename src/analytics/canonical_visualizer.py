#!/usr/bin/env python3
"""
CANONICAL VISUALIZER - Complete Standard Model Visualization
=============================================================

Generates interactive visualizations showing:
- All 8 Progressive Layers (L0-L7)
- All 8 Dimensions (D1-D8)
- All 8 Lenses (R1-R8)
- All 4 Mathematical Pillars
- Detection tools (antimatter, god class, orphans, hotspots, cycles)
- Architecture insights and optimization recommendations

USAGE:
    python canonical_visualizer.py <analysis.json> [output.html]

    # Or programmatically:
    from canonical_visualizer import CanonicalVisualizer
    viz = CanonicalVisualizer()
    viz.generate("unified_analysis.json", "output.html")
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class DetectionResults:
    """Results from all detection tools."""
    antimatter_violations: List[Dict] = field(default_factory=list)
    god_classes: List[Dict] = field(default_factory=list)
    orphan_nodes: List[Dict] = field(default_factory=list)
    coupling_hotspots: List[Dict] = field(default_factory=list)
    dependency_cycles: List[List[str]] = field(default_factory=list)
    hub_nodes: List[Dict] = field(default_factory=list)
    layer_violations: List[Dict] = field(default_factory=list)


@dataclass
class ArchitectureInsights:
    """High-level architecture insights."""
    layer_distribution: Dict[str, int] = field(default_factory=dict)
    role_distribution: Dict[str, int] = field(default_factory=dict)
    health_score: float = 0.0
    coverage: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class FourPillarsMetrics:
    """Metrics from the 4 Mathematical Pillars."""
    # Constructal Law
    omega: float = 0.0
    coupling: float = 0.0
    cohesion: float = 0.0

    # Markov Chains
    stationary: bool = True
    coderank_max: float = 0.0
    reachability: float = 0.0

    # Knot Theory
    spaghetti_score: float = 0.0
    crossing_number: int = 0
    cycles_count: int = 0

    # Game Theory
    nash_equilibrium: bool = True
    strategy: str = "LOOSE"
    conflicts: int = 0


class CanonicalVisualizer:
    """
    Generates the canonical visualization for the Standard Model of Code.

    Integrates all analysis layers, detections, and metrics into
    a single interactive HTML visualization.
    """

    def __init__(self):
        self.atoms: List[Dict] = []
        self.edges: List[Dict] = []
        self.detections = DetectionResults()
        self.insights = ArchitectureInsights()
        self.pillars = FourPillarsMetrics()
        self._atom_by_id: Dict[str, Dict] = {}  # Fast lookup cache

        # Template path
        self.template_path = Path(__file__).parent / "canonical_viz.html"

    # =========================================================================
    # SHARED ALGORITHMS
    # =========================================================================

    @staticmethod
    def _gini_coefficient(values: List[int]) -> float:
        """Calculate Gini coefficient for degree distribution inequality."""
        n = len(values)
        if n == 0:
            return 0.0
        avg = sum(values) / n
        if avg == 0:
            return 0.0
        sorted_vals = sorted(values)
        gini_sum = sum((2 * i - n + 1) * sorted_vals[i] for i in range(n))
        return gini_sum / (n * n * avg)

    @staticmethod
    def _tarjan_scc_iterative(adj: Dict[str, List[str]], nodes: set) -> List[List[str]]:
        """
        Find strongly connected components using iterative Tarjan's algorithm.
        Returns list of SCCs with 2+ nodes (cycles).
        """
        index_counter = 0
        index = {}
        lowlink = {}
        on_stack = set()
        stack = []
        sccs = []

        for start in nodes:
            if start in index:
                continue

            # Iterative DFS with explicit call stack
            call_stack = [(start, 0, iter(adj.get(start, [])))]

            while call_stack:
                node, state, neighbors = call_stack[-1]

                if state == 0:
                    # First visit
                    index[node] = index_counter
                    lowlink[node] = index_counter
                    index_counter += 1
                    stack.append(node)
                    on_stack.add(node)
                    call_stack[-1] = (node, 1, neighbors)

                # Process neighbors
                try:
                    neighbor = next(neighbors)
                    if neighbor not in index:
                        call_stack.append((neighbor, 0, iter(adj.get(neighbor, []))))
                    elif neighbor in on_stack:
                        lowlink[node] = min(lowlink[node], index[neighbor])
                except StopIteration:
                    # All neighbors processed
                    call_stack.pop()

                    if call_stack:
                        parent, _, _ = call_stack[-1]
                        lowlink[parent] = min(lowlink[parent], lowlink[node])

                    if lowlink[node] == index[node]:
                        scc = []
                        while True:
                            w = stack.pop()
                            on_stack.discard(w)
                            scc.append(w)
                            if w == node:
                                break
                        if len(scc) > 1:
                            sccs.append(scc)

        return sccs

    @staticmethod
    def _bfs_components(adj: Dict[str, set], nodes: set) -> List[set]:
        """Find connected components using BFS. Returns list of component sets."""
        visited = set()
        components = []

        for start in nodes:
            if start in visited:
                continue
            component = set()
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                component.add(node)
                for neighbor in adj.get(node, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)
            if component:
                components.append(component)

        return components

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

        # Extract math coverage (fallback if pre-calculated)
        math = data.get("math_coverage", {})
        if math:
            self._extract_pillars(math)

        # Run detections
        self._run_detections()

        # Generate insights
        self._generate_insights()

        print(f"Loaded {len(self.atoms)} atoms, {len(self.edges)} edges")
        return self

    def _extract_pillars(self, math: Dict) -> None:
        """Extract 4 Pillars metrics from math_coverage."""
        # Constructal
        constructal = math.get("constructal", {})
        self.pillars.omega = constructal.get("omega", 0.0)
        self.pillars.coupling = constructal.get("coupling", 0.0)
        self.pillars.cohesion = constructal.get("cohesion", 0.0)

        # Markov
        markov = math.get("markov", {})
        self.pillars.coderank_max = markov.get("max_coderank", 0.0)
        self.pillars.reachability = markov.get("reachability", 0.0)

        # Knot
        knot = math.get("knot", {})
        self.pillars.spaghetti_score = knot.get("spaghetti_score", 0.0)
        self.pillars.crossing_number = knot.get("crossing_number", 0)
        self.pillars.cycles_count = knot.get("cycles", 0)

        # Game
        game = math.get("game", {})
        self.pillars.nash_equilibrium = game.get("nash_equilibrium", True)
        self.pillars.conflicts = game.get("conflicts", 0)

    def _run_detections(self) -> None:
        """Run basic detection tools (antimatter, god classes).
        Orphans/hotspots/hubs calculated later with resolved graph."""
        for atom in self.atoms:
            atom_id = atom.get("id", "")
            role = atom.get("role", "Unknown")
            dims = atom.get("dimensions", {}) or atom.get("L3_DIMENSION", {})
            complexity = atom.get("complexity", 0)

            # Antimatter detection
            d6 = dims.get("D6_EFFECT", "")
            d5 = dims.get("D5_STATE", "")

            if role == "Command" and d6 == "Pure":
                self.detections.antimatter_violations.append({
                    "id": atom_id,
                    "violation": "A1: Command cannot be Pure",
                    "severity": "high"
                })
            if role == "Entity" and d5 == "Stateless":
                self.detections.antimatter_violations.append({
                    "id": atom_id,
                    "violation": "B1: Entity requires state",
                    "severity": "high"
                })
            if role == "Repository" and d6 == "Pure":
                self.detections.antimatter_violations.append({
                    "id": atom_id,
                    "violation": "C1: Repository performs I/O",
                    "severity": "medium"
                })

            # God class detection
            if complexity > 15:
                self.detections.god_classes.append({
                    "id": atom_id,
                    "complexity": complexity,
                    "reason": f"High complexity: {complexity}"
                })

    def _calculate_all_metrics(self, particles: List[Dict], connections: List[Dict]) -> None:
        """
        Calculate all metrics using resolved graph data.
        Single source of truth for 4 Pillars + detections (matches JS).
        """
        n = len(particles)
        e = len(connections)

        if n == 0:
            return

        particle_ids = {p.get("id") for p in particles}
        particle_by_id = {p.get("id"): p for p in particles}

        # Build degree maps
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        for conn in connections:
            out_degree[conn.get("from")] += 1
            in_degree[conn.get("to")] += 1

        # Collect degrees
        degrees = [in_degree.get(p.get("id"), 0) + out_degree.get(p.get("id"), 0) for p in particles]
        avg_degree = sum(degrees) / n

        # === PILLAR 1: Constructal Law ===
        gini = self._gini_coefficient(degrees)
        density = (2 * e) / (n * (n - 1)) if n > 1 else 0
        self.pillars.omega = round(density * 5 + gini * 5, 2)
        self.pillars.coupling = round(avg_degree, 1)

        # === PILLAR 2: Markov Chains (Reachability) ===
        adj_undirected = defaultdict(set)
        for conn in connections:
            src, tgt = conn.get("from"), conn.get("to")
            if src in particle_ids and tgt in particle_ids:
                adj_undirected[src].add(tgt)
                adj_undirected[tgt].add(src)

        components = self._bfs_components(adj_undirected, particle_ids)
        largest = max(len(c) for c in components) if components else 0
        self.pillars.reachability = round((largest / n) * 100, 1)

        # === PILLAR 3: Knot Theory (Cycles) ===
        # Only consider non-containment edges for cycles
        # (contains is hierarchical, not a dependency)
        adj_directed = defaultdict(list)
        for conn in connections:
            if conn.get("type", "").upper() == "CONTAINS":
                continue  # Skip containment edges
            src, tgt = conn.get("from"), conn.get("to")
            if src in particle_ids and tgt in particle_ids:
                adj_directed[src].append(tgt)

        sccs = self._tarjan_scc_iterative(adj_directed, particle_ids)
        cycle_nodes = set(node for scc in sccs for node in scc)
        cycle_ratio = len(cycle_nodes) / n if n > 0 else 0
        edge_ratio = e / n if n > 0 else 0

        self.pillars.spaghetti_score = round(cycle_ratio * 5 + min(edge_ratio, 10) / 2, 2)
        self.pillars.cycles_count = len(sccs)
        self.detections.dependency_cycles = sccs

        # === PILLAR 4: Game Theory (Nash) ===
        LAYER_ORDER = {'Interface': 0, 'Application': 1, 'Core': 2, 'Infrastructure': 1}
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

        # === DETECTIONS ===
        hotspot_threshold = max(avg_degree * 2, 5)
        hub_threshold = max(avg_degree * 1.5, 4)

        self.detections.orphan_nodes = []
        self.detections.coupling_hotspots = []
        self.detections.hub_nodes = []

        for p in particles:
            pid = p.get("id", "")
            in_deg = in_degree.get(pid, 0)
            out_deg = out_degree.get(pid, 0)

            # True orphans: no edges at all
            if in_deg == 0 and out_deg == 0 and p.get("kind") not in ["module", "file"]:
                self.detections.orphan_nodes.append({"id": pid, "reason": "No connections"})

            # Hotspots: high out-degree
            if out_deg > hotspot_threshold:
                self.detections.coupling_hotspots.append({
                    "id": pid, "out_degree": out_deg,
                    "reason": f"Calls {out_deg} components"
                })

            # Hubs: high in-degree
            if in_deg > hub_threshold:
                self.detections.hub_nodes.append({
                    "id": pid, "in_degree": in_deg,
                    "reason": f"Called by {in_deg} components"
                })

    def _regenerate_insights(self) -> None:
        """Regenerate insights after recalculating with resolved graph."""
        # Clear and regenerate recommendations
        self.insights.recommendations = []

        if self.detections.antimatter_violations:
            self.insights.recommendations.append(
                f"Fix {len(self.detections.antimatter_violations)} antimatter violations"
            )
        if self.detections.god_classes:
            self.insights.recommendations.append(
                f"Refactor {len(self.detections.god_classes)} god classes"
            )
        if self.detections.coupling_hotspots:
            self.insights.recommendations.append(
                f"Reduce coupling in {len(self.detections.coupling_hotspots)} hotspots"
            )
        if self.insights.coverage < 80:
            self.insights.recommendations.append(
                f"Improve classification coverage (currently {self.insights.coverage:.1f}%)"
            )

        # Update health score
        issues = (
            len(self.detections.antimatter_violations) * 10 +
            len(self.detections.god_classes) * 5 +
            len(self.detections.coupling_hotspots) * 3 +
            len(self.detections.orphan_nodes) * 1
        )
        self.insights.health_score = max(0, 100 - issues)

    def _generate_insights(self) -> None:
        """Generate high-level architecture insights."""
        # Layer distribution
        for atom in self.atoms:
            layer = atom.get("layer") or atom.get("arch_layer") or "Unknown"
            self.insights.layer_distribution[layer] = \
                self.insights.layer_distribution.get(layer, 0) + 1

        # Role distribution
        for atom in self.atoms:
            role = atom.get("role", "Unknown")
            self.insights.role_distribution[role] = \
                self.insights.role_distribution.get(role, 0) + 1

        # Coverage (classified vs unknown)
        total = len(self.atoms)
        classified = sum(1 for a in self.atoms if a.get("role") != "Unknown")
        self.insights.coverage = (classified / total * 100) if total > 0 else 0

        # Health score
        issues = (
            len(self.detections.antimatter_violations) * 10 +
            len(self.detections.god_classes) * 5 +
            len(self.detections.coupling_hotspots) * 3 +
            len(self.detections.orphan_nodes) * 1
        )
        self.insights.health_score = max(0, 100 - issues)

        # Recommendations
        if self.detections.antimatter_violations:
            self.insights.recommendations.append(
                f"Fix {len(self.detections.antimatter_violations)} antimatter violations"
            )
        if self.detections.god_classes:
            self.insights.recommendations.append(
                f"Refactor {len(self.detections.god_classes)} god classes"
            )
        if self.detections.coupling_hotspots:
            self.insights.recommendations.append(
                f"Reduce coupling in {len(self.detections.coupling_hotspots)} hotspots"
            )
        if self.insights.coverage < 80:
            self.insights.recommendations.append(
                f"Improve classification coverage (currently {self.insights.coverage:.1f}%)"
            )

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
        particles_data = self._prepare_particles()
        valid_ids = {p["id"] for p in particles_data}
        connections_data = self._prepare_connections(valid_ids)

        # Calculate all metrics with resolved graph (matches JS)
        self._calculate_all_metrics(particles_data, connections_data)

        # Regenerate insights with final detections
        self._regenerate_insights()

        analysis_data = self._prepare_analysis()

        # Inject data
        injection = f"""
        /* <!-- DATA_INJECTION_START --> */
        const particles = {json.dumps(particles_data)};
        const connections = {json.dumps(connections_data)};
        const analysisData = {json.dumps(analysis_data)};
        /* <!-- DATA_INJECTION_END --> */
        """

        # Replace injection block
        start_marker = "/* <!-- DATA_INJECTION_START --> */"
        end_marker = "/* <!-- DATA_INJECTION_END --> */"

        start_idx = template.find(start_marker)
        end_idx = template.find(end_marker)

        if start_idx != -1 and end_idx != -1:
            html = template[:start_idx] + injection + template[end_idx + len(end_marker):]
        else:
            # Fallback: simple replacement
            html = template.replace(
                "const particles = [];",
                f"const particles = {json.dumps(particles_data)};"
            ).replace(
                "const connections = [];",
                f"const connections = {json.dumps(connections_data)};"
            ).replace(
                "const analysisData = {};",
                f"const analysisData = {json.dumps(analysis_data)};"
            )

        # Write output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html)

        print(f"Generated: {out_path}")
        print(f"  Atoms: {len(self.atoms)}")
        print(f"  Edges: {len(self.edges)}")
        print(f"  Health: {self.insights.health_score:.0f}%")
        print(f"  Coverage: {self.insights.coverage:.1f}%")

        return out_path

    def _prepare_particles(self) -> List[Dict]:
        """Prepare atom data for visualization (deduplicated)."""
        seen_ids = set()
        particles = []

        for i, a in enumerate(self.atoms):
            atom_id = a.get("id", f"atom_{i}")

            # Deduplicate - skip if we've seen this ID
            if atom_id in seen_ids:
                continue
            seen_ids.add(atom_id)

            particles.append({
                "id": atom_id,
                "label": a.get("name", atom_id.split(":")[-1] if ":" in atom_id else atom_id)[:30],
                "layer": a.get("layer") or a.get("arch_layer") or "Unknown",
                "role": a.get("role", "Unknown"),
                "kind": a.get("kind", "unknown"),
                "file": a.get("file_path") or a.get("file", ""),
                "complexity": a.get("complexity", 1),
                "dimensions": a.get("dimensions") or a.get("L3_DIMENSION", {}),
                "lenses": a.get("lenses") or a.get("L4_LENS", {}),
                "math": a.get("math") or a.get("L6_MATH", {}),
                "in_degree": a.get("in_degree", 0),
                "out_degree": a.get("out_degree", 0),
                "is_orphan": a.get("in_degree", 0) == 0,
                "is_hotspot": a.get("out_degree", 0) > 8
            })

        return particles

    def _prepare_connections(self, valid_ids: set) -> List[Dict]:
        """Prepare edge data for visualization (deduplicated, validated)."""
        seen_edges = set()
        connections = []

        # Build comprehensive name -> ID lookup for fuzzy matching
        # Use lists to handle duplicate short names
        name_to_ids = defaultdict(list)  # name -> list of matching IDs
        module_to_ids = defaultdict(list)  # module name -> list of atom IDs in that module

        for vid in valid_ids:
            # Store full ID (always unique)
            name_to_ids[vid].append(vid)

            # Extract short name from full ID (e.g., "function_name" from "/path/file.py:function_name")
            if ":" in vid:
                short = vid.split(":")[-1]
                name_to_ids[short].append(vid)

            # Store filename:name format
            if "/" in vid and ":" in vid:
                parts = vid.rsplit("/", 1)[-1]  # file.py:Name
                name_to_ids[parts].append(vid)

            # Map module name (file basename without extension) to all its atoms
            if "/" in vid:
                file_part = vid.rsplit("/", 1)[-1]  # file.py:Name or file.py
                if ":" in file_part:
                    module_name = file_part.split(":")[0].rsplit(".", 1)[0]  # "file" from "file.py:Name"
                else:
                    module_name = file_part.rsplit(".", 1)[0]  # "file" from "file.py"
                module_to_ids[module_name].append(vid)
                name_to_ids[module_name].append(vid)

        for e in self.edges:
            src = e.get("source") or e.get("from")
            tgt = e.get("target") or e.get("to")

            if not src or not tgt:
                continue

            # Try to resolve to valid IDs with multiple strategies
            resolved_src = self._resolve_edge_id(src, name_to_ids, module_to_ids)
            resolved_tgt = self._resolve_edge_id(tgt, name_to_ids, module_to_ids)

            if not resolved_src or not resolved_tgt:
                continue

            # Deduplicate edges
            edge_key = (resolved_src, resolved_tgt)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)

            connections.append({
                "from": resolved_src,
                "to": resolved_tgt,
                "type": e.get("edge_type") or e.get("type", "CALLS")
            })

        return connections

    def _resolve_edge_id(self, ref: str, name_to_ids: Dict, module_to_ids: Dict) -> Optional[str]:
        """Resolve an edge reference to a valid node ID."""
        # Direct match (full ID)
        if ref in name_to_ids and name_to_ids[ref]:
            return name_to_ids[ref][0]

        # Try module.function format first (most specific)
        # e.g., "core.intent_detector._enrich_with_why" -> intent_detector module, _enrich_with_why func
        if "." in ref:
            parts = ref.split(".")
            if len(parts) >= 2:
                module = parts[-2]
                func = parts[-1]
                # Find atoms in this module with this function name
                candidates = module_to_ids.get(module, [])
                for cid in candidates:
                    if cid.endswith(f":{func}"):
                        return cid

        # Try last part after dot (less specific, may have duplicates)
        if "." in ref:
            last_part = ref.split(".")[-1]
            if last_part in name_to_ids and name_to_ids[last_part]:
                # If only one match, use it; otherwise need module context
                matches = name_to_ids[last_part]
                if len(matches) == 1:
                    return matches[0]
                # Multiple matches - try to use module hint from ref
                if len(ref.split(".")) >= 2:
                    module_hint = ref.split(".")[-2]
                    for m in matches:
                        if module_hint in m:
                            return m
                # Fall back to first match
                return matches[0]

        # Try short name directly
        if ref in name_to_ids and name_to_ids[ref]:
            return name_to_ids[ref][0]

        # Try as module name only (for external refs like "os", "json", etc.)
        if ref in module_to_ids and module_to_ids[ref]:
            return module_to_ids[ref][0]

        return None

    def _prepare_analysis(self) -> Dict:
        """Prepare analysis metadata."""
        return {
            "detections": {
                "antimatter": len(self.detections.antimatter_violations),
                "god_classes": len(self.detections.god_classes),
                "orphans": len(self.detections.orphan_nodes),
                "hotspots": len(self.detections.coupling_hotspots),
                "hubs": len(self.detections.hub_nodes),
                "cycles": len(self.detections.dependency_cycles)
            },
            "insights": {
                "health_score": self.insights.health_score,
                "coverage": self.insights.coverage,
                "layer_distribution": self.insights.layer_distribution,
                "role_distribution": self.insights.role_distribution,
                "recommendations": self.insights.recommendations
            },
            "pillars": {
                "omega": self.pillars.omega,
                "coupling": self.pillars.coupling,
                "cohesion": self.pillars.cohesion,
                "spaghetti_score": self.pillars.spaghetti_score,
                "crossing_number": self.pillars.crossing_number,
                "cycles": self.pillars.cycles_count,
                "nash_equilibrium": self.pillars.nash_equilibrium,
                "coderank_max": self.pillars.coderank_max,
                "reachability": self.pillars.reachability
            }
        }

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


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python canonical_visualizer.py <analysis.json> [output.html]")
        print("\nGenerates an interactive visualization of the Standard Model analysis.")
        print("\nExamples:")
        print("  python canonical_visualizer.py unified_analysis.json")
        print("  python canonical_visualizer.py output/analysis.json viz.html")
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
