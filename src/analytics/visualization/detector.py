"""
Code Detector
=============

Detects antimatter violations, god classes, and other code smells.
"""

from typing import List, Dict

from .models import DetectionResults


class CodeDetector:
    """Detects code quality issues in atoms."""

    def __init__(self):
        self.results = DetectionResults()

    def run_detections(self, atoms: List[Dict]) -> DetectionResults:
        """Run all detection tools on atoms."""
        self.results = DetectionResults()

        for atom in atoms:
            self._detect_antimatter(atom)
            self._detect_god_class(atom)

        return self.results

    def _detect_antimatter(self, atom: Dict) -> None:
        """Detect antimatter violations (contradictory role/dimension)."""
        atom_id = atom.get("id", "")
        role = atom.get("role", "Unknown")
        dims = atom.get("dimensions", {}) or atom.get("L3_DIMENSION", {})

        d6 = dims.get("D6_EFFECT", "")
        d5 = dims.get("D5_STATE", "")

        # A1: Command cannot be Pure (commands must have side effects)
        if role == "Command" and d6 == "Pure":
            self.results.antimatter_violations.append({
                "id": atom_id,
                "violation": "A1: Command cannot be Pure",
                "severity": "high"
            })

        # B1: Entity requires state (entities are stateful by definition)
        if role == "Entity" and d5 == "Stateless":
            self.results.antimatter_violations.append({
                "id": atom_id,
                "violation": "B1: Entity requires state",
                "severity": "high"
            })

        # C1: Repository performs I/O (repositories do external I/O)
        if role == "Repository" and d6 == "Pure":
            self.results.antimatter_violations.append({
                "id": atom_id,
                "violation": "C1: Repository performs I/O",
                "severity": "medium"
            })

    def _detect_god_class(self, atom: Dict) -> None:
        """Detect god classes (high complexity)."""
        atom_id = atom.get("id", "")
        complexity = atom.get("complexity", 0)

        if complexity > 15:
            self.results.god_classes.append({
                "id": atom_id,
                "complexity": complexity,
                "reason": f"High complexity: {complexity}"
            })

    def detect_graph_issues(
        self,
        particles: List[Dict],
        in_degree: Dict[str, int],
        out_degree: Dict[str, int],
        hotspot_threshold: float,
        hub_threshold: float
    ) -> None:
        """Detect orphans, hotspots, and hubs from graph structure."""
        self.results.orphan_nodes = []
        self.results.coupling_hotspots = []
        self.results.hub_nodes = []

        for p in particles:
            pid = p.get("id", "")
            in_deg = in_degree.get(pid, 0)
            out_deg = out_degree.get(pid, 0)

            # True orphans: no edges at all
            if in_deg == 0 and out_deg == 0 and p.get("kind") not in ["module", "file"]:
                self.results.orphan_nodes.append({
                    "id": pid,
                    "reason": "No connections"
                })

            # Hotspots: high out-degree
            if out_deg > hotspot_threshold:
                self.results.coupling_hotspots.append({
                    "id": pid,
                    "out_degree": out_deg,
                    "reason": f"Calls {out_deg} components"
                })

            # Hubs: high in-degree
            if in_deg > hub_threshold:
                self.results.hub_nodes.append({
                    "id": pid,
                    "in_degree": in_deg,
                    "reason": f"Called by {in_deg} components"
                })
