"""
Insights Package
================

Modular insights engine extracted from InsightsEngine.

Components:
- models: InsightType, Priority, Insight, OptimizationSchema
- schemas: SCHEMAS dictionary with optimization patterns
- detectors: InsightDetector class
- reporter: InsightsReporter class
- engine: InsightsEngine facade
"""

from .models import (
    InsightType,
    Priority,
    Insight,
    OptimizationSchema,
)
from .schemas import SCHEMAS
from .detectors import InsightDetector
from .reporter import InsightsReporter
from .engine import InsightsEngine, generate_insights

__all__ = [
    # Models
    'InsightType',
    'Priority',
    'Insight',
    'OptimizationSchema',

    # Data
    'SCHEMAS',

    # Classes
    'InsightDetector',
    'InsightsReporter',
    'InsightsEngine',

    # Functions
    'generate_insights',
]
