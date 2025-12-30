"""
Purpose Field Package
=====================

Detects the hierarchical emergence of purpose in code:
- Level 1: Atomic Purpose (role of individual functions)
- Level 2: Composite Purpose (emergent from grouped components)
- Level 3: Layer Purpose (shared across architectural layer)
- Level 4: Purpose Field (gradient across entire codebase)

Usage:
    from src.core.purpose import detect_purpose_field, Layer

    field = detect_purpose_field(nodes, edges)
    print(field.summary())
"""

from .constants import (
    Layer,
    LAYER_ORDER,
    LAYER_PURPOSES,
    ROLE_TO_LAYER,
    EMERGENCE_RULES,
    LAYER_NAME_PATTERNS,
)

from .purpose_classifier import PurposeClassifier
from .flow_analyzer import PurposeFlowAnalyzer
from .detector import (
    PurposeNode,
    PurposeField,
    PurposeFieldDetector,
    detect_purpose_field,
)

__all__ = [
    # Constants
    'Layer',
    'LAYER_ORDER',
    'LAYER_PURPOSES',
    'ROLE_TO_LAYER',
    'EMERGENCE_RULES',
    'LAYER_NAME_PATTERNS',
    # Classes
    'PurposeClassifier',
    'PurposeFlowAnalyzer',
    'PurposeNode',
    'PurposeField',
    'PurposeFieldDetector',
    # Functions
    'detect_purpose_field',
]
