"""
Insights Engine - Actionable Intelligence from the Standard Model

REFACTORED: This module now re-exports from the insights/ package.
The monolithic implementation has been split into:
- insights/models.py: InsightType, Priority, Insight, OptimizationSchema
- insights/schemas.py: SCHEMAS dictionary with 13 optimization patterns
- insights/detectors.py: InsightDetector class
- insights/reporter.py: InsightsReporter class
- insights/engine.py: InsightsEngine facade

All original imports continue to work for backward compatibility.
"""

# Re-export everything from the insights package
try:
    from .insights import (
        # Models
        InsightType,
        Priority,
        Insight,
        OptimizationSchema,

        # Data
        SCHEMAS,

        # Classes
        InsightDetector,
        InsightsReporter,
        InsightsEngine,

        # Functions
        generate_insights,
    )
except ImportError:
    from insights import (
        InsightType,
        Priority,
        Insight,
        OptimizationSchema,
        SCHEMAS,
        InsightDetector,
        InsightsReporter,
        InsightsEngine,
        generate_insights,
    )

__all__ = [
    'InsightType',
    'Priority',
    'Insight',
    'OptimizationSchema',
    'SCHEMAS',
    'InsightDetector',
    'InsightsReporter',
    'InsightsEngine',
    'generate_insights',
]


if __name__ == "__main__":
    # Demo
    test_nodes = [
        {"name": "UserService.create", "role": "Command"},
        {"name": "UserService.get", "role": "Query"},
        {"name": "UserService.update", "role": "Command"},
        {"name": "UserRepository.save", "role": "Command"},
        {"name": "User", "role": "Entity"},
        {"name": "Order", "role": "Entity"},
        {"name": "Product", "role": "Entity"},
        {"name": "Payment", "role": "Entity"},
        {"name": "get_config", "role": "Query"},
        {"name": "validate_email", "role": "Utility"},
    ] * 10  # Simulate larger codebase

    insights, report = generate_insights(test_nodes)
    print(report)
