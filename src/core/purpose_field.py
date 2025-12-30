"""
Purpose Field Detector (Backward Compatibility Module)
======================================================

This module re-exports from the refactored purpose package.
New code should import from src.core.purpose directly.

Old:
    from purpose_field import detect_purpose_field, Layer

New:
    from purpose import detect_purpose_field, Layer
"""

# Re-export everything from the new package for backward compatibility
from purpose import (
    Layer,
    LAYER_ORDER,
    LAYER_PURPOSES,
    ROLE_TO_LAYER,
    EMERGENCE_RULES,
    PurposeNode,
    PurposeField,
    PurposeFieldDetector,
    detect_purpose_field,
)

# Also export with old names for full compatibility
PURPOSE_TO_LAYER = ROLE_TO_LAYER  # Old name

__all__ = [
    'Layer',
    'LAYER_ORDER',
    'LAYER_PURPOSES',
    'ROLE_TO_LAYER',
    'PURPOSE_TO_LAYER',  # Deprecated alias
    'EMERGENCE_RULES',
    'PurposeNode',
    'PurposeField',
    'PurposeFieldDetector',
    'detect_purpose_field',
]
