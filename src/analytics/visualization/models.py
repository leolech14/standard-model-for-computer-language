"""
Visualization Models
====================

Data classes for detection results, insights, and metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, List


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
