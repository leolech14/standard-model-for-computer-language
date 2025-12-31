"""
Data Preparation
================

Prepares atoms and edges for visualization output.
"""

from typing import List, Dict, Optional, Set
from collections import defaultdict


class DataPreparator:
    """Prepares data for visualization output."""

    def prepare_particles(self, atoms: List[Dict]) -> List[Dict]:
        """Prepare atom data for visualization (deduplicated)."""
        seen_ids = set()
        particles = []

        for i, a in enumerate(atoms):
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

    def prepare_connections(
        self,
        edges: List[Dict],
        valid_ids: Set[str]
    ) -> List[Dict]:
        """Prepare edge data for visualization (deduplicated, validated)."""
        seen_edges = set()
        connections = []

        # Build comprehensive name -> ID lookup for fuzzy matching
        name_to_ids = defaultdict(list)
        module_to_ids = defaultdict(list)

        for vid in valid_ids:
            name_to_ids[vid].append(vid)

            if ":" in vid:
                short = vid.split(":")[-1]
                name_to_ids[short].append(vid)

            if "/" in vid and ":" in vid:
                parts = vid.rsplit("/", 1)[-1]
                name_to_ids[parts].append(vid)

            if "/" in vid:
                file_part = vid.rsplit("/", 1)[-1]
                if ":" in file_part:
                    module_name = file_part.split(":")[0].rsplit(".", 1)[0]
                else:
                    module_name = file_part.rsplit(".", 1)[0]
                module_to_ids[module_name].append(vid)
                name_to_ids[module_name].append(vid)

        for e in edges:
            src = e.get("source") or e.get("from")
            tgt = e.get("target") or e.get("to")

            if not src or not tgt:
                continue

            resolved_src = self._resolve_edge_id(src, name_to_ids, module_to_ids)
            resolved_tgt = self._resolve_edge_id(tgt, name_to_ids, module_to_ids)

            if not resolved_src or not resolved_tgt:
                continue

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

    def _resolve_edge_id(
        self,
        ref: str,
        name_to_ids: Dict[str, List[str]],
        module_to_ids: Dict[str, List[str]]
    ) -> Optional[str]:
        """Resolve an edge reference to a valid node ID."""
        # Direct match
        if ref in name_to_ids and name_to_ids[ref]:
            return name_to_ids[ref][0]

        # module.function format
        if "." in ref:
            parts = ref.split(".")
            if len(parts) >= 2:
                module = parts[-2]
                func = parts[-1]
                candidates = module_to_ids.get(module, [])
                for cid in candidates:
                    if cid.endswith(f":{func}"):
                        return cid

        # Last part after dot
        if "." in ref:
            last_part = ref.split(".")[-1]
            if last_part in name_to_ids and name_to_ids[last_part]:
                matches = name_to_ids[last_part]
                if len(matches) == 1:
                    return matches[0]
                if len(ref.split(".")) >= 2:
                    module_hint = ref.split(".")[-2]
                    for m in matches:
                        if module_hint in m:
                            return m
                return matches[0]

        # Short name directly
        if ref in name_to_ids and name_to_ids[ref]:
            return name_to_ids[ref][0]

        # Module name only
        if ref in module_to_ids and module_to_ids[ref]:
            return module_to_ids[ref][0]

        return None

    def prepare_analysis(
        self,
        detections,
        insights,
        pillars
    ) -> Dict:
        """Prepare analysis metadata for output."""
        return {
            "detections": {
                "antimatter": len(detections.antimatter_violations),
                "god_classes": len(detections.god_classes),
                "orphans": len(detections.orphan_nodes),
                "hotspots": len(detections.coupling_hotspots),
                "hubs": len(detections.hub_nodes),
                "cycles": len(detections.dependency_cycles)
            },
            "insights": {
                "health_score": insights.health_score,
                "coverage": insights.coverage,
                "layer_distribution": insights.layer_distribution,
                "role_distribution": insights.role_distribution,
                "recommendations": insights.recommendations
            },
            "pillars": {
                "omega": pillars.omega,
                "coupling": pillars.coupling,
                "cohesion": pillars.cohesion,
                "spaghetti_score": pillars.spaghetti_score,
                "crossing_number": pillars.crossing_number,
                "cycles": pillars.cycles_count,
                "nash_equilibrium": pillars.nash_equilibrium,
                "coderank_max": pillars.coderank_max,
                "reachability": pillars.reachability
            }
        }
