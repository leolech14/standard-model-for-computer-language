#!/usr/bin/env python3
# ⚠️ DEPRECATED: This 6D registry is an experimental grouping.
# The canonical model is 8D (particle_registry_8d.py).
# See STANDARD_MODEL_PAPER.md Section 2.3 for authoritative spec.
"""
🔬 6D GROUPED PARTICLE REGISTRY
Dimensions grouped hierarchically (collapsed overlaps).
========================================================
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, List
import json
from pathlib import Path


@dataclass
class WhatDimension:
    """WHAT: Material composition (our 167 atoms)."""
    continent: str = "Unknown"   # Data, Logic, Organization, Execution
    family: str = "Unknown"      # One of 12 families
    atom: str = "Unknown"        # Specific atom type


@dataclass
class HowDimension:
    """HOW: Behavioral characteristics (merged State + Effect)."""
    state: str = "unknown"       # stateful | stateless
    effect: str = "unknown"      # read | write | read_modify | pure
    is_async: bool = False       # sync vs async


@dataclass
class WhereDimension:
    """WHERE: Context/location (merged Layer + Boundary)."""
    layer: str = "unknown"       # interface | app | core | infra | tests
    boundary: str = "unknown"    # internal | input | io | output


@dataclass 
class WhyDimension:
    """WHY: Intent/purpose (merged Role + Smells)."""
    role: str = "unknown"        # orchestrator | data | worker
    pattern: str = "Unknown"     # Factory, Repository, etc.
    smells: List[str] = field(default_factory=list)


@dataclass
class WhenDimension:
    """WHEN: Temporal characteristics (Activation from 7D)."""
    activation: str = "unknown"  # event | time | direct


@dataclass
class HowLongDimension:
    """HOW_LONG: Lifespan (Lifetime from 7D)."""
    lifetime: str = "unknown"    # transient | session | global


@dataclass
class Particle6D:
    """A particle with 6 grouped dimensions."""
    id: str
    name: str
    file: str
    line: int = 0
    
    what: WhatDimension = field(default_factory=WhatDimension)
    how: HowDimension = field(default_factory=HowDimension)
    where: WhereDimension = field(default_factory=WhereDimension)
    why: WhyDimension = field(default_factory=WhyDimension)
    when: WhenDimension = field(default_factory=WhenDimension)
    how_long: HowLongDimension = field(default_factory=HowLongDimension)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "file": self.file,
            "line": self.line,
            "what": asdict(self.what),
            "how": asdict(self.how),
            "where": asdict(self.where),
            "why": asdict(self.why),
            "when": asdict(self.when),
            "how_long": asdict(self.how_long),
        }


class ParticleRegistry6D:
    """Registry storing particles with 6D grouped coordinates."""
    
    def __init__(self):
        self.particles: List[Particle6D] = []
    
    def add(self, particle: Particle6D):
        self.particles.append(particle)
    
    def export(self, output_path: str):
        """Export to JSON."""
        data = {
            "schema": "6D_GROUPED",
            "dimensions": ["what", "how", "where", "why", "when", "how_long"],
            "particle_count": len(self.particles),
            "particles": [p.to_dict() for p in self.particles],
            "stats": self._compute_stats()
        }
        Path(output_path).write_text(json.dumps(data, indent=2))
        return data
    
    def _compute_stats(self) -> dict:
        """Compute distribution stats per dimension."""
        stats = {
            "what": {"by_continent": {}, "by_family": {}},
            "how": {"by_state": {}, "by_effect": {}},
            "where": {"by_layer": {}, "by_boundary": {}},
            "why": {"by_role": {}, "by_pattern": {}, "total_smells": 0},
            "when": {"by_activation": {}},
            "how_long": {"by_lifetime": {}},
        }
        for p in self.particles:
            # WHAT stats
            stats["what"]["by_continent"][p.what.continent] = stats["what"]["by_continent"].get(p.what.continent, 0) + 1
            stats["what"]["by_family"][p.what.family] = stats["what"]["by_family"].get(p.what.family, 0) + 1
            # HOW stats
            stats["how"]["by_state"][p.how.state] = stats["how"]["by_state"].get(p.how.state, 0) + 1
            stats["how"]["by_effect"][p.how.effect] = stats["how"]["by_effect"].get(p.how.effect, 0) + 1
            # WHERE stats
            stats["where"]["by_layer"][p.where.layer] = stats["where"]["by_layer"].get(p.where.layer, 0) + 1
            stats["where"]["by_boundary"][p.where.boundary] = stats["where"]["by_boundary"].get(p.where.boundary, 0) + 1
            # WHY stats
            stats["why"]["by_role"][p.why.role] = stats["why"]["by_role"].get(p.why.role, 0) + 1
            stats["why"]["by_pattern"][p.why.pattern] = stats["why"]["by_pattern"].get(p.why.pattern, 0) + 1
            stats["why"]["total_smells"] += len(p.why.smells)
            # WHEN stats
            stats["when"]["by_activation"][p.when.activation] = stats["when"]["by_activation"].get(p.when.activation, 0) + 1
            # HOW_LONG stats
            stats["how_long"]["by_lifetime"][p.how_long.lifetime] = stats["how_long"]["by_lifetime"].get(p.how_long.lifetime, 0) + 1
        return stats
