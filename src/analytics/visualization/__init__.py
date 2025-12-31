"""
Visualization Package
=====================

Modular visualization components extracted from CanonicalVisualizer.

Components:
- models: Data classes (DetectionResults, ArchitectureInsights, FourPillarsMetrics)
- algorithms: Graph algorithms (Gini, Tarjan SCC, BFS)
- detector: Code quality detection (antimatter, god classes)
- metrics: 4 Pillars calculation
- insights: Architecture insights generation
- data_prep: Data preparation for output
- visualizer: Main CanonicalVisualizer facade
"""

from .models import (
    DetectionResults,
    ArchitectureInsights,
    FourPillarsMetrics,
)
from .algorithms import (
    gini_coefficient,
    tarjan_scc_iterative,
    bfs_components,
)
from .detector import CodeDetector
from .metrics import FourPillarsCalculator
from .insights import InsightsGenerator
from .data_prep import DataPreparator
from .visualizer import CanonicalVisualizer, main

__all__ = [
    # Models
    'DetectionResults',
    'ArchitectureInsights',
    'FourPillarsMetrics',

    # Algorithms
    'gini_coefficient',
    'tarjan_scc_iterative',
    'bfs_components',

    # Classes
    'CodeDetector',
    'FourPillarsCalculator',
    'InsightsGenerator',
    'DataPreparator',
    'CanonicalVisualizer',

    # Functions
    'main',
]
