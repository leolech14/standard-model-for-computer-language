#!/usr/bin/env python3
"""
CANONICAL VISUALIZER - Complete Standard Model Visualization
=============================================================

REFACTORED: This module now re-exports from the visualization/ package.
The monolithic implementation has been split into:
- visualization/models.py: DetectionResults, ArchitectureInsights, FourPillarsMetrics
- visualization/algorithms.py: Graph algorithms (Gini, Tarjan, BFS)
- visualization/detector.py: CodeDetector for antimatter/god class detection
- visualization/metrics.py: FourPillarsCalculator
- visualization/insights.py: InsightsGenerator
- visualization/data_prep.py: DataPreparator
- visualization/visualizer.py: CanonicalVisualizer facade

All original imports continue to work for backward compatibility.

USAGE:
    python canonical_visualizer.py <analysis.json> [output.html]
"""

# Re-export everything from the visualization package
try:
    from .visualization import (
        # Models
        DetectionResults,
        ArchitectureInsights,
        FourPillarsMetrics,

        # Algorithms
        gini_coefficient,
        tarjan_scc_iterative,
        bfs_components,

        # Classes
        CodeDetector,
        FourPillarsCalculator,
        InsightsGenerator,
        DataPreparator,
        CanonicalVisualizer,

        # Functions
        main,
    )
except ImportError:
    from visualization import (
        DetectionResults,
        ArchitectureInsights,
        FourPillarsMetrics,
        gini_coefficient,
        tarjan_scc_iterative,
        bfs_components,
        CodeDetector,
        FourPillarsCalculator,
        InsightsGenerator,
        DataPreparator,
        CanonicalVisualizer,
        main,
    )

__all__ = [
    'DetectionResults',
    'ArchitectureInsights',
    'FourPillarsMetrics',
    'gini_coefficient',
    'tarjan_scc_iterative',
    'bfs_components',
    'CodeDetector',
    'FourPillarsCalculator',
    'InsightsGenerator',
    'DataPreparator',
    'CanonicalVisualizer',
    'main',
]

if __name__ == "__main__":
    main()
